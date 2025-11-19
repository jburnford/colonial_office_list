#!/usr/bin/env python3
"""
Extract all colonies from 1954 Colonial Office List using manually identified boundaries.
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Tuple

# Source file
SOURCE_FILE = "/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1954/olmocr_results.md"

# Output directories
OUTPUT_DIR = Path("/home/user/colonial_office_list/output_3/1954_manual_parsed")
OUTPUT_JSON = Path("/home/user/colonial_office_list/output_3/1954_manual_parsed.json")
REPORT_FILE = Path("/home/user/colonial_office_list/output_3/1954_PARSING_REPORT.md")

# Manually identified colony boundaries (line_start, colony_name)
# Line numbers are 1-indexed as shown in the file
COLONY_BOUNDARIES = [
    (3628, "ADEN"),
    (4098, "BAHAMA_ISLANDS"),
    (4439, "BARBADOS"),
    (4788, "BERMUDA"),
    (5105, "BRITISH_GUIANA"),
    (5434, "BRITISH_HONDURAS"),
    (5707, "BRUNEI"),
    (5948, "CYPRUS"),
    (6295, "FALKLAND_ISLANDS_AND_DEPENDENCIES"),
    (6550, "FIJI"),
    (6849, "THE_GAMBIA"),
    (7197, "GIBRALTAR"),
    (7351, "THE_GOLD_COAST"),
    (7892, "HONG_KONG"),
    (8249, "JAMAICA"),
    (8942, "KENYA"),
    (9465, "THE_LEEWARD_ISLANDS"),
    (10192, "FEDERATION_OF_MALAYA"),
    (10804, "MALTA"),
    (11267, "MAURITIUS"),
    (11648, "NIGERIA"),
    (12125, "NORTH_BORNEO"),
    (12436, "THE_FEDERATION_OF_RHODESIA_AND_NYASALAND"),
    (12512, "NORTHERN_RHODESIA"),
    (12980, "NYASALAND_PROTECTORATE"),
    (13368, "ST_HELENA"),
    (13628, "SARAWAK"),
    (13931, "SEYCHELLES"),
    (14146, "SIERRA_LEONE"),
    (14498, "SINGAPORE"),
    (14925, "SOMALILAND_PROTECTORATE"),
    (15112, "TANGANYIKA"),
    (15532, "KINGDOM_OF_TONGA"),
    (15673, "TRINIDAD_AND_TOBAGO"),
    (16014, "UGANDA"),
    (16355, "WESTERN_PACIFIC_HIGH_COMMISSION"),
    (16837, "THE_WINDWARD_ISLANDS"),
    (17839, "ZANZIBAR"),
    (18085, "MISCELLANEOUS_ISLANDS"),
    (18118, "BASUTOLAND"),
    (18156, "BECHUANALAND_PROTECTORATE"),
    (18186, "SWAZILAND"),
    (18213, "END_OF_TERRITORIES"),  # Marker for end
]


def remove_line_numbers(line: str) -> str:
    """Remove line number prefix from a line."""
    # Line format: "  1234→content"
    match = re.match(r'^\s*\d+→(.*)$', line)
    if match:
        return match.group(1)
    return line


def extract_colonies():
    """Extract all colonies from the source file."""
    print(f"Reading source file: {SOURCE_FILE}")

    # Read all lines
    with open(SOURCE_FILE, 'r', encoding='utf-8') as f:
        all_lines = f.readlines()

    print(f"Total lines in file: {len(all_lines)}")

    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Metadata for JSON output
    metadata = {
        "source_file": SOURCE_FILE,
        "year": 1954,
        "extraction_method": "manual_boundary_identification",
        "total_colonies": len(COLONY_BOUNDARIES) - 1,  # Excluding END marker
        "colonies": []
    }

    # Extract each colony
    for i in range(len(COLONY_BOUNDARIES) - 1):
        start_line, colony_name = COLONY_BOUNDARIES[i]
        end_line, _ = COLONY_BOUNDARIES[i + 1]

        # Extract lines (convert to 0-indexed)
        colony_lines = all_lines[start_line - 1:end_line - 1]

        # Remove line numbers
        cleaned_lines = [remove_line_numbers(line) for line in colony_lines]

        # Join into text
        colony_text = ''.join(cleaned_lines)

        # Write to file
        output_file = OUTPUT_DIR / f"{colony_name}.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(colony_text)

        # Calculate statistics
        num_lines = len(colony_lines)
        num_chars = len(colony_text)
        num_words = len(colony_text.split())

        # Add to metadata
        colony_info = {
            "name": colony_name,
            "start_line": start_line,
            "end_line": end_line - 1,
            "num_lines": num_lines,
            "num_characters": num_chars,
            "num_words": num_words,
            "output_file": str(output_file)
        }
        metadata["colonies"].append(colony_info)

        print(f"Extracted: {colony_name} (lines {start_line}-{end_line-1}, {num_lines} lines)")

    # Write JSON metadata
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)

    print(f"\nMetadata written to: {OUTPUT_JSON}")

    return metadata


def generate_report(metadata: Dict):
    """Generate a parsing report."""
    report_lines = [
        "# 1954 Colonial Office List - Parsing Report\n",
        "\n## Extraction Summary\n",
        f"\n- **Source File:** {metadata['source_file']}",
        f"\n- **Year:** {metadata['year']}",
        f"\n- **Extraction Method:** Manual boundary identification",
        f"\n- **Total Colonies Extracted:** {metadata['total_colonies']}",
        f"\n- **Output Directory:** {OUTPUT_DIR}",
        f"\n- **Metadata File:** {OUTPUT_JSON}",
        "\n\n## Colonies Extracted\n",
        "\n| # | Colony Name | Start Line | End Line | Lines | Words | Characters |",
        "\n|---|-------------|------------|----------|-------|-------|------------|"
    ]

    for i, colony in enumerate(metadata['colonies'], 1):
        report_lines.append(
            f"\n| {i} | {colony['name']} | {colony['start_line']} | "
            f"{colony['end_line']} | {colony['num_lines']} | "
            f"{colony['num_words']:,} | {colony['num_characters']:,} |"
        )

    report_lines.extend([
        "\n\n## Statistics\n",
        f"\n- **Total Lines Extracted:** {sum(c['num_lines'] for c in metadata['colonies']):,}",
        f"\n- **Total Words:** {sum(c['num_words'] for c in metadata['colonies']):,}",
        f"\n- **Total Characters:** {sum(c['num_characters'] for c in metadata['colonies']):,}",
        "\n\n## Colony Details\n"
    ])

    for colony in metadata['colonies']:
        report_lines.extend([
            f"\n### {colony['name'].replace('_', ' ')}",
            f"\n- **Lines:** {colony['start_line']} - {colony['end_line']} ({colony['num_lines']} lines)",
            f"\n- **Size:** {colony['num_words']:,} words, {colony['num_characters']:,} characters",
            f"\n- **Output:** `{os.path.basename(colony['output_file'])}`\n"
        ])

    report_lines.append("\n## Notes\n")
    report_lines.append("\n- All line numbers removed from extracted text")
    report_lines.append("\n- Boundaries manually verified by examining file content")
    report_lines.append("\n- Each colony section extracted to individual text file")
    report_lines.append("\n- High Commission Territories (Basutoland, Bechuanaland, Swaziland) included as separate colonies\n")

    # Write report
    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write(''.join(report_lines))

    print(f"\nReport written to: {REPORT_FILE}")


def main():
    """Main extraction process."""
    print("=" * 80)
    print("1954 Colonial Office List - Manual Colony Extraction")
    print("=" * 80)

    # Extract colonies
    metadata = extract_colonies()

    # Generate report
    generate_report(metadata)

    print("\n" + "=" * 80)
    print("Extraction Complete!")
    print("=" * 80)
    print(f"\nTotal colonies extracted: {metadata['total_colonies']}")
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"Metadata file: {OUTPUT_JSON}")
    print(f"Report file: {REPORT_FILE}")


if __name__ == "__main__":
    main()
