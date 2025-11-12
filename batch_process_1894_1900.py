#!/usr/bin/env python3
"""
Batch process Colonial Office Lists for 1894-1900 (Pre-Second Boer War II batch)

This script:
1. Loads parsed_v5_final.json for each year
2. Filters out table of contents entries (char_count < 1000)
3. Merges consecutive duplicates by extending boundaries
4. Extracts colony text from OCR markdown files
5. Creates output directories and clean JSON metadata
"""

import json
import os
import re
from pathlib import Path
from typing import List, Dict

# Configuration
BASE_DIR = Path("/home/user/colonial_office_list")
OUTPUT_DIR = BASE_DIR / "output"
YEARS = [1894, 1896, 1897, 1898, 1899, 1900]
MIN_CHAR_COUNT = 1000  # Filter out ToC entries

def load_parsed_json(year: int) -> Dict:
    """Load the parsed_v5_final.json for a given year"""
    json_path = OUTPUT_DIR / f"{year}_parsed_v5_final.json"
    with open(json_path, 'r') as f:
        return json.load(f)

def filter_toc_entries(colonies: List[Dict]) -> List[Dict]:
    """Filter out table of contents entries (small char_count)"""
    # Keep entries with char_count >= MIN_CHAR_COUNT
    filtered = [c for c in colonies if c.get('char_count', 0) >= MIN_CHAR_COUNT]
    print(f"  Filtered {len(colonies)} -> {len(filtered)} (removed {len(colonies) - len(filtered)} ToC entries)")
    return filtered

def merge_duplicates(colonies: List[Dict]) -> List[Dict]:
    """Merge consecutive colonies with the same name by extending end_line"""
    if not colonies:
        return []

    merged = []
    current = colonies[0].copy()

    for i in range(1, len(colonies)):
        next_colony = colonies[i]

        # If same name as current, extend the boundary
        if next_colony['colony_name'] == current['colony_name']:
            print(f"  Merging duplicate: {current['colony_name']} (lines {current['start_line']}-{current['end_line']} + {next_colony['start_line']}-{next_colony['end_line']})")
            current['end_line'] = next_colony['end_line']
            current['char_count'] += next_colony.get('char_count', 0)
        else:
            # Different name, save current and move to next
            merged.append(current)
            current = next_colony.copy()

    # Don't forget the last one
    merged.append(current)

    print(f"  Merged {len(colonies)} -> {len(merged)} colonies ({len(colonies) - len(merged)} duplicates merged)")
    return merged

def load_ocr_markdown(year: int) -> List[str]:
    """Load the OCR markdown file and return lines"""
    ocr_path = BASE_DIR / "historical_document_pipeline" / "processed_pdfs" / f"colonial-office-list-{year}" / "olmocr_results.md"
    with open(ocr_path, 'r', encoding='utf-8') as f:
        return f.readlines()

def extract_colony_text(lines: List[str], start_line: int, end_line: int) -> str:
    """Extract text for a colony given line numbers (1-indexed)"""
    # Convert to 0-indexed
    start_idx = start_line - 1
    end_idx = end_line  # end_line is exclusive in slicing

    if start_idx < 0:
        start_idx = 0
    if end_idx > len(lines):
        end_idx = len(lines)

    return ''.join(lines[start_idx:end_idx])

def sanitize_filename(name: str) -> str:
    """Convert colony name to valid filename"""
    # Replace spaces and special characters
    filename = name.upper()
    filename = filename.replace(' ', '_')
    filename = filename.replace("'", '')
    filename = filename.replace('.', '')
    filename = re.sub(r'[^\w\-]', '_', filename)
    return filename + '.md'

def process_year(year: int) -> Dict:
    """Process a single year: clean data, extract texts, save outputs"""
    print(f"\n{'='*60}")
    print(f"Processing {year}")
    print(f"{'='*60}")

    # Load parsed JSON
    data = load_parsed_json(year)
    colonies = data['colonies']
    print(f"Loaded {len(colonies)} raw colonies from parsed_v5_final.json")

    # Filter ToC entries
    colonies = filter_toc_entries(colonies)

    # Merge duplicates
    colonies = merge_duplicates(colonies)

    # Load OCR markdown
    print(f"Loading OCR markdown...")
    lines = load_ocr_markdown(year)
    print(f"Loaded {len(lines)} lines from OCR file")

    # Create output directory
    output_dir = OUTPUT_DIR / f"{year}_manual_parsed"
    output_dir.mkdir(exist_ok=True)
    print(f"Created output directory: {output_dir}")

    # Extract and save each colony
    print(f"\nExtracting {len(colonies)} colonies...")
    for i, colony in enumerate(colonies, 1):
        name = colony['colony_name']
        start = colony['start_line']
        end = colony['end_line']

        # Extract text
        text = extract_colony_text(lines, start, end)

        # Save to file
        filename = sanitize_filename(name)
        filepath = output_dir / filename
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(text)

        # Update colony metadata with actual line count
        colony['line_count'] = end - start
        colony['filename'] = filename
        colony['year'] = year

        print(f"  [{i:2d}/{len(colonies)}] {name:35s} -> {filename:40s} ({start:5d}-{end:5d}, {colony['line_count']:4d} lines)")

    # Create clean JSON metadata
    clean_data = {
        'year': year,
        'source_file': f'historical_document_pipeline/processed_pdfs/colonial-office-list-{year}/olmocr_results.md',
        'total_colonies': len(colonies),
        'colonies': colonies,
        'processing_notes': {
            'toc_entries_filtered': True,
            'duplicates_merged': True,
            'min_char_count_threshold': MIN_CHAR_COUNT
        }
    }

    json_path = OUTPUT_DIR / f"{year}_manual_parsed.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(clean_data, f, indent=2)
    print(f"\nSaved metadata: {json_path}")
    print(f"Final count: {len(colonies)} colonies")

    return clean_data

def main():
    """Process all years in batch"""
    print("="*60)
    print("BATCH PROCESSING: 1894-1900 Colonial Office Lists")
    print("Pre-Second Boer War II Batch")
    print("="*60)

    results = {}
    for year in YEARS:
        try:
            results[year] = process_year(year)
        except Exception as e:
            print(f"\nERROR processing {year}: {e}")
            import traceback
            traceback.print_exc()
            continue

    # Summary
    print("\n" + "="*60)
    print("BATCH PROCESSING COMPLETE")
    print("="*60)
    print("\nSummary:")
    for year in YEARS:
        if year in results:
            count = results[year]['total_colonies']
            print(f"  {year}: {count:2d} colonies")
        else:
            print(f"  {year}: FAILED")

    total = sum(r['total_colonies'] for r in results.values())
    print(f"\nTotal colonies extracted: {total}")
    print(f"Years processed: {len(results)}/{len(YEARS)}")

if __name__ == '__main__':
    main()
