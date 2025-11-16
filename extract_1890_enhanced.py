#!/usr/bin/env python3
"""
Enhanced Knowledge Graph Extraction for Colonial Office List 1890
More sophisticated entity extraction with improved accuracy
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
from collections import defaultdict

class EnhancedColonialExtractor:
    """Enhanced extractor with better pattern matching and context awareness"""

    def __init__(self, base_path: str):
        self.base_path = Path(base_path)
        self.entity_id_counter = defaultdict(int)
        self.knowledge_graph = {
            "metadata": {
                "year": 1890,
                "source": "Colonial Office List 1890",
                "extraction_date": datetime.now().isoformat(),
                "colonies_processed": 0,
                "total_entities": 0
            },
            "entities": {
                "geographic_entities": [],
                "people": [],
                "institutions": [],
                "economic_data": [],
                "infrastructure": [],
                "demographic_data": [],
                "historical_events": [],
                "legal_documents": [],
                "military_units": [],
                "ships": [],
                "buildings": []
            },
            "relationships": []
        }

    def generate_id(self, prefix: str) -> str:
        """Generate unique ID with prefix"""
        self.entity_id_counter[prefix] += 1
        return f"{prefix}_{self.entity_id_counter[prefix]:06d}"

    def extract_section(self, content: str, section_name: str) -> Optional[str]:
        """Extract a specific section from the document"""
        # Pattern to match section headers
        pattern = rf"(?:^|\n)#{1,3}\s*{re.escape(section_name)}.*?\n(.*?)(?=\n#{1,3}\s|\Z)"
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1)

        # Try alternative pattern without markdown
        pattern = rf"(?:^|\n){re.escape(section_name)}[:\.\s]*\n(.*?)(?=\n[A-Z][a-zA-Z\s]+[:\.\s]*\n|\Z)"
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        if match:
            return match.group(1)

        return None

    def extract_governors_list(self, content: str, colony: str) -> List[Dict]:
        """Extract governor information from the Governors section"""
        people = []

        # Find the Governors section
        gov_section = self.extract_section(content, "Governors")
        if not gov_section:
            gov_section = self.extract_section(content, "List of Governors")

        if gov_section:
            # Pattern: Year Name with possible titles
            lines = gov_section.split('\n')
            for line in lines:
                # Match: YYYY Name (with possible dots, commas, titles)
                match = re.match(r'(\d{4})\s+(.+)', line.strip())
                if match:
                    year = int(match.group(1))
                    name_part = match.group(2).strip()

                    # Skip if it's just dots or dashes
                    if re.match(r'^[.\-\s]+$', name_part):
                        continue

                    # Extract honors
                    honors = re.findall(r'\b(K\.C\.M\.G\.|G\.C\.M\.G\.|C\.B\.|K\.C\.B\.|G\.C\.B\.|C\.M\.G\.|K\.C\.S\.I\.|G\.C\.S\.I\.)\b', name_part)

                    # Extract titles
                    titles = []
                    if re.search(r'\bSir\b', name_part):
                        titles.append('Sir')
                    if re.search(r'\b(Lord|Earl|Viscount|Baron|Duke|Marquis)\b', name_part):
                        titles.append('Nobleman')
                    if re.search(r'\b(Major-General|Lieutenant-General|Admiral|Colonel|Captain)\b', name_part):
                        titles.append('Military Officer')

                    # Clean name
                    name_clean = re.sub(r'\b(K\.C\.M\.G\.|G\.C\.M\.G\.|C\.B\.|K\.C\.B\.|G\.C\.B\.|C\.M\.G\.|K\.C\.S\.I\.|G\.C\.S\.I\.)\b', '', name_part)
                    name_clean = re.sub(r'\(.*?\)', '', name_clean)  # Remove parenthetical notes
                    name_clean = re.sub(r'\s+', ' ', name_clean).strip('. ,')

                    # Only add if name looks reasonable (has at least 2 characters and isn't all punctuation)
                    if len(name_clean) >= 2 and re.search(r'[A-Za-z]{2,}', name_clean):
                        people.append({
                            "id": self.generate_id("person"),
                            "name": name_clean,
                            "titles": titles,
                            "honors": honors,
                            "positions": [{
                                "title": "Governor",
                                "location": colony,
                                "start_year": year,
                                "end_year": None
                            }],
                            "salary": None,
                            "source_colony": colony
                        })

        return people

    def extract_civil_establishment(self, content: str, colony: str) -> List[Dict]:
        """Extract current officials from Civil Establishment section"""
        people = []

        civil_section = self.extract_section(content, "Civil Establishment")
        if not civil_section:
            civil_section = self.extract_section(content, "Executive Council")

        if civil_section:
            lines = civil_section.split('\n')
            for line in lines:
                # Pattern: Position, Name, Salary
                # Example: "Governor, Sir John Smith, £2,000"
                salary_match = re.search(r'([^,]+?),\s*([A-Z][^,]+?),\s*[£\$Rs\.]\s*([\d,]+)', line)
                if salary_match:
                    position = salary_match.group(1).strip()
                    name = salary_match.group(2).strip()
                    salary_str = salary_match.group(3).replace(',', '')

                    # Extract honors from name
                    honors = re.findall(r'\b(K\.C\.M\.G\.|G\.C\.M\.G\.|C\.B\.|K\.C\.B\.|G\.C\.B\.|C\.M\.G\.)\b', name)

                    # Clean name
                    name_clean = re.sub(r'\b(K\.C\.M\.G\.|G\.C\.M\.G\.|C\.B\.|K\.C\.B\.|G\.C\.B\.|C\.M\.G\.)\b', '', name)
                    name_clean = re.sub(r'\s+', ' ', name_clean).strip()

                    try:
                        salary_value = int(salary_str)
                        people.append({
                            "id": self.generate_id("person"),
                            "name": name_clean,
                            "titles": ["Sir"] if "Sir" in name else [],
                            "honors": honors,
                            "positions": [{
                                "title": position,
                                "location": colony,
                                "year": 1890
                            }],
                            "salary": {
                                "amount": salary_value,
                                "currency": "£",
                                "period": "annual"
                            },
                            "source_colony": colony
                        })
                    except ValueError:
                        pass

        return people

    def extract_institutions(self, content: str, colony: str) -> List[Dict]:
        """Extract institutional entities"""
        institutions = []

        # Extract councils
        council_patterns = [
            r"(Legislative Council|Executive Council|Privy Council|Council of Government)",
            r"(Supreme Court|High Court|Court of.*?)",
            r"(House of Assembly|Legislative Assembly)",
            r"(.*?Bank.*?)",
            r"(.*?University.*?)",
            r"(.*?College.*?)"
        ]

        for pattern in council_patterns:
            matches = re.finditer(pattern, content)
            for match in matches:
                inst_name = match.group(1).strip()
                if len(inst_name) > 3:  # Filter out very short matches
                    inst_type = "council"
                    if "Court" in inst_name:
                        inst_type = "court"
                    elif "Bank" in inst_name:
                        inst_type = "bank"
                    elif "University" in inst_name or "College" in inst_name:
                        inst_type = "educational"
                    elif "Assembly" in inst_name:
                        inst_type = "legislature"

                    institutions.append({
                        "id": self.generate_id("institution"),
                        "name": inst_name,
                        "type": inst_type,
                        "colony": colony,
                        "year": 1890
                    })

        return institutions

    def extract_economic_comprehensive(self, content: str, colony: str) -> List[Dict]:
        """Extract comprehensive economic data"""
        economic_data = []

        # Extract trade data from tables
        table_pattern = r"\|\s*Year\s*\|.*?Revenue.*?Expenditure.*?\n([\s\S]*?)(?:\n\n|\Z)"
        table_match = re.search(table_pattern, content)

        if table_match:
            table_content = table_match.group(1)
            lines = table_content.split('\n')
            for line in lines:
                # Match: | Year | Revenue | Expenditure |
                data_match = re.search(r'\|\s*(\d{4})\s*\|\s*[£\$Rs\.,\s]*([\d,]+)\s*\|\s*[£\$Rs\.,\s]*([\d,]+)', line)
                if data_match:
                    year = int(data_match.group(1))
                    try:
                        revenue = int(data_match.group(2).replace(',', ''))
                        expenditure = int(data_match.group(3).replace(',', ''))

                        economic_data.append({
                            "id": self.generate_id("economic"),
                            "type": "revenue",
                            "colony": colony,
                            "year": year,
                            "amount": revenue,
                            "currency": "£"
                        })

                        economic_data.append({
                            "id": self.generate_id("economic"),
                            "type": "expenditure",
                            "colony": colony,
                            "year": year,
                            "amount": expenditure,
                            "currency": "£"
                        })
                    except ValueError:
                        pass

        # Extract debt data
        debt_pattern = r"(?:Public )?Debt[:\s,]*[£\$Rs\.]\s*([\d,]+)"
        debt_match = re.search(debt_pattern, content, re.IGNORECASE)
        if debt_match:
            try:
                debt_value = int(debt_match.group(1).replace(',', ''))
                economic_data.append({
                    "id": self.generate_id("economic"),
                    "type": "public_debt",
                    "colony": colony,
                    "year": 1890,
                    "amount": debt_value,
                    "currency": "£"
                })
            except ValueError:
                pass

        return economic_data

    def extract_military(self, content: str, colony: str) -> Tuple[List[Dict], List[Dict]]:
        """Extract military units and ships"""
        military_units = []
        ships = []

        # Extract garrison information
        garrison_pattern = r"(?:Imperial )?garrison of (?:about )?(\d+[,\d]*)\s+men"
        garrison_match = re.search(garrison_pattern, content, re.IGNORECASE)
        if garrison_match:
            try:
                strength = int(garrison_match.group(1).replace(',', ''))
                military_units.append({
                    "id": self.generate_id("military"),
                    "name": f"{colony} Imperial Garrison",
                    "type": "garrison",
                    "colony": colony,
                    "strength": strength,
                    "year": 1890
                })
            except ValueError:
                pass

        # Extract volunteer forces
        volunteer_pattern = r"volunteer.*?(\d+[,\d]*)\s+(?:men|officers and men)"
        volunteer_match = re.search(volunteer_pattern, content, re.IGNORECASE)
        if volunteer_match:
            try:
                strength = int(volunteer_match.group(1).replace(',', ''))
                military_units.append({
                    "id": self.generate_id("military"),
                    "name": f"{colony} Volunteer Force",
                    "type": "volunteers",
                    "colony": colony,
                    "strength": strength,
                    "year": 1890
                })
            except ValueError:
                pass

        # Extract ships
        ship_pattern = r'(?:gunboat|frigate|cruiser|vessel|steamer|ship)\s+"([^"]+)"'
        for ship_match in re.finditer(ship_pattern, content, re.IGNORECASE):
            ship_name = ship_match.group(1)
            ships.append({
                "id": self.generate_id("ship"),
                "name": ship_name,
                "colony": colony,
                "year": 1890
            })

        return military_units, ships

    def process_colony_file(self, file_path: Path) -> Dict[str, int]:
        """Process a single colony file and return entity counts"""
        colony_name = file_path.stem.replace('_', ' ')
        counts = defaultdict(int)

        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract all entity types
            governors = self.extract_governors_list(content, colony_name)
            self.knowledge_graph["entities"]["people"].extend(governors)
            counts["governors"] = len(governors)

            officials = self.extract_civil_establishment(content, colony_name)
            self.knowledge_graph["entities"]["people"].extend(officials)
            counts["officials"] = len(officials)

            institutions = self.extract_institutions(content, colony_name)
            # Deduplicate institutions by name
            unique_institutions = {inst["name"]: inst for inst in institutions}
            self.knowledge_graph["entities"]["institutions"].extend(unique_institutions.values())
            counts["institutions"] = len(unique_institutions)

            economic = self.extract_economic_comprehensive(content, colony_name)
            self.knowledge_graph["entities"]["economic_data"].extend(economic)
            counts["economic"] = len(economic)

            military_units, ships = self.extract_military(content, colony_name)
            self.knowledge_graph["entities"]["military_units"].extend(military_units)
            self.knowledge_graph["entities"]["ships"].extend(ships)
            counts["military"] = len(military_units)
            counts["ships"] = len(ships)

            self.knowledge_graph["metadata"]["colonies_processed"] += 1
            print(f"✓ {colony_name}: {sum(counts.values())} entities")

        except Exception as e:
            print(f"✗ {colony_name}: Error - {e}")

        return counts

    def process_all(self) -> None:
        """Process all colony files"""
        colony_files = sorted(self.base_path.glob("*.md"))
        total_counts = defaultdict(int)

        print("\n" + "="*60)
        print("EXTRACTING KNOWLEDGE GRAPH FROM 1890 COLONIAL OFFICE LIST")
        print("="*60 + "\n")

        for file_path in colony_files:
            counts = self.process_colony_file(file_path)
            for key, value in counts.items():
                total_counts[key] += value

        # Update total entities count
        self.knowledge_graph["metadata"]["total_entities"] = sum(
            len(entities) for entities in self.knowledge_graph["entities"].values()
        )

        print("\n" + "="*60)
        print("EXTRACTION SUMMARY")
        print("="*60)
        print(f"Colonies processed: {self.knowledge_graph['metadata']['colonies_processed']}")
        print(f"Total entities extracted: {self.knowledge_graph['metadata']['total_entities']}")
        print("\nBreakdown by category:")
        for entity_type, entities in self.knowledge_graph["entities"].items():
            if len(entities) > 0:
                print(f"  {entity_type}: {len(entities)}")

    def save(self, output_path: str) -> None:
        """Save knowledge graph to JSON"""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.knowledge_graph, f, indent=2, ensure_ascii=False)

        print(f"\n✓ Saved to: {output_path}")
        print(f"  File size: {output_file.stat().st_size:,} bytes")

def main():
    base_path = "/home/user/colonial_office_list/output_2/1890_manual_parsed"
    output_path = "/home/user/colonial_office_list/knowledge_graph_extracts/1890_extracted.json"

    extractor = EnhancedColonialExtractor(base_path)
    extractor.process_all()
    extractor.save(output_path)

if __name__ == "__main__":
    main()
