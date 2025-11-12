#!/usr/bin/env python3
"""
Extract all colony sections from the 1886 Colonial Office List OCR output.
"""

import os
import json
import re

# Define colony boundaries based on manual identification
# Format: (name, start_line, end_line_marker)
COLONIES = [
    ("BAHAMAS", 1455, "BARBADOS"),
    ("BARBADOS", 1837, "BERMUDA"),
    ("BERMUDA", 2463, "BRITISH GUIANA"),
    ("BRITISH GUIANA", 2906, "BRITISH HONDURAS"),
    ("BRITISH HONDURAS", 3683, "DOMINION OF CANADA"),
    ("DOMINION OF CANADA", 3939, "CAPE OF GOOD HOPE"),
    ("CAPE OF GOOD HOPE", 7243, "CEYLON"),
    ("CEYLON", 9220, "FALKLAND ISLANDS"),
    ("FALKLAND ISLANDS", 10118, "FIJI"),
    ("FIJI", 10273, "GIBRALTAR"),
    ("GIBRALTAR", 10645, "LAGOS"),
    ("LAGOS", 10853, "HONG KONG"),
    ("HONG KONG", 11321, "JAMAICA"),
    ("JAMAICA", 11711, "LABUAN"),
    ("LABUAN", 12583, "LEEWARD ISLANDS"),
    ("LEEWARD ISLANDS", 13352, "MALTA"),
    ("MALTA", 14274, "MAURITIUS"),
    ("MAURITIUS", 14754, "NATAL"),
    ("NATAL", 15717, "NEWFOUNDLAND"),
    ("NEWFOUNDLAND", 16520, "NEW SOUTH WALES"),
    ("NEW SOUTH WALES", 16988, "NEW ZEALAND"),
    ("NEW ZEALAND", 17982, "QUEENSLAND"),
    ("QUEENSLAND", 18838, "ST. HELENA"),
    ("ST. HELENA", 19406, "SOUTH AUSTRALIA"),
    ("SOUTH AUSTRALIA", 19537, "STRAITS SETTLEMENTS"),
    ("STRAITS SETTLEMENTS", 21105, "TASMANIA"),
    ("TASMANIA", 21573, "TRINIDAD"),
    ("TRINIDAD", 22427, "TURKS AND CAICOS ISLANDS"),
    ("TURKS AND CAICOS ISLANDS", 23392, "VICTORIA"),
    ("VICTORIA", 23519, "WEST AFRICA SETTLEMENTS"),
    ("WEST AFRICA SETTLEMENTS", 24879, "WESTERN AUSTRALIA"),
    ("WESTERN AUSTRALIA", 25549, "WINDWARD ISLANDS"),
    ("WINDWARD ISLANDS", 26149, "CYPRUS"),
    ("CYPRUS", 27470, 27888),  # Ends at PART III
]

def extract_colonies(input_file, output_dir, metadata_file):
    """Extract all colonies from the OCR file."""

    # Read the entire file
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    colonies_metadata = []

    for i, (name, start, end_marker) in enumerate(COLONIES):
        # Adjust for 0-indexing (line numbers are 1-indexed)
        start_idx = start - 1

        # Find end line
        if isinstance(end_marker, int):
            end_idx = end_marker - 1
        else:
            # Search for the next colony header
            end_idx = len(lines)
            for j in range(start_idx + 1, len(lines)):
                # Look for the next colony name
                if end_marker in lines[j]:
                    end_idx = j
                    break

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
            "end_line": end_idx + 1,  # Convert back to 1-indexed
            "line_count": len(colony_lines),
            "is_appendix": False
        })

        print(f"Extracted: {name} (lines {start}-{end_idx + 1}, {len(colony_lines)} lines)")

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
