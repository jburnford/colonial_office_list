#!/usr/bin/env python3
"""
1934 Colonial Office List - Manual Colony Extraction
Extracts all colonies from PART II-C based on manual boundary identification
"""

import json
import re
import os
from datetime import datetime

# Source file
OCR_FILE = "/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1934/olmocr_results.md"
OUTPUT_DIR = "/home/user/colonial_office_list/output_3/1934_manual_parsed"
JSON_OUTPUT = "/home/user/colonial_office_list/output_3/1934_manual_parsed.json"
REPORT_OUTPUT = "/home/user/colonial_office_list/output_3/1934_PARSING_REPORT.md"

# Manually identified colony boundaries (PART II-C: Colonial Office colonies)
# Based on systematic manual review of the OCR file
COLONIES = [
    {"name": "BAHAMAS", "start": 22221, "note": ""},
    {"name": "BARBADOS", "start": 22636, "note": "OCR shows 'BARBADOS.*'"},
    {"name": "BERMUDA", "start": 23300, "note": ""},
    {"name": "BRITISH GUIANA", "start": 23715, "note": ""},
    {"name": "BRITISH HONDURAS", "start": 24565, "note": ""},
    {"name": "CEYLON", "start": 25097, "note": "Large colony with multiple provinces"},
    {"name": "CYPRUS", "start": 26578, "note": ""},
    {"name": "FALKLAND ISLANDS", "start": 27316, "note": ""},
    {"name": "FIJI", "start": 27634, "note": ""},
    {"name": "THE GAMBIA", "start": 28184, "note": ""},
    {"name": "GIBRALTAR", "start": 28625, "note": ""},
    {"name": "THE GOLD COAST", "start": 28815, "note": "Includes Ashanti, Northern Territories, and Togoland sections"},
    {"name": "HONG KONG", "start": 29770, "note": "No header line - starts directly with description"},
    {"name": "JAMAICA", "start": 30411, "note": "OCR shows '*JAMAICA.*'"},
    {"name": "CAYMAN ISLANDS", "start": 31372, "note": "Dependency of Jamaica"},
    {"name": "TURKS AND CAICOS ISLANDS", "start": 31434, "note": "OCR shows '**TURKS AND CAICOS ISLANDS.**', dependency of Jamaica"},
    {"name": "KENYA", "start": 31637, "note": "Full name: KENYA COLONY AND PROTECTORATE"},
    {"name": "THE LEEWARD ISLANDS", "start": 32807, "note": "Includes Antigua, Barbuda, Dominica, Montserrat, Virgin Islands"},
    {"name": "MALAYA: STRAITS SETTLEMENTS", "start": 34177, "note": "Includes Singapore, Malacca, Penang, Labuan, Christmas Island"},
    {"name": "MALAYA: FEDERATED MALAY STATES", "start": 35307, "note": "Includes Perak, Selangor, Negri Sembilan, Pahang"},
    {"name": "MALAY STATES NOT INCLUDED IN THE FEDERATION", "start": 36597, "note": "Header for unfederated states"},
    {"name": "JOHORE", "start": 36601, "note": "Unfederated Malay State"},
    {"name": "KEDAH", "start": 36908, "note": "Unfederated Malay State"},
    {"name": "PERLIS", "start": 37012, "note": "OCR shows 'MALAYA : STATE OF PERLIS', unfederated state"},
    {"name": "KELANTAN", "start": 37112, "note": "Unfederated Malay State"},
    {"name": "TRENGGANU", "start": 37231, "note": "Unfederated Malay State"},
    {"name": "BRUNEI", "start": 37255, "note": "Protected state"},
    {"name": "MALTA", "start": 37305, "note": ""},
    {"name": "MAURITIUS", "start": 37985, "note": ""},
    {"name": "NIGERIA", "start": 39024, "note": ""},
    {"name": "NORTHERN RHODESIA", "start": 39694, "note": "OCR shows 'NORTHERN RHODESIA.†'"},
    {"name": "NYASALAND PROTECTORATE", "start": 40200, "note": "OCR shows 'NYASALAND PROTECTORATE.†'"},
    {"name": "PALESTINE", "start": 40615, "note": "Mandate territory"},
    {"name": "ST. HELENA", "start": 41385, "note": ""},
    {"name": "ASCENSION", "start": 41565, "note": "Dependency of St. Helena"},
    {"name": "SEYCHELLES", "start": 41578, "note": ""},
    {"name": "SIERRA LEONE", "start": 41909, "note": ""},
    {"name": "SOMALILAND PROTECTORATE", "start": 42371, "note": ""},
    {"name": "TANGANYIKA TERRITORY", "start": 42555, "note": "OCR shows '**TANGANYIKA TERRITORY.**', mandate territory"},
    {"name": "TRINIDAD AND TOBAGO", "start": 43267, "note": "OCR shows 'TRINIDAD.', includes Tobago subsection"},
    {"name": "UGANDA", "start": 44302, "note": ""},
    {"name": "TONGA", "start": 45212, "note": "Protected state"},
    {"name": "THE WINDWARD ISLANDS", "start": 45363, "note": "OCR shows '**THE WINDWARD ISLANDS.**', includes Grenada, St. Lucia, St. Vincent"},
    {"name": "ZANZIBAR", "start": 46317, "note": "Protectorate"},
    {"name": "NORTH BORNEO", "start": 46621, "note": "Protected state"},
    {"name": "SARAWAK", "start": 46899, "note": "Protected state"},
    {"name": "TRANS-JORDAN", "start": 47145, "note": "Mandate territory"},
    {"name": "ADEN", "start": 47214, "note": "Under MISCELLANEOUS POSSESSIONS section"},
    {"name": "TRISTAN DA CUNHA", "start": 47317, "note": "Under MISCELLANEOUS POSSESSIONS"},
    {"name": "MISCELLANEOUS ISLANDS", "start": 47334, "note": "Last entry in PART II-C"},
]

