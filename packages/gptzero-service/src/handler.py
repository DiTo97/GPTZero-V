"""Streamlit handler for GPTZero-V service using SDK."""

import os
import sys
from pathlib import Path

import streamlit as st


# Add SDK to path
sdk_path = Path(__file__).parent.parent.parent / "gptzero-sdk" / "src"
sys.path.insert(0, str(sdk_path))

from gptzero_sdk import GPTZeroClient  # noqa: E402

from components.card import Card  # noqa: E402
from components.probability import Probability  # noqa: E402


# Get API URL from environment or use default
API_URL = os.getenv("GPTZERO_API_URL", "http://localhost:8000")

st.set_page_config(layout="wide", page_title="GPTZero-V")


def Homepage():  # noqa: N802
    """Render the homepage with information."""
    st.markdown("""
        ### How GPTZero-V Works
        """)

    # Create three columns for the cards
    col1, col2, col3 = st.columns(3)

    # Use a fixed height for all cards to ensure consistency
    card_height = "150px"

    with col1:
        Card(
            title="1. Upload Your Image",
            content="""
            Select and upload the image you want to analyze for authenticity verification.
            """,
            height=card_height,
        )

    with col2:
        Card(
            title="2. Metadata Analysis",
            content="""
            We scan images for both Content Credentials (C2PA metadata) that indicate synthetic generation and EXIF metadata that typically exists in photos captured by physical devices.
            """,
            height=card_height,
        )

    with col3:
        Card(
            title="3. Authenticity Probability Estimation",
            content="""
            Based on the above factors, we provide a simple probability score indicating the likelihood of an image being non-authentic.
            """,
            height=card_height,
        )

    st.markdown("""
        ### Limitations

        - **Not Bulletproof**: All forms of metadata can be manipulated within images, as well as deducted by simply uploading onto
          social media platforms or taking screenshots. However, ensuring compliance with such metadata is already a great initial
          filtering step in verification workflows.

        - **Incomplete Coverage**: This tool currently focuses primarily on metadata verification. Other techniques such as
          Google's [SynthID](https://deepmind.google/technologies/synthid/) and other image generation platforms outside of OpenAI are not covered, although many might become
          C2PA compliant in the future. Additionally, other authenticity verification systems like watermarking and
          blockchain verification are not supported.

        - **Call to Action**: With the increasing sophistication of media manipulation techniques, more structured efforts towards
          media authenticity verification must be enforced. We hope this tool raises awareness and sparks further discussion
          in the community.
        """)


