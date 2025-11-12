#!/usr/bin/env python3
"""
Final batch parser for Colonial Office Lists 1905-1915
Uses structural markers to identify the colonies section
"""

import os
import re
import json
from pathlib import Path
from typing import List, Dict, Tuple, Optional

# Markers that indicate the start of colonies section
COLONY_SECTION_MARKERS = [
    'AUSTRALIA',
    'BAHAMAS',
    'THE COMMONWEALTH',
]

# Patterns that indicate we're past the colonies section (appendices)
APPENDIX_PATTERNS = [
    r'^APPENDIX',
    r'^PART III',
    r'^PART IV',
    r'^PART V',
    r'^SERVICES OF COLONIAL OFFICERS',
    r'^HONOURS GRANTED FOR COLONIAL SERVICES',
    r'^COLONIAL REGULATIONS',
]

# Known non-colony headers (administrative/front matter)
NON_COLONY_HEADERS = {
    'CONTENTS', 'PREFACE', 'THE COLONIAL OFFICE', 'COLONIAL OFFICE LIST',
    'ESTABLISHMENTS IN THE COLONIES', 'CROWN AGENTS FOR THE COLONIES',
    'EXCHEQUER AND AUDIT DEPARTMENT', 'COLONIAL AUDIT BRANCH',
    'ESTABLISHMENT', 'DISTRIBUTION OF BUSINESS', 'TRUSTEESHIPS',
    'EMIGRATION', 'ROYAL BOTANIC GARDENS', 'KEW GARDENS', 'INTRODUCTION',
    'COLONIAL GOVERNMENT EMIGRATION AGENCIES', 'COLONIAL GOVERNMENT EMIGRATION AGENCIES AT CALCUTTA',
    'AGENCY FOR BRITISH GUIANA AND NATAL', 'GENERAL',
    'WEST AFRICAN FRONTIER FORCE', 'ACCOUNTS',
    'THE ESTABLISHMENT OF THE COLONIAL OFFICE',
    'NORTH AMERICAN AND AUSTRALASIAN', 'WEST INDIAN', 'EASTERN',
    'LEGAL ADVISERS', 'THE CROWN AGENTS FOR THE COLONIES',
    'CROWN COLONIES DIVISION', "KING'S AFRICAN RIFLES",
    'THE IMPERIAL INSTITUTE OF THE UNITED KINGDOM, THE COLONIES, AND INDIA',
    'THE IMPERIAL INSTITUTE OF THE UNITED KINGDOM',
    'TROPICAL DISEASES BUREAU', 'IMPERIAL BUREAU OF ENTOMOLOGY',
    'COLONIAL VETERINARY COMMITTEE', 'COLONIAL SURVEY COMMITTEE',
    'THE CEYLON ASSOCIATION IN LONDON', 'THE STRAITS SETTLEMENTS ASSOCIATION',
    'MEMBERS OF THE IMPERIAL CONFERENCE', 'ROYAL BOTANIC GARDENS, KEW',
    'AGENCY FOR TRINIDAD, JAMAICA, MAURITIUS AND FIJI',
    'AGENCY FOR TRINIDAD, JAMAICA AND FIJI',
    'SURGEON-SUPERINTENDENTS OF EMIGRANT VESSELS',
    'MINERAL SURVEYORS IN THE COLONIES AND PROTECTORATES',
    'THE COLONIES, AND INDIA', 'COLONIAL AND INDIAN COLLECTIONS',
}

def find_colony_section_start(lines: List[str]) -> int:
    """Find the line where the actual colonies section starts."""
    for i, line in enumerate(lines, 1):
        line_stripped = line.strip().rstrip('.')
        if line_stripped in COLONY_SECTION_MARKERS:
            return i
    # If no marker found, assume around line 2500
    return 2500

def find_colony_section_end(lines: List[str], start_line: int) -> int:
    """Find the line where the colonies section ends (appendices start)."""
    for i in range(start_line, len(lines) + 1):
        if i >= len(lines):
            return len(lines)
        line_stripped = lines[i-1].strip()
        if any(re.match(pattern, line_stripped, re.I) for pattern in APPENDIX_PATTERNS):
            return i
    return len(lines)

