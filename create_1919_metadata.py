#!/usr/bin/env python3
"""
Create metadata JSON for corrected 1919 colonies.

This script reads all the corrected colony files from output_2/1919_manual_parsed/
and creates a comprehensive metadata file.
"""

import json
from pathlib import Path
from datetime import datetime

# Paths
output_dir = Path('output_2/1919_manual_parsed')
source_file = Path('historical_document_pipeline/processed_pdfs/colonial-office-list-1919/olmocr_results.md')
metadata_file = Path('output_2/1919_manual_parsed.json')

# Define all colonies with their boundaries (from extract_1919_corrected.py)
colonies_data = [
    # Kept colonies (from original extraction, properly extracted)
    {'name': 'AUSTRALIA', 'start': 3702, 'end': 4232},
    {'name': 'BAHAMAS', 'start': 11606, 'end': 12011},
    {'name': 'BARBADOS', 'start': 12011, 'end': 12613},
    {'name': 'BERMUDA', 'start': 12613, 'end': 13127},
    {'name': 'BRITISH GUIANA', 'start': 13127, 'end': 13935},
    {'name': 'BRITISH HONDURAS', 'start': 13935, 'end': 14292},
    {'name': 'CEYLON', 'start': 17532, 'end': 18609},
    {'name': 'CYPRUS', 'start': 18609, 'end': 19427},
    {'name': 'EAST AFRICA PROTECTORATE', 'start': 19427, 'end': 19966},
    {'name': 'FALKLAND ISLANDS', 'start': 19966, 'end': 20287},
    {'name': 'FIJI', 'start': 20287, 'end': 21523},
    {'name': 'GIBRALTAR', 'start': 21523, 'end': 22614},
    {'name': 'HONG KONG', 'start': 22614, 'end': 23216},
    {'name': 'JAMAICA', 'start': 23216, 'end': 24146},
    {'name': 'ANTIGUA', 'start': 24388, 'end': 25104},
    {'name': 'DOMINICA', 'start': 25104, 'end': 25439},
    {'name': 'MONTSERRAT', 'start': 25439, 'end': 25798},
    {'name': 'MALTA', 'start': 25798, 'end': 26392},
    {'name': 'MAURITIUS', 'start': 26392, 'end': 27297},
    {'name': 'NIGERIA', 'start': 28632, 'end': 29991},
    {'name': 'ST. HELENA', 'start': 29991, 'end': 30463},
    {'name': 'BASUTOLAND', 'start': 33406, 'end': 33643},
    {'name': 'SWAZILAND', 'start': 33643, 'end': 34288},
    {'name': 'NORTHERN RHODESIA', 'start': 34288, 'end': 34971},
    {'name': 'UGANDA', 'start': 38095, 'end': 38495},
    {'name': 'WEIHAIWEI', 'start': 38495, 'end': 39202},
    {'name': 'ST. LUCIA', 'start': 39202, 'end': 39540},
    {'name': 'ST. VINCENT', 'start': 39540, 'end': 39857},
    {'name': 'ZANZIBAR', 'start': 39857, 'end': 40097},
    {'name': 'NORTH BORNEO', 'start': 40097, 'end': 40536},
    {'name': 'ADEN', 'start': 40536, 'end': 40546},

    # Corrected colonies (fixed boundaries)
    {'name': 'TASMANIA', 'start': 4292, 'end': 4298},
    {'name': 'DOMINION OF CANADA', 'start': 14292, 'end': 17532},
    {'name': 'CAYMAN ISLANDS', 'start': 24147, 'end': 24184},
    {'name': 'NEWFOUNDLAND', 'start': 27298, 'end': 27672},
    {'name': 'NEW ZEALAND', 'start': 27673, 'end': 28632},
    {'name': 'SIERRA LEONE', 'start': 30464, 'end': 30947},
    {'name': 'SOMALILAND PROTECTORATE', 'start': 30948, 'end': 31097},
    {'name': 'SOUTH AFRICA', 'start': 31098, 'end': 33406},
    {'name': 'LABUAN', 'start': 34972, 'end': 36123},
    {'name': 'TRINIDAD AND TOBAGO', 'start': 36124, 'end': 38095},
    {'name': 'ASCENSION', 'start': 40547, 'end': 40550},
]

# Read source to calculate stats
with open(source_file, 'r') as f:
    source_lines = f.readlines()

# Build metadata for each colony
colonies_metadata = []
for colony in sorted(colonies_data, key=lambda x: x['start']):
    name = colony['name']
    start = colony['start']
    end = colony['end']

    # Calculate stats
    content_lines = source_lines[start-1:end]
    content = ''.join(content_lines)
    char_count = len(content)
    line_count = end - start + 1

    # Create filename
    filename = name.replace(' ', '_').replace(',', '').replace('(', '').replace(')', '').replace("'", '').replace('.', '') + '.md'

    colonies_metadata.append({
        'colony_name': name,
        'year': 1919,
        'start_line': start,
        'end_line': end,
        'char_count': char_count,
        'line_count': line_count,
        'filename': filename
    })

# Create metadata structure
metadata = {
    'year': 1919,
    'source_file': str(source_file),
    'total_colonies': len(colonies_metadata),
    'colonies': colonies_metadata,
    'processing_notes': {
        'parser': 'Manual correction of batch parser output',
        'date': datetime.now().strftime('%Y-%m-%d'),
        'method': 'Manual LLM-based boundary verification and correction',
        'corrections_applied': [
            'Fixed TASMANIA over-extraction (7,315 lines → 7 lines)',
            'Merged BRITISH COLUMBIA into DOMINION OF CANADA',
            'Fixed CAYMAN ISLANDS over-extraction (242 lines → 38 lines)',
            'Fixed NEWFOUNDLAND over-extraction (1,335 lines → 375 lines)',
            'Extracted NEW ZEALAND from NEWFOUNDLAND over-extraction',
            'Fixed SIERRA LEONE over-extraction (2,943 lines → 484 lines)',
            'Extracted SOMALILAND PROTECTORATE from SIERRA LEONE over-extraction',
            'Extracted SOUTH AFRICA from SIERRA LEONE over-extraction',
            'Fixed LABUAN over-extraction (1,344 lines → 1,152 lines)',
            'Merged TOBAGO subsection into TRINIDAD AND TOBAGO',
            'Fixed ASCENSION over-extraction (18,189 lines → 4 lines)',
            'Removed duplicate Australian state entries (VICTORIA, QUEENSLAND, WESTERN AUSTRALIA)'
        ],
        'original_count': 42,
        'corrected_count': 42,
        'note': 'Count remains 42, but composition changed: removed 11 over-extracted/duplicate entries, added 11 corrected entries'
    }
}

# Write metadata file
with open(metadata_file, 'w') as f:
    json.dump(metadata, f, indent=2)

print(f"Created metadata file: {metadata_file}")
print(f"Total colonies: {len(colonies_metadata)}")
print(f"\nColonies list:")
for i, colony in enumerate(colonies_metadata, 1):
    print(f"{i:2d}. {colony['colony_name']:30s} (lines {colony['start_line']:5d}-{colony['end_line']:5d}, {colony['line_count']:5d} lines)")
