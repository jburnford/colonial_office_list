#!/usr/bin/env python3
"""
Extract colonies from the 1946 Colonial Office List.
Uses manually identified boundaries to extract each colony section.
"""

import json
import os
import re
from pathlib import Path

# Paths
OCR_FILE = "/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1946/olmocr_results.md"
COLONIES_FILE = "/home/user/colonial_office_list/output_3/1946_colonies_found.txt"
OUTPUT_DIR = "/home/user/colonial_office_list/output_3/1946_manual_parsed"
METADATA_FILE = "/home/user/colonial_office_list/output_3/1946_manual_parsed.json"

def remove_line_numbers(text):
    """Remove line number prefixes from OCR text."""
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        # Remove line numbers in format: "   123→"
        match = re.match(r'^\s*\d+→(.*)$', line)
        if match:
            cleaned_lines.append(match.group(1))
        else:
            cleaned_lines.append(line)
    return '\n'.join(cleaned_lines)

def extract_colonies():
    """Extract all colonies to individual files."""
    
    # Create output directory
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Load colony boundaries
    with open(COLONIES_FILE, 'r') as f:
        colonies = json.load(f)
    
    # Read OCR file
    print(f"Reading OCR file: {OCR_FILE}")
    with open(OCR_FILE, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    print(f"Total lines in file: {len(lines)}")
    print(f"\nExtracting {len(colonies)} colonies...\n")
    
    metadata = {
        "year": 1946,
        "source_file": OCR_FILE,
        "extraction_date": "2025-11-19",
        "total_colonies": len(colonies),
        "colonies": []
    }
    
    for i, colony in enumerate(colonies, 1):
        name = colony['name']
        start = colony['start_line'] - 1  # Convert to 0-indexed
        end = colony['end_line']  # End is inclusive, so we don't subtract 1
        
        # Extract colony text
        colony_lines = lines[start:end]
        colony_text = ''.join(colony_lines)
        
        # Remove line numbers
        cleaned_text = remove_line_numbers(colony_text)
        
        # Create safe filename
        safe_name = name.lower().replace(' ', '_').replace('.', '')
        filename = f"{safe_name}.txt"
        filepath = os.path.join(OUTPUT_DIR, filename)
        
        # Write to file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(cleaned_text)
        
        # Calculate statistics
        line_count = end - start
        char_count = len(cleaned_text)
        word_count = len(cleaned_text.split())
        
        colony_metadata = {
            "name": name,
            "filename": filename,
            "start_line": colony['start_line'],
            "end_line": colony['end_line'],
            "line_count": line_count,
            "character_count": char_count,
            "word_count": word_count
        }
        
        metadata["colonies"].append(colony_metadata)
        
        print(f"{i:2d}. {name:30s} -> {filename:40s} ({line_count:4d} lines, {word_count:5d} words)")
    
    # Save metadata
    with open(METADATA_FILE, 'w') as f:
        json.dump(metadata, f, indent=2)
    
    print(f"\n{'='*80}")
    print(f"Extraction complete!")
    print(f"{'='*80}")
    print(f"Output directory: {OUTPUT_DIR}")
    print(f"Metadata file: {METADATA_FILE}")
    print(f"Total colonies extracted: {len(colonies)}")

if __name__ == "__main__":
    extract_colonies()
