#!/usr/bin/env python3
"""
Extract 1927 colonies with manual LLM boundary identification for output_3.
All boundaries manually verified by reading OCR content.
"""

import json
from pathlib import Path
from datetime import datetime

# Source file
source_file = Path('historical_document_pipeline/processed_pdfs/colonial-office-list-1927/olmocr_results.md')

# Output directory
output_dir = Path('output_3/1927_manual_parsed')
output_dir.mkdir(parents=True, exist_ok=True)

# Manually identified colony boundaries
# Each entry: (name, start_line, note)
# End line is determined as the line before the next colony starts
colonies = [
    ("AUSTRALIA", 6158, None),
    ("BRITISH COLUMBIA", 16737, None),
    ("NEWFOUNDLAND", 17766, None),
    ("CAPE OF GOOD HOPE", 20372, None),
    ("NATAL", 20427, None),
    ("BASUTOLAND", 22307, None),
    ("SWAZILAND", 22614, None),
    ("SOUTHERN RHODESIA", 22827, None),
    ("BAHAMAS", 23557, None),
    ("BARBADOS", 24115, None),
    ("BERMUDA", 24864, None),
    ("BRITISH GUIANA", 25093, None),
    ("BRITISH HONDURAS", 26057, None),
    ("CEYLON", 26404, None),
    ("FALKLAND ISLANDS", 28518, None),
    ("FIJI", 28799, None),
    ("THE GAMBIA", 29469, None),
    ("GIBRALTAR", 29942, None),
    ("HONG KONG", 31423, None),
    ("JAMAICA", 32067, None),
    ("CAYMAN ISLANDS", 32928, None),
    ("KENYA", 33434, None),
    ("ANTIGUA", 34262, None),
    ("DOMINICA", 34947, None),
    ("MONTSERRAT", 35311, None),
    ("MAURITIUS", 36472, None),
    ("NIGERIA", 37336, None),
    ("NORTHERN RHODESIA", 38441, None),
    ("PALESTINE", 39202, None),
    ("ST. HELENA", 39760, None),
    ("ASCENSION", 39965, None),
    ("SEYCHELLES", 39979, None),
    ("SIERRA LEONE", 40247, None),
    ("STRAITS SETTLEMENTS", 40951, None),
    ("TRINIDAD AND TOBAGO", 44180, "Includes TRINIDAD (44182) and TOBAGO (44482) subsections"),
    ("UGANDA", 45658, None),
    ("WEIHAIWEI", 46112, None),
    ("GRENADA", 46771, None),
    ("ST. LUCIA", 47055, None),
    ("ST. VINCENT", 47344, None),
    ("ZANZIBAR", 47631, None),
    ("IRAQ", 47912, None),
    ("NORTH BORNEO", 48112, None),
    ("TRANS-JORDAN", 48596, "RECOVERY: Was missing from previous extraction - League of Nations mandate territory"),
    ("ADEN", 48646, None),
    ("TRISTAN DA CUNHA", 48670, None),
    ("MISCELLANEOUS ISLANDS", 48686, None),
]

# Read source file
print("Reading source file...")
with open(source_file, 'r') as f:
    source_lines = f.readlines()

total_lines = len(source_lines)
print(f"Total lines in source: {total_lines}")

# Process each colony
extracted_colonies = []

for i, (name, start_line, note) in enumerate(colonies):
    # Determine end line (line before next colony, or end of file)
    if i < len(colonies) - 1:
        end_line = colonies[i + 1][1] - 1
    else:
        # Last colony ends at line 48694 (before PART III starts at 48695)
        end_line = 48694

    # Extract content (converting to 0-indexed)
    content_lines = source_lines[start_line-1:end_line]
    content = ''.join(content_lines)

    # Create filename
    filename = name.replace(' ', '_').replace('-', '_').replace('.', '') + '.txt'

    # Write file
    output_file = output_dir / filename
    with open(output_file, 'w') as f:
        f.write(content)

    # Add to metadata
    colony_entry = {
        "colony_name": name,
        "start_line": start_line,
        "end_line": end_line,
        "line_count": end_line - start_line + 1,
        "file": f"output_3/1927_manual_parsed/{filename}"
    }

    if note:
        colony_entry["note"] = note

    extracted_colonies.append(colony_entry)

    print(f"Extracted: {name} ({start_line}-{end_line}, {end_line - start_line + 1} lines)")

# Create metadata JSON
metadata = {
    "year": 1927,
    "source_file": "historical_document_pipeline/processed_pdfs/colonial-office-list-1927/olmocr_results.md",
    "extraction_date": datetime.now().strftime("%Y-%m-%d"),
    "extraction_method": "Manual LLM boundary identification",
    "total_colonies": len(extracted_colonies),
    "notes": [
        "All colony boundaries manually identified by reading OCR content",
        "TRINIDAD AND TOBAGO treated as single colony (per header '* TRINIDAD AND TOBAGO')",
        "TRANS-JORDAN recovered - was missing from previous extraction (output_2)",
        "Includes PART II-B (Dominions Office territories) and PART II-C (Colonial Office colonies)",
        "Extraction ends at line 48694; PART III (appendices) starts at 48695"
    ],
    "colonies": extracted_colonies
}

metadata_file = Path('output_3/1927_manual_parsed.json')
with open(metadata_file, 'w') as f:
    json.dump(metadata, f, indent=2)

print(f"\n{'='*80}")
print(f"EXTRACTION COMPLETE")
print(f"{'='*80}")
print(f"Total colonies extracted: {len(extracted_colonies)}")
print(f"Output directory: {output_dir}")
print(f"Metadata file: {metadata_file}")
print(f"\nNOTABLE FINDINGS:")
print(f"1. TRANS-JORDAN recovered at line 48596 - was MISSING from previous extraction!")
print(f"2. TRINIDAD AND TOBAGO properly merged (header at 44180)")
print(f"3. All 47 colonies/territories extracted with manual boundary verification")
