#!/usr/bin/env python3
"""
Extract individual colony sections from Colonial Office List 1918
"""

import json
import re
from pathlib import Path

# Define all colonies and their starting line numbers
# Based on manual inspection of the document
COLONIES = [
    ("AUSTRALIA", 3645, 11153),
    ("BAHAMAS", 11153, 11511),
    ("BARBADOS", 11511, 12160),
    ("BERMUDA", 12160, 12558),
    ("BRITISH_GUIANA", 12558, 13421),
    ("BRITISH_HONDURAS", 13421, 13770),
    ("CANADA", 13770, 17089),
    ("CEYLON", 17089, 18150),
    ("CYPRUS", 18150, 19064),
    ("EAST_AFRICA_PROTECTORATE", 19064, 19671),
    ("FALKLAND_ISLANDS", 19671, 19915),
    ("FIJI", 19915, 20523),
    ("GAMBIA", 20523, 21067),
    ("GIBRALTAR", 21067, 21265),
    ("GOLD_COAST", 21265, 22108),
    ("HONG_KONG", 22108, 22667),
    ("JAMAICA", 22667, 23726),
    ("LEEWARD_ISLANDS", 23726, 25229),
    ("MALTA", 25229, 25835),
    ("MAURITIUS", 25835, 26699),
    ("NEWFOUNDLAND", 26699, 27134),
    ("NEW_ZEALAND", 27134, 28346),
    ("NIGERIA", 28346, 29350),
    ("NYASALAND_PROTECTORATE", 29350, 29671),
    ("ST_HELENA", 29671, 29848),
    ("SEYCHELLES", 29848, 30213),
    ("SIERRA_LEONE", 30213, 30774),
    ("SOMALILAND_PROTECTORATE", 30774, 30907),
    ("SOUTH_AFRICA", 30907, 34117),
    ("STRAITS_SETTLEMENTS", 34117, 34955),
    ("FEDERATED_MALAY_STATES", 34955, 35594),
    ("MALAY_STATES_UNFEDERATED", 35594, 35981),
    ("TRINIDAD", 35981, 37687),
    ("TURKS_AND_CAICOS_ISLANDS", 37687, 37804),
    ("UGANDA", 37804, 38223),
    ("WEIHAIWEI", 38223, 38287),
    ("WESTERN_PACIFIC", 38287, 38617),
    ("WINDWARD_ISLANDS", 38617, 39604),
    ("ZANZIBAR", 39604, 39644),
    # Appendix colonies
    ("NORTH_BORNEO", 39648, 39949),
    ("SARAWAK", 39949, 40177),
    ("ADEN", 40179, 40189),
    ("ASCENSION", 40189, 40193),
    ("TRISTAN_DA_CUNHA", 40193, 40204),
]

def extract_colonies(input_file, output_dir):
    """Extract each colony section to a separate file"""

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    print(f"Reading source file: {input_file}")
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    total_lines = len(lines)
    print(f"Total lines in document: {total_lines}")

    extracted = []

    for colony_name, start_line, end_line in COLONIES:
        print(f"\nExtracting {colony_name} (lines {start_line}-{end_line})...")

        # Adjust for 0-indexing (line numbers in grep are 1-indexed)
        start_idx = start_line - 1
        end_idx = min(end_line - 1, total_lines)

        # Extract the lines for this colony
        colony_lines = lines[start_idx:end_idx]
        colony_text = ''.join(colony_lines)

        # Count actual content (non-empty lines)
        content_lines = [l for l in colony_lines if l.strip()]

        # Save to file
        output_file = output_path / f"{colony_name}.md"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(colony_text)

        print(f"  ✓ Saved to {output_file}")
        print(f"  Lines: {len(colony_lines)} ({len(content_lines)} non-empty)")

        extracted.append({
            "name": colony_name.replace("_", " "),
            "file": f"{colony_name}.md",
            "start_line": start_line,
            "end_line": end_line,
            "total_lines": len(colony_lines),
            "content_lines": len(content_lines)
        })

    return extracted

def create_summary_json(extracted_colonies, output_file):
    """Create JSON summary of all extracted colonies"""

    summary = {
        "document": "Colonial Office List 1918",
        "year": 1918,
        "significance": "End of World War I (November 1918)",
        "extraction_date": "2025-11-18",
        "total_colonies": len(extracted_colonies),
        "colonies": extracted_colonies,
        "notes": [
            "This is the Colonial Office List from 1918, the year WWI ended",
            "No post-WWI League of Nations mandates appear in this list",
            "Mandates would appear in subsequent years (1919+)",
            "Document includes dominions (Australia, Canada, New Zealand, South Africa)",
            "Includes protectorates and territories",
            "Appendix includes territories not directly administered by Colonial Office"
        ]
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Summary saved to {output_file}")
    return summary

def main():
    input_file = "/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1918/olmocr_results.md"
    output_dir = "/home/user/colonial_office_list/output_3/1918_manual_parsed"
    summary_file = "/home/user/colonial_office_list/output_3/1918_manual_parsed.json"

    print("="*70)
    print("Colonial Office List 1918 - Colony Extraction")
    print("="*70)

    # Extract all colonies
    extracted = extract_colonies(input_file, output_dir)

    # Create summary JSON
    summary = create_summary_json(extracted, summary_file)

    print("\n" + "="*70)
    print(f"EXTRACTION COMPLETE")
    print("="*70)
    print(f"Total colonies extracted: {len(extracted)}")
    print(f"Output directory: {output_dir}")
    print(f"Summary file: {summary_file}")
    print("="*70)

    # Print colony list
    print("\nExtracted Colonies:")
    print("-" * 70)
    for i, colony in enumerate(extracted, 1):
        print(f"{i:2d}. {colony['name']:40s} ({colony['content_lines']:5d} lines)")

if __name__ == "__main__":
    main()
