#!/usr/bin/env python3
"""
Script to find all colony section headers in the 1900 Colonial Office List
"""

import re

def find_colony_headers(file_path):
    """Find all potential colony section headers"""
    colonies = []

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Patterns to identify colony headers
    # Pattern 1: ALL CAPS ending with period (main pattern)
    pattern1 = re.compile(r'^([A-Z][A-Z\s&,\'()-]+)\.$')
    # Pattern 2: Markdown bold/heading
    pattern2 = re.compile(r'^(\*\*|##)\s*([A-Z][A-Z\s&,\'()-]+)[*.#]*\s*$')

    # Known colony names to look for
    known_colonies = [
        'BAHAMAS', 'BARBADOS', 'BERMUDA', 'BRITISH GUIANA', 'BRITISH HONDURAS',
        'BRITISH NEW GUINEA', 'DOMINION OF CANADA', 'CAPE OF GOOD HOPE', 'CEYLON',
        'CYPRUS', 'FALKLAND ISLANDS', 'FIJI', 'THE GAMBIA', 'GIBRALTAR',
        'THE GOLD COAST COLONY', 'GOLD COAST', 'HONG KONG', 'JAMAICA', 'LABUAN',
        'LAGOS', 'THE LEEWARD ISLANDS', 'LEEWARD ISLANDS', 'MAURITIUS', 'NATAL',
        'NEWFOUNDLAND', 'NEW SOUTH WALES', 'NEW ZEALAND', 'NORTHERN NIGERIA',
        'QUEENSLAND', 'SEYCHELLES', 'SIERRA LEONE', 'SOUTH AFRICA', 'BASUTOLAND',
        'RHODESIA', 'SOUTHERN NIGERIA', 'SOUTH AUSTRALIA', 'STRAITS SETTLEMENTS',
        'TASMANIA', 'TRINIDAD AND TOBAGO', 'TRINIDAD', 'TOBAGO',
        'TURKS AND CAICOS ISLANDS', 'VICTORIA', 'WESTERN AUSTRALIA',
        'WESTERN PACIFIC', 'THE WINDWARD ISLANDS', 'WINDWARD ISLANDS',
        'GRENADA', 'GRENADE', 'ZANZIBAR', 'EAST AFRICA PROTECTORATE',
        'UGANDA', 'BRUNEI', 'NORTH BORNEO', 'SARAWAK', 'ADEN', 'ASCENSION',
        'TRISTAN D\'ACUNHA', 'WEI-HAI-WEI', 'MALTA', 'PITCAIRN ISLAND',
        'NORFOLK ISLAND'
    ]

    for i, line in enumerate(lines, start=1):
        line = line.rstrip('\n')

        # Remove line number prefix if present (format: "3171→")
        clean_line = re.sub(r'^\s*\d+→', '', line)

        # Check pattern 1
        match1 = pattern1.match(clean_line)
        if match1:
            colony_name = match1.group(1).strip()
            # Filter out obvious non-colonies
            if len(colony_name) > 8 and any(k in colony_name for k in known_colonies):
                colonies.append((i, colony_name, 'pattern1'))

        # Check pattern 2
        match2 = pattern2.match(clean_line)
        if match2:
            colony_name = match2.group(2).strip()
            if any(k in colony_name for k in known_colonies):
                colonies.append((i, colony_name, 'pattern2'))

        # Also check for exact matches of known colonies
        for known in known_colonies:
            if clean_line.strip() == known + '.' or clean_line.strip() == known:
                if not any(c[0] == i for c in colonies):  # Avoid duplicates
                    colonies.append((i, known, 'exact'))

    return colonies

if __name__ == '__main__':
    file_path = '/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1900/olmocr_results.md'

    colonies = find_colony_headers(file_path)

    # Sort by line number
    colonies.sort(key=lambda x: x[0])

    # Remove duplicates (keep first occurrence)
    seen = set()
    unique_colonies = []
    for line_num, name, pattern in colonies:
        if name not in seen:
            seen.add(name)
            unique_colonies.append((line_num, name, pattern))

    print(f"Found {len(unique_colonies)} potential colony sections:\n")
    for line_num, name, pattern in unique_colonies:
        print(f"Line {line_num:5d}: {name} ({pattern})")
