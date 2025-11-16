#!/usr/bin/env python3
"""
Create metadata JSON for corrected 1956 colonies.
"""

import json
from pathlib import Path
from datetime import datetime

# Paths
output_dir = Path('output_2/1956_manual_parsed')
source_file = Path('historical_document_pipeline/processed_pdfs/colonial-office-list-1956/olmocr_results.md')
metadata_file = Path('output_2/1956_manual_parsed.json')

# Read source to calculate stats
with open(source_file, 'r') as f:
    source_lines = f.readlines()

# Get all .md files in the output directory
colony_files = sorted(output_dir.glob('*.md'))

colonies_metadata = []
for colony_file in colony_files:
    # Extract colony name from filename
    name = colony_file.stem.replace('_', ' ')

    # Read the file to get content
    with open(colony_file, 'r') as f:
        content = f.read()

    # Count lines and chars
    lines = content.split('\n')
    line_count = len(lines)
    char_count = len(content)

    # Try to determine start/end lines by searching source
    # This is approximate - we look for the first line of content
    start_line = 0
    end_line = 0
    if lines and lines[0]:
        search_text = lines[0][:50]  # First 50 chars
        for i, source_line in enumerate(source_lines):
            if search_text in source_line:
                start_line = i + 1
                end_line = start_line + line_count - 1
                break

    colonies_metadata.append({
        'colony_name': name,
        'year': 1956,
        'start_line': start_line,
        'end_line': end_line,
        'char_count': char_count,
        'line_count': line_count,
        'filename': colony_file.name
    })

# Sort by start line
colonies_metadata.sort(key=lambda x: x['start_line'])

# Create metadata structure
metadata = {
    'year': 1956,
    'source_file': str(source_file),
    'total_colonies': len(colonies_metadata),
    'colonies': colonies_metadata,
    'processing_notes': {
        'parser': 'Manual correction of v5 parser output',
        'date': datetime.now().strftime('%Y-%m-%d'),
        'method': 'Manual LLM-based boundary verification and correction',
        'corrections_applied': [
            'Removed 20 table of contents entries (lines 2976-3606)',
            'Fixed MONTSERRAT over-extraction (1391 lines → 280 lines)',
            'Added BRITISH VIRGIN ISLANDS (126 lines)',
            'Added FEDERATION OF MALAYA (1332 lines)',
            'Added FEDERATION OF NIGERIA (615 lines)',
            'Added NORTHERN RHODESIA (36 lines)',
            'Added FEDERATION OF RHODESIA AND NYASALAND (461 lines)',
            'Added NYASALAND PROTECTORATE (346 lines)',
            'Added SARAWAK (284 lines)',
            'Added SINGAPORE (457 lines)',
            'Added SOMALILAND PROTECTORATE (685 lines)',
            'Added KINGDOM OF TONGA (143 lines)',
            'Added TRINIDAD AND TOBAGO (356 lines)',
            'Added BRITISH SOLOMON ISLANDS PROTECTORATE (182 lines)',
            'Added GILBERT AND ELLICE ISLANDS COLONY (166 lines)',
            'Added NEW HEBRIDES CONDOMINIUM (125 lines)',
            'Added GRENADA (272 lines)',
        ],
        'original_count': 46,
        'corrected_count': 41,
        'note': 'Removed table of contents entries, fixed over-extraction, added missing colonies'
    }
}

# Write metadata file
with open(metadata_file, 'w') as f:
    json.dump(metadata, f, indent=2)

print(f"Created metadata file: {metadata_file}")
print(f"Total colonies: {len(colonies_metadata)}")
print(f"\nColonies list:")
for i, colony in enumerate(colonies_metadata, 1):
    print(f"{i:2d}. {colony['colony_name']:50s} (lines {colony['start_line']:5d}-{colony['end_line']:5d}, {colony['line_count']:5d} lines)")
