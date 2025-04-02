import platform
from pathlib import Path


# MIME type to file extension mapping
mime_map = {
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


def get_c2pa_binary_path():
    """Get the path to the C2PA binary based on platform"""
    current_platform = platform.system()
    c2patool_version = "v0.16.1"
    script_dir = Path(__file__).resolve().parent
    c2patool_dir = script_dir / "resources" / "c2patool" / c2patool_version

    if current_platform == "Windows":
        binary_path = c2patool_dir / current_platform / "c2patool.exe"
    elif current_platform == "Linux":
        binary_path = c2patool_dir / current_platform / "c2patool"
    elif current_platform == "Darwin":
        binary_path = c2patool_dir / "macOS" / "c2patool"
    else:
        binary_path = None

    # Check if the binary exists
    if binary_path is not None and not binary_path.exists():
        binary_path = None

    return binary_path
