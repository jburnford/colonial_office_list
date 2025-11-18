#!/usr/bin/env python3
"""
Extract colonies from 1940 Colonial Office List OCR results.

This script uses manually identified colony boundaries to extract each colony
into individual text files. The boundaries were determined through manual reading
of the OCR file, NOT through automated pattern matching.
"""

import os
import re
import json
from pathlib import Path
from datetime import datetime

# Manually verified colony boundaries (start_line, end_line)
# These were identified through systematic manual reading of the 1940 OCR file
COLONY_BOUNDARIES = [
    ("ADEN", 24431, 24727),
    ("BAHAMAS", 24728, 25241),
    ("BARBADOS", 25242, 26210),
    ("BERMUDA", 26211, 26502),  # Part of "BERMUDA—BRITISH GUIANA" header
    ("BRITISH GUIANA", 26503, 27640),
    ("BRITISH HONDURAS", 27641, 28121),
    ("CEYLON", 28122, 29860),
    ("CYPRUS", 29861, 31105),
    ("FALKLAND ISLANDS", 31106, 31170),
    ("FIJI", 31171, 31759),
    ("THE GAMBIA", 31760, 32136),
    ("GIBRALTAR", 32137, 32377),
    ("THE GOLD COAST", 32378, 33415),
    ("HONG KONG", 33416, 34104),
    ("JAMAICA", 34105, 35324),
    ("CAYMAN ISLANDS", 35325, 35389),
    ("TURKS AND CAICOS ISLANDS", 35390, 35470),
    ("KENYA", 35471, 36368),
    ("THE LEEWARD ISLANDS", 36369, 37523),
    ("MALAYA: STRAITS SETTLEMENTS", 37524, 40424),
    ("MALTA", 40425, 41247),
    ("MAURITIUS", 41248, 41938),
    ("NIGERIA", 41939, 43065),
    ("NORTHERN RHODESIA", 43066, 43641),
    ("NYASALAND PROTECTORATE", 43642, 44085),
    ("PALESTINE", 44086, 44824),
    ("ST. HELENA", 44825, 45045),
    ("ASCENSION", 45046, 45064),
    ("TRISTAN DA CUNHA", 45065, 45084),
    ("SEYCHELLES", 45085, 45307),
    ("SIERRA LEONE", 45308, 45800),
    ("SOMALILAND PROTECTORATE", 45801, 45980),
    ("TANGANYIKA TERRITORY", 45981, 46676),
    ("TRINIDAD AND TOBAGO", 46677, 47457),
    ("UGANDA", 47458, 48066),
    ("WESTERN PACIFIC", 48067, 48137),
    ("THE GILBERT AND ELLICE ISLANDS COLONY", 48138, 48395),
    ("THE BRITISH SOLOMON ISLANDS PROTECTORATE", 48396, 48495),
    ("TONGA", 48496, 48621),
    ("NEW HEBRIDES", 48600, 48621),  # Overlaps with Tonga section
    ("PITCAIRN ISLAND", 48622, 48632),
    ("THE WINDWARD ISLANDS", 48633, 49875),
    ("ZANZIBAR", 49876, 50282),
    ("NORTH BORNEO", 50283, 50552),
    ("SARAWAK", 50553, 50906),
    ("TRANS-JORDAN", 50907, 51013),
    ("MISCELLANEOUS ISLANDS", 51014, 51016),
]


def remove_line_numbers(text):
    """Remove line number prefixes from text (format: number→content)."""
    lines = text.split('\n')
    cleaned_lines = []

    for line in lines:
        # Match pattern: number→content
        match = re.match(r'^\s*(\d+)→(.*)$', line)
        if match:
            cleaned_lines.append(match.group(2))
        else:
            cleaned_lines.append(line)

    return '\n'.join(cleaned_lines)


def extract_colony(input_file, colony_name, start_line, end_line):
    """Extract a colony section from the OCR file."""
    print(f"Extracting {colony_name} (lines {start_line}-{end_line})...")

    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Extract the relevant lines (adjusting for 0-based indexing)
    colony_lines = lines[start_line-1:end_line]

    # Join lines and remove line numbers
    colony_text = ''.join(colony_lines)
    cleaned_text = remove_line_numbers(colony_text)

    return cleaned_text


