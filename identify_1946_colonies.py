#!/usr/bin/env python3
"""
Script to identify all colony section boundaries in the 1946 Colonial Office List
"""

import re

source_file = "/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1946/olmocr_results.md"

# Read the file
with open(source_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Colony patterns to look for - these are the main colony headings
colony_patterns = [
    "ADEN COLONY",
    "ADEN PROTECTORATE",
    "BAHAMA ISLANDS",
    "BARBADOS",
    "BASUTOLAND",
    "BECHUANALAND PROTECTORATE",
    "BERMUDA",
    "BRITISH GUIANA",
    "BRITISH HONDURAS",
    "BRUNEI",
    "CAYMAN ISLANDS",
    "CEYLON",
    "CYPRUS",
    "FALKLAND ISLANDS",
    "FIJI",
    "THE GAMBIA",
    "GIBRALTAR",
    "GILBERT AND ELLICE ISLANDS",
    "THE GOLD COAST",
    "HONG KONG",
    "JAMAICA",
    "KENYA",
    "THE LEEWARD ISLANDS",
    "MALAYA",
    "MALAYAN UNION",
    "MALTA",
    "MAURITIUS",
    "NEW HEBRIDES",
    "NIGERIA",
    "NORTH BORNEO",
    "NORTHERN RHODESIA",
    "NYASALAND PROTECTORATE",
    "PALESTINE",
    "PITCAIRN",
    "ST. HELENA",
    "ASCENSION",
    "TRISTAN DA CUNHA",
    "SARAWAK",
    "SEYCHELLES",
    "SIERRA LEONE",
    "SINGAPORE",
    "SOMALILAND PROTECTORATE",
    "SWAZILAND",
    "TANGANYIKA TERRITORY",
    "TONGA",
    "TRINIDAD AND TOBAGO",
    "TURKS AND CAICOS ISLANDS",
    "UGANDA",
    "WESTERN PACIFIC",
    "THE BRITISH SOLOMON ISLANDS",
    "THE WINDWARD ISLANDS",
    "ZANZIBAR",
    "TRANS-JORDAN",
    "MISCELLANEOUS ISLANDS"
]

# Find all instances of colony headers in Part II
colony_matches = []
in_part_ii = False
part_iii_start = None

for i, line in enumerate(lines, 1):
    stripped = line.strip()

    # Track when we enter Part II (colonies) and Part III (staff)
    if stripped == "PART II A" or (stripped == "ADEN COLONY" and i > 2000):
        in_part_ii = True
    elif (stripped.startswith("PART III") and i > 2000) or (i > 15600 and stripped == "APPENDIX"):
        if part_iii_start is None:
            part_iii_start = i
            in_part_ii = False

    # Only look in Part II region (roughly lines 2600-15700)
    if 2600 < i < 15700:
        for pattern in colony_patterns:
            if stripped == pattern:
                colony_matches.append((i, pattern))
                print(f"Line {i:5d}: {pattern}")
                break

print(f"\nTotal matches found: {len(colony_matches)}")
print(f"Part III starts around line: {part_iii_start}")

# Now let's also look for section boundaries by looking for consecutive colony headers
print("\n\nOrganizing by likely sequence...")
print("="*80)

# Sort by line number
colony_matches.sort(key=lambda x: x[0])

# Group nearby matches (within 10 lines) as likely the same colony
grouped = []
if colony_matches:
    current_group = [colony_matches[0]]
    for match in colony_matches[1:]:
        if match[0] - current_group[-1][0] <= 10:
            current_group.append(match)
        else:
            grouped.append(current_group)
            current_group = [match]
    grouped.append(current_group)

print(f"\nFound {len(grouped)} unique colony sections")
print("\nColony boundaries:")
for i, group in enumerate(grouped):
    print(f"{i+1:2d}. Line {group[0][0]:5d}: {group[0][1]}")
