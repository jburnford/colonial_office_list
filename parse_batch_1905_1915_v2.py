#!/usr/bin/env python3
"""
Improved batch parser for Colonial Office Lists 1905-1915
Uses pattern matching to identify colony sections
"""

import os
import re
import json
from pathlib import Path
from typing import List, Dict, Tuple

# Known non-colony section headers to filter out
NON_COLONY_SECTIONS = {
    'CONTENTS', 'PREFACE', 'THE COLONIAL OFFICE', 'COLONIAL OFFICE LIST',
    'ESTABLISHMENTS IN THE COLONIES', 'CROWN AGENTS FOR THE COLONIES',
    'EXCHEQUER AND AUDIT DEPARTMENT', 'COLONIAL AUDIT BRANCH',
    'ESTABLISHMENT', 'DISTRIBUTION OF BUSINESS', 'TRUSTEESHIPS',
    'EMIGRATION', 'ROYAL BOTANIC GARDENS', 'KEW GARDENS',
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
    'MEMBERS OF THE IMPERIAL CONFERENCE',
}

# Patterns that indicate we're past the colonies section (appendices/back matter)
APPENDIX_PATTERNS = [
    r'^APPENDIX',
    r'^INDEX\.$',
    r'^ADDITIONS AND CORRECTIONS',
    r'^PENSIONS',
    r'^REGULATIONS',
    r'^COLONIAL CIVIL SERVICE',
    r'^PART III',
    r'^PART IV',
    r'^PART V',
    r'^SERVICES OF COLONIAL OFFICERS',
    r'^HONOURS GRANTED FOR COLONIAL SERVICES',
]

def find_all_caps_headers(lines: List[str]) -> List[Tuple[int, str]]:
    """
    Find all potential section headers (all-caps text ending with period).
    Returns list of (line_number, header_text) tuples.
    """
    headers = []
    in_colonies_section = False

    for i, line in enumerate(lines, 1):
        line_stripped = line.strip()

        # Check if we're entering appendices/back matter
        if any(re.match(pattern, line_stripped, re.I) for pattern in APPENDIX_PATTERNS):
            # Stop looking for colonies after this point
            if in_colonies_section:
                break

        # Look for section markers
        if line_stripped in ['AUSTRALIA.', 'BAHAMAS.', 'BARBADOS.']:
            in_colonies_section = True

        # Look for all-caps headers ending with period
        if re.match(r'^[A-Z][A-Z\s\'\-&(),\.]+\.$', line_stripped):
            clean_name = line_stripped.rstrip('.')

            # Skip very short headers
            if len(clean_name) < 4:
                continue

            # Skip known non-colony headers
            if clean_name in NON_COLONY_SECTIONS:
                continue

            # Skip headers with certain keywords
            skip_keywords = ['OFFICE', 'DEPARTMENT', 'BRANCH', 'AGENTS',
                           'ESTABLISHMENT', 'COMMITTEE', 'BUREAU', 'DIVISION',
                           'ASSOCIATION', 'CONFERENCE', 'INSTITUTE']
            if any(keyword in clean_name for keyword in skip_keywords):
                # Unless it's the Imperial Institute header followed by territory content
                if clean_name not in ['THE STRAITS SETTLEMENTS ASSOCIATION']:
                    continue

            headers.append((i, clean_name))

    return headers

