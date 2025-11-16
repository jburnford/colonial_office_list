#!/usr/bin/env python3
"""
Extract comprehensive knowledge graph data from 1932 Colonial Office List files.
Follows EXTRACTION_METHODOLOGY.md and json_schema_template.json specifications.
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
        self.places = {}  # id -> place object
        self.people = {}  # id -> person object
        self.institutions = {}  # id -> institution object
        self.economic_data = {}  # id -> economic_data object
        self.infrastructure = {}  # id -> infrastructure object
        self.demographics = {}  # id -> demographic object
        self.events = {}  # id -> event object
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
        self.person_cache = {}  # name -> person_id mapping
        self.place_cache = {}   # name -> place_id mapping

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

    def extract_text_sections(self, text: str) -> Dict[str, str]:
        """Extract major sections from raw text."""
        sections = {
            'header': '',
            'geographic': '',
            'history': '',
            'climate': '',
            'population': '',
            'economy': '',
            'infrastructure': '',
            'government': '',
            'administration': '',
            'remaining': ''
        }

        # Simple section extraction
        current_section = 'header'
        lines = text.split('\n')

        for line in lines:
            line_lower = line.lower().strip()
            if not line_lower:
                continue

            # Detect section headers
            if any(x in line_lower for x in ['history', 'constitution', 'treaty']):
                current_section = 'history'
            elif any(x in line_lower for x in ['climate', 'temperature', 'rainfall']):
                current_section = 'climate'
            elif any(x in line_lower for x in ['population', 'census', 'inhabitants']):
                current_section = 'population'
            elif any(x in line_lower for x in ['trade', 'commerce', 'export', 'import', 'revenue', 'expenditure']):
                current_section = 'economy'
            elif any(x in line_lower for x in ['railway', 'telegraph', 'postal', 'dock', 'harbour', 'road', 'infrastructure']):
                current_section = 'infrastructure'
            elif any(x in line_lower for x in ['government', 'governor', 'council', 'legislative']):
                current_section = 'government'
            elif any(x in line_lower for x in ['administration', 'officer', 'resident', 'commissioner']):
                current_section = 'administration'
            elif 'situation' in line_lower or 'area' in line_lower or 'latitude' in line_lower:
                current_section = 'geographic'

            if current_section in sections:
                sections[current_section] += line + '\n'
            else:
                sections['remaining'] += line + '\n'

        return sections

    def extract_coordinates(self, text: str) -> Optional[Dict[str, str]]:
        """Extract latitude/longitude from text."""
        # Pattern: "lat. 12° 47' N. and long. 45° 10' E."
        pattern = r"lat\.\s+([0-9°′']+\s+[NSEW]\.?)\s+and\s+long\.\s+([0-9°′']+\s+[NSEW]\.?)"
        match = re.search(pattern, text, re.IGNORECASE)

        if match:
            return {
                "latitude": match.group(1).strip(),
                "longitude": match.group(2).strip()
            }

        # Alternative pattern
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
        # Pattern: "75 square miles" or "9,000 square miles"
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

    def extract_population_data(self, text: str, colony: str) -> Optional[Dict[str, Any]]:
        """Extract population figures and demographics."""
        # Look for population tables or statements
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

        # Patterns for official listings
        person_pattern = r"^([A-Z][a-z\s\-\.]+(?:,\s*[A-Z]\.?[a-z\-\.]*)*),?\s+([A-Z]\.?[A-Z]\.?[A-Z]\.?|[A-Z][a-z]+)"

        i = 0
        while i < len(lines):
            line = lines[i].strip()

            # Look for titles and names
            if any(title in line for title in ['Lt.-Col', 'Col.', 'Major', 'Rev.', 'Sir', 'Mr.', 'Mrs.', 'Dr.', 'Esq.', 'Capt.']):
                # Try to parse person line
                person_data = self._parse_person_line(line, colony)
                if person_data:
                    people.append(person_data)

            i += 1

        return people

    def _parse_person_line(self, line: str, colony: str) -> Optional[Dict[str, Any]]:
        """Parse a single person line."""
        if not line or line.count(',') < 1:
            return None

        # Extract name and position
        person_id = self.generate_id("person")

        # Parse components: Title + Name (comma) Position/Title (Optional: honors/details)
        parts = [p.strip() for p in line.split(',')]

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
            (r'^(Col\.)\s+', 'Col.'),
            (r'^(Major)\s+', 'Major'),
            (r'^(Rev\.)\s+', 'Rev.'),
            (r'^(Sir)\s+', 'Sir'),
            (r'^(Dr\.)\s+', 'Dr.'),
            (r'^(Capt\.)\s+', 'Capt.'),
        ]

        for pattern, title in title_patterns:
            if re.search(pattern, full_line):
                titles.append(title)
                name = re.sub(pattern, '', full_line).strip()
                break

        # Extract honors (K.C.M.G., C.B., O.B.E., etc.)
        honor_pattern = r'\b([A-Z]\.?[A-Z]\.?[A-Z]\.?)\b'
        honor_matches = re.findall(honor_pattern, name)
        for honor in honor_matches:
            if honor not in titles and len(honor) >= 3:
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
                "title": position_info[:100],  # Truncate long titles
                "location": colony,
                "year": "1932",
                "status": "permanent"
            }

            # Check for acting/vacant status
            if 'acting' in position_info.lower():
                position["status"] = "acting"
            elif 'vacant' in position_info.lower():
                position["status"] = "vacant"

            # Try to extract salary
            salary_match = re.search(r'£\s*([0-9,]+)', position_info)
            if salary_match:
                salary_amount = int(salary_match.group(1).replace(',', ''))
                position["salary"] = {
                    "amount": salary_amount,
                    "currency": "£",
                    "period": "annual"
                }

            person["positions"].append(position)

        return person

    def extract_economic_data(self, text: str, colony: str) -> List[Dict[str, Any]]:
        """Extract revenue, expenditure, trade, and economic data."""
        economic_items = []
        lines = text.split('\n')

        # Look for revenue/expenditure tables
        in_table = False
        table_data = []

        for i, line in enumerate(lines):
            line = line.strip()

            # Detect revenue/expenditure section
            if 'REVENUE' in line and 'EXPENDITURE' in line:
                in_table = True
                continue

            if in_table and line and '|' in line:
                # Parse table row
                cells = [cell.strip() for cell in line.split('|')]
                cells = [c for c in cells if c]

                if len(cells) >= 2:
                    # Try to parse year and amounts
                    year_match = re.search(r'\d{4}', cells[0])
                    if year_match:
                        year = year_match.group()

                        # Extract revenue and expenditure
                        for idx, cell in enumerate(cells[1:]):
                            amount_match = re.search(r'([0-9,]+)', cell)
                            if amount_match:
                                amount = int(amount_match.group(1).replace(',', ''))

                                if idx == 0:
                                    econ_id = self.generate_id("economic")
                                    economic_items.append({
                                        "id": econ_id,
                                        "type": "revenue",
                                        "location": colony,
                                        "year": "1932",
                                        "data": {
                                            "category": f"Revenue {year}",
                                            "value": amount,
                                            "currency": "£"
                                        }
                                    })
                                elif idx == 1:
                                    econ_id = self.generate_id("economic")
                                    economic_items.append({
                                        "id": econ_id,
                                        "type": "expenditure",
                                        "location": colony,
                                        "year": "1932",
                                        "data": {
                                            "category": f"Expenditure {year}",
                                            "value": amount,
                                            "currency": "£"
                                        }
                                    })
            elif in_table and not line:
                in_table = False

        return economic_items

    def extract_geographic_entities(self, text: str, colony_name: str) -> List[Dict[str, Any]]:
        """Extract geographic places mentioned in text."""
        places = []

        # Create main colony entry
        colony_id = self.generate_id("place")
        self.place_cache[colony_name] = colony_id

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

        # Extract other geographic entities mentioned
        # Pattern: "City of X", "Island of Y", etc.
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

    def extract_institutions(self, text: str, colony: str) -> List[Dict[str, Any]]:
        """Extract governmental and institutional entities."""
        institutions = []
        lines = text.split('\n')

        # Institutional patterns
        institution_patterns = [
            (r'(?:Executive|Legislative|Privy)\s+Council', 'council'),
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

        # Event patterns: dates and key events
        event_pattern = r'(?:In|By|On|During)\s+(\d{4}|[A-Z][a-z]+\s+\d{1,2},?\s+\d{4})\s+(.{20,150}?)(?:\.|,)'

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

                    # Classify event type
                    if any(x in description.lower() for x in ['treaty', 'agreement', 'signed']):
                        event_type = "treaty"
                    elif any(x in description.lower() for x in ['ceded', 'obtained', 'acquired']):
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

        # Infrastructure patterns
        infra_patterns = [
            (r'(?:Railway|Railroad)\s+([^:\.]*)', 'railway'),
            (r'(?:Telegraph|Telephone)\s+([^:\.]*)', 'telegraph'),
            (r'(?:Postal|Mail)\s+(?:route|service)\s+([^:\.]*)', 'postal_route'),
            (r'(?:Dock|Wharf|Harbor|Harbour)\s+([^:\.]*)', 'dock'),
            (r'(?:Road|Street|Highway)\s+([^:\.]*)', 'road'),
            (r'(?:Bridge|Causeway)\s+([^:\.]*)', 'bridge'),
        ]

        seen_infra = set()

        for pattern, infra_type in infra_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                name = match.group(1).strip()
                if name and name not in seen_infra:
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
            'economic_data': self.extract_economic_data(content, colony_name),
            'infrastructure': self.extract_infrastructure(content, colony_name),
            'demographics': [],
            'events': self.extract_historical_events(content, colony_name)
        }

        # Try to extract demographics
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
                            "title": position.get('title', '')
                        }
                    })

    def generate_output(self) -> Dict[str, Any]:
        """Generate the final JSON output."""
        output = {
            "metadata": {
                "year": "1932",
                "source_directory": str(self.source_dir),
                "extraction_date": datetime.utcnow().isoformat() + "Z",
                "processing_notes": "Automated extraction from Colonial Office List 1932 manual parsed files. 47 colonies/territories processed.",
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
        print(f"Starting knowledge graph extraction for 1932...")
        print(f"Source directory: {self.source_dir}")

        # List all colony files
        colony_files = sorted(self.source_dir.glob("*.md"))
        print(f"Found {len(colony_files)} colony files")

        # Process each file
        extractions = []
        for i, filepath in enumerate(colony_files):
            print(f"  Processing {i+1}/{len(colony_files)}: {filepath.stem}")
            extraction = self.process_colony_file(filepath)
            extractions.append(extraction)

        # Merge all extractions
        print(f"Merging {len(extractions)} extraction results...")
        self.merge_extractions(extractions)

        # Build relationships
        print("Building entity relationships...")
        self.build_relationships()

        # Generate output
        print("Generating output JSON...")
        output = self.generate_output()

        return output


def main():
    source_dir = "/home/user/colonial_office_list/output_2/1932_manual_parsed"
    output_dir = "/home/user/colonial_office_list/knowledge_graph_extracts"

    extractor = KnowledgeGraphExtractor(source_dir, output_dir)
    output = extractor.run()

    # Save output
    output_file = Path(output_dir) / "1932_extracted.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\nExtraction complete!")
    print(f"Output saved to: {output_file}")

    # Print summary statistics
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
