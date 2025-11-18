#!/usr/bin/env python3
"""
Extract all colonies from the 1888 Colonial Office List using manually identified boundaries.
"""

import os
import json
from datetime import datetime

# Manually identified colony boundaries (start lines)
colonies = [
    ("BAHAMAS", 1562),
    ("BARBADOS", 1871),
    ("BASUTOLAND", 2496),
    ("BERMUDA", 2615),
    ("BRITISH GUIANA", 3158),
    ("BRITISH HONDURAS", 3957),
    ("DOMINION OF CANADA", 4309),
    ("CAPE OF GOOD HOPE", 7923),
    ("CEYLON", 9844),
    ("FALKLAND ISLANDS", 10598),
    ("FIJI", 10771),
    ("GIBRALTAR", 11197),
    ("HELIGOLAND", 11720),
    ("HONG KONG", 11843),
    ("JAMAICA", 12207),
    ("LABUAN", 12873),
    ("LEEWARD ISLANDS - ANTIGUA", 13497),
    ("LEEWARD ISLANDS - ST. CHRISTOPHER AND NEVIS", 13995),
    ("LEEWARD ISLANDS - VIRGIN ISLANDS", 14354),
    ("LEEWARD ISLANDS - DOMINICA", 14485),
    ("MAURITIUS", 15271),
    ("NATAL", 16181),
    ("NEWFOUNDLAND", 16886),
    ("NEW SOUTH WALES", 17873),
    ("NEW ZEALAND", 18304),
    ("QUEENSLAND", 19212),
    ("ST. HELENA", 19747),
    ("SOUTH AUSTRALIA", 20274),
    ("STRAITS SETTLEMENTS", 21305),
    ("TASMANIA", 22197),
    ("TRINIDAD", 22612),
    ("VICTORIA", 23622),
    ("SIERRA LEONE", 25072),
    ("WESTERN AUSTRALIA", 25719),
    ("WINDWARD ISLANDS - GRENADA", 25874),
    ("WINDWARD ISLANDS - ST. LUCIA", 26266),
    ("WINDWARD ISLANDS - ST. VINCENT", 26580),
    ("WINDWARD ISLANDS - TOBAGO", 26897),
    ("ZULULAND", 27147),
    ("CYPRUS", 27429),
    ("ASCENSION", 28033),
]

# Sort by start line to ensure proper ordering
colonies.sort(key=lambda x: x[1])

# OCR file path
ocr_file = "/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1888/olmocr_results.md"

# Output directory
output_dir = "/home/user/colonial_office_list/output_3/1888_manual_parsed"
os.makedirs(output_dir, exist_ok=True)

# Read the entire OCR file
print(f"Reading OCR file: {ocr_file}")
with open(ocr_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

total_lines = len(lines)
print(f"Total lines in OCR file: {total_lines}")

# Extract each colony
metadata = {
    "year": 1888,
    "source_file": "historical_document_pipeline/processed_pdfs/colonial-office-list-1888/olmocr_results.md",
    "extraction_date": datetime.now().strftime("%Y-%m-%d"),
    "extraction_method": "manual_llm_boundary_identification",
    "total_ocr_lines": total_lines,
    "colonies": []
}

for i, (colony_name, start_line) in enumerate(colonies):
    # Determine end line (start of next colony - 1, or EOF)
    if i < len(colonies) - 1:
        end_line = colonies[i + 1][1] - 1
    else:
        end_line = total_lines

    print(f"\nExtracting {colony_name}:")
    print(f"  Start line: {start_line}")
    print(f"  End line: {end_line}")
    print(f"  Total lines: {end_line - start_line + 1}")

    # Extract content (convert to 0-indexed)
    content_lines = lines[start_line - 1:end_line]

    # Clean up the content - remove line number prefixes
    cleaned_lines = []
    for line in content_lines:
        # Remove line number prefix (format: "1234→TEXT")
        if '→' in line:
            parts = line.split('→', 1)
            if len(parts) == 2:
                cleaned_lines.append(parts[1])
            else:
                cleaned_lines.append(line)
        else:
            cleaned_lines.append(line)

    content = ''.join(cleaned_lines)

    # Create filename (sanitize colony name)
    filename = colony_name.replace(" ", "_").replace("-", "_").replace(",", "").upper() + ".txt"
    filepath = os.path.join(output_dir, filename)

    # Write colony file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"  Saved to: {filepath}")

    # Add to metadata
    metadata["colonies"].append({
        "colony_name": colony_name,
        "start_line": start_line,
        "end_line": end_line,
        "line_count": end_line - start_line + 1,
        "file": f"output_3/1888_manual_parsed/{filename}"
    })

# Save metadata JSON
metadata_file = "/home/user/colonial_office_list/output_3/1888_manual_parsed.json"
with open(metadata_file, 'w', encoding='utf-8') as f:
    json.dump(metadata, f, indent=2)

print(f"\n{'='*60}")
print(f"Extraction complete!")
print(f"{'='*60}")
print(f"Total colonies extracted: {len(colonies)}")
print(f"Output directory: {output_dir}")
print(f"Metadata file: {metadata_file}")
print(f"\nColonies extracted:")
for colony in metadata["colonies"]:
    print(f"  - {colony['colony_name']} ({colony['line_count']} lines)")
