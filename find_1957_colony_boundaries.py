#!/usr/bin/env python3
"""
Script to identify all colony section boundaries in the 1957 Colonial Office List.
This script reads through the OCR file and identifies where each colony section starts.
"""

import re

def find_colony_boundaries(ocr_file):
    """
    Read through the OCR file and identify colony section boundaries.
    """

    # Expected colonies based on table of contents
    expected_colonies = [
        "ADEN", "BAHAMA ISLANDS", "BARBADOS", "BERMUDA", "BRITISH GUIANA",
        "BRITISH HONDURAS", "BRUNEI", "CYPRUS", "FALKLAND ISLANDS",
        "FIJI", "GAMBIA", "GIBRALTAR", "GOLD COAST", "GHANA", "HONG KONG",
        "JAMAICA", "KENYA", "LEEWARD ISLANDS", "MALAYA", "MALTA",
        "MAURITIUS", "NIGERIA", "NORTH BORNEO", "RHODESIA", "NYASALAND",
        "ST. HELENA", "SARAWAK", "SEYCHELLES", "SIERRA LEONE", "SINGAPORE",
        "SOMALILAND", "TANGANYIKA", "TONGA", "TRINIDAD", "UGANDA",
        "WESTERN PACIFIC", "WINDWARD ISLANDS", "ZANZIBAR"
    ]

    colonies_found = []
    current_line_num = 0
    in_part_ii = False

    with open(ocr_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for i, line in enumerate(lines, 1):
        # The file is plain text, no line number prefixes
        content = line.strip()

        # Check if we've reached PART II
        if content == "PART II":
            in_part_ii = True
            print(f"Line {i}: Found PART II")
            continue

        # Once in Part II, look for colony headers
        if in_part_ii:
            # Check for exact matches of colony names (all caps, standalone)
            if content in ["ADEN", "BAHAMA ISLANDS", "BARBADOS", "BERMUDA",
                          "BRITISH GUIANA", "BRITISH HONDURAS", "BRUNEI", "CYPRUS",
                          "FALKLAND ISLANDS", "FIJI", "GAMBIA", "GIBRALTAR",
                          "GOLD COAST", "GHANA", "HONG KONG", "JAMAICA", "KENYA",
                          "LEEWARD ISLANDS", "MALTA", "MAURITIUS", "NORTH BORNEO",
                          "SARAWAK", "SEYCHELLES", "SIERRA LEONE", "SINGAPORE",
                          "TANGANYIKA", "TONGA", "UGANDA", "WESTERN PACIFIC",
                          "WINDWARD ISLANDS", "ZANZIBAR"]:
                colonies_found.append({
                    'name': content,
                    'start_line': i,
                    'content': content
                })
                print(f"Line {i}: Found colony header: {content}")

            # Check for Federation names
            elif "FEDERATION" in content and any(x in content for x in ["MALAYA", "NIGERIA", "RHODESIA"]):
                colonies_found.append({
                    'name': content,
                    'start_line': i,
                    'content': content
                })
                print(f"Line {i}: Found federation header: {content}")

            # Check for St. Helena variations
            elif content.startswith("ST. HELENA") or content.startswith("ST HELENA"):
                colonies_found.append({
                    'name': content,
                    'start_line': i,
                    'content': content
                })
                print(f"Line {i}: Found colony header: {content}")

            # Check for Trinidad and Tobago
            elif "TRINIDAD" in content and "TOBAGO" in content:
                colonies_found.append({
                    'name': content,
                    'start_line': i,
                    'content': content
                })
                print(f"Line {i}: Found colony header: {content}")

            # Check for Somaliland Protectorate
            elif "SOMALILAND" in content and "PROTECTORATE" in content:
                colonies_found.append({
                    'name': content,
                    'start_line': i,
                    'content': content
                })
                print(f"Line {i}: Found colony header: {content}")

            # Check for Northern Rhodesia or Nyasaland Protectorate
            elif content in ["NORTHERN RHODESIA", "NYASALAND PROTECTORATE"]:
                colonies_found.append({
                    'name': content,
                    'start_line': i,
                    'content': content
                })
                print(f"Line {i}: Found colony header: {content}")

            # Check for Miscellaneous Islands
            elif "MISCELLANEOUS" in content and "ISLANDS" in content:
                colonies_found.append({
                    'name': content,
                    'start_line': i,
                    'content': content
                })
                print(f"Line {i}: Found colony header: {content}")

            # Check for High Commission Territories
            elif "HIGH COMMISSION TERRITORIES" in content:
                colonies_found.append({
                    'name': content,
                    'start_line': i,
                    'content': content
                })
                print(f"Line {i}: Found colony header: {content}")

    return colonies_found

if __name__ == "__main__":
    ocr_file = "/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1957/olmocr_results.md"

    print("=" * 80)
    print("Scanning 1957 Colonial Office List for colony boundaries...")
    print("=" * 80)
    print()

    colonies = find_colony_boundaries(ocr_file)

    print()
    print("=" * 80)
    print(f"SUMMARY: Found {len(colonies)} colony sections")
    print("=" * 80)

    for colony in colonies:
        print(f"{colony['name']:40s} starts at line {colony['start_line']}")
