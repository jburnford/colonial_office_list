#!/usr/bin/env python3
"""Identify all colony boundaries in the 1888 Colonial Office List."""

import re

# Read the OCR file
ocr_file = "/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1888/olmocr_results.md"

with open(ocr_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Expected colony names from historical context (1888)
expected_colonies = [
    "BAHAMAS", "BARBADOS", "BERMUDA", "JAMAICA", "TRINIDAD",
    "BRITISH GUIANA", "BRITISH HONDURAS",
    "GRENADA", "ST. LUCIA", "ST. VINCENT", "TOBAGO",
    "ANTIGUA", "DOMINICA", "MONTSERRAT", "ST. CHRISTOPHER", "ST. KITTS", "NEVIS",
    "VIRGIN ISLANDS",
    "TURKS", "CAICOS",
    "CAPE OF GOOD HOPE", "NATAL", "BASUTOLAND", "BRITISH BECHUANALAND", "ZULULAND",
    "MAURITIUS", "SEYCHELLES", "ST. HELENA", "ASCENSION",
    "SIERRA LEONE", "GAMBIA", "GOLD COAST", "LAGOS",
    "CEYLON", "HONG KONG", "STRAITS SETTLEMENTS", "LABUAN",
    "GIBRALTAR", "MALTA", "CYPRUS", "HELIGOLAND",
    "DOMINION OF CANADA", "NEWFOUNDLAND",
    "NEW SOUTH WALES", "VICTORIA", "QUEENSLAND", "SOUTH AUSTRALIA",
    "WESTERN AUSTRALIA", "TASMANIA", "NEW ZEALAND",
    "FIJI", "FALKLAND ISLANDS", "BRITISH NEW GUINEA"
]

# Search for each colony
found_colonies = {}

for i, line in enumerate(lines, 1):
    stripped = line.strip()

    # Remove line number prefix if present
    if '→' in stripped:
        parts = stripped.split('→', 1)
        if len(parts) == 2:
            stripped = parts[1]

    # Check if this line matches any expected colony name
    for colony in expected_colonies:
        # Match exact colony name (with or without dot)
        if stripped == colony or stripped == f"{colony}.":
            # Make sure it's not a duplicate too close to previous occurrence
            if colony not in found_colonies or (i - found_colonies[colony]) > 100:
                found_colonies[colony] = i
                print(f"Line {i}: {colony}")
                break
        # Also check for compound names like "ST. CHRISTOPHER AND NEVIS"
        elif colony in ["ST. CHRISTOPHER", "ST. KITTS"] and ("ST. CHRISTOPHER" in stripped or "ST. KITTS" in stripped):
            if "ST. CHRISTOPHER" not in found_colonies or (i - found_colonies.get("ST. CHRISTOPHER", 0)) > 100:
                found_colonies["ST. CHRISTOPHER AND NEVIS"] = i
                print(f"Line {i}: {stripped}")
                break

print(f"\n\nTotal colonies found: {len(found_colonies)}")
print("\nColonies found:")
for colony in sorted(found_colonies.items(), key=lambda x: x[1]):
    print(f"  {colony[0]}: Line {colony[1]}")