# PART III starts at line 47341, so all colonies end before this
PART_III_START = 47341

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
        "year": 1934,
        "source_file": "historical_document_pipeline/processed_pdfs/colonial-office-list-1934/olmocr_results.md",
        "extraction_date": datetime.now().strftime("%Y-%m-%d"),
        "extraction_method": "Manual LLM boundary identification with systematic document review",
        "total_colonies": len(extraction_data),
        "notes": [
            "All colony boundaries manually identified by reading OCR content",
            "Extraction covers PART II-C: Colonial Office colonies only",
            "PART II-C starts at line 22219, PART III starts at line 47341",
            "Line number prefixes removed from extracted text",
            "IRAQ not present in 1934 (gained independence in 1932)",
            "HONG KONG found without header - starts at line 29770 with description text",
            "Malaya sections include both Straits Settlements and Malay States",
            "Several territories listed as protectorates or mandate territories",
            "Leeward Islands and Windward Islands are groupings with sub-territories",
            "Some colonies have OCR errors in headers (marked with *, **, or †)"
        ],
        "colonies": extraction_data
    }

    with open(JSON_OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print(f"\nMetadata saved to: {JSON_OUTPUT}")

def generate_report(extraction_data):
    """Generate extraction report"""
    report = f"""# 1934 Colonial Office List - Extraction Report

**Extraction Date:** {datetime.now().strftime("%Y-%m-%d")}
**Source File:** historical_document_pipeline/processed_pdfs/colonial-office-list-1934/olmocr_results.md
**Total Colonies Extracted:** {len(extraction_data)}

## Methodology

All colony boundaries were manually identified by:
1. Locating PART II-C header (line 22219)
2. Identifying PART III start (line 47341)
3. Systematically reading through the section to find all colony headers
4. Cross-referencing with 1932 list to ensure completeness
5. Handling OCR errors and variations in colony name formatting
6. Identifying subsections, island groupings, and Malayan territories
7. Searching for specific patterns and short lines with capital letters

## Key Findings

- **IRAQ**: Not present in 1934 list (gained independence in 1932)
- **HONG KONG**: Found without header at line 29770 - unusual format
- **Malaya**: Complex structure with Straits Settlements, Federated States, and Unfederated States
- **Protected States**: Brunei, North Borneo, Sarawak, Tonga, Zanzibar
- **Mandate Territories**: Palestine, Tanganyika, Trans-Jordan
- **Dependencies**: Cayman Islands, Turks and Caicos (under Jamaica), Ascension (under St. Helena)

## Extraction Summary

Extracted {len(extraction_data)} main colonies/territories from PART II-C (Colonial Office territories):

"""

    for colony in extraction_data:
        report += f"- **{colony['colony_name']}** (lines {colony['start_line']}-{colony['end_line']}, {colony['line_count']} lines)\n"
        if colony.get('note'):
            report += f"  - Note: {colony['note']}\n"

    report += f"""

## Comparison with 1932

- 1932: 43 colonies extracted
- 1934: {len(extraction_data)} colonies extracted

The 1934 list has {len(extraction_data) - 43} more entries ({len(extraction_data)} total vs 43 in 1932) primarily due to:
1. Separate listing of unfederated Malay States (Johore, Kedah, Perlis, Kelantan, Trengganu)
2. Separate section for "Malay States Not Included in the Federation"
3. Different organizational structure for Malayan territories

Notable differences:
- IRAQ removed (gained independence 1932)
- HONG KONG has no header line - starts directly with descriptive text
- More detailed breakdown of Malayan territories
- Addition of Hong Kong (previously may have been in a different section or missing in 1932)

## Output Files

- Individual colony files: `output_3/1934_manual_parsed/[COLONY_NAME].txt`
- Metadata JSON: `output_3/1934_manual_parsed.json`
- This report: `output_3/1934_PARSING_REPORT.md`
"""

    with open(REPORT_OUTPUT, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"Report saved to: {REPORT_OUTPUT}")

def main():
    print("="*80)
    print("1934 Colonial Office List - Manual Colony Extraction")
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
