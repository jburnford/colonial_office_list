#!/usr/bin/env python3
"""
Extract corrected 1950 colonies based on manual boundary verification.

Year 1950: Found 34 colonies (missing FALKLAND ISLANDS, WESTERN PACIFIC, and MISCELLANEOUS ISLANDS
which appear to be formatted differently or located elsewhere in the document).

This script extracts the 34 identified colonies with correct boundaries.
"""

import json
from pathlib import Path

# Load boundaries
with open('1950_boundaries_v2.json', 'r') as f:
    boundaries = json.load(f)

# Output directory
output_dir = Path('output_2/1950_manual_parsed')
output_dir.mkdir(parents=True, exist_ok=True)

# OCR source file
source_file = Path('historical_document_pipeline/processed_pdfs/colonial-office-list-1950/olmocr_results.md')

# Read source file
with open(source_file, 'r') as f:
    source_lines = f.readlines()

# Extract each colony
for colony in boundaries:
    name = colony['name']
    start = colony['start']
    end = colony['end']

    # Extract content (1-indexed in JSON, 0-indexed in Python)
    content_lines = source_lines[start-1:end]
    content = ''.join(content_lines)

    # Create filename (clean up name)
    filename = name.replace(' ', '_').replace(',', '').replace('(', '').replace(')', '').replace("'", '').replace('.', '').replace('**', '') + '.md'

    # Write file
    output_file = output_dir / filename
    with open(output_file, 'w') as f:
        f.write(content)

    print(f"Extracted: {filename:50s} ({end - start + 1:5d} lines)")

print(f"\n=== SUMMARY ===")
print(f"Total colonies extracted: {len(boundaries)}")
print(f"Output directory: {output_dir}")
