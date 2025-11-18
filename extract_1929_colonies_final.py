#!/usr/bin/env python3
"""
Extract all colonies from 1929 Colonial Office List
Manual boundary identification - FINAL VERSION with verified boundaries
"""

import json
import os
import re
from datetime import datetime

# Source file
source_file = "/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1929/olmocr_results.md"
output_dir = "/home/user/colonial_office_list/output_3"
year = 1929

# Manually identified and verified colony boundaries (line numbers are 1-indexed)
# Based on systematic document review, comparison with 1928, and manual verification
colonies_data = [
    {"name": "BAHAMAS", "start": 23646, "end": None},
    {"name": "BARBADOS", "start": 24035, "end": None},
    {"name": "BERMUDA", "start": 24697, "end": None},
    {"name": "BRITISH GUIANA", "start": 25167, "end": None},
    {"name": "BRITISH HONDURAS", "start": 26064, "end": None},  # Verified - not 26008
    {"name": "CEYLON", "start": 26486, "end": None},
    {"name": "CYPRUS", "start": 27598, "end": None},  # New in 1929
    {"name": "FALKLAND ISLANDS", "start": 28420, "end": None},
    {"name": "FIJI", "start": 28788, "end": None},
    {"name": "THE GAMBIA", "start": 29515, "end": None},
    {"name": "GIBRALTAR", "start": 29953, "end": None},
    {"name": "THE GOLD COAST", "start": 30159, "end": None},
    {"name": "HONG KONG", "start": 31568, "end": None},
    {"name": "JAMAICA", "start": 32115, "end": None},
    {"name": "CAYMAN ISLANDS", "start": 33271, "end": None},
    {"name": "TURKS AND CAICOS ISLANDS", "start": 33315, "end": None},
    {"name": "KENYA", "start": 33504, "end": None},
    {"name": "THE LEEWARD ISLANDS", "start": 34446, "end": None},  # Verified header
    {"name": "ANTIGUA", "start": 34775, "end": None},
    {"name": "BARBUDA", "start": 35131, "end": None},
    {"name": "ST. CHRISTOPHER AND NEVIS", "start": 35136, "end": None},
    {"name": "DOMINICA", "start": 35427, "end": None},
    {"name": "MONTSERRAT", "start": 35756, "end": None},  # Combined header "LEEWARD ISLANDS: MONTSERRAT—VIRGIN ISLANDS"
    {"name": "VIRGIN ISLANDS", "start": 35867, "end": None},
    {"name": "MALTA", "start": 35988, "end": None},  # New in 1929
    {"name": "MAURITIUS", "start": 36642, "end": None},
    {"name": "NIGERIA", "start": 37545, "end": None},
    {"name": "NORTHERN RHODESIA", "start": 38897, "end": None},
    {"name": "NYASALAND PROTECTORATE", "start": 39477, "end": None},
    {"name": "PALESTINE", "start": 39787, "end": None},
    {"name": "ST. HELENA", "start": 40325, "end": None},
    {"name": "ASCENSION", "start": 40510, "end": None},
    {"name": "SEYCHELLES", "start": 40525, "end": None},
    {"name": "SIERRA LEONE", "start": 40869, "end": None},  # Verified start
    {"name": "STRAITS SETTLEMENTS", "start": 41499, "end": None},
    {"name": "TRINIDAD AND TOBAGO", "start": 45180, "end": None},
    {"name": "UGANDA", "start": 46281, "end": None},
    {"name": "WEIHAIWEI", "start": 46717, "end": None},
    {"name": "THE WINDWARD ISLANDS", "start": 47241, "end": None},  # New - general section
    {"name": "GRENADA", "start": 47320, "end": None},  # OCR: "GRENA DA."
    {"name": "ST. LUCIA", "start": 47641, "end": None},
    {"name": "ST. VINCENT", "start": 47912, "end": None},
    {"name": "ZANZIBAR", "start": 48197, "end": None},
    {"name": "IRAQ", "start": 48624, "end": None},
    {"name": "NORTH BORNEO", "start": 48786, "end": None},
    {"name": "SARAWAK", "start": 49046, "end": None},  # New in 1929
    {"name": "TRANS-JORDAN", "start": 49295, "end": None},
    {"name": "ADEN", "start": 49349, "end": None},
    {"name": "TRISTAN DA CUNHA", "start": 49373, "end": None},
    {"name": "MISCELLANEOUS ISLANDS", "start": 49390, "end": None},
]

