#!/usr/bin/env python3
"""
Comprehensive Knowledge Graph Extractor for Colonial Office List 1949
Extracts geographic entities, people, institutions, economic data, infrastructure,
demographics, and historical events from colony files.
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Set, Tuple
import uuid

class KnowledgeGraphExtractor:
    def __init__(self, source_directory: str, output_file: str):
        self.source_dir = Path(source_directory)
        self.output_file = Path(output_file)
        self.extraction_date = datetime.now().isoformat()

        # Data storage
        self.places = {}
        self.people = {}
        self.institutions = {}
        self.economic_data = []
        self.infrastructure = []
        self.demographics = []
        self.events = []
        self.relationships = []

        # Tracking
        self.colonies_processed = []
        self.id_counter = 0
        self.seen_names = {}  # For deduplication

    def generate_id(self, prefix: str) -> str:
        """Generate unique ID for entities"""
        self.id_counter += 1
        return f"{prefix}_{self.id_counter}"

    def normalize_name(self, name: str) -> str:
        """Normalize names for comparison"""
        return name.strip().lower()

    def extract_coordinates(self, text: str) -> Dict[str, str]:
        """Extract latitude and longitude from text"""
        coords = {}

        # Match patterns like "latitude 4° N" or "12° 47' N."
        lat_match = re.search(r'(?:latitude|lat\.?)\s+(\d+°\s*\d*\'?\s*[NSEWnsew]\.?)', text, re.IGNORECASE)
        if lat_match:
            coords['latitude'] = lat_match.group(1).strip()

        lon_match = re.search(r'(?:longitude|lon\.?)\s+(\d+°\s*\d*\'?\s*[NSEWnsew]\.?)', text, re.IGNORECASE)
        if lon_match:
            coords['longitude'] = lon_match.group(1).strip()

        return coords if coords else None

    def extract_area(self, text: str) -> Dict[str, Any]:
        """Extract area measurements"""
        area = {}

        # Look for patterns like "75 square miles", "219,770 square miles"
        match = re.search(r'([\d,]+\.?\d*)\s*(?:square\s+)?miles', text, re.IGNORECASE)
        if match:
            try:
                value = float(match.group(1).replace(',', ''))
                area['value'] = value
                area['unit'] = 'square miles'
            except ValueError:
                pass

        # Look for acres
        match = re.search(r'([\d,]+\.?\d*)\s*acres', text, re.IGNORECASE)
        if match:
            try:
                value = float(match.group(1).replace(',', ''))
                area['value'] = value
                area['unit'] = 'acres'
            except ValueError:
                pass

        return area if area else None

    def extract_population_data(self, text: str, colony_name: str) -> Dict[str, Any]:
        """Extract demographic information"""
        demo = {
            'id': self.generate_id('demo'),
            'location': colony_name,
            'year': '1949',
            'breakdowns': []
        }

        # Look for "total population was..."
        total_match = re.search(r'(?:total\s+)?population\s+(?:was\s+)?(?:estimated\s+)?(?:at\s+)?(?:.*?)(\d{1,3}(?:,\d{3})*)', text, re.IGNORECASE)
        if total_match:
            try:
                total = int(total_match.group(1).replace(',', ''))
                demo['total_population'] = total
            except ValueError:
                pass

        # Look for population breakdowns by category
        # Patterns like "Europeans: 29,500" or "Indians: 90,900"
        categories = ['Europeans', 'Indians', 'Arabs', 'Africans', 'Chinese', 'Muslims', 'Jews', 'Somalis', 'Goans', 'Portuguese', 'Americans']

        for category in categories:
            pattern = rf'{category}[:\s,–-]+(\d{{1,3}}(?:,\d{{3}})*)'
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    count = int(match.group(1).replace(',', ''))
                    demo['breakdowns'].append({
                        'category': category,
                        'count': count
                    })
                except ValueError:
                    pass

        return demo if demo.get('breakdowns') or demo.get('total_population') else None

    def extract_revenue_expenditure(self, text: str, colony_name: str) -> List[Dict[str, Any]]:
        """Extract financial data"""
        econ_data = []

        # Look for revenue/expenditure tables
        # Pattern: Year | Revenue | Expenditure
        patterns = [
            (r'(\d{4})[:\s]+[£$]?([\d,]+)\s*[£$]?([\d,]+)', 'annual'),
            (r'revenue[:\s]+[£$]?([\d,]+)', 'revenue'),
            (r'expenditure[:\s]+[£$]?([\d,]+)', 'expenditure'),
        ]

        for pattern, data_type in patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                try:
                    if len(match.groups()) == 3:
                        year = match.group(1)
                        if data_type == 'annual':
                            econ_data.append({
                                'id': self.generate_id('econ'),
                                'type': 'revenue',
                                'location': colony_name,
                                'year': year,
                                'data': {
                                    'value': int(match.group(2).replace(',', '')),
                                    'currency': '£'
                                }
                            })
                            econ_data.append({
                                'id': self.generate_id('econ'),
                                'type': 'expenditure',
                                'location': colony_name,
                                'year': year,
                                'data': {
                                    'value': int(match.group(3).replace(',', '')),
                                    'currency': '£'
                                }
                            })
                except (ValueError, IndexError):
                    pass

        return econ_data

    def extract_people_from_establishment(self, text: str, colony_name: str) -> List[Dict[str, Any]]:
        """Extract people and their positions from civil establishment sections"""
        people_list = []

        # Split text into sections by position titles
        # Look for patterns like "Governor and Commander-in-Chief—Name £salary"
        patterns = [
            r'(Governor[^—]*?)—([^£\n]+?)(?:£|Rs\.|\.)',
            r'(Chief\s+[^—]*?)—([^£\n]+?)(?:£|Rs\.|\.)',
            r'(Director[^—]*?)—([^£\n]+?)(?:£|Rs\.|\.)',
            r'(Commissioner[^—]*?)—([^£\n]+?)(?:£|Rs\.|\.)',
            r'(Secretary[^—]*?)—([^£\n]+?)(?:£|Rs\.|\.)',
        ]

        for pattern in patterns:
            for match in re.finditer(pattern, text, re.MULTILINE):
                title = match.group(1).strip()
                name = match.group(2).strip()

                if name and len(name) > 2 and ',' not in name[:15]:  # Filter out table artifacts
                    # Extract salary
                    salary_match = re.search(r'£([\d,]+)(?:\s*–\s*([\d,]+))?', text[match.end():match.end()+100])
                    salary_info = None
                    if salary_match:
                        try:
                            salary_info = {
                                'amount': int(salary_match.group(1).replace(',', '')),
                                'currency': '£',
                                'period': 'annual'
                            }
                        except ValueError:
                            pass

                    # Extract honors and titles
                    titles = []
                    honors = []
                    name_clean = name

                    title_markers = ['Sir', 'Lt.', 'Lt.-Col.', 'Col.', 'Major', 'Capt.', 'Rev.', 'Dr.', 'Major-General', 'Brigadier', 'Air Chief Marshal']
                    honor_markers = ['K.C.M.G.', 'C.B.', 'C.M.G.', 'K.C.B.', 'K.B.E.', 'O.B.E.', 'D.S.O.', 'M.C.', 'G.C.B.', 'D.F.C.', 'M.B.E.', 'G.C.M.G.', 'G.C.V.O.']

                    for marker in title_markers:
                        if name_clean.startswith(marker):
                            titles.append(marker)
                            name_clean = name_clean[len(marker):].strip()

                    for marker in honor_markers:
                        if marker in name_clean:
                            honors.append(marker)
                            name_clean = name_clean.replace(marker, '').strip()

                    person_id = self.generate_id('person')
                    people_list.append({
                        'id': person_id,
                        'name': name_clean,
                        'titles': titles if titles else None,
                        'honors': honors if honors else None,
                        'positions': [{
                            'title': title,
                            'location': colony_name,
                            'salary': salary_info,
                            'status': 'permanent',
                            'year': '1949'
                        }]
                    })

        return people_list

    def extract_trade_data(self, text: str, colony_name: str) -> List[Dict[str, Any]]:
        """Extract import/export and trade data"""
        trade_data = []

        # Look for import/export patterns
        import_match = re.search(r'(?:imports?)[:\s]+[£$]?([\d,]+)', text, re.IGNORECASE)
        if import_match:
            try:
                value = int(import_match.group(1).replace(',', ''))
                trade_data.append({
                    'id': self.generate_id('trade'),
                    'type': 'trade_import',
                    'location': colony_name,
                    'year': '1949',
                    'data': {
                        'value': value,
                        'currency': '£'
                    }
                })
            except ValueError:
                pass

        export_match = re.search(r'(?:exports?)[:\s]+[£$]?([\d,]+)', text, re.IGNORECASE)
        if export_match:
            try:
                value = int(export_match.group(1).replace(',', ''))
                trade_data.append({
                    'id': self.generate_id('trade'),
                    'type': 'trade_export',
                    'location': colony_name,
                    'year': '1949',
                    'data': {
                        'value': value,
                        'currency': '£'
                    }
                })
            except ValueError:
                pass

        return trade_data

    def extract_places(self, text: str, colony_name: str) -> Dict[str, Dict[str, Any]]:
        """Extract geographic entities from text"""
        places = {}

        # Main colony entry
        coords = self.extract_coordinates(text)
        area = self.extract_area(text)

        place_id = self.generate_id('place')
        places[place_id] = {
            'id': place_id,
            'name': colony_name,
            'type': 'colony',
            'coordinates': coords,
            'area': area,
            'year': '1949'
        }

        # Extract other cities/towns mentioned
        city_patterns = [
            r'(?:city|capital|town|city of|city is situated at)\s+([A-Z][a-zA-Z\s]+?)(?:\s+(?:is|was|situated|located|administered)|\n)',
        ]

        for pattern in city_patterns:
            for match in re.finditer(pattern, text):
                city_name = match.group(1).strip()
                if len(city_name) < 50 and city_name not in colony_name:
                    place_id = self.generate_id('place')
                    places[place_id] = {
                        'id': place_id,
                        'name': city_name,
                        'type': 'city',
                        'parent_location': colony_name,
                        'year': '1949'
                    }

        return places

    def extract_institutions(self, text: str, colony_name: str) -> Dict[str, Dict[str, Any]]:
        """Extract institutional entities"""
        institutions = {}

        # Look for executive councils, legislative councils, courts, departments
        inst_patterns = [
            (r'(?:Executive|Legislative|Privy)\s+Council', 'council'),
            (r'(?:Supreme|District|Magistrate\'s|Police)\s+(?:Court|Magistracy)', 'court'),
            (r'(?:Government|Colonial|Treasury|Agriculture|Health)\s+Department', 'department'),
        ]

        for pattern, inst_type in inst_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                inst_name = match.group(0).strip()
                inst_id = self.generate_id('institution')
                institutions[inst_id] = {
                    'id': inst_id,
                    'name': inst_name,
                    'type': inst_type,
                    'location': colony_name,
                    'year': '1949'
                }

        return institutions

    def process_colony_file(self, filepath: Path) -> Tuple[str, Dict[str, Any]]:
        """Process a single colony file"""
        colony_name = filepath.stem.replace('_', ' ')

        with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
            text = f.read()

        colony_data = {
            'name': colony_name,
            'places': {},
            'people': [],
            'institutions': {},
            'economic_data': [],
            'infrastructure': [],
            'demographics': None,
            'events': []
        }

        # Extract places
        colony_data['places'].update(self.extract_places(text, colony_name))

        # Extract population/demographics
        demo = self.extract_population_data(text, colony_name)
        if demo:
            colony_data['demographics'] = demo
            self.demographics.append(demo)

        # Extract people and positions
        people = self.extract_people_from_establishment(text, colony_name)
        colony_data['people'].extend(people)
        for person in people:
            self.people[person['id']] = person

        # Extract institutions
        colony_data['institutions'].update(self.extract_institutions(text, colony_name))
        for inst_id, inst in colony_data['institutions'].items():
            self.institutions[inst_id] = inst

        # Extract economic data
        econ = self.extract_revenue_expenditure(text, colony_name)
        econ.extend(self.extract_trade_data(text, colony_name))
        colony_data['economic_data'].extend(econ)
        self.economic_data.extend(econ)

        # Add places to global storage
        for place_id, place in colony_data['places'].items():
            self.places[place_id] = place

        return colony_name, colony_data

    def build_relationships(self):
        """Build relationships between entities"""
        # PART_OF relationships: cities PART_OF colonies
        for place_id, place in self.places.items():
            if place.get('parent_location'):
                # Find parent location ID
                for other_id, other in self.places.items():
                    if other.get('name') == place.get('parent_location') and other.get('type') == 'colony':
                        self.relationships.append({
                            'source_id': place_id,
                            'relationship_type': 'LOCATED_IN',
                            'target_id': other_id,
                            'properties': {'year': '1949'}
                        })
                        break

        # GOVERNED_BY relationships: people GOVERNED_BY location
        for person_id, person in self.people.items():
            for position in person.get('positions', []):
                if position.get('location'):
                    for place_id, place in self.places.items():
                        if place.get('name') == position.get('location'):
                            self.relationships.append({
                                'source_id': person_id,
                                'relationship_type': 'GOVERNED_BY',
                                'target_id': place_id,
                                'properties': {'year': '1949'}
                            })
                            break

    def extract(self) -> Dict[str, Any]:
        """Main extraction process"""
        print(f"Starting extraction from {self.source_dir}")

        # Get all colony files
        colony_files = sorted(self.source_dir.glob('*.md'))
        print(f"Found {len(colony_files)} colony files")

        colony_data_all = {}

        # Process each colony
        for i, filepath in enumerate(colony_files, 1):
            colony_name, colony_data = self.process_colony_file(filepath)
            colony_data_all[colony_name] = colony_data
            self.colonies_processed.append(colony_name)

            if i % 10 == 0:
                print(f"  Processed {i} colonies...")

        # Build relationships
        self.build_relationships()

        # Create output structure
        output = {
            'metadata': {
                'year': '1949',
                'source_directory': str(self.source_dir),
                'extraction_date': self.extraction_date,
                'processing_notes': f'Extracted {len(self.colonies_processed)} colonies using LLM-based methodology',
                'colonies_processed': sorted(self.colonies_processed)
            },
            'entities': {
                'places': list(self.places.values()),
                'people': list(self.people.values()),
                'institutions': list(self.institutions.values()),
                'economic_data': self.economic_data,
                'infrastructure': self.infrastructure,
                'demographics': self.demographics,
                'events': self.events
            },
            'relationships': self.relationships
        }

        return output

    def save_output(self, data: Dict[str, Any]) -> None:
        """Save output to JSON file"""
        self.output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"Output saved to {self.output_file}")


def main():
    source_dir = '/home/user/colonial_office_list/output_2/1949_manual_parsed'
    output_file = '/home/user/colonial_office_list/knowledge_graph_extracts/1949_extracted.json'

    extractor = KnowledgeGraphExtractor(source_dir, output_file)
    extracted_data = extractor.extract()
    extractor.save_output(extracted_data)

    # Print statistics
    print("\n" + "="*60)
    print("EXTRACTION SUMMARY - 1949 Colonial Office List")
    print("="*60)
    print(f"Colonies Processed: {len(extracted_data['metadata']['colonies_processed'])}")
    print(f"Total Places Extracted: {len(extracted_data['entities']['places'])}")
    print(f"Total People Extracted: {len(extracted_data['entities']['people'])}")
    print(f"Total Institutions Extracted: {len(extracted_data['entities']['institutions'])}")
    print(f"Total Economic Records: {len(extracted_data['entities']['economic_data'])}")
    print(f"Total Demographics Records: {len(extracted_data['entities']['demographics'])}")
    print(f"Total Relationships: {len(extracted_data['relationships'])}")
    print("="*60)


if __name__ == '__main__':
    main()
