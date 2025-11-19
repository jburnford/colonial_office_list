#!/usr/bin/env python3
"""
Manually identify colony boundaries in the 1949 Colonial Office List
using the exact list from the table of contents.
"""

import re

# List of colonies from the table of contents (manually extracted from lines 3752-3791)
# Format: (display_name, search_pattern, page_number)
colonies_to_find = [
    ("Aden", r"^ADEN$", 52),
    ("Bahamas", r"^(BAHAMAS|BAHAMA ISLANDS)$", 61),
    ("Barbados", r"^BARBADOS$", 66),
    ("Bermuda", r"^BERMUDA$", 73),
    ("British Guiana", r"^BRITISH GUIANA$", 79),
    ("British Honduras", r"^BRITISH HONDURAS$", 91),
    ("British Somaliland Protectorate", r"^(BRITISH SOMALILAND|SOMALILAND PROTECTORATE)$", 96),
    ("Brunei", r"^BRUNEI$", 99),
    ("Cyprus", r"^CYPRUS$", 102),
    ("East Africa High Commission", r"^EAST AFRICA HIGH COMMISSION$", 113),
    ("Falkland Islands", r"^FALKLAND ISLANDS$", 118),
    ("Fiji", r"^FIJI$", 123),
    ("Gambia", r"^(THE GAMBIA|GAMBIA)$", 132),
    ("Gibraltar", r"^GIBRALTAR$", 139),
    ("Gold Coast", r"^(THE GOLD COAST|GOLD COAST)$", 143),
    ("Hong Kong", r"^HONG KONG$", 161),
    ("Jamaica", r"^JAMAICA$", 172),
    ("Kenya", r"^KENYA$", 188),
    ("Leeward Islands", r"^(THE LEEWARD ISLANDS|LEEWARD ISLANDS)$", 202),
    ("Federation of Malaya", r"^(FEDERATION OF MALAYA|MALAYA)$", 214),
    ("Malta", r"^MALTA$", 227),
    ("Mauritius", r"^MAURITIUS$", 234),
    ("Nigeria", r"^NIGERIA$", 246),
    ("North Borneo", r"^NORTH BORNEO$", 272),
    ("Northern Rhodesia", r"^NORTHERN RHODESIA$", 277),
    ("Nyasaland Protectorate", r"^(NYASALAND|NYASALAND PROTECTORATE)$", 290),
    ("St. Helena", r"^(ST\. HELENA|SAINT HELENA)$", 297),
    ("Sarawak", r"^SARAWAK$", 301),
    ("Seychelles", r"^SEYCHELLES$", 308),
    ("Sierra Leone", r"^SIERRA LEONE$", 312),
    ("Singapore", r"^SINGAPORE$", 321),
    ("Tanganyika", r"^TANGANYIKA$", 332),
    ("Trinidad and Tobago", r"^(TRINIDAD|TRINIDAD AND TOBAGO)$", 342),
    ("Uganda", r"^UGANDA$", 352),
    ("Western Pacific", r"^(WESTERN PACIFIC|THE WESTERN PACIFIC)$", 361),
    ("Windward Islands", r"^(THE WINDWARD ISLANDS|WINDWARD ISLANDS)$", 373),
    ("Zanzibar", r"^ZANZIBAR$", 387),
    ("Miscellaneous Islands", r"^MISCELLANEOUS ISLANDS$", 393),
]

# Read the file
with open('/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1949/olmocr_results.md', 'r') as f:
    lines = f.readlines()

print(f"Total lines in file: {len(lines)}")

# Find Part II and Part III boundaries
part_ii_start = None
part_iii_start = None

for i, line in enumerate(lines, 1):
    if "HISTORICAL AND STATISTICAL ACCOUNT" in line and i > 100:
        part_ii_start = i
    if i > 10000 and line.strip() == "PART III":
        part_iii_start = i
        break

print(f"Part II starts at line: {part_ii_start}")
print(f"Part III starts at line: {part_iii_start}")
print()

# Find each colony
colonies_found = []

for display_name, pattern, page_num in colonies_to_find:
    found = False
    for i in range(part_ii_start, part_iii_start):
        line = lines[i-1]  # Convert to 0-based index
        content = line.strip()

        # Extract content after line number prefix if present
        match = re.search(r'^\s*\d+→(.*)$', line)
        if match:
            content = match.group(1).strip()

        # Check if this matches our pattern
        if re.match(pattern, content):
            colonies_found.append({
                'name': display_name,
                'line': i,
                'text': content,
                'page': page_num
            })
            print(f"Found: {display_name:40s} at line {i:5d}: {content}")
            found = True
            break

    if not found:
        print(f"WARNING: Not found: {display_name}")

print()
print("="*80)
print(f"Summary: Found {len(colonies_found)} of {len(colonies_to_find)} colonies")
print("="*80)
print()

# Sort by line number
colonies_found.sort(key=lambda x: x['line'])

# Calculate boundaries
for i in range(len(colonies_found)):
    start_line = colonies_found[i]['line']
    if i < len(colonies_found) - 1:
        end_line = colonies_found[i+1]['line'] - 1
    else:
        end_line = part_iii_start - 1

    colonies_found[i]['start_line'] = start_line
    colonies_found[i]['end_line'] = end_line
    colonies_found[i]['num_lines'] = end_line - start_line + 1

# Print summary
print("Colony boundaries:")
print("="*80)
for col in colonies_found:
    print(f"{col['name']:40s} Lines {col['start_line']:5d} to {col['end_line']:5d} ({col['num_lines']:5d} lines)")

# Save to file
with open('/home/user/colonial_office_list/output_3/1949_colonies_found.txt', 'w') as f:
    f.write("1949 Colonial Office List - Colony Boundaries\n")
    f.write("="*80 + "\n\n")
    for col in colonies_found:
        f.write(f"{col['name']:40s} Lines {col['start_line']:5d} to {col['end_line']:5d} ({col['num_lines']:5d} lines)\n")
    f.write(f"\nTotal colonies found: {len(colonies_found)}\n")

print(f"\nSaved boundaries to: /home/user/colonial_office_list/output_3/1949_colonies_found.txt")
