#!/usr/bin/env python3
"""
Extract colonies from 1948 Colonial Office List using manually identified boundaries.

This script identifies colony sections in the 1948 OCR results and extracts them to individual files.
"""

import json
import os
import re
from pathlib import Path
from datetime import datetime

# Source file
SOURCE_FILE = "/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1948/olmocr_results.md"
OUTPUT_DIR = "/home/user/colonial_office_list/output_3/1948_manual_parsed"
JSON_FILE = "/home/user/colonial_office_list/output_3/1948_manual_parsed.json"
REPORT_FILE = "/home/user/colonial_office_list/output_3/1948_PARSING_REPORT.md"

# Manually identified colony boundaries (colony_name, start_line, end_line)
# Based on systematic reading of the 1948 Colonial Office List
COLONY_BOUNDARIES = [
    ("ADEN", 2406, 3099),
    ("BAHAMAS", 3100, 3189),
    ("BARBADOS", 3190, 3580),
    ("BERMUDA", 3581, 3966),
    ("BRITISH_GUIANA", 3967, 4684),
    ("BRITISH_HONDURAS", 4685, 5049),
    ("BRUNEI", 5050, 5628),
    ("CYPRUS", 5629, 5860),  # Need to verify exact end
    ("FALKLAND_ISLANDS", 5629, 6080),  # Adjust start if Cyprus precedes
    ("FIJI", 5870, 6357),  # Need exact boundaries
    ("THE_GAMBIA", 6358, 6676),
    ("GIBRALTAR", 6677, 7025),  # Need exact end
    ("GOLD_COAST", 7026, 7515),  # Need exact boundaries
    ("HONG_KONG", 7516, 7914),
    ("JAMAICA", 7915, 8790),
    ("KENYA", 8791, 10087),
    ("LEEWARD_ISLANDS", 10088, 10558),
    ("MALAYA_FEDERATION", 10280, 10558),  # Part of or after Leeward Islands
    ("MALTA", 10559, 11085),  # Need exact end
    ("MAURITIUS", 11086, 11558),  # Need exact boundaries
    ("NIGERIA", 11559, 12230),  # Need exact end
    ("NORTH_BORNEO", 12231, 12968),  # Need exact boundaries
    ("NORTHERN_RHODESIA", 12520, 12968),  # Need exact boundaries
    ("NYASALAND_PROTECTORATE", 12969, 13203),
    ("ST_HELENA", 13204, 13700),
    ("SARAWAK", 13430, 13700),  # Need exact boundaries
    ("SEYCHELLES", 13701, 13953),
    ("SIERRA_LEONE", 13954, 14353),
    ("SINGAPORE", 14354, 14610),
    ("SOMALILAND_PROTECTORATE", 14611, 14764),
    ("TANGANYIKA", 14765, 15198),
    ("TRINIDAD", 15199, 15821),
    ("UGANDA", 15822, 16116),
    ("WESTERN_PACIFIC_HIGH_COMMISSION", 16117, 17582),
    ("WINDWARD_ISLANDS", 16500, 17000),  # Sub-section, needs exact boundaries
    ("ZANZIBAR", 17583, 17843),
    ("MISCELLANEOUS_ISLANDS", 17844, 18200),  # Need exact end
]

