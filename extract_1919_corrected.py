#!/usr/bin/env python3
"""
Extract corrected 1919 colonies after manual boundary verification.

Year 1919 shows major over-extraction patterns (42 colonies extracted, but several are wrong):
- TASMANIA: Massive over-extraction (454K chars) - captures thousands of lines of AUSTRALIA subsections
- BRITISH COLUMBIA: Should NOT be separate - it's a province of DOMINION OF CANADA
- SIERRA LEONE: Over-extraction (247K chars) - includes SOMALILAND and SOUTH AFRICA
- LABUAN: Over-extraction (110K chars) - includes TRINIDAD AND TOBAGO
- ASCENSION: Massive over-extraction (2M chars) - captures everything to end of document

This script:
1. Fixes TASMANIA boundary (4292-4298 instead of 4291-11606)
2. Merges BRITISH COLUMBIA into DOMINION OF CANADA
3. Fixes SIERRA LEONE boundary and extracts SOMALILAND, SOUTH AFRICA separately
4. Fixes LABUAN boundary and extracts TRINIDAD AND TOBAGO, LEEWARD ISLANDS separately
5. Fixes ASCENSION boundary (40547-40550)
6. Removes TOBAGO (it's a subsection of TRINIDAD AND TOBAGO, not separate)
7. Removes duplicate/subsection Australian states (VICTORIA, QUEENSLAND, WESTERN AUSTRALIA)
"""

import json
from pathlib import Path

# Load original metadata
with open('output/1919_manual_parsed.json', 'r') as f:
    original_data = json.load(f)

# Output directory
output_dir = Path('output_2/1919_manual_parsed')
output_dir.mkdir(parents=True, exist_ok=True)

# OCR source file
source_file = Path('historical_document_pipeline/processed_pdfs/colonial-office-list-1919/olmocr_results.md')

# Define subsections to skip (over-extracted entries that are part of larger colonies)
skip_entries = {
    # Australian states (subsections of AUSTRALIA)
    'VICTORIA',  # Part of AUSTRALIA
    'QUEENSLAND',  # Part of AUSTRALIA
    'WESTERN AUSTRALIA',  # Part of AUSTRALIA
    'TASMANIA',  # Will be corrected below

    # Canadian province (part of DOMINION OF CANADA)
    'BRITISH COLUMBIA',  # Part of DOMINION OF CANADA (merged below)

    # Over-extracted colonies (will be corrected below)
    'CAYMAN ISLANDS',  # Over-extraction - will be corrected
    'NEWFOUNDLAND',  # Over-extraction - will be corrected
    'SIERRA LEONE',  # Over-extraction - will be corrected
    'LABUAN',  # Over-extraction - will be corrected
    'ASCENSION',  # Over-extraction - will be corrected

    # Subsection of TRINIDAD AND TOBAGO
    'TOBAGO',  # Part of TRINIDAD AND TOBAGO
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

    # Skip over-extracted subsections and duplicates
    if name in skip_entries:
        skipped.append(name)
        continue

    # Keep properly extracted colonies
    start = colony['start_line']
    end = colony['end_line']

    # Extract content (1-indexed in JSON, 0-indexed in Python)
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
print(f"Skipped {len(skipped)} over-extracted/duplicate entries: {sorted(skipped)}")

# Define the corrected colonies (fixed boundaries or merged from subsections)
corrected_colonies = [
    ('TASMANIA', 4292, 4298, 'Fixed over-extraction: was 4291-11606 (7,315 lines), now 4292-4298 (7 lines).'),
    ('DOMINION_OF_CANADA', 14292, 17532, 'Merged BRITISH COLUMBIA into DOMINION OF CANADA (3,241 lines).'),
    ('CAYMAN_ISLANDS', 24147, 24184, 'Fixed over-extraction: was 24146-24388 (242 lines), now 24147-24184 (38 lines).'),
    ('NEWFOUNDLAND', 27298, 27672, 'Fixed over-extraction: was 27297-28632 (1,335 lines), now 27298-27672 (375 lines).'),
    ('NEW_ZEALAND', 27673, 28632, 'Extracted from NEWFOUNDLAND over-extraction (960 lines).'),
    ('SIERRA_LEONE', 30464, 30947, 'Fixed over-extraction: was 30463-33406 (2,943 lines), now 30464-30947 (484 lines).'),
    ('SOMALILAND_PROTECTORATE', 30948, 31097, 'Extracted from SIERRA LEONE over-extraction (150 lines).'),
    ('SOUTH_AFRICA', 31098, 33406, 'Extracted from SIERRA LEONE over-extraction (2,309 lines).'),
    ('LABUAN', 34972, 36123, 'Fixed over-extraction: was 34971-36315 (1,344 lines), now 34972-36123 (1,152 lines).'),
    ('TRINIDAD_AND_TOBAGO', 36124, 38095, 'Merged TOBAGO subsection (was 2 entries, now 1; 1,972 lines).'),
    ('ASCENSION', 40547, 40550, 'Fixed over-extraction: was 40546-58735 (18,189 lines), now 40547-40550 (4 lines).'),
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

print(f"\nCorrected {len(corrected)} colonies:")
for c in corrected:
    print(f"  {c['name']}: {c['note']}")

# Print summary
total_corrected = len(kept) + len(corrected)
print(f"\n=== SUMMARY ===")
print(f"Original extraction: {len(original_data['colonies'])} colonies")
print(f"Skipped (over-extracted/duplicates): {len(skipped)}")
print(f"Kept (properly extracted): {len(kept)}")
print(f"Corrected (fixed boundaries/merged): {len(corrected)}")
print(f"Final total: {total_corrected} colonies")
print(f"\nChange: {len(original_data['colonies'])} → {total_corrected}")
