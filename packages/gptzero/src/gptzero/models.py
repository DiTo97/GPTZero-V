"""Base models for GPTZero-V SDK."""

from dataclasses import dataclass
from enum import Enum
from typing import Any


class MediaType(str, Enum):
    """Supported media types."""

    IMAGE = "image"


class DigitalSourceType(str, Enum):
    """Digital source type classifications."""

    AI_GENERATED = "ai_generated"
    CAPTURED = "captured"
    EDITED = "edited"
    UNKNOWN = "unknown"


@dataclass
class ImageInput:
    """Input model for image verification."""

    data: bytes
    mime_type: str
    filename: str | None = None

    def validate(self) -> None:
        """Validate input data."""
        if not self.data:
            raise ValueError("Image data cannot be empty")
        if not self.mime_type:
            raise ValueError("MIME type is required")


@dataclass
class SoftwareAgent:
    """Represents a software agent that performed an action on the media."""

    name: str
    action: str

    def get_formatted_action(self) -> str:
        """Returns a human-readable description of the action."""
        if self.action == "created":
            return "The asset was created by"
        if self.action == "converted":
            return "The asset format was converted by"
        return f"{self.action} by"


@dataclass
class C2PAMetadata:
    """C2PA metadata information."""

    instance_id: str
    title: str
    issuer: str
    generator_name: str
    digital_source_type: str | None
    software_agents: list[SoftwareAgent]

    @classmethod
    def from_manifest(cls, manifest: dict[str, Any]) -> "C2PAMetadata":
        """
        Parse a C2PA manifest dictionary and extract relevant metadata.

        Supports both c2patool binary format and c2pa-python library format.

        Args:
            manifest: Dictionary containing C2PA manifest data

        Returns:
            C2PAMetadata object with parsed information
        """
        active_manifest_id = manifest.get("active_manifest")
        active_manifest = manifest.get("manifests", {}).get(active_manifest_id, {})

        # Try c2pa-python format first (simpler structure)
        if "claim_generator_info" in active_manifest and isinstance(
            active_manifest["claim_generator_info"], list
        ):
            return cls._from_c2pa_python_format(manifest, active_manifest)

        # Fall back to c2patool binary format
        return cls._from_c2patool_format(manifest, active_manifest)

    @classmethod
    def _from_c2pa_python_format(
        cls, manifest: dict[str, Any], active_manifest: dict[str, Any]
    ) -> "C2PAMetadata":
        """Parse manifest from c2pa-python library format."""
        # Extract basic metadata from active manifest
        instance_id = active_manifest.get("instance_id", "Unknown")
        title = active_manifest.get("title", "Unknown")

        # Get signature info
        signature_info = active_manifest.get("signature_info", {})
        issuer = signature_info.get("issuer", "Unknown")

        # Get claim generator info
        claim_generator_info = active_manifest.get("claim_generator_info", [])
        generator_name = "Unknown"
        if claim_generator_info and isinstance(claim_generator_info, list):
            generator_name = claim_generator_info[0].get("name", "Unknown")

        # Extract software agents and digital source type from ingredients
        software_agents: list[SoftwareAgent] = []
        digital_source_type: str | None = None

        ingredients = active_manifest.get("ingredients", [])
        for ingredient in ingredients:
            ingredient_manifest_id = ingredient.get("active_manifest")
            if ingredient_manifest_id:
                ingredient_manifest = manifest.get("manifests", {}).get(
                    ingredient_manifest_id, {}
                )

                # Look for actions in ingredient assertions
                assertions = ingredient_manifest.get("assertions", [])
                for assertion in assertions:
                    if assertion.get("label") in ("c2pa.actions", "c2pa.actions.v2"):
                        actions_data = assertion.get("data", {})
                        actions = actions_data.get("actions", [])

                        for action in actions:
                            agent_name = action.get("softwareAgent", {}).get("name")
                            if agent_name and agent_name not in [
                                sa.name for sa in software_agents
                            ]:
                                action_type = action.get("action", "").replace("c2pa.", "")
                                software_agents.append(
                                    SoftwareAgent(name=agent_name, action=action_type)
                                )

                            if "digitalSourceType" in action:
                                dst = action.get("digitalSourceType", "")
                                if "trainedAlgorithmicMedia" in dst:
                                    digital_source_type = (
                                        "This content was generated with an AI tool"
                                    )

        return cls(
            instance_id=instance_id,
            title=title,
            issuer=issuer,
            generator_name=generator_name,
            digital_source_type=digital_source_type,
            software_agents=software_agents,
        )

    @classmethod
    def _from_c2patool_format(
        cls, manifest: dict[str, Any], active_manifest: dict[str, Any]
    ) -> "C2PAMetadata":
        """
        Parse manifest from c2patool binary format (legacy).

        .. deprecated:: 0.2.0
            This method is deprecated as c2patool binary is no longer used.
            The c2pa-python library is now used for all C2PA operations.
            This method remains for backward compatibility with old manifest formats.
        """
        claim = active_manifest.get("claim", {})
        claim_generator_info = claim.get("claim_generator_info", {})
        instance_id = claim.get("instanceID", "Unknown")
        title = claim.get("dc:title", "Unknown")

        signature_info = active_manifest.get("signature", {})
        issuer = signature_info.get("issuer", "Unknown")

        assertion_store = active_manifest.get("assertion_store", {})
        assertion_manifest_id = (
            assertion_store.get("c2pa.ingredient.v3", {})
            .get("activeManifest", {})
            .get("url", "")
            .split("/")[-1]
        )

        software_agents: list[SoftwareAgent] = []
        digital_source_type: str | None = None

        assertion_manifest = manifest.get("manifests", {}).get(assertion_manifest_id, {})

        if assertion_manifest:
            assertion_assertion_store = assertion_manifest.get("assertion_store", {})

            # Extract software agents and digital source type from assertions
            actions = assertion_assertion_store.get("c2pa.actions.v2", {}).get("actions", [])
            for action in actions:
                agent_name = action.get("softwareAgent", {}).get("name")
                if agent_name and agent_name not in [sa.name for sa in software_agents]:
                    action_type = action.get("action", "").replace("c2pa.", "")
                    software_agents.append(SoftwareAgent(name=agent_name, action=action_type))

                if "digitalSourceType" in action:
                    digital_source_type = action.get("digitalSourceType", "")
                    if "trainedAlgorithmicMedia" in digital_source_type:
                        digital_source_type = "This content was generated with an AI tool"

        return cls(
            instance_id=instance_id,
            title=title,
            issuer=issuer,
            generator_name=claim_generator_info.get("name", "Unknown"),
            digital_source_type=digital_source_type,
            software_agents=software_agents,
        )

    def is_ai_generated(self) -> bool:
        """Check if metadata indicates AI generation."""
        # Check if generator name indicates AI generation
        if any(
            ai_tool in self.generator_name for ai_tool in ["ChatGPT", "DALL·E", "Dall-E", "OpenAI"]
        ):
            return True

        # Check if any software agent indicates AI generation
        for agent in self.software_agents:
            if any(
                ai_tool in agent.name for ai_tool in ["GPT-4o", "DALL-E", "DALL·E", "OpenAI API"]
            ):
                return True

        # Check if digital source type indicates AI generation
        return bool(self.digital_source_type and "AI tool" in self.digital_source_type)


