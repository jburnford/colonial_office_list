#!/usr/bin/env python3
"""
Extract all colonies from 1937 Colonial Office List
Manual boundary identification with verified line numbers
"""

import os
import json
from datetime import datetime

# Source file
SOURCE_FILE = "historical_document_pipeline/processed_pdfs/colonial-office-list-1937/olmocr_results.md"
OUTPUT_DIR = "output_3/1937_manual_parsed"
JSON_FILE = "output_3/1937_manual_parsed.json"

# Manually verified colony boundaries for 1937
COLONIES = [
    {"name": "BAHAMAS", "start": 24171, "end": 24527, "note": "OCR shows 'BAHAMAS.'"},
    {"name": "BARBADOS", "start": 24528, "end": 25310, "note": "OCR shows 'BARBADOS.*'"},
    {"name": "BERMUDA", "start": 25311, "end": 25437, "note": "OCR shows 'BERMUDA.'"},
    {"name": "BRITISH GUIANA", "start": 25438, "end": 26466, "note": None},
    {"name": "BRITISH HONDURAS", "start": 26467, "end": 26897, "note": None},
    {"name": "CEYLON", "start": 26898, "end": 28454, "note": None},
    {"name": "CYPRUS", "start": 28455, "end": 29140, "note": None},
    {"name": "FALKLAND ISLANDS", "start": 29141, "end": 29516, "note": None},
    {"name": "FIJI", "start": 29517, "end": 30112, "note": None},
    {"name": "THE GAMBIA", "start": 30113, "end": 30532, "note": None},
    {"name": "GIBRALTAR", "start": 30533, "end": 30723, "note": None},
    {"name": "THE GOLD COAST", "start": 30724, "end": 31744, "note": None},
    {"name": "HONG KONG", "start": 31745, "end": 32439, "note": None},
    {"name": "JAMAICA", "start": 32440, "end": 33611, "note": None},
    {"name": "CAYMAN ISLANDS", "start": 33612, "end": 33719, "note": None},
    {"name": "TURKS AND CAICOS ISLANDS", "start": 33720, "end": 33878, "note": None},
    {"name": "KENYA", "start": 33879, "end": 34668, "note": "Full name: KENYA COLONY AND PROTECTORATE"},
    {"name": "THE LEEWARD ISLANDS", "start": 34669, "end": 36119, "note": "OCR shows '**THE LEEWARD ISLANDS.**'"},
    {"name": "MALAYA: STRAITS SETTLEMENTS", "start": 36120, "end": 38823, "note": "OCR shows '**MALAYA: STRAITS SETTLEMENTS**'; includes Federated Malay States"},
    {"name": "BRUNEI", "start": 38824, "end": 38874, "note": None},
    {"name": "MALTA", "start": 38875, "end": 39684, "note": "OCR shows '### MALTA'"},
    {"name": "MAURITIUS", "start": 39685, "end": 40392, "note": None},
    {"name": "NIGERIA", "start": 40393, "end": 41423, "note": None},
    {"name": "NORTHERN RHODESIA", "start": 41424, "end": 41904, "note": "OCR shows 'NORTHERN RHODESIA.*'"},
    {"name": "NYASALAND PROTECTORATE", "start": 41905, "end": 42319, "note": "OCR shows 'NYASALAND PROTECTORATE.†'"},
    {"name": "PALESTINE", "start": 42320, "end": 43110, "note": None},
    {"name": "ST. HELENA", "start": 43111, "end": 43298, "note": None},
    {"name": "ASCENSION", "start": 43299, "end": 43314, "note": None},
    {"name": "SEYCHELLES", "start": 43315, "end": 43515, "note": None},
    {"name": "SIERRA LEONE", "start": 43516, "end": 43974, "note": None},
    {"name": "SOMALILAND PROTECTORATE", "start": 43975, "end": 44155, "note": None},
    {"name": "TANGANYIKA TERRITORY", "start": 44156, "end": 44877, "note": "OCR shows '†TANGANYIKA TERRITORY.'"},
    {"name": "TRINIDAD AND TOBAGO", "start": 44878, "end": 46024, "note": "Includes TOBAGO subsection"},
    {"name": "UGANDA", "start": 46025, "end": 46469, "note": None},
    {"name": "WESTERN PACIFIC", "start": 46470, "end": 47026, "note": "Includes Gilbert & Ellice Islands, Solomon Islands, Tonga, New Hebrides, Phoenix Group, Pitcairn"},
    {"name": "THE WINDWARD ISLANDS", "start": 47027, "end": 47872, "note": "Includes Grenada, St. Lucia, St. Vincent sub-sections"},
    {"name": "ZANZIBAR", "start": 47873, "end": 48179, "note": None},
    {"name": "ADEN", "start": 48180, "end": 48271, "note": "In APPENDIX section"},
    {"name": "NORTH BORNEO", "start": 48272, "end": 48508, "note": "In APPENDIX section"},
    {"name": "SARAWAK", "start": 48509, "end": 48833, "note": "In APPENDIX section"},
    {"name": "TRISTAN DA CUNHA", "start": 48834, "end": 48850, "note": None},
    {"name": "MISCELLANEOUS ISLANDS", "start": 48851, "end": 48855, "note": "Last colony before PART III"},
]

