#!/usr/bin/env python3
"""
Extract colonies from 1964 Colonial Office List using MANUAL boundary identification.

This script extracts individual colony sections from the 1964 OCR results file
based on manually identified boundaries through content analysis.
"""

import os
import json
import re
from pathlib import Path
from datetime import datetime

# Source file
SOURCE_FILE = "/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1964/olmocr_results.md"

# Output directory
OUTPUT_DIR = "/home/user/colonial_office_list/output_3/1964_manual_parsed"

# Metadata file
METADATA_FILE = "/home/user/colonial_office_list/output_3/1964_manual_parsed.json"

# Colony boundaries identified manually by reading the content
# Format: (start_line, end_line, colony_name, notes)
# Line numbers are 1-indexed (as shown by Read tool)
COLONY_BOUNDARIES = [
    (2832, 3298, "malta", "State of Malta, G.C. - became independent May 1964"),
    (3299, 3302, "singapore", "State of Singapore - brief note, see Malaysia"),
    (3303, 4079, "aden", "Aden (with Protectorate and Federation of South Arabia)"),
    (4080, 4193, "antigua", "Antigua"),
    (4194, 4591, "bahama_islands", "Bahama Islands"),
    (4592, 5009, "barbados", "Barbados"),
    (5010, 5399, "bermuda", "Bermuda"),
    (5400, 5476, "british_antarctic_territory", "British Antarctic Territory"),
    (5477, 5966, "british_guiana", "British Guiana"),
    (5967, 6405, "british_honduras", "British Honduras"),
    (6406, 6411, "brunei", "Brunei - very brief entry"),
    (6412, 6571, "cayman_islands", "Cayman Islands"),
    (6572, 6830, "dominica", "Dominica"),
    (6831, 7127, "falkland_islands", "Falkland Islands and Dependencies"),
    (7128, 7451, "fiji", "Fiji"),
    (7452, 7833, "gambia", "Gambia"),
    (7834, 8071, "gibraltar", "Gibraltar"),
    (8072, 8371, "grenada", "Grenada (OCR shows as 'GRENA DA')"),
    (8372, 9114, "high_commission_territories", "The High Commission Territories (Basutoland, Bechuanaland, Swaziland)"),
    (9115, 9534, "hong_kong", "Hong Kong"),
    (9535, 9542, "kenya", "Kenya - became independent December 1963, brief note"),
    (9543, 9569, "malaysia", "Malaysia - formation in 1963"),
    (9570, 9966, "mauritius", "Mauritius"),
    (9967, 10136, "montserrat", "Montserrat"),
    (10137, 10732, "northern_rhodesia", "Northern Rhodesia - became Zambia in October 1964"),
    (10733, 11212, "nyasaland", "Nyasaland Protectorate - became Malawi in July 1964"),
    (11213, 11222, "pitcairn_islands", "Pitcairn Islands Group"),
    (11223, 11395, "st_christopher_nevis_anguilla", "St. Christopher, Nevis and Anguilla"),
    (11396, 11660, "st_helena", "St. Helena (with Ascension and Tristan da Cunha)"),
    (11661, 11896, "st_lucia", "St. Lucia"),
    (11897, 12152, "st_vincent", "St. Vincent"),
    (12153, 12158, "sarawak", "Sarawak - brief note, see Malaysia"),
    (12159, 12547, "seychelles", "Seychelles"),
    (12548, 12692, "tonga", "Kingdom of Tonga"),
    (12693, 12853, "turks_and_caicos_islands", "Turks and Caicos Islands"),
    (12854, 13025, "virgin_islands", "Virgin Islands"),
    (13026, 13731, "western_pacific", "Western Pacific High Commission (British Solomon Islands, Gilbert & Ellice Islands, New Hebrides)"),
    (13732, 13739, "zanzibar", "Zanzibar - brief note"),
    (13740, 13773, "miscellaneous_islands", "Miscellaneous Islands"),
]

