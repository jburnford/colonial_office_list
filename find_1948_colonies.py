#!/usr/bin/env python3
"""
Script to find colony section boundaries in the 1948 Colonial Office List.
"""

import re

# List of colonies from the table of contents
colonies = [
    ("Aden", "ADEN"),
    ("Bahamas", "BAHAMAS"),
    ("Barbados", "BARBADOS"),
    ("Bermuda", "BERMUDA"),
    ("British Guiana", "BRITISH GUIANA"),
    ("British Honduras", "BRITISH HONDURAS"),
    ("Brunei", "BRUNEI"),
    ("Cyprus", "CYPRUS"),
    ("Falkland Islands", "FALKLAND"),
    ("Fiji", "FIJI"),
    ("Gambia", "GAMBIA"),
    ("Gibraltar", "GIBRALTAR"),
    ("Gold Coast", "GOLD COAST"),
    ("Hong Kong", "HONG KONG"),
    ("Jamaica", "JAMAICA"),
    ("Kenya", "KENYA"),
    ("Leeward Islands", "LEEWARD"),
    ("Federation of Malaya", "MALAYA"),
    ("Malta", "MALTA"),
    ("Mauritius", "MAURITIUS"),
    ("Nigeria", "NIGERIA"),
    ("North Borneo", "NORTH BORNEO"),
    ("Northern Rhodesia", "NORTHERN RHODESIA"),
    ("Nyasaland", "NYASALAND"),
    ("St. Helena", "ST. HELENA|ST\. HELENA"),
    ("Sarawak", "SARAWAK"),
    ("Seychelles", "SEYCHELLES"),
    ("Sierra Leone", "SIERRA LEONE"),
    ("Singapore", "SINGAPORE"),
    ("Somaliland Protectorate", "SOMALILAND"),
    ("Tanganyika", "TANGANYIKA"),
    ("Trinidad", "TRINIDAD"),
    ("Uganda", "UGANDA"),
    ("Western Pacific", "WESTERN PACIFIC"),
    ("Windward Islands", "WINDWARD"),
    ("Zanzibar", "ZANZIBAR"),
    ("Miscellaneous Islands", "MISCELLANEOUS"),
]

input_file = "/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1948/olmocr_results.md"

# Read the file
print("Reading file...")
with open(input_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Total lines: {len(lines)}")

# Find Part II start and Part III start
part_ii_start = None
part_iii_start = None

for i, line in enumerate(lines, 1):
    if "HISTORICAL AND STATISTICAL ACCOUNT OF THE COLONIES" in line:
        part_ii_start = i
    if i > 10000 and line.strip() == "PART III":
        part_iii_start = i
        break

print(f"Part II starts at line: {part_ii_start}")
print(f"Part III starts at line: {part_iii_start}")

# Find each colony section
colony_positions = []

for colony_name, search_pattern in colonies:
    # Search for the colony name as a standalone heading
    found = False
    for i in range(part_ii_start, part_iii_start):
        line = lines[i-1]  # Convert to 0-based index
        # Look for the colony name on its own line (after line number prefix)
        # The format is: line_number→TEXT or just TEXT
        content = line.strip()

        # Try to extract content after line number if present
        match = re.search(r'^\s*\d+→(.*)$', line)
        if match:
            content = match.group(1).strip()

        # Check if this line matches our colony name exactly or as a major heading
        if content and re.match(f'^{search_pattern}$', content):
            colony_positions.append((i, colony_name, content))
            print(f"Found {colony_name} at line {i}: {content}")
            found = True
            break

    if not found:
        print(f"WARNING: Could not find {colony_name}")

# Sort by line number
colony_positions.sort(key=lambda x: x[0])

print("\n" + "="*80)
print("Summary of colony positions:")
print("="*80)
for i, (line_no, name, text) in enumerate(colony_positions):
    if i < len(colony_positions) - 1:
        end_line = colony_positions[i+1][0] - 1
    else:
        end_line = part_iii_start - 1
    print(f"{name:30s} Lines {line_no:5d} to {end_line:5d} ({end_line - line_no + 1:5d} lines)")

print(f"\nTotal colonies found: {len(colony_positions)}")
