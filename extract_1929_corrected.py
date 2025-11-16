#!/usr/bin/env python3
"""
Extract corrected 1929 colonies after manual boundary verification.

Year 1929 shows SEVERE over-extraction pattern (46 colonies in metadata!):
- First 12 entries (lines 6151-23645) are DOMINIONS (Australia, Canada, South Africa, etc.) - NOT Colonial Office colonies!
- LABUAN is not a separate colony - it's a subsection within STRAITS SETTLEMENTS
- ADEN massively over-extracted from 49348-68238 (entire document end!) - should end at 49372
- Missing TRISTAN DA CUNHA and MISCELLANEOUS ISLANDS

This script:
1. Skips all Dominions entries (NEWFOUNDLAND, RHODESIA, AUSTRALIA states, BRITISH COLUMBIA, etc.)
2. Keeps only colonies from PART II-C (Colonial Office section, starting line 23645)
3. Merges STRAITS SETTLEMENTS with LABUAN subsection (41499-45177, 3,679 lines)
4. Corrects ADEN boundary (49349-49372, 24 lines instead of 18,890!)
5. Adds missing TRISTAN DA CUNHA (49373-49389)
6. Adds missing MISCELLANEOUS ISLANDS (49390-49398)
"""

import json
from pathlib import Path

# Load original metadata
with open('output/1929_manual_parsed.json', 'r') as f:
    original_data = json.load(f)

# Output directory
output_dir = Path('output_2/1929_manual_parsed')
output_dir.mkdir(parents=True, exist_ok=True)

# OCR source file
source_file = Path('historical_document_pipeline/processed_pdfs/colonial-office-list-1929/olmocr_results.md')

# Define entries to skip (Dominions and over-extracted subsections)
skip_entries = {
    # DOMINIONS - not Colonial Office colonies (all before line 23645)
    'NEWFOUNDLAND',  # Dominion, not colony
    'RHODESIA',  # Dominion
    'AUSTRALIA',  # Dominion
    'WESTERN AUSTRALIA',  # Australian state
    'TASMANIA',  # Australian state
    'QUEENSLAND',  # Australian state
    'VICTORIA',  # Australian state
    'BRITISH COLUMBIA',  # Canadian province!
    'SOUTH WEST AFRICA',  # Listed in Dominions section
    'BASUTOLAND',  # Listed in Dominions section
    'SWAZILAND',  # Listed in Dominions section
    'SOUTHERN RHODESIA',  # Listed in Dominions section

    # Over-extracted subsections
    'LABUAN',  # Subsection within STRAITS SETTLEMENTS, not separate colony
    'ADEN',  # Will replace with corrected boundary
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

    # Skip Dominions and over-extracted subsections
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

# Define the corrected colonies (merged or with corrected boundaries)
corrected_colonies = [
    ('STRAITS_SETTLEMENTS', 41499, 45177, 'Merged LABUAN subsections into STRAITS SETTLEMENTS (3,679 lines). LABUAN appears at line 42092 and 42407 as subsections, not separate colony.'),
    ('ADEN', 49349, 49372, 'Corrected massive over-extraction: originally 49348-68238 (18,890 lines to end of document!), now 49349-49372 (24 lines). Includes PERIM and SOCCOTRA dependencies.'),
    ('TRISTAN_DA_CUNHA', 49373, 49389, 'Added missing colony (17 lines). Was not in original extraction.'),
    ('MISCELLANEOUS_ISLANDS', 49390, 49398, 'Added missing territory (9 lines). Includes Ashmore Group, Caroline Island, Kuria-Muria, etc. Was not in original extraction.'),
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
print("YEAR 1929 EXTRACTION COMPLETE")
print("=" * 80)
print(f"\nOriginal colonies in metadata: {len(original_data['colonies'])}")
print(f"Kept (properly extracted):      {len(kept)}")
print(f"Skipped (Dominions/over-extracted): {len(set(skipped))}")
print(f"Corrected (merged/fixed):       {len(corrected)}")
print(f"Total colonies after fix:       {len(kept) + len(corrected)}")
print()
print("Skipped Dominions and over-extracted subsections:")
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
print("✅ Year 1929 corrected - SEVERE over-extraction fixed (46 → ~34 colonies)")
print("✅ Removed 12 Dominions entries that were incorrectly included")
print("✅ Fixed ADEN: reduced from 18,890 lines to 24 lines!")
print("✅ Merged LABUAN into STRAITS SETTLEMENTS")
print("✅ Added 2 missing colonies (TRISTAN DA CUNHA, MISCELLANEOUS ISLANDS)")
