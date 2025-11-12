#!/usr/bin/env python3
"""
Check for colony name inconsistencies and variations across years.
"""

import json
from pathlib import Path
from collections import defaultdict

def main():
    output_dir = Path('/home/user/colonial_office_list/output')
    manual_parsed_files = sorted(output_dir.glob('*_manual_parsed.json'))

    # Collect all colony names by year
    colonies_by_year = {}
    all_colony_names = set()

    for json_file in manual_parsed_files:
        with open(json_file, 'r') as f:
            data = json.load(f)

        year = data.get('year')
        colonies = data.get('colonies', [])

        colony_names = set()
        for colony in colonies:
            name = colony.get('name') or colony.get('colony_name', 'Unknown')
            colony_names.add(name)
            all_colony_names.add(name)

        colonies_by_year[year] = colony_names

    # Find name variations (similar but different spellings)
    print("=" * 80)
    print("COLONY NAME VARIATIONS ANALYSIS")
    print("=" * 80)
    print(f"\nTotal unique colony names across all years: {len(all_colony_names)}\n")

    # Look for potential duplicates/variations
    sorted_names = sorted(all_colony_names)

    print("\nPotential name variations/duplicates:")
    print("-" * 80)

    # Group by base name
    base_names = defaultdict(list)
    for name in sorted_names:
        # Extract base name (remove common prefixes)
        base = name.replace('THE ', '').replace('DOMINION OF ', '').replace('COMMONWEALTH OF ', '').replace('UNION OF ', '')
        base_names[base].append(name)

    variations = {base: names for base, names in base_names.items() if len(names) > 1}

    if variations:
        for base, names in sorted(variations.items()):
            print(f"\n{base}:")
            for name in names:
                years = [y for y, colonies in colonies_by_year.items() if name in colonies]
                print(f"  - '{name}': Years {min(years)}-{max(years)} ({len(years)} occurrences)")
    else:
        print("\n✅ No obvious name variations found.\n")

    # Find suspicious colony names (likely not real colonies)
    print("\n" + "=" * 80)
    print("SUSPICIOUS 'COLONY' NAMES (Likely Parsing Errors)")
    print("=" * 80)

    suspicious_keywords = [
        'BANK', 'LIMITED', 'COMPANY', 'INTRODUCTION', 'APPENDIX', 'PART',
        'LIST', 'INDEX', 'REGULATIONS', 'LONDON', 'TRANSCRIPT', 'AGENCY',
        'CHARTERED', 'RESISTS', 'RESPECTING', 'ROYAL', 'GARDENS', 'KEW',
        'PARLIAMENTARY', 'HONOURS', 'ORDER', 'KNIGHT', 'BARONET'
    ]

    suspicious = []
    for name in sorted_names:
        for keyword in suspicious_keywords:
            if keyword in name:
                years = [y for y, colonies in colonies_by_year.items() if name in colonies]
                suspicious.append((name, years))
                break

    if suspicious:
        print(f"\nFound {len(suspicious)} suspicious colony names:\n")
        for name, years in suspicious:
            print(f"  {name}: Years {years}")
    else:
        print("\n✅ No suspicious colony names found.\n")

    # Count colonies per year
    print("\n" + "=" * 80)
    print("COLONY COUNT BY YEAR")
    print("=" * 80)
    print()

    for year in sorted(colonies_by_year.keys()):
        count = len(colonies_by_year[year])
        # Flag years with unusually high or low counts
        if count > 80:
            flag = "⚠️  ABNORMALLY HIGH"
        elif count < 5:
            flag = "⚠️  ABNORMALLY LOW"
        else:
            flag = ""

        print(f"{year}: {count:3d} colonies {flag}")

if __name__ == '__main__':
    main()
