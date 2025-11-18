#!/usr/bin/env python3
"""Find all colony headings in the 1888 Colonial Office List OCR file."""

import re

# Read the OCR file
ocr_file = "/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1888/olmocr_results.md"

with open(ocr_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find lines that look like colony headings
# These are typically:
# - All uppercase (or mostly uppercase)
# - Standalone (not part of a larger sentence)
# - After line 1500 (where actual colonies start)

potential_colonies = []

for i, line in enumerate(lines, 1):
    stripped = line.strip()

    # Remove line number prefix if present (format: "1234→TEXT")
    if '→' in stripped:
        parts = stripped.split('→', 1)
        if len(parts) == 2:
            stripped = parts[1]

    # Skip if empty
    if not stripped:
        continue

    # Check if it's after the introduction section
    if i < 1500:
        continue

    # Check if it's all uppercase letters (allowing spaces, hyphens, dots, ampersands, commas, parentheses)
    # and is relatively short (likely a heading, not a full sentence)
    if stripped and len(stripped) < 80:
        # Count uppercase vs total letters
        letters = [c for c in stripped if c.isalpha()]
        if letters:
            uppercase_count = sum(1 for c in letters if c.isupper())
            uppercase_ratio = uppercase_count / len(letters)

            # If mostly uppercase (>80%) and not too long, likely a heading
            if uppercase_ratio > 0.8:
                # Filter out some common non-colony headings
                skip_patterns = [
                    r'^\d',  # Starts with number
                    r'^[IVX]+\.',  # Roman numerals
                    r'^TABLE',
                    r'^PART\s',
                    r'^SECTION',
                    r'^CHAPTER',
                    r'^APPENDIX',
                    r'DIGITIZED BY',
                    r'^PAGE\s',
                    r'^VOL\.',
                ]

                should_skip = False
                for pattern in skip_patterns:
                    if re.match(pattern, stripped, re.IGNORECASE):
                        should_skip = True
                        break

                if not should_skip:
                    potential_colonies.append((i, stripped))

# Print findings
print(f"Found {len(potential_colonies)} potential colony headings:\n")
for line_num, text in potential_colonies[:200]:  # Limit output
    print(f"Line {line_num}: {text}")
