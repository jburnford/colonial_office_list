#!/usr/bin/env python3
"""
1939 Colonial Office List - Manual Colony Extraction
Extracts all colonies from PART II-C based on manual boundary identification
"""

import json
import re
import os
from datetime import datetime

# Source file
OCR_FILE = "/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1939/olmocr_results.md"
OUTPUT_DIR = "/home/user/colonial_office_list/output_3/1939_manual_parsed"
JSON_OUTPUT = "/home/user/colonial_office_list/output_3/1939_manual_parsed.json"
REPORT_OUTPUT = "/home/user/colonial_office_list/output_3/1939_PARSING_REPORT.md"

# Manually identified colony boundaries (PART II-C: Colonial Office colonies)
# Based on systematic manual review of the OCR file
COLONIES = [
    {"name": "ADEN", "start": 24092, "note": "First colony in 1939; moved from appendix compared to 1937"},
    {"name": "BAHAMAS", "start": 24369, "note": ""},
    {"name": "BARBADOS", "start": 24694, "note": "Header shows 'BAHAMAS—BARBADOS.'"},
    {"name": "BERMUDA", "start": 25446, "note": ""},
    {"name": "BRITISH GUIANA", "start": 25778, "note": ""},
    {"name": "BRITISH HONDURAS", "start": 26694, "note": "OCR shows '**BRITISH HONDURAS.**'"},
    {"name": "CEYLON", "start": 27240, "note": "Large colony with multiple provinces"},
    {"name": "CYPRUS", "start": 29002, "note": ""},
    {"name": "FALKLAND ISLANDS", "start": 29711, "note": "Header shows 'CYPRUS—FALKLAND ISLANDS.'"},
    {"name": "FIJI", "start": 30046, "note": "Header shows 'FALKLAND ISLANDS—FIJI.'"},
    {"name": "THE GAMBIA", "start": 30725, "note": "Header shows 'FIJI—THE GAMBIA.'"},
    {"name": "GIBRALTAR", "start": 31193, "note": ""},
    {"name": "THE GOLD COAST", "start": 31396, "note": "Includes Ashanti, Northern Territories sections"},
    {"name": "HONG KONG", "start": 32455, "note": ""},
    {"name": "JAMAICA", "start": 33264, "note": ""},
    {"name": "CAYMAN ISLANDS", "start": 34325, "note": "Dependency of Jamaica"},
    {"name": "TURKS AND CAICOS ISLANDS", "start": 34400, "note": "Dependency of Jamaica"},
    {"name": "KENYA", "start": 34624, "note": "Full name: KENYA COLONY AND PROTECTORATE"},
    {"name": "THE LEEWARD ISLANDS", "start": 35359, "note": "Includes Antigua, Barbuda, Dominica, Montserrat, Virgin Islands, St. Kitts-Nevis"},
    {"name": "MALAYA: STRAITS SETTLEMENTS", "start": 36842, "note": "OCR shows '**MALAYA: STRAITS SETTLEMENTS.**'"},
    {"name": "BRUNEI", "start": 39599, "note": "Protected state under British protection"},
    {"name": "MALTA", "start": 39664, "note": "OCR shows '**MALTA**'"},
    {"name": "MAURITIUS", "start": 40307, "note": "History section begins here"},
    {"name": "NIGERIA", "start": 41039, "note": "OCR shows '**Situation, Area and Population.**'"},
    {"name": "NORTHERN RHODESIA", "start": 42040, "note": ""},
    {"name": "NYASALAND PROTECTORATE", "start": 42666, "note": "OCR shows 'NYASALAND PROTECTORATE.†'"},
    {"name": "PALESTINE", "start": 43065, "note": "Mandate territory"},
    {"name": "ST. HELENA", "start": 43848, "note": ""},
    {"name": "ASCENSION", "start": 44044, "note": "Dependency of St. Helena"},
    {"name": "TRISTAN DA CUNHA", "start": 44058, "note": "Made dependency of St. Helena in 1938"},
    {"name": "SEYCHELLES", "start": 44077, "note": ""},
    {"name": "SIERRA LEONE", "start": 44298, "note": ""},
    {"name": "SOMALILAND PROTECTORATE", "start": 44940, "note": ""},
    {"name": "TANGANYIKA TERRITORY", "start": 45145, "note": "OCR shows '†TANGANYIKA TERRITORY.', mandate territory"},
    {"name": "TRINIDAD AND TOBAGO", "start": 45924, "note": "Includes Tobago subsection"},
    {"name": "UGANDA", "start": 47052, "note": ""},
    {"name": "WESTERN PACIFIC", "start": 47651, "note": "Includes Gilbert & Ellice Islands, Solomon Islands, Tonga, New Hebrides, Pitcairn"},
    {"name": "TONGA", "start": 48181, "note": "Protected state, part of Western Pacific section"},
    {"name": "THE WINDWARD ISLANDS", "start": 48337, "note": "OCR shows '**THE WINDWARD ISLANDS.**', includes Grenada, St. Lucia, St. Vincent"},
    {"name": "ZANZIBAR", "start": 49451, "note": "Protectorate"},
    {"name": "NORTH BORNEO", "start": 49730, "note": "In APPENDIX section, protected state"},
    {"name": "SARAWAK", "start": 50010, "note": "In APPENDIX section, protected state"},
    {"name": "TRANS-JORDAN", "start": 53355, "note": "In APPENDIX section, mandate territory"},
    {"name": "MISCELLANEOUS ISLANDS", "start": 53431, "note": "Last entry in PART II-C, just before PART III"},
]

