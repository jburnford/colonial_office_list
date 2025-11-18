#!/usr/bin/env python3
"""
Extract all colonies from Colonial Office List 1923 - CORRECTED VERSION
Includes Straits Settlements, Labuan, Brunei, and Federated Malay States
"""
import json
import os

# Define colony boundaries (line_start, line_end, colony_name, filename)
# Line numbers are 1-indexed to match the file
COLONIES_1923 = [
    (12707, 13106, "BAHAMAS", "bahamas.txt"),
    (13107, 13763, "BARBADOS", "barbados.txt"),
    (13764, 14280, "BERMUDA", "bermuda.txt"),
    (14281, 15314, "BRITISH GUIANA", "british_guiana.txt"),
    (15315, 19020, "BRITISH HONDURAS", "british_honduras.txt"),
    (19021, 20307, "CEYLON", "ceylon.txt"),
    (20308, 20977, "CYPRUS", "cyprus.txt"),
    (20978, 21280, "FALKLAND ISLANDS", "falkland_islands.txt"),
    (21281, 21947, "FIJI", "fiji.txt"),
    (21948, 22444, "THE GAMBIA", "gambia.txt"),
    (22445, 22682, "GIBRALTAR", "gibraltar.txt"),
    (22683, 23886, "THE GOLD COAST", "gold_coast.txt"),
    (23887, 24492, "HONG KONG", "hong_kong.txt"),
    (24493, 25720, "JAMAICA", "jamaica.txt"),
    (25721, 26356, "THE KENYA COLONY AND PROTECTORATE", "kenya.txt"),
    (26357, 28031, "THE LEEWARD ISLANDS", "leeward_islands.txt"),
    (28032, 28607, "MALTA", "malta.txt"),
    (28608, 31281, "MAURITIUS", "mauritius.txt"),
    (31282, 32225, "NIGERIA", "nigeria.txt"),
    (32226, 32520, "NYASALAND PROTECTORATE", "nyasaland.txt"),
    (32521, 32992, "ST. HELENA", "st_helena.txt"),
    (32993, 33498, "SIERRA LEONE", "sierra_leone.txt"),
    (33499, 36042, "SOMALILAND PROTECTORATE", "somaliland.txt"),
    (36043, 36351, "BASUTOLAND", "basutoland.txt"),
    (36352, 36570, "SWAZILAND", "swaziland.txt"),
    (36571, 37086, "RHODESIA", "rhodesia.txt"),
    (37087, 37928, "STRAITS SETTLEMENTS", "straits_settlements.txt"),
    (37929, 37979, "LABUAN", "labuan.txt"),
    (37980, 38039, "BRUNEI", "brunei.txt"),
    (38042, 38970, "FEDERATED MALAY STATES", "federated_malay_states.txt"),
    (38971, 39444, "TANGANYIKA TERRITORY", "tanganyika.txt"),
    (39445, 41298, "TRINIDAD AND TOBAGO", "trinidad_tobago.txt"),
    (41299, 41722, "UGANDA", "uganda.txt"),
    (41723, 42089, "WEIHAIWEI", "weihaiwei.txt"),
    (42090, 43090, "THE WINDWARD ISLANDS", "windward_islands.txt"),
    (43091, 43679, "ZANZIBAR", "zanzibar.txt"),
    (43680, 44372, "PALESTINE", "palestine.txt"),
    (44373, 44399, "ADEN", "aden.txt"),
]