def find_colony_headers(lines: List[str], start_line: int, end_line: int) -> List[Tuple[int, str]]:
    """
    Find all colony headers between start and end lines.
    Returns list of (line_number, colony_name) tuples.
    """
    headers = []

    for i in range(start_line, end_line + 1):
        if i > len(lines):
            break

        line = lines[i-1]
        line_stripped = line.strip()

        # Look for all-caps headers ending with period
        if re.match(r'^[A-Z][A-Z\s\'\-&(),]+\.$', line_stripped):
            clean_name = line_stripped.rstrip('.')

            # Skip very short headers
            if len(clean_name) < 4:
                continue

            # Skip known non-colony headers
            if clean_name in NON_COLONY_HEADERS:
                continue

            # Skip headers with administrative keywords
            skip_keywords = [
                'OFFICE', 'DEPARTMENT', 'BRANCH', 'AGENTS',
                'ESTABLISHMENT', 'COMMITTEE', 'BUREAU', 'DIVISION',
                'ASSOCIATION', 'CONFERENCE', 'INSTITUTE', 'AGENCY',
                'SURGEON', 'SURVEYOR', 'ADVISER',
            ]
            if any(keyword in clean_name for keyword in skip_keywords):
                continue

            # Skip obvious advertisement/commercial headers
            if any(word in clean_name for word in ['BANK', 'COMPANY', 'LIMITED', 'LTD', 'CO.']):
                continue

            # This looks like a potential colony
            headers.append((i, clean_name))

    return headers

def filter_substantial_colonies(headers: List[Tuple[int, str]], lines: List[str], min_lines: int = 50) -> List[Tuple[int, str]]:
    """
    Filter to keep only substantial sections (likely real colonies).
    """
    substantial = []

    for idx, (line_num, header) in enumerate(headers):
        # Determine where this section ends
        if idx + 1 < len(headers):
            next_line = headers[idx + 1][0]
        else:
            next_line = len(lines) + 1

        section_length = next_line - line_num

        # Keep if it's substantial (at least min_lines)
        if section_length >= min_lines:
            substantial.append((line_num, header))

    return substantial

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
    filename = colony_name.replace(' ', '_')
    filename = filename.replace("'", '')
    filename = filename.replace('-', '_')
    filename = filename.replace('(', '')
    filename = filename.replace(')', '')
    filename = filename.replace(',', '')
    filename = filename.replace('&', 'AND')
    filename = filename.replace('.', '')
    return filename + '.md'

def process_year(year: int, base_dir: str) -> Dict:
    """
    Process a single year's Colonial Office List.
    """
    print(f"\n{'='*70}")
    print(f"Processing {year} Colonial Office List")
    print(f"{'='*70}")

    # Paths
    input_file = f"{base_dir}/historical_document_pipeline/processed_pdfs/colonial-office-list-{year}/olmocr_results.md"
    output_dir = f"{base_dir}/output/{year}_manual_parsed"
    output_json = f"{base_dir}/output/{year}_manual_parsed.json"

    # Read input file
    print(f"Reading {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    print(f"Total lines: {len(lines):,}")

    # Find colonies section boundaries
    colony_start = find_colony_section_start(lines)
    colony_end = find_colony_section_end(lines, colony_start)
    print(f"Colonies section: lines {colony_start:,} to {colony_end:,}")

    # Find all potential headers in colonies section
    print("Finding colony headers...")
    all_headers = find_colony_headers(lines, colony_start, colony_end)
    print(f"Found {len(all_headers)} potential headers")

    # Filter to substantial sections only
    print("Filtering to substantial colonies...")
    colony_headers = filter_substantial_colonies(all_headers, lines, min_lines=50)
    print(f"Identified {len(colony_headers)} substantial colony sections")

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Extract and save each colony
    colonies_data = []

    for idx, (line_num, colony_name) in enumerate(colony_headers):
        # Determine end line (start of next colony or end of colonies section)
        if idx + 1 < len(colony_headers):
            next_line = colony_headers[idx + 1][0]
        else:
            next_line = colony_end

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

        print(f"  {idx+1:2d}. {colony_name:50s} (lines {start:6d}-{end:6d}, {line_count:5d} lines)")

    # Create summary JSON
    summary = {
        "year": year,
        "source_file": f"historical_document_pipeline/processed_pdfs/colonial-office-list-{year}/olmocr_results.md",
        "total_colonies": len(colonies_data),
        "colonies": colonies_data,
        "processing_notes": {
            "parser": "Python automated batch parser v3",
            "date": "2025-11-12",
            "method": "Structural boundary detection with content size filtering",
            "colony_section_start": colony_start,
            "colony_section_end": colony_end
        }
    }

    with open(output_json, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)

    print(f"\n✓ Saved {len(colonies_data)} colonies to {output_dir}/")
    print(f"✓ Saved summary to {output_json}")

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
    print("\n" + "="*70)
    print("BATCH PROCESSING SUMMARY - 1905-1915")
    print("="*70)
    total_colonies = 0
    for result in results:
        count = result['total_colonies']
        total_colonies += count
        print(f"{result['year']}: {count:3d} colonies")
    print(f"{'='*70}")
    print(f"TOTAL: {total_colonies} colonies across 11 years")

    return results

if __name__ == '__main__':
    main()
