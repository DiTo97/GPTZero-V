"""Utility functions."""

# MIME type to file extension mapping
# NOTE: This is kept for backward compatibility but is no longer used
# by the C2PA handler. The c2pa-python library handles MIME type validation.
MIME_MAP = {
    "image/avif": ".avif",
    "image/bmp": ".bmp",
    "image/gif": ".gif",
    "image/heic": ".heic",
    "image/heif": ".heif",
    "image/jpeg": ".jpg",
    "image/jpg": ".jpg",
    "image/png": ".png",
    "image/svg+xml": ".svg",
    "image/tiff": ".tiff",
    "image/webp": ".webp",
}


def get_file_extension(mime_type: str) -> str | None:
    """
    Get file extension for a MIME type.

    .. deprecated:: 0.2.0
        This function is no longer used by C2PAHandler.
        Kept for backward compatibility only.

    Args:
        mime_type: MIME type string

    Returns:
        File extension or None if unsupported
    """
    return MIME_MAP.get(mime_type)
