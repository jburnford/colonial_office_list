#!/usr/bin/env python3
"""
Extract corrected 1886 colonies based on manual boundary verification.

VERIFIED CORRECTION:
- Split WEST AFRICA SETTLEMENTS into 2 colonies:
  * SIERRA LEONE (24884-25333)
  * THE GAMBIA (25334-25548)

Total: 34 → 35 colonies
"""

import json
from pathlib import Path

# Source OCR file
source_file = Path('/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1886/olmocr_results.md')

# Output directory
output_dir = Path('/home/user/colonial_office_list/output_2/1886_manual_parsed')
output_dir.mkdir(parents=True, exist_ok=True)

# Read source file
print("Reading OCR source file...")
with open(source_file, 'r') as f:
    lines = f.readlines()

print(f"Total lines in source: {len(lines)}")
print("=" * 80)
print("EXTRACTING CORRECTED 1886 COLONIES")
print("=" * 80)
print()

# Load original metadata
with open('output/1886_manual_parsed.json', 'r') as f:
    original_data = json.load(f)

print(f"Original extraction had {original_data['total_colonies']} colonies")
print()

# Extract all existing colonies EXCEPT WEST_AFRICA_SETTLEMENTS
print("GROUP A: Extracting 33 existing colonies (excluding WEST AFRICA SETTLEMENTS)...")
print()

extracted_colonies = []
skipped = []

for colony in original_data['colonies']:
    name = colony.get('colony', colony.get('name', 'Unknown'))

    if 'WEST' in name and 'AFRICA' in name:
        skipped.append(name)
        print(f"⏭️  Skipping {name} (will split into 2 colonies)")
        continue

    # Extract this colony
    start = colony['start_line']
    end = colony['end_line']
    colony_lines = lines[start-1:end]

    # Write to file
    filename = colony.get('filename', f"{name}.txt").replace('.txt', '.md')
    output_file = output_dir / filename
    with open(output_file, 'w') as f:
        f.writelines(colony_lines)

    actual_lines = len(colony_lines)
    print(f"✅ {name}: {start}-{end} ({actual_lines} lines)")

    extracted_colonies.append({
        'name': name,
        'filename': filename,
        'start_line': start,
        'end_line': end,
        'line_count': actual_lines,
        'extraction_method': 'original_boundaries'
    })

print()
print("=" * 80)
print("GROUP B: Splitting WEST AFRICA SETTLEMENTS into 2 colonies...")
print("=" * 80)
print()

# Define the 2 West African colonies (post-1874 structure)
west_african_colonies = [
    ('SIERRA_LEONE', 24884, 25333),
    ('THE_GAMBIA', 25334, 25548),
]

for colony_name, start, end in west_african_colonies:
    # Extract lines
    colony_lines = lines[start-1:end]

    # Write to file
    output_file = output_dir / f"{colony_name}.md"
    with open(output_file, 'w') as f:
        f.writelines(colony_lines)

    actual_lines = len(colony_lines)
    display_name = colony_name.replace('_', ' ')
    print(f"✅ {display_name}: {start}-{end} ({actual_lines} lines)")

    extracted_colonies.append({
        'name': display_name,
        'filename': f"{colony_name}.md",
        'start_line': start,
        'end_line': end,
        'line_count': actual_lines,
        'extraction_method': 'split_from_umbrella',
        'original_umbrella': 'WEST AFRICA SETTLEMENTS',
        'note': 'Post-1874 structure: Gold Coast & Lagos separated, Sierra Leone + Gambia remain as West Africa Settlements'
    })

# Sort by start_line
extracted_colonies.sort(key=lambda x: x['start_line'])

print()
print("=" * 80)
print("EXTRACTION COMPLETE")
print("=" * 80)
print()
print(f"Original colonies: {original_data['total_colonies']}")
print(f"Removed: WEST AFRICA SETTLEMENTS (1 umbrella)")
print(f"Added: SIERRA LEONE + THE GAMBIA (2 colonies)")
print(f"Final total: {len(extracted_colonies)} colonies")
print()
print(f"Output directory: {output_dir}")
print()
print("Next step: Run create_1886_metadata.py to generate corrected metadata JSON")