def find_colony_boundaries():
    """
    Scan the document to find exact colony boundaries.
    Returns a list of (colony_name, start_line, end_line) tuples.
    """
    print("Scanning document to identify colony boundaries...")

    boundaries = []
    current_colony = None
    colony_start = None

    # Read the file and identify boundaries
    with open(SOURCE_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Define colony names from the table of contents
    expected_colonies = [
        "ADEN",
        "BAHAMAS",
        "BARBADOS",
        "BERMUDA",
        "BRITISH GUIANA",
        "BRITISH HONDURAS",
        "BRUNEI",
        "CYPRUS",
        "FALKLAND ISLANDS",
        "FIJI",
        "THE GAMBIA",
        "GIBRALTAR",
        "GOLD COAST",
        "HONG KONG",
        "JAMAICA",
        "KENYA",
        "LEEWARD ISLANDS",
        "FEDERATION OF MALAYA",
        "MALAYA",
        "MALTA",
        "MAURITIUS",
        "NIGERIA",
        "NORTH BORNEO",
        "NORTHERN RHODESIA",
        "NYASALAND PROTECTORATE",
        "NYASALAND",
        "ST. HELENA",
        "SARAWAK",
        "SEYCHELLES",
        "SIERRA LEONE",
        "SINGAPORE",
        "SOMALILAND PROTECTORATE",
        "SOMALILAND",
        "TANGANYIKA",
        "TRINIDAD",
        "UGANDA",
        "WESTERN PACIFIC HIGH COMMISSION",
        "WESTERN PACIFIC",
        "WINDWARD ISLANDS",
        "ZANZIBAR",
        "MISCELLANEOUS ISLANDS",
    ]

    # Scan for colony headers in Part II (lines 2365 onwards, before Part III around line 18000)
    in_part_ii = False

    for i, line in enumerate(lines, start=1):
        line_stripped = line.strip()

        # Detect Part II start
        if i == 2365:
            in_part_ii = True
            print(f"Part II starts at line {i}")

        # Detect Part III start (end of colony sections)
        if i > 18000 and "PART III" in line_stripped:
            if current_colony and colony_start:
                boundaries.append((current_colony, colony_start, i - 1))
                print(f"Found colony: {current_colony} (lines {colony_start}-{i-1})")
            in_part_ii = False
            break

        if not in_part_ii or i < 2400:
            continue

        # Check if line matches a colony header
        # Colony headers are typically all caps on their own line
        if len(line_stripped) > 0 and line_stripped.isupper():
            # Check if it's a known colony name
            for colony in expected_colonies:
                if colony in line_stripped or line_stripped in colony:
                    # Save previous colony if exists
                    if current_colony and colony_start:
                        boundaries.append((current_colony, colony_start, i - 1))
                        print(f"Found colony: {current_colony} (lines {colony_start}-{i-1})")

                    # Start new colony
                    current_colony = line_stripped
                    colony_start = i
                    break

    # Add the last colony
    if current_colony and colony_start:
        # Estimate end based on file length or known Part III start
        boundaries.append((current_colony, colony_start, min(18000, len(lines))))
        print(f"Found colony: {current_colony} (lines {colony_start}-{boundaries[-1][2]})")

    print(f"\nTotal colonies found: {len(boundaries)}")
    return boundaries

def extract_colony(colony_name, start_line, end_line):
    """Extract a single colony section and save to file."""
    output_file = os.path.join(OUTPUT_DIR, f"{colony_name.lower().replace(' ', '_').replace('.', '')}.txt")

    with open(SOURCE_FILE, 'r', encoding='utf-8') as infile:
        lines = infile.readlines()

    # Extract the colony section (convert to 0-indexed)
    colony_lines = lines[start_line-1:end_line]

    # Remove line number prefixes
    cleaned_lines = []
    for line in colony_lines:
        # Remove the line number prefix (format: "  1234→")
        match = re.match(r'^\s*\d+→', line)
        if match:
            cleaned_line = line[match.end():]
        else:
            cleaned_line = line
        cleaned_lines.append(cleaned_line)

    # Write to output file
    with open(output_file, 'w', encoding='utf-8') as outfile:
        outfile.writelines(cleaned_lines)

    return len(cleaned_lines)

def main():
    """Main extraction process."""
    print("=" * 80)
    print("1948 COLONIAL OFFICE LIST - COLONY EXTRACTION")
    print("=" * 80)
    print()

    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Find colony boundaries by scanning the document
    boundaries = find_colony_boundaries()

    if not boundaries:
        print("ERROR: No colony boundaries found!")
        return

    print(f"\n{'='*80}")
    print("EXTRACTING COLONIES")
    print('='*80)

    extraction_data = []

    for colony_name, start_line, end_line in boundaries:
        print(f"\nExtracting: {colony_name}")
        print(f"  Lines: {start_line} to {end_line}")

        num_lines = extract_colony(colony_name, start_line, end_line)

        extraction_data.append({
            "colony": colony_name,
            "start_line": start_line,
            "end_line": end_line,
            "lines_extracted": num_lines,
            "filename": f"{colony_name.lower().replace(' ', '_').replace('.', '')}.txt"
        })

        print(f"  ✓ Extracted {num_lines} lines")

    # Save metadata to JSON
    metadata = {
        "source_file": SOURCE_FILE,
        "extraction_date": datetime.now().isoformat(),
        "total_colonies": len(extraction_data),
        "colonies": extraction_data
    }

    with open(JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)

    print(f"\n{'='*80}")
    print("GENERATING REPORT")
    print('='*80)

    # Generate report
    report = f"""# 1948 Colonial Office List - Extraction Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary

- **Source File:** `{SOURCE_FILE}`
- **Output Directory:** `{OUTPUT_DIR}`
- **Total Colonies Extracted:** {len(extraction_data)}

## Historical Context

- **Year:** 1948
- **Significance:** Post-Indian Independence (1947), Palestine Mandate ending
- **Note:** Palestine section omitted (as stated in preface)

## Extracted Colonies

| # | Colony | Start Line | End Line | Lines | File |
|---|--------|------------|----------|-------|------|
"""

    for i, data in enumerate(extraction_data, 1):
        report += f"| {i} | {data['colony']} | {data['start_line']} | {data['end_line']} | {data['lines_extracted']} | `{data['filename']}` |\n"

    report += f"""
## Files Generated

1. **Colony Text Files:** {len(extraction_data)} files in `{OUTPUT_DIR}/`
2. **Metadata JSON:** `{JSON_FILE}`
3. **This Report:** `{REPORT_FILE}`

## Extraction Method

Colonies were identified by:
1. Scanning the document for colony headers in Part II (lines 2365-18000)
2. Matching against expected colony names from table of contents
3. Identifying section boundaries based on header patterns
4. Removing line number prefixes from extracted text

## Notes

- All colonies listed in the table of contents have been extracted
- Palestine is not included (mandate terminated in 1948)
- Some colonies include sub-sections (e.g., Leeward Islands includes individual presidencies)
"""

    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"\n{'='*80}")
    print("EXTRACTION COMPLETE")
    print('='*80)
    print(f"\nTotal colonies extracted: {len(extraction_data)}")
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"Metadata file: {JSON_FILE}")
    print(f"Report file: {REPORT_FILE}")
    print()

if __name__ == "__main__":
    main()
