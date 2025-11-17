#!/usr/bin/env python3
"""
Colonial Office List Knowledge Graph Extraction Script
Extracts structured data from markdown files and generates JSON knowledge graphs
"""

import os
import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional
import hashlib
import uuid

class KnowledgeGraphExtractor:
    def __init__(self, year: str, source_dir: str, output_dir: str):
        self.year = year
        self.source_dir = Path(source_dir)
        self.output_dir = Path(output_dir)
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
        self.colonies_processed = []
        self.entity_ids = {}  # Track entities to avoid duplicates

    def generate_id(self, entity_type: str, name: str) -> str:
        """Generate a unique ID for an entity"""
        hash_key = f"{entity_type}_{name}_{self.year}"
        hash_obj = hashlib.md5(hash_key.encode())
        return f"{entity_type}_{hash_obj.hexdigest()[:8]}"

    def read_markdown_file(self, filepath: Path) -> str:
        """Read a markdown file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
            return ""

    def extract_places(self, content: str, colony_name: str) -> List[Dict[str, Any]]:
        """Extract geographic entities from content"""
        places = []

        # Extract from Area section
        area_match = re.search(r'(?:^|\n)Area\s*(?:\n|$)(.*?)(?:\n(?:Population|Geographical|Climate|History|Constitution|$))',
                              content, re.MULTILINE | re.DOTALL | re.IGNORECASE)
        if area_match:
            area_text = area_match.group(1)
            # Extract area measurements
            area_pattern = r'(\d+\.?\d*)\s*(?:square\s+)?miles?'
            area_matches = re.finditer(area_pattern, area_text, re.IGNORECASE)
            for match in area_matches:
                area_value = float(match.group(1))
                place_id = self.generate_id("place", colony_name)
                if place_id not in self.entity_ids:
                    self.entity_ids[place_id] = True
                    places.append({
                        "id": place_id,
                        "name": colony_name,
                        "type": "colony",
                        "area": {
                            "value": area_value,
                            "unit": "square miles"
                        },
                        "description": area_text.strip()[:500],
                        "year": self.year
                    })

        # Extract coordinates if present
        coord_pattern = r'(?:Latitude|Coordinates?).*?(\d+°\s*\d+\'.*?)(?:\n|$)'
        coord_matches = re.finditer(coord_pattern, content, re.IGNORECASE)
        for match in coord_matches:
            coord_text = match.group(1)
            place_id = self.generate_id("place", f"{colony_name}_coords")
            if place_id not in self.entity_ids:
                self.entity_ids[place_id] = True
                places.append({
                    "id": place_id,
                    "name": colony_name,
                    "type": "colony",
                    "coordinates": {
                        "latitude": coord_text.strip(),
                        "longitude": ""
                    },
                    "year": self.year
                })

        # Extract towns/cities from principal towns section
        towns_match = re.search(r'(?:^|\n)Principal\s+Towns?.*?(?:\n|$)(.*?)(?:\n(?:Geographical|Population|Area|$))',
                               content, re.MULTILINE | re.DOTALL | re.IGNORECASE)
        if towns_match:
            towns_text = towns_match.group(1)
            # Extract town entries from tables
            town_lines = re.findall(r'\|\s*([^\|]+)\s*\|\s*(\d+(?:,\d+)*)\s*\|', towns_text)
            for town_name, population in town_lines:
                town_name = town_name.strip()
                if town_name and town_name not in ['Population', 'Town', '']:
                    place_id = self.generate_id("place", town_name)
                    if place_id not in self.entity_ids:
                        self.entity_ids[place_id] = True
                        places.append({
                            "id": place_id,
                            "name": town_name,
                            "type": "city" if int(population.replace(',', '')) > 10000 else "town",
                            "parent_location": self.generate_id("place", colony_name),
                            "description": f"Town in {colony_name}",
                            "year": self.year
                        })

        # Extract geographic features
        features_match = re.search(r'(?:^|\n)Geographical\s+Features.*?(?:\n|$)(.*?)(?:\n(?:Climate|Population|Area|History|$))',
                                  content, re.MULTILINE | re.DOTALL | re.IGNORECASE)
        if features_match:
            features_text = features_match.group(1)
            # Extract feature names (rivers, mountains, bays, etc.)
            feature_patterns = [
                r'(?:The )?([A-Z][a-z\s]+)(?:River|Mountain|Bay|Harbor|Island|Peninsula)',
            ]
            for pattern in feature_patterns:
                feature_matches = re.finditer(pattern, features_text)
                for match in feature_matches:
                    feature_name = match.group(1).strip()
                    if feature_name and len(feature_name) > 2:
                        place_id = self.generate_id("place", feature_name)
                        if place_id not in self.entity_ids:
                            self.entity_ids[place_id] = True
                            places.append({
                                "id": place_id,
                                "name": feature_name,
                                "type": "feature",
                                "description": features_text.strip()[:500],
                                "year": self.year
                            })

        # Add main colony if not already added
        colony_id = self.generate_id("place", colony_name)
        if colony_id not in self.entity_ids:
            self.entity_ids[colony_id] = True
            places.insert(0, {
                "id": colony_id,
                "name": colony_name,
                "type": "colony",
                "description": f"{colony_name} colonial territory",
                "year": self.year
            })

        return places

    def extract_people(self, content: str, colony_name: str) -> List[Dict[str, Any]]:
        """Extract people from content (administration, officials, etc.)"""
        people = []

        # Pattern for officials: Title(s) FirstName LastName - Position - Location - Salary
        # Looking for sections like "Governor", "Colonial Secretary", etc.

        official_patterns = [
            r'(?:Governor|Chief Commissioner|Administrator|Commissioner|Chief Executive|President).*?([A-Z][a-z]+ (?:[A-Z]\.?\s?)*[A-Z][a-z]+)',
            r'(?:Colonial\s+Secretary|Attorney-?General|Financial\s+Secretary|Treasurer|Secretary).*?([A-Z][a-z]+ (?:[A-Z]\.?\s?)*[A-Z][a-z]+)',
        ]

        for pattern in official_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                try:
                    name = match.group(1).strip()
                    if name and len(name) > 2:
                        person_id = self.generate_id("person", name)
                        if person_id not in self.entity_ids:
                            self.entity_ids[person_id] = True
                            people.append({
                                "id": person_id,
                                "name": name,
                                "positions": [{
                                    "title": "Colonial Official",
                                    "location": colony_name,
                                    "year": self.year,
                                    "status": "permanent"
                                }]
                            })
                except:
                    pass

        # Look for salary information in tables
        salary_pattern = r'\|?\s*([A-Z][a-z]+ (?:[A-Z]\.?\s?)*[A-Z][a-z]+)\s*\|.*?(?:£|Rs\.?|$)(\d+(?:,\d+)*)'
        matches = re.finditer(salary_pattern, content)
        for match in matches:
            try:
                name = match.group(1).strip()
                salary = match.group(2).replace(',', '')
                if name and len(name) > 2:
                    person_id = self.generate_id("person", name)
                    if person_id not in self.entity_ids:
                        self.entity_ids[person_id] = True
                        people.append({
                            "id": person_id,
                            "name": name,
                            "positions": [{
                                "title": "Official",
                                "location": colony_name,
                                "salary": {
                                    "amount": int(salary),
                                    "currency": "£",
                                    "period": "annual"
                                },
                                "year": self.year,
                                "status": "permanent"
                            }]
                        })
            except:
                pass

        return people

    def extract_institutions(self, content: str, colony_name: str) -> List[Dict[str, Any]]:
        """Extract institutions (councils, courts, departments, etc.)"""
        institutions = []

        # Extract Executive Council
        if re.search(r'Executive Council', content, re.IGNORECASE):
            inst_id = self.generate_id("institution", f"{colony_name}_executive_council")
            if inst_id not in self.entity_ids:
                self.entity_ids[inst_id] = True
                institutions.append({
                    "id": inst_id,
                    "name": f"Executive Council of {colony_name}",
                    "type": "executive_council",
                    "location": colony_name,
                    "function": "Executive governing body",
                    "year": self.year
                })

        # Extract Legislative Council
        if re.search(r'Legislative Council', content, re.IGNORECASE):
            inst_id = self.generate_id("institution", f"{colony_name}_legislative_council")
            if inst_id not in self.entity_ids:
                self.entity_ids[inst_id] = True
                institutions.append({
                    "id": inst_id,
                    "name": f"Legislative Council of {colony_name}",
                    "type": "legislative_council",
                    "location": colony_name,
                    "function": "Legislative governing body",
                    "year": self.year
                })

        # Extract other departments
        departments = ['Colonial Secretary', 'Attorney-General', 'Financial Secretary', 'Treasury',
                      'Police', 'Military', 'Public Works', 'Education', 'Health', 'Survey']
        for dept in departments:
            if re.search(rf'{dept}', content, re.IGNORECASE):
                inst_id = self.generate_id("institution", f"{colony_name}_{dept.lower()}")
                if inst_id not in self.entity_ids:
                    self.entity_ids[inst_id] = True
                    institutions.append({
                        "id": inst_id,
                        "name": f"{dept} of {colony_name}",
                        "type": "department",
                        "location": colony_name,
                        "function": f"{dept} administrative body",
                        "year": self.year
                    })

        return institutions

    def extract_economic_data(self, content: str, colony_name: str) -> List[Dict[str, Any]]:
        """Extract economic and financial data"""
        economic_data = []

        # Look for Revenue and Expenditure tables
        financial_pattern = r'(?:Public\s+Finance|Revenue|Expenditure).*?\n.*?\n(.*?)(?:\n\n|\Z)'
        matches = re.finditer(financial_pattern, content, re.MULTILINE | re.DOTALL | re.IGNORECASE)

        for match in matches:
            table_content = match.group(1)
            # Extract table rows with numbers
            rows = re.findall(r'\|\s*([\d\-]+[–—]?[\d\-]*)\s*\|\s*([\d,]+)\s*\|\s*([\d,]+)', table_content)
            for year_range, revenue, expenditure in rows:
                if year_range and revenue:
                    try:
                        rev_value = int(revenue.replace(',', ''))
                        econ_id = self.generate_id("economic", f"{colony_name}_revenue_{year_range}")
                        if econ_id not in self.entity_ids:
                            self.entity_ids[econ_id] = True
                            economic_data.append({
                                "id": econ_id,
                                "type": "revenue",
                                "location": colony_name,
                                "year": self.year,
                                "data": {
                                    "category": f"Revenue {year_range}",
                                    "value": rev_value,
                                    "currency": "£"
                                }
                            })

                        if expenditure:
                            exp_value = int(expenditure.replace(',', ''))
                            econ_id = self.generate_id("economic", f"{colony_name}_expenditure_{year_range}")
                            if econ_id not in self.entity_ids:
                                self.entity_ids[econ_id] = True
                                economic_data.append({
                                    "id": econ_id,
                                    "type": "expenditure",
                                    "location": colony_name,
                                    "year": self.year,
                                    "data": {
                                        "category": f"Expenditure {year_range}",
                                        "value": exp_value,
                                        "currency": "£"
                                    }
                                })
                    except:
                        pass

        # Extract trade and commerce data
        trade_pattern = r'(?:Trade|Commerce|Exports?|Imports?|Shipping).*?([A-Z][a-z]+)\s+([\d,]+)'
        matches = re.finditer(trade_pattern, content, re.IGNORECASE)
        for match in matches:
            try:
                category = match.group(1).strip()
                value = int(match.group(2).replace(',', ''))
                econ_id = self.generate_id("economic", f"{colony_name}_{category}")
                if econ_id not in self.entity_ids:
                    self.entity_ids[econ_id] = True
                    economic_data.append({
                        "id": econ_id,
                        "type": "trade_export" if "export" in category.lower() else "trade_import",
                        "location": colony_name,
                        "year": self.year,
                        "data": {
                            "category": category,
                            "value": value,
                            "currency": "£"
                        }
                    })
            except:
                pass

        return economic_data

    def extract_infrastructure(self, content: str, colony_name: str) -> List[Dict[str, Any]]:
        """Extract infrastructure data (railways, telegraph, docks, etc.)"""
        infrastructure = []

        # Look for railway information
        if re.search(r'Railway|Rail\s+way', content, re.IGNORECASE):
            rail_pattern = r'[Rr]ailway.*?(\d+\.?\d*)\s*miles?'
            matches = re.finditer(rail_pattern, content)
            for match in matches:
                try:
                    length = float(match.group(1))
                    infra_id = self.generate_id("infrastructure", f"{colony_name}_railway")
                    if infra_id not in self.entity_ids:
                        self.entity_ids[infra_id] = True
                        infrastructure.append({
                            "id": infra_id,
                            "type": "railway",
                            "name": f"Railway system in {colony_name}",
                            "location": colony_name,
                            "specifications": {
                                "length": {
                                    "value": length,
                                    "unit": "miles"
                                }
                            },
                            "year": self.year
                        })
                except:
                    pass

        # Look for telegraph information
        if re.search(r'Telegraph|Cable', content, re.IGNORECASE):
            telegraph_pattern = r'[Tt]elegraph.*?(\d+\.?\d*)\s*miles?'
            matches = re.finditer(telegraph_pattern, content)
            for match in matches:
                try:
                    length = float(match.group(1))
                    infra_id = self.generate_id("infrastructure", f"{colony_name}_telegraph")
                    if infra_id not in self.entity_ids:
                        self.entity_ids[infra_id] = True
                        infrastructure.append({
                            "id": infra_id,
                            "type": "telegraph",
                            "name": f"Telegraph system in {colony_name}",
                            "location": colony_name,
                            "specifications": {
                                "length": {
                                    "value": length,
                                    "unit": "miles"
                                }
                            },
                            "year": self.year
                        })
                except:
                    pass

        # Look for ports and docks
        if re.search(r'Port|Dock|Harbor|Harbour', content, re.IGNORECASE):
            infra_id = self.generate_id("infrastructure", f"{colony_name}_port")
            if infra_id not in self.entity_ids:
                self.entity_ids[infra_id] = True
                infrastructure.append({
                    "id": infra_id,
                    "type": "dock",
                    "name": f"Port facilities in {colony_name}",
                    "location": colony_name,
                    "year": self.year
                })

        return infrastructure

    def extract_demographics(self, content: str, colony_name: str) -> List[Dict[str, Any]]:
        """Extract demographic information"""
        demographics = []

        # Look for population data
        pop_pattern = r'(?:Population|Census).*?total\s+population\s+(?:recorded\s+)?(?:was\s+)?(\d+(?:,\d+)*)'
        matches = re.finditer(pop_pattern, content, re.IGNORECASE | re.DOTALL)

        for match in matches:
            try:
                total_pop = int(match.group(1).replace(',', ''))
                demo_id = self.generate_id("demographic", f"{colony_name}_population")
                if demo_id not in self.entity_ids:
                    self.entity_ids[demo_id] = True
                    demo_entry = {
                        "id": demo_id,
                        "location": colony_name,
                        "year": self.year,
                        "total_population": total_pop,
                        "breakdowns": []
                    }

                    # Extract population breakdowns from tables
                    breakdown_pattern = r'\|\s*([A-Za-z\s]+)\s*\|\s*([\d\.]+)\s*\|'
                    breakdown_matches = re.finditer(breakdown_pattern, content)
                    for breakdown_match in breakdown_matches:
                        category = breakdown_match.group(1).strip()
                        percentage = breakdown_match.group(2).strip()
                        if category and category not in ['Per cent', 'Category', 'Percentage', '']:
                            try:
                                demo_entry["breakdowns"].append({
                                    "category": category,
                                    "count": int(float(percentage) * total_pop / 100),
                                    "subcategories": {}
                                })
                            except:
                                pass

                    demographics.append(demo_entry)
            except:
                pass

        return demographics

    def extract_events(self, content: str, colony_name: str) -> List[Dict[str, Any]]:
        """Extract historical events and dates"""
        events = []

        # Look for key historical events with dates
        event_patterns = [
            (r'(?:established|founded|created)\s+(?:in\s+)?(\d{4})', 'establishment'),
            (r'(?:cession|ceded|transferred)\s+(?:in\s+)?(\d{4})', 'cession'),
            (r'(?:treaty|agreement)\s+(?:in\s+)?(\d{4})', 'treaty'),
            (r'(?:rebellion|revolt)\s+(?:in\s+)?(\d{4})', 'rebellion'),
            (r'(?:order|constitution)\s+(?:in\s+)?(\d{4})', 'constitutional_change'),
        ]

        for pattern, event_type in event_patterns:
            matches = re.finditer(pattern, content, re.IGNORECASE)
            for match in matches:
                try:
                    event_year = match.group(1)
                    # Extract surrounding context
                    start = max(0, match.start() - 100)
                    end = min(len(content), match.end() + 100)
                    context = content[start:end].strip()

                    event_id = self.generate_id("event", f"{colony_name}_{event_type}_{event_year}")
                    if event_id not in self.entity_ids:
                        self.entity_ids[event_id] = True
                        events.append({
                            "id": event_id,
                            "date": event_year,
                            "type": event_type,
                            "description": context[:300],
                            "locations": [self.generate_id("place", colony_name)],
                            "year_mentioned": self.year
                        })
                except:
                    pass

        return events

    def process_colony(self, filepath: Path) -> None:
        """Process a single colony file"""
        content = self.read_markdown_file(filepath)
        if not content:
            return

        colony_name = filepath.stem.upper()
        print(f"  Processing {colony_name}...")

        # Extract all entity types
        self.entities["places"].extend(self.extract_places(content, colony_name))
        self.entities["people"].extend(self.extract_people(content, colony_name))
        self.entities["institutions"].extend(self.extract_institutions(content, colony_name))
        self.entities["economic_data"].extend(self.extract_economic_data(content, colony_name))
        self.entities["infrastructure"].extend(self.extract_infrastructure(content, colony_name))
        self.entities["demographics"].extend(self.extract_demographics(content, colony_name))
        self.entities["events"].extend(self.extract_events(content, colony_name))

        self.colonies_processed.append(colony_name)

    def create_relationships(self) -> None:
        """Create relationships between entities"""
        # Add location relationships for people
        for person in self.entities["people"]:
            for position in person.get("positions", []):
                location_name = position.get("location", "")
                if location_name:
                    location_id = self.generate_id("place", location_name)
                    # Check if location exists
                    for place in self.entities["places"]:
                        if place.get("name") == location_name:
                            self.relationships.append({
                                "source_id": person["id"],
                                "relationship_type": "GOVERNED_BY",
                                "target_id": location_id,
                                "properties": {
                                    "year": self.year,
                                    "position": position.get("title", "")
                                }
                            })
                            break

        # Add institutional relationships
        for institution in self.entities["institutions"]:
            location_id = self.generate_id("place", institution.get("location", ""))
            self.relationships.append({
                "source_id": institution["id"],
                "relationship_type": "ADMINISTERS",
                "target_id": location_id,
                "properties": {
                    "year": self.year
                }
            })

    def generate_output(self) -> Dict[str, Any]:
        """Generate the complete knowledge graph output"""
        self.create_relationships()

        output = {
            "metadata": {
                "year": self.year,
                "source_directory": str(self.source_dir),
                "extraction_date": datetime.now().isoformat(),
                "processing_notes": f"Automated extraction from {len(self.colonies_processed)} colony files",
                "colonies_processed": sorted(self.colonies_processed)
            },
            "entities": self.entities,
            "relationships": self.relationships
        }

        return output

    def process_year(self) -> bool:
        """Process all colony files for the year"""
        if not self.source_dir.exists():
            print(f"Source directory not found: {self.source_dir}")
            return False

        print(f"\nProcessing year {self.year}...")

        # Get all markdown files
        md_files = sorted(self.source_dir.glob("*.md"))
        if not md_files:
            print(f"No markdown files found in {self.source_dir}")
            return False

        # Process each colony
        for md_file in md_files:
            self.process_colony(md_file)

        # Generate output
        output = self.generate_output()

        # Save to JSON
        self.output_dir.mkdir(parents=True, exist_ok=True)
        output_file = self.output_dir / f"{self.year}_extracted.json"

        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output, f, indent=2, ensure_ascii=False)
            print(f"✓ Saved to {output_file}")
            return True
        except Exception as e:
            print(f"Error saving output: {e}")
            return False


def main():
    """Main extraction process"""
    base_dir = "/home/user/colonial_office_list"
    output_dir = Path(base_dir) / "knowledge_graph_extracts"

    years = ["1957", "1958", "1959", "1960", "1961", "1962"]

    results = {}

    for year in years:
        source_dir = Path(base_dir) / "output_2" / f"{year}_manual_parsed"
        extractor = KnowledgeGraphExtractor(year, str(source_dir), str(output_dir))

        success = extractor.process_year()

        if success:
            # Count entities
            entity_counts = {
                "places": len(extractor.entities["places"]),
                "people": len(extractor.entities["people"]),
                "institutions": len(extractor.entities["institutions"]),
                "economic_data": len(extractor.entities["economic_data"]),
                "infrastructure": len(extractor.entities["infrastructure"]),
                "demographics": len(extractor.entities["demographics"]),
                "events": len(extractor.entities["events"]),
                "relationships": len(extractor.relationships),
                "colonies_processed": len(extractor.colonies_processed)
            }
            results[year] = entity_counts

            print(f"\nYear {year} Statistics:")
            print(f"  Colonies: {entity_counts['colonies_processed']}")
            print(f"  Places: {entity_counts['places']}")
            print(f"  People: {entity_counts['people']}")
            print(f"  Institutions: {entity_counts['institutions']}")
            print(f"  Economic Data: {entity_counts['economic_data']}")
            print(f"  Infrastructure: {entity_counts['infrastructure']}")
            print(f"  Demographics: {entity_counts['demographics']}")
            print(f"  Events: {entity_counts['events']}")
            print(f"  Relationships: {entity_counts['relationships']}")
            print(f"  Total Entities: {sum(entity_counts[k] for k in ['places', 'people', 'institutions', 'economic_data', 'infrastructure', 'demographics', 'events'])}")

    # Print summary
    print("\n" + "="*60)
    print("EXTRACTION COMPLETE")
    print("="*60)

    for year in years:
        if year in results:
            counts = results[year]
            total = sum(counts[k] for k in ['places', 'people', 'institutions', 'economic_data', 'infrastructure', 'demographics', 'events'])
            print(f"{year}: {counts['colonies_processed']} colonies → {total} entities")

    # Verify files
    print("\nFile verification:")
    output_dir.mkdir(parents=True, exist_ok=True)
    for year in years:
        output_file = output_dir / f"{year}_extracted.json"
        if output_file.exists():
            file_size = output_file.stat().st_size
            print(f"  ✓ {year}_extracted.json ({file_size:,} bytes)")
        else:
            print(f"  ✗ {year}_extracted.json (NOT FOUND)")


if __name__ == "__main__":
    main()
