#!/usr/bin/env python3
"""
Extract all colony sections from the 1878 Colonial Office List.
This script uses manually identified colony boundaries based on comprehensive document inspection.
"""

import re
import json
import os
from datetime import date

# Configuration
OCR_FILE = "/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1878/olmocr_results.md"
OUTPUT_DIR = "/home/user/colonial_office_list/output_3/1878_manual_parsed"
JSON_FILE = "/home/user/colonial_office_list/output_3/1878_manual_parsed.json"
REPORT_FILE = "/home/user/colonial_office_list/output_3/1878_PARSING_REPORT.md"

# Read the OCR file
print("Reading OCR file...")
with open(OCR_FILE, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Total lines in file: {len(lines)}")

# Manually identified colony sections based on document inspection
# PART II starts at line 1184 (Colonial Governors table)
# Colonies content starts around line 1343 (BAHAMAS)
# PART III (EMIGRATION) starts at line 18442
#
# Format: (colony_name, start_line, end_line, notes)

colonies = [
    ("BAHAMAS", 1343, 1576, "First colony in Part II"),
    ("BERMUDAS", 1585, 1846, "Also called Somers' Islands"),
    ("BRITISH_GUIANA", 1853, 2474, "Includes Demerara, Essequebo, and Berbice"),
    ("DOMINION_OF_CANADA", 2475, 4263, "Includes all Canadian provinces"),
    ("CAPE_OF_GOOD_HOPE", 4264, 5589, "South African colony"),
    ("CEYLON", 5590, 6162, "Indian Ocean island"),
    ("FALKLAND_ISLANDS", 6163, 6270, "South Atlantic islands"),
    ("FIJI", 6271, 6357, "Pacific islands"),
    ("GIBRALTAR", 6358, 6464, "Mediterranean British territory"),
    ("THE_GOLD_COAST", 6465, 6541, "West African colony (before Lagos)"),
    ("LAGOS", 6542, 7268, "West African settlement, part of Gold Coast"),
    ("HELIGOLAND", 7269, 7309, "North Sea island"),
    ("HONDURAS", 7310, 7525, "Central American British Honduras"),
    ("HONG_KONG", 7526, 7794, "Chinese island colony"),
    ("JAMAICA", 7795, 8437, "Caribbean island colony"),
    ("LABUAN", 8438, 8810, "Borneo island"),
    ("LEEWARD_ISLANDS", 8811, 9534, "Caribbean island federation"),
    ("ANGUILLA", 9535, 9548, "Small Caribbean island, part of Leeward Islands"),
    ("VIRGIN_ISLANDS", 9549, 9792, "Caribbean islands, part of Leeward Islands"),
    ("MALTA", 9793, 10212, "Mediterranean island"),
    ("MAURITIUS", 10213, 10814, "Indian Ocean island"),
    ("MONTSERRAT", 10815, 10887, "Caribbean island, part of Leeward Islands"),
    ("NATAL", 10891, 11285, "South African colony"),
    ("NEWFOUNDLAND", 11286, 11520, "North American island"),
    ("NEW_SOUTH_WALES", 11521, 12284, "Australian colony"),
    ("NEW_ZEALAND", 12285, 12800, "Pacific colony"),
    ("QUEENSLAND", 12801, 13289, "Australian colony"),
    ("SOUTH_AUSTRALIA", 13290, 14171, "Australian colony"),
    ("STRAITS_SETTLEMENTS", 14172, 14510, "Southeast Asian settlements"),
    ("TASMANIA", 14511, 15106, "Australian island colony"),
    ("THE_TRANSVAAL", 15107, 15205, "South African territory"),
    ("TRINIDAD", 15206, 15867, "Caribbean island"),
    ("TURKS_AND_CAICOS_ISLANDS", 15868, 16468, "Caribbean islands"),
    ("VICTORIA", 16469, 16641, "Australian colony"),
    ("WESTERN_AUSTRALIA", 16642, 16828, "Australian colony"),
    ("WEST_AFRICA_GAMBIA", 16829, 16880, "West African settlements - Gambia"),
    ("SIERRA_LEONE", 16881, 17271, "West African colony"),
    ("WINDWARD_ISLANDS", 17272, 18441, "Caribbean island federation, includes Barbados, St. Vincent, St. Lucia, Grenada, Tobago"),
]

# Create output directory
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Extract colonies
extraction_data = {
    "year": 1878,
    "source_file": "historical_document_pipeline/processed_pdfs/colonial-office-list-1878/olmocr_results.md",
    "extraction_date": str(date.today()),
    "extraction_method": "Manual LLM boundary identification with systematic document review",
    "total_colonies": len(colonies),
    "notes": [
        "All colony boundaries manually identified by reading OCR content",
        "PART II (Colonies) runs from line ~1184 to line 18441",
        "PART III (Emigration) starts at line 18442",
        "Line number prefixes removed from extracted text",
        "Some colonies contain sub-sections (e.g., Leeward Islands, Windward Islands)",
        "Windward Islands section includes Barbados, Tobago, St. Vincent, St. Lucia, and Grenada",
        "Leeward Islands section includes Antigua, Montserrat, Nevis, St. Kitts, Dominica, Virgin Islands, Anguilla",
        "Some headers may have OCR errors (punctuation, spacing)"
    ],
    "colonies": []
}

print(f"\nExtracting {len(colonies)} colonies...\n")

for colony_name, start_line, end_line, note in colonies:
    print(f"Extracting {colony_name} (lines {start_line}-{end_line})...")

    # Extract the lines
    colony_lines = lines[start_line-1:end_line]

    # Remove line number prefixes (format: "  1234→text")
    cleaned_lines = []
    for line in colony_lines:
        # Match pattern like "  1234→" at the start
        cleaned = re.sub(r'^\s*\d+→', '', line)
        cleaned_lines.append(cleaned)

    # Write to file
    output_file = os.path.join(OUTPUT_DIR, f"{colony_name}.txt")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.writelines(cleaned_lines)

    # Add to metadata
    colony_info = {
        "colony_name": colony_name.replace('_', ' '),
        "start_line": start_line,
        "end_line": end_line,
        "line_count": end_line - start_line + 1,
        "file": output_file,
        "note": note if note else None
    }
    extraction_data["colonies"].append(colony_info)

    print(f"  → Written to {output_file} ({len(cleaned_lines)} lines)")

# Write JSON metadata
print(f"\nWriting metadata to {JSON_FILE}...")
with open(JSON_FILE, 'w', encoding='utf-8') as f:
    json.dump(extraction_data, f, indent=2)

# Generate parsing report
print(f"Generating parsing report to {REPORT_FILE}...")
report = f"""# 1878 Colonial Office List - Extraction Report

## Summary

- **Extraction Date**: {extraction_data['extraction_date']}
- **Source File**: {extraction_data['source_file']}
- **Total Colonies Extracted**: {extraction_data['total_colonies']}
- **Extraction Method**: {extraction_data['extraction_method']}

## Methodology

1. Read the entire 1878 OCR results file ({len(lines):,} lines)
2. Manually identified colony section boundaries by reading content
3. Identified PART II (Colonies) boundaries: lines ~1184 to 18441
4. PART III (Emigration) starts at line 18442
5. Extracted each colony to individual text files with line number prefixes removed
6. Generated JSON metadata with boundaries and statistics

## Colonies Extracted

| Colony Name | Start Line | End Line | Lines | Notes |
|-------------|-----------|----------|-------|-------|
"""

for colony in extraction_data["colonies"]:
    name = colony["colony_name"]
    start = colony["start_line"]
    end = colony["end_line"]
    count = colony["line_count"]
    note = colony.get("note", "")
    report += f"| {name} | {start} | {end} | {count} | {note} |\n"

report += f"""

## Notes

- {chr(10).join(f"- {note}" for note in extraction_data['notes'])}

## Files Generated

1. **Individual Colony Files**: {extraction_data['total_colonies']} files in `1878_manual_parsed/`
2. **JSON Metadata**: `1878_manual_parsed.json`
3. **This Report**: `1878_PARSING_REPORT.md`

## Structure

The 1878 Colonial Office List is organized as follows:
- **PART I**: Colonial Office administration and staff
- **PART II**: Individual colony sections (this extraction)
- **PART III**: Emigration information

## Special Sections

### Leeward Islands
The Leeward Islands section includes several sub-colonies:
- Antigua
- Montserrat
- Nevis
- St. Kitts
- Dominica
- Virgin Islands
- Anguilla

### Windward Islands
The Windward Islands section includes:
- Barbados
- St. Vincent
- St. Lucia
- Grenada
- Tobago

### West Africa
West African territories are organized as:
- The Gambia
- Sierra Leone
- Gold Coast (including Lagos)

## Extraction Complete

All {extraction_data['total_colonies']} colonies have been successfully extracted from the 1878 Colonial Office List.
"""

with open(REPORT_FILE, 'w', encoding='utf-8') as f:
    f.write(report)

print(f"\n{'='*60}")
print(f"EXTRACTION COMPLETE")
print(f"{'='*60}")
print(f"Total colonies extracted: {len(colonies)}")
print(f"Output directory: {OUTPUT_DIR}")
print(f"JSON metadata: {JSON_FILE}")
print(f"Parsing report: {REPORT_FILE}")
print(f"{'='*60}\n")
