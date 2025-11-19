#!/usr/bin/env python3
"""
Manual extraction of colonies from 1959 Colonial Office List.
Based on manual boundary identification by reading OCR content.

Year: 1959
Source: /home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1959/olmocr_results.md
Method: Manual boundary identification (reading content to find section starts/ends)
"""

import json
import os
import re
from pathlib import Path

# Manually identified colony boundaries based on reading the OCR file
# Format: {"name": "Colony Name", "start": line_num, "end": line_num, "notes": "any special notes"}
COLONY_BOUNDARIES = [
    {"name": "Aden", "start": 3672, "end": 4151, "notes": "Header: 'ADEN COLONY'"},
    {"name": "Bahama_Islands", "start": 4152, "end": 4457, "notes": ""},
    {"name": "Barbados", "start": 4458, "end": 4461, "notes": "Reference to West Indies Federation only, ** markers"},
    {"name": "Bermuda", "start": 4462, "end": 4803, "notes": "** markers, standalone section despite reference"},
    {"name": "British_Guiana", "start": 4804, "end": 5195, "notes": ""},
    {"name": "British_Honduras", "start": 5196, "end": 5568, "notes": ""},
    {"name": "Brunei", "start": 5569, "end": 5867, "notes": ""},
    {"name": "Christmas_Island", "start": 5868, "end": 5871, "notes": "Very short section"},
    {"name": "Cyprus", "start": 5872, "end": 6321, "notes": ""},
    {"name": "Falkland_Islands", "start": 6322, "end": 6651, "notes": "Header: 'FALKLAND ISLANDS AND DEPENDENCIES'"},
    {"name": "Fiji", "start": 6652, "end": 7016, "notes": ""},
    {"name": "Gambia", "start": 7017, "end": 7409, "notes": "Header: 'THE GAMBIA'"},
    {"name": "Gibraltar", "start": 7410, "end": 7657, "notes": ""},
    {"name": "Hong_Kong", "start": 7658, "end": 8072, "notes": ""},
    {"name": "Kenya", "start": 8073, "end": 8611, "notes": ""},
    {"name": "Leeward_Islands", "start": 8612, "end": 8760, "notes": "Header: 'THE LEEWARD ISLANDS', includes British Virgin Islands"},
    {"name": "Malta", "start": 8761, "end": 9192, "notes": "Header: 'MALTA, G.C.' (George Cross)"},
    {"name": "Mauritius", "start": 9193, "end": 9566, "notes": ""},
    {"name": "Nigeria", "start": 9567, "end": 10641, "notes": "Header: 'FEDERATION OF NIGERIA'"},
    {"name": "Rhodesia_and_Nyasaland", "start": 10642, "end": 10649, "notes": "Header: 'THE FEDERATION OF RHODESIA AND NYASALAND', short intro section"},
    {"name": "Northern_Rhodesia", "start": 10650, "end": 11238, "notes": ""},
    {"name": "Nyasaland", "start": 11239, "end": 11638, "notes": "Header: 'NYASALAND PROTECTORATE'"},
    {"name": "St_Helena", "start": 11639, "end": 11853, "notes": "Includes Ascension and Tristan da Cunha"},
    {"name": "Sarawak", "start": 11854, "end": 12183, "notes": ""},
    {"name": "Seychelles", "start": 12184, "end": 12482, "notes": ""},
    {"name": "Sierra_Leone", "start": 12483, "end": 12875, "notes": ""},
    {"name": "Singapore", "start": 12876, "end": 13335, "notes": ""},
    {"name": "Somaliland", "start": 13336, "end": 13601, "notes": "Header: 'SOMALILAND PROTECTORATE'"},
    {"name": "Tanganyika", "start": 13602, "end": 13984, "notes": ""},
    {"name": "Tonga", "start": 13985, "end": 14130, "notes": "Header: 'KINGDOM OF TONGA'"},
    {"name": "Uganda", "start": 14131, "end": 14590, "notes": "** markers"},
    {"name": "West_Indies", "start": 14591, "end": 17995, "notes": "Header: 'THE WEST INDIES (FEDERATION)', includes Antigua, Dominica, Grenada, Jamaica, Montserrat, St Kitts-Nevis-Anguilla, St Lucia, St Vincent, Trinidad and Tobago"},
    {"name": "Western_Pacific", "start": 17996, "end": 18624, "notes": "Header: 'WESTERN PACIFIC HIGH COMMISSION'"},
    {"name": "Windward_Islands", "start": 18625, "end": 18628, "notes": "Reference to West Indies Federation only, ** markers"},
    {"name": "Zanzibar", "start": 18629, "end": 18904, "notes": "** markers"},
    {"name": "Miscellaneous_Islands", "start": 18905, "end": 18907, "notes": "Very short section"},
    {"name": "High_Commission_Territories", "start": 18908, "end": 19072, "notes": "Basutoland, Bechuanaland Protectorate, and Swaziland"},
]

