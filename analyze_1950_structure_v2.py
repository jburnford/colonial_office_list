#!/usr/bin/env python3
"""
Analyze 1950 OCR structure to identify colony boundaries (version 2 - handles bold formatting).
"""

import re
from pathlib import Path

# Read the OCR file
ocr_file = Path('historical_document_pipeline/processed_pdfs/colonial-office-list-1950/olmocr_results.md')
with open(ocr_file, 'r') as f:
    lines = f.readlines()

# Find all potential colony headers
potential_colonies = []

# Expected colonies from table of contents
expected_colonies = [
    'ADEN',
    'BAHAMA ISLANDS',
    'BARBADOS',
    'BERMUDA',
    'BRITISH GUIANA',
    'BRITISH HONDURAS',
    'BRUNEI',
    'CYPRUS',
    'FALKLAND ISLANDS AND DEPENDENCIES',
    'FIJI',
    'GAMBIA',
    'GIBRALTAR',
    'GOLD COAST',
    'HONG KONG',
    'JAMAICA',
    'KENYA',
    'LEEWARD ISLANDS',
    'FEDERATION OF MALAYA',
    'MALTA',
    'MAURITIUS',
    'NIGERIA',
    'NORTH BORNEO',
    'NORTHERN RHODESIA',
    'NYASALAND PROTECTORATE',
    'ST. HELENA',
    'SARAWAK',
    'SEYCHELLES',
    'SIERRA LEONE',
    'SINGAPORE AND DEPENDENCIES',
    'SOMALILAND PROTECTORATE',
    'TANGANYIKA',
    'TRINIDAD AND TOBAGO',
    'UGANDA',
    'WESTERN PACIFIC',
    'WINDWARD ISLANDS',
    'ZANZIBAR',
    'MISCELLANEOUS ISLANDS',
]

# Create patterns for each expected colony (accounting for variations)
colony_patterns = []
for colony in expected_colonies:
    # Handle "THE " prefix variations
    if colony == 'GAMBIA':
        colony_patterns.append((colony, [r'^(\*\*)?GAMBIA(\*\*)?$', r'^(\*\*)?THE GAMBIA(\*\*)?$']))
    elif colony == 'GOLD COAST':
        colony_patterns.append((colony, [r'^(\*\*)?GOLD COAST(\*\*)?$', r'^(\*\*)?THE GOLD COAST(\*\*)?$']))
    elif colony == 'LEEWARD ISLANDS':
        colony_patterns.append((colony, [r'^(\*\*)?LEEWARD ISLANDS(\*\*)?$', r'^(\*\*)?THE LEEWARD ISLANDS(\*\*)?$']))
    elif colony == 'WINDWARD ISLANDS':
        colony_patterns.append((colony, [r'^(\*\*)?WINDWARD ISLANDS(\*\*)?$', r'^(\*\*)?THE WINDWARD ISLANDS(\*\*)?$']))
    elif colony == 'SINGAPORE AND DEPENDENCIES':
        colony_patterns.append((colony, [r'^(\*\*)?SINGAPORE.*(\*\*)?$']))
    elif colony == 'WESTERN PACIFIC':
        colony_patterns.append((colony, [r'^(\*\*)?WESTERN PACIFIC.*(\*\*)?$']))
    elif colony == 'FALKLAND ISLANDS AND DEPENDENCIES':
        colony_patterns.append((colony, [r'^(\*\*)?FALKLAND ISLANDS.*(\*\*)?$']))
    elif colony == 'ST. HELENA':
        colony_patterns.append((colony, [r'^(\*\*)?ST\.? HELENA.*(\*\*)?$']))
    elif colony == 'NYASALAND PROTECTORATE':
        colony_patterns.append((colony, [r'^(\*\*)?NYASALAND.*(\*\*)?$']))
    elif colony == 'SOMALILAND PROTECTORATE':
        colony_patterns.append((colony, [r'^(\*\*)?SOMALILAND.*(\*\*)?$']))
    else:
        colony_patterns.append((colony, [r'^(\*\*)?' + re.escape(colony) + r'(\*\*)?$']))

# Scan for colony headers (only in main colony section, roughly lines 4000-32000)
for i in range(4000, 32000):
    if i >= len(lines):
        break

    line = lines[i].rstrip()

    # Check against colony patterns
    for colony_name, patterns in colony_patterns:
        matched = False
        for pattern in patterns:
            if re.match(pattern, line):
                matched = True
                break

        if matched:
            # Check if this is a main colony header (not in index, etc.)
            # Main headers typically have content following them like "Situation and Area"
            if i + 10 < len(lines):
                next_lines = ''.join(lines[i+1:i+11]).upper()
                if 'SITUATION' in next_lines or 'AREA' in next_lines or \
                   'GENERAL DESCRIPTION' in next_lines or 'CLIMATE' in next_lines or \
                   'HISTORY' in next_lines or 'CONSTITUTION' in next_lines:
                    # Remove ** markdown if present
                    clean_line = line.replace('**', '')
                    potential_colonies.append((i + 1, clean_line, colony_name))  # +1 for 1-indexed
                    break

# Print findings
print(f"Found {len(potential_colonies)} potential colony sections:\n")
for line_num, line_text, standard_name in sorted(potential_colonies):
    print(f"Line {line_num:5d}: {line_text:45s} (expected: {standard_name})")

# Create a boundaries list
if potential_colonies:
    colonies_with_boundaries = []
    sorted_colonies = sorted(potential_colonies)

    for idx, (start_line, line_text, standard_name) in enumerate(sorted_colonies):
        if idx < len(sorted_colonies) - 1:
            end_line = sorted_colonies[idx + 1][0] - 1
        else:
            # Last colony ends at the Revenue section (around line 32000)
            end_line = 32001

        colonies_with_boundaries.append({
            'name': line_text,
            'standard_name': standard_name,
            'start': start_line,
            'end': end_line,
            'lines': end_line - start_line + 1
        })

    print(f"\n\n=== COLONY BOUNDARIES ===\n")
    for colony in colonies_with_boundaries:
        print(f"{colony['name']:45s} lines {colony['start']:5d}-{colony['end']:5d} ({colony['lines']:5d} lines)")

    print(f"\n\nTotal colonies found: {len(colonies_with_boundaries)}")
    print(f"Expected colonies: {len(expected_colonies)}")

    # Check for missing colonies
    found_standard_names = {c['standard_name'] for c in colonies_with_boundaries}
    missing = set(expected_colonies) - found_standard_names
    if missing:
        print(f"\nMissing colonies: {sorted(missing)}")

    # Save to file
    import json
    output_file = Path('1950_boundaries_v2.json')
    with open(output_file, 'w') as f:
        json.dump(colonies_with_boundaries, f, indent=2)
    print(f"\nSaved boundaries to {output_file}")
