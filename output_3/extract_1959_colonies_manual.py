#!/usr/bin/env python3
"""
Manual extraction of colonies from 1959 Colonial Office List.
Based on manual boundary identification.
"""

import json
import os
import re
from pathlib import Path

# Manually identified colony boundaries based on reading the OCR file
COLONY_BOUNDARIES = [
    {"name": "Aden", "start": 3672, "end": 4151},
    {"name": "Bahama Islands", "start": 4152, "end": 4803},
    {"name": "Bermuda", "start": None, "end": None},  # Need to find
    {"name": "British Guiana", "start": 4804, "end": 5195},
    {"name": "British Honduras", "start": 5196, "end": 5568},
    {"name": "Brunei", "start": 5569, "end": 5867},
    {"name": "Christmas Island", "start": 5868, "end": 5871},
    {"name": "Cyprus", "start": 5872, "end": 6321},
    {"name": "Falkland Islands", "start": 6322, "end": 6651},
    {"name": "Fiji", "start": 6652, "end": 7016},
    {"name": "Gambia", "start": 7017, "end": 7409},
    {"name": "Gibraltar", "start": 7410, "end": 7657},
    {"name": "Hong Kong", "start": 7658, "end": 8072},
    {"name": "Kenya", "start": 8073, "end": 8611},
    {"name": "Leeward Islands", "start": 8612, "end": 8760},
    {"name": "Malta", "start": 8761, "end": 9192},
    {"name": "Mauritius", "start": 9193, "end": 9566},
    {"name": "Nigeria", "start": 9567, "end": 10641},
    {"name": "North Borneo", "start": None, "end": None},  # Need to find
    {"name": "Rhodesia and Nyasaland", "start": 10642, "end": 10649},
    {"name": "Northern Rhodesia", "start": 10650, "end": 11238},
    {"name": "Nyasaland", "start": 11239, "end": 11638},
    {"name": "St. Helena", "start": 11639, "end": 11853},
    {"name": "Sarawak", "start": 11854, "end": 12183},
    {"name": "Seychelles", "start": 12184, "end": 12482},
    {"name": "Sierra Leone", "start": 12483, "end": 12875},
    {"name": "Singapore", "start": 12876, "end": 13335},
    {"name": "Somaliland", "start": 13336, "end": 13601},
    {"name": "Tanganyika", "start": 13602, "end": 13984},
    {"name": "Tonga", "start": 13985, "end": 14130},
    {"name": "Uganda", "start": 14131, "end": 14590},
    {"name": "West Indies", "start": 14591, "end": 17995},
    {"name": "Western Pacific", "start": 17996, "end": 18904},
    {"name": "Zanzibar", "start": 18629, "end": None},  # Within Western Pacific section?
    {"name": "Miscellaneous Islands", "start": 18905, "end": 18907},
    {"name": "High Commission Territories", "start": 18908, "end": None},  # Need to find end
]

def extract_colony_section(input_file, colony_info, output_dir):
    """Extract a single colony section from the OCR file."""

    start_line = colony_info["start"]
    end_line = colony_info["end"]

    if start_line is None:
        print(f"  Skipping {colony_info['name']}: start line not identified")
        return None

    if end_line is None:
        print(f"  Warning: {colony_info['name']}: end line not identified, will estimate")
        # Will handle this case later
        return None

    lines = []
    line_count = 0
    word_count = 0

    with open(input_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, start=1):
            if line_num >= start_line and line_num <= end_line:
                lines.append(line.rstrip('\n'))
                line_count += 1
                word_count += len(line.split())

    # Write to file
    colony_file = output_dir / f"{colony_info['name'].replace(' ', '_').lower()}.txt"
    with open(colony_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    return {
        "name": colony_info["name"],
        "file": str(colony_file.name),
        "start_line": start_line,
        "end_line": end_line,
        "line_count": line_count,
        "word_count": word_count,
        "char_count": sum(len(line) for line in lines)
    }

def main():
    input_file = Path("/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1959/olmocr_results.md")
    output_dir = Path("/home/user/colonial_office_list/output_3/1959_manual_parsed")

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Extracting {len(COLONY_BOUNDARIES)} colonies from 1959 Colonial Office List...")
    print()

    metadata = {
        "year": 1959,
        "source_file": str(input_file),
        "extraction_method": "manual_boundary_identification",
        "colonies": []
    }

    for colony_info in COLONY_BOUNDARIES:
        print(f"Processing: {colony_info['name']}")
        result = extract_colony_section(input_file, colony_info, output_dir)
        if result:
            metadata["colonies"].append(result)

    # Write metadata JSON
    metadata_file = Path("/home/user/colonial_office_list/output_3/1959_manual_parsed.json")
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)

    print()
    print(f"Extraction complete!")
    print(f"  Colonies extracted: {len(metadata['colonies'])}")
    print(f"  Output directory: {output_dir}")
    print(f"  Metadata file: {metadata_file}")

if __name__ == "__main__":
    main()
