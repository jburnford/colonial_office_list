#!/usr/bin/env python3
"""
Final extraction of all 1878 Colonial Office List colonies.
Based on manual inspection of document structure.
"""

import re
import json
import os

# Read the OCR file
ocr_file = "/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1878/olmocr_results.md"

with open(ocr_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# All colony sections with their exact boundaries
# Format: (colony_name, start_line, end_line, notes)
# These were determined by manual inspection

colonies = [
    ("BAHAMAS", 1343, 1576, "Full section"),
    # BARBADOS at 1579 is just a reference to Windward Islands, skip
    ("BERMUDAS", 1585, 1846, "Full section"),
    # BRITISH COLUMBIA at 1847 is a reference to Canada, skip
    # BRITISH HONDURAS at 1850 is a reference to Honduras, skip
    ("BRITISH_GUIANA", 1853, 2474, "Full section"),
    ("DOMINION_OF_CANADA", 2475, 4263, "Full section"),
    ("CAPE_OF_GOOD_HOPE", 4264, 5589, "Full section"),
    ("CEYLON", 5590, 6162, "Full section"),
    ("FALKLAND_ISLANDS", 6163, 6270, "Full section"),
    ("FIJI", 6271, 6357, "Full section, marked as **FIJI.**"),
    ("GIBRALTAR", 6358, 6464, "Full section"),
    ("THE_GOLD_COAST_COLONY", 6465, 7268, "Full section"),
    ("HELIGOLAND", 7269, 7309, "Full section"),
    ("HONDURAS", 7310, 7525, "Full section"),
    ("HONG_KONG", 7526, 7794, "Full section"),
    ("JAMAICA", 7795, 8437, "Full section"),
    ("LABUAN", 8438, 8454, "Full section"),
    ("LEEWARD_ISLANDS", 8455, 10212, "Full section starting with LABUAN—LEEWARD ISLANDS header"),
    # MONTSERRAT at 10888 is a reference to Leeward Islands, skip
    ("MAURITIUS", 10213, 10887, "Full section"),
    ("NATAL", 10891, 11285, "Full section"),
    # NEVIS at 11283-11284 is a reference, within Natal section
    ("NEWFOUNDLAND", 11286, 11520, "Full section"),
    ("NEW_SOUTH_WALES", 11521, 12284, "Full section"),
    ("NEW_ZEALAND", 12285, 12800, "Full section"),
    ("QUEENSLAND", 12801, 13289, "Full section"),
    ("SOUTH_AUSTRALIA", 13290, 14171, "Full section"),
    ("STRAITS_SETTLEMENTS", 14172, 15106, "Full section"),
    # TOBAGO at 15104-15105 is reference to Windward Islands, within STRAITS SETTLEMENTS
    ("THE_TRANSVAAL", 15107, 15205, "Full section"),
    ("TRINIDAD", 15206, 15867, "Full section"),
    ("TURKS_AND_CAICOS_ISLANDS", 15868, 16641, "Full section"),
    # VIRGIN ISLANDS at 16639-16640 is reference within Turks section
    ("WESTERN_AUSTRALIA", 16642, 16876, "Full section"),
    ("WEST_AFRICA_SETTLEMENTS", 16877, 17271, "Full section (Sierra Leone and Gambia)"),
    ("WINDWARD_ISLANDS", 17272, 18453, "Full section (Barbados, Grenada, St. Lucia, St. Vincent, Tobago)"),
    # Note: TOBAGO has a separate section within WINDWARD ISLANDS starting at 18180
]

# Create output directory
output_dir = "/home/user/colonial_office_list/output/1878_manual_parsed"
os.makedirs(output_dir, exist_ok=True)

print(f"Extracting {len(colonies)} colonies to {output_dir}/\n")

# Metadata for JSON
metadata = {
    "year": 1878,
    "parser": "manual_llm",
    "total_colonies": len(colonies),
    "colonies": []
}

# Extract each colony
for colony_name, start_line, end_line, notes in colonies:
    print(f"Extracting {colony_name} (lines {start_line}-{end_line})...")

    # Extract lines (converting from 1-indexed to 0-indexed)
    colony_lines = lines[start_line-1:end_line]
    colony_text = ''.join(colony_lines)

    # Write to file
    output_file = os.path.join(output_dir, f"{colony_name}.txt")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(colony_text)

    # Add to metadata
    line_count = end_line - start_line + 1
    char_count = len(colony_text)

    metadata["colonies"].append({
        "name": colony_name,
        "start_line": start_line,
        "end_line": end_line,
        "line_count": line_count,
        "char_count": char_count,
        "file": f"{colony_name}.txt",
        "notes": notes
    })

    print(f"  Written {line_count} lines ({char_count} characters) to {colony_name}.txt")

# Write metadata JSON
metadata_file = "/home/user/colonial_office_list/output/1878_manual_parsed.json"
with open(metadata_file, 'w', encoding='utf-8') as f:
    json.dump(metadata, f, indent=2)

print(f"\nMetadata written to {metadata_file}")
print(f"\nExtraction complete! {len(colonies)} colonies extracted.")

# Print summary
print("\n=== SUMMARY ===")
print(f"Total colonies: {len(colonies)}")
print("\nColonies extracted:")
for colony in metadata["colonies"]:
    print(f"  - {colony['name']}: {colony['line_count']} lines")