def filter_colony_headers(all_headers: List[Tuple[int, str]], lines: List[str]) -> List[Tuple[int, str]]:
    """
    Filter headers to keep only those that are actual colonies.
    Checks content after each header to verify it's a colony section.
    """
    colonies = []

    for idx, (line_num, header) in enumerate(all_headers):
        # Determine where this section ends
        if idx + 1 < len(all_headers):
            next_line = all_headers[idx + 1][0]
        else:
            next_line = len(lines)

        # Get content preview (next 50 lines or until next header)
        preview_end = min(line_num + 50, next_line)
        preview_lines = lines[line_num-1:preview_end]
        preview_text = ' '.join(preview_lines).lower()

        # Colony indicators - things typically found in colony sections
        colony_indicators = [
            'governor', 'colony', 'protectorate', 'commonwealth',
            'legislative', 'executive', 'chief justice', 'population',
            'revenue', 'area', 'square miles', 'climate', 'history',
            'constitution', 'exports', 'imports', 'trade', 'territory',
            'bounded', 'capital', 'administration', 'official', 'civil service'
        ]

        # Check if this looks like a colony section
        indicator_count = sum(1 for indicator in colony_indicators if indicator in preview_text)

        # Section length (in lines)
        section_lines = next_line - line_num

        # Keep if it has colony indicators and is substantial
        # OR if it's a known colony name from our patterns
        known_colonies = [
            'AUSTRALIA', 'BAHAMAS', 'BARBADOS', 'BERMUDA', 'BRITISH',
            'CANADA', 'CAPE', 'CEYLON', 'CYPRUS', 'FALKLAND', 'FIJI',
            'GAMBIA', 'GIBRALTAR', 'GOLD COAST', 'GRENADA', 'HONG KONG',
            'JAMAICA', 'LABUAN', 'LAGOS', 'LEEWARD', 'MALTA', 'MAURITIUS',
            'NATAL', 'NEWFOUNDLAND', 'NEW SOUTH WALES', 'NEW ZEALAND',
            'NIGERIA', 'QUEENSLAND', 'RHODESIA', 'SIERRA LEONE',
            'SOUTH AUSTRALIA', 'SEYCHELLES', 'ST.', 'STRAITS SETTLEMENTS',
            'TASMANIA', 'TRANSVAAL', 'TRINIDAD', 'TURKS', 'UGANDA',
            'VICTORIA', 'WESTERN AUSTRALIA', 'WEIHAIWEI', 'WINDWARD',
            'ZANZIBAR', 'ORANGE RIVER', 'NORTHERN NIGERIA', 'SOUTHERN NIGERIA',
            'PROTECTORATE', 'THE COMMONWEALTH', 'EAST AFRICA'
        ]

        is_known_colony = any(known in header for known in known_colonies)

        if (indicator_count >= 2 and section_lines >= 20) or is_known_colony:
            colonies.append((line_num, header))

    return colonies

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

    print(f"Total lines: {len(lines):,}")

    # Find all potential headers
    print("Finding all-caps headers...")
    all_headers = find_all_caps_headers(lines)
    print(f"Found {len(all_headers)} all-caps headers")

    # Filter to colony headers only
    print("Filtering to colony sections...")
    colony_headers = filter_colony_headers(all_headers, lines)
    print(f"Identified {len(colony_headers)} colony sections")

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Extract and save each colony
    colonies_data = []

    for idx, (line_num, colony_name) in enumerate(colony_headers):
        # Determine end line (start of next colony or end of file)
        if idx + 1 < len(colony_headers):
            next_line = colony_headers[idx + 1][0]
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

        print(f"  {idx+1:2d}. {colony_name:45s} (lines {start:5d}-{end:5d}, {line_count:5d} lines, {char_count:7d} chars)")

    # Create summary JSON
    summary = {
        "year": year,
        "source_file": f"historical_document_pipeline/processed_pdfs/colonial-office-list-{year}/olmocr_results.md",
        "total_colonies": len(colonies_data),
        "colonies": colonies_data,
        "processing_notes": {
            "parser": "Python automated batch parser v2",
            "date": "2025-11-12",
            "method": "All-caps header detection with content verification"
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
    total_colonies = 0
    for result in results:
        count = result['total_colonies']
        total_colonies += count
        print(f"{result['year']}: {count:2d} colonies")
    print(f"{'='*60}")
    print(f"TOTAL: {total_colonies} colonies across 11 years")

    return results

if __name__ == '__main__':
    main()
