#!/usr/bin/env python3
"""
Extract people data from ALL Fiji Colonial Office List files.
Uses the Fiji-specific extractor that handles multi-role entries and acting officials.
"""

import os
import json
import glob
import re
from pathlib import Path
from extract_fiji_people import FijiExtractionOrchestrator


def find_all_fiji_files():
    """Find all Fiji files in output_3."""
    files = []

    for root, dirs, filenames in os.walk('output_3'):
        for filename in filenames:
            if 'fiji' in filename.lower():
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
    print("FIJI COLONIAL OFFICE LISTS - COMPLETE EXTRACTION")
    print("="*80)
    print("\nUsing Fiji-specific extractor with multi-role and acting official support\n")

    # Find all files
    fiji_files = find_all_fiji_files()
    print(f"Found {len(fiji_files)} Fiji files\n")

    orchestrator = FijiExtractionOrchestrator()

    all_people = []
    year_stats = {}
    failed_files = []
    fiji_specific_stats = {
        'multi_role_entries': 0,
        'acting_officials': 0,
        'aggregate_statements': 0
    }

    # Process each file
    for idx, (year, file_path) in enumerate(fiji_files, 1):
        print(f"\n{'='*80}")
        print(f"[{idx}/{len(fiji_files)}] Processing {year}: {os.path.basename(file_path)}")
        print('='*80)

        try:
            people, metadata = orchestrator.extract_from_file(
                file_path=file_path,
                colony="FIJI",
                year=year
            )

            all_people.extend(people)

            # Track Fiji-specific stats
            multi_role = sum(1 for p in people if p.multi_role_id)
            acting = sum(1 for p in people if p.is_acting)

            fiji_specific_stats['multi_role_entries'] += multi_role
            fiji_specific_stats['acting_officials'] += acting

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
    print(f"Files processed successfully: {len(year_stats)}/{len(fiji_files)}")
    print(f"Files failed: {len(failed_files)}")

    if failed_files:
        print("\nFailed files:")
        for year, path, error in failed_files[:10]:
            print(f"  {year}: {error[:80]}")

    # Fiji-specific metrics
    print(f"\nFiji-Specific Features:")
    print(f"  Multi-role entries: {fiji_specific_stats['multi_role_entries']}")
    print(f"  Acting officials: {fiji_specific_stats['acting_officials']}")

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

    # Save results
    output = {
        'metadata': {
            'extraction_date': '2025-11-20',
            'colony': 'FIJI',
            'total_people': len(all_people),
            'files_processed': len(year_stats),
            'files_failed': len(failed_files),
            'year_range': f"{min(year_stats.keys())}-{max(year_stats.keys())}" if year_stats else "N/A",
            'avg_confidence': sum(p.confidence for p in all_people) / len(all_people) if all_people else 0,
            'fiji_specific': fiji_specific_stats
        },
        'year_stats': year_stats,
        'failed_files': [{'year': y, 'file': os.path.basename(f), 'error': e} for y, f, e in failed_files],
        'people': [p.__dict__ for p in all_people]
    }

    output_file = 'fiji_all_years_v2.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\nResults saved to: {output_file}")
    print(f"\n{'='*80}\n")


if __name__ == "__main__":
    main()
