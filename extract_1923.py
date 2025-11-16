#!/usr/bin/env python3
"""
Extract structured knowledge graph data from Colonial Office List 1923
Follows EXTRACTION_METHODOLOGY.md and json_schema_template.json
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

class ColonialOfficeExtractor:
    def __init__(self, year: str, source_dir: str, output_dir: str):
        self.year = year
        self.source_dir = Path(source_dir)
        self.output_dir = Path(output_dir)
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
        self.entity_id_map = {}
        self.id_counter = 0
        self.colonies_processed = []

    def generate_id(self, prefix: str) -> str:
        """Generate unique entity ID"""
        self.id_counter += 1
        return f"{prefix}_{self.year}_{self.id_counter:05d}"

    def clean_text(self, text: str) -> str:
        """Clean extracted text"""
        return text.strip() if text else ""

    def extract_coordinates(self, text: str) -> Optional[Dict[str, str]]:
        """Extract latitude and longitude from text"""
        # Pattern: N. lat. XX° XX' and long. XX° XX' E. long.
        lat_pattern = r"(\d+°\s*\d+['\"]?\s*[NSE.]?)"
        long_pattern = r"(\d+°\s*\d+['\"]?\s*[WE.]?)"

        lat_match = re.search(lat_pattern, text)
        long_match = re.search(long_pattern, text)

        if lat_match or long_match:
            return {
                "latitude": lat_match.group(1) if lat_match else "",
                "longitude": long_match.group(1) if long_match else ""
            }
        return None

    def extract_area(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract area measurements from text"""
        # Pattern: XXX square miles, XXX acres, etc.
        area_pattern = r"(\d+(?:,\d+)*(?:\.\d+)?)\s*(square\s*miles|acres|sq\.\s*miles|sq\.?\s*miles)"

        matches = re.finditer(area_pattern, text, re.IGNORECASE)
        for match in matches:
            value = match.group(1).replace(',', '')
            unit = match.group(2).replace('.', '').lower()
            try:
                return {
                    "value": float(value),
                    "unit": unit
                }
            except ValueError:
                continue
        return None

    def extract_population(self, text: str) -> Optional[int]:
        """Extract population numbers from text"""
        # Look for "population of XXX" or "population XXX"
        pop_pattern = r"population(?:\s+of)?\s+(?:about\s+)?(\d+(?:,\d+)*)"
        match = re.search(pop_pattern, text, re.IGNORECASE)

        if match:
            try:
                return int(match.group(1).replace(',', ''))
            except ValueError:
                pass
        return None

    def extract_people_with_positions(self, text: str) -> List[Dict[str, Any]]:
        """Extract people and their positions from text"""
        people = []

        # Look for patterns like:
        # "John Smith, Governor, salary £5,000"
        # "Major-General Sir John Smith, K.C.M.G., Governor, £3,000"

        person_pattern = r"(?:^|\n|\s{2,})([A-Z][a-zA-Z\s\.,']+?)(?:,\s*)(?:\s*(?:Major|General|Colonel|Captain|Sir|Rev|Dr|Rt\.?\s*Hon|Esq)[\.,]*)?\s*([^,\n]*?)(?:,\s*(?:£|\$)?(\d+(?:,\d+)*))?"

        # Simpler approach: look for salary lines
        salary_pattern = r"([A-Z][a-zA-Z\s\.,']+?)\s+([^,\n]+?)\s+(?:salary\s+)?(?:£|£|\$)?(\d+(?:,\d+)*[a-z]*\.?\s*[a-z]*)?(?:\n|$)"

        return people

    def extract_institutions(self, text: str, location: str) -> List[Dict[str, Any]]:
        """Extract institutional information from text"""
        institutions = []

        # Look for council, court, department mentions
        council_pattern = r"(Executive Council|Legislative Council|Privy Council|Supreme Court|Police Court)"

        for match in re.finditer(council_pattern, text):
            inst_name = match.group(1)
            inst_id = self.generate_id("inst")

            inst_type = "executive_council" if "Executive" in inst_name else \
                       "legislative_council" if "Legislative" in inst_name else \
                       "privy_council" if "Privy" in inst_name else \
                       "court"

            institution = {
                "id": inst_id,
                "name": inst_name,
                "type": inst_type,
                "location": location,
                "year": self.year,
                "composition": {"description": "", "members": []},
                "function": ""
            }
            institutions.append(institution)

        return institutions

    def extract_economic_data(self, text: str, location: str) -> List[Dict[str, Any]]:
        """Extract economic information from text"""
        economic = []

        # Revenue patterns
        revenue_pattern = r"(revenue|expenditure|trade|exports?|imports?)\s+(?:.*?)(?:£|\$)?(\d+(?:,\d+)*)"

        for match in re.finditer(revenue_pattern, text, re.IGNORECASE):
            data_type = match.group(1).lower()
            try:
                value = int(match.group(2).replace(',', ''))

                econ_id = self.generate_id("econ")
                econ_type = "revenue" if "revenue" in data_type else \
                           "expenditure" if "expenditure" in data_type else \
                           "trade_export" if "export" in data_type else \
                           "trade_import" if "import" in data_type else "trade"

                econ_entry = {
                    "id": econ_id,
                    "type": econ_type,
                    "location": location,
                    "year": self.year,
                    "data": {
                        "category": data_type,
                        "value": value,
                        "currency": "£"
                    }
                }
                economic.append(econ_entry)
            except ValueError:
                continue

        return economic

    def extract_infrastructure(self, text: str, location: str) -> List[Dict[str, Any]]:
        """Extract infrastructure information from text"""
        infrastructure = []

        # Look for railways, telegraphs, ports, etc.
        infra_types = {
            r"railway": "railway",
            r"telegraph": "telegraph",
            r"port|harbour|dock": "dock",
            r"road": "road",
            r"bridge": "bridge"
        }

        for pattern, infra_type in infra_types.items():
            for match in re.finditer(pattern, text, re.IGNORECASE):
                infra_id = self.generate_id("infra")

                infrastructure.append({
                    "id": infra_id,
                    "type": infra_type,
                    "location": location,
                    "year": self.year,
                    "name": f"{location} {infra_type.title()}",
                    "specifications": {},
                    "connections": []
                })

        return infrastructure

    def extract_geography(self, text: str, location: str) -> Dict[str, Any]:
        """Extract primary geographic entity for the colony"""
        place_id = self.generate_id("place")

        # Extract coordinates if present
        coordinates = self.extract_coordinates(text)

        # Extract area
        area = self.extract_area(text)

        # Extract key geographic features mentioned
        description = text[:500] if len(text) > 500 else text

        place = {
            "id": place_id,
            "name": location,
            "type": "colony",
            "coordinates": coordinates,
            "area": area,
            "description": description,
            "year": self.year
        }

        return place, place_id

    def extract_demographics(self, text: str, location: str) -> Optional[Dict[str, Any]]:
        """Extract demographic information from text"""
        # Look for population data and breakdowns
        pop = self.extract_population(text)

        if pop:
            demo_id = self.generate_id("demo")

            demographics = {
                "id": demo_id,
                "location": location,
                "year": self.year,
                "total_population": pop,
                "breakdowns": []
            }

            return demographics

        return None

    def extract_events(self, text: str, location: str) -> List[Dict[str, Any]]:
        """Extract historical events from text"""
        events = []

        # Look for date patterns with events
        event_pattern = r"(in|on|during)?\s*(\d{3,4}|[A-Za-z]+\s+\d{1,2}(?:st|nd|rd|th)?(?:,?\s*\d{3,4})?)"

        for match in re.finditer(event_pattern, text):
            try:
                event_id = self.generate_id("event")

                event = {
                    "id": event_id,
                    "date": match.group(2),
                    "description": f"Event in {location}",
                    "locations": [],
                    "people": [],
                    "year_mentioned": self.year
                }
                events.append(event)
            except:
                pass

        return events

    def process_colony_file(self, filepath: Path) -> Tuple[str, Dict[str, Any]]:
        """Process a single colony file and extract all entities"""

        # Get colony name from filename
        colony_name = filepath.stem.replace('_', ' ').upper()
        self.colonies_processed.append(colony_name)

        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        colony_data = {
            "colony": colony_name,
            "place_id": None
        }

        # Extract geography (primary entity)
        place, place_id = self.extract_geography(content, colony_name)
        self.entities['places'].append(place)
        colony_data['place_id'] = place_id

        # Extract demographics
        demo = self.extract_demographics(content, colony_name)
        if demo:
            self.entities['demographics'].append(demo)

        # Extract institutions
        institutions = self.extract_institutions(content, colony_name)
        self.entities['institutions'].extend(institutions)

        # Extract economic data
        economic = self.extract_economic_data(content, colony_name)
        self.entities['economic_data'].extend(economic)

        # Extract infrastructure
        infrastructure = self.extract_infrastructure(content, colony_name)
        self.entities['infrastructure'].extend(infrastructure)

        # Extract events
        events = self.extract_events(content, colony_name)
        self.entities['events'].extend(events)

        return colony_name, colony_data

    def process_all_colonies(self):
        """Process all colony files in the source directory"""
        colony_files = sorted(self.source_dir.glob('*.md'))

        for filepath in colony_files:
            try:
                self.process_colony_file(filepath)
            except Exception as e:
                print(f"Error processing {filepath}: {e}")

    def build_output(self) -> Dict[str, Any]:
        """Build the final output JSON structure"""
        output = {
            "metadata": {
                "year": self.year,
                "source_directory": str(self.source_dir),
                "extraction_date": datetime.now().isoformat(),
                "colonies_processed": sorted(self.colonies_processed),
                "processing_notes": f"Extracted {len(self.entities['places'])} places, " +
                                   f"{len(self.entities['people'])} people, " +
                                   f"{len(self.entities['institutions'])} institutions, " +
                                   f"{len(self.entities['economic_data'])} economic records, " +
                                   f"{len(self.entities['infrastructure'])} infrastructure items, " +
                                   f"{len(self.entities['demographics'])} demographic records, " +
                                   f"{len(self.entities['events'])} events"
            },
            "entities": self.entities,
            "relationships": self.relationships
        }

        return output

    def save_output(self, output: Dict[str, Any], filepath: Path):
        """Save output to JSON file"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

    def extract(self):
        """Run the complete extraction process"""
        print(f"Starting extraction for year {self.year}...")
        print(f"Source directory: {self.source_dir}")

        self.process_all_colonies()

        print(f"Processed {len(self.colonies_processed)} colonies")
        print(f"Extracted entities:")
        print(f"  - Places: {len(self.entities['places'])}")
        print(f"  - People: {len(self.entities['people'])}")
        print(f"  - Institutions: {len(self.entities['institutions'])}")
        print(f"  - Economic records: {len(self.entities['economic_data'])}")
        print(f"  - Infrastructure: {len(self.entities['infrastructure'])}")
        print(f"  - Demographics: {len(self.entities['demographics'])}")
        print(f"  - Events: {len(self.entities['events'])}")

        output = self.build_output()

        output_file = self.output_dir / f"{self.year}_extracted.json"
        self.save_output(output, output_file)

        print(f"\nOutput saved to: {output_file}")
        print(f"Total relationships: {len(self.relationships)}")

        return output, output_file

def main():
    year = "1923"
    source_dir = "/home/user/colonial_office_list/output_2/1923_manual_parsed"
    output_dir = "/home/user/colonial_office_list/knowledge_graph_extracts"

    extractor = ColonialOfficeExtractor(year, source_dir, output_dir)
    output, output_file = extractor.extract()

    # Print summary statistics
    print("\n" + "="*60)
    print("EXTRACTION SUMMARY")
    print("="*60)
    print(f"Year: {year}")
    print(f"Colonies processed: {len(output['metadata']['colonies_processed'])}")
    print(f"Total entities extracted: {sum(len(v) for v in output['entities'].values())}")
    print(f"Output file: {output_file}")

if __name__ == "__main__":
    main()
