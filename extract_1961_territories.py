#!/usr/bin/env python3
"""
Extract 1961 territories - First-time parsing (not a fix).

Year 1961 is a transition period with many territories gaining independence.
The structure includes traditional colonies plus newly independent nations.

Based on manual analysis of olmocr_results.md, this extracts main territory sections.
"""

import json
from pathlib import Path

# Output directory
output_dir = Path('output_2/1961_manual_parsed')
output_dir.mkdir(parents=True, exist_ok=True)

# OCR source file
source_file = Path('historical_document_pipeline/processed_pdfs/colonial-office-list-1961/olmocr_results.md')

# Read source file
with open(source_file, 'r') as f:
    source_lines = f.readlines()

# Define territories manually identified from analysis
# Format: (name, start_line, end_line, notes)
territories = [
    ('STATE_OF_SINGAPORE', 3489, 4890, 'Full internal self-government as of 1959'),
    ('BERMUDA', 4891, 5252, 'Crown Colony'),
    ('BRITISH_GUIANA', 5253, 5668, 'Colony with internal self-government'),
    ('BRITISH_HONDURAS', 5669, 6039, 'Crown Colony'),
    ('BRUNEI', 6040, 6436, 'Protectorate'),
    ('FALKLAND_ISLANDS', 6437, 6788, 'Colony with dependencies'),
    ('FIJI', 6789, 7137, 'Colony (includes Pitcairn Islands)'),
    ('GAMBIA', 7138, 7536, 'Colony and Protectorate'),
    ('GIBRALTAR', 7537, 7801, 'Crown Colony'),
    ('HONG_KONG', 7802, 8180, 'Crown Colony'),
    ('KENYA', 8181, 8769, 'Colony and Protectorate'),
    ('MALTA', 8770, 9214, 'Crown Colony'),
    ('MAURITIUS', 9215, 9585, 'Colony'),
    ('NORTH_BORNEO', 9592, 9985, 'Crown Colony'),
    ('NORTHERN_RHODESIA', 9994, 10623, 'Protectorate (part of Federation)'),
    ('NYASALAND', 10624, 11041, 'Protectorate (part of Federation)'),
    ('ST_HELENA', 11042, 11313, 'Colony (includes Ascension, Tristan da Cunha)'),
    ('SARAWAK', 11314, 11658, 'Colony'),
    ('SEYCHELLES', 11659, 11974, 'Colony'),
    ('SIERRA_LEONE', 11975, 12399, 'Colony and Protectorate'),
    ('TANGANYIKA', 12406, 12846, 'Trust Territory'),
    ('TONGA', 12847, 12994, 'Protected State'),
    ('UGANDA', 12995, 13460, 'Protectorate'),
    ('VIRGIN_ISLANDS', 13461, 17047, 'Colony'),
    ('BRITISH_SOLOMON_ISLANDS', 17048, 17290, 'Protectorate'),
    ('GILBERT_AND_ELLICE_ISLANDS', 17291, 17446, 'Colony'),
    ('NEW_HEBRIDES', 17447, 17625, 'Anglo-French Condominium'),
    ('ZANZIBAR', 17626, 17946, 'Protectorate'),
]

# Extract and write each territory
extracted = []
for name, start, end, notes in territories:
    # Extract content
    content_lines = source_lines[start-1:end]
    content = ''.join(content_lines)

    # Create filename
    filename = name + '.md'

    # Write file
    output_file = output_dir / filename
    with open(output_file, 'w') as f:
        f.write(content)

    extracted.append({
        'name': name.replace('_', ' '),
        'filename': filename,
        'start': start,
        'end': end,
        'lines': end - start + 1,
        'notes': notes
    })

# Print summary
print("=" * 80)
print("YEAR 1961 EXTRACTION COMPLETE")
print("=" * 80)
print(f"\nTotal territories extracted: {len(extracted)}")
print()
print("Territories:")
for territory in extracted:
    print(f"  - {territory['name']}: {territory['start']}-{territory['end']} ({territory['lines']} lines)")
    if territory['notes']:
        print(f"    Note: {territory['notes']}")
print()
print(f"Output directory: {output_dir}")
print("✅ Year 1961 parsed - First-time extraction (not a fix)")
print("ℹ️  Note: 1961 is transition period - many territories gaining/gained independence")
print("ℹ️  Nigeria became independent October 1, 1960")
print("ℹ️  Sierra Leone became independent April 27, 1961")
print("ℹ️  Somaliland became independent June 26, 1960 (not extracted separately)")
