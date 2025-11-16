#!/usr/bin/env python3
"""
Process Colonial Office List years 1951-1955 using automated LLM-based approach.

For each year:
1. Analyze metadata to find colony boundaries
2. Create extraction script
3. Create metadata file
4. Extract colonies to output_2/{year}_manual_parsed/
"""

import re
import json
from pathlib import Path
from datetime import datetime

def analyze_year(year):
    """Analyze a single year to identify colony boundaries."""
    print(f"\n{'='*70}")
    print(f"Analyzing year {year}")
    print(f"{'='*70}\n")

    # Read the OCR file
    ocr_file = Path(f'historical_document_pipeline/processed_pdfs/colonial-office-list-{year}/olmocr_results.md')

    if not ocr_file.exists():
        print(f"ERROR: OCR file not found: {ocr_file}")
        return None

    with open(ocr_file, 'r') as f:
        lines = f.readlines()

    print(f"Total lines in OCR: {len(lines)}")

    # Find all potential colony headers
    potential_colonies = []

    # Expected colonies (similar to 1950)
    expected_colonies = [
        'ADEN',
        'BAHAMA ISLANDS',
        'BARBADOS',
        'BERMUDA',
        'BRITISH GUIANA',
        'BRITISH HONDURAS',
        'BRUNEI',
        'CEYLON',
        'CYPRUS',
        'FALKLAND ISLANDS',
        'FIJI',
        'GAMBIA',
        'GIBRALTAR',
        'GOLD COAST',
        'HONG KONG',
        'JAMAICA',
        'KENYA',
        'LEEWARD ISLANDS',
        'FEDERATION OF MALAYA',
        'MALTA',
        'MAURITIUS',
        'NIGERIA',
        'NORTH BORNEO',
        'NORTHERN RHODESIA',
        'NYASALAND',
        'ST. HELENA',
        'SARAWAK',
        'SEYCHELLES',
        'SIERRA LEONE',
        'SINGAPORE',
        'SOMALILAND',
        'TANGANYIKA',
        'TRINIDAD',
        'UGANDA',
        'WESTERN PACIFIC',
        'WINDWARD ISLANDS',
        'ZANZIBAR',
    ]

    # Create patterns for each expected colony
    colony_patterns = []
    for colony in expected_colonies:
        # Handle variations
        if colony == 'GAMBIA':
            colony_patterns.append((colony, [r'^(\*\*)?GAMBIA(\*\*)?$', r'^(\*\*)?THE GAMBIA(\*\*)?$']))
        elif colony == 'GOLD COAST':
            colony_patterns.append((colony, [r'^(\*\*)?GOLD COAST(\*\*)?$', r'^(\*\*)?THE GOLD COAST(\*\*)?$']))
        elif colony == 'LEEWARD ISLANDS':
            colony_patterns.append((colony, [r'^(\*\*)?LEEWARD ISLANDS(\*\*)?$', r'^(\*\*)?THE LEEWARD ISLANDS(\*\*)?$']))
        elif colony == 'WINDWARD ISLANDS':
            colony_patterns.append((colony, [r'^(\*\*)?WINDWARD ISLANDS(\*\*)?$', r'^(\*\*)?THE WINDWARD ISLANDS(\*\*)?$']))
        elif colony == 'SINGAPORE':
            colony_patterns.append((colony, [r'^(\*\*)?SINGAPORE.*(\*\*)?$']))
        elif colony == 'WESTERN PACIFIC':
            colony_patterns.append((colony, [r'^(\*\*)?WESTERN PACIFIC.*(\*\*)?$']))
        elif colony == 'FALKLAND ISLANDS':
            colony_patterns.append((colony, [r'^(\*\*)?FALKLAND ISLANDS.*(\*\*)?$']))
        elif colony == 'ST. HELENA':
            colony_patterns.append((colony, [r'^(\*\*)?ST\.? HELENA.*(\*\*)?$']))
        elif colony == 'NYASALAND':
            colony_patterns.append((colony, [r'^(\*\*)?NYASALAND.*(\*\*)?$']))
        elif colony == 'SOMALILAND':
            colony_patterns.append((colony, [r'^(\*\*)?SOMALILAND.*(\*\*)?$']))
        elif colony == 'TRINIDAD':
            colony_patterns.append((colony, [r'^(\*\*)?TRINIDAD.*(\*\*)?$']))
        elif colony == 'CEYLON':
            colony_patterns.append((colony, [r'^(\*\*)?CEYLON(\*\*)?$']))
        else:
            colony_patterns.append((colony, [r'^(\*\*)?' + re.escape(colony) + r'(\*\*)?$']))

    # Scan for colony headers (main colony section, roughly lines 4000-35000)
    for i in range(4000, min(35000, len(lines))):
        line = lines[i].rstrip()

        # Check against colony patterns
        for colony_name, patterns in colony_patterns:
            matched = False
            for pattern in patterns:
                if re.match(pattern, line):
                    matched = True
                    break

            if matched:
                # Check if this is a main colony header
                if i + 10 < len(lines):
                    next_lines = ''.join(lines[i+1:i+11]).upper()
                    if 'SITUATION' in next_lines or 'AREA' in next_lines or \
                       'GENERAL DESCRIPTION' in next_lines or 'CLIMATE' in next_lines or \
                       'HISTORY' in next_lines or 'CONSTITUTION' in next_lines:
                        # Remove ** markdown if present
                        clean_line = line.replace('**', '')
                        potential_colonies.append((i + 1, clean_line, colony_name))  # +1 for 1-indexed
                        break

    print(f"Found {len(potential_colonies)} potential colony sections")

    # Create boundaries list
    if potential_colonies:
        colonies_with_boundaries = []
        sorted_colonies = sorted(potential_colonies)

        for idx, (start_line, line_text, standard_name) in enumerate(sorted_colonies):
            if idx < len(sorted_colonies) - 1:
                end_line = sorted_colonies[idx + 1][0] - 1
            else:
                # Last colony ends around line 32000-35000 (before statistics sections)
                end_line = min(start_line + 3000, len(lines))  # Default max size

        # Try to detect end more precisely
                for check_line in range(start_line + 100, min(start_line + 5000, len(lines))):
                    if check_line < len(lines):
                        check_text = lines[check_line].rstrip()
                        if re.match(r'^##.*Revenue and Expenditure', check_text) or \
                           re.match(r'^##.*INDEX', check_text) or \
                           'ALPHABETICAL LIST' in check_text.upper():
                            end_line = check_line
                            break

            colonies_with_boundaries.append({
                'name': line_text,
                'standard_name': standard_name,
                'start': start_line,
                'end': end_line,
                'lines': end_line - start_line + 1
            })

        return {
            'year': year,
            'ocr_file': str(ocr_file),
            'total_lines': len(lines),
            'colonies': colonies_with_boundaries
        }

    return None


