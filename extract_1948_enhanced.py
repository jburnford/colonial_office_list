#!/usr/bin/env python3
"""
Colonial Office List 1948 Knowledge Graph Extraction - Enhanced Version
Improved extraction of people, institutions, and relationships
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Any

class EnhancedColonialExtractor:
    def __init__(self, source_dir: str):
        self.source_dir = source_dir
        self.year = "1948"
        self.colonies_processed = []

        # Entity aggregation with deduplication
        self.places_by_id = {}
        self.places_by_name = {}
        self.people_by_id = {}
        self.people_by_name = {}
        self.institutions_by_id = {}
        self.economic_data = []
        self.infrastructure = []
        self.demographics = []
        self.events = []
        self.relationships = []

        self.id_counter = {}
        self.place_counter = {}

    def get_unique_id(self, prefix: str) -> str:
        """Generate unique IDs"""
        if prefix not in self.id_counter:
            self.id_counter[prefix] = 0
        self.id_counter[prefix] += 1
        return f"{prefix}_{self.id_counter[prefix]}"

    def extract_basic_info(self, text: str, colony_name: str) -> Dict[str, Any]:
        """Extract basic colony information"""
        info = {
            "name": colony_name,
            "coordinates": {},
            "area": None,
            "description": ""
        }

        # Extract first paragraph as description
        paras = text.split('\n\n')
        if paras:
            desc = paras[0][:300]
            if len(desc) > 20:
                info["description"] = desc

        # Extract coordinates (improved)
        coord_pattern = r"(\d+°\s*\d+[\'′]?\s*[NSns])[^,]*?(\d+°\s*\d+[\'′]?\s*[EWew])"
        match = re.search(coord_pattern, text)
        if match:
            info["coordinates"] = {
                "latitude": match.group(1).strip(),
                "longitude": match.group(2).strip()
            }

        # Extract area
        area_pattern = r"area[^:]*?[:\s]+([0-9,]+)\s*(square\s+miles|acres|square\s+kilometers?)"
        match = re.search(area_pattern, text, re.IGNORECASE)
        if match:
            try:
                info["area"] = {
                    "value": int(match.group(1).replace(",", "")),
                    "unit": match.group(2).lower()
                }
            except:
                pass

        return info

    def register_place(self, name: str, colony_name: str, place_type: str = "feature") -> str:
        """Register a place with deduplication"""
        key = f"{name}_{colony_name}_{place_type}"
        if key in self.places_by_name:
            return self.places_by_name[key]

        place_id = self.get_unique_id("place")
        place_entity = {
            "id": place_id,
            "name": name,
            "type": place_type,
            "parent_location": colony_name,
            "year": self.year
        }
        self.places_by_id[place_id] = place_entity
        self.places_by_name[key] = place_id
        return place_id

    def extract_population(self, text: str, colony_name: str) -> None:
        """Extract population data"""
        # Look for POPULATION section
        pop_section_match = re.search(r"POPULATION.*?(?=\n[A-Z{2,}]|\Z)", text, re.IGNORECASE | re.DOTALL)
        if not pop_section_match:
            return

        pop_text = pop_section_match.group(0)

        # Look for numbers in the section
        numbers = re.findall(r"\d{1,3}(?:,\d{3})*", pop_text)
        if numbers:
            try:
                # Usually the first number or largest number is total
                candidates = [int(n.replace(",", "")) for n in numbers[:10]]
                total = max(candidates) if candidates else None

                if total and total > 1000:  # Reasonable population threshold
                    demo_id = self.get_unique_id("demo")
                    self.demographics.append({
                        "id": demo_id,
                        "location": colony_name,
                        "year": self.year,
                        "total_population": total,
                        "breakdowns": []
                    })
            except:
                pass

    def extract_people_enhanced(self, text: str, colony_name: str) -> None:
        """Extract people more comprehensively"""
        people_patterns = [
            # Pattern: "Title Name (Position)"
            r"((?:The\s+(?:Most\s+)?(?:Reverend|Right\s+Reverend|Honourable|Right\s+Honourable))?(?:\s+)?(?:Sir|Dr\.?)?[^(]*?)\s*\(([^)]+)\)",
            # Pattern: "Title Name, Position" (in lists)
            r"((?:The\s+.*?)?[A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})\s*(?:–|—|:)\s*([A-Z][a-z\s]+(?:Governor|Secretary|Director|Commissioner|Judge|Chief|Officer|President|Bishop|Archbishop|Chairman|Moderator|President))",
            # Pattern: Government officers listed with positions
            r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*(?:,\s*([A-Z][a-z\s]+))*\s+(?:Governor|Administrator|Colonial Secretary|Chief Justice|Chief Commissioner|Acting)",
        ]

        seen_people = set()

        for pattern in people_patterns:
            matches = re.finditer(pattern, text, re.MULTILINE)
            for match in matches:
                try:
                    groups = match.groups()
                    if len(groups) >= 1:
                        name_part = groups[0].strip() if groups[0] else ""
                        position_part = groups[1].strip() if len(groups) > 1 and groups[1] else ""

                        # Clean up name
                        name = re.sub(r"^(The\s+)?(?:Most\s+)?(?:Right\s+)?(?:Reverend|Honourable)\s+", "", name_part).strip()

                        # Filter short or invalid names
                        if len(name) > 3 and len(name) < 80 and name not in seen_people:
                            if name not in self.people_by_name:
                                person_id = self.get_unique_id("person")

                                positions = []
                                if position_part:
                                    positions.append({
                                        "title": position_part,
                                        "location": colony_name,
                                        "status": "permanent",
                                        "year": self.year
                                    })

                                person_entity = {
                                    "id": person_id,
                                    "name": name,
                                    "titles": [],
                                    "honors": [],
                                    "positions": positions
                                }

                                # Extract titles and honors
                                if "Sir" in name_part:
                                    person_entity["titles"].append("Sir")
                                if "Dr" in name_part:
                                    person_entity["titles"].append("Dr.")
                                if "Reverend" in name_part:
                                    person_entity["titles"].append("Rev.")
                                if "Archbishop" in position_part:
                                    person_entity["titles"].append("Archbishop")
                                if "Bishop" in position_part:
                                    person_entity["titles"].append("Bishop")

                                self.people_by_id[person_id] = person_entity
                                self.people_by_name[name] = person_id
                                seen_people.add(name)
                except (IndexError, AttributeError):
                    pass

    def extract_institutions_enhanced(self, text: str, colony_name: str) -> None:
        """Extract institutions comprehensively"""
        institution_patterns = [
            ("Executive Council", "executive_council"),
            ("Legislative Council", "legislative_council"),
            ("Privy Council", "privy_council"),
            ("Supreme Court", "court"),
            ("Colonial Secretary", "department"),
            ("Treasury", "department"),
            ("Police Force", "police_force"),
            ("Education Department", "educational"),
            ("Medical Department", "medical"),
            ("Public Works Department", "public_works"),
            ("Harbour Authority", "infrastructure"),
            ("Port Authority", "infrastructure"),
            ("Water Commission", "public_works"),
            ("Board of Supervision", "administrative"),
            ("Agricultural Loan Societies Board", "administrative"),
        ]

        for keyword, inst_type in institution_patterns:
            if keyword.lower() in text.lower():
                inst_id = self.get_unique_id("inst")

                # Try to extract composition info
                pattern = rf"{keyword}[^\.]*?(?:comprises|consisting of|members?|established)[^\.]*\."
                match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
                composition_text = match.group(0)[:150] if match else ""

                institution = {
                    "id": inst_id,
                    "name": keyword,
                    "type": inst_type,
                    "location": colony_name,
                    "year": self.year
                }

                if composition_text:
                    institution["composition"] = {
                        "description": composition_text,
                        "member_count": None,
                        "members": []
                    }

                self.institutions_by_id[inst_id] = institution

    def extract_economic_comprehensive(self, text: str, colony_name: str) -> None:
        """Extract economic data comprehensively"""
        # Revenue and expenditure
        rev_exp_pattern = r"(?:revenue|expenditure|income|expenditure)\s*[:\s]+[£$]?\s*([0-9,]+)"
        matches = re.finditer(rev_exp_pattern, text, re.IGNORECASE)
        for match in matches:
            try:
                amount = int(match.group(1).replace(",", ""))
                data_type = "revenue" if "revenue" in match.group(0).lower() else "expenditure"

                self.economic_data.append({
                    "id": self.get_unique_id("econ"),
                    "type": data_type,
                    "location": colony_name,
                    "year": self.year,
                    "data": {
                        "value": amount,
                        "currency": "£"
                    }
                })
            except:
                pass

        # Crops and commodities - look for crop/production data
        crop_section = re.search(r"(?:crop|principal.*?production|agriculture|exports?).*?(?:\n[A-Z{2,}]|\Z)", text, re.IGNORECASE | re.DOTALL)
        if crop_section and "|" in crop_section.group(0):
            self.economic_data.append({
                "id": self.get_unique_id("econ"),
                "type": "production",
                "location": colony_name,
                "year": self.year,
                "data": {
                    "category": "crops",
                    "notes": crop_section.group(0)[:150]
                }
            })

        # Banking and currency
        if "bank" in text.lower() or "currency" in text.lower():
            self.economic_data.append({
                "id": self.get_unique_id("econ"),
                "type": "banking",
                "location": colony_name,
                "year": self.year,
                "data": {
                    "category": "banking_and_currency",
                    "notes": "Banking and currency information extracted"
                }
            })

    def extract_infrastructure_simple(self, text: str, colony_name: str) -> None:
        """Extract infrastructure"""
        infra_keywords = [
            ("railway", "railway"),
            ("telegraph", "telegraph"),
            ("postal", "postal_route"),
            ("dock", "dock"),
            ("harbor", "harbor"),
            ("harbour", "harbor"),
            ("road", "road"),
            ("bridge", "bridge"),
            ("airport", "public_building"),
            ("aerodrome", "public_building"),
        ]

        for keyword, infra_type in infra_keywords:
            if keyword.lower() in text.lower():
                # Look for length information
                length_pattern = rf"{keyword}[^\.]*?(\d+)\s*miles"
                match = re.search(length_pattern, text, re.IGNORECASE | re.DOTALL)

                if match:
                    try:
                        length = int(match.group(1))
                        self.infrastructure.append({
                            "id": self.get_unique_id("infra"),
                            "type": infra_type,
                            "name": f"{keyword.title()} in {colony_name}",
                            "location": colony_name,
                            "year": self.year,
                            "specifications": {
                                "length": {
                                    "value": length,
                                    "unit": "miles"
                                }
                            }
                        })
                    except:
                        pass

    def extract_events_comprehensive(self, text: str, colony_name: str) -> None:
        """Extract historical events"""
        date_pattern = r"(\d{1,2}(?:st|nd|rd|th)?)\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+(?:,\s+)?(\d{4})"

        seen_dates = set()
        for match in re.finditer(date_pattern, text):
            date_str = match.group(0)
            year = match.group(2)

            if date_str not in seen_dates:
                # Get context
                start = max(0, match.start() - 80)
                end = min(len(text), match.end() + 80)
                context = text[start:end].replace("\n", " ")

                event_type = "other"
                if any(word in context.lower() for word in ["treaty", "cession", "agreement"]):
                    event_type = "treaty"
                elif any(word in context.lower() for word in ["establish", "found", "created"]):
                    event_type = "establishment"
                elif any(word in context.lower() for word in ["rebel", "revolt", "uprising"]):
                    event_type = "rebellion"
                elif any(word in context.lower() for word in ["appointed", "elected", "transfer"]):
                    event_type = "appointment"
                elif any(word in context.lower() for word in ["hurricane", "earthquake", "disaster"]):
                    event_type = "disaster"

                self.events.append({
                    "id": self.get_unique_id("event"),
                    "date": date_str,
                    "description": context[:120],
                    "locations": [colony_name],
                    "year_mentioned": self.year,
                    "type": event_type
                })

                seen_dates.add(date_str)

    def process_colony(self, filepath: str) -> None:
        """Process a single colony file"""
        colony_name = Path(filepath).stem.replace("_", " ")
        self.colonies_processed.append(colony_name)

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read()

            # Extract basic info
            basic_info = self.extract_basic_info(text, colony_name)
            place_id = self.get_unique_id("place")
            place_entity = {
                "id": place_id,
                "name": basic_info["name"],
                "type": "colony",
                "year": self.year
            }
            if basic_info.get("coordinates"):
                place_entity["coordinates"] = basic_info["coordinates"]
            if basic_info.get("area"):
                place_entity["area"] = basic_info["area"]
            if basic_info.get("description"):
                place_entity["description"] = basic_info["description"]

            self.places_by_id[place_id] = place_entity
            self.places_by_name[colony_name] = place_id

            # Extract other entities
            self.extract_population(text, colony_name)
            self.extract_people_enhanced(text, colony_name)
            self.extract_institutions_enhanced(text, colony_name)
            self.extract_economic_comprehensive(text, colony_name)
            self.extract_infrastructure_simple(text, colony_name)
            self.extract_events_comprehensive(text, colony_name)

        except Exception as e:
            print(f"Error processing {colony_name}: {e}")

    def process_all(self) -> None:
        """Process all colony files"""
        source_path = Path(self.source_dir)
        colony_files = sorted(source_path.glob("*.md"))

        print(f"Processing {len(colony_files)} colonies...")
        for i, filepath in enumerate(colony_files, 1):
            colony_name = filepath.stem.replace("_", " ")
            print(f"  [{i}/{len(colony_files)}] {colony_name}")
            self.process_colony(str(filepath))

    def generate_output(self) -> Dict[str, Any]:
        """Generate final JSON output"""
        return {
            "metadata": {
                "year": self.year,
                "source_directory": self.source_dir,
                "extraction_date": datetime.now().isoformat(),
                "processing_notes": "Comprehensive extraction of geographic entities, people, institutions, economic data, infrastructure, demographics, and historical events from 37 colonies",
                "colonies_processed": sorted(self.colonies_processed)
            },
            "entities": {
                "places": list(self.places_by_id.values()),
                "people": list(self.people_by_id.values()),
                "institutions": list(self.institutions_by_id.values()),
                "economic_data": self.economic_data,
                "infrastructure": self.infrastructure,
                "demographics": self.demographics,
                "events": self.events
            },
            "relationships": self.relationships
        }

    def save_and_report(self, output_path: str) -> None:
        """Save output and generate report"""
        output_data = self.generate_output()
        entities = output_data["entities"]

        # Save JSON
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        # Generate report
        report_lines = [
            "=" * 70,
            "COLONIAL OFFICE LIST 1948 - KNOWLEDGE GRAPH EXTRACTION REPORT",
            "=" * 70,
            "",
            f"Extraction Date: {output_data['metadata']['extraction_date']}",
            f"Year: {output_data['metadata']['year']}",
            "",
            "COLONIES PROCESSED:",
            f"  Total Count: {len(output_data['metadata']['colonies_processed'])}",
            ""
        ]

        for colony in sorted(output_data['metadata']['colonies_processed']):
            report_lines.append(f"  - {colony}")

        report_lines.extend([
            "",
            "ENTITY EXTRACTION SUMMARY:",
            f"  Geographic Entities (Places):     {len(entities['places']):>6}",
            f"  People (with positions):           {len(entities['people']):>6}",
            f"  Institutions:                      {len(entities['institutions']):>6}",
            f"  Economic Data:                     {len(entities['economic_data']):>6}",
            f"  Infrastructure:                    {len(entities['infrastructure']):>6}",
            f"  Demographics:                      {len(entities['demographics']):>6}",
            f"  Historical Events:                 {len(entities['events']):>6}",
            "",
            f"TOTAL ENTITY COUNT: {sum(len(v) if isinstance(v, list) else 0 for v in entities.values())}",
            f"RELATIONSHIPS MAPPED: {len(output_data['relationships'])}",
            "",
            "=" * 70
        ])

        report_text = "\n".join(report_lines)
        print("\n" + report_text)

        # Save report
        report_path = output_path.replace(".json", "_report.txt")
        with open(report_path, 'w') as f:
            f.write(report_text)

        print(f"\nOutput saved to: {output_path}")
        print(f"Report saved to: {report_path}")


def main():
    source_dir = "/home/user/colonial_office_list/output_2/1948_manual_parsed"
    output_path = "/home/user/colonial_office_list/knowledge_graph_extracts/1948_extracted.json"

    extractor = EnhancedColonialExtractor(source_dir)
    extractor.process_all()
    extractor.save_and_report(output_path)


if __name__ == "__main__":
    main()
