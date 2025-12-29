"""Integration tests for GPTZero-o SDK/API."""

import subprocess
import sys
import time

import pytest


# Test image data (1x1 pixel transparent PNG)
TEST_IMAGE_DATA = (
    b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
    b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01"
    b"\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
)


class TestCoreSDK:
    """Test the core SDK functionality."""

    def test_image_verifier_import(self):
        """Test that the ImageVerifier can be imported."""
        from gptzero_o import ImageVerifier, ImageInput

        assert ImageVerifier is not None
        assert ImageInput is not None

    def test_image_verifier_basic_usage(self):
        """Test basic usage of ImageVerifier."""
        from gptzero_o import ImageVerifier, ImageInput

        verifier = ImageVerifier()
        image_input = ImageInput(
            data=TEST_IMAGE_DATA, mime_type="image/png", filename="test.png"
        )

        result = verifier.verify(image_input)

        assert result is not None
        assert result.authenticity is not None
        assert 0 <= result.authenticity.probability <= 100


class TestAPIClient:
    """Test the API client (SDK)."""

    @pytest.fixture
    def api_process(self):
        """Start the API server for testing."""
        # Start the API in a subprocess
        process = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "gptzero_o_api.api:app",
                "--host",
                "127.0.0.1",
                "--port",
                "8888",
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )

        # Wait for the server to start
        time.sleep(3)

        yield process

        # Stop the server
        process.terminate()
        process.wait(timeout=5)

    def test_client_import(self):
        """Test that the client can be imported."""
        from gptzero_o_sdk import GPTZeroClient

        assert GPTZeroClient is not None

    def test_client_health_check(self, api_process):
        """Test the client can check API health."""
        from gptzero_o_sdk import GPTZeroClient

        with GPTZeroClient(base_url="http://127.0.0.1:8888") as client:
            health = client.health()
            assert health.status == "ok"
            assert health.version == "0.1.0"

    def test_client_verify_image_bytes(self, api_process):
        """Test the client can verify an image from bytes."""
        from gptzero_o_sdk import GPTZeroClient

        with GPTZeroClient(base_url="http://127.0.0.1:8888") as client:
            result = client.verify_image(file_bytes=TEST_IMAGE_DATA, filename="test.png")
            assert result is not None
            assert result.authenticity is not None
            assert 0 <= result.authenticity.probability <= 100
