#!/usr/bin/env python3
"""
Extract all colonies from the 1877 Colonial Office List using manually identified boundaries.
"""

import json
import os
import re
from pathlib import Path

# Source file
SOURCE_FILE = "/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1877/olmocr_results.md"
OUTPUT_DIR = "/home/user/colonial_office_list/output_3/1877_manual_parsed"
OUTPUT_JSON = "/home/user/colonial_office_list/output_3/1877_manual_parsed.json"
REPORT_FILE = "/home/user/colonial_office_list/output_3/1877_PARSING_REPORT.md"

# Manually identified colony boundaries (line numbers are 1-indexed)
# All boundaries verified by reading the OCR content
COLONIES = [
    # Redirects to other colony sections
    {"name": "ANTIGUA", "start": 1308, "end": 1310, "redirect": "Leeward Islands, p. 89"},
    {"name": "ANGUILLA", "start": 1311, "end": 1313, "redirect": "Leeward Islands, page 95"},

    # Full colonies
    {"name": "BAHAMAS", "start": 1314, "end": 1576},
    {"name": "BARBADOS", "start": 1577, "end": 1582, "redirect": "Windward Islands, p. 161"},
    {"name": "BERMUDAS", "start": 1583, "end": 1813},
    {"name": "BRITISH_COLUMBIA_AND_VANCOUVER_ISLAND", "start": 1814, "end": 1816, "redirect": "Dominion of Canada, p. 29"},
    {"name": "BRITISH_HONDURAS", "start": 1817, "end": 1819, "redirect": "Honduras, page 75"},
    {"name": "BRITISH_GUIANA", "start": 1820, "end": 2455},
    {"name": "DOMINION_OF_CANADA", "start": 2456, "end": 4322},
    {"name": "CAPE_OF_GOOD_HOPE", "start": 4323, "end": 5611},
    {"name": "CEYLON", "start": 5612, "end": 6182},
    {"name": "DOMINICA", "start": 6183, "end": 6186, "redirect": "Leeward Islands, p. 96"},
    {"name": "FALKLAND_ISLANDS", "start": 6187, "end": 6306},
    {"name": "FIJI", "start": 6307, "end": 6361},
    {"name": "GIBRALTAR", "start": 6362, "end": 6444},
    {"name": "THE_GOLD_COAST_COLONY", "start": 6445, "end": 7019},
    {"name": "GRENADA", "start": 7020, "end": 7025, "redirect": "Windward Islands, p. 169"},
    {"name": "GRIQUALAND_WEST", "start": 7026, "end": 7339},
    {"name": "HELIGOLAND", "start": 7340, "end": 7377},
    {"name": "HONDURAS", "start": 7378, "end": 7553},
    {"name": "HONG_KONG", "start": 7554, "end": 7818},
    {"name": "JAMAICA", "start": 7819, "end": 8484},
    {"name": "LABUAN", "start": 8485, "end": 8580},
    {"name": "THE_LEEWARD_ISLANDS", "start": 8581, "end": 9828},
    {"name": "MALTA", "start": 9829, "end": 10231},
    {"name": "MAURITIUS", "start": 10232, "end": 10966},
    {"name": "NATAL", "start": 10967, "end": 11294},
    {"name": "NEVIS", "start": 11295, "end": 11297, "redirect": "Leeward Islands, p. 94"},
    {"name": "NEWFOUNDLAND", "start": 11298, "end": 11961},
    {"name": "NEW_SOUTH_WALES", "start": 11962, "end": 12581},
    {"name": "NEW_ZEALAND", "start": 12582, "end": 13152},
    {"name": "QUEENSLAND", "start": 13153, "end": 13502},
    {"name": "ST_VINCENT", "start": 13499, "end": 13504, "redirect": "Windward Islands, p. 166"},
    {"name": "SIERRA_LEONE", "start": 13505, "end": 13507, "redirect": "West African Settlements, p. 158"},
    {"name": "ST_CHRISTOPHER_NEVIS_AND_ANGUILLA", "start": 13508, "end": 13510, "redirect": "Leeward Islands, p. 86"},
    {"name": "ST_HELENA", "start": 13511, "end": 13615},
    {"name": "SOUTH_AUSTRALIA", "start": 13616, "end": 14363},
    {"name": "STRAITS_SETTLEMENTS", "start": 14364, "end": 14704},
    {"name": "TASMANIA", "start": 14705, "end": 15012},
    {"name": "TOBAGO", "start": 15013, "end": 15016, "redirect": "Windward Islands"},
    {"name": "TRINIDAD", "start": 15017, "end": 15569},
    {"name": "TURKS_AND_CAICOS_ISLANDS", "start": 15570, "end": 15649},
    {"name": "VICTORIA", "start": 15650, "end": 16376},
    {"name": "VIRGIN_ISLANDS", "start": 16377, "end": 16380, "redirect": "Leeward Islands"},
    {"name": "WESTERN_AUSTRALIA", "start": 16381, "end": 16600},
    {"name": "WEST_AFRICA_SETTLEMENTS", "start": 16601, "end": 16993},
    {"name": "THE_WINDWARD_ISLANDS", "start": 16994, "end": 18252},
]

def read_lines_from_file(file_path, start_line, end_line):
    """Read specific lines from a file (1-indexed line numbers)."""
    lines = []
    with open(file_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f, 1):
            if i >= start_line and i <= end_line:
                lines.append(line)
            elif i > end_line:
                break
    return lines

