#!/usr/bin/env python3
"""
Fix missing colonies by adding them based on OCR file analysis.
"""

import json
import re
from pathlib import Path

BASE_DIR = Path("/home/user/colonial_office_list")
OCR_DIR = BASE_DIR / "historical_document_pipeline/processed_pdfs"
OUTPUT_DIR = BASE_DIR / "output"


def find_colony_line(year, colony_name, after_line=1000):
    """Find a colony section by exact name match, after a certain line."""
    ocr_file = OCR_DIR / f"colonial-office-list-{year}" / "olmocr_results.md"

    with open(ocr_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    pattern = f"^{re.escape(colony_name)}\\.$"

    for i, line in enumerate(lines, 1):
        if i > after_line and re.match(pattern, line.strip()):
            print(f"  Found '{colony_name}' at line {i}")
            return i

    print(f"  WARNING: '{colony_name}' not found after line {after_line}")
    return None


def add_colony(year, colony_name, start_line, end_line):
    """Add a colony to the metadata and extract its content."""
    ocr_file = OCR_DIR / f"colonial-office-list-{year}" / "olmocr_results.md"
    metadata_path = OUTPUT_DIR / f"{year}_manual_parsed.json"
    output_dir = OUTPUT_DIR / f"{year}_manual_parsed"

    # Read OCR file
    with open(ocr_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Extract content
    content = ''.join(lines[start_line - 1:end_line])
    line_count = end_line - start_line + 1

    # Create filename
    filename = colony_name.replace(" ", "_").replace("'", "").replace(",", "").replace("(", "").replace(")", "") + ".md"

    # Save file
    file_path = output_dir / filename
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"  Saved {filename} ({line_count} lines: {start_line}-{end_line})")

    # Load metadata
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)

    # Create colony info
    colony_info = {
        "name": colony_name,
        "filename": filename,
        "start_line": start_line,
        "end_line": end_line,
        "line_count": line_count,
        "is_appendix": False
    }

    # Insert in correct position (sorted by start_line)
    inserted = False
    for i, existing in enumerate(metadata['colonies']):
        if existing['start_line'] > start_line:
            metadata['colonies'].insert(i, colony_info)
            inserted = True
            break

    if not inserted:
        metadata['colonies'].append(colony_info)

    # Update total
    metadata['total_colonies'] = len(metadata['colonies'])

    # Save metadata
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)

    print(f"  Updated metadata - total: {metadata['total_colonies']}")


def get_next_colony_line(year, after_line):
    """Get the start line of the next colony after the given line."""
    metadata_path = OUTPUT_DIR / f"{year}_manual_parsed.json"

    with open(metadata_path, 'r') as f:
        metadata = json.load(f)

    for colony in metadata['colonies']:
        if colony['start_line'] > after_line:
            return colony['start_line']

    # If no next colony, return appendix line (search for it)
    ocr_file = OCR_DIR / f"colonial-office-list-{year}" / "olmocr_results.md"
    with open(ocr_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    for i in range(after_line, len(lines)):
        if "APPENDIX" in lines[i] or "LIST OF THE BRITISH COLONIES" in lines[i]:
            return i + 1

    return len(lines)


def main():
    """Main function."""
    print("="*60)
    print("Fixing Missing Colonies")
    print("="*60)

    # 1890 - Fix BAHAMAS (should be 1531 to 1885, just before BARBADOS at 1886)
    print("\n1890 - Fixing BAHAMAS")
    bahamas_start = find_colony_line(1890, "BAHAMAS", after_line=1000)
    if bahamas_start:
        # Delete the bad entry first
        metadata_path = OUTPUT_DIR / f"1890_manual_parsed.json"
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)

        metadata['colonies'] = [c for c in metadata['colonies'] if c['name'] != 'BAHAMAS']
        metadata['total_colonies'] = len(metadata['colonies'])

        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)

        # Add BAHAMAS correctly
        next_line = get_next_colony_line(1890, bahamas_start)
        add_colony(1890, "BAHAMAS", bahamas_start, next_line - 1)

    # 1888 - Fix SOUTH AUSTRALIA (find correct boundaries)
    print("\n1888 - Fixing SOUTH AUSTRALIA")
    sa_start = find_colony_line(1888, "SOUTH AUSTRALIA", after_line=19000)
    if sa_start:
        # Delete bad entry
        metadata_path = OUTPUT_DIR / f"1888_manual_parsed.json"
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)

        metadata['colonies'] = [c for c in metadata['colonies'] if c['name'] != 'SOUTH AUSTRALIA']
        metadata['total_colonies'] = len(metadata['colonies'])

        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)

        # Add correctly
        next_line = get_next_colony_line(1888, sa_start)
        add_colony(1888, "SOUTH AUSTRALIA", sa_start, next_line - 1)

    # 1888 - Fix ST. HELENA
    print("\n1888 - Fixing ST. HELENA")
    metadata_path = OUTPUT_DIR / f"1888_manual_parsed.json"
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)

    st_helena = [c for c in metadata['colonies'] if c['name'] == 'ST. HELENA']
    if st_helena and st_helena[0]['line_count'] > 1000:
        # Delete and recreate
        metadata['colonies'] = [c for c in metadata['colonies'] if c['name'] != 'ST. HELENA']
        metadata['total_colonies'] = len(metadata['colonies'])

        with open(metadata_path, 'w') as f:
            json.dump(metadata, f, indent=2)

        st_start = find_colony_line(1888, "ST. HELENA", after_line=19000)
        if st_start:
            next_line = get_next_colony_line(1888, st_start)
            add_colony(1888, "ST. HELENA", st_start, next_line - 1)

    # Add missing Australian colonies to 1889
    print("\n1889 - Adding missing Australian colonies")
    for colony_name in ["NEW SOUTH WALES", "TASMANIA", "VICTORIA"]:
        # First check if already exists
        metadata_path = OUTPUT_DIR / f"1889_manual_parsed.json"
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)

        if any(c['name'] == colony_name for c in metadata['colonies']):
            print(f"  {colony_name} already exists, skipping")
            continue

        start_line = find_colony_line(1889, colony_name, after_line=17000)
        if start_line:
            next_line = get_next_colony_line(1889, start_line)
            add_colony(1889, colony_name, start_line, next_line - 1)

    # Add missing colonies to 1890
    print("\n1890 - Adding missing colonies")
    for colony_name in ["FIJI", "TASMANIA"]:
        metadata_path = OUTPUT_DIR / f"1890_manual_parsed.json"
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)

        if any(c['name'] == colony_name for c in metadata['colonies']):
            print(f"  {colony_name} already exists, skipping")
            continue

        start_line = find_colony_line(1890, colony_name, after_line=10000)
        if start_line:
            next_line = get_next_colony_line(1890, start_line)
            add_colony(1890, colony_name, start_line, next_line - 1)

    print("\n" + "="*60)
    print("COMPLETE")
    print("="*60)

    # Print final counts
    for year in [1888, 1889, 1890]:
        metadata_path = OUTPUT_DIR / f"{year}_manual_parsed.json"
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        print(f"{year}: {metadata['total_colonies']} colonies")


if __name__ == "__main__":
    main()
