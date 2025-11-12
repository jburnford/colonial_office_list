#!/usr/bin/env python3
"""
Batch parser for Colonial Office Lists 1905-1915
Extracts colony sections from OCR results and creates structured outputs
"""

import os
import re
import json
from pathlib import Path
from typing import List, Dict, Tuple

def find_colony_headers(lines: List[str]) -> List[Tuple[int, str]]:
    """
    Find all colony headers in the document.
    Returns list of (line_number, colony_name) tuples.
    """
    headers = []

    # Track if we've seen the main colonies section start
    in_colonies_section = False

    # Patterns that indicate we're past the colonies section
    appendix_patterns = [
        r'^APPENDIX',
        r'^INDEX',
        r'^ADDITIONS AND CORRECTIONS',
        r'^PENSIONS',
        r'^REGULATIONS',
        r'^COLONIAL CIVIL SERVICE',
    ]

    # Known section headers that aren't colonies
    non_colony_headers = {
        'CONTENTS', 'PREFACE', 'THE COLONIAL OFFICE', 'COLONIAL OFFICE LIST',
        'ESTABLISHMENTS IN THE COLONIES', 'CROWN AGENTS FOR THE COLONIES',
        'EXCHEQUER AND AUDIT DEPARTMENT', 'COLONIAL AUDIT BRANCH',
        'ESTABLISHMENT', 'DISTRIBUTION OF BUSINESS', 'TRUSTEESHIPS',
        'EMIGRATION', 'ROYAL BOTANIC GARDENS',
    }

    for i, line in enumerate(lines, 1):
        line_stripped = line.strip()

        # Check if we're entering appendices/back matter
        if any(re.match(pattern, line_stripped, re.I) for pattern in appendix_patterns):
            break

        # Look for major section markers
        if line_stripped in ['COLONIES.', 'AUSTRALIA.']:
            in_colonies_section = True
            continue

        # Look for all-caps headers that could be colonies
        if re.match(r'^[A-Z][A-Z\s\'\-&(),]+\.?$', line_stripped):
            # Filter out known non-colony headers
            clean_name = line_stripped.rstrip('.')

            # Skip if it's a known non-colony header
            if clean_name in non_colony_headers:
                continue

            # Skip very short headers (likely not colonies)
            if len(clean_name) < 4:
                continue

            # Skip headers that are clearly not colonies
            if any(keyword in clean_name for keyword in ['OFFICE', 'DEPARTMENT', 'BRANCH', 'AGENTS', 'ESTABLISHMENT']):
                continue

            # If we're in the colonies section or this looks like a substantial header
            if in_colonies_section or len(clean_name) >= 6:
                # Look ahead to verify it's actually a colony section
                # Colonies typically have descriptive text or administrative structure
                if i < len(lines) - 5:
                    next_lines = ' '.join(lines[i:i+10]).lower()
                    # Check for colony-like content
                    colony_indicators = ['governor', 'colony', 'protectorate', 'commonwealth',
                                       'legislative', 'executive', 'chief justice', 'population',
                                       'revenue', 'area']
                    if any(indicator in next_lines for indicator in colony_indicators):
                        headers.append((i, clean_name))

    return headers

def extract_colony_section(lines: List[str], start_line: int, next_start_line: int) -> Tuple[str, int, int, int]:
    """
    Extract a colony section from the document.
    Returns (content, actual_start, actual_end, char_count)
    """
    # Get the section (using 0-based indexing)
    section_lines = lines[start_line-1:next_start_line-1]

    # Remove trailing blank lines
    while section_lines and not section_lines[-1].strip():
        section_lines.pop()

    content = '\n'.join(section_lines)
    actual_end = start_line + len(section_lines) - 1

    return content, start_line, actual_end, len(content)

def sanitize_filename(colony_name: str) -> str:
    """Convert colony name to valid filename."""
    # Replace spaces and special characters
    filename = colony_name.replace(' ', '_')
    filename = filename.replace("'", '')
    filename = filename.replace('-', '_')
    filename = filename.replace('(', '')
    filename = filename.replace(')', '')
    filename = filename.replace(',', '')
    filename = filename.replace('&', 'AND')
    return filename + '.md'

def process_year(year: int, base_dir: str) -> Dict:
    """
    Process a single year's Colonial Office List.
    """
    print(f"\n{'='*60}")
    print(f"Processing {year} Colonial Office List")
    print(f"{'='*60}")

    # Paths
    input_file = f"{base_dir}/historical_document_pipeline/processed_pdfs/colonial-office-list-{year}/olmocr_results.md"
    output_dir = f"{base_dir}/output/{year}_manual_parsed"
    output_json = f"{base_dir}/output/{year}_manual_parsed.json"

    # Read input file
    print(f"Reading {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    print(f"Total lines: {len(lines)}")

    # Find colony headers
    print("Finding colony headers...")
    headers = find_colony_headers(lines)
    print(f"Found {len(headers)} potential colonies")

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Extract and save each colony
    colonies_data = []

    for idx, (line_num, colony_name) in enumerate(headers):
        # Determine end line (start of next colony or end of file)
        if idx + 1 < len(headers):
            next_line = headers[idx + 1][0]
        else:
            next_line = len(lines) + 1

        # Extract section
        content, start, end, char_count = extract_colony_section(lines, line_num, next_line)
        line_count = end - start + 1

        # Create filename
        filename = sanitize_filename(colony_name)

        # Save individual colony file
        colony_file = os.path.join(output_dir, filename)
        with open(colony_file, 'w', encoding='utf-8') as f:
            f.write(content)

        # Record metadata
        colony_info = {
            "colony_name": colony_name,
            "year": year,
            "start_line": start,
            "end_line": end,
            "char_count": char_count,
            "line_count": line_count,
            "filename": filename
        }
        colonies_data.append(colony_info)

        print(f"  {idx+1:2d}. {colony_name:40s} (lines {start:5d}-{end:5d}, {line_count:4d} lines, {char_count:6d} chars)")

    # Create summary JSON
    summary = {
        "year": year,
        "source_file": f"historical_document_pipeline/processed_pdfs/colonial-office-list-{year}/olmocr_results.md",
        "total_colonies": len(colonies_data),
        "colonies": colonies_data,
        "processing_notes": {
            "parser": "Python automated batch parser",
            "date": "2025-11-12",
            "method": "Contextual header detection with colony indicators"
        }
    }

    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)

    print(f"\nSaved {len(colonies_data)} colonies to {output_dir}/")
    print(f"Saved summary to {output_json}")

    return summary

def main():
    base_dir = "/home/user/colonial_office_list"
    years = [1905, 1906, 1907, 1908, 1909, 1910, 1911, 1912, 1913, 1914, 1915]

    results = []

    for year in years:
        try:
            summary = process_year(year, base_dir)
            results.append(summary)
        except Exception as e:
            print(f"ERROR processing {year}: {e}")
            import traceback
            traceback.print_exc()

    # Print summary
    print("\n" + "="*60)
    print("BATCH PROCESSING SUMMARY")
    print("="*60)
    for result in results:
        print(f"{result['year']}: {result['total_colonies']:2d} colonies")

    return results

if __name__ == '__main__':
    main()
