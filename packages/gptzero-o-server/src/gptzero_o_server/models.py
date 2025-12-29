"""Pydantic models for API requests and responses."""

from typing import Any

from pydantic import BaseModel, Field


class SoftwareAgentResponse(BaseModel):
    """Software agent information in response."""

    name: str
    action: str
    formatted_action: str


class C2PAMetadataResponse(BaseModel):
    """C2PA metadata in response."""

    instance_id: str
    title: str
    issuer: str
    generator_name: str
    digital_source_type: str | None
    software_agents: list[SoftwareAgentResponse]
    is_ai_generated: bool


class EXIFMetadataResponse(BaseModel):
    """EXIF metadata in response."""

    has_exif: bool
    exif_version: str | None = None
    make: str | None = None
    model: str | None = None
    software: str | None = None
    datetime_original: str | None = None
    gps_latitude: Any | None = None
    gps_longitude: Any | None = None


class AuthenticityResultResponse(BaseModel):
    """Authenticity result in response."""

    probability: int = Field(..., ge=0, le=100, description="Non-authenticity probability (0-100)")
    is_likely_authentic: bool
    confidence_level: str = Field(..., description="Confidence level: low, medium, or high")


class VerifyImageResponse(BaseModel):
    """Response for image verification."""

    authenticity: AuthenticityResultResponse
    c2pa_metadata: C2PAMetadataResponse | None = None
    exif_metadata: EXIFMetadataResponse | None = None
    has_c2pa: bool
    has_exif: bool
    error: str | None = None


class HealthResponse(BaseModel):
    """Health check response."""

    status: str
    version: str


class ErrorResponse(BaseModel):
    """Error response."""

    detail: str
