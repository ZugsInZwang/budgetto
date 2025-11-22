import pdfplumber
import re


# ------------------------------------------------------------
# HELPER 3: Identify SD / PO / OD
# ------------------------------------------------------------
def detect_identifier(text):
    m = re.search(r"\b(SD|PO|OD)\s?(\d{5})\b", text)
    if m:
        return m.group(1) + m.group(2)
    return None

def is_footer_or_page_number(text):
    footer_text = "OCMW Gent - Stad Gent / MJP 2026 - 2031"
    footer_match = re.search(footer_text, text)
    if footer_match:
        return True
    page_number_match = re.search(r"^\d+$", text)
    if page_number_match:
        return True
    return False


# ------------------------------------------------------------
# TABLE TYPE DETECTORS
# ------------------------------------------------------------
def is_budget_table(tbl):
    if len(tbl) < 2: return False
    header = " ".join(cell or "" for cell in tbl[1]).lower()
    return ("eur" in header) and any(yr in header for yr in ["2026","2027","2028","2029","2030","2031"])


def is_vte_table(tbl):
    if len(tbl) < 2: return False
    header = " ".join(cell or "" for cell in tbl[1]).lower()
    return ("vte" in header) and any(yr in header for yr in ["2026","2027"])


def looks_like_actions_table(tbl):
    # usually the first column contains PRxxxxx ACxxxxx etc.
    first_col_text = " ".join((row[0] or "") for row in tbl if row and len(row) > 0)
    return bool(re.search(r"\b(AC|PR|PRB|ACB)\d+", first_col_text))

