#!/usr/bin/env python3
"""
Extract comprehensive knowledge graph data from 1933 Colonial Office List files.
Follows the methodology defined in EXTRACTION_METHODOLOGY.md
"""

import json
import re
import os
from datetime import datetime
from pathlib import Path
from collections import defaultdict

# Configuration
SOURCE_DIR = Path("/home/user/colonial_office_list/output_2/1933_manual_parsed")
OUTPUT_DIR = Path("/home/user/colonial_office_list/knowledge_graph_extracts")
OUTPUT_FILE = OUTPUT_DIR / "1933_extracted.json"

# Global entity storage
entities = {
    "places": [],
    "people": [],
    "institutions": [],
    "economic_data": [],
    "infrastructure": [],
    "demographics": [],
    "events": []
}

relationships = []
entity_ids = {}  # Track created IDs for relationships
id_counter = defaultdict(int)  # Counter for each entity type

# Set to track processed entities (to avoid duplicates)
processed_places = set()
processed_people = set()
processed_institutions = set()

def generate_id(entity_type):
    """Generate unique ID for entity"""
    id_counter[entity_type] += 1
    return f"{entity_type}_{id_counter[entity_type]:04d}"

def extract_coordinates(text):
    """Extract latitude and longitude from text"""
    coords = {}
    # Pattern: lat. X° Y' direction, long. X° Y' direction
    lat_pattern = r'lat\.?\s+(\d+)°\s*(\d+)?\'?\s*([NSns])'
    long_pattern = r'long\.?\s+(\d+)°\s*(\d+)?\'?\s*([EWew])'

    lat_match = re.search(lat_pattern, text)
    long_match = re.search(long_pattern, text)

    if lat_match:
        coords["latitude"] = f"{lat_match.group(1)}° {lat_match.group(2) or '0'}' {lat_match.group(3)}"
    if long_match:
        coords["longitude"] = f"{long_match.group(1)}° {long_match.group(2) or '0'}' {long_match.group(3)}"

    return coords if coords else None

def extract_area(text):
    """Extract area measurements"""
    area_pattern = r'(\d+(?:,\d+)?(?:\.\d+)?)\s+(square miles|acres|sq\.?\s*miles?|sq\.?\s*ft|hectares)'
    matches = re.finditer(area_pattern, text, re.IGNORECASE)

    areas = []
    for match in matches:
        areas.append({
            "value": float(match.group(1).replace(",", "")),
            "unit": match.group(2)
        })
    return areas[0] if areas else None

def extract_people(text, location):
    """Extract people and their positions from text"""
    people_list = []

    # Pattern for titled persons with positions
    # E.g., "Governor, Sir John Smith, K.C.M.G."
    # E.g., "Postmaster, N. T. Bramble."
    # E.g., "Chief Secretary, A. B. Jones (salary £5,000)"

    person_pattern = r'([A-Za-z\s,]+?),\s*([A-Za-z\s\.]+?)(?:\s*\(|\s*,|\.)'
    lines = text.split('\n')

    for line in lines:
        # Skip lines that are clearly not person records
        if any(skip in line for skip in ['Distance', 'Area', 'Date', '19', '20', '|', '##']):
            continue

        # Pattern: Position title, Person name, honors/details
        if re.match(r'^[A-Z][a-z\s]+,\s+[A-Z]', line):
            parts = line.split(',', 2)
            if len(parts) >= 2:
                position = parts[0].strip()
                name_part = parts[1].strip()

                # Extract titles and honors
                titles = []
                honors = []
                name = name_part

                # Common honors
                honor_patterns = r'(K\.C\.M\.G\.|C\.B\.|G\.C\.B\.|K\.B\.E\.|C\.I\.E\.|O\.B\.E\.|D\.S\.O\.)'
                honor_matches = re.findall(honor_patterns, name)
                if honor_matches:
                    honors = honor_matches
                    name = re.sub(honor_patterns, '', name).strip()

                # Extract salary information
                salary_info = None
                if len(parts) > 2 and 'salary' in parts[2].lower():
                    salary_pattern = r'salary\s*£?(\d+(?:,\d+)*)'
                    salary_match = re.search(salary_pattern, parts[2], re.IGNORECASE)
                    if salary_match:
                        salary_info = {
                            "amount": int(salary_match.group(1).replace(",", "")),
                            "currency": "£",
                            "period": "annual"
                        }

                if name and len(name) > 1:
                    person = {
                        "id": generate_id("person"),
                        "name": name,
                        "titles": titles,
                        "honors": honors,
                        "positions": [{
                            "title": position,
                            "location": location,
                            "status": "permanent",
                            "year": "1933"
                        }]
                    }
                    if salary_info:
                        person["positions"][0]["salary"] = salary_info

                    # Check for duplicates
                    person_key = (name, location, position)
                    if person_key not in processed_people:
                        people_list.append(person)
                        processed_people.add(person_key)
                        entity_ids[(location, name, position)] = person["id"]

    return people_list

