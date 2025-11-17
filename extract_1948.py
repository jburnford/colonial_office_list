#!/usr/bin/env python3
"""
Colonial Office List 1948 Knowledge Graph Extraction
Extracts structured data from colony files following the EXTRACTION_METHODOLOGY.md
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any
import uuid

class ColonialOfficeExtractor:
    def __init__(self, source_dir: str, schema_path: str):
        self.source_dir = source_dir
        self.schema_path = schema_path
        self.year = "1948"
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
        self.entity_ids = {}  # Track IDs for deduplication
        self.person_mentions = {}  # Track persons across colonies

    def generate_id(self, entity_type: str, name: str) -> str:
        """Generate unique IDs for entities"""
        base_id = f"{entity_type}_{name.lower().replace(' ', '_').replace('.', '').replace(',', '')}"
        if base_id in self.entity_ids:
            self.entity_ids[base_id] += 1
            return f"{base_id}_{self.entity_ids[base_id]}"
        self.entity_ids[base_id] = 0
        return base_id

    def extract_coordinates(self, text: str) -> Dict[str, str]:
        """Extract latitude and longitude from text"""
        coords = {}
        # Pattern for coordinates like "17° 43' N" or "76° 11' W"
        lat_pattern = r"(\d+°\s*\d+[\'′]?\s*[NS]\.?)"
        lon_pattern = r"(\d+°\s*\d+[\'′]?\s*[EW]\.?)"

        lat_match = re.search(lat_pattern, text)
        lon_match = re.search(lon_pattern, text)

        if lat_match:
            coords["latitude"] = lat_match.group(1).strip()
        if lon_match:
            coords["longitude"] = lon_match.group(1).strip()

        return coords if coords else None

    def extract_population_data(self, text: str, location: str) -> None:
        """Extract demographic information"""
        # Look for population tables and figures
        pop_patterns = [
            r"(?:total\s+)?population[:\s]+([0-9,]+)",
            r"(?:in\s+)?(\d{4})[:\s]+([0-9,]+)",
        ]

        for pattern in pop_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    if len(match.groups()) == 1:
                        pop_value = int(match.group(1).replace(",", ""))
                        demo_id = self.generate_id("demographic", f"{location}_{self.year}")
                        self.entities["demographics"].append({
                            "id": demo_id,
                            "location": location,
                            "year": self.year,
                            "total_population": pop_value,
                            "breakdowns": []
                        })
                except (ValueError, AttributeError):
                    pass

    def extract_people(self, text: str, location: str) -> None:
        """Extract people and their positions from text"""
        # Look for titles and names
        title_patterns = [
            r"((?:Sir|Dr\.?|Major|Colonel|General|Rev\.?|The\s+Honourable|The\s+Right\s+Honourable)[^,]*),?\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*),?\s+([^,\n]*(?:Governor|Secretary|Director|Commissioner|Inspector|Officer|Judge|Chief).*?)(?:\s*\(|$|\n)",
            r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)(?:,\s+([A-Z]{1,}[a-z\.]*(?:\s+[A-Z]{1,}[a-z\.]*)*))?\s*(?:Governor|Acting Governor|Administrator|Secretary|Director|Commissioner)",
        ]

        seen_people = set()

        for pattern in title_patterns:
            matches = re.finditer(pattern, text, re.MULTILINE)
            for match in matches:
                try:
                    if len(match.groups()) >= 2:
                        title_part = match.group(1) if match.group(1) else ""
                        name_part = match.group(2) if len(match.groups()) > 1 else ""
                        position_part = match.group(3) if len(match.groups()) > 2 else ""

                        if name_part and name_part not in seen_people:
                            seen_people.add(name_part)
                            person_key = f"{name_part}_{location}"

                            if person_key not in self.person_mentions:
                                person_id = self.generate_id("person", name_part)

                                titles = []
                                honors = []
                                if title_part:
                                    if "Sir" in title_part:
                                        titles.append("Sir")
                                    if "Dr" in title_part:
                                        titles.append("Dr.")
                                    if "Rev" in title_part:
                                        titles.append("Rev.")

                                positions = []
                                if position_part:
                                    positions.append({
                                        "title": position_part.strip(),
                                        "location": location,
                                        "status": "permanent",
                                        "year": self.year
                                    })

                                person_entity = {
                                    "id": person_id,
                                    "name": name_part.strip(),
                                    "titles": titles if titles else [],
                                    "honors": honors,
                                    "positions": positions if positions else []
                                }

                                self.entities["people"].append(person_entity)
                                self.person_mentions[person_key] = person_id
                except (IndexError, AttributeError):
                    pass

    def extract_places(self, text: str, colony_name: str) -> None:
        """Extract geographic entities and place names"""
        # Add the colony itself
        colony_id = self.generate_id("place", colony_name)

        coords = self.extract_coordinates(text)

        # Extract area information
        area = None
        area_pattern = r"area[:\s]+([0-9,]+)\s*(square\s+miles|acres|square\s+kilometers?)"
        area_match = re.search(area_pattern, text, re.IGNORECASE)
        if area_match:
            try:
                area = {
                    "value": int(area_match.group(1).replace(",", "")),
                    "unit": area_match.group(2).lower()
                }
            except ValueError:
                pass

        place_entity = {
            "id": colony_id,
            "name": colony_name,
            "type": "colony",
            "year": self.year
        }

        if coords:
            place_entity["coordinates"] = coords
        if area:
            place_entity["area"] = area

        # Extract description from first paragraph
        first_para = text.split("\n\n")[0] if "\n\n" in text else text[:500]
        if first_para:
            place_entity["description"] = first_para[:200]

        self.entities["places"].append(place_entity)

        # Extract other geographic features mentioned
        geo_terms = ["river", "mountain", "harbor", "port", "island", "bay", "strait", "gulf"]
        for term in geo_terms:
            pattern = rf"(?:the\s+)?([A-Z][a-z\s]+?)\s+({term})"
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                geo_name = match.group(1).strip()
                if len(geo_name) > 2 and len(geo_name) < 50:
                    geo_id = self.generate_id("place", geo_name)
                    geo_entity = {
                        "id": geo_id,
                        "name": geo_name,
                        "type": term.lower(),
                        "parent_location": colony_id,
                        "year": self.year
                    }
                    # Check for duplicates
                    if geo_entity not in self.entities["places"]:
                        self.entities["places"].append(geo_entity)
                        # Add relationship
                        self.relationships.append({
                            "source_id": geo_id,
                            "relationship_type": "LOCATED_IN",
                            "target_id": colony_id,
                            "properties": {"year": self.year}
                        })

    def extract_institutions(self, text: str, location: str) -> None:
        """Extract governmental and institutional bodies"""
        institution_keywords = [
            ("Executive Council", "executive_council"),
            ("Legislative Council", "legislative_council"),
            ("Privy Council", "privy_council"),
            ("Supreme Court", "court"),
            ("Colonial Secretary", "department"),
            ("Treasury", "department"),
            ("Police Force", "police_force"),
            ("Education Department", "educational"),
            ("Medical Department", "medical"),
        ]

        for keyword, inst_type in institution_keywords:
            if keyword.lower() in text.lower():
                inst_id = self.generate_id("institution", f"{location}_{keyword}")

                # Extract composition info
                pattern = rf"{keyword}[^\.]*?(?:comprises|consisting of|members?)[^\.]*\.?"
                match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
                composition_text = match.group(0) if match else ""

                institution = {
                    "id": inst_id,
                    "name": keyword,
                    "type": inst_type,
                    "location": location,
                    "year": self.year
                }

                if composition_text:
                    institution["composition"] = {
                        "description": composition_text[:200],
                        "members": []
                    }

                self.entities["institutions"].append(institution)

    def extract_economic_data(self, text: str, location: str) -> None:
        """Extract economic and financial information"""
        # Revenue/expenditure patterns
        financial_pattern = r"(?:revenue|expenditure|income)\s*[:\s]+(?:£|\$)?([0-9,]+)"

        matches = re.finditer(financial_pattern, text, re.IGNORECASE)
        for match in matches:
            try:
                amount = int(match.group(1).replace(",", ""))
                econ_id = self.generate_id("economic", f"{location}_financial")

                # Determine type
                data_type = "revenue" if "revenue" in match.group(0).lower() else "expenditure"

                self.entities["economic_data"].append({
                    "id": econ_id,
                    "type": data_type,
                    "location": location,
                    "year": self.year,
                    "data": {
                        "value": amount,
                        "currency": "£"
                    }
                })
            except ValueError:
                pass

        # Extract trade and commodity information
        trade_keywords = ["exports", "imports", "trade", "commodity", "crops"]
        for keyword in trade_keywords:
            if keyword.lower() in text.lower():
                # Look for crop/commodity lists
                crop_pattern = rf"((?:{keyword}|crops?)\s*[:\s]*(?:.*?\n)*?\|.*?\|.*?\|)"
                matches = re.finditer(crop_pattern, text, re.IGNORECASE | re.DOTALL)

                for match in matches:
                    econ_id = self.generate_id("economic", f"{location}_{keyword}")
                    self.entities["economic_data"].append({
                        "id": econ_id,
                        "type": "production" if "crop" in keyword else "trade_export",
                        "location": location,
                        "year": self.year,
                        "data": {
                            "category": keyword,
                            "notes": match.group(1)[:150]
                        }
                    })

    def extract_infrastructure(self, text: str, location: str) -> None:
        """Extract infrastructure information"""
        infrastructure_types = [
            ("railway", "railway"),
            ("telegraph", "telegraph"),
            ("postal", "postal_route"),
            ("dock", "dock"),
            ("harbor", "harbor"),
            ("road", "road"),
            ("bridge", "bridge"),
        ]

        for keyword, infra_type in infrastructure_types:
            if keyword.lower() in text.lower():
                # Look for length/distance information
                length_pattern = rf"{keyword}[^\.]*?(\d+)\s*miles"
                match = re.search(length_pattern, text, re.IGNORECASE | re.DOTALL)

                if match:
                    try:
                        infra_id = self.generate_id("infrastructure", f"{location}_{keyword}")
                        length = int(match.group(1))

                        self.entities["infrastructure"].append({
                            "id": infra_id,
                            "type": infra_type,
                            "name": f"{keyword.title()} in {location}",
                            "location": location,
                            "year": self.year,
                            "specifications": {
                                "length": {
                                    "value": length,
                                    "unit": "miles"
                                }
                            }
                        })
                    except ValueError:
                        pass

    def extract_events(self, text: str, location: str) -> None:
        """Extract historical events and dates"""
        # Look for date patterns
        date_pattern = r"(\d{1,2}(?:st|nd|rd|th)?)\s+(?:January|February|March|April|May|June|July|August|September|October|November|December|[A-Z][a-z]{2})\s+(?:,\s+)?(\d{4})"

        matches = re.finditer(date_pattern, text)
        for match in matches:
            date_str = match.group(0)

            # Get context around the date
            start = max(0, match.start() - 100)
            end = min(len(text), match.end() + 100)
            context = text[start:end].replace("\n", " ")

            event_id = self.generate_id("event", f"{location}_{match.group(2)}")

            event_entity = {
                "id": event_id,
                "date": date_str,
                "description": context[:150],
                "locations": [location],
                "year_mentioned": self.year
            }

            # Determine event type
            if any(word in context.lower() for word in ["treaty", "cession", "agreement"]):
                event_entity["type"] = "treaty"
            elif any(word in context.lower() for word in ["established", "founded", "created"]):
                event_entity["type"] = "establishment"
            elif any(word in context.lower() for word in ["rebellion", "revolt", "uprising"]):
                event_entity["type"] = "rebellion"
            elif any(word in context.lower() for word in ["appointed", "elected"]):
                event_entity["type"] = "appointment"
            else:
                event_entity["type"] = "other"

            self.entities["events"].append(event_entity)

    def process_colony_file(self, filepath: str, colony_name: str) -> None:
        """Process a single colony file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract all entity types
            self.extract_places(content, colony_name)
            self.extract_people(content, colony_name)
            self.extract_institutions(content, colony_name)
            self.extract_economic_data(content, colony_name)
            self.extract_infrastructure(content, colony_name)
            self.extract_population_data(content, colony_name)
            self.extract_events(content, colony_name)

        except Exception as e:
            print(f"Error processing {filepath}: {e}")

    def process_all_colonies(self) -> None:
        """Process all colony files in the source directory"""
        source_path = Path(self.source_dir)
        colony_files = sorted(source_path.glob("*.md"))

        print(f"Processing {len(colony_files)} colonies...")

        for filepath in colony_files:
            colony_name = filepath.stem.replace("_", " ")
            print(f"  Processing: {colony_name}")
            self.process_colony_file(str(filepath), colony_name)

    def build_deduped_entities(self) -> Dict[str, Any]:
        """Deduplicate entities while preserving data"""
        deduped = {
            "places": [],
            "people": [],
            "institutions": [],
            "economic_data": [],
            "infrastructure": [],
            "demographics": [],
            "events": []
        }

        # Deduplicate places by name
        seen_places = set()
        for place in self.entities["places"]:
            key = (place["name"], place["type"])
            if key not in seen_places:
                deduped["places"].append(place)
                seen_places.add(key)

        # Deduplicate people by name
        seen_people = set()
        for person in self.entities["people"]:
            if person["name"] not in seen_people:
                deduped["people"].append(person)
                seen_people.add(person["name"])

        # Copy other entities (they have less duplication risk)
        deduped["institutions"] = self.entities["institutions"]
        deduped["economic_data"] = self.entities["economic_data"]
        deduped["infrastructure"] = self.entities["infrastructure"]
        deduped["demographics"] = self.entities["demographics"]
        deduped["events"] = self.entities["events"]

        return deduped

    def generate_output(self) -> Dict[str, Any]:
        """Generate the final JSON output"""
        deduped_entities = self.build_deduped_entities()

        output = {
            "metadata": {
                "year": self.year,
                "source_directory": self.source_dir,
                "extraction_date": datetime.now().isoformat(),
                "processing_notes": "Comprehensive extraction of geographic entities, people, institutions, economic data, infrastructure, demographics, and historical events from 37 colonies",
                "colonies_processed": sorted([f.stem.replace("_", " ") for f in Path(self.source_dir).glob("*.md")])
            },
            "entities": deduped_entities,
            "relationships": self.relationships
        }

        return output

    def save_output(self, output_path: str) -> None:
        """Save the extraction to JSON file"""
        output_data = self.generate_output()

        # Ensure output directory exists
        os.makedirs(os.path.dirname(output_path), exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        print(f"Extraction saved to: {output_path}")

    def generate_report(self) -> str:
        """Generate extraction report"""
        output = self.generate_output()
        entities = output["entities"]

        report = []
        report.append("=" * 70)
        report.append("COLONIAL OFFICE LIST 1948 - KNOWLEDGE GRAPH EXTRACTION REPORT")
        report.append("=" * 70)
        report.append("")
        report.append(f"Extraction Date: {output['metadata']['extraction_date']}")
        report.append(f"Year: {output['metadata']['year']}")
        report.append("")
        report.append("COLONIES PROCESSED:")
        report.append(f"  Total: {len(output['metadata']['colonies_processed'])}")
        for colony in sorted(output['metadata']['colonies_processed']):
            report.append(f"    - {colony}")
        report.append("")
        report.append("ENTITY EXTRACTION SUMMARY:")
        report.append(f"  Geographic Entities (Places):     {len(entities['places']):>6}")
        report.append(f"  People (with positions):           {len(entities['people']):>6}")
        report.append(f"  Institutions:                      {len(entities['institutions']):>6}")
        report.append(f"  Economic Data:                     {len(entities['economic_data']):>6}")
        report.append(f"  Infrastructure:                    {len(entities['infrastructure']):>6}")
        report.append(f"  Demographics:                      {len(entities['demographics']):>6}")
        report.append(f"  Historical Events:                 {len(entities['events']):>6}")
        report.append("")
        report.append(f"RELATIONSHIPS MAPPED: {len(output['relationships'])}")
        report.append("")
        report.append("=" * 70)

        return "\n".join(report)


def main():
    source_dir = "/home/user/colonial_office_list/output_2/1948_manual_parsed"
    output_path = "/home/user/colonial_office_list/knowledge_graph_extracts/1948_extracted.json"

    extractor = ColonialOfficeExtractor(source_dir, None)
    extractor.process_all_colonies()
    extractor.save_output(output_path)

    # Generate and print report
    report = extractor.generate_report()
    print("\n" + report)

    # Save report
    report_path = "/home/user/colonial_office_list/knowledge_graph_extracts/1948_extraction_report.txt"
    os.makedirs(os.path.dirname(report_path), exist_ok=True)
    with open(report_path, 'w') as f:
        f.write(report)
    print(f"Report saved to: {report_path}")


if __name__ == "__main__":
    main()
