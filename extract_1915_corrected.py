#!/usr/bin/env python3
"""
Extract corrected 1915 colonies after manual boundary verification.

Year 1915 shows severe over-extraction pattern similar to 1906-1911 (105 colonies):
- Commonwealth of Australia split into 15 subsections (states, territories, departments)
- Dominion of Canada split into 11 subsections (provinces, assemblies, councils)
- South Africa split into 8 subsections (provinces, courts, officials)
- Multiple over-extracted subsections: EXPORTS (5x), IMPORTS (2x), CEYLON (2x), etc.

This script:
1. Merges COMMONWEALTH OF AUSTRALIA from 15 subsections (3537-11000, ~7,464 lines)
2. Merges DOMINION OF CANADA from 11 subsections (13452-16697, ~3,246 lines)
3. Merges CEYLON from 3 subsections (16698-17742, ~1,045 lines)
4. Merges NEW ZEALAND from 5 subsections (26544-27628, ~1,085 lines)
5. Merges NIGERIA from 4 subsections (27629-28646, ~1,018 lines)
6. Merges MAURITIUS from 5 subsections (25249-26543, ~1,295 lines)
7. Merges SOUTH AFRICA from 8 subsections (30145-32528, ~2,384 lines)
8. Skips all over-extracted subsections
9. Keeps all properly extracted colonies
"""

import json
from pathlib import Path

# Load original metadata
with open('output/1915_manual_parsed.json', 'r') as f:
    original_data = json.load(f)

# Output directory
output_dir = Path('output_2/1915_manual_parsed')
output_dir.mkdir(parents=True, exist_ok=True)

# OCR source file
source_file = Path('historical_document_pipeline/processed_pdfs/colonial-office-list-1915/olmocr_results.md')

# Define subsections to skip (over-extracted entries that are part of larger colonies)
skip_entries = {
    # Commonwealth of Australia subsections (will merge into one)
    'THE COMMONWEALTH',  # Start of Australia
    'TASMANIA',  # Appears 2x - once as list, once as state
    'NEW SOUTH WALES',
    'STATE',  # NSW subsection
    'SYDNEY HARBOUR TRUST',  # NSW subsection
    'INDUSTRIAL UNDERTAKINGS',  # Subsection
    'QUEENSLAND',
    'SOUTH AUSTRALIA',
    'COURT OF INSOLVENCY',  # SA subsection
    'COMMONWEALTH CONTROL',  # Subsection
    'VICTORIA',
    'WESTERN AUSTRALIA',
    'PUBLIC LIBRARY OF WESTERN AUSTRALIA',  # WA subsection
    'THE NORTHERN TERRITORY',
    'PAPUA',  # Territory dependent on Commonwealth

    # Dominion of Canada subsections (will merge into one)
    'THE DOMINION',  # Start of Canada
    'SHIPPING ENTERED AND CLEARED',  # Canada subsection
    'THE SENATE OF CANADA',
    'HOUSE OF COMMONS',
    'THE YUKON TERRITORY (DAWSON CITY)',
    'EXECUTIVE COUNCIL',  # Appears 2x - provinces
    'MANITOBA',
    'MEMBERS OF THE LEGISLATIVE ASSEMBLY OF SASKATCHEWAN',
    'PROVINCE OF ALBERTA',
    'MEMBERS OF THE LEGISLATIVE ASSEMBLY OF THE PROVINCE OF ALBERTA',

    # Ceylon subsections (will merge into one)
    'CEYLON',  # Appears 2x
    'EASTERN PROVINCE',  # Ceylon subsection

    # Mauritius and subsections (will merge into one)
    'MAURITIUS',  # Main entry - will be replaced with merged version
    'DEPENDENCIES',  # Mauritius dependencies
    'PUBLIC WORKS AND SURVEYS',  # Mauritius subsection
    'EDUCATION',  # Mauritius subsection
    'FINANCES',  # Mauritius subsection

    # New Zealand and subsections (will merge into one)
    'NEW ZEALAND',  # Main entry - will be replaced with merged version
    'PALMERSTON ATOLL',  # NZ dependency
    'LEGISLATIVE COUNCIL',  # NZ subsection
    'HOUSE OF REPRESENTATIVES',  # NZ subsection
    'LAND TRANSFER AND DEEDS REGISTRY',  # NZ subsection

    # Nigeria and subsections (will merge into one)
    'NIGERIA',  # Main entry - will be replaced with merged version
    'GOVERNORS AND HIGH COMMISSIONERS',  # Nigeria subsection
    'NORTHERN PROVINCES',  # Nigeria subsection
    'INFANTRY',  # Nigeria military subsection

    # South Africa and subsections (will merge into one)
    'SOUTH AFRICA',  # Main entry - will be replaced with merged version
    'RAILWAYS AND HARBOURS BOARDS',  # SA subsection
    'SUPREME COURT OF SOUTH AFRICA',  # SA subsection
    'CAPE OF GOOD HOPE PROVINCE',  # SA province
    'PROVINCIAL COUNCIL',  # SA province subsection
    'PROVINCE OF NATAL',  # SA province
    'TRANSVAAL PROVINCE',  # SA province
    'LOUIS BOTHA',  # Incorrectly extracted - person's name/signature

    # Other over-extracted subsections
    'EXPORTS',  # Appears 5 times
    'IMPORTS',  # Appears 2 times
    'GOVERNMENT STORE',  # Fiji subsection
    'AGRICULTURAL SERVICES',  # Jamaica subsection
    'BARBUDA',  # Leeward Islands subsection
    'DOMINICA',  # Leeward Islands subsection
    'MONTSERRAT',  # Leeward Islands subsection
    'VIRGIN ISLANDS',  # Leeward Islands subsection
    'FEDERAL COUNCIL',  # Malay subsection
    'PRINCIPAL GROUPS UNDER THE HIGH COMMISSIONER',  # Western Pacific subsection
    'GRENA DA',  # OCR error - should be GRENADA, part of Windward Islands
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
    ('COMMONWEALTH_OF_AUSTRALIA', 3537, 11000, 'Merged 16 over-extracted subsections into 1 colony (7,464 lines): states, territories (Papua, Northern Territory), departments.'),
    ('DOMINION_OF_CANADA', 13452, 16697, 'Merged 11 over-extracted subsections into 1 colony (3,246 lines): provinces, assemblies, councils.'),
    ('CEYLON', 16698, 17742, 'Merged 3 over-extracted subsections into 1 colony (1,045 lines): main entry, exports, provinces.'),
    ('MAURITIUS', 25249, 26543, 'Merged 5 over-extracted subsections into 1 colony (1,295 lines): dependencies, public works, education, finances.'),
    ('NEW_ZEALAND', 26544, 27628, 'Merged 5 over-extracted subsections into 1 colony (1,085 lines): dependencies, councils, registries.'),
    ('NIGERIA', 27629, 28646, 'Merged 4 over-extracted subsections into 1 colony (1,018 lines): governors, provinces, military.'),
    ('SOUTH_AFRICA', 30145, 32528, 'Merged 8 over-extracted subsections into 1 colony (2,384 lines): provinces, courts, councils.'),
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
print("YEAR 1915 EXTRACTION COMPLETE")
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
print(f"✅ Year 1915 corrected - over-extraction pattern fixed (105 → {len(kept) + len(corrected)} colonies)")
