#!/usr/bin/env python3
"""
Extract all colonies from 1914 Colonial Office List
Based on manually verified boundaries
"""

import os
import re
import json
from datetime import datetime

# Input and output paths
INPUT_FILE = "/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1914/olmocr_results.md"
OUTPUT_DIR = "/home/user/colonial_office_list/output_3/1914_manual_parsed"
JSON_OUTPUT = "/home/user/colonial_office_list/output_3/1914_manual_parsed.json"

# Manually verified colony boundaries
COLONIES = [
    {"name": "AUSTRALIA", "start": 3519, "end": 10610},
    {"name": "BAHAMAS", "start": 10611, "end": 10991},
    {"name": "BARBADOS", "start": 10992, "end": 11499},
    {"name": "BERMUDA", "start": 11500, "end": 11857},
    {"name": "BRITISH GUIANA", "start": 11858, "end": 12811},
    {"name": "BRITISH HONDURAS", "start": 12812, "end": 13169},
    {"name": "DOMINION OF CANADA", "start": 13170, "end": 16358},
    {"name": "CEYLON", "start": 16359, "end": 17509},
    {"name": "CYPRUS", "start": 17510, "end": 18350},
    {"name": "EAST AFRICA PROTECTORATE", "start": 18351, "end": 18774},
    {"name": "FALKLAND ISLANDS", "start": 18775, "end": 18975},
    {"name": "FIJI", "start": 18976, "end": 19645},
    {"name": "THE GAMBIA", "start": 19646, "end": 20332},
    {"name": "THE GOLD COAST", "start": 20333, "end": 21274},
    {"name": "HONG KONG", "start": 21275, "end": 21928},
    {"name": "JAMAICA", "start": 21929, "end": 22811},
    {"name": "THE LEEWARD ISLANDS", "start": 22812, "end": 24463},
    {"name": "MALTA", "start": 24464, "end": 24981},
    {"name": "MAURITIUS", "start": 24982, "end": 25799},
    {"name": "NEWFOUNDLAND", "start": 25800, "end": 26151},
    {"name": "NEW ZEALAND", "start": 26152, "end": 27390},
    {"name": "NIGERIA", "start": 27391, "end": 28567},
    {"name": "NYASALAND PROTECTORATE", "start": 28568, "end": 28998},
    {"name": "SEYCHELLES", "start": 28999, "end": 29317},
    {"name": "SIERRA LEONE", "start": 29318, "end": 29766},
    {"name": "SOMALILAND PROTECTORATE", "start": 29767, "end": 29957},
    {"name": "SOUTH AFRICA", "start": 29958, "end": 33224},
    {"name": "STRAITS SETTLEMENTS", "start": 33225, "end": 34770},
    {"name": "TRINIDAD AND TOBAGO", "start": 34771, "end": 36169},
    {"name": "TURKS AND CAICOS ISLANDS", "start": 36170, "end": 36343},
    {"name": "UGANDA", "start": 36344, "end": 36727},
    {"name": "WEIHAIWEI", "start": 36728, "end": 36791},
    {"name": "WESTERN PACIFIC", "start": 36792, "end": 36991},
    {"name": "THE WINDWARD ISLANDS", "start": 36992, "end": 38011},
    {"name": "ZANZIBAR", "start": 38012, "end": 38085},
]

def clean_line(line):
    """Remove line number prefix from a line"""
    # Pattern: digits, arrow, content
    return re.sub(r'^\d+→', '', line)

def sanitize_filename(name):
    """Convert colony name to safe filename"""
    # Replace spaces and special chars with underscores
    return re.sub(r'[^\w\s-]', '', name).replace(' ', '_').upper()

def extract_colonies():
    """Extract each colony to individual file"""

    print(f"Reading source file: {INPUT_FILE}")
    with open(INPUT_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    print(f"Total lines in source: {len(lines)}")

    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"Created output directory: {OUTPUT_DIR}")

    extracted_colonies = []

    for colony in COLONIES:
        name = colony["name"]
        start = colony["start"]
        end = colony["end"]

        # Extract lines (convert to 0-indexed)
        colony_lines = lines[start-1:end]

        # Clean lines (remove line number prefixes)
        cleaned_lines = [clean_line(line) for line in colony_lines]

        # Create filename
        filename = f"{sanitize_filename(name)}.md"
        filepath = os.path.join(OUTPUT_DIR, filename)

        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(cleaned_lines)

        line_count = len(colony_lines)
        char_count = sum(len(line) for line in cleaned_lines)

        print(f"✓ Extracted: {name:35s} ({line_count:5d} lines, {char_count:7d} chars) -> {filename}")

        extracted_colonies.append({
            "name": name,
            "filename": filename,
            "start_line": start,
            "end_line": end,
            "line_count": line_count,
            "is_appendix": False,
            "extraction_method": "manual_llm_boundary_identification"
        })

    return extracted_colonies

def create_metadata(colonies):
    """Create JSON metadata file"""

    metadata = {
        "year": 1914,
        "total_colonies": len(colonies),
        "parsing_method": "Manual LLM-based boundary identification (output_3)",
        "extraction_date": datetime.now().strftime("%B %d, %Y"),
        "historical_context": "Pre-WWI (War began August 1914)",
        "historical_notes": [
            "1914 Colonial Office List published just before WWI outbreak in August",
            "Represents colonial administrative state at height of British Empire",
            "Nigeria unified in late 1913 (effective Jan 1914), shown as single entity",
            "Weihaiwei leased from China in 1898, under Colonial Office from 1901"
        ],
        "notes": [
            "All 35 colony boundaries manually verified by examining OCR source",
            "PART II (colonies) spans lines 3431-38085",
            "APPENDIX TO PART II begins line 38086",
            "PART III (miscellaneous) begins line 38578",
            "Weihaiwei has OCR error in header: 'WEIHAIWEL' instead of 'WEIHAIWEI'"
        ],
        "colonies": colonies
    }

    with open(JSON_OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)

    print(f"\n✓ Metadata saved to: {JSON_OUTPUT}")

    return metadata

def main():
    print("="*80)
    print("1914 Colonial Office List - Manual Extraction")
    print("="*80)
    print()

    # Extract colonies
    extracted_colonies = extract_colonies()

    # Create metadata
    metadata = create_metadata(extracted_colonies)

    print()
    print("="*80)
    print("EXTRACTION COMPLETE")
    print("="*80)
    print(f"Year: 1914")
    print(f"Total colonies extracted: {metadata['total_colonies']}")
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"Metadata file: {JSON_OUTPUT}")
    print("="*80)

if __name__ == "__main__":
    main()