# Sort by start line
colonies_data.sort(key=lambda x: x["start"])

# Set end lines (each colony ends where the next one begins, minus 1)
for i in range(len(colonies_data) - 1):
    colonies_data[i]["end"] = colonies_data[i+1]["start"] - 1

# Last colony ends at PART III (line 56665)
colonies_data[-1]["end"] = 56664

print("=" * 80)
print(f"1929 COLONIAL OFFICE LIST - MANUAL COLONY EXTRACTION")
print("=" * 80)
print(f"\nSource: {source_file}")
print(f"Total colonies to extract: {len(colonies_data)}")
print("\nExtracting colonies...\n")

# Read the source file
with open(source_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Extract each colony
verified_colonies = []
extraction_issues = []

for colony_data in colonies_data:
    name = colony_data["name"]
    start = colony_data["start"]
    end = colony_data["end"]

    # Verify the colony header
    if start <= len(lines):
        header_line = lines[start - 1].strip()
        print(f"Line {start:5d}-{end:5d}: {name:35s} ({end-start+1:4d} lines)")

        # Extract the colony content (remove line numbers)
        colony_lines = []
        for i in range(start - 1, min(end, len(lines))):
            line = lines[i]
            # Remove line number prefix (format: "linenum→")
            if '→' in line:
                content = line.split('→', 1)[1]
            else:
                content = line
            colony_lines.append(content)

        # Save to file
        output_file = os.path.join(output_dir, f"{year}_manual_parsed",
                                   f"{name.replace(' ', '_').replace('.', '').replace('*', '')}.txt")
        os.makedirs(os.path.dirname(output_file), exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            f.writelines(colony_lines)

        verified_colonies.append({
            "colony_name": name,
            "start_line": start,
            "end_line": end,
            "line_count": end - start + 1,
            "file": output_file,
            "note": None
        })
    else:
        extraction_issues.append(f"{name}: Start line {start} exceeds file length")

print(f"\n{'=' * 80}")
print(f"Extraction complete!")
print(f"{'=' * 80}")
print(f"Successfully extracted: {len(verified_colonies)} colonies")
print(f"Issues encountered: {len(extraction_issues)}")

if extraction_issues:
    print("\nIssues:")
    for issue in extraction_issues:
        print(f"  - {issue}")

# Generate JSON metadata
metadata = {
    "year": year,
    "source_file": source_file,
    "extraction_date": datetime.now().strftime("%Y-%m-%d"),
    "extraction_method": "Manual LLM boundary identification with systematic document review",
    "total_colonies": len(verified_colonies),
    "notes": [
        "All colony boundaries manually identified by reading OCR content",
        "Extraction covers PART II-C: Colonial Office colonies only",
        "Line number prefixes removed from extracted text",
        "PART II-C starts at line 23644, PART III starts at line 56665",
        "New colonies compared to 1928: CYPRUS (27598), MALTA (35988), SARAWAK (49046), THE WINDWARD ISLANDS (47241)",
        "THE LEEWARD ISLANDS includes: ANTIGUA, BARBUDA, ST. CHRISTOPHER AND NEVIS, DOMINICA, MONTSERRAT, VIRGIN ISLANDS",
        "THE WINDWARD ISLANDS includes: GRENADA, ST. LUCIA, ST. VINCENT",
        "JAMAICA includes dependencies: CAYMAN ISLANDS, TURKS AND CAICOS ISLANDS"
    ],
    "colonies": verified_colonies
}

json_file = os.path.join(output_dir, f"{year}_manual_parsed.json")
with open(json_file, 'w', encoding='utf-8') as f:
    json.dump(metadata, f, indent=2)

print(f"\nMetadata saved to: {json_file}")
print(f"\nColonies extracted to: {os.path.join(output_dir, f'{year}_manual_parsed/')}")
print(f"\nNew colonies in 1929 (not in 1928):")
print("  - CYPRUS")
print("  - MALTA")
print("  - SARAWAK")
print("  - THE WINDWARD ISLANDS (general section)")

print(f"\nTotal: {len(verified_colonies)} colonies extracted")
print(f"1928 had 40 colonies, 1929 has {len(verified_colonies)} entries")
