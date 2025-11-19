#!/usr/bin/env python3
"""
Extract individual colony sections from 1880 Colonial Office List
Using manually identified boundaries
Following the same methodology as 1879 extraction
"""

import os
import re
import json
from datetime import datetime
from pathlib import Path

# Define input/output paths
INPUT_FILE = "/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1880/olmocr_results.md"
OUTPUT_DIR = "/home/user/colonial_office_list/output_3/1880_manual_parsed"
METADATA_FILE = "/home/user/colonial_office_list/output_3/1880_manual_parsed.json"
REPORT_FILE = "/home/user/colonial_office_list/output_3/1880_PARSING_REPORT.md"

# Manually identified colony boundaries
# Format: (colony_name, start_line, end_line, notes)
COLONIES = [
    # Reference sections (short cross-references)
    ("ANTIGUA", 988, 990, "Reference to Leeward Islands"),
    ("ANGUILLA", 991, 993, "Reference to Leeward Islands"),
    ("BARBADOS_REF", 1244, 1247, "Reference to Windward Islands"),
    ("DOMINICA_REF", 6514, 6517, "Reference to Leeward Islands"),
    ("GRENADE_REF", 7439, 7442, "Reference to Windward Islands"),
    ("NEVIS_REF", 11583, 11586, "Reference to Leeward Islands"),
    ("TOBAGO_REF", 15502, 15504, "Reference to Windward Islands"),

    # Full colony sections
    ("BAHAMAS", 994, 1243, "Full section"),
    ("BERMUDAS", 1249, 1504, "Full section"),
    ("BRITISH_GUIANA", 1506, 2225, "Full section"),
    ("BRITISH_HONDURAS", 2227, 2429, "Full section"),
    ("DOMINION_OF_CANADA", 2431, 4542, "Full section including provinces"),
    ("CAPE_OF_GOOD_HOPE", 4544, 5966, "Full section"),
    ("CEYLON", 5968, 6513, "Full section"),
    ("FALKLAND_ISLANDS", 6518, 6648, "Full section"),
    ("FIJI", 6650, 6769, "Full section - FIJI returns in 1880"),
    ("GIBRALTAR", 6771, 6876, "Full section"),
    ("THE_GOLD_COAST_COLONY", 6878, 7438, "Full section - includes Lagos subsection at 6954"),
    ("GRIQUALAND_WEST", 7443, 7681, "Full section"),
    ("HELIGOLAND", 7683, 7726, "Full section"),
    ("HONG_KONG", 7727, 8013, "Full section"),
    ("JAMAICA", 8014, 8647, "Full section"),
    ("LABUAN", 8649, 8755, "Full section"),
    ("LEEWARD_ISLANDS", 8756, 9958, "Full consolidated section"),
    ("MALTA", 9959, 10287, "Full section - no header"),
    ("MAURITIUS", 10289, 11043, "Full section"),
    ("NATAL", 11044, 11582, "Full section"),
    ("NEWFOUNDLAND", 11587, 11837, "Full section"),
    ("NEW_SOUTH_WALES", 11838, 12675, "Full section"),
    ("NEW_ZEALAND", 12677, 13168, "Full section"),
    ("QUEENSLAND", 13169, 13575, "Full section - no header"),
    ("ST_HELENA", 13576, 13678, "Full section"),
    ("SOUTH_AUSTRALIA", 13680, 14738, "Full section"),
    ("STRAITS_SETTLEMENTS", 14739, 15182, "Full section"),
    ("TASMANIA", 15184, 15501, "Full section"),
    ("THE_TRANSVAAL", 15505, 15684, "Full section - annexed 1877"),
    ("TRINIDAD", 15686, 16452, "Full section"),
    ("TURKS_AND_CAICOS_ISLANDS", 16454, 16526, "Full section"),
    ("VICTORIA", 16528, 17100, "Full section"),

    # West Africa Settlements - split into two colonies
    ("SIERRA_LEONE", 17107, 17413, "Part of West Africa Settlements"),
    ("THE_GAMBIA", 17414, 17554, "Part of West Africa Settlements (spelled GAMBLIA in OCR)"),

    ("WESTERN_AUSTRALIA", 17556, 18055, "Full section"),

    # Windward Islands - consolidated section
    ("THE_WINDWARD_ISLANDS", 18057, 19347, "Full consolidated section"),

    # Windward Islands subsections (extracted separately like in 1879)
    ("BARBADOS_WINDWARD", 18060, 18494, "Barbados within Windward Islands"),
    ("ST_VINCENT", 18495, 18722, "St. Vincent within Windward Islands"),
    ("GRENADA_WINDWARD", 18723, 18967, "Grenada within Windward Islands"),
    ("TOBAGO_WINDWARD", 18968, 19191, "Tobago within Windward Islands"),
    ("ST_LUCIA", 19192, 19347, "St. Lucia within Windward Islands"),
]


