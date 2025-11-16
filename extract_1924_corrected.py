#!/usr/bin/env python3
"""
Extract corrected 1924 colonies after manual boundary verification.

Year 1924 shows SEVERE over-extraction for ADEN:
- ADEN incorrectly includes 16,692 lines (44222-60914) extending to end of file
- ADEN should only be 14 lines (44222-44235)
- Missing TRISTAN DA CUNHA as separate colony (44236-44247)
- Missing MISCELLANEOUS ISLANDS as separate colony (44248-44256)
- PART III (LIST OF HONOURS) starting at line 44257 was incorrectly included in ADEN

This script:
1. Keeps all properly extracted colonies (AUSTRALIA through PALESTINE)
2. Corrects ADEN to proper boundaries (44222-44235, 14 lines)
3. Adds missing TRISTAN DA CUNHA (44236-44247, 12 lines)
4. Adds missing MISCELLANEOUS ISLANDS (44248-44256, 9 lines)
5. Does NOT extract PART III (appendix content starting at 44257)
"""

import json
from pathlib import Path

# Load original metadata
with open('output/1924_manual_parsed.json', 'r') as f:
    original_data = json.load(f)

# Output directory
output_dir = Path('output_2/1924_manual_parsed')
output_dir.mkdir(parents=True, exist_ok=True)

# OCR source file
source_file = Path('historical_document_pipeline/processed_pdfs/colonial-office-list-1924/olmocr_results.md')

# Define subsections to skip (over-extracted entries)
skip_entries = {
    'ADEN',  # Will replace with corrected version
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

    # Skip over-extracted entries
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

# Define the corrected colonies (with proper boundaries)
corrected_colonies = [
    ('ADEN', 44222, 44235, 'Fixed over-extraction: was 44222-60914 (16,692 lines), corrected to 44222-44235 (14 lines)'),
    ('TRISTAN_DA_CUNHA', 44236, 44247, 'Added missing colony (12 lines) - was incorrectly included in ADEN'),
    ('MISCELLANEOUS_ISLANDS', 44248, 44256, 'Added missing colony (9 lines) - was incorrectly included in ADEN'),
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
print("YEAR 1924 EXTRACTION COMPLETE")
print("=" * 80)
print(f"\nOriginal colonies in metadata: {len(original_data['colonies'])}")
print(f"Kept (properly extracted):      {len(kept)}")
print(f"Skipped (over-extracted):       {len(skipped)}")
print(f"Corrected (fixed/added):        {len(corrected)}")
print(f"Total colonies after fix:       {len(kept) + len(corrected)}")
print()
print("Skipped over-extracted entries:")
for name in sorted(set(skipped)):
    count = skipped.count(name)
    if count > 1:
        print(f"  - {name} (appeared {count}x)")
    else:
        print(f"  - {name}")
print()
print("Corrected/Added colonies:")
for colony in corrected:
    print(f"  - {colony['name']}: {colony['start']}-{colony['end']} ({colony['lines']} lines)")
    print(f"    {colony['note']}")
print()
print(f"Output directory: {output_dir}")
print("✅ Year 1924 corrected - ADEN over-extraction fixed (16,692 lines → 14 lines)")
print("✅ Added 2 missing colonies: TRISTAN DA CUNHA, MISCELLANEOUS ISLANDS")
print(f"✅ Final count: 47 → 49 colonies")
