#!/usr/bin/env python3
"""
Batch process Colonial Office Lists for 1888, 1889, and 1890.
Extracts all colony sections and creates output files.
"""

import re
import json
import os
from pathlib import Path

# Base paths
BASE_DIR = Path("/home/user/colonial_office_list")
OCR_DIR = BASE_DIR / "historical_document_pipeline/processed_pdfs"
OUTPUT_DIR = BASE_DIR / "output"

# Years to process
YEARS = [1888, 1889, 1890]

# Known colony names from previous years - use this as reference
KNOWN_COLONIES = [
    "BAHAMAS", "BARBADOS", "BASUTOLAND", "BERMUDA", "BRITISH GUIANA",
    "BRITISH HONDURAS", "DOMINION OF CANADA", "CAPE OF GOOD HOPE", "CEYLON",
    "CYPRUS", "FALKLAND ISLANDS", "FIJI", "GAMBIA", "GIBRALTAR", "GOLD COAST",
    "GRENADA", "HONG KONG", "JAMAICA", "LABUAN", "LAGOS", "LEEWARD ISLANDS",
    "MALTA", "MAURITIUS", "NATAL", "NEW SOUTH WALES", "NEW ZEALAND",
    "NEWFOUNDLAND", "QUEENSLAND", "ST. HELENA", "SIERRA LEONE",
    "SOUTH AUSTRALIA", "STRAITS SETTLEMENTS", "TASMANIA", "TRINIDAD",
    "TURKS AND CAICOS ISLANDS", "VICTORIA", "WEST AFRICA SETTLEMENTS",
    "WESTERN AUSTRALIA", "WINDWARD ISLANDS", "ZULULAND", "BRITISH BECHUANALAND",
    "BRITISH NORTH BORNEO", "ASCENSION", "NIGER", "PROTECTED MALAY STATES",
    "NEW GUINEA"
]

# Appendix markers to stop extraction
APPENDIX_MARKERS = [
    "APPENDIX",
    "LIST OF THE BRITISH COLONIES",
    "MODES AND DATES OF ACQUISITION",
    "CLASSIFICATION OF COLONIES",
    "AGREEMENT made this day",
    "CROWN AGENTS FOR THE COLONIES"
]


