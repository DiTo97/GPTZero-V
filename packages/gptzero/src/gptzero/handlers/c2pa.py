"""C2PA metadata handler."""

import io
import json

from c2pa import C2paError, Reader

from gptzero.handlers.base import MetadataHandler
from gptzero.models import C2PAMetadata


class C2PAHandler(MetadataHandler):
    """Handler for C2PA metadata extraction using c2pa-python bindings."""

    def __init__(self):
        """Initialize C2PA handler."""
        pass

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
        try:
            # Create a BytesIO stream from the image data
            stream = io.BytesIO(data)

            # Use c2pa Reader to extract manifest
            reader = Reader(mime_type, stream)
            manifest_json = reader.json()

            if manifest_json is None:
                return True, None, None  # Success, but no C2PA data

            # Parse the manifest JSON
            manifest = json.loads(manifest_json)
            c2pa_metadata = C2PAMetadata.from_manifest(manifest)
            return True, c2pa_metadata, None

        except C2paError as e:
            # Check if it's a ManifestNotFound error (no C2PA data)
            error_str = str(e)
            if "ManifestNotFound" in error_str or "no JUMBF data found" in error_str:
                return True, None, None  # Success, but no C2PA data
            return False, None, f"Error checking C2PA: {error_str}"
        except json.JSONDecodeError:
            return False, None, "C2PA metadata found but cannot be decoded"
        except Exception as e:
            return False, None, f"Error parsing C2PA metadata: {e!s}"
