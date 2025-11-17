#!/usr/bin/env python3
"""
Enhanced extraction for Colonial Office List 1930
Focuses on administrative records, people, institutions, and financial data
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
        "processing_notes": "Enhanced extraction focusing on administrative records, personnel, institutions, and economic data",
        "colonies_processed": [],
        "extraction_methodology": "Regex-based pattern matching with fallback to general entity detection"
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

# Tracking
entity_ids = defaultdict(int)
processed_people = set()
processed_places = set()

def gen_id(entity_type, name):
    """Generate unique ID for entities"""
    entity_ids[entity_type] += 1
    return f"{entity_type}_{entity_ids[entity_type]}"

def extract_titled_people(text):
    """Extract people with titles, positions, and salaries"""
    people = []

    # Enhanced pattern for administrative roles
    # Pattern matches: Title Name, Position, Salary
    patterns = [
        # Governor pattern: "Governor, Name, Title(s), Salary"
        r'(?:Governor|Governor-General|Lieutenant-Governor|High Commissioner),?\s+([A-Z][a-zA-Z\s\.]+?),?\s+([A-Z\.]{1,10}),?\s+(?:Rs\.|£|\$)\s*([\d,]+)',

        # Officer/Staff pattern: "Position, Name, Salary"
        r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*?),?\s+([A-Z][a-zA-Z\s\.]+?),?\s+(?:Rs\.|£|\$)\s*([\d,]+)',

        # Simple name pattern with salary
        r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*(?:Rs\.|£|\$)\s*([\d,]+)',
    ]

    # Extract administrative staff from structured sections
    sections = re.split(r'(?:###|###|Civil Establishment|Executive Council|Department|Office)', text)

    for section in sections:
        lines = section.split('\n')
        for i, line in enumerate(lines):
            # Skip empty lines and headers
            if len(line.strip()) < 3 or line.startswith('|') or '---' in line:
                continue

            # Match officer positions with salaries
            match = re.search(r'^([A-Za-z\s,\.]+?),?\s+([A-Z][a-zA-Z\s\.]+),?\s*(?:Rs\.|£|\$)\s*([\d,]+)', line)
            if match and not match.group(1).startswith('(') and not match.group(1).endswith('*'):
                position = match.group(1).strip().rstrip(',')
                name = match.group(2).strip()
                salary_str = match.group(3).replace(',', '')

                if len(name) > 3 and len(name) < 100 and name not in processed_people:
                    # Extract titles and honors
                    titles = re.findall(r'\b(Sir|Rev|Dr|Major|Capt|Lt|General|Colonel|Baron|Bishop|Right Rev|Rt Rev|Inspector|Director|Superintendent|Chief)\b', name)
                    honors = re.findall(r'\b([A-Z]{1,5}(?:\.[A-Z]{1,2})*)\b', name)

                    clean_name = re.sub(r'^\s*(?:Sir|Rev|Dr|Major|Capt|Lt|General|Colonel|Baron|Bishop|Right Rev|Rt Rev)\s+', '', name).strip()

                    person = {
                        "id": gen_id("person", clean_name),
                        "name": clean_name,
                        "titles": list(set(titles)),
                        "honors": [h for h in list(set(honors)) if len(h) > 1],
                        "positions": [{
                            "title": position,
                            "salary": {
                                "amount": float(salary_str),
                                "currency": "£" if "£" in line else "₹",
                                "period": "annual"
                            },
                            "status": "permanent",
                            "year": "1930"
                        }]
                    }
                    people.append(person)
                    processed_people.add(clean_name)

    return people

def extract_financial_data(text, location):
    """Extract revenue, expenditure, imports, exports"""
    economic = []

    # Financial tables with years
    table_pattern = r'\|\s*(?:Year|1[89]\d{2})\s*\|.*?Revenue.*?\|.*?\n((?:\|\s*\d{4}\s*\|.*?\n)*)'

    # Standalone financial figures
    figures = []

    # Revenue pattern
    revenue = re.search(r'[Rr]evenue.*?(?:Rs\.|£|\$)\s*([\d,]+)', text)
    if revenue:
        economic.append({
            "id": gen_id("economic_data", f"revenue_{location}"),
            "type": "revenue",
            "location": location,
            "year": "1930",
            "data": {
                "category": "Government Revenue",
                "value": float(revenue.group(1).replace(',', '')),
                "currency": "£" if "£" in revenue.group(0) else "₹"
            }
        })

    # Expenditure pattern
    expenditure = re.search(r'[Ee]xpenditure.*?(?:Rs\.|£|\$)\s*([\d,]+)', text)
    if expenditure:
        economic.append({
            "id": gen_id("economic_data", f"expenditure_{location}"),
            "type": "expenditure",
            "location": location,
            "year": "1930",
            "data": {
                "category": "Government Expenditure",
                "value": float(expenditure.group(1).replace(',', '')),
                "currency": "£" if "£" in expenditure.group(0) else "₹"
            }
        })

    # Trade data
    exports = re.findall(r'[Ee]xports?.*?(?:Rs\.|£|\$)\s*([\d,]+)', text)
    imports = re.findall(r'[Ii]mports?.*?(?:Rs\.|£|\$)\s*([\d,]+)', text)

    if exports:
        economic.append({
            "id": gen_id("economic_data", f"exports_{location}"),
            "type": "trade_export",
            "location": location,
            "year": "1930",
            "data": {
                "category": "Total Exports",
                "value": float(exports[0].replace(',', '')),
                "currency": "£" if "£" in exports[0] else "₹"
            }
        })

    if imports:
        economic.append({
            "id": gen_id("economic_data", f"imports_{location}"),
            "type": "trade_import",
            "location": location,
            "year": "1930",
            "data": {
                "category": "Total Imports",
                "value": float(imports[0].replace(',', '')),
                "currency": "£" if "£" in imports[0] else "₹"
            }
        })

    return economic

def extract_population_details(text, location):
    """Extract population and demographic breakdowns"""
    demographics = []

    # Census data pattern
    census_pattern = r'(?:Census|Population).*?(\d{4}).*?(\d+(?:,\d+)?)'
    census_matches = list(re.finditer(census_pattern, text, re.IGNORECASE))

    if census_matches:
        total_pop = None
        breakdowns = []

        # Find total population
        pop_match = re.search(r'(?:population|total).*?(\d+(?:,\d+)?)\s*(?:$|persons|inhabitants)', text, re.IGNORECASE | re.MULTILINE)
        if pop_match:
            total_pop = int(pop_match.group(1).replace(',', ''))

        # Extract demographic categories
        category_pattern = r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*\.+\s*(\d+(?:,\d+)?)'
        for match in re.finditer(category_pattern, text):
            category = match.group(1).strip()
            count = int(match.group(2).replace(',', ''))
            if len(category) < 100 and 10 < count < 10000000:
                breakdowns.append({
                    "category": category,
                    "count": count
                })

        if total_pop or breakdowns:
            demographics.append({
                "id": gen_id("demographics", location),
                "location": location,
                "year": "1930",
                "total_population": total_pop,
                "breakdowns": breakdowns[:10]  # Limit to 10 categories
            })

    return demographics

def extract_infrastructure_details(text, location):
    """Extract railways, telegraphs, docks, etc."""
    infrastructure = []

    # Railway data
    railway_pattern = r'(?:railway|rail).*?(\d+(?:\.\d+)?)\s*miles?'
    railways = re.findall(railway_pattern, text, re.IGNORECASE)
    for rail in railways[:5]:  # Max 5 railways
        infrastructure.append({
            "id": gen_id("infrastructure", f"railway_{location}"),
            "type": "railway",
            "name": f"Railway in {location}",
            "location": location,
            "specifications": {
                "length": {"value": float(rail), "unit": "miles"}
            },
            "year": "1930"
        })

    # Telegraph lines
    if re.search(r'[Tt]elegraph', text):
        telegraph_pattern = r'telegraph.*?(\d+)\s*miles?'
        telegraphs = re.findall(telegraph_pattern, text, re.IGNORECASE)
        if telegraphs:
            infrastructure.append({
                "id": gen_id("infrastructure", f"telegraph_{location}"),
                "type": "telegraph",
                "name": f"Telegraph system in {location}",
                "location": location,
                "specifications": {
                    "length": {"value": float(telegraphs[0]), "unit": "miles"}
                },
                "year": "1930"
            })

    # Harbors/Docks
    harbor_pattern = r'(?:harbour|harbor|port|dock).*?(?:(?:area|size)\s+)?(\d+)\s*(?:acres|feet|yards)'
    harbors = re.findall(harbor_pattern, text, re.IGNORECASE)
    if harbors:
        infrastructure.append({
            "id": gen_id("infrastructure", f"harbor_{location}"),
            "type": "harbor",
            "name": f"Harbor in {location}",
            "location": location,
            "year": "1930"
        })

    return infrastructure

def extract_geographic_entities(text, colony_name):
    """Extract places, cities, districts"""
    places = []

    # Add main colony
    colony_id = gen_id("place", colony_name)

    # Extract coordinates
    coord_pattern = r"(\d+°\s*\d+['′]?\s*[NSEW]\.?)\s+(?:and|,)\s+(\d+°\s*\d+['′]?\s*[NSEW]\.?)"
    coords_match = re.search(coord_pattern, text)

    coordinates = None
    if coords_match:
        coordinates = {
            "latitude": coords_match.group(1).strip(),
            "longitude": coords_match.group(2).strip()
        }

    # Extract area
    area_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:square\s+)?miles|(\d+(?:\.\d+)?)\s*acres', text, re.IGNORECASE)
    area = None
    if area_match:
        if area_match.group(1):
            area = {"value": float(area_match.group(1)), "unit": "square miles"}
        elif area_match.group(2):
            area = {"value": float(area_match.group(2)), "unit": "acres"}

    places.append({
        "id": colony_id,
        "name": colony_name,
        "type": "colony",
        "coordinates": coordinates,
        "area": area,
        "year": "1930"
    })

    if colony_name not in processed_places:
        processed_places.add(colony_name)

    # Extract cities/towns
    city_pattern = r'(?:city|town|capital)\s+(?:of\s+)?([A-Z][a-zA-Z\s]+?)(?:\s*(?:,|;|has|with|is)|$)'
    for match in re.finditer(city_pattern, text, re.IGNORECASE):
        city_name = match.group(1).strip()
        if 3 < len(city_name) < 50 and city_name not in processed_places:
            places.append({
                "id": gen_id("place", city_name),
                "name": city_name,
                "type": "city",
                "parent_location": colony_id,
                "year": "1930"
            })
            processed_places.add(city_name)

    # Extract districts
    district_pattern = r'(?:district|region|province|county)\s+(?:of\s+)?([A-Z][a-zA-Z\s]+?)(?:\s*(?:,|;|has|with|is)|$)'
    for match in re.finditer(district_pattern, text, re.IGNORECASE):
        district_name = match.group(1).strip()
        if 3 < len(district_name) < 50 and district_name not in processed_places:
            places.append({
                "id": gen_id("place", district_name),
                "name": district_name,
                "type": "district",
                "parent_location": colony_id,
                "year": "1930"
            })
            processed_places.add(district_name)

    return places, colony_id

def extract_institutions_detailed(text, location, colony_id):
    """Extract councils, courts, departments"""
    institutions = []

    # Council patterns
    councils = []
    if re.search(r'Executive Council', text):
        councils.append(("Executive Council", "executive_council"))
    if re.search(r'Legislative Council', text):
        councils.append(("Legislative Council", "legislative_council"))
    if re.search(r'Colonial Council', text):
        councils.append(("Colonial Council", "legislative_council"))
    if re.search(r'Privy Council', text):
        councils.append(("Privy Council", "privy_council"))

    for council_name, council_type in councils:
        institutions.append({
            "id": gen_id("institution", f"{location}_{council_type}"),
            "name": f"{location} {council_name}",
            "type": council_type,
            "location": location,
            "year": "1930"
        })

    # Court patterns
    courts = []
    if re.search(r'Supreme Court', text):
        courts.append(("Supreme Court", "court"))
    if re.search(r'Court of Magistrate', text):
        courts.append(("Magistrate Court", "court"))
    if re.search(r'Vice-Admiralty Court', text):
        courts.append(("Vice-Admiralty Court", "court"))

    for court_name, court_type in courts:
        institutions.append({
            "id": gen_id("institution", f"{location}_court"),
            "name": f"{location} {court_name}",
            "type": court_type,
            "location": location,
            "year": "1930"
        })

    # Departments
    departments = []
    if re.search(r'Colonial Secretary', text):
        departments.append("Colonial Secretary's Office")
    if re.search(r'Police', text, re.IGNORECASE):
        departments.append("Police Department")
    if re.search(r'(?:Public Works|PWD)', text):
        departments.append("Public Works Department")
    if re.search(r'(?:Medical|Health|Hospital)', text, re.IGNORECASE):
        departments.append("Medical Department")
    if re.search(r'(?:Education|School)', text, re.IGNORECASE):
        departments.append("Education Department")
    if re.search(r'Railway', text):
        departments.append("Railway Department")

    for dept_name in departments:
        institutions.append({
            "id": gen_id("institution", f"{location}_dept"),
            "name": f"{location} {dept_name}",
            "type": "department",
            "location": location,
            "year": "1930"
        })

    return institutions

def process_file(file_path, colony_name):
    """Process single colony file"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            text = f.read()

        places, colony_id = extract_geographic_entities(text, colony_name)
        people = extract_titled_people(text)
        economic = extract_financial_data(text, colony_name)
        infrastructure = extract_infrastructure_details(text, colony_name)
        demographics = extract_population_details(text, colony_name)
        institutions = extract_institutions_detailed(text, colony_name, colony_id)

        return {
            'places': places,
            'people': people,
            'economic_data': economic,
            'infrastructure': infrastructure,
            'demographics': demographics,
            'institutions': institutions,
            'colony_id': colony_id
        }
    except Exception as e:
        print(f"Error processing {colony_name}: {e}")
        return {
            'places': [],
            'people': [],
            'economic_data': [],
            'infrastructure': [],
            'demographics': [],
            'institutions': [],
            'colony_id': None
        }

