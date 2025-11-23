#!/usr/bin/env python3
"""
Extract people data from ALL Canada Colonial Office List files.
Uses the Canada-specific extractor (Phase 1: Federal departments).
"""

import os
import json
import glob
import re
from pathlib import Path
from extract_canada_people import CanadaExtractionOrchestrator


def find_all_canada_files():
    """Find all Canada files in output_3."""
    files = []

    for root, dirs, filenames in os.walk('output_3'):
        for filename in filenames:
            if 'canada' in filename.lower():
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
    print("CANADA COLONIAL OFFICE LISTS - COMPLETE EXTRACTION")
    print("="*80)
    print("\nUsing Canada Phase 1 extractor (Federal departments only)\n")

    # Find all files
    canada_files = find_all_canada_files()
    print(f"Found {len(canada_files)} Canada files\n")

    orchestrator = CanadaExtractionOrchestrator()

    all_people = []
    year_stats = {}
    failed_files = []
    canada_specific_stats = {
        'multi_role_entries': 0,
        'acting_officials': 0,
        'skip_sections': 0
    }

    # Process each file
    for idx, (year, file_path) in enumerate(canada_files, 1):
        print(f"\n{'='*80}")
        print(f"[{idx}/{len(canada_files)}] Processing {year}: {os.path.basename(file_path)}")
        print('='*80)

        try:
            people, metadata = orchestrator.extract_from_file(
                file_path=file_path,
                colony="CANADA",
                year=year
            )

            all_people.extend(people)

            # Track Canada-specific stats
            multi_role = sum(1 for p in people if hasattr(p, 'multi_role_id') and p.multi_role_id)
            acting = sum(1 for p in people if hasattr(p, 'is_acting') and p.is_acting)

            canada_specific_stats['multi_role_entries'] += multi_role
            canada_specific_stats['acting_officials'] += acting

            year_stats[year] = {
                'file': os.path.basename(file_path),
                'total_people': len(people),
                'multi_role': multi_role,
                'acting_officials': acting,
                'avg_confidence': metadata.get('avg_confidence', 0)
            }

            print(f"\n✓ Extracted {len(people)} people from {year}")
            print(f"  Multi-role: {multi_role}, Acting: {acting}")

        except Exception as e:
            print(f"\n✗ Error processing {year}: {e}")
            failed_files.append((year, file_path, str(e)))

    # Generate summary
    print(f"\n\n{'='*80}")
    print("EXTRACTION COMPLETE - SUMMARY")
    print('='*80)
    print(f"\nTotal people extracted: {len(all_people):,}")
    print(f"Files processed successfully: {len(year_stats)}/{len(canada_files)}")
    print(f"Files failed: {len(failed_files)}")

    if failed_files:
        print(f"\nFailed files:")
        for year, path, error in failed_files[:10]:
            print(f"  {year}: {error}")

    print(f"\nCanada-Specific Features:")
    print(f"  Multi-role entries: {canada_specific_stats['multi_role_entries']}")
    print(f"  Acting officials: {canada_specific_stats['acting_officials']}")

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
    output_file = 'canada_all_years_v2_fixed.json'
    results = {
        'metadata': {
            'colony': 'CANADA',
            'extraction_date': '2025-11-20',
            'total_people': len(all_people),
            'total_files': len(year_stats),
            'year_range': f"{min(year_stats.keys())}-{max(year_stats.keys())}" if year_stats else "N/A",
            'extractor_version': 'v2_fixed (Phase 1 - Federal only)',
            'canada_specific': canada_specific_stats,
            'year_stats': year_stats
        },
        'people': [p.to_dict() if hasattr(p, 'to_dict') else p.__dict__ for p in all_people]
    }

    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\nResults saved to: {output_file}")
    print('='*80)


if __name__ == "__main__":
    main()
