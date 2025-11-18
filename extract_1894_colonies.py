#!/usr/bin/env python3
"""
Extract Colonial Office List 1894 colonies based on manually identified boundaries
"""

import json
import os
import re

def sanitize_filename(name):
    """Convert colony name to safe filename"""
    return name.lower().replace(" ", "_").replace(".", "")

def extract_colonies():
    """Extract all colonies from 1894 OCR results"""

    file_path = "/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1894/olmocr_results.md"
    output_dir = "/home/user/colonial_office_list/output_3/1894_manual_parsed"

    # Manually identified colony boundaries based on careful analysis
    # Format: (name, start_line, marker_line_content)
    colonies_manual = [
        ("BAHAMAS", 1343),
        ("BARBADOS", 1609),
        ("BASUTOLAND", 2099),
        ("BERMUDA", 2215),
        ("BRITISH BECHUANALAND", 2550),
        ("BRITISH GUIANA", 2732),
        ("BRITISH HONDURAS", 3345),
        ("BRITISH NEW GUINEA", 3690),
        ("DOMINION OF CANADA", 3777),
        ("CAPE OF GOOD HOPE", 7298),
        ("CEYLON", 8390),
        ("FALKLAND ISLANDS", 9136),
        ("FIJI", 9437),
        ("THE GAMBIA", 9700),
        ("GIBRALTAR", 9904),
        ("THE GOLD COAST COLONY", 10096),
        ("HONG KONG", 10520),
        ("JAMAICA", 10891),
        ("LABUAN", 11524),
        ("THE LEEWARD ISLANDS", 11994),
        ("ANTIGUA", 12178),
        ("ST. CHRISTOPHER AND NEVIS", 12369),
        ("DOMINICA", 12622),
        ("MONTSERRAT", 12756),
        ("VIRGIN ISLANDS", 12864),
        ("MAURITIUS", 13412),
        ("Natal", 14320),
        ("SEYCHELLES", 14162),
        ("NEWFOUNDLAND", 15301),
        ("NEW SOUTH WALES", 15613),
        ("NEW ZEALAND", 16762),
        ("QUEENSLAND", 17472),
        ("ST. HELENA", 17975),
        ("SIERRA LEONE", 18137),
        ("SOUTH AUSTRALIA", 18583),
        ("Straits Settlements", 19488),
        ("TASMANIA", 20181),
        ("TRINIDAD", 20762),
        ("TOBAGO", 21480),
        ("VICTORIA", 21811),
        ("WESTERN AUSTRALIA", 22633),
        ("THE WINDWARD ISLANDS", 23277),
        ("GRENADA", 23375),
        ("ST. LUCIA", 23632),
        ("ST. VINCENT", 23882),
        ("ZULULAND", 24131),
        ("BRUNEI", 24318),
        ("CYPRUS", 24330),
        ("THE NIGER TERRITORIES", 24781),
        ("NIGER COAST PROTECTORATE", 25176),
        ("SARAWAK", 25314),
        ("SOUTH AFRICA", 25431),
        ("WESTERN PACIFIC", 25457),
        ("ADEN", 25577),
        ("ASCENSION", 25587),
    ]

    # Sort by line number
    colonies_manual.sort(key=lambda x: x[1])

    # Read all lines
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Determine end lines
    colonies = []
    for i, (name, start) in enumerate(colonies_manual):
        if i < len(colonies_manual) - 1:
            end = colonies_manual[i + 1][1] - 1
        else:
            # Last colony - find reasonable end point
            # Look for "PART III" or similar markers around line 25600-26000
            end = 25610  # Based on grep showing "PART III" around here

        colonies.append({
            "name": name,
            "start_line": start,
            "end_line": end,
            "filename": f"{sanitize_filename(name)}.txt",
            "line_count": end - start + 1
        })

    # Create output directory
    os.makedirs(output_dir, exist_ok=True)

    # Extract each colony
    for colony in colonies:
        start_idx = colony['start_line'] - 1  # Convert to 0-indexed
        end_idx = colony['end_line']

        content_lines = lines[start_idx:end_idx]
        content = ''.join(content_lines)

        output_file = os.path.join(output_dir, colony['filename'])
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)

        print(f"Extracted {colony['name']}: {colony['line_count']} lines -> {colony['filename']}")

    # Create JSON metadata
    metadata = {
        "year": 1894,
        "source_file": "historical_document_pipeline/processed_pdfs/colonial-office-list-1894/olmocr_results.md",
        "total_colonies": len(colonies),
        "colonies": colonies
    }

    json_file = "/home/user/colonial_office_list/output_3/1894_manual_parsed.json"
    with open(json_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)

    print(f"\n{'='*80}")
    print(f"EXTRACTION COMPLETE")
    print(f"{'='*80}")
    print(f"Total colonies extracted: {len(colonies)}")
    print(f"Metadata saved to: {json_file}")
    print(f"Colony files saved to: {output_dir}/")

    return colonies

if __name__ == "__main__":
    colonies = extract_colonies()
