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

    # Try to find the binary relative to the original src location
    # This handles the case where resources are in the old location
    script_dir = Path(__file__).resolve().parent
    repo_root = script_dir.parent.parent.parent.parent.parent

    # Check old location first (src/authenticity/resources)
    old_resources_dir = repo_root / "src" / "authenticity" / "resources"
    c2patool_dir = old_resources_dir / "c2patool" / c2patool_version

    if current_platform == "Windows":
        binary_path = c2patool_dir / current_platform / "c2patool.exe"
    elif current_platform == "Linux":
        binary_path = c2patool_dir / current_platform / "c2patool"
    elif current_platform == "Darwin":
        binary_path = c2patool_dir / "macOS" / "c2patool"
    else:
        return None

    # Check if the binary exists in old location
    if binary_path.exists():
        return binary_path

    # Try new location (packages/gptzero/resources)
    new_resources_dir = repo_root / "packages" / "gptzero" / "resources"
    c2patool_dir = new_resources_dir / "c2patool" / c2patool_version

    if current_platform == "Windows":
        binary_path = c2patool_dir / current_platform / "c2patool.exe"
    elif current_platform == "Linux":
        binary_path = c2patool_dir / current_platform / "c2patool"
    elif current_platform == "Darwin":
        binary_path = c2patool_dir / "macOS" / "c2patool"
    else:
        return None

    # Check if the binary exists in new location
    if binary_path.exists():
        return binary_path

    return None
