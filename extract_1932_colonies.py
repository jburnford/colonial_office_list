#!/usr/bin/env python3
"""
1932 Colonial Office List - Manual Colony Extraction
Extracts all colonies from PART II-C based on manual boundary identification
"""

import json
import re
import os
from datetime import datetime

# Source file
OCR_FILE = "/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1932/olmocr_results.md"
OUTPUT_DIR = "/home/user/colonial_office_list/output_3/1932_manual_parsed"
JSON_OUTPUT = "/home/user/colonial_office_list/output_3/1932_manual_parsed.json"
REPORT_OUTPUT = "/home/user/colonial_office_list/output_3/1932_PARSING_REPORT.md"

# Manually identified colony boundaries (PART II-C: Colonial Office colonies)
# Based on systematic manual review of the OCR file
COLONIES = [
    {"name": "BAHAMAS", "start": 23136, "note": "OCR shows 'BAHAMAS.'"},
    {"name": "BARBADOS", "start": 23519, "note": "OCR shows 'BARBADOS.*'"},
    {"name": "BERMUDA", "start": 24163, "note": "OCR shows 'BERMUDA.'"},
    {"name": "BRITISH GUIANA", "start": 24740, "note": ""},
    {"name": "BRITISH HONDURAS", "start": 25623, "note": ""},
    {"name": "CEYLON", "start": 26268, "note": ""},
    {"name": "CYPRUS", "start": 28531, "note": "New colony not in 1928 list"},
    {"name": "FALKLAND ISLANDS", "start": 29155, "note": ""},
    {"name": "FIJI", "start": 29607, "note": ""},
    {"name": "THE GAMBIA", "start": 30222, "note": ""},
    {"name": "GIBRALTAR", "start": 30642, "note": ""},
    {"name": "THE GOLD COAST", "start": 30845, "note": ""},
    {"name": "HONG KONG", "start": 32152, "note": ""},
    {"name": "JAMAICA", "start": 32779, "note": "OCR shows '*JAMAICA'"},
    {"name": "CAYMAN ISLANDS", "start": 33662, "note": ""},
    {"name": "TURKS AND CAICOS ISLANDS", "start": 33729, "note": ""},
    {"name": "KENYA", "start": 33879, "note": "Full name: KENYA COLONY AND PROTECTORATE"},
    {"name": "THE LEEWARD ISLANDS", "start": 34745, "note": ""},
    {"name": "MAURITIUS", "start": 36947, "note": ""},
    {"name": "NIGERIA", "start": 37574, "note": ""},
    {"name": "NORTHERN RHODESIA", "start": 38643, "note": "OCR shows 'NORTHERN RHODESIA.†'"},
    {"name": "NYASALAND PROTECTORATE", "start": 39380, "note": ""},
    {"name": "PALESTINE", "start": 39641, "note": ""},
    {"name": "ST. HELENA", "start": 40338, "note": ""},
    {"name": "ASCENSION", "start": 40547, "note": ""},
    {"name": "SEYCHELLES", "start": 40562, "note": ""},
    {"name": "SIERRA LEONE", "start": 40805, "note": ""},
    {"name": "SOMALILAND PROTECTORATE", "start": 41134, "note": "New colony not in 1928 list"},
    {"name": "STRAITS SETTLEMENTS", "start": 41308, "note": "No clear header; starts with historical narrative about Malacca/Penang"},
    {"name": "TANGANYIKA TERRITORY", "start": 44072, "note": "OCR shows '†TANGANYIKA TERRITORY.'"},
    {"name": "BRUNEI", "start": 44118, "note": "New colony not in 1928 list"},
    {"name": "TRINIDAD AND TOBAGO", "start": 44768, "note": "No clear header; starts mid-sentence; includes TOBAGO subsection at 44977"},
    {"name": "UGANDA", "start": 46080, "note": ""},
    {"name": "GRENADA", "start": 47194, "note": ""},
    {"name": "ST. LUCIA", "start": 47483, "note": "OCR shows '**ST. LUCIA.**'"},
    {"name": "ST. VINCENT", "start": 47768, "note": ""},
    {"name": "ZANZIBAR", "start": 48041, "note": ""},
    {"name": "IRAQ", "start": 48329, "note": ""},
    {"name": "NORTH BORNEO", "start": 48510, "note": ""},
    {"name": "TRANS-JORDAN", "start": 49077, "note": ""},
    {"name": "ADEN", "start": 49158, "note": "Under MISCELLANEOUS POSSESSIONS section"},
    {"name": "TRISTAN DA CUNHA", "start": 49195, "note": ""},
    {"name": "MISCELLANEOUS ISLANDS", "start": 49211, "note": "Last colony in PART II-C"},
]

