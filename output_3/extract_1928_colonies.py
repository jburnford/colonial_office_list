#!/usr/bin/env python3
"""
1928 Colonial Office List - Manual Colony Extraction
Extracts all colonies from PART II-C based on manual boundary identification
"""

import json
import re
import os
from datetime import datetime

# Source file
OCR_FILE = "/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1928/olmocr_results.md"
OUTPUT_DIR = "/home/user/colonial_office_list/output_3/1928_manual_parsed"
JSON_OUTPUT = "/home/user/colonial_office_list/output_3/1928_manual_parsed.json"
REPORT_OUTPUT = "/home/user/colonial_office_list/output_3/1928_PARSING_REPORT.md"

# Manually identified colony boundaries (PART II-C: Colonial Office colonies)
# Based on systematic manual review of the OCR file
COLONIES = [
    {"name": "BAHAMAS", "start": 26393, "note": ""},
    {"name": "BARBADOS", "start": 26768, "note": "OCR shows 'BarBADOS.*'"},
    {"name": "BERMUDA", "start": 27672, "note": ""},
    {"name": "BRITISH GUIANA", "start": 28085, "note": ""},
    {"name": "BRITISH HONDURAS", "start": 29313, "note": ""},
    {"name": "CEYLON", "start": 29909, "note": ""},
    {"name": "FALKLAND ISLANDS", "start": 32308, "note": ""},
    {"name": "FIJI", "start": 32586, "note": ""},
    {"name": "THE GAMBIA", "start": 33363, "note": ""},
    {"name": "GIBRALTAR", "start": 34105, "note": ""},
    {"name": "THE GOLD COAST", "start": 34545, "note": "Full name: THE GOLD COAST COLONY"},
    {"name": "HONG KONG", "start": 35902, "note": ""},
    {"name": "JAMAICA", "start": 36585, "note": "OCR shows '*JAMAICA.'"},
    {"name": "CAYMAN ISLANDS", "start": 37493, "note": ""},
    {"name": "TURKS AND CAICOS ISLANDS", "start": 37542, "note": ""},
    {"name": "KENYA", "start": 37731, "note": "Full name: KENYA COLONY AND PROTECTORATE"},
    {"name": "THE LEEWARD ISLANDS", "start": 38583, "note": "OCR shows '*THE LEEWARD ISLANDS.*'"},
    {"name": "MAURITIUS", "start": 41266, "note": ""},
    {"name": "NIGERIA", "start": 42031, "note": ""},
    {"name": "NORTHERN RHODESIA", "start": 43408, "note": ""},
    {"name": "NYASALAND PROTECTORATE", "start": 43864, "note": "OCR shows 'NYASALAND PROTECTORATE.†'"},
    {"name": "PALESTINE", "start": 44239, "note": ""},
    {"name": "ST. HELENA", "start": 44802, "note": ""},
    {"name": "ASCENSION", "start": 45014, "note": ""},
    {"name": "SEYCHELLES", "start": 45032, "note": ""},
    {"name": "SIERRA LEONE", "start": 45273, "note": ""},
    {"name": "STRAITS SETTLEMENTS", "start": 45999, "note": ""},
    {"name": "TRINIDAD AND TOBAGO", "start": 49477, "note": "Includes TRINIDAD (49479) and TOBAGO subsections"},
    {"name": "UGANDA", "start": 50624, "note": ""},
    {"name": "WEIHAIWEI", "start": 51103, "note": ""},
    {"name": "GRENADA", "start": 52679, "note": ""},
    {"name": "ST. LUCIA", "start": 52053, "note": ""},
    {"name": "ST. VINCENT", "start": 52387, "note": ""},
    {"name": "ZANZIBAR", "start": 53555, "note": ""},
    {"name": "NORTH BORNEO", "start": 53999, "note": ""},
    {"name": "IRAQ", "start": 53828, "note": ""},
    {"name": "TRANS-JORDAN", "start": 54580, "note": ""},
    {"name": "ADEN", "start": 54633, "note": ""},
    {"name": "TRISTAN DA CUNHA", "start": 54656, "note": ""},
    {"name": "MISCELLANEOUS ISLANDS", "start": 54671, "note": "Last colony in PART II-C"},
]

