#!/usr/bin/env python3
"""
Extract corrected 1928 colonies after manual boundary verification.

Year 1928 shows over-extraction pattern (49 colonies):
- WESTERN AUSTRALIA split from AUSTRALIA as separate colony
- LABUAN split from STRAITS SETTLEMENTS as separate colony (2,865 lines!)
- TRINIDAD and TOBAGO split as 2 separate colonies instead of 1
- ADEN massively over-extracted (18,894 lines going to end of file!)
- Missing colonies: TRISTAN DA CUNHA and MISCELLANEOUS ISLANDS

This script:
1. Merges AUSTRALIA with WESTERN AUSTRALIA subsection (8003-8654)
2. Merges STRAITS SETTLEMENTS with LABUAN subsection (45998-49478)
3. Merges TRINIDAD AND TOBAGO from 2 subsections (49477-50623)
4. Corrects ADEN massive over-extraction (54632-54655, not 54632-73526!)
5. Adds missing colonies: TRISTAN DA CUNHA (54656-54670) and MISCELLANEOUS ISLANDS (54671-54679)
6. Skips all over-extracted subsections
7. Keeps all properly extracted colonies
"""

import json
from pathlib import Path

# Load original metadata
with open('output/1928_manual_parsed.json', 'r') as f:
    original_data = json.load(f)

# Output directory
output_dir = Path('output_2/1928_manual_parsed')
output_dir.mkdir(parents=True, exist_ok=True)

# OCR source file
source_file = Path('historical_document_pipeline/processed_pdfs/colonial-office-list-1928/olmocr_results.md')

# Define subsections to skip (over-extracted entries that are part of larger colonies)
skip_entries = {
    # Australian subsections
    'WESTERN AUSTRALIA',  # Part of AUSTRALIA (line 8642-8654)

    # Straits Settlements subsections
    'LABUAN',  # Part of STRAITS SETTLEMENTS (line 46613-49478, 2,865 lines!)

    # Trinidad subsections (will merge into one)
    'TRINIDAD',  # Part of TRINIDAD AND TOBAGO (49478-49683)
    'TOBAGO',   # Part of TRINIDAD AND TOBAGO (49683-50623)

    # Over-extracted main entry (will replace with corrected version)
    'ADEN',  # Massively over-extracted: 54632-73526 (should be 54632-54655)

    # We need to manually handle AUSTRALIA and STRAITS SETTLEMENTS
    'AUSTRALIA',  # Will replace with merged version
    'STRAITS SETTLEMENTS',  # Will replace with merged version
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

# Define the corrected colonies (merged from subsections or corrected boundaries)
corrected_colonies = [
    ('AUSTRALIA', 8003, 8654, 'Merged WESTERN AUSTRALIA subsection (8642-8654, 12 lines) into AUSTRALIA.'),
    ('STRAITS_SETTLEMENTS', 45998, 49478, 'Merged LABUAN subsection (46613-49478, 2,865 lines) into STRAITS SETTLEMENTS.'),
    ('TRINIDAD_AND_TOBAGO', 49477, 50623, 'Merged TRINIDAD (49478-49683) and TOBAGO (49683-50623) subsections into one colony (1,147 lines).'),
    ('ADEN', 54632, 54655, 'Corrected MASSIVE over-extraction: was 54632-73526 (18,894 lines!), now 54632-54655 (24 lines). Original extraction went to end of file!'),
    ('TRISTAN_DA_CUNHA', 54656, 54670, 'Added missing colony TRISTAN DA CUNHA (15 lines) - was not in original extraction.'),
    ('MISCELLANEOUS_ISLANDS', 54671, 54679, 'Added missing colony MISCELLANEOUS ISLANDS (9 lines) - was not in original extraction.'),
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
print("YEAR 1928 EXTRACTION COMPLETE")
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
print("Corrected/merged colonies:")
for colony in corrected:
    print(f"  - {colony['name']}: {colony['start']}-{colony['end']} ({colony['lines']} lines)")
    print(f"    {colony['note']}")
print()
print(f"Output directory: {output_dir}")
print(f"✅ Year 1928 corrected - over-extraction pattern fixed (49 → {len(kept) + len(corrected)} colonies)")
print("⚠️  ADEN was SEVERELY over-extracted: 18,894 lines → 24 lines!")
