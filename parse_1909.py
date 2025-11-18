#!/usr/bin/env python3
"""
Parse the 1909 Colonial Office List OCR results and extract individual colony sections.
"""
import re
import json
from pathlib import Path

# Read the OCR file
ocr_file = Path("/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1909/olmocr_results.md")
output_dir = Path("/home/user/colonial_office_list/output_3/1909_manual_parsed")
output_json = Path("/home/user/colonial_office_list/output_3/1909_manual_parsed.json")

# Create output directory
output_dir.mkdir(parents=True, exist_ok=True)

# Read the file
with open(ocr_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Known colony/territory names to look for (based on 1906-1908 patterns)
# These should appear as section headers in the format "COLONY NAME."
colony_patterns = [
    # Australian states
    "AUSTRALIA—NEW SOUTH WALES",
    "AUSTRALIA—QUEENSLAND",
    "SOUTH AUSTRALIA",
    "AUSTRALIA—SOUTH AUSTRALIA—TASMANIA",
    "TASMANIA",
    "AUSTRALIA—VICTORIA",
    "WESTERN AUSTRALIA",
    "NORTHERN TERRITORY",
    # Canadian Provinces (Dominion of Canada)
    "DOMINION OF CANADA",
    "ONTARIO",
    "QUEBEC",
    "NOVA SCOTIA",
    "NEW BRUNSWICK",
    "PRINCE EDWARD ISLAND",
    "BRITISH COLUMBIA",
    "MANITOBA",
    "SASKATCHEWAN",
    "ALBERTA",
    # Pacific
    "PAPUA",
    # West Indies
    "BAHAMAS",
    "BARBADOS",
    "BERMUDA",
    "BRITISH GUIANA",
    "BRITISH HONDURAS",
    "JAMAICA",
    "THE LEEWARD ISLANDS",
    "ANTIGUA",
    "DOMINICA",
    "MONTSERRAT",
    "ST. CHRISTOPHER",
    "NEVIS",
    "VIRGIN ISLANDS",
    "GRENADA",
    "ST. LUCIA",
    "ST. VINCENT",
    "TRINIDAD AND TOBAGO",
    "TRINIDAD",
    "TOBAGO",
    "TURKS AND CAICOS ISLANDS",
    # Asian/Pacific
    "CEYLON",
    "HONG KONG",
    "STRAITS SETTLEMENTS",
    "LABUAN",
    "FIJI",
    "WESTERN PACIFIC",
    # African
    "THE GAMBIA",
    "THE GOLD COAST",
    "ASHANTI",
    "THE NORTHERN TERRITORIES",
    "SIERRA LEONE",
    "NORTHERN NIGERIA",
    "SOUTHERN NIGERIA",
    "EAST AFRICA PROTECTORATE",
    "UGANDA",
    "NYASALAND PROTECTORATE",
    "SOMALILAND PROTECTORATE",
    "ZANZIBAR",
    "BASUTOLAND",
    "BECHUANALAND PROTECTORATE",
    "SWAZILAND",
    "SOUTHERN RHODESIA",
    "NORTHERN RHODESIA",
    "ORANGE RIVER COLONY",
    "CAPE OF GOOD HOPE",
    "TRANSVAAL",
    "NATAL",
    # Mediterranean/Other
    "CYPRUS",
    "GIBRALTAR",
    "MALTA",
    "ST. HELENA",
    "SEYCHELLES",
    "MAURITIUS",
    "FALKLAND ISLANDS",
    # Dominions
    "NEWFOUNDLAND",
    "NEW ZEALAND",
    # Other
    "WEIHAIWEI",
]

# Find all colony section boundaries
# Skip early sections (before line 5000) which contain indexes, tables, etc.
# End before line 38648 which starts "OTHER MISCELLANEOUS POSSESSIONS"
MIN_LINE = 5000
MAX_LINE = 38648

colony_sections = []
seen_colonies = {}  # Track first occurrence of each colony

for i, line in enumerate(lines):
    if i < MIN_LINE or i >= MAX_LINE:
        continue

    line_stripped = line.strip()
    # Check if this line matches a colony pattern
    for pattern in colony_patterns:
        if line_stripped == pattern + ".":
            # Only keep the first occurrence of each colony
            if pattern not in seen_colonies:
                # Verify it's a real section by checking that the next non-empty lines
                # contain content (not another section header or just tables)
                is_real_section = False

                # Look ahead to verify this is a substantive section
                for j in range(i+1, min(i+100, len(lines))):
                    next_line = lines[j].strip()

                    # Skip empty lines
                    if not next_line:
                        continue

                    # Check for typical subsection headers
                    if next_line in ["Situation and Area.", "History.", "General Description.",
                                     "Area and Climate.", "Constitution.", "Area and Population.",
                                     "Climate.", "Population.", "The State.", "Trade and Industry.",
                                     "Government.", "Administration.", "Geographical Position.",
                                     "Area.", "Geography."]:
                        is_real_section = True
                        break

                    # Check if it starts with descriptive text (not a table or header)
                    # If we find a paragraph of text, it's likely a real section
                    if len(next_line) > 100 and not next_line.startswith("|"):
                        is_real_section = True
                        break

                    # Stop if we hit another colony header
                    if next_line.endswith(".") and next_line.isupper() and len(next_line) > 5:
                        break

                if is_real_section:
                    colony_sections.append({
                        'name': pattern,
                        'line_number': i + 1,  # 1-indexed
                        'line_index': i  # 0-indexed
                    })
                    seen_colonies[pattern] = i
                    print(f"Found colony: {pattern} at line {i + 1}")
            break

# Sort by line number
colony_sections.sort(key=lambda x: x['line_index'])

print(f"\nTotal colonies found: {len(colony_sections)}")

# Extract text for each colony
colonies_data = []
for idx, colony in enumerate(colony_sections):
    start_line = colony['line_index']

    # Find the end line (start of next colony or MAX_LINE)
    if idx < len(colony_sections) - 1:
        end_line = colony_sections[idx + 1]['line_index']
    else:
        end_line = MAX_LINE  # Don't go beyond the colonial sections

    # Extract the text
    colony_text_lines = lines[start_line:end_line]
    colony_text = ''.join(colony_text_lines)

    # Create a safe filename
    safe_name = colony['name'].replace(" ", "_").replace("—", "-").lower()
    filename = f"{safe_name}.md"

    # Write to file
    output_file = output_dir / filename
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(colony_text)

    colonies_data.append({
        'name': colony['name'],
        'filename': filename,
        'start_line': colony['line_number'],
        'end_line': end_line,
        'char_count': len(colony_text)
    })

    print(f"Extracted: {colony['name']} -> {filename} ({len(colony_text)} chars)")

# Create JSON metadata
metadata = {
    'year': 1909,
    'source_file': str(ocr_file),
    'total_colonies': len(colonies_data),
    'colonies': colonies_data
}

with open(output_json, 'w', encoding='utf-8') as f:
    json.dump(metadata, f, indent=2)

print(f"\nMetadata written to: {output_json}")
print(f"Colony files written to: {output_dir}")
print(f"Total colonies extracted: {len(colonies_data)}")
