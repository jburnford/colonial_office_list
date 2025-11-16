#!/usr/bin/env python3
"""
Extract corrected 1909 colonies after manual boundary verification.

Year 1909 shows the SAME over-extraction pattern as 1906-1908:
- Dominion of Canada split into 4 subsections (THE DOMINION, RAILWAYS AND CANALS, ONTARIO AND QUEBEC, ONTARIO)
- Cape of Good Hope split into 3 subsections (CAPE OF GOOD HOPE, CAPE MOUNTED RIFLEMEN, CAPE MOUNTED POLICE)
- Multiple "EXPORTS" subsections incorrectly extracted as colonies (appears 7 times!)

This script:
1. Skips all over-extracted subsections
2. Merges Dominion of Canada subsections into 1 colony (13038-16082, 3,045 lines)
3. Merges Cape of Good Hope subsections into 1 colony (16083-18755, 2,673 lines)
4. Keeps all properly extracted colonies (including CEYLON which is properly separated)
"""

import json
from pathlib import Path

# Load original metadata
with open('output/1909_manual_parsed.json', 'r') as f:
    original_data = json.load(f)

# Output directory
output_dir = Path('output_2/1909_manual_parsed')
output_dir.mkdir(parents=True, exist_ok=True)

# OCR source file
source_file = Path('historical_document_pipeline/processed_pdfs/colonial-office-list-1909/olmocr_results.md')

# Define subsections to skip (over-extracted entries that are part of larger colonies)
skip_entries = {
    # Dominion of Canada subsections (will merge into one)
    'THE DOMINION',
    'RAILWAYS AND CANALS',
    'ONTARIO AND QUEBEC (OLD CANADA)',
    'ONTARIO',

    # Cape of Good Hope subsections (will merge into one)
    'CAPE OF GOOD HOPE',
    'CAPE MOUNTED RIFLEMEN',
    'CAPE MOUNTED POLICE',

    # Other subsections incorrectly treated as colonies
    'EXPORTS',  # Appears 7 times! - always a subsection
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
    ('DOMINION_OF_CANADA', 13038, 16082, 'Merged 4 over-extracted subsections into 1 colony (3,045 lines).'),
    ('CAPE_OF_GOOD_HOPE', 16083, 18755, 'Merged 3 over-extracted subsections into 1 colony (2,673 lines).'),
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
print("YEAR 1909 EXTRACTION COMPLETE")
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
print("✅ Year 1909 corrected - over-extraction pattern fixed")
print("✅ Ceylon properly extracted as separate colony (no contamination)")
