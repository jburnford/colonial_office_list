#!/usr/bin/env python3
"""
Extract people data from ALL Ceylon Colonial Office List files (1867-1963).

Uses the v3 specialized Ceylon extractor (96.2/100 quality).
"""

import os
import json
import glob
import re
from pathlib import Path
from extract_ceylon_people import CeylonExtractionOrchestrator


def find_all_ceylon_files():
    """Find all Ceylon files in output_3."""
    files = []

    for root, dirs, filenames in os.walk('output_3'):
        for filename in filenames:
            if 'ceylon' in filename.lower():
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
    print("CEYLON COLONIAL OFFICE LISTS - COMPLETE EXTRACTION")
    print("="*80)
    print("\nUsing v3 specialized Ceylon extractor (96.2/100 quality)")
    print("Fixes: location filtering, qualification handling, plural roles\n")

    # Find all files
    ceylon_files = find_all_ceylon_files()
    print(f"Found {len(ceylon_files)} Ceylon files (1867-1963)\n")

    orchestrator = CeylonExtractionOrchestrator()

    all_people = []
    year_stats = {}
    failed_files = []

    # Process each file
    for idx, (year, file_path) in enumerate(ceylon_files, 1):
        print(f"\n{'='*80}")
        print(f"[{idx}/{len(ceylon_files)}] Processing {year}: {os.path.basename(file_path)}")
        print('='*80)

        try:
            people, metadata = orchestrator.extract_from_file(
                file_path=file_path,
                colony="CEYLON",
                year=year,
                use_cache=True
            )

            all_people.extend(people)

            year_stats[year] = {
                'file': os.path.basename(file_path),
                'total_people': len(people),
                'regex_extracted': metadata['phases']['pattern_extraction']['extracted'],
                'task_extracted': metadata['phases']['llm_extraction']['extracted'],
                'avg_confidence': metadata['phases']['validation']['avg_confidence']
            }

            print(f"\n✓ Extracted {len(people)} people from {year}")

        except Exception as e:
            print(f"\n✗ Error processing {year}: {e}")
            failed_files.append((year, file_path, str(e)))

    # Generate summary
    print(f"\n\n{'='*80}")
    print("EXTRACTION COMPLETE - SUMMARY")
    print('='*80)
    print(f"\nTotal people extracted: {len(all_people)}")
    print(f"Files processed successfully: {len(year_stats)}/{len(ceylon_files)}")
    print(f"Files failed: {len(failed_files)}")

    if failed_files:
        print("\nFailed files:")
        for year, path, error in failed_files:
            print(f"  {year}: {error}")

    # Quality metrics
    high_conf = sum(1 for p in all_people if p.confidence >= 0.85)
    med_conf = sum(1 for p in all_people if 0.6 <= p.confidence < 0.85)
    low_conf = sum(1 for p in all_people if p.confidence < 0.6)
    unknown_roles = sum(1 for p in all_people if p.role == "Unknown")

    print(f"\nQuality Metrics:")
    print(f"  High confidence (>=0.85): {high_conf} ({high_conf/len(all_people)*100:.1f}%)")
    print(f"  Med confidence (0.6-0.84): {med_conf} ({med_conf/len(all_people)*100:.1f}%)")
    print(f"  Low confidence (<0.6):     {low_conf} ({low_conf/len(all_people)*100:.1f}%)")
    print(f"  Unknown roles:             {unknown_roles} ({unknown_roles/len(all_people)*100:.1f}%)")

    # Extraction methods
    from collections import Counter
    methods = Counter(p.extraction_method for p in all_people)
    print(f"\nExtraction Methods:")
    for method, count in sorted(methods.items(), key=lambda x: -x[1]):
        print(f"  {method}: {count} ({count/len(all_people)*100:.1f}%)")

    # Save results
    output = {
        'metadata': {
            'extraction_date': '2025-11-20',
            'colony': 'CEYLON',
            'total_people': len(all_people),
            'files_processed': len(year_stats),
            'files_failed': len(failed_files),
            'year_range': f"{min(year_stats.keys())}-{max(year_stats.keys())}" if year_stats else "N/A",
            'avg_confidence': sum(p.confidence for p in all_people) / len(all_people) if all_people else 0,
            'quality_metrics': {
                'high_confidence_pct': high_conf / len(all_people) * 100 if all_people else 0,
                'unknown_roles_pct': unknown_roles / len(all_people) * 100 if all_people else 0
            },
            'extraction_methods': dict(methods)
        },
        'year_stats': year_stats,
        'failed_files': [{'year': y, 'file': os.path.basename(f), 'error': e} for y, f, e in failed_files],
        'people': [p.__dict__ for p in all_people]
    }

    output_file = 'ceylon_all_years_v3.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\nResults saved to: {output_file}")
    print(f"\n{'='*80}\n")


if __name__ == "__main__":
    main()
