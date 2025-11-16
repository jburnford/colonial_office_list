#!/usr/bin/env python3
"""
Enhanced Colonial Office List 1924 - Comprehensive Knowledge Graph Extraction
Extracts all entities with improved pattern matching for institutions, economic data, and demographics
"""

import json
import re
import os
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple

class EnhancedColonialOfficeExtractor:
    def __init__(self, source_dir: str, output_dir: str):
        self.source_dir = Path(source_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Data structures
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
        self.colonies_processed = []
        self.id_counters = {}
        self.processed_people = set()

    def generate_id(self, prefix: str) -> str:
        """Generate unique IDs for entities"""
        if prefix not in self.id_counters:
            self.id_counters[prefix] = 0
        self.id_counters[prefix] += 1
        return f"{prefix}_{self.id_counters[prefix]:05d}"

    def extract_numeric_value(self, text: str) -> Optional[float]:
        """Extract numeric value from text"""
        match = re.search(r'[0-9]{1,3}(?:,[0-9]{3})*(?:\.[0-9]+)?', text)
        if match:
            try:
                return float(match.group(0).replace(',', ''))
            except ValueError:
                return None
        return None

    def extract_all_people_entries(self, text: str, colony: str) -> List[Dict[str, Any]]:
        """Comprehensively extract all person entries"""
        people = []

        # Patterns for detecting person entries
        patterns = [
            # Format: Name, Title, Salary
            r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:\s+[A-Z]\.)?),\s+([^,\n]+?),\s+([0-9,]+l\.?)(?:\s+to\s+[0-9,]+l\.)?',
            # Format: Name with honors, Position, Salary
            r'^([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:\s+[A-Z]\.)?(?:,\s+[A-Z\.]+)*),\s+([^,\n]+?),\s+([0-9,]+l\.)',
        ]

        for line in text.split('\n'):
            line = line.strip()
            if not line or len(line) < 10:
                continue

            for pattern in patterns:
                match = re.search(pattern, line)
                if match:
                    full_entry = match.group(0)
                    parts = [p.strip() for p in full_entry.split(',')]

                    if len(parts) >= 2:
                        name = parts[0]
                        position = parts[1] if len(parts) > 1 else ""
                        salary_str = parts[-1] if len(parts) > 2 else ""

                        # Extract salary
                        salary = None
                        salary_match = re.search(r'([0-9,]+)', salary_str)
                        if salary_match:
                            try:
                                salary = {
                                    "amount": int(salary_match.group(1).replace(',', '')),
                                    "currency": "£",
                                    "period": "annual"
                                }
                            except ValueError:
                                pass

                        # Extract titles and honors
                        titles = []
                        honors = []

                        title_list = ['Sir', 'Rev', 'Dr', 'Capt', 'Col', 'Major', 'Lieut', 'General', 'Lord', 'Mrs', 'Miss']
                        for t in title_list:
                            if re.search(rf'\b{t}\.?', full_entry):
                                titles.append(t)

                        honor_list = ['K.C.M.G', 'C.B', 'G.C.B', 'O.B.E', 'M.B.E', 'M.C', 'C.M.G', 'K.C', 'Kt', 'Bart', 'R.D', 'R.N.R', 'R.N']
                        for h in honor_list:
                            if h in full_entry:
                                honors.append(h)

                        person_key = f"{name}_{colony}"
                        if person_key not in self.processed_people:
                            person_id = self.generate_id("person")
                            person = {
                                "id": person_id,
                                "name": name,
                                "titles": list(set(titles)),
                                "honors": list(set(honors)),
                                "positions": [{
                                    "title": position,
                                    "location": colony,
                                    "salary": salary,
                                    "status": "permanent" if "acting" not in position.lower() else "acting",
                                    "year": "1924"
                                }]
                            }
                            people.append(person)
                            self.processed_people.add(person_key)
                    break

        return people

    def extract_councils_and_institutions(self, text: str, colony: str) -> List[Dict[str, Any]]:
        """Extract councils, courts, and other institutions"""
        institutions = []

        # Patterns for institutions
        council_patterns = [
            (r'Executive Council', 'executive_council'),
            (r'Legislative Council', 'legislative_council'),
            (r'(?:Supreme|Superior|District)\s+Court', 'court'),
            (r'Police (?:Court|Force)', 'police_force'),
            (r'Department of [A-Za-z\s]+', 'department'),
        ]

        for pattern, inst_type in council_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                inst_name = match.group(0).strip()
                institution = {
                    "id": self.generate_id("institution"),
                    "name": inst_name,
                    "type": inst_type,
                    "location": colony,
                    "year": "1924"
                }
                institutions.append(institution)

        # Look for composition details (members)
        comp_patterns = [
            r'(?:composed|consists) of ([^\n.]+)',
            r'members?:?\s+([^\n.]+)',
        ]

        for inst in institutions:
            for pattern in comp_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    inst['composition'] = {
                        "description": match.group(1).strip()[:200],
                        "members": []
                    }

        return institutions

    def extract_demographic_data(self, text: str, colony: str) -> List[Dict[str, Any]]:
        """Extract population and demographic information"""
        demographics = []

        # Look for census data
        census_patterns = [
            r'(?:Census|Population)(?:\s+of)?\s*([^\n]*?[0-9,]+)',
            r'(?:total\s+)?population[:\s]+(?:about\s+)?([0-9,]+)',
            r'(?:estimated|estimate)[:\s]+([0-9,]+)',
        ]

        total_pop = None
        for pattern in census_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                text_segment = match.group(1) if match.lastindex else match.group(0)
                num_match = re.search(r'([0-9,]+)', text_segment)
                if num_match:
                    try:
                        value = int(num_match.group(1).replace(',', ''))
                        if not total_pop or value > total_pop:
                            total_pop = value
                    except ValueError:
                        pass

        # Extract population by category
        breakdowns = []
        breakdown_pattern = r'([A-Za-z\s]+):\s*([0-9,]+)(?:\s*\(([^)]+)\))?'
        for match in re.finditer(breakdown_pattern, text):
            category = match.group(1).strip()
            if len(category) > 2 and len(category) < 50:
                try:
                    count = int(match.group(2).replace(',', ''))
                    breakdowns.append({
                        "category": category,
                        "count": count
                    })
                except ValueError:
                    pass

        if total_pop or breakdowns:
            demographic = {
                "id": self.generate_id("demographic"),
                "location": colony,
                "year": "1924",
                "total_population": total_pop,
                "breakdowns": breakdowns
            }
            demographics.append(demographic)

        return demographics

    def extract_economic_and_trade_data(self, text: str, colony: str) -> List[Dict[str, Any]]:
        """Extract revenue, expenditure, trade, and shipping data"""
        economic = []

        # Revenue and expenditure
        patterns = [
            (r'(?:revenue|receipts)[:\s]+([0-9,]+)l\.?', 'revenue'),
            (r'(?:expenditure|expenses)[:\s]+([0-9,]+)l\.?', 'expenditure'),
            (r'(?:imports|total\s+imports)[:\s]+([0-9,]+)l\.?', 'trade_import'),
            (r'(?:exports|total\s+exports)[:\s]+([0-9,]+)l\.?', 'trade_export'),
        ]

        for pattern, econ_type in patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                try:
                    value = int(match.group(1).replace(',', ''))
                    econ_entry = {
                        "id": self.generate_id("economic"),
                        "type": econ_type,
                        "location": colony,
                        "year": "1924",
                        "data": {
                            "value": value,
                            "currency": "£"
                        }
                    }
                    economic.append(econ_entry)
                except ValueError:
                    pass

        # Shipping and trade volume
        shipping_patterns = [
            (r'(?:tonnage|tons)[:\s]+([0-9,]+)', 'shipping'),
            (r'(?:vessels|ships)[:\s]+([0-9,]+)', 'shipping'),
            (r'([0-9,]+)\s+(?:tons|tonnes)', 'shipping'),
        ]

        for pattern, econ_type in shipping_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                try:
                    value = int(match.group(1).replace(',', ''))
                    if value > 100:  # Filter out unrealistic small values
                        econ_entry = {
                            "id": self.generate_id("economic"),
                            "type": econ_type,
                            "location": colony,
                            "year": "1924",
                            "data": {
                                "value": value,
                                "unit": "tons"
                            }
                        }
                        economic.append(econ_entry)
                except ValueError:
                    pass

        return economic

    def extract_infrastructure(self, text: str, colony: str) -> List[Dict[str, Any]]:
        """Extract infrastructure information"""
        infrastructure = []

        infra_patterns = [
            (r'(?:railway|rail)\s+(?:lines?|routes?|routes)[:\s]*([^\n.]+)', 'railway'),
            (r'(?:telegraph|telegraphic)\s+(?:lines?|stations?)[:\s]*([^\n.]+)', 'telegraph'),
            (r'(?:postal|post)\s+(?:routes?|services?)[:\s]*([^\n.]+)', 'postal_route'),
            (r'(?:dock|docks?|harbour|harbor)[:\s]*([^\n.]+)', 'dock'),
            (r'(?:road|roads?|highway)[:\s]*([^\n.]+)', 'road'),
            (r'(?:bridge|bridges?)[:\s]*([^\n.]+)', 'bridge'),
            (r'(\d+)\s+(?:miles?|km)\s+of\s+(?:railway|telegraph|road)', 'infrastructure'),
        ]

        for pattern, infra_type in infra_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                infra_text = match.group(1) if match.lastindex else match.group(0)
                infra_entry = {
                    "id": self.generate_id("infrastructure"),
                    "type": infra_type,
                    "location": colony,
                    "year": "1924",
                    "name": infra_text.strip()[:150]
                }

                # Extract length if present
                length_match = re.search(r'(\d+(?:\.\d+)?)\s+(?:miles?|km)', infra_text)
                if length_match:
                    infra_entry["specifications"] = {
                        "length": {
                            "value": float(length_match.group(1)),
                            "unit": "miles"
                        }
                    }

                infrastructure.append(infra_entry)

        return infrastructure

    def extract_historical_events(self, text: str, colony: str) -> List[Dict[str, Any]]:
        """Extract historical events and dates"""
        events = []

        # Date patterns
        event_patterns = [
            r'(?:in|by|from)\s+(\d{4})[,:]?\s+([^.!?]{20,200}[.!?])',
            r'([A-Z][a-z]+\s+\d{1,2},?\s+\d{4})[,:]?\s+([^.!?]{20,200}[.!?])',
            r'(?:established|founded|ceded|captured|acquired|discovered|surrendered)[^.!?]{20,150}[.!?]',
        ]

        for pattern in event_patterns:
            for match in re.finditer(pattern, text):
                if match.lastindex and match.lastindex >= 2:
                    event_text = match.group(2) if match.lastindex >= 2 else match.group(0)
                else:
                    event_text = match.group(0)

                if len(event_text) > 20:
                    event = {
                        "id": self.generate_id("event"),
                        "description": event_text.strip()[:250],
                        "year_mentioned": "1924"
                    }
                    events.append(event)

        return events

    def extract_from_file(self, filepath: Path) -> Tuple[str, Dict[str, Any]]:
        """Extract all data from a single colony file"""
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        colony_name = filepath.stem.replace('_', ' ')
        extracted = {
            'colony': colony_name,
            'places': [],
            'people': [],
            'institutions': [],
            'economic_data': [],
            'infrastructure': [],
            'demographics': [],
            'events': [],
        }

        # Main place (colony)
        colony_place = {
            "id": f"place_{filepath.stem.lower()}",
            "name": colony_name,
            "type": "colony",
            "year": "1924"
        }
        extracted['places'].append(colony_place)

        # Extract coordinates
        lat_pattern = r"(?:N\.|S\.)\s*(?:lat|latitude)[.:]?\s*([0-9]+°\s*[0-9]+')"
        long_pattern = r"(?:E\.|W\.)\s*(?:long|longitude)[.:]?\s*([0-9]+°\s*[0-9]+')"

        lat_match = re.search(lat_pattern, content)
        long_match = re.search(long_pattern, content)

        if lat_match or long_match:
            colony_place['coordinates'] = {}
            if lat_match:
                colony_place['coordinates']['latitude'] = lat_match.group(1)
            if long_match:
                colony_place['coordinates']['longitude'] = long_match.group(1)

        # Extract area
        area_matches = re.finditer(r"([0-9,]+(?:\.[0-9]+)?)\s+square\s+miles", content)
        for match in area_matches:
            try:
                area_value = float(match.group(1).replace(',', ''))
                colony_place['area'] = {
                    "value": area_value,
                    "unit": "square miles"
                }
                break
            except ValueError:
                pass

        # Extract sub-locations
        location_matches = re.finditer(r"(?:city|town|region|district|settlement|port|harbor)\s+of\s+([A-Z][a-z\s]+)", content)
        for match in location_matches:
            loc_name = match.group(1).strip()
            if len(loc_name) > 2:
                place = {
                    "id": f"place_{len(extracted['places'])}",
                    "name": loc_name,
                    "type": "settlement",
                    "parent_location": colony_place['id'],
                    "year": "1924"
                }
                extracted['places'].append(place)

        # Extract all entities
        extracted['people'] = self.extract_all_people_entries(content, colony_name)
        extracted['institutions'] = self.extract_councils_and_institutions(content, colony_name)
        extracted['economic_data'] = self.extract_economic_and_trade_data(content, colony_name)
        extracted['infrastructure'] = self.extract_infrastructure(content, colony_name)
        extracted['demographics'] = self.extract_demographic_data(content, colony_name)
        extracted['events'] = self.extract_historical_events(content, colony_name)

        return filepath.stem, extracted

    def process_all_colonies(self):
        """Process all colony files for 1924"""
        colony_files = sorted(self.source_dir.glob("*.md"))

        for filepath in colony_files:
            try:
                colony_name, extracted = self.extract_from_file(filepath)
                self.colonies_processed.append(colony_name.replace('_', ' '))

                # Merge into main entities
                self.entities['places'].extend(extracted['places'])
                self.entities['people'].extend(extracted['people'])
                self.entities['institutions'].extend(extracted['institutions'])
                self.entities['economic_data'].extend(extracted['economic_data'])
                self.entities['infrastructure'].extend(extracted['infrastructure'])
                self.entities['demographics'].extend(extracted['demographics'])
                self.entities['events'].extend(extracted['events'])

                print(f"✓ {colony_name.replace('_', ' '):<40} {len(extracted['people']):>4} people, {len(extracted['institutions']):>2} institutions, {len(extracted['economic_data']):>2} econ entries")
            except Exception as e:
                print(f"✗ {filepath.stem:<40} Error: {str(e)[:50]}")

    def build_relationships(self):
        """Build relationships between entities"""
        # LOCATED_IN relationships for sub-locations
        for place in self.entities['places']:
            if place.get('parent_location'):
                self.relationships.append({
                    "source_id": place['id'],
                    "relationship_type": "LOCATED_IN",
                    "target_id": place['parent_location'],
                    "properties": {"year": "1924"}
                })

        # GOVERNED_BY relationships for people in positions
        for person in self.entities['people']:
            for position in person.get('positions', []):
                colony = position.get('location', '').replace(' ', '_').lower()
                location_id = f"place_{colony}"
                self.relationships.append({
                    "source_id": person['id'],
                    "relationship_type": "GOVERNED_BY",
                    "target_id": location_id,
                    "properties": {
                        "year": "1924",
                        "title": position.get('title', '')
                    }
                })

        # MEMBER_OF relationships
        for institution in self.entities['institutions']:
            if institution.get('composition', {}).get('members'):
                for member_id in institution['composition']['members']:
                    self.relationships.append({
                        "source_id": member_id,
                        "relationship_type": "MEMBER_OF",
                        "target_id": institution['id'],
                        "properties": {"year": "1924"}
                    })

    def generate_output(self) -> Dict[str, Any]:
        """Generate the final JSON structure"""
        output = {
            "metadata": {
                "year": "1924",
                "source_directory": str(self.source_dir),
                "extraction_date": datetime.utcnow().isoformat() + "Z",
                "processing_notes": f"Comprehensive extraction from {len(self.colonies_processed)} colonies/territories with enhanced pattern matching for people, institutions, economic data, infrastructure, and demographics. Includes {len(self.entities['people'])} personnel records with titles and honors.",
                "colonies_processed": sorted(self.colonies_processed)
            },
            "entities": self.entities,
            "relationships": self.relationships
        }
        return output

    def save_output(self, output_path: Path):
        """Save extracted data to JSON file"""
        output = self.generate_output()
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        return output

