#!/usr/bin/env python3
"""
Batch process years 1957-1960: run parser, analyze, fix, create metadata.
"""

import json
import subprocess
from pathlib import Path
from datetime import datetime

def process_year(year):
    """Process a single year"""
    print(f"\n{'='*80}")
    print(f"Processing year {year}")
    print(f"{'='*80}\n")

    # Step 1: Run v5 parser
    print(f"[{year}] Step 1: Running v5 parser...")
    input_file = f"historical_document_pipeline/processed_pdfs/colonial-office-list-{year}/olmocr_results.json"
    output_file = f"output/{year}_parsed_v5_final.json"

    cmd = f"python3 colonial_office_parser_v5.py {input_file} -o {output_file}"
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)

    if result.returncode != 0:
        print(f"ERROR: Parser failed for {year}")
        print(result.stderr)
        return None

    # Step 2: Load and analyze
    print(f"[{year}] Step 2: Analyzing parser output...")
    with open(output_file, 'r') as f:
        data = json.load(f)

    total_original = len(data['colonies'])

    # Find PART II boundary (table of contents entries before actual colonies)
    # Heuristic: find the first colony with >100 lines after a series of small (<20 line) entries
    part_ii_start = 0
    for i, colony in enumerate(data['colonies']):
        lines = colony['end_line'] - colony['start_line'] + 1
        if lines > 100:  # First substantial colony section
            part_ii_start = colony['start_line']
            break

    # Step 3: Extract corrected colonies
    print(f"[{year}] Step 3: Extracting corrected colonies...")
    source_file = Path(f'historical_document_pipeline/processed_pdfs/colonial-office-list-{year}/olmocr_results.md')
    output_dir = Path(f'output_2/{year}_manual_parsed')
    output_dir.mkdir(parents=True, exist_ok=True)

    with open(source_file, 'r') as f:
        source_lines = f.readlines()

    kept = 0
    skipped_toc = 0
    for colony in data['colonies']:
        name = colony['colony_name']
        start = colony['start_line']
        end = colony['end_line']

        # Skip table of contents (before PART II or very small entries at start)
        if start < part_ii_start:
            skipped_toc += 1
            continue

        # Extract content
        content_lines = source_lines[start-1:end]
        content = ''.join(content_lines)

        # Create filename
        filename = name.replace(' ', '_').replace(',', '').replace('(', '').replace(')', '').replace("'", '').replace('.', '').replace('-', '_') + '.md'

        # Write file
        output_file_md = output_dir / filename
        with open(output_file_md, 'w') as f:
            f.write(content)

        kept += 1

    # Step 4: Create metadata
    print(f"[{year}] Step 4: Creating metadata...")
    colonies_metadata = []
    for colony in data['colonies']:
        if colony['start_line'] >= part_ii_start:
            colonies_metadata.append({
                'colony_name': colony['colony_name'],
                'year': year,
                'start_line': colony['start_line'],
                'end_line': colony['end_line'],
                'char_count': colony['char_count'],
                'line_count': colony['end_line'] - colony['start_line'] + 1,
                'filename': colony['colony_name'].replace(' ', '_').replace(',', '').replace('(', '').replace(')', '').replace("'", '').replace('.', '').replace('-', '_') + '.md'
            })

    metadata = {
        'year': year,
        'source_file': str(source_file),
        'total_colonies': len(colonies_metadata),
        'colonies': colonies_metadata,
        'processing_notes': {
            'parser': 'Automated v5 parser with table of contents filtering',
            'date': datetime.now().strftime('%Y-%m-%d'),
            'method': 'Automated batch processing with PART II detection',
            'corrections_applied': [
                f'Removed {skipped_toc} table of contents entries (before line {part_ii_start})',
            ],
            'original_count': total_original,
            'corrected_count': len(colonies_metadata),
            'note': 'Automated processing - may need manual verification'
        }
    }

    metadata_file = Path(f'output_2/{year}_manual_parsed.json')
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)

    print(f"[{year}] SUMMARY:")
    print(f"  Original: {total_original} colonies")
    print(f"  Skipped (table of contents): {skipped_toc}")
    print(f"  Final: {len(colonies_metadata)} colonies")
    print(f"  Change: {total_original} → {len(colonies_metadata)}")
    print(f"  Output: {output_dir}/")

    return {
        'year': year,
        'original': total_original,
        'corrected': len(colonies_metadata),
        'skipped_toc': skipped_toc,
        'part_ii_start': part_ii_start
    }

# Process each year
results = []
for year in [1957, 1958, 1959, 1960]:
    result = process_year(year)
    if result:
        results.append(result)

# Print summary table
print(f"\n\n{'='*80}")
print(f"BATCH PROCESSING SUMMARY")
print(f"{'='*80}\n")
print(f"{'Year':<6} | {'Original':<10} | {'Corrected':<10} | {'Change':<12} | {'PART II Start'}")
print(f"{'-'*6}|{'-'*12}|{'-'*12}|{'-'*14}|{'-'*15}")
for r in results:
    print(f"{r['year']:<6} | {r['original']:<10} | {r['corrected']:<10} | {r['original']}→{r['corrected']:<8} | Line {r['part_ii_start']}")
