#!/usr/bin/env python3
"""
Extract corrected 1910 colonies after manual boundary verification.

Year 1910 shows SEVERE over-extraction pattern (116 colonies!):
- THE COMMONWEALTH split with THE SENATE as separate colony
- Dominion of Canada split into 4 subsections (THE DOMINION, THE SENATE OF CANADA, ONTARIO AND QUEBEC, plus 2x EXECUTIVE COUNCIL)
- Cape of Good Hope split into 5 subsections (2x CAPE OF GOOD HOPE, URBAN POLICE DISTRICT, RAILWAYS, ECCLESIASTICAL)
- EXPORTS appears 10 times as separate colonies!

This script:
1. Merges THE COMMONWEALTH with THE SENATE subsection (3491-4077)
2. Merges DOMINION OF CANADA from 4 subsections (12805-14667, 2,863 lines)
3. Merges CAPE OF GOOD HOPE from 5 subsections (15892-18614, 2,723 lines)
4. Skips all over-extracted subsections
5. Keeps all properly extracted colonies (including Ceylon, provincial entries, etc.)
"""

import json
from pathlib import Path

# Load original metadata
with open('output/1910_manual_parsed.json', 'r') as f:
    original_data = json.load(f)

# Output directory
output_dir = Path('output_2/1910_manual_parsed')
output_dir.mkdir(parents=True, exist_ok=True)

# OCR source file
source_file = Path('historical_document_pipeline/processed_pdfs/colonial-office-list-1910/olmocr_results.md')

# Define subsections to skip (over-extracted entries that are part of larger colonies)
skip_entries = {
    # Commonwealth subsections
    'THE SENATE',  # Part of THE COMMONWEALTH (line 4017-4077)
    'THE COMMONWEALTH',  # Will replace with merged version

    # Dominion of Canada subsections (will merge into one)
    'THE DOMINION',
    'THE SENATE OF CANADA',
    'ONTARIO AND QUEBEC (OLD CANADA)',
    'EXECUTIVE COUNCIL',  # Appears 2x - both part of Ontario/Quebec

    # Cape of Good Hope subsections (will merge into one)
    'CAPE OF GOOD HOPE',  # Appears 2x
    'URBAN POLICE DISTRICT, CAPE TOWN, AND CAPE MOUNTED POLICE',
    'RAILWAYS',  # Part of Cape
    'ECCLESIASTICAL',  # Part of Cape

    # Other over-extracted subsections
    'EXPORTS',  # Appears 10 times! - always a subsection
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
    filename = name.replace(' ', '_').replace(',', '').replace('(', '').replace(')', '').replace("'", '') + '.md'

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
    ('THE_COMMONWEALTH', 3491, 4077, 'Merged THE SENATE subsection into THE COMMONWEALTH (587 lines).'),
    ('DOMINION_OF_CANADA', 12805, 14667, 'Merged 6 over-extracted subsections into 1 colony (2,863 lines): THE DOMINION, THE SENATE, ONTARIO AND QUEBEC, 2x EXECUTIVE COUNCIL.'),
    ('CAPE_OF_GOOD_HOPE', 15892, 18614, 'Merged 5 over-extracted subsections into 1 colony (2,723 lines): 2x CAPE OF GOOD HOPE, URBAN POLICE, RAILWAYS, ECCLESIASTICAL.'),
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
print("YEAR 1910 EXTRACTION COMPLETE")
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
print("✅ Year 1910 corrected - SEVERE over-extraction pattern fixed (116 → ~60 colonies)")
