#!/usr/bin/env python3
"""
Create corrected 1888 metadata JSON based on manual boundary verification.
"""

import json
from pathlib import Path

# Load original metadata to get most fields
original_json = Path('/home/user/colonial_office_list/output/1888_manual_parsed.json')
with open(original_json, 'r') as f:
    original_data = json.load(f)

# Create corrected metadata
corrected_data = {
    "year": 1888,
    "total_colonies": 38,  # Was 37, now 38 (added WESTERN AUSTRALIA)
    "parsing_method": "Manual LLM-based boundary verification (output_2)",
    "remediation_date": "November 12, 2025",
    "corrections_applied": [
        "MAURITIUS truncated from 1615 to 910 lines (removed NATAL contamination)",
        "QUEENSLAND truncated from 1008 to 535 lines (removed ST. HELENA contamination)",
        "ST. HELENA truncated from 473 to 90 lines (removed WESTERN AUSTRALIA contamination)",
        "WESTERN AUSTRALIA newly extracted (383 lines) - was missing from original parse",
        "THE WINDWARD ISLANDS truncated from 1085 to 38 lines (removed SOUTH AUSTRALIA contamination and orphaned headers)",
        "Orphaned page headers (lines 20258-20272) intentionally not extracted"
    ],
    "historical_context": "Year 1888 - Colonial expansion peak, Berlin Conference aftermath",
    "colonies": []
}

# Corrected colonies with verified boundaries
corrections = {
    "MAURITIUS": {
        "start_line": 15271,
        "end_line": 16180,
        "line_count": 910,
        "note": "Corrected: removed NATAL contamination"
    },
    "QUEENSLAND": {
        "start_line": 19212,
        "end_line": 19746,
        "line_count": 535,
        "note": "Corrected: removed ST. HELENA contamination"
    },
    "ST. HELENA": {
        "start_line": 19747,
        "end_line": 19836,
        "line_count": 90,
        "note": "Corrected: removed WESTERN AUSTRALIA contamination"
    },
    "WESTERN AUSTRALIA": {
        "start_line": 19837,
        "end_line": 20219,
        "line_count": 383,
        "note": "NEW: Missing from original parse (no standard header)"
    },
    "THE WINDWARD ISLANDS": {
        "start_line": 20220,
        "end_line": 20257,
        "line_count": 38,
        "note": "Corrected: removed SOUTH AUSTRALIA contamination and orphaned headers"
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

# Add WESTERN AUSTRALIA (it wasn't in original)
if not any(c['name'] == 'WESTERN AUSTRALIA' for c in corrected_data['colonies']):
    corrected_data['colonies'].append({
        "name": "WESTERN AUSTRALIA",
        "filename": "WESTERN_AUSTRALIA.md",
        "start_line": 19837,
        "end_line": 20219,
        "line_count": 383,
        "is_appendix": False,
        "correction_note": "NEW: Missing from original parse (no standard header)"
    })

# Sort by start_line
corrected_data['colonies'].sort(key=lambda x: x['start_line'])

# Write corrected metadata
output_file = Path('/home/user/colonial_office_list/output_2/1888_manual_parsed.json')
with open(output_file, 'w') as f:
    json.dump(corrected_data, f, indent=2)

print("=" * 80)
print("CREATED CORRECTED 1888 METADATA")
print("=" * 80)
print(f"\nFile: {output_file}")
print(f"Total colonies: {corrected_data['total_colonies']}")
print(f"Corrections applied: {len(corrected_data['corrections_applied'])}")
print("\nCorrected colonies:")
for name, info in corrections.items():
    print(f"  - {name}: lines {info['start_line']}-{info['end_line']} ({info['line_count']} lines)")
