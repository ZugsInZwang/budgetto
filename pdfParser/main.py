import pdfplumber
import re
import json

from extractors import (extract_text_lines, extract_tables_with_coords)
from detectors import (detect_identifier, is_budget_table, is_vte_table, looks_like_actions_table, is_footer_or_page_number)
from cleaners import (clean_numeric_table, convert_vte_table, convert_budget_table)


# ------------------------------------------------------------
# MAIN PARSER
# ------------------------------------------------------------
def parse_pdf_to_json(pdf_path):

    data = {"sd_targets": []}
    current_sd = None
    current_actionplan = None

    with pdfplumber.open(pdf_path) as pdf:

        for page_number, page in enumerate(pdf.pages, start=85):
            
            # Extract EVERYTHING with coordinates
            text_lines = extract_text_lines(page)
            table_items = extract_tables_with_coords(page)

            # Merge + sort by Y (top to bottom)
            items = text_lines + table_items
            items.sort(key=lambda x: x["y"])

            # Sequential processing
            in_description = False # Indicates if we are currently in the actionplan description
            in_title = False    # Indicates if we are currently in the SD title
            title_text = ""
            for item in items:

                # ------------------------------------------------------------
                # TEXT PROCESSING
                # ------------------------------------------------------------
                if item["type"] == "text":
                    line = item["content"]
                    if is_footer_or_page_number(line):
                        continue
                    
                    ident = detect_identifier(line)

                    # Check for SD policy goal title
                    if current_sd and in_title:
                        current_sd["title"] += line

                    # New SD policy goal
                    if ident and ident.startswith("SD"):
                        current_sd = {
                            "id": ident,
                            "title": "",
                            "page": page_number,
                            "budget": None,
                            "vte": None,
                            "actionplans": []
                        }
                        data["sd_targets"].append(current_sd)
                        current_actionplan = None
                        in_title = True
                        in_description = True
                        continue

                    # New actionplan
                    if ident and (ident.startswith("PO") or ident.startswith("OD")):
                        current_actionplan = {
                            "id": ident,
                            "title": line.replace(ident, "").strip(),
                            "page": page_number,
                            "description": "",
                            "budget": None,
                            "vte": None,
                            "actions": []
                        }
                        if current_sd:
                            current_sd["actionplans"].append(current_actionplan)
                        in_description = True
                        in_title = False
                        continue

                    # Add to description if we are inside an actionplan
                    if current_actionplan:
                        # stop adding if this is a header
                        if in_description and not any(k in line.lower() for k in
                                   ["budget", "vte", "alle acties", "eur", "uitgaven", "ontvangsten" ]):
                            current_actionplan["description"] += line + " "
                        else:
                            in_description = False

                # ------------------------------------------------------------
                # TABLE PROCESSING
                # ------------------------------------------------------------
                elif item["type"] == "table":
                    in_title = False
                    title_text = ""
                    
                    tbl = item["content"]

                    # Determine table type
                    if is_budget_table(tbl):
                        if current_actionplan:
                            current_actionplan["budget"] = convert_budget_table(clean_numeric_table(tbl))
                        elif current_sd:
                            current_sd["budget"] = convert_budget_table(clean_numeric_table(tbl))
                        continue

                    if is_vte_table(tbl):
                        if current_actionplan:
                            current_actionplan["vte"] = convert_vte_table(clean_numeric_table(tbl))
                        elif current_sd:
                            current_sd["vte"] = convert_vte_table(clean_numeric_table(tbl))
                        continue

                    if current_actionplan and looks_like_actions_table(tbl):
                        for row in tbl:
                            if re.match(r"(AC|PR|PRB|ACB)\d+", row[0]):
                                current_actionplan["actions"].append(row)
                        continue

    return data


# ------------------------------------------------------------
# RUN + SAVE
# ------------------------------------------------------------


pdf_path = "../data/pdf/p90-194_strategische_nota.pdf"  #"../data/p90-95 BO 2026 - MJP 26-31.pdf" #p90-194_strategische_nota.pdf"
result = parse_pdf_to_json(pdf_path)
with open("../strategische_nota.json", "w", encoding="utf-8") as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print("Saved json")

