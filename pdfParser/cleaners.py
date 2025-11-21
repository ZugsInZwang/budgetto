import pdfplumber
import re
import json


# ------------------------------------------------------------
# TABLE CLEANERS
# ------------------------------------------------------------

def clean_numeric_table(tbl):
    """
    Given a raw table extracted by pdfplumber:
    - Remove header row
    - Remove first column
    - Convert European number formatting ("1.234,56") to float
    """
    cleaned = []

    # Remove header row (row 0)
    for row in tbl[1:]:
        # Remove first column
        row = row[1:]        

        new_row = []
        for cell in row:
            if cell is None:
                new_row.append(None)
                continue

            cell = cell.strip()

            # Convert European number format to float
            if re.match(r"^[\d\.\,]+$", cell):
                # remove thousands separator '.', convert ',' to '.'
                num = cell.replace(".", "").replace(",", ".")
                try:
                    new_row.append(float(num))
                except ValueError:
                    new_row.append(cell)
            else:
                new_row.append(cell)

        cleaned.append(new_row)

    return cleaned


def convert_vte_table(tbl):
    """
    tbl = [
        [years...],
        [vte...]
    ]
    Returns dict with keys: years, vte
    """
    if len(tbl) < 2:
        return None  # unexpected format

    years = tbl[0]
    vte = tbl[1]

    return {
        "years": years,
        "vte": vte
    }


def convert_budget_table(tbl):
    """
    tbl = [
        [years...],
        [expenses...],
        [income...]
    ]
    Returns dict with keys: years, expenses, income
    """
    if len(tbl) < 3:
        return None  # unexpected format

    years = tbl[0]
    expenses = tbl[1]
    income = tbl[2]

    return {
        "years": years,
        "expenses": expenses,
        "income": income
    }