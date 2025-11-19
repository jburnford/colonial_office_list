#!/usr/bin/env python3
"""
Extract individual colony sections from 1879 Colonial Office List
Using manually identified boundaries
"""

import os
import re
import json
from datetime import datetime
from pathlib import Path

# Define input/output paths
INPUT_FILE = "/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1879/olmocr_results.md"
OUTPUT_DIR = "/home/user/colonial_office_list/output_3/1879_manual_parsed"
METADATA_FILE = "/home/user/colonial_office_list/output_3/1879_manual_parsed.json"
REPORT_FILE = "/home/user/colonial_office_list/output_3/1879_PARSING_REPORT.md"

# Manually identified colony boundaries
# Format: (colony_name, start_line, end_line, notes)
COLONIES = [
    ("ANTIGUA", 1394, 1396, "Reference to Leeward Islands"),
    ("ANGUILLA", 1397, 1399, "Reference to Leeward Islands"),
    ("BAHAMAS", 1400, 1636, "Full section"),
    ("BARBADOS", 1637, 1642, "Reference to Windward Islands"),
    ("BERMUDAS", 1643, 1887, "Full section"),
    ("BRITISH_GUIANA", 1888, 2531, "Full section"),
    ("BRITISH_HONDURAS", 2532, 2740, "Full section"),
    ("DOMINION_OF_CANADA", 2741, 4854, "Full section including provinces"),
    ("CAPE_OF_GOOD_HOPE", 4855, 6263, "Full section"),
    ("CEYLON", 6264, 6863, "Full section"),
    ("DOMINICA", 6864, 6867, "Reference to Leeward Islands"),
    ("FALKLAND_ISLANDS", 6868, 6964, "Full section"),
    ("FIJI", 6965, 7072, "Embedded section without header"),
    ("GIBRALTAR", 7073, 7152, "Full section"),
    ("GOLD_COAST_COLONY", 7153, 7228, "Full section"),
    ("LAGOS", 7229, 7695, "Full section"),
    ("GRENADA", 7696, 7699, "Reference to Windward Islands"),
    ("GRIQUALAND_WEST", 7700, 7928, "Full section"),
    ("HELIGOLAND", 7929, 7971, "Full section without standard header"),
    ("HONG_KONG", 7972, 8125, "Full section (actual start at 7972)"),
    ("JAMAICA", 8259, 8863, "Full section"),
    ("LABUAN", 8864, 8976, "Full section"),
    ("LEEWARD_ISLANDS", 8977, 10573, "Full section including sub-islands"),
    ("MAURITIUS", 10574, 11356, "Full section"),
    ("MONTSERRAT", 11357, 11360, "Reference to Leeward Islands"),
    ("NATAL", 11361, 11804, "Full section"),
    ("NEVIS", 11805, 11807, "Reference to Leeward Islands"),
    ("NEWFOUNDLAND", 11808, 12364, "Full section"),
    ("NEW_SOUTH_WALES", 12365, 12942, "Full section"),
    ("NEW_ZEALAND", 12943, 13514, "Full section"),
    ("QUEENSLAND", 13515, 13898, "Full section"),
    ("ST_HELENA", 13899, 14007, "Full section"),
    ("SOUTH_AUSTRALIA", 14008, 15004, "Full section"),
    ("STRAITS_SETTLEMENTS", 15005, 15472, "Full section"),
    ("TASMANIA", 15473, 15794, "Full section"),
    ("TOBAGO", 15795, 15798, "Reference to Windward Islands"),
    ("TRANSVAAL", 15799, 15991, "Full section"),
    ("TRINIDAD", 15992, 16685, "Full section"),
    ("TURKS_AND_CAICOS_ISLANDS", 16686, 16775, "Full section"),
    ("VICTORIA", 16776, 17345, "Full section"),
    ("WEST_AFRICA", 17346, 17424, "Section header/intro"),
    ("SIERRA_LEONE", 17425, 17670, "Full section"),
    ("GAMBIA", 17671, 17827, "Full section (spelled GAMBLIA in original)"),
    ("WESTERN_AUSTRALIA", 17828, 18287, "Full section"),
    ("WINDWARD_ISLANDS", 18288, 18754, "Section header/intro"),
    ("ST_VINCENT", 18755, 18956, "Under Windward Islands"),
    ("GRENADA_WINDWARD", 18957, 19185, "Grenada under Windward Islands"),
    ("TOBAGO_WINDWARD", 19186, 19397, "Tobago under Windward Islands"),
    ("ST_LUCIA", 19398, 19549, "Under Windward Islands"),
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
            print(f"  ✓ Saved to {filename} ({line_count} lines, {word_count} words)")

        except Exception as e:
            print(f"  ✗ Error extracting {colony_name}: {e}")
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
    report.append("# 1879 Colonial Office List - Parsing Report")
    report.append("")
    report.append(f"**Extraction Date:** {metadata['extraction_date']}")
    report.append(f"**Source File:** {metadata['source_file']}")
    report.append(f"**Method:** Manual boundary identification")
    report.append("")
    report.append("## Summary")
    report.append("")
    report.append(f"- **Total Colonies Extracted:** {successful}")
    report.append(f"- **Total Source Lines:** {metadata['total_source_lines']:,}")
    report.append(f"- **Failed Extractions:** {len(failed)}")
    report.append("")

    if failed:
        report.append("## Failed Extractions")
        report.append("")
        for name, error in failed:
            report.append(f"- **{name}**: {error}")
        report.append("")

    report.append("## Extracted Colonies")
    report.append("")
    report.append("| Colony Name | Lines | Start | End | Words | Notes |")
    report.append("|-------------|-------|-------|-----|-------|-------|")

    for colony in sorted(metadata['colonies'], key=lambda x: x['start_line']):
        report.append(
            f"| {colony['name']} | {colony['line_count']} | "
            f"{colony['start_line']} | {colony['end_line']} | "
            f"{colony['word_count']:,} | {colony['notes']} |"
        )

    report.append("")
    report.append("## Statistics by Colony Size")
    report.append("")

    # Sort by word count
    by_size = sorted(metadata['colonies'], key=lambda x: x['word_count'], reverse=True)
    report.append("### Top 10 Largest Colonies (by word count)")
    report.append("")
    for i, colony in enumerate(by_size[:10], 1):
        report.append(f"{i}. **{colony['name']}**: {colony['word_count']:,} words ({colony['line_count']} lines)")

    report.append("")
    report.append("### Top 10 Smallest Colonies (by word count)")
    report.append("")
    for i, colony in enumerate(by_size[-10:][::-1], 1):
        report.append(f"{i}. **{colony['name']}**: {colony['word_count']:,} words ({colony['line_count']} lines)")

    report.append("")
    report.append("## Notes")
    report.append("")
    report.append("- All colony boundaries were manually identified by reading the OCR results")
    report.append("- Line number prefixes (e.g., '1234→') have been removed from extracted text")
    report.append("- Some colonies are references to other sections (e.g., ANTIGUA → Leeward Islands)")
    report.append("- FIJI section has no formal header (embedded in document)")
    report.append("- GAMBIA spelled as 'GAMBLIA' in original (OCR error)")
    report.append("- Some colonies appear multiple times (main section + subsections)")
    report.append("")
    report.append("## Cross-Reference Notes")
    report.append("")
    report.append("Colonies with cross-references to other sections:")
    report.append("")
    for colony in metadata['colonies']:
        if "Reference to" in colony['notes'] or "Under" in colony['notes']:
            report.append(f"- **{colony['name']}**: {colony['notes']}")

    # Write report
    with open(REPORT_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))


if __name__ == "__main__":
    main()
