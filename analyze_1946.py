#!/usr/bin/env python3
"""
Analyze 1946 Colonial Office List structure to identify colony boundaries.
"""

from pathlib import Path
import re

source_file = Path('historical_document_pipeline/processed_pdfs/colonial-office-list-1946/olmocr_results.md')

with open(source_file, 'r') as f:
    lines = f.readlines()

# Find major section headers
print("=" * 80)
print("MAJOR SECTIONS")
print("=" * 80)
for i, line in enumerate(lines, 1):
    stripped = line.strip()
    if stripped in ['PART I', 'PART II', 'PART III', 'APPENDIX'] or 'PART II A' in stripped:
        print(f"{i:5d}: {stripped}")
        # Print next few lines for context
        for j in range(1, min(5, len(lines) - i)):
            print(f"       {lines[i+j-1].strip()}")
        print()

# Find potential colony headers (all caps, reasonable length)
print("\n" + "=" * 80)
print("POTENTIAL COLONY HEADERS (lines 2600-16000)")
print("=" * 80)

colony_headers = []
for i in range(2600, min(16000, len(lines))):
    line = lines[i].strip()

    # Colony header patterns:
    # 1. Short all-caps lines (likely colony names)
    # 2. Followed by "SITUATION AND AREA" or similar
    if (line and line.isupper() and
        5 < len(line) < 80 and
        not any(skip in line for skip in ['PART II', 'PART III', 'PAGE ', 'CONTINUED',
                                          'SITUATION', 'CLIMATE', 'HISTORY', 'CONSTITUTION',
                                          'POPULATION', 'ADMINISTRATION', 'RELIGION',
                                          'CURRENCY', 'COMMUNICATIONS', 'SOCIAL SERVICES',
                                          'REVENUE', 'EXECUTIVE', 'LEGISLATIVE', 'COUNCIL',
                                          'FOREIGN', 'REPRESENTATIVES', 'EDUCATION',
                                          'IMPORTS', 'EXPORTS', 'GENERAL DESCRIPTION'])):

        # Check if next non-empty line looks like a section header
        next_lines = []
        for j in range(1, 10):
            if i + j < len(lines):
                next_line = lines[i + j].strip()
                if next_line:
                    next_lines.append(next_line)
                    if len(next_lines) >= 3:
                        break

        # If followed by typical section headers, likely a colony
        if any(header in ' '.join(next_lines) for header in ['SITUATION', 'CLIMATE', 'AREA', 'HISTORY']):
            colony_headers.append((i + 1, line))
            print(f"{i+1:5d}: {line}")
            for nl in next_lines[:2]:
                print(f"       {nl}")
            print()

print(f"\nFound {len(colony_headers)} potential colony headers")
