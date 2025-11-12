#!/usr/bin/env python3
"""
Find all colony boundaries in 1890 by looking for patterns.
"""

with open('/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1890/olmocr_results.md', 'r') as f:
    lines = f.readlines()

# Look for lines that are likely colony headers (all caps, ends with period, short)
potential_colonies = []
for i, line in enumerate(lines, start=1):
    stripped = line.strip()
    # Colony headers are typically: ALL CAPS, end with period, 5-40 chars
    if stripped and stripped.endswith('.') and len(stripped) >= 5 and len(stripped) <= 50:
        if stripped.isupper() and stripped[:-1].replace(' ', '').replace('-', '').replace('THE', '').isalpha():
            potential_colonies.append((i, stripped))

# Print colonies in the problematic range
print("Potential colony headers in range 20000-23500:")
print("=" * 80)
for line_num, text in potential_colonies:
    if 20000 <= line_num <= 23500:
        print(f"Line {line_num}: {text}")
