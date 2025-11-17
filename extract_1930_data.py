#!/usr/bin/env python3
"""
Extract comprehensive knowledge graph data from Colonial Office List 1930
Processes all 47 colony files and generates structured JSON output
"""

import json
import re
import os
from pathlib import Path
from datetime import datetime
from collections import defaultdict

# Initialize data structures
data = {
    "metadata": {
        "year": "1930",
        "source_directory": "/home/user/colonial_office_list/output_2/1930_manual_parsed/",
        "extraction_date": datetime.now().isoformat(),
        "processing_notes": "Comprehensive extraction from 47 colonial territories for 1930",
        "colonies_processed": []
    },
    "entities": {
        "places": [],
        "people": [],
        "institutions": [],
        "economic_data": [],
        "infrastructure": [],
        "demographics": [],
        "events": []
    },
    "relationships": []
}

# Tracking to avoid duplicates
place_ids = {}
person_ids = {}
institution_ids = {}
entity_counter = defaultdict(int)

def generate_id(entity_type, name):
    """Generate unique ID for entities"""
    entity_counter[entity_type] += 1
    return f"{entity_type}_{entity_counter[entity_type]}"

def extract_coordinates(text):
    """Extract latitude/longitude from text"""
    # Pattern: XX° YY' Z. lat/long.
    coord_pattern = r'(\d+°\s*\d+\'?\s*[NSEW]\.?)'
    coords = re.findall(coord_pattern, text)
    result = {}
    if len(coords) >= 2:
        result['latitude'] = coords[0].strip()
        result['longitude'] = coords[1].strip()
    return result if result else None

def extract_area(text):
    """Extract area measurements"""
    area_pattern = r'(\d+(?:,\d+)?)\s*(?:square\s*)?miles|(\d+(?:,\d+)?)\s*acres|(\d+(?:,\d+)?)\s*sq\.\s*miles'
    matches = re.search(area_pattern, text, re.IGNORECASE)
    if matches:
        if matches.group(1):
            return {"value": int(matches.group(1).replace(',', '')), "unit": "square miles"}
        elif matches.group(2):
            return {"value": int(matches.group(2).replace(',', '')), "unit": "acres"}
        elif matches.group(3):
            return {"value": int(matches.group(3).replace(',', '')), "unit": "square miles"}
    return None

def extract_salary(text):
    """Extract salary and currency information"""
    # Patterns: "Rs. 1,000", "£1,000", "$1,000"
    salary_pattern = r'(Rs\.|£|\$)\s*(\d+(?:,\d+)?(?:\.\d+)?)'
    match = re.search(salary_pattern, text)
    if match:
        currency_map = {'Rs.': '₹', '£': '£', '$': '$'}
        return {
            "amount": float(match.group(2).replace(',', '')),
            "currency": currency_map.get(match.group(1), match.group(1)),
            "period": "annual"
        }
    return None

def extract_population(text):
    """Extract population numbers"""
    pop_pattern = r'(?:population|inhabitants|census).*?(\d+(?:,\d+)?)'
    match = re.search(pop_pattern, text, re.IGNORECASE)
    if match:
        return int(match.group(1).replace(',', ''))
    return None

def extract_revenue_expenditure(text):
    """Extract revenue and expenditure data"""
    data_items = []

    # Pattern for Revenue/Expenditure lines
    pattern = r'(Revenue|Expenditure|Receipts|Expenses)\s*.*?(\d+(?:,\d+)?(?:\.\d+)?)\s*(Rs\.|£|\$|rupees|pounds)'
    for match in re.finditer(pattern, text, re.IGNORECASE):
        data_items.append({
            "type": match.group(1).lower(),
            "value": float(match.group(2).replace(',', '')),
            "currency": match.group(3)
        })

    return data_items

