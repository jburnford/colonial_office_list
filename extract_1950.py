#!/usr/bin/env python3
"""
Extract comprehensive knowledge graph data from Colonial Office List 1950
Follows EXTRACTION_METHODOLOGY.md and json_schema_template.json
"""

import json
import os
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
import glob

class ColonialOfficeExtractor:
    def __init__(self, source_dir: str, output_dir: str):
        self.source_dir = source_dir
        self.output_dir = output_dir
        self.year = "1950"

        # Initialize data structures
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
        self.entity_ids = {}  # For deduplication
        self.id_counter = 0
        self.processed_files = []

    def generate_id(self, prefix: str, name: str) -> str:
        """Generate unique ID for entities"""
        base_id = f"{prefix}_{name.lower().replace(' ', '_').replace('-', '_')}"
        if base_id not in self.entity_ids:
            self.entity_ids[base_id] = True
            return base_id
        else:
            self.id_counter += 1
            return f"{base_id}_{self.id_counter}"

    def extract_coordinates(self, text: str) -> Optional[Dict[str, str]]:
        """Extract latitude and longitude from text"""
        # Pattern: "latitude XX° YY' N. and longitude XX° YY' E."
        pattern = r"latitude\s+([\d°\'\s]+)\s+and\s+longitude\s+([\d°\'\s]+)"
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return {
                "latitude": match.group(1).strip(),
                "longitude": match.group(2).strip()
            }
        return None

    def extract_area(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract area measurements"""
        patterns = [
            r"(\d+(?:\.\d+)?)\s+square\s+miles",
            r"(\d+(?:\.\d+)?)\s+acres",
            r"(\d+(?:\.\d+)?)\s+sq\.\s+miles",
            r"(\d+(?:\.\d+)?)\s+km"
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                if "square miles" in match.group(0).lower() or "sq." in match.group(0).lower():
                    unit = "square miles"
                elif "acres" in match.group(0).lower():
                    unit = "acres"
                else:
                    unit = "km²"
                return {
                    "value": float(match.group(1)),
                    "unit": unit
                }
        return None

    def extract_population(self, text: str, colony_name: str) -> None:
        """Extract demographic information"""
        # Look for population sections
        sections = re.split(r'(?:^|\n)(?:POPULATION|Population)', text, flags=re.MULTILINE | re.IGNORECASE)

        for section in sections[1:]:  # Skip first split which is before Population section
            lines = section.strip().split('\n')[:50]  # Limit to first 50 lines
            section_text = '\n'.join(lines)

            # Extract total population
            total_match = re.search(r'total\s+population[:\s]+(\d+(?:,\d+)*)', section_text, re.IGNORECASE)
            total_pop = None
            if total_match:
                total_str = total_match.group(1).replace(',', '').strip()
                if total_str:
                    try:
                        total_pop = int(total_str)
                    except ValueError:
                        pass

            # Extract demographic breakdowns
            breakdowns = []

            # Look for race/ethnicity breakdowns
            race_patterns = [
                (r'Arabs?\s*\.+\s*(\d+(?:,\d+)*)', 'Arabs'),
                (r'Jews?\s*\.+\s*(\d+(?:,\d+)*)', 'Jews'),
                (r'Somalis?\s*\.+\s*(\d+(?:,\d+)*)', 'Somalis'),
                (r'Indians?\s*\.+\s*(\d+(?:,\d+)*)', 'Indians'),
                (r'Europeans?\s*\.+\s*(\d+(?:,\d+)*)', 'Europeans'),
                (r'Chinese\s*\.+\s*(\d+(?:,\d+)*)', 'Chinese'),
                (r'Malays?\s*\.+\s*(\d+(?:,\d+)*)', 'Malays'),
                (r'Natives?\s*\.+\s*(\d+(?:,\d+)*)', 'Natives'),
            ]

            for pattern, category in race_patterns:
                matches = re.finditer(pattern, section_text, re.IGNORECASE)
                for match in matches:
                    count_str = match.group(1).replace(',', '').strip()
                    if not count_str:
                        continue
                    try:
                        count = int(count_str)
                    except ValueError:
                        continue
                    breakdowns.append({
                        "category": category,
                        "count": count,
                        "subcategories": {}
                    })

            if total_pop or breakdowns:
                demo_id = self.generate_id("demo", f"{colony_name}_{self.year}")
                self.entities["demographics"].append({
                    "id": demo_id,
                    "location": colony_name,
                    "year": self.year,
                    "census_date": self._extract_census_date(section_text),
                    "total_population": total_pop,
                    "breakdowns": breakdowns
                })
                break

    def _extract_census_date(self, text: str) -> Optional[str]:
        """Extract census date from text"""
        patterns = [
            r'census\s+(?:taken\s+)?(?:in\s+)?([A-Za-z]+\s+\d{4})',
            r'(\d{1,2}(?:st|nd|rd|th)?\s+[A-Za-z]+\s*,?\s*\d{4})',
            r'([A-Za-z]+\s+\d{1,2}\s*,\s*\d{4})',
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return match.group(1).strip()
        return None

    def extract_people(self, text: str, colony_name: str) -> None:
        """Extract people with positions and salaries"""
        # Find civil establishment sections
        sections = re.split(r'(?:^|\n)(?:CIVIL ESTABLISHMENT|Civil Establishment)', text, flags=re.MULTILINE | re.IGNORECASE)

        for section in sections[1:]:
            lines = section.strip().split('\n')

            for i, line in enumerate(lines[:200]):  # Process first 200 lines
                # Skip empty lines and section headers
                if not line.strip() or line.isupper() or line.startswith('**'):
                    continue

                # Pattern: Name—Title. Salary or Name—Title. £/Rs salary
                # Examples:
                # Governor and Commander-in-Chief—Sir Reginald Stuart Champion, K.C.M.G., O.B.E. £2,500. £1,150 duty allowance.
                # Chief Secretary—W. A. C. Goode. £1,450.

                if '—' in line:
                    parts = line.split('—', 1)
                    if len(parts) == 2:
                        position_title = parts[0].strip()
                        details = parts[1].strip()

                        # Extract person name and additional details
                        name_match = re.match(r'^([A-Za-z\.\s,\'&\(\)]+?)(?:\s+[£Rs]|\.\s*[£Rs]|,\s*[A-Z]|\s*$)', details)
                        if name_match:
                            name = name_match.group(1).strip()

                            # Skip if name is too short or contains only titles
                            if len(name) < 2 or name.startswith('Scale'):
                                continue

                            # Extract salary information
                            salary_info = self._extract_salary(details)

                            # Extract titles and honors
                            titles, honors = self._extract_titles_and_honors(name)
                            clean_name = self._clean_name(name)

                            if clean_name and len(clean_name) > 2:
                                person_id = self.generate_id("person", f"{clean_name}_{colony_name}")

                                person_data = {
                                    "id": person_id,
                                    "name": clean_name,
                                    "titles": titles,
                                    "honors": honors,
                                    "positions": [{
                                        "title": position_title,
                                        "department": self._infer_department(position_title),
                                        "location": colony_name,
                                        "salary": salary_info,
                                        "allowances": self._extract_allowances(details),
                                        "status": "permanent",
                                        "year": self.year
                                    }]
                                }

                                # Check if person already exists
                                existing = next((p for p in self.entities["people"] if p["name"] == clean_name), None)
                                if existing:
                                    existing["positions"].append(person_data["positions"][0])
                                else:
                                    self.entities["people"].append(person_data)

    def _extract_salary(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract salary information"""
        patterns = [
            r'£([\d,]+)(?:\s*[-–]\s*£([\d,]+))?',
            r'Rs\.?\s*([\d,]+)(?:\s+p\.m\.)?',
            r'\$([\d,]+)(?:\s*[-–]\s*\$([\d,]+))?',
        ]

        for pattern in patterns:
            match = re.search(pattern, text)
            if match:
                amount_str = match.group(1).replace(',', '').strip()
                if not amount_str:
                    continue
                try:
                    amount = int(amount_str)
                except ValueError:
                    continue

                if '£' in text[:match.start() + 20]:
                    currency = '£'
                elif 'Rs' in text[:match.start() + 20]:
                    currency = 'Rs'
                else:
                    currency = '$'

                return {
                    "amount": amount,
                    "currency": currency,
                    "period": "annual"
                }
        return None

    def _extract_allowances(self, text: str) -> List[Dict[str, Any]]:
        """Extract allowances"""
        allowances = []
        patterns = [
            (r'(quarters|table\s+money|horse|chair|entertainment|duty)\s+allowance[:\s]+([£Rs$][\d,]+)', 'allowance'),
            (r'([£Rs$][\d,]+)\s+(quarters|table\s+money|horse|chair|entertainment|duty)', 'allowance'),
        ]

        for pattern, _ in patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                allowances.append({
                    "type": match.group(1).lower(),
                    "amount": self._parse_currency_amount(match.group(0)),
                    "currency": self._extract_currency(match.group(0)),
                    "description": match.group(0).strip()
                })

        return allowances

    def _parse_currency_amount(self, text: str) -> Optional[int]:
        """Parse currency amount from text"""
        match = re.search(r'[£Rs$]\s*([\d,]+)', text)
        if match:
            amount_str = match.group(1).replace(',', '').strip()
            if amount_str:
                try:
                    return int(amount_str)
                except ValueError:
                    return None
        return None

    def _extract_currency(self, text: str) -> str:
        """Extract currency symbol"""
        if '£' in text:
            return '£'
        elif 'Rs' in text:
            return 'Rs'
        elif '$' in text:
            return '$'
        return 'Rs'

    def _extract_titles_and_honors(self, name: str) -> Tuple[List[str], List[str]]:
        """Extract titles and honors from name"""
        titles = []
        honors = []

        # Common titles
        title_patterns = [r'\b(Sir|Dame|Rev\.?|Dr\.?|Major|Colonel|Lieut\.-?Col\.?|General|Captain|Capt\.)\b']
        # Common honors
        honor_patterns = [r'\b(K\.?C\.?M\.?G\.?|C\.?B\.?|O\.?B\.?E\.?|G\.?C\.?B\.?|D\.?S\.?O\.?|M\.?C\.?|K\.?B\.?E\.?|C\.?M\.?G\.?|D\.?F\.?C\.?|C\.?B\.?E\.?|K\.?C\.?|O\.?St\.?J\.?|K\.?P\.?M\.?|M\.?B\.?E\.?)\b']

        for match in re.finditer('|'.join(title_patterns), name):
            titles.append(match.group(0))

        for match in re.finditer('|'.join(honor_patterns), name):
            honors.append(match.group(0))

        return titles, honors

    def _clean_name(self, name: str) -> str:
        """Clean up name by removing extra honors and titles"""
        # Remove common abbreviations at the end
        cleaned = re.sub(r',?\s*(?:K\.?C\.?M\.?G\.?|C\.?B\.?|O\.?B\.?E\.?|G\.?C\.?B\.?|D\.?S\.?O\.?|M\.?C\.?|etc\.?)\s*$', '', name)
        return cleaned.strip()

    def _infer_department(self, position: str) -> Optional[str]:
        """Infer department from position title"""
        position_lower = position.lower()

        departments = {
            'education': ['education', 'director of education', 'principal'],
            'medical': ['medical', 'health', 'doctor', 'physician', 'surgeon'],
            'police': ['police', 'commissioner'],
            'public works': ['public works', 'engineer', 'surveyor', 'architect'],
            'treasury': ['treasury', 'accountant', 'financial', 'auditor'],
            'legal': ['attorney', 'solicitor', 'judge', 'magistrate'],
            'agriculture': ['agriculture', 'agricultural'],
            'customs': ['customs', 'collector'],
            'secretariat': ['secretary', 'chief secretary'],
        }

        for dept, keywords in departments.items():
            for keyword in keywords:
                if keyword in position_lower:
                    return dept

        return None

    def extract_institutions(self, text: str, colony_name: str) -> None:
        """Extract institutional information"""
        # Look for council mentions
        council_patterns = [
            (r'(?:Executive|Legislative|Privy)\s+Council', 'council'),
            (r'Supreme Court', 'court'),
            (r'Court of\s+\w+', 'court'),
            (r'Hospital', 'medical'),
            (r'Police Force', 'police_force'),
            (r'Government Guards', 'military_unit'),
        ]

        for pattern, inst_type in council_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                inst_name = match.group(0).strip()
                inst_id = self.generate_id("inst", f"{inst_name}_{colony_name}")

                # Check for composition information
                composition = self._extract_institution_composition(text, inst_name)

                self.entities["institutions"].append({
                    "id": inst_id,
                    "name": inst_name,
                    "type": self._categorize_institution(inst_type),
                    "location": colony_name,
                    "composition": composition,
                    "function": self._infer_institution_function(inst_name, inst_type),
                    "year": self.year
                })

    def _extract_institution_composition(self, text: str, inst_name: str) -> Dict[str, Any]:
        """Extract composition details of institution"""
        return {
            "description": f"Members of {inst_name}",
            "member_count": None,
            "members": []
        }

    def _categorize_institution(self, inst_type: str) -> str:
        """Categorize institution type"""
        type_map = {
            'council': 'executive_council',
            'court': 'court',
            'medical': 'medical',
            'police_force': 'police_force',
            'military_unit': 'military_unit',
        }
        return type_map.get(inst_type, inst_type)

    def _infer_institution_function(self, name: str, inst_type: str) -> str:
        """Infer institution function"""
        if 'executive' in name.lower():
            return "Executive governance and policy advice"
        elif 'legislative' in name.lower():
            return "Legislative authority and law-making"
        elif 'court' in name.lower():
            return "Judicial authority and dispute resolution"
        elif 'hospital' in name.lower():
            return "Medical services and healthcare"
        elif 'police' in name.lower():
            return "Law enforcement and public safety"
        return "Administrative function"

    def extract_economic_data(self, text: str, colony_name: str) -> None:
        """Extract economic and trade information"""
        # Find PUBLIC FINANCE section
        finance_match = re.search(r'(?:PUBLIC\s+FINANCE|PUBLIC FINANCE)(.*?)(?=\n[A-Z][A-Z\s]+$|\Z)', text, re.MULTILINE | re.DOTALL | re.IGNORECASE)

        if finance_match:
            finance_text = finance_match.group(1)

            # Extract revenue and expenditure data
            # Look for tables or lists with numerical data
            patterns = [
                (r'Revenue[:\s]+(?:Rs\.|£|\$)?\s*([\d,]+)', 'revenue'),
                (r'Expenditure[:\s]+(?:Rs\.|£|\$)?\s*([\d,]+)', 'expenditure'),
                (r'Imports[:\s]+(?:Rs\.|£|\$)?\s*([\d,\.]+)', 'trade_import'),
                (r'Exports[:\s]+(?:Rs\.|£|\$)?\s*([\d,\.]+)', 'trade_export'),
            ]

            for pattern, data_type in patterns:
                for match in re.finditer(pattern, finance_text, re.IGNORECASE):
                    amount = match.group(1).strip().replace(',', '')
                    if not amount:
                        continue
                    try:
                        value = float(amount)
                    except ValueError:
                        continue

                    econ_id = self.generate_id("econ", f"{data_type}_{colony_name}_{self.year}")
                    self.entities["economic_data"].append({
                        "id": econ_id,
                        "type": data_type,
                        "location": colony_name,
                        "year": self.year,
                        "data": {
                            "category": data_type.replace('_', ' ').title(),
                            "value": value,
                            "currency": self._infer_currency_from_context(finance_text),
                            "unit": "currency"
                        },
                        "notes": f"Extracted from {data_type} data for {colony_name} in {self.year}"
                    })

    def _infer_currency_from_context(self, text: str) -> str:
        """Infer currency from context"""
        if 'Rs' in text or 'rupee' in text.lower():
            return 'Rs'
        elif '£' in text or 'pound' in text.lower():
            return '£'
        elif '$' in text:
            return '$'
        return 'Rs'

    def extract_infrastructure(self, text: str, colony_name: str) -> None:
        """Extract infrastructure information"""
        infrastructure_keywords = {
            'railway': [r'railway', r'rail\s+route'],
            'telegraph': [r'telegraph', r'wireless'],
            'postal_route': [r'postal\s+route', r'mail\s+service'],
            'dock': [r'dock', r'wharf'],
            'harbor': [r'harbour', r'harbor', r'port'],
            'road': [r'road', r'highway'],
            'bridge': [r'bridge'],
            'water_works': [r'water\s+works', r'waterworks'],
        }

        for inf_type, patterns in infrastructure_keywords.items():
            for pattern in patterns:
                for match in re.finditer(pattern, text, re.IGNORECASE):
                    inf_name = match.group(0).strip()
                    inf_id = self.generate_id("infra", f"{inf_type}_{colony_name}")

                    # Extract specifications if available
                    context_start = max(0, match.start() - 200)
                    context_end = min(len(text), match.end() + 200)
                    context = text[context_start:context_end]

                    self.entities["infrastructure"].append({
                        "id": inf_id,
                        "type": inf_type,
                        "name": inf_name,
                        "location": colony_name,
                        "specifications": self._extract_infrastructure_specs(context),
                        "connections": [],
                        "year": self.year
                    })

    def _extract_infrastructure_specs(self, text: str) -> Dict[str, Any]:
        """Extract infrastructure specifications"""
        specs = {}

        # Look for length/distance
        length_match = re.search(r'(\d+(?:\.\d+)?)\s+(?:miles|kilometers?|km)', text, re.IGNORECASE)
        if length_match:
            specs["length"] = {
                "value": float(length_match.group(1)),
                "unit": "miles" if "miles" in length_match.group(0).lower() else "km"
            }

        # Look for cost
        cost_match = re.search(r'[£Rs$]\s*([\d,]+)', text)
        if cost_match:
            cost_str = cost_match.group(1).replace(',', '').strip()
            if cost_str:
                try:
                    specs["construction_cost"] = {
                        "value": int(cost_str),
                        "currency": self._extract_currency(text)
                    }
                except ValueError:
                    pass

        # Look for stations
        stations_match = re.search(r'(\d+)\s+stations?', text, re.IGNORECASE)
        if stations_match:
            try:
                specs["stations"] = int(stations_match.group(1))
            except ValueError:
                pass

        return specs

    def extract_places(self, text: str, colony_name: str) -> None:
        """Extract geographic entities"""
        # First, add the colony itself
        place_id = self.generate_id("place", colony_name)

        description = ""
        area = None
        coordinates = None

        # Extract initial description
        desc_match = re.search(r'(?:^|\n)(?:SITUATION AND AREA|Situation and Area)(.*?)(?=\n(?:[A-Z][A-Z\s]+|$))', text, re.MULTILINE | re.IGNORECASE | re.DOTALL)
        if desc_match:
            description = desc_match.group(1)[:500].strip()
            coordinates = self.extract_coordinates(description)
            area = self.extract_area(description)

        self.entities["places"].append({
            "id": place_id,
            "name": colony_name,
            "modern_name": colony_name,
            "type": "colony",
            "coordinates": coordinates,
            "area": area,
            "description": description[:300] if description else "",
            "parent_location": None,
            "year": self.year
        })

        # Extract other geographic features mentioned
        geo_features = {
            'island': r'island\s+(?:of\s+)?([A-Z][A-Za-z\s]+)',
            'river': r'river\s+([A-Z][A-Za-z\s]+)',
            'mountain': r'(?:mountain|mount|peak)\s+(?:of\s+)?([A-Z][A-Za-z\s]+)',
            'bay': r'bay\s+(?:of\s+)?([A-Z][A-Za-z\s]+)',
            'harbor': r'(?:harbour|harbor)\s+(?:of\s+)?([A-Z][A-Za-z\s]+)',
            'city': r'(?:city|town)\s+(?:of\s+)?([A-Z][A-Za-z\s]+)',
        }

        for feat_type, pattern in geo_features.items():
            for match in re.finditer(pattern, text):
                feat_name = match.group(1).strip()
                if len(feat_name) > 1 and feat_name not in colony_name:
                    feat_id = self.generate_id("place", f"{feat_type}_{feat_name}_{colony_name}")
                    self.entities["places"].append({
                        "id": feat_id,
                        "name": feat_name,
                        "type": feat_type,
                        "parent_location": place_id,
                        "description": "",
                        "year": self.year
                    })

    def process_colony_file(self, filepath: str) -> None:
        """Process a single colony file"""
        colony_name = Path(filepath).stem.replace('_', ' ')

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read()

            # Extract all entity types
            self.extract_places(text, colony_name)
            self.extract_population(text, colony_name)
            self.extract_people(text, colony_name)
            self.extract_institutions(text, colony_name)
            self.extract_economic_data(text, colony_name)
            self.extract_infrastructure(text, colony_name)

            self.processed_files.append(colony_name)

        except Exception as e:
            print(f"Error processing {filepath}: {e}")

    def build_relationships(self) -> None:
        """Build relationships between entities"""
        # LOCATED_IN relationships between places and colonies
        colonies = {p["id"]: p["name"] for p in self.entities["places"] if p["type"] == "colony"}

        for place in self.entities["places"]:
            if place.get("parent_location"):
                parent = next((p for p in self.entities["places"] if p["id"] == place.get("parent_location")), None)
                if parent:
                    self.relationships.append({
                        "source_id": place["id"],
                        "relationship_type": "LOCATED_IN",
                        "target_id": parent["id"],
                        "properties": {"year": self.year}
                    })

        # GOVERNED_BY relationships
        for person in self.entities["people"]:
            for position in person["positions"]:
                colony_id = next((p["id"] for p in self.entities["places"] if p["name"] == position["location"]), None)
                if colony_id:
                    self.relationships.append({
                        "source_id": person["id"],
                        "relationship_type": "GOVERNED_BY",
                        "target_id": colony_id,
                        "properties": {
                            "year": self.year,
                            "position": position["title"]
                        }
                    })

    def generate_json(self) -> Dict[str, Any]:
        """Generate final JSON structure"""
        return {
            "metadata": {
                "year": self.year,
                "source_directory": self.source_dir,
                "extraction_date": datetime.now().isoformat(),
                "processing_notes": f"Comprehensive extraction from {len(self.processed_files)} colony files",
                "colonies_processed": sorted(self.processed_files)
            },
            "entities": self.entities,
            "relationships": self.relationships
        }

    def extract(self) -> None:
        """Main extraction process"""
        # Find all colony files
        colony_files = sorted(glob.glob(os.path.join(self.source_dir, "*.md")))

        print(f"Found {len(colony_files)} colony files")

        # Process each file
        for filepath in colony_files:
            print(f"Processing: {Path(filepath).stem}")
            self.process_colony_file(filepath)

        # Build relationships
        self.build_relationships()

        # Save output
        os.makedirs(self.output_dir, exist_ok=True)
        output_file = os.path.join(self.output_dir, "1950_extracted.json")

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.generate_json(), f, indent=2, ensure_ascii=False)

        print(f"\nExtraction complete!")
        print(f"Output saved to: {output_file}")

        # Generate report
        self.print_report()

    def print_report(self) -> None:
        """Print extraction report"""
        print("\n" + "="*60)
        print("EXTRACTION REPORT: COLONIAL OFFICE LIST 1950")
        print("="*60)

        print(f"\nColonies Processed: {len(self.processed_files)}")
        print("Colonies:")
        for colony in sorted(self.processed_files):
            print(f"  - {colony}")

        print(f"\nEntity Counts by Type:")
        print(f"  Places: {len(self.entities['places'])}")
        print(f"  People: {len(self.entities['people'])}")
        print(f"  Institutions: {len(self.entities['institutions'])}")
        print(f"  Economic Data: {len(self.entities['economic_data'])}")
        print(f"  Infrastructure: {len(self.entities['infrastructure'])}")
        print(f"  Demographics: {len(self.entities['demographics'])}")
        print(f"  Events: {len(self.entities['events'])}")
        print(f"  Total Entities: {sum(len(v) for v in self.entities.values())}")

        print(f"\nRelationships: {len(self.relationships)}")

        print("\n" + "="*60)

if __name__ == "__main__":
    source_dir = "/home/user/colonial_office_list/output_2/1950_manual_parsed/"
    output_dir = "/home/user/colonial_office_list/knowledge_graph_extracts/"

    extractor = ColonialOfficeExtractor(source_dir, output_dir)
    extractor.extract()
