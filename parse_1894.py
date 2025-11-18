#!/usr/bin/env python3
"""
Parse Colonial Office List 1894 to identify colony boundaries
"""

import re
import json
import os

def find_colony_boundaries(file_path):
    """Read the file and identify colony section boundaries"""

    # List of known colonies from 1896 and expected in 1894
    potential_colonies = [
        "BAHAMAS", "BARBADOS", "BASUTOLAND", "BERMUDA", "BRITISH BECHUANALAND",
        "BRITISH GUIANA", "BRITISH HONDURAS", "BRITISH NEW GUINEA",
        "DOMINION OF CANADA", "CAPE OF GOOD HOPE", "CEYLON",
        "FALKLAND ISLANDS", "FIJI", "THE GAMBIA", "GIBRALTAR", "THE GOLD COAST COLONY",
        "HONG KONG", "JAMAICA", "LABUAN", "LAGOS", "THE LEEWARD ISLANDS",
        "ANTIGUA", "ST. CHRISTOPHER AND NEVIS", "DOMINICA", "MONTSERRAT", "VIRGIN ISLANDS",
        "MALTA", "MAURITIUS", "SEYCHELLES", "NATAL", "NEWFOUNDLAND",
        "NEW SOUTH WALES", "NEW ZEALAND", "QUEENSLAND", "ST. HELENA",
        "SIERRA LEONE", "SOUTH AUSTRALIA", "STRAITS SETTLEMENTS", "TASMANIA",
        "TRINIDAD", "TRINIDAD AND TOBAGO", "TOBAGO", "TURKS AND CAICOS ISLANDS",
        "VICTORIA", "WESTERN AUSTRALIA", "ST. LUCIA", "ST. VINCENT",
        "ZULULAND", "BRITISH EAST AFRICA", "ZANZIBAR", "CYPRUS",
        "BRITISH ZAMBEZIA", "BRITISH CENTRAL AFRICA", "SOUTH AFRICA",
        "THE WINDWARD ISLANDS", "GRENADA", "THE NIGER TERRITORIES",
        "NIGER COAST PROTECTORATE", "BRUNEI", "SARAWAK", "WESTERN PACIFIC",
        "COOK ISLANDS", "HERVEY ISLANDS", "ADEN", "ASCENSION",
        "PITCAIRN ISLAND", "NORFOLK ISLAND", "LORD HOWE ISLAND"
    ]

    colonies = []
    current_colony = None

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Scan for colony headers
    for line_num, line in enumerate(lines, 1):
        line_stripped = line.strip()

        # Check if this line matches a colony name
        for colony_name in potential_colonies:
            # Look for exact match or with period
            if line_stripped == colony_name or line_stripped == f"{colony_name}.":
                # Check if it's likely a real colony section (not a subtitle or reference)
                # by checking the context
                if line_num > 1000:  # Skip headers and ads in first 1000 lines
                    # Check if previous line is blank (typical pattern)
                    if line_num > 1 and lines[line_num - 2].strip() == "":
                        colonies.append({
                            "name": colony_name,
                            "start_line": line_num,
                            "line": line_stripped
                        })
                        print(f"Found: {colony_name} at line {line_num}")

    # Sort by line number
    colonies.sort(key=lambda x: x['start_line'])

    # Assign end lines (start of next colony - 1)
    for i in range(len(colonies)):
        if i < len(colonies) - 1:
            colonies[i]['end_line'] = colonies[i+1]['start_line'] - 1
        else:
            # Last colony - need to find where it ends
            # Typically ends before "CONTENTS" or "PART III" or similar
            colonies[i]['end_line'] = len(lines)

    return colonies, lines

def main():
    file_path = "/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1894/olmocr_results.md"

    print("Scanning 1894 Colonial Office List for colony boundaries...")
    print("=" * 80)

    colonies, all_lines = find_colony_boundaries(file_path)

    print(f"\nFound {len(colonies)} potential colony sections")
    print("=" * 80)

    for colony in colonies:
        print(f"{colony['name']}: lines {colony['start_line']} - {colony['end_line']}")

    return colonies

if __name__ == "__main__":
    main()