def read_file_lines(filepath):
    """Read all lines from the file."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.readlines()

def remove_line_numbers(line):
    """
    Remove line number prefixes from OCR output.
    Format is typically: '  1234→content' or '1234→content'
    """
    # Match optional spaces, digits, arrow, then capture the rest
    match = re.match(r'^\s*\d+→(.*)$', line)
    if match:
        return match.group(1)
    return line

def extract_colony(lines, start_line, end_line, colony_name, notes):
    """
    Extract a colony section from the lines.

    Args:
        lines: List of all lines from the file
        start_line: Starting line number (1-indexed)
        end_line: Ending line number (1-indexed, inclusive)
        colony_name: Name for the output file
        notes: Description/notes about this colony

    Returns:
        Dictionary with extraction info
    """
    # Convert to 0-indexed for Python list access
    start_idx = start_line - 1
    end_idx = end_line  # end_line is inclusive, so we go up to but not including end_line

    # Extract the lines
    colony_lines = lines[start_idx:end_idx]

    # Remove line number prefixes
    cleaned_lines = [remove_line_numbers(line) for line in colony_lines]

    # Join into content
    content = ''.join(cleaned_lines)

    # Count statistics
    num_lines = len(cleaned_lines)
    num_words = len(content.split())
    num_chars = len(content)

    return {
        'colony_name': colony_name,
        'notes': notes,
        'start_line': start_line,
        'end_line': end_line,
        'num_lines': num_lines,
        'num_words': num_words,
        'num_chars': num_chars,
        'content': content
    }

def main():
    """Main extraction function."""
    print("=" * 80)
    print("1964 Colonial Office List - Manual Colony Extraction")
    print("=" * 80)
    print()

    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"Output directory: {OUTPUT_DIR}")
    print()

    # Read the source file
    print(f"Reading source file: {SOURCE_FILE}")
    lines = read_file_lines(SOURCE_FILE)
    total_lines = len(lines)
    print(f"Total lines in source: {total_lines:,}")
    print()

    # Extract each colony
    print(f"Extracting {len(COLONY_BOUNDARIES)} colonies...")
    print()

    metadata = {
        'extraction_date': datetime.now().isoformat(),
        'source_file': SOURCE_FILE,
        'total_source_lines': total_lines,
        'methodology': 'MANUAL boundary identification by reading content',
        'num_colonies': len(COLONY_BOUNDARIES),
        'colonies': []
    }

    total_words = 0
    total_colony_lines = 0

    for start_line, end_line, colony_name, notes in COLONY_BOUNDARIES:
        print(f"Extracting: {colony_name:40s} (lines {start_line:5d}-{end_line:5d})")

        # Extract colony
        colony_data = extract_colony(lines, start_line, end_line, colony_name, notes)

        # Write to file
        output_file = os.path.join(OUTPUT_DIR, f"{colony_name}.txt")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(colony_data['content'])

        # Add to metadata (without content)
        colony_meta = {k: v for k, v in colony_data.items() if k != 'content'}
        colony_meta['output_file'] = output_file
        metadata['colonies'].append(colony_meta)

        # Update totals
        total_words += colony_data['num_words']
        total_colony_lines += colony_data['num_lines']

        print(f"  → {colony_data['num_lines']:4d} lines, {colony_data['num_words']:6d} words")

    print()
    print("=" * 80)
    print("EXTRACTION SUMMARY")
    print("=" * 80)
    print(f"Colonies extracted:     {len(COLONY_BOUNDARIES)}")
    print(f"Total lines extracted:  {total_colony_lines:,}")
    print(f"Total words extracted:  {total_words:,}")
    print(f"Output directory:       {OUTPUT_DIR}")
    print()

    # Add summary to metadata
    metadata['summary'] = {
        'total_lines_extracted': total_colony_lines,
        'total_words_extracted': total_words,
        'avg_lines_per_colony': total_colony_lines / len(COLONY_BOUNDARIES),
        'avg_words_per_colony': total_words / len(COLONY_BOUNDARIES)
    }

    # Write metadata
    print(f"Writing metadata to: {METADATA_FILE}")
    with open(METADATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)

    print()
    print("✓ Extraction complete!")
    print()

    # Print notable observations
    print("=" * 80)
    print("NOTABLE OBSERVATIONS FOR 1964")
    print("=" * 80)
    print()
    print("MAJOR INDEPENDENCE EVENTS:")
    print("  • Malta - Independence May 1964")
    print("  • Kenya - Independence December 1963 (brief note only)")
    print("  • Zanzibar - Independence December 1963 (brief note only)")
    print("  • Nyasaland → Malawi - Independence July 1964")
    print("  • Northern Rhodesia → Zambia - Independence October 1964")
    print()
    print("MALAYSIA FORMATION (1963):")
    print("  • Malaysia entry created from Malaya, Singapore, North Borneo (Sabah), Sarawak")
    print("  • Singapore shown as separate brief entry")
    print("  • Sarawak shown as brief entry")
    print("  • Brunei did not join Malaysia")
    print()
    print("FEDERATION CHANGES:")
    print("  • Federation of Rhodesia & Nyasaland dissolved")
    print("  • South Arabia Federation formation in progress")
    print()
    print("SPECIAL ENTRIES:")
    print("  • High Commission Territories (Basutoland, Bechuanaland, Swaziland)")
    print("  • Western Pacific High Commission")
    print("  • British Antarctic Territory")
    print()
    print("OCR ISSUES NOTED:")
    print("  • 'GRENADA' appears as 'GRENA DA' at line 8072")
    print()

if __name__ == "__main__":
    main()