def main():
    source_dir = "/home/user/colonial_office_list/output_2/1924_manual_parsed"
    output_dir = "/home/user/colonial_office_list/knowledge_graph_extracts"
    output_file = Path(output_dir) / "1924_extracted.json"

    extractor = EnhancedColonialOfficeExtractor(source_dir, output_dir)

    print("=" * 80)
    print("ENHANCED Colonial Office List 1924 - Knowledge Graph Extraction")
    print("=" * 80)
    print(f"\nProcessing {len(list(Path(source_dir).glob('*.md')))} colony files...")
    print("-" * 80 + "\n")

    extractor.process_all_colonies()
    extractor.build_relationships()

    print(f"\n" + "-" * 80)
    print(f"Building final output and generating report...\n")
    output = extractor.save_output(output_file)

    # Generate detailed report
    print("=" * 80)
    print("COMPREHENSIVE EXTRACTION REPORT - 1924")
    print("=" * 80)

    metadata = output['metadata']
    entities = output['entities']

    print(f"\n📍 GEOGRAPHIC COVERAGE:")
    print(f"   Colonies Processed: {len(metadata['colonies_processed'])}")

    print(f"\n📊 ENTITY EXTRACTION SUMMARY:")
    print(f"   Places: {len(entities['places']):>6}")
    print(f"   People: {len(entities['people']):>6}")
    print(f"   Institutions: {len(entities['institutions']):>6}")
    print(f"   Economic Records: {len(entities['economic_data']):>6}")
    print(f"   Infrastructure: {len(entities['infrastructure']):>6}")
    print(f"   Demographics: {len(entities['demographics']):>6}")
    print(f"   Historical Events: {len(entities['events']):>6}")

    print(f"\n📈 ENTITY BREAKDOWN:")

    # Places by type
    place_types = {}
    for place in entities['places']:
        ptype = place.get('type', 'unknown')
        place_types[ptype] = place_types.get(ptype, 0) + 1
    print(f"\n   Places by Type:")
    for ptype in sorted(place_types.keys()):
        print(f"      • {ptype}: {place_types[ptype]}")

    # People analysis
    with_salary = sum(1 for p in entities['people'] if any(pos.get('salary') for pos in p.get('positions', [])))
    with_honors = sum(1 for p in entities['people'] if p.get('honors'))
    with_titles = sum(1 for p in entities['people'] if p.get('titles'))
    print(f"\n   People:")
    print(f"      • Total Personnel: {len(entities['people'])}")
    print(f"      • With Salary Data: {with_salary}")
    print(f"      • With Honors/Orders: {with_honors}")
    print(f"      • With Titles: {with_titles}")

    # Institutions by type
    if entities['institutions']:
        inst_types = {}
        for inst in entities['institutions']:
            itype = inst.get('type', 'unknown')
            inst_types[itype] = inst_types.get(itype, 0) + 1
        print(f"\n   Institutions by Type:")
        for itype in sorted(inst_types.keys()):
            print(f"      • {itype}: {inst_types[itype]}")

    # Economic data by type
    if entities['economic_data']:
        econ_types = {}
        for econ in entities['economic_data']:
            etype = econ.get('type', 'unknown')
            econ_types[etype] = econ_types.get(etype, 0) + 1
        print(f"\n   Economic Data by Type:")
        for etype in sorted(econ_types.keys()):
            print(f"      • {etype}: {econ_types[etype]}")

    # Infrastructure by type
    if entities['infrastructure']:
        infra_types = {}
        for infra in entities['infrastructure']:
            itype = infra.get('type', 'unknown')
            infra_types[itype] = infra_types.get(itype, 0) + 1
        print(f"\n   Infrastructure by Type:")
        for itype in sorted(infra_types.keys()):
            print(f"      • {itype}: {infra_types[itype]}")

    # Demographics
    total_pop_recorded = sum(d.get('total_population', 0) or 0 for d in entities['demographics'])
    print(f"\n   Demographics:")
    print(f"      • Records: {len(entities['demographics'])}")
    print(f"      • Total Population Recorded: {total_pop_recorded:,}")

    # Relationships
    rel_types = {}
    for rel in output['relationships']:
        rtype = rel.get('relationship_type', 'unknown')
        rel_types[rtype] = rel_types.get(rtype, 0) + 1
    print(f"\n   Relationships: {len(output['relationships'])}")
    print(f"      Breakdown by Type:")
    for rtype in sorted(rel_types.keys()):
        print(f"      • {rtype}: {rel_types[rtype]}")

    print(f"\n✅ KNOWLEDGE GRAPH SUCCESSFULLY CREATED")
    print(f"   Output File: {output_file}")
    print(f"   File Size: {output_file.stat().st_size / (1024*1024):.2f} MB")
    print(f"   JSON Lines: {sum(1 for _ in open(output_file))}")

    print("\n" + "=" * 80)

if __name__ == "__main__":
    main()
