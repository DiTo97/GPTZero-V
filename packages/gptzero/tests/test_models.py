"""Tests for gptzero models."""

import pytest

from gptzero.models import (
    AuthenticityResult,
    C2PAMetadata,
    EXIFMetadata,
    ImageInput,
    SoftwareAgent,
    VerificationOutput,
)


class TestImageInput:
    """Tests for ImageInput model."""

    def test_valid_input(self):
        """Test creating valid ImageInput."""
        input_data = ImageInput(
            data=b"fake_image_data", mime_type="image/jpeg", filename="test.jpg"
        )
        assert input_data.data == b"fake_image_data"
        assert input_data.mime_type == "image/jpeg"
        assert input_data.filename == "test.jpg"

    def test_validate_empty_data(self):
        """Test validation with empty data."""
        input_data = ImageInput(data=b"", mime_type="image/jpeg")
        with pytest.raises(ValueError, match="Image data cannot be empty"):
            input_data.validate()

    def test_validate_missing_mime_type(self):
        """Test validation with missing MIME type."""
        input_data = ImageInput(data=b"fake_data", mime_type="")
        with pytest.raises(ValueError, match="MIME type is required"):
            input_data.validate()


class TestSoftwareAgent:
    """Tests for SoftwareAgent model."""

    def test_formatted_action_created(self):
        """Test formatted action for 'created'."""
        agent = SoftwareAgent(name="DALL-E", action="created")
        assert agent.get_formatted_action() == "The asset was created by"

    def test_formatted_action_converted(self):
        """Test formatted action for 'converted'."""
        agent = SoftwareAgent(name="Tool", action="converted")
        assert agent.get_formatted_action() == "The asset format was converted by"

    def test_formatted_action_other(self):
        """Test formatted action for other actions."""
        agent = SoftwareAgent(name="Tool", action="edited")
        assert agent.get_formatted_action() == "edited by"


class TestC2PAMetadata:
    """Tests for C2PAMetadata model."""

    def test_is_ai_generated_by_generator_name(self):
        """Test AI detection by generator name."""
        metadata = C2PAMetadata(
            instance_id="test",
            title="Test",
            issuer="Test Issuer",
            generator_name="OpenAI ChatGPT",
            digital_source_type=None,
            software_agents=[],
        )
        assert metadata.is_ai_generated() is True

    def test_is_ai_generated_by_software_agent(self):
        """Test AI detection by software agent."""
        metadata = C2PAMetadata(
            instance_id="test",
            title="Test",
            issuer="Test Issuer",
            generator_name="Unknown",
            digital_source_type=None,
            software_agents=[SoftwareAgent(name="GPT-4o", action="created")],
        )
        assert metadata.is_ai_generated() is True

    def test_is_ai_generated_by_digital_source_type(self):
        """Test AI detection by digital source type."""
        metadata = C2PAMetadata(
            instance_id="test",
            title="Test",
            issuer="Test Issuer",
            generator_name="Unknown",
            digital_source_type="This content was generated with an AI tool",
            software_agents=[],
        )
        assert metadata.is_ai_generated() is True

    def test_is_not_ai_generated(self):
        """Test when content is not AI generated."""
        metadata = C2PAMetadata(
            instance_id="test",
            title="Test",
            issuer="Test Issuer",
            generator_name="Adobe Photoshop",
            digital_source_type=None,
            software_agents=[SoftwareAgent(name="Photoshop", action="edited")],
        )
        assert metadata.is_ai_generated() is False


class TestEXIFMetadata:
    """Tests for EXIFMetadata model."""

    def test_has_exif_true(self):
        """Test EXIF metadata with data."""
        metadata = EXIFMetadata(
            has_exif=True, make="Canon", model="EOS 5D", exif_version="0230"
        )
        assert metadata.has_exif is True
        assert metadata.make == "Canon"
        assert metadata.model == "EOS 5D"

    def test_has_exif_false(self):
        """Test EXIF metadata without data."""
        metadata = EXIFMetadata(has_exif=False)
        assert metadata.has_exif is False
        assert metadata.make is None


class TestAuthenticityResult:
    """Tests for AuthenticityResult model."""

    def test_valid_probability(self):
        """Test valid probability values."""
        result = AuthenticityResult(
            probability=50, is_likely_authentic=False, confidence_level="medium"
        )
        assert result.probability == 50

    def test_invalid_probability_negative(self):
        """Test invalid negative probability."""
        with pytest.raises(ValueError, match="Probability must be between 0 and 100"):
            AuthenticityResult(probability=-1, is_likely_authentic=False, confidence_level="low")

    def test_invalid_probability_over_100(self):
        """Test invalid probability over 100."""
        with pytest.raises(ValueError, match="Probability must be between 0 and 100"):
            AuthenticityResult(probability=101, is_likely_authentic=False, confidence_level="low")


class TestVerificationOutput:
    """Tests for VerificationOutput model."""

    def test_has_c2pa_true(self):
        """Test has_c2pa property when C2PA is present."""
        c2pa = C2PAMetadata(
            instance_id="test",
            title="Test",
            issuer="Issuer",
            generator_name="Generator",
            digital_source_type=None,
            software_agents=[],
        )
        output = VerificationOutput(
            authenticity=AuthenticityResult(
                probability=50, is_likely_authentic=False, confidence_level="medium"
            ),
            c2pa_metadata=c2pa,
            exif_metadata=None,
        )
        assert output.has_c2pa is True

    def test_has_c2pa_false(self):
        """Test has_c2pa property when C2PA is absent."""
        output = VerificationOutput(
            authenticity=AuthenticityResult(
                probability=50, is_likely_authentic=False, confidence_level="medium"
            ),
            c2pa_metadata=None,
            exif_metadata=None,
        )
        assert output.has_c2pa is False

    def test_has_exif_true(self):
        """Test has_exif property when EXIF is present."""
        exif = EXIFMetadata(has_exif=True, make="Canon")
        output = VerificationOutput(
            authenticity=AuthenticityResult(
                probability=50, is_likely_authentic=False, confidence_level="medium"
            ),
            c2pa_metadata=None,
            exif_metadata=exif,
        )
        assert output.has_exif is True

    def test_has_exif_false(self):
        """Test has_exif property when EXIF is absent."""
        output = VerificationOutput(
            authenticity=AuthenticityResult(
                probability=50, is_likely_authentic=False, confidence_level="medium"
            ),
            c2pa_metadata=None,
            exif_metadata=EXIFMetadata(has_exif=False),
        )
        assert output.has_exif is False
