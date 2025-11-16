#!/usr/bin/env python3
"""
Colonial Office List 1948 Knowledge Graph Extraction - Optimized Version
Extracts structured data from colony files following the EXTRACTION_METHODOLOGY.md
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Tuple, Any

class OptimizedColonialExtractor:
    def __init__(self, source_dir: str):
        self.source_dir = source_dir
        self.year = "1948"
        self.colonies_processed = []

        # Entity aggregation
        self.places = {}  # id -> entity
        self.people = {}  # id -> entity
        self.institutions = {}  # id -> entity
        self.economic_data = []
        self.infrastructure = []
        self.demographics = []
        self.events = []
        self.relationships = []

        self.id_counter = {}

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
            info["description"] = paras[0][:300]

        # Extract coordinates (simplified)
        coord_pattern = r"(\d+°[^,\n]*?[NSns])[^,]*?(\d+°[^,\n]*?[EWew])"
        match = re.search(coord_pattern, text)
        if match:
            info["coordinates"] = {
                "latitude": match.group(1),
                "longitude": match.group(2)
            }

        # Extract area
        area_pattern = r"area[^:]*?:\s*([0-9,]+)\s*(square\s+miles|acres)"
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

    def extract_population(self, text: str, colony_name: str) -> None:
        """Extract population data"""
        # Look for POPULATION section
        pop_section_match = re.search(r"POPULATION.*?(?=\n[A-Z]|\Z)", text, re.IGNORECASE | re.DOTALL)
        if not pop_section_match:
            return

        pop_text = pop_section_match.group(0)

        # Extract numbers from tables or text
        numbers = re.findall(r"\d{1,3}(?:,\d{3})*", pop_text)
        if numbers:
            try:
                total = int(numbers[0].replace(",", ""))
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

    def extract_people_simple(self, text: str, colony_name: str) -> None:
        """Extract people more efficiently"""
        # Look for ADMINISTRATION or PERSONNEL sections
        admin_match = re.search(r"ADMINISTRATION.*?(?=\n[A-Z{2,}]|\Z)", text, re.IGNORECASE | re.DOTALL)
        if not admin_match:
            admin_match = re.search(r"GOVERNMENT.*?(?=\n[A-Z{2,}]|\Z)", text, re.IGNORECASE | re.DOTALL)

        if not admin_match:
            return

        admin_text = admin_match.group(0)

        # Find names with titles/positions
        # Look for patterns like "Sir John Smith, Governor" or "Dr. Jane Doe, Colonial Secretary"
        person_pattern = r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*,\s*([A-Z][a-z\s]+(?:Governor|Secretary|Director|Commissioner|Judge|Chief|Officer))"

        seen = set()
        for match in re.finditer(person_pattern, admin_text):
            name = match.group(1).strip()
            position = match.group(2).strip()

            if name not in seen and len(name) > 2:
                seen.add(name)
                person_id = self.get_unique_id("person")

                if person_id not in self.people:
                    self.people[person_id] = {
                        "id": person_id,
                        "name": name,
                        "titles": [],
                        "honors": [],
                        "positions": [{
                            "title": position,
                            "location": colony_name,
                            "status": "permanent",
                            "year": self.year
                        }]
                    }

    def extract_institutions_simple(self, text: str, colony_name: str) -> None:
        """Extract institutions"""
        institutions_to_find = [
            ("Executive Council", "executive_council"),
            ("Legislative Council", "legislative_council"),
            ("Privy Council", "privy_council"),
            ("Supreme Court", "court"),
            ("Colonial Secretary", "department"),
            ("Education Department", "educational"),
            ("Medical Department", "medical"),
        ]

        for inst_name, inst_type in institutions_to_find:
            if inst_name.lower() in text.lower():
                inst_id = self.get_unique_id("inst")

                if inst_id not in self.institutions:
                    self.institutions[inst_id] = {
                        "id": inst_id,
                        "name": inst_name,
                        "type": inst_type,
                        "location": colony_name,
                        "year": self.year
                    }

    def extract_economic_simple(self, text: str, colony_name: str) -> None:
        """Extract economic data"""
        # Look for revenue, exports, crops, etc.

        # Revenue/expenditure
        rev_pattern = r"(?:revenue|expenditure)\s*[:\s]+[£$]?\s*([0-9,]+)"
        for match in re.finditer(rev_pattern, text, re.IGNORECASE):
            try:
                amount = int(match.group(1).replace(",", ""))
                self.economic_data.append({
                    "id": self.get_unique_id("econ"),
                    "type": "revenue" if "revenue" in match.group(0).lower() else "expenditure",
                    "location": colony_name,
                    "year": self.year,
                    "data": {
                        "value": amount,
                        "currency": "£"
                    }
                })
            except:
                pass

        # Crops and commodities
        if "crop" in text.lower() or "export" in text.lower():
            crop_match = re.search(r"(?:crop|principal.*?production).*?(?:\n[A-Z]|\Z)", text, re.IGNORECASE | re.DOTALL)
            if crop_match and ("|" in crop_match.group(0) or "acre" in crop_match.group(0).lower()):
                self.economic_data.append({
                    "id": self.get_unique_id("econ"),
                    "type": "production",
                    "location": colony_name,
                    "year": self.year,
                    "data": {
                        "category": "crops",
                        "notes": crop_match.group(0)[:150]
                    }
                })

    def extract_events_simple(self, text: str, colony_name: str) -> None:
        """Extract historical events"""
        # Look for dates and events
        date_pattern = r"(\d{1,2}(?:st|nd|rd|th)?)\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+(?:,\s+)?(\d{4})"

        for match in re.finditer(date_pattern, text):
            date_str = match.group(0)
            year = match.group(2)

            # Get context
            start = max(0, match.start() - 80)
            end = min(len(text), match.end() + 80)
            context = text[start:end].replace("\n", " ")

            self.events.append({
                "id": self.get_unique_id("event"),
                "date": date_str,
                "description": context[:120],
                "locations": [colony_name],
                "year_mentioned": self.year,
                "type": "other"
            })

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
            self.places[place_id] = {
                "id": place_id,
                "name": basic_info["name"],
                "type": "colony",
                "year": self.year,
                **{k: v for k, v in basic_info.items() if k != "name"}
            }

            # Extract other entities
            self.extract_population(text, colony_name)
            self.extract_people_simple(text, colony_name)
            self.extract_institutions_simple(text, colony_name)
            self.extract_economic_simple(text, colony_name)
            self.extract_events_simple(text, colony_name)

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
                "processing_notes": "Extraction of colonial administrative data from 37 territories",
                "colonies_processed": sorted(self.colonies_processed)
            },
            "entities": {
                "places": list(self.places.values()),
                "people": list(self.people.values()),
                "institutions": list(self.institutions.values()),
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
            f"TOTAL ENTITY COUNT: {sum(len(v) for k, v in entities.items())}",
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

    extractor = OptimizedColonialExtractor(source_dir)
    extractor.process_all()
    extractor.save_and_report(output_path)


if __name__ == "__main__":
    main()
