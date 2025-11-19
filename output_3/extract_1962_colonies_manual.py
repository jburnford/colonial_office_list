#!/usr/bin/env python3
"""
Extract individual colony sections from 1962 Colonial Office List
using manually identified boundaries.
"""

import json
import os
import re
from pathlib import Path

def remove_line_numbers(line):
    """Remove line number prefix from OCR output."""
    # Pattern: spaces + line number + → + content
    match = re.match(r'^\s*\d+→(.*)', line)
    if match:
        return match.group(1)
    return line

def extract_colonies(source_file, boundaries_file, output_dir):
    """
    Extract each colony section to its own file.
    """
    # Load boundaries
    with open(boundaries_file, 'r') as f:
        colonies = json.load(f)

    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Read entire source file
    with open(source_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    stats = []

    print(f"Extracting {len(colonies)} colonies...")
    print("=" * 80)

    for colony in colonies:
        name = colony['name']
        start = colony['start_line']
        end = colony['end_line']

        # Create safe filename
        safe_name = name.replace('/', '_').replace(' ', '_').replace('(', '').replace(')', '').replace(',', '')
        filename = f"{safe_name}.txt"
        output_file = output_path / filename

        # Extract lines (convert 1-indexed to 0-indexed)
        colony_lines = lines[start-1:end]

        # Remove line numbers
        clean_lines = [remove_line_numbers(line) for line in colony_lines]

        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.writelines(clean_lines)

        # Calculate statistics
        num_lines = len(clean_lines)
        text = ''.join(clean_lines)
        num_words = len(text.split())
        num_chars = len(text)

        stats.append({
            'name': name,
            'filename': filename,
            'start_line': start,
            'end_line': end,
            'num_lines': num_lines,
            'num_words': num_words,
            'num_chars': num_chars
        })

        print(f"✓ {name:50s} → {filename:50s} ({num_lines:4d} lines, {num_words:5d} words)")

    return stats

if __name__ == '__main__':
    source_file = '/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1962/olmocr_results.md'
    boundaries_file = '/home/user/colonial_office_list/output_3/1962_colonies_boundaries.json'
    output_dir = '/home/user/colonial_office_list/output_3/1962_manual_parsed'

    print("1962 Colonial Office List - Manual Colony Extraction")
    print("=" * 80)
    print()

    stats = extract_colonies(source_file, boundaries_file, output_dir)

    print()
    print("=" * 80)
    print(f"Extraction complete! {len(stats)} colony files created.")
    print(f"Output directory: {output_dir}")

    # Calculate totals
    total_lines = sum(s['num_lines'] for s in stats)
    total_words = sum(s['num_words'] for s in stats)
    total_chars = sum(s['num_chars'] for s in stats)

    print()
    print("Summary Statistics:")
    print(f"  Total colonies: {len(stats)}")
    print(f"  Total lines:    {total_lines:,}")
    print(f"  Total words:    {total_words:,}")
    print(f"  Total chars:    {total_chars:,}")

    # Save detailed statistics
    metadata = {
        'year': 1962,
        'extraction_method': 'manual_boundary_identification',
        'source_file': source_file,
        'num_colonies': len(stats),
        'total_lines': total_lines,
        'total_words': total_words,
        'total_chars': total_chars,
        'colonies': stats
    }

    metadata_file = '/home/user/colonial_office_list/output_3/1962_manual_parsed.json'
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)

    print(f"\nMetadata saved to: {metadata_file}")
