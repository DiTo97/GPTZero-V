"""Integration tests for C2PA handler using real example images."""

from pathlib import Path

from gptzero_o.handlers.c2pa import C2PAHandler
from gptzero_o.models import ImageInput
from gptzero_o.verification import ImageVerifier


# Path to example images
# Use parents[3] for more robust path traversal
# test_c2pa_integration.py -> tests (0) -> gptzero (1) -> packages (2) -> GPTZero-V (3) -> examples
EXAMPLES_DIR = Path(__file__).parents[3] / "examples"


class TestC2PAHandlerIntegration:
    """Integration tests for C2PAHandler with real images."""

    def test_extract_from_gpt4o_image(self):
        """Test extraction from GPT-4o generated image with C2PA."""
        image_path = EXAMPLES_DIR / "GPT-4o.png"
        assert image_path.exists(), f"Example image not found: {image_path}"

        with open(image_path, "rb") as f:
            data = f.read()

        handler = C2PAHandler()
        success, metadata, error = handler.extract(data, "image/png")

        assert success is True, f"Extraction failed: {error}"
        assert metadata is not None, "Expected C2PA metadata but got None"
        assert error is None, f"Unexpected error: {error}"

        # Verify metadata fields
        assert metadata.instance_id is not None
        assert metadata.title is not None
        assert metadata.generator_name is not None
        assert "ChatGPT" in metadata.generator_name or "GPT" in metadata.generator_name

        # This should be detected as AI-generated
        assert metadata.is_ai_generated() is True

    def test_extract_from_gpt4o_screenshot(self):
        """Test extraction from GPT-4o screenshot image (no C2PA expected)."""
        image_path = EXAMPLES_DIR / "GPT-4o-screenshot.png"
        assert image_path.exists(), f"Example image not found: {image_path}"

        with open(image_path, "rb") as f:
            data = f.read()

        handler = C2PAHandler()
        success, metadata, error = handler.extract(data, "image/png")

        # Screenshots typically don't have C2PA metadata
        assert success is True, f"Extraction failed: {error}"
        # This image may or may not have C2PA - accept either case
        assert error is None, f"Unexpected error: {error}"

    def test_extract_from_image_without_c2pa(self):
        """Test extraction from image without C2PA metadata."""
        image_path = EXAMPLES_DIR / "Google-Pixel-8.jpg"
        assert image_path.exists(), f"Example image not found: {image_path}"

        with open(image_path, "rb") as f:
            data = f.read()

        handler = C2PAHandler()
        success, metadata, error = handler.extract(data, "image/jpeg")

        # Should succeed but return no metadata
        assert success is True, f"Extraction should succeed but got error: {error}"
        assert metadata is None, "Expected no C2PA metadata"
        assert error is None, f"Should not have error for missing C2PA: {error}"

    def test_extract_from_timestamp_image(self):
        """Test extraction from timestamp image."""
        image_path = EXAMPLES_DIR / "1743366489519.jpg"
        assert image_path.exists(), f"Example image not found: {image_path}"

        with open(image_path, "rb") as f:
            data = f.read()

        handler = C2PAHandler()
        success, metadata, error = handler.extract(data, "image/jpeg")

        # Should succeed (whether it has C2PA or not)
        assert success is True, f"Extraction failed: {error}"
        assert error is None, f"Unexpected error: {error}"


class TestImageVerifierIntegration:
    """Integration tests for ImageVerifier with real images."""

    def test_verify_ai_generated_image(self):
        """Test verification of AI-generated image."""
        image_path = EXAMPLES_DIR / "GPT-4o.png"
        assert image_path.exists(), f"Example image not found: {image_path}"

        with open(image_path, "rb") as f:
            data = f.read()

        verifier = ImageVerifier()
        result = verifier.verify(
            ImageInput(data=data, mime_type="image/png", filename="GPT-4o.png")
        )

        # Should have C2PA metadata
        assert result.has_c2pa is True
        assert result.c2pa_metadata is not None

        # Should be detected as AI-generated
        assert result.c2pa_metadata.is_ai_generated() is True

        # Should have high probability of being non-authentic (AI-generated)
        assert result.authenticity.probability >= 80
        assert result.authenticity.is_likely_authentic is False

    def test_verify_camera_captured_image(self):
        """Test verification of camera-captured image."""
        image_path = EXAMPLES_DIR / "Google-Pixel-8.jpg"
        assert image_path.exists(), f"Example image not found: {image_path}"

        with open(image_path, "rb") as f:
            data = f.read()

        verifier = ImageVerifier()
        result = verifier.verify(
            ImageInput(data=data, mime_type="image/jpeg", filename="Google-Pixel-8.jpg")
        )

        # May or may not have C2PA, but should not have error
        assert result.error is None

        # If it has EXIF data, probability should be lower
        if result.has_exif:
            assert result.authenticity.probability <= 30


class TestFeatureParity:
    """Tests to ensure feature parity with c2patool binary."""

    def test_manifest_structure_compatibility(self):
        """Test that manifest structure is compatible with C2PAMetadata.from_manifest."""
        image_path = EXAMPLES_DIR / "GPT-4o.png"
        assert image_path.exists(), f"Example image not found: {image_path}"

        with open(image_path, "rb") as f:
            data = f.read()

        handler = C2PAHandler()
        success, metadata, error = handler.extract(data, "image/png")

        assert success is True
        assert metadata is not None

        # Verify all expected fields are present
        assert hasattr(metadata, "instance_id")
        assert hasattr(metadata, "title")
        assert hasattr(metadata, "issuer")
        assert hasattr(metadata, "generator_name")
        assert hasattr(metadata, "digital_source_type")
        assert hasattr(metadata, "software_agents")

        # Verify methods work
        assert isinstance(metadata.is_ai_generated(), bool)

    def test_error_handling_consistency(self):
        """Test that error handling is consistent with binary approach."""
        handler = C2PAHandler()

        # Test with empty data
        success, metadata, error = handler.extract(b"", "image/jpeg")
        assert success is False or metadata is None

        # Test with invalid data
        success, metadata, error = handler.extract(b"invalid image data", "image/jpeg")
        assert success is False or metadata is None
