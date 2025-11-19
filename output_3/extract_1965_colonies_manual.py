#!/usr/bin/env python3
"""
Extract colonies from 1965 Colonial Office List using MANUAL boundary identification.
This script extracts individual colony sections from the OCR results.
"""

import json
import re
from pathlib import Path
from datetime import datetime

# Source file
SOURCE_FILE = "/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1965/olmocr_results.md"

# Output directory
OUTPUT_DIR = Path("/home/user/colonial_office_list/output_3/1965_manual_parsed")

# Manually identified colony boundaries (line numbers)
# Each entry: (colony_name, start_line, end_line)
COLONIES = [
    ("aden", 2821, 3548),
    ("antigua", 3549, 3714),
    ("bahama_islands", 3715, 4101),
    ("barbados", 4102, 4531),
    ("basutoland", 4532, 4995),
    ("bechuanaland_protectorate", 4996, 5294),
    ("bermuda", 5295, 5690),
    ("british_antarctic_territory", 5691, 5767),
    ("british_guiana", 5768, 6244),
    ("british_honduras", 6245, 6666),
    ("cayman_islands", 6667, 6835),
    ("dominica", 6836, 7090),
    ("falkland_islands_and_dependencies", 7091, 7368),
    ("fiji", 7369, 7752),
    ("gambia", 7753, 8146),
    ("gibraltar", 8147, 8430),
    ("grenada", 8431, 8780),
    ("hong_kong", 8781, 9217),
    ("malta", 9218, 9225),
    ("mauritius", 9226, 9683),
    ("montserrat", 9684, 9861),
    ("pitcairn_islands_group", 9862, 9871),
    ("st_christopher_nevis_anguilla", 9872, 10048),
    ("st_helena", 10049, 10314),
    ("st_lucia", 10315, 10556),
    ("st_vincent", 10557, 10810),
    ("seychelles", 10811, 11206),
    ("swaziland", 11207, 11457),
    ("tonga", 11458, 11603),
    ("turks_and_caicos_islands", 11604, 11766),
    ("virgin_islands", 11767, 11952),
    ("western_pacific_high_commission", 11953, 12978),
]

def remove_line_numbers(line):
    """Remove line number prefix from a line.

    Format: '  1234→content' becomes 'content'
    """
    match = re.match(r'^\s*\d+→(.*)$', line)
    if match:
        return match.group(1)
    return line

def extract_colony(lines, start, end):
    """Extract lines for a colony and remove line numbers."""
    colony_lines = []
    for i in range(start - 1, min(end, len(lines))):  # -1 for 0-indexing
        if i < len(lines):
            cleaned = remove_line_numbers(lines[i])
            colony_lines.append(cleaned)
    return colony_lines

def count_words(lines):
    """Count total words in lines."""
    return sum(len(line.split()) for line in lines)

def main():
    print("=" * 80)
    print("1965 COLONIAL OFFICE LIST - MANUAL EXTRACTION")
    print("=" * 80)
    print()

    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Read source file
    print(f"Reading source file: {SOURCE_FILE}")
    with open(SOURCE_FILE, 'r', encoding='utf-8') as f:
        all_lines = f.readlines()

    print(f"Total lines in source: {len(all_lines):,}")
    print()

    # Extract each colony
    metadata = {
        "extraction_date": datetime.now().isoformat(),
        "source_file": SOURCE_FILE,
        "method": "manual_boundary_identification",
        "year": 1965,
        "total_colonies": len(COLONIES),
        "colonies": []
    }

    total_lines_extracted = 0
    total_words_extracted = 0

    print("Extracting colonies:")
    print("-" * 80)

    for colony_name, start_line, end_line in COLONIES:
        # Extract colony content
        colony_lines = extract_colony(all_lines, start_line, end_line)

        # Calculate statistics
        line_count = len(colony_lines)
        word_count = count_words(colony_lines)
        char_count = sum(len(line) for line in colony_lines)

        # Save to file
        output_file = OUTPUT_DIR / f"{colony_name}.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(colony_lines))

        # Update totals
        total_lines_extracted += line_count
        total_words_extracted += word_count

        # Add to metadata
        colony_meta = {
            "name": colony_name,
            "display_name": colony_name.replace('_', ' ').title(),
            "start_line": start_line,
            "end_line": end_line,
            "line_count": line_count,
            "word_count": word_count,
            "char_count": char_count,
            "output_file": str(output_file)
        }
        metadata["colonies"].append(colony_meta)

        print(f"✓ {colony_name:40s} | Lines: {line_count:5d} | Words: {word_count:7,d} | {start_line:5d}-{end_line:5d}")

    print("-" * 80)
    print(f"Total lines extracted: {total_lines_extracted:,}")
    print(f"Total words extracted: {total_words_extracted:,}")
    print()

    # Add summary to metadata
    metadata["summary"] = {
        "total_lines_extracted": total_lines_extracted,
        "total_words_extracted": total_words_extracted,
        "average_lines_per_colony": total_lines_extracted / len(COLONIES),
        "average_words_per_colony": total_words_extracted / len(COLONIES)
    }

    # Save metadata
    metadata_file = Path("/home/user/colonial_office_list/output_3/1965_manual_parsed.json")
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)

    print(f"✓ Metadata saved to: {metadata_file}")
    print()

    # Print notable colonies (largest and smallest)
    print("Notable Colonies:")
    print("-" * 80)

    sorted_by_size = sorted(metadata["colonies"], key=lambda x: x["word_count"], reverse=True)

    print("\nLargest (by word count):")
    for colony in sorted_by_size[:5]:
        print(f"  • {colony['display_name']:40s} {colony['word_count']:7,d} words")

    print("\nSmallest (by word count):")
    for colony in sorted_by_size[-5:]:
        print(f"  • {colony['display_name']:40s} {colony['word_count']:7,d} words")

    print()
    print("=" * 80)
    print("EXTRACTION COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    main()
