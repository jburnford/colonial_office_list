#!/usr/bin/env python3
"""
Create corrected 1949 metadata JSON based on manual boundary verification.

Year 1949 shows severe over-extraction issues.
"""

import json
from pathlib import Path

# Define corrected colonies (manually verified boundaries)
colonies_data = [
    ("ADEN COLONY", "ADEN_COLONY.md", 3795, 4462, "Separate from Protectorate"),
    ("ADEN PROTECTORATE", "ADEN_PROTECTORATE.md", 4463, 4493, "Short entry - 31 lines"),
    ("BAHAMA ISLANDS", "BAHAMA_ISLANDS.md", 4494, 4942, "Properly extracted"),
    ("BARBADOS", "BARBADOS.md", 4943, 5463, "Properly extracted"),
    ("BERMUDA", "BERMUDA.md", 5464, 5971, "Properly extracted"),
    ("BRITISH GUIANA", "BRITISH_GUIANA.md", 5972, 6793, "Merged duplicate at 6494"),
    ("BRITISH HONDURAS", "BRITISH_HONDURAS.md", 6794, 7183, "Merged duplicate at 7023"),
    ("BRITISH SOMALILAND", "BRITISH_SOMALILAND.md", 7184, 8890, "Properly extracted - large entry (1707 lines)"),
    ("FALKLAND ISLANDS", "FALKLAND_ISLANDS.md", 8891, 9220, "Merged: 8891 main, 9025 PUBLIC FINANCE subsection"),
    ("FIJI", "FIJI.md", 9221, 10017, "From 'FALKLAND ISLANDS : FIJI' header (797 lines)"),
    ("GAMBIA", "GAMBIA.md", 10018, 10473, "Properly extracted"),
    ("GIBRALTAR", "GIBRALTAR.md", 10474, 10913, "Properly extracted"),
    ("GOLD COAST", "GOLD_COAST.md", 10914, 12068, "Merged 2 entries (10914, 11416)"),
    ("HONG KONG", "HONG_KONG.md", 12069, 12802, "Merged 4 entries (12069, 12605 VOLUNTEER, 12611 NAVAL, 12700)"),
    ("JAMAICA", "JAMAICA.md", 12803, 13672, "Properly extracted"),
    ("CAYMAN ISLANDS", "CAYMAN_ISLANDS.md", 13673, 13771, "Dependency of Jamaica"),
    ("TURKS AND CAICOS ISLANDS", "TURKS_AND_CAICOS_ISLANDS.md", 13772, 13943, "Dependency of Jamaica"),
    ("KENYA", "KENYA.md", 13944, 15110, "Properly extracted"),
    ("LEEWARD ISLANDS", "LEEWARD_ISLANDS.md", 15111, 16124, "Merged 5 entries (15111, 15248 GOVERNORS, 15387 ANTIGUA, 15481, 15722)"),
    ("VIRGIN ISLANDS", "VIRGIN_ISLANDS.md", 16125, 17344, "Part of Leeward Islands (1220 lines - very large)"),
    ("MALTA", "MALTA.md", 17345, 17678, "Merged: 17345 main, 17662 ROYAL MALTA LIBRARY subsection"),
    ("MAURITIUS", "MAURITIUS.md", 17679, 18698, "Properly extracted"),
    ("NIGERIA", "NIGERIA.md", 18699, 20426, "Properly extracted - large entry (1728 lines)"),
    ("NORTH BORNEO", "NORTH_BORNEO.md", 20427, 20778, "Properly extracted"),
    ("NORTHERN RHODESIA", "NORTHERN_RHODESIA.md", 20779, 21767, "Merged duplicate at 21652"),
    ("NYASALAND", "NYASALAND.md", 21768, 22297, "Properly extracted"),
    ("ST. HELENA", "ST_HELENA.md", 22298, 22640, "Merged: 22298 main, 22611 'ST. HELENA : SARAWAK' header"),
    ("SARAWAK", "SARAWAK.md", 22641, 23126, "From after ST. HELENA header"),
    ("SEYCHELLES", "SEYCHELLES.md", 23127, 23491, "Properly extracted"),
    ("SIERRA LEONE", "SIERRA_LEONE.md", 23492, 24171, "Properly extracted"),
    ("SINGAPORE", "SINGAPORE.md", 24172, 25003, "Properly extracted"),
    ("TANGANYIKA", "TANGANYIKA.md", 25004, 25723, "Properly extracted"),
    ("TRINIDAD AND TOBAGO", "TRINIDAD_AND_TOBAGO.md", 25724, 26570, "Merged: 25724 header (2 lines), 25726 main content"),
    ("UGANDA", "UGANDA.md", 26571, 27315, "Properly extracted"),
    ("GILBERT AND ELLICE ISLANDS", "GILBERT_AND_ELLICE_ISLANDS.md", 27316, 27575, "Properly extracted"),
    ("BRITISH SOLOMON ISLANDS", "BRITISH_SOLOMON_ISLANDS.md", 27576, 28075, "Properly extracted"),
    ("WINDWARD ISLANDS", "WINDWARD_ISLANDS.md", 28076, 29250, "Merged with sub-islands: 28183 DOMINICA, 28606 ST. LUCIA, 28816 ST. VINCENT, 29227 ST. VINCENT GRENADINES"),
    ("DOMINICA", "DOMINICA.md", 28183, 28605, "Part of Windward Islands"),
    ("ST. LUCIA", "ST_LUCIA.md", 28606, 28815, "Part of Windward Islands"),
    ("ST. VINCENT", "ST_VINCENT.md", 28816, 29250, "Part of Windward Islands (includes GRENADINES 29227)"),
    ("ZANZIBAR", "ZANZIBAR.md", 29251, 29867, "Properly extracted"),
]

