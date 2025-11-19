#!/usr/bin/env python3
"""
Extract all colonies from the 1949 Colonial Office List using manually verified boundaries.
"""

import json
import os
import re
from pathlib import Path

# Manually verified colony boundaries
COLONIES = [
    ('Aden', 3793, 4493),
    ('Bahamas', 4494, 4942),
    ('Barbados', 4943, 5463),
    ('Bermuda', 5464, 5971),
    ('British Guiana', 5972, 6793),
    ('British Honduras', 6794, 7183),
    ('British Somaliland Protectorate', 7184, 7451),
    ('Brunei', 7452, 7703),
    ('Cyprus', 7704, 8406),
    ('East Africa High Commission', 8407, 8890),
    ('Falkland Islands', 8891, 9279),
    ('Fiji', 9280, 10017),
    ('Gambia', 10018, 10473),
    ('Gibraltar', 10474, 10913),
    ('Gold Coast', 10914, 12068),
    ('Hong Kong', 12069, 12802),
    ('Jamaica', 12803, 13943),
    ('Kenya', 13944, 15110),
    ('Leeward Islands', 15111, 16254),
    ('Federation of Malaya', 16255, 17145),
    ('Malta', 17146, 17678),
    ('Mauritius', 17679, 18698),
    ('Nigeria', 18699, 20426),
    ('North Borneo', 20427, 20778),
    ('Northern Rhodesia', 20779, 21767),
    ('Nyasaland Protectorate', 21768, 22297),
    ('St. Helena', 22298, 22640),
    ('Sarawak', 22641, 23126),
    ('Seychelles', 23127, 23491),
    ('Sierra Leone', 23492, 24166),
    ('Singapore', 24167, 25003),
    ('Tanganyika', 25004, 25723),
    ('Trinidad and Tobago', 25724, 26570),
    ('Uganda', 26571, 27231),
    ('Western Pacific', 27232, 28075),
    ('Windward Islands', 28076, 29250),
    ('Zanzibar', 29251, 29696),
    ('Miscellaneous Islands', 29697, 29867),
]

# File paths
INPUT_FILE = "/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1949/olmocr_results.md"
OUTPUT_DIR = "/home/user/colonial_office_list/output_3/1949_manual_parsed"
JSON_FILE = "/home/user/colonial_office_list/output_3/1949_manual_parsed.json"
REPORT_FILE = "/home/user/colonial_office_list/output_3/1949_PARSING_REPORT.md"

def clean_line(line):
    """Remove line number prefix from a line."""
    # Pattern: number→content
    match = re.match(r'^\s*\d+→(.*)$', line)
    if match:
        return match.group(1)
    return line

def sanitize_filename(name):
    """Convert colony name to safe filename."""
    # Replace spaces and special characters
    safe = name.replace(' ', '_').replace('/', '_').replace('&', 'and')
    safe = re.sub(r'[^\w\-]', '', safe)
    return safe

def extract_colonies():
    """Extract all colony sections to individual files."""
    
    print(f"Reading {INPUT_FILE}...")
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"Total lines in file: {len(lines)}")
    
    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Extract each colony
    metadata = {
        'source_file': INPUT_FILE,
        'year': 1949,
        'extraction_date': '2025-11-19',
        'total_colonies': len(COLONIES),
        'colonies': []
    }
    
    for colony_name, start_line, end_line in COLONIES:
        print(f"Extracting {colony_name} (lines {start_line}-{end_line})...")
        
        # Extract lines (convert to 0-based indexing)
        colony_lines = lines[start_line-1:end_line]
        
        # Clean lines (remove line number prefixes)
        cleaned_lines = [clean_line(line) for line in colony_lines]
        
        # Create output file
        filename = sanitize_filename(colony_name) + '.txt'
        filepath = os.path.join(OUTPUT_DIR, filename)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(cleaned_lines)
        
        # Add to metadata
        colony_info = {
            'name': colony_name,
            'filename': filename,
            'start_line': start_line,
            'end_line': end_line,
            'num_lines': end_line - start_line + 1,
            'file_size': os.path.getsize(filepath)
        }
        metadata['colonies'].append(colony_info)
        
        print(f"  Saved to {filename} ({colony_info['num_lines']} lines, {colony_info['file_size']} bytes)")
    
    # Save metadata JSON
    print(f"\nSaving metadata to {JSON_FILE}...")
    with open(JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)
    
    # Generate report
    print(f"Generating report {REPORT_FILE}...")
    generate_report(metadata)
    
    print(f"\n{'='*80}")
    print(f"Extraction complete!")
    print(f"Total colonies extracted: {len(COLONIES)}")
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"Metadata file: {JSON_FILE}")
    print(f"Report file: {REPORT_FILE}")
    print(f"{'='*80}")

def generate_report(metadata):
    """Generate a detailed parsing report."""
    
    report = []
    report.append("# 1949 Colonial Office List - Extraction Report\n")
    report.append(f"**Date:** {metadata['extraction_date']}\n")
    report.append(f"**Source:** {metadata['source_file']}\n")
    report.append(f"**Total Colonies:** {metadata['total_colonies']}\n")
    report.append("\n## Summary\n")
    report.append(f"Successfully extracted {metadata['total_colonies']} colonies from the 1949 Colonial Office List using manual boundary identification.\n")
    report.append("\n## Colonies Extracted\n")
    report.append("| # | Colony Name | Lines | Size (bytes) |\n")
    report.append("|---|-------------|-------|-------------|\n")
    
    for i, colony in enumerate(metadata['colonies'], 1):
        report.append(f"| {i:2d} | {colony['name']:40s} | {colony['start_line']:5d}-{colony['end_line']:5d} ({colony['num_lines']:5d}) | {colony['file_size']:8d} |\n")
    
    report.append("\n## Methodology\n")
    report.append("- **Approach:** Manual boundary identification\n")
    report.append("- **Part II Range:** Lines 3750-29867\n")
    report.append("- **Colonies found:** All 38 colonies from table of contents\n")
    report.append("\n## Notes\n")
    report.append("- Some colonies (Cyprus, Malta, Singapore) use different heading formats (bold instead of all caps)\n")
    report.append("- Malta section begins at line 17146 without a clear heading\n")
    report.append("- All line number prefixes have been removed from extracted text\n")
    report.append("- Western Pacific High Commission found at line 27232\n")
    report.append("- Miscellaneous Islands found at line 29697\n")
    
    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        f.writelines(report)

if __name__ == '__main__':
    extract_colonies()
