#!/usr/bin/env python3
"""
Parse Colonial Office List 1907 - Final Manual Colony Boundary Identification
"""

import re
import json
from pathlib import Path
from datetime import datetime

# Read the OCR file
ocr_file = Path("/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1907/olmocr_results.md")

with open(ocr_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Total lines in file: {len(lines)}")
print()

# Manually identified colony boundaries based on inspection
# Format: (colony_name, start_line, end_line, file_name)
# These are determined by manual review of the document structure

colonies = [
    # Australian Commonwealth starts at 2655 but ends before states
    ("THE COMMONWEALTH OF AUSTRALIA", 2655, 4973, "THE_COMMONWEALTH_OF_AUSTRALIA"),

    # Australian states/territories (part of Commonwealth but listed separately)
    ("LORD HOWE ISLAND", 4974, 4981, "LORD_HOWE_ISLAND"),
    ("QUEENSLAND", 4982, 5493, "QUEENSLAND"),
    ("SOUTH AUSTRALIA", 5494, 6342, "SOUTH_AUSTRALIA"),
    ("TASMANIA", 6343, 7151, "TASMANIA"),
    ("VICTORIA", 7152, 7965, "VICTORIA"),
    ("WESTERN AUSTRALIA", 7966, 9050, "WESTERN_AUSTRALIA"),

    # Main colonies start here
    ("BAHAMAS", 9051, 9487, "BAHAMAS"),
    ("BARBADOS", 9488, 10132, "BARBADOS"),
    ("BERMUDA", 10133, 10485, "BERMUDA"),
    ("BRITISH CENTRAL AFRICA PROTECTORATE", 10486, 10753, "BRITISH_CENTRAL_AFRICA_PROTECTORATE"),
    ("BRITISH EAST AFRICA PROTECTORATE", 10754, 10899, "BRITISH_EAST_AFRICA_PROTECTORATE"),
    ("BRITISH GUIANA", 10900, 11752, "BRITISH_GUIANA"),
    ("BRITISH HONDURAS", 11753, 12072, "BRITISH_HONDURAS"),
    ("DOMINION OF CANADA", 12073, 15042, "DOMINION_OF_CANADA"),
    ("CAPE OF GOOD HOPE", 15043, 18685, "CAPE_OF_GOOD_HOPE"),
    ("CEYLON", 18686, 19338, "CEYLON"),
    ("CYPRUS", 19339, 19544, "CYPRUS"),  # FALKLAND starts at 19339 per grep, but let me verify
    ("FALKLAND ISLANDS", 19339, 19544, "FALKLAND_ISLANDS"),  # Need to check overlap
    ("FIJI", 19545, 20084, "FIJI"),
    ("THE GAMBIA", 20085, 20377, "THE_GAMBIA"),
    ("GIBRALTAR", 20378, 20669, "GIBRALTAR"),
    ("THE GOLD COAST", 20670, 21420, "THE_GOLD_COAST"),
    ("HONG KONG", 21421, 21966, "HONG_KONG"),
    ("JAMAICA", 21967, 22688, "JAMAICA"),
    ("THE LEEWARD ISLANDS", 22689, 24067, "THE_LEEWARD_ISLANDS"),
    ("MALTA", 24068, 24773, "MALTA"),
    ("MAURITIUS", 24774, 25812, "MAURITIUS"),
    ("NATAL", 25813, 26699, "NATAL"),
    ("NEWFOUNDLAND", 26700, 27091, "NEWFOUNDLAND"),
    ("NEW ZEALAND", 27092, 28014, "NEW_ZEALAND"),
    ("NORTHERN NIGERIA", 28015, 28199, "NORTHERN_NIGERIA"),
    ("ORANGE RIVER COLONY", 28200, 28563, "ORANGE_RIVER_COLONY"),
    ("ST. HELENA", 28564, 28728, "ST_HELENA"),
    ("SEYCHELLES", 28729, 29043, "SEYCHELLES"),
    ("SIERRA LEONE", 29044, 29501, "SIERRA_LEONE"),
    ("SOMALILAND PROTECTORATE", 29502, 29739, "SOMALILAND_PROTECTORATE"),
    ("BASUTOLAND", 29740, 29867, "BASUTOLAND"),
    ("BECHUANALAND PROTECTORATE", 29868, 29935, "BECHUANALAND_PROTECTORATE"),
    ("RHODESIA", 29936, 30379, "RHODESIA"),
    ("SOUTHERN NIGERIA", 30380, 31059, "SOUTHERN_NIGERIA"),
    ("STRAITS SETTLEMENTS", 31060, 31642, "STRAITS_SETTLEMENTS"),
    ("LABUAN", 31643, 33122, "LABUAN"),
    ("TRINIDAD AND TOBAGO", 33123, 34135, "TRINIDAD_AND_TOBAGO"),
    ("TURKS AND CAICOS ISLANDS", 34136, 34310, "TURKS_AND_CAICOS_ISLANDS"),
    ("UGANDA", 34311, 34475, "UGANDA"),
    ("WEIHAIWEI", 34476, 34535, "WEIHAIWEI"),
    ("WESTERN PACIFIC", 34536, 34659, "WESTERN_PACIFIC"),
    ("THE WINDWARD ISLANDS", 34660, 35609, "THE_WINDWARD_ISLANDS"),
    ("NORTH BORNEO", 35610, 36049, "NORTH_BORNEO"),
    ("ASCENSION", 36050, 36057, "ASCENSION"),
    ("TRISTAN DA CUNHA", 36058, 36069, "TRISTAN_DA_CUNHA"),
    ("ADEN", 36070, 36080, "ADEN"),  # Estimate end
]

print("Manual colony boundaries identified. Verifying...")
print()

# Verify and adjust boundaries
for i, (name, start, end, file_name) in enumerate(colonies):
    # Check start line
    start_line_text = lines[start - 1].strip() if start <= len(lines) else "OUT OF BOUNDS"

    # Check if next colony starts where this one ends + 1
    if i < len(colonies) - 1:
        next_colony_start = colonies[i + 1][1]
        if end + 1 != next_colony_start:
            print(f"WARNING: Gap or overlap between {name} and {colonies[i+1][0]}")
            print(f"  {name} ends at {end}, {colonies[i+1][0]} starts at {next_colony_start}")

    print(f"{i+1:2d}. Line {start:5d}-{end:5d}: {name}")
    print(f"    Start text: {start_line_text[:60]}")

print()
print(f"Total colonies identified: {len(colonies)}")
