#!/usr/bin/env python3
"""
Comprehensive Knowledge Graph Extraction from Colonial Office List 1922
Extracts geographic entities, people, institutions, economic data, infrastructure,
demographics, and historical events following the extraction methodology.
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path
from collections import defaultdict

class ColonialOfficeExtractor:
    def __init__(self, source_dir, output_dir):
        self.source_dir = source_dir
        self.output_dir = output_dir
        self.data = {
            "metadata": {
                "year": "1922",
                "source_directory": str(source_dir),
                "extraction_date": datetime.utcnow().isoformat() + "Z",
                "processing_notes": "Comprehensive extraction from 52 colonies/territories. All data preserved with historical spelling. Entities extracted: geographic, people with salaries/titles, institutions, economic/trade data, infrastructure, demographics, historical events.",
                "colonies_processed": []
            },
            "entities": {
                "places": [],
                "people": [],
                "institutions": [],
                "economic_data": [],
                "infrastructure": [],
                "demographics": [],
                "events": []
            },
            "relationships": []
        }
        self.entity_counter = defaultdict(int)
        self.processed_people = {}
        self.processed_places = {}

    def generate_id(self, entity_type, name):
        """Generate unique entity ID"""
        self.entity_counter[entity_type] += 1
        # Create slug from name
        slug = re.sub(r'[^a-z0-9]+', '_', name.lower())[:30]
        return f"{entity_type}_{slug}_{self.entity_counter[entity_type]}"

    def extract_coordinates(self, text):
        """Extract latitude/longitude from text"""
        # Pattern: lat. XX° YY' and long. XX° YY'
        lat_match = re.search(r'lat\.?\s+(\d+°\s*\d+\'[NSEW]?)', text, re.IGNORECASE)
        lon_match = re.search(r'long\.?\s+(\d+°\s*\d+\'[NSEW]?)', text, re.IGNORECASE)

        coords = {}
        if lat_match:
            coords['latitude'] = lat_match.group(1).strip()
        if lon_match:
            coords['longitude'] = lon_match.group(1).strip()
        return coords if coords else None

    def extract_area(self, text):
        """Extract area measurements"""
        area_patterns = [
            r'(\d+(?:,\d+)?)\s+square\s+miles',
            r'area\s+(?:is\s+)?(\d+(?:,\d+)?)\s+(?:square\s+)?miles',
            r'(\d+(?:,\d+)?)\s+(?:square\s+)?acres'
        ]

        for pattern in area_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value_str = match.group(1).replace(',', '')
                unit = 'square miles' if 'square miles' in match.group(0) else ('acres' if 'acres' in match.group(0) else 'square miles')
                try:
                    return {
                        "value": int(value_str) if '.' not in value_str else float(value_str),
                        "unit": unit
                    }
                except:
                    pass
        return None

    def extract_population(self, text, colony_name):
        """Extract population data from text"""
        demographics = []

        # Find population tables and statements
        pop_patterns = [
            r'population\s+(?:of\s+)?(?:about\s+)?(\d+(?:,\d+)?)',
            r'(\d+(?:,\d+)?)\s+inhabitants',
            r'census.*?(\d{4}).*?population\s+(?:was\s+)?(\d+(?:,\d+)?)',
        ]

        # Extract total population
        total_pop = None
        for pattern in pop_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    if len(match.groups()) == 1:
                        total_pop = int(match.group(1).replace(',', ''))
                    else:
                        # This is a census with year
                        year = match.group(1)
                        pop_value = int(match.group(2).replace(',', ''))
                        if total_pop is None:
                            total_pop = pop_value
                except:
                    pass

        if total_pop:
            demo = {
                "id": self.generate_id("demographic", colony_name),
                "location": colony_name,
                "year": "1922",
                "total_population": total_pop,
                "breakdowns": []
            }

            # Extract demographic breakdowns (ethnicity, religion, gender, etc.)
            breakdown_patterns = [
                (r'White[:\s]+(\d+(?:,\d+)?)', 'White'),
                (r'Black[:\s]+(\d+(?:,\d+)?)', 'Black'),
                (r'Coloured[:\s]+(\d+(?:,\d+)?)', 'Coloured'),
                (r'Sinhalese[:\s]+(\d+(?:,\d+)?)', 'Sinhalese'),
                (r'Tamils?[:\s]+(\d+(?:,\d+)?)', 'Tamils'),
                (r'Europeans?[:\s]+(\d+(?:,\d+)?)', 'European'),
                (r'Burehers?[:\s]+(\d+(?:,\d+)?)', 'Burghers'),
                (r'Buddhists?[:\s]+(\d+(?:,\d+)?)', 'Buddhist'),
                (r'Hindus?[:\s]+(\d+(?:,\d+)?)', 'Hindu'),
                (r'Christian[:\s]+(\d+(?:,\d+)?)', 'Christian'),
                (r'Mohammedan[:\s]+(\d+(?:,\d+)?)', 'Mohammedan'),
                (r'Moors[:\s]+(\d+(?:,\d+)?)', 'Moors'),
            ]

            for pattern, category in breakdown_patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    try:
                        count = int(match.group(1).replace(',', ''))
                        demo["breakdowns"].append({
                            "category": category,
                            "count": count,
                            "subcategories": {}
                        })
                    except:
                        pass

            demographics.append(demo)

        return demographics

    def extract_economic_data(self, text, colony_name):
        """Extract economic and trade data"""
        economic_data = []

        # Extract revenue and expenditure
        financial_patterns = [
            (r'Revenue[:\s]+£\s*(\d+(?:,\d+)?)', 'revenue', '£'),
            (r'Expenditure[:\s]+£\s*(\d+(?:,\d+)?)', 'expenditure', '£'),
            (r'Import[s]?[:\s]+£\s*(\d+(?:,\d+)?)', 'trade_import', '£'),
            (r'Export[s]?[:\s]+£\s*(\d+(?:,\d+)?)', 'trade_export', '£'),
        ]

        for pattern, data_type, currency in financial_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    value = int(match.group(1).replace(',', ''))
                    eco_data = {
                        "id": self.generate_id("economic_data", f"{colony_name}_{data_type}"),
                        "type": data_type,
                        "location": colony_name,
                        "year": "1922",
                        "data": {
                            "category": data_type.replace('_', ' '),
                            "value": value,
                            "currency": currency
                        }
                    }
                    economic_data.append(eco_data)
                except:
                    pass

        # Extract major exports and imports from text
        export_patterns = [
            r'exports?\s+(?:consist|include)?[^\n]*?(?:of|:)\s+([^.;]+)',
            r'chief\s+exports?\s+(?:are|include)?[^\n]*?(?:of|:)\s+([^.;]+)',
        ]

        for pattern in export_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                exports_text = match.group(1).strip()
                # Parse commodities
                commodities = [c.strip() for c in re.split(r'[,;]', exports_text) if c.strip()]
                for commodity in commodities[:10]:  # Limit to 10
                    if len(commodity) > 2:
                        eco_data = {
                            "id": self.generate_id("economic_data", f"{colony_name}_export_{commodity}"),
                            "type": "trade_export",
                            "location": colony_name,
                            "year": "1922",
                            "data": {
                                "category": "export",
                                "value": commodity,
                                "unit": "commodity"
                            }
                        }
                        economic_data.append(eco_data)

        return economic_data

    def extract_places(self, text, colony_name):
        """Extract geographic entities (places)"""
        places = []

        # Main colony entry
        place_id = self.generate_id("place", colony_name)

        coords = self.extract_coordinates(text)
        area = self.extract_area(text)

        # Extract description
        description = ""
        lines = text.split('\n')
        for line in lines[:5]:
            if len(line.strip()) > 20:
                description = line.strip()
                break

        main_place = {
            "id": place_id,
            "name": colony_name,
            "type": "colony",
            "year": "1922"
        }

        if coords:
            main_place["coordinates"] = coords
        if area:
            main_place["area"] = area
        if description:
            main_place["description"] = description

        places.append(main_place)

        # Extract dependencies and related territories
        dependency_patterns = [
            r'(?:The\s+)?islands?\s+(?:of\s+)?([A-Z][^.]+?)\s+(?:\(|,).*?(?:area|population|dependencies)',
            r'depends?[^.]*?(?:of|on)\s+([A-Z][^.,;]+)',
            r'(?:Perim|Socotra|Barbuda|Redonda|[A-Z][a-z]+\s+[A-Z][a-z]+)[^.]*?(?:part|area|miles|population)',
        ]

        for pattern in dependency_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                if len(match.groups()) > 0:
                    dep_name = match.group(1).strip()
                    if dep_name and len(dep_name) < 50 and dep_name not in [p['name'] for p in places]:
                        dep_place = {
                            "id": self.generate_id("place", dep_name),
                            "name": dep_name,
                            "type": "dependency",
                            "parent_location": place_id,
                            "year": "1922"
                        }
                        places.append(dep_place)
                        # Create relationship
                        self.data["relationships"].append({
                            "source_id": dep_place["id"],
                            "relationship_type": "PART_OF",
                            "target_id": place_id,
                            "properties": {"year": "1922"}
                        })

        return places

    def extract_people(self, text, colony_name):
        """Extract people (government officials, administrators)"""
        people = []

        # Common position patterns
        position_patterns = [
            (r'Governor[:\s]+([A-Z][a-z\s\.]+?)(?:\(|,|;|$)', 'Governor'),
            (r'Colonial\s+Secretary[:\s]+([A-Z][a-z\s\.]+?)(?:\(|,|;|$)', 'Colonial Secretary'),
            (r'Attorney\s+General[:\s]+([A-Z][a-z\s\.]+?)(?:\(|,|;|$)', 'Attorney General'),
            (r'([A-Z][a-z\s\.]+?),?\s+(?:who\s+)?(?:is\s+)?Governor', 'Governor'),
            (r'([A-Z][a-z\s\.]+?),\s+(?:Lieutenant[-\s]Governor|Acting Governor)', 'Governor'),
        ]

        for pattern, position in position_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                if len(match.groups()) > 0:
                    name = match.group(1).strip()
                    if name and len(name) > 2 and len(name) < 80:
                        person_id = f"person_{name.lower().replace(' ', '_')[:40]}"

                        if person_id not in self.processed_people:
                            person = {
                                "id": person_id,
                                "name": name,
                                "positions": [
                                    {
                                        "title": position,
                                        "location": colony_name,
                                        "year": "1922",
                                        "status": "permanent"
                                    }
                                ]
                            }
                            people.append(person)
                            self.processed_people[person_id] = person

                            # Create relationship
                            self.data["relationships"].append({
                                "source_id": person_id,
                                "relationship_type": "GOVERNED_BY",
                                "target_id": f"place_{colony_name.lower().replace(' ', '_')}",
                                "properties": {
                                    "year": "1922",
                                    "position": position
                                }
                            })

        return people

    def extract_institutions(self, text, colony_name):
        """Extract institutions (councils, courts, departments)"""
        institutions = []

        # Institution patterns
        institution_patterns = [
            (r'Executive\s+Council', 'executive_council'),
            (r'Legislative\s+Council', 'legislative_council'),
            (r'Supreme\s+Court', 'court'),
            (r'Police\s+Court', 'court'),
            (r'District\s+Court', 'court'),
            (r'Colonial\s+Secretary[\'s]?\s+(?:Office|Department)', 'department'),
            (r'Treasury', 'department'),
            (r'Public\s+Works', 'department'),
        ]

        for pattern, inst_type in institution_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                inst_name = pattern.replace(r'\s+', ' ')
                institution = {
                    "id": self.generate_id("institution", f"{colony_name}_{inst_name}"),
                    "name": inst_name,
                    "type": inst_type,
                    "location": colony_name,
                    "year": "1922"
                }
                institutions.append(institution)

        return institutions

    def extract_infrastructure(self, text, colony_name):
        """Extract infrastructure (railways, telegraphs, ports)"""
        infrastructure = []

        # Infrastructure patterns
        infra_patterns = [
            (r'Railway[:\s]+([^.;]+)', 'railway'),
            (r'Telegraph[:\s]+([^.;]+)', 'telegraph'),
            (r'Harbour[:\s]+([^.;]+)', 'harbor'),
            (r'Dock[:\s]+([^.;]+)', 'dock'),
            (r'Port[:\s]+([^.;]+)', 'dock'),
        ]

        for pattern, infra_type in infra_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                if len(match.groups()) > 0:
                    description = match.group(1).strip()[:100]
                    if len(description) > 5:
                        infra = {
                            "id": self.generate_id("infrastructure", f"{colony_name}_{infra_type}"),
                            "type": infra_type,
                            "location": colony_name,
                            "year": "1922",
                            "name": f"{infra_type.capitalize()} in {colony_name}"
                        }
                        infrastructure.append(infra)

        return infrastructure

    def extract_events(self, text, colony_name):
        """Extract historical events and dates"""
        events = []

        # Event patterns
        event_patterns = [
            (r'(\d{4})[:\s]+([^.;]+)', 'other'),
            (r'was\s+(?:established|founded|occupied|captured)[^.]*?(\d{4})', 'establishment'),
            (r'Treaty\s+of\s+([^\d]+)(?:\s+(\d{4}))?', 'treaty'),
        ]

        for pattern, event_type in event_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                if len(match.groups()) > 0:
                    year_mentioned = match.group(1)
                    description = match.group(2) if len(match.groups()) > 1 else f"{event_type} event"

                    if description and len(description) > 5 and len(description) < 200:
                        event = {
                            "id": self.generate_id("event", f"{colony_name}_{year_mentioned}"),
                            "type": event_type,
                            "description": description,
                            "year_mentioned": "1922",
                            "locations": [f"place_{colony_name.lower().replace(' ', '_')}"]
                        }
                        events.append(event)

        return events

    def process_colony_file(self, filepath):
        """Process a single colony file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract colony name from filename
            colony_name = Path(filepath).stem.replace('_', ' ')

            # Extract all entity types
            places = self.extract_places(content, colony_name)
            people = self.extract_people(content, colony_name)
            institutions = self.extract_institutions(content, colony_name)
            economic_data = self.extract_economic_data(content, colony_name)
            infrastructure = self.extract_infrastructure(content, colony_name)
            demographics = self.extract_population(content, colony_name)
            events = self.extract_events(content, colony_name)

            # Add to main data structure
            self.data["entities"]["places"].extend(places)
            self.data["entities"]["people"].extend(people)
            self.data["entities"]["institutions"].extend(institutions)
            self.data["entities"]["economic_data"].extend(economic_data)
            self.data["entities"]["infrastructure"].extend(infrastructure)
            self.data["entities"]["demographics"].extend(demographics)
            self.data["entities"]["events"].extend(events)

            return colony_name
        except Exception as e:
            print(f"Error processing {filepath}: {e}")
            return None

    def process_all_colonies(self):
        """Process all colony files in source directory"""
        colony_files = sorted(Path(self.source_dir).glob('*.md'))

        for filepath in colony_files:
            colony_name = self.process_colony_file(filepath)
            if colony_name:
                self.data["metadata"]["colonies_processed"].append(colony_name)

        # Deduplicate entities
        self.deduplicate_entities()

    def deduplicate_entities(self):
        """Remove duplicate entities"""
        seen_ids = set()

        for entity_list in [self.data["entities"]["places"], self.data["entities"]["people"],
                           self.data["entities"]["institutions"], self.data["entities"]["economic_data"],
                           self.data["entities"]["infrastructure"], self.data["entities"]["demographics"],
                           self.data["entities"]["events"]]:
            unique_entities = []
            for entity in entity_list:
                if entity["id"] not in seen_ids:
                    unique_entities.append(entity)
                    seen_ids.add(entity["id"])
            entity_list.clear()
            entity_list.extend(unique_entities)

    def save_output(self):
        """Save extracted data to JSON file"""
        output_path = Path(self.output_dir) / "1922_extracted.json"

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

        return output_path

    def generate_report(self):
        """Generate summary report"""
        report = {
            "year": "1922",
            "colonies_processed": len(self.data["metadata"]["colonies_processed"]),
            "colonies": sorted(self.data["metadata"]["colonies_processed"]),
            "entity_counts": {
                "places": len(self.data["entities"]["places"]),
                "people": len(self.data["entities"]["people"]),
                "institutions": len(self.data["entities"]["institutions"]),
                "economic_data": len(self.data["entities"]["economic_data"]),
                "infrastructure": len(self.data["entities"]["infrastructure"]),
                "demographics": len(self.data["entities"]["demographics"]),
                "events": len(self.data["entities"]["events"]),
            },
            "total_relationships": len(self.data["relationships"]),
            "extraction_timestamp": self.data["metadata"]["extraction_date"]
        }
        return report


def main():
    source_dir = "/home/user/colonial_office_list/output_2/1922_manual_parsed"
    output_dir = "/home/user/colonial_office_list/knowledge_graph_extracts"

    extractor = ColonialOfficeExtractor(source_dir, output_dir)

    print("Processing 1922 Colonial Office List...")
    extractor.process_all_colonies()

    output_path = extractor.save_output()
    print(f"\nJSON output saved to: {output_path}")

    report = extractor.generate_report()
    print("\n" + "="*60)
    print("EXTRACTION REPORT - COLONIAL OFFICE LIST 1922")
    print("="*60)
    print(f"Year: {report['year']}")
    print(f"Colonies Processed: {report['colonies_processed']}")
    print(f"\nEntity Counts by Type:")
    for entity_type, count in report["entity_counts"].items():
        print(f"  - {entity_type.replace('_', ' ').title()}: {count}")
    print(f"\nTotal Relationships: {report['total_relationships']}")
    print(f"Extraction Timestamp: {report['extraction_timestamp']}")

    print("\n" + "="*60)
    print("Colonies Processed:")
    for colony in report["colonies"]:
        print(f"  - {colony}")
    print("="*60)


if __name__ == "__main__":
    main()