def extract_places_from_colony_file(colony_name, text):
    """Extract geographic entities from a single colony file"""
    places_list = []

    # Primary place: The colony itself
    colony_id = generate_id("place")

    # Extract area
    area = extract_area(text)

    # Extract coordinates
    coords = extract_coordinates(text)

    # Get first sentence as description
    first_sentence = re.match(r'^[^\.!?]+[\.!?]', text.strip())
    description = first_sentence.group(0) if first_sentence else ""

    colony_place = {
        "id": colony_id,
        "name": colony_name.replace("_", " "),
        "type": "colony",
        "year": "1933"
    }

    if coords:
        colony_place["coordinates"] = coords
    if area:
        colony_place["area"] = area
    if description:
        colony_place["description"] = description

    place_key = colony_name
    if place_key not in processed_places:
        places_list.append(colony_place)
        processed_places.add(place_key)
        entity_ids[colony_name] = colony_id

    # Extract secondary geographic features
    # Rivers, mountains, towns, harbors, etc.
    feature_patterns = [
        (r'([A-Z][a-zA-Z\s]+)\s+(?:river|River)', 'river'),
        (r'([A-Z][a-zA-Z\s]+)\s+(?:mountain|Mountain|peak|Peak)', 'mountain'),
        (r'(?:town|Town|city|City)\s+(?:of\s+)?([A-Z][a-zA-Z\s]+)', 'city'),
        (r'(?:harbour|harbor|Harbour|Harbor)\s+(?:of\s+)?([A-Z][a-zA-Z\s]+)', 'harbor'),
        (r'(?:bay|Bay)\s+(?:of\s+)?([A-Z][a-zA-Z\s]+)', 'bay'),
        (r'(?:island|Island)\s+(?:of\s+)?([A-Z][a-zA-Z\s]+)', 'island'),
    ]

    for pattern, feature_type in feature_patterns:
        matches = re.finditer(pattern, text)
        for match in matches:
            feature_name = match.group(1).strip()
            if len(feature_name) > 2 and feature_name not in processed_places:
                feature = {
                    "id": generate_id("place"),
                    "name": feature_name,
                    "type": feature_type,
                    "parent_location": colony_id,
                    "year": "1933"
                }
                places_list.append(feature)
                processed_places.add(feature_name)
                entity_ids[feature_name] = feature["id"]

    return places_list

