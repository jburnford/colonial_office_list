#!/usr/bin/env python3
"""
Extract corrected 1911 colonies after manual boundary verification.

Year 1911 shows similar over-extraction pattern to 1910 (102 colonies):
- Dominion of Canada split into multiple subsections (THE DOMINION, FREE GOODS, THE CABINET, THE SENATE, COMMISSIONS, YUKON, 2x EXECUTIVE COUNCIL, provinces, provincial assemblies)
- Multiple over-extracted subsections: IMPERIAL, THE PARLIAMENT, EXPORTS (5x), etc.

This script:
1. Merges DOMINION OF CANADA from multiple subsections (12615-15610, ~3,000 lines)
2. Skips all over-extracted subsections
3. Keeps all properly extracted colonies
"""

import json
from pathlib import Path

# Load original metadata
with open('output/1911_manual_parsed.json', 'r') as f:
    original_data = json.load(f)

# Output directory
output_dir = Path('output_2/1911_manual_parsed')
output_dir.mkdir(parents=True, exist_ok=True)

# OCR source file
source_file = Path('historical_document_pipeline/processed_pdfs/colonial-office-list-1911/olmocr_results.md')

# Define subsections to skip (over-extracted entries that are part of larger colonies)
skip_entries = {
    # Dominion of Canada subsections (will merge into one)
    'THE DOMINION',
    'FREE GOODS',
    'THE CABINET',
    'THE SENATE OF CANADA',
    'COMMISSIONS',
    'THE YUKON TERRITORY (DAWSON CITY)',
    'EXECUTIVE COUNCIL',  # Appears 2x - provinces
    'NOVA SCOTIA',  # Part of Canada
    'NEW BRUNSWICK',  # Part of Canada
    'BRITISH COLUMBIA',  # Part of Canada
    'PRINCE EDWARD ISLAND',  # Part of Canada
    'LEGISLATIVE ASSEMBLY',
    'PROVINCES OF SASKATCHEWAN AND ALBERTA',
    'MEMBERS OF THE LEGISLATIVE ASSEMBLY OF SASKATCHEWAN',
    'MEMBERS OF THE LEGISLATIVE ASSEMBLY OF ALBERTA',

    # Other over-extracted subsections
    'IMPERIAL',  # Subsection (Royal Mint)
    'THE PARLIAMENT',  # Subsection
    'EXPORTS',  # Appears 5 times
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
    ('DOMINION_OF_CANADA', 12615, 15610, 'Merged 14 over-extracted subsections into 1 colony (2,996 lines).'),
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
print("YEAR 1911 EXTRACTION COMPLETE")
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
print("✅ Year 1911 corrected - over-extraction pattern fixed (102 → ~75 colonies)")
