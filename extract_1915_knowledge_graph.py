#!/usr/bin/env python3
"""
Comprehensive Knowledge Graph Extraction for Colonial Office List 1915
Extracts geographic entities, people, institutions, economic data,
infrastructure, demographics, and historical events.
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path
from collections import defaultdict
import uuid

class KnowledgeGraphExtractor:
    def __init__(self, source_dir, output_file):
        self.source_dir = Path(source_dir)
        self.output_file = output_file
        self.year = "1915"
        self.data = {
            "metadata": {
                "year": self.year,
                "source_directory": str(source_dir),
                "extraction_date": datetime.utcnow().isoformat() + "Z",
                "processing_notes": "Comprehensive extraction from 45 colony files",
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
        self.id_counters = defaultdict(int)
        self.place_ids = {}
        self.person_ids = {}
        self.institution_ids = {}

    def generate_id(self, entity_type, name):
        """Generate unique ID for entity"""
        base_id = f"{entity_type}_{name[:20].lower().replace(' ', '_').replace(',', '')}"
        self.id_counters[base_id] += 1
        if self.id_counters[base_id] == 1:
            return base_id
        else:
            return f"{base_id}_{self.id_counters[base_id]}"

    def extract_location_data(self, content, colony_name):
        """Extract geographic entities from content"""
        places = []

        # Extract main colony entry
        colony_id = self.generate_id("place", colony_name)
        self.place_ids[colony_name] = colony_id

        colony_entry = {
            "id": colony_id,
            "name": colony_name,
            "type": "colony",
            "year": self.year
        }

        # Extract coordinates if present
        coord_pattern = r"latitude\s+(\d+°\s*\d+['\"]?\s*[NSEWnsew]?)\s+[and]*\s*longitude\s+(\d+°\s*\d+['\"]?\s*[NSEWnsew]?)"
        coord_match = re.search(coord_pattern, content, re.IGNORECASE)
        if coord_match:
            colony_entry["coordinates"] = {
                "latitude": coord_match.group(1),
                "longitude": coord_match.group(2)
            }

        # Extract area if present
        area_pattern = r"area\s+(?:of\s+)?[a-z\s]+(?:is\s+)?(\d+(?:,\d+)?)\s+(square\s+miles|acres|square\s+feet|km)"
        area_match = re.search(area_pattern, content, re.IGNORECASE)
        if area_match:
            colony_entry["area"] = {
                "value": float(area_match.group(1).replace(",", "")),
                "unit": area_match.group(2).lower()
            }

        places.append(colony_entry)

        # Extract subsidiary places (cities, towns, regions)
        place_patterns = [
            (r"Chief town[s]?\s+(?:and\s+)?(?:port|capital)[s]?[,:]?\s+([^,\.]+)", "city"),
            (r"([A-Z][a-z]+)\s+(?:is\s+)?(?:the\s+)?(?:only\s+)?(?:other\s+)?town", "town"),
            (r"(?:parish|district|region)\s+(?:of\s+)?([A-Z][a-z\s]+)", "region"),
            (r"(?:harbor|harbour|bay)\s+(?:of\s+)?([A-Z][a-z\s]+)", "harbor"),
            (r"([A-Z][a-z]+)\s+(?:Island|Island[s])", "island")
        ]

        for pattern, place_type in place_patterns:
            matches = re.findall(pattern, content)
            for match in matches:
                place_name = match if isinstance(match, str) else match[0]
                if place_name and len(place_name) > 2:
                    place_id = self.generate_id("place", place_name)
                    if place_name not in self.place_ids:
                        self.place_ids[place_name] = place_id

                        place_entry = {
                            "id": place_id,
                            "name": place_name.strip(),
                            "type": place_type,
                            "parent_location": colony_id,
                            "year": self.year
                        }

                        # Extract population if mentioned with place name
                        pop_pattern = rf"{re.escape(place_name)}[,\s]+(?:with\s+)?(?:a\s+)?population[^,\.]*?(\d+(?:,\d+)?)\s+(?:inhabitants|persons)"
                        pop_match = re.search(pop_pattern, content, re.IGNORECASE)
                        if pop_match:
                            place_entry["description"] = f"Population: {pop_match.group(1)}"

                        places.append(place_entry)

        return places

    def extract_people(self, content, colony_name):
        """Extract people and their positions from content"""
        people = []

        # Pattern to match person entries with titles, positions, and salaries
        # Examples: "Governor, Field-Marshal Rt. Hon. Lord Methuen, G.C.B., G.C.V.O., C.M.G."
        # "Lieut.-Governor and Chief Secretary to Government, H. A. Byatt, C.M.G., 1,300l."

        person_pattern = r"(?:^|\n)([A-Z][^,\n]+?)(?:,\s+)?(?:((?:Rt\.\s+Hon\.|Gen\.|Major|Lieut\.|Col\.|Capt\.|Sir|Lady|Rev\.|Dr\.|Prof\.)[^,\n]*?))?(?:,\s+)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*(?:\s+[A-Z]\.(?:\s+[A-Z]\.)?)?[A-Z][a-z]*)|([A-Z]{1,3}\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*))(?:,\s+((?:[A-Z]\.?[A-Z]\.?[A-Z]\.?|[A-Z][a-z]+(?:\.[A-Z])?)+(?:\s+[A-Z][a-z]+)*))?\s*,?\s*([\d,]+l\.?|[£$][\d,]+)?"

        # More targeted pattern for administrative positions
        lines = content.split('\n')
        for i, line in enumerate(lines):
            # Skip section headers and empty lines
            if not line.strip() or line.isupper() or line.startswith('#') or line.startswith('|'):
                continue

            # Look for lines with positions and names
            if re.search(r"\b(?:Governor|Secretary|Clerk|Judge|Magistrate|Director|Superintendent|Officer|Chief|Inspector)", line):
                # Extract position
                pos_match = re.match(r"^([^,]+?)\s*,\s*(.+?)(?:,\s*([\d,]+l\.?))?$", line)
                if pos_match:
                    position = pos_match.group(1).strip()
                    name_and_honors = pos_match.group(2).strip()
                    salary = pos_match.group(3).strip() if pos_match.group(3) else None

                    # Parse name and honors
                    # Pattern: "H. A. Byatt, C.M.G." or "Lord Methuen, G.C.B., G.C.V.O., C.M.G."
                    name_honors_match = re.match(r"([^,]+?)(?:\s*,\s*(.+))?$", name_and_honors)
                    if name_honors_match:
                        name = name_honors_match.group(1).strip()
                        honors_str = name_honors_match.group(2) if name_honors_match.group(2) else ""

                        # Extract titles and honors
                        titles = re.findall(r"\b(?:Sir|Lady|Gen\.|Major|Lieut\.|Col\.|Capt\.|Rev\.|Dr\.|Prof\.|Field-Marshal|Brigadier|Admiral)", name + " " + honors_str)
                        honors = [h.strip('.') for h in re.findall(r"[A-Z]+(?:\.[A-Z])*\.", honors_str)]

                        person_id = self.generate_id("person", name)
                        if name not in self.person_ids:
                            self.person_ids[name] = person_id

                            person_entry = {
                                "id": person_id,
                                "name": name,
                                "titles": titles,
                                "honors": honors,
                                "positions": [
                                    {
                                        "title": position,
                                        "location": colony_name,
                                        "year": self.year,
                                        "status": "vacant" if "vacant" in position.lower() else "permanent"
                                    }
                                ]
                            }

                            if salary:
                                person_entry["positions"][0]["salary"] = {
                                    "amount": float(salary.replace(",", "").replace("l.", "").replace("£", "")),
                                    "currency": "£",
                                    "period": "annual"
                                }

                            people.append(person_entry)

        return people

    def extract_institutions(self, content, colony_name):
        """Extract institutional entities"""
        institutions = []

        # Extract Executive Council
        if "Executive Council" in content:
            exec_council_id = self.generate_id("institution", f"{colony_name}_executive_council")
            institutions.append({
                "id": exec_council_id,
                "name": f"Executive Council of {colony_name}",
                "type": "executive_council",
                "location": colony_name,
                "year": self.year
            })

        # Extract Legislative Council
        if "Legislative Council" in content or "House of Assembly" in content:
            leg_council_id = self.generate_id("institution", f"{colony_name}_legislative_council")
            institutions.append({
                "id": leg_council_id,
                "name": f"Legislative Council of {colony_name}",
                "type": "legislative_council",
                "location": colony_name,
                "year": self.year
            })

        # Extract courts
        court_types = [
            ("Supreme Court", "court"),
            ("Court of Appeal", "court"),
            ("Criminal Court", "court"),
            ("Civil Court", "court"),
            ("Vice-Admiralty", "court"),
            ("Police Court", "court")
        ]

        for court_name, court_type in court_types:
            if court_name in content:
                court_id = self.generate_id("institution", f"{colony_name}_{court_name}")
                institutions.append({
                    "id": court_id,
                    "name": f"{court_name} of {colony_name}",
                    "type": court_type,
                    "location": colony_name,
                    "year": self.year
                })

        # Extract departments
        departments = [
            "Colonial Secretary", "Treasury", "Survey", "Police Force",
            "Public Works", "Education", "Medical", "Postal", "Military"
        ]

        for dept in departments:
            if dept in content:
                dept_id = self.generate_id("institution", f"{colony_name}_{dept}")
                institutions.append({
                    "id": dept_id,
                    "name": f"{dept} of {colony_name}",
                    "type": "department",
                    "location": colony_name,
                    "year": self.year
                })

        return institutions

    def extract_economic_data(self, content, colony_name):
        """Extract economic and financial information"""
        economic_data = []

        # Extract revenue and expenditure from tables
        table_pattern = r"\|?\s*Year\s*\|?\s*Revenue\s*\|?\s*Expenditure\s*\|?.*?(?=\n[^|]|\Z)"
        table_match = re.search(table_pattern, content, re.IGNORECASE | re.DOTALL)

        if table_match:
            table_text = table_match.group(0)
            # Extract rows
            rows = re.findall(r"\|\s*(\d{4}(?:-\d{1,2})?)?\s*\|\s*([\d,]+)\s*\|\s*([\d,]+)\s*\|", table_text)

            for row in rows:
                if row[0]:  # Has year
                    year = row[0]
                    # Revenue
                    if row[1]:
                        econ_id = self.generate_id("economic", f"{colony_name}_revenue_{year}")
                        economic_data.append({
                            "id": econ_id,
                            "type": "revenue",
                            "location": colony_name,
                            "year": self.year,
                            "data": {
                                "category": "Total Revenue",
                                "value": float(row[1].replace(",", "")),
                                "currency": "£"
                            }
                        })

                    # Expenditure
                    if row[2]:
                        econ_id = self.generate_id("economic", f"{colony_name}_expenditure_{year}")
                        economic_data.append({
                            "id": econ_id,
                            "type": "expenditure",
                            "location": colony_name,
                            "year": self.year,
                            "data": {
                                "category": "Total Expenditure",
                                "value": float(row[2].replace(",", "")),
                                "currency": "£"
                            }
                        })

        # Extract trade data
        # Imports
        imports_pattern = r"\|?\s*Year\s*\|?\s*From\s+U\.K\..*?(?=\n[^|]|\Z)"
        imports_match = re.search(imports_pattern, content, re.IGNORECASE | re.DOTALL)
        if imports_match:
            import_rows = re.findall(r"\|\s*(\d{4})\s*\|.*?\|\s*([\d,]+)\s*\|", imports_match.group(0))
            for row in import_rows:
                year = row[0]
                value = row[1]
                econ_id = self.generate_id("economic", f"{colony_name}_imports_{year}")
                economic_data.append({
                    "id": econ_id,
                    "type": "trade_import",
                    "location": colony_name,
                    "year": self.year,
                    "data": {
                        "category": "Total Imports",
                        "value": float(value.replace(",", "")),
                        "currency": "£"
                    }
                })

        # Extract sugar/commodity production
        sugar_pattern = r"(\d+(?:,\d+)?)\s+hogsheads\s+of\s+(?:sugar|[a-z\s]+)"
        sugar_matches = re.findall(sugar_pattern, content, re.IGNORECASE)
        if sugar_matches:
            for match in sugar_matches[:1]:  # Just get first instance
                econ_id = self.generate_id("economic", f"{colony_name}_sugar_production")
                economic_data.append({
                    "id": econ_id,
                    "type": "production",
                    "location": colony_name,
                    "year": self.year,
                    "data": {
                        "category": "Sugar Production",
                        "value": float(match.replace(",", "")),
                        "unit": "hogsheads"
                    }
                })

        return economic_data

    def extract_infrastructure(self, content, colony_name):
        """Extract infrastructure information"""
        infrastructure = []

        # Railway
        if "railway" in content.lower():
            railway_id = self.generate_id("infrastructure", f"{colony_name}_railway")
            infrastructure.append({
                "id": railway_id,
                "type": "railway",
                "name": f"Railway",
                "location": colony_name,
                "year": self.year
            })

        # Telegraph
        if "telegraph" in content.lower():
            telegraph_id = self.generate_id("infrastructure", f"{colony_name}_telegraph")
            infrastructure.append({
                "id": telegraph_id,
                "type": "telegraph",
                "name": f"Telegraph Service",
                "location": colony_name,
                "year": self.year
            })

        # Postal
        if "postal" in content.lower() or "post office" in content.lower():
            postal_id = self.generate_id("infrastructure", f"{colony_name}_postal")
            infrastructure.append({
                "id": postal_id,
                "type": "postal_route",
                "name": f"Postal Service",
                "location": colony_name,
                "year": self.year
            })

        # Dock/Harbor
        if "dock" in content.lower() or "harbor" in content.lower():
            dock_id = self.generate_id("infrastructure", f"{colony_name}_dock")
            infrastructure.append({
                "id": dock_id,
                "type": "dock",
                "name": f"Dock/Harbor",
                "location": colony_name,
                "year": self.year
            })

        # Water works
        if "water" in content.lower() and ("works" in content.lower() or "supply" in content.lower()):
            water_id = self.generate_id("infrastructure", f"{colony_name}_water")
            infrastructure.append({
                "id": water_id,
                "type": "water_works",
                "name": f"Water Supply",
                "location": colony_name,
                "year": self.year
            })

        return infrastructure

    def extract_demographics(self, content, colony_name):
        """Extract demographic information"""
        demographics = []

        # Extract population data from census information
        pop_pattern = r"(?:census|population).*?(\d{4}).*?(\d+(?:,\d+)?)\s+(?:inhabitants|persons|population)"
        pop_matches = re.findall(pop_pattern, content, re.IGNORECASE)

        if pop_matches:
            demo_id = self.generate_id("demographics", f"{colony_name}_population")

            # Use most recent census
            census_year = pop_matches[-1][0]
            total_pop = float(pop_matches[-1][1].replace(",", ""))

            demo_entry = {
                "id": demo_id,
                "location": colony_name,
                "year": self.year,
                "census_date": census_year,
                "total_population": int(total_pop),
                "breakdowns": []
            }

            # Try to extract demographic breakdowns
            breakdown_pattern = r"(?:Male|Female|British|White|Black|Mixed).*?(?:population|persons)?.*?[:\s]+(\d+(?:,\d+)?)"
            breakdown_matches = re.findall(breakdown_pattern, content, re.IGNORECASE)

            for match in breakdown_matches:
                demo_entry["breakdowns"].append({
                    "category": "Various categories",
                    "count": int(match.replace(",", ""))
                })

            demographics.append(demo_entry)

        return demographics

    def extract_events(self, content, colony_name):
        """Extract historical events"""
        events = []

        # Extract establishment/founding dates
        establish_pattern = r"(?:established|founded|ceded|granted|annexed|settled)\s+(?:in\s+)?(\d{3,4})"
        establish_matches = re.findall(establish_pattern, content, re.IGNORECASE)

        for year_str in establish_matches[:3]:  # Limit to first 3
            year = year_str
            event_id = self.generate_id("event", f"{colony_name}_establishment_{year}")
            events.append({
                "id": event_id,
                "date": year,
                "type": "establishment",
                "description": f"{colony_name} historical event/establishment",
                "locations": [self.place_ids.get(colony_name, "")],
                "year_mentioned": self.year
            })

        # Extract treaty information
        if "treaty" in content.lower():
            treaty_id = self.generate_id("event", f"{colony_name}_treaty")
            events.append({
                "id": treaty_id,
                "type": "treaty",
                "description": "Treaty mentioned in colonial records",
                "locations": [self.place_ids.get(colony_name, "")],
                "year_mentioned": self.year
            })

        return events

    def build_relationships(self):
        """Build relationships between entities"""
        relationships = []

        # Add PART_OF relationships for places with parent_location
        for place in self.data["entities"]["places"]:
            if "parent_location" in place:
                rel_id = f"rel_{len(relationships)}"
                relationships.append({
                    "source_id": place["id"],
                    "relationship_type": "PART_OF",
                    "target_id": place["parent_location"],
                    "properties": {
                        "year": self.year
                    }
                })

        # Add GOVERNED_BY relationships (person governs location)
        for person in self.data["entities"]["people"]:
            if person["positions"]:
                for pos in person["positions"]:
                    if "Governor" in pos.get("title", "") or "Chief" in pos.get("title", ""):
                        if pos.get("location") in self.place_ids:
                            relationships.append({
                                "source_id": self.place_ids[pos["location"]],
                                "relationship_type": "GOVERNED_BY",
                                "target_id": person["id"],
                                "properties": {
                                    "year": self.year,
                                    "position": pos.get("title", "")
                                }
                            })

        return relationships

    def process_all_files(self):
        """Process all colony files"""
        files = sorted([f for f in self.source_dir.glob("*.md") if f.stat().st_size > 0])

        for file_path in files:
            colony_name = file_path.stem

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Extract all entity types
                self.data["entities"]["places"].extend(self.extract_location_data(content, colony_name))
                self.data["entities"]["people"].extend(self.extract_people(content, colony_name))
                self.data["entities"]["institutions"].extend(self.extract_institutions(content, colony_name))
                self.data["entities"]["economic_data"].extend(self.extract_economic_data(content, colony_name))
                self.data["entities"]["infrastructure"].extend(self.extract_infrastructure(content, colony_name))
                self.data["entities"]["demographics"].extend(self.extract_demographics(content, colony_name))
                self.data["entities"]["events"].extend(self.extract_events(content, colony_name))

                self.data["metadata"]["colonies_processed"].append(colony_name)

            except Exception as e:
                print(f"Error processing {colony_name}: {e}")

        # Build relationships after all entities are extracted
        self.data["relationships"] = self.build_relationships()

    def save(self):
        """Save to JSON file"""
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)
        print(f"Knowledge graph saved to {self.output_file}")

    def generate_report(self):
        """Generate extraction report"""
        report = {
            "year": self.year,
            "total_colonies": len(self.data["metadata"]["colonies_processed"]),
            "entity_counts": {
                "places": len(self.data["entities"]["places"]),
                "people": len(self.data["entities"]["people"]),
                "institutions": len(self.data["entities"]["institutions"]),
                "economic_data": len(self.data["entities"]["economic_data"]),
                "infrastructure": len(self.data["entities"]["infrastructure"]),
                "demographics": len(self.data["entities"]["demographics"]),
                "events": len(self.data["entities"]["events"])
            },
            "relationship_count": len(self.data["relationships"]),
            "colonies_processed": self.data["metadata"]["colonies_processed"]
        }
        return report

def main():
    source_dir = "/home/user/colonial_office_list/output_2/1915_manual_parsed"
    output_file = "/home/user/colonial_office_list/knowledge_graph_extracts/1915_extracted.json"

    extractor = KnowledgeGraphExtractor(source_dir, output_file)
    extractor.process_all_files()
    extractor.save()

    report = extractor.generate_report()
    print("\n" + "="*60)
    print("EXTRACTION REPORT - 1915 COLONIAL OFFICE LIST")
    print("="*60)
    print(f"Year: {report['year']}")
    print(f"Total Colonies Processed: {report['total_colonies']}")
    print(f"\nEntity Counts by Type:")
    for entity_type, count in report['entity_counts'].items():
        print(f"  {entity_type}: {count}")
    print(f"\nRelationships: {report['relationship_count']}")
    print(f"\nFile created: {output_file}")
    print("="*60)

if __name__ == "__main__":
    main()
