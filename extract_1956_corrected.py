#!/usr/bin/env python3
"""
Extract corrected 1956 colonies after manual boundary verification.

Issues found in parser output:
- Lines 2976-3606: Table of contents entries (19 entries) - SKIP ALL
- SIERRA LEONE (3144-3606): Also table of contents filler - SKIP
- MONTSERRAT (9663-11053): Over-extraction, includes BRITISH VIRGIN ISLANDS, FEDERATION OF MALAYA, MALTA
- Missing colonies: BRITISH VIRGIN ISLANDS, FEDERATION OF MALAYA, MALTA, FEDERATION OF NIGERIA,
  NORTHERN RHODESIA, FEDERATION OF RHODESIA AND NYASALAND, NYASALAND, THE GOLD COAST (actual section),
  FALKLAND ISLANDS, KENYA, SARAWAK, SINGAPORE, SOMALILAND, TONGA, TRINIDAD AND TOBAGO,
  BRITISH SOLOMON ISLANDS, GILBERT AND ELLICE, NEW HEBRIDES, GRENADA

This script manually extracts with corrected boundaries.
"""

import json
from pathlib import Path

# Load original metadata to use as base
with open('output/1956_parsed_v5_final.json', 'r') as f:
    original_data = json.load(f)

# Output directory
output_dir = Path('output_2/1956_manual_parsed')
output_dir.mkdir(parents=True, exist_ok=True)

# OCR source file
source_file = Path('historical_document_pipeline/processed_pdfs/colonial-office-list-1956/olmocr_results.md')

# Read source file
with open(source_file, 'r') as f:
    source_lines = f.readlines()

# Track statistics
kept = []
skipped = []
corrected = []

# Keep properly extracted colonies (from line 3606 onwards)
for colony in original_data['colonies']:
    name = colony['colony_name']
    start = colony['start_line']
    end = colony['end_line']

    # Skip table of contents entries (before PART II)
    if start < 3606:
        skipped.append(f"{name} (table of contents)")
        continue

    # Skip the over-extracted MONTSERRAT - we'll fix it below
    if name == 'MONTSERRAT' and start == 9663:
        skipped.append(name + ' (over-extracted)')
        continue

    # Keep the rest

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

print(f"Kept {len(kept)} properly extracted colonies")
print(f"Skipped {len(skipped)} entries: {skipped}")

# Define corrected/new colonies
# Based on manual OCR verification
corrected_colonies = [
    # Fix MONTSERRAT boundary
    ('MONTSERRAT', 9664, 9944, 'Fixed over-extraction'),
    ('BRITISH_VIRGIN_ISLANDS', 9944, 10070, 'Added missing colony'),
    ('FEDERATION_OF_MALAYA', 10070, 11402, 'Added missing colony - includes MALTA subsection'),
    ('FEDERATION_OF_NIGERIA', 11402, 12017, 'Added missing colony'),
    ('NORTHERN_RHODESIA', 12293, 12329, 'Added missing colony'),
    ('FEDERATION_OF_RHODESIA_AND_NYASALAND', 12329, 12790, 'Added missing colony'),
    ('NYASALAND_PROTECTORATE', 12790, 13136, 'Added missing colony'),
    ('SARAWAK', 13420, 13704, 'Added missing colony'),
    ('SINGAPORE', 14262, 14719, 'Added missing colony'),
    ('SOMALILAND_PROTECTORATE', 14719, 15404, 'Added missing colony'),
    ('KINGDOM_OF_TONGA', 15404, 15547, 'Added missing colony'),
    ('TRINIDAD_AND_TOBAGO', 15547, 15903, 'Added missing colony'),
    ('BRITISH_SOLOMON_ISLANDS_PROTECTORATE', 16283, 16465, 'Added missing colony'),
    ('GILBERT_AND_ELLICE_ISLANDS_COLONY', 16465, 16631, 'Added missing colony'),
    ('NEW_HEBRIDES_CONDOMINIUM', 16631, 16756, 'Added missing colony'),
    ('GRENADA', 17099, 17371, 'Added missing colony'),
]

# Extract corrected colonies
for name, start, end, note in corrected_colonies:
    content_lines = source_lines[start-1:end]
    content = ''.join(content_lines)

    filename = name + '.md'
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

print(f"\nCorrected/added {len(corrected)} colonies:")
for c in corrected:
    print(f"  {c['name']:45s}: {c['note']}")

# Print summary
total_corrected = len(kept) + len(corrected)
print(f"\n=== SUMMARY ===")
print(f"Original extraction: {len(original_data['colonies'])} colonies")
print(f"Skipped (table of contents/over-extracted): {len(skipped)}")
print(f"Kept (properly extracted): {len(kept)}")
print(f"Corrected/added: {len(corrected)}")
print(f"Final total: {total_corrected} colonies")
print(f"\nChange: {len(original_data['colonies'])} → {total_corrected}")
print(f"\nOutput directory: {output_dir}/")
