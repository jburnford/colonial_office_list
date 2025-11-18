#!/usr/bin/env python3
"""
Extract all colonies from the 1930 Colonial Office List
Manual boundary identification with systematic document review
"""

import re
import json
import os
from pathlib import Path

# Read the source file
SOURCE_FILE = 'historical_document_pipeline/processed_pdfs/colonial-office-list-1930/olmocr_results.md'
OUTPUT_DIR = 'output_3/1930_manual_parsed'
JSON_FILE = 'output_3/1930_manual_parsed.json'

with open(SOURCE_FILE, 'r', encoding='utf-8') as f:
    lines = f.readlines()

total_lines = len(lines)
print(f"Total lines in source file: {total_lines}")

# Manually identified colony boundaries through systematic document review
# Based on:
# 1. Reading the OCR content and identifying colony headers
# 2. Cross-referencing with 1928 colonies list
# 3. Verifying boundaries by checking section headers (Situation, History, etc.)

colonies = [
    {
        "colony_name": "BAHAMAS",
        "start_line": 23905,
        "end_line": 24319,
        "note": None
    },
    {
        "colony_name": "BARBADOS",
        "start_line": 24320,
        "end_line": 24952,
        "note": "OCR shows 'BARBADOS.*'"
    },
    {
        "colony_name": "BERMUDA",
        "start_line": 24953,
        "end_line": 25377,
        "note": None
    },
    {
        "colony_name": "BRITISH GUIANA",
        "start_line": 25378,
        "end_line": 26336,
        "note": None
    },
    {
        "colony_name": "BRITISH HONDURAS",
        "start_line": 26337,
        "end_line": 26721,
        "note": None
    },
    {
        "colony_name": "CEYLON",
        "start_line": 26722,
        "end_line": 28119,
        "note": None
    },
    {
        "colony_name": "CYPRUS",
        "start_line": 28120,
        "end_line": 28972,
        "note": None
    },
    {
        "colony_name": "FALKLAND ISLANDS",
        "start_line": 28973,
        "end_line": 29359,
        "note": None
    },
    {
        "colony_name": "FIJI",
        "start_line": 29360,
        "end_line": 30059,
        "note": None
    },
    {
        "colony_name": "THE GAMBIA",
        "start_line": 30060,
        "end_line": 30472,
        "note": None
    },
    {
        "colony_name": "GIBRALTAR",
        "start_line": 30473,
        "end_line": 30740,
        "note": None
    },
    {
        "colony_name": "THE GOLD COAST",
        "start_line": 30743,
        "end_line": 31950,
        "note": "Full name at line 30743: THE GOLD COAST COLONY; includes ASHANTI (31067), THE NORTHERN TERRITORIES (31088), THE BRITISH SPHERE OF TOGO-LAND (31115)"
    },
    {
        "colony_name": "HONG KONG",
        "start_line": 31951,
        "end_line": 32599,
        "note": None
    },
    {
        "colony_name": "JAMAICA",
        "start_line": 32600,
        "end_line": 33514,
        "note": "OCR shows '*JAMAICA.*'"
    },
    {
        "colony_name": "CAYMAN ISLANDS",
        "start_line": 33515,
        "end_line": 33558,
        "note": "Dependency of Jamaica"
    },
    {
        "colony_name": "TURKS AND CAICOS ISLANDS",
        "start_line": 33559,
        "end_line": 33747,
        "note": "Dependency of Jamaica"
    },
    {
        "colony_name": "KENYA",
        "start_line": 33748,
        "end_line": 34636,
        "note": "Full name: KENYA COLONY AND PROTECTORATE"
    },
    {
        "colony_name": "THE LEEWARD ISLANDS",
        "start_line": 34637,
        "end_line": 36178,
        "note": "Includes ANTIGUA (34883), BARBUDA (35271), ST. CHRISTOPHER AND NEVIS (35275), DOMINICA (35588), MONTSERRAT (35879)"
    },
    {
        "colony_name": "MALTA",
        "start_line": 36179,
        "end_line": 36986,
        "note": None
    },
    {
        "colony_name": "MAURITIUS",
        "start_line": 36987,
        "end_line": 37773,
        "note": None
    },
    {
        "colony_name": "NIGERIA",
        "start_line": 37774,
        "end_line": 38975,
        "note": None
    },
    {
        "colony_name": "NORTHERN RHODESIA",
        "start_line": 38976,
        "end_line": 39497,
        "note": "OCR shows 'NORTHERN RHODESIA.†'"
    },
    {
        "colony_name": "NYASALAND PROTECTORATE",
        "start_line": 39498,
        "end_line": 39875,
        "note": None
    },
    {
        "colony_name": "PALESTINE",
        "start_line": 39876,
        "end_line": 40437,
        "note": None
    },
    {
        "colony_name": "ST. HELENA",
        "start_line": 40438,
        "end_line": 40632,
        "note": None
    },
    {
        "colony_name": "ASCENSION",
        "start_line": 40633,
        "end_line": 40649,
        "note": "Dependency of St. Helena"
    },
    {
        "colony_name": "SEYCHELLES",
        "start_line": 40650,
        "end_line": 40945,
        "note": None
    },
    {
        "colony_name": "SIERRA LEONE",
        "start_line": 40946,
        "end_line": 41609,
        "note": None
    },
    {
        "colony_name": "SOMALILAND PROTECTORATE",
        "start_line": 41610,
        "end_line": 41760,
        "note": None
    },
    {
        "colony_name": "STRAITS SETTLEMENTS",
        "start_line": 41761,
        "end_line": 44731,
        "note": "Large section including THE FEDERATED STATES OF THE MALAY PENINSULA (42700), and MALAY STATES NOT INCLUDED IN THE FEDERATION (43855)"
    },
    {
        "colony_name": "TANGANYIKA TERRITORY",
        "start_line": 44732,
        "end_line": 45269,
        "note": None
    },
    {
        "colony_name": "TRINIDAD AND TOBAGO",
        "start_line": 45270,
        "end_line": 46386,
        "note": "Includes TRINIDAD subsection at line 45272"
    },
    {
        "colony_name": "UGANDA",
        "start_line": 46387,
        "end_line": 46797,
        "note": None
    },
    {
        "colony_name": "WEIHAIWEI",
        "start_line": 46798,
        "end_line": 46868,
        "note": None
    },
    {
        "colony_name": "WESTERN PACIFIC",
        "start_line": 46869,
        "end_line": 47313,
        "note": "Includes THE GILBERT AND ELICE ISLANDS COLONY (46936), THE BRITISH SOLOMON ISLANDS PROTECTORATE (47061), THE NEW HEBRIDES (47243), PITCAIRN ISLAND (47306)"
    },
    {
        "colony_name": "THE WINDWARD ISLANDS",
        "start_line": 47314,
        "end_line": 48346,
        "note": "Includes GRENADA (47389), ST. LUCIA (47658), ST. VINCENT (48057)"
    },
    {
        "colony_name": "ZANZIBAR",
        "start_line": 48347,
        "end_line": 48625,
        "note": None
    },
    {
        "colony_name": "IRAQ",
        "start_line": 48626,
        "end_line": 48813,
        "note": None
    },
    {
        "colony_name": "NORTH BORNEO",
        "start_line": 48814,
        "end_line": 49358,
        "note": None
    },
    {
        "colony_name": "ADEN",
        "start_line": 49361,
        "end_line": 49384,
        "note": "Within MISCELLANEOUS POSSESSIONS section (49359)"
    },
    {
        "colony_name": "TRISTAN DA CUNHA",
        "start_line": 49385,
        "end_line": 49400,
        "note": "Within MISCELLANEOUS POSSESSIONS section"
    },
    {
        "colony_name": "MISCELLANEOUS ISLANDS",
        "start_line": 49401,
        "end_line": 49409,
        "note": "Last colony in PART II-C; PART III starts at 49410"
    }
]

