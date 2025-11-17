#!/usr/bin/env python3
"""
Toponym Discovery Agent for years 1918-1927
Discovers ALL toponyms in source documents and compares against existing KG extractions
"""

import json
import os
import re
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set, Tuple

# Years to process
YEARS = [1918, 1919, 1921, 1922, 1923, 1924, 1925, 1927]

# Toponym patterns to identify
TOPONYM_PATTERNS = {
    'island': r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+Island\b',
    'islands': r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+Islands\b',
    'river': r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+River\b',
    'mountain': r'\b(?:Mount|Mt\.)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b',
    'mountains': r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+Mountains\b',
    'bay': r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+Bay\b',
    'harbor': r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+Harbo[u]?r\b',
    'harbour': r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+Harbour\b',
    'district': r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+District\b',
    'parish': r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+Parish\b',
    'province': r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+Province\b',
    'territory': r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+Territory\b',
    'protectorate': r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+Protectorate\b',
    'colony': r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+Colony\b',
    'cape': r'\b(?:Cape)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b',
    'point': r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+Point\b',
    'town': r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+Town\b',
    'city': r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+City\b',
    'fort': r'\b(?:Fort)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b',
    'port': r'\b(?:Port)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b',
    'lake': r'\b(?:Lake)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b',
    'strait': r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+Strait\b',
    'straits': r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+Straits\b',
    'sound': r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+Sound\b',
    'channel': r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+Channel\b',
    'peninsula': r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+Peninsula\b',
    'reef': r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+Reef\b',
    'valley': r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+Valley\b',
    'hill': r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+Hill\b',
    'hills': r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+Hills\b',
}

# Additional capitalized place names (cities, regions, etc.)
CAPITAL_PATTERN = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,3})\b'

# Generic terms to exclude
EXCLUDE_GENERIC = {
    'the', 'The', 'Governor', 'Government', 'Secretary', 'Chief', 'Officer',
    'Commissioner', 'Council', 'Colonial', 'Office', 'Department', 'Service',
    'British', 'His', 'Her', 'Majesty', 'King', 'Queen', 'Prince', 'Princess',
    'Lord', 'Lady', 'Sir', 'Honourable', 'Right', 'Most', 'Very', 'January',
    'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September',
    'October', 'November', 'December', 'Monday', 'Tuesday', 'Wednesday',
    'Thursday', 'Friday', 'Saturday', 'Sunday', 'Crown', 'Imperial', 'Royal',
    'Empire', 'Kingdom', 'Dominion', 'Commonwealth', 'Union', 'Republic',
    'State', 'National', 'Public', 'General', 'Special', 'Assistant',
    'Deputy', 'Acting', 'Superintendent', 'Inspector', 'Director', 'Manager',
    'Clerk', 'Accountant', 'Treasurer', 'Auditor', 'Surveyor', 'Engineer',
    'Medical', 'Education', 'Police', 'Military', 'Naval', 'Army', 'Navy',
    'Force', 'Regiment', 'Battalion', 'Company', 'Squadron', 'Division',
}


def load_existing_kg(year: int) -> Tuple[Dict, Set[str]]:
    """Load existing KG and extract all place names"""
    kg_path = Path(f"/home/user/colonial_office_list/knowledge_graph_extracts_v3/{year}_extracted.json")

    if not kg_path.exists():
        print(f"WARNING: No KG file for {year}")
        return {}, set()

    with open(kg_path, 'r', encoding='utf-8') as f:
        kg = json.load(f)

    # Extract all existing place names
    existing_places = set()

    # Handle new KG structure where entities is a dict with category keys
    entities_data = kg.get('entities', {})

    # If entities is a dict (new structure)
    if isinstance(entities_data, dict):
        # Get places specifically
        for entity in entities_data.get('places', []):
            if isinstance(entity, dict):
                name = entity.get('name', '')
                if name:
                    existing_places.add(name)
                    existing_places.add(name.lower())

        # Also check infrastructure as it may contain geographic features
        for entity in entities_data.get('infrastructure', []):
            if isinstance(entity, dict):
                name = entity.get('name', '')
                entity_type = entity.get('type', '')
                if name and entity_type in ['port', 'harbor', 'railway', 'road']:
                    existing_places.add(name)
                    existing_places.add(name.lower())

    # If entities is a list (old structure)
    elif isinstance(entities_data, list):
        for entity in entities_data:
            if isinstance(entity, dict):
                if entity.get('type') in ['colony', 'city', 'island', 'district', 'parish',
                                           'region', 'location', 'place', 'territory', 'protectorate',
                                           'province', 'town', 'port', 'fort', 'bay', 'harbor',
                                           'harbour', 'river', 'mountain', 'lake', 'cape']:
                    name = entity.get('name', '')
                    if name:
                        existing_places.add(name)
                        existing_places.add(name.lower())

    return kg, existing_places


