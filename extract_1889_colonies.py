#!/usr/bin/env python3
"""
Extract 1889 Colonial Office List colonies based on manually identified boundaries.
This script uses ONLY the line numbers for extraction - NOT pattern matching for boundaries.
"""

import json
from datetime import date
from pathlib import Path

# Source file
SOURCE_FILE = "/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1889/olmocr_results.md"
OUTPUT_DIR = "/home/user/colonial_office_list/output_3/1889_manual_parsed"
OUTPUT_JSON = "/home/user/colonial_office_list/output_3/1889_manual_parsed.json"

# Manually identified colony boundaries (start_line, end_line, colony_name)
# These boundaries were determined by manually reading the OCR file
COLONIES = [
    (1366, 1714, "BAHAMAS"),
    (1715, 2377, "BARBADOS"),
    (2378, 2477, "BASUTOLAND"),
    (2478, 2819, "BERMUDA"),
    (2820, 2997, "BRITISH_BECHUANALAND"),
    (2998, 3715, "BRITISH_GUIANA"),
    (3716, 4051, "BRITISH_HONDURAS"),
    (4052, 4101, "BRITISH_NEW_GUINEA"),
    (4102, 7148, "DOMINION_OF_CANADA"),
    (7149, 7478, "PRINCE_EDWARD_ISLAND"),
    (7479, 9326, "CAPE_OF_GOOD_HOPE"),
    (9327, 10163, "CEYLON"),
    (10164, 10336, "FALKLAND_ISLANDS"),
    (10337, 10736, "FIJI"),
    (10737, 10962, "THE_GAMBIA"),
    (10963, 11132, "GIBRALTAR"),
    (11133, 11494, "THE_GOLD_COAST_COLONY"),
    (11495, 11613, "HELIGOLAND"),
    (11614, 11956, "HONG_KONG"),
    (11957, 12743, "JAMAICA"),
    (12744, 12866, "LABUAN"),
    (12867, 13194, "LAGOS"),
    (13195, 14547, "THE_LEEWARD_ISLANDS"),
    (14548, 14994, "MALTA"),
    (14995, 15831, "MAURITIUS"),
    (15832, 15915, "SEYCHELLES_ISLANDS"),
    (15916, 15956, "RODRIGUES"),
    (15957, 16693, "NATAL"),
    (16694, 17147, "NEWFOUNDLAND"),
    (17148, 18079, "NEW_SOUTH_WALES"),
    (18080, 18928, "NEW_ZEALAND"),
    (19177, 19461, "QUEENSLAND"),
    (19462, 19639, "ST_HELENA"),
    (19640, 20039, "SIERRA_LEONE"),
    (20040, 21040, "SOUTH_AUSTRALIA"),
    (21041, 21481, "STRAITS_SETTLEMENTS"),
    (21482, 22247, "TASMANIA"),
    (22250, 23272, "TRINIDAD"),
    (23273, 23502, "TOBAGO"),
    (23503, 23680, "TURKS_AND_CAICOS_ISLANDS"),
    (23681, 24989, "VICTORIA"),
    (24990, 25556, "WESTERN_AUSTRALIA"),
    (25557, 26635, "THE_WINDWARD_ISLANDS"),
    (26636, 26908, "ZULULAND"),
    (26909, 27594, "CYPRUS"),
]

def extract_lines(file_path, start_line, end_line):
    """Extract lines from start_line to end_line (inclusive)."""
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Convert to 0-indexed
    start_idx = start_line - 1
    end_idx = end_line  # end_line is inclusive, so we go up to but not including end_line+1

    return ''.join(lines[start_idx:end_idx])

def main():
    print(f"Extracting colonies from 1889 Colonial Office List...")
    print(f"Source: {SOURCE_FILE}")
    print(f"Output directory: {OUTPUT_DIR}")

    # Create output directory
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

    # Extract each colony
    colony_metadata = []

    for start_line, end_line, colony_name in COLONIES:
        print(f"Extracting {colony_name} (lines {start_line}-{end_line})...")

        # Extract content
        content = extract_lines(SOURCE_FILE, start_line, end_line)

        # Save to file
        output_file = f"{OUTPUT_DIR}/{colony_name}.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)

        # Add to metadata
        colony_metadata.append({
            "colony_name": colony_name,
            "start_line": start_line,
            "end_line": end_line,
            "file": output_file
        })

        print(f"  ✓ Saved to {output_file}")

    # Create JSON metadata
    metadata = {
        "year": 1889,
        "source_file": SOURCE_FILE,
        "extraction_date": str(date.today()),
        "extraction_method": "manual_boundary_identification",
        "total_colonies": len(COLONIES),
        "colonies": colony_metadata
    }

    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)

    print(f"\n✓ Extraction complete!")
    print(f"✓ Total colonies extracted: {len(COLONIES)}")
    print(f"✓ Metadata saved to: {OUTPUT_JSON}")

    # Print summary
    print("\n" + "="*60)
    print("EXTRACTION SUMMARY")
    print("="*60)
    print(f"Year: 1889")
    print(f"Total colonies: {len(COLONIES)}")
    print(f"\nColonies extracted:")
    for i, (_, _, name) in enumerate(COLONIES, 1):
        print(f"  {i:2d}. {name.replace('_', ' ')}")

if __name__ == "__main__":
    main()
