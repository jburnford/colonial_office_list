#!/usr/bin/env python3
"""
Extract all colonies from the 1958 Colonial Office List using MANUAL boundary identification.
This is a high-priority extraction due to 40 missing colonies from automated extraction.
"""

import json
import os
import re
from pathlib import Path

# Input and output paths
INPUT_FILE = "/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1958/olmocr_results.md"
OUTPUT_DIR = "/home/user/colonial_office_list/output_3/1958_manual_parsed"
METADATA_FILE = "/home/user/colonial_office_list/output_3/1958_manual_parsed.json"

# Create output directory
os.makedirs(OUTPUT_DIR, exist_ok=True)

print("=" * 80)
print("1958 COLONIAL OFFICE LIST - MANUAL EXTRACTION")
print("HIGH-PRIORITY: 40 missing colonies from automated extraction")
print("=" * 80)

# Read the OCR results file
print("\nReading OCR file...")
with open(INPUT_FILE, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Total lines in file: {len(lines)}")

# MANUALLY IDENTIFIED BOUNDARIES
# These are 1-based line numbers from Read tool analysis
# Array indices are 0-based (subtract 1)
#
# Each entry: (name, start_line, is_cross_reference)
# Cross-references don't have full sections, just point to West Indies Federation

COLONIES = [
    ("Aden", 3378, False),
    ("Bahama Islands", 3864, False),
    ("Barbados", 4218, True),  # See West Indies
    ("Bermuda", 4221, False),
    ("British Guiana", 4573, False),
    ("British Honduras", 5065, False),
    ("Brunei", 5441, False),
    ("Cyprus", 5722, False),
    ("Falkland Islands and Dependencies", 6205, False),
    ("Fiji", 6527, False),
    ("Gambia", 6842, False),
    ("Gibraltar", 7213, False),
    ("Hong Kong", 7466, False),
    ("Jamaica", 7934, True),  # See West Indies
    ("Kenya", 7939, False),
    ("Leeward Islands", 8462, False),
    ("Federation of Malaya", 8602, False),
    ("Malta", 8608, False),
    ("Mauritius", 9146, False),
    ("Federation of Nigeria", 9536, False),
    ("North Borneo", 10184, False),
    ("Northern Rhodesia", 10412, False),
    ("Nyasaland Protectorate", 11063, False),
    ("St. Helena", 11450, False),
    ("Sarawak", 11748, False),
    ("Seychelles", 12056, False),
    ("Sierra Leone", 12363, False),
    ("Singapore", 12761, False),
    ("Somaliland Protectorate", 13181, False),
    ("Tanganyika", 13468, False),
    ("Tonga", 13912, False),
    ("Trinidad and Tobago", 7934, True),  # Same as Jamaica, see West Indies
    ("Uganda", 14051, False),
    ("West Indies Federation", 14515, False),
    ("Western Pacific", 17835, False),
    ("Zanzibar", 18473, False),
    ("Miscellaneous Islands", 18767, False),
    ("High Commission Territories", 18770, False),
]

# Part III starts at line 19708, marking the end of Part II
PART_II_END = 19708

# Calculate boundaries for each colony
print("\nCalculating colony boundaries...")
colony_data = []

# Sort colonies by start line to ensure correct ordering
sorted_colonies = sorted(enumerate(COLONIES), key=lambda x: x[1][1])

for i, (idx, (name, start_line, is_cross_ref)) in enumerate(sorted_colonies):
    start_index = start_line - 1  # Convert to 0-based array index

    # Find end line (start of next colony or end of Part II)
    if i < len(sorted_colonies) - 1:
        # End is one line before the next colony starts
        next_start_line = sorted_colonies[i + 1][1][1]
        end_line = next_start_line - 1
    else:
        # Last colony ends at Part II end
        end_line = PART_II_END - 1

    end_index = end_line - 1  # Convert to 0-based array index

    # Extract content (skip the header line itself, start from next line)
    # Actually, let's include the header line for context
    colony_lines = lines[start_index:end_index + 1]

    # Join and clean up
    content = ''.join(colony_lines).strip()

    # Count statistics
    line_count = len(colony_lines)
    word_count = len(content.split())
    char_count = len(content)

    colony_info = {
        'name': name,
        'filename': name.lower().replace(' ', '_').replace(',', ''),
        'start_line': start_line,
        'end_line': end_line,
        'start_index': start_index,
        'end_index': end_index,
        'line_count': line_count,
        'word_count': word_count,
        'char_count': char_count,
        'is_cross_reference': is_cross_ref,
        'original_index': idx
    }

    colony_data.append(colony_info)

    # Save to individual file
    output_file = os.path.join(OUTPUT_DIR, f"{colony_info['filename']}.txt")
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(content)

    status = "CROSS-REF" if is_cross_ref else "EXTRACTED"
    print(f"  [{status}] {name:40s} | Lines {start_line:5d}-{end_line:5d} | {line_count:4d} lines | {word_count:6d} words")

# Sort colony_data back to original order for output
colony_data.sort(key=lambda x: x['original_index'])

# Create comprehensive metadata
metadata = {
    'source_file': INPUT_FILE,
    'extraction_date': '2025-11-19',
    'extraction_method': 'manual_boundary_identification',
    'part_ii_start': 3377,
    'part_ii_end': PART_II_END,
    'total_colonies': len(colony_data),
    'total_cross_references': sum(1 for c in colony_data if c['is_cross_reference']),
    'total_full_sections': sum(1 for c in colony_data if not c['is_cross_reference']),
    'total_lines_extracted': sum(c['line_count'] for c in colony_data),
    'total_words_extracted': sum(c['word_count'] for c in colony_data),
    'colonies': colony_data,
    'notes': [
        'Ghana became independent in 1957, so not in 1958 list',
        'West Indies Federation was formed in 1958',
        'Some territories are cross-references to West Indies Federation',
        'High Commission Territories includes Basutoland, Bechuanaland, and Swaziland',
    ]
}

# Save metadata
print(f"\nSaving metadata to {METADATA_FILE}...")
with open(METADATA_FILE, 'w', encoding='utf-8') as f:
    json.dump(metadata, f, indent=2)

# Print summary
print("\n" + "=" * 80)
print("EXTRACTION SUMMARY")
print("=" * 80)
print(f"Total colonies/territories: {metadata['total_colonies']}")
print(f"  - Full sections: {metadata['total_full_sections']}")
print(f"  - Cross-references: {metadata['total_cross_references']}")
print(f"Total lines extracted: {metadata['total_lines_extracted']:,}")
print(f"Total words extracted: {metadata['total_words_extracted']:,}")
print(f"\nOutput directory: {OUTPUT_DIR}")
print(f"Metadata file: {METADATA_FILE}")
print("\n" + "=" * 80)

# Print notable observations
print("\nNOTABLE OBSERVATIONS:")
print("1. Ghana became independent in 1957, hence not in this 1958 Colonial Office List")
print("2. The West Indies Federation was established in 1958")
print("3. Several territories (Barbados, Jamaica, Trinidad & Tobago, Windward Islands)")
print("   are listed as cross-references to the West Indies Federation")
print("4. The High Commission Territories section covers Basutoland, Bechuanaland,")
print("   and Swaziland together")
print("5. Some territories appear with special formatting (**, ###) in headers")
print("\n" + "=" * 80)
print("EXTRACTION COMPLETE")
print("=" * 80)
