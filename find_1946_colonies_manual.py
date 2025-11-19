#!/usr/bin/env python3
"""
Manually identify all colony boundaries in the 1946 Colonial Office List.
Based on careful reading of the OCR file.
"""

import json

# Manually identified colony boundaries (1-indexed line numbers)
# Based on visual inspection of the 1946 Colonial Office List

colonies = [
    {"name": "Aden", "start_line": 2667, "end_line": 2990},
    {"name": "Bahamas", "start_line": 2991, "end_line": 3354},
    {"name": "Barbados", "start_line": 3355, "end_line": 3949},
    {"name": "British Guiana", "start_line": 3950, "end_line": 4596},
    {"name": "British Honduras", "start_line": 4597, "end_line": 4831},
    {"name": "Ceylon", "start_line": 4832, "end_line": 5439},
    {"name": "Cyprus", "start_line": 5440, "end_line": 5852},
    {"name": "Falkland Islands", "start_line": 5853, "end_line": 6106},
    {"name": "Fiji", "start_line": 6107, "end_line": 6483},
    {"name": "Gambia", "start_line": 6484, "end_line": 6949},
    {"name": "Gold Coast", "start_line": 6950, "end_line": 7479},
    {"name": "Hong Kong", "start_line": 7480, "end_line": 7483},
    {"name": "Jamaica", "start_line": 7484, "end_line": 8512},
    {"name": "Kenya", "start_line": 8513, "end_line": 8913},
    {"name": "Leeward Islands", "start_line": 8914, "end_line": 9997},
    {"name": "Mauritius", "start_line": 9998, "end_line": 10505},
    {"name": "Nigeria", "start_line": 10506, "end_line": 11047},
    {"name": "North Borneo", "start_line": 11048, "end_line": 11051},
    {"name": "Northern Rhodesia", "start_line": 11052, "end_line": 11419},
    {"name": "Nyasaland", "start_line": 11420, "end_line": 11590},
    {"name": "Palestine", "start_line": 11591, "end_line": 12003},
    {"name": "St. Helena", "start_line": 12004, "end_line": 12200},
    {"name": "Seychelles", "start_line": 12201, "end_line": 12368},
    {"name": "Sierra Leone", "start_line": 12369, "end_line": 12693},
    {"name": "Singapore", "start_line": 12694, "end_line": 12696},
    {"name": "Somaliland Protectorate", "start_line": 12697, "end_line": 13180},
    {"name": "Trinidad", "start_line": 13181, "end_line": 13899},
    {"name": "Western Pacific", "start_line": 13900, "end_line": 14323},
    {"name": "Windward Islands", "start_line": 14324, "end_line": 15609},
]

def main():
    print(f"{'='*80}")
    print(f"1946 COLONIAL OFFICE LIST - MANUALLY IDENTIFIED COLONIES")
    print(f"{'='*80}\n")
    
    print(f"Found {len(colonies)} colonies/territories in Part II:\n")
    
    for i, colony in enumerate(colonies, 1):
        lines_count = colony['end_line'] - colony['start_line'] + 1
        print(f"{i:2d}. {colony['name']:30s} Lines {colony['start_line']:5d}-{colony['end_line']:5d} ({lines_count:4d} lines)")
    
    # Note missing colonies
    missing = [
        "Bermuda", "Gibraltar", "Malaya", "Malta", "Sarawak", 
        "Tanganyika Territory", "Uganda", "Zanzibar"
    ]
    
    print(f"\n{'='*80}")
    print("MISSING FROM PART II (only in Part III staff lists):")
    print(f"{'='*80}\n")
    
    for colony in missing:
        print(f"  - {colony} (likely military administration or special circumstances)")
    
    # Save to JSON
    output_file = '/home/user/colonial_office_list/output_3/1946_colonies_found.txt'
    with open(output_file, 'w') as f:
        json.dump(colonies, f, indent=2)
    
    print(f"\n{'='*80}")
    print(f"Colony boundaries saved to: {output_file}")
    print(f"{'='*80}\n")
    
    # Summary statistics
    total_lines = sum(c['end_line'] - c['start_line'] + 1 for c in colonies)
    print(f"Total colonies: {len(colonies)}")
    print(f"Total lines covered: {total_lines}")
    print(f"Part II ends at line: 15610")

if __name__ == "__main__":
    main()
