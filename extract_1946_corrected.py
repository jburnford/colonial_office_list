#!/usr/bin/env python3
"""
Extract corrected 1946 colonies after manual boundary verification.
"""

import json
from pathlib import Path

# Load corrected metadata
with open('/home/user/colonial_office_list/output_2/1946_manual_parsed.json', 'r') as f:
    metadata = json.load(f)

# Output directory
output_dir = Path('output_2/1946_manual_parsed')
output_dir.mkdir(parents=True, exist_ok=True)

# OCR source file
source_file = Path('historical_document_pipeline/processed_pdfs/colonial-office-list-1946/olmocr_results.md')

# Read source file
with open(source_file, 'r') as f:
    source_lines = f.readlines()

# Extract each colony
for colony in metadata['colonies']:
    name = colony['name']
    filename = colony['filename']
    start = colony['start_line']
    end = colony['end_line']

    # Extract content
    content_lines = source_lines[start-1:end]
    content = ''.join(content_lines)

    # Write file
    output_file = output_dir / filename
    with open(output_file, 'w') as f:
        f.write(content)

    print(f"✓ {name}: {start}-{end} ({end-start+1} lines) → {filename}")

print()
print("=" * 80)
print("YEAR 1946 EXTRACTION COMPLETE")
print("=" * 80)
print(f"Total colonies: {metadata['total_colonies']}")
print(f"Output directory: {output_dir}")
print()
print("✅ Year 1946 corrected and extracted")
print("✅ Merged over-extracted subsections")
print("✅ Removed non-colony entries")