def read_file_lines(file_path):
    """Read file and return list of lines."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return f.readlines()


def is_colony_header(line, line_num):
    """
    Check if a line is a colony header.
    Colony headers are:
    - ALL CAPS (with possible spaces, &, ', -, parentheses)
    - End with a period
    - After line 1000 (skip front matter)
    - Match known colony patterns
    """
    if line_num < 1000:
        return False

    stripped = line.strip()

    # Must end with period
    if not stripped.endswith('.'):
        return False

    # Remove the period
    name = stripped[:-1]

    # Must be all uppercase (allowing spaces, &, ', -, parentheses)
    if not re.match(r'^[A-Z][A-Z\s&,\'()\-]+$', name):
        return False

    # Length check - colony names are typically 3-50 chars
    if len(name) < 3 or len(name) > 50:
        return False

    # Must not be a common section header
    excluded = [
        "FINANCES", "IMPORTS", "EXPORTS", "FREE GOODS", "SHIPPING ENTERED AND CLEARED",
        "EXECUTIVE COUNCIL", "LEGISLATIVE COUNCIL", "LEGISLATIVE ASSEMBLY",
        "HOUSE OF ASSEMBLY", "TREASURY BOARD", "SUPREME COURT", "ECCLESIASTICAL",
        "CHURCH OF ENGLAND", "ROMAN CATHOLIC CHURCH", "PRESBYTERIAN CHURCH",
        "METHODIST CHURCH", "CONSULS IN THE DOMINION", "SEAT OF GOVERNMENT",
        "JUDICIAL ESTABLISHMENT", "LOCAL DEPARTMENTS", "DOMINION OFFICIALS",
        "OFFICERS OF DEPARTMENTS", "JUDICIAL AND LEGAL DEPARTMENTS",
        "FINANCE DEPARTMENT", "AUDIT OFFICE", "DEPARTMENT OF PUBLIC WORKS",
        "INLAND REVENUE DEPARTMENT", "CUSTOMS DEPARTMENT", "RAILWAYS AND CANALS",
        "POST OFFICE DEPARTMENT", "DEPARTMENT OF JUSTICE", "MOUNTED POLICE OFFICE",
        "BUREAU OF AGRICULTURE AND STATISTICS", "DEPARTMENT OF MARINE",
        "DEPARTMENT OF MILITIA AND DEFENCE", "DEPARTMENT OF FISHERIES",
        "HIGH COMMISSIONER IN LONDON", "ATTORNEY-GENERAL'S DEPARTMENT",
        "PROVINCIAL SECRETARY'S DEPARTMENT", "TREASURER'S DEPARTMENT",
        "DEPARTMENT OF AGRICULTURE AND PUBLIC WORKS", "DEPARTMENT OF EDUCATION",
        "SUPREME COURT OF JUDICATURE", "MARITIME COURT", "DIVISION OF",
        "DISTRICT OF", "PROVINCE OF", "PREFACE", "CONTENTS", "THE COLONIAL OFFICE",
        "UNDER-SECRETARIES OF STATE FOR THE COLONIES", "THE ESTABLISHMENT",
        "DISTRIBUTION OF BUSINESS", "WEST INDIAN", "NORTH AMERICAN AND AUSTRALIAN",
        "AFRICAN AND CYPRUS", "EASTERN", "GENERAL", "REGISTRY", "PRINTING BRANCH",
        "LIBRARY", "COPYING BRANCH", "FINANCIAL", "EMIGRATION",
        "THE CROWN AGENTS FOR THE COLONIES", "PROFESSIONAL BRANCH", "EXPORT DUTIES",
        "THE DOMINION", "THE SENATE OF CANADA", "THE COURT OF EXCHEQUER",
        "THE QUEEN'S PRIVY COUNCIL", "THE SUPREME COURT OF CANADA"
    ]

    if any(name.startswith(exc) for exc in excluded):
        return False

    return True


def is_appendix_start(line):
    """Check if line marks the start of appendix/reference material."""
    stripped = line.strip()
    return any(marker in stripped for marker in APPENDIX_MARKERS)


def extract_colonies(year):
    """Extract all colonies from a year's OCR file."""
    ocr_file = OCR_DIR / f"colonial-office-list-{year}" / "olmocr_results.md"

    print(f"\n{'='*60}")
    print(f"Processing {year}")
    print(f"{'='*60}")

    if not ocr_file.exists():
        print(f"ERROR: OCR file not found: {ocr_file}")
        return None

    lines = read_file_lines(ocr_file)
    print(f"Total lines in file: {len(lines)}")

    # Find all colony headers
    colonies = []
    colony_lines = []

    for i, line in enumerate(lines, 1):
        if is_colony_header(line, i):
            colony_name = line.strip()[:-1]  # Remove period
            # Check if this might be a colony (not a subsection)
            # Heuristic: if previous colony is within 100 lines, it's probably a subsection
            if colony_lines and (i - colony_lines[-1]) < 100:
                continue

            colony_lines.append(i)
            print(f"Found colony at line {i}: {colony_name}")

    # Filter to only keep main colony sections
    # Strategy: Look for colonies that are in our known list or follow the pattern
    filtered_colonies = []
    filtered_lines = []

    for i, line_num in enumerate(colony_lines):
        colony_name = lines[line_num - 1].strip()[:-1]

        # Check if appendix has started
        if is_appendix_start(lines[line_num - 1]):
            print(f"Stopping at line {line_num}: Appendix/reference material detected")
            break

        # Include if it's a known colony or matches patterns
        is_known = any(known in colony_name for known in KNOWN_COLONIES)
        is_province = "PROVINCE OF" in colony_name
        is_division = "DIVISION OF" in colony_name

        if is_known and not is_province and not is_division:
            filtered_colonies.append(colony_name)
            filtered_lines.append(line_num)

    print(f"\nFiltered to {len(filtered_colonies)} main colonies")

    # Extract content for each colony
    colony_data = []
    for i, (colony_name, start_line) in enumerate(zip(filtered_colonies, filtered_lines)):
        # Determine end line (start of next colony or appendix)
        if i < len(filtered_lines) - 1:
            end_line = filtered_lines[i + 1] - 1
        else:
            # For last colony, find appendix or end of file
            end_line = len(lines)
            for j in range(start_line, len(lines)):
                if is_appendix_start(lines[j]):
                    end_line = j
                    break

        # Extract content
        content = ''.join(lines[start_line - 1:end_line])
        line_count = end_line - start_line + 1

        # Create filename
        filename = colony_name.replace(" ", "_").replace("'", "").replace(",", "").replace("(", "").replace(")", "") + ".md"

        colony_info = {
            "name": colony_name,
            "filename": filename,
            "start_line": start_line,
            "end_line": end_line,
            "line_count": line_count,
            "content": content,
            "is_appendix": False
        }

        colony_data.append(colony_info)
        print(f"  {colony_name}: lines {start_line}-{end_line} ({line_count} lines)")

    return colony_data


def save_colony_files(year, colonies):
    """Save individual colony files and metadata."""
    if not colonies:
        print(f"No colonies to save for {year}")
        return

    # Create output directory
    output_dir = OUTPUT_DIR / f"{year}_manual_parsed"
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save each colony file
    for colony in colonies:
        file_path = output_dir / colony['filename']
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(colony['content'])

    print(f"\nSaved {len(colonies)} colony files to {output_dir}")

    # Create metadata JSON (without content field)
    metadata = {
        "year": year,
        "total_colonies": len(colonies),
        "parsing_method": "LLM-based manual parsing (batch processing)",
        "historical_context": f"Year {year} - Scramble for Africa peak, pre-Second Boer War",
        "colonies": [
            {k: v for k, v in colony.items() if k != 'content'}
            for colony in colonies
        ]
    }

    metadata_path = OUTPUT_DIR / f"{year}_manual_parsed.json"
    with open(metadata_path, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)

    print(f"Saved metadata to {metadata_path}")


def main():
    """Main batch processing function."""
    print("="*60)
    print("Batch Processing Colonial Office Lists: 1888-1890")
    print("="*60)

    results = {}

    for year in YEARS:
        colonies = extract_colonies(year)
        if colonies:
            save_colony_files(year, colonies)
            results[year] = len(colonies)
        else:
            results[year] = 0

    print("\n" + "="*60)
    print("BATCH PROCESSING COMPLETE")
    print("="*60)
    print("\nColony counts by year:")
    for year, count in results.items():
        print(f"  {year}: {count} colonies")

    return results


if __name__ == "__main__":
    main()
