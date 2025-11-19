#!/usr/bin/env python3
"""
Scan the 1966 Colonial Office List OCR file to identify territory section boundaries.
"""

import re

# Expected territories from the table of contents
EXPECTED_TERRITORIES = [
    "ADEN",
    "ANTIGUA",
    "BAHAMA",
    "BARBADOS",
    "BASUTOLAND",
    "BECHUANALAND",
    "BERMUDA",
    "BRITISH ANTARCTIC",
    "BRITISH GUIANA",
    "BRITISH HONDURAS",
    "BRITISH INDIAN OCEAN",
    "CAYMAN",
    "DOMINICA",
    "FALKLAND",
    "FIJI",
    "GAMBIA",
    "GIBRALTAR",
    "GRENADA",
    "HONG KONG",
    "MAURITIUS",
    "MONTSERRAT",
    "PITCAIRN",
    "ST. CHRISTOPHER",
    "ST. HELENA",
    "ST. LUCIA",
    "ST. VINCENT",
    "SEYCHELLES",
    "SWAZILAND",
    "TONGA",
    "TURKS AND CAICOS",
    "VIRGIN ISLANDS",
    "WESTERN PACIFIC"
]

def find_territory_boundaries(filepath):
    """Scan the file and identify where each territory section starts."""

    territories = []

    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    in_part_ii = False
    part_ii_start = None

    for i, line in enumerate(lines, 1):
        # Look for start of Part II
        if 'PART II' in line and i > 2000:  # Skip table of contents
            in_part_ii = True
            part_ii_start = i
            print(f"Part II starts at line {i}")
            continue

        if not in_part_ii:
            continue

        # Look for Part III which marks end of territories
        if 'PART III' in line:
            print(f"Part III starts at line {i} - end of territories")
            break

        # Check if this line is a territory header
        # Territory headers are typically just the name in caps, sometimes with underscores
        stripped = line.strip()

        # Remove line number prefix (format: "  1234→")
        if '→' in stripped:
            content = stripped.split('→', 1)[1] if len(stripped.split('→', 1)) > 1 else ''
        else:
            content = stripped

        # Check if this matches any expected territory (exactly or as prefix)
        for territory in EXPECTED_TERRITORIES:
            if content == territory or (content.startswith(territory) and len(content) < len(territory) + 20):
                # Additional validation: next few lines should have content
                has_content = False
                for j in range(i, min(i+10, len(lines))):
                    next_line = lines[j].strip()
                    if '→' in next_line:
                        next_content = next_line.split('→', 1)[1] if len(next_line.split('→', 1)) > 1 else ''
                        if next_content and len(next_content) > 5 and not next_content.isupper():
                            has_content = True
                            break

                if has_content:
                    territories.append({
                        'name': content,
                        'line': i,
                        'raw_line': line.strip()
                    })
                    print(f"Found territory: {content} at line {i}")
                break

    return territories

if __name__ == '__main__':
    filepath = '/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1966/olmocr_results.md'

    print("Scanning for territory boundaries in 1966 Colonial Office List...")
    print("=" * 80)

    territories = find_territory_boundaries(filepath)

    print("\n" + "=" * 80)
    print(f"\nFound {len(territories)} territories:")
    print("=" * 80)

    for i, terr in enumerate(territories):
        if i < len(territories) - 1:
            next_line = territories[i + 1]['line']
            length = next_line - terr['line']
        else:
            length = "unknown"

        print(f"{terr['name']:40} Line {terr['line']:5} (length: {length})")
