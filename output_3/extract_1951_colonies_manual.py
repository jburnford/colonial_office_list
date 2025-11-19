#!/usr/bin/env python3
"""
Extract all colonies from the 1951 Colonial Office List
Manual boundary identification approach
"""

import json
import os
import re
from pathlib import Path
from datetime import datetime

# Colony boundaries manually identified by reading the OCR file
# Each colony's start and end line numbers have been verified
COLONIES = [
    {"name": "Aden", "start": 5176, "end": 6251},
    {"name": "Bahamas", "start": 6252, "end": 6448},
    {"name": "Barbados", "start": 6449, "end": 6981},
    {"name": "Bermuda", "start": 6982, "end": 7542},
    {"name": "British Guiana", "start": 7543, "end": 8478},
    {"name": "British Honduras", "start": 8479, "end": 8954},
    {"name": "Brunei", "start": 8955, "end": 9215},
    {"name": "Cyprus", "start": 9216, "end": 10028},
    {"name": "Falkland Islands", "start": 10029, "end": 10412},
    {"name": "Fiji", "start": 10413, "end": 11527},
    {"name": "Gambia", "start": 11528, "end": 11719},
    {"name": "Gibraltar", "start": 11720, "end": 12846},
    {"name": "Gold Coast", "start": 12847, "end": 13766},
    {"name": "Hong Kong", "start": 13767, "end": 14697},
    {"name": "Jamaica", "start": 14698, "end": 16035},
    {"name": "Kenya", "start": 16036, "end": 17232},
    {"name": "Leeward Islands", "start": 17233, "end": 18374},
    {"name": "Federation of Malaya", "start": 18375, "end": 19829},
    {"name": "Malta", "start": 19830, "end": 20394},
    {"name": "Mauritius", "start": 20395, "end": 21393},
    {"name": "Nigeria", "start": 21394, "end": 23173},
    {"name": "North Borneo", "start": 23174, "end": 23660},
    {"name": "Northern Rhodesia", "start": 23661, "end": 24796},
    {"name": "Nyasaland Protectorate", "start": 24797, "end": 25301},
    {"name": "St. Helena", "start": 25302, "end": 25660},
    {"name": "Sarawak", "start": 25661, "end": 26218},
    {"name": "Seychelles", "start": 26219, "end": 26634},
    {"name": "Sierra Leone", "start": 26635, "end": 27415},
    {"name": "Singapore", "start": 27416, "end": 28564},
    {"name": "Somaliland Protectorate", "start": 28565, "end": 28846},
    {"name": "Tanganyika", "start": 28847, "end": 29554},
    {"name": "Trinidad and Tobago", "start": 29555, "end": 30475},
    {"name": "Uganda", "start": 30476, "end": 31230},
    {"name": "Western Pacific", "start": 31231, "end": 32638},
    {"name": "Windward Islands", "start": 32639, "end": 33669},
    {"name": "Zanzibar", "start": 33670, "end": 34087},
    {"name": "Miscellaneous Islands", "start": 34088, "end": 34417},
]

def remove_line_numbers(text):
    """Remove line number prefixes from text (format: '   123→')"""
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        # Match pattern like '  5176→' or '   123→' (spaces, number, arrow)
        match = re.match(r'^\s*\d+→', line)
        if match:
            cleaned_lines.append(line[match.end():])
        else:
            cleaned_lines.append(line)
    return '\n'.join(cleaned_lines)

def extract_colony(input_file, colony_info, output_dir):
    """Extract a single colony section to a text file"""

    start_line = colony_info['start']
    end_line = colony_info['end']
    colony_name = colony_info['name']

    # Read the specific section
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Extract lines (convert to 0-indexed)
    section_lines = lines[start_line-1:end_line]
    section_text = ''.join(section_lines)

    # Remove line numbers
    cleaned_text = remove_line_numbers(section_text)

    # Create safe filename
    safe_name = colony_name.replace(' ', '_').replace('.', '').lower()
    output_file = output_dir / f"{safe_name}.txt"

    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(cleaned_text)

    # Return metadata
    return {
        'name': colony_name,
        'start_line': start_line,
        'end_line': end_line,
        'line_count': end_line - start_line + 1,
        'char_count': len(cleaned_text),
        'output_file': str(output_file)
    }

def main():
    # Setup paths
    input_file = Path('/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1951/olmocr_results.md')
    output_base = Path('/home/user/colonial_office_list/output_3')
    output_dir = output_base / '1951_manual_parsed'

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"Extracting colonies from 1951 Colonial Office List...")
    print(f"Input: {input_file}")
    print(f"Output: {output_dir}")
    print(f"Total colonies to extract: {len(COLONIES)}\n")

    # Extract all colonies
    metadata_list = []
    for i, colony in enumerate(COLONIES, 1):
        print(f"[{i}/{len(COLONIES)}] Extracting {colony['name']}...")
        try:
            metadata = extract_colony(input_file, colony, output_dir)
            metadata_list.append(metadata)
            print(f"  ✓ Lines {metadata['start_line']}-{metadata['end_line']} ({metadata['line_count']} lines, {metadata['char_count']} chars)")
        except Exception as e:
            print(f"  ✗ Error: {e}")

    # Create JSON metadata file
    json_output = output_base / '1951_manual_parsed.json'
    json_data = {
        'extraction_date': datetime.now().isoformat(),
        'source_file': str(input_file),
        'year': 1951,
        'total_colonies': len(metadata_list),
        'colonies': metadata_list
    }

    with open(json_output, 'w', encoding='utf-8') as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Extraction complete!")
    print(f"  Colonies extracted: {len(metadata_list)}")
    print(f"  Output directory: {output_dir}")
    print(f"  Metadata file: {json_output}")

    # Generate parsing report
    report_file = output_base / '1951_PARSING_REPORT.md'
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# 1951 Colonial Office List - Parsing Report\n\n")
        f.write(f"**Extraction Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"**Source File:** `{input_file}`\n\n")
        f.write(f"**Total Colonies Extracted:** {len(metadata_list)}\n\n")
        f.write("## Colony List\n\n")
        f.write("| # | Colony Name | Start Line | End Line | Lines | Characters |\n")
        f.write("|---|-------------|------------|----------|-------|------------|\n")

        for i, meta in enumerate(metadata_list, 1):
            f.write(f"| {i} | {meta['name']} | {meta['start_line']} | {meta['end_line']} | {meta['line_count']} | {meta['char_count']:,} |\n")

        f.write("\n## Extraction Method\n\n")
        f.write("Manual boundary identification was used to extract colonies from the 1951 Colonial Office List.\n\n")
        f.write("Each colony section was identified by:\n")
        f.write("1. Reading the OCR results file\n")
        f.write("2. Manually locating each colony section based on headers and content\n")
        f.write("3. Verifying boundaries against the table of contents\n")
        f.write("4. Cross-referencing with 1950 (37 colonies) to ensure no colonies were missed\n\n")
        f.write("## Files Generated\n\n")
        f.write(f"- `{output_dir}/` - Directory containing {len(metadata_list)} individual colony text files\n")
        f.write(f"- `{json_output}` - JSON metadata with extraction details\n")
        f.write(f"- `{report_file}` - This parsing report\n")

    print(f"  Parsing report: {report_file}\n")

if __name__ == '__main__':
    main()
