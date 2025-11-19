#!/usr/bin/env python3
"""
Extract all colonies from the 1883 Colonial Office List
Using manually verified boundaries
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path

# Source file
SOURCE_FILE = "/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1883/olmocr_results.md"
OUTPUT_DIR = "/home/user/colonial_office_list/output_3/1883_manual_parsed"
JSON_FILE = "/home/user/colonial_office_list/output_3/1883_manual_parsed.json"
REPORT_FILE = "/home/user/colonial_office_list/output_3/1883_PARSING_REPORT.md"

# Manually identified colony boundaries
# Format: (colony_name, start_line, end_line, notes)
COLONIES = [
    ("ANTIGUA", 1558, 1559, "Reference to Leeward Islands"),
    ("ANGUILLA", 1561, 1562, "Reference to Leeward Islands"),
    ("BAHAMAS", 1564, 1756, "Full section"),
    ("BARBADOS", 1757, 1759, "Reference to Windward Islands"),
    ("BERMUDA", 1761, 2053, "Full section"),
    ("BRITISH_GUIANA", 2054, 2747, "Full section"),
    ("BRITISH_HONDURAS", 2748, 2948, "Full section"),
    ("DOMINION_OF_CANADA", 2949, 5542, "Full section including provinces"),
    ("CAPE_OF_GOOD_HOPE", 5543, 7551, "Full section"),
    ("CEYLON", 7552, 8217, "Full section"),
    ("DOMINICA", 8218, 8220, "Reference to Leeward Islands"),
    ("FALKLAND_ISLANDS", 8222, 8605, "Full section"),
    ("GIBRALTAR", 8606, 8687, "Full section"),
    ("GOLD_COAST_COLONY", 8688, 8761, "Full section (includes Lagos)"),
    ("LAGOS", 8762, 9303, "Full section (part of Gold Coast Colony)"),
    ("GRENADA", 9304, 9306, "Reference to Windward Islands"),
    ("HELGOLAND", 9308, 9370, "Full section"),
    ("HONG_KONG", 9371, 9677, "Full section"),
    ("JAMAICA", 9678, 10243, "Full section"),
    ("LABUAN", 10244, 10361, "Full section"),
    ("LEEWARD_ISLANDS", 10362, 11573, "Full section including sub-islands"),
    ("MALTA", 11574, 11874, "Full section"),
    ("MAURITIUS", 11875, 12769, "Full section"),
    ("NATAL", 12770, 13387, "Full section"),
    ("NEWFOUNDLAND", 13388, 14616, "Full section"),
    ("NEW_ZEALAND", 14617, 15231, "Full section"),
    ("QUEENSLAND", 15232, 15755, "Full section"),
    ("ST_HELENA", 15756, 15863, "Full section"),
    ("SOUTH_AUSTRALIA", 15864, 17911, "Full section including Northern Territory"),
    ("TOBAGO", 17912, 17914, "Reference to Windward Islands"),
    ("TRINIDAD", 17916, 18645, "Full section"),
    ("TURKS_AND_CAICOS_ISLANDS", 18646, 18718, "Full section"),
    ("VICTORIA", 18719, 19514, "Full section - Australian colony"),
    ("WEST_AFRICA_SETTLEMENTS", 19515, 19516, "Section header"),
    ("SIERRA_LEONE", 19517, 19814, "Full section"),
    ("GAMBIA", 19815, 20429, "Full section"),
    ("WINDWARD_ISLANDS", 20430, 21775, "Full section including sub-islands"),
    ("CYPRUS", 21776, 22077, "Full section"),
]

def remove_line_numbers(text):
    """Remove line number prefixes from extracted text"""
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        # Remove line number prefix pattern (spaces, number, tab)
        cleaned_line = re.sub(r'^\s*\d+→', '', line)
        cleaned_lines.append(cleaned_line)
    return '\n'.join(cleaned_lines)

def extract_colonies():
    """Extract all colony sections from the OCR file"""

    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    # Read the entire source file
    print(f"Reading source file: {SOURCE_FILE}")
    with open(SOURCE_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    total_lines = len(lines)
    print(f"Total lines in source file: {total_lines}")

    # Extract each colony
    extracted_colonies = []

    for colony_name, start_line, end_line, notes in COLONIES:
        print(f"\nExtracting {colony_name} (lines {start_line}-{end_line})...")

        # Extract lines (convert to 0-based indexing)
        colony_lines = lines[start_line-1:end_line]
        colony_text = ''.join(colony_lines)

        # Remove line numbers
        cleaned_text = remove_line_numbers(colony_text)

        # Create filename
        filename = f"{colony_name.lower()}.txt"
        filepath = os.path.join(OUTPUT_DIR, filename)

        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(cleaned_text)

        # Calculate statistics
        line_count = end_line - start_line + 1
        char_count = len(cleaned_text)
        word_count = len(cleaned_text.split())

        print(f"  Lines: {line_count}, Characters: {char_count}, Words: {word_count}")

        # Add to metadata
        extracted_colonies.append({
            "name": colony_name,
            "filename": filename,
            "start_line": start_line,
            "end_line": end_line,
            "line_count": line_count,
            "character_count": char_count,
            "word_count": word_count,
            "notes": notes
        })

    # Create JSON metadata
    metadata = {
        "extraction_date": datetime.now().isoformat(),
        "source_file": SOURCE_FILE,
        "total_source_lines": total_lines,
        "colonies_extracted": len(extracted_colonies),
        "colonies": extracted_colonies
    }

    print(f"\nWriting JSON metadata to: {JSON_FILE}")
    with open(JSON_FILE, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)

    # Create parsing report
    create_report(metadata)

    print(f"\n{'='*60}")
    print(f"EXTRACTION COMPLETE")
    print(f"{'='*60}")
    print(f"Total colonies extracted: {len(extracted_colonies)}")
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"JSON metadata: {JSON_FILE}")
    print(f"Report: {REPORT_FILE}")

    return metadata

def create_report(metadata):
    """Create a detailed parsing report"""

    report = f"""# 1883 Colonial Office List - Parsing Report

