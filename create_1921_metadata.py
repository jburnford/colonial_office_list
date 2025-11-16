#!/usr/bin/env python3
"""
Create metadata JSON for corrected 1921 colonies.

This script reads all the corrected colony files from output_2/1921_manual_parsed/
and creates a comprehensive metadata file.
"""

import json
from pathlib import Path
from datetime import datetime

# Paths
output_dir = Path('output_2/1921_manual_parsed')
source_file = Path('historical_document_pipeline/processed_pdfs/colonial-office-list-1921/olmocr_results.md')
metadata_file = Path('output_2/1921_manual_parsed.json')

# Define all colonies with their boundaries (from extract_1921_corrected.py)
colonies_data = [
    # Kept colonies (from original extraction, properly extracted)
    {'name': 'AUSTRALIA', 'start': 4213, 'end': 6635},
    {'name': 'BAHAMAS', 'start': 12207, 'end': 12617},
    {'name': 'BARBADOS', 'start': 12617, 'end': 13316},
    {'name': 'BERMUDA', 'start': 13316, 'end': 13727},
    {'name': 'BRITISH GUIANA', 'start': 13727, 'end': 14599},
    {'name': 'CEYLON', 'start': 18721, 'end': 19870},
    {'name': 'CYPRUS', 'start': 19870, 'end': 20548},
    {'name': 'FALKLAND ISLANDS', 'start': 20548, 'end': 20804},
    {'name': 'FIJI', 'start': 20804, 'end': 21520},
    {'name': 'THE GAMBIA', 'start': 21520, 'end': 21943},
    {'name': 'GIBRALTAR', 'start': 21943, 'end': 22492},
    {'name': 'TOGOLAND', 'start': 22492, 'end': 23666},
    {'name': 'JAMAICA', 'start': 23666, 'end': 24592},
    {'name': 'ANTIGUA', 'start': 25614, 'end': 26344},
    {'name': 'DOMINICA', 'start': 26344, 'end': 26595},
    {'name': 'MONTSERRAT', 'start': 26595, 'end': 26956},
    {'name': 'MALTA', 'start': 26956, 'end': 27477},
    {'name': 'MAURITIUS', 'start': 27477, 'end': 28229},
    {'name': 'NEWFOUNDLAND', 'start': 28229, 'end': 29964},
    {'name': 'NIGERIA', 'start': 29964, 'end': 30967},
    {'name': 'ST. HELENA', 'start': 30967, 'end': 31150},
    {'name': 'SEYCHELLES', 'start': 31150, 'end': 31454},
    {'name': 'SIERRA LEONE', 'start': 31454, 'end': 32715},
    {'name': 'CAPE OF GOOD HOPE', 'start': 32715, 'end': 32776},
    {'name': 'NATAL', 'start': 32776, 'end': 32796},
    {'name': 'TRANSVAAL', 'start': 32796, 'end': 34353},
    {'name': 'BASUTOLAND', 'start': 34353, 'end': 34612},
    {'name': 'SWAZILAND', 'start': 34612, 'end': 35299},
    {'name': 'STRAITS SETTLEMENTS', 'start': 35299, 'end': 35877},
    {'name': 'LABUAN', 'start': 35877, 'end': 37020},
    {'name': 'TANGANYIKA TERRITORY', 'start': 37020, 'end': 37327},
    {'name': 'TRINIDAD', 'start': 37327, 'end': 37504},
    {'name': 'UGANDA', 'start': 38943, 'end': 39318},
    {'name': 'WEIHAIWEI', 'start': 39318, 'end': 40137},
    {'name': 'ST. LUCIA', 'start': 40137, 'end': 40576},
    {'name': 'ST. VINCENT', 'start': 40576, 'end': 40892},
    {'name': 'ZANZIBAR', 'start': 40892, 'end': 41449},
    {'name': 'PALESTINE', 'start': 41449, 'end': 42159},
    {'name': 'ADEN', 'start': 42159, 'end': 42235},

    # Corrected colonies (fixed boundaries)
    {'name': 'BRITISH HONDURAS', 'start': 14599, 'end': 15046},
    {'name': 'DOMINION OF CANADA', 'start': 15047, 'end': 18721},
    {'name': 'CAYMAN ISLANDS', 'start': 24593, 'end': 24630},
    {'name': 'THE KENYA COLONY AND PROTECTORATE', 'start': 24631, 'end': 25399},
    {'name': 'THE LEEWARD ISLANDS', 'start': 25400, 'end': 25614},
    {'name': 'TRINIDAD AND TOBAGO', 'start': 37327, 'end': 38943},
    {'name': 'ASCENSION', 'start': 42236, 'end': 42252},
    {'name': 'TRISTAN DA CUNHA', 'start': 42253, 'end': 42262},
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
        'year': 1921,
        'start_line': start,
        'end_line': end,
        'char_count': char_count,
        'line_count': line_count,
        'filename': filename
    })

# Create metadata structure
metadata = {
    'year': 1921,
    'source_file': str(source_file),
    'total_colonies': len(colonies_metadata),
    'colonies': colonies_metadata,
    'processing_notes': {
        'parser': 'Manual correction of batch parser output',
        'date': datetime.now().strftime('%Y-%m-%d'),
        'method': 'Manual LLM-based boundary verification and correction',
        'corrections_applied': [
            'Removed duplicate Australian state entries (QUEENSLAND, TASMANIA, VICTORIA, WESTERN AUSTRALIA)',
            'Fixed BRITISH HONDURAS over-extraction (3,285 lines → 448 lines)',
            'Merged BRITISH COLUMBIA into DOMINION OF CANADA',
            'Fixed CAYMAN ISLANDS over-extraction (1,022 lines → 38 lines)',
            'Extracted THE KENYA COLONY AND PROTECTORATE from CAYMAN ISLANDS over-extraction',
            'Extracted THE LEEWARD ISLANDS from CAYMAN ISLANDS over-extraction',
            'Merged TOBAGO subsection into TRINIDAD AND TOBAGO',
            'Fixed ASCENSION over-extraction (20,698 lines → 17 lines)',
            'Extracted TRISTAN DA CUNHA from ASCENSION over-extraction'
        ],
        'original_count': 48,
        'corrected_count': 47,
        'note': 'Count changed from 48 to 47: removed 10 over-extracted/duplicate entries, added 9 corrected entries'
    }
}

# Write metadata file
with open(metadata_file, 'w') as f:
    json.dump(metadata, f, indent=2)

print(f"Created metadata file: {metadata_file}")
print(f"Total colonies: {len(colonies_metadata)}")
print(f"\nColonies list:")
for i, colony in enumerate(colonies_metadata, 1):
    print(f"{i:2d}. {colony['colony_name']:40s} (lines {colony['start_line']:5d}-{colony['end_line']:5d}, {colony['line_count']:5d} lines)")
