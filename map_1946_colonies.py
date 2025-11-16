#!/usr/bin/env python3
"""
Map all colonies in 1946 by finding major headers and their boundaries.
"""

from pathlib import Path
import re

source_file = Path('historical_document_pipeline/processed_pdfs/colonial-office-list-1946/olmocr_results.md')

with open(source_file, 'r') as f:
    lines = f.readlines()

# Define known colony patterns
COLONY_PATTERNS = [
    'ADEN', 'BAHAMA', 'BARBADOS', 'BERMUDA', 'BRITISH GUIANA', 'BRITISH HONDURAS',
    'CEYLON', 'CYPRUS', 'FALKLAND', 'FIJI', 'GAMBIA', 'GIBRALTAR', 'GOLD COAST',
    'GRENADA', 'HONG KONG', 'JAMAICA', 'KENYA', 'LEEWARD ISLANDS', 'MALTA',
    'MAURITIUS', 'NIGERIA', 'NORTH BORNEO', 'NORTHERN RHODESIA', 'NYASALAND',
    'PALESTINE', 'ST. HELENA', 'ST. LUCIA', 'ST. VINCENT', 'SARAWAK', 'SEYCHELLES',
    'SIERRA LEONE', 'SINGAPORE', 'SOMALILAND', 'TANGANYIKA', 'TRINIDAD',
    'UGANDA', 'WINDWARD ISLANDS', 'ZANZIBAR', 'DOMINICA', 'MONTSERRAT', 'ANTIGUA',
    'PROTECTORATE', 'ISLANDS', 'SOLOMON'
]

# Find all potential colony headers (start of sections)
colonies = []
part_iii_start = None

for i, line in enumerate(lines, 1):
    stripped = line.strip()

    # Find PART III boundary
    if stripped == 'PART III' and i > 10000:
        part_iii_start = i
        break

    # Find APPENDIX before PART III
    if stripped == 'APPENDIX' and i > 10000 and 'MISCELLANEOUS' in ''.join(lines[i:i+5]):
        part_iii_start = i
        break

# Search for colony headers in PART II.B (lines 2600 to PART III)
print(f"Searching for colonies from line 2600 to {part_iii_start}")
print("=" * 80)

for i in range(2600, part_iii_start if part_iii_start else 16000):
    line = lines[i-1].strip()

    # Skip if not potential header
    if not line or len(line) < 5 or len(line) > 100:
        continue

    # Check if it matches colony pattern
    is_colony = False
    for pattern in COLONY_PATTERNS:
        if pattern in line and (line.isupper() or line.startswith('**')):
            # Verify it's not a subsection header
            if not any(skip in line for skip in ['SITUATION', 'CLIMATE', 'HISTORY',
                                                  'CONSTITUTION', 'POPULATION', 'ADMINISTRATION',
                                                  'RELIGION', 'CURRENCY', 'COMMUNICATIONS',
                                                  'REVENUE', 'EXECUTIVE', 'LEGISLATIVE',
                                                  'COUNCIL', 'FOREIGN', 'REPRESENTATIVES',
                                                  'EDUCATION', 'IMPORTS', 'EXPORTS',
                                                  'GENERAL DESCRIPTION', 'SOCIAL SERVICES']):
                is_colony = True
                break

    if is_colony:
        # Check next lines for section headers
        next_lines = []
        for j in range(1, 5):
            if i + j - 1 < len(lines):
                next_line = lines[i + j - 1].strip()
                if next_line:
                    next_lines.append(next_line)

        # If followed by typical section headers, it's a colony
        has_section_header = any(h in ' '.join(next_lines) for h in
                                ['SITUATION', 'AREA', 'CLIMATE', 'HISTORY', 'DESCRIPTION'])

        if has_section_header or (len(line) < 40 and line.count(' ') < 5):
            colonies.append((i, line))
            print(f"{i:5d}: {line}")

print(f"\n\nFound {len(colonies)} colonies")
print("=" * 80)

# Print with boundaries
if colonies:
    for idx, (line_num, name) in enumerate(colonies):
        if idx < len(colonies) - 1:
            end_line = colonies[idx + 1][0] - 1
        else:
            end_line = part_iii_start - 1 if part_iii_start else 15604

        line_count = end_line - line_num + 1
        print(f"{line_num:5d}-{end_line:5d} ({line_count:5d} lines): {name}")
