#!/usr/bin/env python3
"""
Extract corrected 1888 colonies based on manual boundary verification.

VERIFIED CORRECTIONS:
1. MAURITIUS: 15271-16180 (was 15271-16885, -705 lines NATAL contamination)
2. QUEENSLAND: 19212-19746 (was 19212-20219, -473 lines ST. HELENA contamination)
3. ST. HELENA: 19747-19836 (was 19747-20219, -383 lines WA contamination)
4. WESTERN AUSTRALIA: 19837-20219 (NEW - was missing entirely!)
5. THE WINDWARD ISLANDS: 20220-20257 (was 20220-21304, -1047 lines contamination)
   Note: Lines 20258-20272 are orphaned headers, not extracted
6. SOUTH AUSTRALIA: 20274-21304 (already correct, will copy from original)
"""

import json
from pathlib import Path

# Source OCR file
source_file = Path('/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1888/olmocr_results.md')

# Output directory
output_dir = Path('/home/user/colonial_office_list/output_2/1888_manual_parsed')
output_dir.mkdir(parents=True, exist_ok=True)

# Read source file
with open(source_file, 'r') as f:
    lines = f.readlines()

# Corrections to apply (colony_name, start_line, end_line)
corrections = [
    ('MAURITIUS', 15271, 16180),
    ('QUEENSLAND', 19212, 19746),
    ('ST_HELENA', 19747, 19836),
    ('WESTERN_AUSTRALIA', 19837, 20219),  # NEW!
    ('THE_WINDWARD_ISLANDS', 20220, 20257),
]

print("=" * 80)
print("EXTRACTING CORRECTED 1888 COLONIES")
print("=" * 80)
print()

for colony_name, start, end in corrections:
    # Extract lines (convert to 0-indexed)
    colony_lines = lines[start-1:end]

    # Write to file
    output_file = output_dir / f"{colony_name}.md"
    with open(output_file, 'w') as f:
        f.writelines(colony_lines)

    actual_lines = len(colony_lines)
    print(f"✅ {colony_name}:")
    print(f"   Lines: {start}-{end} ({actual_lines} lines)")
    print(f"   File: {output_file.name}")
    print()

print("=" * 80)
print("EXTRACTION COMPLETE")
print("=" * 80)
print()
print("Files created in: output_2/1888_manual_parsed/")
print()
print("Note: SOUTH AUSTRALIA (20274-21304) is already correct in original.")
print("      Lines 20258-20272 are orphaned headers, intentionally not extracted.")
print()
print("Next step: Copy remaining colonies from output/1888_manual_parsed/")
print("           (those without overlap issues)")