def extract_population_data(colony_name, text):
    """Extract demographic information"""
    demographics_list = []

    # Look for census data
    census_pattern = r'[Cc]ensus\s+(?:of\s+)?(\d{4})[:\s]+([^.]+)'

    # Pattern for population tables
    pop_pattern = r'(?:population|Population)[:\s]+(\d+(?:,\d+)*)'

    census_matches = re.finditer(census_pattern, text)
    for match in census_matches:
        census_year = match.group(1)
        census_data = match.group(2)

        # Extract total population
        total_pop_match = re.search(r'(\d+(?:,\d+)*)', census_data)
        if total_pop_match:
            total_pop = int(total_pop_match.group(1).replace(",", ""))

            demo = {
                "id": generate_id("demographic"),
                "location": colony_name.replace("_", " "),
                "year": "1933",
                "census_date": census_year,
                "total_population": total_pop
            }
            demographics_list.append(demo)

    # Also look for direct population mentions
    pop_matches = re.finditer(pop_pattern, text)
    pop_found = False
    for match in pop_matches:
        if not pop_found:
            total_pop = int(match.group(1).replace(",", ""))
            # Try to extract census date
            census_year_match = re.search(r'(\d{4})\s+[Cc]ensus', text[:match.start()])
            census_year = census_year_match.group(1) if census_year_match else "1931"

            demo = {
                "id": generate_id("demographic"),
                "location": colony_name.replace("_", " "),
                "year": "1933",
                "census_date": census_year,
                "total_population": total_pop
            }
            demographics_list.append(demo)
            pop_found = True

    return demographics_list

def extract_economic_data(colony_name, text):
    """Extract economic information (revenue, exports, imports, etc.)"""
    economic_list = []

    # Revenue pattern: "Revenue ... £X" or "Rs. X"
    revenue_patterns = [
        (r'[Rr]evenue[^£Rs]*[£](\d+(?:,\d+)*)', '£'),
        (r'[Rr]evenue[^£Rs]*Rs\.?\s*(\d+(?:,\d+)*)', 'Rs'),
        (r'[Rr]evenue[^£Rs]*\$(\d+(?:,\d+)*)', '$'),
    ]

    for pattern, currency in revenue_patterns:
        matches = re.finditer(pattern, text)
        for match in matches:
            amount = int(match.group(1).replace(",", ""))
            economic = {
                "id": generate_id("economic_data"),
                "type": "revenue",
                "location": colony_name.replace("_", " "),
                "year": "1933",
                "data": {
                    "category": "Government Revenue",
                    "value": amount,
                    "currency": currency
                }
            }
            economic_list.append(economic)

    # Exports pattern
    export_pattern = r'[Ee]xports?[:\s]+[£$Rs\.]*(\d+(?:,\d+)*)[^\n]*?([a-zA-Z\s]+?)(?:\n|$)'
    matches = re.finditer(export_pattern, text)
    for match in matches:
        amount = int(match.group(1).replace(",", ""))
        commodity = match.group(2).strip() if len(match.group(2).strip()) < 50 else "commodities"
        economic = {
            "id": generate_id("economic_data"),
            "type": "trade_export",
            "location": colony_name.replace("_", " "),
            "year": "1933",
            "data": {
                "category": commodity,
                "value": amount,
                "currency": "£"
            }
        }
        economic_list.append(economic)

    return economic_list

def extract_institutions(colony_name, text):
    """Extract institutional entities"""
    institutions_list = []

    institution_patterns = [
        (r'[Ee]xecutive\s+[Cc]ouncil', 'executive_council'),
        (r'[Ll]egislative\s+[Cc]ouncil', 'legislative_council'),
        (r'[Ss]upreme\s+[Cc]ourt', 'court'),
        (r'[Dd]istrict\s+[Cc]ourt', 'court'),
        (r'[Pp]olice\s+[Cc]ourt', 'court'),
        (r'[Rr]oyal\s+[Cc]ollege', 'educational'),
        (r'[Cc]ivil\s+[Hh]ospital', 'medical'),
        (r'[Gg]overnment\s+[Hh]ospital', 'medical'),
        (r'[Tt]reasury', 'department'),
        (r'[Cc]olonial\s+[Ss]ecretary', 'department'),
        (r'[Dd]epartment\s+of\s+([A-Za-z\s]+)', 'department'),
    ]

    for pattern, inst_type in institution_patterns:
        matches = re.finditer(pattern, text)
        for match in matches:
            inst_name = match.group(0)
            if len(inst_name) > 3:
                inst = {
                    "id": generate_id("institution"),
                    "name": inst_name,
                    "type": inst_type,
                    "location": colony_name.replace("_", " "),
                    "year": "1933"
                }
                institutions_list.append(inst)

    return institutions_list

