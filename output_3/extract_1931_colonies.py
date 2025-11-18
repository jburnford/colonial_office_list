#!/usr/bin/env python3
"""
1931 Colonial Office List - Manual Colony Extraction
Extracts all colonies from PART II-C based on manual boundary identification
"""

import json
import re
import os
from datetime import datetime

# Source file
OCR_FILE = "/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1931/olmocr_results.md"
OUTPUT_DIR = "/home/user/colonial_office_list/output_3/1931_manual_parsed"
JSON_OUTPUT = "/home/user/colonial_office_list/output_3/1931_manual_parsed.json"
REPORT_OUTPUT = "/home/user/colonial_office_list/output_3/1931_PARSING_REPORT.md"

# Manually identified colony boundaries (PART II-C: Colonial Office colonies)
# Based on systematic manual review of the OCR file
COLONIES = [
    {"name": "BAHAMAS", "start": 25066, "note": ""},
    {"name": "BARBADOS", "start": 25432, "note": ""},
    {"name": "BERMUDA", "start": 26089, "note": ""},
    {"name": "BRITISH GUIANA", "start": 26541, "note": ""},
    {"name": "BRITISH HONDURAS", "start": 27354, "note": ""},
    {"name": "CEYLON", "start": 27995, "note": ""},
    {"name": "FALKLAND ISLANDS", "start": 30021, "note": ""},
    {"name": "FIJI", "start": 30389, "note": ""},
    {"name": "THE GAMBIA", "start": 31217, "note": ""},
    {"name": "GIBRALTAR", "start": 31636, "note": ""},
    {"name": "THE GOLD COAST", "start": 31840, "note": "Includes Ashanti subsection"},
    {"name": "HONG KONG", "start": 33199, "note": ""},
    {"name": "JAMAICA", "start": 34115, "note": "Includes Cayman Islands and Turks and Caicos"},
    {"name": "KENYA", "start": 35725, "note": ""},
    {"name": "THE LEEWARD ISLANDS", "start": 36326, "note": "Includes Antigua, Barbuda, St. Christopher-Nevis, Dominica, Montserrat, Virgin Islands"},
    {"name": "MALTA", "start": 38102, "note": ""},
    {"name": "MAURITIUS", "start": 38846, "note": "Includes Rodrigues"},
    {"name": "NIGERIA", "start": 39586, "note": ""},
    {"name": "NORTHERN RHODESIA", "start": 40847, "note": ""},
    {"name": "NYASALAND PROTECTORATE", "start": 41603, "note": ""},
    {"name": "PALESTINE", "start": 41941, "note": ""},
    {"name": "ST. HELENA", "start": 42559, "note": "Includes Ascension"},
    {"name": "SEYCHELLES", "start": 42770, "note": ""},
    {"name": "SIERRA LEONE", "start": 43018, "note": ""},
    {"name": "STRAITS SETTLEMENTS", "start": 43922, "note": "Includes Singapore, Malacca, Penang, Labuan"},
    {"name": "UNFEDERATED MALAY STATES", "start": 46575, "note": "Includes Johore, Kedah, Kelantan, Trengganu, Perlis"},
    {"name": "TRINIDAD AND TOBAGO", "start": 48352, "note": "Includes Tobago subsection"},
    {"name": "UGANDA", "start": 49406, "note": ""},
    {"name": "TONGA", "start": 50461, "note": ""},
    {"name": "THE WINDWARD ISLANDS", "start": 50590, "note": "Includes Grenada, St. Lucia, St. Vincent"},
    {"name": "ZANZIBAR", "start": 51416, "note": ""},
    {"name": "IRAQ", "start": 51706, "note": ""},
    {"name": "NORTH BORNEO", "start": 51901, "note": ""},
    {"name": "SARAWAK", "start": 52111, "note": ""},
    {"name": "TRANS-JORDAN", "start": 52432, "note": ""},
    {"name": "ADEN", "start": 52513, "note": ""},
]

# PART III starts at line 52580, so all colonies end before this
PART_III_START = 52580

def clean_line_numbers(text):
    """Remove line number prefixes (e.g., '12345→') from text"""
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        # Remove line numbers in format "12345→"
        cleaned = re.sub(r'^\s*\d+→', '', line)
        cleaned_lines.append(cleaned)
    return '\n'.join(cleaned_lines)

