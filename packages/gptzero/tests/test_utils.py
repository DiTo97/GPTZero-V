"""Tests for utility functions."""

from gptzero.utils import get_file_extension


class TestUtils:
    """Tests for utility functions."""

    def test_get_file_extension_jpeg(self):
        """Test getting file extension for JPEG."""
        assert get_file_extension("image/jpeg") == ".jpg"

    def test_get_file_extension_png(self):
        """Test getting file extension for PNG."""
        assert get_file_extension("image/png") == ".png"

    def test_get_file_extension_unsupported(self):
        """Test getting file extension for unsupported type."""
        assert get_file_extension("image/xyz") is None

    def test_get_file_extension_empty(self):
        """Test getting file extension for empty string."""
        assert get_file_extension("") is None