def extract_infrastructure(colony_name, text):
    """Extract infrastructure entities"""
    infrastructure_list = []

    infrastructure_patterns = [
        (r'([A-Za-z\s]+?)\s+[Rr]ailway(?:\s|,)', 'railway'),
        (r'([A-Za-z\s]+?)\s+[Rr]oad', 'road'),
        (r'([A-Za-z\s]+?)\s+[Dd]ock', 'dock'),
        (r'([A-Za-z\s]+?)\s+[Hh]arbour', 'harbor'),
        (r'([A-Za-z\s]+?)\s+[Tt]elegraph', 'telegraph'),
        (r'([A-Za-z\s]+?)\s+[Rr]eservoir', 'water_works'),
    ]

    for pattern, infra_type in infrastructure_patterns:
        matches = re.finditer(pattern, text)
        for match in matches:
            infra_name = match.group(1).strip()
            if len(infra_name) > 3 and len(infra_name) < 100:
                infra = {
                    "id": generate_id("infrastructure"),
                    "type": infra_type,
                    "name": infra_name,
                    "location": colony_name.replace("_", " "),
                    "year": "1933"
                }
                infrastructure_list.append(infra)

    return infrastructure_list

def extract_events(colony_name, text):
    """Extract historical events mentioned"""
    events_list = []

    # Look for dates and associated events
    event_pattern = r'(\d{1,2}(?:st|nd|rd|th)?)\s+([A-Za-z]+)\s+(\d{4})[:\s]+([^.]+\.)'

    matches = re.finditer(event_pattern, text)
    for match in matches:
        day = match.group(1)
        month = match.group(2)
        year = match.group(3)
        description = match.group(4).strip()

        event = {
            "id": generate_id("event"),
            "date": f"{day} {month} {year}",
            "description": description,
            "locations": [colony_name.replace("_", " ")],
            "year_mentioned": "1933",
            "type": "other"
        }
        events_list.append(event)

    # Look for establishment/cession dates
    establishment_pattern = r'(?:taken possession of|ceded|established|founded)[:\s]+([^.]+?)\b(\d{4})'
    matches = re.finditer(establishment_pattern, text)
    for match in matches:
        context = match.group(1).strip()
        year = match.group(2)

        event = {
            "id": generate_id("event"),
            "date": year,
            "description": f"{context} in {year}",
            "locations": [colony_name.replace("_", " ")],
            "year_mentioned": "1933",
            "type": "establishment" if "taken possession" in text[match.start()-20:match.start()] else "cession"
        }
        events_list.append(event)

    return events_list

def process_colony_file(filepath):
    """Process a single colony file and extract all data"""
    colony_name = filepath.stem

    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()
    except Exception as e:
        print(f"Error reading {filepath}: {e}")
        return

    # Extract all entity types
    places = extract_places_from_colony_file(colony_name, text)
    people = extract_people(text, colony_name.replace("_", " "))
    demographics = extract_population_data(colony_name, text)
    economic = extract_economic_data(colony_name, text)
    institutions = extract_institutions(colony_name, text)
    infrastructure = extract_infrastructure(colony_name, text)
    events = extract_events(colony_name, text)

    # Add to global storage
    entities["places"].extend(places)
    entities["people"].extend(people)
    entities["demographics"].extend(demographics)
    entities["economic_data"].extend(economic)
    entities["institutions"].extend(institutions)
    entities["infrastructure"].extend(infrastructure)
    entities["events"].extend(events)

def process_all_files():
    """Process all colony files in the 1933 directory"""
    files = sorted(SOURCE_DIR.glob("*.md"))

    print(f"Processing {len(files)} files from {SOURCE_DIR}")

    for i, filepath in enumerate(files, 1):
        print(f"  [{i}/{len(files)}] Processing {filepath.stem}...")
        process_colony_file(filepath)

    print(f"Extraction complete. Total entities:")
    print(f"  Places: {len(entities['places'])}")
    print(f"  People: {len(entities['people'])}")
    print(f"  Demographics: {len(entities['demographics'])}")
    print(f"  Economic data: {len(entities['economic_data'])}")
    print(f"  Institutions: {len(entities['institutions'])}")
    print(f"  Infrastructure: {len(entities['infrastructure'])}")
    print(f"  Events: {len(entities['events'])}")

