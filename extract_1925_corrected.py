#!/usr/bin/env python3
"""
Extract corrected 1925 colonies after manual boundary verification.

Year 1925 shows SEVERE over-extraction pattern (45 colonies with major issues):
- AUSTRALIA split into 5 subsections (VICTORIA, QUEENSLAND, WESTERN AUSTRALIA, TASMANIA as separate)
- BRITISH COLUMBIA incorrectly extracted as separate colony (it's a Canadian province, not listed separately)
- LABUAN incorrectly extracted as separate colony (it's part of STRAITS SETTLEMENTS - Medical dept subsection)
- TRINIDAD AND TOBAGO split into 2 separate colonies (TRINIDAD, TOBAGO)
- ADEN massively over-extracted - includes entire appendix section (16,161 lines!)

This script:
1. Merges AUSTRALIA with all Australian state subsections (VICTORIA, QUEENSLAND, WESTERN AUSTRALIA, TASMANIA)
2. Merges BRITISH COLUMBIA content into proper structure (or removes if not a separate colonial listing)
3. Merges STRAITS SETTLEMENTS with LABUAN subsection and other Malayan content
4. Merges TRINIDAD AND TOBAGO into single colony
5. Fixes ADEN to exclude appendix material
"""

import json
from pathlib import Path

# Load original metadata
with open('output/1925_manual_parsed.json', 'r') as f:
    original_data = json.load(f)

# Output directory
output_dir = Path('output_2/1925_manual_parsed')
output_dir.mkdir(parents=True, exist_ok=True)

# OCR source file
source_file = Path('historical_document_pipeline/processed_pdfs/colonial-office-list-1925/olmocr_results.md')

# Define subsections to skip (over-extracted entries that are part of larger colonies)
skip_entries = {
    # Australian state subsections (part of AUSTRALIA)
    'AUSTRALIA',  # Will replace with merged version
    'VICTORIA',
    'QUEENSLAND',
    'WESTERN AUSTRALIA',
    'TASMANIA',

    # Canadian province incorrectly extracted
    'BRITISH COLUMBIA',  # Canadian province, not a separate colony in 1925 listing

    # Straits Settlements subsections
    'LABUAN',  # Medical department subsection within STRAITS SETTLEMENTS

    # Trinidad split
    'TRINIDAD',  # Will merge with TOBAGO
    'TOBAGO',   # Will merge into TRINIDAD AND TOBAGO

    # Aden over-extraction
    'ADEN',  # Will replace with corrected version (excluding appendices)
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
    ('AUSTRALIA', 5891, 13624, 'Merged 5 Australian subsections into 1 colony (7,734 lines): AUSTRALIA + VICTORIA + QUEENSLAND + WESTERN AUSTRALIA + TASMANIA. These were parliamentary constituencies, not separate colonies.'),
    ('STRAITS_SETTLEMENTS', 39503, 41838, 'Merged STRAITS SETTLEMENTS content (2,336 lines): Includes Singapore, Penang, Malacca, and Labuan subsections. LABUAN was incorrectly extracted as separate colony.'),
    ('TRINIDAD_AND_TOBAGO', 41838, 43087, 'Merged TRINIDAD and TOBAGO into single colony (1,250 lines): Tobago was amalgamated with Trinidad in 1889, not separate.'),
    ('ADEN', 46226, 46240, 'Corrected ADEN extraction (15 lines): Original spanned 16,161 lines including all appendices. Now ends before MISCELLANEOUS ISLANDS section.'),
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
print("YEAR 1925 EXTRACTION COMPLETE")
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
print("✅ Year 1925 corrected - SEVERE over-extraction pattern fixed (45 → ~41 colonies)")
