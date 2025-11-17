#!/usr/bin/env python3
"""
Enhanced extraction for Colonial Office List 1923
Includes economic data and relationship building
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional

class EnhancedColonialExtractor:
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
        self.place_map = {}  # Map colony names to place IDs

    def generate_id(self, prefix: str) -> str:
        """Generate unique entity ID"""
        self.id_counter += 1
        return f"{prefix}_{self.year}_{self.id_counter:05d}"

    def should_skip_file(self, filename: str) -> bool:
        """Skip non-colony files"""
        skip_patterns = ['APPENDIX', 'INDEX', 'HONOURS']
        return any(pattern.lower() in filename.lower() for pattern in skip_patterns)

    def extract_place_entity(self, colony_name: str, text: str) -> tuple:
        """Extract primary geographic entity"""
        place_id = self.generate_id("place")

        # Try to extract coordinates
        coords = None

        # Pattern: lat. XX° XX' and long. XX° XX'
        coord_patterns = [
            r"(\d+°\s*\d+['\"]?\s*[NS]\.?\s*(?:lat\.)?)\s*(?:and|,)\s*(\d+°\s*\d+['\"]?\s*[EW]\.?\s*(?:long\.)?)",
            r"between\s+(\d+°[^,]+)\s+and\s+(\d+°[^,]+?)(?:\n|,)",
        ]

        for pattern in coord_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                coords = {
                    "latitude": match.group(1).strip(),
                    "longitude": match.group(2).strip()
                }
                break

        # Extract area
        area = None
        area_patterns = [
            r"(?:area.*?)?(\d+(?:,\d+)?)\s*(?:square\s+)?(miles|acres)",
            r"comprising\s+(?:about\s+)?(\d+(?:,\d+)?)\s*square\s+(miles)",
        ]

        for pattern in area_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                try:
                    area = {
                        "value": float(match.group(1).replace(',', '')),
                        "unit": match.group(2).lower().replace('square ', '').strip()
                    }
                    break
                except:
                    pass

        # Extract description
        desc_match = re.search(
            r"^[A-Z][^.]*?(?:is|consists of).*?(?:\n\n|(?=\n[A-Z][a-z]+))",
            text,
            re.IGNORECASE | re.DOTALL
        )
        description = desc_match.group(0)[:400] if desc_match else text[:300]

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

        self.place_map[colony_name] = place_id
        return place, place_id

    def extract_demographics(self, text: str, colony_name: str) -> Optional[Dict[str, Any]]:
        """Extract demographic information"""
        # More comprehensive population patterns
        pop_patterns = [
            r"population.*?(?:is|was|of|about)\s+(\d+(?:,\d+)*)\s*(?:persons?|inhabitants)",
            r"(?:The\s+)?inhabitants.*?(?:is|are|estimated\s+at|about)\s+(\d+(?:,\d+)*)",
            r"(?:census|enumerated).*?(?:was|is)\s+(\d+(?:,\d+)*)",
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

            # Extract population breakdowns
            breakdown_patterns = [
                (r"Europeans?.*?(\d+(?:,\d+)*)", "European"),
                (r"native[s]?.*?(\d+(?:,\d+)*)", "Native"),
                (r"Africans?.*?(\d+(?:,\d+)*)", "African"),
                (r"Asians?.*?(\d+(?:,\d+)*)", "Asian"),
                (r"coolies?.*?(\d+(?:,\d+)*)", "Coolie"),
                (r"Chinese.*?(\d+(?:,\d+)*)", "Chinese"),
                (r"East Indians?.*?(\d+(?:,\d+)*)", "East Indian"),
                (r"mixed.*?(\d+(?:,\d+)*)", "Mixed Race"),
            ]

            for pattern, category in breakdown_patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    try:
                        count = int(match.group(1).replace(',', ''))
                        if count > 0:
                            demographics['breakdowns'].append({
                                "category": category,
                                "count": count,
                                "subcategories": {}
                            })
                            break
                    except:
                        pass

            return demographics

        return None

    def extract_institutions(self, text: str, colony_name: str) -> List[Dict[str, Any]]:
        """Extract institutions more comprehensively"""
        institutions = []

        inst_patterns = [
            (r"Executive Council", "executive_council"),
            (r"Legislative Council", "legislative_council"),
            (r"Privy Council", "privy_council"),
            (r"Supreme Court", "court"),
            (r"(?:Resident\s+)?Magistrates?\s+Court", "court"),
            (r"Police\s+(?:Court|Force|Constabulary)", "police_force"),
            (r"(?:Colonial\s+)?Treasury", "department"),
            (r"Colonial\s+Secretary", "department"),
            (r"(?:Public\s+)?Works\s+Department", "public_works"),
            (r"Medical\s+(?:Department|Officer)", "medical"),
            (r"Education\s+Department", "educational"),
            (r"Post Office", "postal"),
        ]

        found = set()
        for pattern, inst_type in inst_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                inst_name = match.group(0).strip()
                if inst_name not in found:
                    found.add(inst_name)
                    inst_id = self.generate_id("inst")
                    institutions.append({
                        "id": inst_id,
                        "name": inst_name,
                        "type": inst_type,
                        "location": colony_name,
                        "year": self.year,
                        "composition": {"description": "", "members": []},
                        "function": ""
                    })

        return institutions

    def extract_economic_data(self, text: str, colony_name: str) -> List[Dict[str, Any]]:
        """Extract economic data with multiple patterns"""
        economic = []

        # Enhanced patterns for currency and numbers
        patterns = [
            # Revenue patterns
            (r"(?:revenue|receipts?).*?(?:£|£)(\d+(?:,\d+)*)", "revenue"),
            (r"total\s+(?:revenue|receipts?).*?(\d+(?:,\d+)*)", "revenue"),

            # Expenditure patterns
            (r"(?:expenditure|expenses?).*?(?:£|£)(\d+(?:,\d+)*)", "expenditure"),
            (r"spending\s+(?:£|£)(\d+(?:,\d+)*)", "expenditure"),

            # Trade patterns
            (r"(?:exports?|exported).*?(?:£|£|value[d]?\s+at)(\d+(?:,\d+)*)", "trade_export"),
            (r"(?:imports?|imported).*?(?:£|£|value[d]?\s+at)(\d+(?:,\d+)*)", "trade_import"),

            # Production/commodities
            (r"(?:production|output).*?(?:£|£)(\d+(?:,\d+)*)", "production"),
        ]

        found = set()
        for pattern, econ_type in patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                try:
                    value_str = match.group(1).replace(',', '')
                    value = int(value_str)

                    # Create a unique key to avoid duplicates
                    key = f"{econ_type}_{value}"
                    if key not in found and value > 100:  # Only significant values
                        found.add(key)
                        econ_id = self.generate_id("econ")
                        economic.append({
                            "id": econ_id,
                            "type": econ_type,
                            "location": colony_name,
                            "year": self.year,
                            "data": {
                                "category": econ_type.replace('_', ' ').title(),
                                "value": value,
                                "currency": "£"
                            }
                        })
                except:
                    pass

        return economic

    def extract_infrastructure(self, text: str, colony_name: str) -> List[Dict[str, Any]]:
        """Extract infrastructure information"""
        infrastructure = []

        infra_patterns = [
            (r"railway\s+(?:from|to|connecting|of).*?(\d+)\s*miles", "railway"),
            (r"telegraph.*?(?:lines?|wires?|miles).*?(\d+)?", "telegraph"),
            (r"(?:port|harbour|harbor|dock|wharf)", "dock"),
            (r"(?:road|roads).*?(?:of|~).*?(\d+)?", "road"),
            (r"(?:bridge|bridges)", "bridge"),
            (r"water\s+(?:works|supply)", "water_works"),
            (r"(?:lighthouses?|lighthouse)", "public_building"),
        ]

        found = set()
        for pattern, infra_type in infra_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                key = f"{infra_type}_{colony_name}"
                if key not in found:
                    found.add(key)
                    infra_id = self.generate_id("infra")
                    infrastructure.append({
                        "id": infra_id,
                        "type": infra_type,
                        "name": f"{colony_name} {infra_type.replace('_', ' ').title()}",
                        "location": colony_name,
                        "year": self.year,
                        "specifications": {},
                        "connections": []
                    })

        return infrastructure

    def extract_historical_events(self, text: str, colony_name: str) -> List[Dict[str, Any]]:
        """Extract historical events"""
        events = []

        # More selective event extraction
        event_patterns = [
            r"(?:in|on)\s+(\d{4}),?\s+(?:the\s+)?([A-Za-z\s]+?)(?:\.|;)",
            r"([A-Za-z]+\s+(?:1|2)\d\d\d),?\s+([A-Za-z\s.,']+?)(?:\n|$)",
        ]

        found = set()
        for pattern in event_patterns:
            for match in re.finditer(pattern, text):
                try:
                    date_str = match.group(1)
                    desc_str = match.group(2)[:100] if len(match.groups()) > 1 else ""

                    if date_str not in found and len(desc_str) > 3:
                        found.add(date_str)
                        event_id = self.generate_id("event")
                        events.append({
                            "id": event_id,
                            "date": date_str,
                            "description": desc_str.strip(),
                            "locations": [colony_name],
                            "people": [],
                            "year_mentioned": self.year
                        })
                except:
                    pass

        return events[:5]  # Limit to 5 per colony

    def process_colony_file(self, filepath: Path) -> bool:
        """Process a single colony file"""
        try:
            if self.should_skip_file(filepath.name):
                return False

            colony_name = filepath.stem.replace('_', ' ').upper()

            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()

            if not content.strip() or len(content) < 100:
                return False

            # Geographic entity
            place, place_id = self.extract_place_entity(colony_name, content)
            self.entities['places'].append(place)

            # Demographics
            demo = self.extract_demographics(content, colony_name)
            if demo:
                self.entities['demographics'].append(demo)

            # Institutions
            institutions = self.extract_institutions(content, colony_name)
            self.entities['institutions'].extend(institutions)

            # Economic data
            economic = self.extract_economic_data(content, colony_name)
            self.entities['economic_data'].extend(economic)

            # Infrastructure
            infrastructure = self.extract_infrastructure(content, colony_name)
            self.entities['infrastructure'].extend(infrastructure)

            # Events
            events = self.extract_historical_events(content, colony_name)
            self.entities['events'].extend(events)

            self.colonies_processed.append(colony_name)
            return True

        except Exception as e:
            print(f"Error in {filepath.name}: {str(e)[:50]}")
            return False

    def build_relationships(self):
        """Build entity relationships"""
        # Add relationships from places to institutions
        for inst in self.entities['institutions']:
            if inst['location'] in self.place_map:
                self.relationships.append({
                    "source_id": inst['id'],
                    "relationship_type": "LOCATED_IN",
                    "target_id": self.place_map[inst['location']],
                    "properties": {"year": self.year}
                })

        # Add relationships from economic data to places
        for econ in self.entities['economic_data']:
            if econ['location'] in self.place_map:
                self.relationships.append({
                    "source_id": econ['id'],
                    "relationship_type": "DURING_YEAR",
                    "target_id": self.place_map[econ['location']],
                    "properties": {"year": self.year}
                })

        # Add relationships from infrastructure to places
        for infra in self.entities['infrastructure']:
            if infra['location'] in self.place_map:
                self.relationships.append({
                    "source_id": infra['id'],
                    "relationship_type": "LOCATED_IN",
                    "target_id": self.place_map[infra['location']],
                    "properties": {"year": self.year}
                })

    def process_all_colonies(self):
        """Process all colony files"""
        colony_files = sorted(self.source_dir.glob('*.md'))
        success = 0

        for filepath in colony_files:
            if self.process_colony_file(filepath):
                success += 1

        return success

    def build_output(self) -> Dict[str, Any]:
        """Build final output"""
        return {
            "metadata": {
                "year": self.year,
                "source_directory": str(self.source_dir),
                "extraction_date": datetime.now().isoformat(),
                "colonies_processed": sorted(self.colonies_processed),
                "processing_notes": (
                    f"Comprehensive extraction of {len(self.colonies_processed)} colonies. "
                    f"Extracted {len(self.entities['places'])} geographic entities, "
                    f"{len(self.entities['people'])} people, "
                    f"{len(self.entities['institutions'])} institutions, "
                    f"{len(self.entities['economic_data'])} economic records, "
                    f"{len(self.entities['infrastructure'])} infrastructure items, "
                    f"{len(self.entities['demographics'])} demographic records, "
                    f"{len(self.entities['events'])} historical events, and "
                    f"{len(self.relationships)} relationships."
                )
            },
            "entities": self.entities,
            "relationships": self.relationships
        }

    def save_output(self, output: Dict[str, Any], filepath: Path):
        """Save to JSON"""
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

    def extract(self) -> tuple:
        """Run full extraction"""
        print(f"Enhanced extraction for {self.year}...")
        print(f"Source: {self.source_dir}\n")

        success = self.process_all_colonies()
        print(f"Processed {success} colonies successfully\n")

        # Build relationships
        self.build_relationships()
        print(f"Built {len(self.relationships)} relationships\n")

        # Print entity summary
        print("Entity Summary:")
        for etype, items in self.entities.items():
            print(f"  {etype}: {len(items)}")

        output = self.build_output()
        output_file = self.output_dir / f"{self.year}_extracted.json"
        self.save_output(output, output_file)

        print(f"\nOutput: {output_file}")

        return output, output_file

def main():
    year = "1923"
    source_dir = "/home/user/colonial_office_list/output_2/1923_manual_parsed"
    output_dir = "/home/user/colonial_office_list/knowledge_graph_extracts"

    extractor = EnhancedColonialExtractor(year, source_dir, output_dir)
    output, output_file = extractor.extract()

    print("\n" + "="*75)
    print(" COLONIAL OFFICE LIST 1923 - KNOWLEDGE GRAPH EXTRACTION")
    print("="*75)
    print(f"Year: {year}")
    print(f"Colonies: {len(output['metadata']['colonies_processed'])}")
    print(f"Total Entities: {sum(len(v) for v in output['entities'].values())}")
    print(f"  Places: {len(output['entities']['places'])}")
    print(f"  Institutions: {len(output['entities']['institutions'])}")
    print(f"  Economic Records: {len(output['entities']['economic_data'])}")
    print(f"  Infrastructure: {len(output['entities']['infrastructure'])}")
    print(f"  Demographics: {len(output['entities']['demographics'])}")
    print(f"  Events: {len(output['entities']['events'])}")
    print(f"Relationships: {len(output['relationships'])}")
    print(f"File: {output_file}")
    print(f"Size: {output_file.stat().st_size / 1024:.1f} KB")
    print("="*75)

if __name__ == "__main__":
    main()
