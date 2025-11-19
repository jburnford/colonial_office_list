#!/usr/bin/env python3
"""
Script to identify colony boundaries in the 1956 Colonial Office List OCR file
by manually reading and analyzing the content structure.
"""

import re

# Path to the OCR results file
OCR_FILE = "/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1956/olmocr_results.md"

# Territory names to search for based on the table of contents
TERRITORIES = [
    "ADEN",
    "BAHAMA ISLANDS",
    "BARBADOS",
    "BERMUDA",
    "BRITISH GUIANA",
    "BRITISH HONDURAS",
    "BRUNEI",
    "CYPRUS",
    "FALKLAND ISLANDS",
    "FIJI",
    "GAMBIA",
    "GIBRALTAR",
    "GOLD COAST",
    "HONG KONG",
    "JAMAICA",
    "KENYA",
    "LEEWARD ISLANDS",
    "FEDERATION OF MALAYA",
    "MALTA",
    "MAURITIUS",
    "FEDERATION OF NIGERIA",
    "NORTH BORNEO",
    "FEDERATION OF RHODESIA AND NYASALAND",
    "NYASALAND PROTECTORATE",
    "ST. HELENA",
    "SARAWAK",
    "SEYCHELLES",
    "SIERRA LEONE",
    "SINGAPORE",
    "SOMALILAND PROTECTORATE",
    "TANGANYIKA",
    "TONGA",
    "TRINIDAD AND TOBAGO",
    "UGANDA",
    "WESTERN PACIFIC",
    "WINDWARD ISLANDS",
    "ZANZIBAR",
]

def find_colony_boundaries():
    """Read the OCR file and find where each colony section starts."""

    print("Searching for colony boundaries in 1956 Colonial Office List...")
    print("=" * 80)

    with open(OCR_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Find Part II start (there may be multiple - we want the one in actual content, not TOC)
    part_ii_indices = []
    part_iii_indices = []

    for i, line in enumerate(lines):
        # Check for Part II (may have line number or not)
        if re.search(r'PART II\s*$', line):
            part_ii_indices.append(i)
            print(f"Found 'PART II' at line {i+1} (index {i})")
        elif re.search(r'PART III\s*$', line):
            part_iii_indices.append(i)
            print(f"Found 'PART III' at line {i+1} (index {i})")

    # Use the second Part II (the actual content, not the TOC)
    if len(part_ii_indices) < 2:
        print("ERROR: Could not find Part II in content area")
        return []

    part_ii_idx = part_ii_indices[1]  # Second occurrence
    # Find the corresponding Part III (should be second occurrence too)
    part_iii_idx = part_iii_indices[1] if len(part_iii_indices) >= 2 else None

    print(f"\nUsing Part II at line {part_ii_idx+1}")
    if part_iii_idx:
        print(f"Using Part III at line {part_iii_idx+1}")

    if part_ii_idx is None:
        print("ERROR: Could not find Part II")
        return []

    print()

    # Now search for each territory within Part II
    colony_boundaries = []

    end_idx = min(part_iii_idx, len(lines)) if part_iii_idx else len(lines)
    for i in range(part_ii_idx, end_idx):
        line = lines[i]

        # Remove line number prefix and arrow
        content = re.sub(r'^\s*\d+→', '', line).strip()

        # Check if this line matches any territory name exactly
        for territory in TERRITORIES:
            if content == territory:
                # Check if this is in the main content area (not table of contents)
                # by verifying it's after index 3600 (line 3601)
                if i > 3600:
                    colony_boundaries.append({
                        'line': i + 1,  # Convert to 1-based line number
                        'index': i,  # Keep 0-based index for processing
                        'name': territory,
                        'raw_line': line.rstrip()
                    })
                    print(f"Line {i+1:5d}: {territory}")
                    break

    print()
    print(f"Found {len(colony_boundaries)} colonies")
    print("=" * 80)

    return colony_boundaries

if __name__ == '__main__':
    boundaries = find_colony_boundaries()
