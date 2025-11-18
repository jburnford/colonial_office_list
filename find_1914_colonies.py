#!/usr/bin/env python3
"""
Script to find all colony section boundaries in 1914 Colonial Office List
by examining the OCR output for potential section headers.
"""

import re

# Read the file
input_file = "/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1914/olmocr_results.md"

print("Searching for colony section headers in 1914...")
print("=" * 80)

# Expected colonies based on 1915
expected_colonies = [
    "AUSTRALIA", "BAHAMAS", "BARBADOS", "BERMUDA", "BRITISH GUIANA",
    "BRITISH HONDURAS", "CANADA", "CEYLON", "CYPRUS", "EAST AFRICA",
    "FALKLAND", "FIJI", "GAMBIA", "GOLD COAST", "HONG KONG", "JAMAICA",
    "LEEWARD", "MALTA", "MAURITIUS", "NEWFOUNDLAND", "NEW ZEALAND",
    "NIGERIA", "NYASALAND", "SEYCHELLES", "SIERRA LEONE", "SOMALILAND",
    "SOUTH AFRICA", "STRAITS SETTLEMENTS", "TRINIDAD", "TURKS",
    "UGANDA", "WEIHAIWEI", "WESTERN PACIFIC", "WINDWARD", "ZANZIBAR"
]

# Find potential section headers
# Looking for lines that start a colony section
with open(input_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Track findings
found_sections = []
part_ii_start = None
part_iii_start = None

for i, line in enumerate(lines, 1):
    stripped = line.strip()

    # Find PART II and PART III markers
    if "PART II" in stripped and "INTRODUCTION" in stripped:
        part_ii_start = i
        print(f"Line {i}: {stripped[:100]}")

    if stripped.startswith("APPENDIX TO PART II"):
        print(f"Line {i}: {stripped[:100]}")

    if stripped.startswith("PART III"):
        part_iii_start = i
        print(f"Line {i}: {stripped[:100]}")

    # Look for colony section headers
    # Pattern: line with just a colony name (all caps, short line)
    if stripped and len(stripped) < 50:
        # Check if it matches expected colony patterns
        for colony in expected_colonies:
            if colony in stripped and len(stripped.split()) <= 5:
                found_sections.append((i, stripped))
                print(f"Line {i}: {stripped}")
                break

print("\n" + "=" * 80)
print(f"Found PART II at line: {part_ii_start}")
print(f"Found PART III at line: {part_iii_start}")
print(f"\nFound {len(found_sections)} potential colony sections")
