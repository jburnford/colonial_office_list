#!/usr/bin/env python3
"""
Parse Colonial Office List 1917 - Manual Colony Extraction
Identifies all colony boundaries and extracts individual colony sections
"""

import re
import json
import os
from pathlib import Path

# Read the olmocr file
olmocr_file = "/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1917/olmocr_results.md"
output_dir = "/home/user/colonial_office_list/output_3/1917_manual_parsed"
output_json = "/home/user/colonial_office_list/output_3/1917_manual_parsed.json"

print("Reading olmocr file...")
with open(olmocr_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Total lines: {len(lines)}")

# Known colony boundaries from manual inspection
# These are the major section headers in all caps
colony_boundaries = [
    (3591, "AUSTRALIA"),
    (3593, "THE COMMONWEALTH"),
    (4377, "NEW SOUTH WALES"),
    (5832, "QUEENSLAND"),
    (6417, "SOUTH AUSTRALIA"),
    (7500, "TASMANIA"),
    (8260, "COMMONWEALTH CONTROL"),
    (8599, "VICTORIA"),
    (9403, "WESTERN AUSTRALIA"),
    (10483, "THE NORTHERN TERRITORY"),
    (10863, "PAPUA"),
    (11106, "NORFOLK ISLAND"),
    (11121, "BAHAMAS"),
    (11494, "BARBADOS"),
    (12062, "BERMUDA"),
    (12418, "BRITISH GUIANA"),
    (13279, "BRITISH HONDURAS"),
    (13640, "DOMINION OF CANADA"),
    (16955, "CEYLON"),
    (18022, "CYPRUS"),
    (18781, "EAST AFRICA PROTECTORATE"),
    (19288, "FALKLAND ISLANDS"),
    (19569, "FIJI"),
    (20291, "THE GAMBIA"),
    (20702, "GIBRALTAR"),
    (20908, "THE GOLD COAST"),
    (21766, "HONG KONG"),
    (23141, "JAMAICA"),
    (24055, "THE LEEWARD ISLANDS"),
    (25529, "MALTA"),
    (26128, "MAURITIUS"),
    (26874, "NEWFOUNDLAND"),
    (27641, "NEW ZEALAND"),
    (28771, "NIGERIA"),
    (29733, "NYASALAND PROTECTORATE"),
    (30038, "ST. HELENA"),
    (30210, "SEYCHELLES"),
    (30531, "SIERRA LEONE"),
    (31094, "SOMALILAND PROTECTORATE"),
    (31246, "SOUTH AFRICA"),
    (33655, "BASUTOLAND"),
    (33795, "BECHUANALAND PROTECTORATE"),
    (33875, "SWAZILAND"),
    (34051, "RHODESIA"),
    (34682, "STRAITS SETTLEMENTS"),
    (36622, "TOBAGO"),
    (37308, "TRINIDAD AND TOBAGO"),
    (38019, "TURKS AND CAICOS ISLANDS"),
    (38195, "UGANDA"),
    (38624, "WEIHAIWEI"),
    (38688, "WESTERN PACIFIC"),
    (38980, "GRENA DA"),  # This appears to be GRENADA with OCR error
    (39312, "ST. LUCIA"),
    (39659, "ST. VINCENT"),
    (39928, "ZANZIBAR"),
]

# Sort by line number
colony_boundaries.sort(key=lambda x: x[0])

# Add end marker
colony_boundaries.append((40311, "APPENDIX TO PART II"))

print(f"\nFound {len(colony_boundaries)-1} potential colony sections")

# Create output directory
os.makedirs(output_dir, exist_ok=True)

# Extract colonies
colonies = []
for i in range(len(colony_boundaries) - 1):
    start_line = colony_boundaries[i][0]
    colony_name = colony_boundaries[i][1]
    end_line = colony_boundaries[i + 1][0] - 1

    # Extract content
    content_lines = lines[start_line-1:end_line]  # -1 because line numbers are 1-indexed
    content = ''.join(content_lines)

    # Create filename
    filename = colony_name.replace(" ", "_").replace("/", "_").replace("—", "_").upper() + ".md"
    filename = re.sub(r'[^\w\-_.]', '', filename)

    # Calculate stats
    char_count = len(content)
    line_count = len(content_lines)

    # Save file
    output_path = os.path.join(output_dir, filename)
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(content)

    # Add to metadata
    colony_data = {
        "colony_name": colony_name,
        "year": 1917,
        "start_line": start_line,
        "end_line": end_line,
        "char_count": char_count,
        "line_count": line_count,
        "filename": filename
    }
    colonies.append(colony_data)

    print(f"Extracted: {colony_name:40s} Lines {start_line:5d}-{end_line:5d} ({line_count:4d} lines)")

# Create JSON metadata
metadata = {
    "year": 1917,
    "source_file": "historical_document_pipeline/processed_pdfs/colonial-office-list-1917/olmocr_results.md",
    "total_colonies": len(colonies),
    "colonies": colonies,
    "processing_notes": {
        "parser": "Python manual boundary parser",
        "date": "2025-11-18",
        "method": "Manual boundary identification based on structural analysis",
        "colony_section_start": 3591,
        "colony_section_end": 40311,
        "notes": "1917 is mid-WWI. Document may include German territories captured during war."
    }
}

# Save JSON
with open(output_json, 'w', encoding='utf-8') as f:
    json.dump(metadata, f, indent=2, ensure_ascii=False)

print(f"\n✓ Saved {len(colonies)} colonies to {output_dir}/")
print(f"✓ Saved metadata to {output_json}")
print(f"\nTotal colonies extracted: {len(colonies)}")

# Check for German territories or WWI-related notes
print("\n" + "="*60)
print("ANALYZING FOR WWI CONTEXT AND GERMAN TERRITORIES")
print("="*60)

german_related = []
for colony in colonies:
    colony_name = colony['colony_name']
    filename = os.path.join(output_dir, colony['filename'])
    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read().lower()

    # Look for German, war, military, captured, occupied
    keywords = ['german', 'war', 'captured', 'occupied', 'military', 'enemy', 'conquest']
    matches = []
    for keyword in keywords:
        if keyword in content:
            matches.append(keyword)

    if matches:
        german_related.append({
            'colony': colony_name,
            'keywords': matches,
            'lines': f"{colony['start_line']}-{colony['end_line']}"
        })

if german_related:
    print("\nColonies with WWI/German-related content:")
    for item in german_related:
        print(f"  • {item['colony']:40s} - Keywords: {', '.join(item['keywords'])}")
else:
    print("\nNo obvious German territory references found in colony names.")

print("\n" + "="*60)
print("EXTRACTION COMPLETE")
print("="*60)
