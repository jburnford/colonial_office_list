#!/usr/bin/env python3
"""
Analyze 1950 OCR structure to identify colony boundaries.
"""

import re
from pathlib import Path

# Read the OCR file
ocr_file = Path('historical_document_pipeline/processed_pdfs/colonial-office-list-1950/olmocr_results.md')
with open(ocr_file, 'r') as f:
    lines = f.readlines()

# Find all potential colony headers
# Looking for lines that are all-caps with specific colony names
potential_colonies = []

# Common colony name patterns
colony_patterns = [
    r'^ADEN$',
    r'^BAHAMA ISLANDS$',
    r'^BARBADOS$',
    r'^BERMUDA$',
    r'^BRITISH GUIANA$',
    r'^BRITISH HONDURAS$',
    r'^BRUNEI$',
    r'^CEYLON$',
    r'^CYPRUS$',
    r'^FALKLAND ISLANDS',
    r'^FIJI$',
    r'^(THE )?GAMBIA$',
    r'^GIBRALTAR$',
    r'^(THE )?GOLD COAST$',
    r'^HONG KONG$',
    r'^JAMAICA$',
    r'^KENYA$',
    r'^(THE )?LEEWARD ISLANDS$',
    r'^FEDERATION OF MALAYA$',
    r'^MALTA$',
    r'^MAURITIUS$',
    r'^NIGERIA$',
    r'^NORTH BORNEO$',
    r'^NORTHERN RHODESIA$',
    r'^NYASALAND',
    r'^ST\. HELENA$',
    r'^SARAWAK$',
    r'^SEYCHELLES$',
    r'^SIERRA LEONE$',
    r'^SINGAPORE',
    r'^SOMALILAND',
    r'^TANGANYIKA$',
    r'^TRINIDAD',
    r'^UGANDA$',
    r'^WESTERN PACIFIC',
    r'^WINDWARD ISLANDS$',
    r'^ZANZIBAR$',
    r'^MISCELLANEOUS ISLANDS$',
]

# Scan for colony headers (only in main colony section, roughly lines 4000-32000)
for i in range(4000, 32000):
    if i >= len(lines):
        break

    line = lines[i].rstrip()

    # Check against colony patterns
    for pattern in colony_patterns:
        if re.match(pattern, line):
            # Check if this is a main colony header (not in index, etc.)
            # Main headers typically have content following them like "Situation and Area"
            if i + 5 < len(lines):
                next_lines = ''.join(lines[i+1:i+6])
                if 'SITUATION' in next_lines or 'Situation' in next_lines or \
                   'AREA' in next_lines or 'Area' in next_lines or \
                   'GENERAL DESCRIPTION' in next_lines or 'General Description' in next_lines:
                    potential_colonies.append((i + 1, line))  # +1 for 1-indexed line numbers
                    break

# Print findings
print(f"Found {len(potential_colonies)} potential colony sections:\n")
for line_num, name in sorted(potential_colonies):
    print(f"Line {line_num:5d}: {name}")

# Create a boundaries list
if potential_colonies:
    colonies_with_boundaries = []
    sorted_colonies = sorted(potential_colonies)

    for idx, (start_line, name) in enumerate(sorted_colonies):
        if idx < len(sorted_colonies) - 1:
            end_line = sorted_colonies[idx + 1][0] - 1
        else:
            # Last colony ends at the Revenue section (around line 32000)
            end_line = 32001

        colonies_with_boundaries.append({
            'name': name,
            'start': start_line,
            'end': end_line,
            'lines': end_line - start_line + 1
        })

    print(f"\n\n=== COLONY BOUNDARIES ===\n")
    for colony in colonies_with_boundaries:
        print(f"{colony['name']:40s} lines {colony['start']:5d}-{colony['end']:5d} ({colony['lines']:5d} lines)")

    print(f"\n\nTotal colonies: {len(colonies_with_boundaries)}")

    # Save to file
    import json
    output_file = Path('1950_boundaries.json')
    with open(output_file, 'w') as f:
        json.dump(colonies_with_boundaries, f, indent=2)
    print(f"\nSaved boundaries to {output_file}")
