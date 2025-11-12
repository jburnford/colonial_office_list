#!/usr/bin/env python3
"""
Parse 1883 Colonial Office List - Systematic colony extraction
"""

import re
import json
from pathlib import Path

# Define the path
ocr_file = Path("/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1883/olmocr_results.md")
output_dir = Path("/home/user/colonial_office_list/output/1883_manual_parsed")

# Read the file
print("Reading OCR file...")
with open(ocr_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Total lines: {len(lines)}")

# Define colony sections based on manual analysis
# Format: (name, start_line_number, is_appendix)
colony_sections = [
    ("BAHAMAS", 1564, False),
    ("BARBADOS", 20432, False),  # Part of Windward Islands but has own section
    ("BERMUDA", 1761, False),
    ("BRITISH_GUIANA", 2054, False),
    ("BRITISH_HONDURAS", 2748, False),
    ("CANADA", 2949, False),
    ("CAPE_OF_GOOD_HOPE", 5543, False),
    ("CEYLON", 7552, False),
    ("CYPRUS", 21776, True),  # Appendix
    ("FALKLAND_ISLANDS", 8222, False),
    ("FIJI", 8340, False),
    ("GAMBIA", 19815, False),
    ("GIBRALTAR", 8606, False),
    ("GOLD_COAST_COLONY", 8688, False),
    ("GRENADA", 21173, False),  # Part of Windward Islands
    ("HELIGOLAND", 9310, False),
    ("HONG_KONG", 9371, False),
    ("JAMAICA", 9678, False),
    ("LABUAN", 10244, False),
    ("LAGOS", 8762, False),
    ("LEEWARD_ISLANDS", 10362, False),
    ("MALTA", 11574, False),
    ("MAURITIUS", 11875, False),
    ("NATAL", 12770, False),
    ("NEWFOUNDLAND", 13388, False),
    ("NEW_SOUTH_WALES", 13666, False),
    ("NEW_ZEALAND", 14617, False),
    ("QUEENSLAND", 15232, False),
    ("ST_HELENA", 15756, False),
    ("ST_LUCIA", 21557, False),  # Part of Windward Islands
    ("ST_VINCENT", 20954, False),  # Part of Windward Islands
    ("SIERRA_LEONE", 19517, False),
    ("SOUTH_AUSTRALIA", 15864, False),
    ("STRAITS_SETTLEMENTS", 17139, False),
    ("TASMANIA", 17381, False),
    ("TOBAGO", 21386, False),  # Part of Windward Islands
    ("TRANSVAAL_STATE", 22011, True),  # Appendix - POST-BOER WAR!
    ("TRINIDAD", 17916, False),
    ("TURKS_AND_CAICOS_ISLANDS", 18646, False),
    ("VICTORIA", 18719, False),
    ("WESTERN_AUSTRALIA", 19983, False),
    ("WINDWARD_ISLANDS", 20430, False),
]

# Sort by start line
colony_sections.sort(key=lambda x: x[1])

print(f"\nIdentified {len(colony_sections)} colony sections")
print("\nColony sections:")
for name, start, is_appendix in colony_sections:
    print(f"  {name}: line {start} {'(APPENDIX)' if is_appendix else ''}")

# Extract each colony section
metadata = {
    "year": 1883,
    "total_colonies": len(colony_sections),
    "parsing_method": "LLM-based manual parsing",
    "historical_context": "Post-First Boer War (1880-1881) - Transvaal in Appendix",
    "colonies": []
}

print("\nExtracting colony sections...")
for i, (name, start, is_appendix) in enumerate(colony_sections):
    # Determine end line (start of next colony or end of file)
    if i < len(colony_sections) - 1:
        end = colony_sections[i + 1][1]
    else:
        # For the last colony, we need to find where it ends
        # Typically before "COLONIAL REGULATIONS" or similar section
        end = start + 500  # Conservative estimate

    # Extract the section (adjusting for 0-indexed vs 1-indexed)
    section_lines = lines[start-1:end-1]
    section_text = ''.join(section_lines)

    # Write to file
    output_file = output_dir / f"{name}.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(section_text)

    print(f"  ✓ Extracted {name} ({len(section_lines)} lines)")

    # Add to metadata
    metadata["colonies"].append({
        "name": name.replace('_', ' '),
        "filename": f"{name}.md",
        "start_line": start,
        "end_line": end,
        "line_count": len(section_lines),
        "is_appendix": is_appendix
    })

# Write metadata
metadata_file = Path("/home/user/colonial_office_list/output/1883_manual_parsed.json")
with open(metadata_file, 'w', encoding='utf-8') as f:
    json.dump(metadata, f, indent=2)

print(f"\n✓ Metadata saved to {metadata_file}")
print(f"\n✓ Total colonies extracted: {len(colony_sections)}")
print(f"  - Main colonies: {sum(1 for _, _, is_app in colony_sections if not is_app)}")
print(f"  - Appendix: {sum(1 for _, _, is_app in colony_sections if is_app)}")
print("\n✓ Extraction complete!")
