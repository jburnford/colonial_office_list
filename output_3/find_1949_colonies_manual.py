#!/usr/bin/env python3
"""
Manually identify colony boundaries in the 1949 Colonial Office List
by looking for patterns that indicate the start of a new colony section.
"""

import re

# Read the file
with open('/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1949/olmocr_results.md', 'r') as f:
    lines = f.readlines()

# Colony sections start between ADEN (around line 3793) and PART III (line 29868)
START_SCAN = 3793
END_SCAN = 29868

# Pattern: Colony names are usually followed by standard sections
# Look for lines followed by "SITUATION AND AREA" or similar within 50 lines

colonies = []
i = START_SCAN - 1

while i < END_SCAN - 1:
    line_num = i + 1
    line_text = lines[i].strip()

    # Check if this looks like a colony heading:
    # 1. All caps
    # 2. Reasonable length (4-60 chars)
    # 3. Not a common section header
    if line_text and line_text.isupper() and 4 <= len(line_text) <= 60:
        # Look ahead for indicators this is a colony start
        # Check next 100 lines for "SITUATION AND AREA" or "GENERAL DESCRIPTION" or "CLIMATE"
        is_colony = False
        for j in range(i+1, min(i+100, len(lines))):
            next_line = lines[j].strip()
            if next_line in ['SITUATION AND AREA', 'GENERAL DESCRIPTION', 'CLIMATE', 'POPULATION']:
                # Found a colony indicator
                is_colony = True
                break
            # If we hit another all-caps line that's long, stop searching
            if next_line and next_line.isupper() and len(next_line) > 15:
                if next_line not in ['SITUATION AND AREA', 'GENERAL DESCRIPTION', 'CLIMATE',
                                      'POPULATION', 'RELIGION', 'HISTORY', 'CONSTITUTION',
                                      'ADMINISTRATION', 'SOCIAL SERVICES', 'PUBLIC FINANCE',
                                      'CURRENCY AND BANKING', 'PRODUCTION AND TRADE', 'COMMUNICATIONS',
                                      'TRADE, INDUSTRY AND AGRICULTURE', 'INDUSTRY, TRADE AND CUSTOMS']:
                    break

        if is_colony:
            colonies.append({
                'line': line_num,
                'name': line_text
            })
            print(f"Found colony at line {line_num}: {line_text}")

    i += 1

print(f"\n{'='*80}")
print(f"Total colonies found: {len(colonies)}")
print(f"{'='*80}\n")

# Print them all
for idx, col in enumerate(colonies, 1):
    print(f"{idx:2d}. Line {col['line']:5d}: {col['name']}")

# Save to file
with open('/home/user/colonial_office_list/output_3/1949_colonies_found.txt', 'w') as f:
    f.write(f"Colonies found in 1949 Colonial Office List\n")
    f.write(f"{'='*80}\n\n")
    for idx, col in enumerate(colonies, 1):
        f.write(f"{idx:2d}. Line {col['line']:5d}: {col['name']}\n")

print(f"\nResults saved to 1949_colonies_found.txt")
