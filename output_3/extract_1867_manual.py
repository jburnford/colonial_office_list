#!/usr/bin/env python3
"""
Extract all colonies from the 1867 Colonial Office List
Using manually identified boundaries.

This is the EARLIEST Colonial Office List we have (just after Confederation of Canada).
Victorian era formatting differs significantly from later years.
"""

import json
import re
from pathlib import Path
from datetime import datetime

# Source file
SOURCE_FILE = "/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1867/olmocr_results.md"

# Output directory
OUTPUT_DIR = Path("/home/user/colonial_office_list/output_3/1867_manual_parsed")

# Manually identified colony boundaries
# Format: (start_line, end_line, colony_name, notes)
COLONIES = [
    (1113, 1373, "ANTIGUA", "Leeward Islands - main seat of government"),
    (1374, 1376, "ANGUILLA", "Brief reference - see St. Christopher's"),
    (1377, 1510, "BAHAMAS", "Chain of islands"),
    (1511, 2200, "BARBADOS", "Caribbee Islands - most windward"),
    (2201, 2426, "BRITISH COLUMBIA", "Marked with asterisk - recently established"),
    (2427, 2927, "BRITISH GUIANA", "South American mainland"),
    (2928, 2936, "BULAMA", "Dependency of Sierra Leone"),
    (2937, 3187, "CANADA", "Just after Confederation - July 1, 1867"),
    (3188, 4059, "CAPE OF GOOD HOPE", "South Africa"),
    (4060, 4523, "CEYLON", "Island colony"),
    (4524, 4640, "DOMINICA", "West Indies"),
    (4641, 5099, "FALKLAND ISLANDS", "South Atlantic"),
    (5100, 5119, "HONDURAS", "Central America"),
    (5120, 5313, "HELIGOLAND", "North Sea island"),
    (5314, 5556, "HONG KONG", "East Asia"),
    (5557, 5962, "JAMAICA", "West Indies"),
    (5963, 7259, "LABUAN", "Southeast Asia"),
    (7260, 7382, "NEVIS", "Leeward Islands"),
    (7383, 7655, "NEW BRUNSWICK", "British North America"),
    (7656, 7871, "NEWFOUNDLAND", "British North America"),
    (7872, 8458, "NEW SOUTH WALES", "Australia"),
    (8459, 8853, "NEW ZEALAND", "Pacific"),
    (8854, 9135, "NOVA SCOTIA", "British North America - marked with asterisk"),
    (9136, 9301, "PRINCE EDWARD ISLAND", "British North America"),
    (9302, 9539, "QUEENSLAND", "Australia"),
    (9540, 9699, "ST. CHRISTOPHER'S AND ANGUILLA (AND NEVIS)", "Combined administration"),
    (9700, 9711, "ANGUILLA", "Full section - part of St. Christopher's government"),
    (9712, 9870, "ST. HELENA", "South Atlantic"),
    (9871, 10069, "ST. LUCIA", "West Indies"),
    (10070, 10340, "SAINT VINCENT", "West Indies"),
    (10341, 10344, "SIERRA LEONE", "West Africa - brief section, see also West African Settlements"),
    (10345, 10904, "SOUTH AUSTRALIA", "Australia"),
    (10905, 11080, "STRAITS SETTLEMENTS", "Southeast Asia"),
    (11081, 11362, "SINGAPORE", "Part of Straits Settlements"),
    (11363, 11678, "TASMANIA", "Australia - formerly Van Diemen's Land"),
    (11679, 12033, "TOBAGO", "West Indies"),
    (12034, 12288, "TRINIDAD", "West Indies"),
    (12289, 12385, "TURKS AND CAICOS ISLANDS", "West Indies"),
    (12386, 13112, "VICTORIA", "Australia"),
    (13113, 13285, "WESTERN AUSTRALIA", "Australia"),
    (13286, 13406, "WEST AFRICAN SETTLEMENTS", "Umbrella administration for Sierra Leone, Gambia, Gold Coast, and Lagos"),
    (13407, 13519, "THE GAMBIA", "West Africa - part of West African Settlements"),
    (13520, 13590, "GOLD COAST", "West Africa - part of West African Settlements"),
    (13591, 13683, "LAGOS", "West Africa - part of West African Settlements - bold formatting"),
    (13684, 13712, "VANCOUVER'S ISLAND", "Pacific Northwest - about to be incorporated into British Columbia"),
]

def remove_line_numbers(text):
    """Remove line number prefixes from extracted text."""
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        # Remove line numbers at start of line
        cleaned_line = re.sub(r'^\s*\d+→', '', line)
        cleaned_lines.append(cleaned_line)
    return '\n'.join(cleaned_lines)