# PART III starts at line 49220, so all colonies end before this
PART_III_START = 49220

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

        print(f"Extracted: {colony['name']:40s} (lines {start_line:5d}-{end_line:5d}, {line_count:5d} lines)")

    return extraction_data

def save_metadata(extraction_data):
    """Save extraction metadata to JSON"""
    metadata = {
        "year": 1932,
        "source_file": "historical_document_pipeline/processed_pdfs/colonial-office-list-1932/olmocr_results.md",
        "extraction_date": datetime.now().strftime("%Y-%m-%d"),
        "extraction_method": "Manual LLM boundary identification with systematic document review",
        "total_colonies": len(extraction_data),
        "notes": [
            "All colony boundaries manually identified by reading OCR content",
            "Extraction covers PART II-C: Colonial Office colonies only",
            "PART II-C starts at line 23134, PART III starts at line 49220",
            "Line number prefixes removed from extracted text",
            "New colonies compared to 1928: CYPRUS, SOMALILAND PROTECTORATE, BRUNEI, TANGANYIKA TERRITORY",
            "Missing from 1928 list: WEIHAIWEI (likely returned to China)",
            "STRAITS SETTLEMENTS has no clear header - starts with historical narrative",
            "TRINIDAD AND TOBAGO has no clear header - starts mid-sentence at line 44768",
            "Some colonies have OCR errors in headers (e.g., 'BARBADOS.*', '*JAMAICA')",
        ],
        "colonies": extraction_data
    }

    with open(JSON_OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print(f"\nMetadata saved to: {JSON_OUTPUT}")

def generate_report(extraction_data):
    """Generate extraction report"""
    report = f"""# 1932 Colonial Office List - Extraction Report

**Extraction Date:** {datetime.now().strftime("%Y-%m-%d")}
**Source File:** historical_document_pipeline/processed_pdfs/colonial-office-list-1932/olmocr_results.md
**Total Colonies Extracted:** {len(extraction_data)}

## Methodology

All colony boundaries were manually identified by:
1. Locating PART II-C header (line 23134)
2. Identifying PART III start (line 49220)
3. Systematically reading through the section to find all colony headers
4. Cross-referencing with 1928 list to identify new/missing colonies
5. Handling OCR errors and variations in colony name formatting
6. Manually reading content where headers were missing or ambiguous

## Extraction Summary

Extracted {len(extraction_data)} colonies from PART II-C (Colonial Office territories):

"""

    for colony in extraction_data:
        report += f"- **{colony['colony_name']}** (lines {colony['start_line']}-{colony['end_line']}, {colony['line_count']} lines)\n"
        if colony.get('note'):
            report += f"  - Note: {colony['note']}\n"

    report += f"""

## Changes from 1928

### New Colonies in 1932:
- **CYPRUS** (line 28531) - New colony added
- **SOMALILAND PROTECTORATE** (line 41134) - New colony added
- **BRUNEI** (line 44118) - New colony added
- **TANGANYIKA TERRITORY** (line 44072) - Former German colony, now British mandate

### Colonies Removed from 1928:
- **WEIHAIWEI** - No longer in 1932 list (likely returned to China in 1930)

## Notable Issues

- **STRAITS SETTLEMENTS** (line 41308): No clear colony header. Section starts directly with historical narrative about Malacca and Penang.
- **TRINIDAD AND TOBAGO** (line 44768): No clear header. Section starts mid-sentence, possibly due to OCR error. Includes TOBAGO as subsection at line 44977.
- Several colonies have OCR errors in headers (e.g., 'BARBADOS.*' instead of 'BARBADOS')
- Some headers have special characters: '*JAMAICA', '†TANGANYIKA TERRITORY', 'NORTHERN RHODESIA.†'

## Output Files

- Individual colony files: `output_3/1932_manual_parsed/[COLONY_NAME].txt`
- Metadata JSON: `output_3/1932_manual_parsed.json`
- This report: `output_3/1932_PARSING_REPORT.md`

## Comparison with 1928

1928 had 40 colonies in PART II-C (Colonial Office only).
1932 has {len(extraction_data)} colonies in PART II-C.

The increase reflects the addition of former German colonies (Tanganyika), protectorates (Somaliland), and other territories (Cyprus, Brunei).
"""

    with open(REPORT_OUTPUT, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"Report saved to: {REPORT_OUTPUT}")

def main():
    print("="*80)
    print("1932 Colonial Office List - Manual Colony Extraction")
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
