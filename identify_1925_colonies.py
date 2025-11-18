#!/usr/bin/env python3
"""
Script to identify colony section boundaries in the 1925 Colonial Office List.
This script helps with MANUAL identification by searching for likely colony headers.
"""

import re

# Read the file
file_path = "/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1925/olmocr_results.md"

print("Scanning 1925 Colonial Office List for colony headers...\n")

# Known colonies to search for (based on 1924 and historical context)
known_colonies = [
    "BAHAMAS", "BARBADOS", "BERMUDA", "BRITISH GUIANA", "BRITISH HONDURAS",
    "CEYLON", "CYPRUS", "FALKLAND", "FIJI", "GAMBIA", "GIBRALTAR",
    "GOLD COAST", "GRENADA", "HONG KONG", "JAMAICA", "KENYA",
    "LEEWARD ISLANDS", "MALTA", "MAURITIUS", "NIGERIA", "NORTHERN RHODESIA",
    "NYASALAND", "PALESTINE", "SEYCHELLES", "SIERRA LEONE", "SOUTHERN RHODESIA",
    "ST. HELENA", "ST. LUCIA", "ST. VINCENT", "STRAITS SETTLEMENTS",
    "TANGANYIKA", "TRINIDAD", "UGANDA", "WINDWARD ISLANDS", "ZANZIBAR",
    "FEDERATED MALAY STATES", "UNFEDERATED MALAY STATES", "ASHANTI",
    "SOMALILAND", "BASUTOLAND", "BECHUANALAND", "SWAZILAND", "WEIHAIWEI",
    "LABUAN", "NEW GUINEA", "NAURU"
]

with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

found_headers = []

for i, line in enumerate(lines, 1):
    line_stripped = line.strip()

    # Look for lines that are likely colony headers
    # Pattern 1: Lines with colony names, possibly with asterisks or dots
    for colony in known_colonies:
        # Check for exact matches with various patterns
        patterns = [
            f"^{colony}\\.$",  # COLONY.
            f"^\\*{colony}\\.\\*$",  # *COLONY.*
            f"^\\*\\*{colony}\\.\\*\\*$",  # **COLONY.**
            f"^{colony}\\s*$",  # COLONY (no period)
            f"^THE TERRITORY OF {colony}",  # THE TERRITORY OF COLONY
            f"^{colony} PROTECTORATE",  # COLONY PROTECTORATE
            f"^{colony} COLONY",  # COLONY COLONY
        ]

        for pattern in patterns:
            if re.match(pattern, line_stripped, re.IGNORECASE):
                found_headers.append((i, line_stripped))
                break

# Also look for specific multi-word colonies
multiword_patterns = [
    (r"^BRITISH GUIANA", "BRITISH GUIANA"),
    (r"^BRITISH HONDURAS", "BRITISH HONDURAS"),
    (r"^GOLD COAST", "GOLD COAST"),
    (r"^HONG KONG", "HONG KONG"),
    (r"^NORTHERN RHODESIA", "NORTHERN RHODESIA"),
    (r"^SOUTHERN RHODESIA", "SOUTHERN RHODESIA"),
    (r"^SIERRA LEONE", "SIERRA LEONE"),
    (r"^ST\. HELENA", "ST. HELENA"),
    (r"^ST\. LUCIA", "ST. LUCIA"),
    (r"^ST\. VINCENT", "ST. VINCENT"),
    (r"^STRAITS SETTLEMENTS", "STRAITS SETTLEMENTS"),
    (r"^FEDERATED MALAY STATES", "FEDERATED MALAY STATES"),
    (r"^LEEWARD ISLANDS", "LEEWARD ISLANDS"),
    (r"^WINDWARD ISLANDS", "WINDWARD ISLANDS"),
    (r"^TRINIDAD AND TOBAGO", "TRINIDAD AND TOBAGO"),
    (r"^TANGANYIKA TERRITORY", "TANGANYIKA TERRITORY"),
    (r"^NYASALAND PROTECTORATE", "NYASALAND PROTECTORATE"),
    (r"^KENYA COLONY", "KENYA COLONY"),
    (r"^THE TERRITORY OF NEW GUINEA", "NEW GUINEA"),
]

for i, line in enumerate(lines, 1):
    line_stripped = line.strip()
    for pattern, name in multiword_patterns:
        if re.match(pattern + r"[\.\*\s]*$", line_stripped, re.IGNORECASE) and len(line_stripped) < 60:
            found_headers.append((i, line_stripped))

# Remove duplicates and sort
found_headers = sorted(list(set(found_headers)))

print(f"Found {len(found_headers)} potential colony headers:\n")
for line_num, header in found_headers:
    print(f"Line {line_num:5d}: {header}")

print(f"\n\nTotal: {len(found_headers)} headers found")