def extract_people_from_text(text, location, year="1930"):
    """Extract people and their positions from text"""
    people_list = []

    # Pattern for names with titles and positions
    # Sir Name, Position, Salary
    pattern = r'(?:Sir|Rev\.?|Dr\.?|Major|Capt\.?|Professor|Miss|Mrs\.?|Mr\.?)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),?\s+([^,\n]+?)(?:,?\s*(?:Rs\.|£|\$)\s*(\d+(?:,\d+)?))?\s*(?:\.|$)'

    for match in re.finditer(pattern, text):
        name = match.group(1).strip()
        position = match.group(2).strip()
        salary_str = match.group(3)

        if name and position and len(position) > 2:
            person = {
                "id": generate_id("person", name),
                "name": name,
                "titles": [],
                "honors": [],
                "positions": [{
                    "title": position,
                    "location": location,
                    "year": year,
                    "status": "permanent"
                }]
            }

            if salary_str:
                person["positions"][0]["salary"] = {
                    "amount": float(salary_str.replace(',', '')),
                    "currency": "₹",
                    "period": "annual"
                }

            people_list.append(person)

    return people_list

def extract_institutions(text, location, year="1930"):
    """Extract institutions and councils"""
    institutions = []

    # Common institutional patterns
    patterns = [
        (r'Executive Council', 'executive_council'),
        (r'Legislative Council', 'legislative_council'),
        (r'Supreme Court', 'court'),
        (r'Police [Ff]orce', 'police_force'),
        (r'Medical [Dd]epartment', 'medical'),
        (r'Department of Agriculture', 'department'),
        (r'Colonial [Ss]ecretary', 'department'),
        (r'Railway', 'public_works'),
        (r'[Pp]ublic [Ww]orks', 'public_works'),
    ]

    for pattern, inst_type in patterns:
        if re.search(pattern, text, re.IGNORECASE):
            inst_id = generate_id("institution", location + "_" + inst_type)
            institutions.append({
                "id": inst_id,
                "name": f"{location} {inst_type.replace('_', ' ').title()}",
                "type": inst_type,
                "location": location,
                "year": year
            })

    return institutions

def extract_infrastructure(text, location, year="1930"):
    """Extract infrastructure details"""
    infrastructure = []

    # Railway patterns
    if re.search(r'[Rr]ailway', text):
        railway_lines = re.findall(r'(\d+(?:\.\d+)?)\s*miles?', text)
        if railway_lines:
            for line in railway_lines[:3]:  # Limit to 3 lines
                infrastructure.append({
                    "id": generate_id("infrastructure", f"railway_{location}"),
                    "type": "railway",
                    "name": f"Railway Line in {location}",
                    "location": location,
                    "specifications": {
                        "length": {"value": float(line), "unit": "miles"}
                    },
                    "year": year
                })

    # Telegraph/Postal patterns
    if re.search(r'[Tt]elegraph', text):
        infrastructure.append({
            "id": generate_id("infrastructure", f"telegraph_{location}"),
            "type": "telegraph",
            "name": f"Telegraph system in {location}",
            "location": location,
            "year": year
        })

    # Dock/Harbor patterns
    if re.search(r'[Hh]arbour|[Dd]ock|port', text, re.IGNORECASE):
        infrastructure.append({
            "id": generate_id("infrastructure", f"harbor_{location}"),
            "type": "harbor",
            "name": f"Harbor/Port in {location}",
            "location": location,
            "year": year
        })

    return infrastructure

