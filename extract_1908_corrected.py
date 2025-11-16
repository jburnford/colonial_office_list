#!/usr/bin/env python3
"""
Extract corrected 1908 colonies after manual boundary verification.

Year 1908 shows the SAME over-extraction pattern as 1906-1907:
- Dominion of Canada split into 5 subsections
- Cape of Good Hope split into 6 subsections (3 "CAPE OF GOOD HOPE" headers + 3 other subsections)
- Third "CAPE OF GOOD HOPE" entry contaminated with Ceylon content at the end
- Multiple "EXPORTS" subsections incorrectly extracted as colonies
- Ceylon content (18086-18923) exists but lacks proper colony header

This script:
1. Skips all over-extracted subsections
2. Merges Dominion of Canada subsections into 1 colony (12015-15175, 3,161 lines)
3. Merges Cape of Good Hope subsections into 1 colony (15176-18085, 2,910 lines)
   - Stops before Ceylon content contamination starts (line 18086)
4. Keeps Ceylon province subsections (orphaned content)
5. Keeps all properly extracted colonies
"""

import json
from pathlib import Path

# Load original metadata
with open('output/1908_manual_parsed.json', 'r') as f:
    original_data = json.load(f)

# Output directory
output_dir = Path('output_2/1908_manual_parsed')
output_dir.mkdir(parents=True, exist_ok=True)

# OCR source file
source_file = Path('historical_document_pipeline/processed_pdfs/colonial-office-list-1908/olmocr_results.md')

# Define subsections to skip (over-extracted entries that are part of larger colonies)
skip_entries = {
    # Dominion of Canada subsections (will merge into one)
    'THE SENATE',
    'THE DOMINION',
    'THE SENATE OF CANADA',
    'RAILWAYS AND CANALS',
    'ONTARIO AND QUEBEC (OLD CANADA)',

    # Cape of Good Hope subsections (will merge into one)
    # Note: All 3 "CAPE OF GOOD HOPE" headers will be skipped and replaced by merged version
    'CAPE OF GOOD HOPE',
    'THE EXECUTIVE COUNCIL',  # Subsection between first Cape entry and CAPE MOUNTED POLICE
    'CAPE MOUNTED POLICE',
    'URBAN POLICE DISTRICT, CAPE TOWN',

    # Other subsections incorrectly treated as colonies
    'EXPORTS',  # Appears 3 times - always a subsection
}

# Track statistics
kept = []
skipped = []
corrected = []

# Read source file
with open(source_file, 'r') as f:
    source_lines = f.readlines()

# Extract existing colonies (except those in skip list)
for colony in original_data['colonies']:
    name = colony['colony_name']

    # Skip over-extracted subsections
    if name in skip_entries:
        skipped.append(name)
        continue

    # Keep properly extracted colonies
    start = colony['start_line']
    end = colony['end_line']

    # Extract content
    content_lines = source_lines[start-1:end]
    content = ''.join(content_lines)

    # Create filename
    filename = name.replace(' ', '_').replace(',', '').replace('(', '').replace(')', '') + '.md'

    # Write file
    output_file = output_dir / filename
    with open(output_file, 'w') as f:
        f.write(content)

    kept.append({
        'name': name,
        'filename': filename,
        'start': start,
        'end': end,
        'lines': end - start + 1
    })

# Define the corrected colonies (merged from subsections)
corrected_colonies = [
    ('DOMINION_OF_CANADA', 12015, 15175, 'Merged 5 over-extracted subsections into 1 colony (3,161 lines).'),
    ('CAPE_OF_GOOD_HOPE', 15176, 18085, 'Merged 6 over-extracted subsections into 1 colony (2,910 lines). Excluded Ceylon contamination (18086+).'),
]

# Extract corrected colonies
for name, start, end, note in corrected_colonies:
    # Extract content
    content_lines = source_lines[start-1:end]
    content = ''.join(content_lines)

    # Create filename
    filename = name + '.md'

    # Write file
    output_file = output_dir / filename
    with open(output_file, 'w') as f:
        f.write(content)

    corrected.append({
        'name': name.replace('_', ' '),
        'filename': filename,
        'start': start,
        'end': end,
        'lines': end - start + 1,
        'note': note
    })

# Print summary
print("=" * 80)
print("YEAR 1908 EXTRACTION COMPLETE")
print("=" * 80)
print(f"\nOriginal colonies in metadata: {len(original_data['colonies'])}")
print(f"Kept (properly extracted):      {len(kept)}")
print(f"Skipped (over-extracted):       {len(skipped)}")
print(f"Corrected (merged):             {len(corrected)}")
print(f"Total colonies after fix:       {len(kept) + len(corrected)}")
print()
print("Skipped over-extracted subsections:")
for name in sorted(set(skipped)):
    count = skipped.count(name)
    if count > 1:
        print(f"  - {name} (appeared {count}x)")
    else:
        print(f"  - {name}")
print()
print("Corrected colonies (merged subsections):")
for colony in corrected:
    print(f"  - {colony['name']}: {colony['start']}-{colony['end']} ({colony['lines']} lines)")
    print(f"    {colony['note']}")
print()
print(f"Output directory: {output_dir}")
print("✅ Year 1908 corrected - over-extraction pattern fixed")
print("⚠️  Note: Ceylon content (18086-18923) orphaned - no proper colony header found")