def remove_line_numbers(line):
    """Remove line number prefix from OCR output"""
    if '→' in line:
        return line.split('→', 1)[1]
    return line

def extract_colony(lines, colony_info):
    """Extract a single colony's text"""
    start = colony_info['start'] - 1  # Convert to 0-indexed
    end = colony_info['end']  # end is inclusive, so we don't subtract 1

    colony_lines = []
    for i in range(start, end):
        if i < len(lines):
            clean_line = remove_line_numbers(lines[i])
            colony_lines.append(clean_line)

    return ''.join(colony_lines)

def sanitize_filename(name):
    """Convert colony name to safe filename"""
    # Replace special characters
    safe_name = name.replace(' ', '_')
    safe_name = safe_name.replace(':', '')
    safe_name = safe_name.replace('.', '')
    safe_name = safe_name.replace('*', '')
    safe_name = safe_name.replace('†', '')
    safe_name = safe_name.replace('#', '')
    safe_name = safe_name.replace('**', '')
    return safe_name

def main():
    print("=" * 80)
    print("Extracting 1937 Colonial Office List Colonies")
    print("=" * 80)

    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"Output directory: {OUTPUT_DIR}")

    # Read source file
    print(f"Reading source file: {SOURCE_FILE}")
    with open(SOURCE_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    print(f"Total lines in source: {len(lines)}")

    # Extract each colony
    extracted_colonies = []
    for colony in COLONIES:
        name = colony['name']
        start = colony['start']
        end = colony['end']
        line_count = end - start + 1

        print(f"\nExtracting: {name}")
        print(f"  Lines: {start} - {end} ({line_count} lines)")

        # Extract text
        colony_text = extract_colony(lines, colony)

        # Save to file
        filename = sanitize_filename(name)
        filepath = os.path.join(OUTPUT_DIR, f"{filename}.txt")
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(colony_text)
        print(f"  Saved to: {filepath}")

        # Add to metadata
        extracted_colonies.append({
            "colony_name": name,
            "start_line": start,
            "end_line": end,
            "line_count": line_count,
            "file": filepath,
            "note": colony.get('note')
        })

    # Create JSON metadata
    metadata = {
        "year": 1937,
        "source_file": SOURCE_FILE,
        "extraction_date": datetime.now().strftime("%Y-%m-%d"),
        "extraction_method": "Manual LLM boundary identification with systematic document review",
        "total_colonies": len(COLONIES),
        "notes": [
            "All colony boundaries manually identified by reading OCR content",
            "Extraction covers PART II-C: Colonial Office colonies and APPENDIX sections",
            "PART II-C starts at line 24169, PART III starts at line 48856",
            "Line number prefixes removed from extracted text",
            "IRAQ and TRANS-JORDAN from 1932 moved to different section (not Colonial Office)",
            "MALAYA section includes Straits Settlements and Federated Malay States",
            "WESTERN PACIFIC includes multiple sub-territories (Gilbert & Ellice, Solomon Islands, etc.)",
            "WINDWARD ISLANDS includes Grenada, St. Lucia, St. Vincent sub-sections",
            "ADEN, NORTH BORNEO, SARAWAK appear in APPENDIX section",
            "Some colonies have OCR errors in headers (marked with *, †, #, **)"
        ],
        "colonies": extracted_colonies
    }

    print(f"\n{'=' * 80}")
    print(f"Creating metadata file: {JSON_FILE}")
    with open(JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print(f"\n{'=' * 80}")
    print("EXTRACTION SUMMARY")
    print(f"{'=' * 80}")
    print(f"Total colonies extracted: {len(COLONIES)}")
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"Metadata file: {JSON_FILE}")
    print(f"{'=' * 80}")

if __name__ == "__main__":
    main()