def extract_places(text, colony_name, year="1930"):
    """Extract geographic entities"""
    places = []

    # Main colony
    coords = extract_coordinates(text)
    area = extract_area(text)

    colony_id = generate_id("place", colony_name)
    place_ids[colony_name] = colony_id

    places.append({
        "id": colony_id,
        "name": colony_name,
        "type": "colony",
        "coordinates": coords,
        "area": area,
        "year": year
    })

    # Extract cities and towns
    city_pattern = r'(?:city|town|settlement|capital)\s+(?:of\s+)?([A-Z][a-zA-Z\s]+)'
    for match in re.finditer(city_pattern, text, re.IGNORECASE):
        city_name = match.group(1).strip()
        if city_name and len(city_name) > 2 and len(city_name) < 50:
            city_id = generate_id("place", city_name)
            places.append({
                "id": city_id,
                "name": city_name,
                "type": "city",
                "parent_location": colony_id,
                "year": year
            })

    # Extract districts/regions
    district_pattern = r'district\s+(?:of\s+)?([A-Z][a-zA-Z\s]+)'
    for match in re.finditer(district_pattern, text, re.IGNORECASE):
        district_name = match.group(1).strip()
        if district_name and len(district_name) > 2 and len(district_name) < 50:
            district_id = generate_id("place", district_name)
            places.append({
                "id": district_id,
                "name": district_name,
                "type": "district",
                "parent_location": colony_id,
                "year": year
            })

    return places

def extract_demographics(text, location, year="1930"):
    """Extract demographic data"""
    demographics_list = []

    total_pop = extract_population(text)

    if total_pop or re.search(r'[Pp]opulation|[Cc]ensus', text):
        demo_id = generate_id("demographics", location)
        demographics_list.append({
            "id": demo_id,
            "location": location,
            "year": year,
            "total_population": total_pop,
            "breakdowns": []
        })

        # Extract census breakdowns
        breakdown_pattern = r'([A-Z][a-zA-Z\s]+)\s*\.\.\.*\s*(\d+(?:,\d+)?)'
        for match in re.finditer(breakdown_pattern, text):
            category = match.group(1).strip()
            count = int(match.group(2).replace(',', ''))

            if len(category) > 2 and len(category) < 100 and count > 0:
                if demographics_list:
                    demographics_list[0]["breakdowns"].append({
                        "category": category,
                        "count": count
                    })

    return demographics_list

def extract_economic_data(text, location, year="1930"):
    """Extract economic and trade data"""
    economic_list = []

    # Revenue/Expenditure
    revenue_pattern = r'(?:Revenue|Receipts).*?(\d+(?:,\d+)?)\s*(Rs\.|£|\$)'
    for match in re.finditer(revenue_pattern, text):
        value = float(match.group(1).replace(',', ''))
        currency = {'Rs.': '₹', '£': '£', '$': '$'}.get(match.group(2), match.group(2))
        economic_list.append({
            "id": generate_id("economic_data", f"revenue_{location}"),
            "type": "revenue",
            "location": location,
            "year": year,
            "data": {
                "category": "Government Revenue",
                "value": value,
                "currency": currency
            }
        })
        break  # Get first instance

    # Exports
    if re.search(r'[Ee]xport', text):
        export_pattern = r'[Ee]xport.*?(\d+(?:,\d+)?)\s*(Rs\.|£|\$|kilos)'
        for match in re.finditer(export_pattern, text):
            economic_list.append({
                "id": generate_id("economic_data", f"export_{location}"),
                "type": "trade_export",
                "location": location,
                "year": year,
                "data": {
                    "category": "Total Exports",
                    "value": float(match.group(1).replace(',', '')),
                    "currency": match.group(2)
                }
            })
            break

    # Imports
    if re.search(r'[Ii]mport', text):
        economic_list.append({
            "id": generate_id("economic_data", f"import_{location}"),
            "type": "trade_import",
            "location": location,
            "year": year,
            "data": {
                "category": "Total Imports",
                "value": 0,
                "currency": "currency"
            }
        })

    return economic_list