def Authenticity():  # noqa: N802
    """Render the authenticity verification interface."""
    # Create two columns for side-by-side layout
    col1, col2 = st.columns(2)  # Equal width columns

    # First column for file uploader and image
    with col1:
        subcc = st.columns([1, 4, 1])
        with subcc[1]:
            uploaded_file = st.file_uploader(
                "Choose an image for authenticity analysis",
                type=["jpg", "jpeg", "png"],
                accept_multiple_files=False,
            )

            if uploaded_file is not None:
                file_bytes = uploaded_file.read()
                st.image(file_bytes, caption="", width="content")

    # Second column for analysis cards
    with col2:
        if uploaded_file is not None:
            try:
                # Create SDK client and verify image
                client = GPTZeroClient(base_url=API_URL)
                result = client.verify_image(
                    file_data=file_bytes,
                    filename=uploaded_file.name,
                )
                client.close()

                if result.error:
                    Card(
                        title="Image Authenticity",
                        content=f"<p><strong>Unknown</strong> authenticity status due to: {result.error}</p>",
                    )
                else:
                    # Show Authenticity Probability Circular Widget
                    message, fig = Probability(result.authenticity.probability)

                    # Create nested columns to center the chart
                    _, center_col, _ = st.columns([1, 1, 1])
                    with center_col:
                        st.plotly_chart(
                            fig, use_container_width=True, config={"displayModeBar": False}
                        )

                    Card(title="Image Authenticity", content=message)

                subcolumns = st.columns(2)

                with subcolumns[0]:
                    # If C2PA is present, show its card
                    if result.c2pa_metadata and not result.error:
                        c2pa = result.c2pa_metadata
                        # Create HTML content for the card
                        c2pa_content = "<div class='card-title'>Claim</div><ul>"

                        # Add generators
                        c2pa_content += f"<li><strong>ID:</strong> {c2pa.instance_id}</li>"
                        c2pa_content += (
                            f"<li><strong>generated by:</strong> {c2pa.generator_name}</li>"
                        )
                        c2pa_content += f"<li><strong>title:</strong> {c2pa.title}</li>"
                        c2pa_content += "</ul>"

                        c2pa_content += "<div class='card-title'>Process</div>"

                        # Add source type if available
                        if c2pa.digital_source_type:
                            c2pa_content += c2pa.digital_source_type

                        if c2pa.software_agents:
                            c2pa_content += ":<ul>"
                            # Add software agents
                            for agent in c2pa.software_agents:
                                c2pa_content += f"<li><strong>{agent.formatted_action}</strong> {agent.name}</li>"
                            c2pa_content += "</ul>"
                        else:
                            c2pa_content += "."

                        # Add credential info
                        c2pa_content += (
                            "<div class='card-title'>About this Content Credential</div><ul>"
                        )
                        c2pa_content += f"<li><strong>issued by:</strong> {c2pa.issuer}</li>"
                        c2pa_content += "</ul>"

                        c2pa_content += "For more information, visit C2PA <a href='https://contentcredentials.org/verify'>Verify</a>."

                        # Use the card function to display the information
                        Card("C2PA Metadata", c2pa_content)

                    elif result.error:
                        Card("C2PA Metadata", f"<p>{result.error}</p>")
                    else:
                        Card("C2PA Metadata", "<p>No C2PA metadata found.</p>")

                with subcolumns[1]:
                    # If EXIF is present, show an EXIF card with a few interesting fields
                    if result.has_exif and result.exif_metadata:
                        exif = result.exif_metadata
                        # Gather some typical fields
                        exif_fields_of_interest = [
                            ("version", exif.exif_version),
                            ("device make", exif.make),
                            ("device model", exif.model),
                            ("OS", exif.software),
                            ("taken at", exif.datetime_original),
                            ("GPS latitude", exif.gps_latitude),
                            ("GPS longitude", exif.gps_longitude),
                        ]

                        exif_content = "<ul>"
                        for label, value in exif_fields_of_interest:
                            if value is not None:
                                exif_content += f"<li><strong>{label}:</strong> {value}</li>"
                        exif_content += "</ul>"

                        Card("EXIF Metadata", exif_content)
                    else:
                        Card("EXIF Metadata", "<p>No EXIF metadata found.</p>")

            except Exception as e:
                st.error(f"Error verifying image: {str(e)}")
                st.info(f"Make sure the API is running at {API_URL}")


def main() -> None:
    """Main function to run the Streamlit app."""
    # Inject some CSS to mimic "shadcn card" style
    st.markdown(
        """
    <style>
    .card {
      background-color: #fff;
      border: 1px solid rgba(0,0,0,0.08);
      border-radius: 8px;
      padding: 16px;
      margin-bottom: 16px;
      box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    .card-title {
      font-size: 1.1rem;
      font-weight: 600;
      margin-bottom: 8px;
      color: #000;
    }
    .card-content {
      font-size: 0.95rem;
      color: #000;
    }
    </style>
    """,
        unsafe_allow_html=True,
    )

    st.title("GPTZero-V")
    st.write("""
    This Streamlit app is designed to verify image authenticity through metadata analysis, helping to identify
    manipulated or synthetic images (including AI-generated content, deepfakes, and screenshots).
    """)

    # Create tabs for different sections
    tab1, tab2 = st.tabs(["How It Works", "Image Authenticity Verification"])

    with tab1:
        Homepage()

    with tab2:
        Authenticity()


if __name__ == "__main__":
    main()
