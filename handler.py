import streamlit as st
import io
import json
import platform
import subprocess
import tempfile
import os
from pathlib import Path

# c2pa-python library for reading C2PA data
# See usage: https://raw.githubusercontent.com/contentauth/c2pa-python/refs/heads/main/docs/usage.md
from c2pa import Reader as C2PAReader
from c2pa.c2pa.c2pa import Error as C2PAError

# exif library for reading EXIF data
from exif import Image as ExifImage

# Detect the platform and set the binary path
current_platform = platform.system().lower()
resources_dir = Path(__file__).resolve().parent / "resources"
if current_platform == "windows":
    binary_path = resources_dir / "c2patool_windows.exe"
elif current_platform == "linux":
    binary_path = resources_dir / "c2patool_linux"
elif current_platform == "darwin":
    binary_path = resources_dir / "c2patool_macos"
else:
    binary_path = None

# Check if the binary exists
if binary_path is not None and not binary_path.exists():
    binary_path = None


def compute_probability(c2pa_generated: bool, exif_present: bool) -> int:
    """
    Returns an integer from 0 to 100 representing our 'best guess' 
    of AI-generated probability (purely for demonstration).
    """
    if c2pa_generated:
        return 95  # If explicitly C2PA says "OpenAI", we guess high probability
    elif not exif_present:
        return 50  # No C2PA, no EXIF -> ambiguous
    else:
        return 10   # EXIF present, no AI metadata -> guess it's likely real


def check_c2pa(file_bytes: bytes, mime_type: str = "image/jpeg") -> tuple[bool, dict | None, str | None]:
    """
    Check for C2PA metadata in the image.
    Returns tuple: (is_generated, manifest_dict, error_message).
    """
    try:
        # Use a stream-based reader with the provided mime type
        stream = io.BytesIO(file_bytes)
        reader = C2PAReader(mime_type, stream)
        manifest = reader.get_active_manifest()
        if manifest:
            claim_generator = manifest.get("claim_generator", "")
            if "openai" in claim_generator.lower():
                return True, manifest, None
        return False, manifest, None
    except C2PAError.ManifestNotFound:
        # This is normal for non-C2PA images like regular smartphone photos
        return False, None, "No C2PA metadata found (ManifestNotFound)"
    except C2PAError.Decoding as e:
        print(e)
        # This occurs with some AI-generated images that have malformed C2PA data
        return True, None, "C2PA data present but could not be decoded"
    except Exception as e:
        # For any other unexpected errors
        return False, None, f"Error checking C2PA: {str(e)}"


def check_exif(file_bytes: bytes, mime_type: str | None = None) -> tuple[bool, ExifImage | None]:
    """
    Check for EXIF metadata in the image.
    Returns (has_exif, exif_object).
    """
    try:
        stream = io.BytesIO(file_bytes)
        exif_img = ExifImage(stream)
        if exif_img.has_exif:
            return True, exif_img
        return False, None
    except Exception:
        return False, None


def card(title: str, content: str) -> None:
    st.markdown(f"""
    <div class="card">
      <div class="card-title">{title}</div>
      <div class="card-content">{content}</div>
    </div>
    """, unsafe_allow_html=True)


def c2pa_check_from_binary(file_bytes: bytes) -> tuple[bool, dict | None, str | None]:
    """
    Check for C2PA metadata using platform-specific binaries.
    Returns tuple: (is_generated, manifest_dict, error_message).
    """
    if binary_path is None:
        return False, None, f"Unsupported platform or missing binary: {current_platform}"

    try:
        # Create a temporary file to save the image
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_file.write(file_bytes)
            temp_file_path = temp_file.name

        # Run the c2patool binary with the image file path as a parameter
        result = subprocess.run([str(binary_path), temp_file_path], capture_output=True, text=True)

        # Remove the temporary file
        os.remove(temp_file_path)

        # Capture the output and try to parse it as JSON
        output = result.stdout
        try:
            manifest = json.loads(output)
            claim_generator = manifest.get("claim_generator", "")
            if "openai" in claim_generator.lower():
                return True, manifest, None
            return False, manifest, None
        except json.JSONDecodeError:
            return False, None, "Failed to parse JSON output from c2patool"

    except Exception as e:
        return False, None, f"Error checking C2PA from binary: {str(e)}"


