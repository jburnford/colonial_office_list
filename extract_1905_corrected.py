#!/usr/bin/env python3
"""
Extract corrected 1905 colonies based on manual boundary verification.

VERIFIED CORRECTIONS:
- 49 colonies with correct boundaries (extract as-is)
- 6 colonies with multiple segments to merge
- 36 non-colony sections to exclude

Total: 55 legitimate colonies (from 91 original extractions)
"""

import json
from pathlib import Path

# Source OCR file
source_file = Path('/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1905/olmocr_results.md')

# Output directory
output_dir = Path('/home/user/colonial_office_list/output_2/1905_manual_parsed')
output_dir.mkdir(parents=True, exist_ok=True)

# Read source file
print("Reading OCR source file...")
with open(source_file, 'r') as f:
    lines = f.readlines()

print(f"Total lines in source: {len(lines)}")
print("=" * 80)
print("EXTRACTING CORRECTED 1905 COLONIES")
print("=" * 80)
print()

# Group A: Colonies with correct boundaries (extract as-is)
colonies_exact = [
    ('THE_COMMONWEALTH', 2639, 3449),
    ('NEW_SOUTH_WALES', 3451, 4830),
    ('QUEENSLAND', 4832, 5097),
    ('SOUTH_AUSTRALIA', 5487, 5741),
    ('TASMANIA', 6313, 6999),
    ('VICTORIA', 7000, 7266),
    ('BAHAMAS', 8696, 8996),
    ('BARBADOS', 8998, 9611),
    ('BRITISH_CENTRAL_AFRICA_PROTECTORATE', 9978, 10164),
    ('BRITISH_GUIANA', 10166, 10323),
    ('THE_DOMINION', 11135, 11506),
    ('PROVINCE_OF_ONTARIO', 11679, 12163),
    ('NOVA_SCOTIA', 13036, 13270),
    ('NEW_BRUNSWICK', 13272, 13431),
    ('MANITOBA_AND_KEEWATIN', 13433, 13582),
    ('BRITISH_COLUMBIA', 13583, 13805),
    ('PRINCE_EDWARD_ISLAND', 13806, 13916),
    ('THE_NORTH_WEST_TERRITORIES', 13917, 14059),
    ('CEYLON', 17397, 17632),
    ('CYPRUS', 18213, 18842),
    ('FALKLAND_ISLANDS', 18844, 18967),
    ('GIBRALTAR', 19861, 20077),
    ('THE_GOLD_COAST_COLONY', 20079, 20145),
    ('THE_NORTHERN_TERRITORIES', 20315, 21194),
    ('JAMAICA', 21196, 21400),
    ('LABUAN', 21990, 22714),
    ('THE_LEEWARD_ISLANDS', 22715, 22897),
    ('ANTIGUA', 22899, 23203),
    ('DOMINICA', 23410, 23659),
    ('MONTSERRAT', 23661, 23833),
    ('VIRGIN_ISLANDS', 23835, 23981),
    ('MALTA', 23983, 24581),
    ('MAURITIUS', 24582, 24951),
    ('NEWFOUNDLAND', 26236, 26661),
    ('NEW_ZEALAND', 26663, 26981),
    ('PUKAPUKA_OR_DANGER_ISLAND_AND_NASSAU', 26983, 27508),
    ('NORTHERN_NIGERIA', 27658, 27836),
    ('ORANGE_RIVER_COLONY', 27838, 28644),
    ('SEYCHELLES', 28646, 28983),
    ('SIERRA_LEONE', 28984, 29427),
    ('BASUTOLAND', 29429, 29562),
    ('BECHUANALAND_PROTECTORATE', 29564, 30061),
    ('SOUTHERN_NIGERIA', 30062, 30837),
    ('SINGAPORE', 30839, 31062),
    ('THE_FEDERATED_STATES_OF_THE_MALAY_PENINSULA', 31064, 31381),
    ('TURKS_AND_CAICOS_ISLANDS', 33447, 33591),
    ('WEIHAIWEI', 33592, 33755),
    ('THE_WINDWARD_ISLANDS', 33756, 33834),
    ('GRENADA', 33835, 34568),
]

print(f"GROUP A: Extracting {len(colonies_exact)} colonies with correct boundaries...")
print()

extracted_colonies = []

for colony_name, start, end in colonies_exact:
    # Extract lines (convert to 0-indexed)
    colony_lines = lines[start-1:end]

    # Write to file
    output_file = output_dir / f"{colony_name}.md"
    with open(output_file, 'w') as f:
        f.writelines(colony_lines)

    actual_lines = len(colony_lines)
    print(f"✅ {colony_name}:")
    print(f"   Lines: {start}-{end} ({actual_lines} lines)")
    print(f"   File: {output_file.name}")

    extracted_colonies.append({
        'name': colony_name.replace('_', ' '),
        'filename': f"{colony_name}.md",
        'start_line': start,
        'end_line': end,
        'line_count': actual_lines,
        'extraction_method': 'exact_boundaries'
    })

print()
print("=" * 80)
print(f"GROUP B: Extracting 6 colonies with merged segments...")
print("=" * 80)
print()

# Group B: Colonies requiring segment merging
colonies_merged = [
    ('BERMUDA', [(9613, 9842), (9843, 9977)]),
    ('BRITISH_HONDURAS', [(10799, 10925), (10926, 11133)]),
    ('CAPE_OF_GOOD_HOPE', [(14061, 14459), (14460, 16313)]),
    ('FIJI', [(19033, 19206), (19207, 19277), (19278, 19859)]),
    ('NATAL', [(25473, 25608), (25610, 26235)]),
    ('TRINIDAD_AND_TOBAGO', [(32351, 32773), (32774, 33043), (33044, 33445)]),
]

for colony_name, segments in colonies_merged:
    # Merge all segments
    colony_lines = []
    total_lines = 0

    for start, end in segments:
        segment_lines = lines[start-1:end]
        colony_lines.extend(segment_lines)
        total_lines += len(segment_lines)

    # Write merged content to file
    output_file = output_dir / f"{colony_name}.md"
    with open(output_file, 'w') as f:
        f.writelines(colony_lines)

    # Format segment info for display
    segment_str = ", ".join([f"{s}-{e}" for s, e in segments])

    print(f"✅ {colony_name}:")
    print(f"   Segments merged: {segment_str}")
    print(f"   Total lines: {total_lines}")
    print(f"   File: {output_file.name}")

    # Use full range for metadata
    full_start = segments[0][0]
    full_end = segments[-1][1]

    extracted_colonies.append({
        'name': colony_name.replace('_', ' '),
        'filename': f"{colony_name}.md",
        'start_line': full_start,
        'end_line': full_end,
        'line_count': total_lines,
        'extraction_method': 'merged_segments',
        'segments': [{'start': s, 'end': e} for s, e in segments]
    })

print()
print("=" * 80)
print("EXTRACTION COMPLETE")
print("=" * 80)
print()
print(f"Total colonies extracted: {len(extracted_colonies)}")
print(f"Output directory: {output_dir}")
print()
print("Next step: Run create_1905_metadata.py to generate corrected metadata JSON")
