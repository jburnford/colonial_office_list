#!/usr/bin/env python3
"""
Extract colonies from 1925 Colonial Office List using manually identified boundaries.
All boundaries identified through careful manual reading of the OCR file.
"""

import json
import os
from datetime import datetime

# Source file
SOURCE_FILE = "/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1925/olmocr_results.md"
OUTPUT_DIR = "/home/user/colonial_office_list/output_3/1925_manual_parsed"
METADATA_FILE = "/home/user/colonial_office_list/output_3/1925_manual_parsed.json"

# Manually identified colony boundaries (start line, colony name)
# Boundaries identified by reading OCR content and finding section headers
COLONY_BOUNDARIES = [
    (13395, "THE_TERRITORY_OF_NEW_GUINEA"),
    (13625, "BAHAMAS"),
    (14048, "BARBADOS"),
    (14631, "BERMUDA"),
    (15027, "BRITISH_GUIANA"),
    (16141, "BRITISH_HONDURAS"),
    (20039, "CEYLON"),
    (21277, "CYPRUS"),
    (21989, "FALKLAND_ISLANDS"),
    (22264, "FIJI"),
    (22894, "THE_GAMBIA"),
    (23424, "GIBRALTAR"),
    (23692, "THE_GOLD_COAST_COLONY"),
    (24004, "THE_BRITISH_SPHERE_OF_TOGOLAND"),
    (24746, "HONG_KONG"),
    (25473, "JAMAICA"),
    (26749, "THE_KENYA_COLONY_AND_PROTECTORATE"),
    (27593, "THE_LEEWARD_ISLANDS"),
    (29276, "MALTA"),
    (30016, "MAURITIUS"),
    (32587, "NIGERIA"),
    (33660, "NORTHERN_RHODESIA"),
    (34054, "NYASALAND_PROTECTORATE"),
    (34334, "ST_HELENA"),
    (34508, "SEYCHELLES"),
    (34790, "SIERRA_LEONE"),
    (35358, "SOMALILAND_PROTECTORATE"),
    (37862, "BASUTOLAND"),
    (38031, "BECHUANALAND_PROTECTORATE"),
    (38134, "SWAZILAND"),
    (38348, "SOUTHERN_RHODESIA"),
    (38905, "STRAITS_SETTLEMENTS"),
    (40298, "FEDERATED_MALAY_STATES"),
    (41255, "TANGANYIKA_TERRITORY"),
    (41838, "TRINIDAD_AND_TOBAGO"),
    (43088, "UGANDA"),
    (43406, "WEIHAIWEI"),
    (43540, "THE_GILBERT_AND_ELLICE_ISLANDS_COLONY"),
    (43840, "THE_WINDWARD_ISLANDS"),
    (44758, "ZANZIBAR"),
    (45171, "NAURU"),
    (45461, "PALESTINE"),
]

def extract_colonies():
    """Extract all colonies using manually identified boundaries."""

    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Read the source file
    print(f"Reading source file: {SOURCE_FILE}")
    with open(SOURCE_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    total_lines = len(lines)
    print(f"Total lines in file: {total_lines}")

    # Extract each colony
    colonies_metadata = []

    for i in range(len(COLONY_BOUNDARIES)):
        start_line, colony_name = COLONY_BOUNDARIES[i]

        # Determine end line (start of next colony or end of file)
        if i + 1 < len(COLONY_BOUNDARIES):
            end_line = COLONY_BOUNDARIES[i + 1][0] - 1
        else:
            # For the last colony, need to find where it ends
            # Typically colonies end before around line 50000 where indexes begin
            end_line = 49500  # Approximate end before indexes/appendices

        print(f"\nExtracting: {colony_name}")
        print(f"  Lines: {start_line} to {end_line}")

        # Extract content (convert to 0-indexed)
        content_lines = lines[start_line-1:end_line]
        content = ''.join(content_lines)

        # Save to file
        output_file = os.path.join(OUTPUT_DIR, f"{colony_name}.txt")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"  Saved: {output_file}")
        print(f"  Size: {len(content)} characters, {len(content_lines)} lines")

        # Add to metadata
        colonies_metadata.append({
            "colony_name": colony_name.replace('_', ' '),
            "start_line": start_line,
            "end_line": end_line,
            "file": output_file
        })

    # Create metadata JSON
    metadata = {
        "year": 1925,
        "source_file": SOURCE_FILE,
        "extraction_date": datetime.now().strftime("%Y-%m-%d"),
        "extraction_method": "manual_llm_boundary_identification",
        "total_colonies": len(colonies_metadata),
        "colonies": colonies_metadata
    }

    # Save metadata
    with open(METADATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)

    print(f"\n{'='*60}")
    print(f"Extraction complete!")
    print(f"Total colonies extracted: {len(colonies_metadata)}")
    print(f"Metadata saved to: {METADATA_FILE}")
    print(f"Colonies saved to: {OUTPUT_DIR}")
    print(f"{'='*60}")

    return metadata

if __name__ == "__main__":
    metadata = extract_colonies()

    # Print summary
    print("\nColonies extracted:")
    for i, colony in enumerate(metadata['colonies'], 1):
        print(f"{i:2d}. {colony['colony_name']:40s} (lines {colony['start_line']:5d}-{colony['end_line']:5d})")