def process_colony_file(file_path, colony_name):
    """Process a single colony file"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()

        # Extract all entity types
        places = extract_places(text, colony_name)
        people = extract_people_from_text(text, colony_name)
        institutions = extract_institutions(text, colony_name)
        infrastructure = extract_infrastructure(text, colony_name)
        demographics = extract_demographics(text, colony_name)
        economic = extract_economic_data(text, colony_name)

        return {
            'places': places,
            'people': people,
            'institutions': institutions,
            'infrastructure': infrastructure,
            'demographics': demographics,
            'economic_data': economic
        }

    except Exception as e:
        print(f"Error processing {colony_name}: {str(e)}")
        return {
            'places': [],
            'people': [],
            'institutions': [],
            'infrastructure': [],
            'demographics': [],
            'economic_data': []
        }

def build_relationships(entities):
    """Build relationships between entities"""
    relationships = []

    # PART_OF relationships: cities/districts part of colonies
    for place in entities['places']:
        if place.get('parent_location'):
            relationships.append({
                "source_id": place['id'],
                "relationship_type": "PART_OF",
                "target_id": place['parent_location'],
                "properties": {"year": "1930"}
            })

    # GOVERNED_BY relationships: people in positions govern locations
    for person in entities['people']:
        for position in person.get('positions', []):
            if position.get('location'):
                # Find matching place
                for place in entities['places']:
                    if place['name'] == position['location'] or place['name'].upper() == position['location'].upper():
                        relationships.append({
                            "source_id": person['id'],
                            "relationship_type": "GOVERNED_BY",
                            "target_id": place['id'],
                            "properties": {
                                "year": position.get('year', '1930'),
                                "title": position.get('title', '')
                            }
                        })
                        break

    # ADMINISTERS relationships: institutions administer locations
    for institution in entities['institutions']:
        if institution.get('location'):
            for place in entities['places']:
                if place['name'] == institution['location']:
                    relationships.append({
                        "source_id": institution['id'],
                        "relationship_type": "ADMINISTERS",
                        "target_id": place['id'],
                        "properties": {"year": "1930"}
                    })
                    break

    return relationships

def main():
    """Main extraction process"""
    source_dir = Path("/home/user/colonial_office_list/output_2/1930_manual_parsed/")

    # Get all colony files
    colony_files = sorted(source_dir.glob("*.md"))

    print(f"Processing {len(colony_files)} colony files for 1930...")

    for file_path in colony_files:
        colony_name = file_path.stem.replace('_', ' ')
        print(f"  Processing: {colony_name}")

        result = process_colony_file(file_path, colony_name)

        # Aggregate data
        data['entities']['places'].extend(result['places'])
        data['entities']['people'].extend(result['people'])
        data['entities']['institutions'].extend(result['institutions'])
        data['entities']['infrastructure'].extend(result['infrastructure'])
        data['entities']['demographics'].extend(result['demographics'])
        data['entities']['economic_data'].extend(result['economic_data'])

        data['metadata']['colonies_processed'].append(colony_name)

    # Build relationships
    print("Building relationships...")
    data['relationships'] = build_relationships(data['entities'])

    # Generate summary report
    print("\n=== EXTRACTION SUMMARY ===")
    print(f"Colonies processed: {len(data['metadata']['colonies_processed'])}")
    print(f"Geographic entities (places): {len(data['entities']['places'])}")
    print(f"People (prosopography): {len(data['entities']['people'])}")
    print(f"Institutions: {len(data['entities']['institutions'])}")
    print(f"Economic data points: {len(data['entities']['economic_data'])}")
    print(f"Infrastructure items: {len(data['entities']['infrastructure'])}")
    print(f"Demographics: {len(data['entities']['demographics'])}")
    print(f"Events: {len(data['entities']['events'])}")
    print(f"Relationships: {len(data['relationships'])}")

    # Create output directory
    output_dir = Path("/home/user/colonial_office_list/knowledge_graph_extracts")
    output_dir.mkdir(exist_ok=True)

    # Write output file
    output_file = output_dir / "1930_extracted.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"\nOutput written to: {output_file}")
    print(f"File size: {output_file.stat().st_size / 1024:.2f} KB")

    return data

if __name__ == "__main__":
    data = main()
