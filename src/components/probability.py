import plotly.graph_objects as go


def Probability(probability: int) -> tuple[str, go.Figure]:
    """
    Displays a circular widget filled based on the probability value.
    The color and text change dynamically based on the authenticity probability range.

    Args:
        probability: Integer percentage (0-100) representing non-authenticity probability

    Returns:
        Tuple containing (HTML message, Plotly figure)
    """
    # Define color based on probability range
    if probability < 30:
        color = "#4CAF50"  # Green for high authenticity
        message = "<p>This image is <strong>likely authentic</strong> with minimal signs of manipulation or AI generation.</p>"
    elif 30 <= probability < 70:
        color = "#FFC107"  # Yellow/ocra for medium probability
        message = "<p>This image has <strong>some characteristics</strong> that could indicate it's not authentic, but with <strong>significant uncertainty</strong>.</p>"
    else:
        color = "#F44336"  # Red for low authenticity
        message = "<p>This image shows <strong>strong indicators</strong> of being <strong>non-authentic</strong> (manipulated, AI-generated, or deepfake).</p>"

    values = [probability, 100 - probability]
    colors = [color, "#E0E0E0"]  # Use grey for the second segment

    # Use `hole` to create a donut-like pie chart
    fig = go.Figure(
        data=[
            go.Pie(
                values=values,
                hole=0.67,
                marker={"colors": colors},
                showlegend=False,
                hoverinfo="none",  # Disable hover text
                textinfo="none",  # Hide values text on the chart
            )
        ]
    )

    fig.update_layout(
        # Add annotations in the center of the donut pies
        annotations=[
            {
                "text": "AI",
                "x": 0.5,
                "y": 0.5,
                "font": {"size": 17.6, "color": color},
                "showarrow": False,
                "xanchor": "center",
            }
        ],
        width=200,  # Make the figure smaller
        height=200,
        margin={"l": 10, "r": 10, "t": 10, "b": 10},
    )

    # Disable modebar which contains download and fullscreen options
    fig.update_layout(
        modebar_remove=[
            "zoom",
            "pan",
            "select",
            "zoomIn",
            "zoomOut",
            "autoScale",
            "resetScale",
            "toImage",
            "lasso2d",
        ]
    )

    message = (
        f"<p style='text-decoration: underline {color};'><strong>{100 - probability}%</strong> authentic</p>"
        + message
    )

    return message, fig
