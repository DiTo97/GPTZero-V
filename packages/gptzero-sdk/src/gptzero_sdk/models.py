"""Models for SDK responses."""

from typing import Any

from pydantic import BaseModel


class SoftwareAgent(BaseModel):
    """Software agent information."""

    name: str
    action: str
    formatted_action: str


class C2PAMetadata(BaseModel):
    """C2PA metadata."""

    instance_id: str
    title: str
    issuer: str
    generator_name: str
    digital_source_type: str | None
    software_agents: list[SoftwareAgent]
    is_ai_generated: bool


class EXIFMetadata(BaseModel):
    """EXIF metadata."""

    has_exif: bool
    exif_version: str | None = None
    make: str | None = None
    model: str | None = None
    software: str | None = None
    datetime_original: str | None = None
    gps_latitude: Any | None = None
    gps_longitude: Any | None = None


class AuthenticityResult(BaseModel):
    """Authenticity result."""

    probability: int
    is_likely_authentic: bool
    confidence_level: str


class VerifyImageResponse(BaseModel):
    """Response for image verification."""

    authenticity: AuthenticityResult
    c2pa_metadata: C2PAMetadata | None = None
    exif_metadata: EXIFMetadata | None = None
    has_c2pa: bool
    has_exif: bool
    error: str | None = None


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str
