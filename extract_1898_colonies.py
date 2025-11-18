#!/usr/bin/env python3
"""
Extract colony sections from Colonial Office List 1898
Based on manually identified colony boundaries
"""

import json
import os

# Manually identified colony boundaries (line numbers where each colony starts)
COLONIES = [
    # Main Colonies (Part II)
    {"name": "BAHAMAS", "start_line": 1506, "type": "colony"},
    {"name": "BARBADOS", "start_line": 1767, "type": "colony"},
    {"name": "BASUTOLAND", "start_line": 2325, "type": "colony"},
    {"name": "BERMUDA", "start_line": 2446, "type": "colony"},
    {"name": "BRITISH_GUIANA", "start_line": 2788, "type": "colony"},
    {"name": "BRITISH_HONDURAS", "start_line": 3476, "type": "colony"},
    {"name": "BRITISH_NEW_GUINEA", "start_line": 3804, "type": "colony"},
    {"name": "CANADA", "start_line": 3894, "type": "colony"},
    {"name": "CAPE_OF_GOOD_HOPE", "start_line": 6760, "type": "colony"},
    {"name": "CEYLON", "start_line": 9055, "type": "colony"},
    {"name": "FALKLAND_ISLANDS", "start_line": 9765, "type": "colony"},
    {"name": "FIJI", "start_line": 10131, "type": "colony"},
    {"name": "GAMBIA", "start_line": 10345, "type": "colony"},
    {"name": "GIBRALTAR", "start_line": 10547, "type": "colony"},
    {"name": "GOLD_COAST", "start_line": 10767, "type": "colony"},
    {"name": "HONG_KONG", "start_line": 11323, "type": "colony"},
    {"name": "JAMAICA", "start_line": 11882, "type": "colony"},
    {"name": "LABUAN", "start_line": 12483, "type": "colony"},
    {"name": "LAGOS", "start_line": 12591, "type": "colony"},

    # Leeward Islands sub-colonies
    {"name": "LEEWARD_ISLANDS_ANTIGUA", "start_line": 13090, "type": "leeward_islands"},
    {"name": "LEEWARD_ISLANDS_ST_CHRISTOPHER_NEVIS", "start_line": 13343, "type": "leeward_islands"},
    {"name": "LEEWARD_ISLANDS_DOMINICA", "start_line": 13766, "type": "leeward_islands"},
    {"name": "LEEWARD_ISLANDS_MONTSERRAT", "start_line": 13900, "type": "leeward_islands"},
    {"name": "LEEWARD_ISLANDS_VIRGIN_ISLANDS", "start_line": 14018, "type": "leeward_islands"},

    {"name": "MALTA", "start_line": 14124, "type": "colony"},
    {"name": "MAURITIUS", "start_line": 14635, "type": "colony"},
    {"name": "SEYCHELLES", "start_line": 15455, "type": "colony"},
    {"name": "NATAL", "start_line": 15617, "type": "colony"},
    {"name": "NEWFOUNDLAND", "start_line": 16156, "type": "colony"},
    {"name": "NEW_SOUTH_WALES", "start_line": 16496, "type": "colony"},
    {"name": "NORFOLK_ISLAND", "start_line": 17558, "type": "dependency"},
    {"name": "NEW_ZEALAND", "start_line": 17574, "type": "colony"},
    {"name": "QUEENSLAND", "start_line": 18316, "type": "colony"},
    {"name": "ST_HELENA", "start_line": 18919, "type": "colony"},
    {"name": "SIERRA_LEONE", "start_line": 19113, "type": "colony"},
    {"name": "SOUTH_AUSTRALIA", "start_line": 19595, "type": "colony"},
    {"name": "STRAITS_SETTLEMENTS", "start_line": 20367, "type": "colony"},
    {"name": "TASMANIA", "start_line": 21069, "type": "colony"},
    {"name": "TRINIDAD", "start_line": 21663, "type": "colony"},
    {"name": "TURKS_AND_CAICOS_ISLANDS", "start_line": 22618, "type": "colony"},
    {"name": "VICTORIA", "start_line": 22788, "type": "colony"},
    {"name": "WESTERN_AUSTRALIA", "start_line": 23780, "type": "colony"},

    # Windward Islands sub-colonies
    {"name": "WINDWARD_ISLANDS_GRENADA", "start_line": 24636, "type": "windward_islands"},
    {"name": "WINDWARD_ISLANDS_ST_LUCIA", "start_line": 24886, "type": "windward_islands"},
    {"name": "WINDWARD_ISLANDS_ST_VINCENT", "start_line": 25127, "type": "windward_islands"},

    {"name": "CYPRUS", "start_line": 25745, "type": "colony"},

    # Appendix - Territories and Protectorates
    {"name": "AMATONGALAND", "start_line": 25574, "type": "protectorate"},
    {"name": "ZULULAND", "start_line": 25392, "type": "protectorate"},
    {"name": "BECHUANALAND_PROTECTORATE", "start_line": 25592, "type": "protectorate"},
    {"name": "BRITISH_CENTRAL_AFRICA", "start_line": 25648, "type": "protectorate"},
    {"name": "BRUNEI", "start_line": 25733, "type": "protectorate"},
    {"name": "BRITISH_EAST_AFRICA_ZANZIBAR_UGANDA", "start_line": 25703, "type": "protectorate"},
    {"name": "BRITISH_SOUTH_AFRICA_COMPANY", "start_line": 26514, "type": "company"},
    {"name": "RHODESIA", "start_line": 26512, "type": "territory"},
    {"name": "NIGER_COAST_PROTECTORATE", "start_line": 26257, "type": "protectorate"},
    {"name": "NORTH_BORNEO", "start_line": 26380, "type": "company"},
    {"name": "SARAWAK", "start_line": 26603, "type": "protectorate"},
    {"name": "WESTERN_PACIFIC", "start_line": 26783, "type": "high_commission"},
    {"name": "ADEN", "start_line": 26920, "type": "territory"},
    {"name": "ASCENSION", "start_line": 26931, "type": "dependency"},
    {"name": "TRISTAN_DA_CUNHA", "start_line": 26937, "type": "dependency"},
]

