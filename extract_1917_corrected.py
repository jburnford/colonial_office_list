#!/usr/bin/env python3
"""
Extract corrected 1917 colonies after manual boundary verification.

Year 1917 shows significant issues (44 colonies parsed):
- Missing major dominions: DOMINION OF CANADA, NEW ZEALAND, SOUTH AFRICA
- Missing major protectorates: RHODESIA, NYASALAND, SOMALILAND, BECHUANALAND
- Missing colonies: THE GOLD COAST, ST. CHRISTOPHER AND NEVIS, VIRGIN ISLANDS, SARAWAK
- Over-extraction of Australian state subsections: VICTORIA, QUEENSLAND, WESTERN AUSTRALIA, TASMANIA (parliamentary representatives, not colonies)
- BRITISH COLUMBIA over-extracted (part of Canada, joined Confederation in 1871)
- TOBAGO over-extracted (part of TRINIDAD AND TOBAGO)
- ASCENSION incorrectly extended to end of document (should end at line 40812)

This script:
1. Merges Australian subsections back into AUSTRALIA (3590-4210)
2. Merges BRITISH COLUMBIA into DOMINION OF CANADA (13640-16954)
3. Merges TOBAGO into TRINIDAD AND TOBAGO (37308-38018)
4. Fixes ASCENSION boundary (40782-40786)
5. Adds missing major colonies and protectorates
6. Keeps all properly extracted colonies
"""

import json
from pathlib import Path

# Load original metadata
with open('output/1917_manual_parsed.json', 'r') as f:
    original_data = json.load(f)

# Output directory
output_dir = Path('output_2/1917_manual_parsed')
output_dir.mkdir(parents=True, exist_ok=True)

# OCR source file
source_file = Path('historical_document_pipeline/processed_pdfs/colonial-office-list-1917/olmocr_results.md')

# Define subsections to skip (over-extracted entries)
skip_entries = {
    # Australian state subsections (parliamentary representatives, not colonies)
    'VICTORIA',
    'QUEENSLAND',
    'WESTERN AUSTRALIA',
    'TASMANIA',

    # Canadian province (joined Confederation 1871)
    'BRITISH COLUMBIA',

    # Part of Trinidad and Tobago
    'TOBAGO',

    # Wrong boundaries
    'ASCENSION',
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

# Define the corrected/new colonies
corrected_colonies = [
    # AUSTRALIA with merged subsections (includes VICTORIA, QUEENSLAND, WESTERN AUSTRALIA, TASMANIA subsections)
    ('AUSTRALIA', 3590, 4210, 'Merged 5 over-extracted subsections (AUSTRALIA + 4 state parliamentary representative lists) into 1 colony (620 lines).'),

    # DOMINION OF CANADA with merged BRITISH COLUMBIA
    ('DOMINION_OF_CANADA', 13640, 16954, 'Merged BRITISH COLUMBIA (Canadian province since 1871) into DOMINION OF CANADA (3,315 lines).'),

    # Missing major dominions
    ('NEW_ZEALAND', 27641, 28770, 'Missing dominion - New Zealand (proclaimed dominion 1907) (1,130 lines).'),
    ('SOUTH_AFRICA', 31246, 33654, 'Missing dominion - Union of South Africa (formed 1910) (2,409 lines).'),

    # Missing major territories
    ('RHODESIA', 34051, 34681, 'Missing territory - Rhodesia (British South Africa Company administration) (631 lines).'),

    # Missing major colonies
    ('THE_GOLD_COAST', 20908, 21765, 'Missing colony - The Gold Coast Colony (858 lines).'),
    ('ST_CHRISTOPHER_AND_NEVIS', 24533, 25235, 'Missing colony - St. Christopher and Nevis Presidency (703 lines).'),
    ('VIRGIN_ISLANDS', 25386, 25528, 'Missing colony - Virgin Islands (Leeward Islands) (143 lines).'),

    # Missing protectorates
    ('NYASALAND_PROTECTORATE', 29733, 30037, 'Missing protectorate - Nyasaland Protectorate (305 lines).'),
    ('SOMALILAND_PROTECTORATE', 31094, 31246, 'Missing protectorate - Somaliland Protectorate (153 lines).'),
    ('BECHUANALAND_PROTECTORATE', 33795, 33874, 'Missing protectorate - Bechuanaland Protectorate (80 lines).'),

    # Missing protected states
    ('SARAWAK', 40540, 40771, 'Missing protected state - Sarawak (under British protection since 1888) (232 lines).'),

    # Corrected boundaries
    ('ASCENSION', 40782, 40786, 'Corrected ASCENSION boundaries (5 lines, was incorrectly 15,284 lines to end of document).'),
    ('TRISTAN_DA_CUNHA', 40786, 40799, 'Missing island - Tristan da Cunha (14 lines).'),
    ('MISCELLANEOUS_ISLANDS', 40799, 40812, 'Missing section - Miscellaneous Islands (14 lines).'),

    # TRINIDAD AND TOBAGO merged
    ('TRINIDAD_AND_TOBAGO', 37308, 38018, 'Merged TRINIDAD AND TOBAGO (TOBAGO was over-extracted separately) (711 lines).'),
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
print("YEAR 1917 EXTRACTION COMPLETE")
print("=" * 80)
print(f"\nOriginal colonies in metadata: {len(original_data['colonies'])}")
print(f"Kept (properly extracted):      {len(kept)}")
print(f"Skipped (over-extracted):       {len(skipped)}")
print(f"Corrected/Added (merged+new):   {len(corrected)}")
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
print("Corrected/Added colonies:")
for colony in corrected:
    print(f"  - {colony['name']}: {colony['start']}-{colony['end']} ({colony['lines']} lines)")
    print(f"    {colony['note']}")
print()
print(f"Output directory: {output_dir}")
print("✅ Year 1917 corrected - major missing dominions/colonies added, over-extraction fixed (44 → ~54 colonies)")
