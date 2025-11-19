#!/usr/bin/env python3
"""
Script to find colony section boundaries in the 1959 Colonial Office List
by searching for colony header patterns.
"""

import re

def find_colony_boundaries(filename):
    """Find all potential colony section starts."""

    # Based on the table of contents, these are the colonies we expect
    expected_colonies = [
        "ADEN",
        "BAHAMA ISLANDS",
        "BERMUDA",
        "BRITISH GUIANA",
        "BRITISH HONDURAS",
        "BRUNEI",
        "CHRISTMAS ISLAND",
        "CYPRUS",
        "FALKLAND ISLANDS",
        "FIJI",
        "GAMBIA",
        "GIBRALTAR",
        "HONG KONG",
        "KENYA",
        "LEEWARD ISLANDS",
        "MALTA",
        "MAURITIUS",
        "NIGERIA",
        "NORTH BORNEO",
        "RHODESIA AND NYASALAND",
        "NORTHERN RHODESIA",
        "NYASALAND",
        "ST. HELENA",
        "SARAWAK",
        "SEYCHELLES",
        "SIERRA LEONE",
        "SINGAPORE",
        "SOMALILAND",
        "TANGANYIKA",
        "TONGA",
        "UGANDA",
        "WEST INDIES",
        "WESTERN PACIFIC",
        "ZANZIBAR",
        "MISCELLANEOUS ISLANDS",
        "HIGH COMMISSION TERRITORIES"
    ]

    boundaries = []

    with open(filename, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, start=1):
            # The file doesn't have line number prefixes - just the content
            content = line.strip()

            # Look for exact colony names at start of line
            # We want lines that are JUST the colony name (possibly with qualifier)
            if content in ["ADEN COLONY", "ADEN"]:
                boundaries.append((line_num, "ADEN", content))
            elif content == "BAHAMA ISLANDS":
                boundaries.append((line_num, "BAHAMA ISLANDS", content))
            elif content == "BERMUDA":
                boundaries.append((line_num, "BERMUDA", content))
            elif content == "BRITISH GUIANA":
                boundaries.append((line_num, "BRITISH GUIANA", content))
            elif content == "BRITISH HONDURAS":
                boundaries.append((line_num, "BRITISH HONDURAS", content))
            elif content == "BRUNEI":
                boundaries.append((line_num, "BRUNEI", content))
            elif content == "CHRISTMAS ISLAND":
                boundaries.append((line_num, "CHRISTMAS ISLAND", content))
            elif content == "CYPRUS":
                boundaries.append((line_num, "CYPRUS", content))
            elif content in ["FALKLAND ISLANDS", "FALKLAND ISLANDS AND DEPENDENCIES"]:
                boundaries.append((line_num, "FALKLAND ISLANDS", content))
            elif content in ["FIJI", "FIJI (AND PITCAIRN ISLANDS GROUP)"]:
                boundaries.append((line_num, "FIJI", content))
            elif content == "GAMBIA":
                boundaries.append((line_num, "GAMBIA", content))
            elif content == "GIBRALTAR":
                boundaries.append((line_num, "GIBRALTAR", content))
            elif content == "HONG KONG":
                boundaries.append((line_num, "HONG KONG", content))
            elif content == "KENYA":
                boundaries.append((line_num, "KENYA", content))
            elif content in ["LEEWARD ISLANDS", "LEEWARD ISLANDS (BRITISH VIRGIN ISLANDS)"]:
                boundaries.append((line_num, "LEEWARD ISLANDS", content))
            elif content == "MALTA":
                boundaries.append((line_num, "MALTA", content))
            elif content == "MAURITIUS":
                boundaries.append((line_num, "MAURITIUS", content))
            elif content in ["NIGERIA", "FEDERATION OF NIGERIA"]:
                boundaries.append((line_num, "NIGERIA", content))
            elif content == "NORTH BORNEO":
                boundaries.append((line_num, "NORTH BORNEO", content))
            elif content in ["FEDERATION OF RHODESIA AND NYASALAND", "RHODESIA AND NYASALAND"]:
                boundaries.append((line_num, "RHODESIA AND NYASALAND", content))
            elif content == "NORTHERN RHODESIA":
                boundaries.append((line_num, "NORTHERN RHODESIA", content))
            elif content in ["NYASALAND", "NYASALAND PROTECTORATE"]:
                boundaries.append((line_num, "NYASALAND", content))
            elif content in ["ST. HELENA", "ST. HELENA (WITH ASCENSION AND TRISTAN DA CUNHA)"]:
                boundaries.append((line_num, "ST. HELENA", content))
            elif content == "SARAWAK":
                boundaries.append((line_num, "SARAWAK", content))
            elif content == "SEYCHELLES":
                boundaries.append((line_num, "SEYCHELLES", content))
            elif content == "SIERRA LEONE":
                boundaries.append((line_num, "SIERRA LEONE", content))
            elif content == "SINGAPORE":
                boundaries.append((line_num, "SINGAPORE", content))
            elif content in ["SOMALILAND", "SOMALILAND PROTECTORATE"]:
                boundaries.append((line_num, "SOMALILAND", content))
            elif content == "TANGANYIKA":
                boundaries.append((line_num, "TANGANYIKA", content))
            elif content == "TONGA":
                boundaries.append((line_num, "TONGA", content))
            elif content == "UGANDA":
                boundaries.append((line_num, "UGANDA", content))
            elif content in ["THE WEST INDIES", "WEST INDIES", "THE WEST INDIES (FEDERATION)"]:
                boundaries.append((line_num, "WEST INDIES", content))
            elif content in ["WESTERN PACIFIC", "WESTERN PACIFIC HIGH COMMISSION"]:
                boundaries.append((line_num, "WESTERN PACIFIC", content))
            elif content == "ZANZIBAR":
                boundaries.append((line_num, "ZANZIBAR", content))
            elif content == "MISCELLANEOUS ISLANDS":
                boundaries.append((line_num, "MISCELLANEOUS ISLANDS", content))
            elif content in ["HIGH COMMISSION TERRITORIES", "THE HIGH COMMISSION TERRITORIES"]:
                boundaries.append((line_num, "HIGH COMMISSION TERRITORIES", content))

    return boundaries

if __name__ == "__main__":
    filename = "/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1959/olmocr_results.md"

    boundaries = find_colony_boundaries(filename)

    # Filter to only Part II (lines 3000-29000 approximately)
    part_ii_boundaries = [(line_num, name, content) for line_num, name, content in boundaries
                          if 3000 <= line_num <= 29000]

    print(f"Found {len(part_ii_boundaries)} colony sections in Part II:")
    print()
    for line_num, name, content in part_ii_boundaries:
        print(f"Line {line_num:5d}: {name:30s} ({content})")
