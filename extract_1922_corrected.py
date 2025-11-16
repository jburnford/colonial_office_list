#!/usr/bin/env python3
"""
Extract corrected 1922 colonies after manual boundary verification.

Year 1922 shows major over-extraction patterns (47 colonies extracted, but several are wrong):
- TASMANIA: Massive over-extraction (469K chars, 7298 lines) - captures content up to BAHAMAS
- VICTORIA, QUEENSLAND, WESTERN AUSTRALIA: Should NOT be separate - they're subsections of AUSTRALIA
- CAYMAN ISLANDS: Over-extraction (76K chars, 1217 lines) - includes TURKS AND CAICOS, KENYA, LEEWARD ISLANDS
- CAPE OF GOOD HOPE, NATAL, TRANSVAAL: Should NOT be separate - they're subsections of SOUTH AFRICA
- MAURITIUS: Over-extraction (280K chars, 3652 lines) - includes NEW ZEALAND
- ASCENSION: Massive over-extraction (1959K chars, 15658 lines) - captures everything to end of document
- TOBAGO: Should be merged with TRINIDAD

This script:
1. Fixes TASMANIA boundary (5191-5206 instead of 5190-12488)
2. Removes Australian state subsections (VICTORIA, QUEENSLAND, WESTERN AUSTRALIA)
3. Fixes CAYMAN ISLANDS boundary (25111-25151) and extracts TURKS AND CAICOS, KENYA, LEEWARD ISLANDS
4. Adds missing DOMINION OF CANADA (15241-18726)
5. Adds missing THE GOLD COAST (22465-22801)
6. Removes South African subsections (CAPE OF GOOD HOPE, NATAL, TRANSVAAL) and adds SOUTH AFRICA
7. Fixes MAURITIUS boundary (28328-29630) and extracts NEW ZEALAND
8. Merges TOBAGO into TRINIDAD AND TOBAGO
9. Adds TONGA (41157-41663)
10. Fixes ASCENSION boundary (43480-43485) and extracts TRISTAN DA CUNHA, SARAWAK
"""

import json
from pathlib import Path

# Load original metadata
with open('output/1922_manual_parsed.json', 'r') as f:
    original_data = json.load(f)

# Output directory
output_dir = Path('output_2/1922_manual_parsed')
output_dir.mkdir(parents=True, exist_ok=True)

# OCR source file
source_file = Path('historical_document_pipeline/processed_pdfs/colonial-office-list-1922/olmocr_results.md')

# Define subsections to skip (over-extracted entries that are part of larger colonies)
skip_entries = {
    # Australian states (subsections of AUSTRALIA)
    'VICTORIA',  # Part of AUSTRALIA
    'QUEENSLAND',  # Part of AUSTRALIA
    'WESTERN AUSTRALIA',  # Part of AUSTRALIA
    'TASMANIA',  # Will be corrected below

    # South African provinces (part of SOUTH AFRICA)
    'CAPE OF GOOD HOPE',  # Part of SOUTH AFRICA
    'NATAL',  # Part of SOUTH AFRICA
    'TRANSVAAL',  # Part of SOUTH AFRICA

    # Over-extracted colonies (will be corrected below)
    'BRITISH HONDURAS',  # Over-extraction - will be corrected
    'GIBRALTAR',  # Over-extraction - will be corrected
    'CAYMAN ISLANDS',  # Over-extraction - will be corrected
    'MAURITIUS',  # Over-extraction - will be corrected
    'SIERRA LEONE',  # Over-extraction - will be corrected
    'WEIHAIWEI',  # Over-extraction - will be corrected
    'PALESTINE',  # Over-extraction - will be corrected
    'ASCENSION',  # Over-extraction - will be corrected

    # Subsection of TRINIDAD AND TOBAGO
    'TOBAGO',  # Part of TRINIDAD AND TOBAGO
    'TRINIDAD',  # Will be merged with TOBAGO to create TRINIDAD AND TOBAGO
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
    ('TASMANIA', 5191, 5206, 'Fixed over-extraction: was 5190-12488 (7,298 lines), now 5191-5206 (16 lines).'),
    ('BRITISH_HONDURAS', 14880, 15240, 'Fixed over-extraction: was 14880-18726 (3,846 lines), now 14880-15240 (361 lines).'),
    ('DOMINION_OF_CANADA', 15241, 18726, 'Added missing colony (3,486 lines).'),
    ('GIBRALTAR', 22154, 22464, 'Fixed over-extraction: was 22154-22801 (647 lines), now 22154-22464 (311 lines).'),
    ('THE_GOLD_COAST', 22465, 22801, 'Added missing colony (337 lines).'),
    ('CAYMAN_ISLANDS', 25111, 25151, 'Fixed over-extraction: was 25110-26327 (1,217 lines), now 25111-25151 (41 lines).'),
    ('TURKS_AND_CAICOS_ISLANDS', 25154, 25327, 'Extracted from CAYMAN ISLANDS over-extraction (174 lines).'),
    ('THE_KENYA_COLONY_AND_PROTECTORATE', 25328, 26093, 'Extracted from CAYMAN ISLANDS over-extraction (766 lines).'),
    ('THE_LEEWARD_ISLANDS', 26094, 26327, 'Extracted from CAYMAN ISLANDS over-extraction (234 lines).'),
    ('MAURITIUS', 28328, 29630, 'Fixed over-extraction: was 28327-31979 (3,652 lines), now 28328-29630 (1,303 lines).'),
    ('NEW_ZEALAND', 29631, 31978, 'Extracted from MAURITIUS over-extraction (2,348 lines).'),
    ('SIERRA_LEONE', 32409, 33049, 'Fixed over-extraction: was 32409-33636 (1,227 lines), now 32409-33049 (641 lines).'),
    ('SOUTH_AFRICA', 33050, 35227, 'Merged CAPE OF GOOD HOPE, NATAL, TRANSVAAL subsections (2,178 lines).'),
    ('TRINIDAD_AND_TOBAGO', 38797, 40471, 'Merged TOBAGO subsection into TRINIDAD (1,675 lines).'),
    ('WEIHAIWEI', 40895, 41156, 'Fixed over-extraction: was 40895-41663 (768 lines), now 40895-41156 (262 lines).'),
    ('TONGA', 41157, 41663, 'Added missing colony (507 lines).'),
    ('PALESTINE', 42850, 43227, 'Fixed over-extraction: was 42850-43467 (617 lines), now 42850-43227 (378 lines).'),
    ('SARAWAK', 43228, 43466, 'Extracted from ASCENSION over-extraction (239 lines).'),
    ('ASCENSION', 43480, 43485, 'Fixed over-extraction: was 43479-59137 (15,658 lines), now 43480-43485 (6 lines).'),
    ('TRISTAN_DA_CUNHA', 43486, 43499, 'Extracted from ASCENSION over-extraction (14 lines).'),
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
