#!/usr/bin/env python3
"""
Extract corrected 1890 colonies based on manual boundary verification.

VERIFIED CORRECTIONS:
1. MAURITIUS: 15414-16422 (was 15414-17069, -647 lines of NATAL contamination)
2. NATAL: 16423-17069 (already correct)
3. SOUTH AUSTRALIA: 20508-21538 (was 20508-22802, -1264 lines)
4. STRAITS SETTLEMENTS: 21539-22326 (was 21539-22802, -476 lines TASMANIA contamination)
5. TASMANIA: 22327-22802 (NEW - was missing entirely!)
"""

import json
from pathlib import Path

# Source OCR file
source_file = Path('/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1890/olmocr_results.md')

# Output directory
output_dir = Path('/home/user/colonial_office_list/output_2/1890_manual_parsed')
output_dir.mkdir(parents=True, exist_ok=True)

# Read source file
with open(source_file, 'r') as f:
    lines = f.readlines()

# Corrections to apply (colony_name, start_line, end_line)
corrections = [
    ('MAURITIUS', 15414, 16422),
    ('SOUTH_AUSTRALIA', 20508, 21538),
    ('STRAITS_SETTLEMENTS', 21539, 22326),
    ('TASMANIA', 22327, 22802),  # NEW!
]

print("=" * 80)
print("EXTRACTING CORRECTED 1890 COLONIES")
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
print("Files created in: output_2/1890_manual_parsed/")
print()
print("Next step: Copy remaining colonies from output/1890_manual_parsed/")
print("           (those without overlap issues)")
