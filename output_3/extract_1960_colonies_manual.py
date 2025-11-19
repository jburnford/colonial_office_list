#!/usr/bin/env python3
"""
Extract colonies from 1960 Colonial Office List using MANUAL boundary identification.
This is the "Year of Africa" - a pivotal moment in decolonization history.
"""

import json
import os
import re
from pathlib import Path
from datetime import datetime

# MANUALLY IDENTIFIED COLONY BOUNDARIES
# Based on careful reading of the 1960 Colonial Office List structure
COLONIES = [
    {"name": "State of Singapore", "start": 3548, "header_line": 3548},
    {"name": "Aden Colony", "start": 4014, "header_line": 4014},
    {"name": "Bahama Islands", "start": 4601, "header_line": 4601},
    {"name": "Bermuda", "start": 4966, "header_line": 4966},
    {"name": "British Guiana", "start": 5325, "header_line": 5325},
    {"name": "British Honduras", "start": 5798, "header_line": 5798},
    {"name": "Brunei", "start": 6188, "header_line": 6188},
    {"name": "Cyprus", "start": 6493, "header_line": 6493},
    {"name": "Falkland Islands and Dependencies", "start": 6501, "header_line": 6501},
    {"name": "Fiji", "start": 6809, "header_line": 6809},
    {"name": "The Gambia", "start": 7217, "header_line": 7217},
    {"name": "Gibraltar", "start": 7613, "header_line": 7613},
    {"name": "Hong Kong", "start": 7830, "header_line": 7830},
    {"name": "Kenya", "start": 8260, "header_line": 8260},
    {"name": "Malta", "start": 8763, "header_line": 8763},
    {"name": "Mauritius", "start": 9172, "header_line": 9172},
    {"name": "Federation of Nigeria", "start": 9552, "header_line": 9552},
    {"name": "North Borneo", "start": 10305, "header_line": 10305},
    {"name": "Federation of Rhodesia and Nyasaland", "start": 10680, "header_line": 10680},
    {"name": "Northern Rhodesia", "start": 10690, "header_line": 10690},
    {"name": "Nyasaland Protectorate", "start": 11267, "header_line": 11267},
    {"name": "St. Helena", "start": 11674, "header_line": 11674},
    {"name": "Sarawak", "start": 11953, "header_line": 11953},
    {"name": "Seychelles", "start": 12297, "header_line": 12297},
    {"name": "Sierra Leone", "start": 12595, "header_line": 12595},
    {"name": "Somaliland Protectorate", "start": 12974, "header_line": 12974},
    {"name": "Tanganyika", "start": 13248, "header_line": 13248},
    {"name": "Kingdom of Tonga", "start": 13749, "header_line": 13749},
    {"name": "Uganda", "start": 13886, "header_line": 13886},
    {"name": "Virgin Islands", "start": 14423, "header_line": 14423},
    {"name": "The West Indies (Federation)", "start": 14577, "header_line": 14577},
    {"name": "Western Pacific High Commission", "start": 17861, "header_line": 17861},
    {"name": "Zanzibar", "start": 18486, "header_line": 18486},
    {"name": "Miscellaneous Islands", "start": 18777, "header_line": 18777},
    {"name": "The High Commission Territories", "start": 18780, "header_line": 18780},
]

# Part III starts around line 19694 (STAFF section) - this is where Part II ends
PART_II_END = 19693

def sanitize_filename(name):
    """Convert colony name to safe filename."""
    # Remove special characters, replace spaces with underscores
    safe = re.sub(r'[^\w\s-]', '', name)
    safe = re.sub(r'[-\s]+', '_', safe)
    return safe.lower()

def extract_colonies(input_file, output_dir):
    """Extract each colony section to individual files."""

    print(f"Reading {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    total_lines = len(lines)
    print(f"Total lines in file: {total_lines}")

    # Create output directory
    parsed_dir = Path(output_dir) / "1960_manual_parsed"
    parsed_dir.mkdir(parents=True, exist_ok=True)

    metadata = {
        "year": 1960,
        "extraction_date": datetime.now().isoformat(),
        "source_file": input_file,
        "method": "manual_boundary_identification",
        "historical_context": "Year of Africa - 17 African nations gained independence in 1960",
        "note": "British Somaliland, Nigeria, and Cyprus achieved independence in 1960",
        "total_colonies": len(COLONIES),
        "colonies": []
    }

    # Calculate end boundaries for each colony
    for i, colony in enumerate(COLONIES):
        # End is the start of the next colony (or Part II end for the last one)
        if i < len(COLONIES) - 1:
            end_line = COLONIES[i + 1]["start"] - 1
        else:
            end_line = PART_II_END

        colony["end"] = end_line

        # Extract the section (convert to 0-indexed)
        start_idx = colony["start"] - 1
        end_idx = colony["end"]

        section_lines = lines[start_idx:end_idx]

        # Count statistics
        total_section_lines = len(section_lines)
        non_empty_lines = sum(1 for line in section_lines if line.strip())
        word_count = sum(len(line.split()) for line in section_lines)

        # Save to file
        filename = sanitize_filename(colony["name"]) + ".txt"
        output_path = parsed_dir / filename

        with open(output_path, 'w', encoding='utf-8') as f:
            f.writelines(section_lines)

        print(f"✓ Extracted: {colony['name']}")
        print(f"  Lines: {colony['start']}-{colony['end']} ({total_section_lines} lines, {word_count} words)")

        # Add to metadata
        metadata["colonies"].append({
            "name": colony["name"],
            "filename": filename,
            "start_line": colony["start"],
            "end_line": colony["end"],
            "header_line": colony["header_line"],
            "total_lines": total_section_lines,
            "non_empty_lines": non_empty_lines,
            "word_count": word_count,
            "estimated_pages": round(total_section_lines / 50, 1)  # Rough estimate
        })

    # Save metadata
    metadata_path = Path(output_dir) / "1960_manual_parsed.json"
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)

    print(f"\n✓ Metadata saved to: {metadata_path}")

    return metadata

