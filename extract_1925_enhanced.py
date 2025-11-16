#!/usr/bin/env python3
"""
Enhanced extraction with better institutional and infrastructure data.
"""

import json
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional

class EnhancedColonialExtractor:
    def __init__(self, source_dir: str, output_dir: str):
        self.source_dir = Path(source_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Entity storage
        self.places = []
        self.people = []
        self.institutions = []
        self.economic_data = []
        self.infrastructure = []
        self.demographics = []
        self.events = []
        self.relationships = []

        # ID tracking
        self.entity_counter = {'place': 0, 'person': 0, 'institution': 0,
                               'economic': 0, 'infrastructure': 0, 'demographic': 0, 'event': 0}

        self.colonies_processed = []
        self.year = "1925"

    def generate_id(self, entity_type: str, name: str) -> str:
        """Generate unique ID for entity."""
        self.entity_counter[entity_type] += 1
        safe_name = re.sub(r'[^a-zA-Z0-9]', '', str(name)[:20])
        return f"{entity_type}_{self.year}_{safe_name[:10]}_{self.entity_counter[entity_type]}"

    def extract_governor_list(self, text: str, colony_name: str) -> List[Dict]:
        """Extract Governor/Administrator lists."""
        people_list = []

        # Pattern: Title + Name + Date
        gov_pattern = r"(?:Sir|Mr\.?)\s+([A-Z][a-z\s\.]+?),?\s+(?:K\.?C\.?M\.?G\.?|C\.?B\.?|D\.?S\.?O\.?|Major|Colonel|General|Lord|Justice|Rev\.?).*?\s+\.+\s+(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4})"

        matches = re.finditer(gov_pattern, text, re.IGNORECASE)
        for match in matches:
            name = match.group(1).strip()
            date = match.group(2).strip()

            person_id = self.generate_id('person', name)
            person = {
                "id": person_id,
                "name": name,
                "positions": [{
                    "title": "Governor",
                    "location": colony_name,
                    "year": self.year,
                    "appointment_date": date
                }],
                "year": self.year
            }
            people_list.append(person)

        return people_list

    def extract_administrative_positions(self, text: str, colony_name: str) -> List[Dict]:
        """Extract administrative positions (Colonial Secretary, Attorney General, etc.)."""
        people_list = []

        # Pattern for administrative positions
        admin_titles = [
            "Colonial Secretary", "Attorney General", "Solicitor General",
            "Chief Justice", "Auditor", "Treasurer", "Surveyor",
            "Director", "Inspector", "Superintendent", "Commissioner",
            "Magistrate", "Clerk", "Registrar", "Archivist"
        ]

        for title in admin_titles:
            # Pattern: [Title].... [Name]
            pattern = rf"{title}.*?\.{{2,}}\s+([A-Z][a-z\s\.]+?)(?:\n|,|;)"
            matches = re.finditer(pattern, text, re.IGNORECASE)

            for match in matches:
                name_str = match.group(1).strip()
                # Clean up name (remove extra whitespace and punctuation)
                names = name_str.split(',')[0].strip()

                if names and len(names) > 2 and not any(c.isdigit() for c in names):
                    person_id = self.generate_id('person', names)
                    person = {
                        "id": person_id,
                        "name": names,
                        "positions": [{
                            "title": title,
                            "location": colony_name,
                            "year": self.year,
                            "status": "permanent"
                        }],
                        "year": self.year
                    }
                    people_list.append(person)

        return people_list

    def extract_councils(self, text: str, colony_name: str) -> List[Dict]:
        """Extract council structures."""
        institutions = []

        council_patterns = [
            (r"Executive Council.*?(?:consists of|composed of|members?):\s*([^.]+)", "executive_council"),
            (r"Legislative Council.*?(?:consists of|composed of|members?):\s*([^.]+)", "legislative_council"),
            (r"Privy Council.*?(?:consists of|composed of|members?):\s*([^.]+)", "privy_council"),
        ]

        for pattern, council_type in council_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                description = match.group(1)[:300]
                institution_id = self.generate_id('institution', f"{colony_name}_{council_type}")
                institution = {
                    "id": institution_id,
                    "name": f"{council_type.replace('_', ' ').title()} of {colony_name}",
                    "type": council_type,
                    "location": colony_name,
                    "composition": {
                        "description": description
                    },
                    "year": self.year
                }
                institutions.append(institution)

        return institutions

    def extract_infrastructure(self, text: str, colony_name: str) -> List[Dict]:
        """Extract infrastructure details (railways, telegraph, dock, etc.)."""
        infrastructure_list = []

        # Railway patterns
        railway_pattern = r"(?:railway|rail line|line).*?(?:length|distance|route).*?([0-9]+(?:\.[0-9]+)?)\s*miles?"
        matches = re.finditer(railway_pattern, text, re.IGNORECASE | re.DOTALL)
        for idx, match in enumerate(matches):
            length_value = float(match.group(1))
            infra_id = self.generate_id('infrastructure', f"{colony_name}_railway{idx}")
            infrastructure_list.append({
                "id": infra_id,
                "type": "railway",
                "location": colony_name,
                "name": f"Railway Line {idx + 1}",
                "specifications": {
                    "length": {"value": length_value, "unit": "miles"}
                },
                "year": self.year
            })

        # Telegraph patterns
        telegraph_pattern = r"telegraph.*?([0-9]+(?:\.[0-9]+)?)\s*miles?"
        match = re.search(telegraph_pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            length_value = float(match.group(1))
            infra_id = self.generate_id('infrastructure', f"{colony_name}_telegraph")
            infrastructure_list.append({
                "id": infra_id,
                "type": "telegraph",
                "location": colony_name,
                "name": "Telegraph System",
                "specifications": {
                    "length": {"value": length_value, "unit": "miles"}
                },
                "year": self.year
            })

        # Dock/Harbor patterns
        dock_pattern = r"dock.*?(?:capacity|area|accommodation).*?([0-9]+(?:,[0-9]{3})*)\s*(?:sq\.?\s*ft|acres|vessels)"
        match = re.search(dock_pattern, text, re.IGNORECASE | re.DOTALL)
        if match:
            infra_id = self.generate_id('infrastructure', f"{colony_name}_dock")
            infrastructure_list.append({
                "id": infra_id,
                "type": "dock",
                "location": colony_name,
                "name": "Main Dock/Harbor",
                "year": self.year
            })

        return infrastructure_list[:10]  # Limit to avoid excessive data

    def extract_financial_table(self, text: str, colony_name: str) -> List[Dict]:
        """Extract financial data from structured tables."""
        economic_list = []

        # Revenue pattern from tables
        revenue_pattern = r"Revenue.*?(\d{1,2}\d{1,2}[-/]\d{1,2}\d{1,2})\s*[|:]?\s*([0-9,]+)"
        matches = re.finditer(revenue_pattern, text, re.IGNORECASE)

        for match in matches:
            year_range = match.group(1)
            value_str = match.group(2).replace(',', '')
            try:
                value = float(value_str)
                econ_id = self.generate_id('economic', f"{colony_name}_revenue")
                economic_list.append({
                    "id": econ_id,
                    "type": "revenue",
                    "location": colony_name,
                    "year": self.year,
                    "data": {
                        "category": f"Revenue {year_range}",
                        "value": value,
                        "currency": "Rs."
                    }
                })
            except ValueError:
                pass

        # Import/Export values
        trade_pattern = r"(?:imports?|exports?)\s*.*?([0-9,]+(?:\.[0-9]+)?)"
        matches = re.finditer(trade_pattern, text, re.IGNORECASE)
        count = 0
        for match in matches:
            if count < 5:  # Limit
                value_str = match.group(1).replace(',', '')
                try:
                    value = float(value_str)
                    econ_id = self.generate_id('economic', f"{colony_name}_trade{count}")
                    economic_list.append({
                        "id": econ_id,
                        "type": "trade_import",
                        "location": colony_name,
                        "year": self.year,
                        "data": {
                            "value": value,
                            "currency": "Rs."
                        }
                    })
                    count += 1
                except ValueError:
                    pass

        return economic_list

    def extract_major_events(self, text: str, colony_name: str) -> List[Dict]:
        """Extract major historical events and dates."""
        events_list = []

        # Pattern: significant date + description
        significant_events = [
            r"(Treaty of [^.]+\.\s*\d{4})",
            r"((?:ceded|captured|established|founded|discovered).*?\d{4})",
            r"(\d{1,2}(?:st|nd|rd|th)?\s+(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{4}[^.]*\.)",
        ]

        for pattern in significant_events:
            matches = re.finditer(pattern, text, re.IGNORECASE | re.DOTALL)
            for match in matches:
                description = match.group(0)[:250]
                event_id = self.generate_id('event', f"{colony_name}_{description[:20]}")
                events_list.append({
                    "id": event_id,
                    "description": description,
                    "locations": [],
                    "year_mentioned": self.year
                })

        return events_list[:20]  # Limit to avoid noise

    def extract_from_colony_file(self, colony_name: str, content: str):
        """Main extraction method for each colony."""

        # Extract coordinates and area
        coords = self._extract_coordinates(content)
        area = self._extract_area(content)

        # Place entry
        place_id = self.generate_id('place', colony_name)
        place = {
            "id": place_id,
            "name": colony_name,
            "type": "colony",
            "year": self.year
        }
        if coords:
            place["coordinates"] = coords
        if area:
            place["area"] = area

        desc_match = re.search(r'^[^.!?]*[.!?]', content, re.MULTILINE)
        if desc_match:
            place["description"] = desc_match.group(0)[:500]

        self.places.append(place)

        # Extract people (governors, administrators)
        governors = self.extract_governor_list(content, colony_name)
        self.people.extend(governors)

        admin_staff = self.extract_administrative_positions(content, colony_name)
        self.people.extend(admin_staff)

        # Extract institutions
        councils = self.extract_councils(content, colony_name)
        self.institutions.extend(councils)

        # Extract infrastructure
        infra = self.extract_infrastructure(content, colony_name)
        self.infrastructure.extend(infra)

        # Extract economic data
        econ = self.extract_financial_table(content, colony_name)
        self.economic_data.extend(econ)

        # Extract events
        events = self.extract_major_events(content, colony_name)
        self.events.extend(events)

        # Extract demographics
        demo = self._extract_demographics(content, colony_name, place_id)
        if demo:
            self.demographics.append(demo)

        # Build relationships
        if governors:
            for gov in governors:
                self.relationships.append({
                    "source_id": gov["id"],
                    "relationship_type": "GOVERNED_BY",
                    "target_id": place_id,
                    "properties": {"year": self.year}
                })

    def _extract_coordinates(self, text: str) -> Optional[Dict]:
        """Extract latitude/longitude."""
        patterns = [
            r"([0-9]{1,3})°\s*([0-9]{1,2})'\s*([NSEWnsew]\.?)",
            r"([0-9]{1,3})°\s*([0-9]{1,2})′\s*([NSEWnsew]\.?)",
        ]

        coords = {}
        for pattern in patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                degree, minute, direction = match
                coord_str = f"{degree}° {minute}' {direction}"
                if direction.upper().startswith(('N', 'S')):
                    if 'latitude' not in coords:
                        coords['latitude'] = coord_str
                else:
                    if 'longitude' not in coords:
                        coords['longitude'] = coord_str

        return coords if coords else None

    def _extract_area(self, text: str) -> Optional[Dict]:
        """Extract area measurements."""
        patterns = [
            (r"([0-9,]+(?:\.[0-9]+)?)\s*square\s+miles", "square miles"),
            (r"([0-9,]+(?:\.[0-9]+)?)\s*square\s+feet", "square feet"),
            (r"([0-9,]+(?:\.[0-9]+)?)\s*acres", "acres"),
        ]

        for pattern, unit in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value_str = match.group(1).replace(',', '')
                try:
                    return {"value": float(value_str), "unit": unit}
                except ValueError:
                    pass
        return None

    def _extract_demographics(self, text: str, colony_name: str, place_id: str) -> Optional[Dict]:
        """Extract demographic data."""
        census_pattern = r"[Cc]ensus\s+(?:of\s+)?(\d{4})"
        total_pattern = r"[Tt]otal.*?population.*?(\d+(?:,\d{3})*)"

        census_year = None
        match = re.search(census_pattern, text)
        if match:
            census_year = match.group(1)

        total_pop = None
        match = re.search(total_pattern, text, re.IGNORECASE)
        if match:
            pop_str = match.group(1).replace(',', '')
            try:
                total_pop = int(pop_str)
            except ValueError:
                pass

        if total_pop or census_year:
            demo_id = self.generate_id('demographic', colony_name)
            return {
                "id": demo_id,
                "location": colony_name,
                "year": self.year,
                "census_date": census_year,
                "total_population": total_pop
            }

        return None

    def process_all_colonies(self):
        """Process all colony files."""
        colony_files = sorted(self.source_dir.glob("*.md"))

        for colony_file in colony_files:
            try:
                colony_name = colony_file.stem
                content = colony_file.read_text(encoding='utf-8')

                self.extract_from_colony_file(colony_name, content)
                self.colonies_processed.append(colony_name)

                print(f"Enhanced extraction: {colony_name}")
            except Exception as e:
                print(f"Error processing {colony_file.name}: {e}")

    def save_output(self, output_file: str):
        """Save to JSON."""
        output_data = {
            "metadata": {
                "year": self.year,
                "source_directory": str(self.source_dir),
                "extraction_date": datetime.utcnow().isoformat() + "Z",
                "processing_notes": "Enhanced extraction with institutional, administrative, and infrastructure data",
                "colonies_processed": self.colonies_processed
            },
            "entities": {
                "places": self.places,
                "people": self.people,
                "institutions": self.institutions,
                "economic_data": self.economic_data,
                "infrastructure": self.infrastructure,
                "demographics": self.demographics,
                "events": self.events
            },
            "relationships": self.relationships
        }

        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        return output_data

    def generate_report(self) -> str:
        """Generate statistics report."""
        return f"""
ENHANCED EXTRACTION REPORT - 1925 COLONIAL OFFICE LIST
========================================================

EXTRACTION DATE: {datetime.utcnow().isoformat()}
YEAR: {self.year}
SOURCE: {self.source_dir}
COLONIES PROCESSED: {len(self.colonies_processed)}

ENTITY COUNTS:
- Geographic Places: {len(self.places)}
- People (Administrative): {len(self.people)}
- Institutions (Councils, Courts, Departments): {len(self.institutions)}
- Economic Data Records: {len(self.economic_data)}
- Infrastructure (Railways, Docks, Telegraph): {len(self.infrastructure)}
- Demographics: {len(self.demographics)}
- Historical Events: {len(self.events)}
- Relationships: {len(self.relationships)}

TOTAL ENTITIES: {len(self.places) + len(self.people) + len(self.institutions) + len(self.economic_data) + len(self.infrastructure) + len(self.demographics) + len(self.events)}

IMPROVEMENTS OVER BASIC EXTRACTION:
- Better extraction of Governor and Administrator names with dates
- Administrative position parsing (Colonial Secretary, Attorney General, etc.)
- Council and institutional structures
- Infrastructure details (railways, telegraph systems, docks)
- Financial table parsing
- Improved event extraction
- Administrative-geographic relationships
"""


def main():
    """Main workflow."""
    source_dir = "/home/user/colonial_office_list/output_2/1925_manual_parsed"
    output_dir = "/home/user/colonial_office_list/knowledge_graph_extracts"
    output_file = f"{output_dir}/1925_enhanced_extracted.json"

    extractor = EnhancedColonialExtractor(source_dir, output_dir)

    print("Starting Enhanced 1925 Extraction...")
    print("=" * 70)

    extractor.process_all_colonies()

    output_data = extractor.save_output(output_file)
    report = extractor.generate_report()

    print(report)

    # Save report
    report_file = f"{output_dir}/1925_enhanced_extraction_report.txt"
    with open(report_file, 'w') as f:
        f.write(report)

    print(f"Output: {output_file}")
    print(f"Report: {report_file}")

    return output_data


if __name__ == "__main__":
    main()