def main() -> None:
    # Inject some CSS to mimic "shadcn card" style
    st.markdown("""
    <style>
    .card {
      background-color: #fff;
      border: 1px solid rgba(0,0,0,0.08);
      border-radius: 8px;
      padding: 16px;
      margin-bottom: 16px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .card-title {
      font-size: 1.1rem;
      font-weight: 600;
      margin-bottom: 8px;
      color: #000;
    }
    .card-content {
      font-size: 0.95rem;
      color: #000;
    }
    </style>
    """, unsafe_allow_html=True)

    st.title("Media Validity Verification")
    st.write("""
    This tool checks if an image contains:
    
    - **C2PA Metadata**: If present, and if the `claim_generator` field indicates an OpenAI image generation model,
      the image is flagged as generated.
    - **EXIF Metadata**: If no relevant C2PA metadata is found, the tool checks for EXIF data, which usually suggests 
      the image was captured from a device.
      
    Finally, it calculates a simplistic "AI-generated probability" for demonstration.
    """)

    # Create two columns: left for uploader, right for results
    left_col, right_col = st.columns([1,2], gap="large")

    with left_col:
        if binary_path is None:
            st.error("c2patool binary is missing. Please ensure the tool is available in the resources directory.")
        else:
            uploaded_file = st.file_uploader("Choose an image", type=["jpg", "jpeg", "png"])

    with right_col:
        if uploaded_file is not None:
            file_bytes = uploaded_file.read()
            # Get the MIME type of the uploaded file
            mime_type = uploaded_file.type
            st.image(file_bytes, caption="Uploaded Image", use_container_width=True)

            # 1) Check C2PA with the detected MIME type
            c2pa_generated, manifest, c2pa_error = c2pa_check_from_binary(file_bytes)

            # 2) Check EXIF with the detected MIME type
            exif_present, exif_data = check_exif(file_bytes, mime_type)

            # 3) Compute AI probability
            ai_probability = compute_probability(c2pa_generated, exif_present)

            # Show AI Probability Card
            card(
                title="AI-Generated Probability",
                content=f"""
                <p><strong>{ai_probability}%</strong> chance this image was generated by AI (heuristic estimate).</p>
                """
            )

            # If C2PA is present, show its card
            if manifest is not None:
                # We can pretty-print the manifest or just highlight relevant fields
                # Here, let's highlight 'claim_generator' and 'title', if available
                claim_generator = manifest.get("claim_generator", "Not specified")
                claim_title = manifest.get("title", "N/A")

                c2pa_html = f"""
                <ul>
                  <li><strong>Claim Generator:</strong> {claim_generator}</li>
                  <li><strong>Title:</strong> {claim_title}</li>
                </ul>
                <p><em>Full Manifest:</em></p>
                <pre style="white-space: pre-wrap;">{json.dumps(manifest, indent=2)}</pre>
                """
                card("C2PA Metadata Found", c2pa_html)
            else:
                c2pa_message = c2pa_error or "No C2PA metadata found."
                card("C2PA Metadata", f"<p>{c2pa_message}</p>")

            # If EXIF is present, show an EXIF card with a few interesting fields
            if exif_present:
                # Gather some typical fields
                exif_fields_of_interest = [
                    ("EXIF Version", getattr(exif_data, 'exif_version', None)),
                    ("Camera Make", getattr(exif_data, 'make', None)),
                    ("Camera Model", getattr(exif_data, 'model', None)),
                    ("Date/Time Original", getattr(exif_data, 'datetime_original', None)),
                    ("GPS Latitude", getattr(exif_data, 'gps_latitude', None)),
                    ("GPS Longitude", getattr(exif_data, 'gps_longitude', None)),
                ]

                exif_content = "<ul>"
                for label, value in exif_fields_of_interest:
                    if value is not None:
                        exif_content += f"<li><strong>{label}:</strong> {value}</li>"
                exif_content += "</ul>"

                card("EXIF Metadata Found", exif_content)
            else:
                card("EXIF Metadata", "<p>No EXIF metadata found.</p>")

        else:
            st.info("Please upload an image to see the analysis.")

    # A horizontal rule
    st.markdown("---")
    st.header("README")
    st.markdown("""
    ### Media Validity Verification Tool

    **Overview**:
    
    This Streamlit app is designed as an early stage mechanism to verify whether an image appears to be
    captured from a device or generated using AI image generation tools (e.g., OpenAI models).
    
    **How It Works**:
    
    1. **C2PA Metadata Check**:
       - The app uses the [c2pa-python](https://github.com/contentauth/c2pa-python) library to read C2PA metadata.
       - It checks the active manifest's `claim_generator` field.
       - If this field contains the string `"openai"`, the image is flagged as likely generated.
    
    2. **EXIF Metadata Check**:
       - If no relevant C2PA metadata is found, the app uses the [exif](https://gitlab.com/TNThieding/exif) library.
       - Presence of EXIF metadata (e.g., camera information) can indicate that the image was taken by a device.
    
    3. **Heuristic Probability**:
       - As a demo, we compute a basic probability from 0–100 for AI generation. This is purely illustrative 
         and should not be considered a reliable metric.
    
    **Limitations**:
    
    - **Not Bulletproof**: EXIF metadata can be manipulated or added to images that were not actually captured by a device.
    - **Incomplete Coverage**: This tool does not cover all watermarking or authenticity measures (for example,
      [Google's SynthID](https://ai.googleblog.com/2022/05/announcing-synthid-for-generative-ai.html) is not supported).
    - **Call to Action**: With the increasing accuracy of media generation models, more structured efforts towards
      media validity verification must be enforced. We hope this tool raises awareness and sparks further discussion
      in the community.
    """)


if __name__ == "__main__":
    main()
