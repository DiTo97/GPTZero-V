# GPTZero SDK

Python SDK client for interacting with the GPTZero API.

## Features

- **Sync & Async Support**: Use httpx for both synchronous and asynchronous requests
- **Type Safety**: Full type hints with Pydantic models
- **Easy to Use**: Simple, intuitive API
- **Context Managers**: Proper resource management

## Installation

```bash
pip install gptzero-sdk
```

## Usage

### Synchronous

```python
from gptzero_sdk import GPTZeroClient

# Create client
client = GPTZeroClient(base_url="http://localhost:8000")

# Check health
health = client.health()
print(f"Status: {health.status}")

# Verify image from file path
result = client.verify_image(file_path="image.jpg")
print(f"Authenticity: {result.authenticity.probability}%")

# Verify image from bytes
with open("image.jpg", "rb") as f:
    data = f.read()
result = client.verify_image(file_data=data, filename="image.jpg")

# Close client
client.close()
```

### Asynchronous

```python
import asyncio
from gptzero_sdk import GPTZeroClient

async def verify():
    client = GPTZeroClient(base_url="http://localhost:8000")
    
    # Check health
    health = await client.health_async()
    print(f"Status: {health.status}")
    
    # Verify image
    result = await client.verify_image_async(file_path="image.jpg")
    print(f"Authenticity: {result.authenticity.probability}%")
    
    await client.aclose()

asyncio.run(verify())
```

### Context Manager

```python
from gptzero_sdk import GPTZeroClient

# Sync context manager
with GPTZeroClient(base_url="http://localhost:8000") as client:
    result = client.verify_image(file_path="image.jpg")
    print(result.authenticity.probability)

# Async context manager
async with GPTZeroClient(base_url="http://localhost:8000") as client:
    result = await client.verify_image_async(file_path="image.jpg")
    print(result.authenticity.probability)
```

## Response Format

```python
result = client.verify_image(file_path="image.jpg")

# Access authenticity info
print(result.authenticity.probability)  # 0-100
print(result.authenticity.is_likely_authentic)  # bool
print(result.authenticity.confidence_level)  # "low", "medium", "high"

# Check metadata presence
print(result.has_c2pa)  # bool
print(result.has_exif)  # bool

# Access metadata if present
if result.c2pa_metadata:
    print(result.c2pa_metadata.generator_name)
    print(result.c2pa_metadata.is_ai_generated)

if result.exif_metadata:
    print(result.exif_metadata.make)
    print(result.exif_metadata.model)
```

## Development

```bash
# Install development dependencies
pip install -e ".[dev]"

# Run tests
pytest
```

## License

MIT License
