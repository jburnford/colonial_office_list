#!/usr/bin/env python3
"""
Identify all colony section boundaries in the 1958 Colonial Office List.
This script scans Part II to find where each colony section starts and ends.
"""

import re
import json

# Read the OCR results file
input_file = "/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1958/olmocr_results.md"

print("Reading OCR file...")
with open(input_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Total lines in file: {len(lines)}")

# Part II boundaries based on manual inspection
# Note: These are 1-based line numbers from the Read tool
# Array indices are 0-based, so subtract 1
PART_II_START_LINE = 3377  # Line number where "PART II" appears in Read tool
PART_II_END_LINE = 19708   # Line number where "PART III" appears in Read tool
PART_II_START = PART_II_START_LINE - 1  # Array index
PART_II_END = PART_II_END_LINE - 1  # Array index

print(f"\nScanning Part II (lines {PART_II_START} to {PART_II_END})...\n")

# Debug: Show first few lines of Part II
print("DEBUG: First 10 lines of Part II:")
for i in range(PART_II_START - 1, min(PART_II_START + 9, len(lines))):
    print(f"  Array index {i}, Raw line: {repr(lines[i][:80])}")
print()

# Known territories from table of contents
# These are the main sections we expect to find
EXPECTED_TERRITORIES = [
    "ADEN",
    "BAHAMA ISLANDS",
    "BARBADOS",  # Cross-reference
    "BERMUDA",
    "BRITISH GUIANA",
    "BRITISH HONDURAS",
    "BRUNEI",
    "CYPRUS",
    "FALKLAND ISLANDS",
    "FIJI",
    "GAMBIA",
    "GIBRALTAR",
    "HONG KONG",
    "JAMAICA",  # Cross-reference
    "KENYA",
    "LEEWARD ISLANDS",
    "FEDERATION OF MALAYA",
    "MALTA",
    "MAURITIUS",
    "FEDERATION OF NIGERIA",
    "NORTH BORNEO",
    "FEDERATION OF RHODESIA AND NYASALAND",
    "NORTHERN RHODESIA",
    "NYASALAND PROTECTORATE",
    "ST. HELENA",
    "SARAWAK",
    "SEYCHELLES",
    "SIERRA LEONE",
    "SINGAPORE",
    "SOMALILAND PROTECTORATE",
    "TANGANYIKA",
    "TONGA",
    "TRINIDAD AND TOBAGO",  # Cross-reference
    "UGANDA",
    "THE WEST INDIES",
    "WESTERN PACIFIC",
    "WINDWARD ISLANDS",  # Cross-reference
    "ZANZIBAR",
    "MISCELLANEOUS ISLANDS",
    "THE HIGH COMMISSION TERRITORIES"
]

# Find all potential section headers in Part II
# A section header is typically:
# - All uppercase
# - At start of line (after line number)
# - Usually short (1-5 words)
# - Not a subsection header within a colony

potential_sections = []

for i in range(PART_II_START, PART_II_END):
    line = lines[i]
    content = line.strip()

    # Check if this looks like a major section header
    # Must be uppercase, not too long, and match expected patterns
    if content and content.isupper() and len(content) > 0:
        # For now, collect ALL uppercase lines to see what we have
        line_num = i + 1  # Convert to 1-based line number for consistency with Read tool
        potential_sections.append({
            'line_num': line_num,
            'array_index': i,
            'content': content
        })

print(f"Found {len(potential_sections)} potential territory sections:\n")
for section in potential_sections[:100]:  # Show first 100
    print(f"  Line {section['line_num']:5d}: {section['content']}")

# Now manually refine this list based on knowledge of the structure
# Look at the context around each potential section to confirm it's a main territory header

print("\n\nAnalyzing context to identify main territory sections...\n")

confirmed_sections = []

for section in potential_sections:
    idx = section['array_index']
    line_num = section['line_num']
    content = section['content']

    # Get context (2 lines before and after)
    context_before = []
    context_after = []

    for j in range(max(0, idx-2), idx):
        context_before.append(lines[j].strip())

    for j in range(idx+1, min(len(lines), idx+3)):
        context_after.append(lines[j].strip())

    # A main territory section usually:
    # 1. Has blank lines or minimal content before it
    # 2. Is followed by subsection headers or descriptive text
    # 3. Is not indented or part of a list

    # Check if this is likely a main section
    is_main_section = False

    # If preceded by blank line or previous section ended
    if len(context_before) == 0 or all(len(cb) == 0 for cb in context_before):
        is_main_section = True

    # Special handling for known territory names
    if any(content == terr or content.startswith(terr) for terr in EXPECTED_TERRITORIES):
        is_main_section = True

    if is_main_section:
        confirmed_sections.append(section)

print(f"Confirmed {len(confirmed_sections)} main territory sections:\n")
for section in confirmed_sections:
    print(f"  Line {section['line_num']:5d}: {section['content']}")

# Save to JSON for manual review
output = {
    'part_ii_start_line': PART_II_START_LINE,
    'part_ii_end_line': PART_II_END_LINE,
    'part_ii_start_index': PART_II_START,
    'part_ii_end_index': PART_II_END,
    'potential_sections': potential_sections,
    'confirmed_sections': confirmed_sections
}

with open('/home/user/colonial_office_list/output_3/1958_potential_boundaries.json', 'w', encoding='utf-8') as f:
    json.dump(output, f, indent=2)

print(f"\n\nResults saved to output_3/1958_potential_boundaries.json")
