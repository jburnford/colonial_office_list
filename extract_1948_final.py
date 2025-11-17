#!/usr/bin/env python3
"""
Colonial Office List 1948 Knowledge Graph Extraction - Final Refined Version
Focuses on high-quality data extraction with strict validation
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Set, Any, Optional

class RefinedColonialExtractor:
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
        self.valid_titles = {"Sir", "Dr.", "Dr", "Rev.", "Rev", "Major", "Colonel", "General",
                            "Admiral", "Captain", "The Right Honourable", "The Honourable"}

    def get_unique_id(self, prefix: str) -> str:
        if prefix not in self.id_counter:
            self.id_counter[prefix] = 0
        self.id_counter[prefix] += 1
        return f"{prefix}_{self.id_counter[prefix]}"

    def is_valid_name(self, name: str) -> bool:
        """Validate if string is likely a person's name"""
        # Must have length between 4-60 characters
        if not (4 <= len(name) <= 60):
            return False
        # Should have proper capitalization
        if not name[0].isupper():
            return False
        # Should not be all caps (likely section header)
        if name.isupper():
            return False
        # Should have at least one lowercase letter
        if not any(c.islower() for c in name):
            return False
        # Should not contain excessive punctuation or special chars
        if name.count(',') > 1 or name.count(';') > 0:
            return False
        return True

    def extract_place_info(self, text: str, colony_name: str) -> Dict[str, Any]:
        """Extract geographic information"""
        info = {
            "name": colony_name,
            "coordinates": {},
            "area": None
        }

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

    def extract_people_strict(self, text: str, colony_name: str) -> None:
        """Extract people with strict validation"""
        # Look for RELIGION section with clergy names
        religion_section = re.search(r"(?:RELIGION|RELIGIOUS|CLERGY).*?(?=\n[A-Z{2,}]|\Z)",
                                    text, re.IGNORECASE | re.DOTALL)

        if religion_section:
            # Pattern: "Title Name (Position)"
            pattern = r"((?:The\s+)?(?:Most\s+)?(?:Right\s+)?(?:Reverend|Archbishop|Bishop|Rabbi))\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*(?:\(([^)]+)\)|—|–)"

            for match in re.finditer(pattern, religion_section.group(0)):
                title = match.group(1).strip()
                name = match.group(2).strip()
                position = match.group(3).strip() if match.group(3) else ""

                if self.is_valid_name(name) and name not in self.people:
                    person_id = self.get_unique_id("person")
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
                        "titles": [title] if title else [],
                        "honors": [],
                        "positions": positions
                    }

        # Look for GOVERNMENT/ADMINISTRATION section with officials
        admin_section = re.search(r"(?:GOVERNMENT|ADMINISTRATION).*?(?=\n[A-Z{2,}]|\Z)",
                                 text, re.IGNORECASE | re.DOTALL)

        if admin_section:
            # Pattern: "Name, Title" in lists
            pattern = r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})\s*,\s*([A-Z][a-z\s]+(?:Governor|Secretary|Director|Commissioner|Judge|Chief|Officer|Administrator))"

            for match in re.finditer(pattern, admin_section.group(0)):
                name = match.group(1).strip()
                position = match.group(2).strip()

                if self.is_valid_name(name) and name not in self.people:
                    person_id = self.get_unique_id("person")

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

    def extract_population_strict(self, text: str, colony_name: str) -> None:
        """Extract population data with validation"""
        # Look for POPULATION section
        pop_section = re.search(r"(?:POPULATION|Census).*?(?:\n[A-Z{2,}]|\Z)",
                               text, re.IGNORECASE | re.DOTALL)

        if not pop_section:
            return

        pop_text = pop_section.group(0)

        # Look for tables with populations
        # Extract numbers and find reasonable total
        numbers = []
        for num_match in re.finditer(r"(\d{1,3}(?:,\d{3})*)", pop_text):
            try:
                numbers.append(int(num_match.group(1).replace(",", "")))
            except:
                pass

        if numbers:
            # Filter for reasonable population sizes (> 500, < 50 million)
            valid_pops = [n for n in numbers if 500 < n < 50000000]
            if valid_pops:
                # Use the largest as total population
                total = max(valid_pops)
                demo_id = self.get_unique_id("demo")

                self.demographics.append({
                    "id": demo_id,
                    "location": colony_name,
                    "year": self.year,
                    "total_population": total,
                    "breakdowns": []
                })

    def extract_institutions_strict(self, text: str, colony_name: str) -> None:
        """Extract institutions found in text"""
        institutions_map = [
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
        ]

        for inst_name, inst_type in institutions_map:
            if re.search(r"\b" + re.escape(inst_name) + r"\b", text, re.IGNORECASE):
                inst_id = self.get_unique_id("inst")

                self.institutions[inst_id] = {
                    "id": inst_id,
                    "name": inst_name,
                    "type": inst_type,
                    "location": colony_name,
                    "year": self.year
                }

    def extract_economic_data_strict(self, text: str, colony_name: str) -> None:
        """Extract economic data"""
        # Look for CURRENCY/BANKING section
        if re.search(r"(?:CURRENCY|BANKING|FINANCIAL)", text, re.IGNORECASE):
            self.economic_data.append({
                "id": self.get_unique_id("econ"),
                "type": "banking",
                "location": colony_name,
                "year": self.year,
                "data": {
                    "category": "currency_and_banking",
                    "notes": "Banking and currency systems documented"
                }
            })

        # Look for AGRICULTURE/CROPS section
        if re.search(r"(?:AGRICULTURE|CROPS|PRINCIPAL.*PRODUCTS)", text, re.IGNORECASE):
            crop_section = re.search(r"(?:crop|agriculture).*?(?:\n[A-Z{2,}]|\Z)",
                                    text, re.IGNORECASE | re.DOTALL)
            if crop_section:
                self.economic_data.append({
                    "id": self.get_unique_id("econ"),
                    "type": "production",
                    "location": colony_name,
                    "year": self.year,
                    "data": {
                        "category": "agriculture",
                        "notes": "Agricultural production documented"
                    }
                })

        # Look for revenue/expenditure
        if re.search(r"revenue|expenditure|income", text, re.IGNORECASE):
            self.economic_data.append({
                "id": self.get_unique_id("econ"),
                "type": "financial",
                "location": colony_name,
                "year": self.year,
                "data": {
                    "category": "revenue_and_expenditure",
                    "notes": "Financial data documented"
                }
            })

    def extract_infrastructure_strict(self, text: str, colony_name: str) -> None:
        """Extract infrastructure"""
        infra_types = [
            ("railway", "railway"),
            ("harbour", "harbor"),
            ("harbor", "harbor"),
            ("port", "dock"),
            ("postal", "postal_route"),
        ]

        for keyword, infra_type in infra_types:
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
                                "length": {"value": length, "unit": "miles"}
                            }
                        })
                    except:
                        pass

    def extract_events_strict(self, text: str, colony_name: str) -> None:
        """Extract historical events"""
        date_pattern = r"(\d{1,2}(?:st|nd|rd|th)?)\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+(?:,\s+)?(\d{4})"

        seen_events = set()
        for match in re.finditer(date_pattern, text):
            date_str = match.group(0)

            if date_str not in seen_events:
                # Get surrounding context
                start = max(0, match.start() - 60)
                end = min(len(text), match.end() + 60)
                context = text[start:end].replace("\n", " ").strip()

                event_type = "other"
                if any(w in context.lower() for w in ["treaty", "agreement", "cession"]):
                    event_type = "treaty"
                elif any(w in context.lower() for w in ["established", "founded"]):
                    event_type = "establishment"
                elif any(w in context.lower() for w in ["hurricane", "earthquake"]):
                    event_type = "disaster"

                self.events.append({
                    "id": self.get_unique_id("event"),
                    "date": date_str,
                    "description": context[:100],
                    "locations": [colony_name],
                    "year_mentioned": self.year,
                    "type": event_type
                })

                seen_events.add(date_str)

    def process_colony(self, filepath: str) -> None:
        """Process a single colony file"""
        colony_name = Path(filepath).stem.replace("_", " ")
        self.colonies_processed.append(colony_name)

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read()

            # Extract place info
            place_info = self.extract_place_info(text, colony_name)
            place_id = self.get_unique_id("place")

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
            self.extract_people_strict(text, colony_name)
            self.extract_institutions_strict(text, colony_name)
            self.extract_population_strict(text, colony_name)
            self.extract_economic_data_strict(text, colony_name)
            self.extract_infrastructure_strict(text, colony_name)
            self.extract_events_strict(text, colony_name)

        except Exception as e:
            print(f"  ERROR processing {colony_name}: {e}")

    def process_all(self) -> None:
        """Process all colonies"""
        source_path = Path(self.source_dir)
        colony_files = sorted(source_path.glob("*.md"))

        print(f"Processing {len(colony_files)} colonies...")
        for i, filepath in enumerate(colony_files, 1):
            colony_name = filepath.stem.replace("_", " ")
            print(f"  [{i:2d}/{len(colony_files)}] {colony_name:<30}", end="")
            self.process_colony(str(filepath))
            print(" ✓")

    def generate_output(self) -> Dict[str, Any]:
        """Generate final output"""
        return {
            "metadata": {
                "year": self.year,
                "source_directory": self.source_dir,
                "extraction_date": datetime.now().isoformat(),
                "processing_notes": "Refined extraction focusing on high-quality data from 37 colonies: geographic entities, people, institutions, economic data, infrastructure, demographics, and historical events",
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
            "=" * 75,
            "COLONIAL OFFICE LIST 1948 - KNOWLEDGE GRAPH EXTRACTION REPORT",
            "=" * 75,
            "",
            f"Extraction Date: {output_data['metadata']['extraction_date']}",
            f"Year: {output_data['metadata']['year']}",
            "",
            "COLONIES PROCESSED:",
            f"  Total Count: {len(output_data['metadata']['colonies_processed'])}",
            ""
        ]

        for colony in sorted(output_data['metadata']['colonies_processed']):
            report_lines.append(f"    {colony}")

        report_lines.extend([
            "",
            "ENTITY EXTRACTION SUMMARY:",
            f"  Geographic Entities (Places):           {len(entities['places']):>6}",
            f"  People (with roles/titles):             {len(entities['people']):>6}",
            f"  Institutions (councils, courts, etc):   {len(entities['institutions']):>6}",
            f"  Economic Data (banking, trade, crops):  {len(entities['economic_data']):>6}",
            f"  Infrastructure (ports, railways, etc):  {len(entities['infrastructure']):>6}",
            f"  Demographics (population data):         {len(entities['demographics']):>6}",
            f"  Historical Events (treaties, founded):  {len(entities['events']):>6}",
            "",
            f"TOTAL EXTRACTED ENTITIES: {sum(len(v) if isinstance(v, list) else 0 for v in entities.values())}",
            f"RELATIONSHIPS MAPPED: {len(output_data['relationships'])}",
            "",
            "FILE INFORMATION:",
            f"  Output JSON: {output_path}",
            f"  Output JSON Size: {os.path.getsize(output_path) / 1024:.1f} KB",
            f"  JSON Lines: {sum(1 for line in open(output_path))}",
            "",
            "=" * 75
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

    extractor = RefinedColonialExtractor(source_dir)
    extractor.process_all()
    extractor.save_and_report(output_path)


if __name__ == "__main__":
    main()
