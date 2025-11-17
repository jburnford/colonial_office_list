#!/usr/bin/env python3
"""
Comprehensive Knowledge Graph Extraction for Colonial Office List 1890
Extracts structured entities and relationships from all colony files
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

class ColonialOfficeExtractor:
    """Extract structured knowledge graph data from Colonial Office List entries"""

    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.knowledge_graph = {
            "metadata": {
                "year": 1890,
                "source": "Colonial Office List 1890",
                "extraction_date": datetime.now().isoformat(),
                "colonies_processed": 0,
                "extraction_methodology": "Comprehensive entity and relationship extraction from manually parsed Colonial Office List entries"
            },
            "entities": {
                "geographic_entities": [],
                "people": [],
                "institutions": [],
                "economic_data": [],
                "infrastructure": [],
                "demographic_data": [],
                "historical_events": [],
                "legal_documents": [],
                "military_units": []
            },
            "relationships": []
        }
        self.entity_id_counter = 0

    def generate_entity_id(self, entity_type: str) -> str:
        """Generate unique entity ID"""
        self.entity_id_counter += 1
        return f"{entity_type}_{self.entity_id_counter:06d}"

    def extract_coordinates(self, text: str) -> List[Dict]:
        """Extract geographic coordinates from text"""
        coords = []
        # Pattern for latitude/longitude
        lat_pattern = r"(\d+)°\s*(\d+)?'?\s*(N|S)"
        lon_pattern = r"(\d+)°\s*(\d+)?'?\s*(E|W)"

        lat_matches = re.finditer(lat_pattern, text, re.IGNORECASE)
        lon_matches = re.finditer(lon_pattern, text, re.IGNORECASE)

        for lat_match in lat_matches:
            lat_deg = lat_match.group(1)
            lat_min = lat_match.group(2) or "0"
            lat_dir = lat_match.group(3)

            for lon_match in lon_matches:
                lon_deg = lon_match.group(1)
                lon_min = lon_match.group(2) or "0"
                lon_dir = lon_match.group(3)

                coords.append({
                    "latitude": f"{lat_deg}° {lat_min}' {lat_dir}",
                    "longitude": f"{lon_deg}° {lon_min}' {lon_dir}"
                })
                break

        return coords

    def extract_areas(self, text: str) -> List[Dict]:
        """Extract area measurements"""
        areas = []
        # Pattern for square miles/acres
        area_pattern = r"(\d+[,\d]*)\s*(square miles|acres|sq\. miles)"

        for match in re.finditer(area_pattern, text, re.IGNORECASE):
            value = match.group(1).replace(",", "")
            unit = match.group(2)
            areas.append({
                "value": int(value),
                "unit": unit.lower().replace("sq.", "square")
            })

        return areas

    def extract_people(self, text: str, colony: str) -> List[Dict]:
        """Extract people entities (governors, officials, etc.)"""
        people = []

        # Extract governors from Governor lists
        governor_pattern = r"(\d{4})\s+(.+?)(?:\.|\n)"
        for match in re.finditer(governor_pattern, text):
            year = match.group(1)
            name_title = match.group(2).strip()

            # Parse titles and honors
            titles = []
            honors = []
            if "Sir" in name_title:
                titles.append("Sir")
            if "Lord" in name_title or "Earl" in name_title or "Viscount" in name_title:
                titles.append("Nobleman")

            honor_matches = re.findall(r'\b(K\.C\.M\.G\.|G\.C\.M\.G\.|C\.B\.|K\.C\.B\.|G\.C\.B\.)\b', name_title)
            honors.extend(honor_matches)

            name_clean = re.sub(r'\b(K\.C\.M\.G\.|G\.C\.M\.G\.|C\.B\.|K\.C\.B\.|G\.C\.B\.|Sir|Lord|Earl|Viscount)\b', '', name_title).strip()
            name_clean = re.sub(r'\s+', ' ', name_clean)

            if name_clean:
                person_entity = {
                    "id": self.generate_entity_id("person"),
                    "name": name_clean,
                    "titles": titles,
                    "honors": honors,
                    "positions": [{
                        "title": "Governor",
                        "colony": colony,
                        "year": int(year)
                    }],
                    "salary": None,
                    "allowances": []
                }
                people.append(person_entity)

        # Extract current officials with salaries
        salary_pattern = r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),\s*([^,]+?),\s*[£\$Rs]\s*([\d,]+)"
        for match in re.finditer(salary_pattern, text):
            name = match.group(1).strip()
            position = match.group(2).strip()
            salary_str = match.group(3).replace(",", "")

            try:
                salary = int(salary_str)
                person_entity = {
                    "id": self.generate_entity_id("person"),
                    "name": name,
                    "titles": [],
                    "honors": [],
                    "positions": [{
                        "title": position,
                        "colony": colony,
                        "year": 1890
                    }],
                    "salary": {
                        "amount": salary,
                        "currency": "£",  # Default, would need context
                        "period": "annual"
                    },
                    "allowances": []
                }
                people.append(person_entity)
            except ValueError:
                pass

        return people

    def extract_financial_data(self, text: str, colony: str) -> List[Dict]:
        """Extract financial/economic data"""
        financial_data = []

        # Extract revenue and expenditure
        revenue_pattern = r"Revenue[:\s]*[£\$Rs]\s*([\d,]+)"
        expenditure_pattern = r"Expenditure[:\s]*[£\$Rs]\s*([\d,]+)"

        revenue_matches = re.finditer(revenue_pattern, text, re.IGNORECASE)
        for match in revenue_matches:
            value_str = match.group(1).replace(",", "")
            try:
                value = int(value_str)
                financial_data.append({
                    "id": self.generate_entity_id("economic"),
                    "type": "revenue",
                    "colony": colony,
                    "year": 1890,
                    "amount": value,
                    "currency": "£",  # Would need to detect from context
                    "source": "colonial_government"
                })
            except ValueError:
                pass

        expenditure_matches = re.finditer(expenditure_pattern, text, re.IGNORECASE)
        for match in expenditure_matches:
            value_str = match.group(1).replace(",", "")
            try:
                value = int(value_str)
                financial_data.append({
                    "id": self.generate_entity_id("economic"),
                    "type": "expenditure",
                    "colony": colony,
                    "year": 1890,
                    "amount": value,
                    "currency": "£",
                    "source": "colonial_government"
                })
            except ValueError:
                pass

        return financial_data

    def extract_population(self, text: str, colony: str) -> List[Dict]:
        """Extract population data"""
        population_data = []

        # Extract total population
        pop_pattern = r"population[:\s]*(?:of\s+)?(\d+[,\d]*)"
        for match in re.finditer(pop_pattern, text, re.IGNORECASE):
            value_str = match.group(1).replace(",", "")
            try:
                value = int(value_str)
                population_data.append({
                    "id": self.generate_entity_id("demographic"),
                    "colony": colony,
                    "year": 1890,
                    "total_population": value,
                    "breakdowns": []
                })
            except ValueError:
                pass

        return population_data

    def extract_infrastructure(self, text: str, colony: str) -> List[Dict]:
        """Extract infrastructure entities"""
        infrastructure = []

        # Extract railway data
        railway_pattern = r"(\d+)\s+miles?\s+of\s+railway"
        for match in re.finditer(railway_pattern, text, re.IGNORECASE):
            miles = int(match.group(1))
            infrastructure.append({
                "id": self.generate_entity_id("infrastructure"),
                "type": "railway",
                "colony": colony,
                "length_miles": miles,
                "year": 1890
            })

        # Extract telegraph data
        telegraph_pattern = r"(\d+)\s+miles?\s+of\s+telegraph"
        for match in re.finditer(telegraph_pattern, text, re.IGNORECASE):
            miles = int(match.group(1))
            infrastructure.append({
                "id": self.generate_entity_id("infrastructure"),
                "type": "telegraph",
                "colony": colony,
                "length_miles": miles,
                "year": 1890
            })

        return infrastructure

    def extract_historical_events(self, text: str, colony: str) -> List[Dict]:
        """Extract historical events"""
        events = []

        # Extract discovery/founding dates
        discovery_pattern = r"discovered\s+(?:by\s+([^,]+?)\s+)?in\s+(\d{4})"
        for match in re.finditer(discovery_pattern, text, re.IGNORECASE):
            discoverer = match.group(1) or "Unknown"
            year = int(match.group(2))
            events.append({
                "id": self.generate_entity_id("event"),
                "type": "discovery",
                "colony": colony,
                "year": year,
                "description": f"Discovered by {discoverer}",
                "participants": [discoverer] if match.group(1) else []
            })

        return events

    def process_colony_file(self, file_path: Path) -> None:
        """Process a single colony file and extract all entities"""
        colony_name = file_path.stem.replace("_", " ")

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract geographic information
            coords = self.extract_coordinates(content)
            areas = self.extract_areas(content)

            if coords or areas:
                geo_entity = {
                    "id": self.generate_entity_id("geo"),
                    "name": colony_name,
                    "type": "colony",
                    "coordinates": coords,
                    "area": areas,
                    "year": 1890
                }
                self.knowledge_graph["entities"]["geographic_entities"].append(geo_entity)

            # Extract people
            people = self.extract_people(content, colony_name)
            self.knowledge_graph["entities"]["people"].extend(people)

            # Extract financial data
            financial_data = self.extract_financial_data(content, colony_name)
            self.knowledge_graph["entities"]["economic_data"].extend(financial_data)

            # Extract population data
            population_data = self.extract_population(content, colony_name)
            self.knowledge_graph["entities"]["demographic_data"].extend(population_data)

            # Extract infrastructure
            infrastructure = self.extract_infrastructure(content, colony_name)
            self.knowledge_graph["entities"]["infrastructure"].extend(infrastructure)

            # Extract historical events
            events = self.extract_historical_events(content, colony_name)
            self.knowledge_graph["entities"]["historical_events"].extend(events)

            self.knowledge_graph["metadata"]["colonies_processed"] += 1
            print(f"Processed: {colony_name}")

        except Exception as e:
            print(f"Error processing {colony_name}: {e}")

    def process_all_colonies(self) -> None:
        """Process all colony files in the directory"""
        colony_files = sorted(self.base_path.glob("*.md"))

        for file_path in colony_files:
            self.process_colony_file(file_path)

    def save_knowledge_graph(self, output_path: str) -> None:
        """Save the extracted knowledge graph to JSON file"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.knowledge_graph, f, indent=2, ensure_ascii=False)

        print(f"\nKnowledge graph saved to: {output_path}")
        print(f"Total colonies processed: {self.knowledge_graph['metadata']['colonies_processed']}")
        print(f"Total entities extracted:")
        for entity_type, entities in self.knowledge_graph["entities"].items():
            print(f"  - {entity_type}: {len(entities)}")


def main():
    """Main extraction process"""
    base_path = "/home/user/colonial_office_list/output_2/1890_manual_parsed"
    output_path = "/home/user/colonial_office_list/knowledge_graph_extracts/1890_extracted.json"

    extractor = ColonialOfficeExtractor(base_path)
    extractor.process_all_colonies()
    extractor.save_knowledge_graph(output_path)


if __name__ == "__main__":
    main()