## Extraction Summary

- **Extraction Date**: {metadata['extraction_date']}
- **Source File**: {metadata['source_file']}
- **Total Source Lines**: {metadata['total_source_lines']:,}
- **Colonies Extracted**: {metadata['colonies_extracted']}

## Methodology

This extraction was performed using **manual boundary identification**. Each colony section was identified by:
1. Reading the OCR results file systematically
2. Identifying colony headers (typically all-caps followed by a period)
3. Determining section boundaries by context
4. Cross-referencing with neighboring years (1879, 1888)
5. Distinguishing between full sections and references to other sections

## Colony List

| # | Colony Name | Lines | Start | End | Type | Words |
|---|-------------|-------|-------|-----|------|-------|
"""

    for i, colony in enumerate(metadata['colonies'], 1):
        colony_type = "Full" if "Full section" in colony['notes'] else "Ref"
        report += f"| {i} | {colony['name'].replace('_', ' ')} | {colony['line_count']} | {colony['start_line']} | {colony['end_line']} | {colony_type} | {colony['word_count']:,} |\n"

    report += f"""

## Colony Details

"""

    for colony in metadata['colonies']:
        report += f"""### {colony['name'].replace('_', ' ')}
- **File**: `{colony['filename']}`
- **Lines**: {colony['start_line']} - {colony['end_line']} ({colony['line_count']} lines)
- **Content**: {colony['character_count']:,} characters, {colony['word_count']:,} words
- **Notes**: {colony['notes']}

"""

    report += f"""## Notes on 1883 Structure

### Full Sections vs. References

In the 1883 Colonial Office List, some colonies have full dedicated sections while others are simple references to federated groups:

**References Only:**
- ANTIGUA, ANGUILLA, DOMINICA → Leeward Islands
- BARBADOS, GRENADA, TOBAGO → Windward Islands

**Full Sections:**
- LEEWARD ISLANDS (includes details on Antigua, Montserrat, St. Kitts, Nevis, Dominica, Virgin Islands)
- WINDWARD ISLANDS (includes details on sub-islands)
- Major colonies like CANADA, CAPE OF GOOD HOPE, CEYLON, etc.

### Notable Observations

1. **Gold Coast Colony**: This section includes both the Gold Coast Proper and Lagos as separate subsections
2. **Canada**: Very large section covering the Dominion and all provinces
3. **Cape of Good Hope**: Extensive section with many administrative divisions
4. **Leeward and Windward Islands**: Complex federal structures with multiple sub-islands

### Missing or Unusual Entries

- **Straits Settlements**: Not found as a standalone major section in 1883
- **Tasmania**: Appears later in emigration section (line 22155)
- **Western Australia**: Appears in emigration section (line 22189)
- Some Australian colonies appear multiple times (main section + emigration info)

## Comparison with Neighboring Years

- **1879**: 49 colonies extracted
- **1883**: {metadata['colonies_extracted']} colonies/sections extracted
- **1888**: 40 colonies extracted

The 1883 list structure follows the typical pattern with some colonies having full sections and others being references to federated groupings.

## Data Quality

- All line numbers manually verified
- Section boundaries confirmed by reading context
- Line number prefixes removed from extracted text
- UTF-8 encoding preserved throughout

## Files Generated

1. **Individual Colony Files**: {metadata['colonies_extracted']} text files in `1883_manual_parsed/`
2. **JSON Metadata**: `1883_manual_parsed.json` with complete extraction details
3. **This Report**: `1883_PARSING_REPORT.md`

---
*Generated on {datetime.now().strftime('%Y-%m-%d at %H:%M:%S')}*
"""

    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write(report)

    print(f"Report created: {REPORT_FILE}")

if __name__ == "__main__":
    metadata = extract_colonies()
