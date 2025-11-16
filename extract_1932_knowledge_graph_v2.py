#!/usr/bin/env python3
"""
Extract comprehensive knowledge graph data from 1932 Colonial Office List files.
Version 2: Improved economic data and table parsing
"""

import os
import json
import re
from datetime import datetime
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Any, Optional, Tuple

class KnowledgeGraphExtractor:
    def __init__(self, source_dir: str, output_dir: str):
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

    def extract_revenue_expenditure(self, text: str, colony: str) -> List[Dict[str, Any]]:
        """Extract revenue and expenditure data from tables."""
        economic_items = []

        # Split text to find revenue/expenditure section
        sections = text.split('\n')
        in_revenue_section = False
        table_text = []

        for i, line in enumerate(sections):
            if 'REVENUE' in line and 'EXPENDITURE' in line:
                in_revenue_section = True
                # Collect next lines that form the table
                j = i + 1
                while j < len(sections) and j < i + 10:
                    table_text.append(sections[j])
                    j += 1
                break

        if table_text:
            table_str = '\n'.join(table_text)
            rows = self.parse_markdown_table(table_str)

            if rows:
                for row in rows:
                    # Try to find year, revenue, and expenditure
                    year = None
                    revenue = None
                    expenditure = None

                    for key, value in row.items():
                        # Find year column
                        year_match = re.search(r'\d{4}', value)
                        if year_match:
                            year = year_match.group()

                        # Find numeric values
                        num_match = re.search(r'([0-9,]+)', value)
                        if num_match:
                            amount = int(num_match.group(1).replace(',', ''))

                            # Try to classify as revenue or expenditure
                            if revenue is None:
                                revenue = amount
                            elif expenditure is None:
                                expenditure = amount

                    if year and revenue:
                        econ_id = self.generate_id("economic")
                        economic_items.append({
                            "id": econ_id,
                            "type": "revenue",
                            "location": colony,
                            "year": "1932",
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
                            "year": "1932",
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

        # Pattern: "Population at 1931 Census, 188"
        pattern = r"Population\s+(?:at\s+)?(\d{4})?\s+[Cc]ensus[,:]?\s+([0-9,]+)"
        for line in lines:
            match = re.search(pattern, line)
            if match:
                total_population = int(match.group(2).replace(',', ''))
                break

        # Pattern: "population 34,471"
        if not total_population:
            pattern2 = r"population\s+([0-9,]+)"
            for line in lines:
                matches = re.findall(pattern2, line, re.IGNORECASE)
                if matches:
                    total_population = int(matches[0].replace(',', ''))
                    break

        if total_population:
            demographics = {
                "id": demo_id,
                "location": colony,
                "year": "1932",
                "total_population": total_population,
                "breakdowns": []
            }

            # Extract ethnic breakdowns if available
            ethnic_pattern = r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+([0-9,]+)"
            for line in lines:
                if any(x in line for x in ['White', 'Chinese', 'Black', 'Indian', 'Native', 'European', 'Asian']):
                    matches = re.findall(ethnic_pattern, line)
                    for match in matches:
                        if match[0] not in ['The', 'A', 'And']:
                            count = int(match[1].replace(',', ''))
                            demographics["breakdowns"].append({
                                "category": match[0],
                                "count": count,
                                "subcategories": {}
                            })

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
            if any(title in line for title in ['Lt.-Col', 'Col.', 'Major', 'Rev.', 'Sir', 'Mr.', 'Mrs.', 'Dr.', 'Esq.', 'Capt.', 'Lieut', 'Captain']):
                person_data = self._parse_person_line(line, colony)
                if person_data:
                    people.append(person_data)

            i += 1

        return people

    def _parse_person_line(self, line: str, colony: str) -> Optional[Dict[str, Any]]:
        """Parse a single person line."""
        if not line or len(line) < 3:
            return None

        person_id = self.generate_id("person")

        # Extract title and name first
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
            if honor not in titles and len(honor) >= 3:
                honors.append(honor)
                name = name.replace(honor, '').strip()

        # Also try single letter honors like "C.I.E." etc
        honor_pattern2 = r'\b([A-Z]\.[A-Z]\.[A-Z]\.?)\b'
        honor_matches2 = re.findall(honor_pattern2, name)
        for honor in honor_matches2:
            if honor not in honors and honor not in titles:
                honors.append(honor)
                name = name.replace(honor, '').strip()

        name = re.sub(r'\s+', ' ', name).strip()

        if not name or len(name) < 2:
            return None

        person = {
            "id": person_id,
            "name": name,
            "titles": titles,
            "honors": honors,
            "positions": []
        }

        # Parse position info
        if position_info:
            position = {
                "title": position_info[:150],
                "location": colony,
                "year": "1932",
                "status": "permanent"
            }

            # Check for acting/vacant status
            if 'acting' in position_info.lower():
                position["status"] = "acting"
            elif 'vacant' in position_info.lower():
                position["status"] = "vacant"
            elif 'temporary' in position_info.lower():
                position["status"] = "temporary"

            # Try to extract salary
            salary_match = re.search(r'£\s*([0-9,]+)', position_info)
            if salary_match:
                salary_amount = int(salary_match.group(1).replace(',', ''))
                position["salary"] = {
                    "amount": salary_amount,
                    "currency": "£",
                    "period": "annual"
                }

            # Extract allowances
            allowance_pattern = r'([A-Za-z\s]+)\s+£\s*([0-9,]+)'
            allowance_matches = re.findall(allowance_pattern, position_info)
            allowances = []
            for allowance_type, amount in allowance_matches:
                allowance_type = allowance_type.strip()
                if allowance_type not in ['']:
                    allowances.append({
                        "type": allowance_type[:50],
                        "amount": int(amount.replace(',', '')),
                        "currency": "£"
                    })

            if allowances:
                position["allowances"] = allowances

            person["positions"].append(position)

        return person

    def extract_geographic_entities(self, text: str, colony_name: str) -> List[Dict[str, Any]]:
        """Extract geographic places mentioned in text."""
        places = []

        # Create main colony entry
        colony_id = self.generate_id("place")
        self.place_cache[colony_name] = colony_id

        # Extract coordinates
        coordinates = self.extract_coordinates(text)
        area = self.extract_area(text)

        colony_place = {
            "id": colony_id,
            "name": colony_name,
            "type": "colony",
            "year": "1932"
        }

        if coordinates:
            colony_place["coordinates"] = coordinates
        if area:
            colony_place["area"] = area

        places.append(colony_place)

        # Extract other geographic entities
        geo_patterns = [
            (r'(?:City|Town|Settlement) of ([A-Z][a-z\s\-]+)', 'city'),
            (r'(?:Island|Isles?) of ([A-Z][a-z\s\-]+)', 'island'),
            (r'(?:Peninsula|Cape|Point) of ([A-Z][a-z\s\-]+)', 'feature'),
            (r'(?:River|Stream) ([A-Z][a-z\s\-]+)', 'river'),
            (r'(?:Mountain|Mount|Hill) ([A-Z][a-z\s\-]+)', 'mountain'),
            (r'(?:Bay|Gulf|Strait) of ([A-Z][a-z\s\-]+)', 'bay'),
            (r'(?:Harbor|Harbour|Port) of ([A-Z][a-z\s\-]+)', 'harbor'),
        ]

        for pattern, geo_type in geo_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if match not in self.place_cache:
                    place_id = self.generate_id("place")
                    self.place_cache[match] = place_id

                    places.append({
                        "id": place_id,
                        "name": match,
                        "type": geo_type,
                        "parent_location": colony_id,
                        "year": "1932"
                    })

        return places

    def extract_coordinates(self, text: str) -> Optional[Dict[str, str]]:
        """Extract latitude/longitude from text."""
        pattern = r"lat\.\s+([0-9°′']+\s+[NSEW]\.?)\s+and\s+long\.\s+([0-9°′']+\s+[NSEW]\.?)"
        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            return {
                "latitude": match.group(1).strip(),
                "longitude": match.group(2).strip()
            }

        pattern2 = r"between\s+([0-9°′']+)\s+and\s+([0-9°′']+)\s+N\.\s+lat\.\s*,?\s+and\s+([0-9°′']+)\s+and\s+([0-9°′']+)\s+([EW])\s+long\."
        match2 = re.search(pattern2, text, re.IGNORECASE)
        if match2:
            return {
                "latitude": f"{match2.group(1)}-{match2.group(2)} N",
                "longitude": f"{match2.group(3)}-{match2.group(4)} {match2.group(5)}"
            }

        return None

    def extract_area(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract area measurements from text."""
        patterns = [
            r"(\d{1,3}(?:,\d{3})*)\s+(?:square\s+)?miles?",
            r"(\d{1,3}(?:,\d{3})*)\s+(?:square\s+)?feet",
            r"(\d{1,3}(?:,\d{3})*)\s+acres?"
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                value = float(match.group(1).replace(',', ''))
                if 'feet' in text[match.start():match.end()].lower():
                    unit = 'square feet'
                elif 'acre' in text[match.start():match.end()].lower():
                    unit = 'acres'
                else:
                    unit = 'square miles'
                return {"value": value, "unit": unit}

        return None

    def extract_institutions(self, text: str, colony: str) -> List[Dict[str, Any]]:
        """Extract governmental and institutional entities."""
        institutions = []
        lines = text.split('\n')

        institution_patterns = [
            (r'(?:Executive|Legislative|Privy)\s+Council', 'executive_council'),
            (r'(?:Supreme|Magistrate\'s|Police)\s+Court', 'court'),
            (r'(?:Colonial|Colonial\s+Secretary\'s)\s+Office', 'department'),
            (r'(?:Treasury|Public\s+Works|Survey)\s+(?:Department|Office)', 'department'),
            (r'(?:Military|Police|Garrison)', 'military_unit'),
            (r'(?:Hospital|Medical)\s+(?:Service|Department)', 'medical'),
            (r'(?:Church|Cathedral|Mosque|Temple)', 'religious'),
            (r'(?:Bank|Banking\s+Corporation)', 'bank'),
            (r'(?:University|School|College)', 'educational'),
        ]

        seen_institutions = set()

        for line in lines:
            for pattern, inst_type in institution_patterns:
                matches = re.findall(pattern, line, re.IGNORECASE)
                for match in matches:
                    if match not in seen_institutions:
                        seen_institutions.add(match)
                        inst_id = self.generate_id("institution")

                        institutions.append({
                            "id": inst_id,
                            "name": match,
                            "type": inst_type,
                            "location": colony,
                            "year": "1932"
                        })

        return institutions

    def extract_historical_events(self, text: str, colony: str) -> List[Dict[str, Any]]:
        """Extract historical events and dates mentioned."""
        events = []
        lines = text.split('\n')

        event_pattern = r'(?:In|By|On|During|Since)\s+(\d{4}|[A-Z][a-z]+\s+\d{1,2},?\s+\d{4})\s+(.{20,150}?)(?:\.|,)'

        seen_events = set()

        for line in lines:
            matches = re.finditer(event_pattern, line)
            for match in matches:
                date = match.group(1)
                description = match.group(2).strip()

                event_key = (date, description[:50])
                if event_key not in seen_events:
                    seen_events.add(event_key)

                    event_id = self.generate_id("event")
                    event_type = "other"

                    if any(x in description.lower() for x in ['treaty', 'agreement', 'signed']):
                        event_type = "treaty"
                    elif any(x in description.lower() for x in ['ceded', 'obtained', 'acquired', 'captured']):
                        event_type = "cession"
                    elif any(x in description.lower() for x in ['established', 'founded', 'constituted']):
                        event_type = "establishment"
                    elif any(x in description.lower() for x in ['rebellion', 'revolt', 'uprising']):
                        event_type = "rebellion"

                    events.append({
                        "id": event_id,
                        "date": date,
                        "type": event_type,
                        "description": description[:200],
                        "locations": [self.place_cache.get(colony, colony)],
                        "year_mentioned": "1932"
                    })

        return events

    def extract_infrastructure(self, text: str, colony: str) -> List[Dict[str, Any]]:
        """Extract infrastructure information."""
        infrastructure = []

        infra_patterns = [
            (r'(?:Railway|Railroad)\s+([^:\.]+)', 'railway'),
            (r'(?:Telegraph|Telephone)\s+([^:\.]+)', 'telegraph'),
            (r'(?:Postal|Mail)\s+(?:route|service)\s+([^:\.]+)', 'postal_route'),
            (r'(?:Dock|Wharf|Harbor|Harbour)\s+([^:\.]+)', 'dock'),
            (r'(?:Road|Street|Highway)\s+([^:\.]+)', 'road'),
            (r'(?:Bridge|Causeway)\s+([^:\.]+)', 'bridge'),
        ]

        seen_infra = set()

        for pattern, infra_type in infra_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                name = match.group(1).strip()
                if name and name not in seen_infra and len(name) < 100:
                    seen_infra.add(name)

                    infra_id = self.generate_id("infrastructure")
                    infrastructure.append({
                        "id": infra_id,
                        "type": infra_type,
                        "name": name[:100],
                        "location": colony,
                        "year": "1932"
                    })

        return infrastructure

    def process_colony_file(self, filepath: Path) -> Dict[str, List[Dict]]:
        """Process a single colony file and extract all entities."""
        colony_name = filepath.stem
        self.colonies_processed.append(colony_name)

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
            return {
                'places': [], 'people': [], 'institutions': [],
                'economic_data': [], 'infrastructure': [],
                'demographics': [], 'events': []
            }

        extraction_result = {
            'places': self.extract_geographic_entities(content, colony_name),
            'people': self.extract_people(content, colony_name),
            'institutions': self.extract_institutions(content, colony_name),
            'economic_data': self.extract_revenue_expenditure(content, colony_name),
            'infrastructure': self.extract_infrastructure(content, colony_name),
            'demographics': [],
            'events': self.extract_historical_events(content, colony_name)
        }

        demo = self.extract_population_data(content, colony_name)
        if demo:
            extraction_result['demographics'].append(demo)

        return extraction_result

    def merge_extractions(self, extractions: List[Dict[str, List[Dict]]]):
        """Merge all extracted data from multiple colonies."""
        for extraction in extractions:
            self.places.update({p['id']: p for p in extraction['places']})
            self.people.update({p['id']: p for p in extraction['people']})
            self.institutions.update({i['id']: i for i in extraction['institutions']})
            self.economic_data.update({e['id']: e for e in extraction['economic_data']})
            self.infrastructure.update({i['id']: i for i in extraction['infrastructure']})
            self.demographics.update({d['id']: d for d in extraction['demographics']})
            self.events.update({e['id']: e for e in extraction['events']})

    def build_relationships(self):
        """Build relationships between entities."""
        # LOCATED_IN relationships
        for place_id, place in self.places.items():
            if 'parent_location' in place and place['parent_location']:
                self.relationships.append({
                    "source_id": place_id,
                    "relationship_type": "LOCATED_IN",
                    "target_id": place['parent_location'],
                    "properties": {"year": "1932"}
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
                            "year": "1932",
                            "title": position.get('title', '')[:100]
                        }
                    })

    def generate_output(self) -> Dict[str, Any]:
        """Generate the final JSON output."""
        output = {
            "metadata": {
                "year": "1932",
                "source_directory": str(self.source_dir),
                "extraction_date": datetime.utcnow().isoformat() + "Z",
                "processing_notes": "Automated extraction from Colonial Office List 1932 manual parsed files. 47 colonies/territories processed with enhanced economic data extraction.",
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
        print(f"Starting knowledge graph extraction for 1932 (v2)...")
        print(f"Source directory: {self.source_dir}")

        colony_files = sorted(self.source_dir.glob("*.md"))
        print(f"Found {len(colony_files)} colony files")

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


def main():
    source_dir = "/home/user/colonial_office_list/output_2/1932_manual_parsed"
    output_dir = "/home/user/colonial_office_list/knowledge_graph_extracts"

    extractor = KnowledgeGraphExtractor(source_dir, output_dir)
    output = extractor.run()

    output_file = Path(output_dir) / "1932_extracted.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\nExtraction complete!")
    print(f"Output saved to: {output_file}")

    print("\n=== EXTRACTION SUMMARY ===")
    print(f"Colonies processed: {len(output['metadata']['colonies_processed'])}")
    print(f"Geographic entities: {len(output['entities']['places'])}")
    print(f"People extracted: {len(output['entities']['people'])}")
    print(f"Institutions: {len(output['entities']['institutions'])}")
    print(f"Economic records: {len(output['entities']['economic_data'])}")
    print(f"Infrastructure items: {len(output['entities']['infrastructure'])}")
    print(f"Demographic records: {len(output['entities']['demographics'])}")
    print(f"Historical events: {len(output['entities']['events'])}")
    print(f"Total relationships: {len(output['relationships'])}")


if __name__ == "__main__":
    main()
