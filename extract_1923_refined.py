#!/usr/bin/env python3
"""
Refined extraction for Colonial Office List 1923
Focuses on accuracy and data quality
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

class RefinedColonialExtractor:
    def __init__(self, year: str, source_dir: str, output_dir: str):
        self.year = year
        self.source_dir = Path(source_dir)
        self.output_dir = Path(output_dir)
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
        self.id_counter = 0
        self.colonies_processed = []

    def generate_id(self, prefix: str) -> str:
        """Generate unique entity ID"""
        self.id_counter += 1
        return f"{prefix}_{self.year}_{self.id_counter:05d}"

    def extract_place_entity(self, colony_name: str, text: str) -> Dict[str, Any]:
        """Extract primary geographic entity"""
        place_id = self.generate_id("place")

        # Extract coordinates using more precise pattern
        coords = None
        coord_match = re.search(
            r"(?:between\s+)?(\d+°\s*\d+['\"]?\s*[NSE]\.?\s*(?:lat\.)?)\s*and\s+(\d+°\s*\d+['\"]?\s*[WE]\.?\s*(?:long\.)?)",
            text
        )
        if coord_match:
            coords = {
                "latitude": coord_match.group(1),
                "longitude": coord_match.group(2)
            }

        # Extract area
        area = None
        area_match = re.search(
            r"(?:area|comprising)\s+(?:about\s+)?(\d+(?:,\d+)?)\s*(?:square\s+)?(miles|acres|sq\.\s*miles)",
            text,
            re.IGNORECASE
        )
        if area_match:
            try:
                area = {
                    "value": float(area_match.group(1).replace(',', '')),
                    "unit": area_match.group(2).lower()
                }
            except:
                pass

        # Extract description from first substantive paragraph
        desc_match = re.search(
            r"(?:is\s+(?:an?\s+)?(?:island|peninsula|settlement|colony|territory).*?(?:\n\n|$))",
            text,
            re.IGNORECASE | re.DOTALL
        )
        description = desc_match.group(0)[:500] if desc_match else text[:300]

        place = {
            "id": place_id,
            "name": colony_name,
            "modern_name": None,
            "type": "colony",
            "coordinates": coords,
            "area": area,
            "description": description.strip(),
            "year": self.year
        }

        return place, place_id

    def extract_demographics(self, text: str, colony_name: str) -> Optional[Dict[str, Any]]:
        """Extract demographic information with better accuracy"""
        # Look for explicit population statements
        pop_patterns = [
            r"(?:The\s+)?population.*?(?:is\s+)?(?:estimated\s+at|about|of)\s+(\d+(?:,\d+)*)",
            r"(?:population\s+)?(?:was|is)\s+(\d+(?:,\d+)*)",
        ]

        population = None
        for pattern in pop_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    population = int(match.group(1).replace(',', ''))
                    break
                except:
                    pass

        if population:
            demo_id = self.generate_id("demo")
            demographics = {
                "id": demo_id,
                "location": colony_name,
                "year": self.year,
                "total_population": population,
                "breakdowns": []
            }

            # Extract ethnic/racial breakdowns if present
            breakdown_patterns = [
                (r"European.*?(\d+(?:,\d+)*)", "European"),
                (r"[Nn]ative.*?(\d+(?:,\d+)*)", "Native"),
                (r"[Aa]frican.*?(\d+(?:,\d+)*)", "African"),
                (r"[Aa]sian.*?(\d+(?:,\d+)*)", "Asian"),
                (r"[Cc]oolie.*?(\d+(?:,\d+)*)", "Coolie"),
                (r"[Cc]hinese.*?(\d+(?:,\d+)*)", "Chinese"),
            ]

            for pattern, category in breakdown_patterns:
                match = re.search(pattern, text)
                if match:
                    try:
                        count = int(match.group(1).replace(',', ''))
                        demographics['breakdowns'].append({
                            "category": category,
                            "count": count,
                            "subcategories": {}
                        })
                    except:
                        pass

            return demographics

        return None

    def extract_institutions(self, text: str, colony_name: str) -> List[Dict[str, Any]]:
        """Extract institutional information"""
        institutions = []

        # Institution type patterns with context
        inst_patterns = [
            (r"(?:Executive Council|Executive\s+Council)", "executive_council"),
            (r"(?:Legislative Council|Legislative\s+Council)", "legislative_council"),
            (r"(?:Privy Council|Privy\s+Council)", "privy_council"),
            (r"Supreme Court", "court"),
            (r"(?:District|Resident|Magistrates)\s+Court", "court"),
            (r"(?:Police|Constabulary)", "police_force"),
            (r"(?:Medical|Health)\s+Department", "medical"),
            (r"(?:Public\s+Works|Public\s+Works\s+Department)", "public_works"),
        ]

        found_institutions = set()

        for pattern, inst_type in inst_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                inst_name = match.group(0).strip()

                if inst_name not in found_institutions:
                    found_institutions.add(inst_name)
                    inst_id = self.generate_id("inst")

                    institution = {
                        "id": inst_id,
                        "name": inst_name,
                        "type": inst_type,
                        "location": colony_name,
                        "year": self.year,
                        "composition": {"description": "", "members": []},
                        "function": ""
                    }
                    institutions.append(institution)

        return institutions

    def extract_economic_data(self, text: str, colony_name: str) -> List[Dict[str, Any]]:
        """Extract economic information with high precision"""
        economic = []

        # More selective revenue/expenditure patterns
        patterns = [
            (r"(?:revenue|revenues)\s+(?:of|for|in|at)\s+(?:about\s+)?(?:£|£)(\d+(?:,\d+)*)", "revenue"),
            (r"(?:expenditure)\s+(?:of|for|in|at)\s+(?:about\s+)?(?:£|£)(\d+(?:,\d+)*)", "expenditure"),
            (r"(?:exports?)\s+(?:of|for|in|at|valued\s+at)\s+(?:about\s+)?(?:£|£)(\d+(?:,\d+)*)", "trade_export"),
            (r"(?:imports?)\s+(?:of|for|in|at|valued\s+at)\s+(?:about\s+)?(?:£|£)(\d+(?:,\d+)*)", "trade_import"),
        ]

        found_entries = set()

        for pattern, econ_type in patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                try:
                    value = int(match.group(1).replace(',', ''))
                    entry_key = f"{econ_type}_{value}"

                    if entry_key not in found_entries and value > 0:
                        found_entries.add(entry_key)
                        econ_id = self.generate_id("econ")

                        econ_entry = {
                            "id": econ_id,
                            "type": econ_type,
                            "location": colony_name,
                            "year": self.year,
                            "data": {
                                "category": econ_type.replace('_', ' '),
                                "value": value,
                                "currency": "£"
                            }
                        }
                        economic.append(econ_entry)
                except:
                    pass

        return economic

    def extract_infrastructure(self, text: str, colony_name: str) -> List[Dict[str, Any]]:
        """Extract infrastructure information"""
        infrastructure = []

        # Infrastructure with specific measurements
        patterns = [
            (r"(?:railway|rail(?:way)?)\s+(?:of|from|connecting|to).*?(\d+)\s*miles", "railway"),
            (r"(?:telegraph|telegraphic)\s+(?:line|lines).*?(\d+)(?:\s+(?:miles|wire\s+miles))?", "telegraph"),
            (r"(?:port|harbour|harbor|dock)", "dock"),
            (r"(?:road)(?:s)?", "road"),
        ]

        found_infra = set()

        for pattern, infra_type in patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                infra_key = f"{infra_type}_{colony_name}"
                if infra_key not in found_infra:
                    found_infra.add(infra_key)
                    infra_id = self.generate_id("infra")

                    infrastructure.append({
                        "id": infra_id,
                        "type": infra_type,
                        "name": f"{colony_name} {infra_type.title()}",
                        "location": colony_name,
                        "year": self.year,
                        "specifications": {},
                        "connections": []
                    })

        return infrastructure

    def extract_historical_events(self, text: str, colony_name: str) -> List[Dict[str, Any]]:
        """Extract significant historical events"""
        events = []

        # More selective event patterns
        event_patterns = [
            r"(?:in|on|during)\s+(\d{4}),?\s+(?:the\s+)?([A-Za-z\s,()]+?)(?:\.|\n)",
            r"([A-Za-z]+\s+\d{1,2}),?\s+(\d{4}),?\s+(.+?)(?:\.|\n)",
        ]

        found_events = set()

        for pattern in event_patterns:
            for match in re.finditer(pattern, text):
                try:
                    if len(match.groups()) >= 2:
                        date_part = match.group(1)
                        desc_part = match.group(2) if len(match.groups()) >= 2 else ""

                        if date_part not in found_events and len(desc_part) > 5:
                            found_events.add(date_part)
                            event_id = self.generate_id("event")

                            event = {
                                "id": event_id,
                                "date": date_part,
                                "description": desc_part[:200],
                                "locations": [colony_name],
                                "people": [],
                                "year_mentioned": self.year
                            }
                            events.append(event)
                except:
                    pass

        # Limit to 10 most significant events per colony
        return events[:10]

    def process_colony_file(self, filepath: Path) -> bool:
        """Process a single colony file"""
        try:
            colony_name = filepath.stem.replace('_', ' ').upper()

            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            if not content.strip():
                return False

            # Extract primary place entity
            place, place_id = self.extract_place_entity(colony_name, content)
            self.entities['places'].append(place)

            # Extract demographics
            demo = self.extract_demographics(content, colony_name)
            if demo:
                self.entities['demographics'].append(demo)

            # Extract institutions
            institutions = self.extract_institutions(content, colony_name)
            self.entities['institutions'].extend(institutions)

            # Extract economic data
            economic = self.extract_economic_data(content, colony_name)
            self.entities['economic_data'].extend(economic)

            # Extract infrastructure
            infrastructure = self.extract_infrastructure(content, colony_name)
            self.entities['infrastructure'].extend(infrastructure)

            # Extract events
            events = self.extract_historical_events(content, colony_name)
            self.entities['events'].extend(events)

            self.colonies_processed.append(colony_name)
            return True

        except Exception as e:
            print(f"Error processing {filepath.name}: {str(e)[:50]}")
            return False

    def process_all_colonies(self):
        """Process all colony files"""
        colony_files = sorted(self.source_dir.glob('*.md'))
        success_count = 0

        for filepath in colony_files:
            if self.process_colony_file(filepath):
                success_count += 1

        return success_count

    def build_output(self) -> Dict[str, Any]:
        """Build final output structure"""
        output = {
            "metadata": {
                "year": self.year,
                "source_directory": str(self.source_dir),
                "extraction_date": datetime.now().isoformat(),
                "colonies_processed": sorted(self.colonies_processed),
                "processing_notes": (
                    f"High-quality extraction of {len(self.colonies_processed)} colonies. "
                    f"Extracted {len(self.entities['places'])} places, "
                    f"{len(self.entities['institutions'])} institutions, "
                    f"{len(self.entities['economic_data'])} economic records, "
                    f"{len(self.entities['infrastructure'])} infrastructure items, "
                    f"{len(self.entities['demographics'])} demographic records, "
                    f"{len(self.entities['events'])} historical events."
                )
            },
            "entities": self.entities,
            "relationships": self.relationships
        }

        return output

    def save_output(self, output: Dict[str, Any], filepath: Path):
        """Save to JSON"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

    def extract(self) -> tuple:
        """Run extraction"""
        print(f"Extracting knowledge graph for {self.year}...")
        print(f"Source: {self.source_dir}")

        success_count = self.process_all_colonies()

        print(f"\nProcessed {success_count} colonies successfully")
        print(f"Total entities extracted: {sum(len(v) for v in self.entities.values())}")
        for etype, items in self.entities.items():
            print(f"  - {etype}: {len(items)}")

        output = self.build_output()
        output_file = self.output_dir / f"{self.year}_extracted.json"
        self.save_output(output, output_file)

        print(f"\nSaved to: {output_file}")

        return output, output_file

def main():
    year = "1923"
    source_dir = "/home/user/colonial_office_list/output_2/1923_manual_parsed"
    output_dir = "/home/user/colonial_office_list/knowledge_graph_extracts"

    extractor = RefinedColonialExtractor(year, source_dir, output_dir)
    output, output_file = extractor.extract()

    print("\n" + "="*70)
    print("COLONIAL OFFICE LIST 1923 - KNOWLEDGE GRAPH EXTRACTION COMPLETE")
    print("="*70)
    print(f"Year: {year}")
    print(f"Colonies: {len(output['metadata']['colonies_processed'])}")
    print(f"Places: {len(output['entities']['places'])}")
    print(f"Institutions: {len(output['entities']['institutions'])}")
    print(f"Economic Records: {len(output['entities']['economic_data'])}")
    print(f"Infrastructure: {len(output['entities']['infrastructure'])}")
    print(f"Demographics: {len(output['entities']['demographics'])}")
    print(f"Historical Events: {len(output['entities']['events'])}")
    print(f"File: {output_file}")
    print("="*70)

if __name__ == "__main__":
    main()
