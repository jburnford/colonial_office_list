#!/usr/bin/env python3
"""
Extract corrected 1889 colonies based on manual boundary verification.

CRITICAL CORRECTIONS:
- BRITISH NEW GUINEA was contaminated (4,256 lines) containing 3 colonies!
- Split into 3 separate colonies
- Add missing DOMINION OF CANADA (3,377 lines!)
- Fix CAPE OF GOOD HOPE to include missing main section

Total: 30 → 31 colonies (add missing DOMINION OF CANADA)
"""

import json
from pathlib import Path

# Source OCR file
source_file = Path('/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1889/olmocr_results.md')

# Output directory
output_dir = Path('/home/user/colonial_office_list/output_2/1889_manual_parsed')
output_dir.mkdir(parents=True, exist_ok=True)

# Read source file
print("Reading OCR source file...")
with open(source_file, 'r') as f:
    lines = f.readlines()

print(f"Total lines in source: {len(lines)}")
print("=" * 80)
print("EXTRACTING CORRECTED 1889 COLONIES")
print("=" * 80)
print()

# Load original metadata
with open('output/1889_manual_parsed.json', 'r') as f:
    original_data = json.load(f)

print(f"Original extraction had {original_data['total_colonies']} colonies")
print()

# Extract all existing colonies EXCEPT contaminated British New Guinea and incorrectly bounded Cape
print("GROUP A: Extracting colonies with correct boundaries...")
print()

extracted_colonies = []
skipped = []

for colony in original_data['colonies']:
    name = colony.get('name', 'Unknown')

    # Skip the contaminated British New Guinea
    if 'BRITISH NEW GUINEA' in name:
        skipped.append(name)
        print(f"⏭️  Skipping {name} (contaminated, will extract correctly)")
        continue

    # Skip Cape - will re-extract with correct boundaries
    if 'CAPE' in name:
        skipped.append(name)
        print(f"⏭️  Skipping {name} (incorrect boundaries, will re-extract)")
        continue

    # Extract this colony
    start = colony['start_line']
    end = colony['end_line']
    colony_lines = lines[start-1:end]

    # Write to file
    filename = colony.get('file', colony.get('filename', f"{name.replace(' ', '_')}.txt")).replace('.txt', '.md')
    output_file = output_dir / filename
    with open(output_file, 'w') as f:
        f.writelines(colony_lines)

    actual_lines = len(colony_lines)
    line_count = colony.get('line_count') or colony.get('num_lines', 0)
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
print("GROUP B: Fixing contaminated BRITISH NEW GUINEA...")
print("=" * 80)
print()

# Extract the 3 colonies that were contaminated together
corrected_colonies = [
    ('BRITISH_NEW_GUINEA', 4052, 4101, 'Was contaminated with Canada + Cape content'),
    ('DOMINION_OF_CANADA', 4102, 7478, 'COMPLETELY MISSING - recovered from contaminated file'),
    ('CAPE_OF_GOOD_HOPE', 7479, 9326, 'Was missing main section 7479-8307, incorrectly started at 8308'),
]

for colony_name, start, end, _ in corrected_colonies:
    # Extract lines
    colony_lines = lines[start-1:end]

    # Write to file
    output_file = output_dir / f"{colony_name}.md"
    with open(output_file, 'w') as f:
        f.writelines(colony_lines)

    actual_lines = len(colony_lines)
    display_name = colony_name.replace('_', ' ')

    if 'DOMINION' in colony_name:
        print(f"✅ {display_name}: {start}-{end} ({actual_lines} lines) **RECOVERED MISSING COLONY!**")
        note = 'COMPLETELY MISSING - was incorrectly merged into BRITISH NEW GUINEA file'
    elif 'BRITISH_NEW_GUINEA' in colony_name:
        print(f"✅ {display_name}: {start}-{end} ({actual_lines} lines) - Fixed from 4,256 contaminated lines")
        note = 'Was contaminated file of 4,256 lines containing 3 colonies'
    else:  # Cape
        print(f"✅ {display_name}: {start}-{end} ({actual_lines} lines) - Fixed boundaries, added missing section")
        note = 'Was incorrectly bounded 8308-9326, missing main colony section 7479-8307'

    extracted_colonies.append({
        'name': display_name,
        'filename': f"{colony_name}.md",
        'start_line': start,
        'end_line': end,
        'line_count': actual_lines,
        'extraction_method': 'corrected_contamination',
        'note': note
    })

# Sort by start_line
extracted_colonies.sort(key=lambda x: x['start_line'])

print()
print("=" * 80)
print("EXTRACTION COMPLETE")
print("=" * 80)
print()
print(f"Original colonies: {original_data['total_colonies']}")
print(f"Fixed: BRITISH NEW GUINEA contamination")
print(f"Recovered: DOMINION OF CANADA (was completely missing!)")
print(f"Fixed: CAPE OF GOOD HOPE boundaries")
print(f"Final total: {len(extracted_colonies)} colonies")
print()
print(f"Output directory: {output_dir}")
print()
print("Next step: Run create_1889_metadata.py to generate corrected metadata JSON")
