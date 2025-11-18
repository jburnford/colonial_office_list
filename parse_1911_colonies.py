#!/usr/bin/env python3
"""
Script to parse Colonial Office List 1911 and extract individual colonies
"""

import json
import re
import os

# Read the full document
print("Reading document...")
with open('/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1911/olmocr_results.md', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Total lines: {len(lines)}")

# Define colony boundaries
colony_start = 9866  # Papua starts here
colony_end = 37511   # PART III starts here

# List of expected colony names (without trailing period)
expected_colonies = [
    'Papua', 'BAHAMAS', 'BARBADOS', 'BERMUDA', 'BRITISH GUIANA',
    'BRITISH HONDURAS', 'CEYLON', 'CYPRUS', 'EAST AFRICA PROTECTORATE',
    'FALKLAND ISLANDS', 'FIJI', 'GIBRALTAR', 'THE GOLD COAST', 'HONG KONG',
    'JAMAICA', 'THE LEEWARD ISLANDS', 'MALTA', 'MAURITIUS', 'NEWFOUNDLAND',
    'NORTHERN NIGERIA', 'NYASALAND PROTECTORATE', 'ST. HELENA',
    'SEYCHELLES', 'SIERRA LEONE', 'SOMALILAND PROTECTORATE',
    'BASUTOLAND', 'BECHUANALAND PROTECTORATE', 'SWAZILAND',
    'SOUTHERN RHODESIA ADMINISTRATION', 'SOUTHERN NIGERIA',
    'STRAITS SETTLEMENTS', 'TRINIDAD',
    'TURKS AND CAICOS ISLANDS', 'UGANDA', 'WEIHAIWEI',
    'COOK ISLANDS', 'GRENA DA', 'GRENADA', 'ST. LUCIA', 'ST. VINCENT',
    'ZANZIBAR'
]

# Find first occurrence of each colony
found_colonies = {}
colony_headings = []

for i in range(colony_start - 1, colony_end):
    line = lines[i].strip()
    clean_line = re.sub(r'^\s*\d+→', '', line).strip()

    # Check if this is a colony heading
    colony_name = clean_line.rstrip('.')

    if colony_name in expected_colonies and colony_name not in found_colonies:
        found_colonies[colony_name] = True
        colony_headings.append({
            'name': colony_name,
            'line_num': i + 1,
            'line_index': i
        })
        print(f"Found: {colony_name} at line {i + 1}")

# Sort by line number
colony_headings.sort(key=lambda x: x['line_num'])

print(f"\nFound {len(colony_headings)} unique colonies")
print("\nAll colonies in order:")
for i, h in enumerate(colony_headings):
    print(f"{i+1}. {h['name']} (line {h['line_num']})")

# Determine end line for each colony (start of next colony or end of colonies section)
colonies = []
for i, heading in enumerate(colony_headings):
    start_line = heading['line_index']
    if i < len(colony_headings) - 1:
        end_line = colony_headings[i + 1]['line_index']
    else:
        end_line = colony_end - 1

    colonies.append({
        'name': heading['name'],
        'start_line': heading['line_num'],
        'end_line': end_line + 1,  # +1 for 1-indexed
        'start_index': start_line,
        'end_index': end_line
    })

# Create output directory
output_dir = '/home/user/colonial_office_list/output_3/1911_manual_parsed'
os.makedirs(output_dir, exist_ok=True)

# Extract each colony to a separate file
print(f"\nExtracting colonies to {output_dir}...")
for colony in colonies:
    # Create safe filename
    filename = colony['name'].lower().replace(' ', '_').replace('.', '') + '.txt'
    filename = filename.replace('the_', '')  # Remove 'the_' prefix
    filepath = os.path.join(output_dir, filename)

    # Extract lines for this colony
    colony_lines = lines[colony['start_index']:colony['end_index']]

    # Write to file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(colony_lines)

    num_lines = len(colony_lines)
    print(f"  {colony['name']}: {num_lines} lines -> {filename}")

# Create JSON metadata file
metadata = {
    'source_file': 'historical_document_pipeline/processed_pdfs/colonial-office-list-1911/olmocr_results.md',
    'year': 1911,
    'total_colonies': len(colonies),
    'extraction_date': '2025-11-18',
    'colonies': [
        {
            'name': c['name'],
            'start_line': c['start_line'],
            'end_line': c['end_line'],
            'total_lines': c['end_index'] - c['start_index']
        }
        for c in colonies
    ]
}

json_path = '/home/user/colonial_office_list/output_3/1911_manual_parsed.json'
with open(json_path, 'w', encoding='utf-8') as f:
    json.dump(metadata, f, indent=2)

print(f"\nMetadata saved to {json_path}")
print(f"\nTotal colonies extracted: {len(colonies)}")
print(f"\nComparison with 1910: 1910 had 45 colonies, 1911 has {len(colonies)} colonies")
print(f"Difference: {len(colonies) - 45} ({'+' if len(colonies) - 45 > 0 else ''}{len(colonies) - 45})")
