#!/usr/bin/env python3
"""
Extract corrected colonies for 1931 Colonial Office List.
Fixes major over-extraction issues found in batch parser output.
"""

import json
import os
from pathlib import Path

# Source file
SOURCE_FILE = "/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1931/olmocr_results.md"
OUTPUT_DIR = "/home/user/colonial_office_list/output_2/1931_manual_parsed"
YEAR = 1931

# Corrected colony boundaries (manually verified by reading OCR)
COLONIES = [
    # DOMINIONS
    {"name": "AUSTRALIA", "start": 6122, "end": 14047, "note": "Merged from 7 over-extracted state subsections"},
    {"name": "DOMINION OF CANADA", "start": 14048, "end": 16590},
    {"name": "BRITISH COLUMBIA", "start": 16590, "end": 17792},
    {"name": "NEWFOUNDLAND", "start": 17792, "end": 18264},
    {"name": "NEW ZEALAND", "start": 18264, "end": 22678},
    {"name": "SOUTH AFRICA", "start": 22678, "end": 23097, "note": "Includes Union of South Africa"},
    {"name": "BASUTOLAND", "start": 23097, "end": 23518},
    {"name": "SWAZILAND", "start": 23518, "end": 23734},
    {"name": "SOUTHERN RHODESIA", "start": 23734, "end": 25065},

    # COLONIES
    {"name": "BAHAMAS", "start": 25065, "end": 25883},
    {"name": "BARBADOS", "start": 25883, "end": 26088},
    {"name": "BERMUDA", "start": 26088, "end": 26540},
    {"name": "BRITISH GUIANA", "start": 26540, "end": 27353},
    {"name": "BRITISH HONDURAS", "start": 27353, "end": 27994},
    {"name": "CEYLON", "start": 27994, "end": 30020},
    {"name": "FALKLAND ISLANDS", "start": 30020, "end": 30388},
    {"name": "FIJI", "start": 30388, "end": 31216},
    {"name": "THE GAMBIA", "start": 31216, "end": 31635},
    {"name": "GIBRALTAR", "start": 31635, "end": 33198},
    {"name": "HONG KONG", "start": 33198, "end": 34114},
    {"name": "JAMAICA", "start": 34114, "end": 35042},
    {"name": "CAYMAN ISLANDS", "start": 35042, "end": 35083},
    {"name": "TURKS AND CAICOS ISLANDS", "start": 35083, "end": 35939},
    {"name": "KENYA", "start": 35939, "end": 36581},
    {"name": "LEEWARD ISLANDS", "start": 36581, "end": 38101, "note": "Merged ANTIGUA and DOMINICA"},
    {"name": "MALTA", "start": 38101, "end": 38845},
    {"name": "MAURITIUS", "start": 38845, "end": 39585},
    {"name": "NIGERIA", "start": 39585, "end": 40846},
    {"name": "NORTHERN RHODESIA", "start": 40846, "end": 41940},
    {"name": "PALESTINE", "start": 41940, "end": 42558},
    {"name": "ST. HELENA", "start": 42558, "end": 42754},
    {"name": "ASCENSION", "start": 42754, "end": 42769},
    {"name": "SEYCHELLES", "start": 42769, "end": 43017},
    {"name": "SIERRA LEONE", "start": 43017, "end": 43921},
    {"name": "STRAITS SETTLEMENTS", "start": 43921, "end": 44945},
    {"name": "LABUAN", "start": 44945, "end": 48351, "note": "Fixed boundaries - was 44944-48351"},
    {"name": "TRINIDAD AND TOBAGO", "start": 48351, "end": 49405, "note": "Merged TRINIDAD (200 lines) and TOBAGO (854 lines)"},
    {"name": "UGANDA", "start": 49405, "end": 50677},
    {"name": "WINDWARD ISLANDS", "start": 50677, "end": 51415, "note": "Merged GRENADA and ST. LUCIA"},
    {"name": "ZANZIBAR", "start": 51415, "end": 51705},
    {"name": "IRAQ", "start": 51705, "end": 51900},
    {"name": "NORTH BORNEO", "start": 51900, "end": 52513},

    # MISCELLANEOUS POSSESSIONS - these were missing or severely over-extracted
    {"name": "ADEN", "start": 52513, "end": 52556, "note": "Fixed massive over-extraction from 20,134 lines to 44 lines!"},
    {"name": "TRISTAN DA CUNHA", "start": 52556, "end": 52571, "note": "Missing from original extraction"},
    {"name": "MISCELLANEOUS ISLANDS", "start": 52571, "end": 52580, "note": "Missing from original extraction"},
]

def read_lines(filename, start_line, end_line):
    """Read specific lines from file (1-indexed, inclusive)."""
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    return ''.join(lines[start_line-1:end_line])

def main():
    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    print(f"Extracting {len(COLONIES)} colonies for {YEAR}...")

    for colony in COLONIES:
        name = colony['name']
        start = colony['start']
        end = colony['end']

        # Read content
        content = read_lines(SOURCE_FILE, start, end)
        line_count = end - start

        # Create filename
        filename = name.replace(" ", "_").replace(".", "") + ".md"
        filepath = os.path.join(OUTPUT_DIR, filename)

        # Write file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        note = colony.get('note', '')
        status = f" ({note})" if note else ""
        print(f"  {name}: {start}-{end} ({line_count} lines){status}")

    print(f"\nExtracted {len(COLONIES)} colonies to {OUTPUT_DIR}/")

if __name__ == "__main__":
    main()
