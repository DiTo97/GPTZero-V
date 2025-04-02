# GPTZero-V

A simple attempt at a heuristic GPTZero algorithm for image authenticity verification through metadata analysis.

![GIF](static/GPTZero-V.gif)

## 🔍 overview

With the proliferation of manipulated, edited, and synthetic imagery, determining the authenticity of digital media has become increasingly challenging. This includes AI-generated content, deepfakes, and other forms of manipulated media. This Streamlit app helps assess an image's authenticity by analyzing its metadata, checking for:

- **C2PA Metadata**: Content providers, including AI image generation providers like OpenAI, are leveraging the C2PA standard for content authenticity and provenance tracking. The presence and content of C2PA data can indicate whether an image has been modified or synthetically generated.
- **EXIF Metadata**: Presence of consistent and valid EXIF data typically suggests the image was captured by a physical device, though this can be manipulated.
- **Authenticity Probability Score**: A heuristic estimate (0-100%) of the likelihood that an image is non-authentic, based on combined metadata findings.

This project explores a metadata-based approach to authenticity verification, complementary to detection methods from visual cues. The goal is to raise awareness about media integrity and encourage more robust authentication mechanisms.

## 🚀 usage

ensure you have uv as package manager. Then run:

```shell
uv run streamlit run app.py
```

Alternatively, it is available on Streamlit Cloud, at [gptzero-v.streamlit.app](https://gptzero-v.streamlit.app).

## ⚠️ limitations

- **Metadata can be manipulated or stripped**, reducing reliability as the sole authenticity measure.
- **Not all authenticity markers are covered** (e.g., digital signatures, blockchain verification, watermarking).
- **Authenticity probability is heuristic**, meant for demonstration purposes only.
- **Various types of non-authentic content exist** beyond AI-generated imagery, including edited photos, composites, deepfakes, and more.
- **Metadata analysis alone is insufficient** for comprehensive authenticity verification.

## 🤝 contributing

Contributions to **GPTZero-V** are welcome! Fork the repository, create a branch for your feature or bug fix, write tests to cover your changes, and submit a pull request.

```bash
git clone https://github.com/DiTo97/GPTZero-V.git
cd GPTZero-V
uv sync --all-extras
```

## 🔗 license

See the [LICENSE](LICENSE) file for more details.

## 📢 call to action

As digital content manipulation becomes more sophisticated, it is crucial to implement stronger verification methods across the ecosystem. Metadata analysis is just one piece of a larger authenticity verification puzzle. Future efforts should integrate multiple approaches including cryptographic verification, provenance tracking, and standardizing authenticity indicators at an industry-wide level.
