# GPTZero-V Service

Streamlit frontend for GPTZero-V image authenticity verification.

## Features

- **Interactive UI**: User-friendly Streamlit interface
- **Real-time Analysis**: Upload and analyze images instantly
- **Visual Feedback**: Charts and cards for easy interpretation
- **SDK-based**: Uses gptzero-sdk to communicate with the API

## Installation

```bash
pip install gptzero-service
```

## Usage

### Running the Service

```bash
# Set API URL (optional, defaults to http://localhost:8000)
export GPTZERO_API_URL=http://localhost:8000

# Run Streamlit app
streamlit run handler.py
```

Or directly with the package:

```bash
streamlit run packages/gptzero-service/src/handler.py
```

### Configuration

Set the `GPTZERO_API_URL` environment variable to point to your GPTZero-V API instance:

```bash
export GPTZERO_API_URL=http://api.example.com:8000
```

## Development

The service maintains full feature parity with the original monolithic application while using the SDK for backend communication.

## License

MIT License
