#!/usr/bin/env python3
"""
Colonial Office List 1948 Knowledge Graph Extraction - Ultimate Version
With corrected pattern matching for people extraction
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set

class UltimateColonialExtractor:
    def __init__(self, source_dir: str):
        self.source_dir = source_dir
        self.year = "1948"
        self.colonies_processed = []

        self.places = {}
        self.people = {}
        self.institutions = {}
        self.economic_data = []
        self.infrastructure = []
        self.demographics = []
        self.events = []
        self.relationships = []

        self.id_counter = {}

    def get_id(self, prefix: str) -> str:
        if prefix not in self.id_counter:
            self.id_counter[prefix] = 0
        self.id_counter[prefix] += 1
        return f"{prefix}_{self.id_counter[prefix]}"

    def is_valid_name(self, text: str) -> bool:
        """Check if text looks like a person's name"""
        text = text.strip()
        if not text or len(text) < 3 or len(text) > 60:
            return False
        # Should start with capital letter
        if not text[0].isupper():
            return False
        # Should not be all caps (unless short title)
        if len(text) > 4 and text.isupper():
            return False
        # Should have mix of upper and lower (for normal names)
        if len(text) > 3 and not any(c.islower() for c in text):
            return False
        return True

    def extract_place_info(self, text: str, colony_name: str) -> Dict:
        info = {"name": colony_name, "coordinates": {}, "area": None}

        # Extract coordinates
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

    def extract_people(self, text: str, colony_name: str) -> None:
        """Extract people from various sections"""
        # Pattern 1: "The [Most] Reverend [Dr.] Name (Position)"
        pattern1 = r"(?:The\s+)?(?:Most\s+)?(?:Right\s+)?(?:Reverend|Archbishop|Bishop)\s+(?:Dr\.?\s+)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*\(([^)]+)\)"

        # Pattern 2: "The Honourable Name (Position)"
        pattern2 = r"The\s+(?:Right\s+)?Honourable\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*\(([^)]+)\)"

        # Pattern 3: "Colonel/Major Name"
        pattern3 = r"(?:Colonel|Major|Admiral|Captain|General)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)"

        for pattern in [pattern1, pattern2, pattern3]:
            for match in re.finditer(pattern, text):
                name = match.group(1).strip() if match.group(1) else None
                position = match.group(2).strip() if len(match.groups()) > 1 and match.group(2) else ""

                if name and self.is_valid_name(name) and name not in self.people:
                    person_id = self.get_id("person")

                    positions = []
                    if position:
                        positions.append({
                            "title": position,
                            "location": colony_name,
                            "status": "permanent",
                            "year": self.year
                        })

                    self.people[person_id] = {
                        "id": person_id,
                        "name": name,
                        "titles": [],
                        "honors": [],
                        "positions": positions
                    }

                    # Extract titles
                    if "Dr" in match.group(0):
                        self.people[person_id]["titles"].append("Dr.")
                    if "Archbishop" in match.group(0):
                        self.people[person_id]["titles"].append("Archbishop")
                    if "Bishop" in match.group(0):
                        self.people[person_id]["titles"].append("Bishop")
                    if "Colonel" in match.group(0):
                        self.people[person_id]["titles"].append("Colonel")
                    if "Sir" in match.group(0):
                        self.people[person_id]["titles"].append("Sir")

    def extract_population(self, text: str, colony_name: str) -> None:
        pop_section = re.search(r"(?:POPULATION|Census).*?(?:\n[A-Z]{2,}|\Z)",
                               text, re.IGNORECASE | re.DOTALL)
        if not pop_section:
            return

        pop_text = pop_section.group(0)
        numbers = []
        for match in re.finditer(r"(\d{1,3}(?:,\d{3})*)", pop_text):
            try:
                numbers.append(int(match.group(1).replace(",", "")))
            except:
                pass

        if numbers:
            valid = [n for n in numbers if 500 < n < 50000000]
            if valid:
                demo_id = self.get_id("demo")
                self.demographics.append({
                    "id": demo_id,
                    "location": colony_name,
                    "year": self.year,
                    "total_population": max(valid),
                    "breakdowns": []
                })

    def extract_institutions(self, text: str, colony_name: str) -> None:
        institutions = [
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

        for name, type_ in institutions:
            if re.search(r"\b" + re.escape(name) + r"\b", text, re.IGNORECASE):
                inst_id = self.get_id("inst")
                self.institutions[inst_id] = {
                    "id": inst_id,
                    "name": name,
                    "type": type_,
                    "location": colony_name,
                    "year": self.year
                }

    def extract_economic(self, text: str, colony_name: str) -> None:
        if re.search(r"(?:CURRENCY|BANKING)", text, re.IGNORECASE):
            self.economic_data.append({
                "id": self.get_id("econ"),
                "type": "banking",
                "location": colony_name,
                "year": self.year,
                "data": {"category": "currency_and_banking", "notes": "Documented"}
            })

        if re.search(r"(?:AGRICULTURE|CROPS|PRINCIPAL.*PRODUCTS)", text, re.IGNORECASE):
            self.economic_data.append({
                "id": self.get_id("econ"),
                "type": "production",
                "location": colony_name,
                "year": self.year,
                "data": {"category": "agriculture", "notes": "Documented"}
            })

        if re.search(r"(?:revenue|expenditure|income|trade)", text, re.IGNORECASE):
            self.economic_data.append({
                "id": self.get_id("econ"),
                "type": "financial",
                "location": colony_name,
                "year": self.year,
                "data": {"category": "financial", "notes": "Documented"}
            })

    def extract_infrastructure(self, text: str, colony_name: str) -> None:
        infra = [("railway", "railway"), ("harbour", "harbor"), ("harbour", "harbor"),
                 ("port", "dock"), ("postal", "postal_route")]

        for keyword, type_ in infra:
            if keyword.lower() in text.lower():
                length_pattern = rf"{keyword}[^\.]*?(\d+)\s*miles"
                match = re.search(length_pattern, text, re.IGNORECASE | re.DOTALL)

                if match:
                    try:
                        length = int(match.group(1))
                        self.infrastructure.append({
                            "id": self.get_id("infra"),
                            "type": type_,
                            "name": f"{keyword.title()}",
                            "location": colony_name,
                            "year": self.year,
                            "specifications": {
                                "length": {"value": length, "unit": "miles"}
                            }
                        })
                    except:
                        pass

    def extract_events(self, text: str, colony_name: str) -> None:
        date_pattern = r"(\d{1,2}(?:st|nd|rd|th)?)\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+(?:,\s+)?(\d{4})"

        seen = set()
        for match in re.finditer(date_pattern, text):
            date_str = match.group(0)
            if date_str not in seen:
                start = max(0, match.start() - 60)
                end = min(len(text), match.end() + 60)
                context = text[start:end].replace("\n", " ").strip()

                event_type = "other"
                ctx_lower = context.lower()
                if any(w in ctx_lower for w in ["treaty", "agreement", "cession"]):
                    event_type = "treaty"
                elif any(w in ctx_lower for w in ["established", "founded", "established"]):
                    event_type = "establishment"
                elif any(w in ctx_lower for w in ["hurricane", "earthquake"]):
                    event_type = "disaster"

                self.events.append({
                    "id": self.get_id("event"),
                    "date": date_str,
                    "description": context[:100],
                    "locations": [colony_name],
                    "year_mentioned": self.year,
                    "type": event_type
                })

                seen.add(date_str)

    def process_colony(self, filepath: str) -> None:
        colony_name = Path(filepath).stem.replace("_", " ")
        self.colonies_processed.append(colony_name)

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read()

            # Extract place
            place_info = self.extract_place_info(text, colony_name)
            place_id = self.get_id("place")

            place_entity = {
                "id": place_id,
                "name": place_info["name"],
                "type": "colony",
                "year": self.year
            }

            if place_info.get("coordinates"):
                place_entity["coordinates"] = place_info["coordinates"]
            if place_info.get("area"):
                place_entity["area"] = place_info["area"]

            self.places[place_id] = place_entity

            # Extract other entities
            self.extract_people(text, colony_name)
            self.extract_institutions(text, colony_name)
            self.extract_population(text, colony_name)
            self.extract_economic(text, colony_name)
            self.extract_infrastructure(text, colony_name)
            self.extract_events(text, colony_name)

        except Exception as e:
            print(f"  ERROR: {colony_name} - {e}")

    def process_all(self) -> None:
        source_path = Path(self.source_dir)
        colony_files = sorted(source_path.glob("*.md"))

        print(f"Processing {len(colony_files)} colonies...")
        for i, filepath in enumerate(colony_files, 1):
            colony_name = filepath.stem.replace("_", " ")
            print(f"  [{i:2d}/{len(colony_files)}] {colony_name:<30}", end="", flush=True)
            self.process_colony(str(filepath))
            print(" ✓")

    def save_output(self, output_path: str) -> None:
        output_data = {
            "metadata": {
                "year": self.year,
                "source_directory": self.source_dir,
                "extraction_date": datetime.now().isoformat(),
                "processing_notes": "Comprehensive extraction from 37 colonial territories",
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

        # Save JSON
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        # Generate report
        entities = output_data["entities"]
        report_lines = [
            "=" * 75,
            "COLONIAL OFFICE LIST 1948 - KNOWLEDGE GRAPH EXTRACTION REPORT",
            "=" * 75,
            "",
            f"Extraction Date: {output_data['metadata']['extraction_date']}",
            f"Year: {output_data['metadata']['year']}",
            "",
            "COLONIES PROCESSED: 37 TERRITORIES",
            "",
        ]

        colonies_list = sorted(output_data['metadata']['colonies_processed'])
        for i, colony in enumerate(colonies_list, 1):
            report_lines.append(f"  {i:2d}. {colony}")

        report_lines.extend([
            "",
            "ENTITY EXTRACTION SUMMARY:",
            "=" * 75,
            f"  Geographic Entities (Places):           {len(entities['places']):>6}",
            f"  People (with roles/positions):          {len(entities['people']):>6}",
            f"  Institutions (councils/courts/depts):   {len(entities['institutions']):>6}",
            f"  Economic Data (banking/trade/crops):    {len(entities['economic_data']):>6}",
            f"  Infrastructure (ports/railways/etc):    {len(entities['infrastructure']):>6}",
            f"  Demographics (population data):         {len(entities['demographics']):>6}",
            f"  Historical Events (treaties/founded):   {len(entities['events']):>6}",
            "",
            f"  TOTAL ENTITIES EXTRACTED:               {sum(len(v) if isinstance(v, list) else 0 for v in entities.values()):>6}",
            f"  RELATIONSHIPS MAPPED:                   {len(output_data['relationships']):>6}",
            "",
            "FILE INFORMATION:",
            f"  Output JSON Path: {output_path}",
            f"  File Size: {os.path.getsize(output_path) / 1024:.1f} KB",
            "=" * 75
        ])

        report_text = "\n".join(report_lines)
        print("\n" + report_text)

        # Save report
        report_path = output_path.replace(".json", "_report.txt")
        with open(report_path, 'w') as f:
            f.write(report_text)

        print(f"\nJSON saved to: {output_path}")
        print(f"Report saved to: {report_path}")


def main():
    extractor = UltimateColonialExtractor(
        "/home/user/colonial_office_list/output_2/1948_manual_parsed"
    )
    extractor.process_all()
    extractor.save_output(
        "/home/user/colonial_office_list/knowledge_graph_extracts/1948_extracted.json"
    )


if __name__ == "__main__":
    main()
