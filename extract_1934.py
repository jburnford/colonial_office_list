#!/usr/bin/env python3
"""
Colonial Office List 1934 - Comprehensive Knowledge Graph Extraction
Extracts structured data from colonial administrative records following EXTRACTION_METHODOLOGY.md
"""

import json
import re
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Set, Tuple
from collections import defaultdict
import uuid

class ColonialOfficeExtractor:
    def __init__(self, source_dir: str, output_file: str):
        self.source_dir = Path(source_dir)
        self.output_file = Path(output_file)
        self.year = "1934"

        # Storage for extracted entities
        self.places: Dict[str, Dict] = {}
        self.people: Dict[str, Dict] = {}
        self.institutions: Dict[str, Dict] = {}
        self.economic_data: List[Dict] = []
        self.infrastructure: List[Dict] = []
        self.demographics: List[Dict] = []
        self.events: List[Dict] = []
        self.relationships: List[Dict] = []

        # Tracking
        self.colonies_processed: List[str] = []
        self.entity_counts = defaultdict(int)
        self.id_cache: Dict[str, str] = {}  # Map human-readable names to IDs

    def generate_id(self, prefix: str, name: str) -> str:
        """Generate consistent IDs for entities"""
        cache_key = f"{prefix}:{name}"
        if cache_key not in self.id_cache:
            # Use UUID for uniqueness
            self.id_cache[cache_key] = f"{prefix}_{uuid.uuid4().hex[:8]}"
        return self.id_cache[cache_key]

    def extract_coordinates(self, text: str) -> Optional[Dict]:
        """Extract latitude and longitude from text"""
        # Pattern: lat. XX° XX' [N/S] and long. XX° XX' [E/W]
        pattern = r"lat\.\s*(\d+°\s*\d+\'?(?:\s*\d+\")?)\s*([NSns])[.,\s]+" \
                  r"(?:and\s+)?long\.\s*(\d+°\s*\d+\'?(?:\s*\d+\")?)\s*([EWew])"
        match = re.search(pattern, text)
        if match:
            return {
                "latitude": f"{match.group(1)} {match.group(2)}",
                "longitude": f"{match.group(3)} {match.group(4)}"
            }
        return None

    def extract_area(self, text: str) -> Optional[Dict]:
        """Extract area measurements from text"""
        patterns = [
            (r"(\d+(?:\.\d+)?)\s*square\s*miles", "square miles"),
            (r"(\d+(?:\.\d+)?)\s*square\s*miles", "square miles"),
            (r"(\d+(?:\.\d+)?)\s*acres", "acres"),
            (r"(?:area\s+of\s+)?(?:about\s+)?(\d+(?:\.\d+)?)\s*(?:sq\.?\s*)?m\.?", "square miles"),
        ]
        for pattern, unit in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return {
                    "value": float(match.group(1)),
                    "unit": unit
                }
        return None

    def extract_population(self, text: str) -> Optional[int]:
        """Extract population figures from text"""
        # Look for patterns like "population 34,471" or "population of 34471"
        pattern = r"population\s+(?:of\s+)?(\d+(?:,\d{3})*)"
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return int(match.group(1).replace(",", ""))
        return None

    def extract_people(self, text: str, location: str) -> List[Dict]:
        """Extract people with their positions, titles, and salaries"""
        people = []

        # Pattern for lines with titles/positions (e.g., "Governor, John Smith, K.C.B., £5,000")
        person_pattern = r"^([A-Z][a-z\s\-]+?),\s+([A-Z][a-z\s\.]*\s+[A-Z][a-z\s\.]*(?:\s+[A-Z][a-z\s\.]*)?)"

        lines = text.split('\n')
        for i, line in enumerate(lines):
            line = line.strip()
            if not line or len(line) < 5:
                continue

            # Look for lines with titles/positions
            if any(title in line for title in ['Chief Commissioner', 'Governor', 'Judge', 'Commissioner',
                                                'Resident', 'Officer', 'Secretary', 'Magistrate', 'Director',
                                                'Principal', 'Superintendent', 'Commandant', 'Chairman',
                                                'Collector', 'Agent']):
                # Extract position and name
                parts = line.split(',', 1)
                if len(parts) >= 2:
                    position = parts[0].strip()
                    rest = parts[1].strip()

                    # Extract name and titles/honors
                    name_honors = rest.split('.')
                    if len(name_honors) >= 1:
                        name_match = re.match(r"([A-Z][a-z\s\.]*(?:[A-Z][a-z\s\.]*)*(?:\s+[A-Z][a-z\s\.]*)*)", name_honors[0])
                        if name_match:
                            name = name_match.group(1).strip()

                            # Extract honors/titles (K.C.M.G., C.B., etc.)
                            honors = []
                            for part in name_honors[1:]:
                                part = part.strip()
                                if len(part) <= 10 and part.isupper() or '.' in part:
                                    honors.append(part)

                            # Extract salary if present
                            salary_match = re.search(r"£([\d,]+)", line)
                            salary_data = None
                            if salary_match:
                                salary_data = {
                                    "amount": int(salary_match.group(1).replace(",", "")),
                                    "currency": "£",
                                    "period": "annual"
                                }

                            person_id = self.generate_id("person", name)

                            if person_id not in self.people:
                                self.people[person_id] = {
                                    "id": person_id,
                                    "name": name,
                                    "titles": [],
                                    "honors": honors,
                                    "positions": []
                                }

                            position_obj = {
                                "title": position,
                                "location": location,
                                "status": "permanent",
                                "year": self.year
                            }

                            if salary_data:
                                position_obj["salary"] = salary_data

                            self.people[person_id]["positions"].append(position_obj)

        return list(self.people.values())

    def extract_geographic_entities(self, text: str, colony_name: str) -> None:
        """Extract geographic entities (places, features, etc.)"""
        # Main colony entry
        coords = self.extract_coordinates(text[:1000])  # Check first part of text
        area = self.extract_area(text[:1000])
        pop = self.extract_population(text[:1000])

        place_id = self.generate_id("place", colony_name)

        if place_id not in self.places:
            self.places[place_id] = {
                "id": place_id,
                "name": colony_name,
                "type": "colony",
                "year": self.year
            }

            if coords:
                self.places[place_id]["coordinates"] = coords
            if area:
                self.places[place_id]["area"] = area
            if pop:
                self.places[place_id]["population"] = pop

        # Extract mentioned cities/towns/regions
        place_names = self._extract_place_names(text, colony_name)
        for place_name, place_type in place_names:
            place_id = self.generate_id("place", place_name)
            if place_id not in self.places:
                self.places[place_id] = {
                    "id": place_id,
                    "name": place_name,
                    "type": place_type,
                    "year": self.year,
                    "parent_location": self.generate_id("place", colony_name)
                }

    def _extract_place_names(self, text: str, colony_name: str) -> List[Tuple[str, str]]:
        """Extract place names from text"""
        places = []

        # Common place type indicators
        place_indicators = {
            'city': ['city of', 'town of', 'capital'],
            'town': ['town', 'township'],
            'settlement': ['settlement', 'settlement of'],
            'island': ['island of', 'island', 'isle'],
            'region': ['region of', 'district of', 'province'],
            'harbor': ['harbor', 'harbour', 'port'],
            'feature': ['mountains', 'mountain', 'river', 'bay', 'cape', 'strait']
        }

        # Look for capitalized place names
        capital_pattern = r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)"

        for match in re.finditer(capital_pattern, text):
            name = match.group(1).strip()

            # Skip common non-place words
            skip_words = ['The', 'A', 'An', 'Government', 'British', 'His', 'Her', 'Imperial',
                         'Colonial', 'Department', 'Officer', 'General', 'Chief', 'Major',
                         'Lieutenant', 'Captain', 'Sir', 'Dr', 'Rev', 'Esq']

            if name not in skip_words and len(name) > 2 and name != colony_name:
                # Try to determine type
                place_type = 'settlement'

                # Check context before and after
                start = max(0, match.start() - 50)
                end = min(len(text), match.end() + 50)
                context = text[start:end].lower()

                for ptype, indicators in place_indicators.items():
                    if any(ind in context for ind in indicators):
                        place_type = ptype
                        break

                if (name, place_type) not in places and len(places) < 30:  # Limit extraction
                    places.append((name, place_type))

        return places

    def extract_institutions(self, text: str, location: str) -> None:
        """Extract institutional information"""
        institution_types = {
            'executive_council': ['Executive Council', 'Executive Council'],
            'legislative_council': ['Legislative Council', 'Legislative Council'],
            'court': ['Court', 'Supreme Court', 'Court of', 'Justice', 'Admiralty', 'Police Court'],
            'department': ['Department', 'Office', 'Bureau', 'Treasury', 'Survey', 'Secretary'],
            'military_unit': ['Regiment', 'Battalion', 'Garrison', 'Armed', 'Military'],
            'police_force': ['Police', 'Constabulary'],
            'educational': ['School', 'College', 'University', 'Academy'],
            'medical': ['Hospital', 'Medical', 'Health'],
            'religious': ['Church', 'Cathedral', 'Chapel', 'Diocese'],
            'bank': ['Bank', 'Banking'],
            'postal': ['Post Office', 'Postal'],
            'public_works': ['Public Works', 'Works Department']
        }

        # Extract institutions mentioned
        for inst_type, keywords in institution_types.items():
            for keyword in keywords:
                pattern = rf"{re.escape(keyword)}[^.\n]*"
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    inst_name = match.group(0).strip()
                    if len(inst_name) > 5:
                        inst_id = self.generate_id("institution", inst_name)
                        if inst_id not in self.institutions:
                            self.institutions[inst_id] = {
                                "id": inst_id,
                                "name": inst_name,
                                "type": inst_type,
                                "location": location,
                                "year": self.year
                            }

    def extract_economic_data(self, text: str, location: str) -> None:
        """Extract economic and trade data"""
        # Extract revenue/expenditure
        revenue_pattern = r"(?:Revenue|Income)[\s\:]*(?:Rs\.|£)?[\s]*(\d+(?:,\d{3})*)"
        expenditure_pattern = r"Expenditure[\s\:]*(?:Rs\.|£)?[\s]*(\d+(?:,\d{3})*)"

        for match in re.finditer(revenue_pattern, text, re.IGNORECASE):
            value = int(match.group(1).replace(",", ""))
            econ_id = self.generate_id("economic", f"{location}_revenue_1934")
            self.economic_data.append({
                "id": econ_id,
                "type": "revenue",
                "location": location,
                "year": self.year,
                "data": {
                    "category": "Annual Revenue",
                    "value": value,
                    "currency": "£/Rs."
                }
            })

        for match in re.finditer(expenditure_pattern, text, re.IGNORECASE):
            value = int(match.group(1).replace(",", ""))
            econ_id = self.generate_id("economic", f"{location}_expenditure_1934")
            self.economic_data.append({
                "id": econ_id,
                "type": "expenditure",
                "location": location,
                "year": self.year,
                "data": {
                    "category": "Annual Expenditure",
                    "value": value,
                    "currency": "£/Rs."
                }
            })

        # Extract trade data
        trade_pattern = r"(?:Exports?|Imports?|Trade)[\s\:]*([^\n]*(?:goods|commodity|commodity|commodities))"
        for match in re.finditer(trade_pattern, text, re.IGNORECASE):
            trade_desc = match.group(1).strip()
            econ_id = self.generate_id("economic", f"{location}_trade_1934")
            trade_type = "trade_export" if "export" in match.group(0).lower() else "trade_import"
            self.economic_data.append({
                "id": econ_id,
                "type": trade_type,
                "location": location,
                "year": self.year,
                "data": {
                    "category": trade_desc[:100],
                    "notes": trade_desc
                }
            })

    def extract_infrastructure(self, text: str, location: str) -> None:
        """Extract infrastructure information"""
        infra_types = {
            'railway': ['railway', 'railroad'],
            'telegraph': ['telegraph'],
            'postal_route': ['postal', 'mail route'],
            'dock': ['dock', 'docks'],
            'harbor': ['harbor', 'harbour', 'port'],
            'road': ['road', 'highway'],
            'bridge': ['bridge'],
            'water_works': ['water works', 'waterworks']
        }

        for infra_type, keywords in infra_types.items():
            for keyword in keywords:
                pattern = rf"{re.escape(keyword)}[^.\n]*(?:[\d,]+\s*(?:miles?|feet|stations?))?[^.\n]*"
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    desc = match.group(0).strip()
                    if len(desc) > 5:
                        infra_id = self.generate_id("infrastructure", f"{location}_{infra_type}")

                        # Try to extract specifications
                        length_match = re.search(r"(\d+(?:\.\d+)?)\s*miles?", desc, re.IGNORECASE)
                        stations_match = re.search(r"(\d+)\s*stations?", desc, re.IGNORECASE)

                        spec = {}
                        if length_match:
                            spec["length"] = {"value": float(length_match.group(1)), "unit": "miles"}
                        if stations_match:
                            spec["stations"] = int(stations_match.group(1))

                        infra_obj = {
                            "id": infra_id,
                            "type": infra_type,
                            "location": location,
                            "name": desc[:80],
                            "year": self.year
                        }
                        if spec:
                            infra_obj["specifications"] = spec

                        self.infrastructure.append(infra_obj)

    def extract_demographics(self, text: str, location: str) -> None:
        """Extract demographic data"""
        # Look for population tables and census data
        pop_pattern = r"population\s+(?:of\s+)?(\d+(?:,\d+)*)"
        matches = re.finditer(pop_pattern, text, re.IGNORECASE)

        populations_found = set()
        for match in matches:
            pop_value = int(match.group(1).replace(",", ""))
            if pop_value not in populations_found:
                populations_found.add(pop_value)

                demo_id = self.generate_id("demographic", f"{location}_pop_1934")
                self.demographics.append({
                    "id": demo_id,
                    "location": location,
                    "year": self.year,
                    "total_population": pop_value,
                    "census_date": "1934"
                })

    def extract_events(self, text: str, location: str) -> None:
        """Extract historical events and dates"""
        event_patterns = [
            (r"(?:Established|Founded|Settled|Ceded|Occupied)\s+(?:in\s+)?(\d{4})", "establishment"),
            (r"Treaty\s+(?:of\s+)?([^\n]+?)(?:\d{4})?", "treaty"),
            (r"(?:Rebellion|Revolt|Uprising|Insurrection)[^\n]*", "rebellion"),
            (r"(?:Constitutional|Reforms?)\s+(?:of\s+)?(\d{4})", "constitutional_change"),
        ]

        for pattern, event_type in event_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                desc = match.group(0).strip()
                if len(desc) > 5:
                    event_id = self.generate_id("event", f"{location}_{event_type}_{match.start()}")
                    self.events.append({
                        "id": event_id,
                        "type": event_type,
                        "description": desc[:200],
                        "locations": [self.generate_id("place", location)],
                        "year_mentioned": self.year
                    })

    def process_colony_file(self, filepath: Path) -> None:
        """Process a single colony file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            text = f.read()

        colony_name = filepath.stem.replace('_', ' ')
        self.colonies_processed.append(colony_name)

        # Extract all entity types
        self.extract_geographic_entities(text, colony_name)
        self.extract_people(text, colony_name)
        self.extract_institutions(text, colony_name)
        self.extract_economic_data(text, colony_name)
        self.extract_infrastructure(text, colony_name)
        self.extract_demographics(text, colony_name)
        self.extract_events(text, colony_name)

    def build_relationships(self) -> None:
        """Build relationships between entities"""
        # LOCATED_IN: places/people/institutions in locations
        for person_id, person in self.people.items():
            if person["positions"]:
                location = person["positions"][0].get("location")
                if location:
                    location_id = self.generate_id("place", location)
                    self.relationships.append({
                        "source_id": person_id,
                        "relationship_type": "LOCATED_IN",
                        "target_id": location_id,
                        "properties": {"year": self.year}
                    })

        # GOVERNED_BY: locations governed by people
        for person_id, person in self.people.items():
            for position in person["positions"]:
                if any(title in position["title"] for title in ["Governor", "Chief Commissioner", "Resident"]):
                    location = position.get("location")
                    if location:
                        location_id = self.generate_id("place", location)
                        self.relationships.append({
                            "source_id": location_id,
                            "relationship_type": "GOVERNED_BY",
                            "target_id": person_id,
                            "properties": {"year": self.year, "title": position["title"]}
                        })

        # ADMINISTERS: institutions administer locations
        for inst_id, institution in self.institutions.items():
            location = institution.get("location")
            if location:
                location_id = self.generate_id("place", location)
                self.relationships.append({
                    "source_id": inst_id,
                    "relationship_type": "ADMINISTERS",
                    "target_id": location_id,
                    "properties": {"year": self.year}
                })

        # PART_OF: dependency relationships (if inferable from text)
        for place_id, place in self.places.items():
            if "parent_location" in place:
                self.relationships.append({
                    "source_id": place_id,
                    "relationship_type": "PART_OF",
                    "target_id": place["parent_location"],
                    "properties": {"year": self.year}
                })

    def generate_output(self) -> Dict:
        """Generate final JSON output"""
        return {
            "metadata": {
                "year": self.year,
                "source_directory": str(self.source_dir),
                "extraction_date": datetime.utcnow().isoformat() + "Z",
                "colonies_processed": self.colonies_processed,
                "processing_notes": f"Comprehensive extraction of 1934 Colonial Office List data. "
                                   f"Processed {len(self.colonies_processed)} colonies/territories."
            },
            "entities": {
                "places": list(self.places.values()),
                "people": list(self.people.values()),
                "institutions": list(self.institutions.values()),
                "economic_data": self.economic_data,
                "infrastructure": self.infrastructure,
                "demographics": self.demographics,
                "events": self.events
            },
            "relationships": self.relationships,
            "summary": {
                "total_places": len(self.places),
                "total_people": len(self.people),
                "total_institutions": len(self.institutions),
                "total_economic_entries": len(self.economic_data),
                "total_infrastructure": len(self.infrastructure),
                "total_demographics": len(self.demographics),
                "total_events": len(self.events),
                "total_relationships": len(self.relationships)
            }
        }

    def extract(self) -> None:
        """Main extraction workflow"""
        # Process all colony files
        for colony_file in sorted(self.source_dir.glob("*.md")):
            print(f"Processing: {colony_file.name}")
            self.process_colony_file(colony_file)

        # Build relationships
        print("Building relationships...")
        self.build_relationships()

        # Generate and write output
        print("Generating output JSON...")
        output_data = self.generate_output()

        # Create output directory if needed
        self.output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        print(f"Extraction complete! Output written to: {self.output_file}")

        # Print summary
        summary = output_data["summary"]
        print("\n" + "="*60)
        print("EXTRACTION SUMMARY - 1934 COLONIAL OFFICE LIST")
        print("="*60)
        print(f"Colonies Processed: {len(self.colonies_processed)}")
        print(f"\nEntity Counts:")
        print(f"  Places:               {summary['total_places']}")
        print(f"  People:               {summary['total_people']}")
        print(f"  Institutions:         {summary['total_institutions']}")
        print(f"  Economic Entries:     {summary['total_economic_entries']}")
        print(f"  Infrastructure:       {summary['total_infrastructure']}")
        print(f"  Demographics:         {summary['total_demographics']}")
        print(f"  Events:               {summary['total_events']}")
        print(f"  Relationships:        {summary['total_relationships']}")
        print("="*60)

        return output_data


if __name__ == "__main__":
    source_dir = "/home/user/colonial_office_list/output_2/1934_manual_parsed/"
    output_file = "/home/user/colonial_office_list/knowledge_graph_extracts/1934_extracted.json"

    extractor = ColonialOfficeExtractor(source_dir, output_file)
    extractor.extract()
