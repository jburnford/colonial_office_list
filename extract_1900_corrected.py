#!/usr/bin/env python3
"""
Extract corrected 1900 colonies based on manual boundary verification.

VERIFIED CORRECTIONS:
- BRITISH NEW GUINEA: Was 945 lines (4346-5291) → Fixed to 138 lines (4346-4483)
- DOMINION OF CANADA: 807 lines (4484-5290) - COMPLETELY MISSING from metadata!
  - Note: "CANADA" at 6599-7250 is just a subsection within another colony
- CAPE OF GOOD HOPE: Fix boundary (7250→7251)

Total: 50 → 51 colonies (+1 recovered)
"""

import json
from pathlib import Path

# Source OCR file
source_file = Path('/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1900/olmocr_results.md')

# Output directory
output_dir = Path('/home/user/colonial_office_list/output_2/1900_manual_parsed')
output_dir.mkdir(parents=True, exist_ok=True)

# Read source file
print("Reading OCR source file...")
with open(source_file, 'r') as f:
    lines = f.readlines()

print(f"Total lines in source: {len(lines)}")
print("=" * 80)
print("EXTRACTING CORRECTED 1900 COLONIES")
print("=" * 80)
print()

# Load original metadata
with open('output_2/1900_manual_parsed.json', 'r') as f:
    original_data = json.load(f)

print(f"Original extraction had {original_data['total_colonies']} colonies")
print()

# Extract all existing colonies EXCEPT contaminated ones
print("GROUP A: Extracting 48 existing colonies (excluding contaminated files)...")
print()

extracted_colonies = []
skipped = []

for colony in original_data['colonies']:
    name = colony.get('colony_name', colony.get('name', 'Unknown'))
    
    # Skip contaminated British New Guinea
    if 'BRITISH NEW GUINEA' in name:
        skipped.append(name)
        print(f"⏭️  Skipping {name} (contaminated - will re-extract)")
        continue
    
    # Skip fake "CANADA" subsection (6599-7250)
    if name == 'CANADA':
        skipped.append(name)
        print(f"⏭️  Skipping {name} (subsection, not main colony - will extract real Dominion)")
        continue
    
    # Skip Cape (needs boundary fix)
    if 'CAPE OF GOOD HOPE' in name:
        skipped.append(name)
        print(f"⏭️  Skipping {name} (boundary fix needed - will re-extract)")
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
print(f"Skipped {len(skipped)} files: {', '.join(skipped)}")
print()
print("=" * 80)
print("GROUP B: Re-extracting 3 corrected colonies...")
print("=" * 80)
print()

# Define the corrected colonies
corrected_colonies = [
    ('BRITISH_NEW_GUINEA', 4346, 4483, 'Was contaminated (945 lines containing 2 colonies). Fixed to actual colony content.'),
    ('DOMINION_OF_CANADA', 4484, 5290, 'COMPLETELY MISSING from metadata! Recovered 807 lines. Note: "CANADA" at 6599-7250 was just a subsection.'),
    ('CAPE_OF_GOOD_HOPE', 7251, 9803, 'Boundary fix (was 7250-9803, corrected to 7251-9803).'),
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
print(f"Fake subsection removed: 1 (CANADA 6599-7250)")
print(f"Recovered colony: 1 (DOMINION OF CANADA 4484-5290)")
print(f"Boundary fix: 1 (CAPE OF GOOD HOPE)")
print(f"Final total: {len(extracted_colonies)} colonies")
print()
print(f"Output directory: {output_dir}")
print()
print("Next step: Run create_1900_metadata.py to generate corrected metadata JSON")