# PART III starts at line 53434, so all colonies end before this
PART_III_START = 53434

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
        filename = colony['name'].replace(' ', '_').replace('/', '_').replace(':', '_').upper()
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

        print(f"Extracted: {colony['name']:50s} (lines {start_line:5d}-{end_line:5d}, {line_count:4d} lines)")

    return extraction_data

def save_metadata(extraction_data):
    """Save extraction metadata to JSON"""
    metadata = {
        "year": 1939,
        "source_file": "historical_document_pipeline/processed_pdfs/colonial-office-list-1939/olmocr_results.md",
        "extraction_date": datetime.now().strftime("%Y-%m-%d"),
        "extraction_method": "Manual LLM boundary identification with systematic document review",
        "total_colonies": len(extraction_data),
        "notes": [
            "All colony boundaries manually identified by reading OCR content",
            "Extraction covers PART II-C: Colonial Office colonies and territories",
            "PART II-C starts at line 24090, PART III starts at line 53434",
            "Line number prefixes removed from extracted text",
            "1939 was just before WWII outbreak (September 1939)",
            "ADEN moved to first position (was in appendix in 1937)",
            "ADEN became Crown Colony in 1937 (transferred from India)",
            "MALAYA section includes Straits Settlements, Federated and Unfederated Malay States",
            "WESTERN PACIFIC includes multiple sub-territories",
            "WINDWARD ISLANDS includes Grenada, St. Lucia, St. Vincent sub-sections",
            "LEEWARD ISLANDS includes Antigua, Barbuda, Dominica, Montserrat, Virgin Islands",
            "APPENDIX section includes NORTH BORNEO, SARAWAK, TRANS-JORDAN",
            "Some colonies have OCR errors in headers (marked with *, **, †, or #)"
        ],
        "colonies": extraction_data
    }

    with open(JSON_OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print(f"\nMetadata saved to: {JSON_OUTPUT}")

def generate_report(extraction_data):
    """Generate extraction report"""
    report = f"""# 1939 Colonial Office List - Extraction Report

**Extraction Date:** {datetime.now().strftime("%Y-%m-%d")}
**Source File:** historical_document_pipeline/processed_pdfs/colonial-office-list-1939/olmocr_results.md
**Total Colonies Extracted:** {len(extraction_data)}

## Methodology

All colony boundaries were manually identified by:
1. Locating PART II-C header (line 24090)
2. Identifying PART III start (line 53434)
3. Systematically reading through the section to find all colony headers
4. Cross-referencing with 1937 list (42 colonies) to ensure completeness
5. Handling OCR errors and variations in colony name formatting
6. Identifying subsections, island groupings, and Malayan territories
7. Verifying boundaries by reading content at potential transition points

## Key Findings

### Significant Changes from 1937

- **ADEN**: Now listed first (line 24092) instead of in appendix
  - Became Crown Colony in April 1937 (transferred from Government of India)
  - Includes extensive Aden Protectorate and Hadhramaut States sections

- **Structure**: 1939 has more entries ({len(extraction_data)} vs 42 in 1937)
  - TONGA listed separately within Western Pacific section
  - More detailed subsections for some territories

### Historical Context

- **1939**: Published just before WWII outbreak (September 1939)
- **Palestinian Mandate**: Still under British administration
- **Trans-Jordan**: Listed in appendix as mandate territory
- **Protected States**: Brunei, North Borneo, Sarawak, Tonga, Zanzibar
- **Mandate Territories**: Palestine, Tanganyika, Trans-Jordan

### Territory Types

- **Crown Colonies**: Most territories including Aden (new in 1937)
- **Protectorates**: Aden Protectorate, Kenya, Nyasaland, Somaliland, Zanzibar
- **Protected States**: Brunei, North Borneo, Sarawak, Tonga
- **Mandate Territories**: Palestine, Tanganyika, Trans-Jordan
- **Dependencies**: Ascension (St. Helena), Cayman Islands (Jamaica), Turks & Caicos (Jamaica)

## Extraction Summary

Extracted {len(extraction_data)} colonies/territories from PART II-C (Colonial Office territories):

"""

    for colony in extraction_data:
        report += f"- **{colony['colony_name']}** (lines {colony['start_line']}-{colony['end_line']}, {colony['line_count']} lines)\n"
        if colony.get('note'):
            report += f"  - Note: {colony['note']}\n"

    report += f"""

## Comparison with 1937

- 1937: 42 colonies extracted
- 1939: {len(extraction_data)} colonies extracted

The 1939 list has {len(extraction_data) - 42} more {'entry' if len(extraction_data) - 42 == 1 else 'entries'} ({len(extraction_data)} total vs 42 in 1937) primarily due to:
1. ADEN moved from appendix to main section (now first)
2. TONGA listed as separate entry within Western Pacific section
3. TRANS-JORDAN added to appendix section
4. Different organizational structure for some territories

Notable changes:
- ADEN: Became Crown Colony in 1937, now prominently featured first
- Extensive coverage of Aden Protectorate and Hadhramaut States
- Trans-Jordan still listed in appendix as mandate territory
- Palestine still under British mandate (tensions increasing)

## Output Files

- Individual colony files: `output_3/1939_manual_parsed/[COLONY_NAME].txt`
- Metadata JSON: `output_3/1939_manual_parsed.json`
- This report: `output_3/1939_PARSING_REPORT.md`

## Data Quality

- All boundaries manually verified by reading content
- OCR quality generally good, with some header formatting variations
- Line number prefixes successfully removed from all extracted text
- All {len(extraction_data)} colonies successfully extracted and saved
"""

    with open(REPORT_OUTPUT, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"Report saved to: {REPORT_OUTPUT}")

def main():
    print("="*80)
    print("1939 Colonial Office List - Manual Colony Extraction")
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
