#!/usr/bin/env python3
"""Extract all colonies from 1890 Colonial Office List"""

import json
import os
import re

# Define all colony boundaries based on manual analysis
COLONIES = [
    {"name": "BAHAMAS", "start": 1531, "end": 1885},
    {"name": "BARBADOS", "start": 1886, "end": 2538},
    {"name": "BASUTOLAND", "start": 2539, "end": 2663},
    {"name": "BERMUDA", "start": 2664, "end": 3002},
    {"name": "BRITISH BECHUANALAND", "start": 3003, "end": 3184},
    {"name": "BRITISH GUIANA", "start": 3185, "end": 3897},
    {"name": "BRITISH HONDURAS", "start": 3898, "end": 4341},
    {"name": "BRITISH NEW GUINEA", "start": 4342, "end": 4381},
    {"name": "DOMINION OF CANADA", "start": 4382, "end": 7927},
    {"name": "CAPE OF GOOD HOPE", "start": 7928, "end": 9784},
    {"name": "CEYLON", "start": 9785, "end": 10629},
    {"name": "FALKLAND ISLANDS", "start": 10630, "end": 11195},
    {"name": "THE GAMBIA", "start": 11196, "end": 11405},
    {"name": "GIBRALTAR", "start": 11406, "end": 11583},
    {"name": "THE GOLD COAST COLONY", "start": 11584, "end": 11945},
    {"name": "HELIGOLAND", "start": 11946, "end": 12062},
    {"name": "HONG KONG", "start": 12063, "end": 12430},
    {"name": "JAMAICA", "start": 12431, "end": 13243},
    {"name": "LABUAN", "start": 13244, "end": 13709},
    {"name": "THE LEEWARD ISLANDS", "start": 13710, "end": 13889},
    {"name": "ANTIGUA", "start": 13890, "end": 14486},
    {"name": "DOMINICA", "start": 14487, "end": 14812},
    {"name": "VIRGIN ISLANDS", "start": 14813, "end": 15413},
    {"name": "MAURITIUS", "start": 15414, "end": 16340},
    {"name": "SEYCHELLES ISLANDS", "start": 16341, "end": 16394},
    {"name": "RODRIGUES", "start": 16395, "end": 16422},
    {"name": "NATAL", "start": 16423, "end": 17069},
    {"name": "NEWFOUNDLAND", "start": 17070, "end": 18511},
    {"name": "PITCAIRN ISLAND", "start": 18512, "end": 18515},
    {"name": "NORFOLK ISLAND", "start": 18516, "end": 18522},
    {"name": "NEW ZEALAND", "start": 18523, "end": 19384},
    {"name": "QUEENSLAND", "start": 19385, "end": 20507},
    {"name": "SOUTH AUSTRALIA", "start": 20508, "end": 21538},
    {"name": "STRAITS SETTLEMENTS", "start": 21539, "end": 22802},
    {"name": "TRINIDAD AND TOBAGO", "start": 22803, "end": 22804},
    {"name": "TRINIDAD", "start": 22805, "end": 23725},
    {"name": "TOBAGO", "start": 23726, "end": 23886},
    {"name": "TURKS AND CAICOS ISLANDS", "start": 23887, "end": 24125},
    {"name": "VICTORIA", "start": 24126, "end": 25540},
    {"name": "WESTERN AUSTRALIA", "start": 25541, "end": 26152},
    {"name": "THE WINDWARD ISLANDS", "start": 26153, "end": 26212},
    {"name": "GRENADA", "start": 26213, "end": 26552},
    {"name": "ST. LUCIA", "start": 26553, "end": 27058},
    {"name": "ST. VINCENT", "start": 27059, "end": 27392},
    {"name": "ZULULAND", "start": 27393, "end": 27493},
    # Appendix to Part II
    {"name": "IMPERIAL BRITISH EAST AFRICAN COMPANY", "start": 27498, "end": 27517},
    {"name": "BRITISH NORTH BORNEO", "start": 27518, "end": 27727},
    {"name": "SARAWAK", "start": 27728, "end": 27845},
    {"name": "BRUNEI", "start": 27846, "end": 27849},
    {"name": "CYPRUS", "start": 27850, "end": 28320},
    {"name": "NIGER PROTECTORATE", "start": 28321, "end": 28384},
    {"name": "SOUTH AFRICA", "start": 28385, "end": 28408},
    {"name": "WESTERN PACIFIC", "start": 28409, "end": 28429},
    {"name": "ASCENSION", "start": 28430, "end": 28439},
    {"name": "MISCELLANEOUS ISLANDS", "start": 28440, "end": 28449},
]

def sanitize_filename(name):
    """Convert colony name to safe filename"""
    # Convert to lowercase and replace spaces with underscores
    filename = name.lower().replace(" ", "_").replace(".", "")
    # Remove special characters
    filename = re.sub(r'[^a-z0-9_]', '', filename)
    return f"{filename}.txt"

def extract_colonies():
    """Extract all colonies to separate files"""
    input_file = "/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1890/olmocr_results.md"
    output_dir = "/home/user/colonial_office_list/output_3/1890_manual_parsed"

    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)

    # Read the entire file
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Extract each colony
    results = []
    for colony in COLONIES:
        filename = sanitize_filename(colony['name'])
        filepath = os.path.join(output_dir, filename)

        # Extract lines (adjusting for 0-based indexing)
        start_idx = colony['start'] - 1
        end_idx = colony['end']
        colony_lines = lines[start_idx:end_idx]

        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.writelines(colony_lines)

        line_count = len(colony_lines)
        print(f"Extracted {colony['name']}: {line_count} lines -> {filename}")

        results.append({
            "name": colony['name'],
            "start_line": colony['start'],
            "end_line": colony['end'],
            "filename": filename,
            "line_count": line_count
        })

    return results

def create_metadata(colonies_data):
    """Create JSON metadata file"""
    metadata = {
        "year": 1890,
        "source_file": "historical_document_pipeline/processed_pdfs/colonial-office-list-1890/olmocr_results.md",
        "total_colonies": len(colonies_data),
        "colonies": colonies_data
    }

    output_file = "/home/user/colonial_office_list/output_3/1890_manual_parsed.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)

    print(f"\nCreated metadata file: {output_file}")
    print(f"Total colonies extracted: {len(colonies_data)}")

    return metadata

if __name__ == "__main__":
    print("Extracting 1890 colonies...")
    print("=" * 60)
    colonies_data = extract_colonies()
    print("=" * 60)
    metadata = create_metadata(colonies_data)
    print("\nExtraction complete!")
