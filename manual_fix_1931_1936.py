#!/usr/bin/env python3
"""
Manual fixes for 1931 and 1936 ADEN over-extraction.
The automated script missed these due to **TRISTAN formatting.
"""

import json
import os

BASE_DIR = "/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs"
OUTPUT_BASE = "/home/user/colonial_office_list/output_2"

def read_lines(filename, start_line, end_line):
    """Read specific lines from file (1-indexed, inclusive)."""
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    if end_line > len(lines):
        end_line = len(lines)
    return ''.join(lines[start_line-1:end_line])

def fix_year_1931():
    """Fix year 1931 ADEN over-extraction."""
    print("Fixing year 1931...")

    year = 1931
    ocr_file = f"{BASE_DIR}/colonial-office-list-1931/olmocr_results.md"
    metadata_file = f"{OUTPUT_BASE}/1931_manual_parsed.json"

    with open(metadata_file, 'r') as f:
        metadata = json.load(f)

    # Fix ADEN: was 52512-72646 (20134 lines), should be 52513-52556 (44 lines)
    for colony in metadata['colonies']:
        if colony['name'] == 'ADEN':
            colony['start_line'] = 52513
            colony['end_line'] = 52556
            colony['line_count'] = 43
            colony['extraction_method'] = 'merged_or_manually_added'
            break

    # Add TRISTAN DA CUNHA: 52556-52571 (15 lines)
    tristan_exists = any(c['name'] == 'TRISTAN DA CUNHA' for c in metadata['colonies'])
    if not tristan_exists:
        metadata['colonies'].append({
            "name": "TRISTAN DA CUNHA",
            "filename": "TRISTAN_DA_CUNHA.md",
            "start_line": 52556,
            "end_line": 52571,
            "line_count": 15,
            "is_appendix": False,
            "extraction_method": "merged_or_manually_added"
        })

    # Add MISCELLANEOUS ISLANDS: 52571-52580 (9 lines)
    misc_exists = any(c['name'] == 'MISCELLANEOUS ISLANDS' for c in metadata['colonies'])
    if not misc_exists:
        metadata['colonies'].append({
            "name": "MISCELLANEOUS ISLANDS",
            "filename": "MISCELLANEOUS_ISLANDS.md",
            "start_line": 52571,
            "end_line": 52580,
            "line_count": 9,
            "is_appendix": False,
            "extraction_method": "merged_or_manually_added"
        })

    # Sort by start_line
    metadata['colonies'].sort(key=lambda x: x['start_line'])
    metadata['total_colonies'] = len(metadata['colonies'])

    # Update corrections
    if 'corrections_applied' not in metadata:
        metadata['corrections_applied'] = []
    metadata['corrections_applied'].extend([
        "Fixed ADEN massive over-extraction: 20134 → 43 lines",
        "Added missing TRISTAN DA CUNHA (15 lines)",
        "Added missing MISCELLANEOUS ISLANDS (9 lines)"
    ])

    # Write metadata
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)

    # Extract files
    output_dir = f"{OUTPUT_BASE}/1931_manual_parsed"
    for colony in metadata['colonies']:
        if colony['name'] in ['ADEN', 'TRISTAN DA CUNHA', 'MISCELLANEOUS ISLANDS']:
            content = read_lines(ocr_file, colony['start_line'], colony['end_line'])
            filepath = f"{output_dir}/{colony['filename']}"
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  ✓ {colony['name']}: {colony['line_count']} lines")

    print(f"  ✓ Total colonies: {metadata['total_colonies']}")

def fix_year_1936():
    """Fix year 1936 ADEN over-extraction."""
    print("\nFixing year 1936...")

    year = 1936
    ocr_file = f"{BASE_DIR}/colonial-office-list-1936/olmocr_results.md"
    metadata_file = f"{OUTPUT_BASE}/1936_manual_parsed.json"

    with open(metadata_file, 'r') as f:
        metadata = json.load(f)

    # Fix ADEN: was 48758-69342 (20584 lines), should be 48758-48864 (106 lines)
    for colony in metadata['colonies']:
        if colony['name'] == 'ADEN':
            colony['start_line'] = 48758
            colony['end_line'] = 48864
            colony['line_count'] = 106
            colony['extraction_method'] = 'merged_or_manually_added'
            break

    # Add TRISTAN DA CUNHA: 48864-48879 (15 lines)
    tristan_exists = any(c['name'] == 'TRISTAN DA CUNHA' for c in metadata['colonies'])
    if not tristan_exists:
        metadata['colonies'].append({
            "name": "TRISTAN DA CUNHA",
            "filename": "TRISTAN_DA_CUNHA.md",
            "start_line": 48864,
            "end_line": 48879,
            "line_count": 15,
            "is_appendix": False,
            "extraction_method": "merged_or_manually_added"
        })

    # Add MISCELLANEOUS ISLANDS: 48879-48888 (9 lines)
    misc_exists = any(c['name'] == 'MISCELLANEOUS ISLANDS' for c in metadata['colonies'])
    if not misc_exists:
        metadata['colonies'].append({
            "name": "MISCELLANEOUS ISLANDS",
            "filename": "MISCELLANEOUS_ISLANDS.md",
            "start_line": 48879,
            "end_line": 48888,
            "line_count": 9,
            "is_appendix": False,
            "extraction_method": "merged_or_manually_added"
        })

    # Sort by start_line
    metadata['colonies'].sort(key=lambda x: x['start_line'])
    metadata['total_colonies'] = len(metadata['colonies'])

    # Update corrections
    if 'corrections_applied' not in metadata:
        metadata['corrections_applied'] = []
    metadata['corrections_applied'].extend([
        "Fixed ADEN massive over-extraction: 20584 → 106 lines",
        "Added missing TRISTAN DA CUNHA (15 lines)",
        "Added missing MISCELLANEOUS ISLANDS (9 lines)"
    ])

    # Write metadata
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)

    # Extract files
    output_dir = f"{OUTPUT_BASE}/1936_manual_parsed"
    for colony in metadata['colonies']:
        if colony['name'] in ['ADEN', 'TRISTAN DA CUNHA', 'MISCELLANEOUS ISLANDS']:
            content = read_lines(ocr_file, colony['start_line'], colony['end_line'])
            filepath = f"{output_dir}/{colony['filename']}"
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  ✓ {colony['name']}: {colony['line_count']} lines")

    print(f"  ✓ Total colonies: {metadata['total_colonies']}")

def main():
    fix_year_1931()
    fix_year_1936()
    print("\n✓ Manual fixes complete!")

if __name__ == "__main__":
    main()
