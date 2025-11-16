#!/usr/bin/env python3
"""
Colonial Office List 1924 - Comprehensive Knowledge Graph Extraction
Extracts all entities and relationships from 49 colonies/territories
"""

import json
import re
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple, Set
import glob

class ColonialOfficeExtractor:
    def __init__(self, source_dir: str, output_dir: str):
        self.source_dir = Path(source_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Data structures
        self.entities = {
            'places': [],
            'people': [],
            'institutions': [],
            'economic_data': [],
            'infrastructure': [],
            'demographics': [],
            'events': []
        }
        self.relationships = []
        self.colonies_processed = []
        self.id_counters = {}
        self.person_map = {}  # For deduplication
        self.place_map = {}   # For deduplication

    def generate_id(self, prefix: str) -> str:
        """Generate unique IDs for entities"""
        if prefix not in self.id_counters:
            self.id_counters[prefix] = 0
        self.id_counters[prefix] += 1
        return f"{prefix}_{self.id_counters[prefix]:04d}"

    def extract_coordinates(self, text: str) -> Optional[Dict[str, str]]:
        """Extract latitude and longitude from text"""
        # Pattern: N. lat. 12° 47' (or lat. 12° 47')
        lat_pattern = r"(?:N\.|S\.)\s*(?:lat|latitude)[.:]?\s*([0-9]+°\s*[0-9]+'(?:\s*[0-9]+\")?)"
        long_pattern = r"(?:E\.|W\.)\s*(?:long|longitude)[.:]?\s*([0-9]+°\s*[0-9]+'(?:\s*[0-9]+\")?)"

        lat_match = re.search(lat_pattern, text, re.IGNORECASE)
        long_match = re.search(long_pattern, text, re.IGNORECASE)

        if lat_match or long_match:
            return {
                "latitude": lat_match.group(1).strip() if lat_match else None,
                "longitude": long_match.group(1).strip() if long_match else None
            }
        return None

    def extract_area(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract area measurements"""
        area_patterns = [
            (r"area\s+of\s+about\s+([0-9,]+(?:\.[0-9]+)?)\s+square\s+miles", "square miles"),
            (r"([0-9,]+(?:\.[0-9]+)?)\s+square\s+miles", "square miles"),
            (r"([0-9,]+(?:\.[0-9]+)?)\s+acres", "acres"),
            (r"area\s+of\s+about\s+([0-9,]+(?:\.[0-9]+)?)\s+sq\.\s+m", "square miles"),
        ]

        for pattern, unit in area_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    value = float(match.group(1).replace(',', ''))
                    return {"value": value, "unit": unit}
                except ValueError:
                    continue
        return None

    def extract_population(self, text: str) -> Optional[int]:
        """Extract population numbers"""
        patterns = [
            r"(?:total\s+)?population[:\s]+(?:about\s+)?([0-9,]+(?:\.[0-9]+)?)",
            r"population\s+of\s+(?:about\s+)?([0-9,]+(?:\.[0-9]+)?)",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    return int(match.group(1).replace(',', ''))
                except ValueError:
                    continue
        return None

    def extract_monetary_value(self, text: str) -> Optional[Tuple[float, str]]:
        """Extract monetary values and currency"""
        # Patterns for £ and $ with amounts
        patterns = [
            (r"([0-9,]+(?:\.[0-9]+)?)\s*l\.", "£"),
            (r"£\s*([0-9,]+(?:\.[0-9]+)?)", "£"),
            (r"\$\s*([0-9,]+(?:\.[0-9]+)?)", "$"),
            (r"([0-9,]+(?:\.[0-9]+)?)\s*dollars", "$"),
        ]

        for pattern, currency in patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    value = float(match.group(1).replace(',', ''))
                    return (value, currency)
                except ValueError:
                    continue
        return None

    def extract_people_from_text(self, text: str, colony: str) -> List[Dict[str, Any]]:
        """Extract person records from text"""
        people = []

        # Patterns for person entries
        # Format: Name, Title, Position, Salary
        person_pattern = r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:\s+[A-Z]\.)*),?\s+([A-Z\.]+[^,\n]*?),?\s*([0-9]+l\.?(?:\s+to\s+[0-9]+l\.)?)"

        for match in re.finditer(person_pattern, text):
            full_text = match.group(0)
            parts = full_text.split(',')

            if len(parts) >= 2:
                name = parts[0].strip()

                # Extract titles and honors
                titles = []
                honors = []

                # Common titles
                title_patterns = {
                    'titles': [r'\bSir\b', r'\bRev\b\.?', r'\bDr\b\.?', r'\bCapt\b\.?', r'\bCol\b\.?',
                              r'\bGeneral\b', r'\bMajor\b', r'\bLieut\b\.?', r'\bLord\b'],
                    'honors': [r'K\.C\.M\.G', r'C\.B\.?', r'G\.C\.B', r'O\.B\.E', r'M\.B\.E', r'M\.C',
                              r'C\.M\.G', r'K\.C', r'Kt\.?', r'Bart\.']
                }

                for title_pattern in title_patterns['titles']:
                    if re.search(title_pattern, full_text):
                        match_obj = re.search(title_pattern, full_text)
                        if match_obj:
                            titles.append(match_obj.group(0))

                for honor_pattern in title_patterns['honors']:
                    if re.search(honor_pattern, full_text):
                        match_obj = re.search(honor_pattern, full_text)
                        if match_obj:
                            honors.append(match_obj.group(0))

                # Extract salary
                salary_match = re.search(r"([0-9]+)l\.?(?:\s+to\s+([0-9]+)l\.)?", full_text)
                salary = None
                if salary_match:
                    salary = {
                        "amount": int(salary_match.group(1)),
                        "currency": "£",
                        "period": "annual"
                    }

                person_id = self.generate_id("person")
                person = {
                    "id": person_id,
                    "name": name,
                    "titles": titles,
                    "honors": honors,
                    "positions": [{
                        "title": parts[1].strip() if len(parts) > 1 else "",
                        "location": colony,
                        "salary": salary,
                        "status": "permanent",
                        "year": "1924"
                    }]
                }

                people.append(person)

        return people

    def extract_place_from_colony_name(self, colony_name: str) -> Dict[str, Any]:
        """Create a place entity for the colony itself"""
        place_id = f"place_{colony_name.replace(' ', '_').lower()}"

        # Map colony names to modern names where appropriate
        modern_names = {
            'CAPE_OF_GOOD_HOPE': 'Cape of Good Hope (South Africa)',
            'CEYLON': 'Sri Lanka',
            'HONG_KONG': 'Hong Kong',
            'PALESTINE': 'Palestine/Israel',
            'RHODESIA': 'Zimbabwe (Northern Rhodesia)',
            'NORTHERN_RHODESIA': 'Zambia',
            'SOUTH_WEST_AFRICA': 'Namibia',
            'SWAZILAND': 'Eswatini',
            'BASUTOLAND': 'Lesotho',
            'GOLD_COAST': 'Ghana',
            'BRITISH_GUIANA': 'Guyana',
            'BRITISH_HONDURAS': 'Belize',
            'STRAITS_SETTLEMENTS': 'Malaysia',
            'NEWFOUNDLAND': 'Newfoundland and Labrador (Canada)',
        }

        return {
            "id": place_id,
            "name": colony_name.replace('_', ' '),
            "modern_name": modern_names.get(colony_name),
            "type": "colony",
            "year": "1924"
        }

    def extract_from_file(self, filepath: Path) -> Tuple[str, Dict[str, Any]]:
        """Extract all data from a single colony file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        colony_name = filepath.stem
        extracted = {
            'colony': colony_name,
            'places': [],
            'people': [],
            'institutions': [],
            'economic_data': [],
            'infrastructure': [],
            'demographics': [],
            'events': [],
        }

        # Extract colony as main place
        colony_place = self.extract_place_from_colony_name(colony_name)
        extracted['places'].append(colony_place)

        # Extract geographic locations mentioned
        location_patterns = [
            r"(?:island|city|town|region|settlement|district|parish)\s+(?:of\s+)?([A-Z][a-z\s]+)",
            r"(?:Cape|Port|Bay|River|Mountain|Island)\s+([A-Z][a-z\s]+)"
        ]

        locations_found = set()
        for pattern in location_patterns:
            for match in re.finditer(pattern, content):
                loc_name = match.group(1).strip()
                if len(loc_name) > 2 and loc_name not in locations_found:
                    locations_found.add(loc_name)
                    place = {
                        "id": f"place_{len(extracted['places'])}",
                        "name": loc_name,
                        "type": "settlement" if "town" in match.group(0).lower() else "region",
                        "year": "1924"
                    }
                    extracted['places'].append(place)

        # Extract people from administrative sections
        # Split by department headers
        dept_sections = re.split(r'(?:###|##)\s+[A-Za-z\s]+\n', content)

        for section in dept_sections:
            people = self.extract_people_from_text(section, colony_name)
            extracted['people'].extend(people)

        # Extract population data
        pop_match = re.search(r"(?:census|population)[:\s]+([^.]+)", content, re.IGNORECASE)
        if pop_match:
            pop_text = pop_match.group(1)
            population = self.extract_population(pop_text)
            if population:
                demographic = {
                    "id": self.generate_id("demographic"),
                    "location": colony_name,
                    "year": "1924",
                    "total_population": population,
                    "breakdowns": []
                }
                extracted['demographics'].append(demographic)

        # Extract coordinates from first mention
        coords = self.extract_coordinates(content[:2000])  # Check first part
        if coords and extracted['places']:
            extracted['places'][0]['coordinates'] = coords

        # Extract area
        area = self.extract_area(content[:2000])
        if area and extracted['places']:
            extracted['places'][0]['area'] = area

        # Extract economic data from tables and text
        # Look for revenue/expenditure mentions
        econ_patterns = [
            (r"(?:revenue|receipts)[:\s]+([0-9,]+l\.)", "revenue"),
            (r"(?:expenditure|expenses)[:\s]+([0-9,]+l\.)", "expenditure"),
        ]

        for pattern, econ_type in econ_patterns:
            for match in re.finditer(pattern, content, re.IGNORECASE):
                value_str = match.group(1).replace('l.', '').replace(',', '')
                try:
                    value = float(value_str)
                    econ = {
                        "id": self.generate_id("economic"),
                        "type": econ_type,
                        "location": colony_name,
                        "year": "1924",
                        "data": {
                            "value": value,
                            "currency": "£"
                        }
                    }
                    extracted['economic_data'].append(econ)
                except ValueError:
                    pass

        # Extract infrastructure mentions
        infra_keywords = ['railway', 'telegraph', 'postal', 'dock', 'harbour', 'harbor', 'road', 'bridge']
        for keyword in infra_keywords:
            pattern = rf"{keyword}[s]?(?:\s+[a-z]+)*:\s*([^.]+)"
            for match in re.finditer(pattern, content, re.IGNORECASE):
                infra = {
                    "id": self.generate_id("infrastructure"),
                    "type": keyword,
                    "location": colony_name,
                    "year": "1924",
                    "name": match.group(1).strip()[:100]
                }
                extracted['infrastructure'].append(infra)

        # Extract historical events
        event_patterns = [
            r"(?:in\s+)?([0-9]{4})[,:]?\s+([^.]{20,150}[.!?])",
            r"(?:established|founded|ceded|captured)[^.]{10,150}[.!?]",
        ]

        for pattern in event_patterns:
            for match in re.finditer(pattern, content):
                event_text = match.group(0)
                if len(event_text) > 20:
                    event = {
                        "id": self.generate_id("event"),
                        "description": event_text[:200],
                        "year_mentioned": "1924"
                    }
                    extracted['events'].append(event)

        return colony_name, extracted

    def process_all_colonies(self):
        """Process all colony files for 1924"""
        colony_files = sorted(self.source_dir.glob("*.md"))

        for filepath in colony_files:
            try:
                colony_name, extracted = self.extract_from_file(filepath)
                self.colonies_processed.append(colony_name)

                # Merge into main entities
                self.entities['places'].extend(extracted['places'])
                self.entities['people'].extend(extracted['people'])
                self.entities['institutions'].extend(extracted['institutions'])
                self.entities['economic_data'].extend(extracted['economic_data'])
                self.entities['infrastructure'].extend(extracted['infrastructure'])
                self.entities['demographics'].extend(extracted['demographics'])
                self.entities['events'].extend(extracted['events'])

                print(f"✓ Processed {colony_name}")
            except Exception as e:
                print(f"✗ Error processing {filepath.stem}: {str(e)}")

    def build_relationships(self):
        """Build relationships between entities"""
        # Create relationships between colonies and their sub-locations
        for place in self.entities['places']:
            if place['type'] == 'colony':
                for other_place in self.entities['places']:
                    if other_place['type'] in ['settlement', 'region'] and other_place.get('location') == place['id']:
                        self.relationships.append({
                            "source_id": other_place['id'],
                            "relationship_type": "LOCATED_IN",
                            "target_id": place['id'],
                            "properties": {"year": "1924"}
                        })

        # Create relationships between people and their positions
        for person in self.entities['people']:
            for position in person.get('positions', []):
                location_id = f"place_{position.get('location', '').replace(' ', '_').lower()}"
                self.relationships.append({
                    "source_id": person['id'],
                    "relationship_type": "GOVERNED_BY",
                    "target_id": location_id,
                    "properties": {"year": "1924", "position": position.get('title')}
                })

    def generate_output(self) -> Dict[str, Any]:
        """Generate the final JSON structure"""
        output = {
            "metadata": {
                "year": "1924",
                "source_directory": str(self.source_dir),
                "extraction_date": datetime.utcnow().isoformat() + "Z",
                "processing_notes": f"Extracted from {len(self.colonies_processed)} colonies/territories. Data includes geographic entities, people, institutions, economic data, infrastructure, demographics, and historical events.",
                "colonies_processed": sorted(self.colonies_processed)
            },
            "entities": self.entities,
            "relationships": self.relationships
        }
        return output

    def save_output(self, output_path: Path):
        """Save extracted data to JSON file"""
        output = self.generate_output()
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        return output

def main():
    source_dir = "/home/user/colonial_office_list/output_2/1924_manual_parsed"
    output_dir = "/home/user/colonial_office_list/knowledge_graph_extracts"
    output_file = Path(output_dir) / "1924_extracted.json"

    extractor = ColonialOfficeExtractor(source_dir, output_dir)

    print("=" * 60)
    print("Colonial Office List 1924 - Knowledge Graph Extraction")
    print("=" * 60)
    print(f"\nProcessing {len(list(Path(source_dir).glob('*.md')))} colony files...\n")

    extractor.process_all_colonies()
    extractor.build_relationships()

    print(f"\nBuilding final output...")
    output = extractor.save_output(output_file)

    # Generate report
    print("\n" + "=" * 60)
    print("EXTRACTION SUMMARY - 1924")
    print("=" * 60)
    print(f"\nColonies Processed: {len(output['metadata']['colonies_processed'])}")
    print(f"\nEntity Counts:")
    print(f"  Places: {len(output['entities']['places'])}")
    print(f"  People: {len(output['entities']['people'])}")
    print(f"  Institutions: {len(output['entities']['institutions'])}")
    print(f"  Economic Data: {len(output['entities']['economic_data'])}")
    print(f"  Infrastructure: {len(output['entities']['infrastructure'])}")
    print(f"  Demographics: {len(output['entities']['demographics'])}")
    print(f"  Events: {len(output['entities']['events'])}")
    print(f"\nRelationships: {len(output['relationships'])}")
    print(f"\nOutput File: {output_file}")
    print(f"File Size: {output_file.stat().st_size:,} bytes")
    print("\n✓ Extraction complete!")

if __name__ == "__main__":
    main()
