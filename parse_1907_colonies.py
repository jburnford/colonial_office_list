#!/usr/bin/env python3
"""
Parse Colonial Office List 1907 - Manual Colony Boundary Identification
"""

import re
import json
from pathlib import Path

# Read the OCR file
ocr_file = Path("/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1907/olmocr_results.md")

with open(ocr_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Known colony names from 1906 and expected patterns
# Note: These need to match exactly with periods where they appear
colony_patterns = [
    ("THE COMMONWEALTH OF AUSTRALIA", "THE_COMMONWEALTH_OF_AUSTRALIA"),
    ("NEW SOUTH WALES", "NEW_SOUTH_WALES"),
    ("NORFOLK ISLAND", "NORFOLK_ISLAND"),
    ("LORD HOWE ISLAND", "LORD_HOWE_ISLAND"),
    ("QUEENSLAND", "QUEENSLAND"),
    ("SOUTH AUSTRALIA", "SOUTH_AUSTRALIA"),
    ("TASMANIA", "TASMANIA"),
    ("VICTORIA", "VICTORIA"),
    ("WESTERN AUSTRALIA", "WESTERN_AUSTRALIA"),
    ("BRITISH NEW GUINEA", "BRITISH_NEW_GUINEA"),
    ("BAHAMAS", "BAHAMAS"),
    ("BARBADOS", "BARBADOS"),
    ("BERMUDA", "BERMUDA"),
    ("BRITISH CENTRAL AFRICA PROTECTORATE", "BRITISH_CENTRAL_AFRICA_PROTECTORATE"),
    ("BRITISH EAST AFRICA PROTECTORATE", "BRITISH_EAST_AFRICA_PROTECTORATE"),
    ("BRITISH GUIANA", "BRITISH_GUIANA"),
    ("BRITISH HONDURAS", "BRITISH_HONDURAS"),
    ("DOMINION OF CANADA", "DOMINION_OF_CANADA"),
    ("CAPE OF GOOD HOPE", "CAPE_OF_GOOD_HOPE"),
    ("CEYLON", "CEYLON"),
    ("CYPRUS", "CYPRUS"),
    ("FALKLAND ISLANDS", "FALKLAND_ISLANDS"),
    ("FIJI", "FIJI"),
    ("THE GAMBIA", "THE_GAMBIA"),
    ("GIBRALTAR", "GIBRALTAR"),
    ("THE GOLD COAST", "THE_GOLD_COAST"),
    ("HONG KONG", "HONG_KONG"),
    ("JAMAICA", "JAMAICA"),
    ("LABUAN", "LABUAN"),
    ("LAGOS", "LAGOS"),
    ("THE LEEWARD ISLANDS", "THE_LEEWARD_ISLANDS"),
    ("MALTA", "MALTA"),
    ("MAURITIUS", "MAURITIUS"),
    ("NATAL", "NATAL"),
    ("NEWFOUNDLAND", "NEWFOUNDLAND"),
    ("NEW ZEALAND", "NEW_ZEALAND"),
    ("NORTHERN NIGERIA", "NORTHERN_NIGERIA"),
    ("ORANGE RIVER COLONY", "ORANGE_RIVER_COLONY"),
    ("ST. HELENA", "ST_HELENA"),
    ("SEYCHELLES", "SEYCHELLES"),
    ("SIERRA LEONE", "SIERRA_LEONE"),
    ("SOMALILAND PROTECTORATE", "SOMALILAND_PROTECTORATE"),
    ("BASUTOLAND", "BASUTOLAND"),
    ("BECHUANALAND PROTECTORATE", "BECHUANALAND_PROTECTORATE"),
    ("RHODESIA", "RHODESIA"),
    ("SOUTHERN NIGERIA", "SOUTHERN_NIGERIA"),
    ("THE FEDERATED MALAY STATES", "THE_FEDERATED_MALAY_STATES"),
    ("STRAITS SETTLEMENTS", "STRAITS_SETTLEMENTS"),
    ("TRANSVAAL", "TRANSVAAL"),
    ("TRINIDAD AND TOBAGO", "TRINIDAD_AND_TOBAGO"),
    ("TURKS AND CAICOS ISLANDS", "TURKS_AND_CAICOS_ISLANDS"),
    ("UGANDA", "UGANDA"),
    ("WEIHAIWEI", "WEIHAIWEI"),
    ("WESTERN PACIFIC", "WESTERN_PACIFIC"),
    ("THE WINDWARD ISLANDS", "THE_WINDWARD_ISLANDS"),
    ("NORTH BORNEO", "NORTH_BORNEO"),
    ("ZANZIBAR", "ZANZIBAR"),
    ("ADEN", "ADEN"),
    ("ASCENSION", "ASCENSION"),
    ("TRISTAN DA CUNHA", "TRISTAN_DA_CUNHA")
]

# Find all potential colony headers
potential_headers = []

for i, line in enumerate(lines):
    line_text = line.strip()

    # Check each pattern - need to handle variations like "BAHAMAS." vs "BAHAMAS"
    for pattern, file_name in colony_patterns:
        if line_text == pattern or line_text == pattern + ".":
            line_num = i + 1  # 1-indexed

            # Get context
            prev_line_text = lines[i-1].strip() if i > 0 else ""
            next_line_text = lines[i+1].strip() if i < len(lines) - 1 else ""

            # Skip if in early content (front matter, ads, etc.)
            if line_num > 2000:
                potential_headers.append({
                    'name': pattern,
                    'file_name': file_name,
                    'line_number': line_num,
                    'line_text': line_text,
                    'context_before': prev_line_text[:70] if prev_line_text else "",
                    'context_after': next_line_text[:70] if next_line_text else ""
                })

print(f"Found {len(potential_headers)} potential colony headers:")
print()

for header in potential_headers:
    print(f"Line {header['line_number']:5d}: {header['line_text']}")
    print(f"  Before: {header['context_before']}")
    print(f"  After:  {header['context_after']}")
    print()
