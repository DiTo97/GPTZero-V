"""C2PA metadata handler."""

import json
import subprocess
import tempfile
from pathlib import Path

from gptzero.handlers.base import MetadataHandler
from gptzero.models import C2PAMetadata
from gptzero.utils import get_c2pa_binary_path, get_file_extension


class C2PAHandler(MetadataHandler):
    """Handler for C2PA metadata extraction."""

    def __init__(self, binary_path: Path | None = None):
        """
        Initialize C2PA handler.

        Args:
            binary_path: Optional path to c2patool binary. If None, will auto-detect.
        """
        self.binary_path = binary_path or get_c2pa_binary_path()

    def extract(
        self, data: bytes, mime_type: str
    ) -> tuple[bool, C2PAMetadata | None, str | None]:
        """
        Extract C2PA metadata from image data.

        Args:
            data: Binary image data
            mime_type: MIME type of the image

        Returns:
            Tuple of (success, C2PAMetadata, error_message)
        """
        if self.binary_path is None:
            return False, None, "Unsupported platform or missing binary"

        extension = get_file_extension(mime_type)
        if extension is None:
            return False, None, f"Unsupported MIME type: {mime_type}"

        # Create a temporary file to save the image
        with tempfile.NamedTemporaryFile(suffix=extension) as temp_file:
            temp_file.write(data)
            temp_file.flush()
            temp_file_path = temp_file.name

            # Run the c2patool binary
            result = subprocess.run(
                [str(self.binary_path), "-d", temp_file_path],
                capture_output=True,
                text=True,
                check=False,
            )

        if result.returncode != 0:
            stderr_stripped = result.stderr.strip()
            if stderr_stripped == "Error: No claim found":
                return True, None, None  # Success, but no C2PA data
            return False, None, f"Error checking C2PA: {stderr_stripped}"

        # Parse the output
        try:
            manifest = json.loads(result.stdout)
            c2pa_metadata = C2PAMetadata.from_manifest(manifest)
            return True, c2pa_metadata, None
        except json.JSONDecodeError:
            return False, None, "C2PA metadata found but cannot be decoded"
        except Exception as e:
            return False, None, f"Error parsing C2PA metadata: {e!s}"
