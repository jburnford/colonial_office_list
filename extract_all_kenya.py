#!/usr/bin/env python3
"""
Extract people data from ALL Kenya Colonial Office List files.
Uses the Kenya-specific extractor (based on Ceylon v3 model).
"""

import os
import json
import glob
import re
from pathlib import Path
from extract_kenya_people import KenyaExtractionOrchestrator


def find_all_kenya_files():
    """Find all Kenya files in output_3."""
    files = []

    for root, dirs, filenames in os.walk('output_3'):
        for filename in filenames:
            if 'kenya' in filename.lower():
                full_path = os.path.join(root, filename)

                # Extract year from directory name
                dir_name = os.path.basename(root)
                year_match = re.search(r'(\d{4})', dir_name)

                if year_match:
                    year = int(year_match.group(1))
                    files.append((year, full_path))

    # Sort by year
    files.sort()
    return files


def main():
    print("="*80)
    print("KENYA COLONIAL OFFICE LISTS - COMPLETE EXTRACTION")
    print("="*80)
    print("\nUsing Kenya-specific extractor (based on Ceylon v3 model)\n")

    # Find all files
    kenya_files = find_all_kenya_files()
    print(f"Found {len(kenya_files)} Kenya files\n")

    orchestrator = KenyaExtractionOrchestrator()

    all_people = []
    year_stats = {}
    failed_files = []

    # Process each file
    for idx, (year, file_path) in enumerate(kenya_files, 1):
        print(f"\n{'='*80}")
        print(f"[{idx}/{len(kenya_files)}] Processing {year}: {os.path.basename(file_path)}")
        print('='*80)

        try:
            people, metadata = orchestrator.extract_from_file(
                file_path=file_path,
                colony="KENYA",
                year=year
            )

            all_people.extend(people)

            year_stats[year] = {
                'file': os.path.basename(file_path),
                'total_people': len(people),
                'avg_confidence': metadata.get('avg_confidence', 0)
            }

            print(f"\n✓ Extracted {len(people)} people from {year}")

        except Exception as e:
            print(f"\n✗ Error processing {year}: {e}")
            import traceback
            traceback.print_exc()
            failed_files.append((year, file_path, str(e)))

    # Generate summary
    print(f"\n\n{'='*80}")
    print("EXTRACTION COMPLETE - SUMMARY")
    print('='*80)
    print(f"\nTotal people extracted: {len(all_people):,}")
    print(f"Files processed successfully: {len(year_stats)}/{len(kenya_files)}")
    print(f"Files failed: {len(failed_files)}")

    if failed_files:
        print(f"\nFailed files:")
        for year, path, error in failed_files[:10]:
            print(f"  {year}: {error}")

    # Quality metrics
    if all_people:
        high_conf = sum(1 for p in all_people if p.confidence >= 0.85)
        med_conf = sum(1 for p in all_people if 0.6 <= p.confidence < 0.85)
        low_conf = sum(1 for p in all_people if p.confidence < 0.6)
        unknown_roles = sum(1 for p in all_people if p.role == "Unknown")

        print(f"\nQuality Metrics:")
        print(f"  High confidence (>=0.85): {high_conf} ({100*high_conf/len(all_people):.1f}%)")
        print(f"  Med confidence (0.6-0.84): {med_conf} ({100*med_conf/len(all_people):.1f}%)")
        print(f"  Low confidence (<0.6):     {low_conf} ({100*low_conf/len(all_people):.1f}%)")
        print(f"  Unknown roles:             {unknown_roles} ({100*unknown_roles/len(all_people):.1f}%)")

    # Save results
    output_file = 'kenya_all_years_v1.json'
    results = {
        'metadata': {
            'colony': 'KENYA',
            'extraction_date': '2025-11-23',
            'total_people': len(all_people),
            'total_files': len(year_stats),
            'year_range': f"{min(year_stats.keys())}-{max(year_stats.keys())}" if year_stats else "N/A",
            'extractor_version': 'v1.0',
            'year_stats': year_stats,
            'failed_files': [{'year': y, 'file': os.path.basename(f), 'error': e} for y, f, e in failed_files]
        },
        'people': [p.__dict__ for p in all_people]
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\nResults saved to: {output_file}")
    print('='*80)


if __name__ == "__main__":
    main()
