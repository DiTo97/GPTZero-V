import io

from exif import Image as ExifImage


def check_exif(file_bytes: bytes) -> tuple[bool, ExifImage | None]:
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
    except Exception as e:
        return False, None
