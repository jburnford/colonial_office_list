#!/usr/bin/env python3
"""
Cleanup duplicate colonies and merge them into single entries.
"""

import json
import os
from pathlib import Path
from collections import OrderedDict

BASE_DIR = Path("/home/user/colonial_office_list")
OUTPUT_DIR = BASE_DIR / "output"

YEARS = [1888, 1889, 1890]


def merge_duplicates(colonies):
    """Merge duplicate colony entries."""
    merged = OrderedDict()

    for colony in colonies:
        name = colony['name']

        if name not in merged:
            # First occurrence - keep as is
            merged[name] = colony.copy()
        else:
            # Duplicate found - merge by extending the end_line
            print(f"  Merging duplicate: {name}")
            print(f"    Original: lines {merged[name]['start_line']}-{merged[name]['end_line']}")
            print(f"    Duplicate: lines {colony['start_line']}-{colony['end_line']}")

            # Extend end_line to include the duplicate section
            merged[name]['end_line'] = colony['end_line']
            merged[name]['line_count'] = merged[name]['end_line'] - merged[name]['start_line'] + 1

            print(f"    Merged: lines {merged[name]['start_line']}-{merged[name]['end_line']} ({merged[name]['line_count']} lines)")

    return list(merged.values())


def extract_colony_content(year, colony):
    """Extract content for a colony from the OCR file."""
    ocr_file = BASE_DIR / "historical_document_pipeline/processed_pdfs" / f"colonial-office-list-{year}" / "olmocr_results.md"

    with open(ocr_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    start = colony['start_line'] - 1  # Convert to 0-indexed
    end = colony['end_line']

    return ''.join(lines[start:end])


def process_year(year):
    """Process a single year - merge duplicates and recreate files."""
    print(f"\n{'='*60}")
    print(f"Cleaning up {year}")
    print(f"{'='*60}")

    metadata_path = OUTPUT_DIR / f"{year}_manual_parsed.json"

    if not metadata_path.exists():
        print(f"ERROR: Metadata not found: {metadata_path}")
        return

    # Load metadata
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)

    print(f"Original colony count: {metadata['total_colonies']}")

    # Merge duplicates
    merged_colonies = merge_duplicates(metadata['colonies'])

    print(f"Merged colony count: {len(merged_colonies)}")

    # Recreate output directory
    output_dir = OUTPUT_DIR / f"{year}_manual_parsed"

    # Remove old files
    for file in output_dir.glob("*.md"):
        file.unlink()

    # Write new colony files with merged content
    for colony in merged_colonies:
        content = extract_colony_content(year, colony)

        file_path = output_dir / colony['filename']
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)

    print(f"Saved {len(merged_colonies)} merged colony files")

    # Update metadata
    metadata['total_colonies'] = len(merged_colonies)
    metadata['colonies'] = merged_colonies

    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)

    print(f"Updated metadata")

    return merged_colonies


def main():
    """Main cleanup function."""
    print("="*60)
    print("Cleaning Up Duplicate Colonies")
    print("="*60)

    results = {}

    for year in YEARS:
        colonies = process_year(year)
        if colonies:
            results[year] = len(colonies)

    print("\n" + "="*60)
    print("CLEANUP COMPLETE")
    print("="*60)
    print("\nFinal colony counts:")
    for year, count in results.items():
        print(f"  {year}: {count} colonies")

    return results


if __name__ == "__main__":
    main()
