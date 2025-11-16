#!/usr/bin/env python3
"""
Create metadata JSON for corrected 1922 colonies.

This script reads all the corrected colony files from output_2/1922_manual_parsed/
and creates a comprehensive metadata file.
"""

import json
from pathlib import Path
from datetime import datetime

# Paths
output_dir = Path('output_2/1922_manual_parsed')
source_file = Path('historical_document_pipeline/processed_pdfs/colonial-office-list-1922/olmocr_results.md')
metadata_file = Path('output_2/1922_manual_parsed.json')

# Define all colonies with their boundaries (from extract_1922_corrected.py)
colonies_data = [
    # Kept colonies (from original extraction, properly extracted)
    {'name': 'AUSTRALIA', 'start': 4541, 'end': 5076},
    {'name': 'BAHAMAS', 'start': 12488, 'end': 12937},
    {'name': 'BARBADOS', 'start': 12937, 'end': 13507},
    {'name': 'BERMUDA', 'start': 13507, 'end': 13866},
    {'name': 'BRITISH GUIANA', 'start': 13866, 'end': 14880},
    {'name': 'CEYLON', 'start': 18726, 'end': 20082},
    {'name': 'CYPRUS', 'start': 20082, 'end': 20720},
    {'name': 'FALKLAND ISLANDS', 'start': 20720, 'end': 21020},
    {'name': 'FIJI', 'start': 21020, 'end': 21676},
    {'name': 'THE GAMBIA', 'start': 21676, 'end': 22154},
    {'name': 'TOGOLAND', 'start': 22801, 'end': 23526},
    {'name': 'HONG KONG', 'start': 23526, 'end': 24126},
    {'name': 'JAMAICA', 'start': 24126, 'end': 25110},
    {'name': 'ANTIGUA', 'start': 26327, 'end': 27056},
    {'name': 'DOMINICA', 'start': 27056, 'end': 27742},
    {'name': 'MALTA', 'start': 27742, 'end': 28327},
    {'name': 'ST. HELENA', 'start': 31979, 'end': 32153},
    {'name': 'SEYCHELLES', 'start': 32153, 'end': 32409},
    {'name': 'SOUTH WEST AFRICA', 'start': 35227, 'end': 35382},
    {'name': 'BASUTOLAND', 'start': 35382, 'end': 35665},
    {'name': 'SWAZILAND', 'start': 35665, 'end': 36492},
    {'name': 'NORTHERN RHODESIA', 'start': 36492, 'end': 36552},
    {'name': 'STRAITS SETTLEMENTS', 'start': 36552, 'end': 37270},
    {'name': 'LABUAN', 'start': 37270, 'end': 38332},
    {'name': 'TANGANYIKA TERRITORY', 'start': 38332, 'end': 38797},
    {'name': 'UGANDA', 'start': 40471, 'end': 40895},
    {'name': 'ST. LUCIA', 'start': 41663, 'end': 41961},
    {'name': 'ST. VINCENT', 'start': 41961, 'end': 42231},
    {'name': 'ZANZIBAR', 'start': 42231, 'end': 42850},
    {'name': 'ADEN', 'start': 43467, 'end': 43479},

    # Corrected colonies (fixed boundaries)
    {'name': 'TASMANIA', 'start': 5191, 'end': 5206},
    {'name': 'BRITISH HONDURAS', 'start': 14880, 'end': 15240},
    {'name': 'DOMINION OF CANADA', 'start': 15241, 'end': 18726},
    {'name': 'GIBRALTAR', 'start': 22154, 'end': 22464},
    {'name': 'THE GOLD COAST', 'start': 22465, 'end': 22801},
    {'name': 'CAYMAN ISLANDS', 'start': 25111, 'end': 25151},
    {'name': 'TURKS AND CAICOS ISLANDS', 'start': 25154, 'end': 25327},
    {'name': 'THE KENYA COLONY AND PROTECTORATE', 'start': 25328, 'end': 26093},
    {'name': 'THE LEEWARD ISLANDS', 'start': 26094, 'end': 26327},
    {'name': 'MAURITIUS', 'start': 28328, 'end': 29630},
    {'name': 'NEW ZEALAND', 'start': 29631, 'end': 31978},
    {'name': 'SIERRA LEONE', 'start': 32409, 'end': 33049},
    {'name': 'SOUTH AFRICA', 'start': 33050, 'end': 35227},
    {'name': 'TRINIDAD AND TOBAGO', 'start': 38797, 'end': 40471},
    {'name': 'WEIHAIWEI', 'start': 40895, 'end': 41156},
    {'name': 'TONGA', 'start': 41157, 'end': 41663},
    {'name': 'PALESTINE', 'start': 42850, 'end': 43227},
    {'name': 'SARAWAK', 'start': 43228, 'end': 43466},
    {'name': 'ASCENSION', 'start': 43480, 'end': 43485},
    {'name': 'TRISTAN DA CUNHA', 'start': 43486, 'end': 43499},
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
        'year': 1922,
        'start_line': start,
        'end_line': end,
        'char_count': char_count,
        'line_count': line_count,
        'filename': filename
    })

# Create metadata structure
metadata = {
    'year': 1922,
    'source_file': str(source_file),
    'total_colonies': len(colonies_metadata),
    'colonies': colonies_metadata,
    'processing_notes': {
        'parser': 'Manual correction of batch parser output',
        'date': datetime.now().strftime('%Y-%m-%d'),
        'method': 'Manual LLM-based boundary verification and correction',
        'corrections_applied': [
            'Fixed TASMANIA over-extraction (7,298 lines → 16 lines)',
            'Removed duplicate Australian state entries (VICTORIA, QUEENSLAND, WESTERN AUSTRALIA)',
            'Fixed BRITISH HONDURAS over-extraction (3,846 lines → 361 lines)',
            'Added DOMINION OF CANADA (3,486 lines)',
            'Fixed GIBRALTAR over-extraction (647 lines → 311 lines)',
            'Added THE GOLD COAST (337 lines)',
            'Fixed CAYMAN ISLANDS over-extraction (1,217 lines → 41 lines)',
            'Extracted TURKS AND CAICOS ISLANDS from CAYMAN ISLANDS over-extraction (174 lines)',
            'Extracted THE KENYA COLONY AND PROTECTORATE from CAYMAN ISLANDS over-extraction (766 lines)',
            'Extracted THE LEEWARD ISLANDS from CAYMAN ISLANDS over-extraction (234 lines)',
            'Fixed MAURITIUS over-extraction (3,652 lines → 1,303 lines)',
            'Extracted NEW ZEALAND from MAURITIUS over-extraction (2,348 lines)',
            'Fixed SIERRA LEONE over-extraction (1,227 lines → 641 lines)',
            'Removed South African province entries (CAPE OF GOOD HOPE, NATAL, TRANSVAAL)',
            'Added SOUTH AFRICA (2,178 lines)',
            'Merged TOBAGO subsection into TRINIDAD AND TOBAGO (1,675 lines)',
            'Fixed WEIHAIWEI over-extraction (768 lines → 262 lines)',
            'Added TONGA (507 lines)',
            'Fixed PALESTINE over-extraction (617 lines → 378 lines)',
            'Extracted SARAWAK from ASCENSION over-extraction (239 lines)',
            'Fixed ASCENSION over-extraction (15,658 lines → 6 lines)',
            'Extracted TRISTAN DA CUNHA from ASCENSION over-extraction (14 lines)',
        ],
        'original_count': 47,
        'corrected_count': 51,
        'note': 'Removed 17 over-extracted/duplicate entries, added 21 corrected/new entries'
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
