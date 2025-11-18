#!/usr/bin/env python3
"""
Analyze output_2 files to find missing colonies by identifying gaps in year coverage.
If a colony appears in year X and year X+N but not in years X+1 to X+N-1, we likely missed those years.
"""

import json
import os
from collections import defaultdict
from pathlib import Path

def extract_colonies_from_year(year_file):
    """Extract all colony names from a year's JSON file."""
    try:
        with open(year_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        colonies = set()

        # Handle different possible structures
        if isinstance(data, dict):
            if 'colonies' in data:
                for colony in data['colonies']:
                    if isinstance(colony, dict):
                        # Try both 'name' and 'colony_name' fields
                        name = colony.get('name') or colony.get('colony_name')
                        if name:
                            colonies.add(name)
            elif 'territories' in data:
                for territory in data['territories']:
                    if isinstance(territory, dict):
                        name = territory.get('name') or territory.get('colony_name')
                        if name:
                            colonies.add(name)
            else:
                # Try to find colony names in the structure
                for key, value in data.items():
                    if isinstance(value, list):
                        for item in value:
                            if isinstance(item, dict):
                                name = item.get('name') or item.get('colony_name')
                                if name:
                                    colonies.add(name)
        elif isinstance(data, list):
            for item in data:
                if isinstance(item, dict):
                    name = item.get('name') or item.get('colony_name')
                    if name:
                        colonies.add(name)

        return colonies
    except Exception as e:
        print(f"Error processing {year_file}: {e}")
        return set()

def normalize_colony_name(name):
    """Normalize colony names for comparison."""
    # Remove common variations
    name = name.upper()
    name = name.replace('THE ', '')
    name = name.replace('BRITISH ', '')
    name = name.strip()
    return name

def main():
    output_dir = Path('output_2')

    # Find all year JSON files
    year_files = sorted([f for f in output_dir.glob('*_manual_parsed.json')])

    if not year_files:
        print("No year files found in output_2/")
        return

    # Extract year and colonies for each file
    year_to_colonies = {}
    all_years = []

    for year_file in year_files:
        # Extract year from filename (e.g., "1867_manual_parsed.json" -> 1867)
        year_str = year_file.stem.split('_')[0]
        try:
            year = int(year_str)
            all_years.append(year)
            colonies = extract_colonies_from_year(year_file)
            year_to_colonies[year] = colonies
            print(f"Year {year}: {len(colonies)} colonies found")
        except ValueError:
            print(f"Skipping non-year file: {year_file}")

    all_years.sort()
    print(f"\nTotal years analyzed: {len(all_years)}")
    print(f"Year range: {min(all_years)} - {max(all_years)}")

    # Build colony -> years mapping
    colony_to_years = defaultdict(set)

    for year, colonies in year_to_colonies.items():
        for colony in colonies:
            normalized = normalize_colony_name(colony)
            colony_to_years[normalized].add(year)

    print(f"\nTotal unique colonies found: {len(colony_to_years)}")

    # Find missing years (gaps in the dataset)
    all_years_set = set(all_years)
    min_year, max_year = min(all_years), max(all_years)
    all_possible_years = set(range(min_year, max_year + 1))
    missing_years = sorted(all_possible_years - all_years_set)

    print(f"\n{'='*80}")
    print(f"MISSING YEARS IN DATASET (no parsed file exists)")
    print(f"{'='*80}")
    print(f"\nTotal missing years: {len(missing_years)}")

    # Group consecutive missing years
    if missing_years:
        ranges = []
        start = missing_years[0]
        end = missing_years[0]

        for year in missing_years[1:]:
            if year == end + 1:
                end = year
            else:
                ranges.append((start, end))
                start = year
                end = year
        ranges.append((start, end))

        for start, end in ranges:
            if start == end:
                print(f"  {start}")
            else:
                print(f"  {start}-{end} ({end - start + 1} years)")

    # Find gaps in colony coverage
    print(f"\n{'='*80}")
    print(f"COLONIES WITH GAPS IN COVERAGE")
    print(f"{'='*80}")
    print(f"\nAnalyzing colonies that appear in multiple non-consecutive years...")
    print(f"(Gaps likely indicate missing parsed data)\n")

    gaps_found = []

    for colony, years in sorted(colony_to_years.items()):
        if len(years) < 2:
            continue

        years_list = sorted(years)
        min_year = years_list[0]
        max_year = years_list[-1]

        # Find gaps within the colony's coverage period
        expected_years = set(range(min_year, max_year + 1))

        # Only consider years where we have dataset files
        expected_years = expected_years & all_years_set

        missing_in_coverage = sorted(expected_years - set(years_list))

        if missing_in_coverage:
            # Group consecutive missing years
            ranges = []
            start = missing_in_coverage[0]
            end = missing_in_coverage[0]

            for year in missing_in_coverage[1:]:
                if year == end + 1:
                    end = year
                else:
                    ranges.append((start, end))
                    start = year
                    end = year
            ranges.append((start, end))

            gap_info = {
                'colony': colony,
                'first_year': min_year,
                'last_year': max_year,
                'total_years_found': len(years_list),
                'missing_count': len(missing_in_coverage),
                'missing_ranges': ranges
            }
            gaps_found.append(gap_info)

    # Sort by number of missing years (descending)
    gaps_found.sort(key=lambda x: x['missing_count'], reverse=True)

    print(f"Found {len(gaps_found)} colonies with gaps in coverage\n")

    for gap in gaps_found:
        print(f"\n{gap['colony']}")
        print(f"  Coverage: {gap['first_year']}-{gap['last_year']} ({gap['total_years_found']} years found)")
        print(f"  Missing {gap['missing_count']} year(s):")
        for start, end in gap['missing_ranges']:
            if start == end:
                print(f"    - {start}")
            else:
                print(f"    - {start}-{end} ({end - start + 1} years)")

    # Summary statistics
    print(f"\n{'='*80}")
    print(f"SUMMARY")
    print(f"{'='*80}")
    print(f"Total colonies analyzed: {len(colony_to_years)}")
    print(f"Colonies with gaps: {len(gaps_found)}")
    print(f"Total missing year-colony combinations: {sum(g['missing_count'] for g in gaps_found)}")

    # Export detailed report
    report_file = 'missing_colonies_report.json'
    report = {
        'missing_years': missing_years,
        'colonies_with_gaps': [
            {
                'colony': g['colony'],
                'first_year': g['first_year'],
                'last_year': g['last_year'],
                'years_found': g['total_years_found'],
                'years_missing': g['missing_count'],
                'missing_years': [
                    f"{s}-{e}" if s != e else str(s)
                    for s, e in g['missing_ranges']
                ]
            }
            for g in gaps_found
        ],
        'total_gaps': sum(g['missing_count'] for g in gaps_found)
    }

    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)

    print(f"\nDetailed report saved to: {report_file}")

if __name__ == '__main__':
    main()
