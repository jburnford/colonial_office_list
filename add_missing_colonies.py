#!/usr/bin/env python3
"""
Add missing colonies that were filtered out by the initial script.
"""

import json
import re
from pathlib import Path

BASE_DIR = Path("/home/user/colonial_office_list")
OCR_DIR = BASE_DIR / "historical_document_pipeline/processed_pdfs"
OUTPUT_DIR = BASE_DIR / "output"


def find_colony_by_name(year, colony_name):
    """Find a colony section by exact name match."""
    ocr_file = OCR_DIR / f"colonial-office-list-{year}" / "olmocr_results.md"

    with open(ocr_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Find exact match
    pattern = f"^{re.escape(colony_name)}\\.$"

    for i, line in enumerate(lines, 1):
        if re.match(pattern, line.strip()):
            print(f"Found '{colony_name}' at line {i}")
            return i

    print(f"WARNING: '{colony_name}' not found")
    return None


def add_colony_manually(year, colony_name, start_line, end_colony_name=None):
    """Manually add a colony by extracting its content."""
    ocr_file = OCR_DIR / f"colonial-office-list-{year}" / "olmocr_results.md"
    metadata_path = OUTPUT_DIR / f"{year}_manual_parsed.json"

    with open(ocr_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Find end line (either specified colony or appendix)
    end_line = len(lines)

    if end_colony_name:
        end_line_num = find_colony_by_name(year, end_colony_name)
        if end_line_num:
            end_line = end_line_num - 1
    else:
        # Find appendix
        for i in range(start_line, len(lines)):
            if "APPENDIX" in lines[i] or "LIST OF THE BRITISH COLONIES" in lines[i]:
                end_line = i
                break

    # Extract content
    content = ''.join(lines[start_line - 1:end_line])
    line_count = end_line - start_line + 1

    # Create filename
    filename = colony_name.replace(" ", "_").replace("'", "").replace(",", "").replace("(", "").replace(")", "") + ".md"

    # Save file
    output_dir = OUTPUT_DIR / f"{year}_manual_parsed"
    file_path = output_dir / filename

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

    print(f"Saved {colony_name} to {filename} ({line_count} lines)")

    # Update metadata
    with open(metadata_path, 'r') as f:
        metadata = json.load(f)

    colony_info = {
        "name": colony_name,
        "filename": filename,
        "start_line": start_line,
        "end_line": end_line,
        "line_count": line_count,
        "is_appendix": False
    }

    # Insert in correct position (by start_line)
    inserted = False
    for i, existing in enumerate(metadata['colonies']):
        if existing['start_line'] > start_line:
            metadata['colonies'].insert(i, colony_info)
            inserted = True
            break

    if not inserted:
        metadata['colonies'].append(colony_info)

    metadata['total_colonies'] = len(metadata['colonies'])

    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)

    print(f"Updated metadata - total colonies: {metadata['total_colonies']}")


def main():
    """Main function to add missing colonies."""
    print("="*60)
    print("Adding Missing Colonies")
    print("="*60)

    # 1890 - Add BAHAMAS (line 1531, before BARBADOS at 1886)
    print("\n1890 - Adding BAHAMAS")
    add_colony_manually(1890, "BAHAMAS", 1531, "BARBADOS")

    # 1889 - Add colonies that might be missing
    # Check if we need to add any

    # 1888 - Check if we need any additions
    # Most seem ok

    # Let me also add other possibly missing ones
    # For 1890, let's check for missing Australian colonies

    print("\n" + "="*60)
    print("Checking for other missing colonies...")
    print("="*60)

    # Check for MALTA in 1888
    malta_line = find_colony_by_name(1888, "MALTA")
    if malta_line:
        print("\n1888 - Adding MALTA")
        add_colony_manually(1888, "MALTA", malta_line, "MAURITIUS")

    # Check for CYPRUS in 1888
    cyprus_line = find_colony_by_name(1888, "CYPRUS")
    if cyprus_line:
        print("\n1888 - Adding CYPRUS")
        add_colony_manually(1888, "CYPRUS", cyprus_line)

    # Check for ST HELENA in 1888
    st_helena_line = find_colony_by_name(1888, "ST. HELENA")
    if st_helena_line:
        print("\n1888 - Adding ST. HELENA")
        add_colony_manually(1888, "ST. HELENA", st_helena_line)

    # Check for NATAL
    for year in [1888, 1889, 1890]:
        natal_line = find_colony_by_name(year, "NATAL")
        if natal_line:
            metadata_path = OUTPUT_DIR / f"{year}_manual_parsed.json"
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)

            # Check if NATAL already exists
            has_natal = any(c['name'] == 'NATAL' for c in metadata['colonies'])
            if not has_natal:
                print(f"\n{year} - Adding NATAL")
                # Find next colony
                next_colony = None
                for c in metadata['colonies']:
                    if c['start_line'] > natal_line:
                        next_colony = c['name']
                        break
                add_colony_manually(year, "NATAL", natal_line, next_colony)

    # Check for SOUTH AUSTRALIA in 1888
    sa_line = find_colony_by_name(1888, "SOUTH AUSTRALIA")
    if sa_line:
        metadata_path = OUTPUT_DIR / f"1888_manual_parsed.json"
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        has_sa = any(c['name'] == 'SOUTH AUSTRALIA' for c in metadata['colonies'])
        if not has_sa:
            print("\n1888 - Adding SOUTH AUSTRALIA")
            add_colony_manually(1888, "SOUTH AUSTRALIA", sa_line, "THE WINDWARD ISLANDS")

    # Check for missing Australian colonies in 1889
    for colony_name in ["NEW SOUTH WALES", "VICTORIA", "TASMANIA"]:
        line_num = find_colony_by_name(1889, colony_name)
        if line_num:
            metadata_path = OUTPUT_DIR / f"1889_manual_parsed.json"
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            has_colony = any(c['name'] == colony_name for c in metadata['colonies'])
            if not has_colony:
                print(f"\n1889 - Adding {colony_name}")
                next_colony = None
                for c in metadata['colonies']:
                    if c['start_line'] > line_num:
                        next_colony = c['name']
                        break
                if next_colony:
                    add_colony_manually(1889, colony_name, line_num, next_colony)

    # Check for STRAITS SETTLEMENTS in 1889 and 1890
    for year in [1889, 1890]:
        ss_line = find_colony_by_name(year, "STRAITS SETTLEMENTS")
        if ss_line:
            metadata_path = OUTPUT_DIR / f"{year}_manual_parsed.json"
            with open(metadata_path, 'r') as f:
                metadata = json.load(f)
            has_ss = any(c['name'] == 'STRAITS SETTLEMENTS' for c in metadata['colonies'])
            if not has_ss:
                print(f"\n{year} - Adding STRAITS SETTLEMENTS")
                next_colony = None
                for c in metadata['colonies']:
                    if c['start_line'] > ss_line:
                        next_colony = c['name']
                        break
                if next_colony:
                    add_colony_manually(year, "STRAITS SETTLEMENTS", ss_line, next_colony)

    # Check for TASMANIA in 1890
    tas_line = find_colony_by_name(1890, "TASMANIA")
    if tas_line:
        metadata_path = OUTPUT_DIR / f"1890_manual_parsed.json"
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        has_tas = any(c['name'] == 'TASMANIA' for c in metadata['colonies'])
        if not has_tas:
            print("\n1890 - Adding TASMANIA")
            next_colony = None
            for c in metadata['colonies']:
                if c['start_line'] > tas_line:
                    next_colony = c['name']
                    break
            if next_colony:
                add_colony_manually(1890, "TASMANIA", tas_line, next_colony)

    # Check for FIJI in 1890
    fiji_line = find_colony_by_name(1890, "FIJI")
    if fiji_line:
        metadata_path = OUTPUT_DIR / f"1890_manual_parsed.json"
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        has_fiji = any(c['name'] == 'FIJI' for c in metadata['colonies'])
        if not has_fiji:
            print("\n1890 - Adding FIJI")
            next_colony = None
            for c in metadata['colonies']:
                if c['start_line'] > fiji_line:
                    next_colony = c['name']
                    break
            if next_colony:
                add_colony_manually(1890, "FIJI", fiji_line, next_colony)

    print("\n" + "="*60)
    print("DONE")
    print("="*60)


if __name__ == "__main__":
    main()
