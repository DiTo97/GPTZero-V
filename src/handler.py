import streamlit as st

from authenticity.authenticity import compute_probability
from authenticity.c2pa_handler import c2pa_check_from_binary
from authenticity.exif_handler import check_exif
from authenticity.metadata_utils import get_c2pa_binary_path
from components.card import Card
from components.probability import Probability


st.set_page_config(layout="wide", page_title="GPTZero-V")

# Get the binary path
binary_path = get_c2pa_binary_path()


def Homepage():
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


def Authenticity():
    if binary_path is None:
        st.error(
            "c2patool binary is missing. Please ensure the tool is available in the resources directory."
        )
    else:
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
                    # Get the MIME type of the uploaded file
                    mime_type = uploaded_file.type
                    st.image(file_bytes, caption="", use_container_width=True)

        # Second column for analysis cards
        with col2:
            if uploaded_file is not None:
                # 1) Check C2PA with the detected MIME type
                c2pa_generated, c2pa_metadata, c2pa_error = c2pa_check_from_binary(
                    file_bytes, mime_type
                )

                # 2) Check EXIF with the detected MIME type
                exif_present, exif_data = check_exif(file_bytes)

                if c2pa_error:
                    Card(
                        title="Image Authenticity",
                        content=f"<p><strong>Unknown</strong> authenticity status due to metadata parsing errors.</p>",
                    )
                else:
                    # 3) Compute authenticity probability
                    authenticity_probability = compute_probability(c2pa_generated, exif_present)

                    # Show Authenticity Probability Circular Widget
                    message, fig = Probability(authenticity_probability)

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
                    if c2pa_metadata and not c2pa_error:
                        # Create HTML content for the card
                        c2pa_content = "<div class='card-title'>Claim</div><ul>"

                        # Add generators
                        c2pa_content += f"<li><strong>ID:</strong> {c2pa_metadata.instance_id}</li>"
                        c2pa_content += f"<li><strong>generated by:</strong> {c2pa_metadata.generator_name}</li>"
                        c2pa_content += f"<li><strong>title:</strong> {c2pa_metadata.title}</li>"
                        c2pa_content += "</ul>"

                        c2pa_content += "<div class='card-title'>Process</div>"

                        # Add source type if available
                        if c2pa_metadata.digital_source_type:
                            c2pa_content += c2pa_metadata.digital_source_type

                        if c2pa_metadata.software_agents:
                            c2pa_content += ":<ul>"
                            # Add software agents
                            for agent in c2pa_metadata.software_agents:
                                formatted_action = agent.get_formatted_action()
                                c2pa_content += (
                                    f"<li><strong>{formatted_action}</strong> {agent.name}</li>"
                                )
                            c2pa_content += "</ul>"
                        else:
                            c2pa_content += "."

                        # Add credential info
                        c2pa_content += (
                            "<div class='card-title'>About this Content Credential</div><ul>"
                        )
                        c2pa_content += (
                            f"<li><strong>issued by:</strong> {c2pa_metadata.issuer}</li>"
                        )
                        c2pa_content += "</ul>"

                        c2pa_content += "For more information, visit C2PA <a href='https://contentcredentials.org/verify'>Verify</a>."

                        # Use the card function to display the information
                        Card("C2PA Metadata", c2pa_content)

                    elif c2pa_error:
                        Card("C2PA Metadata", f"<p>{c2pa_error}</p>")
                    else:
                        Card("C2PA Metadata", f"<p>No C2PA metadata found.</p>")

                with subcolumns[1]:
                    # If EXIF is present, show an EXIF card with a few interesting fields
                    if exif_present:
                        # Gather some typical fields
                        exif_fields_of_interest = [
                            ("version", getattr(exif_data, "exif_version", None)),
                            ("device make", getattr(exif_data, "make", None)),
                            ("device model", getattr(exif_data, "model", None)),
                            ("OS", getattr(exif_data, "software", None)),
                            (
                                "taken at",
                                getattr(exif_data, "datetime_original", None),
                            ),
                            ("GPS latitude", getattr(exif_data, "gps_latitude", None)),
                            ("GPS longitude", getattr(exif_data, "gps_longitude", None)),
                        ]

                        exif_content = "<ul>"
                        for label, value in exif_fields_of_interest:
                            if value is not None:
                                exif_content += f"<li><strong>{label}:</strong> {value}</li>"
                        exif_content += "</ul>"

                        Card("EXIF Metadata", exif_content)
                    else:
                        Card("EXIF Metadata", "<p>No EXIF metadata found.</p>")


def main() -> None:
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
