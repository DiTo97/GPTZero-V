"""GPTZero-V SDK Client."""

from pathlib import Path
from typing import BinaryIO

import httpx

from gptzero_sdk.models import HealthResponse, VerifyImageResponse


class GPTZeroClient:
    """Client for GPTZero-V API."""

    def __init__(self, base_url: str = "http://localhost:8000", timeout: float = 30.0):
        """
        Initialize the GPTZero-V client.

        Args:
            base_url: Base URL of the GPTZero-V API
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._sync_client: httpx.Client | None = None
        self._async_client: httpx.AsyncClient | None = None

    @property
    def sync_client(self) -> httpx.Client:
        """Get or create sync HTTP client."""
        if self._sync_client is None:
            self._sync_client = httpx.Client(
                base_url=self.base_url,
                timeout=self.timeout,
            )
        return self._sync_client

    @property
    def async_client(self) -> httpx.AsyncClient:
        """Get or create async HTTP client."""
        if self._async_client is None:
            self._async_client = httpx.AsyncClient(
                base_url=self.base_url,
                timeout=self.timeout,
            )
        return self._async_client

    def health(self) -> HealthResponse:
        """
        Check API health (sync).

        Returns:
            HealthResponse with status and version
        """
        response = self.sync_client.get("/health")
        response.raise_for_status()
        return HealthResponse(**response.json())

    async def health_async(self) -> HealthResponse:
        """
        Check API health (async).

        Returns:
            HealthResponse with status and version
        """
        response = await self.async_client.get("/health")
        response.raise_for_status()
        return HealthResponse(**response.json())

    def verify_image(
        self,
        file_path: str | Path | None = None,
        file_data: bytes | None = None,
        file_obj: BinaryIO | None = None,
        filename: str | None = None,
    ) -> VerifyImageResponse:
        """
        Verify image authenticity (sync).

        Provide exactly one of: file_path, file_data, or file_obj.

        Args:
            file_path: Path to image file
            file_data: Binary image data
            file_obj: File-like object
            filename: Optional filename (required if using file_data or file_obj)

        Returns:
            VerifyImageResponse with verification results

        Raises:
            ValueError: If arguments are invalid
            httpx.HTTPStatusError: If API returns error status
        """
        files = self._prepare_file(file_path, file_data, file_obj, filename)

        response = self.sync_client.post("/v1/verify", files=files)
        response.raise_for_status()
        return VerifyImageResponse(**response.json())

    async def verify_image_async(
        self,
        file_path: str | Path | None = None,
        file_data: bytes | None = None,
        file_obj: BinaryIO | None = None,
        filename: str | None = None,
    ) -> VerifyImageResponse:
        """
        Verify image authenticity (async).

        Provide exactly one of: file_path, file_data, or file_obj.

        Args:
            file_path: Path to image file
            file_data: Binary image data
            file_obj: File-like object
            filename: Optional filename (required if using file_data or file_obj)

        Returns:
            VerifyImageResponse with verification results

        Raises:
            ValueError: If arguments are invalid
            httpx.HTTPStatusError: If API returns error status
        """
        files = self._prepare_file(file_path, file_data, file_obj, filename)

        response = await self.async_client.post("/v1/verify", files=files)
        response.raise_for_status()
        return VerifyImageResponse(**response.json())

    def _prepare_file(
        self,
        file_path: str | Path | None,
        file_data: bytes | None,
        file_obj: BinaryIO | None,
        filename: str | None,
    ) -> dict:
        """Prepare file for upload."""
        provided = sum([file_path is not None, file_data is not None, file_obj is not None])

        if provided == 0:
            raise ValueError("Must provide one of: file_path, file_data, or file_obj")
        if provided > 1:
            raise ValueError("Must provide exactly one of: file_path, file_data, or file_obj")

        if file_path is not None:
            path = Path(file_path)
            with open(path, "rb") as f:
                file_data = f.read()
            return {"file": (path.name, file_data, self._guess_mime_type(path))}

        if file_data is not None:
            if filename is None:
                raise ValueError("filename is required when using file_data")
            return {"file": (filename, file_data, self._guess_mime_type_from_name(filename))}

        if file_obj is not None:
            if filename is None:
                raise ValueError("filename is required when using file_obj")
            return {"file": (filename, file_obj, self._guess_mime_type_from_name(filename))}

        raise ValueError("Invalid file parameters")

    def _guess_mime_type(self, path: Path) -> str:
        """Guess MIME type from file path."""
        return self._guess_mime_type_from_name(path.name)

    def _guess_mime_type_from_name(self, filename: str) -> str:
        """Guess MIME type from filename."""
        ext = filename.lower().split(".")[-1]
        mime_map = {
            "jpg": "image/jpeg",
            "jpeg": "image/jpeg",
            "png": "image/png",
            "gif": "image/gif",
            "bmp": "image/bmp",
            "webp": "image/webp",
            "tiff": "image/tiff",
            "tif": "image/tiff",
        }
        return mime_map.get(ext, "application/octet-stream")

    def close(self) -> None:
        """Close sync client."""
        if self._sync_client is not None:
            self._sync_client.close()
            self._sync_client = None

    async def aclose(self) -> None:
        """Close async client."""
        if self._async_client is not None:
            await self._async_client.aclose()
            self._async_client = None

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.aclose()
