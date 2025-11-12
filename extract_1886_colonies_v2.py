#!/usr/bin/env python3
"""
Extract all colony sections from the 1886 Colonial Office List OCR output.
Version 2: More accurate boundary detection.
"""

import os
import json
import re

# Define colony boundaries with exact start lines
# The end line is the start of the next colony
COLONIES = [
    ("BAHAMAS", 1455),
    ("BARBADOS", 1837),
    ("BERMUDA", 2463),
    ("BRITISH GUIANA", 2906),
    ("BRITISH HONDURAS", 3683),
    ("DOMINION OF CANADA", 3939),
    ("CAPE OF GOOD HOPE", 7243),
    ("CEYLON", 9220),
    ("FALKLAND ISLANDS", 10118),
    ("FIJI", 10273),
    ("GIBRALTAR", 10645),
    ("LAGOS", 10853),
    ("HONG KONG", 11321),
    ("JAMAICA", 11711),
    ("LABUAN", 12583),
    ("LEEWARD ISLANDS", 13352),
    ("MALTA", 14274),
    ("MAURITIUS", 14754),
    ("NATAL", 15717),
    ("NEWFOUNDLAND", 16520),
    ("NEW SOUTH WALES", 16988),
    ("NEW ZEALAND", 17982),
    ("QUEENSLAND", 18838),
    ("ST. HELENA", 19406),
    ("SOUTH AUSTRALIA", 19537),
    ("STRAITS SETTLEMENTS", 21105),
    ("TASMANIA", 21573),
    ("TRINIDAD", 22427),
    ("TURKS AND CAICOS ISLANDS", 23392),
    ("VICTORIA", 23519),
    ("WEST AFRICA SETTLEMENTS", 24879),
    ("WESTERN AUSTRALIA", 25549),
    ("WINDWARD ISLANDS", 26149),
    ("CYPRUS", 27470),
]

# PART III starts at line 27888
PART_III_START = 27888

def extract_colonies(input_file, output_dir, metadata_file):
    """Extract all colonies from the OCR file."""

    # Read the entire file
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    colonies_metadata = []

    for i in range(len(COLONIES)):
        name, start = COLONIES[i]

        # Determine end line (start of next colony, or PART III)
        if i + 1 < len(COLONIES):
            end = COLONIES[i + 1][1]
        else:
            end = PART_III_START

        # Adjust for 0-indexing (line numbers are 1-indexed)
        start_idx = start - 1
        end_idx = end - 1

        # Extract colony content
        colony_lines = lines[start_idx:end_idx]

        # Remove trailing blank lines
        while colony_lines and colony_lines[-1].strip() == '':
            colony_lines.pop()

        # Create filename
        filename = name.replace(" ", "_").replace(".", "") + ".md"
        filepath = os.path.join(output_dir, filename)

        # Write colony file
        with open(filepath, 'w', encoding='utf-8') as f:
            # Remove line numbers if present (format: "  1234→content")
            content = []
            for line in colony_lines:
                # Remove line number prefix if present
                cleaned = re.sub(r'^\s*\d+→', '', line)
                content.append(cleaned)
            f.writelines(content)

        # Add to metadata
        colonies_metadata.append({
            "name": name,
            "filename": filename,
            "start_line": start,
            "end_line": start + len(colony_lines),
            "line_count": len(colony_lines),
            "is_appendix": False
        })

        print(f"Extracted: {name} (lines {start}-{start + len(colony_lines)}, {len(colony_lines)} lines)")

    # Create metadata JSON
    metadata = {
        "year": 1886,
        "total_colonies": len(colonies_metadata),
        "parsing_method": "LLM-based manual parsing",
        "historical_context": "Mid-1880s stability period, 5 years before Second Boer War preparations",
        "colonies": colonies_metadata
    }

    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)

    print(f"\nTotal colonies extracted: {len(colonies_metadata)}")
    print(f"Metadata saved to: {metadata_file}")

    return colonies_metadata

if __name__ == "__main__":
    input_file = "/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1886/olmocr_results.md"
    output_dir = "/home/user/colonial_office_list/output/1886_manual_parsed"
    metadata_file = "/home/user/colonial_office_list/output/1886_manual_parsed.json"

    extract_colonies(input_file, output_dir, metadata_file)