# Calculate line counts
for colony in colonies:
    colony['line_count'] = colony['end_line'] - colony['start_line'] + 1

print(f"\nTotal colonies identified: {len(colonies)}")
print("\nColonies:")
for colony in colonies:
    print(f"  {colony['colony_name']:40} Lines {colony['start_line']:6}-{colony['end_line']:6} ({colony['line_count']:4} lines)")

# Create output directory
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Extract each colony to a separate file
def extract_colony_text(colony):
    """Extract colony text, removing line number prefixes from Read tool display"""
    start_idx = colony['start_line'] - 1  # Convert to 0-indexed
    end_idx = colony['end_line']

    # Extract lines (they're already in plain text format without prefixes)
    colony_lines = lines[start_idx:end_idx]

    # Create filename
    filename = colony['colony_name'].replace(' ', '_').replace('.', '').replace('*', '').replace('†', '')
    filename = filename.replace(',', '').replace('(', '').replace(')', '').replace("'", '')
    filepath = os.path.join(OUTPUT_DIR, f"{filename}.txt")

    # Write to file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(colony_lines)

    colony['file'] = f"/home/user/colonial_office_list/{filepath}"
    return filepath

print("\n\nExtracting colonies...")
for colony in colonies:
    filepath = extract_colony_text(colony)
    print(f"  Extracted: {colony['colony_name']} -> {filepath}")

# Generate JSON metadata
metadata = {
    "year": 1930,
    "source_file": SOURCE_FILE,
    "extraction_date": "2025-11-18",
    "extraction_method": "Manual LLM boundary identification with systematic document review",
    "total_colonies": len(colonies),
    "notes": [
        "All colony boundaries manually identified by reading OCR content",
        "Extraction covers PART II-C: Colonial Office colonies only",
        "PART II-C starts at line 23903, PART III starts at line 49410",
        "Some colonies have OCR errors in headers (e.g., '*JAMAICA.*', 'BARBADOS.*')",
        "Several colonies include sub-territories and dependencies",
        "Line counts include all content from start to end boundaries",
        "Compared with 1928: Cyprus added (new in 1930), Weihaiwei still present (removed in 1931)",
        "SOMALILAND PROTECTORATE present (new compared to 1928)",
        "TANGANYIKA TERRITORY present (mandated territory)",
        "WESTERN PACIFIC added as umbrella colony"
    ],
    "colonies": colonies
}

with open(JSON_FILE, 'w', encoding='utf-8') as f:
    json.dump(metadata, f, indent=2, ensure_ascii=False)

print(f"\n\nMetadata written to: {JSON_FILE}")
print(f"\nExtraction complete!")
print(f"Total colonies extracted: {len(colonies)}")
print(f"Output directory: {OUTPUT_DIR}/")
print(f"JSON metadata: {JSON_FILE}")
