#!/usr/bin/env python3
"""
Comprehensive Knowledge Graph Extraction for Colonial Office List 1919
Extracts geographic entities, people, institutions, economic data, infrastructure,
demographics, and historical events from all 42 colonies for 1919.
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Set, Optional, Any, Tuple
from collections import defaultdict
from datetime import datetime
import unicodedata


class KnowledgeGraphExtractor:
    """Extract structured knowledge graph data from 1919 Colonial Office List files"""

    def __init__(self, year: str = "1919"):
        self.year = year
        self.source_dir = Path(f"/home/user/colonial_office_list/output_2/{year}_manual_parsed")
        self.extraction_date = datetime.utcnow().isoformat() + "Z"

        # Entity collections
        self.places: Dict[str, Dict] = {}
        self.people: Dict[str, Dict] = {}
        self.institutions: Dict[str, Dict] = {}
        self.economic_data: List[Dict] = []
        self.infrastructure: List[Dict] = []
        self.demographics: List[Dict] = []
        self.events: List[Dict] = []
        self.relationships: List[Dict] = []

        # Entity ID tracking
        self.place_ids: Set[str] = set()
        self.person_ids: Set[str] = set()
        self.institution_ids: Set[str] = set()
        self.entity_counter = defaultdict(int)

        # Colonies processed
        self.colonies_processed: List[str] = []

    def generate_id(self, entity_type: str, name: str, location: str = "") -> str:
        """Generate unique ID for entity"""
        base = f"{entity_type}_{name.replace(' ', '_').replace(',', '').lower()}"
        if location:
            base = f"{base}_{location.replace(' ', '_').lower()}"

        self.entity_counter[base] += 1
        if self.entity_counter[base] > 1:
            return f"{base}_{self.entity_counter[base]}"
        return base

    def extract_numbers(self, text: str) -> List[Tuple[float, str]]:
        """Extract numbers and surrounding units from text"""
        pattern = r'([\d,]+\.?\d*)\s*([a-zA-Z°\'\"]*)'
        matches = re.findall(pattern, text)
        results = []
        for num, unit in matches:
            try:
                value = float(num.replace(',', ''))
                results.append((value, unit.strip()))
            except:
                pass
        return results

    def extract_coordinates(self, text: str) -> Optional[Dict]:
        """Extract latitude and longitude from text"""
        # Pattern: lat. XX° YY' (N|S) and long. XX° YY' (E|W)
        lat_pattern = r"lat\.?\s*([0-9°\'\s\.\-]*)[NS]?"
        long_pattern = r"long\.?\s*([0-9°\'\s\.\-]*)[EW]?"

        lat_match = re.search(lat_pattern, text, re.IGNORECASE)
        long_match = re.search(long_pattern, text, re.IGNORECASE)

        if lat_match or long_match:
            coords = {}
            if lat_match:
                coords['latitude'] = lat_match.group(0)
            if long_match:
                coords['longitude'] = long_match.group(0)
            if coords:
                return coords
        return None

    def extract_places_from_text(self, text: str, colony_name: str) -> List[Dict]:
        """Extract geographic entities from text"""
        places = []

        # Extract from coordinate patterns
        coord_pattern = r"([A-Z][a-zA-Z\s]+?)(?:\s+is\s+situated|,\s+(?:an|a)\s+(?:island|city|town|region))"

        for match in re.finditer(coord_pattern, text):
            place_name = match.group(1).strip()
            if len(place_name) < 100:  # Avoid overly long matches

                # Determine type
                place_type = "settlement"
                if "island" in text[max(0, match.start()-50):match.end()+50].lower():
                    place_type = "island"
                elif "river" in text[max(0, match.start()-50):match.end()+50].lower():
                    place_type = "river"
                elif "mountain" in text[max(0, match.start()-50):match.end()+50].lower():
                    place_type = "mountain"
                elif "harbor" in text[max(0, match.start()-50):match.end()+50].lower() or "harbour" in text[max(0, match.start()-50):match.end()+50].lower():
                    place_type = "harbor"
                elif "bay" in text[max(0, match.start()-50):match.end()+50].lower():
                    place_type = "bay"

                # Extract from context
                context = text[max(0, match.start()-200):min(len(text), match.end()+200)]
                coords = self.extract_coordinates(context)

                place_id = self.generate_id("place", place_name, colony_name)
                if place_id not in self.place_ids:
                    self.place_ids.add(place_id)
                    places.append({
                        'id': place_id,
                        'name': place_name,
                        'type': place_type,
                        'colony': colony_name,
                        'coordinates': coords,
                        'year': self.year
                    })

        # Add the colony itself
        colony_id = self.generate_id("place", colony_name)
        if colony_id not in self.place_ids:
            self.place_ids.add(colony_id)
            places.insert(0, {
                'id': colony_id,
                'name': colony_name,
                'type': 'colony',
                'coordinates': None,
                'year': self.year
            })

        return places

    def extract_people_from_text(self, text: str, colony_name: str) -> List[Dict]:
        """Extract people and their positions from text"""
        people = []

        # Patterns for administrative positions
        patterns = [
            # Governor, etc. format
            r"([A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?),\s*([A-Z][A-Z\.\s]+)?(?:Governor|Lieutenant-Governor|Resident|High Commissioner|Commissioner)",
            # Name with honors/titles in parentheses
            r"([A-Z][a-z]+\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)?),\s*([A-Z\.]+(?:\s+[A-Z\.]+)*)\.",
            # Position followed by name and salary
            r"(Governor|Colonial Secretary|Attorney-General|Resident|Commissioner),\s+([A-Z][a-z]+\s+[A-Z][a-z]+)",
        ]

        people_found = {}

        for pattern in patterns:
            for match in re.finditer(pattern, text):
                try:
                    if len(match.groups()) >= 2:
                        name = match.group(1).strip() if match.group(1) else match.group(2).strip()
                        if name and len(name) < 100:
                            # Check if this looks like a real name
                            if re.match(r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*$', name):
                                person_id = self.generate_id("person", name, colony_name)
                                if person_id not in people_found:
                                    people_found[person_id] = {
                                        'id': person_id,
                                        'name': name,
                                        'positions': []
                                    }
                except:
                    pass

        # Extract salary information
        salary_pattern = r"(?:salary|payment|income).*?([0-9,]+)\s*[£$]"
        salary_matches = {}
        for match in re.finditer(salary_pattern, text, re.IGNORECASE):
            try:
                amount = int(match.group(1).replace(',', ''))
                # Associate with nearby name
                context_start = max(0, match.start() - 200)
                context = text[context_start:match.start()]
                name_in_context = re.findall(r'([A-Z][a-z]+\s+[A-Z][a-z]+)', context)
                if name_in_context:
                    salary_matches[name_in_context[-1]] = {'amount': amount, 'currency': '£'}
            except:
                pass

        # Enrich people with salary information
        for person_id, person in people_found.items():
            for name_variant, salary_info in salary_matches.items():
                if name_variant.lower() in person['name'].lower() or person['name'].lower() in name_variant.lower():
                    person['positions'].append({
                        'title': 'Colonial Officer',
                        'location': colony_name,
                        'salary': salary_info,
                        'year': self.year,
                        'status': 'permanent'
                    })

        return list(people_found.values())

    def extract_institutions_from_text(self, text: str, colony_name: str) -> List[Dict]:
        """Extract institutions from text"""
        institutions = []

        institution_patterns = {
            'Executive Council': r"Executive Council",
            'Legislative Council': r"Legislative Council",
            'Privy Council': r"Privy Council",
            'Supreme Court': r"Supreme Court",
            'Colonial Office': r"Colonial Office|Colonial Secretary",
            'Police Force': r"Police Force|Police Commissioner",
            'Military Unit': r"Regiment|Battalion|Garrison|Military",
        }

        found_institutions = set()

        for inst_name, pattern in institution_patterns.items():
            if re.search(pattern, text):
                if inst_name not in found_institutions:
                    found_institutions.add(inst_name)
                    inst_type = inst_name.lower().replace(' ', '_')
                    inst_id = self.generate_id("institution", inst_name, colony_name)

                    # Extract composition if available
                    composition_pattern = rf"{pattern}.*?(?:members?|members?hip|composed|consists)[:\s]+([^.\n]+)"
                    comp_match = re.search(composition_pattern, text, re.IGNORECASE | re.DOTALL)
                    composition = comp_match.group(1).strip()[:200] if comp_match and comp_match.group(1) else None

                    institutions.append({
                        'id': inst_id,
                        'name': inst_name,
                        'type': inst_type,
                        'location': colony_name,
                        'composition': {
                            'description': composition
                        } if composition else {},
                        'year': self.year
                    })

        return institutions

    def extract_economic_data_from_text(self, text: str, colony_name: str) -> List[Dict]:
        """Extract economic data from text"""
        economic_data = []

        # Look for revenue/expenditure sections
        sections = {
            'revenue': r"(?:Revenue|Income).*?([0-9,]+)",
            'expenditure': r"(?:Expenditure|Expenses).*?([0-9,]+)",
            'imports': r"(?:Imports).*?([0-9,]+)",
            'exports': r"(?:Exports).*?([0-9,]+)",
            'trade': r"(?:Trade).*?([0-9,]+)",
            'shipping': r"(?:Shipping|Vessels|Tonnage).*?([0-9,]+)",
        }

        for data_type, pattern in sections.items():
            for match in re.finditer(pattern, text, re.IGNORECASE):
                try:
                    value = int(match.group(1).replace(',', ''))
                    data_id = self.generate_id("economic", data_type, colony_name)

                    economic_data.append({
                        'id': data_id,
                        'type': data_type,
                        'location': colony_name,
                        'year': self.year,
                        'data': {
                            'value': value,
                            'currency': '£',
                            'unit': 'pounds'
                        }
                    })
                except:
                    pass

        return economic_data

    def extract_demographics_from_text(self, text: str, colony_name: str) -> List[Dict]:
        """Extract demographic information from text"""
        demographics = []

        # Look for population data
        pop_pattern = r"[Pp]opulation.*?([0-9,]+)"
        for match in re.finditer(pop_pattern, text):
            try:
                population = int(match.group(1).replace(',', ''))
                demo_id = self.generate_id("demographic", "population", colony_name)

                demographics.append({
                    'id': demo_id,
                    'location': colony_name,
                    'year': self.year,
                    'total_population': population,
                    'breakdowns': []
                })
                break  # Only take first population number
            except:
                pass

        # Look for demographic breakdowns
        breakdown_pattern = r"((?:White|Black|Coloured|European|Native|Chinese|Indian|Male|Female))\s*[:\-]?\s*([0-9,]+)"
        breakdowns = defaultdict(int)

        for match in re.finditer(breakdown_pattern, text):
            try:
                category = match.group(1).strip()
                count = int(match.group(2).replace(',', ''))
                breakdowns[category] = count
            except:
                pass

        if breakdowns and demographics:
            demographics[0]['breakdowns'] = [
                {'category': cat, 'count': count}
                for cat, count in breakdowns.items()
            ]

        return demographics

    def extract_historical_events_from_text(self, text: str, colony_name: str) -> List[Dict]:
        """Extract historical events and dates from text"""
        events = []

        # Date patterns
        date_pattern = r"(?:in\s+)?([0-9]{4})|(?:[A-Z][a-z]+\s+[0-9]{1,2},\s+[0-9]{4})"
        event_types = {
            'established': r"(?:established|founded|created|settled)",
            'treaty': r"(?:treaty|agreement|accord)",
            'transfer': r"(?:transfer|ceded|granted|handed over)",
            'rebellion': r"(?:rebellion|revolt|uprising|mutiny)",
        }

        for date_match in re.finditer(date_pattern, text):
            date_str = date_match.group(0)
            context_start = max(0, date_match.start() - 150)
            context_end = min(len(text), date_match.end() + 150)
            context = text[context_start:context_end]

            event_type = 'other'
            for evt_type, evt_pattern in event_types.items():
                if re.search(evt_pattern, context, re.IGNORECASE):
                    event_type = evt_type
                    break

            event_id = self.generate_id("event", event_type, colony_name)
            events.append({
                'id': event_id,
                'date': date_str,
                'type': event_type,
                'description': context.strip(),
                'locations': [colony_name],
                'year_mentioned': self.year
            })

        return events[:10]  # Limit to 10 events per colony to avoid noise

    def process_colony_file(self, filepath: Path) -> Dict:
        """Process a single colony file and extract all entity types"""

        colony_name = filepath.stem

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read()
        except:
            with open(filepath, 'r', encoding='latin-1') as f:
                text = f.read()

        # Extract all entity types
        places = self.extract_places_from_text(text, colony_name)
        people = self.extract_people_from_text(text, colony_name)
        institutions = self.extract_institutions_from_text(text, colony_name)
        economic = self.extract_economic_data_from_text(text, colony_name)
        infrastructure = self.extract_infrastructure_from_text(text, colony_name)
        demographics = self.extract_demographics_from_text(text, colony_name)
        events = self.extract_historical_events_from_text(text, colony_name)

        # Add to collections
        for place in places:
            self.places[place['id']] = place

        for person in people:
            self.people[person['id']] = person

        for inst in institutions:
            self.institutions[inst['id']] = inst

        self.economic_data.extend(economic)
        self.infrastructure.extend(infrastructure)
        self.demographics.extend(demographics)
        self.events.extend(events)

        # Create relationships
        if places:
            colony_id = places[0]['id']
            for place in places[1:]:
                self.relationships.append({
                    'source_id': place['id'],
                    'relationship_type': 'LOCATED_IN',
                    'target_id': colony_id,
                    'properties': {'year': self.year}
                })

        for inst in institutions:
            self.relationships.append({
                'source_id': inst['id'],
                'relationship_type': 'ADMINISTERS',
                'target_id': places[0]['id'] if places else None,
                'properties': {'year': self.year}
            })

        self.colonies_processed.append(colony_name)

        return {
            'colony': colony_name,
            'places_count': len(places),
            'people_count': len(people),
            'institutions_count': len(institutions),
            'economic_count': len(economic),
            'infrastructure_count': len(infrastructure),
            'demographics_count': len(demographics),
            'events_count': len(events),
        }

    def extract_infrastructure_from_text(self, text: str, colony_name: str) -> List[Dict]:
        """Extract infrastructure information from text"""
        infrastructure = []

        infrastructure_types = {
            'railway': r"(?:railway|railroad|rail)",
            'telegraph': r"(?:telegraph|telephone)",
            'dock': r"(?:dock|wharf|harbor|harbour|port)",
            'road': r"(?:road|highway|route)",
            'bridge': r"(?:bridge)",
            'postal_route': r"(?:postal|mail)",
        }

        for infra_type, pattern in infrastructure_types.items():
            for match in re.finditer(pattern, text, re.IGNORECASE):
                infra_id = self.generate_id("infrastructure", infra_type, colony_name)
                context = text[max(0, match.start()-100):min(len(text), match.end()+100)]

                # Extract dimensions if available
                length_match = re.search(r"([0-9,]+)\s*miles?", context)
                length = None
                if length_match:
                    try:
                        length = {'value': int(length_match.group(1).replace(',', '')), 'unit': 'miles'}
                    except:
                        pass

                infrastructure.append({
                    'id': infra_id,
                    'type': infra_type,
                    'location': colony_name,
                    'specifications': {
                        'length': length
                    } if length else {},
                    'year': self.year
                })

        return infrastructure

    def build_output_json(self) -> Dict:
        """Build the final JSON output structure"""

        return {
            'metadata': {
                'year': self.year,
                'source_directory': str(self.source_dir),
                'extraction_date': self.extraction_date,
                'colonies_processed': self.colonies_processed,
                'processing_notes': 'Comprehensive knowledge graph extraction from 1919 Colonial Office Lists. All entities extracted from source documents with historical spelling preserved.'
            },
            'entities': {
                'places': list(self.places.values()),
                'people': list(self.people.values()),
                'institutions': list(self.institutions.values()),
                'economic_data': self.economic_data,
                'infrastructure': self.infrastructure,
                'demographics': self.demographics,
                'events': self.events
            },
            'relationships': self.relationships
        }

    def extract(self) -> Dict:
        """Main extraction workflow"""

        print(f"Starting knowledge graph extraction for year {self.year}")
        print(f"Processing colonies from: {self.source_dir}")

        # Get all colony files
        colony_files = sorted(self.source_dir.glob('*.md'))
        print(f"Found {len(colony_files)} colony files")

        # Process each colony
        summary_stats = []
        for filepath in colony_files:
            print(f"  Processing {filepath.stem}...", end=' ')
            stats = self.process_colony_file(filepath)
            summary_stats.append(stats)
            total_entities = stats['places_count'] + stats['people_count'] + stats['institutions_count']
            print(f"({total_entities} total entities)")

        print(f"\nExtraction complete. Processed {len(self.colonies_processed)} colonies.")

        # Print summary
        print("\nEntity Summary:")
        print(f"  Places: {len(self.places)}")
        print(f"  People: {len(self.people)}")
        print(f"  Institutions: {len(self.institutions)}")
        print(f"  Economic Records: {len(self.economic_data)}")
        print(f"  Infrastructure: {len(self.infrastructure)}")
        print(f"  Demographics: {len(self.demographics)}")
        print(f"  Events: {len(self.events)}")
        print(f"  Relationships: {len(self.relationships)}")

        return self.build_output_json()


def main():
    """Main execution"""

    # Create extractor
    extractor = KnowledgeGraphExtractor(year="1919")

    # Run extraction
    result = extractor.extract()

    # Create output directory
    output_dir = Path("/home/user/colonial_office_list/knowledge_graph_extracts")
    output_dir.mkdir(parents=True, exist_ok=True)

    # Save result
    output_file = output_dir / "1919_extracted.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print(f"\nKnowledge graph saved to: {output_file}")

    # Print final report
    print("\n" + "="*70)
    print("EXTRACTION REPORT: 1919 COLONIAL OFFICE LIST")
    print("="*70)
    print(f"Year: 1919")
    print(f"Colonies Processed: {len(result['metadata']['colonies_processed'])}")
    print(f"Extraction Date: {result['metadata']['extraction_date']}")
    print(f"\nEntity Counts by Type:")
    print(f"  - Geographic Places: {len(result['entities']['places'])}")
    print(f"  - People (Colonial Officers): {len(result['entities']['people'])}")
    print(f"  - Institutions: {len(result['entities']['institutions'])}")
    print(f"  - Economic Data Points: {len(result['entities']['economic_data'])}")
    print(f"  - Infrastructure Elements: {len(result['entities']['infrastructure'])}")
    print(f"  - Demographic Records: {len(result['entities']['demographics'])}")
    print(f"  - Historical Events: {len(result['entities']['events'])}")
    print(f"  - Total Relationships: {len(result['relationships'])}")
    print(f"\nTotal Entities Extracted: {sum(len(v) if isinstance(v, list) else len([v]) for v in result['entities'].values())}")
    print(f"\nOutput File: {output_file}")
    print("="*70)


if __name__ == "__main__":
    main()
