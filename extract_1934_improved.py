#!/usr/bin/env python3
"""
Colonial Office List 1934 - Enhanced Knowledge Graph Extraction
Improved version with better name parsing and data quality
"""

import json
import re
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Set, Tuple
from collections import defaultdict
import uuid

class ImprovedColonialOfficeExtractor:
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
        self.id_cache: Dict[str, str] = {}

    def generate_id(self, prefix: str, name: str) -> str:
        """Generate consistent IDs for entities"""
        cache_key = f"{prefix}:{name}"
        if cache_key not in self.id_cache:
            self.id_cache[cache_key] = f"{prefix}_{uuid.uuid4().hex[:8]}"
        return self.id_cache[cache_key]

    def extract_coordinates(self, text: str) -> Optional[Dict]:
        """Extract latitude and longitude from text"""
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
            (r"(\d+(?:\.\d+)?)\s*acres", "acres"),
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
        pattern = r"population\s+(?:of\s+)?(\d+(?:,\d{3})*)"
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return int(match.group(1).replace(",", ""))
        return None

    def extract_people_improved(self, text: str, location: str) -> None:
        """Extract people with better name parsing"""
        # Better pattern: Title, Full Name [, Honors]
        # Examples:
        # Governor, John Smith, K.C.M.G.
        # Chief Commissioner, Lt.-Col. B. R. Reilly, C.I.E., O.B.E.
        # District Judge, E. Weston, Esq., I.C.S.

        lines = text.split('\n')
        titles_keywords = [
            'Governor', 'Chief Commissioner', 'Resident', 'Judge', 'Commissioner',
            'Officer', 'Secretary', 'Magistrate', 'Director', 'Principal',
            'Superintendent', 'Commandant', 'Chairman', 'Collector', 'Agent',
            'Inspector', 'Director-General', 'Assistant', 'Deputy'
        ]

        for line in lines:
            line = line.strip()
            if not line or len(line) < 10:
                continue

            # Check if line contains a position title
            title_found = None
            for title in titles_keywords:
                if f"{title}," in line:
                    title_found = title
                    break

            if not title_found:
                continue

            # Extract position, name, and honors
            # Split by commas
            parts = [p.strip() for p in line.split(',')]
            if len(parts) < 2:
                continue

            position = parts[0]
            name_part = parts[1]

            # Clean up name (remove common prefixes like "Lt.", "Major", etc.)
            # These are typically followed by a hyphen in military ranks
            name = name_part

            # Extract honors (items that are typically all caps or initials)
            honors = []
            for part in parts[2:]:
                part = part.strip()
                # Check if it looks like an honor (short, caps, dots)
                if len(part) <= 15 and (part.isupper() or re.match(r'^[A-Z\.\-\s]+$', part)):
                    honors.append(part)

            # Only extract if name looks reasonable (not just initials or too short)
            if name and len(name) > 3 and not name.isupper():
                person_id = self.generate_id("person", name)

                if person_id not in self.people:
                    self.people[person_id] = {
                        "id": person_id,
                        "name": name,
                        "titles": [],
                        "honors": honors if honors else [],
                        "positions": []
                    }

                # Extract salary if present
                salary_data = None
                salary_match = re.search(r"£([\d,]+)", line)
                if salary_match:
                    salary_data = {
                        "amount": int(salary_match.group(1).replace(",", "")),
                        "currency": "£",
                        "period": "annual"
                    }

                position_obj = {
                    "title": position,
                    "location": location,
                    "status": "permanent",
                    "year": self.year
                }

                if salary_data:
                    position_obj["salary"] = salary_data

                # Avoid duplicates
                if position_obj not in self.people[person_id]["positions"]:
                    self.people[person_id]["positions"].append(position_obj)

    def extract_geographic_entities(self, text: str, colony_name: str) -> None:
        """Extract geographic entities"""
        coords = self.extract_coordinates(text[:1000])
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
                self.places[place_id]["description"] = f"Population: {pop}"

    def extract_institutions(self, text: str, location: str) -> None:
        """Extract institutional information"""
        # Look for "Executive Council", "Legislative Council", etc.
        institution_patterns = [
            (r"Executive Council", "executive_council"),
            (r"Legislative Council", "legislative_council"),
            (r"Supreme Court", "court"),
            (r"Court of[^.]*", "court"),
            (r"Vice-Admiralty Court", "court"),
            (r"Police Court", "court"),
            (r"Colonial Secretary", "department"),
            (r"Treasury[,\s]", "department"),
            (r"Survey Department", "department"),
            (r"Public Works", "public_works"),
            (r"Hospital[s]?", "medical"),
            (r"Church[es]?", "religious"),
            (r"Bank of", "bank"),
            (r"Post Office", "postal"),
            (r"Garrison", "military_unit"),
            (r"Regiment", "military_unit"),
            (r"Police Force", "police_force"),
        ]

        for pattern, inst_type in institution_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                inst_name = match.group(0).strip()
                if len(inst_name) > 3:
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
        """Extract economic data"""
        # Revenue/Expenditure in various formats
        patterns = [
            (r"Revenue[:\s]+(?:Rs\.|£)?[\s]*(\d+(?:,\d{3})*)", "revenue", "£/Rs."),
            (r"Expenditure[:\s]+(?:Rs\.|£)?[\s]*(\d+(?:,\d{3})*)", "expenditure", "£/Rs."),
            (r"Annual Revenue[:\s]+(?:Rs\.|£)?[\s]*(\d+(?:,\d{3})*)", "revenue", "£/Rs."),
            (r"(?:Exports?|shipped)[:\s]+([A-Za-z\s,]+?)(?:\d{4}|\.)", "trade_export", None),
            (r"(?:Imports?)[:\s]+([A-Za-z\s,]+?)(?:\d{4}|\.)", "trade_import", None),
        ]

        for pattern, econ_type, currency in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    value = match.group(1)
                    if value.isdigit() or value.replace(",", "").isdigit():
                        value = int(value.replace(",", ""))
                        econ_id = self.generate_id("economic", f"{location}_{econ_type}_{match.start()}")
                        self.economic_data.append({
                            "id": econ_id,
                            "type": econ_type,
                            "location": location,
                            "year": self.year,
                            "data": {
                                "category": econ_type.replace("_", " ").title(),
                                "value": value,
                                "currency": currency if currency else "unknown"
                            }
                        })
                except:
                    pass

    def extract_infrastructure(self, text: str, location: str) -> None:
        """Extract infrastructure information"""
        # Look for railways, telegraphs, docks, etc.
        infra_patterns = [
            (r"Railway[^.]*?(?:\d+\s*miles)?", "railway"),
            (r"Telegraph[^.]*", "telegraph"),
            (r"Postal[^.]*", "postal_route"),
            (r"Dock[s]?[^.]*", "dock"),
            (r"Harbour[^.]*|Harbor[^.]*", "harbor"),
            (r"Port[^.]*", "dock"),
            (r"Road[s]?[^.]*", "road"),
            (r"Bridge[s]?[^.]*", "bridge"),
        ]

        for pattern, infra_type in infra_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                desc = match.group(0).strip()
                if 4 < len(desc) < 200:
                    infra_id = self.generate_id("infrastructure", f"{location}_{infra_type}_{match.start()}")

                    length_match = re.search(r"(\d+(?:\.\d+)?)\s*miles?", desc, re.IGNORECASE)
                    spec = {}
                    if length_match:
                        spec["length"] = {"value": float(length_match.group(1)), "unit": "miles"}

                    infra_obj = {
                        "id": infra_id,
                        "type": infra_type,
                        "location": location,
                        "name": desc[:100],
                        "year": self.year
                    }
                    if spec:
                        infra_obj["specifications"] = spec

                    self.infrastructure.append(infra_obj)

    def extract_demographics(self, text: str, location: str) -> None:
        """Extract demographic data"""
        pop_pattern = r"population\s+(?:of\s+)?(\d+(?:,\d{3})*)"
        matches = re.finditer(pop_pattern, text, re.IGNORECASE)

        populations_found = set()
        for match in matches:
            pop_value = int(match.group(1).replace(",", ""))
            if pop_value not in populations_found and pop_value > 100:  # Skip small numbers
                populations_found.add(pop_value)

                demo_id = self.generate_id("demographic", f"{location}_pop_{pop_value}")
                self.demographics.append({
                    "id": demo_id,
                    "location": location,
                    "year": self.year,
                    "total_population": pop_value,
                    "census_date": "1934"
                })

    def extract_events(self, text: str, location: str) -> None:
        """Extract historical events"""
        event_patterns = [
            (r"(?:Established|Founded|Settled|Ceded|Occupied)[^.]*?(\d{4})", "establishment"),
            (r"Treaty[^.]*", "treaty"),
            (r"(?:Rebellion|Revolt|Uprising)", "rebellion"),
        ]

        for pattern, event_type in event_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                desc = match.group(0).strip()
                if 5 < len(desc) < 500:
                    event_id = self.generate_id("event", f"{location}_{event_type}_{match.start()}")
                    if event_id not in {e['id'] for e in self.events}:
                        self.events.append({
                            "id": event_id,
                            "type": event_type,
                            "description": desc[:300],
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
        self.extract_people_improved(text, colony_name)
        self.extract_institutions(text, colony_name)
        self.extract_economic_data(text, colony_name)
        self.extract_infrastructure(text, colony_name)
        self.extract_demographics(text, colony_name)
        self.extract_events(text, colony_name)

    def build_relationships(self) -> None:
        """Build relationships between entities"""
        # LOCATED_IN: people/institutions in locations
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

        # GOVERNED_BY
        for person_id, person in self.people.items():
            for position in person["positions"]:
                if any(word in position["title"] for word in ["Governor", "Chief Commissioner", "Resident"]):
                    location = position.get("location")
                    if location:
                        location_id = self.generate_id("place", location)
                        self.relationships.append({
                            "source_id": location_id,
                            "relationship_type": "GOVERNED_BY",
                            "target_id": person_id,
                            "properties": {"year": self.year, "title": position["title"]}
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
                                   f"Processed {len(self.colonies_processed)} colonies/territories. "
                                   f"Improved data quality with enhanced name parsing and pattern matching."
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
        print("\n" + "="*70)
        print("1934 COLONIAL OFFICE LIST - KNOWLEDGE GRAPH EXTRACTION")
        print("="*70)
        print(f"Colonies Processed: {len(self.colonies_processed)}")
        print(f"\nEntity Counts:")
        print(f"  Geographic Places:    {summary['total_places']:>8}")
        print(f"  People Identified:    {summary['total_people']:>8}")
        print(f"  Institutions:         {summary['total_institutions']:>8}")
        print(f"  Economic Records:     {summary['total_economic_entries']:>8}")
        print(f"  Infrastructure:       {summary['total_infrastructure']:>8}")
        print(f"  Demographics:         {summary['total_demographics']:>8}")
        print(f"  Historical Events:    {summary['total_events']:>8}")
        print(f"  Entity Relationships: {summary['total_relationships']:>8}")
        print("="*70)
        print(f"\nOutput File: {self.output_file}")
        print(f"File Size: {self.output_file.stat().st_size / (1024*1024):.1f} MB")
        print("="*70)

        return output_data


if __name__ == "__main__":
    source_dir = "/home/user/colonial_office_list/output_2/1934_manual_parsed/"
    output_file = "/home/user/colonial_office_list/knowledge_graph_extracts/1934_extracted.json"

    extractor = ImprovedColonialOfficeExtractor(source_dir, output_file)
    extractor.extract()
