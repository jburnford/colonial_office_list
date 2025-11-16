#!/usr/bin/env python3
"""
Extract corrected 1897 colonies based on manual boundary verification.

VERIFIED CORRECTIONS:
- BRITISH NEW GUINEA: Was 1,796 lines (3509-5305) → Fixed to 78 lines (3510-3587)
- DOMINION OF CANADA: 2,710 lines (3588-6297) - COMPLETELY MISSING from metadata!
- CAPE OF GOOD HOPE: 2,334 lines (6297-8630) - Already correct in metadata

Total: 39 → 40 colonies (+1 recovered)
"""

import json
from pathlib import Path

# Source OCR file
source_file = Path('/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1897/olmocr_results.md')

# Output directory
output_dir = Path('/home/user/colonial_office_list/output_2/1897_manual_parsed')
output_dir.mkdir(parents=True, exist_ok=True)

# Read source file
print("Reading OCR source file...")
with open(source_file, 'r') as f:
    lines = f.readlines()

print(f"Total lines in source: {len(lines)}")
print("=" * 80)
print("EXTRACTING CORRECTED 1897 COLONIES")
print("=" * 80)
print()

# Load original metadata
with open('output_2/1897_manual_parsed.json', 'r') as f:
    original_data = json.load(f)

print(f"Original extraction had {original_data['total_colonies']} colonies")
print()

# Extract all existing colonies EXCEPT contaminated British New Guinea
print("GROUP A: Extracting 38 existing colonies (excluding contaminated British New Guinea)...")
print()

extracted_colonies = []
skipped = []

for colony in original_data['colonies']:
    name = colony.get('colony_name', colony.get('name', 'Unknown'))
    
    # Skip contaminated British New Guinea - we'll re-extract it correctly
    if 'BRITISH NEW GUINEA' in name:
        skipped.append(name)
        print(f"⏭️  Skipping {name} (contaminated - will re-extract)")
        continue
    
    # Extract this colony
    start = colony['start_line']
    end = colony['end_line']
    colony_lines = lines[start-1:end]
    
    # Write to file
    filename = colony.get('filename', f"{name}.md")
    output_file = output_dir / filename
    with open(output_file, 'w') as f:
        f.writelines(colony_lines)
    
    actual_lines = len(colony_lines)
    print(f"✅ {name}: {start}-{end} ({actual_lines} lines)")
    
    extracted_colonies.append({
        'colony_name': name,
        'filename': filename,
        'start_line': start,
        'end_line': end,
        'line_count': actual_lines,
        'extraction_method': 'original_boundaries'
    })

print()
print(f"Skipped {len(skipped)} contaminated file: {', '.join(skipped)}")
print()
print("=" * 80)
print("GROUP B: Re-extracting 2 corrected colonies...")
print("=" * 80)
print()

# Define the corrected colonies
corrected_colonies = [
    ('BRITISH_NEW_GUINEA', 3510, 3587, 'Was contaminated (1,796 lines containing 2 colonies). Fixed to actual colony content.'),
    ('DOMINION_OF_CANADA', 3588, 6297, 'COMPLETELY MISSING from metadata! Recovered 2,710 lines.'),
]

for colony_name, start, end, note in corrected_colonies:
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
        'colony_name': display_name,
        'filename': f"{colony_name}.md",
        'start_line': start,
        'end_line': end,
        'line_count': actual_lines,
        'extraction_method': 'contamination_fix',
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
print(f"Contaminated file fixed: 1 (BRITISH NEW GUINEA)")
print(f"Recovered colony: 1 (DOMINION OF CANADA)")
print(f"Cape of Good Hope: Already correct, kept unchanged")
print(f"Final total: {len(extracted_colonies)} colonies")
print()
print(f"Output directory: {output_dir}")
print()
print("Next step: Run create_1897_metadata.py to generate corrected metadata JSON")
