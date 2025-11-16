#!/usr/bin/env python3
"""
Comprehensive fix for Colonial Office List years 1931-1940.
Automatically identifies and corrects over-extraction patterns.
"""

import json
import os
import re
from pathlib import Path
from datetime import datetime

BASE_DIR = "/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs"
INPUT_DIR = "/home/user/colonial_office_list/output"
OUTPUT_BASE = "/home/user/colonial_office_list/output_2"

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

def find_boundary_in_ocr(ocr_file, search_patterns, start_line=1, max_search=1000):
    """Find line number where any of the patterns match."""
    with open(ocr_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for i in range(start_line-1, min(start_line + max_search, len(lines))):
        line = lines[i].strip()
        for pattern in search_patterns:
            if re.match(pattern, line):
                return i + 1, line
    return None, None

def fix_year(year):
    """Fix a single year's extraction."""
    print(f"\n{'='*70}")
    print(f"FIXING YEAR {year}")
    print(f"{'='*70}")

    year_dir = YEAR_DIRS.get(year)
    ocr_file = f"{BASE_DIR}/{year_dir}/olmocr_results.md"
    original_json = f"{INPUT_DIR}/{year}_manual_parsed.json"

    if not os.path.exists(ocr_file):
        print(f"  ERROR: OCR file not found")
        return None

    # Count total OCR lines
    with open(ocr_file, 'r') as f:
        total_ocr_lines = sum(1 for _ in f)

    print(f"  OCR file: {total_ocr_lines} lines")

    # Load original extraction if exists
    if os.path.exists(original_json):
        with open(original_json, 'r') as f:
            original_data = json.load(f)
        print(f"  Original extraction: {original_data['total_colonies']} colonies")
    else:
        print(f"  No original extraction - needs manual processing")
        return None

    # Analyze and fix
    colonies = original_data['colonies']
    corrected_colonies = []
    corrections = []

    # Group Australian states
    aus_colonies = [c for c in colonies if 'AUSTRALIA' in c['colony_name'].upper()]
    non_aus_colonies = [c for c in colonies if 'AUSTRALIA' not in c['colony_name'].upper()]

    if len(aus_colonies) > 1:
        # Merge all AUSTRALIA entries
        aus_start = min(c['start_line'] for c in aus_colonies)
        aus_end = max(c['end_line'] for c in aus_colonies)

        # Find the actual end of AUSTRALIA section
        next_colony_after_aus = None
        for c in non_aus_colonies:
            if c['start_line'] > aus_start:
                if next_colony_after_aus is None or c['start_line'] < next_colony_after_aus['start_line']:
                    next_colony_after_aus = c

        if next_colony_after_aus:
            aus_end = next_colony_after_aus['start_line']

        corrected_colonies.append({
            "name": "AUSTRALIA",
            "filename": "AUSTRALIA.md",
            "start_line": aus_start,
            "end_line": aus_end,
            "line_count": aus_end - aus_start,
            "is_appendix": False,
            "extraction_method": "merged_or_manually_added"
        })
        corrections.append(f"Merged {len(aus_colonies)} AUSTRALIA subsections into 1 entry ({aus_start}-{aus_end}, {aus_end-aus_start} lines)")
        print(f"  ✓ Fixed AUSTRALIA: {len(aus_colonies)} entries → 1 entry")

    # Merge TRINIDAD and TOBAGO
    trinidad = [c for c in colonies if c['colony_name'] == 'TRINIDAD']
    tobago = [c for c in colonies if c['colony_name'] == 'TOBAGO']

    if trinidad and tobago:
        merged_start = min(trinidad[0]['start_line'], tobago[0]['start_line'])
        merged_end = max(trinidad[0]['end_line'], tobago[0]['end_line'])
        corrected_colonies.append({
            "name": "TRINIDAD AND TOBAGO",
            "filename": "TRINIDAD_AND_TOBAGO.md",
            "start_line": merged_start,
            "end_line": merged_end,
            "line_count": merged_end - merged_start,
            "is_appendix": False,
            "extraction_method": "merged_or_manually_added"
        })
        corrections.append(f"Merged TRINIDAD and TOBAGO ({trinidad[0]['line_count']} + {tobago[0]['line_count']} lines)")
        print(f"  ✓ Fixed TRINIDAD/TOBAGO: merged into 1 entry")
    elif trinidad:
        corrected_colonies.append({
            "name": "TRINIDAD",
            "filename": "TRINIDAD.md",
            "start_line": trinidad[0]['start_line'],
            "end_line": trinidad[0]['end_line'],
            "line_count": trinidad[0]['line_count'],
            "is_appendix": False,
            "extraction_method": "original_boundaries"
        })
    elif tobago:
        corrected_colonies.append({
            "name": "TOBAGO",
            "filename": "TOBAGO.md",
            "start_line": tobago[0]['start_line'],
            "end_line": tobago[0]['end_line'],
            "line_count": tobago[0]['line_count'],
            "is_appendix": False,
            "extraction_method": "original_boundaries"
        })

    # Fix ADEN over-extraction
    aden = [c for c in colonies if c['colony_name'] == 'ADEN']
    if aden and aden[0]['line_count'] > 500:
        # ADEN is severely over-extracted, find the real boundary
        aden_start = aden[0]['start_line']

        # Look for TRISTAN DA CUNHA marker
        tristan_line, tristan_text = find_boundary_in_ocr(
            ocr_file,
            [r'^TRISTAN DA CUNHA\.', r'^TRISTAN DA CUNHA'],
            aden_start,
            1000
        )

        if tristan_line:
            # ADEN ends where TRISTAN begins
            aden_end = tristan_line
            corrected_colonies.append({
                "name": "ADEN",
                "filename": "ADEN.md",
                "start_line": aden_start,
                "end_line": aden_end,
                "line_count": aden_end - aden_start,
                "is_appendix": False,
                "extraction_method": "merged_or_manually_added"
            })
            corrections.append(f"Fixed ADEN massive over-extraction: {aden[0]['line_count']} → {aden_end - aden_start} lines")
            print(f"  ✓ Fixed ADEN: {aden[0]['line_count']} lines → {aden_end - aden_start} lines")

            # Add TRISTAN DA CUNHA (likely missing)
            misc_line, misc_text = find_boundary_in_ocr(
                ocr_file,
                [r'^MISCELLANEOUS', r'^PART III'],
                tristan_line,
                500
            )

            if misc_line:
                corrected_colonies.append({
                    "name": "TRISTAN DA CUNHA",
                    "filename": "TRISTAN_DA_CUNHA.md",
                    "start_line": tristan_line,
                    "end_line": misc_line,
                    "line_count": misc_line - tristan_line,
                    "is_appendix": False,
                    "extraction_method": "merged_or_manually_added"
                })
                corrections.append(f"Added missing TRISTAN DA CUNHA ({misc_line - tristan_line} lines)")
                print(f"  ✓ Added TRISTAN DA CUNHA: {misc_line - tristan_line} lines")
        else:
            # If can't find TRISTAN, maybe it's already correct (like 1937)
            corrected_colonies.append({
                "name": "ADEN",
                "filename": "ADEN.md",
                "start_line": aden[0]['start_line'],
                "end_line": aden[0]['end_line'],
                "line_count": aden[0]['line_count'],
                "is_appendix": False,
                "extraction_method": "original_boundaries"
            })
    elif aden:
        # ADEN looks OK
        corrected_colonies.append({
            "name": "ADEN",
            "filename": "ADEN.md",
            "start_line": aden[0]['start_line'],
            "end_line": aden[0]['end_line'],
            "line_count": aden[0]['line_count'],
            "is_appendix": False,
            "extraction_method": "original_boundaries"
        })

    # Add all other colonies that weren't specially processed
    skip_names = ['AUSTRALIA', 'QUEENSLAND', 'TASMANIA', 'VICTORIA', 'SOUTH AUSTRALIA', 'WESTERN AUSTRALIA',
                  'NEW SOUTH WALES', 'COMMONWEALTH OF AUSTRALIA', 'TRINIDAD', 'TOBAGO', 'ADEN', 'TRISTAN DA CUNHA']

    for colony in colonies:
        if colony['colony_name'] not in skip_names:
            corrected_colonies.append({
                "name": colony['colony_name'],
                "filename": colony['filename'],
                "start_line": colony['start_line'],
                "end_line": colony['end_line'],
                "line_count": colony['line_count'],
                "is_appendix": colony.get('is_appendix', False),
                "extraction_method": "original_boundaries"
            })

    # Sort by start_line
    corrected_colonies.sort(key=lambda x: x['start_line'])

    # Generate metadata
    metadata = {
        "year": year,
        "total_colonies": len(corrected_colonies),
        "parsing_method": "Manual LLM-based boundary verification with automated pattern detection (output_2)",
        "remediation_date": datetime.now().strftime("%B %d, %Y"),
        "original_extraction_count": original_data['total_colonies'],
        "corrections_applied": corrections,
        "issues_found": {
            "australia_over_extraction": len(aus_colonies) > 1,
            "trinidad_tobago_split": bool(trinidad and tobago),
            "aden_over_extraction": aden and aden[0]['line_count'] > 500 if aden else False,
        },
        "colonies": corrected_colonies
    }

    # Create output directory
    output_dir = f"{OUTPUT_BASE}/{year}_manual_parsed"
    os.makedirs(output_dir, exist_ok=True)

    # Extract files
    print(f"  Extracting {len(corrected_colonies)} colonies...")
    for colony in corrected_colonies:
        content = read_lines(ocr_file, colony['start_line'], colony['end_line'])
        filepath = f"{output_dir}/{colony['filename']}"
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

    # Write metadata
    metadata_file = f"{OUTPUT_BASE}/{year}_manual_parsed.json"
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)

    print(f"  ✓ Output: {output_dir}/")
    print(f"  ✓ Metadata: {metadata_file}")
    print(f"  ✓ Corrections: {len(corrections)}")

    return {
        "year": year,
        "original_count": original_data['total_colonies'],
        "corrected_count": len(corrected_colonies),
        "corrections": corrections
    }

def main():
    print("Comprehensive fix for Colonial Office List years 1931-1937, 1939-1940")
    print(f"Starting at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    results = {}
    for year in [1931, 1932, 1933, 1934, 1936, 1937]:  # Skip 1935, 1939, 1940 for now
        result = fix_year(year)
        if result:
            results[year] = result

    print(f"\n{'='*70}")
    print("SUMMARY TABLE")
    print(f"{'='*70}")
    print(f"{'Year':<6} | {'Original→Corrected':<20} | {'Corrections'}")
    print(f"{'-'*70}")
    for year, data in sorted(results.items()):
        summary = f"{data['original_count']}→{data['corrected_count']}"
        corrections_summary = f"{len(data['corrections'])} fixes applied"
        print(f"{year:<6} | {summary:<20} | {corrections_summary}")

if __name__ == "__main__":
    main()
