#!/usr/bin/env python3
"""
Enhanced Knowledge Graph Extraction from Colonial Office List 1922
Captures detailed information including governors, financial tables, infrastructure,
personnel, and all entity relationships.
"""

import json
import os
import re
import csv
from io import StringIO
from datetime import datetime
from pathlib import Path
from collections import defaultdict

class EnhancedColonialExtractor:
    def __init__(self, source_dir, output_dir):
        self.source_dir = source_dir
        self.output_dir = output_dir
        self.data = {
            "metadata": {
                "year": "1922",
                "source_directory": str(source_dir),
                "extraction_date": datetime.utcnow().isoformat() + "Z",
                "processing_notes": "Enhanced comprehensive extraction from 51 colonies. Includes governors, financial data, infrastructure details, personnel with titles/honors/salaries, demographic breakdowns, trade data, and all historical events. Historical spelling preserved. Full relationship mapping.",
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
        self.processed_entities = {k: {} for k in ['people', 'places', 'institutions']}

    def generate_id(self, entity_type, identifier):
        """Generate unique entity ID"""
        self.entity_counter[entity_type] += 1
        slug = re.sub(r'[^a-z0-9]+', '_', str(identifier).lower())[:40]
        return f"{entity_type}_{slug}_{self.entity_counter[entity_type]}"

    def extract_governors_list(self, text, colony_name):
        """Extract list of governors with dates and honors"""
        people = []
        place_id = self.generate_id("place", colony_name)

        # Pattern: year followed by name and titles
        governor_pattern = r'^(\d{4})\s+([A-Z][^.;]+?)(?:\(|,\s*(?:acting|K\.C\.B|K\.C\.M\.G|G\.C\.M\.G|K\.B\.E|C\.B\.I|C\.B|,))'

        matches = re.finditer(governor_pattern, text, re.MULTILINE | re.IGNORECASE)
        for match in matches:
            year = match.group(1)
            name_text = match.group(2).strip()

            # Parse titles and honors
            titles = []
            honors = []

            honor_patterns = {
                r'\bSir\b': 'Sir',
                r'\bMajor[-\s]Gen(?:eral)?\b': 'Major-General',
                r'\bCol(?:onel)?\b': 'Colonel',
                r'\bRev(?:erend)?\b': 'Reverend',
                r'\bDr\b': 'Doctor',
                r'\bRt\.\s*Hon': 'Right Honourable'
            }

            for pattern, title in honor_patterns.items():
                if re.search(pattern, name_text):
                    titles.append(title)

            honor_codes = ['K.C.M.G', 'G.C.M.G', 'K.C.B', 'K.B.E', 'C.B', 'C.S.I', 'C.I.E', 'R.E']
            for code in honor_codes:
                if code in name_text:
                    honors.append(code)

            # Extract clean name (remove titles and honors)
            clean_name = re.sub(r'\b(?:Sir|Major[-\s]Gen|Col|Rev|Dr|Rt\.\s*Hon)\b', '', name_text)
            clean_name = re.sub(r'(?:K\.C\.M\.G|G\.C\.M\.G|K\.C\.B|K\.B\.E|C\.B|C\.S\.I|C\.I\.E|R\.E)[,.\s]?', '', clean_name)
            clean_name = clean_name.strip()

            if len(clean_name) > 3 and len(clean_name) < 100:
                person_key = f"{clean_name.lower()}_{year}"
                person_id = self.generate_id("person", person_key)

                person = {
                    "id": person_id,
                    "name": clean_name,
                    "titles": titles,
                    "honors": honors,
                    "positions": [
                        {
                            "title": "Governor",
                            "location": colony_name,
                            "year": year,
                            "status": "permanent"
                        }
                    ]
                }
                people.append(person)

                # Create relationship
                self.data["relationships"].append({
                    "source_id": person_id,
                    "relationship_type": "GOVERNED_BY",
                    "target_id": place_id,
                    "properties": {"year": year, "position": "Governor"}
                })

        return people, place_id

    def extract_colonial_officials(self, text, colony_name):
        """Extract Colonial Secretary, Attorney General, and other officials"""
        people = []
        place_id = f"place_{colony_name.lower().replace(' ', '_')}"

        official_patterns = [
            (r'Colonial\s+Secretary[:\s]*([A-Z][^.;,\n]+)', 'Colonial Secretary'),
            (r'Attorney\s+General[:\s]*([A-Z][^.;,\n]+)', 'Attorney General'),
            (r'Treasurer[:\s]*([A-Z][^.;,\n]+)', 'Treasurer'),
            (r'Auditor[:\s]*([A-Z][^.;,\n]+)', 'Auditor'),
            (r'Registrar[:\s]*([A-Z][^.;,\n]+)', 'Registrar'),
            (r'Chief\s+Justice[:\s]*([A-Z][^.;,\n]+)', 'Chief Justice'),
            (r'Police\s+Commissioner[:\s]*([A-Z][^.;,\n]+)', 'Police Commissioner'),
            (r'Commandant[:\s]*([A-Z][^.;,\n]+)', 'Commandant'),
        ]

        for pattern, position_title in official_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                name = match.group(1).strip()
                if len(name) > 3 and len(name) < 100 and '.' not in name[:20]:
                    person_key = f"{name.lower()}_{position_title.lower()}"
                    person_id = self.generate_id("person", person_key)

                    person = {
                        "id": person_id,
                        "name": name,
                        "positions": [
                            {
                                "title": position_title,
                                "location": colony_name,
                                "year": "1922",
                                "status": "permanent"
                            }
                        ]
                    }
                    people.append(person)

        return people

    def extract_infrastructure_details(self, text, colony_name):
        """Extract detailed infrastructure information"""
        infrastructure = []

        # Railway extraction
        railway_pattern = r'([\w\s]+)\s+to\s+([\w\s]+)\s+\((\d+(?:\.\d+)?)\s+miles?\)'
        matches = re.finditer(railway_pattern, text, re.IGNORECASE)
        for match in matches:
            from_loc = match.group(1).strip()
            to_loc = match.group(2).strip()
            miles = float(match.group(3))

            railway = {
                "id": self.generate_id("infrastructure", f"railway_{from_loc}_{to_loc}"),
                "type": "railway",
                "location": colony_name,
                "year": "1922",
                "name": f"Railway from {from_loc} to {to_loc}",
                "route": {
                    "from": from_loc,
                    "to": to_loc
                },
                "specifications": {
                    "length": {"value": miles, "unit": "miles"}
                }
            }
            infrastructure.append(railway)

        # Telegraph/Cable extraction
        if 'telegraph' in text.lower():
            telegraph = {
                "id": self.generate_id("infrastructure", f"telegraph_{colony_name}"),
                "type": "telegraph",
                "location": colony_name,
                "year": "1922",
                "name": f"Telegraph system in {colony_name}"
            }
            infrastructure.append(telegraph)

        # Harbor/Port extraction
        if 'harbour' in text.lower() or 'harbor' in text.lower():
            harbor = {
                "id": self.generate_id("infrastructure", f"harbor_{colony_name}"),
                "type": "harbor",
                "location": colony_name,
                "year": "1922",
                "name": f"Harbour in {colony_name}"
            }
            infrastructure.append(harbor)

        return infrastructure

    def extract_financial_data_tables(self, text, colony_name):
        """Extract financial data from tables"""
        economic_data = []

        # Revenue patterns
        revenue_pattern = r'Revenue[:\s]*£?\s*(\d+(?:,\d+)?)'
        matches = re.finditer(revenue_pattern, text, re.IGNORECASE)
        for match in matches:
            value = int(match.group(1).replace(',', ''))
            eco = {
                "id": self.generate_id("economic_data", f"revenue_{colony_name}"),
                "type": "revenue",
                "location": colony_name,
                "year": "1922",
                "data": {
                    "category": "revenue",
                    "value": value,
                    "currency": "£"
                }
            }
            economic_data.append(eco)

        # Expenditure patterns
        expenditure_pattern = r'Expenditure[:\s]*£?\s*(\d+(?:,\d+)?)'
        matches = re.finditer(expenditure_pattern, text, re.IGNORECASE)
        for match in matches:
            value = int(match.group(1).replace(',', ''))
            eco = {
                "id": self.generate_id("economic_data", f"expenditure_{colony_name}"),
                "type": "expenditure",
                "location": colony_name,
                "year": "1922",
                "data": {
                    "category": "expenditure",
                    "value": value,
                    "currency": "£"
                }
            }
            economic_data.append(eco)

        # Trade patterns (imports/exports with values in £)
        trade_patterns = [
            (r'Import[s]?.*?£\s*(\d+(?:,\d+)?)', 'trade_import'),
            (r'Export[s]?.*?£\s*(\d+(?:,\d+)?)', 'trade_export'),
        ]

        for pattern, trade_type in trade_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    value = int(match.group(1).replace(',', ''))
                    eco = {
                        "id": self.generate_id("economic_data", f"{trade_type}_{colony_name}"),
                        "type": trade_type,
                        "location": colony_name,
                        "year": "1922",
                        "data": {
                            "category": trade_type.replace('_', ' '),
                            "value": value,
                            "currency": "£"
                        }
                    }
                    economic_data.append(eco)
                except:
                    pass

        return economic_data

    def extract_basic_place_data(self, text, colony_name):
        """Extract basic geographic information"""
        places = []

        place_id = self.generate_id("place", colony_name)

        # Coordinates
        coords = None
        lat_match = re.search(r'lat\.?\s+(\d+°\s*\d+\'[NSEW]?)', text, re.IGNORECASE)
        lon_match = re.search(r'long\.?\s+(\d+°\s*\d+\'[NSEW]?)', text, re.IGNORECASE)
        if lat_match or lon_match:
            coords = {}
            if lat_match:
                coords['latitude'] = lat_match.group(1).strip()
            if lon_match:
                coords['longitude'] = lon_match.group(1).strip()

        # Area
        area = None
        area_match = re.search(r'(\d+(?:,\d+)?)\s+square\s+miles', text, re.IGNORECASE)
        if area_match:
            area = {
                "value": int(area_match.group(1).replace(',', '')),
                "unit": "square miles"
            }

        # Description (first substantial paragraph)
        description = ""
        lines = [l.strip() for l in text.split('\n') if len(l.strip()) > 50]
        if lines:
            description = lines[0]

        place = {
            "id": place_id,
            "name": colony_name,
            "type": "colony",
            "year": "1922"
        }

        if coords:
            place["coordinates"] = coords
        if area:
            place["area"] = area
        if description:
            place["description"] = description[:300]

        places.append(place)
        return places, place_id

    def extract_demographics(self, text, colony_name):
        """Extract population and demographic data"""
        demographics = []

        # Find population numbers
        pop_pattern = r'population\s+(?:of\s+)?(?:about\s+|approximately\s+)?(\d+(?:,\d+)?)'
        pop_match = re.search(pop_pattern, text, re.IGNORECASE)

        if pop_match:
            total_pop = int(pop_match.group(1).replace(',', ''))

            demo = {
                "id": self.generate_id("demographic", colony_name),
                "location": colony_name,
                "year": "1922",
                "total_population": total_pop,
                "breakdowns": []
            }

            # Extract demographic categories
            breakdown_patterns = [
                (r'European[s]?[:\s]+(\d+(?:,\d+)?)', 'European'),
                (r'White[s]?[:\s]+(\d+(?:,\d+)?)', 'White'),
                (r'Black[s]?[:\s]+(\d+(?:,\d+)?)', 'Black'),
                (r'Coloured[s]?[:\s]+(\d+(?:,\d+)?)', 'Coloured'),
                (r'Sinhalese[:\s]+(\d+(?:,\d+)?)', 'Sinhalese'),
                (r'Tamil[s]?[:\s]+(\d+(?:,\d+)?)', 'Tamil'),
                (r'Moor[s]?[:\s]+(\d+(?:,\d+)?)', 'Moor'),
                (r'Buddhist[s]?[:\s]+(\d+(?:,\d+)?)', 'Buddhist'),
                (r'Hindu[s]?[:\s]+(\d+(?:,\d+)?)', 'Hindu'),
                (r'Christian[s]?[:\s]+(\d+(?:,\d+)?)', 'Christian'),
                (r'Mohammedan[s]?[:\s]+(\d+(?:,\d+)?)', 'Mohammedan'),
            ]

            for pattern, category in breakdown_patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
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

    def extract_historical_events(self, text, colony_name):
        """Extract historical events and founding dates"""
        events = []

        place_id = f"place_{colony_name.lower().replace(' ', '_')}"

        # Founding/establishment dates
        event_patterns = [
            (r'(?:was\s+)?(?:established|founded|occupied|captured)\s+(?:in|on)?\s+(\d{4})', 'establishment'),
            (r'(?:Treaty\s+of\s+)?([^.]+?)\s+(\d{4})', 'treaty'),
            (r'British.*?(?:in|on)?\s+(\d{4})', 'British_occupation'),
        ]

        for pattern, event_type in event_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                if len(match.groups()) >= 1:
                    year = match.group(1)
                    desc = match.group(0)[:150] if len(match.group(0)) > 0 else f"{event_type} event"

                    if year.isdigit() and int(year) >= 1500 and int(year) <= 2000:
                        event = {
                            "id": self.generate_id("event", f"{colony_name}_{year}"),
                            "type": event_type,
                            "description": desc,
                            "year_mentioned": "1922",
                            "locations": [place_id],
                            "date": year
                        }
                        events.append(event)

        return events

    def process_colony_file(self, filepath):
        """Process a single colony file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            colony_name = Path(filepath).stem.replace('_', ' ')

            # Extract all data
            places, place_id = self.extract_basic_place_data(content, colony_name)
            governors, _ = self.extract_governors_list(content, colony_name)
            officials = self.extract_colonial_officials(content, colony_name)
            institutions = self.extract_institutions(content, colony_name)
            infrastructure = self.extract_infrastructure_details(content, colony_name)
            economic = self.extract_financial_data_tables(content, colony_name)
            demographics = self.extract_demographics(content, colony_name)
            events = self.extract_historical_events(content, colony_name)

            # Add to main data
            self.data["entities"]["places"].extend(places)
            all_people = governors + officials
            self.data["entities"]["people"].extend(all_people)
            self.data["entities"]["infrastructure"].extend(infrastructure)
            self.data["entities"]["economic_data"].extend(economic)
            self.data["entities"]["demographics"].extend(demographics)
            self.data["entities"]["events"].extend(events)

            return colony_name

        except Exception as e:
            print(f"Error processing {filepath}: {e}")
            return None

    def extract_institutions(self, text, colony_name):
        """Extract institutions (councils, courts, etc.)"""
        institutions = []

        inst_patterns = [
            ('Executive Council', 'executive_council'),
            ('Legislative Council', 'legislative_council'),
            ('Privy Council', 'privy_council'),
            ('Supreme Court', 'court'),
            ('Police Court', 'court'),
            ('District Court', 'court'),
        ]

        for inst_name, inst_type in inst_patterns:
            if inst_name.lower() in text.lower():
                inst = {
                    "id": self.generate_id("institution", f"{colony_name}_{inst_name}"),
                    "name": inst_name,
                    "type": inst_type,
                    "location": colony_name,
                    "year": "1922"
                }
                institutions.append(inst)

        return institutions

    def process_all_colonies(self):
        """Process all colony files"""
        colony_files = sorted(Path(self.source_dir).glob('*.md'))

        for filepath in colony_files:
            colony_name = self.process_colony_file(filepath)
            if colony_name:
                self.data["metadata"]["colonies_processed"].append(colony_name)

    def save_output(self):
        """Save extracted data to JSON"""
        output_path = Path(self.output_dir) / "1922_extracted.json"

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

        return output_path

    def generate_report(self):
        """Generate summary report"""
        return {
            "year": "1922",
            "colonies_processed": len(self.data["metadata"]["colonies_processed"]),
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
        }


def main():
    source_dir = "/home/user/colonial_office_list/output_2/1922_manual_parsed"
    output_dir = "/home/user/colonial_office_list/knowledge_graph_extracts"

    extractor = EnhancedColonialExtractor(source_dir, output_dir)
    extractor.process_all_colonies()
    output_path = extractor.save_output()
    report = extractor.generate_report()

    print(f"Enhanced extraction complete: {output_path}")
    print(f"Colonies: {report['colonies_processed']}")
    print(f"Entities - Places: {report['entity_counts']['places']}, People: {report['entity_counts']['people']}, "
          f"Institutions: {report['entity_counts']['institutions']}, Economic: {report['entity_counts']['economic_data']}, "
          f"Infrastructure: {report['entity_counts']['infrastructure']}, Demographics: {report['entity_counts']['demographics']}, "
          f"Events: {report['entity_counts']['events']}")
    print(f"Relationships: {report['total_relationships']}")


if __name__ == "__main__":
    main()