def build_relationships(entities):
    """Build entity relationships"""
    relationships = []
    place_map = {p['name']: p['id'] for p in entities['places']}

    # PART_OF relationships
    for place in entities['places']:
        if place.get('parent_location'):
            relationships.append({
                "source_id": place['id'],
                "relationship_type": "PART_OF",
                "target_id": place['parent_location'],
                "properties": {"year": "1930"}
            })

    # GOVERNED_BY relationships
    for person in entities['people']:
        for position in person.get('positions', []):
            if position.get('salary'):
                for place in entities['places']:
                    if place.get('type') == 'colony':
                        relationships.append({
                            "source_id": person['id'],
                            "relationship_type": "GOVERNED_BY",
                            "target_id": place['id'],
                            "properties": {
                                "title": position.get('title', ''),
                                "year": "1930"
                            }
                        })
                        break

    # ADMINISTERS relationships
    for inst in entities['institutions']:
        if inst.get('location') in place_map:
            relationships.append({
                "source_id": inst['id'],
                "relationship_type": "ADMINISTERS",
                "target_id": place_map[inst['location']],
                "properties": {"year": "1930"}
            })

    return relationships

def main():
    """Main extraction"""
    source_dir = Path("/home/user/colonial_office_list/output_2/1930_manual_parsed/")
    colony_files = sorted(source_dir.glob("*.md"))

    print(f"Processing {len(colony_files)} colony files with enhanced extraction...")

    for file_path in colony_files:
        colony_name = file_path.stem.replace('_', ' ')
        print(f"  {colony_name}")

        result = process_file(file_path, colony_name)

        data['entities']['places'].extend(result['places'])
        data['entities']['people'].extend(result['people'])
        data['entities']['economic_data'].extend(result['economic_data'])
        data['entities']['infrastructure'].extend(result['infrastructure'])
        data['entities']['demographics'].extend(result['demographics'])
        data['entities']['institutions'].extend(result['institutions'])
        data['metadata']['colonies_processed'].append(colony_name)

    # Build relationships
    print("Building relationships...")
    data['relationships'] = build_relationships(data['entities'])

    # Output
    output_dir = Path("/home/user/colonial_office_list/knowledge_graph_extracts")
    output_dir.mkdir(exist_ok=True)
    output_file = output_dir / "1930_extracted.json"

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    # Report
    print(f"\n=== ENHANCED EXTRACTION COMPLETE ===")
    print(f"Colonies: {len(data['metadata']['colonies_processed'])}")
    print(f"Places: {len(data['entities']['places'])}")
    print(f"People: {len(data['entities']['people'])}")
    print(f"Institutions: {len(data['entities']['institutions'])}")
    print(f"Economic Data: {len(data['entities']['economic_data'])}")
    print(f"Infrastructure: {len(data['entities']['infrastructure'])}")
    print(f"Demographics: {len(data['entities']['demographics'])}")
    print(f"Relationships: {len(data['relationships'])}")
    print(f"Output: {output_file}")
    print(f"Size: {output_file.stat().st_size / 1024:.2f} KB")

if __name__ == "__main__":
    main()
