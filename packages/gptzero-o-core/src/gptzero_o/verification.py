"""Core verification logic."""

from gptzero_o.handlers.c2pa import C2PAHandler
from gptzero_o.handlers.exif import EXIFHandler
from gptzero_o.models import AuthenticityResult, ImageInput, VerificationOutput


class ImageVerifier:
    """Main class for image authenticity verification."""

    def __init__(self):
        """Initialize the verifier with handlers."""
        self.c2pa_handler = C2PAHandler()
        self.exif_handler = EXIFHandler()

    def verify(self, image_input: ImageInput) -> VerificationOutput:
        """
        Verify image authenticity.

        Args:
            image_input: ImageInput object containing image data

        Returns:
            VerificationOutput with verification results
        """
        # Validate input
        try:
            image_input.validate()
        except ValueError as e:
            return VerificationOutput(
                authenticity=AuthenticityResult(
                    probability=50, is_likely_authentic=False, confidence_level="low"
                ),
                c2pa_metadata=None,
                exif_metadata=None,
                error=str(e),
            )

        # Extract C2PA metadata
        c2pa_success, c2pa_metadata, c2pa_error = self.c2pa_handler.extract(
            image_input.data, image_input.mime_type
        )

        # Extract EXIF metadata
        exif_success, exif_metadata, exif_error = self.exif_handler.extract(
            image_input.data, image_input.mime_type
        )

        # Handle errors
        if not c2pa_success or not exif_success:
            error = c2pa_error or exif_error
            return VerificationOutput(
                authenticity=AuthenticityResult(
                    probability=50, is_likely_authentic=False, confidence_level="low"
                ),
                c2pa_metadata=c2pa_metadata,
                exif_metadata=exif_metadata,
                error=error,
            )

        # Compute authenticity probability
        authenticity = self._compute_authenticity(c2pa_metadata, exif_metadata)

        return VerificationOutput(
            authenticity=authenticity,
            c2pa_metadata=c2pa_metadata,
            exif_metadata=exif_metadata,
            error=None,
        )

    def _compute_authenticity(
        self, c2pa_metadata, exif_metadata
    ) -> AuthenticityResult:
        """
        Compute authenticity probability based on metadata.

        Args:
            c2pa_metadata: C2PA metadata or None
            exif_metadata: EXIF metadata or None

        Returns:
            AuthenticityResult with probability and confidence
        """
        # Check if C2PA indicates AI generation
        is_ai_generated = c2pa_metadata is not None and c2pa_metadata.is_ai_generated()

        # Check if EXIF is present
        has_exif = exif_metadata is not None and exif_metadata.has_exif

        # Compute probability (higher = more likely non-authentic)
        if is_ai_generated:
            probability = 95
            is_likely_authentic = False
            confidence_level = "high"
        elif not has_exif and c2pa_metadata is None:
            probability = 50
            is_likely_authentic = False
            confidence_level = "low"
        elif has_exif and c2pa_metadata is None:
            probability = 10
            is_likely_authentic = True
            confidence_level = "high"
        else:
            probability = 30
            is_likely_authentic = True
            confidence_level = "medium"

        return AuthenticityResult(
            probability=probability,
            is_likely_authentic=is_likely_authentic,
            confidence_level=confidence_level,
        )
