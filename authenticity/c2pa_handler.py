import json
import subprocess
import tempfile

from authenticity.c2pa_metadata import C2PAMetadata

from .metadata_utils import get_c2pa_binary_path, mime_map


def c2pa_check_from_binary(
    file_bytes: bytes, mime_type: str
) -> tuple[bool, C2PAMetadata | None, str | None]:
    """
    Check for C2PA metadata using platform-specific binaries.
    Returns tuple: (is_generated, c2pa_metadata_obj, error_message).
    """
    binary_path = get_c2pa_binary_path()

    if binary_path is None:
        return False, None, f"Unsupported platform or missing binary"

    extension = mime_map[mime_type]

    # Create a temporary file to save the image
    with tempfile.NamedTemporaryFile(suffix=extension) as temp_file:
        temp_file.write(file_bytes)
        temp_file_path = temp_file.name

        # Run the c2patool binary with the image file path as a parameter
        result = subprocess.run(
            [str(binary_path), "-d", temp_file_path], capture_output=True, text=True, check=False
        )

    if result.returncode != 0:
        stderr_stripped = result.stderr.strip()
        if stderr_stripped == "Error: No claim found":
            return False, None, None  # Not generated, no manifest, no error
        return False, None, f"Error checking C2PA from binary: {stderr_stripped}"

    # Capture the output and try to parse it as JSON
    output = result.stdout
    try:
        manifest = json.loads(output)
        c2pa_metadata = C2PAMetadata.from_manifest(manifest)
    except json.JSONDecodeError:
        return False, None, "The image has C2PA metadata, but it cannot be decoded"
    except Exception as e:
        return False, None, f"Error parsing C2PA metadata: {e!s}"

    # Check if the image is generated based on C2PAMetadata fields
    is_generated = False

    # Check if generator name indicates AI generation
    if any(
        ai_tool in c2pa_metadata.generator_name
        for ai_tool in ["ChatGPT", "DALL·E", "Dall-E", "OpenAI"]
    ):
        is_generated = True

    # Check if any software agent indicates AI generation
    if not is_generated:
        for agent in c2pa_metadata.software_agents:
            if any(
                ai_tool in agent.name for ai_tool in ["GPT-4o", "DALL-E", "DALL·E", "OpenAI API"]
            ):
                is_generated = True
                break

    # Check if digital source type indicates AI generation
    if (
        not is_generated
        and c2pa_metadata.digital_source_type
        and "AI tool" in c2pa_metadata.digital_source_type
    ):
        is_generated = True

    return is_generated, c2pa_metadata, None
