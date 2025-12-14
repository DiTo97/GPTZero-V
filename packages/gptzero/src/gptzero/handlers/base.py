"""Base handler interface."""

from abc import ABC, abstractmethod
from typing import Any


class MetadataHandler(ABC):
    """Abstract base class for metadata handlers."""

    @abstractmethod
    def extract(self, data: bytes, mime_type: str) -> tuple[bool, Any | None, str | None]:
        """
        Extract metadata from media data.

        Args:
            data: Binary data of the media
            mime_type: MIME type of the media

        Returns:
            Tuple of (success, metadata, error_message)
        """
        pass
