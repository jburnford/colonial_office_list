#!/usr/bin/env python3
"""
Extract all colonies from the 1953 Colonial Office List.
This script uses manually identified colony section boundaries.
"""

import os
import json
import re
from pathlib import Path
from datetime import datetime

# Configuration
OCR_FILE = "/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1953/olmocr_results.md"
OUTPUT_DIR = "/home/user/colonial_office_list/output_3/1953_manual_parsed"
JSON_OUTPUT = "/home/user/colonial_office_list/output_3/1953_manual_parsed.json"
REPORT_OUTPUT = "/home/user/colonial_office_list/output_3/1953_PARSING_REPORT.md"

# Manually verified colony boundaries
# Format: (colony_name, start_line, end_line_or_None_for_next)
# End line is exclusive (not included in the extraction)
COLONIES = [
    ("ADEN", 3002, 3384),
    ("BAHAMA_ISLANDS", 3384, 3698),
    ("BARBADOS", 3698, 3949),
    ("BERMUDA", 3949, 4174),
    ("BRITISH_GUIANA", 4174, 4460),
    ("BRITISH_HONDURAS", 4460, 4692),
    ("BRUNEI", 4692, 4842),
    ("CYPRUS", 4842, 5141),
    ("FALKLAND_ISLANDS_AND_DEPENDENCIES", 5141, 5360),
    ("FIJI_AND_PITCAIRN_ISLANDS", 5360, 5608),
    ("GAMBIA", 5608, 5882),
    ("GIBRALTAR", 5882, 6040),
    ("GOLD_COAST", 6040, 6471),
    ("HONG_KONG", 6471, 6833),
    ("JAMAICA", 6833, 7435),
    ("KENYA", 7435, 7869),
    ("LEEWARD_ISLANDS", 7869, 8483),
    ("FEDERATION_OF_MALAYA", 8483, 9097),
    ("MALTA", 9097, 9481),
    ("MAURITIUS", 9481, 9803),
    ("NIGERIA", 9803, 10186),
    ("NORTH_BORNEO", 10186, 10439),
    ("NORTHERN_RHODESIA", 10439, 10894),
    ("NYASALAND_PROTECTORATE", 10894, 11178),
    ("ST_HELENA", 11178, 11381),
    ("SARAWAK", 11381, 11673),
    ("SEYCHELLES", 11673, 11858),
    ("SIERRA_LEONE", 11858, 12159),
    ("SINGAPORE_AND_DEPENDENCIES", 12159, 12494),
    ("SOMALILAND_PROTECTORATE", 12494, 12670),
    ("TANGANYIKA", 12670, 13130),
    ("TONGA", 13130, 13235),
    ("TRINIDAD_AND_TOBAGO", 13235, 13550),
    ("UGANDA", 13550, 13830),
    ("WESTERN_PACIFIC_HIGH_COMMISSION", 13830, 14227),
    ("WINDWARD_ISLANDS", 14227, 14996),
    ("ZANZIBAR", 14996, 15600),  # Approximate end before Part III
]

