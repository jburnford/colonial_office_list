#!/usr/bin/env python3
"""
Extract all colonies from the 1948 Colonial Office List.
Boundaries have been manually identified by reading the OCR file.
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

# Manually identified colony boundaries
# Format: (colony_name, start_line, end_line)
# These were identified by systematically reading the OCR file
COLONY_BOUNDARIES = [
    ("ADEN", 2406, 3099),
    ("BAHAMAS", 3100, 3189),
    ("BARBADOS", 3190, 3580),
    ("BERMUDA", 3581, 3966),
    ("BRITISH_GUIANA", 3967, 4684),
    ("BRITISH_HONDURAS", 4685, 5049),
    ("BRUNEI", 5050, 5628),
    ("FALKLAND_ISLANDS", 5629, 5954),
    ("FIJI", 5955, 6357),
    ("THE_GAMBIA", 6358, 6676),
    ("GIBRALTAR", 6677, 6889),
    ("GOLD_COAST", 6890, 7515),
    ("HONG_KONG", 7516, 7914),
    ("JAMAICA", 7915, 8790),
    ("KENYA", 8791, 10087),
    ("LEEWARD_ISLANDS", 10088, 10300),
    ("FEDERATION_OF_MALAYA", 10301, 10558),
    ("MALTA", 10559, 10857),
    ("MAURITIUS", 10858, 11558),
    ("NIGERIA", 11559, 12262),
    ("NORTH_BORNEO", 12263, 12487),
    ("NORTHERN_RHODESIA", 12488, 12968),
    ("NYASALAND_PROTECTORATE", 12969, 13203),
    ("ST_HELENA", 13204, 13441),
    ("SARAWAK", 13442, 13700),
    ("SEYCHELLES", 13701, 13953),
    ("SIERRA_LEONE", 13954, 14353),
    ("SINGAPORE", 14354, 14610),
    ("SOMALILAND_PROTECTORATE", 14611, 14764),
    ("TANGANYIKA", 14765, 15198),
    ("TRINIDAD", 15199, 15821),
    ("UGANDA", 15822, 16116),
    ("WESTERN_PACIFIC_HIGH_COMMISSION", 16117, 16766),
    ("WINDWARD_ISLANDS", 16767, 17582),
    ("ZANZIBAR", 17583, 17843),
    ("MISCELLANEOUS_ISLANDS", 17844, 18200),
]

def extract_colony(colony_name, start_line, end_line):
    """Extract a single colony section and save to file."""
    output_file = os.path.join(OUTPUT_DIR, f"{colony_name.lower()}.txt")

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
    print("1948 COLONIAL OFFICE LIST - MANUAL COLONY EXTRACTION")
    print("=" * 80)
    print()
    print(f"Source: {SOURCE_FILE}")
    print(f"Output: {OUTPUT_DIR}")
    print(f"Total colonies to extract: {len(COLONY_BOUNDARIES)}")
    print()

    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    extraction_data = []

    for colony_name, start_line, end_line in COLONY_BOUNDARIES:
        print(f"Extracting {colony_name:40s} (lines {start_line:5d}-{end_line:5d})...", end=" ")

        num_lines = extract_colony(colony_name, start_line, end_line)

        extraction_data.append({
            "colony": colony_name,
            "start_line": start_line,
            "end_line": end_line,
            "lines_extracted": num_lines,
            "filename": f"{colony_name.lower()}.txt"
        })

        print(f"✓ ({num_lines} lines)")

    # Save metadata to JSON
    metadata = {
        "source_file": SOURCE_FILE,
        "extraction_date": datetime.now().isoformat(),
        "year": 1948,
        "total_colonies": len(extraction_data),
        "method": "Manual boundary identification",
        "notes": [
            "Palestine excluded (mandate terminated in 1948)",
            "Post-Indian Independence (1947)",
            "Early decolonization period"
        ],
        "colonies": extraction_data
    }

    with open(JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)

    # Generate report
    report = f"""# 1948 Colonial Office List - Extraction Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Summary

- **Source File:** `{SOURCE_FILE}`
- **Output Directory:** `{OUTPUT_DIR}`
- **Total Colonies Extracted:** {len(extraction_data)}
- **Extraction Method:** Manual boundary identification

## Historical Context

- **Year:** 1948
- **Significance:**
  - Post-Indian Independence (August 1947)
  - Palestine Mandate ending (Israel founded May 1948)
  - Early decolonization period
  - Major post-war administrative changes
  - Cyprus not included as separate section in Part II

## Notes

- **Palestine:** Excluded from Part II (as stated in preface: "The Palestine Mandate having been terminated the historical and statistical account has been omitted from Part II")
- **Cyprus:** Not found as a separate entry in Part II of the 1948 edition
- The Federation of Malaya appears as a distinct entry following the Leeward Islands

## Extracted Colonies

| # | Colony | Start Line | End Line | Lines | File |
|---|--------|------------|----------|-------|------|
"""

    for i, data in enumerate(extraction_data, 1):
        report += f"| {i} | {data['colony']} | {data['start_line']} | {data['end_line']} | {data['lines_extracted']} | `{data['filename']}` |\n"

    report += f"""
## Comparison with 1946

Notable changes expected:
- Loss of India (independent 1947)
- Palestine mandate ending
- Increased focus on African and Caribbean territories
- Formation of Federation of Malaya

## Files Generated

1. **Colony Text Files:** {len(extraction_data)} files in `{OUTPUT_DIR}/`
2. **Metadata JSON:** `{JSON_FILE}`
3. **This Report:** `{REPORT_FILE}`

## Extraction Method

Colonies were extracted using manually identified boundaries by:
1. Reading the table of contents (lines 2367-2405)
2. Systematically scanning Part II for colony headers
3. Identifying boundaries by recognizing header patterns and section endings
4. Manual verification of each boundary
5. Removing line number prefixes from extracted text

## Colony List

The 1948 Colonial Office List includes 36 territories:
"""

    for i, data in enumerate(extraction_data, 1):
        report += f"{i}. {data['colony'].replace('_', ' ')}\n"

    report += "\n---\nExtraction completed successfully.\n"

    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write(report)

    print()
    print("=" * 80)
    print("EXTRACTION COMPLETE")
    print("=" * 80)
    print(f"\nTotal colonies extracted: {len(extraction_data)}")
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"Metadata file: {JSON_FILE}")
    print(f"Report file: {REPORT_FILE}")
    print()

if __name__ == "__main__":
    main()
