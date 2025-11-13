#!/usr/bin/env python3
"""
Extract corrected 1906 colonies based on manual boundary verification.

MAJOR OVER-EXTRACTION ISSUES:
- British New Guinea contaminated with Bahamas (203→159 lines)
- Dominion of Canada split into 3 subsections instead of 1 colony
- Cape of Good Hope split into 4 subsections instead of 1 colony
- Many other subsections incorrectly treated as separate colonies

VERIFIED CORRECTIONS:
- BRITISH NEW GUINEA: Was 203 lines (8983-9185) → Fixed to 158 lines (8983-9140)
- DOMINION OF CANADA: Merge 3 subsections → 1 colony (11892-14892, 3,001 lines)
- CAPE OF GOOD HOPE: Merge 4 subsections → 1 colony (14893-17474, 2,582 lines)

Expected result: 92 colonies → ~50 colonies (removing over-extracted subsections)
"""

import json
from pathlib import Path

# Source OCR file
source_file = Path('/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1906/olmocr_results.md')

# Output directory
output_dir = Path('/home/user/colonial_office_list/output_2/1906_manual_parsed')
output_dir.mkdir(parents=True, exist_ok=True)

# Read source file
print("Reading OCR source file...")
with open(source_file, 'r') as f:
    lines = f.readlines()

print(f"Total lines in source: {len(lines)}")
print("=" * 80)
print("EXTRACTING CORRECTED 1906 COLONIES")
print("=" * 80)
print()

# Load original metadata
with open('output/1906_manual_parsed.json', 'r') as f:
    original_data = json.load(f)

print(f"Original extraction had {original_data['total_colonies']} colonies")
print()

# Define subsections to skip (over-extracted entries)
skip_entries = {
    # British New Guinea (will re-extract)
    'BRITISH NEW GUINEA',
    # Dominion of Canada subsections (will merge into one)
    'THE DOMINION',
    'THE SENATE OF CANADA', 
    'ONTARIO AND QUEBEC (OLD CANADA)',
    # Cape of Good Hope subsections (will merge into one)
    'CAPE OF GOOD HOPE',
    'CAPE MOUNTED POLICE',
    'URBAN POLICE DISTRICT, CAPE TOWN',
    # Other likely subsections
    'RAILWAYS',
}

print(f"GROUP A: Extracting colonies (skipping {len(skip_entries)} over-extracted subsections)...")
print()

extracted_colonies = []
skipped = []

for colony in original_data['colonies']:
    name = colony.get('colony_name', colony.get('name', 'Unknown'))
    
    # Skip over-extracted subsections
    if name in skip_entries:
        skipped.append(name)
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
print(f"Skipped {len(skipped)} over-extracted subsections")
print()
print("=" * 80)
print("GROUP B: Extracting 3 corrected/merged colonies...")
print("=" * 80)
print()

# Define the corrected colonies
corrected_colonies = [
    ('BRITISH_NEW_GUINEA', 8983, 9140, 'Was contaminated with Bahamas (203 lines). Fixed to actual colony content (158 lines).'),
    ('DOMINION_OF_CANADA', 11892, 14892, 'Merged 3 over-extracted subsections into 1 colony (3,001 lines).'),
    ('CAPE_OF_GOOD_HOPE', 14893, 17474, 'Merged 4 over-extracted subsections into 1 colony (2,582 lines).'),
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
        'extraction_method': 'merged_subsections',
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
print(f"Over-extracted subsections removed: {len(skipped)}")
print(f"Corrected/merged colonies added: 3")
print(f"Final total: {len(extracted_colonies)} colonies")
print()
print(f"Output directory: {output_dir}")
print()
print("Next step: Run create_1906_metadata.py to generate corrected metadata JSON")
