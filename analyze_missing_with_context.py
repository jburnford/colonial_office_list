#!/usr/bin/env python3
"""
Historically-aware analysis of missing colonies.
Distinguishes between:
1. True gaps (colony appears, disappears, then reappears) - PARSER FAILURE
2. Terminal disappearance (colony stops appearing and never returns) - LIKELY DECOLONIZATION
3. Initial appearance (colony starts appearing at some point) - NORMAL
"""

import json
from pathlib import Path
from collections import defaultdict

def extract_colonies_from_year(year_file):
    """Extract all colony names from a year's JSON file."""
    try:
        with open(year_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        colonies = set()

        if isinstance(data, dict):
            if 'colonies' in data:
                for colony in data['colonies']:
                    if isinstance(colony, dict):
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
    name = name.upper()
    name = name.replace('THE ', '')
    name = name.replace('BRITISH ', '')
    name = name.strip()
    return name

def find_true_gaps(years_list, all_years_set):
    """
    Find TRUE GAPS where a colony appears, disappears, then reappears.
    These indicate parser failures, not decolonization.

    Returns:
    - true_gaps: List of (start, end) tuples for gap periods
    - terminal_year: Year after which colony never appears again (or None)
    """
    if len(years_list) < 2:
        return [], None

    years_sorted = sorted(years_list)
    min_year = years_sorted[0]
    max_year = years_sorted[-1]

    # Find all missing years within the range that have data files
    expected_years = set(range(min_year, max_year + 1))
    expected_years = expected_years & all_years_set  # Only consider years we have data for
    missing_in_range = sorted(expected_years - set(years_sorted))

    if not missing_in_range:
        return [], max_year

    # Group consecutive missing years into gaps
    gaps = []
    start = missing_in_range[0]
    end = missing_in_range[0]

    for year in missing_in_range[1:]:
        if year == end + 1:
            end = year
        else:
            gaps.append((start, end))
            start = year
            end = year
    gaps.append((start, end))

    return gaps, max_year

def main():
    output_dir = Path('output_2')
    year_files = sorted([f for f in output_dir.glob('*_manual_parsed.json')])

    if not year_files:
        print("No year files found in output_2/")
        return

    # Extract year and colonies for each file
    year_to_colonies = {}
    all_years = []

    for year_file in year_files:
        year_str = year_file.stem.split('_')[0]
        try:
            year = int(year_str)
            all_years.append(year)
            colonies = extract_colonies_from_year(year_file)
            year_to_colonies[year] = colonies
        except ValueError:
            continue

    all_years.sort()
    all_years_set = set(all_years)

    print(f"Analyzing {len(all_years)} years: {min(all_years)}-{max(all_years)}\n")

    # Build colony -> years mapping
    colony_to_years = defaultdict(set)
    for year, colonies in year_to_colonies.items():
        for colony in colonies:
            normalized = normalize_colony_name(colony)
            colony_to_years[normalized].add(year)

    # Analyze each colony
    true_gaps_found = []
    terminal_disappearances = []

    for colony, years in sorted(colony_to_years.items()):
        years_list = sorted(years)
        gaps, terminal_year = find_true_gaps(years_list, all_years_set)

        if gaps:
            # This colony has TRUE GAPS (appears, disappears, reappears)
            for gap_start, gap_end in gaps:
                gap_size = gap_end - gap_start + 1
                true_gaps_found.append({
                    'colony': colony,
                    'first_appearance': min(years_list),
                    'last_appearance': max(years_list),
                    'gap_start': gap_start,
                    'gap_end': gap_end,
                    'gap_size': gap_size,
                    'total_years_found': len(years_list)
                })

        # Check if colony disappears before end of dataset
        if terminal_year and terminal_year < max(all_years):
            # Colony stopped appearing before our dataset ends
            # Could be decolonization OR parser failure
            years_absent = max(all_years) - terminal_year
            terminal_disappearances.append({
                'colony': colony,
                'first_year': min(years_list),
                'last_year': terminal_year,
                'years_found': len(years_list),
                'absent_since': terminal_year + 1,
                'years_absent': years_absent
            })

    # Sort by gap size
    true_gaps_found.sort(key=lambda x: x['gap_size'], reverse=True)
    terminal_disappearances.sort(key=lambda x: x['years_absent'], reverse=True)

    # Report TRUE GAPS (these are definitely parser failures)
    print("="*80)
    print("TRUE GAPS - Colony appears, disappears, then REAPPEARS")
    print("="*80)
    print("These are DEFINITE PARSER FAILURES\n")

    if true_gaps_found:
        print(f"Found {len(true_gaps_found)} true gaps across {len(set(g['colony'] for g in true_gaps_found))} colonies\n")

        # Group by colony
        colony_gaps = defaultdict(list)
        for gap in true_gaps_found:
            colony_gaps[gap['colony']].append(gap)

        for colony, gaps in sorted(colony_gaps.items(),
                                   key=lambda x: sum(g['gap_size'] for g in x[1]),
                                   reverse=True):
            total_gap_years = sum(g['gap_size'] for g in gaps)
            print(f"\n{colony}")
            print(f"  Coverage: {gaps[0]['first_appearance']}-{gaps[0]['last_appearance']} ({gaps[0]['total_years_found']} years found)")
            print(f"  Total gap years: {total_gap_years}")
            print(f"  Gaps:")
            for gap in sorted(gaps, key=lambda x: x['gap_start']):
                if gap['gap_start'] == gap['gap_end']:
                    print(f"    - {gap['gap_start']} (1 year)")
                else:
                    print(f"    - {gap['gap_start']}-{gap['gap_end']} ({gap['gap_size']} years)")
    else:
        print("No true gaps found!")

    print(f"\n{'='*80}")
    print("SUMMARY STATISTICS")
    print("="*80)
    total_gap_years = sum(g['gap_size'] for g in true_gaps_found)
    print(f"Total TRUE GAP years (parser failures): {total_gap_years}")
    print(f"Colonies with true gaps: {len(set(g['colony'] for g in true_gaps_found))}")

    # Save detailed report
    report = {
        'true_gaps': true_gaps_found,
        'terminal_disappearances': terminal_disappearances[:50],  # Top 50
        'summary': {
            'total_true_gap_years': total_gap_years,
            'colonies_with_gaps': len(set(g['colony'] for g in true_gaps_found))
        }
    }

    with open('true_gaps_report.json', 'w', encoding='utf-8') as f:
        json.dump(report, f, indent=2)

    print(f"\nDetailed report saved to: true_gaps_report.json")

    # Show most problematic years
    print(f"\n{'='*80}")
    print("MOST PROBLEMATIC YEARS (where gaps occur)")
    print("="*80)

    year_gap_count = defaultdict(int)
    for gap in true_gaps_found:
        for year in range(gap['gap_start'], gap['gap_end'] + 1):
            year_gap_count[year] += 1

    print("\nYears with most colonies missing (top 20):")
    for year, count in sorted(year_gap_count.items(), key=lambda x: x[1], reverse=True)[:20]:
        print(f"  {year}: {count} colonies missing")

if __name__ == '__main__':
    main()