# Sort by start_line to determine end lines
COLONIES_SORTED = sorted(COLONIES, key=lambda x: x['start_line'])

# Read the source file
source_file = "/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1898/olmocr_results.md"
output_dir = "/home/user/colonial_office_list/output_3/1898_manual_parsed"

print(f"Reading source file: {source_file}")

with open(source_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Extract each colony
metadata = []
total_lines_in_file = len(lines)

for i, colony in enumerate(COLONIES_SORTED):
    start_line = colony['start_line'] - 1  # Convert to 0-indexed

    # Determine end line (start of next colony or end of file)
    if i < len(COLONIES_SORTED) - 1:
        end_line = COLONIES_SORTED[i + 1]['start_line'] - 1
    else:
        end_line = total_lines_in_file

    # Extract lines
    colony_lines = lines[start_line:end_line]

    # Create output filename
    output_filename = f"{colony['name']}.md"
    output_path = os.path.join(output_dir, output_filename)

    # Write to file
    with open(output_path, 'w', encoding='utf-8') as out_f:
        out_f.writelines(colony_lines)

    # Collect metadata
    line_count = len(colony_lines)
    metadata.append({
        "colony_name": colony['name'],
        "type": colony['type'],
        "start_line": colony['start_line'],
        "end_line": end_line,
        "line_count": line_count,
        "filename": output_filename
    })

    print(f"Extracted {colony['name']}: lines {colony['start_line']}-{end_line} ({line_count} lines)")

# Write metadata JSON
metadata_file = "/home/user/colonial_office_list/output_3/1898_manual_parsed.json"
with open(metadata_file, 'w', encoding='utf-8') as f:
    json.dump({
        "source_file": "historical_document_pipeline/processed_pdfs/colonial-office-list-1898/olmocr_results.md",
        "extraction_date": "2025-11-18",
        "total_colonies": len(COLONIES),
        "colonies": metadata
    }, f, indent=2)

print(f"\nExtraction complete!")
print(f"Total colonies extracted: {len(COLONIES)}")
print(f"Metadata saved to: {metadata_file}")

# Count by type
type_counts = {}
for colony in COLONIES:
    colony_type = colony['type']
    type_counts[colony_type] = type_counts.get(colony_type, 0) + 1

print(f"\nBreakdown by type:")
for colony_type, count in sorted(type_counts.items()):
    print(f"  {colony_type}: {count}")
