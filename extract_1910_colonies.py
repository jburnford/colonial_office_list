#!/usr/bin/env python3
"""Extract colonies from Colonial Office List 1910"""

import json
import os

# Define colony boundaries (line numbers)
# Format: (name, start_line, end_line or None for next colony)
colonies = [
    ("BAHAMAS", 10319, 10681),
    ("BARBADOS", 10681, 11259),
    ("BERMUDA", 11259, 11613),
    ("BRITISH_GUIANA", 11613, 12457),
    ("BRITISH_HONDURAS", 12457, 18615),
    ("CEYLON", 18615, 19416),
    ("CYPRUS", 19416, 20150),
    ("EAST_AFRICA_PROTECTORATE", 20150, 20536),
    ("FALKLAND_ISLANDS", 20536, 20714),
    ("FIJI", 20714, 21291),
    ("THE_GAMBIA", 21291, 21699),
    ("GIBRALTAR", 21699, 21968),
    ("THE_GOLD_COAST", 21968, 22696),
    ("HONG_KONG", 22696, 23253),
    ("JAMAICA", 23253, 24497),
    ("LEEWARD_ISLANDS_ANTIGUA", 24497, 24751),
    ("LEEWARD_ISLANDS_ST_CHRISTOPHER_NEVIS", 24751, 25138),
    ("LEEWARD_ISLANDS_DOMINICA", 25138, 25452),
    ("LEEWARD_ISLANDS_MONTSERRAT", 25452, 25658),
    ("LEEWARD_ISLANDS_VIRGIN_ISLANDS", 25658, 25799),
    ("MALTA", 25799, 26331),
    ("MAURITIUS", 26331, 27308),
    ("NATAL", 27308, 28058),
    ("NEWFOUNDLAND", 28058, 29526),
    ("NORTHERN_NIGERIA", 29526, 29744),
    ("NYASALAND_PROTECTORATE", 29744, 30592),
    ("ST_HELENA", 30592, 30746),
    ("SEYCHELLES", 30746, 31114),
    ("SIERRA_LEONE", 31114, 31749),
    ("BASUTOLAND", 31749, 31884),
    ("BECHUANALAND_PROTECTORATE", 31884, 31960),
    ("SWAZILAND", 31960, 32107),
    ("RHODESIA", 32107, 32614),
    ("SOUTHERN_NIGERIA", 32614, 33542),
    ("STRAITS_SETTLEMENTS", 33542, 35890),
    ("TRINIDAD_AND_TOBAGO", 35890, 37054),
    ("TURKS_AND_CAICOS_ISLANDS", 37054, 37242),
    ("UGANDA", 37242, 37545),
    ("WEIHAIWEI", 37545, 37862),
    ("WINDWARD_ISLANDS_GRENADA", 37862, 38185),
    ("WINDWARD_ISLANDS_ST_LUCIA", 38185, 38518),
    ("WINDWARD_ISLANDS_ST_VINCENT", 38518, 38779),
    ("NORTH_BORNEO", 38779, 39084),
    ("SARAWAK", 39084, 39262),
    ("ZANZIBAR", 39262, 39304),  # Ends before "OTHER MISCELLANEOUS POSSESSIONS"
]

def extract_colonies():
    """Extract each colony section to a separate file"""
    input_file = "/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1910/olmocr_results.md"
    output_dir = "/home/user/colonial_office_list/output_3/1910_manual_parsed"

    # Read the entire file
    print(f"Reading {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    print(f"Total lines: {len(lines)}")

    # Extract each colony
    extracted_colonies = []
    for name, start, end in colonies:
        print(f"Extracting {name} (lines {start}-{end})...")

        # Extract lines (convert to 0-indexed)
        colony_lines = lines[start-1:end-1]

        # Write to file
        output_file = os.path.join(output_dir, f"{name}.txt")
        with open(output_file, 'w', encoding='utf-8') as f:
            f.writelines(colony_lines)

        extracted_colonies.append({
            "name": name,
            "start_line": start,
            "end_line": end,
            "line_count": end - start,
            "file": f"{name}.txt"
        })

    # Create JSON manifest
    manifest = {
        "year": 1910,
        "source": "historical_document_pipeline/processed_pdfs/colonial-office-list-1910/olmocr_results.md",
        "total_colonies": len(colonies),
        "colonies": extracted_colonies
    }

    manifest_file = "/home/user/colonial_office_list/output_3/1910_manual_parsed.json"
    with open(manifest_file, 'w', encoding='utf-8') as f:
        json.dump(manifest, f, indent=2)

    print(f"\nExtraction complete!")
    print(f"Total colonies extracted: {len(colonies)}")
    print(f"Manifest saved to: {manifest_file}")

    return manifest

if __name__ == "__main__":
    manifest = extract_colonies()

    # Print summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Year: {manifest['year']}")
    print(f"Total colonies: {manifest['total_colonies']}")
    print("\nColonies extracted:")
    for colony in manifest['colonies']:
        print(f"  {colony['name']:40s} ({colony['line_count']:4d} lines)")