def read_file_lines(filepath):
    """Read file and return list of lines."""
    with open(filepath, 'r', encoding='utf-8') as f:
        return f.readlines()


def remove_line_numbers(line):
    """Remove line number prefix from a line (e.g., '  1234→')."""
    # Pattern matches optional spaces, digits, and arrow
    pattern = r'^\s*\d+→'
    return re.sub(pattern, '', line)


def extract_colony(lines, start_line, end_line, colony_name):
    """Extract colony text from lines, removing line numbers."""
    # Adjust for 0-based indexing
    start_idx = start_line - 1
    end_idx = end_line

    colony_lines = lines[start_idx:end_idx]
    cleaned_lines = [remove_line_numbers(line) for line in colony_lines]

    return ''.join(cleaned_lines)


def sanitize_filename(name):
    """Create safe filename from colony name."""
    # Replace spaces and underscores, remove special characters
    safe_name = re.sub(r'[^a-zA-Z0-9_-]', '_', name)
    safe_name = re.sub(r'_+', '_', safe_name)  # Remove multiple underscores
    return safe_name.strip('_').lower()


def main():
    """Main extraction process."""
    print(f"Reading OCR file: {INPUT_FILE}")
    lines = read_file_lines(INPUT_FILE)
    total_lines = len(lines)
    print(f"Total lines in file: {total_lines}")

    # Create output directory
    Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    print(f"Output directory: {OUTPUT_DIR}")

    # Extract each colony
    metadata = {
        "extraction_date": datetime.now().isoformat(),
        "source_file": INPUT_FILE,
        "total_source_lines": total_lines,
        "colonies_extracted": len(COLONIES),
        "year": 1880,
        "methodology": "Manual boundary identification following 1879 approach",
        "colonies": []
    }

    successful = 0
    failed = []

    for colony_name, start_line, end_line, notes in COLONIES:
        try:
            print(f"\nExtracting: {colony_name} (lines {start_line}-{end_line})")

            # Extract colony text
            colony_text = extract_colony(lines, start_line, end_line, colony_name)

            # Create filename
            filename = f"{sanitize_filename(colony_name)}.txt"
            filepath = os.path.join(OUTPUT_DIR, filename)

            # Write to file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(colony_text)

            # Calculate statistics
            line_count = end_line - start_line + 1
            char_count = len(colony_text)
            word_count = len(colony_text.split())

            # Add to metadata
            colony_metadata = {
                "name": colony_name,
                "filename": filename,
                "start_line": start_line,
                "end_line": end_line,
                "line_count": line_count,
                "character_count": char_count,
                "word_count": word_count,
                "notes": notes
            }
            metadata["colonies"].append(colony_metadata)

            successful += 1
            print(f"  Saved to {filename} ({line_count} lines, {word_count} words)")

        except Exception as e:
            print(f"  Error extracting {colony_name}: {e}")
            failed.append((colony_name, str(e)))

    # Save metadata
    print(f"\nSaving metadata to: {METADATA_FILE}")
    with open(METADATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)

    # Generate report
    print(f"Generating report: {REPORT_FILE}")
    generate_report(metadata, successful, failed)

    print(f"\n{'='*70}")
    print(f"EXTRACTION COMPLETE")
    print(f"{'='*70}")
    print(f"Successfully extracted: {successful}/{len(COLONIES)} colonies")
    if failed:
        print(f"Failed: {len(failed)}")
        for name, error in failed:
            print(f"  - {name}: {error}")
    print(f"\nOutput directory: {OUTPUT_DIR}")
    print(f"Metadata file: {METADATA_FILE}")
    print(f"Report file: {REPORT_FILE}")


