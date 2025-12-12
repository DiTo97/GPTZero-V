import streamlit as st


def Card(title: str, content: str, height: str | None = None) -> None:
    """
    Display a card with a title and content.

    Args:
        title: The card title
        content: The card content (HTML allowed)
        height: Optional fixed height for the card
    """
    height_style = f"height: {height};" if height else ""

    st.markdown(
        f"""
    <div class="card" style="{height_style}">
      <div class="card-title">{title}</div>
      <div class="card-content">{content}</div>
    </div>
    """,
        unsafe_allow_html=True,
    )
