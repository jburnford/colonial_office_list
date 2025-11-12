#!/usr/bin/env python3
"""
Create corrected 1890 metadata JSON based on manual boundary verification.
"""

import json
from pathlib import Path

# Load original metadata to get most fields
original_json = Path('/home/user/colonial_office_list/output/1890_manual_parsed.json')
with open(original_json, 'r') as f:
    original_data = json.load(f)

# Create corrected metadata
corrected_data = {
    "year": 1890,
    "total_colonies": 32,  # Was 31, now 32 (added TASMANIA)
    "parsing_method": "Manual LLM-based boundary verification (output_2)",
    "remediation_date": "November 12, 2025",
    "corrections_applied": [
        "MAURITIUS truncated from 1656 to 1009 lines (removed NATAL contamination)",
        "SOUTH AUSTRALIA truncated from 2295 to 1031 lines (removed STRAITS/TASMANIA contamination)",
        "STRAITS SETTLEMENTS truncated from 1264 to 788 lines (removed TASMANIA contamination)",
        "TASMANIA newly extracted (476 lines) - was missing from original parse"
    ],
    "historical_context": "Year 1890 - Scramble for Africa peak, pre-Second Boer War",
    "colonies": []
}

# Corrected colonies with verified boundaries
corrections = {
    "MAURITIUS": {
        "start_line": 15414,
        "end_line": 16422,
        "line_count": 1009,
        "note": "Corrected: removed NATAL contamination"
    },
    "SOUTH AUSTRALIA": {
        "start_line": 20508,
        "end_line": 21538,
        "line_count": 1031,
        "note": "Corrected: removed STRAITS SETTLEMENTS and TASMANIA contamination"
    },
    "STRAITS SETTLEMENTS": {
        "start_line": 21539,
        "end_line": 22326,
        "line_count": 788,
        "note": "Corrected: removed TASMANIA contamination"
    },
    "TASMANIA": {
        "start_line": 22327,
        "end_line": 22802,
        "line_count": 476,
        "note": "NEW: Missing from original parse (no standard header)"
    }
}

# Start with original colonies
for colony in original_data['colonies']:
    name = colony.get('name', '')

    if name in corrections:
        # Use corrected metadata
        corrected_data['colonies'].append({
            "name": name,
            "filename": f"{name.replace(' ', '_')}.md",
            "start_line": corrections[name]["start_line"],
            "end_line": corrections[name]["end_line"],
            "line_count": corrections[name]["line_count"],
            "is_appendix": False,
            "correction_note": corrections[name]["note"]
        })
    else:
        # Keep original metadata
        corrected_data['colonies'].append(colony)

# Add TASMANIA (it wasn't in original)
if not any(c['name'] == 'TASMANIA' for c in corrected_data['colonies']):
    corrected_data['colonies'].append({
        "name": "TASMANIA",
        "filename": "TASMANIA.md",
        "start_line": 22327,
        "end_line": 22802,
        "line_count": 476,
        "is_appendix": False,
        "correction_note": "NEW: Missing from original parse (no standard header)"
    })

# Sort by start_line
corrected_data['colonies'].sort(key=lambda x: x['start_line'])

# Write corrected metadata
output_file = Path('/home/user/colonial_office_list/output_2/1890_manual_parsed.json')
with open(output_file, 'w') as f:
    json.dump(corrected_data, f, indent=2)

print("=" * 80)
print("CREATED CORRECTED 1890 METADATA")
print("=" * 80)
print(f"\nFile: {output_file}")
print(f"Total colonies: {corrected_data['total_colonies']}")
print(f"Corrections applied: {len(corrected_data['corrections_applied'])}")
print("\nCorrected colonies:")
for name, info in corrections.items():
    print(f"  - {name}: lines {info['start_line']}-{info['end_line']} ({info['line_count']} lines)")
