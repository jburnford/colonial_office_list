#!/usr/bin/env python3
"""
Batch fix Colonial Office List years 1931-1937, 1939-1940.
Identifies and corrects over-extraction patterns systematically.
"""

import json
import os
import re
from pathlib import Path
from collections import defaultdict

BASE_DIR = "/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs"
OUTPUT_BASE = "/home/user/colonial_office_list/output_2"

# Map years to their directory names
YEAR_DIRS = {
    1931: "colonial-office-list-1931",
    1932: "colonial-office-list-1932",
    1933: "colonial-office-list-1933",
    1934: "colonial-office-list-1934",
    1935: "dominions-office-list-1935",
    1936: "colonial-office-list-1936",
    1937: "colonial-office-list-1937",
    1939: "colonial-office-list-1939",
    1940: "colonial-office-list-1940",
}

def read_lines(filename, start_line, end_line):
    """Read specific lines from file (1-indexed, inclusive)."""
    with open(filename, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    if end_line > len(lines):
        end_line = len(lines)
    return ''.join(lines[start_line-1:end_line])

def find_section_boundaries(ocr_file):
    """Find colony section boundaries by scanning for headers."""
    with open(ocr_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    boundaries = []
    colony_patterns = [
        r'^AUSTRALIA\.',
        r'^DOMINION OF CANADA\.',
        r'^CANADA\.',
        r'^NEW ZEALAND\.',
        r'^SOUTH AFRICA\.',
        r'^ADEN\.',
        r'^TRISTAN DA CUNHA\.',
        r'^MISCELLANEOUS',
    ]

    for i, line in enumerate(lines, 1):
        for pattern in colony_patterns:
            if re.match(pattern, line):
                boundaries.append((i, line.strip()))

    return boundaries

def analyze_year(year):
    """Analyze a single year's extraction."""
    print(f"\n{'='*60}")
    print(f"ANALYZING YEAR {year}")
    print(f"{'='*60}")

    year_dir = YEAR_DIRS.get(year)
    if not year_dir:
        print(f"  ERROR: No directory mapping for year {year}")
        return None

    ocr_file = f"{BASE_DIR}/{year_dir}/olmocr_results.md"
    if not os.path.exists(ocr_file):
        print(f"  ERROR: OCR file not found: {ocr_file}")
        return None

    # Count total lines
    with open(ocr_file, 'r') as f:
        total_lines = sum(1 for _ in f)

    print(f"  OCR file: {total_lines} total lines")

    # Check if original extraction exists
    original_json = f"/home/user/colonial_office_list/output/{year}_manual_parsed.json"
    if os.path.exists(original_json):
        with open(original_json, 'r') as f:
            original_data = json.load(f)
        print(f"  Original extraction: {original_data['total_colonies']} colonies")

        # Analyze for over-extraction
        issues = []

        # Check ADEN
        aden = [c for c in original_data['colonies'] if c['colony_name'] == 'ADEN']
        if aden and aden[0]['line_count'] > 500:
            issues.append(f"ADEN over-extraction: {aden[0]['line_count']} lines")

        # Check AUSTRALIA states
        aus_states = [c for c in original_data['colonies'] if c['colony_name'] in [
            'QUEENSLAND', 'SOUTH AUSTRALIA', 'WESTERN AUSTRALIA', 'TASMANIA', 'VICTORIA'
        ]]
        if aus_states:
            small_states = [s for s in aus_states if s['line_count'] < 50]
            if small_states:
                issues.append(f"AUSTRALIA over-extraction: {len(small_states)} state subsections < 50 lines")

        # Check TRINIDAD/TOBAGO split
        trinidad = [c for c in original_data['colonies'] if c['colony_name'] == 'TRINIDAD']
        tobago = [c for c in original_data['colonies'] if c['colony_name'] == 'TOBAGO']
        if trinidad and tobago:
            issues.append(f"TRINIDAD/TOBAGO split: {trinidad[0]['line_count']} + {tobago[0]['line_count']} lines")

        if issues:
            print(f"\n  ISSUES FOUND:")
            for issue in issues:
                print(f"    - {issue}")
        else:
            print(f"  No obvious issues detected")

        return original_data
    else:
        print(f"  No original extraction found - needs full processing")
        return None

def main():
    print("Analyzing Colonial Office List years 1931-1937, 1939-1940...")

    results = {}
    for year in [1931, 1932, 1933, 1934, 1935, 1936, 1937, 1939, 1940]:
        results[year] = analyze_year(year)

    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    for year, data in results.items():
        if data:
            print(f"  {year}: {data['total_colonies']} colonies (needs fixing)")
        else:
            print(f"  {year}: No data (needs full extraction)")

if __name__ == "__main__":
    main()
