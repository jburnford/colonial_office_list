#!/usr/bin/env python3
"""
Toponym Quality Refinement Script
Filters and improves the quality of discovered toponyms for 1961-1966

This script:
1. Loads the raw toponym discoveries
2. Applies strict filtering for true geographic places
3. Removes false positives (companies, titles, sections)
4. Reclassifies place types accurately
5. Generates cleaned KG files
"""

import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set

BASE_DIR = Path("/home/user/colonial_office_list")
V3_DIR = BASE_DIR / "knowledge_graph_extracts_v3"
REPORT_DIR = BASE_DIR / "reports" / "phase_c"

YEARS = [1961, 1962, 1964, 1965, 1966]

# Strong geographic indicators - must have one of these
STRONG_GEO_TERMS = {
    'island', 'islands', 'isle', 'isles',
    'river', 'bay', 'harbor', 'harbour', 'gulf', 'strait', 'channel', 'sound',
    'mountain', 'mountains', 'mount', 'mt', 'hill', 'hills', 'peak', 'range',
    'lake', 'lagoon', 'pond',
    'cape', 'point', 'peninsula', 'headland',
    'colony', 'territory', 'protectorate', 'state',
    'town', 'city', 'village', 'port',
    'district', 'province', 'county', 'parish', 'division',
    'reef', 'atoll', 'cay', 'key',
}

# Known valid place names (actual colonies and territories)
VALID_PLACES = {
    'bermuda', 'british guiana', 'british honduras', 'british solomon islands',
    'brunei', 'falkland islands', 'fiji', 'gambia', 'gibraltar',
    'gilbert and ellice islands', 'hong kong', 'kenya', 'malta', 'mauritius',
    'new hebrides', 'northern rhodesia', 'north borneo', 'nyasaland',
    'sarawak', 'seychelles', 'sierra leone', 'singapore', 'st. helena',
    'tanganyika', 'tonga', 'uganda', 'virgin islands', 'zanzibar',
    'bahama islands', 'barbados', 'jamaica', 'trinidad', 'tobago',
    'aden', 'cyprus', 'nigeria', 'rhodesia', 'ascension', 'tristan da cunha',
    'pitcairn', 'somaliland', 'basutoland', 'swaziland', 'bechuanaland',
    'montserrat', 'grenada', 'st. lucia', 'st. vincent', 'antigua',
    'dominica', 'st. kitts', 'nevis', 'anguilla', 'turks', 'caicos',
    # Major cities and towns
    'london', 'hamilton', 'georgetown', 'belize', 'nairobi', 'kampala',
    'dar es salaam', 'mombasa', 'zanzibar town', 'freetown', 'bathurst',
    'valletta', 'port louis', 'victoria', 'suva', 'port of spain',
    'bridgetown', 'kingston', 'nassau', 'basseterre', 'roseau',
    # Geographic features
    'atlantic ocean', 'indian ocean', 'pacific ocean', 'caribbean sea',
    'mediterranean sea', 'red sea',
}

# Invalid patterns - definitely not toponyms
INVALID_PATTERNS = [
    r'^(Secretary|Minister|Governor|Commissioner|Director|Chief|Deputy|Assistant)',
    r'^(Department|Office|Ministry|Board|Council|Committee|Commission)',
    r'^(Government|Administration|Service|Agency)',
    r'^(British|English|Colonial|Royal|Crown|Imperial)',
    r'^(List|Order|Act|Law|Regulation|Ordinance)',
    r'^(Functions|Distribution|History)',
    r'(and|of|for|in|at|to|from|with)\s+(the|a|an)\s',
    r'Bank\s+of',
    r'(Ltd|Limited|Corporation|Company|Corp)',
    r'(Esq|Sir|Mr|Mrs|Miss|Dr|Rev|Hon)',
    r'^(January|February|March|April|May|June|July|August|September|October|November|December)',
    r'^\d+',  # Starts with number
]

