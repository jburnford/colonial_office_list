#!/usr/bin/env python3
"""
Extract corrected 1918 colonies after manual boundary verification.

Year 1918 shows over-extraction pattern (44 colonies with issues):
- AUSTRALIA split into 5 subsections (AUSTRALIA, VICTORIA, QUEENSLAND, WESTERN AUSTRALIA, TASMANIA)
- BRITISH HONDURAS incorrectly capturing DOMINION OF CANADA content
- DOMINION OF CANADA missing entirely from metadata
- ASCENSION capturing all appendices (17,100 lines of PART III, PART IV content)

This script:
1. Merges AUSTRALIA from 5 subsections (3644-11137)
2. Fixes BRITISH HONDURAS boundary (13420-13769, not 17088)
3. Adds DOMINION OF CANADA (13770-27133)
4. Fixes ASCENSION (40189-40192, not 40188-57288)
5. Keeps all properly extracted colonies
"""

import json
from pathlib import Path

# Load original metadata
with open('output/1918_manual_parsed.json', 'r') as f:
    original_data = json.load(f)

# Output directory
output_dir = Path('output_2/1918_manual_parsed')
output_dir.mkdir(parents=True, exist_ok=True)

# OCR source file
source_file = Path('historical_document_pipeline/processed_pdfs/colonial-office-list-1918/olmocr_results.md')

# Define subsections to skip (over-extracted entries that are part of larger colonies)
skip_entries = {
    # Australian states/territories (will merge into AUSTRALIA)
    'AUSTRALIA',  # Original AUSTRALIA entry will be replaced with merged version
    'VICTORIA',
    'QUEENSLAND',
    'WESTERN AUSTRALIA',
    'TASMANIA',
}

# Define entries to fix (wrong boundaries)
fix_entries = {
    'BRITISH HONDURAS': (13420, 13769),  # Currently 13420-17088, should end at 13769
    'CEYLON': (17089, 18149),  # Currently 17088-18149, should start at 17089 (skip OCR corruption 17083-17088)
    'ASCENSION': (40189, 40192),  # Currently 40188-57288, should be 40189-40192
    'LABUAN': (34848, 36181),  # Currently 34847-36181, should start at 34848
}

# Track statistics
kept = []
skipped = []
fixed = []
corrected = []

# Read source file
with open(source_file, 'r') as f:
    source_lines = f.readlines()

# Extract existing colonies (except those in skip list or fix list)
for colony in original_data['colonies']:
    name = colony['colony_name']

    # Skip over-extracted subsections
    if name in skip_entries:
        skipped.append(name)
        continue

    # Fix entries with wrong boundaries
    if name in fix_entries:
        start, end = fix_entries[name]
        fixed.append({
            'name': name,
            'old_range': f"{colony['start_line']}-{colony['end_line']}",
            'new_range': f"{start}-{end}"
        })
    else:
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

# Define the corrected colonies (merged from subsections or added)
corrected_colonies = [
    ('AUSTRALIA', 3644, 11137, 'Merged 5 over-extracted subsections into 1 complete colony (original AUSTRALIA 3644-4180 + VICTORIA + QUEENSLAND + WESTERN AUSTRALIA + TASMANIA). Includes PAPUA and NORFOLK ISLAND as territories.'),
    ('DOMINION_OF_CANADA', 13770, 17082, 'Added missing colony - was incorrectly captured by BRITISH HONDURAS in original extraction. Ends at YUKON section before OCR corruption at 17083-17088.'),
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
print("YEAR 1918 EXTRACTION COMPLETE")
print("=" * 80)
print(f"\nOriginal colonies in metadata: {len(original_data['colonies'])}")
print(f"Kept (properly extracted):      {len(kept)}")
print(f"Skipped (over-extracted):       {len(skipped)}")
print(f"Fixed (wrong boundaries):       {len(fixed)}")
print(f"Corrected (merged/added):       {len(corrected)}")
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
print("Fixed entries (boundary corrections):")
for entry in fixed:
    print(f"  - {entry['name']}: {entry['old_range']} → {entry['new_range']}")
print()
print("Corrected colonies (merged/added):")
for colony in corrected:
    print(f"  - {colony['name']}: {colony['start']}-{colony['end']} ({colony['lines']} lines)")
    print(f"    {colony['note']}")
print()
print(f"Output directory: {output_dir}")
print("✅ Year 1918 corrected - over-extraction pattern fixed (44 → ~43 colonies)")
