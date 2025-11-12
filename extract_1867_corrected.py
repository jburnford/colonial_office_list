#!/usr/bin/env python3
"""
Extract corrected 1867 colonies based on manual boundary verification.

VERIFIED CORRECTIONS:
- Split WEST_AFRICAN_SETTLEMENTS (121 KB) into 4 colonies:
  * SIERRA LEONE (13286-13406)
  * THE GAMBIA (13407-13519)
  * GOLD COAST (13520-13590)
  * LAGOS (13591-13683)
- Add missing VANCOUVER'S ISLAND (13684-13712)
  (Was incorrectly included in WEST_AFRICAN_SETTLEMENTS)

Total: 44 → 48 colonies
"""

import json
from pathlib import Path

# Source OCR file
source_file = Path('/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1867/olmocr_results.md')

# Output directory
output_dir = Path('/home/user/colonial_office_list/output_2/1867_manual_parsed')
output_dir.mkdir(parents=True, exist_ok=True)

# Read source file
print("Reading OCR source file...")
with open(source_file, 'r') as f:
    lines = f.readlines()

print(f"Total lines in source: {len(lines)}")
print("=" * 80)
print("EXTRACTING CORRECTED 1867 COLONIES")
print("=" * 80)
print()

# Load original metadata to get existing colonies
with open('output/1867_manual_parsed.json', 'r') as f:
    original_data = json.load(f)

print(f"Original extraction had {original_data['total_colonies']} colonies")
print()

# Extract all existing colonies EXCEPT WEST_AFRICAN_SETTLEMENTS
print("GROUP A: Extracting 43 existing colonies (excluding WEST_AFRICAN_SETTLEMENTS)...")
print()

extracted_colonies = []
skipped = []

for colony in original_data['colonies']:
    if 'WEST' in colony['name'] and 'AFRICA' in colony['name']:
        skipped.append(colony['name'])
        print(f"⏭️  Skipping {colony['name']} (will split into 4 colonies)")
        continue

    # Extract this colony
    start = colony['start_line']
    end = colony['end_line']
    colony_lines = lines[start-1:end]

    # Write to file
    filename = colony['file'].replace('.txt', '.md')
    output_file = output_dir / filename
    with open(output_file, 'w') as f:
        f.writelines(colony_lines)

    actual_lines = len(colony_lines)
    print(f"✅ {colony['name']}: {start}-{end} ({actual_lines} lines)")

    extracted_colonies.append({
        'name': colony['name'],
        'filename': filename,
        'start_line': start,
        'end_line': end,
        'line_count': actual_lines,
        'extraction_method': 'original_boundaries'
    })

print()
print("=" * 80)
print("GROUP B: Splitting WEST_AFRICAN_SETTLEMENTS into 4 colonies...")
print("=" * 80)
print()

# Define the 4 West African colonies
west_african_colonies = [
    ('SIERRA_LEONE', 13286, 13406),
    ('THE_GAMBIA', 13407, 13519),
    ('GOLD_COAST', 13520, 13590),
    ('LAGOS', 13591, 13683),
]

for colony_name, start, end in west_african_colonies:
    # Extract lines
    colony_lines = lines[start-1:end]

    # Write to file
    output_file = output_dir / f"{colony_name}.md"
    with open(output_file, 'w') as f:
        f.writelines(colony_lines)

    actual_lines = len(colony_lines)
    print(f"✅ {colony_name.replace('_', ' ')}: {start}-{end} ({actual_lines} lines)")

    extracted_colonies.append({
        'name': colony_name.replace('_', ' '),
        'filename': f"{colony_name}.md",
        'start_line': start,
        'end_line': end,
        'line_count': actual_lines,
        'extraction_method': 'split_from_umbrella',
        'original_umbrella': 'WEST_AFRICAN_SETTLEMENTS'
    })

print()
print("=" * 80)
print("GROUP C: Adding missing VANCOUVER'S ISLAND...")
print("=" * 80)
print()

# Add missing VANCOUVER'S ISLAND
vancouver_name = 'VANCOUVERS_ISLAND'
vancouver_start = 13684
vancouver_end = 13712

vancouver_lines = lines[vancouver_start-1:vancouver_end]
output_file = output_dir / f"{vancouver_name}.md"
with open(output_file, 'w') as f:
    f.writelines(vancouver_lines)

actual_lines = len(vancouver_lines)
print(f"✅ VANCOUVER'S ISLAND: {vancouver_start}-{vancouver_end} ({actual_lines} lines)")
print(f"   Note: Was incorrectly merged into WEST_AFRICAN_SETTLEMENTS")

extracted_colonies.append({
    'name': "VANCOUVER'S ISLAND",
    'filename': f"{vancouver_name}.md",
    'start_line': vancouver_start,
    'end_line': vancouver_end,
    'line_count': actual_lines,
    'extraction_method': 'recovered_missing',
    'note': 'Was incorrectly included in WEST_AFRICAN_SETTLEMENTS umbrella file'
})

print()
print("=" * 80)
print("EXTRACTION COMPLETE")
print("=" * 80)
print()
print(f"Original colonies: {original_data['total_colonies']}")
print(f"Removed: WEST_AFRICAN_SETTLEMENTS (1 umbrella)")
print(f"Added: 4 West African colonies + VANCOUVER'S ISLAND (5 total)")
print(f"Final total: {len(extracted_colonies)} colonies")
print()
print(f"Output directory: {output_dir}")
print()
print("Next step: Run create_1867_metadata.py to generate corrected metadata JSON")
