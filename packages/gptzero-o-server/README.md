# GPTZero-o API

FastAPI service for media content authenticity verification.

## Features

- **RESTful API**: Clean, well-documented REST endpoints
- **Async Support**: Built on FastAPI for high performance
- **CORS Enabled**: Ready for cross-origin requests
- **Request Logging**: Structured logging with timing information
- **Health Check**: Endpoint for monitoring service health

## Installation

```bash
pip install gptzero-o-server
```

## Usage

### Running the API

```bash
uvicorn gptzero_api.api:app --host 0.0.0.0 --port 8000
```

### API Endpoints

#### Health Check
```
GET /health
```

#### Verify Image
```
POST /v1/verify
Content-Type: multipart/form-data

file: [image file]
```

### Example with curl

```bash
curl -X POST "http://localhost:8000/v1/verify" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/image.jpg"
```

### Response Format

```json
{
  "authenticity": {
    "probability": 10,
    "is_likely_authentic": true,
    "confidence_level": "high"
  },
  "has_c2pa": false,
  "has_exif": true,
  "exif_metadata": {
    "has_exif": true,
    "make": "Canon",
    "model": "EOS 5D"
  },
  "c2pa_metadata": null,
  "error": null
}
```

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run with auto-reload
uvicorn gptzero_api.api:app --reload
```

## License

MIT License
