#!/usr/bin/env python3
"""
Comprehensive Knowledge Graph Extraction for Colonial Office List 1908
Extracts structured data from all colony files following the schema.
"""

import json
import re
import os
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict

class ColonialOfficeExtractor:
    def __init__(self, source_dir: str, schema_path: str):
        self.source_dir = Path(source_dir)
        self.schema_path = Path(schema_path)
        self.entity_counter = defaultdict(int)

        # Initialize knowledge graph structure
        self.knowledge_graph = {
            "year": 1908,
            "source": "Colonial Office List 1908",
            "extraction_date": "2025-11-16",
            "entities": {
                "people": [],
                "places": [],
                "institutions": [],
                "events": [],
                "documents": []
            },
            "relationships": [],
            "statistics": {
                "economic_data": [],
                "demographic_data": [],
                "trade_data": [],
                "infrastructure_data": []
            }
        }

    def generate_entity_id(self, entity_type: str, name: str) -> str:
        """Generate unique entity ID"""
        self.entity_counter[entity_type] += 1
        # Clean name for ID
        clean_name = re.sub(r'[^a-zA-Z0-9]', '_', name)[:30]
        return f"1908_{entity_type}_{clean_name}_{self.entity_counter[entity_type]}"

    def extract_people(self, text: str, colony_name: str) -> List[Dict]:
        """Extract people with their titles, positions, salaries"""
        people = []

        # Pattern for people with titles and salaries
        # Examples: "Governor, Sir John Anderson, K.C.M.G., £6,000"
        patterns = [
            # Pattern with title, name, honors, salary
            r'(?P<position>[A-Z][a-zA-Z\s\-&,\.]+?),\s*(?P<name>(?:Sir|Hon\.|Rev\.|Dr\.|Captain|Major|Colonel|Lieutenant|Lieut\.|Lt\.)?\s*[A-Z][a-zA-Z\.\s\-\']+?),?\s*(?P<honors>[A-Z\.]+(?:,\s*[A-Z\.]+)*)?[,\s]*(?:£|[$])?\s*(?P<salary>[\d,]+)?',
        ]

        for line in text.split('\n'):
            line = line.strip()
            if not line:
                continue

            # Look for salary indicators
            if '£' in line or '$' in line or re.search(r'\d{2,4}l\.', line):
                # Try to extract person info
                for pattern in patterns:
                    match = re.search(pattern, line)
                    if match:
                        person = {
                            "id": "",
                            "name": match.group('name').strip() if match.group('name') else "",
                            "position": match.group('position').strip() if match.group('position') else "",
                            "honors": match.group('honors').strip() if match.group('honors') else "",
                            "salary": match.group('salary').strip() if match.group('salary') else "",
                            "colony": colony_name,
                            "source_line": line
                        }

                        if person['name']:
                            person['id'] = self.generate_entity_id('person', person['name'])
                            people.append(person)

        return people

    def extract_places(self, text: str, colony_name: str) -> List[Dict]:
        """Extract geographic entities with coordinates, areas, descriptions"""
        places = []

        # Pattern for coordinates
        coord_pattern = r'(?:lat\.|latitude)\s*(\d+°?\s*\d+\'?\s*[NS])'
        coord_pattern_long = r'(?:long\.|longitude)\s*(\d+°?\s*\d+\'?\s*[EW])'

        # Pattern for areas
        area_pattern = r'(?:area|containing)\s*(?:of)?\s*(\d+[\d,]*)\s*(square miles|sq\. miles|acres)'

        for line in text.split('\n'):
            # Extract coordinates
            lat_match = re.search(coord_pattern, line, re.IGNORECASE)
            lon_match = re.search(coord_pattern_long, line, re.IGNORECASE)

            if lat_match or lon_match:
                place = {
                    "id": "",
                    "name": colony_name,
                    "latitude": lat_match.group(1) if lat_match else "",
                    "longitude": lon_match.group(1) if lon_match else "",
                    "colony": colony_name,
                    "source_line": line.strip()
                }
                place['id'] = self.generate_entity_id('place', colony_name)
                places.append(place)

            # Extract areas
            area_match = re.search(area_pattern, line, re.IGNORECASE)
            if area_match:
                place = {
                    "id": self.generate_entity_id('place', colony_name + '_area'),
                    "name": colony_name,
                    "area": area_match.group(1),
                    "area_unit": area_match.group(2),
                    "colony": colony_name,
                    "source_line": line.strip()
                }
                places.append(place)

        return places

    def extract_institutions(self, text: str, colony_name: str) -> List[Dict]:
        """Extract institutions: councils, courts, departments"""
        institutions = []

        # Headers that indicate institutions
        inst_headers = [
            'Executive Council', 'Legislative Council', 'Supreme Court',
            'Department', 'Board', 'Commission', 'Office', 'Hospital',
            'School', 'College', 'Bank', 'Railway', 'Police', 'Constabulary',
            'Prison', 'Gaol', 'Asylum', 'Church'
        ]

        for line in text.split('\n'):
            for header in inst_headers:
                if header.lower() in line.lower() and len(line) < 100:
                    institution = {
                        "id": self.generate_entity_id('institution', header),
                        "name": line.strip(),
                        "type": header,
                        "colony": colony_name,
                        "source_line": line.strip()
                    }
                    institutions.append(institution)
                    break

        return institutions

    def extract_economic_data(self, text: str, colony_name: str) -> List[Dict]:
        """Extract revenue, expenditure, trade statistics"""
        economic_data = []

        # Pattern for revenue/expenditure
        patterns = [
            r'Revenue\s*[:\s]*£?\s*([\d,]+)',
            r'Expenditure\s*[:\s]*£?\s*([\d,]+)',
            r'Exports?\s*[:\s]*£?\s*([\d,]+)',
            r'Imports?\s*[:\s]*£?\s*([\d,]+)',
        ]

        for line in text.split('\n'):
            for pattern in patterns:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    data_type = pattern.split('\\s')[0]
                    data = {
                        "colony": colony_name,
                        "type": data_type,
                        "amount": match.group(1),
                        "currency": "£" if '£' in line or pattern.startswith('£') else "$",
                        "source_line": line.strip()
                    }
                    economic_data.append(data)

        return economic_data

    def extract_demographics(self, text: str, colony_name: str) -> List[Dict]:
        """Extract population statistics"""
        demographics = []

        # Pattern for population
        pop_patterns = [
            r'[Pp]opulation[:\s]*([\d,]+)',
            r'[Ii]nhabitants[:\s]*([\d,]+)',
            r'[Cc]ensus[:\s]*([\d,]+)',
        ]

        for line in text.split('\n'):
            for pattern in pop_patterns:
                match = re.search(pattern, line)
                if match:
                    data = {
                        "colony": colony_name,
                        "type": "population",
                        "count": match.group(1),
                        "source_line": line.strip()
                    }
                    demographics.append(data)
                    break

        return demographics

    def extract_from_file(self, file_path: Path) -> Dict:
        """Extract all data from a single colony file"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()

            colony_name = file_path.stem.replace('_', ' ').title()

            print(f"Processing: {colony_name}")

            # Extract different entity types
            people = self.extract_people(text, colony_name)
            places = self.extract_places(text, colony_name)
            institutions = self.extract_institutions(text, colony_name)
            economic_data = self.extract_economic_data(text, colony_name)
            demographics = self.extract_demographics(text, colony_name)

            return {
                "colony": colony_name,
                "people": people,
                "places": places,
                "institutions": institutions,
                "economic_data": economic_data,
                "demographics": demographics,
                "file_path": str(file_path)
            }

        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return {
                "colony": file_path.stem,
                "error": str(e),
                "file_path": str(file_path)
            }

    def process_all_files(self):
        """Process all colony files in the directory"""
        md_files = list(self.source_dir.glob('*.md'))

        # Filter out non-colony files
        exclude_patterns = ['APPENDIX', 'BISHOPS', 'COUNCIL', 'EXECUTIVE',
                          'LEGISLATIVE', 'MAIL', 'LANDS_FOR']

        colony_files = [
            f for f in md_files
            if not any(pattern in f.stem for pattern in exclude_patterns)
        ]

        print(f"Found {len(colony_files)} colony files to process")

        all_extractions = []

        for file_path in sorted(colony_files):
            extraction = self.extract_from_file(file_path)
            all_extractions.append(extraction)

            # Add to main knowledge graph
            if 'error' not in extraction:
                self.knowledge_graph['entities']['people'].extend(extraction.get('people', []))
                self.knowledge_graph['entities']['places'].extend(extraction.get('places', []))
                self.knowledge_graph['entities']['institutions'].extend(extraction.get('institutions', []))
                self.knowledge_graph['statistics']['economic_data'].extend(extraction.get('economic_data', []))
                self.knowledge_graph['statistics']['demographic_data'].extend(extraction.get('demographics', []))

        return all_extractions

    def save_results(self, output_path: str):
        """Save extraction results to JSON file"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.knowledge_graph, f, indent=2, ensure_ascii=False)

        print(f"\nKnowledge graph saved to: {output_path}")
        print(f"\nExtraction Statistics:")
        print(f"  People: {len(self.knowledge_graph['entities']['people'])}")
        print(f"  Places: {len(self.knowledge_graph['entities']['places'])}")
        print(f"  Institutions: {len(self.knowledge_graph['entities']['institutions'])}")
        print(f"  Economic Data Points: {len(self.knowledge_graph['statistics']['economic_data'])}")
        print(f"  Demographic Data Points: {len(self.knowledge_graph['statistics']['demographic_data'])}")


def main():
    source_dir = '/home/user/colonial_office_list/output_2/1908_manual_parsed'
    schema_path = '/home/user/colonial_office_list/json_schema_template.json'
    output_path = '/home/user/colonial_office_list/knowledge_graph_extracts/1908_extracted.json'

    extractor = ColonialOfficeExtractor(source_dir, schema_path)
    extractor.process_all_files()
    extractor.save_results(output_path)


if __name__ == '__main__':
    main()
