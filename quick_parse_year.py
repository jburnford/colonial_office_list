#!/usr/bin/env python3
"""
Quick parser for years 1962-1966.
Uses similar structure detection as 1961.
"""

import re
import json
import sys
from pathlib import Path

if len(sys.argv) < 2:
    print("Usage: python3 quick_parse_year.py YEAR")
    print("Example: python3 quick_parse_year.py 1962")
    sys.exit(1)

year = sys.argv[1]

# Paths
ocr_file = Path(f'historical_document_pipeline/processed_pdfs/colonial-office-list-{year}/olmocr_results.md')
output_dir = Path(f'output_2/{year}_manual_parsed')
output_dir.mkdir(parents=True, exist_ok=True)

if not ocr_file.exists():
    print(f"ERROR: OCR file not found: {ocr_file}")
    sys.exit(1)

# Read file
with open(ocr_file, 'r') as f:
    lines = f.readlines()

print(f"Processing year {year}")
print(f"Total lines: {len(lines)}\n")

# Find territory starts by looking for pattern:
# - Standalone line (all caps or title case)
# - Followed by "Area" or similar within 5 lines
territories = []
SECTION_INDICATORS = ['Area', 'Population', 'History', 'Government', 'Geography',
                     'Geographical', 'Climate', 'Constitution', 'The area',
                     'The total area', 'Situation']

for i in range(2500, min(20000, len(lines))):  # Start search after admin sections
    line = lines[i].strip()

    if not line or len(line) < 4:
        continue
    if line.startswith('|') or line.startswith('#') or line.startswith('-'):
        continue
    if any(char.isdigit() for char in line[:10]):
        continue
    if line.endswith(':'):
        continue

    # Check next lines
    next_text = ' '.join([lines[i+j].strip() for j in range(1, min(6, len(lines)-i))])

    is_territory = any(indicator in next_text for indicator in SECTION_INDICATORS)

    if is_territory:
        # Must be mostly uppercase or title case
        if line.isupper() or (line[0].isupper() and sum(1 for c in line if c.isupper()) > len(line) * 0.3):
            territories.append((i+1, line))

# Remove duplicates and sort
seen = set()
unique_territories = []
for line_num, name in territories:
    if name not in seen:
        seen.add(name)
        unique_territories.append((line_num, name))

print(f"Found {len(unique_territories)} potential territories:\n")
for line_num, name in unique_territories:
    print(f"  Line {line_num}: {name}")

print("\n" + "="*80)
print("Creating territory files...")
print("="*80 + "\n")

# Create boundaries (each territory ends where next begins, or at line 20000)
extracted = []
for i, (start_line, name) in enumerate(unique_territories):
    end_line = unique_territories[i+1][0] - 1 if i+1 < len(unique_territories) else min(20000, len(lines))

    # Extract content
    content = ''.join(lines[start_line-1:end_line])

    # Create filename
    filename = name.replace(' ', '_').replace(',', '').replace('(', '').replace(')', '').replace("'", '').replace('.', '') + '.md'

    # Write file
    output_file = output_dir / filename
    with open(output_file, 'w') as f:
        f.write(content)

    extracted.append({
        'name': name,
        'filename': filename,
        'start_line': start_line,
        'end_line': end_line,
        'line_count': end_line - start_line + 1
    })

    print(f"  {name}: {start_line}-{end_line} ({end_line - start_line + 1} lines)")

# Create metadata
metadata = {
    "year": int(year),
    "total_colonies": len(extracted),
    "parsing_method": "Quick LLM-based automatic parsing (output_2)",
    "parsing_date": "November 16, 2025",
    "notes": [
        f"First-time parsing for year {year}",
        "Decolonization period - territories declining as independence granted",
        "Automatic boundary detection - may need manual verification"
    ],
    "colonies": []
}

for territory in extracted:
    metadata["colonies"].append({
        "name": territory['name'],
        "filename": territory['filename'],
        "start_line": territory['start_line'],
        "end_line": territory['end_line'],
        "line_count": territory['line_count'],
        "is_appendix": False,
        "extraction_method": "automatic_llm_parsing"
    })

# Write metadata
metadata_file = Path(f'output_2/{year}_manual_parsed.json')
with open(metadata_file, 'w') as f:
    json.dump(metadata, f, indent=2)

print(f"\n✅ Year {year} parsed successfully")
print(f"   Territories: {len(extracted)}")
print(f"   Output: {output_dir}")
print(f"   Metadata: {metadata_file}")