def build_relationships():
    """Build relationships between entities"""
    global relationships
    relationships = []

    # PART_OF relationships: cities/features in colonies
    for place in entities["places"]:
        if place["type"] != "colony" and "parent_location" in place:
            relationships.append({
                "source_id": place["id"],
                "relationship_type": "PART_OF",
                "target_id": place["parent_location"],
                "properties": {"year": "1933"}
            })

    # GOVERNED_BY relationships: people in colonies
    for person in entities["people"]:
        for position in person.get("positions", []):
            location = position.get("location", "")
            # Find colony
            for place in entities["places"]:
                if place["name"] == location and place["type"] == "colony":
                    relationships.append({
                        "source_id": person["id"],
                        "relationship_type": "GOVERNED_BY",
                        "target_id": place["id"],
                        "properties": {"year": "1933", "position": position.get("title", "")}
                    })

    # LOCATED_IN relationships: demographics
    for demo in entities["demographics"]:
        location = demo.get("location", "")
        for place in entities["places"]:
            if place["name"] == location and place["type"] == "colony":
                relationships.append({
                    "source_id": demo["id"],
                    "relationship_type": "LOCATED_IN",
                    "target_id": place["id"],
                    "properties": {"year": "1933"}
                })

    # ADMINISTERS relationships: institutions
    for inst in entities["institutions"]:
        location = inst.get("location", "")
        for place in entities["places"]:
            if place["name"] == location and place["type"] == "colony":
                relationships.append({
                    "source_id": inst["id"],
                    "relationship_type": "ADMINISTERS",
                    "target_id": place["id"],
                    "properties": {"year": "1933"}
                })

def generate_output():
    """Generate final JSON output"""
    output = {
        "metadata": {
            "year": "1933",
            "source_directory": str(SOURCE_DIR),
            "extraction_date": datetime.now().isoformat(),
            "processing_notes": "Comprehensive extraction of geographic entities, people, institutions, economic data, infrastructure, and demographics from 1933 Colonial Office List. Preserves historical spelling and terminology.",
            "colonies_processed": sorted([f.stem for f in SOURCE_DIR.glob("*.md")])
        },
        "entities": entities,
        "relationships": relationships
    }

    return output

def main():
    """Main execution"""
    print("=" * 70)
    print("1933 Colonial Office List - Knowledge Graph Extraction")
    print("=" * 70)

    # Process all files
    process_all_files()

    # Build relationships
    print("\nBuilding entity relationships...")
    build_relationships()
    print(f"  Total relationships: {len(relationships)}")

    # Generate output
    print("\nGenerating JSON output...")
    output = generate_output()

    # Write to file
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\nOutput written to: {OUTPUT_FILE}")

    # Print summary
    print("\n" + "=" * 70)
    print("EXTRACTION SUMMARY FOR 1933")
    print("=" * 70)
    print(f"Colonies Processed: {len(output['metadata']['colonies_processed'])}")
    print(f"  {', '.join(output['metadata']['colonies_processed'][:5])}...")
    print(f"\nEntity Counts by Type:")
    print(f"  Geographic Places: {len(entities['places'])}")
    print(f"  People (with positions): {len(entities['people'])}")
    print(f"  Institutions: {len(entities['institutions'])}")
    print(f"  Economic Data Records: {len(entities['economic_data'])}")
    print(f"  Infrastructure: {len(entities['infrastructure'])}")
    print(f"  Demographics: {len(entities['demographics'])}")
    print(f"  Historical Events: {len(entities['events'])}")
    print(f"\nTotal Entities: {sum(len(v) for v in entities.values())}")
    print(f"Total Relationships: {len(relationships)}")
    print(f"\nOutput File: {OUTPUT_FILE}")
    print("=" * 70)

if __name__ == "__main__":
    main()
