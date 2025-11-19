#!/usr/bin/env python3
"""
Extract all colonies from the 1961 Colonial Office List using MANUALLY identified boundaries.

This script extracts each colony section based on careful manual reading of the OCR results,
identifying where each colony section begins and ends by examining the document structure.
"""

import re
import json
import os
from pathlib import Path
from collections import defaultdict

# Manually identified colony boundaries (start_line, end_line, colony_name)
# These boundaries were identified by reading the document and finding where each section starts and ends
COLONY_BOUNDARIES = [
    (3916, 4469, "aden_colony"),
    (4470, 4890, "bahamas_islands"),
    (4891, 5252, "bermuda"),
    (5253, 5668, "british_guiana"),
    (5669, 6039, "british_honduras"),
    (6040, 6418, "brunei"),
    (6419, 6428, "cameroons_uk_trusteeship"),  # Very short section
    (6429, 6436, "republic_of_cyprus"),  # Very short - independent in 1960
    (6437, 6788, "falkland_islands_and_dependencies"),
    (6789, 7137, "fiji"),  # Includes Pitcairn Islands Group
    (7138, 7536, "the_gambia"),
    (7537, 7801, "gibraltar"),
    (7802, 8180, "hong_kong"),
    (8181, 8769, "kenya"),
    (8770, 9214, "malta"),
    (9215, 9585, "mauritius"),
    (9586, 9591, "federation_of_nigeria"),  # Very short header section
    (9592, 9985, "north_borneo"),
    (9986, 9993, "federation_rhodesia_nyasaland"),  # Very short header section
    (9994, 10623, "northern_rhodesia"),
    (10624, 11041, "nyasaland_protectorate"),
    (11042, 11313, "st_helena"),  # Includes Ascension and Tristan da Cunha
    (11314, 11658, "sarawak"),
    (11659, 12399, "seychelles"),
    (12400, 12405, "somaliland_protectorate"),  # Very short - independent as Somali Republic in 1960
    (12406, 12846, "tanganyika"),
    (12847, 13327, "tonga"),
    (13328, 13460, "uganda"),
    (13461, 13597, "virgin_islands"),
    (13598, 14925, "west_indies_federation"),  # The Federation section
    (14926, 15519, "west_indies_jamaica"),
    (15520, 16420, "west_indies_cayman_turks_caicos"),
    (16421, 16982, "west_indies_st_vincent"),  # Assuming other islands included
    (16983, 17625, "western_pacific_high_commission"),
    (17626, 17940, "zanzibar"),
]

def extract_colony_section(input_file, start_line, end_line):
    """
    Extract a section of the file from start_line to end_line,
    removing line number prefixes.
    """
    lines = []

    with open(input_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            if start_line <= line_num <= end_line:
                # Remove line number prefix (format: "  1234→")
                content = re.sub(r'^\s*\d+→', '', line)
                lines.append(content)

    return ''.join(lines)

def extract_all_colonies(input_file, output_dir):
    """Extract all colony sections to individual files."""

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    metadata = {
        "source_file": str(input_file),
        "extraction_date": "2025-11-19",
        "total_colonies": len(COLONY_BOUNDARIES),
        "methodology": "Manual boundary identification through careful reading of document structure",
        "colonies": []
    }

    print(f"Extracting {len(COLONY_BOUNDARIES)} colonies from 1961 Colonial Office List...")
    print(f"Output directory: {output_path}\n")

    for start_line, end_line, colony_name in COLONY_BOUNDARIES:
        # Extract the section
        content = extract_colony_section(input_file, start_line, end_line)

        # Calculate statistics
        total_lines = end_line - start_line + 1
        non_empty_lines = len([line for line in content.split('\n') if line.strip()])
        word_count = len(content.split())
        char_count = len(content)

        # Write to file
        output_file = output_path / f"{colony_name}.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)

        # Add to metadata
        colony_metadata = {
            "name": colony_name,
            "display_name": colony_name.replace('_', ' ').title(),
            "start_line": start_line,
            "end_line": end_line,
            "total_lines": total_lines,
            "non_empty_lines": non_empty_lines,
            "word_count": word_count,
            "character_count": char_count,
            "output_file": str(output_file.name)
        }
        metadata["colonies"].append(colony_metadata)

        print(f"✓ {colony_name:45s} Lines {start_line:5d}-{end_line:5d} ({total_lines:4d} lines, {word_count:6d} words)")

    # Write metadata JSON
    metadata_file = output_path.parent / "1961_manual_parsed.json"
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)

    print(f"\n{'='*80}")
    print(f"Extraction complete!")
    print(f"{'='*80}")
    print(f"Total colonies extracted: {len(COLONY_BOUNDARIES)}")
    print(f"Total lines processed: {sum(c['total_lines'] for c in metadata['colonies'])}")
    print(f"Total words extracted: {sum(c['word_count'] for c in metadata['colonies']):,}")
    print(f"Metadata saved to: {metadata_file}")

    return metadata

if __name__ == '__main__':
    input_file = '/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1961/olmocr_results.md'
    output_dir = '/home/user/colonial_office_list/output_3/1961_manual_parsed'

    metadata = extract_all_colonies(input_file, output_dir)
