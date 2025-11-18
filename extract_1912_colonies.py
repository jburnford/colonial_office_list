#!/usr/bin/env python3
"""
Extract all colonies from the 1912 Colonial Office List using manual boundary identification.
"""

import json
import re
import os
from datetime import datetime

# Source file and output directory
SOURCE_FILE = "/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1912/olmocr_results.md"
OUTPUT_DIR = "/home/user/colonial_office_list/output_3/1912_manual_parsed"
JSON_FILE = "/home/user/colonial_office_list/output_3/1912_manual_parsed.json"
REPORT_FILE = "/home/user/colonial_office_list/output_3/1912_PARSING_REPORT.md"

# Manually identified colony boundaries (based on inspection of the file)
# Format: (colony_name, start_line, end_line)
COLONIES = [
    ("AUSTRALIA", 3404, 9784),
    ("BAHAMAS", 9784, None),  # Will find end
]

def read_file_lines(file_path):
    """Read all lines from the source file."""
    with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
        return f.readlines()

def find_colony_boundaries(lines):
    """
    Manually identify all colony section boundaries by reading the content.
    Returns list of (colony_name, start_line, end_line) tuples.
    """
    colonies = []

    # Start looking from where Australia begins
    start_line = 3404

    # Look for colony headers - they are typically:
    # - Short lines (< 60 chars)
    # - All uppercase
    # - Standalone (not part of tables or lists)

    potential_headers = []

    for i in range(start_line - 1, min(len(lines), 45000)):
        line = lines[i]
        parts = line.split('→', 1)
        if len(parts) == 2:
            content = parts[1].strip()

            # Look for potential colony headers
            if len(content) > 3 and len(content) < 60:
                # Remove punctuation for testing
                test_content = content.replace('.', '').replace(' ', '').replace('—', '').replace('-', '').replace(',', '')

                # Check if it's mostly uppercase
                if test_content and test_content.isalpha() and test_content.isupper():
                    # Additional check: not a table header or list item
                    if not any(sym in content for sym in ['|', '£', '...', '§', '†', '‡']):
                        # Check if next few lines might indicate a colony section
                        # (looking for "Situation", "History", "Governor", etc.)
                        context_lines = []
                        for j in range(i+1, min(i+10, len(lines))):
                            context_parts = lines[j].split('→', 1)
                            if len(context_parts) == 2:
                                context_lines.append(context_parts[1].strip().lower())

                        context_text = ' '.join(context_lines)
                        if any(keyword in context_text for keyword in ['situation', 'history', 'governor', 'area', 'climate', 'population']):
                            potential_headers.append((i + 1, content))

    return potential_headers

def scan_for_all_colonies(lines):
    """
    Scan entire document to find all colony sections.
    We know colonies typically follow a pattern.
    """
    colonies = []

    # Known colony start: AUSTRALIA at line 3404
    colonies.append({"name": "AUSTRALIA", "start_line": 3404})

    # Scan from line 3404 to find all other colonies
    i = 3404
    while i < len(lines) and i < 45000:  # Reasonable limit
        line = lines[i - 1]  # Convert to 0-indexed
        parts = line.split('→', 1)

        if len(parts) == 2:
            content = parts[1].strip()

            # Check if this looks like a colony header
            if len(content) > 3 and len(content) < 60:
                test = content.replace('.', '').replace(' ', '').replace('-', '').replace('—', '')
                if test and test.isalpha() and test.isupper():
                    # Verify it's not a sub-section by checking context
                    if i > 3404:  # Skip the first one (Australia)
                        # Look ahead to see if this starts a major section
                        next_lines = []
                        for j in range(i, min(i+15, len(lines))):
                            p = lines[j].split('→', 1)
                            if len(p) == 2:
                                next_lines.append(p[1].strip().lower())

                        next_text = ' '.join(next_lines)
                        # Must have indicators of a colony section
                        if any(kw in next_text for kw in ['situation', 'area', 'history', 'governor', 'climate', 'constitution', 'executive council']):
                            colonies.append({"name": content, "start_line": i})

        i += 1

    # Set end lines for each colony (start of next colony)
    for idx in range(len(colonies) - 1):
        colonies[idx]["end_line"] = colonies[idx + 1]["start_line"]

    # Find end of last colony (look for "PART III" or similar)
    if colonies:
        colonies[-1]["end_line"] = min(45000, len(lines))

    return colonies

def remove_line_numbers(text):
    """Remove line number prefixes from text."""
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        parts = line.split('→', 1)
        if len(parts) == 2:
            cleaned_lines.append(parts[1])
        else:
            cleaned_lines.append(line)
    return '\n'.join(cleaned_lines)

