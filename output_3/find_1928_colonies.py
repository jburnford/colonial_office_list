#!/usr/bin/env python3
"""
Script to manually identify all colony section boundaries in 1928 Colonial Office List
Based on manual review and cross-reference with 1927 list
"""

import json
import re

# Read the OCR file
ocr_file = "/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1928/olmocr_results.md"

# Known colonies from 1927 that we should look for in 1928
known_colonies_1927 = [
    "AUSTRALIA", "BRITISH COLUMBIA", "NEWFOUNDLAND", "CAPE OF GOOD HOPE", "NATAL",
    "BASUTOLAND", "SWAZILAND", "SOUTHERN RHODESIA", "BAHAMAS", "BARBADOS",
    "BERMUDA", "BRITISH GUIANA", "BRITISH HONDURAS", "CEYLON", "FALKLAND ISLANDS",
    "FIJI", "THE GAMBIA", "GIBRALTAR", "THE GOLD COAST", "HONG KONG",
    "JAMAICA", "CAYMAN ISLANDS", "KENYA", "THE LEEWARD ISLANDS", "MAURITIUS",
    "NIGERIA", "NORTHERN RHODESIA", "PALESTINE", "ST. HELENA", "ASCENSION",
    "SEYCHELLES", "SIERRA LEONE", "STRAITS SETTLEMENTS", "TRINIDAD AND TOBAGO",
    "UGANDA", "WEIHAIWEI", "GRENADA", "ST. LUCIA", "ST. VINCENT",
    "ZANZIBAR", "IRAQ", "NORTH BORNEO", "TRANS-JORDAN", "ADEN",
    "TRISTAN DA CUNHA", "MISCELLANEOUS ISLANDS"
]

# Potential colony headers - we'll search for these patterns
colony_patterns = [
    r'^([A-Z][A-Z ]+)\.$',  # "COLONY NAME."
    r'^\*([A-Z][A-Z ]+)\.$',  # "*COLONY NAME."
    r'^THE ([A-Z][A-Z ]+)\.$',  # "THE COLONY NAME."
    r'^\*THE ([A-Z][A-Z ]+)\.\*$',  # "*THE COLONY NAME.*"
    r'^([A-Z][A-Z ]+ COLONY)\.$',  # "COLONY NAME COLONY."
    r'^([A-Z][A-Z ]+ PROTECTORATE)\.$',  # "COLONY NAME PROTECTORATE."
    r'^([A-Z][A-Z ]+ ISLANDS)\.$',  # "COLONY NAME ISLANDS."
]

# Find potential colony sections
potential_colonies = []
with open(ocr_file, 'r', encoding='utf-8') as f:
    for line_num, line in enumerate(f, 1):
        line = line.rstrip('\n')

        # Check each pattern
        for pattern in colony_patterns:
            match = re.match(pattern, line)
            if match:
                colony_name = match.group(1) if match.lastindex else line.rstrip('.')
                colony_name = colony_name.strip('*').strip()

                # Filter out obvious non-colonies (short names, numbers, etc.)
                if len(colony_name) >= 4 and not re.match(r'^[0-9]+', colony_name):
                    # Check if line is in reasonable range (after line 8000)
                    if line_num > 8000 and line_num < 65000:
                        potential_colonies.append({
                            'line': line_num,
                            'text': line,
                            'name': colony_name
                        })

# Sort by line number
potential_colonies.sort(key=lambda x: x['line'])

# Print findings
print(f"Found {len(potential_colonies)} potential colony section headers:")
print("=" * 80)
for col in potential_colonies:
    print(f"Line {col['line']:5d}: {col['name']}")

# Save to file for review
output_file = "/home/user/colonial_office_list/output_3/1928_potential_colonies.json"
with open(output_file, 'w') as f:
    json.dump(potential_colonies, f, indent=2)

print(f"\n\nSaved to {output_file}")
