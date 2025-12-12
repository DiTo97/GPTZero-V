"""EXIF metadata handler."""

import io

from exif import Image as ExifImage

from gptzero.handlers.base import MetadataHandler
from gptzero.models import EXIFMetadata


class EXIFHandler(MetadataHandler):
    """Handler for EXIF metadata extraction."""

    def extract(
        self, data: bytes, mime_type: str
    ) -> tuple[bool, EXIFMetadata | None, str | None]:
        """
        Extract EXIF metadata from image data.

        Args:
            data: Binary image data
            mime_type: MIME type of the image

        Returns:
            Tuple of (success, EXIFMetadata, error_message)
        """
        try:
            stream = io.BytesIO(data)
            exif_img = ExifImage(stream)

            if exif_img.has_exif:
                metadata = EXIFMetadata.from_exif_image(exif_img)
                return True, metadata, None
            else:
                metadata = EXIFMetadata(has_exif=False)
                return True, metadata, None
        except Exception:
            # If EXIF parsing fails (e.g., corrupted data, unsupported format),
            # treat it as "no EXIF data" rather than an error.
            # This is expected for many valid images.
            metadata = EXIFMetadata(has_exif=False)
            return True, metadata, None
