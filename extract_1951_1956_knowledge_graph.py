#!/usr/bin/env python3
"""
Extract comprehensive knowledge graph data from 1951-1956 Colonial Office List files.
Processes all six years with full entity extraction and relationship mapping.
"""

import os
import json
import re
from datetime import datetime
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Any, Optional, Tuple

class KnowledgeGraphExtractor:
    def __init__(self, year: str, source_dir: str, output_dir: str):
        self.year = year
        self.source_dir = Path(source_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Entity storage
        self.places = {}
        self.people = {}
        self.institutions = {}
        self.economic_data = {}
        self.infrastructure = {}
        self.demographics = {}
        self.events = {}
        self.relationships = []

        # ID trackers
        self.place_id_counter = 0
        self.person_id_counter = 0
        self.institution_id_counter = 0
        self.economic_id_counter = 0
        self.infrastructure_id_counter = 0
        self.demographic_id_counter = 0
        self.event_id_counter = 0

        # Caches
        self.colonies_processed = []
        self.person_cache = {}
        self.place_cache = {}

    def generate_id(self, entity_type: str) -> str:
        """Generate unique ID for entity."""
        if entity_type == "place":
            self.place_id_counter += 1
            return f"place_{self.place_id_counter:04d}"
        elif entity_type == "person":
            self.person_id_counter += 1
            return f"person_{self.person_id_counter:04d}"
        elif entity_type == "institution":
            self.institution_id_counter += 1
            return f"institution_{self.institution_id_counter:04d}"
        elif entity_type == "economic":
            self.economic_id_counter += 1
            return f"economic_{self.economic_id_counter:04d}"
        elif entity_type == "infrastructure":
            self.infrastructure_id_counter += 1
            return f"infrastructure_{self.infrastructure_id_counter:04d}"
        elif entity_type == "demographic":
            self.demographic_id_counter += 1
            return f"demographic_{self.demographic_id_counter:04d}"
        elif entity_type == "event":
            self.event_id_counter += 1
            return f"event_{self.event_id_counter:04d}"
        return ""

    def parse_markdown_table(self, text: str) -> Optional[List[Dict[str, str]]]:
        """Parse markdown tables from text."""
        rows = []
        lines = text.strip().split('\n')

        header = None
        separator_found = False

        for line in lines:
            if not line.strip() or not '|' in line:
                continue

            cells = [cell.strip() for cell in line.split('|')]
            cells = [c for c in cells if c]

            if not separator_found:
                # Check if this is separator row
                if all(c.startswith('-') or c.startswith(':') or c.endswith('-') for c in cells):
                    separator_found = True
                    continue

                # This is header row
                if not header:
                    header = cells
                    continue

            # Data row
            if header and len(cells) >= len(header):
                row = {}
                for i, h in enumerate(header):
                    if i < len(cells):
                        row[h] = cells[i]
                rows.append(row)

        return rows if rows else None

    def extract_colony_place(self, filename: str, text: str) -> Optional[Dict[str, Any]]:
        """Extract the main colony/territory as a place entity."""
        colony_name = filename.replace('.md', '').replace('_', ' ')

        place_id = self.generate_id("place")
        self.place_cache[colony_name] = place_id

        # Extract coordinates if present (pattern: "latitude XX° YY' N. and longitude XX° YY' W.")
        coords = {"latitude": None, "longitude": None}
        coord_pattern = r"latitude\s+([\d°\'\s\.\,NSEW]+)\s+and\s+longitude\s+([\d°\'\s\.\,NSEW]+)"
        match = re.search(coord_pattern, text, re.IGNORECASE)
        if match:
            coords["latitude"] = match.group(1).strip()
            coords["longitude"] = match.group(2).strip()

        # Extract area if present
        area = {}
        area_pattern = r"total\s+area\s+.*?(\d+(?:\.\d+)?)\s+(square\s+miles|acres|square\s+kilometres?)"
        match = re.search(area_pattern, text, re.IGNORECASE)
        if match:
            area["value"] = float(match.group(1))
            area["unit"] = match.group(2)

        place = {
            "id": place_id,
            "name": colony_name,
            "type": "colony",
            "year": self.year
        }

        if coords["latitude"] or coords["longitude"]:
            place["coordinates"] = {k: v for k, v in coords.items() if v}
        if area:
            place["area"] = area

        # Add description from first few lines
        lines = text.split('\n')
        description_lines = []
        for i, line in enumerate(lines[:20]):
            if line.strip() and not any(x in line for x in ['===', '---', '###', '##']):
                description_lines.append(line.strip())
        if description_lines:
            place["description"] = ' '.join(description_lines)[:500]

        return place

    def extract_revenue_expenditure(self, text: str, colony: str) -> List[Dict[str, Any]]:
        """Extract revenue and expenditure data from tables."""
        economic_items = []

        # Look for revenue/expenditure sections
        sections = text.split('\n\n')
        for section in sections:
            if 'Revenue' in section or 'Expenditure' in section:
                lines = section.split('\n')
                table_text = []

                for line in lines:
                    if '|' in line:
                        table_text.append(line)

                if table_text:
                    table_str = '\n'.join(table_text)
                    rows = self.parse_markdown_table(table_str)

                    if rows:
                        for row in rows:
                            year = None
                            revenue = None
                            expenditure = None

                            for key, value in row.items():
                                # Try to extract year
                                year_match = re.search(r'\d{4}', value)
                                if year_match and not year:
                                    year = year_match.group()

                                # Try to extract numeric values
                                num_match = re.search(r'([\d,]+)', value)
                                if num_match:
                                    try:
                                        amount = int(num_match.group(1).replace(',', ''))

                                        # Classify as revenue or expenditure based on column position
                                        if 'revenue' in key.lower() and revenue is None:
                                            revenue = amount
                                        elif 'expenditure' in key.lower() and expenditure is None:
                                            expenditure = amount
                                        elif revenue is None:
                                            revenue = amount
                                        elif expenditure is None:
                                            expenditure = amount
                                    except:
                                        pass

                            if year and revenue:
                                econ_id = self.generate_id("economic")
                                economic_items.append({
                                    "id": econ_id,
                                    "type": "revenue",
                                    "location": colony,
                                    "year": self.year,
                                    "data": {
                                        "category": f"Revenue {year}",
                                        "value": revenue,
                                        "currency": "£",
                                        "source": "Colonial Office List"
                                    }
                                })

                            if year and expenditure:
                                econ_id = self.generate_id("economic")
                                economic_items.append({
                                    "id": econ_id,
                                    "type": "expenditure",
                                    "location": colony,
                                    "year": self.year,
                                    "data": {
                                        "category": f"Expenditure {year}",
                                        "value": expenditure,
                                        "currency": "£",
                                        "source": "Colonial Office List"
                                    }
                                })

        return economic_items

    def extract_population_data(self, text: str, colony: str) -> Optional[Dict[str, Any]]:
        """Extract population figures and demographics."""
        lines = text.split('\n')
        demo_id = self.generate_id("demographic")
        total_population = None

        # Pattern: "Population: 34,471" or "Total population 35,560"
        patterns = [
            r"total\s+population[,:]?\s+([0-9,]+)",
            r"population[,:]?\s+([0-9,]+)",
            r"Population\s+(?:at\s+)?(\d{4})?\s+[Cc]ensus[,:]?\s+([0-9,]+)"
        ]

        for pattern in patterns:
            for line in lines:
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    # Handle two-group pattern
                    if len(match.groups()) == 2:
                        pop_str = match.group(2) if match.group(2) else match.group(1)
                    else:
                        pop_str = match.group(1) if match.group(1) else match.group(2) if len(match.groups()) > 1 else match.group(0)

                    try:
                        total_population = int(pop_str.replace(',', ''))
                        break
                    except:
                        pass

            if total_population:
                break

        if total_population:
            demographics = {
                "id": demo_id,
                "location": colony,
                "year": self.year,
                "total_population": total_population,
                "breakdowns": []
            }

            # Extract ethnic/racial breakdowns if available
            breakdown_lines = text.split('\n')
            for line in breakdown_lines:
                if any(x in line for x in ['White', 'Coloured', 'Chinese', 'Black', 'Indian', 'Native', 'European', 'Asian', 'African']):
                    # Try to extract category and count
                    matches = re.findall(r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s*\|?\s*([0-9,]+)", line)
                    for match in matches:
                        if match[0] not in ['The', 'A', 'And', 'Total']:
                            try:
                                count = int(match[1].replace(',', ''))
                                demographics["breakdowns"].append({
                                    "category": match[0],
                                    "count": count,
                                    "subcategories": {}
                                })
                            except:
                                pass

            return demographics

        return None

    def extract_people(self, text: str, colony: str) -> List[Dict[str, Any]]:
        """Extract individual people and their positions."""
        people = []
        lines = text.split('\n')

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # Look for titles and names
            if any(title in line for title in ['Lt.-Col', 'Col.', 'Major', 'Rev.', 'Sir', 'Mr.', 'Mrs.', 'Dr.', 'Esq.', 'Capt.', 'Lieut', 'Captain', 'Viscount', 'Baron', 'Admiral', 'General']):
                person_data = self._parse_person_line(line, colony)
                if person_data:
                    people.append(person_data)

            i += 1

        return people

    def _parse_person_line(self, line: str, colony: str) -> Optional[Dict[str, Any]]:
        """Parse a single person line with name, titles, and positions."""
        if not line or len(line) < 3:
            return None

        person_id = self.generate_id("person")

        # Split on commas to separate name from position info
        parts = line.split(',')
        if len(parts) < 1:
            return None

        full_line = parts[0]
        position_info = ', '.join(parts[1:]) if len(parts) > 1 else ''

        # Extract titles
        titles = []
        honors = []
        name = full_line

        title_patterns = [
            (r'^(Viscount)\s+', 'Viscount'),
            (r'^(Baron)\s+', 'Baron'),
            (r'^(Admiral)\s+', 'Admiral'),
            (r'^(General)\s+', 'General'),
            (r'^(Lieut\.-Gen\.)\s+', 'Lieut.-Gen.'),
            (r'^(Lt\.-Col\.)\s+', 'Lt.-Col.'),
            (r'^(Lieut\.-Col\.)\s+', 'Lieut.-Col.'),
            (r'^(Col\.)\s+', 'Col.'),
            (r'^(Major)\s+', 'Major'),
            (r'^(Captain|Capt\.)\s+', 'Capt.'),
            (r'^(Rev\.)\s+', 'Rev.'),
            (r'^(Sir)\s+', 'Sir'),
            (r'^(Dr\.)\s+', 'Dr.'),
            (r'^(Mr\.)\s+', 'Mr.'),
            (r'^(Mrs\.)\s+', 'Mrs.'),
        ]

        for pattern, title in title_patterns:
            if re.search(pattern, full_line):
                titles.append(title)
                name = re.sub(pattern, '', full_line).strip()
                break

        # Extract honors (K.C.M.G., C.B., O.B.E., etc.)
        honor_pattern = r'\b([A-Z]\.(?:[A-Z]\.)*)\b'
        honor_matches = re.findall(honor_pattern, name)
        for honor in honor_matches:
            if honor not in titles and len(honor) >= 3 and '.' in honor:
                honors.append(honor)
                name = name.replace(honor, '').strip()

        # Clean up name
        name = re.sub(r'\s+', ' ', name).strip()

        if not name or len(name) < 2:
            return None

        # Extract salary if present
        salary = {}
        salary_pattern = r"£([0-9,]+)\s*p\.?a\.?"
        salary_match = re.search(salary_pattern, position_info)
        if salary_match:
            try:
                salary["amount"] = int(salary_match.group(1).replace(',', ''))
                salary["currency"] = "£"
                salary["period"] = "annual"
            except:
                pass

        # Extract position title
        position_title = ""
        if position_info:
            # Remove salary info to get position title
            position_title = re.sub(salary_pattern, '', position_info).strip()

        person = {
            "id": person_id,
            "name": name,
            "year": self.year
        }

        if titles:
            person["titles"] = titles
        if honors:
            person["honors"] = honors

        if position_title or salary:
            position = {
                "title": position_title if position_title else "Unknown",
                "location": colony,
                "year": self.year,
                "status": "permanent"
            }
            if salary:
                position["salary"] = salary
            person["positions"] = [position]

        return person

    def extract_institutions(self, text: str, colony: str) -> List[Dict[str, Any]]:
        """Extract governmental and administrative institutions."""
        institutions = []
        lines = text.split('\n')

        # Look for sections with institutional names
        institutional_keywords = ['COUNCIL', 'COURT', 'EXECUTIVE', 'LEGISLATIVE', 'DEPARTMENT', 'MINISTRY', 'BOARD']

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            if any(keyword in line for keyword in institutional_keywords):
                inst_id = self.generate_id("institution")
                inst_name = line.replace('#', '').replace('*', '').strip()

                # Determine type
                inst_type = "department"
                if 'EXECUTIVE' in line:
                    inst_type = "executive_council"
                elif 'LEGISLATIVE' in line:
                    inst_type = "legislative_council"
                elif 'COURT' in line:
                    inst_type = "court"
                elif 'BOARD' in line:
                    inst_type = "department"

                institution = {
                    "id": inst_id,
                    "name": inst_name,
                    "type": inst_type,
                    "location": colony,
                    "year": self.year,
                    "composition": {
                        "description": f"Members of {inst_name}",
                        "members": []
                    }
                }

                # Try to collect member information from following lines
                member_lines = []
                for j in range(i+1, min(i+20, len(lines))):
                    next_line = lines[j].strip()
                    if not next_line or any(kw in next_line for kw in institutional_keywords):
                        break
                    if next_line and not any(x in next_line for x in ['===', '---', '###']):
                        member_lines.append(next_line)

                if member_lines:
                    institution["composition"]["member_count"] = len(member_lines)

                institutions.append(institution)

            i += 1

        return institutions

    def extract_infrastructure(self, text: str, colony: str) -> List[Dict[str, Any]]:
        """Extract infrastructure information (roads, railways, telegraph, etc.)."""
        infrastructure = []
        lines = text.split('\n')

        # Look for infrastructure mentions
        infra_keywords = ['railway', 'telegraph', 'postal', 'road', 'dock', 'harbor', 'telephone', 'airport', 'aerodrome', 'pier']

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            if any(kw in line.lower() for kw in infra_keywords):
                infra_id = self.generate_id("infrastructure")

                # Determine type
                infra_type = "road"
                if 'railway' in line.lower():
                    infra_type = "railway"
                elif 'telegraph' in line.lower():
                    infra_type = "telegraph"
                elif 'postal' in line.lower():
                    infra_type = "postal_route"
                elif 'dock' in line.lower() or 'harbor' in line.lower():
                    infra_type = "dock"
                elif 'airport' in line.lower() or 'aerodrome' in line.lower():
                    infra_type = "public_building"

                # Extract length/distance if present
                specifications = {}
                length_pattern = r"(\d+(?:\.\d+)?)\s*(miles?|kilometres?|km)"
                length_match = re.search(length_pattern, line)
                if length_match:
                    specifications["length"] = {
                        "value": float(length_match.group(1)),
                        "unit": length_match.group(2)
                    }

                infrastructure_item = {
                    "id": infra_id,
                    "type": infra_type,
                    "name": line[:100],
                    "location": colony,
                    "year": self.year
                }

                if specifications:
                    infrastructure_item["specifications"] = specifications

                infrastructure.append(infrastructure_item)

            i += 1

        return infrastructure

    def extract_events(self, text: str, colony: str) -> List[Dict[str, Any]]:
        """Extract historical events and dates."""
        events = []
        lines = text.split('\n')

        # Look for event indicators
        event_keywords = ['established', 'founded', 'treaty', 'rebellion', 'independence', 'transfer', 'ceded', 'acquired']

        for line in lines:
            if any(kw in line.lower() for kw in event_keywords):
                event_id = self.generate_id("event")

                # Try to extract date
                date_pattern = r"(\d{4}|[A-Z][a-z]+\s+\d{1,2},?\s+\d{4}|[A-Z][a-z]+\s+\d{4})"
                date_match = re.search(date_pattern, line)
                date_str = date_match.group(1) if date_match else ""

                # Determine event type
                event_type = "other"
                if 'established' in line.lower() or 'founded' in line.lower():
                    event_type = "establishment"
                elif 'treaty' in line.lower():
                    event_type = "treaty"
                elif 'rebellion' in line.lower():
                    event_type = "rebellion"
                elif 'ceded' in line.lower() or 'transfer' in line.lower():
                    event_type = "transfer"

                event = {
                    "id": event_id,
                    "description": line[:200],
                    "type": event_type,
                    "locations": [self.place_cache.get(colony, "")],
                    "year_mentioned": self.year
                }

                if date_str:
                    event["date"] = date_str

                events.append(event)

        return events

    def process_colony_file(self, filepath: Path) -> Dict[str, Any]:
        """Process a single colony file."""
        filename = filepath.name
        colony_name = filename.replace('.md', '').replace('_', ' ')

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read()
        except Exception as e:
            print(f"    Error reading {filename}: {e}")
            return {}

        extraction = {
            "places": [],
            "people": [],
            "institutions": [],
            "economic_data": [],
            "infrastructure": [],
            "demographics": [],
            "events": []
        }

        # Extract colony as main place
        place = self.extract_colony_place(filename, text)
        if place:
            extraction["places"].append(place)

        # Extract all entity types
        extraction["people"] = self.extract_people(text, colony_name)
        extraction["institutions"] = self.extract_institutions(text, colony_name)
        extraction["economic_data"] = self.extract_revenue_expenditure(text, colony_name)
        extraction["infrastructure"] = self.extract_infrastructure(text, colony_name)
        extraction["demographics"] = [d for d in [self.extract_population_data(text, colony_name)] if d]
        extraction["events"] = self.extract_events(text, colony_name)

        self.colonies_processed.append(colony_name)
        return extraction

    def merge_extractions(self, extractions: List[Dict[str, Any]]):
        """Merge all colony extractions into unified stores."""
        for extraction in extractions:
            for place in extraction.get("places", []):
                self.places[place["id"]] = place

            for person in extraction.get("people", []):
                self.people[person["id"]] = person

            for institution in extraction.get("institutions", []):
                self.institutions[institution["id"]] = institution

            for econ in extraction.get("economic_data", []):
                self.economic_data[econ["id"]] = econ

            for infra in extraction.get("infrastructure", []):
                self.infrastructure[infra["id"]] = infra

            for demo in extraction.get("demographics", []):
                self.demographics[demo["id"]] = demo

            for event in extraction.get("events", []):
                self.events[event["id"]] = event

    def build_relationships(self):
        """Build relationships between entities."""
        # LOCATED_IN relationships for places
        for place_id, place in self.places.items():
            if place.get('parent_location'):
                self.relationships.append({
                    "source_id": place_id,
                    "relationship_type": "LOCATED_IN",
                    "target_id": place['parent_location'],
                    "properties": {"year": self.year}
                })

        # GOVERNED_BY relationships
        for person_id, person in self.people.items():
            for position in person.get('positions', []):
                location = position.get('location')
                if location in self.place_cache:
                    self.relationships.append({
                        "source_id": person_id,
                        "relationship_type": "GOVERNED_BY",
                        "target_id": self.place_cache[location],
                        "properties": {
                            "year": self.year,
                            "title": position.get('title', '')[:100]
                        }
                    })

    def generate_output(self) -> Dict[str, Any]:
        """Generate the final JSON output."""
        output = {
            "metadata": {
                "year": self.year,
                "source_directory": str(self.source_dir),
                "extraction_date": datetime.utcnow().isoformat() + "Z",
                "processing_notes": f"Automated extraction from Colonial Office List {self.year} manual parsed files. {len(self.colonies_processed)} colonies/territories processed.",
                "colonies_processed": sorted(self.colonies_processed)
            },
            "entities": {
                "places": list(self.places.values()),
                "people": list(self.people.values()),
                "institutions": list(self.institutions.values()),
                "economic_data": list(self.economic_data.values()),
                "infrastructure": list(self.infrastructure.values()),
                "demographics": list(self.demographics.values()),
                "events": list(self.events.values())
            },
            "relationships": self.relationships
        }

        return output

    def run(self) -> Dict[str, Any]:
        """Execute the full extraction pipeline."""
        print(f"Starting knowledge graph extraction for {self.year}...")
        print(f"Source directory: {self.source_dir}")

        if not self.source_dir.exists():
            print(f"ERROR: Source directory does not exist!")
            return {}

        colony_files = sorted(self.source_dir.glob("*.md"))
        print(f"Found {len(colony_files)} colony files")

        if not colony_files:
            print("ERROR: No colony files found!")
            return {}

        extractions = []
        for i, filepath in enumerate(colony_files):
            print(f"  Processing {i+1}/{len(colony_files)}: {filepath.stem}")
            extraction = self.process_colony_file(filepath)
            extractions.append(extraction)

        print(f"Merging {len(extractions)} extraction results...")
        self.merge_extractions(extractions)

        print("Building entity relationships...")
        self.build_relationships()

        print("Generating output JSON...")
        output = self.generate_output()

        return output


def process_year(year: str, output_dir: str):
    """Process a single year."""
    source_dir = f"/home/user/colonial_office_list/output_2/{year}_manual_parsed"

    extractor = KnowledgeGraphExtractor(year, source_dir, output_dir)
    output = extractor.run()

    if not output:
        print(f"ERROR: Failed to extract data for {year}")
        return False

    output_file = Path(output_dir) / f"{year}_extracted.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\nExtraction complete for {year}!")
    print(f"Output saved to: {output_file}")

    print(f"\n=== {year} EXTRACTION SUMMARY ===")
    print(f"Colonies processed: {len(output['metadata']['colonies_processed'])}")
    print(f"Geographic entities: {len(output['entities']['places'])}")
    print(f"People extracted: {len(output['entities']['people'])}")
    print(f"Institutions: {len(output['entities']['institutions'])}")
    print(f"Economic records: {len(output['entities']['economic_data'])}")
    print(f"Infrastructure items: {len(output['entities']['infrastructure'])}")
    print(f"Demographic records: {len(output['entities']['demographics'])}")
    print(f"Historical events: {len(output['entities']['events'])}")
    print(f"Total relationships: {len(output['relationships'])}")
    print("-" * 50)

    return True


def main():
    output_dir = "/home/user/colonial_office_list/knowledge_graph_extracts"
    years = ["1951", "1952", "1953", "1954", "1955", "1956"]

    print("=" * 60)
    print("COLONIAL OFFICE LIST KNOWLEDGE GRAPH EXTRACTION")
    print("Years 1951-1956")
    print("=" * 60)

    success_count = 0
    for year in years:
        try:
            if process_year(year, output_dir):
                success_count += 1
        except Exception as e:
            print(f"EXCEPTION in {year}: {e}")

    print("\n" + "=" * 60)
    print(f"FINAL SUMMARY: {success_count}/{len(years)} years processed successfully")
    print("=" * 60)


if __name__ == "__main__":
    main()
