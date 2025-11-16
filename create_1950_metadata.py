#!/usr/bin/env python3
"""
Create metadata JSON for corrected 1950 colonies.

This script reads all the corrected colony files from output_2/1950_manual_parsed/
and creates a comprehensive metadata file.
"""

import json
from pathlib import Path
from datetime import datetime

# Paths
output_dir = Path('output_2/1950_manual_parsed')
source_file = Path('historical_document_pipeline/processed_pdfs/colonial-office-list-1950/olmocr_results.md')
metadata_file = Path('output_2/1950_manual_parsed.json')

# Load boundaries data
with open('1950_boundaries_v2.json', 'r') as f:
    boundaries = json.load(f)

# Read source to calculate stats
with open(source_file, 'r') as f:
    source_lines = f.readlines()

# Build metadata for each colony
colonies_metadata = []
for colony in boundaries:
    name = colony['name']
    start = colony['start']
    end = colony['end']

    # Calculate stats
    content_lines = source_lines[start-1:end]
    content = ''.join(content_lines)
    char_count = len(content)
    line_count = end - start + 1

    # Create filename
    filename = name.replace(' ', '_').replace(',', '').replace('(', '').replace(')', '').replace("'", '').replace('.', '').replace('**', '') + '.md'

    colonies_metadata.append({
        'colony_name': name,
        'year': 1950,
        'start_line': start,
        'end_line': end,
        'char_count': char_count,
        'line_count': line_count,
        'filename': filename
    })

# Create metadata structure
metadata = {
    'year': 1950,
    'source_file': str(source_file),
    'total_colonies': len(colonies_metadata),
    'colonies': colonies_metadata,
    'processing_notes': {
        'parser': 'Manual LLM-based boundary identification',
        'date': datetime.now().strftime('%Y-%m-%d'),
        'method': 'Automated pattern matching with manual verification',
        'notes': [
            'Identified 34 colonies using OCR pattern matching',
            'Three colonies from table of contents not found: FALKLAND ISLANDS AND DEPENDENCIES, WESTERN PACIFIC, MISCELLANEOUS ISLANDS',
            'These may be formatted differently or located in a different section of the document',
            'All identified colonies have verified boundaries based on content structure',
            'Colony sections identified by all-caps headers followed by "Situation", "Area", "Climate", etc.',
        ]
    }
}

# Write metadata file
with open(metadata_file, 'w') as f:
    json.dump(metadata, f, indent=2)

print(f"Created metadata file: {metadata_file}")
print(f"Total colonies: {len(colonies_metadata)}")
print(f"\nColonies list:")
for i, colony in enumerate(colonies_metadata, 1):
    print(f"{i:2d}. {colony['colony_name']:45s} (lines {colony['start_line']:5d}-{colony['end_line']:5d}, {colony['line_count']:5d} lines)")