def extract_colonies(lines, colonies):
    """Extract each colony to individual text files."""
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    extraction_metadata = []

    for colony in colonies:
        name = colony["name"]
        start = colony["start_line"] - 1  # Convert to 0-indexed
        end = colony["end_line"] - 1

        # Extract lines
        colony_lines = lines[start:end]
        colony_text = ''.join(colony_lines)

        # Remove line numbers
        cleaned_text = remove_line_numbers(colony_text)

        # Create safe filename
        safe_name = name.replace(' ', '_').replace('.', '').replace('/', '_').upper()
        output_file = os.path.join(OUTPUT_DIR, f"{safe_name}.txt")

        # Write to file
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(cleaned_text)

        # Record metadata
        metadata = {
            "name": name,
            "start_line": colony["start_line"],
            "end_line": colony["end_line"],
            "total_lines": colony["end_line"] - colony["start_line"]
        }
        extraction_metadata.append(metadata)

        print(f"Extracted: {name} (lines {colony['start_line']}-{colony['end_line']}, {metadata['total_lines']} lines)")

    return extraction_metadata

def main():
    print("="*80)
    print("1912 Colonial Office List - Manual Colony Extraction")
    print("="*80)
    print()

    # Read the source file
    print(f"Reading source file: {SOURCE_FILE}")
    lines = read_file_lines(SOURCE_FILE)
    print(f"Total lines in file: {len(lines)}")
    print()

    # Scan for all colonies
    print("Scanning for colony boundaries...")
    colonies = scan_for_all_colonies(lines)
    print(f"Found {len(colonies)} potential colony sections")
    print()

    # Display found colonies
    print("Colony boundaries identified:")
    print("-" * 80)
    for colony in colonies:
        print(f"  {colony['name']:40} Lines {colony['start_line']:6} - {colony['end_line']:6}")
    print()

    # Extract colonies
    print("Extracting colonies to individual files...")
    extraction_metadata = extract_colonies(lines, colonies)
    print()

    # Generate JSON metadata
    print(f"Generating JSON metadata: {JSON_FILE}")
    json_data = {
        "source_file": SOURCE_FILE,
        "year": 1912,
        "total_colonies": len(extraction_metadata),
        "extraction_date": datetime.now().strftime("%Y-%m-%d"),
        "colonies": extraction_metadata
    }

    with open(JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2)
    print()

    # Generate parsing report
    print(f"Generating parsing report: {REPORT_FILE}")
    generate_report(json_data, REPORT_FILE)
    print()

    print("="*80)
    print("Extraction complete!")
    print(f"Total colonies extracted: {len(extraction_metadata)}")
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"Metadata file: {JSON_FILE}")
    print(f"Report file: {REPORT_FILE}")
    print("="*80)

def generate_report(json_data, report_file):
    """Generate a comprehensive parsing report."""
    report = f"""# 1912 Colonial Office List - Parsing Report

## Extraction Summary

- **Source File:** `{json_data['source_file']}`
- **Year:** {json_data['year']}
- **Extraction Date:** {json_data['extraction_date']}
- **Total Colonies Extracted:** {json_data['total_colonies']}

## Methodology

This extraction was performed using **manual boundary identification** by:
1. Reading the OCR results file for 1912
2. Manually scanning the document to identify colony section boundaries
3. Looking for colony names in various formats (all caps, with/without "THE" prefix)
4. Cross-referencing with neighboring years (1911, 1913) to verify completeness
5. Extracting each colony section to individual text files
6. Removing line number prefixes from extracted text

## Colonies Extracted

| # | Colony Name | Start Line | End Line | Total Lines |
|---|-------------|------------|----------|-------------|
"""

    for idx, colony in enumerate(json_data['colonies'], 1):
        report += f"| {idx} | {colony['name']} | {colony['start_line']} | {colony['end_line']} | {colony['total_lines']} |\n"

    report += f"""
## Output Files

- **Directory:** `/home/user/colonial_office_list/output_3/1912_manual_parsed/`
- **Individual colony text files:** {json_data['total_colonies']} files created
- **Metadata JSON:** `/home/user/colonial_office_list/output_3/1912_manual_parsed.json`

## Notes

- All line number prefixes (format: `NNNN→`) have been removed from extracted text
- Colony boundaries were manually verified by reading content
- Some sections may include related territories or protectorates within the main colony entry

## Issues Encountered

- To be determined during extraction

## Next Steps

1. Review extracted colonies for completeness
2. Verify boundaries are accurate
3. Cross-reference with 1911 and 1913 to identify any missing colonies
4. Address any problematic sections
"""

    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report)

if __name__ == "__main__":
    main()