@dataclass
class EXIFMetadata:
    """EXIF metadata information."""

    has_exif: bool
    exif_version: str | None = None
    make: str | None = None
    model: str | None = None
    software: str | None = None
    datetime_original: str | None = None
    gps_latitude: Any | None = None
    gps_longitude: Any | None = None

    @classmethod
    def from_exif_image(cls, exif_img: Any) -> "EXIFMetadata":
        """Create EXIFMetadata from exif.Image object."""
        return cls(
            has_exif=True,
            exif_version=getattr(exif_img, "exif_version", None),
            make=getattr(exif_img, "make", None),
            model=getattr(exif_img, "model", None),
            software=getattr(exif_img, "software", None),
            datetime_original=getattr(exif_img, "datetime_original", None),
            gps_latitude=getattr(exif_img, "gps_latitude", None),
            gps_longitude=getattr(exif_img, "gps_longitude", None),
        )


@dataclass
class AuthenticityResult:
    """Result of authenticity analysis."""

    probability: int  # 0-100, where higher means more likely non-authentic
    is_likely_authentic: bool
    confidence_level: str  # "high", "medium", "low"

    def __post_init__(self) -> None:
        """Validate probability range."""
        if not 0 <= self.probability <= 100:
            raise ValueError("Probability must be between 0 and 100")


@dataclass
class VerificationOutput:
    """Complete verification output."""

    authenticity: AuthenticityResult
    c2pa_metadata: C2PAMetadata | None
    exif_metadata: EXIFMetadata | None
    error: str | None = None

    @property
    def has_c2pa(self) -> bool:
        """Check if C2PA metadata is present."""
        return self.c2pa_metadata is not None

    @property
    def has_exif(self) -> bool:
        """Check if EXIF metadata is present."""
        return self.exif_metadata is not None and self.exif_metadata.has_exif
