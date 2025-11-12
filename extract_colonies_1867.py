#!/usr/bin/env python3
"""
Manual LLM-based parser for 1867 Colonial Office List.
This script extracts individual colony sections from the OCR output.
"""

import json
import re
from pathlib import Path

# Define all colony start lines found through manual inspection
COLONIES = [
    ("ANTIGUA", 1113),
    ("BAHAMAS", 1377),
    ("BARBADOS", 1511),
    ("BERMUDAS", 1998),
    ("BRITISH_COLUMBIA", 2201),
    ("BRITISH_GUIANA", 2427),
    ("BULAMA", 2928),
    ("CANADA", 2937),
    ("CAPE_OF_GOOD_HOPE", 3188),
    ("CEYLON", 4060),
    ("DOMINICA", 4524),
    ("FALKLAND_ISLANDS", 4641),
    ("GIBRALTAR", 4728),
    ("GRENADA", 4757),
    ("HONDURAS", 5100),
    ("HELIGOLAND", 5120),
    ("HONG_KONG", 5314),
    ("JAMAICA", 5557),
    ("LABUAN", 5963),
    ("MALTA", 6067),
    ("MAURITIUS", 6413),
    ("MONTSERRAT", 6939),
    ("NATAL", 7066),
    ("NEVIS", 7260),
    ("NEW_BRUNSWICK", 7383),
    ("NEWFOUNDLAND", 7656),
    ("NEW_SOUTH_WALES", 7872),
    ("NEW_ZEALAND", 8459),
    ("NOVA_SCOTIA", 8854),
    ("PRINCE_EDWARD_ISLAND", 9136),
    ("QUEENSLAND", 9302),
    ("ST_CHRISTOPHERS_AND_ANGUILLA", 9540),
    ("ST_HELENA", 9712),
    ("ST_LUCIA", 9871),
    ("SAINT_VINCENT", 10070),
    ("SOUTH_AUSTRALIA", 10345),
    ("STRAITS_SETTLEMENTS", 10905),
    ("TASMANIA", 11363),
    ("TOBAGO", 11679),
    ("TRINIDAD", 11875),
    ("TURKS_AND_CAICOS_ISLANDS", 12289),
    ("VICTORIA", 12386),
    ("WESTERN_AUSTRALIA", 13113),
    ("WEST_AFRICAN_SETTLEMENTS", 13286),
]

def main():
    # Read the OCR file
    input_file = Path("/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1867/olmocr_results.md")
    output_dir = Path("/home/user/colonial_office_list/output/1867_manual_parsed")

    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    metadata = {
        "year": 1867,
        "parser": "manual_llm",
        "total_colonies": len(COLONIES),
        "colonies": []
    }

    # Process each colony
    for i, (colony_name, start_line) in enumerate(COLONIES):
        # Determine end line (line before next colony, or end of file)
        if i < len(COLONIES) - 1:
            next_start = COLONIES[i + 1][1]
            # End line is the line before the next colony starts
            # But we need to remove trailing blank lines
            end_line = next_start - 1
            while end_line > start_line and lines[end_line - 1].strip() == "":
                end_line -= 1
        else:
            # Last colony: find where content actually ends
            # Look for where the appendix or other non-colony content starts
            end_line = len(lines)
            # Search for common end markers
            for j in range(start_line, len(lines)):
                line_content = lines[j].strip()
                # Look for patterns that indicate end of colony content
                if j > start_line + 100:  # Ensure we're past the colony header
                    if (line_content.startswith("EXAMINATION") or
                        line_content.startswith("GOVERNORS' PENSION") or
                        line_content.startswith("RULES AND REGULATIONS") or
                        line_content.startswith("LIST OF PAPERS") or
                        line_content == "CONSULS RESIDENT IN THE COLONIES."):
                        end_line = j
                        break

        # Extract the colony text
        colony_lines = lines[start_line - 1:end_line]  # -1 because line numbers are 1-indexed
        colony_text = ''.join(colony_lines)

        # Calculate stats
        line_count = end_line - start_line + 1
        char_count = len(colony_text)

        # Save to file
        output_file = output_dir / f"{colony_name}.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(colony_text)

        # Add to metadata
        metadata["colonies"].append({
            "name": colony_name,
            "start_line": start_line,
            "end_line": end_line,
            "line_count": line_count,
            "char_count": char_count,
            "file": f"{colony_name}.txt"
        })

        print(f"Extracted {colony_name}: lines {start_line}-{end_line} ({line_count} lines, {char_count} chars)")

    # Save metadata
    metadata_file = Path("/home/user/colonial_office_list/output/1867_manual_parsed.json")
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)

    print(f"\nExtraction complete! {len(COLONIES)} colonies extracted.")
    print(f"Metadata saved to {metadata_file}")

if __name__ == "__main__":
    main()
