#!/usr/bin/env python3
"""
Identify colony boundaries in the 1946 Colonial Office List.
This script manually identifies where each colony section starts and ends.
"""

import re
import json

# Path to the OCR results file
OCR_FILE = "/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1946/olmocr_results.md"

def find_colony_start(lines, colony_pattern, start_from=0):
    """Find the line number where a colony section starts."""
    for i in range(start_from, len(lines)):
        line = lines[i].strip()
        if re.match(colony_pattern, line):
            return i
    return -1

def read_file():
    """Read the OCR file."""
    with open(OCR_FILE, 'r', encoding='utf-8') as f:
        return f.readlines()

def identify_colonies():
    """Identify all colony boundaries manually."""
    print("Reading OCR file...")
    lines = read_file()
    total_lines = len(lines)
    print(f"Total lines: {total_lines}")

    # List of colonies from the table of contents
    # We'll search for each one in order
    colonies = []

    # Manually identified boundaries based on visual inspection
    # Line numbers are 0-indexed

    colony_definitions = [
        ("Aden", r"^ADEN COLONY$"),
        ("Bahamas", r"^BAHAMA ISLANDS$"),
        ("Barbados", r"^BARBADOS$"),
        ("Bermuda", r"^BERMUDA$"),
        ("British Guiana", r"^BRITISH GUIANA$"),
        ("British Honduras", r"^BRITISH HONDURAS$"),
        ("Ceylon", r"^CEYLON$"),
        ("Cyprus", r"^CYPRUS$"),
        ("Falkland Islands", r"^FALKLAND ISLANDS$"),
        ("Fiji", r"^FIJI$"),
        ("Gambia", r"^THE GAMBIA$|^GAMBIA$"),
        ("Gibraltar", r"^GIBRALTAR$"),
        ("Gold Coast", r"^THE GOLD COAST$|^GOLD COAST$"),
        ("Hong Kong", r"^HONG KONG$"),
        ("Jamaica", r"^JAMAICA$"),
        ("Kenya", r"^KENYA$"),
        ("Leeward Islands", r"^LEEWARD ISLANDS$"),
        ("Malaya", r"^MALAYA$"),
        ("Malta", r"^MALTA$"),
        ("Mauritius", r"^MAURITIUS$"),
        ("Nigeria", r"^NIGERIA$"),
        ("North Borneo", r"^NORTH BORNEO$"),
        ("Northern Rhodesia", r"^NORTHERN RHODESIA$"),
        ("Nyasaland", r"^NYASALAND PROTECTORATE$|^NYASALAND$"),
        ("Palestine", r"^PALESTINE$"),
        ("St. Helena", r"^ST\. HELENA$|^ST HELENA$"),
        ("Sarawak", r"^SARAWAK$"),
        ("Seychelles", r"^SEYCHELLES$"),
        ("Sierra Leone", r"^SIERRA LEONE$"),
        ("Singapore", r"^SINGAPORE$"),
        ("Somaliland Protectorate", r"^SOMALILAND PROTECTORATE$"),
        ("Tanganyika Territory", r"^TANGANYIKA TERRITORY$"),
        ("Trinidad", r"^TRINIDAD$"),
        ("Uganda", r"^UGANDA$"),
        ("Western Pacific", r"^WESTERN PACIFIC$"),
        ("Windward Islands", r"^WINDWARD ISLANDS$"),
        ("Zanzibar", r"^ZANZIBAR$"),
    ]

    # Start searching from line 2666 (after table of contents)
    search_start = 2666
    # End searching before Part III starts (around line 15610)
    search_end = 15610

    print(f"\nSearching for colonies between lines {search_start} and {search_end}...")

    for colony_name, pattern in colony_definitions:
        # Find the start of this colony
        start_line = find_colony_start(lines, pattern, search_start)

        if start_line >= 0 and start_line < search_end:
            colonies.append({
                'name': colony_name,
                'start_line': start_line + 1,  # Convert to 1-indexed
                'pattern': pattern
            })
            print(f"Found: {colony_name} at line {start_line + 1}")
        else:
            print(f"WARNING: Could not find {colony_name}")

    # Add end lines (each colony ends where the next one begins)
    for i in range(len(colonies) - 1):
        colonies[i]['end_line'] = colonies[i + 1]['start_line'] - 1

    # The last colony ends at the start of Part III or Appendix
    if colonies:
        # Find where Part III starts
        part_iii_line = find_colony_start(lines, r"^PART III$", search_start)
        if part_iii_line > 0:
            colonies[-1]['end_line'] = part_iii_line
            print(f"\nPart III starts at line {part_iii_line + 1}")
        else:
            colonies[-1]['end_line'] = search_end

    return colonies

def main():
    colonies = identify_colonies()

    print(f"\n{'='*80}")
    print(f"SUMMARY: Found {len(colonies)} colonies")
    print(f"{'='*80}\n")

    for i, colony in enumerate(colonies, 1):
        lines_count = colony['end_line'] - colony['start_line'] + 1
        print(f"{i:2d}. {colony['name']:30s} Lines {colony['start_line']:5d}-{colony['end_line']:5d} ({lines_count:4d} lines)")

    # Save to JSON for use by extraction script
    output_file = '/home/user/colonial_office_list/output_3/1946_colonies_found.txt'
    with open(output_file, 'w') as f:
        json.dump(colonies, f, indent=2)
    print(f"\nColony boundaries saved to: {output_file}")

if __name__ == "__main__":
    main()
