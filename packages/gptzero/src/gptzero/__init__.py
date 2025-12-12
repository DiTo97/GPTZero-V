"""GPTZero - Image Authenticity Verification SDK."""

from gptzero.models import (
    AuthenticityResult,
    C2PAMetadata,
    EXIFMetadata,
    ImageInput,
    SoftwareAgent,
    VerificationOutput,
)
from gptzero.verification import ImageVerifier

__version__ = "0.1.0"

__all__ = [
    "AuthenticityResult",
    "C2PAMetadata",
    "EXIFMetadata",
    "ImageInput",
    "ImageVerifier",
    "SoftwareAgent",
    "VerificationOutput",
]
