#!/usr/bin/env python3
"""
Analyze 1961 structure to identify territory boundaries.
This script reads the OCR file and identifies potential territory section starts.
"""

import re
from pathlib import Path

# OCR file
ocr_file = Path('historical_document_pipeline/processed_pdfs/colonial-office-list-1961/olmocr_results.md')

# Read file
with open(ocr_file, 'r') as f:
    lines = f.readlines()

print(f"Total lines: {len(lines)}")
print()

# Known territory names from the table of contents (pages 49-221)
TERRITORIES = [
    'STATE OF SINGAPORE',
    'ADEN',
    'BAHAMA ISLANDS',
    'BAHAMAS',
    'BERMUDA',
    'BRITISH GUIANA',
    'BRITISH HONDURAS',
    'BRUNEI',
    'CAMEROONS UNDER U.K. TRUSTEESHIP',
    'SOUTHERN CAMEROONS',
    'CYPRUS',
    'FALKLAND ISLANDS AND DEPENDENCIES',
    'FALKLAND ISLANDS',
    'FIJI',
    'PITCAIRN ISLANDS',
    'GAMBIA',
    'THE GAMBIA',
    'GIBRALTAR',
    'HONG KONG',
    'KENYA',
    'MALTA',
    'MAURITIUS',
    'FEDERATION OF NIGERIA',
    'NIGERIA',
    'NORTH BORNEO',
    'FEDERATION OF RHODESIA AND NYASALAND',
    'NORTHERN RHODESIA',
    'NYASALAND PROTECTORATE',
    'NYASALAND',
    'ST. HELENA',
    'ASCENSION',
    'TRISTAN DA CUNHA',
    'SARAWAK',
    'SEYCHELLES',
    'SIERRA LEONE',
    'SOMALILAND',
    'SOMALI REPUBLIC',
    'TANGANYIKA',
    'TONGA',
    'TRINIDAD AND TOBAGO',
    'THE WEST INDIES',
    'WEST INDIES',
    'UGANDA',
    'ZANZIBAR',
]

# Find potential territory section starts
print("=" * 80)
print("POTENTIAL TERRITORY SECTION STARTS")
print("=" * 80)
print()

territory_starts = []

for i, line in enumerate(lines):
    stripped = line.strip()

    # Look for territory names as standalone lines
    if stripped in TERRITORIES:
        # Check context - make sure it's not in a table or list
        prev_line = lines[i-1].strip() if i > 0 else ""
        next_line = lines[i+1].strip() if i < len(lines)-1 else ""

        # Skip if it looks like it's in a table of contents or header
        if '|' in prev_line or '|' in next_line:
            continue
        if prev_line.startswith('Page') or 'Page' in next_line:
            continue

        territory_starts.append((i+1, stripped))  # i+1 for 1-indexed line numbers
        print(f"Line {i+1}: {stripped}")
        if i > 0:
            print(f"  Previous: {lines[i-1].strip()[:60]}")
        if i < len(lines)-1:
            print(f"  Next: {lines[i+1].strip()[:60]}")
        print()

print()
print(f"Found {len(territory_starts)} potential territory starts")
print()

# Look for PART III or INDEX as end marker
print("=" * 80)
print("LOOKING FOR END MARKERS (PART III, INDEX, etc.)")
print("=" * 80)
print()

for i, line in enumerate(lines):
    stripped = line.strip()
    if stripped in ['PART III', '## PART III', 'INDEX', '## INDEX']:
        print(f"Line {i+1}: {stripped}")
        if i > 0:
            print(f"  Previous: {lines[i-1].strip()[:60]}")
        if i < len(lines)-1:
            print(f"  Next: {lines[i+1].strip()[:60]}")
        print()
