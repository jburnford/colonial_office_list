#!/usr/bin/env python3
"""
Extract people data from ALL Gold Coast Colonial Office List files.
Uses the Gold Coast-specific extractor that handles both table and narrative formats.
"""

import os
import json
import glob
import re
from pathlib import Path
from extract_gold_coast_people import GoldCoastExtractionOrchestrator


def find_all_gold_coast_files():
    """Find all Gold Coast files in output_3."""
    files = []

    for root, dirs, filenames in os.walk('output_3'):
        for filename in filenames:
            if 'gold' in filename.lower() and 'coast' in filename.lower():
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
    print("GOLD COAST COLONIAL OFFICE LISTS - COMPLETE EXTRACTION")
    print("="*80)
    print("\nUsing Gold Coast-specific extractor with table and narrative format support\n")

    # Find all files
    gc_files = find_all_gold_coast_files()
    print(f"Found {len(gc_files)} Gold Coast files\n")

    orchestrator = GoldCoastExtractionOrchestrator()

    all_people = []
    year_stats = {}
    failed_files = []
    format_stats = {'table': 0, 'narrative': 0, 'mixed': 0}

    # Process each file
    for idx, (year, file_path) in enumerate(gc_files, 1):
        print(f"\n{'='*80}")
        print(f"[{idx}/{len(gc_files)}] Processing {year}: {os.path.basename(file_path)}")
        print('='*80)

        try:
            people, metadata = orchestrator.extract_from_file(
                file_path=file_path,
                colony="GOLD_COAST",
                year=year
            )

            all_people.extend(people)

            # Detect primary format
            table_count = sum(1 for p in people if 'table' in p.extraction_method)
            narrative_count = sum(1 for p in people if 'narrative' in p.extraction_method or 'pattern' in p.extraction_method)

            if table_count > narrative_count * 2:
                primary_format = 'table'
                format_stats['table'] += 1
            elif narrative_count > table_count * 2:
                primary_format = 'narrative'
                format_stats['narrative'] += 1
            else:
                primary_format = 'mixed'
                format_stats['mixed'] += 1

            year_stats[year] = {
                'file': os.path.basename(file_path),
                'total_people': len(people),
                'format': primary_format,
                'table_entries': table_count,
                'narrative_entries': narrative_count,
                'avg_confidence': metadata.get('avg_confidence', 0)
            }

            print(f"\n✓ Extracted {len(people)} people from {year}")
            print(f"  Format: {primary_format} (table: {table_count}, narrative: {narrative_count})")

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
    print(f"Files processed successfully: {len(year_stats)}/{len(gc_files)}")
    print(f"Files failed: {len(failed_files)}")

    if failed_files:
        print("\nFailed files:")
        for year, path, error in failed_files[:10]:
            print(f"  {year}: {error[:80]}")

    # Format distribution
    print(f"\nFormat Distribution:")
    print(f"  Table format: {format_stats['table']} files")
    print(f"  Narrative format: {format_stats['narrative']} files")
    print(f"  Mixed format: {format_stats['mixed']} files")

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
            'colony': 'GOLD_COAST',
            'total_people': len(all_people),
            'files_processed': len(year_stats),
            'files_failed': len(failed_files),
            'year_range': f"{min(year_stats.keys())}-{max(year_stats.keys())}" if year_stats else "N/A",
            'avg_confidence': sum(p.confidence for p in all_people) / len(all_people) if all_people else 0,
            'format_distribution': format_stats
        },
        'year_stats': year_stats,
        'failed_files': [{'year': y, 'file': os.path.basename(f), 'error': e} for y, f, e in failed_files],
        'people': [p.__dict__ for p in all_people]
    }

    output_file = 'gold_coast_all_years_v2.json'
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\nResults saved to: {output_file}")
    print(f"\n{'='*80}\n")


if __name__ == "__main__":
    main()