def is_valid_toponym(place: Dict) -> bool:
    """Determine if a place entity is a valid toponym"""
    name = place['name'].strip()
    name_lower = name.lower()

    # Check if it's a known valid place
    if name_lower in VALID_PLACES:
        return True

    # Check if it matches invalid patterns
    for pattern in INVALID_PATTERNS:
        if re.search(pattern, name, re.IGNORECASE):
            return False

    # Check if it has strong geographic terms
    has_geo_term = any(term in name_lower for term in STRONG_GEO_TERMS)

    # Check if it has a valid geographic type
    has_valid_type = place.get('type') in {
        'colony', 'island', 'river', 'bay', 'mountain', 'lake',
        'town', 'city', 'district', 'province', 'county', 'parish',
        'territory', 'protectorate'
    }

    # Must have either strong geo term or valid type
    if not (has_geo_term or has_valid_type):
        return False

    # Additional validation: must have at least one uppercase letter
    # and be at least 3 characters
    if not any(c.isupper() for c in name) or len(name) < 3:
        return False

    # Must not be too long (probably not a real place name)
    if len(name) > 50:
        return False

    return True

def reclassify_place_type(place: Dict) -> str:
    """Improve place type classification"""
    name = place['name'].lower()

    # Colony/Territory
    if 'colony' in name or 'protectorate' in name or 'territory' in name:
        return 'colony'

    # Islands
    if 'island' in name or 'isle' in name or 'atoll' in name:
        return 'island'

    # Water bodies
    if any(term in name for term in ['river', 'bay', 'harbor', 'harbour', 'gulf', 'strait', 'channel', 'sound', 'ocean', 'sea']):
        if 'river' in name:
            return 'river'
        elif any(term in name for term in ['bay', 'harbor', 'harbour']):
            return 'bay'
        else:
            return 'water_body'

    # Mountains
    if any(term in name for term in ['mountain', 'mount', 'mt.', 'hill', 'peak', 'range']):
        return 'mountain'

    # Lakes
    if any(term in name for term in ['lake', 'lagoon', 'pond']):
        return 'lake'

    # Settlements
    if any(term in name for term in ['town', 'city', 'village', 'port']):
        if 'city' in name:
            return 'city'
        elif 'town' in name:
            return 'town'
        else:
            return 'settlement'

    # Administrative divisions
    if any(term in name for term in ['district', 'province', 'county', 'parish', 'division', 'region']):
        return 'administrative_division'

    # Check if it's a known colony
    if any(colony in name for colony in VALID_PLACES):
        return 'colony'

    return 'place'

