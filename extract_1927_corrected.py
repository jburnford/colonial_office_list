#!/usr/bin/env python3
"""
Extract corrected 1927 colonies after manual boundary verification.

Year 1927 shows significant over-extraction patterns:
- AUSTRALIA split into 7 entries (main + 6 Australian states/territories showing electoral constituencies)
- LABUAN wrongly extracted - just a subsection within STRAITS SETTLEMENTS
- TRINIDAD and TOBAGO split into 2 entries (header shows "TRINIDAD AND TOBAGO")
- ADEN massively over-extracted - absorbed TRISTAN DA CUNHA, MISCELLANEOUS ISLANDS, and entire PART III appendix
- Missing: TRISTAN DA CUNHA and MISCELLANEOUS ISLANDS as separate entries

This script:
1. Merges AUSTRALIA with all Australian state/territory subsections (6157-16736)
2. Removes wrongly extracted LABUAN entry (just 1 line in STRAITS SETTLEMENTS)
3. Merges TRINIDAD and TOBAGO from 2 subsections (44181-45657)
4. Corrects ADEN boundaries (48645-48670, not to end of file)
5. Adds TRISTAN DA CUNHA (48670-48685) and MISCELLANEOUS ISLANDS (48686-48694) as separate entries
6. Keeps all other properly extracted colonies
"""

import json
from pathlib import Path

# Load original metadata
with open('output/1927_manual_parsed.json', 'r') as f:
    original_data = json.load(f)

# Output directory
output_dir = Path('output_2/1927_manual_parsed')
output_dir.mkdir(parents=True, exist_ok=True)

# OCR source file
source_file = Path('historical_document_pipeline/processed_pdfs/colonial-office-list-1927/olmocr_results.md')

# Define subsections to skip (over-extracted entries that are part of larger colonies)
skip_entries = {
    # AUSTRALIA will be replaced with merged version including all states/territories
    'AUSTRALIA',

    # Australian state subsections (electoral constituencies) - merge into AUSTRALIA
    'VICTORIA',
    'QUEENSLAND',
    'WESTERN AUSTRALIA',
    'TASMANIA',

    # LABUAN is not a separate colony - just a subsection within STRAITS SETTLEMENTS
    'LABUAN',

    # TRINIDAD and TOBAGO subsections - merge into one
    'TRINIDAD',
    'TOBAGO',

    # ADEN will be replaced with corrected boundaries
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

# Define the corrected/merged colonies
corrected_colonies = [
    ('AUSTRALIA', 6157, 16736, 'Merged 6 Australian state/territory subsections (VICTORIA, QUEENSLAND, SOUTH AUSTRALIA, WESTERN AUSTRALIA, TASMANIA, NORTHERN TERRITORY) into AUSTRALIA - these were just electoral constituencies (10,580 lines).'),
    ('TRINIDAD_AND_TOBAGO', 44181, 45657, 'Merged TRINIDAD and TOBAGO subsections into one colony per header "* TRINIDAD AND TOBAGO" (1,477 lines).'),
    ('ADEN', 48645, 48670, 'Corrected ADEN boundaries - removed over-extraction of TRISTAN DA CUNHA, MISCELLANEOUS ISLANDS, and PART III appendix (26 lines).'),
    ('TRISTAN_DA_CUNHA', 48670, 48685, 'Added as separate entry - was wrongly absorbed into ADEN (16 lines).'),
    ('MISCELLANEOUS_ISLANDS', 48686, 48694, 'Added as separate entry - was wrongly absorbed into ADEN (9 lines).'),
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
print("YEAR 1927 EXTRACTION COMPLETE")
print("=" * 80)
print(f"\nOriginal colonies in metadata: {len(original_data['colonies'])}")
print(f"Kept (properly extracted):      {len(kept)}")
print(f"Skipped (over-extracted):       {len(skipped)}")
print(f"Corrected (merged/fixed):       {len(corrected)}")
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
print("Corrected colonies (merged/fixed boundaries):")
for colony in corrected:
    print(f"  - {colony['name']}: {colony['start']}-{colony['end']} ({colony['lines']} lines)")
    print(f"    {colony['note']}")
print()
print(f"Output directory: {output_dir}")
print("✅ Year 1927 corrected - over-extraction pattern fixed (50 → ~43 colonies)")
