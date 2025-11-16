#!/usr/bin/env python3
"""
Extract corrected 1890 colonies based on manual boundary verification.

VERIFIED CORRECTIONS:
- BRITISH NEW GUINEA: Was 4,574 lines (4342-8915) → Fixed to 44 lines (4342-4385)
- DOMINION OF CANADA: 3,542 lines (4386-7927) - COMPLETELY MISSING from metadata!
- CAPE OF GOOD HOPE: Was 869 lines (8916-9784) → Fixed to 1,857 lines (7928-9784)

Total: 32 → 33 colonies (+1 recovered)
"""

import json
from pathlib import Path

# Source OCR file
source_file = Path('/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1890/olmocr_results.md')

# Output directory
output_dir = Path('/home/user/colonial_office_list/output_2/1890_manual_parsed')
output_dir.mkdir(parents=True, exist_ok=True)

# Read source file
print("Reading OCR source file...")
with open(source_file, 'r') as f:
    lines = f.readlines()

print(f"Total lines in source: {len(lines)}")
print("=" * 80)
print("EXTRACTING CORRECTED 1890 COLONIES")
print("=" * 80)
print()

# Load original metadata
with open('output_2/1890_manual_parsed.json', 'r') as f:
    original_data = json.load(f)

print(f"Original extraction had {original_data['total_colonies']} colonies")
print()

# Extract all existing colonies EXCEPT contaminated ones
print("GROUP A: Extracting 30 existing colonies (excluding contaminated files)...")
print()

extracted_colonies = []
skipped = []

for colony in original_data['colonies']:
    name = colony.get('name', colony.get('colony', 'Unknown'))
    
    # Skip contaminated files - we'll re-extract them correctly
    if 'BRITISH NEW GUINEA' in name:
        skipped.append(name)
        print(f"⏭️  Skipping {name} (contaminated - will re-extract)")
        continue
    
    if 'CAPE OF GOOD HOPE' in name:
        skipped.append(name)
        print(f"⏭️  Skipping {name} (missing main section - will re-extract)")
        continue
    
    # Extract this colony
    start = colony['start_line']
    end = colony['end_line']
    colony_lines = lines[start-1:end]
    
    # Write to file
    filename = colony.get('filename', colony.get('file', f"{name}.txt")).replace('.txt', '.md')
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
print(f"Skipped {len(skipped)} contaminated files: {', '.join(skipped)}")
print()
print("=" * 80)
print("GROUP B: Re-extracting 3 corrected colonies...")
print("=" * 80)
print()

# Define the corrected colonies
corrected_colonies = [
    ('BRITISH_NEW_GUINEA', 4342, 4385, 'Was contaminated (4,574 lines containing 3 colonies). Fixed to actual colony content.'),
    ('DOMINION_OF_CANADA', 4386, 7927, 'COMPLETELY MISSING from metadata! Recovered 3,542 lines.'),
    ('CAPE_OF_GOOD_HOPE', 7928, 9784, 'Was missing main section (started at 8916). Fixed to include full colony content from 7928.'),
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
        'name': display_name,
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
print(f"Contaminated files fixed: 2 (BRITISH NEW GUINEA, CAPE OF GOOD HOPE)")
print(f"Recovered colony: 1 (DOMINION OF CANADA - 3,542 lines!)")
print(f"Final total: {len(extracted_colonies)} colonies")
print()
print(f"Output directory: {output_dir}")
print()
print("Next step: Run create_1890_metadata.py to generate corrected metadata JSON")
