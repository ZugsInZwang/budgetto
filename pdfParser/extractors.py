import pdfplumber

# ------------------------------------------------------------
# HELPER 1: GROUP WORDS INTO TEXT LINES
# ------------------------------------------------------------
def extract_text_lines(page, tolerance=3):
    """
    Extract text lines with y-coordinates.
    Groups words whose 'top' coordinate is close.
    Returns: list of dicts: {type: 'text', y: y, content: '...'}
    """
    words = page.extract_words()

    # Sort by vertical then left coordinate
    words.sort(key=lambda w: (w['top'], w['x0']))

    lines = []
    current_line_words = []
    current_y = None

    for w in words:
        if current_y is None:
            # First line
            current_y = w['top']
            current_line_words = [w]
            continue

        if abs(w['top'] - current_y) <= tolerance:
            # Same line
            current_line_words.append(w)
        else:
            # Commit previous line
            text = " ".join([cw['text'] for cw in current_line_words])
            lines.append({
                "type": "text",
                "y": current_y,
                "content": text
            })
            # Start new line
            current_line_words = [w]
            current_y = w['top']

    # Commit final line
    if current_line_words:
        text = " ".join([cw['text'] for cw in current_line_words])
        lines.append({
            "type": "text",
            "y": current_y,
            "content": text
        })

    return lines


# ------------------------------------------------------------
# HELPER 2: EXTRACT TABLES + coordinates
# ------------------------------------------------------------
def extract_tables_with_coords(page):
    """
    Uses pdfplumber's more advanced table detection (find_tables).
    Returns tables with their y coordinate.
    """
    output = []
    for table in page.find_tables():
        extracted = table.extract()
        if extracted:
            output.append({
                "type": "table",
                "y": table.bbox[1],
                "content": extracted
            })
    return output
