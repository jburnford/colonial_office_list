#!/usr/bin/env python3
"""
Extract corrected 1923 colonies after manual boundary verification.

Year 1923 shows SEVERE over-extraction pattern (45 colonies reported):
- AUSTRALIA split into 5 subsections: AUSTRALIA, VICTORIA, QUEENSLAND, WESTERN AUSTRALIA, TASMANIA
- TRINIDAD split with TOBAGO as separate colony
- ADEN massively over-extracted to include TRISTAN DA CUNHA, MISCELLANEOUS ISLANDS, and entire PART III appendix (16,746 lines!)

This script:
1. Merges AUSTRALIA with VICTORIA, QUEENSLAND, WESTERN AUSTRALIA, TASMANIA subsections (4399-12706, 8,307 lines)
2. Merges TRINIDAD with TOBAGO subsection (39444-41298, 1,854 lines)
3. Splits massive ADEN section into proper colonies:
   - ADEN (44373-44387, ~15 lines)
   - TRISTAN DA CUNHA (44388-44408, ~21 lines including MISCELLANEOUS ISLANDS)
4. Adds APPENDIX for LIST OF HONOURS (44409-61118)
5. Skips all over-extracted subsections
"""

import json
from pathlib import Path

# Load original metadata
with open('output/1923_manual_parsed.json', 'r') as f:
    original_data = json.load(f)

# Output directory
output_dir = Path('output_2/1923_manual_parsed')
output_dir.mkdir(parents=True, exist_ok=True)

# OCR source file
source_file = Path('historical_document_pipeline/processed_pdfs/colonial-office-list-1923/olmocr_results.md')

# Define subsections to skip (over-extracted entries that are part of larger colonies)
skip_entries = {
    # Australian subsections (all part of AUSTRALIA)
    'AUSTRALIA',  # Will be replaced with merged version
    'VICTORIA',
    'QUEENSLAND',
    'WESTERN AUSTRALIA',
    'TASMANIA',

    # Trinidad subsections (will merge into TRINIDAD AND TOBAGO)
    'TRINIDAD',
    'TOBAGO',

    # Aden over-extraction (will be replaced with corrected versions)
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
    filename = name.replace(' ', '_').replace(',', '').replace('(', '').replace(')', '').replace("'", '').replace('.', '') + '.md'

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
    ('AUSTRALIA', 4399, 12706, 'Merged 5 over-extracted subsections: AUSTRALIA, VICTORIA, QUEENSLAND, WESTERN AUSTRALIA, TASMANIA (8,307 lines total).'),
    ('TRINIDAD_AND_TOBAGO', 39444, 41298, 'Merged TRINIDAD and TOBAGO subsections into one colony (1,854 lines).'),
    ('ADEN', 44373, 44387, 'Corrected ADEN boundaries - removed TRISTAN DA CUNHA and appendix contamination (15 lines).'),
    ('TRISTAN_DA_CUNHA', 44388, 44408, 'Extracted TRISTAN DA CUNHA from ADEN over-extraction, includes MISCELLANEOUS ISLANDS section (21 lines).'),
    ('APPENDIX_LIST_OF_HONOURS', 44409, 61118, 'PART III: List of Honours conferred on persons for Services in Oversea Dominions, Colonies (16,709 lines).'),
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
print("YEAR 1923 EXTRACTION COMPLETE")
print("=" * 80)
print(f"\nOriginal colonies in metadata: {len(original_data['colonies'])}")
print(f"Kept (properly extracted):      {len(kept)}")
print(f"Skipped (over-extracted):       {len(skipped)}")
print(f"Corrected (merged/split):       {len(corrected)}")
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
print("Corrected colonies (merged/split subsections):")
for colony in corrected:
    print(f"  - {colony['name']}: {colony['start']}-{colony['end']} ({colony['lines']} lines)")
    print(f"    {colony['note']}")
print()
print(f"Output directory: {output_dir}")
print("✅ Year 1923 corrected - SEVERE over-extraction pattern fixed (45 → ~43 colonies + 1 appendix)")