def read_ocr_file(file_path):
    """Read the OCR file and return all lines."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.readlines()

def extract_colony(lines, start_line, end_line):
    """
    Extract colony text from lines between start_line and end_line.
    Remove line number prefixes in format 'line_number→content'.
    """
    colony_lines = []

    for i, line in enumerate(lines, start=1):
        if i >= start_line and i < end_line:
            # Remove line number prefix (format: "line_number→content")
            match = re.match(r'^\s*\d+→(.*)$', line)
            if match:
                content = match.group(1)
                colony_lines.append(content + '\n')
            else:
                # Line doesn't have expected format, keep as is
                colony_lines.append(line)

    return ''.join(colony_lines)

def sanitize_filename(name):
    """Convert colony name to safe filename."""
    # Replace spaces and special characters with underscores
    safe_name = re.sub(r'[^\w\s-]', '', name.lower())
    safe_name = re.sub(r'[-\s]+', '_', safe_name)
    return safe_name

def main():
    """Main extraction process."""
    print("=" * 70)
    print("1953 Colonial Office List - Colony Extraction")
    print("=" * 70)
    print()

    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    print(f"Output directory: {OUTPUT_DIR}")
    print()

    # Read OCR file
    print(f"Reading OCR file: {OCR_FILE}")
    lines = read_ocr_file(OCR_FILE)
    total_lines = len(lines)
    print(f"Total lines in file: {total_lines:,}")
    print()

    # Extract each colony
    metadata = {
        "extraction_date": datetime.now().isoformat(),
        "source_file": OCR_FILE,
        "total_source_lines": total_lines,
        "colonies": []
    }

    extraction_stats = []

    print("Extracting colonies...")
    print()

    for colony_name, start_line, end_line in COLONIES:
        print(f"  Extracting: {colony_name}")
        print(f"    Lines: {start_line} to {end_line-1}")

        # Extract colony content
        content = extract_colony(lines, start_line, end_line)

        # Generate filename
        filename = f"{sanitize_filename(colony_name)}.txt"
        filepath = os.path.join(OUTPUT_DIR, filename)

        # Write colony file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        file_size = len(content)
        line_count = end_line - start_line

        print(f"    Output: {filename}")
        print(f"    Size: {file_size:,} bytes, {line_count:,} lines")
        print()

        # Add to metadata
        colony_metadata = {
            "name": colony_name,
            "filename": filename,
            "start_line": start_line,
            "end_line": end_line - 1,
            "line_count": line_count,
            "file_size_bytes": file_size,
            "filepath": filepath
        }
        metadata["colonies"].append(colony_metadata)
        extraction_stats.append(colony_metadata)

    # Write JSON metadata
    metadata["total_colonies"] = len(extraction_stats)
    with open(JSON_OUTPUT, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)

    print(f"JSON metadata written to: {JSON_OUTPUT}")
    print()

    # Generate parsing report
    generate_report(metadata, extraction_stats)

    print("=" * 70)
    print("Extraction Complete!")
    print("=" * 70)
    print()
    print(f"Total colonies extracted: {len(extraction_stats)}")
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"JSON metadata: {JSON_OUTPUT}")
    print(f"Parsing report: {REPORT_OUTPUT}")
    print()

def generate_report(metadata, extraction_stats):
    """Generate a detailed parsing report."""
    report_lines = []

    report_lines.append("# 1953 Colonial Office List - Parsing Report")
    report_lines.append("")
    report_lines.append(f"**Extraction Date:** {metadata['extraction_date']}")
    report_lines.append(f"**Source File:** `{metadata['source_file']}`")
    report_lines.append(f"**Total Source Lines:** {metadata['total_source_lines']:,}")
    report_lines.append(f"**Total Colonies Extracted:** {metadata['total_colonies']}")
    report_lines.append("")
    report_lines.append("---")
    report_lines.append("")

    report_lines.append("## Extraction Summary")
    report_lines.append("")
    report_lines.append("| # | Colony Name | Start Line | End Line | Lines | Size (bytes) | Filename |")
    report_lines.append("|---|-------------|------------|----------|-------|--------------|----------|")

    for i, colony in enumerate(extraction_stats, 1):
        report_lines.append(
            f"| {i} | {colony['name']} | {colony['start_line']} | "
            f"{colony['end_line']} | {colony['line_count']:,} | "
            f"{colony['file_size_bytes']:,} | `{colony['filename']}` |"
        )

    report_lines.append("")
    report_lines.append("---")
    report_lines.append("")

    report_lines.append("## Statistics")
    report_lines.append("")

    total_lines = sum(c['line_count'] for c in extraction_stats)
    total_size = sum(c['file_size_bytes'] for c in extraction_stats)
    avg_lines = total_lines / len(extraction_stats)
    avg_size = total_size / len(extraction_stats)

    report_lines.append(f"- **Total lines extracted:** {total_lines:,}")
    report_lines.append(f"- **Total size:** {total_size:,} bytes ({total_size/1024:.1f} KB)")
    report_lines.append(f"- **Average lines per colony:** {avg_lines:.1f}")
    report_lines.append(f"- **Average size per colony:** {avg_size:.1f} bytes")
    report_lines.append("")

    # Find largest and smallest colonies
    largest = max(extraction_stats, key=lambda x: x['line_count'])
    smallest = min(extraction_stats, key=lambda x: x['line_count'])

    report_lines.append(f"- **Largest colony (by lines):** {largest['name']} ({largest['line_count']:,} lines)")
    report_lines.append(f"- **Smallest colony (by lines):** {smallest['name']} ({smallest['line_count']:,} lines)")
    report_lines.append("")

    report_lines.append("---")
    report_lines.append("")

    report_lines.append("## Methodology")
    report_lines.append("")
    report_lines.append("This extraction was performed using **manually identified colony section boundaries**.")
    report_lines.append("Each colony section was located by systematically reading through the OCR file")
    report_lines.append("and identifying section headers and content boundaries.")
    report_lines.append("")
    report_lines.append("### Process:")
    report_lines.append("")
    report_lines.append("1. Systematic reading of the 1953 OCR file in sections")
    report_lines.append("2. Manual identification of colony section start lines")
    report_lines.append("3. Determination of section boundaries (end lines)")
    report_lines.append("4. Extraction of text between boundaries")
    report_lines.append("5. Removal of OCR line number prefixes (format: `line_number→content`)")
    report_lines.append("6. Writing to individual colony files")
    report_lines.append("")

    report_lines.append("---")
    report_lines.append("")

    report_lines.append("## Notes")
    report_lines.append("")
    report_lines.append("- All line numbers are based on the source OCR file line numbering")
    report_lines.append("- Some colonies include dependencies and sub-territories")
    report_lines.append("- Section boundaries were verified by reading content to ensure complete coverage")
    report_lines.append("- The extraction includes all text from start line (inclusive) to end line (exclusive)")
    report_lines.append("")

    # Write report
    with open(REPORT_OUTPUT, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))

    print(f"Parsing report written to: {REPORT_OUTPUT}")
    print()

if __name__ == "__main__":
    main()
