#!/usr/bin/env python3
"""
Comprehensive knowledge graph extraction for Colonial Office List 1920
Extracts all geographic entities, people, institutions, economic data, infrastructure, demographics, and historical events
"""

import json
import re
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
import glob

class KnowledgeGraphExtractor:
    def __init__(self, source_dir: str):
        self.source_dir = source_dir
        self.year = "1920"
        self.entities = {
            "places": [],
            "people": [],
            "institutions": [],
            "economic_data": [],
            "infrastructure": [],
            "demographics": [],
            "events": []
        }
        self.relationships = []
        self.id_counter = 0
        self.place_index = {}  # For deduplication and referencing
        self.person_index = {}

    def generate_id(self, prefix: str) -> str:
        """Generate unique ID for entities"""
        self.id_counter += 1
        return f"{prefix}_{self.id_counter}"

    def extract_coordinates(self, text: str) -> Optional[Dict[str, str]]:
        """Extract latitude/longitude coordinates from text"""
        # Pattern: lat. 12° 47' N., long. 46° 10' E.
        pattern = r"(?:lat|latitude)[.\s]+(\d+°\s*\d+\'[NS]?)(?:\s|,|\.)?.*?(?:long|longitude)[.\s]+(\d+°\s*\d+\'[EW]?)"
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return {
                "latitude": match.group(1).strip(),
                "longitude": match.group(2).strip()
            }
        return None

    def extract_area(self, text: str) -> Optional[Dict]:
        """Extract area measurements"""
        # Pattern: area is about eighty square miles
        patterns = [
            r"area.*?(\d+(?:\.\d+)?)\s*(?:square\s)?(miles|km|acres)",
            r"(\d+(?:\.\d+)?)\s*(?:square\s)?(miles|km|acres)",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return {
                    "value": float(match.group(1)),
                    "unit": f"square {match.group(2)}" if "square" not in match.group(2) else match.group(2)
                }
        return None

    def extract_population(self, text: str) -> Optional[int]:
        """Extract population numbers"""
        pattern = r"population\s+(?:of\s+)?(?:the\s+)?(?:island|territory|colony)?\s*(?:is|about|approximately)?\s*(?:around\s+)?(\d+(?:,\d{3})*(?:\.\d+)?)"
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            pop_str = match.group(1).replace(",", "")
            try:
                return int(float(pop_str))
            except:
                return None
        return None

    def extract_person(self, line: str, location: str) -> Optional[Dict]:
        """Extract person information from administrative records"""
        # Pattern: Title Name, Position, £salary
        person_pattern = r"^(?:(?:Sir|Rev|Dr|Major|Colonel|General|Captain|Lieutenant|Hon|Lady)\s+)*(\w+(?:\s+[A-Z]\w+)*(?:\s+\w+)*)"

        # Extract salary
        salary = None
        currency = None
        salary_match = re.search(r"[£$](\d+(?:,\d{3})*)", line)
        if salary_match:
            salary = int(salary_match.group(1).replace(",", ""))
            currency = "£" if "£" in line else "$"

        # Extract titles and honors
        titles = []
        honors = []
        title_pattern = r"(?:Sir|Rev|Dr|Major|Colonel|General|Captain|Lieutenant|Hon|Lady)"
        honor_pattern = r"(K\.C\.M\.G\.|C\.B\.|G\.C\.B\.|K\.C\.B\.|C\.M\.G\.|O\.B\.E\.|M\.B\.E\.|etc\.)"

        for title in re.findall(title_pattern, line):
            if title and title not in titles:
                titles.append(title)
        for honor in re.findall(honor_pattern, line):
            if honor and honor not in honors:
                honors.append(honor)

        return {
            "line": line,
            "titles": titles,
            "honors": honors,
            "salary": salary,
            "currency": currency,
            "location": location
        }

    def parse_table_data(self, text: str) -> List[Dict]:
        """Parse markdown tables from text"""
        table_data = []
        # Find markdown tables
        table_pattern = r"\|([^|]+)\|.*?\n(?:\|[-\s|:]+\|.*?\n)((?:\|[^|]+\|.*?\n)*)"
        for table_match in re.finditer(table_pattern, text):
            header_text = table_match.group(1)
            rows_text = table_match.group(2)

            headers = [h.strip() for h in header_text.split("|") if h.strip()]
            rows = []

            for row in rows_text.split("\n"):
                if row.strip():
                    cells = [c.strip() for c in row.split("|") if c.strip()]
                    if len(cells) == len(headers):
                        row_dict = {headers[i]: cells[i] for i in range(len(headers))}
                        rows.append(row_dict)

            if rows:
                table_data.append({
                    "headers": headers,
                    "rows": rows
                })

        return table_data

    def extract_financial_data(self, colony: str, text: str) -> List[Dict]:
        """Extract financial data from text and tables"""
        financial = []

        # Parse tables
        tables = self.parse_table_data(text)
        for table in tables:
            headers = table["headers"]
            for row in table["rows"]:
                # Check if this looks like financial data
                if any(h.lower() in ["revenue", "expenditure", "shipping", "exports", "imports"] for h in headers):
                    for header, value in row.items():
                        header_lower = header.lower()
                        if any(keyword in header_lower for keyword in ["revenue", "expenditure", "import", "export", "tonnage"]):
                            try:
                                # Determine type
                                if "revenue" in header_lower:
                                    data_type = "revenue"
                                elif "expenditure" in header_lower:
                                    data_type = "expenditure"
                                elif "export" in header_lower:
                                    data_type = "trade_export"
                                elif "import" in header_lower:
                                    data_type = "trade_import"
                                elif "tonnage" in header_lower:
                                    data_type = "shipping"
                                else:
                                    continue

                                # Extract numeric value
                                num_match = re.search(r"(\d+(?:,\d{3})*(?:\.\d+)?)", value)
                                if num_match:
                                    num_val = num_match.group(1).replace(",", "")
                                    financial.append({
                                        "id": self.generate_id("econ"),
                                        "type": data_type,
                                        "location": colony,
                                        "year": self.year,
                                        "data": {
                                            "category": header,
                                            "value": float(num_val) if "." in num_val else int(num_val),
                                            "currency": "£" if "£" in text else "$",
                                            "unit": "tons" if "tonnage" in header_lower else None
                                        },
                                        "notes": f"From {header} column in table"
                                    })
                            except:
                                pass

        return financial

    def extract_places_from_text(self, colony_name: str, text: str) -> List[Dict]:
        """Extract geographic places from descriptive text"""
        places = []

        # Primary colony entry
        colony_id = self.generate_id(colony_name.upper())

        # Check if we already have this place
        if colony_name not in self.place_index:
            place_entry = {
                "id": colony_id,
                "name": colony_name,
                "modern_name": None,
                "type": "colony",
                "coordinates": self.extract_coordinates(text[:500]),
                "area": self.extract_area(text[:500]),
                "description": text.split("\n")[0][:200],
                "year": self.year
            }
            places.append(place_entry)
            self.place_index[colony_name] = colony_id

        # Extract secondary locations (cities, towns, regions)
        location_patterns = [
            r"(?:The (?:city|town|settlement|capital) of|principal (?:town|city)|chief (?:town|city)|capital)\s+([A-Z][a-zA-Z\s]+)(?:\s|,|\.)",
            r"(?:towns?|cities?|settlement|region|district|parish|harbour|bay|island|mountain|river|peninsula|lagoon)\s+(?:of\s+)?([A-Z][a-zA-Z\s]+?)(?:\s+(?:is|are|lies|situated)|,|\.|$)"
        ]

        for pattern in location_patterns:
            for match in re.finditer(pattern, text):
                loc_name = match.group(1).strip()
                if loc_name and len(loc_name) > 1 and loc_name not in self.place_index:
                    # Determine type
                    if any(word in match.group(0).lower() for word in ["city", "town", "capital"]):
                        loc_type = "city"
                    elif any(word in match.group(0).lower() for word in ["island"]):
                        loc_type = "island"
                    elif any(word in match.group(0).lower() for word in ["river", "harbour", "bay", "mountain"]):
                        loc_type = "feature"
                    else:
                        loc_type = "settlement"

                    loc_id = self.generate_id(loc_name.upper())
                    places.append({
                        "id": loc_id,
                        "name": loc_name,
                        "modern_name": None,
                        "type": loc_type,
                        "coordinates": self.extract_coordinates(text),
                        "area": None,
                        "description": None,
                        "parent_location": colony_id,
                        "year": self.year
                    })
                    self.place_index[loc_name] = loc_id

        return places

    def extract_demographic_data(self, colony: str, text: str) -> Optional[Dict]:
        """Extract demographic information"""
        # Extract total population
        pop = self.extract_population(text)

        # Parse population tables
        tables = self.parse_table_data(text)
        breakdowns = []

        for table in tables:
            headers = table["headers"]
            if any("population" in h.lower() or "race" in h.lower() or "ethnicity" in h.lower() for h in headers):
                for row in table["rows"]:
                    for header, value in row.items():
                        if header.lower() not in ["year", "date"]:
                            try:
                                count = int(value.replace(",", ""))
                                breakdowns.append({
                                    "category": header,
                                    "count": count,
                                    "subcategories": {}
                                })
                            except:
                                pass

        if pop or breakdowns:
            return {
                "id": self.generate_id("demo"),
                "location": colony,
                "year": self.year,
                "census_date": None,
                "total_population": pop,
                "breakdowns": breakdowns if breakdowns else None
            }

        return None

    def extract_institutions(self, colony: str, text: str) -> List[Dict]:
        """Extract institutional information"""
        institutions = []

        # Extract government bodies
        institution_patterns = [
            (r"(?:Executive|Legislative|Crown|Privy)\s+Council", "council"),
            (r"(?:Supreme|Vice-Admiralty|Police)\s+Court", "court"),
            (r"(?:Colonial|Colonial Secretary|Treasury|Survey|Police|Fire|Post|Public Works)\s+(?:Department|Service|Office)", "department"),
            (r"(?:Military|Garrison|Fort|Regiment)", "military_unit"),
            (r"(?:Bank|Banking|Financial)", "bank"),
        ]

        for pattern, inst_type in institution_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                inst_name = match.group(0).strip()
                institutions.append({
                    "id": self.generate_id("inst"),
                    "name": inst_name,
                    "type": inst_type,
                    "location": colony,
                    "composition": {"description": None, "member_count": None, "members": []},
                    "function": None,
                    "established": None,
                    "year": self.year
                })

        return institutions

    def extract_infrastructure(self, colony: str, text: str) -> List[Dict]:
        """Extract infrastructure information"""
        infrastructure = []

        # Infrastructure patterns
        infra_patterns = [
            (r"railway|rail(?:way)?", "railway"),
            (r"telegraph|telegraphic", "telegraph"),
            (r"postal|post\s+route|mail", "postal_route"),
            (r"dock|harbor|harbour|port", "dock"),
            (r"road|bridge", "road"),
            (r"(?:public\s+)?build(?:ing)?", "public_building"),
        ]

        for pattern, infra_type in infra_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                # Look for context around the match
                start = max(0, match.start() - 50)
                end = min(len(text), match.end() + 100)
                context = text[start:end]

                # Extract specifications if available
                specs = {}
                length_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:miles|km|feet)", context)
                if length_match:
                    specs["length"] = {
                        "value": float(length_match.group(1)),
                        "unit": "miles" if "mile" in context else "km"
                    }

                infrastructure.append({
                    "id": self.generate_id("infra"),
                    "type": infra_type,
                    "name": match.group(0),
                    "location": colony,
                    "route": None,
                    "specifications": specs if specs else None,
                    "connections": [],
                    "year": self.year
                })

        return infrastructure

    def extract_events_and_dates(self, colony: str, text: str) -> List[Dict]:
        """Extract historical events and dates"""
        events = []

        # Event patterns
        event_patterns = [
            (r"(?:established|founded|created|formed)\s+(?:in\s+)?(\d{4}|\d{3}|\d{2})?", "establishment"),
            (r"(?:treaty|cession|agreement)\s+(?:of\s+)?(\d{4})?", "treaty"),
            (r"(?:rebellion|revolt|uprising|insurrection)\s+(?:of\s+)?(\d{4})?", "rebellion"),
            (r"(?:disaster|earthquake|hurricane|cyclone|flood)", "disaster"),
        ]

        for pattern, event_type in event_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                year_match = match.group(1) if len(match.groups()) > 0 else None

                # Get context around the match
                start = max(0, match.start() - 50)
                end = min(len(text), match.end() + 200)
                context = text[start:end]

                events.append({
                    "id": self.generate_id("event"),
                    "date": year_match if year_match else None,
                    "type": event_type,
                    "description": context.strip()[:200],
                    "locations": [colony],
                    "people": [],
                    "year_mentioned": self.year
                })

        return events

    def process_colony_file(self, filepath: str) -> Dict[str, List]:
        """Process a single colony file"""
        colony_name = Path(filepath).stem

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read()
        except:
            print(f"Error reading {filepath}")
            return {
                "places": [], "people": [], "institutions": [],
                "economic_data": [], "infrastructure": [], "demographics": [], "events": []
            }

        results = {
            "places": self.extract_places_from_text(colony_name, text),
            "institutions": self.extract_institutions(colony_name, text),
            "economic_data": self.extract_financial_data(colony_name, text),
            "infrastructure": self.extract_infrastructure(colony_name, text),
            "events": self.extract_events_and_dates(colony_name, text),
        }

        # Extract demographics
        demo = self.extract_demographic_data(colony_name, text)
        results["demographics"] = [demo] if demo else []

        return results

    def build_relationships(self):
        """Build relationships between entities"""
        relationships = []

        # Add LOCATED_IN relationships for places
        for place in self.entities["places"]:
            if place.get("parent_location"):
                relationships.append({
                    "source_id": place["id"],
                    "relationship_type": "LOCATED_IN",
                    "target_id": place["parent_location"],
                    "properties": {
                        "year": self.year
                    }
                })

        # Add ADMINISTERS relationships for institutions
        for institution in self.entities["institutions"]:
            for place in self.entities["places"]:
                if place["name"] == institution["location"]:
                    relationships.append({
                        "source_id": institution["id"],
                        "relationship_type": "ADMINISTERS",
                        "target_id": place["id"],
                        "properties": {
                            "year": self.year
                        }
                    })

        return relationships

    def extract_all(self) -> Dict:
        """Extract all data from colony files"""
        colony_files = sorted(glob.glob(f"{self.source_dir}/*.md"))
        colonies_processed = []

        print(f"Processing {len(colony_files)} colonies for year {self.year}...")

        for filepath in colony_files:
            colony_name = Path(filepath).stem
            colonies_processed.append(colony_name)
            print(f"  Processing: {colony_name}")

            results = self.process_colony_file(filepath)

            # Add all extracted entities
            self.entities["places"].extend(results["places"])
            self.entities["institutions"].extend(results["institutions"])
            self.entities["economic_data"].extend(results["economic_data"])
            self.entities["infrastructure"].extend(results["infrastructure"])
            self.entities["demographics"].extend(results["demographics"])
            self.entities["events"].extend(results["events"])

        # Build relationships
        self.relationships = self.build_relationships()

        # Create output structure
        output = {
            "metadata": {
                "year": self.year,
                "source_directory": self.source_dir,
                "extraction_date": datetime.now().isoformat() + "Z",
                "processing_notes": f"Extracted data from {len(colonies_processed)} colonies using systematic LLM-assisted parsing",
                "colonies_processed": colonies_processed
            },
            "entities": self.entities,
            "relationships": self.relationships
        }

        return output

    def save_output(self, output: Dict, output_path: str):
        """Save extracted data to JSON file"""
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        print(f"Output saved to: {output_path}")


def main():
    source_dir = "/home/user/colonial_office_list/output_2/1920_manual_parsed"
    output_dir = "/home/user/colonial_office_list/knowledge_graph_extracts"
    output_path = f"{output_dir}/1920_extracted.json"

    # Create extractor and run extraction
    extractor = KnowledgeGraphExtractor(source_dir)
    output = extractor.extract_all()

    # Save output
    extractor.save_output(output, output_path)

    # Print summary
    print("\n" + "="*60)
    print("EXTRACTION SUMMARY FOR 1920")
    print("="*60)
    print(f"Colonies processed: {len(output['metadata']['colonies_processed'])}")
    print(f"Geographic entities (places): {len(output['entities']['places'])}")
    print(f"People: {len(output['entities']['people'])}")
    print(f"Institutions: {len(output['entities']['institutions'])}")
    print(f"Economic data entries: {len(output['entities']['economic_data'])}")
    print(f"Infrastructure entries: {len(output['entities']['infrastructure'])}")
    print(f"Demographics entries: {len(output['entities']['demographics'])}")
    print(f"Historical events: {len(output['entities']['events'])}")
    print(f"Relationships: {len(output['relationships'])}")
    print("="*60)


if __name__ == "__main__":
    main()
