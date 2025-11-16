#!/usr/bin/env python3
"""
Extract corrected 1921 colonies after manual boundary verification.

Year 1921 shows major over-extraction patterns (48 colonies extracted, but several are wrong):
- Australian states (QUEENSLAND, TASMANIA, VICTORIA, WESTERN AUSTRALIA): Should NOT be separate - they're states of AUSTRALIA
- BRITISH HONDURAS: Massive over-extraction (3,285 lines) - captures DOMINION OF CANADA
- BRITISH COLUMBIA: Should NOT be separate - it's a province of DOMINION OF CANADA
- CAYMAN ISLANDS: Massive over-extraction (1,022 lines) - captures THE KENYA COLONY and THE LEEWARD ISLANDS
- TOBAGO: Should NOT be separate - it's part of TRINIDAD AND TOBAGO
- ASCENSION: Massive over-extraction (20,698 lines) - captures everything to end of document

This script:
1. Removes duplicate Australian state entries (QUEENSLAND, TASMANIA, VICTORIA, WESTERN AUSTRALIA)
2. Fixes BRITISH HONDURAS boundary (ends at line 15046)
3. Merges BRITISH COLUMBIA into DOMINION OF CANADA
4. Fixes CAYMAN ISLANDS boundary (ends at line 24630)
5. Extracts THE KENYA COLONY AND PROTECTORATE and THE LEEWARD ISLANDS separately
6. Merges TOBAGO into TRINIDAD AND TOBAGO
7. Fixes ASCENSION boundary and extracts TRISTAN DA CUNHA separately
"""

import json
from pathlib import Path

# Load original metadata
with open('output/1921_manual_parsed.json', 'r') as f:
    original_data = json.load(f)

# Output directory
output_dir = Path('output_2/1921_manual_parsed')
output_dir.mkdir(parents=True, exist_ok=True)

# OCR source file
source_file = Path('historical_document_pipeline/processed_pdfs/colonial-office-list-1921/olmocr_results.md')

# Define subsections to skip (over-extracted entries that are part of larger colonies)
skip_entries = {
    # Australian states (subsections of AUSTRALIA)
    'QUEENSLAND',  # Part of AUSTRALIA
    'TASMANIA',  # Part of AUSTRALIA
    'VICTORIA',  # Part of AUSTRALIA
    'WESTERN AUSTRALIA',  # Part of AUSTRALIA

    # Canadian province (part of DOMINION OF CANADA)
    'BRITISH COLUMBIA',  # Part of DOMINION OF CANADA (merged below)

    # Over-extracted colonies (will be corrected below)
    'BRITISH HONDURAS',  # Over-extraction - will be corrected
    'CAYMAN ISLANDS',  # Over-extraction - will be corrected
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
    ('BRITISH_HONDURAS', 14599, 15046, 'Fixed over-extraction: was 14599-17884 (3,285 lines), now 14599-15046 (448 lines).'),
    ('DOMINION_OF_CANADA', 15047, 18721, 'Merged BRITISH COLUMBIA into DOMINION OF CANADA (3,675 lines).'),
    ('CAYMAN_ISLANDS', 24593, 24630, 'Fixed over-extraction: was 24593-25614 (1,022 lines), now 24593-24630 (38 lines).'),
    ('THE_KENYA_COLONY_AND_PROTECTORATE', 24631, 25399, 'Extracted from CAYMAN ISLANDS over-extraction (769 lines).'),
    ('THE_LEEWARD_ISLANDS', 25400, 25614, 'Extracted from CAYMAN ISLANDS over-extraction (215 lines).'),
    ('TRINIDAD_AND_TOBAGO', 37327, 38943, 'Merged TOBAGO subsection (was 2 entries: TRINIDAD 37327-37504 + TOBAGO 37504-38943, now 1; 1,617 lines).'),
    ('ASCENSION', 42236, 42252, 'Fixed over-extraction: was 42235-62933 (20,698 lines), now 42236-42252 (17 lines).'),
    ('TRISTAN_DA_CUNHA', 42253, 42262, 'Extracted from ASCENSION over-extraction (10 lines).'),
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