def generate_report(metadata, output_dir):
    """Generate a detailed parsing report."""

    report_path = Path(output_dir) / "1960_PARSING_REPORT.md"

    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# 1960 Colonial Office List - Parsing Report\n\n")
        f.write("## Historical Context: The Year of Africa\n\n")
        f.write("1960 was a watershed year in decolonization history, known as the ")
        f.write("**'Year of Africa'** when 17 African nations gained independence:\n\n")
        f.write("- **Cameroon** (January 1, 1960)\n")
        f.write("- **Togo** (April 27, 1960)\n")
        f.write("- **Mali** (June 20, 1960)\n")
        f.write("- **Senegal** (June 20, 1960)\n")
        f.write("- **Madagascar** (June 26, 1960)\n")
        f.write("- **Democratic Republic of the Congo** (June 30, 1960)\n")
        f.write("- **Somalia** (July 1, 1960) - including British Somaliland\n")
        f.write("- **Benin** (August 1, 1960)\n")
        f.write("- **Niger** (August 3, 1960)\n")
        f.write("- **Burkina Faso** (August 5, 1960)\n")
        f.write("- **Ivory Coast** (August 7, 1960)\n")
        f.write("- **Chad** (August 11, 1960)\n")
        f.write("- **Central African Republic** (August 13, 1960)\n")
        f.write("- **Republic of the Congo** (August 15, 1960)\n")
        f.write("- **Gabon** (August 17, 1960)\n")
        f.write("- **Nigeria** (October 1, 1960) - British colony\n")
        f.write("- **Mauritania** (November 28, 1960)\n\n")
        f.write("Additionally, **Cyprus** gained independence on August 16, 1960.\n\n")

        f.write("## Extraction Methodology\n\n")
        f.write(f"- **Method:** Manual boundary identification by reading content\n")
        f.write(f"- **Date:** {metadata['extraction_date']}\n")
        f.write(f"- **Source:** {metadata['source_file']}\n\n")

        f.write("## Summary Statistics\n\n")
        f.write(f"- **Total Colonies/Territories Extracted:** {metadata['total_colonies']}\n")

        total_lines = sum(c['total_lines'] for c in metadata['colonies'])
        total_words = sum(c['word_count'] for c in metadata['colonies'])

        f.write(f"- **Total Lines Extracted:** {total_lines:,}\n")
        f.write(f"- **Total Words:** {total_words:,}\n")
        f.write(f"- **Average Lines per Colony:** {total_lines // len(metadata['colonies'])}\n")
        f.write(f"- **Average Words per Colony:** {total_words // len(metadata['colonies']):,}\n\n")

        f.write("## Colonies Extracted\n\n")
        f.write("| # | Colony/Territory | Lines | Words | Pages (est.) |\n")
        f.write("|---|-----------------|-------|-------|-------------|\n")

        for i, colony in enumerate(metadata['colonies'], 1):
            f.write(f"| {i} | {colony['name']} | ")
            f.write(f"{colony['total_lines']} | ")
            f.write(f"{colony['word_count']:,} | ")
            f.write(f"{colony['estimated_pages']} |\n")

        f.write("\n## Detailed Colony Information\n\n")

        for colony in metadata['colonies']:
            f.write(f"### {colony['name']}\n\n")
            f.write(f"- **File:** `{colony['filename']}`\n")
            f.write(f"- **Line Range:** {colony['start_line']:,} - {colony['end_line']:,}\n")
            f.write(f"- **Header Line:** {colony['header_line']:,}\n")
            f.write(f"- **Total Lines:** {colony['total_lines']:,}\n")
            f.write(f"- **Non-empty Lines:** {colony['non_empty_lines']:,}\n")
            f.write(f"- **Word Count:** {colony['word_count']:,}\n")
            f.write(f"- **Estimated Pages:** {colony['estimated_pages']}\n\n")

        f.write("## Notable Observations\n\n")
        f.write("### Territories That Gained Independence in 1960\n\n")
        f.write("1. **British Somaliland** (Somaliland Protectorate) - merged with Italian ")
        f.write("Somaliland on July 1, 1960 to form Somalia\n")
        f.write("2. **Nigeria** (Federation of Nigeria) - gained independence on October 1, 1960\n")
        f.write("3. **Cyprus** - gained independence on August 16, 1960\n\n")

        f.write("### Major Changes from 1959\n\n")
        f.write("- Singapore achieved statehood in 1959 with full internal self-government\n")
        f.write("- Federation of Nigeria preparing for independence (October 1960)\n")
        f.write("- Kenya moving towards independence (achieved 1963)\n")
        f.write("- Tanganyika on path to independence (achieved 1961)\n")
        f.write("- Uganda preparing for independence (achieved 1962)\n\n")

        f.write("### Territorial Organization\n\n")
        f.write("- **Federations:** West Indies, Nigeria, Rhodesia and Nyasaland\n")
        f.write("- **Protectorates:** Somaliland, Nyasaland, Bechuanaland, Basutoland, Swaziland\n")
        f.write("- **High Commission Territories:** Basutoland, Bechuanaland, Swaziland\n")
        f.write("- **Special Status:** Singapore (State with internal self-government)\n\n")

        f.write("### Geographic Distribution\n\n")

        regions = {
            "Africa": ["Aden Colony", "The Gambia", "Kenya", "Mauritius", "Federation of Nigeria",
                      "Northern Rhodesia", "Nyasaland Protectorate", "Seychelles", "Sierra Leone",
                      "Somaliland Protectorate", "Tanganyika", "Uganda", "Zanzibar",
                      "The High Commission Territories"],
            "Caribbean/Americas": ["Bahama Islands", "Bermuda", "British Guiana", "British Honduras",
                                   "Virgin Islands", "The West Indies (Federation)"],
            "Asia/Pacific": ["Brunei", "Fiji", "Hong Kong", "North Borneo", "Sarawak",
                           "State of Singapore", "Kingdom of Tonga", "Western Pacific High Commission"],
            "Mediterranean": ["Cyprus", "Gibraltar", "Malta"],
            "Atlantic": ["Falkland Islands and Dependencies", "St. Helena", "Miscellaneous Islands"]
        }

        for region, territories in regions.items():
            count = len([c for c in metadata['colonies'] if c['name'] in territories])
            f.write(f"- **{region}:** {count} territories\n")

        f.write("\n## Challenges and Special Cases\n\n")
        f.write("1. **Federation of Rhodesia and Nyasaland** - Complex structure with separate ")
        f.write("entries for Northern Rhodesia and Nyasaland\n")
        f.write("2. **The West Indies (Federation)** - Multi-island federation with complex ")
        f.write("administrative structure\n")
        f.write("3. **Western Pacific High Commission** - Covering multiple island groups\n")
        f.write("4. **Falkland Islands and Dependencies** - Including Antarctic territories\n")
        f.write("5. **The High Commission Territories** - Administered by High Commissioner ")
        f.write("for Basutoland, the Bechuanaland Protectorate and Swaziland\n\n")

        f.write("## Files Generated\n\n")
        f.write(f"- **Individual colony files:** {len(metadata['colonies'])} files in ")
        f.write("`1960_manual_parsed/`\n")
        f.write("- **Metadata:** `1960_manual_parsed.json`\n")
        f.write("- **This report:** `1960_PARSING_REPORT.md`\n\n")

        f.write("## Conclusion\n\n")
        f.write("The 1960 Colonial Office List captures a pivotal moment in British colonial ")
        f.write("history. This year marked the beginning of the end of the British Empire in ")
        f.write("Africa, with Nigeria (the most populous colony) gaining independence and many ")
        f.write("other territories on the path to self-government. The detailed administrative ")
        f.write("information preserved in this document provides invaluable insight into the ")
        f.write("structure and governance of these territories at this crucial historical juncture.\n\n")

        f.write("---\n\n")
        f.write("*Report generated by manual extraction script*\n")
        f.write(f"*Extraction date: {metadata['extraction_date']}*\n")

    print(f"✓ Report saved to: {report_path}")
    return report_path

if __name__ == '__main__':
    input_file = '/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1960/olmocr_results.md'
    output_dir = '/home/user/colonial_office_list/output_3'

    print("=" * 70)
    print("1960 COLONIAL OFFICE LIST - MANUAL EXTRACTION")
    print("Year of Africa: A Pivotal Moment in Decolonization")
    print("=" * 70)
    print()

    # Extract colonies
    metadata = extract_colonies(input_file, output_dir)

    print()
    print("=" * 70)
    print("GENERATING PARSING REPORT")
    print("=" * 70)
    print()

    # Generate report
    report_path = generate_report(metadata, output_dir)

    print()
    print("=" * 70)
    print("EXTRACTION COMPLETE")
    print("=" * 70)
    print()
    print(f"Total colonies extracted: {len(metadata['colonies'])}")
    print(f"Total lines: {sum(c['total_lines'] for c in metadata['colonies']):,}")
    print(f"Total words: {sum(c['word_count'] for c in metadata['colonies']):,}")
    print()
    print("Output files:")
    print(f"  - Individual files: output_3/1960_manual_parsed/")
    print(f"  - Metadata: output_3/1960_manual_parsed.json")
    print(f"  - Report: output_3/1960_PARSING_REPORT.md")
    print()