def extract_colonies():
    """Extract each colony to a separate file"""

    input_file = "/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1923/olmocr_results.md"
    output_dir = "/home/user/colonial_office_list/output_3/1923_manual_parsed"

    # Read the entire file
    print(f"Reading {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    print(f"Total lines in file: {len(lines)}")

    # Extract each colony
    colonies_info = []

    for start_line, end_line, colony_name, filename in COLONIES_1923:
        print(f"Extracting {colony_name} (lines {start_line}-{end_line})...")

        # Extract lines (convert from 1-indexed to 0-indexed)
        colony_lines = lines[start_line-1:end_line]

        # Write to file
        output_path = os.path.join(output_dir, filename)
        with open(output_path, 'w', encoding='utf-8') as f:
            f.writelines(colony_lines)

        # Calculate stats
        line_count = end_line - start_line + 1
        char_count = sum(len(line) for line in colony_lines)

        colonies_info.append({
            "name": colony_name,
            "filename": filename,
            "start_line": start_line,
            "end_line": end_line,
            "line_count": line_count,
            "char_count": char_count
        })

        print(f"  -> Wrote {line_count} lines to {filename}")

    return colonies_info

def create_summary_json(colonies_info):
    """Create summary JSON file"""

    summary = {
        "year": 1923,
        "total_colonies": len(colonies_info),
        "source_file": "historical_document_pipeline/processed_pdfs/colonial-office-list-1923/olmocr_results.md",
        "extraction_method": "manual_parsing",
        "historical_context": "Post-WWI stabilization, League of Nations mandates established",
        "notes": [
            "RHODESIA includes both Southern and Northern Rhodesia",
            "TANGANYIKA is a League of Nations mandate territory (former German East Africa)",
            "PALESTINE is a League of Nations mandate territory (former Ottoman territory)",
            "WEIHAIWEI was leased from China (to be returned in 1923)",
            "THE LEEWARD ISLANDS is a federal colony of multiple islands",
            "THE WINDWARD ISLANDS comprises St. Lucia, St. Vincent, and Grenada",
            "BASUTOLAND and SWAZILAND are High Commission Territories",
            "STRAITS SETTLEMENTS comprises Singapore, Penang, Malacca, and dependencies",
            "FEDERATED MALAY STATES comprises Perak, Selangor, Negri Sembilan, and Pahang",
            "LABUAN and BRUNEI are protected states in Borneo",
            "THE GOLD COAST includes British mandated territory of Togoland"
        ],
        "colonies": colonies_info
    }

    output_path = "/home/user/colonial_office_list/output_3/1923_manual_parsed.json"
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(summary, f, indent=2)

    print(f"\nSummary written to {output_path}")
    return summary

def main():
    print("="*80)
    print("COLONIAL OFFICE LIST 1923 - MANUAL PARSING (CORRECTED)")
    print("="*80)
    print()

    colonies_info = extract_colonies()
    summary = create_summary_json(colonies_info)

    print()
    print("="*80)
    print("EXTRACTION COMPLETE")
    print("="*80)
    print(f"Total colonies extracted: {summary['total_colonies']}")
    print(f"Output directory: output_3/1923_manual_parsed/")
    print(f"Summary file: output_3/1923_manual_parsed.json")
    print()

    # List all colonies by region
    print("Colonies extracted by region:")
    print()

    caribbean = [c for c in colonies_info if c['name'] in ['BAHAMAS', 'BARBADOS', 'BERMUDA', 'BRITISH GUIANA', 'BRITISH HONDURAS', 'JAMAICA', 'THE LEEWARD ISLANDS', 'TRINIDAD AND TOBAGO', 'THE WINDWARD ISLANDS']]
    print(f"CARIBBEAN & ATLANTIC ({len(caribbean)}):")
    for c in caribbean:
        print(f"  - {c['name']}")

    print()
    africa_west = [c for c in colonies_info if c['name'] in ['THE GAMBIA', 'THE GOLD COAST', 'NIGERIA', 'SIERRA LEONE']]
    print(f"AFRICA - WEST ({len(africa_west)}):")
    for c in africa_west:
        print(f"  - {c['name']}")

    print()
    africa_east = [c for c in colonies_info if c['name'] in ['THE KENYA COLONY AND PROTECTORATE', 'NYASALAND PROTECTORATE', 'SOMALILAND PROTECTORATE', 'TANGANYIKA TERRITORY', 'UGANDA', 'ZANZIBAR']]
    print(f"AFRICA - EAST ({len(africa_east)}):")
    for c in africa_east:
        print(f"  - {c['name']}")

    print()
    africa_south = [c for c in colonies_info if c['name'] in ['BASUTOLAND', 'RHODESIA', 'ST. HELENA', 'SWAZILAND']]
    print(f"AFRICA - SOUTHERN ({len(africa_south)}):")
    for c in africa_south:
        print(f"  - {c['name']}")

    print()
    asia = [c for c in colonies_info if c['name'] in ['CEYLON', 'HONG KONG', 'WEIHAIWEI', 'STRAITS SETTLEMENTS', 'FEDERATED MALAY STATES', 'LABUAN', 'BRUNEI']]
    print(f"ASIA-PACIFIC ({len(asia)}):")
    for c in asia:
        print(f"  - {c['name']}")

    print()
    med_me = [c for c in colonies_info if c['name'] in ['CYPRUS', 'GIBRALTAR', 'MALTA', 'PALESTINE', 'ADEN']]
    print(f"MEDITERRANEAN & MIDDLE EAST ({len(med_me)}):")
    for c in med_me:
        print(f"  - {c['name']}")

    print()
    other = [c for c in colonies_info if c['name'] in ['FALKLAND ISLANDS', 'FIJI', 'MAURITIUS']]
    print(f"OTHER ({len(other)}):")
    for c in other:
        print(f"  - {c['name']}")

    return summary

if __name__ == "__main__":
    main()
