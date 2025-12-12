# GPTZero-V SDK

Python SDK for image authenticity verification through metadata analysis.

## Features

- **C2PA Metadata Analysis**: Extract and analyze Content Credentials
- **EXIF Metadata Extraction**: Check for device capture metadata
- **Authenticity Scoring**: Heuristic-based authenticity probability
- **Extensible Design**: SOLID principles for future media types

## Installation

```bash
pip install gptzero
```

## Usage

```python
from gptzero import ImageVerifier, ImageInput

# Initialize verifier
verifier = ImageVerifier()

# Load image
with open("image.jpg", "rb") as f:
    image_data = f.read()

# Create input
image_input = ImageInput(
    data=image_data,
    mime_type="image/jpeg",
    filename="image.jpg"
)

# Verify authenticity
result = verifier.verify(image_input)

print(f"Authenticity probability: {result.authenticity.probability}%")
print(f"Is likely authentic: {result.authenticity.is_likely_authentic}")
print(f"Has C2PA: {result.has_c2pa}")
print(f"Has EXIF: {result.has_exif}")
```

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
ruff check src/ tests/
```

## License

MIT License
