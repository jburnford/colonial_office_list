#!/usr/bin/env python3
"""
Create corrected 1946 metadata JSON based on manual boundary verification.

Year 1946 (post-WWII) shows over-extraction issues:
- BAHAMAS appears 3x (subsection headers treated as colonies)
- BRITISH GUIANA appears 2x
- CEYLON appears 2x
- GAMBIA appears 2x
- FALKLAND ISLANDS COMPANY (not a colony!)
- GOLD COAST split into 3 entries
- HONG KONG only 4 lines (military admin note)
- LEEWARD ISLANDS over-extracted with sub-islands
- NORTH BORNEO only 4 lines (military admin note)
- SINGAPORE only 3 lines (see under Malaya)
- TRINIDAD appears 4x
- WINDWARD ISLANDS over-extracted with sub-islands
"""

import json
from pathlib import Path

# Output directory
output_dir = Path('/home/user/colonial_office_list/output_2/1946_manual_parsed')

# Define corrected colonies (manually verified boundaries)
colonies_data = [
    ("ADEN", "ADEN.md", 2667, 2990, "Colony section"),
    ("BAHAMA ISLANDS", "BAHAMA_ISLANDS.md", 2991, 3354, "Merged 3 BAHAMAS over-extracted subsections (3075, 3246)"),
    ("BARBADOS", "BARBADOS.md", 3355, 3949, "Properly extracted"),
    ("BERMUDA", "BERMUDA.md", 16902, 17064, "From PART III staff section - no PART II entry"),
    ("BRITISH GUIANA", "BRITISH_GUIANA.md", 3950, 4596, "Merged duplicate at 4478"),
    ("BRITISH HONDURAS", "BRITISH_HONDURAS.md", 4597, 4831, "Properly extracted"),
    ("BRITISH SOLOMON ISLANDS", "BRITISH_SOLOMON_ISLANDS.md", 14040, 14323, "Properly extracted"),
    ("CAYMAN ISLANDS", "CAYMAN_ISLANDS.md", 8139, 8512, "Dependency of Jamaica"),
    ("CEYLON", "CEYLON.md", 4832, 5439, "Merged duplicate at 5245"),
    ("CYPRUS", "CYPRUS.md", 5440, 5852, "Properly extracted"),
    ("DOMINICA", "DOMINICA.md", 15138, 15349, "Part of Windward Islands group"),
    ("FALKLAND ISLANDS", "FALKLAND_ISLANDS.md", 5853, 5933, "Excluded Falkland Islands Company (5934-6097)"),
    ("FIJI", "FIJI.md", 6098, 6483, "Properly extracted"),
    ("GAMBIA", "GAMBIA.md", 6484, 6773, "Merged duplicate at 6686"),
    ("GIBRALTAR", "GIBRALTAR.md", 6774, 6949, "Properly extracted"),
    ("GOLD COAST", "GOLD_COAST.md", 6950, 7479, "Merged 3 entries (6950, 6952, 7394)"),
    ("GRENADA", "GRENADA.md", 14433, 14661, "Part of Windward Islands group - standalone section"),
    ("HONG KONG", "HONG_KONG.md", 7480, 7483, "Short entry - still under military admin post-WWII"),
    ("JAMAICA", "JAMAICA.md", 7484, 8138, "Properly extracted"),
    ("KENYA", "KENYA.md", 8513, 8913, "Properly extracted"),
    ("LEEWARD ISLANDS", "LEEWARD_ISLANDS.md", 8914, 9695, "Merged sub-islands ANTIGUA (9096), MONTSERRAT (9443), VIRGIN ISLANDS (9587), subsection header (9657)"),
    ("MALTA", "MALTA.md", 9696, 9997, "Properly extracted"),
    ("MAURITIUS", "MAURITIUS.md", 9998, 10505, "Properly extracted"),
    ("NIGERIA", "NIGERIA.md", 10506, 11047, "Properly extracted"),
    ("NORTH BORNEO", "NORTH_BORNEO.md", 11048, 11051, "Short entry - still under military admin post-WWII"),
    ("NORTHERN RHODESIA", "NORTHERN_RHODESIA.md", 11052, 11419, "Properly extracted"),
    ("NYASALAND", "NYASALAND.md", 11420, 11590, "Properly extracted"),
    ("PALESTINE", "PALESTINE.md", 11591, 12003, "Properly extracted"),
    ("ST. HELENA", "ST_HELENA.md", 12004, 12200, "Properly extracted"),
    ("ST. LUCIA", "ST_LUCIA.md", 14920, 15137, "Part of Windward Islands group"),
    ("ST. VINCENT", "ST_VINCENT.md", 14662, 14919, "Part of Windward Islands group"),
    ("SARAWAK", "SARAWAK.md", 23310, 23324, "From PART III staff section - no PART II entry"),
    ("SEYCHELLES", "SEYCHELLES.md", 12201, 12368, "Properly extracted"),
    ("SIERRA LEONE", "SIERRA_LEONE.md", 12369, 12693, "Properly extracted"),
    ("SINGAPORE", "SINGAPORE.md", 12694, 12696, "Short entry - see under Malaya"),
    ("SOMALILAND", "SOMALILAND.md", 12697, 13178, "Properly extracted"),
    ("TANGANYIKA", "TANGANYIKA.md", 23606, 24219, "From PART III staff section - no PART II entry"),
    ("TRINIDAD AND TOBAGO", "TRINIDAD_AND_TOBAGO.md", 13179, 13680, "Merged 4 TRINIDAD entries (13179, 13181, 13551, 13666)"),
    ("UGANDA", "UGANDA.md", 13681, 14039, "Properly extracted"),
    ("WINDWARD ISLANDS", "WINDWARD_ISLANDS.md", 14324, 15137, "Merged with ST. VINCENT (14662), ST. LUCIA (14920), DOMINICA (15138) - but keeping separate for historical accuracy"),
    ("ZANZIBAR", "ZANZIBAR.md", 15350, 15603, "Properly extracted"),
]

