#!/usr/bin/env python3
"""
Script to identify all colony sections in the 1878 Colonial Office List OCR file.
"""

import re
import json

# Read the OCR file
ocr_file = "/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1878/olmocr_results.md"

with open(ocr_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Potential colony names based on 1877 and context
potential_colonies = [
    "BAHAMAS", "BERMUDAS", "BRITISH GUIANA", "CAPE OF GOOD HOPE", "CEYLON",
    "DOMINION OF CANADA", "FALKLAND ISLANDS", "FIJI", "GIBRALTAR",
    "GRIQUALAND WEST", "HELIGOLAND", "HONDURAS", "HONG KONG", "JAMAICA",
    "LABUAN", "MAURITIUS", "NATAL", "NEWFOUNDLAND", "NEW SOUTH WALES",
    "NEW ZEALAND", "QUEENSLAND", "SOUTH AUSTRALIA", "STRAITS SETTLEMENTS",
    "ST. HELENA", "ST HELENA", "SEYCHELLES", "TASMANIA", "TRINIDAD",
    "VICTORIA", "WESTERN AUSTRALIA", "GOLD COAST", "LEEWARD ISLANDS",
    "WINDWARD ISLANDS", "WEST AFRICA", "MALTA", "TOBAGO", "TRANSVAAL",
    "TURKS", "CAICOS"
]

# Find potential colony headers
colony_candidates = []

for i, line in enumerate(lines, 1):
    line_stripped = line.strip()

    # Look for lines that could be colony headers
    # Pattern 1: All caps colony name followed by period
    if re.match(r'^[A-Z][A-Z\s\-—,()\']+\.$', line_stripped):
        for colony in potential_colonies:
            if colony in line_stripped.upper():
                colony_candidates.append((i, line_stripped))
                break

    # Pattern 2: All caps colony name without period
    elif re.match(r'^[A-Z][A-Z\s\-—,()\']+$', line_stripped):
        for colony in potential_colonies:
            if colony == line_stripped or colony in line_stripped:
                colony_candidates.append((i, line_stripped))
                break

# Remove duplicates and sort
colony_candidates = sorted(list(set(colony_candidates)), key=lambda x: x[0])

print(f"Found {len(colony_candidates)} potential colony header candidates:\n")
for line_num, text in colony_candidates[:100]:  # Show first 100
    print(f"{line_num:5d}: {text}")

print(f"\n\nTotal candidates: {len(colony_candidates)}")