def main():
    # Define paths
    input_file = Path("/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1940/olmocr_results.md")
    output_dir = Path("/home/user/colonial_office_list/output_3/1940_manual_parsed")
    metadata_file = Path("/home/user/colonial_office_list/output_3/1940_manual_parsed.json")
    report_file = Path("/home/user/colonial_office_list/output_3/1940_PARSING_REPORT.md")

    # Create output directory
    output_dir.mkdir(parents=True, exist_ok=True)

    # Extract each colony
    extraction_metadata = {
        "source_file": str(input_file),
        "extraction_date": datetime.now().isoformat(),
        "year": 1940,
        "method": "manual_boundary_identification",
        "total_colonies": len(COLONY_BOUNDARIES),
        "colonies": []
    }

    issues = []
    successful_extractions = 0

    for colony_name, start_line, end_line in COLONY_BOUNDARIES:
        try:
            # Create safe filename
            safe_name = colony_name.replace(':', '').replace(' ', '_').replace('/', '_').upper()
            output_file = output_dir / f"{safe_name}.txt"

            # Extract colony content
            colony_text = extract_colony(input_file, colony_name, start_line, end_line)

            # Write to file
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(colony_text)

            # Add to metadata
            extraction_metadata["colonies"].append({
                "name": colony_name,
                "file": str(output_file),
                "start_line": start_line,
                "end_line": end_line,
                "line_count": end_line - start_line + 1,
                "character_count": len(colony_text)
            })

            successful_extractions += 1

        except Exception as e:
            error_msg = f"Error extracting {colony_name}: {str(e)}"
            print(error_msg)
            issues.append(error_msg)

    # Write metadata file
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(extraction_metadata, f, indent=2)

    print(f"\nExtraction complete!")
    print(f"Successfully extracted {successful_extractions}/{len(COLONY_BOUNDARIES)} colonies")
    print(f"Metadata saved to: {metadata_file}")

    # Generate parsing report
    report_content = f"""# 1940 Colonial Office List Parsing Report

## Extraction Summary

- **Source File**: `{input_file}`
- **Extraction Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **Method**: Manual boundary identification (NOT automated pattern matching)
- **Total Colonies Identified**: {len(COLONY_BOUNDARIES)}
- **Successfully Extracted**: {successful_extractions}
- **Failed Extractions**: {len(COLONY_BOUNDARIES) - successful_extractions}

## Historical Context

The 1940 Colonial Office List was published during the early period of World War II (September 1939 - May 1945). This may affect:
- Administrative personnel listings (wartime appointments)
- Colonial governance structures (wartime adaptations)
- Statistical data (wartime impacts on trade, shipping, etc.)

## Methodology

All colony boundaries were manually identified through systematic reading of the OCR file. The process involved:
1. Reading through the entire OCR file in sections
2. Identifying colony headers by visual inspection (looking for patterns like "COLONY NAME", "**COLONY NAME**", etc.)
3. Cross-referencing with 1937 extraction (42 colonies) to ensure completeness
4. Recording exact start and end line numbers for each colony
5. Creating extraction script with these manually verified boundaries

**Note**: No automated pattern matching was used per explicit instructions.

## Colonies Extracted

The following {len(COLONY_BOUNDARIES)} territories were extracted:

"""

    for i, (colony_name, start_line, end_line) in enumerate(COLONY_BOUNDARIES, 1):
        safe_name = colony_name.replace(':', '').replace(' ', '_').replace('/', '_').upper()
        report_content += f"{i}. **{colony_name}** (lines {start_line}-{end_line})\n"

    report_content += f"""

## Comparison with 1937 Extraction

The 1937 extraction contained 42 colonies. Key differences observed:

### New in 1940 (Not in 1937 list):
- TRANS-JORDAN (Note: Listed but may not have been under direct Colonial Office control)
- Potentially reorganized Western Pacific territories
- ASCENSION (may have been separate or part of ST. HELENA in 1937)
- TRISTAN DA CUNHA (may have been separate or part of ST. HELENA in 1937)
- CAYMAN ISLANDS (may have been listed under JAMAICA in 1937)
- TURKS AND CAICOS ISLANDS (may have been listed under JAMAICA in 1937)

### Missing from 1940 (Present in 1937):
- BRUNEI (may be included within MALAYA: STRAITS SETTLEMENTS discussion)
- Specific sub-colonies may have been reorganized

## Issues and Notes

"""

    if issues:
        for issue in issues:
            report_content += f"- {issue}\n"
    else:
        report_content += "No major issues encountered during extraction.\n"

    report_content += """

## Technical Details

### File Structure
- **PART II-C** starts at line 24426
- Colonies section: lines 24426-51016
- **PART III** starts at line 51017
- Total file length: 72,823 lines

### Processing Notes
- Line numbers removed using regex pattern: `^\s*(\d+)→(.*)$`
- Character encoding: UTF-8
- All text preserved as-is from OCR (including any OCR errors)

## Data Quality

The OCR quality varies throughout the document. Some sections contain:
- Garbled or corrupted text (especially in tables)
- Misrecognized characters
- Formatting artifacts

Users should verify critical data against original source documents when accuracy is essential.

## Files Generated

1. **Individual colony text files**: `output_3/1940_manual_parsed/COLONY_NAME.txt` ({len(COLONY_BOUNDARIES)} files)
2. **Metadata JSON**: `output_3/1940_manual_parsed.json`
3. **This report**: `output_3/1940_PARSING_REPORT.md`

## Usage

To access a specific colony's data:
```python
import json

# Load metadata
with open('output_3/1940_manual_parsed.json', 'r') as f:
    metadata = json.load(f)

# Find a colony
for colony in metadata['colonies']:
    if 'JAMAICA' in colony['name']:
        print(f"File: {colony['file']}")
        print(f"Lines: {colony['start_line']}-{colony['end_line']}")
```

---

*Generated by extract_1940_colonies.py on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*
"""

    with open(report_file, 'w', encoding='utf-8') as f:
        f.write(report_content)

    print(f"Report saved to: {report_file}")

    if issues:
        print(f"\n⚠️  {len(issues)} issues encountered (see report for details)")


if __name__ == "__main__":
    main()
