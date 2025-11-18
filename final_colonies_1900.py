#!/usr/bin/env python3
"""
Final manually-verified list of all colonies in 1900 Colonial Office List
with exact start and end line numbers
"""

def get_final_colony_boundaries():
    """
    Return the complete manually-verified list of all colonies with boundaries.
    Each entry: (start_line, end_line, colony_name, notes)
    """
    colonies = [
        # Main colonies in order of appearance
        (1937, 2241, 'BAHAMAS', ''),
        (2242, 2807, 'BARBADOS', ''),
        (2808, 3170, 'BERMUDA', ''),
        (3171, 3986, 'BRITISH GUIANA', ''),
        (3987, 4346, 'BRITISH HONDURAS', ''),
        (4347, 4483, 'BRITISH NEW GUINEA', ''),
        (4484, 7250, 'DOMINION OF CANADA', 'Includes BRITISH COLUMBIA, MANITOBA AND KEWATIN as provinces'),
        (7251, 9803, 'CAPE OF GOOD HOPE', ''),
        (9804, 10608, 'CEYLON', ''),
        (10609, 11104, 'CYPRUS', ''),
        (11105, 11291, 'FALKLAND ISLANDS', ''),
        (11292, 11836, 'FIJI', ''),
        (11837, 12038, 'THE GAMBIA', ''),
        (12039, 12309, 'GIBRALTAR', ''),
        (12310, 12896, 'THE GOLD COAST COLONY', 'Variant: GOLD COAST'),
        (12897, 13276, 'HONG KONG', ''),
        (13277, 14024, 'JAMAICA', ''),
        (14025, 14175, 'LABUAN', ''),
        (14176, 14652, 'LAGOS', ''),
        (14653, 16458, 'THE LEEWARD ISLANDS', 'Variant: LEEWARD ISLANDS'),
        (16459, 17300, 'MAURITIUS', ''),
        (17301, 17917, 'NATAL', ''),
        (17918, 18283, 'NEWFOUNDLAND', ''),
        (18284, 19425, 'NEW SOUTH WALES', ''),
        (19426, 19447, 'PITCAIRN ISLAND', 'Short section'),
        (19448, 19470, 'NORFOLK ISLAND', 'Short section'),
        (19471, 20148, 'NEW ZEALAND', ''),
        (20149, 20251, 'NORTHERN NIGERIA', ''),
        (20252, 20940, 'QUEENSLAND', ''),
        (20941, 21137, 'SEYCHELLES', ''),
        (21138, 21734, 'SIERRA LEONE', ''),
        (21735, 21763, 'SOUTH AFRICA', 'Short section'),
        (21764, 21952, 'BASUTOLAND', ''),
        (21953, 22058, 'RHODESIA', ''),
        (22059, 22808, 'SOUTH AUSTRALIA', ''),
        (22809, 23027, 'SOUTHERN NIGERIA', ''),
        (23028, 23690, 'STRAITS SETTLEMENTS', ''),
        (23691, 24240, 'TASMANIA', ''),
        (24241, 25326, 'TRINIDAD AND TOBAGO', 'Includes TRINIDAD and TOBAGO subsections'),
        (25327, 25516, 'TURKS AND CAICOS ISLANDS', ''),
        (25517, 26308, 'VICTORIA', ''),
        (26309, 27037, 'WESTERN AUSTRALIA', ''),
        (27038, 27195, 'WESTERN PACIFIC', ''),
        (27196, 27302, 'THE WINDWARD ISLANDS', 'Variant: WINDWARD ISLANDS'),
        (27303, 28207, 'GRENADE', 'OCR variant of GRENADA'),
        (28208, 28220, 'ZANZIBAR', 'Short section'),
        (28221, 28239, 'EAST AFRICA PROTECTORATE', 'Short section'),
        (28240, 28261, 'UGANDA', 'Short section'),
        (28262, 28271, 'BRUNEI', 'Short section'),
        (28272, 28509, 'NORTH BORNEO', ''),
        (28510, 28670, 'SARAWAK', ''),
        (28671, 28682, 'ADEN', 'Short section'),
        (28683, 28688, 'ASCENSION', 'Very short section'),
        (28689, 28692, 'TRISTAN D\'ACUNHA', 'Very short section'),
        (28693, 28717, 'WEI-HAI-WEI', 'Short section'),
    ]
    return colonies

def analyze_missing_colonies():
    """Analyze which of the originally missing 13 colonies were found"""
    colonies = get_final_colony_boundaries()
    colony_names = [c[2] for c in colonies]

    missing_original = [
        ('CANADA', 'DOMINION OF CANADA'),
        ('COLUMBIA', 'BRITISH COLUMBIA (province within DOMINION OF CANADA)'),
        ('GOLD COAST', 'THE GOLD COAST COLONY'),
        ('GRENADA', 'GRENADE'),
        ('LEEWARD ISLANDS', 'THE LEEWARD ISLANDS'),
        ('MALTA', 'NOT FOUND - No dedicated section in 1900'),
        ('MANITOBA', 'MANITOBA AND KEWATIN (province within DOMINION OF CANADA)'),
        ('SOUTH AUSTRALIA', 'SOUTH AUSTRALIA'),
        ('STRAITS SETTLEMENTS', 'STRAITS SETTLEMENTS'),
        ('TRINIDAD AND TOBAGO', 'TRINIDAD AND TOBAGO'),
        ('WINDWARD ISLANDS', 'THE WINDWARD ISLANDS'),
    ]

    return missing_original

if __name__ == '__main__':
    colonies = get_final_colony_boundaries()

    print(f"="*80)
    print(f"FINAL MANUALLY-VERIFIED COLONY LIST FOR 1900")
    print(f"="*80)
    print(f"\nTotal colonies found: {len(colonies)}\n")

    for start, end, name, notes in colonies:
        lines = end - start + 1
        print(f"{name:35s} start_line={start:5d}, end_line={end:5d} ({lines:5d} lines) {notes}")

    print(f"\n{'='*80}")
    print(f"ANALYSIS OF 13 ORIGINALLY MISSING COLONIES")
    print(f"={'='*80}\n")

    missing = analyze_missing_colonies()
    found_count = 0
    for original, found_as in missing:
        if 'NOT FOUND' in found_as:
            status = '✗ NOT FOUND'
        else:
            status = '✓ FOUND'
            found_count += 1
        print(f"{status:12s} {original:25s} → {found_as}")

    print(f"\n{'='*80}")
    print(f"SUMMARY: {found_count}/11 originally missing colonies were found")
    print(f"{'='*80}")
    print(f"\nNote: MALTA does not have a dedicated colony section in the 1900 Colonial")
    print(f"Office List. It only appears in the governors table (line 1550) but lacks")
    print(f"a full descriptive section like other colonies.")
