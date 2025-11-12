#!/usr/bin/env python3
"""
Comprehensive script to parse all colony sections from the 1878 Colonial Office List.
"""

import re
import json
import os

# Read the OCR file
ocr_file = "/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1878/olmocr_results.md"

with open(ocr_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Manual identification of colonies based on inspection of the document
# Format: (start_line, colony_name, is_reference)
# is_reference = True means it's just a pointer to another section

colonies_structure = []

# Let me first find the exact line numbers by searching
def find_line_with_text(text, start=0):
    """Find the line number containing the exact text"""
    for i in range(start, len(lines)):
        if lines[i].strip() == text:
            return i + 1  # Return 1-indexed line number
    return None

# Based on the candidates found, let me identify the structure
# I'll search for specific patterns

print("Analyzing document structure...\n")

# Find where colonies section starts
colonies_start = None
for i, line in enumerate(lines, 1):
    if "ANTIGUA—ANGUILLA—BAHAMAS." in line:
        colonies_start = i
        print(f"Found colonies section start at line {i}")
        break

# Now let's identify major colony sections by looking for patterns
# Main colony sections will have substantive content after the header

# Known major sections from 1877:
expected_colonies = [
    "BAHAMAS",
    "BERMUDAS",
    "BRITISH GUIANA",
    "DOMINION OF CANADA",
    "CAPE OF GOOD HOPE",
    "CEYLON",
    "FALKLAND ISLANDS",
    "FIJI",
    "GIBRALTAR",
    "THE GOLD COAST COLONY",
    "GRIQUALAND WEST",
    "HELIGOLAND",
    "HONDURAS",
    "HONG KONG",
    "JAMAICA",
    "LABUAN",
    "LEEWARD ISLANDS",
    "MAURITIUS",
    "NATAL",
    "NEWFOUNDLAND",
    "NEW SOUTH WALES",
    "NEW ZEALAND",
    "QUEENSLAND",
    "SOUTH AUSTRALIA",
    "STRAITS SETTLEMENTS",
    "ST. HELENA",
    "ST HELENA",
    "SEYCHELLES",
    "TASMANIA",
    "THE TRANSVAAL",
    "TRINIDAD",
    "TURKS AND CAICOS ISLANDS",
    "VICTORIA",
    "WESTERN AUSTRALIA",
    "WEST AFRICA SETTLEMENTS",
    "WINDWARD ISLANDS",
    "TOBAGO"
]

# Find all potential colony headers
potential_headers = []

for i, line in enumerate(lines, 1):
    line_stripped = line.strip()

    # Skip if before colonies section
    if colonies_start and i < colonies_start:
        continue

    # Look for all-caps headers that might be colonies
    # Check if line matches colony pattern
    for colony in expected_colonies:
        # Check for exact match or colony name at start of line
        if (line_stripped == colony + "." or
            line_stripped == colony or
            line_stripped == colony + "," or
            (line_stripped.startswith(colony) and "—" in line_stripped)):
            potential_headers.append((i, line_stripped, colony))
            break

print(f"\nFound {len(potential_headers)} potential colony headers:")
for line_num, text, colony in potential_headers[:50]:
    print(f"{line_num:5d}: {text[:80]}")

# Now let's manually identify the actual sections based on examination
# I'll need to check each one to see if it's a reference or actual section
