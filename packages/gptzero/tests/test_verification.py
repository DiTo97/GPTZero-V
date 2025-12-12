"""Tests for verification logic."""

from unittest.mock import Mock, patch

import pytest

from gptzero.models import C2PAMetadata, EXIFMetadata, ImageInput, SoftwareAgent
from gptzero.verification import ImageVerifier


class TestImageVerifier:
    """Tests for ImageVerifier class."""

    def test_verify_with_invalid_input(self):
        """Test verification with invalid input."""
        verifier = ImageVerifier()
        invalid_input = ImageInput(data=b"", mime_type="image/jpeg")

        result = verifier.verify(invalid_input)

        assert result.error is not None
        assert "cannot be empty" in result.error
        assert result.authenticity.probability == 50

    @patch("gptzero.verification.C2PAHandler")
    @patch("gptzero.verification.EXIFHandler")
    def test_verify_ai_generated_image(self, mock_exif_handler, mock_c2pa_handler):
        """Test verification of AI-generated image."""
        # Setup mocks
        c2pa_metadata = C2PAMetadata(
            instance_id="test",
            title="Test",
            issuer="OpenAI",
            generator_name="DALL·E",
            digital_source_type=None,
            software_agents=[],
        )
        mock_c2pa_handler.return_value.extract.return_value = (True, c2pa_metadata, None)
        mock_exif_handler.return_value.extract.return_value = (
            True,
            EXIFMetadata(has_exif=False),
            None,
        )

        verifier = ImageVerifier()
        image_input = ImageInput(data=b"fake_data", mime_type="image/jpeg")

        result = verifier.verify(image_input)

        assert result.authenticity.probability == 95
        assert result.authenticity.is_likely_authentic is False
        assert result.authenticity.confidence_level == "high"
        assert result.has_c2pa is True

    @patch("gptzero.verification.C2PAHandler")
    @patch("gptzero.verification.EXIFHandler")
    def test_verify_authentic_image_with_exif(self, mock_exif_handler, mock_c2pa_handler):
        """Test verification of authentic image with EXIF."""
        # Setup mocks
        mock_c2pa_handler.return_value.extract.return_value = (True, None, None)
        exif_metadata = EXIFMetadata(has_exif=True, make="Canon", model="EOS 5D")
        mock_exif_handler.return_value.extract.return_value = (True, exif_metadata, None)

        verifier = ImageVerifier()
        image_input = ImageInput(data=b"fake_data", mime_type="image/jpeg")

        result = verifier.verify(image_input)

        assert result.authenticity.probability == 10
        assert result.authenticity.is_likely_authentic is True
        assert result.authenticity.confidence_level == "high"
        assert result.has_exif is True

    @patch("gptzero.verification.C2PAHandler")
    @patch("gptzero.verification.EXIFHandler")
    def test_verify_ambiguous_image(self, mock_exif_handler, mock_c2pa_handler):
        """Test verification of ambiguous image (no C2PA, no EXIF)."""
        # Setup mocks
        mock_c2pa_handler.return_value.extract.return_value = (True, None, None)
        mock_exif_handler.return_value.extract.return_value = (
            True,
            EXIFMetadata(has_exif=False),
            None,
        )

        verifier = ImageVerifier()
        image_input = ImageInput(data=b"fake_data", mime_type="image/jpeg")

        result = verifier.verify(image_input)

        assert result.authenticity.probability == 50
        assert result.authenticity.is_likely_authentic is False
        assert result.authenticity.confidence_level == "low"

    @patch("gptzero.verification.C2PAHandler")
    @patch("gptzero.verification.EXIFHandler")
    def test_verify_with_extraction_error(self, mock_exif_handler, mock_c2pa_handler):
        """Test verification when extraction fails."""
        # Setup mocks
        mock_c2pa_handler.return_value.extract.return_value = (
            False,
            None,
            "C2PA extraction failed",
        )
        mock_exif_handler.return_value.extract.return_value = (True, None, None)

        verifier = ImageVerifier()
        image_input = ImageInput(data=b"fake_data", mime_type="image/jpeg")

        result = verifier.verify(image_input)

        assert result.error == "C2PA extraction failed"
        assert result.authenticity.probability == 50


class TestComputeAuthenticity:
    """Tests for _compute_authenticity method."""

    def test_compute_authenticity_ai_generated(self):
        """Test authenticity computation for AI-generated content."""
        verifier = ImageVerifier()
        c2pa = C2PAMetadata(
            instance_id="test",
            title="Test",
            issuer="OpenAI",
            generator_name="DALL·E",
            digital_source_type=None,
            software_agents=[],
        )
        exif = EXIFMetadata(has_exif=False)

        result = verifier._compute_authenticity(c2pa, exif)

        assert result.probability == 95
        assert result.is_likely_authentic is False
        assert result.confidence_level == "high"

    def test_compute_authenticity_no_metadata(self):
        """Test authenticity computation with no metadata."""
        verifier = ImageVerifier()
        exif = EXIFMetadata(has_exif=False)

        result = verifier._compute_authenticity(None, exif)

        assert result.probability == 50
        assert result.is_likely_authentic is False
        assert result.confidence_level == "low"

    def test_compute_authenticity_with_exif_only(self):
        """Test authenticity computation with EXIF only."""
        verifier = ImageVerifier()
        exif = EXIFMetadata(has_exif=True, make="Canon")

        result = verifier._compute_authenticity(None, exif)

        assert result.probability == 10
        assert result.is_likely_authentic is True
        assert result.confidence_level == "high"

    def test_compute_authenticity_with_c2pa_not_ai(self):
        """Test authenticity computation with C2PA but not AI-generated."""
        verifier = ImageVerifier()
        c2pa = C2PAMetadata(
            instance_id="test",
            title="Test",
            issuer="Adobe",
            generator_name="Photoshop",
            digital_source_type=None,
            software_agents=[],
        )
        exif = EXIFMetadata(has_exif=True, make="Canon")

        result = verifier._compute_authenticity(c2pa, exif)

        assert result.probability == 30
        assert result.is_likely_authentic is True
        assert result.confidence_level == "medium"
