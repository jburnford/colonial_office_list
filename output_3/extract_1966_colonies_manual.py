#!/usr/bin/env python3
"""
Extract all colonies from the 1966 Colonial Office List using MANUALLY identified boundaries.

THIS IS THE FINAL YEAR - completing the entire 100-year extraction project (1867-1966)!

Territory boundaries were identified by manually reading the OCR file and verifying
section starts and ends based on content analysis.
"""

import json
import os
import re
from pathlib import Path

# Source file
SOURCE_FILE = '/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1966/olmocr_results.md'

# Output directory
OUTPUT_DIR = '/home/user/colonial_office_list/output_3/1966_manual_parsed'

# Manually identified territory boundaries
# Each entry: (start_line, end_line, display_name, filename)
TERRITORIES = [
    (2713, 3441, "ADEN AND THE PROTECTORATE OF SOUTH ARABIA", "aden"),
    (3442, 3617, "ANTIGUA", "antigua"),
    (3618, 4071, "BAHAMA ISLANDS", "bahama_islands"),
    (4072, 4530, "BARBADOS", "barbados"),
    (4531, 4787, "BASUTOLAND", "basutoland"),
    (4788, 5073, "BECHUANALAND PROTECTORATE", "bechuanaland"),
    (5074, 5493, "BERMUDA", "bermuda"),
    (5494, 5595, "BRITISH ANTARCTIC TERRITORY", "british_antarctic_territory"),
    (5596, 6089, "BRITISH GUIANA", "british_guiana"),
    (6090, 6610, "BRITISH HONDURAS", "british_honduras"),
    (6611, 6781, "CAYMAN ISLANDS", "cayman_islands"),
    (6782, 7076, "DOMINICA", "dominica"),
    (7077, 7371, "FALKLAND ISLANDS AND DEPENDENCIES", "falkland_islands"),
    (7372, 7713, "FIJI", "fiji"),
    (7714, 7723, "THE GAMBIA", "gambia"),  # Note: Became independent Feb 1965
    (7724, 8030, "GIBRALTAR", "gibraltar"),
    (8031, 8306, "GRENADA", "grenada"),  # OCR has "GRENADE" but it's GRENADA
    (8307, 8762, "HONG KONG", "hong_kong"),
    (8763, 9179, "MAURITIUS", "mauritius"),
    (9180, 9348, "MONTSERRAT", "montserrat"),
    (9349, 9381, "PITCAIRN ISLANDS GROUP", "pitcairn_islands"),
    (9382, 9574, "ST. CHRISTOPHER, NEVIS AND ANGUILLA", "st_christopher_nevis_anguilla"),
    (9575, 9898, "ST. HELENA (WITH ASCENSION AND TRISTAN DA CUNHA)", "st_helena"),
    (9899, 10137, "ST. LUCIA", "st_lucia"),
    (10138, 10418, "ST. VINCENT", "st_vincent"),
    (10419, 10807, "SEYCHELLES", "seychelles"),
    (10808, 11061, "SWAZILAND", "swaziland"),
    (11062, 11198, "KINGDOM OF TONGA", "tonga"),
    (11199, 11381, "TURKS AND CAICOS ISLANDS", "turks_and_caicos_islands"),
    (11382, 11557, "VIRGIN ISLANDS", "virgin_islands"),
    (11558, 12669, "WESTERN PACIFIC HIGH COMMISSION", "western_pacific"),
]

def extract_colonies():
    """Extract all colony sections from the 1966 Colonial Office List."""

    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Read the source file
    print(f"Reading source file: {SOURCE_FILE}")
    with open(SOURCE_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    print(f"Total lines in source: {len(lines)}")
    print(f"\nExtracting {len(TERRITORIES)} territories...")
    print("=" * 80)

    metadata = {
        "year": 1966,
        "source_file": SOURCE_FILE,
        "extraction_method": "manual_boundary_identification",
        "note": "FINAL YEAR of Colonial Office List series (1867-1966). Historic end of British Empire documentation.",
        "major_events_1966": [
            "Barbados independence (November 30, 1966)",
            "Guyana independence (May 26, 1966) - was British Guiana",
            "Lesotho independence (October 4, 1966) - was Basutoland",
            "Botswana independence (September 30, 1966) - was Bechuanaland",
            "The Gambia already independent (February 18, 1965)",
            "Rapid decolonization - final wave"
        ],
        "total_territories": len(TERRITORIES),
        "territories": {}
    }

    total_words = 0
    total_lines_extracted = 0

    # Extract each territory
    for start_line, end_line, display_name, filename in TERRITORIES:
        print(f"\nExtracting: {display_name}")
        print(f"  Lines {start_line} to {end_line} ({end_line - start_line + 1} lines)")

        # Extract the section (convert to 0-indexed)
        section_lines = lines[start_line - 1:end_line]

        # Join into text
        section_text = ''.join(section_lines)

        # Count words and lines
        word_count = len(section_text.split())
        line_count = len(section_lines)
        total_words += word_count
        total_lines_extracted += line_count

        # Write to individual file
        output_path = os.path.join(OUTPUT_DIR, f"{filename}.txt")
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(section_text)

        print(f"  → Saved to: {filename}.txt")
        print(f"  → Words: {word_count:,}, Lines: {line_count}")

        # Add to metadata
        metadata["territories"][filename] = {
            "display_name": display_name,
            "start_line": start_line,
            "end_line": end_line,
            "line_count": line_count,
            "word_count": word_count,
            "filename": f"{filename}.txt"
        }

    # Add summary statistics
    metadata["summary"] = {
        "total_territories_extracted": len(TERRITORIES),
        "total_lines_extracted": total_lines_extracted,
        "total_words_extracted": total_words,
        "average_lines_per_territory": total_lines_extracted // len(TERRITORIES),
        "average_words_per_territory": total_words // len(TERRITORIES)
    }

    # Save metadata
    metadata_path = '/home/user/colonial_office_list/output_3/1966_manual_parsed.json'
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)

    print("\n" + "=" * 80)
    print("EXTRACTION COMPLETE - 1966 FINAL YEAR")
    print("=" * 80)
    print(f"\nTotal territories extracted: {len(TERRITORIES)}")
    print(f"Total lines extracted: {total_lines_extracted:,}")
    print(f"Total words extracted: {total_words:,}")
    print(f"Average per territory: {total_lines_extracted // len(TERRITORIES)} lines, {total_words // len(TERRITORIES):,} words")
    print(f"\nOutput directory: {OUTPUT_DIR}")
    print(f"Metadata saved to: {metadata_path}")
    print("\n" + "=" * 80)
    print("HISTORIC MILESTONE: 100-year Colonial Office List extraction project COMPLETE!")
    print("Series: 1867-1966")
    print("=" * 80)

    return metadata

if __name__ == '__main__':
    metadata = extract_colonies()
