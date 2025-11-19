#!/usr/bin/env python3
"""
Script to identify colony section boundaries in the 1961 Colonial Office List.
Uses manual inspection to find where each colony section starts and ends.
"""

import re

def find_colony_boundaries(file_path):
    """Read through the file and identify potential colony section starts."""

    boundaries = []

    with open(file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            # Remove line number prefix and arrow
            content = re.sub(r'^\s*\d+→', '', line).strip()

            # Look for potential colony headers (all caps, standalone lines)
            # These would be major section headers
            if content and len(content) < 80:  # Not too long
                # Check if it's mostly uppercase and looks like a header
                if content.isupper() and not content.startswith('|'):
                    # Exclude common subsection headers
                    if content not in ['AREA', 'POPULATION', 'HISTORY', 'CLIMATE',
                                      'CONSTITUTION', 'GEOGRAPHY', 'TAXATION',
                                      'EDUCATION', 'HEALTH', 'JUDICIARY', 'COMMUNICATIONS',
                                      'CURRENCY', 'TRADE', 'GOVERNORS', 'MINISTERS',
                                      'EXECUTIVE COUNCIL', 'LEGISLATIVE COUNCIL',
                                      'GOVERNMENT', 'ADMINISTRATION', 'DEVELOPMENT',
                                      'PUBLIC FINANCE']:
                        boundaries.append((line_num, content))

    return boundaries

if __name__ == '__main__':
    file_path = '/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1961/olmocr_results.md'

    print("Scanning for potential colony section boundaries...")
    boundaries = find_colony_boundaries(file_path)

    # Filter to likely colony sections (between lines 3900-18000 based on manual inspection)
    colony_boundaries = [(ln, title) for ln, title in boundaries if 3900 <= ln <= 18000]

    print(f"\nFound {len(colony_boundaries)} potential colony sections:\n")
    for line_num, title in colony_boundaries:
        print(f"{line_num:5d}: {title}")
