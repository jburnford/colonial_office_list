#!/usr/bin/env python3
"""
Extract colonies from Colonial Office List 1920
Manually identifies colony boundaries and extracts each to a separate file
"""

import json
import os
import re

def main():
    input_file = 'historical_document_pipeline/processed_pdfs/colonial-office-list-1920/olmocr_results.md'
    output_dir = 'output_3/1920_manual_parsed'

    # Read the entire file
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Define colony boundaries based on manual inspection
    # Format: (name, start_line, next_colony_start_line or end)
    # Line numbers are 1-indexed
    colonies = [
        ("AUSTRALIA", 4001, 11562),
        ("BAHAMAS", 11562, 11943),
        ("BARBADOS", 11943, 12600),
        ("BERMUDA", 12600, 12990),
        ("BRITISH GUIANA", 12990, 13751),
        ("BRITISH HONDURAS", 13751, 14067),
        ("CANADA", 14067, 17474),
        ("CEYLON", 17474, 18419),
        ("CYPRUS", 18419, 19248),
        ("EAST AFRICA PROTECTORATE", 19248, 19927),
        ("FALKLAND ISLANDS", 19927, 20224),
        ("FIJI", 20224, 20858),
        ("GAMBIA", 20858, 21385),
        ("GIBRALTAR", 21385, 21619),
        ("GOLD COAST", 21619, 21906),
        ("TOGOLAND", 21906, 22462),
        ("HONG KONG", 22462, 23028),
        ("JAMAICA", 23028, 23996),
        ("LEEWARD ISLANDS", 23996, 25678),
        ("MALTA", 25678, 26242),
        ("MAURITIUS", 26242, 27209),
        ("NEWFOUNDLAND", 27209, 27642),
        ("NEW ZEALAND", 27642, 28781),
        ("NIGERIA", 28781, 29720),
        ("NYASALAND PROTECTORATE", 29720, 30050),
        ("ST HELENA", 30050, 30223),
        ("SEYCHELLES", 30223, 30550),
        ("SIERRA LEONE", 30550, 31060),
        ("SOMALILAND PROTECTORATE", 31060, 31259),
        ("SOUTH AFRICA", 31259, 33611),
        ("BASUTOLAND", 33611, 33912),
        ("SWAZILAND", 33912, 34635),
        ("STRAITS SETTLEMENTS", 34635, 35966),
        ("FEDERATED MALAY STATES", 35966, 36382),
        ("TANGANYIKA TERRITORY", 36382, 36655),
        ("TRINIDAD", 36655, 36830),
        ("TOBAGO", 36830, 37868),
        ("TURKS AND CAICOS ISLANDS", 37868, 37999),
        ("UGANDA", 37999, 38371),
        ("WEIHAIWEI", 38371, 38441),
        ("WESTERN PACIFIC", 38441, 38844),
        ("WINDWARD ISLANDS", 38844, 39803),
        ("ZANZIBAR", 39803, 40040),
        ("NORTH BORNEO", 40040, 40253),
        ("SARAWAK", 40253, 40505),
        ("ADEN", 40505, 40515),
        ("ASCENSION", 40515, 40519),
        ("TRISTAN DA CUNHA", 40519, 40530),
    ]

    metadata = {
        "document": "Colonial Office List 1920",
        "year": 1920,
        "significance": "League of Nations mandates formally established (Tanganyika, Togoland, Cameroons)",
        "extraction_date": "2025-11-18",
        "total_colonies": len(colonies),
        "colonies": []
    }

    # Extract each colony
    for i, (name, start, end) in enumerate(colonies):
        print(f"Extracting: {name} (lines {start}-{end})")

        # Extract lines (convert from 1-indexed to 0-indexed)
        colony_lines = lines[start-1:end-1]

        # Count non-empty lines
        content_lines = sum(1 for line in colony_lines if line.strip())

        # Create filename
        filename = name.replace(' ', '_').replace('.', '') + '.md'
        filepath = os.path.join(output_dir, filename)

        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(colony_lines)

        # Add to metadata
        metadata["colonies"].append({
            "name": name,
            "file": filename,
            "start_line": start,
            "end_line": end,
            "total_lines": end - start,
            "content_lines": content_lines
        })

    # Add notes about mandates
    metadata["notes"] = [
        "This is the Colonial Office List from 1920, after Treaty of Versailles (1919)",
        "League of Nations mandates appear in this list:",
        "- TANGANYIKA TERRITORY (formerly German East Africa) - British mandate",
        "- TOGOLAND (British zone) - British mandate, administered jointly with French",
        "- CAMEROONS (British zone) - mentioned within NIGERIA section, British mandate",
        "Palestine, Transjordan, and Iraq/Mesopotamia were under Foreign Office/India Office, not Colonial Office",
        "Document includes dominions (Australia, Canada, New Zealand, South Africa)",
        "Includes protectorates, territories, and crown colonies"
    ]

    metadata["league_of_nations_mandates"] = {
        "tanganyika_territory": {
            "status": "British mandate under League of Nations",
            "notes": "Appears as separate territory section (line 36382)",
            "former_name": "German East Africa",
            "mandate_class": "Class B Mandate"
        },
        "togoland": {
            "status": "British mandate under League of Nations (British zone)",
            "notes": "Appears as separate section (line 21906); administered jointly with France",
            "former_name": "German Togoland",
            "mandate_class": "Class B Mandate"
        },
        "cameroons": {
            "status": "British mandate under League of Nations (British zone)",
            "notes": "Discussed within NIGERIA section; administered by Governor of Nigeria",
            "former_name": "German Kamerun",
            "mandate_class": "Class B Mandate"
        },
        "palestine": {
            "status": "Not in Colonial Office List - under Foreign Office jurisdiction in 1920",
            "notes": "Palestine mandate not yet established under Colonial Office in 1920"
        },
        "transjordan": {
            "status": "Not in Colonial Office List - under Foreign Office jurisdiction in 1920",
            "notes": "Transjordan not yet separately established in 1920"
        },
        "iraq_mesopotamia": {
            "status": "Not in Colonial Office List - under India Office jurisdiction in 1920",
            "notes": "Mesopotamia/Iraq under India Office control in 1920, not Colonial Office"
        }
    }

    # Write metadata JSON
    json_path = 'output_3/1920_manual_parsed.json'
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)

    print(f"\nExtraction complete!")
    print(f"Total colonies extracted: {len(colonies)}")
    print(f"Metadata written to: {json_path}")

    # Print mandates found
    print("\nLeague of Nations Mandates identified:")
    print("- TANGANYIKA TERRITORY (separate section)")
    print("- TOGOLAND (separate section)")
    print("- CAMEROONS (within NIGERIA section)")

if __name__ == '__main__':
    main()
