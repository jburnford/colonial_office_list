#!/usr/bin/env python3
"""
Extract all colonies from the 1936 Colonial Office List.
Manual boundary identification with cross-reference to 1932.
"""

import json
import os
import re
from datetime import datetime

# Define colony boundaries manually identified
# Each entry: (colony_name, start_line, end_line, notes)
COLONIES_1936 = [
    ("BAHAMAS", 22736, None, "First colony in PART II-C"),
    ("BARBADOS", 23080, None, "OCR shows 'BARBADOS.*'"),
    ("BERMUDA", 23745, None, None),
    ("BRITISH GUIANA", 24176, None, None),
    ("BRITISH HONDURAS", 25145, None, None),
    ("CEYLON", 25603, None, None),
    ("CYPRUS", 27304, None, None),
    ("FALKLAND ISLANDS", 27999, None, None),
    ("FIJI", 28382, None, None),
    ("THE GAMBIA", 29009, None, None),
    ("GIBRALTAR", 29453, None, None),
    ("THE GOLD COAST", 29636, None, None),
    ("HONG KONG", 30595, None, None),
    ("JAMAICA", 31193, None, None),
    ("CAYMAN ISLANDS", 32208, None, "Dependency of Jamaica"),
    ("TURKS AND CAICOS ISLANDS", 32278, None, "OCR shows '**TURKS AND CAICOS ISLANDS.**'"),
    ("KENYA", 32390, None, "Full name: KENYA COLONY AND PROTECTORATE"),
    ("THE LEEWARD ISLANDS", 33332, None, "Federation with subsections"),
    ("MALAYA: STRAITS SETTLEMENTS", 35043, None, "Malaya section 1"),
    ("CHRISTMAS ISLAND", 36409, None, "Dependency of Straits Settlements"),
    ("MALAYA: FEDERATED MALAY STATES", 36414, None, "Malaya section 2"),
    ("MALAYA: UNFEDERATED MALAY STATES", 37649, None, "Johore, Kedah, Perlis, Kelantan, Trengganu"),
    ("BRUNEI", 38354, None, "OCR shows '**BRUNEI'"),
    ("MALTA", 38403, None, None),
    ("MAURITIUS", 39139, None, None),
    ("NIGERIA", 39838, None, None),
    ("NORTHERN RHODESIA", 40856, None, None),
    ("NYASALAND PROTECTORATE", 41371, None, None),
    ("PALESTINE", 41795, None, None),
    ("ST. HELENA", 42620, None, None),
    ("ASCENSION", 42822, None, "Dependency of St. Helena"),
    ("SEYCHELLES", 42835, None, None),
    ("SIERRA LEONE", 43051, None, None),
    ("SOMALILAND PROTECTORATE", 43478, None, None),
    ("TANGANYIKA TERRITORY", 43653, None, "OCR shows '†TANGANYIKA TERRITORY'"),
    ("TRINIDAD", 44421, None, "Includes Tobago"),
    ("UGANDA", 45600, None, None),
    ("WESTERN PACIFIC", 46196, None, "High Commission territory"),
    ("THE WINDWARD ISLANDS", 46859, None, "Grenada, St. Lucia, St. Vincent"),
    ("ZANZIBAR", 47863, None, None),
    ("NORTH BORNEO", 48177, None, "Under APPENDIX section"),
    ("SARAWAK", 48455, None, "Under APPENDIX section"),
    ("TRANS-JORDAN", 48684, None, None),
    ("ADEN", 48759, None, "Under MISCELLANEOUS POSSESSIONS"),
    ("MISCELLANEOUS ISLANDS", 48881, None, "Last entry before PART III"),
]

# PART III starts at line 48886
PART_III_START = 48886

def extract_colonies():
    """Extract all colonies to individual files."""

    source_file = "/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1936/olmocr_results.md"
    output_dir = "/home/user/colonial_office_list/output_3/1936_manual_parsed"

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Read the source file
    print(f"Reading {source_file}...")
    with open(source_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    print(f"Total lines in file: {len(lines)}")

    # Calculate end lines for each colony
    colonies_with_bounds = []
    for i, (name, start, _, note) in enumerate(COLONIES_1936):
        # End line is the start of the next colony (or PART III for the last one)
        if i < len(COLONIES_1936) - 1:
            end = COLONIES_1936[i + 1][1] - 1
        else:
            end = PART_III_START - 1

        colonies_with_bounds.append((name, start, end, note))

    # Extract each colony
    results = []

    for colony_name, start_line, end_line, note in colonies_with_bounds:
        print(f"\nExtracting {colony_name}: lines {start_line}-{end_line}")

        # Extract lines (convert to 0-based index)
        colony_lines = lines[start_line-1:end_line]

        # Remove line number prefixes
        cleaned_lines = []
        for line in colony_lines:
            if '→' in line:
                parts = line.split('→', 1)
                if len(parts) == 2:
                    cleaned_lines.append(parts[1])
                else:
                    cleaned_lines.append(line)
            else:
                cleaned_lines.append(line)

        # Write to file
        safe_filename = colony_name.replace(" ", "_").replace(":", "").replace("/", "_")
        output_file = os.path.join(output_dir, f"{safe_filename}.txt")

        with open(output_file, 'w', encoding='utf-8') as f:
            f.writelines(cleaned_lines)

        line_count = end_line - start_line + 1
        print(f"  Wrote {line_count} lines to {safe_filename}.txt")

        # Add to results
        results.append({
            "colony_name": colony_name,
            "start_line": start_line,
            "end_line": end_line,
            "line_count": line_count,
            "file": output_file,
            "note": note
        })

    # Create JSON metadata
    metadata = {
        "year": 1936,
        "source_file": "historical_document_pipeline/processed_pdfs/colonial-office-list-1936/olmocr_results.md",
        "extraction_date": datetime.now().strftime("%Y-%m-%d"),
        "extraction_method": "Manual LLM boundary identification with systematic document review",
        "total_colonies": len(results),
        "notes": [
            "All colony boundaries manually identified by reading OCR content",
            "Extraction covers PART II-C: Colonial Office colonies only",
            f"PART II-C starts at line 22734, PART III starts at line {PART_III_START}",
            "Line number prefixes removed from extracted text",
            "Malaya divided into 3 sections: Straits Settlements, Federated States, Unfederated States",
            "Western Pacific and Windward Islands are federations with subsections",
            "North Borneo and Sarawak appear in APPENDIX section",
            "Aden and Miscellaneous Islands under MISCELLANEOUS POSSESSIONS"
        ],
        "colonies": results
    }

    metadata_file = "/home/user/colonial_office_list/output_3/1936_manual_parsed.json"
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)

    print(f"\n✓ Extraction complete!")
    print(f"✓ Total colonies extracted: {len(results)}")
    print(f"✓ Metadata saved to: {metadata_file}")

    return metadata

if __name__ == "__main__":
    metadata = extract_colonies()

    print("\n" + "="*70)
    print("EXTRACTION SUMMARY")
    print("="*70)
    print(f"Year: {metadata['year']}")
    print(f"Total colonies: {metadata['total_colonies']}")
    print(f"Output directory: /home/user/colonial_office_list/output_3/1936_manual_parsed/")
    print(f"Metadata file: /home/user/colonial_office_list/output_3/1936_manual_parsed.json")
    print("\nColonies extracted:")
    for i, colony in enumerate(metadata['colonies'], 1):
        print(f"  {i:2d}. {colony['colony_name']:45s} ({colony['line_count']:4d} lines)")
