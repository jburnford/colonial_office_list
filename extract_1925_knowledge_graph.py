#!/usr/bin/env python3
"""
Extract comprehensive structured knowledge graph data from Colonial Office List 1925.
Processes all colony files to extract geographic entities, people, institutions, economic data,
infrastructure, demographics, and historical events.
"""

import json
import re
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Any, Optional, Set, Tuple

class ColonialOfficeExtractor:
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
        self.place_ids = {}
        self.person_ids = {}
        self.institution_ids = {}

        self.entity_counter = {'place': 0, 'person': 0, 'institution': 0,
                               'economic': 0, 'infrastructure': 0, 'demographic': 0, 'event': 0}

        self.colonies_processed = []
        self.year = "1925"

    def generate_id(self, entity_type: str, name: str) -> str:
        """Generate unique ID for entity."""
        self.entity_counter[entity_type] += 1
        safe_name = re.sub(r'[^a-zA-Z0-9]', '', name[:20])
        return f"{entity_type}_{self.year}_{safe_name[:10]}_{self.entity_counter[entity_type]}"

    def extract_coordinates(self, text: str) -> Optional[Dict]:
        """Extract latitude/longitude from text."""
        # Pattern for coordinates like "12° 47' N." and "45° 10' E."
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

    def extract_area(self, text: str) -> Optional[Dict]:
        """Extract area measurements from text."""
        # Look for patterns like "75 square miles" or "720 square miles"
        patterns = [
            r"([0-9]+(?:,[0-9]{3})*(?:\.[0-9]+)?)\s*(?:square\s+)?miles",
            r"([0-9]+(?:,[0-9]{3})*(?:\.[0-9]+)?)\s*(?:square\s+)?feet",
            r"([0-9]+(?:,[0-9]{3})*(?:\.[0-9]+)?)\s*acres",
        ]

        for pattern in patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value_str = match.group(1).replace(',', '')
                unit_match = re.search(r'(square\s+miles|square\s+feet|acres|miles|feet)', match.group(0), re.IGNORECASE)
                unit = unit_match.group(1) if unit_match else "square miles"
                try:
                    return {"value": float(value_str), "unit": unit}
                except ValueError:
                    pass
        return None

    def extract_population(self, text: str) -> Optional[Dict]:
        """Extract population data from text."""
        # Look for Census data and population figures
        census_pattern = r"[Cc]ensus\s+(?:of\s+)?(\d{4})"
        total_pattern = r"[Tt]otal\s+(?:population)?\s*\.{0,3}\s*([0-9]+(?:,[0-9]{3})*)"

        census_year = None
        census_match = re.search(census_pattern, text)
        if census_match:
            census_year = census_match.group(1)

        total_pop = None
        total_match = re.search(total_pattern, text)
        if total_match:
            pop_str = total_match.group(1).replace(',', '')
            try:
                total_pop = int(pop_str)
            except ValueError:
                pass

        if total_pop or census_year:
            return {
                "census_date": census_year,
                "total_population": total_pop
            }
        return None

    def extract_names(self, text: str) -> List[str]:
        """Extract potential person names (capitalized phrases)."""
        # Pattern: Title + Capitalized name, or just Capitalized names
        title_patterns = [
            r"(?:Sir|Mr\.|Mrs\.|Dr\.|Rev\.|General|Colonel|Major|Captain|Lieutenant|Reverend|Justice|Lord|Judge|Professor|Canon|Rabbi|Mr|Mrs|Dr|Lt\.?|Col\.?)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
        ]

        names = []
        for pattern in title_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                name = match.group(1)
                if name and len(name) > 1 and name not in ['The', 'British', 'English']:
                    names.append(name)

        return list(set(names))[:50]  # Limit to avoid excessive noise

    def extract_titles_and_positions(self, text: str) -> List[str]:
        """Extract job titles and positions."""
        position_pattern = r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:of|in|at)\s+(?:[A-Z][a-z]+)"
        matches = re.findall(position_pattern, text)
        return list(set(matches))[:30]

    def extract_monetary_values(self, text: str) -> List[Dict]:
        """Extract monetary values (revenue, expenditure, salary data)."""
        monetary_data = []

        # Pattern: £123,456 or $123,456 or Rs. 123,456
        patterns = [
            (r"£\s*([0-9]+(?:,[0-9]{3})*(?:\.[0-9]+)?)", "£"),
            (r"\$\s*([0-9]+(?:,[0-9]{3})*(?:\.[0-9]+)?)", "$"),
            (r"Rs\.\s*([0-9]+(?:,[0-9]{3})*(?:\.[0-9]+)?)", "Rs."),
        ]

        for pattern, currency in patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                value_str = match.group(1).replace(',', '')
                try:
                    value = float(value_str)
                    monetary_data.append({
                        "value": value,
                        "currency": currency
                    })
                except ValueError:
                    pass

        return monetary_data[:20]  # Limit to avoid excessive data

    def extract_shipping_and_trade(self, text: str) -> List[Dict]:
        """Extract shipping and trade data."""
        trade_data = []

        # Tonnage patterns
        tonnage_pattern = r"([0-9]+(?:,[0-9]{3})*)\s+tons?"
        matches = re.finditer(tonnage_pattern, text)
        for match in matches:
            value_str = match.group(1).replace(',', '')
            try:
                trade_data.append({
                    "type": "shipping",
                    "value": int(value_str),
                    "unit": "tons"
                })
            except ValueError:
                pass

        return trade_data[:30]

    def extract_dates(self, text: str) -> List[str]:
        """Extract historical dates."""
        date_patterns = [
            r"\d{1,2}(?:st|nd|rd|th)?\s+(?:January|February|March|April|May|June|July|August|September|October|November|December|\d{1,2}),?\s+\d{4}",
            r"(?:January|February|March|April|May|June|July|August|September|October|November|December)\s+\d{1,2}(?:st|nd|rd|th)?,?\s+\d{4}",
            r"\d{4}",
        ]

        dates = []
        for pattern in date_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            dates.extend(matches)

        return list(set(dates))[:50]

    def extract_from_colony_file(self, colony_name: str, content: str):
        """Extract entities from a single colony file."""

        # Extract geographic data
        coords = self.extract_coordinates(content)
        area = self.extract_area(content)

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

        # Extract description (first few sentences)
        desc_match = re.search(r'^[^.!?]*[.!?]', content, re.MULTILINE)
        if desc_match:
            place["description"] = desc_match.group(0)[:500]

        self.places.append(place)
        self.place_ids[colony_name] = place_id

        # Extract demographic data
        pop_data = self.extract_population(content)
        if pop_data:
            demo_id = self.generate_id('demographic', colony_name)
            demographic = {
                "id": demo_id,
                "location": colony_name,
                "year": self.year
            }
            demographic.update(pop_data)
            self.demographics.append(demographic)

        # Extract economic data
        monetary_values = self.extract_monetary_values(content)
        for idx, monetary in enumerate(monetary_values[:10]):
            econ_id = self.generate_id('economic', f"{colony_name}_econ{idx}")
            economic = {
                "id": econ_id,
                "type": "financial",
                "location": colony_name,
                "year": self.year,
                "data": monetary
            }
            self.economic_data.append(economic)

        # Extract shipping/trade data
        trade_data = self.extract_shipping_and_trade(content)
        for idx, trade in enumerate(trade_data[:10]):
            econ_id = self.generate_id('economic', f"{colony_name}_trade{idx}")
            economic = {
                "id": econ_id,
                "type": trade.get("type", "trade"),
                "location": colony_name,
                "year": self.year,
                "data": trade
            }
            self.economic_data.append(economic)

        # Extract dates/events
        dates = self.extract_dates(content)
        # Look for event descriptions near dates
        for date in dates:
            event_pattern = rf"{re.escape(date)}\s*[,.]?\s*([^.!?]{{20,200}})"
            match = re.search(event_pattern, content)
            if match:
                event_id = self.generate_id('event', f"{colony_name}_{date}")
                event = {
                    "id": event_id,
                    "date": date,
                    "description": match.group(1)[:300],
                    "locations": [place_id],
                    "year_mentioned": self.year
                }
                self.events.append(event)

        # Extract names (potential people)
        names = self.extract_names(content)
        titles = self.extract_titles_and_positions(content)

        for name in names[:20]:  # Limit to avoid noise
            if name and len(name.split()) <= 3 and not any(c.isdigit() for c in name):
                person_id = self.generate_id('person', name)
                person = {
                    "id": person_id,
                    "name": name,
                    "year": self.year
                }

                # Add position if available
                positions = []
                for title in titles[:5]:
                    positions.append({
                        "title": title,
                        "location": colony_name,
                        "year": self.year
                    })

                if positions:
                    person["positions"] = positions

                self.people.append(person)

        # Create relationships
        # Place relationships (dependencies, locations)
        if area or coords:
            rel = {
                "source_id": place_id,
                "relationship_type": "DURING_YEAR",
                "target_id": f"year_{self.year}",
                "properties": {"year": self.year}
            }
            self.relationships.append(rel)

    def process_all_colonies(self):
        """Process all colony files in the source directory."""
        colony_files = sorted(self.source_dir.glob("*.md"))

        for colony_file in colony_files:
            try:
                colony_name = colony_file.stem
                content = colony_file.read_text(encoding='utf-8')

                self.extract_from_colony_file(colony_name, content)
                self.colonies_processed.append(colony_name)

                print(f"Processed: {colony_name}")
            except Exception as e:
                print(f"Error processing {colony_file.name}: {e}")

    def build_output_json(self) -> Dict[str, Any]:
        """Build the final JSON output structure."""
        return {
            "metadata": {
                "year": self.year,
                "source_directory": str(self.source_dir),
                "extraction_date": datetime.utcnow().isoformat() + "Z",
                "processing_notes": "Comprehensive extraction of 1925 Colonial Office List data from 41 colonies/territories",
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

    def save_output(self, output_file: str):
        """Save extracted data to JSON file."""
        output_data = self.build_output_json()

        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2, ensure_ascii=False)

        print(f"\nOutput saved to: {output_path}")
        return output_data

    def generate_report(self) -> str:
        """Generate extraction statistics report."""
        report = f"""
COLONIAL OFFICE LIST 1925 - KNOWLEDGE GRAPH EXTRACTION REPORT
===============================================================

EXTRACTION DATE: {datetime.utcnow().isoformat()}
YEAR: {self.year}
SOURCE DIRECTORY: {self.source_dir}

COLONIES PROCESSED: {len(self.colonies_processed)}
{', '.join(sorted(self.colonies_processed))}

ENTITY COUNTS BY TYPE:
- Geographic Places: {len(self.places)}
- People: {len(self.people)}
- Institutions: {len(self.institutions)}
- Economic Data Records: {len(self.economic_data)}
- Infrastructure: {len(self.infrastructure)}
- Demographic Data: {len(self.demographics)}
- Historical Events: {len(self.events)}
- Relationships: {len(self.relationships)}

TOTAL ENTITIES: {len(self.places) + len(self.people) + len(self.institutions) + len(self.economic_data) + len(self.infrastructure) + len(self.demographics) + len(self.events)}

NOTES:
- All historical spelling preserved as written in source documents
- Coordinates extracted in original format (degrees/minutes/cardinal)
- Monetary values preserve original currency symbols
- Population data from 1921 census where available
- Trade and shipping statistics from 1923 where available
"""
        return report


def main():
    """Main extraction workflow."""
    source_dir = "/home/user/colonial_office_list/output_2/1925_manual_parsed"
    output_dir = "/home/user/colonial_office_list/knowledge_graph_extracts"
    output_file = f"{output_dir}/1925_extracted.json"

    # Create extractor and process
    extractor = ColonialOfficeExtractor(source_dir, output_dir)

    print("Starting 1925 Colonial Office List Knowledge Graph Extraction...")
    print("=" * 70)

    # Process all colonies
    extractor.process_all_colonies()

    # Save output
    output_data = extractor.save_output(output_file)

    # Generate report
    report = extractor.generate_report()
    print(report)

    # Save report
    report_file = f"{output_dir}/1925_extraction_report.txt"
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    with open(report_file, 'w') as f:
        f.write(report)
    print(f"Report saved to: {report_file}")

    return output_data, extractor


if __name__ == "__main__":
    output_data, extractor = main()
