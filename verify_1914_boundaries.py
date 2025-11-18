#!/usr/bin/env python3
"""
Verify and extract exact colony boundaries for 1914
"""

import re

input_file = "/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1914/olmocr_results.md"

# Potential colony starting lines based on initial search
potential_starts = [
    3519,   # AUSTRALIA
    10611,  # BAHAMAS
    10992,  # BARBADOS
    11500,  # BERMUDA
    11858,  # BRITISH GUIANA
    12812,  # BRITISH HONDURAS
    13170,  # DOMINION OF CANADA
    16359,  # CEYLON
    17510,  # CYPRUS
    18351,  # EAST AFRICA PROTECTORATE
    18775,  # FALKLAND ISLANDS
    18976,  # FIJI
    19646,  # THE GAMBIA
    20333,  # THE GOLD COAST
    21275,  # HONG KONG
    21929,  # JAMAICA
    22812,  # THE LEEWARD ISLANDS
    24464,  # MALTA
    24982,  # MAURITIUS
    25800,  # NEWFOUNDLAND
    26152,  # NEW ZEALAND
    27391,  # NIGERIA
    28568,  # NYASALAND PROTECTORATE
    28999,  # SEYCHELLES
    29318,  # SIERRA LEONE
    29767,  # SOMALILAND PROTECTORATE
    29958,  # SOUTH AFRICA
    33225,  # STRAITS SETTLEMENTS
    34771,  # TRINIDAD AND TOBAGO
    36170,  # TURKS AND CAICOS ISLANDS
    36344,  # UGANDA
    36792,  # WESTERN PACIFIC
    36992,  # THE WINDWARD ISLANDS
    38012,  # ZANZIBAR
    38086,  # APPENDIX (end marker)
]

with open(input_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print("Verifying colony boundaries...\n")

colonies = []

for i, start_line in enumerate(potential_starts[:-1]):  # Exclude the last APPENDIX marker
    # Read the line and a few around it
    line_num = start_line - 1  # Convert to 0-indexed
    if line_num < len(lines):
        # Get the colony name from the line
        colony_line = lines[line_num].strip()
        # Remove line number prefix if present
        colony_name = re.sub(r'^\d+→', '', colony_line).strip()

        # Get the next colony's start line (or APPENDIX)
        end_line = potential_starts[i + 1] - 1
        line_count = end_line - start_line

        # Show context
        print(f"\nColony #{i+1}:")
        print(f"  Start Line: {start_line}")
        print(f"  Name: {colony_name}")
        print(f"  End Line: {end_line}")
        print(f"  Line Count: {line_count}")

        # Show first few lines of content
        print(f"  First lines:")
        for j in range(start_line - 1, min(start_line + 2, len(lines))):
            content = lines[j].strip()
            if content:
                display = content[:80] + "..." if len(content) > 80 else content
                print(f"    {j+1}: {display}")

        colonies.append({
            "name": colony_name,
            "start_line": start_line,
            "end_line": end_line,
            "line_count": line_count
        })

print(f"\n{'='*80}")
print(f"Total colonies identified: {len(colonies)}")
print(f"{'='*80}")

# Save results
import json
output = {
    "year": 1914,
    "total_colonies": len(colonies),
    "colonies": colonies
}

with open("/home/user/colonial_office_list/1914_preliminary_boundaries.json", "w") as f:
    json.dump(output, f, indent=2)

print(f"\nPreliminary boundaries saved to: /home/user/colonial_office_list/1914_preliminary_boundaries.json")
