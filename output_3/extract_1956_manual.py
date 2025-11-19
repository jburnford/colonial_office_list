#!/usr/bin/env python3
"""
Manual extraction of colonies from the 1956 Colonial Office List.
This script uses manually identified boundaries to extract each colony section.
"""

import os
import re
import json
from pathlib import Path

# Paths
OCR_FILE = "/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1956/olmocr_results.md"
OUTPUT_DIR = "/home/user/colonial_office_list/output_3/1956_manual_parsed"
METADATA_FILE = "/home/user/colonial_office_list/output_3/1956_manual_parsed.json"

# Manually identified colony boundaries
# Format: (start_line, name, end_line_will_be_calculated)
COLONIES = [
    (3607, "ADEN"),
    (4095, "BAHAMA_ISLANDS"),
    (4362, "BARBADOS"),
    (4684, "BERMUDA"),
    (4920, "BRITISH_GUIANA"),
    (5324, "BRITISH_HONDURAS"),
    (5638, "BRUNEI"),
    (5882, "CYPRUS"),
    (6240, "FALKLAND_ISLANDS"),  # Note: multi-line header "FALKLAND ISLANDS AND\nDEPENDENCIES"
    (6601, "FIJI"),
    (6890, "THE_GAMBIA"),
    (7224, "GIBRALTAR"),
    (7397, "THE_GOLD_COAST"),
    (7877, "HONG_KONG"),
    (8233, "JAMAICA"),
    (8923, "KENYA"),
    (9632, "LEEWARD_ISLANDS"),
    (10070, "FEDERATION_OF_MALAYA"),
    (10679, "MALTA"),
    (11054, "MAURITIUS"),
    (11402, "FEDERATION_OF_NIGERIA"),
    (12017, "NORTH_BORNEO"),
    (12329, "FEDERATION_OF_RHODESIA_AND_NYASALAND"),
    (12337, "NORTHERN_RHODESIA"),
    (12790, "NYASALAND_PROTECTORATE"),
    (13136, "ST_HELENA"),
    (13420, "SARAWAK"),
    (13705, "SEYCHELLES"),
    (13912, "SIERRA_LEONE"),
    (14262, "SINGAPORE"),
    (14719, "SOMALILAND_PROTECTORATE"),
    (14939, "TANGANYIKA"),
    (15404, "KINGDOM_OF_TONGA"),
    (15547, "TRINIDAD_AND_TOBAGO"),
    (15904, "UGANDA"),
    (16248, "WESTERN_PACIFIC_HIGH_COMMISSION"),
    (16756, "THE_WINDWARD_ISLANDS"),
    (17827, "ZANZIBAR"),
]

# Part III starts at line 19214 (this is where Part II content ends)
PART_III_LINE = 19214


def remove_line_numbers(line):
    """Remove line number prefix (e.g., '  3607→') from a line."""
    return re.sub(r'^\s*\d+→', '', line)


def extract_colonies():
    """Extract each colony section and save to individual files."""

    print("=" * 80)
    print("EXTRACTING COLONIES FROM 1956 COLONIAL OFFICE LIST")
    print("=" * 80)
    print()

    # Create output directory
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)

    # Read the entire file
    print(f"Reading OCR file: {OCR_FILE}")
    with open(OCR_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    print(f"Total lines in file: {len(lines)}")
    print()

    # Metadata for all colonies
    metadata = {
        "source_file": OCR_FILE,
        "extraction_date": "2025-11-19",
        "total_colonies": len(COLONIES),
        "part_ii_start": 3606,
        "part_iii_start": PART_III_LINE,
        "colonies": []
    }

    # Process each colony
    for i, (start_line, colony_name) in enumerate(COLONIES):
        # Determine end line (start of next colony or Part III)
        if i < len(COLONIES) - 1:
            end_line = COLONIES[i + 1][0] - 1
        else:
            end_line = PART_III_LINE - 1

        print(f"Processing: {colony_name}")
        print(f"  Lines: {start_line} to {end_line}")

        # Extract lines for this colony (convert to 0-based indexing)
        colony_lines = lines[start_line - 1:end_line]

        # Remove line number prefixes
        clean_lines = [remove_line_numbers(line) for line in colony_lines]

        # Count statistics
        total_lines = len(clean_lines)
        non_empty_lines = sum(1 for line in clean_lines if line.strip())
        total_words = sum(len(line.split()) for line in clean_lines)
        total_chars = sum(len(line) for line in clean_lines)

        # Save to file
        output_file = os.path.join(OUTPUT_DIR, f"{colony_name}.txt")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.writelines(clean_lines)

        print(f"  Lines: {total_lines} ({non_empty_lines} non-empty)")
        print(f"  Words: {total_words}")
        print(f"  Saved to: {output_file}")
        print()

        # Add to metadata
        metadata["colonies"].append({
            "name": colony_name,
            "start_line": start_line,
            "end_line": end_line,
            "total_lines": total_lines,
            "non_empty_lines": non_empty_lines,
            "total_words": total_words,
            "total_characters": total_chars,
            "output_file": output_file
        })

    # Save metadata
    print(f"Saving metadata to: {METADATA_FILE}")
    with open(METADATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)

    print()
    print("=" * 80)
    print("EXTRACTION COMPLETE")
    print("=" * 80)
    print(f"Total colonies extracted: {len(COLONIES)}")
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"Metadata file: {METADATA_FILE}")

    return metadata


def print_summary(metadata):
    """Print a summary of the extraction."""
    print()
    print("=" * 80)
    print("SUMMARY")
    print("=" * 80)
    print()

    total_lines = sum(c["total_lines"] for c in metadata["colonies"])
    total_words = sum(c["total_words"] for c in metadata["colonies"])

    print(f"Total colonies: {metadata['total_colonies']}")
    print(f"Total lines extracted: {total_lines:,}")
    print(f"Total words extracted: {total_words:,}")
    print()

    print("Colonies by size (lines):")
    sorted_colonies = sorted(metadata["colonies"], key=lambda x: x["total_lines"], reverse=True)
    for i, colony in enumerate(sorted_colonies[:10], 1):
        print(f"  {i:2d}. {colony['name']:40s} {colony['total_lines']:5d} lines, {colony['total_words']:6d} words")

    print()
    print("Smallest colonies:")
    for i, colony in enumerate(sorted_colonies[-5:], 1):
        print(f"  {i:2d}. {colony['name']:40s} {colony['total_lines']:5d} lines, {colony['total_words']:6d} words")


if __name__ == '__main__':
    metadata = extract_colonies()
    print_summary(metadata)
