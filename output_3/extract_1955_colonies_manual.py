#!/usr/bin/env python3
"""
Extract colonies from 1955 Colonial Office List using manual boundary identification.

This script extracts individual colony sections based on manually identified
line boundaries, removing OCR line number prefixes.
"""

import re
import json
import os
from pathlib import Path
from collections import Counter

# Configuration
SOURCE_FILE = "/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1955/olmocr_results.md"
OUTPUT_DIR = Path("/home/user/colonial_office_list/output_3/1955_manual_parsed")
BOUNDARIES_FILE = "/home/user/colonial_office_list/output_3/1955_colony_boundaries.json"
METADATA_FILE = "/home/user/colonial_office_list/output_3/1955_manual_parsed.json"

# Line number prefix pattern (e.g., "  3200→" or "     1→")
LINE_PREFIX_PATTERN = re.compile(r'^\s*\d+→')


def remove_line_numbers(line):
    """Remove OCR line number prefix from a line."""
    # The line numbers appear as: spaces + digits + arrow
    # e.g., "  3200→ADEN COLONY" becomes "ADEN COLONY"
    match = LINE_PREFIX_PATTERN.match(line)
    if match:
        return line[match.end():]
    return line


def extract_colonies():
    """Extract all colonies based on manual boundaries."""

    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Load boundaries
    with open(BOUNDARIES_FILE, 'r') as f:
        boundaries = json.load(f)

    print(f"Loading source file: {SOURCE_FILE}")
    with open(SOURCE_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    print(f"Total lines in source: {len(lines)}")
    print(f"Extracting {len(boundaries)} colonies...\n")

    metadata = {
        'source_file': SOURCE_FILE,
        'total_colonies': len(boundaries),
        'extraction_date': '2025-11-19',
        'method': 'manual_boundary_identification',
        'colonies': []
    }

    for colony_info in boundaries:
        name = colony_info['name']
        start_line = colony_info['start_line']
        end_line = colony_info['end_line']

        # Extract lines (convert to 0-indexed)
        colony_lines = lines[start_line-1:end_line]

        # Remove line number prefixes
        cleaned_lines = [remove_line_numbers(line) for line in colony_lines]

        # Join into text
        colony_text = ''.join(cleaned_lines)

        # Calculate statistics
        word_count = len(colony_text.split())
        char_count = len(colony_text)
        line_count = len(cleaned_lines)

        # Save to file
        output_file = OUTPUT_DIR / f"{name}.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(colony_text)

        # Add to metadata
        colony_metadata = {
            'name': name,
            'start_line': start_line,
            'end_line': end_line,
            'line_count': line_count,
            'word_count': word_count,
            'char_count': char_count,
            'output_file': str(output_file.relative_to(OUTPUT_DIR.parent))
        }
        metadata['colonies'].append(colony_metadata)

        print(f"✓ {name:30} | Lines {start_line:5}-{end_line:5} | {line_count:4} lines | {word_count:6} words")

    # Calculate totals
    total_lines = sum(c['line_count'] for c in metadata['colonies'])
    total_words = sum(c['word_count'] for c in metadata['colonies'])
    total_chars = sum(c['char_count'] for c in metadata['colonies'])

    metadata['totals'] = {
        'total_lines': total_lines,
        'total_words': total_words,
        'total_chars': total_chars
    }

    # Save metadata
    with open(METADATA_FILE, 'w') as f:
        json.dump(metadata, f, indent=2)

    print(f"\n{'='*80}")
    print(f"EXTRACTION COMPLETE")
    print(f"{'='*80}")
    print(f"Total colonies extracted: {len(boundaries)}")
    print(f"Total lines: {total_lines:,}")
    print(f"Total words: {total_words:,}")
    print(f"Total characters: {total_chars:,}")
    print(f"\nOutput directory: {OUTPUT_DIR}")
    print(f"Metadata file: {METADATA_FILE}")


if __name__ == '__main__':
    extract_colonies()
