#!/usr/bin/env python3
"""
Analyze quality of manual parsed outputs across all years.
Checks for:
1. Overlapping line ranges (data contamination)
2. Suspiciously large colonies (>100KB)
3. Suspiciously small colonies (<500 chars)
4. Line range inconsistencies
"""

import json
import os
from pathlib import Path
from collections import defaultdict

def analyze_year(json_path):
    """Analyze a single year's manual parsed data."""
    with open(json_path, 'r') as f:
        data = json.load(f)

    year = data.get('year')
    colonies = data.get('colonies', [])

    issues = {
        'overlaps': [],
        'huge_colonies': [],
        'tiny_colonies': [],
        'line_issues': []
    }

    # Check for overlapping line ranges
    for i, colony1 in enumerate(colonies):
        name1 = colony1.get('name') or colony1.get('colony_name', 'Unknown')
        start1 = colony1.get('start_line', 0)
        end1 = colony1.get('end_line', 0)
        char_count1 = colony1.get('char_count', 0)
        line_count1 = colony1.get('line_count', 0)

        # Check for line range issues
        if end1 <= start1:
            issues['line_issues'].append({
                'colony': name1,
                'start': start1,
                'end': end1,
                'issue': 'end <= start'
            })

        # Check for huge colonies (>500KB)
        if char_count1 > 500000:
            issues['huge_colonies'].append({
                'colony': name1,
                'start': start1,
                'end': end1,
                'lines': line_count1,
                'chars': char_count1
            })

        # Check for tiny colonies (<500 chars)
        if char_count1 > 0 and char_count1 < 500:
            issues['tiny_colonies'].append({
                'colony': name1,
                'start': start1,
                'end': end1,
                'lines': line_count1,
                'chars': char_count1
            })

        # Check for overlaps with other colonies
        for j, colony2 in enumerate(colonies[i+1:], start=i+1):
            name2 = colony2.get('name') or colony2.get('colony_name', 'Unknown')
            start2 = colony2.get('start_line', 0)
            end2 = colony2.get('end_line', 0)

            # Check if ranges overlap
            if start2 < end1:
                overlap_start = max(start1, start2)
                overlap_end = min(end1, end2)
                overlap_lines = overlap_end - overlap_start

                issues['overlaps'].append({
                    'colony1': name1,
                    'range1': f"{start1}-{end1}",
                    'colony2': name2,
                    'range2': f"{start2}-{end2}",
                    'overlap': f"{overlap_start}-{overlap_end} ({overlap_lines} lines)"
                })

    return year, issues

def main():
    output_dir = Path('/home/user/colonial_office_list/output')

    # Find all manual parsed JSON files
    manual_parsed_files = sorted(output_dir.glob('*_manual_parsed.json'))

    print("=" * 80)
    print("MANUAL PARSED OUTPUTS QUALITY ANALYSIS")
    print("=" * 80)
    print(f"\nAnalyzing {len(manual_parsed_files)} years of manually parsed data...\n")

    all_issues = defaultdict(list)
    years_with_issues = defaultdict(set)

    for json_file in manual_parsed_files:
        year, issues = analyze_year(json_file)

        # Track issues
        for issue_type, issue_list in issues.items():
            if issue_list:
                all_issues[issue_type].extend([(year, issue) for issue in issue_list])
                years_with_issues[issue_type].add(year)

    # Report findings
    print("\n" + "=" * 80)
    print("CRITICAL ISSUE #1: OVERLAPPING LINE RANGES (DATA CONTAMINATION)")
    print("=" * 80)

    if all_issues['overlaps']:
        print(f"\nFound {len(all_issues['overlaps'])} overlapping colonies across {len(years_with_issues['overlaps'])} years!\n")
        for year, overlap in sorted(all_issues['overlaps'], key=lambda x: x[0]):
            print(f"Year {year}:")
            print(f"  {overlap['colony1']} ({overlap['range1']})")
            print(f"  OVERLAPS WITH")
            print(f"  {overlap['colony2']} ({overlap['range2']})")
            print(f"  Overlap region: {overlap['overlap']}")
            print()
    else:
        print("\n✅ No overlapping line ranges found.\n")

    print("\n" + "=" * 80)
    print("CRITICAL ISSUE #2: SUSPICIOUSLY LARGE COLONIES (>500KB)")
    print("=" * 80)

    if all_issues['huge_colonies']:
        print(f"\nFound {len(all_issues['huge_colonies'])} huge colonies across {len(years_with_issues['huge_colonies'])} years!\n")
        for year, colony in sorted(all_issues['huge_colonies'], key=lambda x: x[1]['chars'], reverse=True):
            print(f"Year {year}: {colony['colony']}")
            print(f"  Lines: {colony['lines']:,} | Chars: {colony['chars']:,} | Range: {colony['start']}-{colony['end']}")
            print()
    else:
        print("\n✅ No suspiciously large colonies found.\n")

    print("\n" + "=" * 80)
    print("WARNING: SUSPICIOUSLY SMALL COLONIES (<500 chars)")
    print("=" * 80)

    if all_issues['tiny_colonies']:
        print(f"\nFound {len(all_issues['tiny_colonies'])} tiny colonies across {len(years_with_issues['tiny_colonies'])} years.\n")
        print("Top 20 smallest colonies:")
        for year, colony in sorted(all_issues['tiny_colonies'], key=lambda x: x[1]['chars'])[:20]:
            print(f"Year {year}: {colony['colony']}")
            print(f"  Lines: {colony['lines']} | Chars: {colony['chars']} | Range: {colony['start']}-{colony['end']}")
    else:
        print("\n✅ No suspiciously small colonies found.\n")

    print("\n" + "=" * 80)
    print("SUMMARY STATISTICS")
    print("=" * 80)

    print(f"\nYears analyzed: {len(manual_parsed_files)}")
    print(f"Years with overlapping colonies: {len(years_with_issues['overlaps'])}")
    print(f"Years with huge colonies (>500KB): {len(years_with_issues['huge_colonies'])}")
    print(f"Years with tiny colonies (<500 chars): {len(years_with_issues['tiny_colonies'])}")
    print(f"Years with line range issues: {len(years_with_issues['line_issues'])}")

    total_issues = sum(len(issues) for issues in all_issues.values())
    print(f"\nTotal issues found: {total_issues}")

    if total_issues == 0:
        print("\n✅ ALL YEARS PASSED QUALITY CHECKS!")
    else:
        print(f"\n❌ {len(set.union(*years_with_issues.values()))} years have quality issues")
        print("\nYears with issues:")
        for year in sorted(set.union(*years_with_issues.values())):
            issue_types = [itype for itype, years in years_with_issues.items() if year in years]
            print(f"  {year}: {', '.join(issue_types)}")

if __name__ == '__main__':
    main()