def extract_colonies():
    """Extract all colony sections to individual files."""

    # Create output directory
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    # Read source file
    with open(SOURCE_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    print(f"Total lines in source file: {len(lines)}")
    print(f"Extracting {len(COLONIES)} colonies...\n")

    metadata = {
        "year": 1867,
        "source_file": str(SOURCE_FILE),
        "extraction_date": datetime.now().isoformat(),
        "total_colonies": len(COLONIES),
        "method": "manual boundary identification",
        "notes": "Earliest Colonial Office List - Victorian era formatting - just after Canadian Confederation (July 1, 1867)",
        "colonies": []
    }

    extraction_stats = []

    for start_line, end_line, colony_name, notes in COLONIES:
        # Extract lines (converting from 1-indexed to 0-indexed)
        colony_lines = lines[start_line-1:end_line]
        colony_text = ''.join(colony_lines)

        # Don't remove line numbers - keep original format for now
        # We can clean later if needed

        # Create safe filename
        safe_name = re.sub(r'[^\w\s\-]', '', colony_name)
        safe_name = re.sub(r'\s+', '_', safe_name)
        safe_name = safe_name.lower()

        # Save to file
        output_file = OUTPUT_DIR / f"{safe_name}.txt"
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(colony_text)

        # Calculate statistics
        line_count = len(colony_lines)
        char_count = len(colony_text)

        colony_metadata = {
            "name": colony_name,
            "filename": output_file.name,
            "start_line": start_line,
            "end_line": end_line,
            "line_count": line_count,
            "character_count": char_count,
            "notes": notes
        }

        metadata["colonies"].append(colony_metadata)
        extraction_stats.append((colony_name, start_line, end_line, line_count))

        print(f"✓ {colony_name:45s} | Lines {start_line:5d}-{end_line:5d} ({line_count:4d} lines)")

    # Save metadata
    metadata_file = Path("/home/user/colonial_office_list/output_3/1867_manual_parsed.json")
    with open(metadata_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*80}")
    print(f"Extraction complete!")
    print(f"{'='*80}")
    print(f"Total colonies extracted: {len(COLONIES)}")
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"Metadata file: {metadata_file}")

    return metadata, extraction_stats

