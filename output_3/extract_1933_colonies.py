#!/usr/bin/env python3
"""
1933 Colonial Office List - Manual Colony Extraction
Extracts all colonies from PART II-C based on manual boundary identification
"""

import json
import re
import os
from datetime import datetime

# Source file
OCR_FILE = "/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1933/olmocr_results.md"
OUTPUT_DIR = "/home/user/colonial_office_list/output_3/1933_manual_parsed"
JSON_OUTPUT = "/home/user/colonial_office_list/output_3/1933_manual_parsed.json"
REPORT_OUTPUT = "/home/user/colonial_office_list/output_3/1933_PARSING_REPORT.md"

# Manually identified colony boundaries (PART II-C: Colonial Office colonies)
# Based on systematic manual review of the OCR file
# PART II-C starts at line 23437, PART III starts at line 49061

COLONIES = [
    {"name": "BAHAMAS", "start": 23439, "note": ""},
    {"name": "BARBADOS", "start": 24018, "note": ""},
    {"name": "BERMUDA", "start": 24442, "note": ""},
    {"name": "BRITISH GUIANA", "start": 24848, "note": ""},
    {"name": "BRITISH HONDURAS", "start": 25694, "note": ""},
    {"name": "CEYLON", "start": 26177, "note": ""},
    {"name": "CYPRUS", "start": 27424, "note": ""},
    {"name": "FALKLAND ISLANDS", "start": 28193, "note": ""},
    {"name": "FIJI", "start": 28551, "note": ""},
    {"name": "THE GAMBIA", "start": 29124, "note": ""},
    {"name": "GIBRALTAR", "start": 29494, "note": ""},
    {"name": "THE GOLD COAST", "start": 29755, "note": "Includes Ashanti, Northern Territories, and Togoland subsections"},
    {"name": "HONG KONG", "start": 30863, "note": ""},
    {"name": "JAMAICA", "start": 31699, "note": "OCR shows '*JAMAICA'"},
    {"name": "CAYMAN ISLANDS", "start": 32563, "note": "Dependency of Jamaica"},
    {"name": "TURKS AND CAICOS ISLANDS", "start": 32622, "note": "Dependency of Jamaica"},
    {"name": "KENYA", "start": 32899, "note": "Full name: KENYA COLONY AND PROTECTORATE"},
    {"name": "THE LEEWARD ISLANDS", "start": 33906, "note": "OCR shows '*THE LEEWARD ISLANDS.*' - Includes Antigua, Barbuda, St. Christopher-Nevis, Dominica, Montserrat, Virgin Islands"},
    {"name": "STRAITS SETTLEMENTS", "start": 35321, "note": "Includes Singapore, Malacca, Penang, Labuan, Christmas Island"},
    {"name": "UNFEDERATED MALAY STATES", "start": 37880, "note": "Includes Johore, Kedah, Perlis, Kelantan, Trengganu"},
    {"name": "BRUNEI", "start": 38519, "note": "Protected state"},
    {"name": "MALTA", "start": 38574, "note": ""},
    {"name": "MAURITIUS", "start": 39305, "note": ""},
    {"name": "NIGERIA", "start": 40617, "note": ""},
    {"name": "NORTHERN RHODESIA", "start": 41356, "note": ""},
    {"name": "NYASALAND PROTECTORATE", "start": 41953, "note": "OCR shows 'NYASALAND PROTECTORATE.†'"},
    {"name": "PALESTINE", "start": 42336, "note": ""},
    {"name": "ST. HELENA", "start": 43094, "note": ""},
    {"name": "ASCENSION", "start": 43300, "note": "Dependency of St. Helena"},
    {"name": "SEYCHELLES", "start": 43315, "note": ""},
    {"name": "SIERRA LEONE", "start": 43596, "note": ""},
    {"name": "SOMALILAND PROTECTORATE", "start": 44039, "note": ""},
    {"name": "TANGANYIKA TERRITORY", "start": 44192, "note": "Mandate territory"},
    {"name": "TRINIDAD AND TOBAGO", "start": 44985, "note": "Includes Tobago subsection"},
    {"name": "UGANDA", "start": 46107, "note": ""},
    {"name": "WESTERN PACIFIC", "start": 46672, "note": "Includes Gilbert and Ellice Islands, British Solomon Islands, Tonga, New Hebrides, Phoenix Group, Pitcairn"},
    {"name": "THE WINDWARD ISLANDS", "start": 47163, "note": "OCR shows '**THE WINDWARD ISLANDS.**' - Includes Grenada, St. Lucia, St. Vincent"},
    {"name": "ZANZIBAR", "start": 48116, "note": ""},
    {"name": "NORTH BORNEO", "start": 48419, "note": "Under Appendix"},
    {"name": "SARAWAK", "start": 48636, "note": "Protected state under Appendix"},
    {"name": "TRANS-JORDAN", "start": 48878, "note": "OCR shows '**TRANS-JORDAN.**'"},
    {"name": "ADEN", "start": 48945, "note": ""},
    {"name": "TRISTAN DA CUNHA", "start": 49037, "note": ""},
    {"name": "MISCELLANEOUS ISLANDS", "start": 49052, "note": "Last section before PART III"},
]

