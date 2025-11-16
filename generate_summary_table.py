#!/usr/bin/env python3
"""
Generate summary table for years 1950-1955 processing.

Shows: year | original→corrected | key issues | files created
"""

import json
from pathlib import Path
from datetime import datetime

def analyze_year(year):
    """Analyze a single year's results."""
    metadata_file = Path(f'output_2/{year}_manual_parsed.json')

    if not metadata_file.exists():
        return None

    with open(metadata_file, 'r') as f:
        metadata = json.load(f)

    # Count files created
    output_dir = Path(f'output_2/{year}_manual_parsed')
    files_created = []
    if output_dir.exists():
        files_created = [
            f"extract_{year}_corrected.py" if year == 1950 else None,
            f"create_{year}_metadata.py" if year == 1950 else None,
            f"output_2/{year}_manual_parsed.json",
            f"output_2/{year}_manual_parsed/"
        ]
        files_created = [f for f in files_created if f is not None]

    # Determine key issues
    colony_count = metadata['total_colonies']
    colonies = metadata['colonies']

    # Calculate statistics
    total_lines = sum(c['line_count'] for c in colonies)
    avg_lines = total_lines // len(colonies) if colonies else 0

    # Identify potential issues
    issues = []

    # Check for very small or very large colonies (potential over/under extraction)
    small_colonies = [c for c in colonies if c['line_count'] < 100]
    large_colonies = [c for c in colonies if c['line_count'] > 2000]

    if small_colonies:
        issues.append(f"{len(small_colonies)} colonies < 100 lines")
    if large_colonies:
        issues.append(f"{len(large_colonies)} colonies > 2000 lines")

    # Check for duplicates or similar names
    names = [c['colony_name'] for c in colonies]
    if len(names) != len(set(names)):
        issues.append("Potential duplicate names")

    # No issues found
    if not issues:
        issues.append("No major issues detected")

    return {
        'year': year,
        'colony_count': colony_count,
        'original_count': 'N/A',  # We don't have original automated extraction for comparison
        'key_issues': '; '.join(issues),
        'files_created': len([f for f in Path('.').glob(f'*{year}*') if f.is_file()]) + 2,  # Scripts + metadata + dir
        'total_lines': total_lines,
        'avg_lines': avg_lines
    }


def main():
    """Generate summary table."""
    years = [1950, 1951, 1952, 1953, 1954, 1955]
    results = []

    print("\n" + "="*120)
    print("COLONIAL OFFICE LIST YEARS 1950-1955 - PROCESSING SUMMARY")
    print("="*120)
    print(f"\nProcessing Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Method: Manual LLM-based boundary identification with automated extraction\n")

    # Collect data for all years
    for year in years:
        result = analyze_year(year)
        if result:
            results.append(result)

    # Print table header
    print(f"\n{'Year':<8} | {'Colonies':<12} | {'Avg Lines':<12} | {'Key Issues':<45} | {'Files Created':<15}")
    print("-" * 120)

    # Print table rows
    for result in results:
        year = result['year']
        colony_count = result['colony_count']
        avg_lines = result['avg_lines']
        issues = result['key_issues']
        files = result['files_created']

        print(f"{year:<8} | {colony_count:<12} | {avg_lines:<12} | {issues:<45} | {files:<15}")

    # Print summary statistics
    print("\n" + "="*120)
    print("DETAILED STATISTICS")
    print("="*120 + "\n")

    for result in results:
        year = result['year']
        print(f"\nYear {year}:")
        print(f"  - Colonies extracted: {result['colony_count']}")
        print(f"  - Total lines: {result['total_lines']:,}")
        print(f"  - Average lines per colony: {result['avg_lines']}")
        print(f"  - Key issues: {result['key_issues']}")
        print(f"  - Output directory: output_2/{year}_manual_parsed/")
        print(f"  - Metadata file: output_2/{year}_manual_parsed.json")

    # Print file locations
    print("\n" + "="*120)
    print("FILES CREATED")
    print("="*120 + "\n")

    print("Extraction and Metadata Scripts:")
    for year in years:
        if year == 1950:
            print(f"  - extract_{year}_corrected.py")
            print(f"  - create_{year}_metadata.py")
            print(f"  - analyze_{year}_structure.py")
            print(f"  - analyze_{year}_structure_v2.py")

    print(f"\nBatch Processing Script:")
    print(f"  - process_years_1951_1955.py")

    print(f"\nMetadata Files:")
    for year in years:
        print(f"  - output_2/{year}_manual_parsed.json")

    print(f"\nOutput Directories:")
    for year in years:
        print(f"  - output_2/{year}_manual_parsed/")

    print(f"\nResults File:")
    print(f"  - years_1951_1955_results.json")

    # Save summary to file
    summary_file = Path('YEARS_1950_1955_SUMMARY.md')
    with open(summary_file, 'w') as f:
        f.write("# Colonial Office List Years 1950-1955 - Processing Summary\n\n")
        f.write(f"**Processing Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"**Method:** Manual LLM-based boundary identification with automated extraction\n\n")

        f.write("## Summary Table\n\n")
        f.write("| Year | Colonies | Avg Lines | Key Issues | Files Created |\n")
        f.write("|------|----------|-----------|------------|---------------|\n")

        for result in results:
            f.write(f"| {result['year']} | {result['colony_count']} | {result['avg_lines']} | {result['key_issues']} | {result['files_created']} |\n")

        f.write("\n## Detailed Statistics\n\n")
        for result in results:
            year = result['year']
            f.write(f"### Year {year}\n\n")
            f.write(f"- **Colonies extracted:** {result['colony_count']}\n")
            f.write(f"- **Total lines:** {result['total_lines']:,}\n")
            f.write(f"- **Average lines per colony:** {result['avg_lines']}\n")
            f.write(f"- **Key issues:** {result['key_issues']}\n")
            f.write(f"- **Output directory:** `output_2/{year}_manual_parsed/`\n")
            f.write(f"- **Metadata file:** `output_2/{year}_manual_parsed.json`\n\n")

        f.write("## Files Created\n\n")
        f.write("### Extraction and Metadata Scripts\n\n")
        f.write("Year 1950:\n")
        f.write("- `extract_1950_corrected.py`\n")
        f.write("- `create_1950_metadata.py`\n")
        f.write("- `analyze_1950_structure.py`\n")
        f.write("- `analyze_1950_structure_v2.py`\n\n")

        f.write("### Batch Processing Script\n\n")
        f.write("- `process_years_1951_1955.py`\n\n")

        f.write("### Metadata Files\n\n")
        for year in years:
            f.write(f"- `output_2/{year}_manual_parsed.json`\n")

        f.write("\n### Output Directories\n\n")
        for year in years:
            f.write(f"- `output_2/{year}_manual_parsed/`\n")

        f.write("\n### Results Files\n\n")
        f.write("- `years_1951_1955_results.json`\n")
        f.write("- `YEARS_1950_1955_SUMMARY.md` (this file)\n")

    print(f"\n\n✓ Summary saved to {summary_file}\n")


if __name__ == '__main__':
    main()
