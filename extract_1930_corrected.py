#!/usr/bin/env python3
"""
Extract corrected 1930 colonies after manual boundary verification.

Year 1930 shows SEVERE over-extraction and missing colonies:
- AUSTRALIA split into 5 separate entries (AUSTRALIA, WESTERN AUSTRALIA, TASMANIA, QUEENSLAND, VICTORIA)
- NEW ZEALAND completely missing from extraction
- SOUTH AFRICA split with CAPE OF GOOD HOPE as separate entry
- ADEN massively over-extracted: 49360-72637 (23,277 lines!) instead of 49360-49384 (25 lines)
- TRISTAN DA CUNHA missing
- MISCELLANEOUS ISLANDS missing

This script:
1. Merges AUSTRALIA from 5 over-extracted state subsections into 1 Dominion (6092-16814, 10,722 lines)
2. Adds missing NEW ZEALAND (18323-19551, 1,229 lines)
3. Merges SOUTH AFRICA with CAPE OF GOOD HOPE subsection (19552-22196, 2,645 lines)
4. Fixes ADEN to correct boundary (49360-49384, 25 lines) - was 23,277 lines!
5. Adds missing TRISTAN DA CUNHA (49385-49400, 16 lines)
6. Adds missing MISCELLANEOUS ISLANDS (49401-49409, 9 lines)
7. Keeps all properly extracted colonies
"""

import json
from pathlib import Path

# Load original metadata
with open('output/1930_manual_parsed.json', 'r') as f:
    original_data = json.load(f)

# Output directory
output_dir = Path('output_2/1930_manual_parsed')
output_dir.mkdir(parents=True, exist_ok=True)

# OCR source file
source_file = Path('historical_document_pipeline/processed_pdfs/colonial-office-list-1930/olmocr_results.md')

# Define subsections to skip (over-extracted entries that are part of larger colonies)
skip_entries = {
    # Australian state subsections (will merge into AUSTRALIA)
    'AUSTRALIA',
    'WESTERN AUSTRALIA',
    'TASMANIA',
    'QUEENSLAND',
    'VICTORIA',

    # South African province subsection (will merge into SOUTH AFRICA)
    'CAPE OF GOOD HOPE',
    'BASUTOLAND',  # Will re-add after SOUTH AFRICA
    'SWAZILAND',   # Will re-add after SOUTH AFRICA
    'SOUTHERN RHODESIA',  # Will re-add after SOUTH AFRICA

    # ADEN - will replace with corrected version
    'ADEN',
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

# Define the corrected colonies (merged/fixed/added)
corrected_colonies = [
    ('AUSTRALIA', 6092, 16814, 'Merged 5 over-extracted state subsections into 1 Dominion (10,722 lines): AUSTRALIA, WESTERN AUSTRALIA, TASMANIA, QUEENSLAND, VICTORIA.'),
    ('NEW ZEALAND', 18323, 19551, 'Missing from original extraction - manually added (1,229 lines).'),
    ('SOUTH_AFRICA', 19552, 22196, 'Merged CAPE OF GOOD HOPE subsection into SOUTH AFRICA (2,645 lines).'),
    ('BASUTOLAND', 22197, 22602, 'Re-added after SOUTH AFRICA merge (405 lines).'),
    ('SWAZILAND', 22602, 22834, 'Re-added after SOUTH AFRICA merge (232 lines).'),
    ('SOUTHERN_RHODESIA', 22834, 23904, 'Re-added after SOUTH AFRICA merge (1,070 lines).'),
    ('ADEN', 49360, 49384, 'Fixed massive over-extraction: was 49360-72637 (23,277 lines!), now 49360-49384 (25 lines).'),
    ('TRISTAN_DA_CUNHA', 49385, 49400, 'Missing from original extraction - manually added (16 lines).'),
    ('MISCELLANEOUS_ISLANDS', 49401, 49409, 'Missing from original extraction - manually added (9 lines).'),
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
print("YEAR 1930 EXTRACTION COMPLETE")
print("=" * 80)
print(f"\nOriginal colonies in metadata: {len(original_data['colonies'])}")
print(f"Kept (properly extracted):      {len(kept)}")
print(f"Skipped (over-extracted):       {len(skipped)}")
print(f"Corrected (merged/fixed/added): {len(corrected)}")
print(f"Total colonies after fix:       {len(kept) + len(corrected)}")
print()
print("Skipped over-extracted/incorrect subsections:")
for name in sorted(set(skipped)):
    count = skipped.count(name)
    if count > 1:
        print(f"  - {name} (appeared {count}x)")
    else:
        print(f"  - {name}")
print()
print("Corrected colonies (merged/fixed/added):")
for colony in corrected:
    print(f"  - {colony['name']}: {colony['start']}-{colony['end']} ({colony['lines']} lines)")
    print(f"    {colony['note']}")
print()
print(f"Output directory: {output_dir}")
print("✅ Year 1930 corrected - SEVERE over-extraction and missing colonies fixed")
print("✅ ADEN fixed: was 23,277 lines (largest over-extraction ever!), now 25 lines")
print("✅ NEW ZEALAND added (was completely missing)")
print("✅ AUSTRALIA merged from 5 state subsections")