# PART III starts at line 49061
PART_III_START = 49061

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
        "year": 1933,
        "source_file": "historical_document_pipeline/processed_pdfs/colonial-office-list-1933/olmocr_results.md",
        "extraction_date": datetime.now().strftime("%Y-%m-%d"),
        "extraction_method": "Manual LLM boundary identification with systematic document review",
        "total_colonies": len(extraction_data),
        "notes": [
            "All colony boundaries manually identified by reading OCR content",
            "Extraction covers PART II-C: Colonial Office colonies only",
            "PART II-B (Dominions) colonies not included",
            "Line number prefixes removed from extracted text",
            "PART II-C starts at line 23437, PART III starts at line 49061",
            "Some colonies include subsections (e.g., Gold Coast includes Ashanti)",
            "Island groupings: Leeward Islands, Windward Islands, Western Pacific",
            "Straits Settlements includes Singapore, Malacca, Penang, Labuan, Christmas Island",
            "Dependencies extracted separately: Cayman Islands, Turks and Caicos, Ascension",
            "Some colonies in Appendix: North Borneo, Sarawak"
        ],
        "colonies": extraction_data
    }

    with open(JSON_OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print(f"\nMetadata saved to: {JSON_OUTPUT}")

def generate_report(extraction_data):
    """Generate extraction report"""
    report = f"""# 1933 Colonial Office List - Extraction Report

**Extraction Date:** {datetime.now().strftime("%Y-%m-%d")}
**Source File:** historical_document_pipeline/processed_pdfs/colonial-office-list-1933/olmocr_results.md
**Total Colonies Extracted:** {len(extraction_data)}

## Methodology

All colony boundaries were manually identified by:
1. Locating PART II-C header (line 23437)
2. Identifying PART III start (line 49061)
3. Systematically reading through the section to find all colony headers
4. Cross-referencing with 1932 list (43 colonies) to ensure completeness
5. Handling OCR errors and variations in colony name formatting
6. Identifying subsections, island groupings, and dependencies

## Extraction Summary

Extracted {len(extraction_data)} colonies/territories from PART II-C (Colonial Office territories):

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
  - **Straits Settlements**: Singapore, Malacca, Penang, Labuan, Christmas Island
  - **Western Pacific**: Gilbert and Ellice Islands, British Solomon Islands, Tonga, New Hebrides, Pitcairn
- Some colonies include administrative subsections (e.g., Gold Coast includes Ashanti and Northern Territories)
- Dependencies extracted separately: Cayman Islands and Turks and Caicos Islands (Jamaica), Ascension (St. Helena)

## Output Files

- Individual colony files: `output_3/1933_manual_parsed/[COLONY_NAME].txt`
- Metadata JSON: `output_3/1933_manual_parsed.json`
- This report: `output_3/1933_PARSING_REPORT.md`

## Comparison with Other Years

- 1932: 43 colonies extracted
- 1933: {len(extraction_data)} colonies extracted

The count may differ from other years due to administrative reorganization, consolidation of island groups, and inclusion/exclusion of dependencies.
"""

    with open(REPORT_OUTPUT, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"Report saved to: {REPORT_OUTPUT}")

def main():
    print("="*80)
    print("1933 Colonial Office List - Manual Colony Extraction")
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
