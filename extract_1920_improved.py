#!/usr/bin/env python3
"""
Comprehensive knowledge graph extraction for Colonial Office List 1920 - IMPROVED VERSION
Better captures people, economic data, and all relationship types
"""

import json
import re
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
import glob

class KnowledgeGraphExtractorV2:
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
        self.place_index = {}
        self.person_index = {}
        self.seen_people = set()

    def generate_id(self, prefix: str) -> str:
        """Generate unique ID for entities"""
        self.id_counter += 1
        return f"{prefix}_{self.id_counter:04d}"

    def extract_coordinates(self, text: str) -> Optional[Dict[str, str]]:
        """Extract latitude/longitude coordinates from text"""
        # Pattern: lat. 12° 47' N., long. 46° 10' E.
        pattern = r"(?:lat|latitude)[.\s]+(\d+°\s*\d+[\'′]?\s*[NS]?)(?:\s|,|\.)?.*?(?:long|longitude)[.\s]+(\d+°\s*\d+[\'′]?\s*[EW]?)"
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return {
                "latitude": match.group(1).strip(),
                "longitude": match.group(2).strip()
            }
        return None

    def extract_area(self, text: str) -> Optional[Dict]:
        """Extract area measurements"""
        patterns = [
            r"area\s+(?:is\s+)?(?:about\s+)?(\d+(?:\.\d+)?)\s*(?:square\s+)?(miles|km|acres)",
            r"(\d+(?:\.\d+)?)\s*(?:square\s+)?(miles|km|acres)",
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                unit = match.group(2).lower()
                if "square" not in unit:
                    unit = f"square {unit}"
                return {
                    "value": float(match.group(1)),
                    "unit": unit
                }
        return None

    def extract_population(self, text: str) -> Optional[int]:
        """Extract population numbers"""
        patterns = [
            r"population\s+(?:of\s+)?(?:the\s+)?(?:island|territory|colony)?\s*(?:is|about|approximately|of)?\s*(?:around\s+)?(\d+(?:,\d{3})*(?:\.\d+)?)",
            r"total(?:\s+population)?\s+(\d+(?:,\d{3})*)"
        ]
        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                pop_str = match.group(1).replace(",", "")
                try:
                    return int(float(pop_str))
                except:
                    return None
        return None

    def extract_people_from_text(self, text: str, location: str, colony: str) -> List[Dict]:
        """Extract person information from administrative records"""
        people = []

        # Pattern for government officials: Name, Title, Amount
        # Examples: "Colonial Secretary, Lt.-Col. H. Bryan, C.M.G., 1,200l."
        person_patterns = [
            # Position, Name, Honors, Salary
            r"^([A-Za-z\s\-,]+?),\s+(?:((?:Sir|Rev|Dr|Major|Colonel|General|Captain|Lieutenant|Hon|Lady|Lt\.-?Col|Rt\.|Mr|Maj\.)-?.*?),\s+)?((?:[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),\s+)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:\s+[A-Z][a-z]+)?(?:\s+[A-Z]\.)?(?:\s+[A-Z][a-z]+)?)\s*(?:,\s*((?:[A-Z]\.?[A-Z]\.?[A-Z]\.?|[A-Z][A-Z]\.[A-Z]*\.?)+))?\s*(?:,\s*([£$]\d+(?:,\d{3})*(?:\s+to\s+[£$]\d+(?:,\d{3})*)?))?",
            # Simpler pattern for lists like: "Sir John Pringle, K.C.M.G., M.B."
            r"^((?:Sir|Rev|Dr|Major|Colonel|General|Captain|Lieutenant|Hon|Lady|Lt\.-?Col|Rt\.)?.*?)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*,\s*((?:[A-Z][A-Z]\.?[A-Z]*\.?)+)?(?:\s*,\s*([£$]\d+(?:,\d{3})*))?",
        ]

        lines = text.split("\n")
        for line in lines:
            line = line.strip()
            if not line or line.startswith("#") or len(line) < 5:
                continue

            # Skip section headers and table markers
            if "|" in line or line.startswith("---") or line.isupper():
                continue

            # Try to extract person information
            extracted = self._parse_person_line(line, location, colony)
            if extracted:
                person_id = extracted["id"]
                # Avoid duplicates
                if person_id not in self.seen_people:
                    people.append(extracted)
                    self.seen_people.add(person_id)
                    self.person_index[extracted["name"]] = person_id

        return people

    def _parse_person_line(self, line: str, location: str, colony: str) -> Optional[Dict]:
        """Parse individual person line"""
        # Extract name
        name_match = re.search(r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:\s+[A-Z][a-z]+)?)", line)
        if not name_match:
            return None

        name = name_match.group(1).strip()

        # Extract titles (Sir, Rev, Dr, etc)
        titles = []
        for title in ["Sir", "Rev", "Dr", "Major", "Colonel", "General", "Captain", "Lieutenant", "Hon", "Lady", "Lt.-Col", "Lt.Col", "Maj."]:
            if re.search(rf"\b{title}\b", line):
                titles.append(title)

        # Extract honors (K.C.M.G., C.B., etc)
        honors = []
        honor_pattern = r"((?:[A-Z]\.?)+[A-Z]\.?(?:[A-Z]\.?[A-Z]\.?)?)"
        for match in re.finditer(honor_pattern, line):
            honor = match.group(1).strip()
            if len(honor) > 1 and "." in honor and honor not in titles and honor not in ["U.K.", "N.S.", "S.A."]:
                if honor not in honors:
                    honors.append(honor)

        # Extract salary
        salary = None
        currency = None
        salary_match = re.search(r"([£$])(\d+(?:,\d{3})*)", line)
        if salary_match:
            currency = salary_match.group(1)
            salary = int(salary_match.group(2).replace(",", ""))

        # Extract position title (before the comma and name)
        position = None
        colon_match = re.search(r"^([A-Za-z\s\-]+?)(?:,|\s+(?:Sir|Rev|Dr))", line)
        if colon_match:
            position = colon_match.group(1).strip()

        # Generate unique ID based on name and location
        person_id = f"person_{hash(name + location) % 10000:04d}"

        return {
            "id": person_id,
            "name": name,
            "titles": titles if titles else None,
            "honors": honors if honors else None,
            "positions": [{
                "title": position if position else "Official",
                "department": None,
                "location": location,
                "salary": {
                    "amount": salary,
                    "currency": currency,
                    "period": "annual"
                } if salary else None,
                "allowances": [],
                "status": "permanent",
                "year": self.year
            }] if position or salary else None
        }

    def parse_markdown_tables(self, text: str) -> List[Dict]:
        """Parse markdown tables from text"""
        table_data = []
        # Split by markdown table markers
        lines = text.split("\n")

        i = 0
        while i < len(lines):
            line = lines[i]
            # Check for table header
            if "|" in line and i + 1 < len(lines) and "-" in lines[i + 1] and "|" in lines[i + 1]:
                headers = [h.strip() for h in line.split("|")[1:-1]]
                rows = []
                i += 2

                # Parse rows
                while i < len(lines) and "|" in lines[i]:
                    cells = [c.strip() for c in lines[i].split("|")[1:-1]]
                    if len(cells) == len(headers):
                        row_dict = {headers[j]: cells[j] for j in range(len(headers))}
                        rows.append(row_dict)
                    i += 1

                if rows:
                    table_data.append({
                        "headers": headers,
                        "rows": rows
                    })
            else:
                i += 1

        return table_data

    def extract_financial_data(self, colony: str, text: str) -> List[Dict]:
        """Extract financial data from text and tables"""
        financial = []

        tables = self.parse_markdown_tables(text)

        for table_idx, table in enumerate(tables):
            headers = table["headers"]
            table_name = ""

            # Determine table type from headers
            is_financial = any(keyword in " ".join(headers).lower() for keyword in
                             ["revenue", "expenditure", "import", "export", "shipping", "tonnage", "trade"])

            if not is_financial:
                continue

            for row_idx, row in enumerate(table["rows"]):
                for col_idx, (header, value) in enumerate(row.items()):
                    header_lower = header.lower()
                    value_lower = value.lower()

                    # Try to extract numeric value
                    num_match = re.search(r"(\d+(?:,\d{3})*(?:\.\d+)?)", value)
                    if num_match:
                        try:
                            num_val = num_match.group(1).replace(",", "")
                            num_float = float(num_val) if "." in num_val else int(num_val)

                            # Determine data type
                            data_type = "other"
                            if "revenue" in header_lower:
                                data_type = "revenue"
                            elif "expenditure" in header_lower or "expense" in header_lower:
                                data_type = "expenditure"
                            elif "export" in header_lower:
                                data_type = "trade_export"
                            elif "import" in header_lower:
                                data_type = "trade_import"
                            elif "tonnage" in header_lower or "shipping" in header_lower:
                                data_type = "shipping"
                            elif "trade" in header_lower:
                                data_type = "trade_export"  # Default to export
                            else:
                                continue

                            # Determine year from row if possible
                            year_str = self.year
                            if "year" in [h.lower() for h in headers]:
                                year_idx = [h.lower() for h in headers].index("year")
                                year_str = list(row.values())[year_idx]

                            financial.append({
                                "id": self.generate_id("econ"),
                                "type": data_type,
                                "location": colony,
                                "year": self.year,
                                "data": {
                                    "category": header,
                                    "value": num_float,
                                    "currency": "£" if "l." in text else "$",
                                    "unit": "tons" if "tonnage" in header_lower else None
                                },
                                "notes": f"From table row {row_idx + 1}, year {year_str}"
                            })
                        except:
                            pass

        return financial

    def extract_places_from_text(self, colony_name: str, text: str) -> List[Dict]:
        """Extract geographic places from descriptive text"""
        places = []

        # Create place entry for the colony itself
        colony_id = f"place_{hash(colony_name) % 100000:05d}"

        if colony_name not in self.place_index:
            place_entry = {
                "id": colony_id,
                "name": colony_name,
                "modern_name": None,
                "type": "colony",
                "coordinates": self.extract_coordinates(text[:1000]),
                "area": self.extract_area(text[:1000]),
                "description": text.split("\n")[1][:150] if len(text.split("\n")) > 1 else text[:150],
                "year": self.year
            }
            places.append(place_entry)
            self.place_index[colony_name] = colony_id

        # Extract secondary locations
        location_keywords = {
            "city": [r"\bcity\b", r"capital"],
            "town": [r"\btown\b", r"township"],
            "settlement": [r"settlement", r"hamlet"],
            "island": [r"\bisland\b", r"isle"],
            "river": [r"\briver\b"],
            "mountain": [r"mountain", r"peak", r"hill"],
            "harbor": [r"harbor|harbour|port"],
            "bay": [r"\bbay\b"],
            "feature": [r"strait", r"gulf", r"peninsula", r"lagoon", r"pass"]
        }

        seen_locations = {colony_name}

        for loc_type, patterns in location_keywords.items():
            for pattern in patterns:
                # Pattern: "the City of [Name]" or "[Name] (city)"
                for match in re.finditer(rf"(?:(?:the\s+)?{pattern}\s+of\s+)?([A-Z][a-zA-Z\s]+?)(?:\s*\(|\s+(?:is|are|lies|situated)|,|\.|$)", text, re.IGNORECASE):
                    loc_name = match.group(1).strip()
                    if loc_name and len(loc_name) > 1 and loc_name not in seen_locations and not any(keyword in loc_name.lower() for keyword in ["and", "or", "the", "of"]):
                        seen_locations.add(loc_name)
                        loc_id = f"place_{hash(loc_name + colony_name) % 100000:05d}"
                        places.append({
                            "id": loc_id,
                            "name": loc_name,
                            "modern_name": None,
                            "type": loc_type,
                            "coordinates": None,
                            "area": None,
                            "description": None,
                            "parent_location": colony_id,
                            "year": self.year
                        })
                        self.place_index[loc_name] = loc_id

        return places

    def extract_demographic_data(self, colony: str, text: str) -> Optional[Dict]:
        """Extract demographic information"""
        pop = self.extract_population(text)

        tables = self.parse_markdown_tables(text)
        breakdowns = []

        for table in tables:
            headers = table["headers"]
            headers_lower = [h.lower() for h in headers]

            # Check if this is a population table
            if any(keyword in " ".join(headers_lower) for keyword in ["population", "race", "ethnicity", "white", "black", "coloured", "asian"]):
                for row in table["rows"]:
                    for header, value in row.items():
                        header_lower = header.lower()
                        if header_lower not in ["year", "date", "census"]:
                            try:
                                count = int(value.replace(",", ""))
                                if count > 0:
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

        institution_patterns = [
            (r"(?:Executive|Legislative|Crown|Privy|House of)\s+Council", "council", "executive_council"),
            (r"(?:Supreme|Vice-Admiralty|Police|District)\s+Court", "court", "court"),
            (r"Colonial\s+(?:Secretary|Treasury|Survey|Police|Fire|Post|Works)[\s']s?\s+(?:Department|Service|Office)?", "department", "department"),
            (r"(?:Military|Garrison|Fort|Regiment|Army)", "military_unit", "military_unit"),
            (r"(?:Bank|Banking|Financial|Savings)", "bank", "bank"),
            (r"(?:School|University|College|Educational|Academy)", "school", "educational"),
            (r"(?:Hospital|Medical|Health|Dispensary)", "medical", "medical"),
            (r"(?:Church|Cathedral|Parish)", "religious", "religious"),
        ]

        seen_institutions = set()

        for full_pattern, short_type, db_type in institution_patterns:
            for match in re.finditer(full_pattern, text, re.IGNORECASE):
                inst_name = match.group(0).strip()
                if inst_name not in seen_institutions:
                    institutions.append({
                        "id": self.generate_id("inst"),
                        "name": inst_name,
                        "type": db_type,
                        "location": colony,
                        "composition": {"description": None, "member_count": None, "members": []},
                        "function": None,
                        "established": None,
                        "year": self.year
                    })
                    seen_institutions.add(inst_name)

        return institutions

    def extract_infrastructure(self, colony: str, text: str) -> List[Dict]:
        """Extract infrastructure information"""
        infrastructure = []

        infra_patterns = [
            (r"railway|rail(?:way)?|railroad", "railway"),
            (r"telegraph|telegraphic|telephone", "telegraph"),
            (r"postal|post\s+route|mail", "postal_route"),
            (r"dock|harbor|harbour|port|wharf", "dock"),
            (r"(?:public\s+)?road|bridge|highway", "road"),
            (r"(?:public\s+)?building|structure|fort", "public_building"),
            (r"(?:water\s+)?works|aqueduct|pipeline", "water_works"),
        ]

        seen_infrastructure = set()

        for pattern, infra_type in infra_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                infra_name = match.group(0).strip()
                context_start = max(0, match.start() - 100)
                context_end = min(len(text), match.end() + 200)
                context = text[context_start:context_end]

                if infra_name not in seen_infrastructure:
                    # Extract specifications
                    specs = {}
                    length_match = re.search(r"(\d+(?:\.\d+)?)\s*(?:miles|km|feet|metres)", context)
                    if length_match:
                        specs["length"] = {
                            "value": float(length_match.group(1)),
                            "unit": "miles" if "mile" in context else "km"
                        }

                    cost_match = re.search(r"[£$](\d+(?:,\d{3})*)", context)
                    if cost_match:
                        specs["construction_cost"] = {
                            "value": int(cost_match.group(1).replace(",", "")),
                            "currency": "£" if "£" in context else "$"
                        }

                    infrastructure.append({
                        "id": self.generate_id("infra"),
                        "type": infra_type,
                        "name": infra_name,
                        "location": colony,
                        "route": None,
                        "specifications": specs if specs else None,
                        "connections": [],
                        "year": self.year
                    })
                    seen_infrastructure.add(infra_name)

        return infrastructure

    def extract_events(self, colony: str, text: str) -> List[Dict]:
        """Extract historical events and dates"""
        events = []

        event_patterns = [
            (r"(?:established|founded|created|formed)\s+(?:in\s+)?(\d{4})?", "establishment"),
            (r"(?:treaty|agreement|cession)\s+(?:of\s+)?(\d{4})?", "treaty"),
            (r"(?:rebellion|revolt|uprising)", "rebellion"),
            (r"(?:proclamation|declaration)", "establishment"),
        ]

        seen_events = set()

        for pattern, event_type in event_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                year_match = match.group(1) if match.groups() else None

                context_start = max(0, match.start() - 50)
                context_end = min(len(text), match.end() + 150)
                context = text[context_start:context_end].strip()

                event_key = f"{event_type}_{year_match}_{context[:50]}"
                if event_key not in seen_events:
                    events.append({
                        "id": self.generate_id("event"),
                        "date": year_match,
                        "type": event_type,
                        "description": context,
                        "locations": [colony],
                        "people": [],
                        "year_mentioned": self.year
                    })
                    seen_events.add(event_key)

        return events

    def process_colony_file(self, filepath: str) -> Dict[str, List]:
        """Process a single colony file"""
        colony_name = Path(filepath).stem

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read()
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
            return {
                "places": [], "people": [], "institutions": [],
                "economic_data": [], "infrastructure": [], "demographics": [], "events": []
            }

        results = {
            "places": self.extract_places_from_text(colony_name, text),
            "people": self.extract_people_from_text(text, colony_name, colony_name),
            "institutions": self.extract_institutions(colony_name, text),
            "economic_data": self.extract_financial_data(colony_name, text),
            "infrastructure": self.extract_infrastructure(colony_name, text),
            "events": self.extract_events(colony_name, text),
        }

        demo = self.extract_demographic_data(colony_name, text)
        results["demographics"] = [demo] if demo else []

        return results

    def build_relationships(self):
        """Build relationships between entities"""
        relationships = []

        # LOCATED_IN relationships for places
        for place in self.entities["places"]:
            if place.get("parent_location"):
                relationships.append({
                    "source_id": place["id"],
                    "relationship_type": "LOCATED_IN",
                    "target_id": place["parent_location"],
                    "properties": {"year": self.year}
                })

        # GOVERNED_BY relationships for people in positions
        for person in self.entities["people"]:
            if person.get("positions"):
                for position in person["positions"]:
                    if position.get("location"):
                        # Find the place ID for this location
                        for place in self.entities["places"]:
                            if place["name"].lower() == position["location"].lower():
                                relationships.append({
                                    "source_id": person["id"],
                                    "relationship_type": "GOVERNED_BY",
                                    "target_id": place["id"],
                                    "properties": {
                                        "year": self.year,
                                        "position": position.get("title")
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

            self.entities["places"].extend(results["places"])
            self.entities["people"].extend(results["people"])
            self.entities["institutions"].extend(results["institutions"])
            self.entities["economic_data"].extend(results["economic_data"])
            self.entities["infrastructure"].extend(results["infrastructure"])
            self.entities["demographics"].extend(results["demographics"])
            self.entities["events"].extend(results["events"])

        # Build relationships
        self.relationships = self.build_relationships()

        output = {
            "metadata": {
                "year": self.year,
                "source_directory": self.source_dir,
                "extraction_date": datetime.now().isoformat() + "Z",
                "processing_notes": f"Comprehensive extraction from {len(colonies_processed)} colonies. Includes places, people, institutions, economic data, infrastructure, demographics, and events with relationships.",
                "colonies_processed": colonies_processed
            },
            "entities": self.entities,
            "relationships": self.relationships
        }

        return output

    def save_output(self, output: Dict, output_path: str):
        """Save extracted data to JSON file"""
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        print(f"Output saved to: {output_path}")


def main():
    source_dir = "/home/user/colonial_office_list/output_2/1920_manual_parsed"
    output_dir = "/home/user/colonial_office_list/knowledge_graph_extracts"
    output_path = f"{output_dir}/1920_extracted.json"

    extractor = KnowledgeGraphExtractorV2(source_dir)
    output = extractor.extract_all()

    extractor.save_output(output, output_path)

    # Print summary
    print("\n" + "="*70)
    print("COMPREHENSIVE KNOWLEDGE GRAPH EXTRACTION - COLONIAL OFFICE LIST 1920")
    print("="*70)
    print(f"Colonies processed: {len(output['metadata']['colonies_processed'])}")
    print(f"Geographic entities (places): {len(output['entities']['places'])}")
    print(f"People extracted: {len(output['entities']['people'])}")
    print(f"Institutions: {len(output['entities']['institutions'])}")
    print(f"Economic data entries: {len(output['entities']['economic_data'])}")
    print(f"Infrastructure entries: {len(output['entities']['infrastructure'])}")
    print(f"Demographics entries: {len(output['entities']['demographics'])}")
    print(f"Historical events: {len(output['entities']['events'])}")
    print(f"Relationships: {len(output['relationships'])}")
    print("="*70)

    # Additional statistics
    print("\nBREAKDOWN BY ENTITY TYPE:")
    print(f"  - Places by type:")
    place_types = {}
    for place in output['entities']['places']:
        ptype = place.get('type', 'unknown')
        place_types[ptype] = place_types.get(ptype, 0) + 1
    for ptype, count in sorted(place_types.items()):
        print(f"      {ptype}: {count}")

    print(f"\n  - Institutions by type:")
    inst_types = {}
    for inst in output['entities']['institutions']:
        itype = inst.get('type', 'unknown')
        inst_types[itype] = inst_types.get(itype, 0) + 1
    for itype, count in sorted(inst_types.items()):
        print(f"      {itype}: {count}")

    print(f"\n  - Economic data by type:")
    econ_types = {}
    for econ in output['entities']['economic_data']:
        etype = econ.get('type', 'unknown')
        econ_types[etype] = econ_types.get(etype, 0) + 1
    for etype, count in sorted(econ_types.items()):
        print(f"      {etype}: {count}")

    print(f"\n  - Infrastructure by type:")
    infra_types = {}
    for infra in output['entities']['infrastructure']:
        itype = infra.get('type', 'unknown')
        infra_types[itype] = infra_types.get(itype, 0) + 1
    for itype, count in sorted(infra_types.items()):
        print(f"      {itype}: {count}")

    print(f"\nFILE LOCATION: {output_path}")
    print("="*70)


if __name__ == "__main__":
    main()