def extract_colonies():
    """Extract all colonies to individual files"""

    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Sort colonies by start line
    sorted_colonies = sorted(COLONIES, key=lambda x: x['start'])

    # Read entire file
    with open(OCR_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Extract each colony
    extraction_data = []

    for i, colony in enumerate(sorted_colonies):
        start_line = colony['start']

        # Determine end line (start of next colony, or PART III)
        if i < len(sorted_colonies) - 1:
            end_line = sorted_colonies[i + 1]['start'] - 1
        else:
            end_line = PART_III_START - 1

        # Extract lines for this colony
        colony_lines = lines[start_line - 1:end_line]  # -1 because list is 0-indexed
        colony_text = ''.join(colony_lines)

        # Clean line numbers
        colony_text_clean = clean_line_numbers(colony_text)

        # Create safe filename
        filename = colony['name'].replace(' ', '_').replace('/', '_').upper()
        filename = re.sub(r'[^A-Z0-9_]', '', filename)
        filepath = os.path.join(OUTPUT_DIR, f"{filename}.txt")

        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(colony_text_clean)

        line_count = end_line - start_line + 1

        extraction_data.append({
            "colony_name": colony['name'],
            "start_line": start_line,
            "end_line": end_line,
            "line_count": line_count,
            "file": filepath,
            "note": colony['note'] if colony['note'] else None
        })

        print(f"Extracted: {colony['name']:45s} (lines {start_line:5d}-{end_line:5d}, {line_count:4d} lines)")

    return extraction_data

def save_metadata(extraction_data):
    """Save extraction metadata to JSON"""
    metadata = {
        "year": 1931,
        "source_file": "historical_document_pipeline/processed_pdfs/colonial-office-list-1931/olmocr_results.md",
        "extraction_date": datetime.now().strftime("%Y-%m-%d"),
        "extraction_method": "Manual LLM boundary identification with systematic document review",
        "total_colonies": len(extraction_data),
        "notes": [
            "All colony boundaries manually identified by reading OCR content",
            "Extraction covers PART II-C: Colonial Office colonies only",
            "PART II-B (Dominions) colonies not included",
            "Line number prefixes removed from extracted text",
            "PART II-C starts at line 25064, PART III starts at line 52580",
            "Some colonies include subsections (e.g., Gold Coast includes Ashanti)",
            "Leeward Islands and Windward Islands are groupings with sub-colonies",
            "Straits Settlements includes Singapore, Malacca, Penang, and Labuan"
        ],
        "colonies": extraction_data
    }

    with open(JSON_OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print(f"\nMetadata saved to: {JSON_OUTPUT}")

def generate_report(extraction_data):
    """Generate extraction report"""
    report = f"""# 1931 Colonial Office List - Extraction Report

**Extraction Date:** {datetime.now().strftime("%Y-%m-%d")}
**Source File:** historical_document_pipeline/processed_pdfs/colonial-office-list-1931/olmocr_results.md
**Total Colonies Extracted:** {len(extraction_data)}

## Methodology

All colony boundaries were manually identified by:
1. Locating PART II-C header (line 25064)
2. Identifying PART III start (line 52580)
3. Systematically reading through the section to find all colony headers
4. Cross-referencing with 1928 and 1930 lists to ensure completeness
5. Handling OCR errors and variations in colony name formatting
6. Identifying subsections and island groupings

## Extraction Summary

Extracted {len(extraction_data)} main colonies/territories from PART II-C (Colonial Office territories):

"""

    for colony in extraction_data:
        report += f"- **{colony['colony_name']}** (lines {colony['start_line']}-{colony['end_line']}, {colony['line_count']} lines)\n"
        if colony.get('note'):
            report += f"  - Note: {colony['note']}\n"

    report += f"""

## Notes

- PART II-C covers colonies administered by the Colonial Office
- PART II-B (Dominions) contains territories under Dominions Office - NOT extracted
- Some colony headers may have OCR errors
- Line number prefixes (format: '12345→') were removed from extracted text
- Island groupings include:
  - **Leeward Islands**: Antigua, Barbuda, St. Christopher-Nevis, Dominica, Montserrat, Virgin Islands
  - **Windward Islands**: Grenada, St. Lucia, St. Vincent
  - **Straits Settlements**: Singapore, Malacca, Penang, Labuan
- Some colonies include administrative subsections (e.g., Gold Coast includes Ashanti)

## Output Files

- Individual colony files: `output_3/1931_manual_parsed/[COLONY_NAME].txt`
- Metadata JSON: `output_3/1931_manual_parsed.json`
- This report: `output_3/1931_PARSING_REPORT.md`

## Comparison with Other Years

- 1928: 40 colonies extracted
- 1931: {len(extraction_data)} colonies extracted

The count includes main administrative units and may differ from other years due to administrative reorganization.
"""

    with open(REPORT_OUTPUT, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"Report saved to: {REPORT_OUTPUT}")

def main():
    print("="*80)
    print("1931 Colonial Office List - Manual Colony Extraction")
    print("="*80)
    print()

    # Extract colonies
    extraction_data = extract_colonies()

    # Save metadata
    save_metadata(extraction_data)

    # Generate report
    generate_report(extraction_data)

    print()
    print("="*80)
    print(f"✓ Extraction complete: {len(extraction_data)} colonies extracted")
    print("="*80)

if __name__ == "__main__":
    main()
