#!/usr/bin/env python3
"""
Comprehensive Knowledge Graph Extraction for Colonial Office List 1909
Extracts structured entities and relationships from all colony files.
"""

import json
import re
import glob
import os
from collections import defaultdict
from datetime import datetime

class KnowledgeGraphExtractor:
    def __init__(self, source_dir, schema_file):
        self.source_dir = source_dir
        self.schema = self.load_schema(schema_file)
        self.knowledge_graph = {
            "metadata": {
                "year": 1909,
                "source": "Colonial Office List 1909",
                "extraction_date": datetime.now().isoformat(),
                "files_processed": 0,
                "extraction_methodology": "See EXTRACTION_METHODOLOGY.md"
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
        self.entity_index = {}

    def load_schema(self, schema_file):
        """Load the JSON schema template."""
        with open(schema_file, 'r') as f:
            return json.load(f)

    def process_all_files(self):
        """Process all colony files in the source directory."""
        files = sorted(glob.glob(os.path.join(self.source_dir, "*.md")))
        print(f"Found {len(files)} colony files to process")

        for file_path in files:
            print(f"Processing: {os.path.basename(file_path)}")
            self.process_colony_file(file_path)

        self.knowledge_graph["metadata"]["files_processed"] = len(files)
        return self.knowledge_graph

    def process_colony_file(self, file_path):
        """Extract all entities from a single colony file."""
        colony_name = os.path.basename(file_path).replace('.md', '').replace('_', ' ')

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract entities by category
        self.extract_geographic_entities(content, colony_name)
        self.extract_people(content, colony_name)
        self.extract_institutions(content, colony_name)
        self.extract_economic_data(content, colony_name)
        self.extract_infrastructure(content, colony_name)
        self.extract_demographics(content, colony_name)
        self.extract_events(content, colony_name)

    def extract_geographic_entities(self, content, colony_name):
        """Extract toponyms, coordinates, areas, and geographic descriptions."""
        place_entity = {
            "id": f"place_{len(self.knowledge_graph['entities']['places'])}",
            "type": "colony",
            "name": colony_name,
            "historical_spelling": colony_name,
            "data": {}
        }

        # Extract coordinates
        coord_patterns = [
            r"(\d+)°\s*(\d+)?['\s]*([NS])\s*lat\.?,?\s*(\d+)°\s*(\d+)?['\s]*([EW])\s*long",
            r"between\s+(\d+)°.*?([NS]).*?lat.*?(\d+)°.*?([EW]).*?long",
        ]
        for pattern in coord_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                place_entity["data"]["coordinates"] = str(matches[0])
                break

        # Extract area
        area_patterns = [
            r"area.*?(\d+[,\d]*)\s*square\s*miles",
            r"(\d+[,\d]*)\s*square\s*miles",
        ]
        for pattern in area_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                area_text = match.group(1).replace(',', '')
                place_entity["data"]["area_square_miles"] = area_text
                break

        # Extract population from situation/description sections
        situation_match = re.search(r"Situation and Area\.(.*?)(?=\n\n[A-Z]|\Z)", content, re.DOTALL | re.IGNORECASE)
        if situation_match:
            place_entity["data"]["description"] = situation_match.group(1).strip()[:500]

        self.knowledge_graph["entities"]["places"].append(place_entity)

    def extract_people(self, content, colony_name):
        """Extract people with names, titles, honors, positions, salaries."""
        # Governor pattern
        governor_patterns = [
            r"Governor.*?[:,]\s*([A-Z][a-z]+(?:\s+[A-Z]\.?)*\s+[A-Z][a-z]+(?:,\s*[A-Z]\.[A-Z]\.?[A-Z]\.?[A-Z]\.?)?),?\s*(\d+[,\d]*l\.?)",
            r"Governor\s+and\s+Commander-in-Chief.*?[:,]\s*([^,\n]+(?:,\s*[A-Z]\.[A-Z]\.?[A-Z]\.?[A-Z]\.?)?),?\s*(\d+[,\d]*l\.?)",
        ]

        for pattern in governor_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                name, salary = match
                person = {
                    "id": f"person_{len(self.knowledge_graph['entities']['people'])}",
                    "name": name.strip(),
                    "positions": [{"title": "Governor and Commander-in-Chief", "colony": colony_name}],
                    "salary": salary.strip(),
                    "honors": self.extract_honors(name)
                }
                self.knowledge_graph["entities"]["people"].append(person)

        # Colonial Secretary pattern
        sec_pattern = r"Colonial Secretary.*?[:,]\s*([A-Z][a-z]+(?:\s+[A-Z]\.?)*\s+[A-Z][a-z]+(?:,\s*[A-Z]\.[A-Z]\.?[A-Z]\.?[A-Z]\.?)?),?\s*(\d+[,\d]*l\.?)"
        matches = re.findall(sec_pattern, content)
        for match in matches:
            name, salary = match
            person = {
                "id": f"person_{len(self.knowledge_graph['entities']['people'])}",
                "name": name.strip(),
                "positions": [{"title": "Colonial Secretary", "colony": colony_name}],
                "salary": salary.strip(),
                "honors": self.extract_honors(name)
            }
            self.knowledge_graph["entities"]["people"].append(person)

    def extract_honors(self, name):
        """Extract honors/decorations from a name string."""
        honor_patterns = [
            r'K\.C\.M\.G\.', r'C\.M\.G\.', r'C\.B\.', r'K\.C\.B\.',
            r'D\.S\.O\.', r'M\.V\.O\.', r'I\.S\.O\.', r'Kt\.', r'Sir', r'Dame'
        ]
        honors = []
        for pattern in honor_patterns:
            if re.search(pattern, name):
                honors.append(pattern.replace('\\', '').replace('.', ''))
        return honors

    def extract_institutions(self, content, colony_name):
        """Extract councils, courts, departments, military units."""
        # Executive Council
        if re.search(r"Executive Council", content, re.IGNORECASE):
            institution = {
                "id": f"inst_{len(self.knowledge_graph['entities']['institutions'])}",
                "type": "council",
                "name": f"Executive Council of {colony_name}",
                "colony": colony_name,
                "members": []
            }

            # Extract council members
            ec_section = re.search(r"Executive Council\.(.*?)(?=\n\n[A-Z]|\Z)", content, re.DOTALL | re.IGNORECASE)
            if ec_section:
                members = re.findall(r"([A-Z][a-z]+(?:\s+[A-Z]\.?)*\s+[A-Z][a-z]+(?:,\s*[A-Z]\.[A-Z]\.?[A-Z]\.?[A-Z]\.?)?)", ec_section.group(1))
                institution["members"] = [m.strip() for m in members[:10]]

            self.knowledge_graph["entities"]["institutions"].append(institution)

        # Legislative Council
        if re.search(r"Legislative Council", content, re.IGNORECASE):
            institution = {
                "id": f"inst_{len(self.knowledge_graph['entities']['institutions'])}",
                "type": "council",
                "name": f"Legislative Council of {colony_name}",
                "colony": colony_name,
                "members": []
            }
            self.knowledge_graph["entities"]["institutions"].append(institution)

    def extract_economic_data(self, content, colony_name):
        """Extract revenue, expenditure, trade, shipping data."""
        # Revenue and expenditure tables
        revenue_pattern = r"(\d{4})\s+[£|Rs\.]?\s*(\d+[,\d]*)\s+[£|Rs\.]?\s*(\d+[,\d]*)"
        matches = re.findall(revenue_pattern, content)

        for match in matches[:5]:  # Limit to avoid duplicates
            year, revenue, expenditure = match
            economic_data = {
                "id": f"econ_{len(self.knowledge_graph['entities']['economic_data'])}",
                "colony": colony_name,
                "year": year,
                "revenue": revenue.replace(',', ''),
                "expenditure": expenditure.replace(',', ''),
                "currency": self.detect_currency(content)
            }
            self.knowledge_graph["entities"]["economic_data"].append(economic_data)

    def detect_currency(self, content):
        """Detect the currency used in the colony."""
        if re.search(r"Rs\.|rupees|Rupees", content):
            return "Rupees"
        elif re.search(r"£|sterling|pounds", content):
            return "Pounds Sterling"
        return "Unknown"

    def extract_infrastructure(self, content, colony_name):
        """Extract railways, telegraphs, postal routes, docks, roads."""
        infrastructure_items = []

        # Railways
        railway_pattern = r"(\d+[,\d]*)\s*miles?\s*of.*?railwa"
        match = re.search(railway_pattern, content, re.IGNORECASE)
        if match:
            infrastructure = {
                "id": f"infra_{len(self.knowledge_graph['entities']['infrastructure'])}",
                "type": "railway",
                "colony": colony_name,
                "extent": match.group(1),
                "unit": "miles"
            }
            self.knowledge_graph["entities"]["infrastructure"].append(infrastructure)

        # Telegraphs
        telegraph_pattern = r"(\d+[,\d]*)\s*miles?\s*of.*?telegraph"
        match = re.search(telegraph_pattern, content, re.IGNORECASE)
        if match:
            infrastructure = {
                "id": f"infra_{len(self.knowledge_graph['entities']['infrastructure'])}",
                "type": "telegraph",
                "colony": colony_name,
                "extent": match.group(1),
                "unit": "miles"
            }
            self.knowledge_graph["entities"]["infrastructure"].append(infrastructure)

    def extract_demographics(self, content, colony_name):
        """Extract population data with breakdowns."""
        # Census data
        census_patterns = [
            r"population.*?(\d{4}).*?(\d+[,\d]+)",
            r"Census.*?(\d{4}).*?(\d+[,\d]+)",
        ]

        for pattern in census_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches:
                year, population = match
                demographic = {
                    "id": f"demo_{len(self.knowledge_graph['entities']['demographics'])}",
                    "colony": colony_name,
                    "year": year,
                    "total_population": population.replace(',', ''),
                    "source": "census"
                }
                self.knowledge_graph["entities"]["demographics"].append(demographic)
                break
            if matches:
                break

    def extract_events(self, content, colony_name):
        """Extract historical events mentioned."""
        # Look for historical dates and events
        event_patterns = [
            r"In\s+(\d{4})[,\s]+(.*?)(?:\.|;|\n)",
            r"(\d{4}).*?(discovered|captured|ceded|annexed|treaty)",
        ]

        for pattern in event_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches[:5]:  # Limit events
                if len(match) == 2:
                    year, description = match
                    event = {
                        "id": f"event_{len(self.knowledge_graph['entities']['events'])}",
                        "colony": colony_name,
                        "year": year,
                        "description": description.strip()[:200]
                    }
                    self.knowledge_graph["entities"]["events"].append(event)

    def save_knowledge_graph(self, output_file):
        """Save the knowledge graph to JSON file."""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.knowledge_graph, f, indent=2, ensure_ascii=False)
        print(f"\nKnowledge graph saved to: {output_file}")

def main():
    source_dir = "/home/user/colonial_office_list/output_2/1909_manual_parsed"
    schema_file = "/home/user/colonial_office_list/json_schema_template.json"
    output_file = "/home/user/colonial_office_list/knowledge_graph_extracts/1909_extracted.json"

    print("="*80)
    print("Colonial Office List 1909 - Knowledge Graph Extraction")
    print("="*80)

    extractor = KnowledgeGraphExtractor(source_dir, schema_file)
    knowledge_graph = extractor.process_all_files()
    extractor.save_knowledge_graph(output_file)

    # Print summary statistics
    print("\n" + "="*80)
    print("EXTRACTION SUMMARY")
    print("="*80)
    print(f"Files Processed: {knowledge_graph['metadata']['files_processed']}")
    print(f"\nEntity Counts:")
    for entity_type, entities in knowledge_graph['entities'].items():
        print(f"  {entity_type.capitalize()}: {len(entities)}")
    print("="*80)

if __name__ == "__main__":
    main()