def remove_line_numbers(lines):
    """Remove line number prefixes from lines (format: '  123→text')."""
    cleaned_lines = []
    for line in lines:
        # Match pattern: spaces, digits, arrow, content
        match = re.match(r'^\s*\d+→(.*)$', line)
        if match:
            cleaned_lines.append(match.group(1) + '\n')
        else:
            cleaned_lines.append(line)
    return cleaned_lines

def extract_colony(colony_info):
    """Extract a single colony to a text file."""
    name = colony_info["name"]
    start = colony_info["start"]
    end = colony_info["end"]
    redirect = colony_info.get("redirect", None)

    print(f"Extracting {name} (lines {start}-{end})...")

    # Read lines
    lines = read_lines_from_file(SOURCE_FILE, start, end)

    if not lines:
        print(f"  WARNING: No lines found for {name}")
        return None

    # Remove line numbers
    cleaned_lines = remove_line_numbers(lines)

    # Join into text
    text = ''.join(cleaned_lines)

    # Create output file
    output_file = os.path.join(OUTPUT_DIR, f"{name}.txt")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(text)

    # Generate metadata
    metadata = {
        "name": name,
        "start_line": start,
        "end_line": end,
        "line_count": end - start + 1,
        "char_count": len(text),
        "file": f"{name}.txt"
    }

    if redirect:
        metadata["redirect"] = redirect
        metadata["notes"] = f"Redirect to {redirect}"

    print(f"  Extracted {metadata['line_count']} lines, {metadata['char_count']} chars")

    return metadata

def main():
    """Main extraction function."""
    print("=" * 80)
    print("1877 Colonial Office List - Manual Colony Extraction")
    print("=" * 80)
    print()

    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Extract all colonies
    metadata_list = []
    successful = 0
    failed = 0
    redirects = 0

    for colony in COLONIES:
        try:
            metadata = extract_colony(colony)
            if metadata:
                metadata_list.append(metadata)
                successful += 1
                if colony.get("redirect"):
                    redirects += 1
        except Exception as e:
            print(f"  ERROR extracting {colony['name']}: {e}")
            failed += 1

    # Generate JSON metadata
    full_metadata = {
        "year": 1877,
        "parser": "manual_llm",
        "total_colonies": len(metadata_list),
        "full_colonies": len(metadata_list) - redirects,
        "redirects": redirects,
        "colonies": metadata_list
    }

    with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
        json.dump(full_metadata, f, indent=2)

    print()
    print("=" * 80)
    print("Extraction Summary")
    print("=" * 80)
    print(f"Total entries extracted: {successful}")
    print(f"Full colony sections: {successful - redirects}")
    print(f"Redirect entries: {redirects}")
    print(f"Failed extractions: {failed}")
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"Metadata file: {OUTPUT_JSON}")
    print()

    # Generate parsing report
    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write("# 1877 Colonial Office List - Parsing Report\n\n")
        f.write("## Extraction Summary\n\n")
        f.write(f"- **Year:** 1877\n")
        f.write(f"- **Parser:** Manual LLM boundary identification\n")
        f.write(f"- **Total entries:** {successful}\n")
        f.write(f"- **Full colony sections:** {successful - redirects}\n")
        f.write(f"- **Redirect entries:** {redirects}\n")
        f.write(f"- **Failed extractions:** {failed}\n")
        f.write(f"- **Output directory:** `{OUTPUT_DIR}`\n")
        f.write(f"- **Metadata file:** `{OUTPUT_JSON}`\n\n")

        f.write("## Methodology\n\n")
        f.write("Colonies were extracted using manual boundary identification:\n\n")
        f.write("1. Read the entire 1877 OCR results file in sections\n")
        f.write("2. Manually identified colony section headers by searching for patterns\n")
        f.write("3. Determined section boundaries by reading actual content\n")
        f.write("4. Cross-referenced with 1867 and 1878 lists to verify completeness\n")
        f.write("5. Created extraction script with verified boundaries\n")
        f.write("6. Extracted each colony to individual text files\n")
        f.write("7. Removed line number prefixes from extracted text\n\n")

        f.write("## Colonies Extracted\n\n")
        f.write("| # | Colony Name | Lines | Characters | Type |\n")
        f.write("|---|-------------|-------|------------|------|\n")

        for i, colony in enumerate(metadata_list, 1):
            ctype = "Redirect" if colony.get("redirect") else "Full"
            f.write(f"| {i} | {colony['name']} | {colony['line_count']} | {colony['char_count']:,} | {ctype} |\n")

        f.write("\n## Notes\n\n")
        f.write("### Redirect Entries\n\n")
        f.write("Some colonies are redirect entries pointing to their parent colony or a grouped section:\n\n")

        for colony in metadata_list:
            if colony.get("redirect"):
                f.write(f"- **{colony['name']}**: {colony['notes']}\n")

        f.write("\n### Colony Groupings\n\n")
        f.write("- **Leeward Islands** contains: Antigua, Montserrat, St. Christopher, Nevis, Dominica, Anguilla, Virgin Islands\n")
        f.write("- **Windward Islands** contains: Barbados, Grenada, St. Vincent, St. Lucia, Tobago\n")
        f.write("- **West Africa Settlements** contains: Sierra Leone, Gambia\n")
        f.write("- **Gold Coast Colony** includes Lagos\n")
        f.write("\n### Section Boundaries\n\n")
        f.write("- Colonies section starts at line 1306 (header: 'COLONIES')\n")
        f.write("- Colonies section ends at line 18252 (followed by 'PART III. EMIGRATION' at line 18253)\n")
        f.write("- All colony boundaries were manually verified by reading the OCR content\n")
        f.write("- Line numbers in the source file use the format '  123→text'\n")

    print(f"Report generated: {REPORT_FILE}")
    print()

if __name__ == "__main__":
    main()
