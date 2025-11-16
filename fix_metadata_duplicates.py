#!/usr/bin/env python3
"""
Fix metadata files to remove duplicate entries and match actual files on disk.
"""

import json
import os
from pathlib import Path
from datetime import datetime

for year in [1957, 1958, 1959, 1960]:
    print(f"\nFixing {year}...")

    # Load metadata
    metadata_file = Path(f'output_2/{year}_manual_parsed.json')
    with open(metadata_file, 'r') as f:
        data = json.load(f)

    # Get actual files on disk
    output_dir = Path(f'output_2/{year}_manual_parsed')
    actual_files = {f.name for f in output_dir.glob('*.md')}

    # Filter colonies to only those with files on disk
    original_count = len(data['colonies'])
    seen_filenames = set()
    unique_colonies = []

    for colony in data['colonies']:
        filename = colony['filename']
        # Keep only if file exists and we haven't seen this filename before
        if filename in actual_files and filename not in seen_filenames:
            seen_filenames.add(filename)
            unique_colonies.append(colony)

    # Update metadata
    data['colonies'] = sorted(unique_colonies, key=lambda x: x['start_line'])
    data['total_colonies'] = len(unique_colonies)

    # Update processing notes
    data['processing_notes']['corrected_count'] = len(unique_colonies)
    data['processing_notes']['corrections_applied'].append(
        f'Removed {original_count - len(unique_colonies)} duplicate entries from metadata'
    )
    data['processing_notes']['note'] += f' | Metadata corrected to remove {original_count - len(unique_colonies)} duplicates'

    # Write corrected metadata
    with open(metadata_file, 'w') as f:
        json.dump(data, f, indent=2)

    print(f"  Original metadata: {original_count} colonies")
    print(f"  Corrected metadata: {len(unique_colonies)} colonies")
    print(f"  Removed: {original_count - len(unique_colonies)} duplicates")
    print(f"  Files on disk: {len(actual_files)} (should match corrected)")

print("\nAll metadata files corrected!")
