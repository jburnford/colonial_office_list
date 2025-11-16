#!/usr/bin/env python3
"""
Find all territories in 1961 by looking for section patterns.
Territories typically start with a name, followed by "Area" or similar sections.
"""

import re
from pathlib import Path

# OCR file
ocr_file = Path('historical_document_pipeline/processed_pdfs/colonial-office-list-1961/olmocr_results.md')

# Read file
with open(ocr_file, 'r') as f:
    lines = f.readlines()

print(f"Total lines: {len(lines)}\n")

# Find territories by looking for patterns like:
# LINE: TERRITORY NAME
# LINE+1: (blank or short)
# LINE+2-5: "Area" or "Population" or "History" or "Government" or "Geography"

territories = []

# Start from line 3489 (STATE OF SINGAPORE) to 29537 (INDEX)
for i in range(3488, min(29537, len(lines))):
    line = lines[i].strip()

    # Skip empty lines or very short lines
    if not line or len(line) < 4:
        continue

    # Skip lines that are clearly not territory headers
    if line.startswith('|') or line.startswith('#') or line.startswith('-'):
        continue
    if any(char.isdigit() for char in line[:10]):  # Skip if starts with numbers (tables, dates)
        continue
    if line.endswith(':'):  # Skip labeled lists
        continue

    # Look ahead to see if this could be a territory header
    # Check next few lines for common section headers
    next_lines = []
    for j in range(1, min(6, len(lines) - i)):
        next_lines.append(lines[i+j].strip())

    next_text = ' '.join(next_lines[:3])

    # Common section headers that follow territory names
    section_indicators = [
        'Area', 'Population', 'History', 'Government', 'Geography',
        'Geographical', 'Climate', 'Constitution', 'The area',
        'The total area', 'was possessed', 'is a', 'consists of'
    ]

    is_territory = False
    for indicator in section_indicators:
        if indicator in next_text:
            is_territory = True
            break

    if is_territory:
        # Make sure it's mostly uppercase or title case (territory names)
        if line.isupper() or (line[0].isupper() and sum(1 for c in line if c.isupper()) > len(line) * 0.3):
            territories.append((i+1, line, next_text[:100]))

# Print results
print("=" * 80)
print("TERRITORIES FOUND")
print("=" * 80)
print()

for line_num, name, context in territories:
    print(f"Line {line_num}: {name}")
    print(f"  Context: {context}")
    print()

print(f"\nTotal territories found: {len(territories)}")