def extract_colony_section(input_file, colony_info, output_dir):
    """Extract a single colony section from the OCR file."""

    start_line = colony_info["start"]
    end_line = colony_info["end"]
    name = colony_info["name"]

    lines = []
    line_count = 0
    word_count = 0

    with open(input_file, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, start=1):
            if line_num >= start_line and line_num <= end_line:
                lines.append(line.rstrip('\n'))
                line_count += 1
                word_count += len(line.split())

    # Write to file
    colony_file = output_dir / f"{name}.txt"
    with open(colony_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(lines))

    return {
        "name": colony_info["name"],
        "display_name": colony_info["name"].replace('_', ' '),
        "file": str(colony_file.name),
        "start_line": start_line,
        "end_line": end_line,
        "line_count": line_count,
        "word_count": word_count,
        "char_count": sum(len(line) for line in lines),
        "notes": colony_info.get("notes", "")
    }

def main():
    input_file = Path("/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1959/olmocr_results.md")
    output_dir = Path("/home/user/colonial_office_list/output_3/1959_manual_parsed")

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Extracting {len(COLONY_BOUNDARIES)} colonies from 1959 Colonial Office List...")
    print(f"Source: {input_file}")
    print(f"Output: {output_dir}")
    print()

    metadata = {
        "year": 1959,
        "source_file": str(input_file),
        "extraction_method": "manual_boundary_identification",
        "extraction_date": "2025-11-19",
        "methodology": "Manual reading of OCR content to identify section boundaries. No automated pattern matching used.",
        "total_colonies": len(COLONY_BOUNDARIES),
        "colonies": [],
        "notes": [
            "North Borneo: NOT found as a standalone section in Part II. Listed in Governors table but no territory description section.",
            "Several territories use ** markers (Barbados, Bermuda, Uganda, Zanzibar, Windward Islands)",
            "Some territories are just references to West Indies Federation (Barbados, Windward Islands)",
            "West Indies Federation section includes multiple territories: Antigua, Barbados, Dominica, Grenada, Jamaica, Montserrat, St Kitts-Nevis-Anguilla, St Lucia, St Vincent, Trinidad and Tobago",
            "High Commission Territories (Basutoland, Bechuanaland, Swaziland) are administered by Commonwealth Relations Office but included in this list",
            "1959 was just before the 'Year of Africa' (1960) when many colonies became independent"
        ]
    }

    total_lines = 0
    total_words = 0
    total_chars = 0

    for colony_info in COLONY_BOUNDARIES:
        print(f"Extracting: {colony_info['name']:35s} (lines {colony_info['start']:5d}-{colony_info['end']:5d})")
        result = extract_colony_section(input_file, colony_info, output_dir)
        metadata["colonies"].append(result)
        total_lines += result["line_count"]
        total_words += result["word_count"]
        total_chars += result["char_count"]

    # Add totals
    metadata["totals"] = {
        "total_lines": total_lines,
        "total_words": total_words,
        "total_characters": total_chars
    }

    # Write metadata JSON
    metadata_file = Path("/home/user/colonial_office_list/output_3/1959_manual_parsed.json")
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)

    print()
    print("="*80)
    print(f"Extraction complete!")
    print(f"  Colonies extracted: {len(metadata['colonies'])}")
    print(f"  Total lines: {total_lines:,}")
    print(f"  Total words: {total_words:,}")
    print(f"  Total characters: {total_chars:,}")
    print(f"  Output directory: {output_dir}")
    print(f"  Metadata file: {metadata_file}")
    print("="*80)

    # Print summary by size
    print()
    print("Colonies by size (line count):")
    sorted_colonies = sorted(metadata["colonies"], key=lambda x: x["line_count"], reverse=True)
    for colony in sorted_colonies[:10]:
        print(f"  {colony['display_name']:35s}: {colony['line_count']:5d} lines, {colony['word_count']:7,d} words")

if __name__ == "__main__":
    main()
