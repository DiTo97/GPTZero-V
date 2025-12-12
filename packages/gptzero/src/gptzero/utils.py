"""Utility functions."""

import platform
from pathlib import Path


# MIME type to file extension mapping
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

    Args:
        mime_type: MIME type string

    Returns:
        File extension or None if unsupported
    """
    return MIME_MAP.get(mime_type)


def get_c2pa_binary_path() -> Path | None:
    """
    Get the path to the C2PA binary based on platform.

    Returns:
        Path to c2patool binary or None if not found
    """
    current_platform = platform.system()
    c2patool_version = "v0.16.1"

    # Determine binary filename based on platform
    if current_platform == "Windows":
        binary_name = "c2patool.exe"
        platform_dir = "Windows"
    elif current_platform == "Linux":
        binary_name = "c2patool"
        platform_dir = "Linux"
    elif current_platform == "Darwin":
        binary_name = "c2patool"
        platform_dir = "macOS"
    else:
        return None

    # Try to find the binary relative to this file
    script_dir = Path(__file__).resolve().parent

    # Check package-local resources (packages/gptzero/resources)
    local_resources = script_dir.parent / "resources" / "c2patool" / c2patool_version / platform_dir
    local_binary = local_resources / binary_name
    if local_binary.exists():
        return local_binary

    # Try to find repo root more robustly
    current = script_dir
    for _ in range(10):  # Prevent infinite loop
        if (current / ".git").exists() or (current / "pyproject.toml").exists():
            # Found repo root, check old location
            old_resources = current / "src" / "authenticity" / "resources"
            old_binary = old_resources / "c2patool" / c2patool_version / platform_dir / binary_name
            if old_binary.exists():
                return old_binary
            break
        current = current.parent

    return None