def generate_report(metadata, extraction_stats):
    """Generate a detailed parsing report."""

    report_file = Path("/home/user/colonial_office_list/output_3/1867_PARSING_REPORT.md")

    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# 1867 Colonial Office List - Extraction Report\n\n")
        f.write("## Overview\n\n")
        f.write(f"- **Year**: 1867\n")
        f.write(f"- **Extraction Date**: {metadata['extraction_date']}\n")
        f.write(f"- **Total Colonies Extracted**: {metadata['total_colonies']}\n")
        f.write(f"- **Method**: {metadata['method']}\n")
        f.write(f"- **Source File**: `{metadata['source_file']}`\n\n")

        f.write("## Historical Context\n\n")
        f.write("- **Earliest Colonial Office List** we have in the collection\n")
        f.write("- Published just after the **Confederation of Canada** (July 1, 1867)\n")
        f.write("- **Victorian era** administrative structure\n")
        f.write("- Different formatting compared to later years (mix of periods, asterisks, bold text)\n\n")

        f.write("## Extracted Colonies\n\n")
        f.write("| # | Colony Name | Lines | Count | Notes |\n")
        f.write("|---|-------------|-------|-------|-------|\n")

        for i, colony in enumerate(metadata['colonies'], 1):
            f.write(f"| {i:2d} | {colony['name']:45s} | {colony['start_line']:5d}-{colony['end_line']:5d} | {colony['line_count']:4d} | {colony['notes']} |\n")

        f.write("\n## Regional Distribution\n\n")

        # Group by region
        regions = {
            "West Indies / Caribbean": [],
            "British North America": [],
            "Australia": [],
            "West Africa": [],
            "Asia": [],
            "Atlantic Islands": [],
            "South America": [],
            "Pacific": []
        }

        for colony in metadata['colonies']:
            name = colony['name']
            if any(x in name.upper() for x in ['ANTIGUA', 'BAHAMAS', 'BARBADOS', 'DOMINICA', 'JAMAICA', 'NEVIS', 'ST.', 'SAINT', 'TRINIDAD', 'TOBAGO', 'TURKS', 'ANGUILLA', 'LUCIA', 'VINCENT', 'CHRISTOPHER']):
                regions["West Indies / Caribbean"].append(name)
            elif any(x in name.upper() for x in ['CANADA', 'BRUNSWICK', 'NEWFOUNDLAND', 'NOVA SCOTIA', 'PRINCE EDWARD', 'BRITISH COLUMBIA', 'VANCOUVER']):
                regions["British North America"].append(name)
            elif any(x in name.upper() for x in ['WALES', 'QUEENSLAND', 'SOUTH AUSTRALIA', 'TASMANIA', 'VICTORIA', 'WESTERN AUSTRALIA']):
                regions["Australia"].append(name)
            elif any(x in name.upper() for x in ['SIERRA LEONE', 'GAMBIA', 'GOLD COAST', 'LAGOS', 'WEST AFRICAN', 'BULAMA']):
                regions["West Africa"].append(name)
            elif any(x in name.upper() for x in ['CEYLON', 'HONG KONG', 'LABUAN', 'STRAITS', 'SINGAPORE']):
                regions["Asia"].append(name)
            elif any(x in name.upper() for x in ['HELENA', 'FALKLAND', 'HELIGOLAND']):
                regions["Atlantic Islands"].append(name)
            elif 'GUIANA' in name.upper():
                regions["South America"].append(name)
            elif any(x in name.upper() for x in ['ZEALAND', 'CAPE OF GOOD HOPE']):
                regions["Pacific"].append(name)

        for region, colonies in regions.items():
            if colonies:
                f.write(f"### {region} ({len(colonies)})\n\n")
                for colony in colonies:
                    f.write(f"- {colony}\n")
                f.write("\n")

        f.write("## Notable Features of 1867 List\n\n")
        f.write("1. **Mixed Formatting**: Colonies use different header formats:\n")
        f.write("   - Most use `COLONY NAME.` (with period)\n")
        f.write("   - Some use `COLONY NAME` (without period): BARBADOS, TOBAGO\n")
        f.write("   - Some marked with asterisk: BRITISH COLUMBIA.*, NOVA SCOTIA.*\n")
        f.write("   - LAGOS uses bold formatting: `**LAGOS.**`\n\n")

        f.write("2. **Canadian Confederation**: This list is published just after Canada was formed (July 1, 1867)\n")
        f.write("   - Shows pre-Confederation structure with separate provinces\n")
        f.write("   - CANADA appears as a unified entity\n")
        f.write("   - Also shows NEW BRUNSWICK, NOVA SCOTIA, PRINCE EDWARD ISLAND separately\n\n")

        f.write("3. **West African Settlements**: Umbrella administration structure\n")
        f.write("   - SIERRA LEONE appears twice (brief main section + under West African Settlements)\n")
        f.write("   - THE GAMBIA, GOLD COAST, LAGOS grouped under West African Settlements\n")
        f.write("   - BULAMA listed as dependency of Sierra Leone\n\n")

        f.write("4. **Straits Settlements**: Two-tier structure\n")
        f.write("   - STRAITS SETTLEMENTS main section\n")
        f.write("   - SINGAPORE as subsection\n\n")

        f.write("5. **Island Groupings**:\n")
        f.write("   - ST. CHRISTOPHER'S AND ANGUILLA (AND NEVIS) - combined administration\n")
        f.write("   - ANGUILLA appears three times: brief reference, combined section, full section\n")
        f.write("   - NEVIS has its own section but also part of St. Christopher's\n\n")

        f.write("6. **Colonies in Transition**:\n")
        f.write("   - VANCOUVER'S ISLAND noted as \"about to be incorporated into British Columbia\"\n")
        f.write("   - BRITISH COLUMBIA marked with asterisk (recently established)\n\n")

        f.write("## Extraction Statistics\n\n")

        total_lines = sum(c['line_count'] for c in metadata['colonies'])
        avg_lines = total_lines / len(metadata['colonies'])

        f.write(f"- **Total lines extracted**: {total_lines:,}\n")
        f.write(f"- **Average lines per colony**: {avg_lines:.1f}\n")
        f.write(f"- **Smallest colony**: {min(metadata['colonies'], key=lambda x: x['line_count'])['name']} ({min(c['line_count'] for c in metadata['colonies'])} lines)\n")
        f.write(f"- **Largest colony**: {max(metadata['colonies'], key=lambda x: x['line_count'])['name']} ({max(c['line_count'] for c in metadata['colonies'])} lines)\n\n")

        f.write("## Files Created\n\n")
        f.write(f"- **Directory**: `{OUTPUT_DIR}/`\n")
        f.write(f"- **Metadata**: `1867_manual_parsed.json`\n")
        f.write(f"- **Report**: `1867_PARSING_REPORT.md`\n")
        f.write(f"- **Colony text files**: {len(metadata['colonies'])} files\n\n")

        f.write("## Comparison with Later Years\n\n")
        f.write("Notable differences from 1929-1932 lists:\n\n")
        f.write("- **Fewer standardized sections**: Victorian-era lists have more variation\n")
        f.write("- **Different administrative groupings**: West African Settlements structure\n")
        f.write("- **Pre-confederation Canada**: Shows transition period\n")
        f.write("- **British North America**: Multiple separate entities\n")
        f.write("- **HELIGOLAND**: Present in 1867, ceded to Germany in 1890\n")
        f.write("- **VANCOUVER'S ISLAND**: Separate in 1867, later merged with British Columbia\n\n")

        f.write("## Issues and Notes\n\n")
        f.write("- Some colonies have very brief sections (e.g., BULAMA: 9 lines)\n")
        f.write("- SIERRA LEONE appears twice in different contexts\n")
        f.write("- ANGUILLA appears three times with different levels of detail\n")
        f.write("- Mixed formatting styles reflect evolving standardization\n")
        f.write("- Some sections include subsections (Cape Division, Road Works, etc.)\n\n")

        f.write("---\n\n")
        f.write(f"*Generated by extract_1867_manual.py on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*\n")

    print(f"Report generated: {report_file}")
    return report_file

if __name__ == "__main__":
    print("="*80)
    print("1867 COLONIAL OFFICE LIST - MANUAL EXTRACTION")
    print("="*80)
    print()

    metadata, stats = extract_colonies()
    report_file = generate_report(metadata, stats)

    print(f"\n{'='*80}")
    print("All files created successfully!")
    print(f"{'='*80}")
