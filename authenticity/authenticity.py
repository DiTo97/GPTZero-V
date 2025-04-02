def compute_probability(c2pa_generated: bool, exif_present: bool) -> int:
    """
    Returns an integer from 0 to 100 representing our 'best guess'
    of AI-generated probability (purely for demonstration).
    """
    if c2pa_generated:
        return 95  # If explicitly C2PA says "OpenAI", we guess high probability
    if not exif_present:
        return 50  # No C2PA, no EXIF -> ambiguous
    return 10  # EXIF present, no AI metadata -> guess it's likely real
