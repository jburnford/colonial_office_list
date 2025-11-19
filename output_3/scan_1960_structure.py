#!/usr/bin/env python3
"""
Scan the 1960 Colonial Office List to identify colony section boundaries.
"""

import re

def scan_file_structure(input_file):
    """Scan the file to find all major territory section headers."""

    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Find Part II and Part III boundaries
    part_ii_start = None
    part_iii_start = None

    for i, line in enumerate(lines, 1):
        if 'PART II' in line and i > 3000:  # The actual PART II content
            part_ii_start = i
            print(f"PART II content starts at line {i}")
        elif 'PART III' in line:
            if i > 3000:
                part_iii_start = i
                print(f"PART III starts at line {i}: {line.strip()}")
                break

    if part_iii_start is None:
        print("PART III not found, using end of file")
        part_iii_start = len(lines)

    # Debug: print first 20 lines after PART II
    print("\n\nFirst 20 lines after PART II start:")
    for i in range(part_ii_start - 1, min(part_ii_start + 19, len(lines))):
        print(f"{i+1}: {lines[i].rstrip()}")

    # Now scan for potential territory headers between Part II and Part III
    # Pattern: lines that are in ALL CAPS and relatively short
    # NOTE: The file does NOT have line number prefixes - those are added by the Read tool
    potential_headers = []

    for i in range(part_ii_start - 1, min(part_iii_start, len(lines))):
        line = lines[i]
        content = line.strip()

        # Look for lines that might be section headers
        # Characteristics: all caps, not too long, not empty
        if content and 3 < len(content) < 80:
            # Check if line is all uppercase (allowing spaces, punctuation, and some special chars)
            # Remove common non-letter characters to check
            letters_only = re.sub(r'[^A-Za-z]', '', content)
            if letters_only and letters_only.isupper():
                # Exclude obvious non-headers
                if len(content) < 50:  # Territory names are usually shorter
                    potential_headers.append((i + 1, content))

    print(f"\n\nFound {len(potential_headers)} potential territory headers:\n")
    for line_num, header in potential_headers:
        print(f"Line {line_num}: {header}")

    return potential_headers, part_ii_start, part_iii_start

if __name__ == '__main__':
    input_file = '/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1960/olmocr_results.md'
    scan_file_structure(input_file)
