"""Service layer for verification logic."""

from gptzero_o import ImageInput, ImageVerifier

from gptzero_o_server.models import (
    AuthenticityResultResponse,
    C2PAMetadataResponse,
    EXIFMetadataResponse,
    SoftwareAgentResponse,
    VerifyImageResponse,
)


class VerificationService:
    """Service for image authenticity verification."""

    def __init__(self):
        """Initialize the verification service."""
        self.verifier = ImageVerifier()

    def verify_image(
        self, data: bytes, mime_type: str, filename: str | None = None
    ) -> VerifyImageResponse:
        """
        Verify image authenticity.

        Args:
            data: Image binary data
            mime_type: MIME type of the image
            filename: Optional filename

        Returns:
            VerifyImageResponse with verification results
        """
        # Create input
        image_input = ImageInput(data=data, mime_type=mime_type, filename=filename)

        # Verify
        result = self.verifier.verify(image_input)

        # Convert to API response
        authenticity = AuthenticityResultResponse(
            probability=result.authenticity.probability,
            is_likely_authentic=result.authenticity.is_likely_authentic,
            confidence_level=result.authenticity.confidence_level,
        )

        c2pa_response = None
        if result.c2pa_metadata:
            software_agents = [
                SoftwareAgentResponse(
                    name=agent.name,
                    action=agent.action,
                    formatted_action=agent.get_formatted_action(),
                )
                for agent in result.c2pa_metadata.software_agents
            ]
            c2pa_response = C2PAMetadataResponse(
                instance_id=result.c2pa_metadata.instance_id,
                title=result.c2pa_metadata.title,
                issuer=result.c2pa_metadata.issuer,
                generator_name=result.c2pa_metadata.generator_name,
                digital_source_type=result.c2pa_metadata.digital_source_type,
                software_agents=software_agents,
                is_ai_generated=result.c2pa_metadata.is_ai_generated(),
            )

        exif_response = None
        if result.exif_metadata:
            exif_response = EXIFMetadataResponse(
                has_exif=result.exif_metadata.has_exif,
                exif_version=result.exif_metadata.exif_version,
                make=result.exif_metadata.make,
                model=result.exif_metadata.model,
                software=result.exif_metadata.software,
                datetime_original=result.exif_metadata.datetime_original,
                gps_latitude=result.exif_metadata.gps_latitude,
                gps_longitude=result.exif_metadata.gps_longitude,
            )

        return VerifyImageResponse(
            authenticity=authenticity,
            c2pa_metadata=c2pa_response,
            exif_metadata=exif_response,
            has_c2pa=result.has_c2pa,
            has_exif=result.has_exif,
            error=result.error,
        )
