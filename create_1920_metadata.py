#!/usr/bin/env python3
"""
Create metadata JSON for corrected 1920 colonies.

This script reads all the corrected colony files from output_2/1920_manual_parsed/
and creates a comprehensive metadata file.
"""

import json
from pathlib import Path
from datetime import datetime

# Paths
output_dir = Path('output_2/1920_manual_parsed')
source_file = Path('historical_document_pipeline/processed_pdfs/colonial-office-list-1920/olmocr_results.md')
metadata_file = Path('output_2/1920_manual_parsed.json')

# Define all colonies with their boundaries (from extract_1920_corrected.py)
colonies_data = [
    # Kept colonies (from original extraction, properly extracted)
    {'name': 'AUSTRALIA', 'start': 4000, 'end': 4605},
    {'name': 'BAHAMAS', 'start': 11561, 'end': 11942},
    {'name': 'BARBADOS', 'start': 11942, 'end': 12599},
    {'name': 'BERMUDA', 'start': 12599, 'end': 12989},
    {'name': 'BRITISH GUIANA', 'start': 12989, 'end': 13750},
    {'name': 'CEYLON', 'start': 17473, 'end': 18418},
    {'name': 'CYPRUS', 'start': 18418, 'end': 19247},
    {'name': 'EAST AFRICA PROTECTORATE', 'start': 19247, 'end': 19926},
    {'name': 'FALKLAND ISLANDS', 'start': 19926, 'end': 20223},
    {'name': 'FIJI', 'start': 20223, 'end': 20857},
    {'name': 'THE GAMBIA', 'start': 20857, 'end': 21384},
    {'name': 'GIBRALTAR', 'start': 21384, 'end': 21905},
    {'name': 'TOGOLAND', 'start': 21905, 'end': 23209},
    {'name': 'JAMAICA', 'start': 23209, 'end': 23964},
    {'name': 'ANTIGUA', 'start': 24211, 'end': 25054},
    {'name': 'DOMINICA', 'start': 25054, 'end': 25333},
    {'name': 'MONTSERRAT', 'start': 25333, 'end': 25677},
    {'name': 'MALTA', 'start': 25677, 'end': 26241},
    {'name': 'MAURITIUS', 'start': 26241, 'end': 27208},
    {'name': 'NIGERIA', 'start': 28780, 'end': 30049},
    {'name': 'ST. HELENA', 'start': 30049, 'end': 30222},
    {'name': 'SEYCHELLES', 'start': 30222, 'end': 30549},
    {'name': 'BASUTOLAND', 'start': 33610, 'end': 33911},
    {'name': 'SWAZILAND', 'start': 33911, 'end': 34613},
    {'name': 'SOUTH WEST AFRICA', 'start': 34613, 'end': 34634},
    {'name': 'STRAITS SETTLEMENTS', 'start': 34634, 'end': 35229},
    {'name': 'TANGANYIKA TERRITORY', 'start': 36381, 'end': 36654},
    {'name': 'TURKS AND CAICOS ISLANDS', 'start': 37867, 'end': 37998},
    {'name': 'UGANDA', 'start': 37998, 'end': 38370},
    {'name': 'WEIHAIWEI', 'start': 38370, 'end': 38843},
    {'name': 'GRENADA', 'start': 38843, 'end': 39152},
    {'name': 'ST. LUCIA', 'start': 39152, 'end': 39545},
    {'name': 'ST. VINCENT', 'start': 39545, 'end': 39802},
    {'name': 'ZANZIBAR', 'start': 39802, 'end': 40039},
    {'name': 'NORTH BORNEO', 'start': 40039, 'end': 40504},
    {'name': 'ADEN', 'start': 40504, 'end': 40514},

    # Corrected colonies (fixed boundaries)
    {'name': 'BRITISH HONDURAS', 'start': 13750, 'end': 14067},
    {'name': 'DOMINION OF CANADA', 'start': 14067, 'end': 17473},
    {'name': 'CAYMAN ISLANDS', 'start': 23964, 'end': 24211},
    {'name': 'NEWFOUNDLAND', 'start': 27209, 'end': 27642},
    {'name': 'NEW ZEALAND', 'start': 27642, 'end': 28780},
    {'name': 'SIERRA LEONE', 'start': 30550, 'end': 31060},
    {'name': 'SOMALILAND PROTECTORATE', 'start': 31104, 'end': 31259},
    {'name': 'SOUTH AFRICA', 'start': 31259, 'end': 33610},
    {'name': 'LABUAN', 'start': 35229, 'end': 36381},
    {'name': 'TRINIDAD AND TOBAGO', 'start': 36654, 'end': 37867},
    {'name': 'ASCENSION', 'start': 40514, 'end': 40535},
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
        'year': 1920,
        'start_line': start,
        'end_line': end,
        'char_count': char_count,
        'line_count': line_count,
        'filename': filename
    })

# Create metadata structure
metadata = {
    'year': 1920,
    'source_file': str(source_file),
    'total_colonies': len(colonies_metadata),
    'colonies': colonies_metadata,
    'processing_notes': {
        'parser': 'Manual correction of batch parser output',
        'date': datetime.now().strftime('%Y-%m-%d'),
        'method': 'Manual LLM-based boundary verification and correction',
        'corrections_applied': [
            'Removed duplicate Australian state entries (VICTORIA, QUEENSLAND, WESTERN AUSTRALIA, TASMANIA)',
            'Fixed BRITISH HONDURAS over-extraction (2,896 lines → 318 lines)',
            'Merged BRITISH COLUMBIA into DOMINION OF CANADA',
            'Fixed CAYMAN ISLANDS boundary (verified 247 lines)',
            'Fixed NEWFOUNDLAND over-extraction (1,572 lines → 434 lines)',
            'Extracted NEW ZEALAND from NEWFOUNDLAND over-extraction',
            'Fixed SIERRA LEONE over-extraction (3,061 lines → 511 lines)',
            'Extracted SOMALILAND PROTECTORATE from SIERRA LEONE over-extraction',
            'Extracted SOUTH AFRICA from SIERRA LEONE over-extraction',
            'Verified LABUAN boundary (1,152 lines)',
            'Merged TRINIDAD and TOBAGO into TRINIDAD AND TOBAGO',
            'Fixed ASCENSION over-extraction (19,513 lines → 22 lines)'
        ],
        'original_count': 49,
        'corrected_count': 47,
        'note': 'Reduced from 49 to 47 colonies: removed 12 over-extracted/duplicate entries, added 10 corrected entries'
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
