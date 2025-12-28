# GPTZero-V

A comprehensive image authenticity verification system through metadata analysis.

![GIF](static/GPTZero-V.gif)

## 🔍 Overview

With the proliferation of manipulated, edited, and synthetic imagery, determining the authenticity of digital media has become increasingly challenging. GPTZero-V is a modular system that helps assess an image's authenticity by analyzing its metadata, checking for:

- **C2PA Metadata**: Content providers, including AI image generation providers like OpenAI, are leveraging the C2PA standard for content authenticity and provenance tracking.
- **EXIF Metadata**: Presence of consistent and valid EXIF data typically suggests the image was captured by a physical device.
- **Authenticity Probability Score**: A heuristic estimate (0-100%) of the likelihood that an image is non-authentic.

## 📦 Package Structure

GPTZero-V has been restructured into four modular packages:

### 1. **gptzero** - Core SDK
Python SDK for image authenticity verification with structured base models, following DRY and SOLID patterns.

- 📁 Location: `packages/gptzero/`
- 🔧 Features: C2PA/EXIF handlers, base models, verification logic
- 📊 Test Coverage: 71% (32 tests passing)
- 📚 [Documentation](packages/gptzero/README.md)

### 2. **gptzero-api** - FastAPI Service
RESTful API service exposing authenticity verification endpoints.

- 📁 Location: `packages/gptzero-api/`
- 🔧 Features: FastAPI application, Pydantic models, middleware, CORS support
- 🌐 Default Port: 8000
- 📚 [Documentation](packages/gptzero-api/README.md)

### 3. **gptzero-sdk** - Python Client
Python SDK client for interacting with the GPTZero API.

- 📁 Location: `packages/gptzero-sdk/`
- 🔧 Features: Sync/async httpx client, type-safe models, context managers
- 📚 [Documentation](packages/gptzero-sdk/README.md)

### 4. **gptzero-service** - Streamlit Frontend
Interactive web interface for image authenticity verification.

- 📁 Location: `packages/gptzero-service/`
- 🔧 Features: Streamlit UI, visual feedback, SDK integration
- 🌐 Default Port: 8501
- 📚 [Documentation](packages/gptzero-service/README.md)

## 🚀 Installation

### Using Docker (Recommended)

The Docker image runs both the API and the service from the same container:

```bash
# Build the image
docker build -t gptzero-v:0.1 .

# Run both API (port 8000) and Service (port 8501)
docker run -p 8000:8000 -p 8501:8501 gptzero-v:0.1
```

Access the services:
- **API Documentation**: http://localhost:8000/docs
- **Web Interface**: http://localhost:8501

### Local Installation with uv

```bash
# Clone the repository
git clone https://github.com/DiTo97/GPTZero-V.git
cd GPTZero-V

# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Install all packages using uv workspace
uv sync --all-packages

# For development (includes pytest, ruff, etc.)
uv sync --all-packages --group dev
```

### Running Services Locally

```bash
# Terminal 1: Start the API
uv run --package gptzero-api gptzero-api

# Terminal 2: Start the Service
export GPTZERO_API_URL=http://localhost:8000
uv run --package gptzero-service streamlit run packages/gptzero-service/src/handler.py
```

## 💻 Usage Examples

### Core SDK

```python
from gptzero import ImageVerifier, ImageInput

verifier = ImageVerifier()

with open("image.jpg", "rb") as f:
    data = f.read()

result = verifier.verify(ImageInput(
    data=data,
    mime_type="image/jpeg",
    filename="image.jpg"
))

print(f"Authenticity: {result.authenticity.probability}%")
print(f"Has C2PA: {result.has_c2pa}")
print(f"Has EXIF: {result.has_exif}")
```

### API Client

```python
from gptzero_sdk import GPTZeroClient

with GPTZeroClient(base_url="http://localhost:8000") as client:
    result = client.verify_image(file_path="image.jpg")
    print(f"Authenticity: {result.authenticity.probability}%")
```

### API Endpoints

```bash
# Health check
curl http://localhost:8000/health

# Verify image
curl -X POST "http://localhost:8000/v1/verify" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@image.jpg"
```

## 🧪 Testing

Run the test suite:

```bash
# Test core SDK
cd packages/gptzero
pytest tests/ -v --cov=gptzero

# Lint all packages
cd packages/gptzero && ruff check src/ tests/ && cd ../..
cd packages/gptzero-api && ruff check src/ && cd ../..
cd packages/gptzero-sdk && ruff check src/ && cd ../..
cd packages/gptzero-service && ruff check src/ && cd ../..
```

## 🔄 CI/CD

GitHub Actions workflow runs automatically on:
- Push to `main` branch
- Pull request events

The workflow includes:
- Unit tests with coverage reporting
- Linting for all packages
- Multi-package validation

## ⚠️ Limitations

- **Metadata can be manipulated or stripped**, reducing reliability as the sole authenticity measure.
- **Not all authenticity markers are covered** (e.g., digital signatures, blockchain verification, watermarking).
- **Authenticity probability is heuristic**, meant for demonstration purposes only.
- **Various types of non-authentic content exist** beyond AI-generated imagery.
- **Metadata analysis alone is insufficient** for comprehensive authenticity verification.

## 🏗️ Architecture

```
┌─────────────────────────────────────────────┐
│         gptzero-service (Streamlit)         │
│              Port 8501                      │
└────────────────┬────────────────────────────┘
                 │
                 │ SDK Client
                 ▼
┌─────────────────────────────────────────────┐
│          gptzero-api (FastAPI)              │
│              Port 8000                      │
└────────────────┬────────────────────────────┘
                 │
                 │ Uses
                 ▼
┌─────────────────────────────────────────────┐
│           gptzero (Core SDK)                │
│   - Models & Handlers                       │
│   - C2PA/EXIF Extraction                    │
│   - Verification Logic                      │
└─────────────────────────────────────────────┘
```

## 🤝 Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository
2. Create a feature branch
3. Make your changes with tests
4. Ensure all tests pass and linting is clean
5. Submit a pull request

```bash
# Install development dependencies
cd packages/gptzero
pip install -e ".[dev]"

# Run tests before committing
pytest tests/ -v
ruff check src/ tests/
```

## 🔗 License

See the [LICENSE](LICENSE) file for details.

## 📢 Call to Action

As digital content manipulation becomes more sophisticated, it is crucial to implement stronger verification methods across the ecosystem. Metadata analysis is just one piece of a larger authenticity verification puzzle. Future efforts should integrate multiple approaches including cryptographic verification, provenance tracking, and standardizing authenticity indicators at an industry-wide level.
