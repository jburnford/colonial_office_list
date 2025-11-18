#!/usr/bin/env python3
"""
Extract all colonies from 1900 Colonial Office List based on manually-verified boundaries
"""

import json
import os
from pathlib import Path
from final_colonies_1900 import get_final_colony_boundaries
import re

def clean_colony_name(name):
    """Convert colony name to valid filename"""
    # Remove "THE " prefix
    name = re.sub(r'^THE\s+', '', name)
    # Replace spaces and special characters with underscores
    name = re.sub(r'[^A-Z0-9]+', '_', name)
    # Remove leading/trailing underscores
    name = name.strip('_')
    return name

def extract_colonies(source_file, output_dir):
    """Extract all colonies and save to individual files"""

    # Create output directory
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    # Get colony boundaries
    colonies = get_final_colony_boundaries()

    # Read source file
    print(f"Reading source file: {source_file}")
    with open(source_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Extract each colony
    extracted = []
    print(f"\nExtracting {len(colonies)} colonies...")

    for start_line, end_line, colony_name, notes in colonies:
        # Extract lines (convert to 0-indexed)
        colony_lines = lines[start_line-1:end_line]

        # Join into content
        content = ''.join(colony_lines)

        # Clean up line number prefixes (format: "3171→")
        content = re.sub(r'^\s*\d+→', '', content, flags=re.MULTILINE)

        # Create filename
        filename = clean_colony_name(colony_name) + '.txt'
        filepath = output_path / filename

        # Save to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)

        # Record metadata
        extracted.append({
            'colony_name': colony_name,
            'clean_name': clean_colony_name(colony_name),
            'filename': filename,
            'start_line': start_line,
            'end_line': end_line,
            'line_count': end_line - start_line + 1,
            'notes': notes
        })

        print(f"  ✓ {colony_name:35s} → {filename:35s} ({end_line - start_line + 1:5d} lines)")

    return extracted

def save_metadata(extracted, output_file):
    """Save extraction metadata as JSON"""
    metadata = {
        'year': 1900,
        'source_file': 'historical_document_pipeline/processed_pdfs/colonial-office-list-1900/olmocr_results.md',
        'extraction_method': 'manual_verification',
        'total_colonies': len(extracted),
        'colonies': extracted
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(metadata, f, indent=2)

    print(f"\n✓ Metadata saved to: {output_file}")

if __name__ == '__main__':
    # Paths
    source_file = '/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1900/olmocr_results.md'
    output_dir = '/home/user/colonial_office_list/output_3/1900_manual_parsed'
    metadata_file = '/home/user/colonial_office_list/output_3/1900_manual_parsed.json'

    # Extract colonies
    print("="*80)
    print("EXTRACTING COLONIES FROM 1900 COLONIAL OFFICE LIST")
    print("="*80)

    extracted = extract_colonies(source_file, output_dir)

    # Save metadata
    save_metadata(extracted, metadata_file)

    print("\n" + "="*80)
    print(f"EXTRACTION COMPLETE")
    print("="*80)
    print(f"Total colonies extracted: {len(extracted)}")
    print(f"Output directory: {output_dir}")
    print(f"Metadata file: {metadata_file}")