# PART III starts at line 54680, so all colonies end before this
PART_III_START = 54680

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

        print(f"Extracted: {colony['name']:35s} (lines {start_line:5d}-{end_line:5d}, {line_count:4d} lines)")

    return extraction_data

def save_metadata(extraction_data):
    """Save extraction metadata to JSON"""
    metadata = {
        "year": 1928,
        "source_file": "historical_document_pipeline/processed_pdfs/colonial-office-list-1928/olmocr_results.md",
        "extraction_date": datetime.now().strftime("%Y-%m-%d"),
        "extraction_method": "Manual LLM boundary identification with systematic document review",
        "total_colonies": len(extraction_data),
        "notes": [
            "All colony boundaries manually identified by reading OCR content",
            "Extraction covers PART II-C: Colonial Office colonies only",
            "PART II-B (Dominions) colonies not included (e.g., BASUTOLAND, SWAZILAND, SOUTHERN RHODESIA at lines 25066-25711)",
            "Line number prefixes removed from extracted text",
            "PART II-C starts at line 26391, PART III starts at line 54680",
            "Some colonies have OCR errors in headers (e.g., 'BarBADOS.*' for BARBADOS)",
            "TRINIDAD AND TOBAGO includes both TRINIDAD and TOBAGO subsections"
        ],
        "colonies": extraction_data
    }

    with open(JSON_OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print(f"\nMetadata saved to: {JSON_OUTPUT}")

def generate_report(extraction_data):
    """Generate extraction report"""
    report = f"""# 1928 Colonial Office List - Extraction Report

**Extraction Date:** {datetime.now().strftime("%Y-%m-%d")}
**Source File:** historical_document_pipeline/processed_pdfs/colonial-office-list-1928/olmocr_results.md
**Total Colonies Extracted:** {len(extraction_data)}

## Methodology

All colony boundaries were manually identified by:
1. Locating PART II-C header (line 26391)
2. Identifying PART III start (line 54680)
3. Systematically reading through the section to find all colony headers
4. Cross-referencing with 1927 list to ensure completeness
5. Handling OCR errors and variations in colony name formatting

## Extraction Summary

Extracted {len(extraction_data)} colonies from PART II-C (Colonial Office territories):

"""

    for colony in extraction_data:
        report += f"- **{colony['colony_name']}** (lines {colony['start_line']}-{colony['end_line']}, {colony['line_count']} lines)\n"
        if colony.get('note'):
            report += f"  - Note: {colony['note']}\n"

    report += f"""

## Notes

- PART II-C covers colonies administered by the Colonial Office
- PART II-B (Dominions) contains BASUTOLAND, BECHUANALAND, SWAZILAND, SOUTHERN RHODESIA (lines 25066-25711) - NOT extracted as they are High Commission Territories
- Some colony headers have OCR errors (e.g., 'BarBADOS.*' instead of 'BARBADOS')
- Line number prefixes (format: '12345→') were removed from extracted text

## Output Files

- Individual colony files: `output_3/1928_manual_parsed/[COLONY_NAME].txt`
- Metadata JSON: `output_3/1928_manual_parsed.json`
- This report: `output_3/1928_PARSING_REPORT.md`

## Comparison with 1927

1927 had 46 colonies (including Dominions Office territories).
1928 has {len(extraction_data)} colonies in PART II-C (Colonial Office only).

The decrease is due to administrative restructuring where some territories
(BASUTOLAND, SWAZILAND, SOUTHERN RHODESIA, etc.) were moved to High Commissioner/Dominions Office oversight.
"""

    with open(REPORT_OUTPUT, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"Report saved to: {REPORT_OUTPUT}")

def main():
    print("="*80)
    print("1928 Colonial Office List - Manual Colony Extraction")
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