def refine_toponyms_for_year(year: int) -> Dict:
    """Refine toponyms for a specific year"""
    print(f"\n{'='*80}")
    print(f"Refining toponyms for {year}")
    print('='*80)

    # Load raw toponyms file
    raw_file = V3_DIR / f"{year}_extracted_toponyms.json"

    if not raw_file.exists():
        print(f"Error: {raw_file} does not exist")
        return {}

    with open(raw_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    raw_places = data.get('entities', {}).get('places', [])
    print(f"Loaded {len(raw_places)} raw place entities")

    # Filter and refine
    refined_places = []
    filtered_out = 0

    for place in raw_places:
        if is_valid_toponym(place):
            # Reclassify type
            place['type'] = reclassify_place_type(place)
            refined_places.append(place)
        else:
            filtered_out += 1

    print(f"Valid toponyms: {len(refined_places)}")
    print(f"Filtered out: {filtered_out}")

    # Update data
    data['entities']['places'] = refined_places

    # Update metadata
    data['metadata']['refinement_date'] = datetime.now().isoformat()
    data['metadata']['toponyms_before_refinement'] = len(raw_places)
    data['metadata']['toponyms_after_refinement'] = len(refined_places)
    data['metadata']['toponyms_filtered_out'] = filtered_out

    # Save refined file
    refined_file = V3_DIR / f"{year}_extracted_toponyms.json"
    with open(refined_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"Saved refined file: {refined_file}")

    return {
        'year': year,
        'raw_count': len(raw_places),
        'refined_count': len(refined_places),
        'filtered_out': filtered_out,
        'retention_rate': (len(refined_places) / len(raw_places) * 100) if raw_places else 0
    }

def generate_refinement_report(results: List[Dict]):
    """Generate refinement quality report"""
    report_lines = []
    report_lines.append("# Toponym Quality Refinement Report")
    report_lines.append("")
    report_lines.append(f"**Report Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append("")
    report_lines.append("## Overview")
    report_lines.append("")
    report_lines.append("This report documents the quality refinement process applied to the")
    report_lines.append("discovered toponyms, removing false positives and improving type classification.")
    report_lines.append("")

    # Summary table
    report_lines.append("## Summary by Year")
    report_lines.append("")
    report_lines.append("| Year | Raw Count | Refined Count | Filtered Out | Retention Rate |")
    report_lines.append("|------|-----------|---------------|--------------|----------------|")

    for result in results:
        report_lines.append(f"| {result['year']} | {result['raw_count']} | "
                          f"{result['refined_count']} | {result['filtered_out']} | "
                          f"{result['retention_rate']:.1f}% |")

    report_lines.append("")

    # Total summary
    total_raw = sum(r['raw_count'] for r in results)
    total_refined = sum(r['refined_count'] for r in results)
    total_filtered = sum(r['filtered_out'] for r in results)

    report_lines.append("## Total Across All Years")
    report_lines.append("")
    report_lines.append(f"- **Raw Toponyms:** {total_raw}")
    report_lines.append(f"- **Refined Toponyms:** {total_refined}")
    report_lines.append(f"- **Filtered Out:** {total_filtered}")
    report_lines.append(f"- **Overall Retention Rate:** {(total_refined / total_raw * 100):.1f}%")
    report_lines.append("")

    # Quality criteria
    report_lines.append("## Quality Criteria Applied")
    report_lines.append("")
    report_lines.append("### Inclusion Criteria")
    report_lines.append("")
    report_lines.append("Toponyms were kept if they met ANY of the following:")
    report_lines.append("")
    report_lines.append("1. **Known Valid Places:** Match list of known colonies and territories")
    report_lines.append("2. **Strong Geographic Terms:** Contains terms like Island, River, Bay, Colony, etc.")
    report_lines.append("3. **Valid Geographic Type:** Classified as colony, island, river, bay, mountain, etc.")
    report_lines.append("")

    report_lines.append("### Exclusion Criteria")
    report_lines.append("")
    report_lines.append("Toponyms were filtered out if they matched ANY of the following:")
    report_lines.append("")
    report_lines.append("1. **Administrative Titles:** Secretary, Minister, Governor, Commissioner, etc.")
    report_lines.append("2. **Departments:** Department, Office, Ministry, Board, Council, etc.")
    report_lines.append("3. **Company Names:** Contains Ltd, Limited, Corporation, Bank of, etc.")
    report_lines.append("4. **Document Sections:** Functions, Distribution, History, List of, etc.")
    report_lines.append("5. **Generic Terms:** British, Colonial, Royal, Government, etc.")
    report_lines.append("6. **Too Long:** Names over 50 characters")
    report_lines.append("7. **Too Short:** Names under 3 characters")
    report_lines.append("")

    report_lines.append("## Type Reclassification")
    report_lines.append("")
    report_lines.append("Place types were improved using the following logic:")
    report_lines.append("")
    report_lines.append("- **colony:** Contains 'colony', 'protectorate', 'territory', or is a known colony")
    report_lines.append("- **island:** Contains 'island', 'isle', 'atoll'")
    report_lines.append("- **river:** Contains 'river'")
    report_lines.append("- **bay:** Contains 'bay', 'harbor', 'harbour'")
    report_lines.append("- **mountain:** Contains 'mountain', 'mount', 'hill', 'peak', 'range'")
    report_lines.append("- **lake:** Contains 'lake', 'lagoon', 'pond'")
    report_lines.append("- **city/town:** Contains 'city' or 'town'")
    report_lines.append("- **administrative_division:** Contains 'district', 'province', 'county', 'parish'")
    report_lines.append("")

    # Save report
    report_file = REPORT_DIR / "toponym_refinement_1961_1966.md"
    with open(report_file, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report_lines))

    print(f"\nGenerated refinement report: {report_file}")

def main():
    """Main execution"""
    print("="*80)
    print("TOPONYM QUALITY REFINEMENT - 1961-1966")
    print("="*80)

    results = []

    for year in YEARS:
        result = refine_toponyms_for_year(year)
        if result:
            results.append(result)

    # Generate report
    print(f"\n{'='*80}")
    print("Generating Refinement Report")
    print('='*80)
    generate_refinement_report(results)

    print(f"\n{'='*80}")
    print("REFINEMENT COMPLETE")
    print('='*80)

if __name__ == '__main__':
    main()