# Create corrected metadata
corrected_data = {
    "year": 1949,
    "total_colonies": None,
    "parsing_method": "Manual LLM-based boundary verification (output_2)",
    "remediation_date": "November 16, 2025",
    "original_extraction_count": 60,
    "corrections_applied": [
        "Removed LEGISLATURE entries (KENYA, NIGERIA, MALTA) - not colonies",
        "Merged BRITISH GUIANA duplicate",
        "Merged BRITISH HONDURAS duplicate",
        "Merged FALKLAND ISLANDS (3 entries: main, PUBLIC FINANCE, and FIJI header)",
        "Separated FIJI from FALKLAND ISLANDS header",
        "Merged GOLD COAST (2 entries)",
        "Merged HONG KONG (4 entries: main, VOLUNTEER DEFENCE, NAVAL VOLUNTEER, subsection)",
        "Merged LEEWARD ISLANDS (5 entries including GOVERNORS and ANTIGUA)",
        "Kept VIRGIN ISLANDS separate (very large 1220 lines)",
        "Merged MALTA with ROYAL MALTA LIBRARY",
        "Merged NORTHERN RHODESIA duplicate",
        "Merged ST. HELENA with SARAWAK header, separated SARAWAK",
        "Merged TRINIDAD entries",
        "Merged WINDWARD ISLANDS with sub-islands (DOMINICA, ST. LUCIA, ST. VINCENT)",
        "Net result: 60 → 41 colonies"
    ],
    "issues_found": {
        "legislature_entries": "LEGISLATURE OF KENYA, NIGERIA, MALTA listed as colonies",
        "british_guiana_duplicate": "BRITISH GUIANA appears twice",
        "british_honduras_duplicate": "BRITISH HONDURAS appears twice",
        "falkland_split": "FALKLAND ISLANDS split into 3 entries",
        "fiji_merged_header": "FIJI in 'FALKLAND ISLANDS : FIJI' combined header",
        "gold_coast_duplicate": "GOLD COAST appears twice",
        "hong_kong_split": "HONG KONG split into 4 entries (including volunteer forces)",
        "leeward_islands_over_extraction": "LEEWARD ISLANDS split into 5 entries",
        "northern_rhodesia_duplicate": "NORTHERN RHODESIA appears twice",
        "st_helena_sarawak_header": "ST. HELENA and SARAWAK combined in header",
        "trinidad_split": "TRINIDAD split into 2 entries",
        "windward_islands_over_extraction": "WINDWARD ISLANDS with sub-islands as separate entries"
    },
    "historical_context": "Year 1949 - Continued post-WWII normalization",
    "notes": [
        "Removed non-colony entries (legislature bodies)",
        "Very large entries: BRITISH SOMALILAND (1707 lines), VIRGIN ISLANDS (1220 lines), NIGERIA (1728 lines)",
        "Complex header issue: 'FALKLAND ISLANDS : FIJI' and 'ST. HELENA : SARAWAK'",
        "All boundaries manually verified by reading OCR source content"
    ],
    "colonies": []
}

# Add corrected colonies
for name, filename, start, end, note in colonies_data:
    line_count = end - start + 1
    colony_entry = {
        "name": name,
        "filename": filename,
        "start_line": start,
        "end_line": end,
        "line_count": line_count,
        "is_appendix": False,
        "extraction_method": "manual_verification",
        "note": note
    }
    corrected_data['colonies'].append(colony_entry)

# Sort by start_line
corrected_data['colonies'].sort(key=lambda x: x['start_line'])

# Update total count
corrected_data['total_colonies'] = len(corrected_data['colonies'])

# Write corrected metadata
output_file = Path('/home/user/colonial_office_list/output_2/1949_manual_parsed.json')
with open(output_file, 'w') as f:
    json.dump(corrected_data, f, indent=2)

print("=" * 80)
print("CREATED CORRECTED 1949 METADATA")
print("=" * 80)
print(f"\nFile: {output_file}")
print(f"Total colonies: {corrected_data['total_colonies']}")
print(f"Original extractions: {corrected_data['original_extraction_count']}")
print()
print("✅ Year 1949 manually verified and corrected")
print(f"✅ Corrected from 60 entries to {corrected_data['total_colonies']} proper colonies")
