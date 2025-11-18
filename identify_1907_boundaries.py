#!/usr/bin/env python3
"""
Systematically identify all colony boundaries in 1907
"""

import re
from pathlib import Path

ocr_file = Path("/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1907/olmocr_results.md")

with open(ocr_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Step 1: Find all lines that are potential colony headers
# These are lines that are all uppercase, short, and match known patterns

potential_headers = []
known_colonies = {
    "BAHAMAS", "BARBADOS", "BERMUDA", "BRITISH CENTRAL AFRICA PROTECTORATE",
    "BRITISH EAST AFRICA PROTECTORATE", "BRITISH GUIANA", "BRITISH HONDURAS",
    "DOMINION OF CANADA", "CAPE OF GOOD HOPE", "CYPRUS", "FALKLAND ISLANDS",
    "FIJI", "THE GAMBIA", "GIBRALTAR", "THE GOLD COAST", "HONG KONG", "JAMAICA",
    "LABUAN", "THE LEEWARD ISLANDS", "MALTA", "MAURITIUS", "NATAL", "NEWFOUNDLAND",
    "NEW ZEALAND", "NORTHERN NIGERIA", "ORANGE RIVER COLONY", "ST. HELENA",
    "SEYCHELLES", "SIERRA LEONE", "SOMALILAND PROTECTORATE", "BASUTOLAND",
    "BECHUANALAND PROTECTORATE", "RHODESIA", "SOUTHERN NIGERIA",
    "STRAITS SETTLEMENTS", "TRINIDAD AND TOBAGO", "TURKS AND CAICOS ISLANDS",
    "UGANDA", "WEIHAIWEI", "WESTERN PACIFIC", "THE WINDWARD ISLANDS",
    "NORTH BORNEO", "ASCENSION", "TRISTAN DA CUNHA", "ADEN",
    "QUEENSLAND", "SOUTH AUSTRALIA", "TASMANIA", "VICTORIA",
    "WESTERN AUSTRALIA", "LORD HOWE ISLAND"
}

for i, line in enumerate(lines):
    line_stripped = line.strip()
    line_no_period = line_stripped.rstrip('.')

    if line_no_period in known_colonies and i > 2000:  # Skip front matter
        # Check context to ensure it's a section header
        next_line = lines[i+1].strip() if i < len(lines)-1 else ""
        prev_line = lines[i-1].strip() if i > 0 else ""

        # Heuristic: section headers often have blank lines around them
        # or are followed by "Situation and Area" type text
        if not next_line or "Situation" in next_line or "Extent" in next_line:
            potential_headers.append((i+1, line_stripped, line_no_period))

print(f"Found {len(potential_headers)} potential section headers:\n")
for line_num, text, clean_name in potential_headers:
    print(f"{line_num:5d}: {clean_name}")

# Now manually identify CEYLON since it might not have appeared
print("\n\nLooking for CEYLON content between CAPE and CYPRUS...")
# We know CAPE is around 15043 and CYPRUS is at 18686
# Let's find where CAPE content ends
for i in range(18300, 18700):
    line = lines[i].strip()
    if "Ceylon" in line and i > 18200:
        print(f"Line {i+1}: {line[:80]}")
        if i == 18300:  # Stop after finding a few
            break