def extract_toponyms_from_text(text: str, filename: str) -> List[Dict]:
    """Extract all toponyms from text using patterns"""
    toponyms = []
    lines = text.split('\n')

    for line_num, line in enumerate(lines, 1):
        # Skip empty lines and headers
        if not line.strip() or line.startswith('#'):
            continue

        # Apply each pattern
        for place_type, pattern in TOPONYM_PATTERNS.items():
            matches = re.finditer(pattern, line)
            for match in matches:
                name = match.group(0)  # Full match including type word
                base_name = match.group(1)  # Just the name part

                toponyms.append({
                    'name': name.strip(),
                    'base_name': base_name.strip(),
                    'type': place_type,
                    'source_file': filename,
                    'source_line': line_num,
                    'context': line.strip()
                })

    return toponyms


def extract_capitalized_places(text: str, filename: str, existing_places: Set[str]) -> List[Dict]:
    """Extract capitalized names that might be places (cities, regions)"""
    toponyms = []
    lines = text.split('\n')

    for line_num, line in enumerate(lines, 1):
        # Skip empty lines and headers
        if not line.strip() or line.startswith('#'):
            continue

        # Find capitalized words/phrases
        matches = re.finditer(CAPITAL_PATTERN, line)
        for match in matches:
            name = match.group(1).strip()

            # Filter out generic terms
            if name in EXCLUDE_GENERIC:
                continue

            # Filter out single letters
            if len(name) <= 1:
                continue

            # Check if likely a place (appears in context with location words)
            context_lower = line.lower()
            location_indicators = ['in ', 'at ', 'from ', 'to ', 'near ', 'of ',
                                   'colony', 'island', 'district', 'town', 'city',
                                   'port', 'settlement', 'station', 'post']

            has_location_context = any(ind in context_lower for ind in location_indicators)

            if has_location_context and name not in existing_places:
                toponyms.append({
                    'name': name,
                    'base_name': name,
                    'type': 'city_or_region',  # Inferred type
                    'source_file': filename,
                    'source_line': line_num,
                    'context': line.strip()
                })

    return toponyms


def process_year(year: int) -> Dict:
    """Process a single year - find all toponyms"""
    print(f"\n{'='*80}")
    print(f"Processing year {year}")
    print(f"{'='*80}")

    # Load existing KG
    kg, existing_places = load_existing_kg(year)
    print(f"Loaded KG with {len(existing_places)} existing places")

    # Read all source files
    source_dir = Path(f"/home/user/colonial_office_list/output_2/{year}_manual_parsed")
    if not source_dir.exists():
        print(f"WARNING: No source directory for {year}")
        return {}

    source_files = list(source_dir.glob("*.md"))
    print(f"Found {len(source_files)} source files")

    # Extract toponyms from all files
    all_toponyms = []
    for source_file in source_files:
        with open(source_file, 'r', encoding='utf-8') as f:
            text = f.read()

        # Extract structured toponyms (with type keywords)
        toponyms = extract_toponyms_from_text(text, source_file.name)
        all_toponyms.extend(toponyms)

        # Extract capitalized places
        cap_places = extract_capitalized_places(text, source_file.name, existing_places)
        all_toponyms.extend(cap_places)

    print(f"Extracted {len(all_toponyms)} total toponym mentions")

    # Deduplicate and filter
    unique_toponyms = {}
    for topo in all_toponyms:
        key = topo['name'].lower()
        if key not in existing_places:
            if key not in unique_toponyms:
                unique_toponyms[key] = topo

    print(f"Found {len(unique_toponyms)} NEW unique toponyms")

    # Convert to entity format
    new_entities = []
    for idx, (key, topo) in enumerate(sorted(unique_toponyms.items()), 1):
        entity = {
            "id": f"place_{year}_new_{idx:03d}",
            "name": topo['name'],
            "type": topo['type'],
            "parent_location": extract_parent_location(topo['source_file']),
            "description": topo['context'][:200] + "..." if len(topo['context']) > 200 else topo['context'],
            "year": year,
            "provenance": {
                "source_file": f"output_2/{year}_manual_parsed/{topo['source_file']}",
                "source_line": topo['source_line'],
                "extraction_confidence": 0.95 if topo['type'] != 'city_or_region' else 0.85,
                "extraction_agent": "toponym_discovery_1918_1927"
            }
        }
        new_entities.append(entity)

    # Save results
    output_file = f"/home/user/colonial_office_list/knowledge_graph_extracts_v3/{year}_extracted_toponyms.json"
    output_data = {
        "year": year,
        "extraction_date": "2025-11-17",
        "extraction_agent": "toponym_discovery_1918_1927",
        "total_new_toponyms": len(new_entities),
        "existing_places_count": len(existing_places),
        "entities": new_entities
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)

    print(f"Saved {len(new_entities)} new toponyms to {output_file}")

    return {
        "year": year,
        "new_toponyms": len(new_entities),
        "existing_places": len(existing_places),
        "entities": new_entities
    }