# Create corrected metadata
corrected_data = {
    "year": 1946,
    "total_colonies": None,  # Will calculate
    "parsing_method": "Manual LLM-based boundary verification (output_2)",
    "remediation_date": "November 16, 2025",
    "original_extraction_count": 52,
    "corrections_applied": [
        "Merged BAHAMA ISLANDS from 3 over-extracted subsections",
        "Merged BRITISH GUIANA duplicate entry",
        "Merged CEYLON duplicate entry",
        "Merged GAMBIA duplicate entry",
        "Removed THE FALKLAND ISLANDS COMPANY (not a colony)",
        "Merged GOLD COAST from 3 entries",
        "Kept HONG KONG short entry (military admin)",
        "Merged LEEWARD ISLANDS with 4 sub-entries (ANTIGUA, MONTSERRAT, VIRGIN ISLANDS, subsection)",
        "Kept NORTH BORNEO short entry (military admin)",
        "Kept SINGAPORE short entry (see under Malaya)",
        "Merged TRINIDAD from 4 entries",
        "Added colonies from PART III: BERMUDA, SARAWAK, TANGANYIKA",
        "Created separate entries for Windward Islands components",
        "Net result: 52 → 41 colonies"
    ],
    "issues_found": {
        "bahamas_over_extraction": "BAHAMAS split into 3 entries - subsection headers treated as separate colonies",
        "british_guiana_duplicate": "BRITISH GUIANA appears twice",
        "ceylon_duplicate": "CEYLON appears twice",
        "gambia_duplicate": "GAMBIA appears twice",
        "falkland_company": "THE FALKLAND ISLANDS COMPANY listed as colony",
        "gold_coast_split": "GOLD COAST split into 3 entries",
        "hong_kong_short": "HONG KONG only 4 lines - still under military admin",
        "leeward_islands_over_extraction": "LEEWARD ISLANDS split with sub-islands ANTIGUA, MONTSERRAT, VIRGIN ISLANDS as separate entries",
        "north_borneo_short": "NORTH BORNEO only 4 lines - military admin",
        "singapore_short": "SINGAPORE only 3 lines - see under Malaya",
        "trinidad_split": "TRINIDAD split into 4 entries",
        "post_wwii_effects": "Post-WWII context: Hong Kong and North Borneo still under military administration"
    },
    "historical_context": "Year 1946 - Post-WWII, some territories still under military administration",
    "notes": [
        "1946 is first post-WWII edition",
        "HONG KONG and NORTH BORNEO have abbreviated entries due to ongoing military administration",
        "SINGAPORE marked as 'see under Malaya'",
        "Some colonies appear only in PART III (staff listings) not PART II (historical/statistical)",
        "WINDWARD ISLANDS and LEEWARD ISLANDS show complex grouping structures",
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
output_file = Path('/home/user/colonial_office_list/output_2/1946_manual_parsed.json')
with open(output_file, 'w') as f:
    json.dump(corrected_data, f, indent=2)

print("=" * 80)
print("CREATED CORRECTED 1946 METADATA")
print("=" * 80)
print(f"\nFile: {output_file}")
print(f"Total colonies: {corrected_data['total_colonies']}")
print(f"Original extractions: {corrected_data['original_extraction_count']}")
print()
print("Major fixes:")
print("  - BAHAMA ISLANDS: merged 3 subsections")
print("  - GOLD COAST: merged 3 entries")
print("  - LEEWARD ISLANDS: merged 4 sub-entries")
print("  - TRINIDAD: merged 4 entries")
print("  - Removed FALKLAND ISLANDS COMPANY")
print("  - Post-WWII effects: HONG KONG and NORTH BORNEO short entries")
print()
print(f"✅ Year 1946 manually verified and corrected")
print(f"✅ Corrected from 52 entries to {corrected_data['total_colonies']} proper colonies")
