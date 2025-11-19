#!/usr/bin/env python3
"""
Extract colonies from 1963 Colonial Office List using manual boundary identification.

This script uses manually identified boundaries to extract each colony section
from the OCR results and save them as individual files.
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Tuple

# Manually identified colony boundaries (start_line, colony_name)
# These boundaries were identified by reading the OCR content
COLONY_BOUNDARIES = [
    (2733, "STATE OF MALTA"),
    (3196, "STATE OF SINGAPORE"),
    (3736, "ADEN"),
    (4346, "ANTIGUA"),
    (4497, "BAHAMA ISLANDS"),
    (4879, "BARBADOS"),
    (5299, "BERMUDA"),
    (5670, "BRITISH ANTARCTIC TERRITORY"),
    (5752, "BRITISH GUIANA"),
    (6168, "BRITISH HONDURAS"),
    (6598, "BRUNEI"),
    (6953, "CAYMAN ISLANDS"),
    (7112, "DOMINICA"),
    (7369, "FALKLAND ISLANDS AND DEPENDENCIES"),
    (7688, "FIJI AND PITCAIRN ISLANDS GROUP"),
    (8041, "THE GAMBIA"),
    (8435, "GIBRALTAR"),
    (8689, "GRENADA"),
    (9024, "THE HIGH COMMISSION TERRITORIES"),
    (9723, "HONG KONG"),
    (10138, "JAMAICA"),
    (10147, "KENYA"),
    (10733, "MAURITIUS"),
    (11147, "MONTSERRAT"),
    (11303, "NORTH BORNEO"),
    (11741, "NORTHERN RHODESIA"),
    (12331, "NYASALAND PROTECTORATE"),
    (12805, "ST CHRISTOPHER NEVIS AND ANGUILLA"),
    (12980, "ST HELENA"),
    (13170, "ST LUCIA"),
    (13420, "ST VINCENT"),
    (13660, "SARAWAK"),
    (14036, "SEYCHELLES"),
    (14376, "KINGDOM OF TONGA"),
    (14525, "TRINIDAD AND TOBAGO"),
    (14534, "TURKS AND CAICOS ISLANDS"),
    (14696, "UGANDA"),
    (14706, "VIRGIN ISLANDS"),
    (14855, "WESTERN PACIFIC HIGH COMMISSION"),
    (15516, "ZANZIBAR"),
    (15854, "END_OF_PART_II"),  # Marker for end of Part II
]


def remove_line_numbers(line: str) -> str:
    """
    Remove line number prefix from a line.

    Format is: spaces + line_number + → + content
    Example: "  2733→STATE OF MALTA, G.C."
    """
    # Match pattern: optional spaces, digits, →, content
    match = re.match(r'^\s*\d+→(.*)$', line)
    if match:
        return match.group(1)
    return line


def sanitize_filename(name: str) -> str:
    """Convert colony name to a valid filename."""
    # Replace spaces and special characters
    filename = name.lower()
    filename = filename.replace(' ', '_')
    filename = filename.replace(',', '')
    filename = filename.replace('.', '')
    filename = re.sub(r'[^a-z0-9_]', '_', filename)
    filename = re.sub(r'_+', '_', filename)  # Remove multiple underscores
    filename = filename.strip('_')
    return filename


def extract_colonies(source_file: str, output_dir: str) -> Dict:
    """
    Extract all colonies from the source file.

    Args:
        source_file: Path to the OCR results file
        output_dir: Directory to save individual colony files

    Returns:
        Dictionary containing metadata about the extraction
    """
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    print(f"Reading source file: {source_file}")
    with open(source_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    total_lines = len(lines)
    print(f"Total lines in source: {total_lines:,}")

    metadata = {
        "source_file": source_file,
        "extraction_method": "manual_boundary_identification",
        "year": 1963,
        "total_source_lines": total_lines,
        "colonies": []
    }

    # Extract each colony
    for i in range(len(COLONY_BOUNDARIES) - 1):
        start_line, colony_name = COLONY_BOUNDARIES[i]
        end_line = COLONY_BOUNDARIES[i + 1][0]

        # Skip the END_OF_PART_II marker
        if colony_name == "END_OF_PART_II":
            continue

        print(f"\nExtracting: {colony_name}")
        print(f"  Lines: {start_line} to {end_line-1}")

        # Extract lines (convert to 0-based indexing)
        colony_lines = lines[start_line-1:end_line-1]

        # Remove line numbers
        cleaned_lines = [remove_line_numbers(line) for line in colony_lines]

        # Calculate statistics
        num_lines = len(cleaned_lines)
        text = ''.join(cleaned_lines)
        num_words = len(text.split())
        num_chars = len(text)

        # Create filename
        filename = sanitize_filename(colony_name) + '.txt'
        filepath = output_path / filename

        # Save to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(cleaned_lines)

        print(f"  Saved to: {filename}")
        print(f"  Lines: {num_lines:,} | Words: {num_words:,} | Chars: {num_chars:,}")

        # Add to metadata
        metadata["colonies"].append({
            "name": colony_name,
            "filename": filename,
            "start_line": start_line,
            "end_line": end_line - 1,
            "num_lines": num_lines,
            "num_words": num_words,
            "num_characters": num_chars
        })

    metadata["total_colonies"] = len(metadata["colonies"])

    return metadata


def main():
    """Main extraction process."""
    source_file = "/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1963/olmocr_results.md"
    output_dir = "/home/user/colonial_office_list/output_3/1963_manual_parsed"
    metadata_file = "/home/user/colonial_office_list/output_3/1963_manual_parsed.json"

    print("="*70)
    print("1963 COLONIAL OFFICE LIST - MANUAL EXTRACTION")
    print("="*70)

    # Extract colonies
    metadata = extract_colonies(source_file, output_dir)

    # Save metadata
    print(f"\n{'='*70}")
    print("SAVING METADATA")
    print("="*70)
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    print(f"Metadata saved to: {metadata_file}")

    # Print summary
    print(f"\n{'='*70}")
    print("EXTRACTION SUMMARY")
    print("="*70)
    print(f"Total colonies extracted: {metadata['total_colonies']}")
    print(f"Total lines extracted: {sum(c['num_lines'] for c in metadata['colonies']):,}")
    print(f"Total words extracted: {sum(c['num_words'] for c in metadata['colonies']):,}")
    print(f"Total characters extracted: {sum(c['num_characters'] for c in metadata['colonies']):,}")

    print(f"\n{'='*70}")
    print("COLONIES EXTRACTED")
    print("="*70)
    for i, colony in enumerate(metadata['colonies'], 1):
        print(f"{i:2}. {colony['name']:<45} ({colony['num_lines']:>5} lines, {colony['num_words']:>6} words)")

    print(f"\n{'='*70}")
    print("EXTRACTION COMPLETE")
    print("="*70)


if __name__ == "__main__":
    main()