def extract_parent_location(filename: str) -> str:
    """Extract parent location from filename"""
    # Remove .md extension
    name = filename.replace('.md', '')
    # Replace underscores with spaces
    name = name.replace('_', ' ')
    # Title case
    return name.title()


def generate_report(results: Dict[int, Dict]):
    """Generate comprehensive report"""
    report_dir = Path("/home/user/colonial_office_list/reports/phase_c")
    report_dir.mkdir(parents=True, exist_ok=True)

    report_file = report_dir / "toponym_discovery_1918_1927.md"

    total_new = sum(r['new_toponyms'] for r in results.values())
    total_existing = sum(r['existing_places'] for r in results.values())

    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# Toponym Discovery Report: 1918-1927\n\n")
        f.write(f"**Generated:** 2025-11-17\n\n")
        f.write(f"**Agent:** toponym_discovery_1918_1927\n\n")
        f.write("## Executive Summary\n\n")
        f.write(f"- **Years Processed:** {len(results)}\n")
        f.write(f"- **Total New Toponyms Discovered:** {total_new}\n")
        f.write(f"- **Total Existing Places:** {total_existing}\n")
        if total_existing + total_new > 0:
            f.write(f"- **Coverage Increase:** {(total_new/(total_existing+total_new)*100):.1f}%\n\n")
        else:
            f.write(f"- **Coverage Increase:** N/A\n\n")

        f.write("## Results by Year\n\n")
        for year in sorted(results.keys()):
            r = results[year]
            f.write(f"### {year}\n\n")
            f.write(f"- Existing places in KG: {r['existing_places']}\n")
            f.write(f"- New toponyms discovered: {r['new_toponyms']}\n")
            f.write(f"- Output file: `knowledge_graph_extracts_v3/{year}_extracted_toponyms.json`\n\n")

            # Show top 20 toponyms by type
            if r['entities']:
                f.write(f"#### Sample New Toponyms (first 20)\n\n")
                type_counts = defaultdict(int)
                for entity in r['entities'][:20]:
                    f.write(f"- **{entity['name']}** ({entity['type']}) - {entity['parent_location']}\n")
                    type_counts[entity['type']] += 1

                f.write(f"\n#### Type Distribution (all)\n\n")
                for etype in sorted(type_counts.keys()):
                    full_count = sum(1 for e in r['entities'] if e['type'] == etype)
                    f.write(f"- {etype}: {full_count}\n")
                f.write("\n")

        f.write("## Methodology\n\n")
        f.write("1. Loaded existing KG for each year from `knowledge_graph_extracts_v3/{year}_extracted.json`\n")
        f.write("2. Extracted all existing place entities to avoid duplicates\n")
        f.write("3. Read ALL source files from `output_2/{year}_manual_parsed/`\n")
        f.write("4. Applied pattern matching for:\n")
        f.write("   - Islands, rivers, mountains, bays, harbors\n")
        f.write("   - Districts, parishes, provinces, territories\n")
        f.write("   - Cities, towns, ports, forts\n")
        f.write("   - Capes, points, straits, channels\n")
        f.write("   - Lakes, valleys, hills, reefs\n")
        f.write("5. Extracted capitalized names with location context\n")
        f.write("6. Filtered out generic terms and duplicates\n")
        f.write("7. Saved results with full provenance\n\n")

        f.write("## Files Generated\n\n")
        for year in sorted(results.keys()):
            f.write(f"- `knowledge_graph_extracts_v3/{year}_extracted_toponyms.json`\n")
        f.write("\n")

    print(f"\n{'='*80}")
    print(f"Report saved to {report_file}")
    print(f"{'='*80}")


def main():
    """Main processing function"""
    print("=" * 80)
    print("TOPONYM DISCOVERY AGENT: 1918-1927")
    print("=" * 80)

    results = {}
    for year in YEARS:
        try:
            result = process_year(year)
            results[year] = result
        except Exception as e:
            print(f"ERROR processing {year}: {e}")
            import traceback
            traceback.print_exc()

    # Generate report
    generate_report(results)

    print("\n" + "=" * 80)
    print("PROCESSING COMPLETE")
    print("=" * 80)
    print(f"Processed {len(results)} years")
    print(f"Total new toponyms: {sum(r['new_toponyms'] for r in results.values())}")


if __name__ == "__main__":
    main()