def extract_colonies(year_data):
    """Extract colonies for a given year."""
    year = year_data['year']
    ocr_file = Path(year_data['ocr_file'])
    colonies = year_data['colonies']

    print(f"\nExtracting {len(colonies)} colonies for year {year}...")

    # Output directory
    output_dir = Path(f'output_2/{year}_manual_parsed')
    output_dir.mkdir(parents=True, exist_ok=True)

    # Read source file
    with open(ocr_file, 'r') as f:
        source_lines = f.readlines()

    # Extract each colony
    extracted_count = 0
    for colony in colonies:
        name = colony['name']
        start = colony['start']
        end = colony['end']

        # Extract content (1-indexed in JSON, 0-indexed in Python)
        content_lines = source_lines[start-1:end]
        content = ''.join(content_lines)

        # Create filename (clean up name)
        filename = name.replace(' ', '_').replace(',', '').replace('(', '').replace(')', '').replace("'", '').replace('.', '').replace('**', '') + '.md'

        # Write file
        output_file = output_dir / filename
        with open(output_file, 'w') as f:
            f.write(content)

        extracted_count += 1

    print(f"Extracted {extracted_count} colonies to {output_dir}")
    return output_dir


def create_metadata(year_data, output_dir):
    """Create metadata file for a given year."""
    year = year_data['year']
    ocr_file = Path(year_data['ocr_file'])
    colonies = year_data['colonies']

    print(f"\nCreating metadata for year {year}...")

    # Read source to calculate stats
    with open(ocr_file, 'r') as f:
        source_lines = f.readlines()

    # Build metadata for each colony
    colonies_metadata = []
    for colony in colonies:
        name = colony['name']
        start = colony['start']
        end = colony['end']

        # Calculate stats
        content_lines = source_lines[start-1:end]
        content = ''.join(content_lines)
        char_count = len(content)
        line_count = end - start + 1

        # Create filename
        filename = name.replace(' ', '_').replace(',', '').replace('(', '').replace(')', '').replace("'", '').replace('.', '').replace('**', '') + '.md'

        colonies_metadata.append({
            'colony_name': name,
            'year': year,
            'start_line': start,
            'end_line': end,
            'char_count': char_count,
            'line_count': line_count,
            'filename': filename
        })

    # Create metadata structure
    metadata = {
        'year': year,
        'source_file': str(ocr_file),
        'total_colonies': len(colonies_metadata),
        'colonies': colonies_metadata,
        'processing_notes': {
            'parser': 'Automated LLM-based boundary identification',
            'date': datetime.now().strftime('%Y-%m-%d'),
            'method': 'Automated pattern matching with content structure verification',
            'notes': [
                f'Identified {len(colonies_metadata)} colonies using OCR pattern matching',
                'Colony sections identified by all-caps headers followed by "Situation", "Area", "Climate", etc.',
                'Boundaries verified based on content structure',
            ]
        }
    }

    # Write metadata file
    metadata_file = Path(f'output_2/{year}_manual_parsed.json')
    with open(metadata_file, 'w') as f:
        json.dump(metadata, f, indent=2)

    print(f"Created metadata file: {metadata_file}")
    return metadata_file


def main():
    """Process all years 1951-1955."""
    years = [1951, 1952, 1953, 1954, 1955]
    results = []

    for year in years:
        try:
            # Analyze year
            year_data = analyze_year(year)

            if year_data:
                # Extract colonies
                output_dir = extract_colonies(year_data)

                # Create metadata
                metadata_file = create_metadata(year_data, output_dir)

                results.append({
                    'year': year,
                    'status': 'success',
                    'colonies_count': len(year_data['colonies']),
                    'output_dir': str(output_dir),
                    'metadata_file': str(metadata_file)
                })

                print(f"\n✓ Year {year} completed successfully")
            else:
                results.append({
                    'year': year,
                    'status': 'failed',
                    'error': 'No colonies found or OCR file missing'
                })
                print(f"\n✗ Year {year} failed")

        except Exception as e:
            results.append({
                'year': year,
                'status': 'error',
                'error': str(e)
            })
            print(f"\n✗ Year {year} error: {e}")

    # Print summary
    print(f"\n\n{'='*70}")
    print("PROCESSING SUMMARY")
    print(f"{'='*70}\n")

    for result in results:
        year = result['year']
        status = result['status']
        if status == 'success':
            print(f"Year {year}: ✓ {result['colonies_count']} colonies extracted")
        else:
            print(f"Year {year}: ✗ {result.get('error', 'Failed')}")

    # Save results
    results_file = Path('years_1951_1955_results.json')
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nResults saved to {results_file}")


if __name__ == '__main__':
    main()
