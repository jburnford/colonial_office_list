#!/usr/bin/env python3
"""
Script to determine exact boundaries for each colony section
"""

import re

def get_colony_list():
    """Return manually curated list of colony start lines"""
    # Exclude false positives like "SOUTH AFRICAN", "VICTORIAN RAILWAYS", "VICTORIA R", "TABLE OF PRECEDENCE"
    colonies = [
        (1937, 'BAHAMAS'),
        (2242, 'BARBADOS'),  # Line 191 was in advertisement section
        (2808, 'BERMUDA'),
        (3171, 'BRITISH GUIANA'),
        (3987, 'BRITISH HONDURAS'),
        (4347, 'BRITISH NEW GUINEA'),
        (4484, 'DOMINION OF CANADA'),
        (7251, 'CAPE OF GOOD HOPE'),
        (9804, 'CEYLON'),
        (10609, 'CYPRUS'),
        (11105, 'FALKLAND ISLANDS'),
        (11292, 'FIJI'),
        (11837, 'THE GAMBIA'),
        (12039, 'GIBRALTAR'),
        (12310, 'THE GOLD COAST COLONY'),
        (12897, 'HONG KONG'),
        (13277, 'JAMAICA'),
        (14025, 'LABUAN'),
        (14176, 'LAGOS'),
        (14653, 'THE LEEWARD ISLANDS'),
        (16459, 'MAURITIUS'),
        (17301, 'NATAL'),
        (17918, 'NEWFOUNDLAND'),
        (18284, 'NEW SOUTH WALES'),
        (19426, 'PITCAIRN ISLAND'),
        (19448, 'NORFOLK ISLAND'),
        (19471, 'NEW ZEALAND'),
        (20149, 'NORTHERN NIGERIA'),
        (20252, 'QUEENSLAND'),
        (20941, 'SEYCHELLES'),
        (21138, 'SIERRA LEONE'),
        (21735, 'SOUTH AFRICA'),
        (21764, 'BASUTOLAND'),
        (21953, 'RHODESIA'),
        (22059, 'SOUTH AUSTRALIA'),
        (22809, 'SOUTHERN NIGERIA'),
        (23028, 'STRAITS SETTLEMENTS'),
        (23691, 'TASMANIA'),
        (24157, 'TOBAGO'),  # This might be a subsection
        (24243, 'TRINIDAD'),  # This might be a subsection
        (24562, 'TRINIDAD AND TOBAGO'),  # Main section
        (25327, 'TURKS AND CAICOS ISLANDS'),
        (25517, 'VICTORIA'),
        (26309, 'WESTERN AUSTRALIA'),
        (27038, 'WESTERN PACIFIC'),
        (27196, 'THE WINDWARD ISLANDS'),
        (27303, 'GRENADE'),  # GRENADA
        (28208, 'ZANZIBAR'),
        (28221, 'EAST AFRICA PROTECTORATE'),
        (28240, 'UGANDA'),
        (28262, 'BRUNEI'),
        (28272, 'NORTH BORNEO'),
        (28510, 'SARAWAK'),
        (28671, 'ADEN'),
        (28683, 'ASCENSION'),
        (28689, 'TRISTAN D\'ACUNHA'),
        (28693, 'WEI-HAI-WEI'),
    ]
    return colonies

def determine_boundaries(file_path):
    """Determine start and end lines for each colony"""
    colonies = get_colony_list()

    # Calculate end lines (end when next colony starts minus 1)
    boundaries = []
    for i, (start_line, name) in enumerate(colonies):
        if i < len(colonies) - 1:
            end_line = colonies[i + 1][0] - 1
        else:
            # Last colony - need to find where content ends
            # For now, use a reasonable estimate
            end_line = 28720  # Around where appendices start

        boundaries.append({
            'name': name,
            'start_line': start_line,
            'end_line': end_line
        })

    return boundaries

if __name__ == '__main__':
    file_path = '/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1900/olmocr_results.md'

    boundaries = determine_boundaries(file_path)

    print(f"Determined boundaries for {len(boundaries)} colonies:\n")
    for col in boundaries:
        print(f"{col['name']:35s} start_line={col['start_line']:5d}, end_line={col['end_line']:5d}")

    # Check for missing colonies
    missing = [
        'CANADA', 'COLUMBIA', 'GOLD COAST', 'GRENADA', 'LEEWARD ISLANDS',
        'MALTA', 'MANITOBA', 'SOUTH AUSTRALIA', 'STRAITS SETTLEMENTS',
        'TRINIDAD AND TOBAGO', 'WINDWARD ISLANDS'
    ]

    print("\n\nChecking for 13 missing colonies:")
    for m in missing:
        found = False
        for col in boundaries:
            if m in col['name'] or col['name'] in m:
                print(f"✓ {m:25s} FOUND as '{col['name']}'")
                found = True
                break
        if not found:
            print(f"✗ {m:25s} NOT FOUND")