def generate_report(metadata, successful, failed):
    """Generate parsing report."""
    report = []
    report.append("# 1880 Colonial Office List - Parsing Report")
    report.append("")
    report.append(f"**Extraction Date:** {metadata['extraction_date']}")
    report.append(f"**Source File:** {metadata['source_file']}")
    report.append(f"**Method:** Manual boundary identification (following 1879 methodology)")
    report.append("")
    report.append("## Summary")
    report.append("")
    report.append(f"- **Total Sections Extracted:** {successful}")
    report.append(f"- **Total Source Lines:** {metadata['total_source_lines']:,}")
    report.append(f"- **Failed Extractions:** {len(failed)}")
    report.append("")

    # Count by type
    references = [c for c in metadata['colonies'] if 'Reference' in c['notes'] or '_REF' in c['name']]
    full_sections = [c for c in metadata['colonies'] if 'Full' in c['notes'] or 'Part of' in c['notes']]
    subsections = [c for c in metadata['colonies'] if 'within' in c['notes']]

    report.append("## Extraction Breakdown")
    report.append("")
    report.append(f"- **Reference Sections:** {len(references)} (cross-references to other sections)")
    report.append(f"- **Full Colony Sections:** {len(full_sections)}")
    report.append(f"- **Subsections (Windward Islands):** {len(subsections)}")
    report.append("")

    if failed:
        report.append("## Failed Extractions")
        report.append("")
        for name, error in failed:
            report.append(f"- **{name}**: {error}")
        report.append("")

    report.append("## All Extracted Sections")
    report.append("")
    report.append("| Section Name | Lines | Start | End | Words | Notes |")
    report.append("|--------------|-------|-------|-----|-------|-------|")

    for colony in sorted(metadata['colonies'], key=lambda x: x['start_line']):
        report.append(
            f"| {colony['name']} | {colony['line_count']} | "
            f"{colony['start_line']} | {colony['end_line']} | "
            f"{colony['word_count']:,} | {colony['notes']} |"
        )

    report.append("")
    report.append("## Statistics by Section Size")
    report.append("")

    # Sort by word count
    by_size = sorted(metadata['colonies'], key=lambda x: x['word_count'], reverse=True)
    report.append("### Top 10 Largest Sections (by word count)")
    report.append("")
    for i, colony in enumerate(by_size[:10], 1):
        report.append(f"{i}. **{colony['name']}**: {colony['word_count']:,} words ({colony['line_count']} lines)")

    report.append("")
    report.append("### Top 10 Smallest Sections (by word count)")
    report.append("")
    for i, colony in enumerate(by_size[-10:][::-1], 1):
        report.append(f"{i}. **{colony['name']}**: {colony['word_count']:,} words ({colony['line_count']} lines)")

    report.append("")
    report.append("## Key Notes for 1880")
    report.append("")
    report.append("### Structural Changes from 1879")
    report.append("")
    report.append("1. **FIJI Returns**: FIJI reappears in 1880 after being absent in 1879")
    report.append("2. **Lagos Integration**: Lagos is now a subsection within THE GOLD COAST COLONY (line 6954), not a separate colony as in 1879. This follows the 1874 charter that merged Lagos with Gold Coast.")
    report.append("3. **The Transvaal**: New addition - annexed by Britain in 1877")
    report.append("4. **Malta**: Appears with no formal header (content starts directly)")
    report.append("5. **Queensland**: Also has no formal header")
    report.append("")
    report.append("### West Africa Settlements")
    report.append("")
    report.append("- Split into SIERRA LEONE and THE GAMBIA (per 1874 charter)")
    report.append("- THE GAMBIA has OCR error: spelled 'GAMBLIA' in original")
    report.append("- Gold Coast and Lagos were separated from West Africa Settlements in 1874")
    report.append("")
    report.append("### Windward Islands Structure")
    report.append("")
    report.append("The Windward Islands section is consolidated but contains:")
    report.append("- BARBADOS (starting line 18060)")
    report.append("- ST. VINCENT (starting line 18495)")
    report.append("- GRENADA (starting line 18723)")
    report.append("- TOBAGO (starting line 18968)")
    report.append("- ST. LUCIA (starting line 19192)")
    report.append("")
    report.append("Each island has been extracted both as part of the consolidated section AND individually.")
    report.append("")
    report.append("### Comparison with 1879")
    report.append("")
    report.append("- **1879**: 49 sections extracted")
    report.append("- **1880**: {} sections extracted".format(len(metadata['colonies'])))
    report.append("")
    report.append("Main differences:")
    report.append("- Lagos merged into Gold Coast Colony (1874 charter)")
    report.append("- Transvaal added (annexed 1877)")
    report.append("- FIJI returns after absence in 1879")
    report.append("- Similar structure with references and subsections")
    report.append("")
    report.append("## Cross-Reference Sections")
    report.append("")
    report.append("The following are short reference sections pointing to consolidated sections:")
    report.append("")
    for colony in references:
        report.append(f"- **{colony['name']}** (lines {colony['start_line']}-{colony['end_line']}): {colony['notes']}")
    report.append("")
    report.append("## Technical Notes")
    report.append("")
    report.append("- All colony boundaries were manually identified by reading the OCR results")
    report.append("- Line number prefixes (e.g., '1234→') have been removed from extracted text")
    report.append("- OCR errors preserved in extracted text (e.g., 'GAMBLIA' for 'GAMBIA')")
    report.append("- Extraction follows the same methodology as 1879 for consistency")

    # Write report
    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))


if __name__ == "__main__":
    main()
