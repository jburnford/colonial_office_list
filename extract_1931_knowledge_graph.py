#!/usr/bin/env python3
"""
Extract comprehensive structured knowledge graph data from the Colonial Office List for year 1931.
Follows the extraction methodology defined in EXTRACTION_METHODOLOGY.md
"""

import json
import re
import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Set, Any, Optional
import uuid

# Configuration
YEAR = "1931"
SOURCE_DIR = "/home/user/colonial_office_list/output_2/1931_manual_parsed"
OUTPUT_DIR = "/home/user/colonial_office_list/knowledge_graph_extracts"
OUTPUT_FILE = f"{OUTPUT_DIR}/1931_extracted.json"

class KnowledgeGraphExtractor:
    def __init__(self, year: str, source_dir: str):
        self.year = year
        self.source_dir = source_dir
        self.colonies_processed = []
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
        self.entity_ids = {}  # Cache for deduplication
        self.people_names = {}  # Track unique people by name

    def generate_id(self, entity_type: str, name: str) -> str:
        """Generate consistent unique IDs for entities"""
        key = f"{entity_type}_{name}".lower().replace(" ", "_").replace("'", "").replace(".", "")
        if key not in self.entity_ids:
            self.entity_ids[key] = f"{entity_type}_{len(self.entity_ids)}_{uuid.uuid4().hex[:8]}"
        return self.entity_ids[key]

    def extract_coordinates(self, text: str) -> Optional[Dict[str, str]]:
        """Extract latitude and longitude coordinates from text"""
        # Pattern for coordinates like "22° 9' N. lat., 114° 5' E. long."
        coord_pattern = r"(\d+°\s*\d+\'?\s*[NSnsEWew]\.?\s*(?:lat|long)\.|[\d°\'\s]+[NSEWnsew])"
        matches = re.findall(coord_pattern, text)

        if len(matches) >= 2:
            return {
                "latitude": matches[0].strip(),
                "longitude": matches[1].strip() if len(matches) > 1 else None
            }
        return None

    def extract_area(self, text: str) -> Optional[Dict[str, Any]]:
        """Extract area measurements from text"""
        # Pattern for area like "720 square miles" or "32 square miles"
        area_patterns = [
            r"(\d+(?:,\d+)?)\s*square\s*miles",
            r"(\d+(?:,\d+)?)\s*acres",
            r"(\d+(?:,\d+)?)\s*sq\.\s*ft\.",
            r"(\d+(?:,\d+)?)\s*square\s*feet"
        ]

        for pattern in area_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                value_str = match.group(1).replace(",", "")
                try:
                    value = float(value_str)
                    unit_match = re.search(r"(square miles|acres|sq\. ft\.|square feet)", match.group(0), re.IGNORECASE)
                    unit = unit_match.group(1) if unit_match else "unknown"
                    return {"value": value, "unit": unit}
                except ValueError:
                    continue
        return None

    def extract_people_and_positions(self, text: str, location: str) -> List[Dict[str, Any]]:
        """Extract people with positions and salaries from text"""
        people = []

        # Pattern to find salary ranges: "£600 to £1,000" or "l. to l."
        salary_pattern = r"(?:[£l]\.?\s*)?(\d+(?:,\d+)?)\s*(?:to|–|-)?\s*(?:[£l]\.?\s*)?(\d+(?:,\d+)?)?"

        # Split by common position headers
        position_headers = re.split(
            r"((?:^|\n)(?:[A-Z][a-z\s]+)(?:\.|\s*[,;]))",
            text,
            flags=re.MULTILINE
        )

        current_position_title = None
        current_department = None

        for i, section in enumerate(position_headers):
            # Check if this is a position header
            if re.match(r"^[A-Z][a-z\s]+\.?$", section.strip()):
                current_position_title = section.strip()
                continue

            # Extract names and salaries from this section
            # Pattern: "Name, qualifications, salary"
            name_pattern = r"([A-Z][a-z]+(?: [A-Z]\.?)?(?:[a-z\-]+ )*[A-Z][a-z]+(?:,| and| &))"

            lines = section.strip().split('\n')
            for line in lines:
                if not line.strip():
                    continue

                # Try to extract names and salaries
                parts = line.split(',')
                if len(parts) >= 1:
                    # First part likely contains name
                    name_part = parts[0].strip()

                    # Skip if it looks like a header or continuation
                    if not name_part or len(name_part) < 2 or name_part.isupper():
                        continue

                    # Extract qualifications if present
                    qualifications = []
                    salary = None

                    for part in parts[1:]:
                        part = part.strip()

                        # Check for degree/qualification patterns
                        if any(q in part for q in ["M.A.", "M.B.", "Ph.D.", "B.Sc.", "M.D.", "L.R.C.P.", "M.R.C.S.", "D.P.H.", "K.C.M.G.", "C.B.", "O.B.E.", "M.B.E.", "D.S.O."]):
                            qualifications.append(part)

                        # Check for salary
                        if "l." in part or "£" in part or re.search(r"\d+\s*to\s*\d+", part):
                            salary = part

                    # Extract honorifics and titles
                    titles = []
                    honors = []
                    name_clean = name_part

                    for title in ["Sir", "Rev.", "Dr.", "Capt.", "Col.", "Lt.", "Major", "Captain", "Colonel", "Lieutenant", "Flight-Lieut."]:
                        if name_clean.startswith(title):
                            titles.append(title)
                            name_clean = name_clean[len(title):].strip()

                    for honor in ["K.C.M.G.", "C.B.", "G.C.B.", "O.B.E.", "M.B.E.", "D.S.O.", "M.C."]:
                        if honor in name_part:
                            honors.append(honor)

                    if name_clean and len(name_clean) > 1:
                        person = {
                            "id": self.generate_id("person", name_clean),
                            "name": name_clean.strip(),
                            "titles": titles,
                            "honors": honors,
                            "positions": []
                        }

                        if current_position_title:
                            position = {
                                "title": current_position_title,
                                "location": location,
                                "year": self.year
                            }

                            if salary:
                                position["salary"] = self.parse_salary(salary)

                            person["positions"].append(position)

                        people.append(person)

        return people

    def parse_salary(self, salary_str: str) -> Dict[str, Any]:
        """Parse salary information"""
        salary_data = {
            "amount": None,
            "currency": "£",
            "period": "annual"
        }

        # Extract currency
        if "$" in salary_str:
            salary_data["currency"] = "$"

        # Extract amount(s)
        amounts = re.findall(r"(\d+(?:,\d+)?)", salary_str)
        if amounts:
            salary_data["amount"] = int(amounts[0].replace(",", ""))

        return salary_data

    def extract_geographic_entities(self, text: str, colony_name: str) -> List[Dict[str, Any]]:
        """Extract geographic entities and locations from text"""
        places = []

        # Add the colony itself
        colony_id = self.generate_id("place", colony_name)

        place = {
            "id": colony_id,
            "name": colony_name,
            "type": "colony",
            "year": self.year
        }

        # Extract area if present
        area = self.extract_area(text)
        if area:
            place["area"] = area

        # Extract coordinates if present
        coords = self.extract_coordinates(text)
        if coords:
            place["coordinates"] = coords

        # Extract description (first few sentences)
        description = text[:500] if len(text) > 500 else text
        if description.strip():
            place["description"] = description.strip()

        places.append(place)

        # Extract sub-regions, cities, towns
        city_pattern = r"(?:The (?:city|town) of |in the |at |near )([A-Z][a-zA-Z\s\-]+)(?:,|\s+is|\s+was)"
        for match in re.finditer(city_pattern, text):
            city_name = match.group(1).strip()
            if len(city_name) > 2 and not city_name.isupper():
                city_type = "city" if "city" in match.group(0).lower() else "town" if "town" in match.group(0).lower() else "settlement"

                city = {
                    "id": self.generate_id("place", city_name),
                    "name": city_name,
                    "type": city_type,
                    "parent_location": colony_id,
                    "year": self.year
                }
                places.append(city)

        return places

    def extract_economic_data(self, text: str, colony_name: str) -> List[Dict[str, Any]]:
        """Extract economic data (revenue, expenditure, trade, shipping)"""
        economic_data = []

        # Look for revenue/expenditure tables
        revenue_patterns = [
            r"Revenue[:\s]+(?:[£$]?)\s*(\d+(?:,\d+)?(?:\.\d+)?)",
            r"Revenue\s+(\d+(?:,\d+)?(?:\.\d+)?)",
        ]

        for pattern in revenue_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                amount_str = match.group(1).replace(",", "")
                try:
                    amount = float(amount_str)

                    econ = {
                        "id": self.generate_id("economic", f"{colony_name}_revenue"),
                        "type": "revenue",
                        "location": colony_name,
                        "year": self.year,
                        "data": {
                            "category": "government_revenue",
                            "value": amount,
                            "currency": "£"
                        }
                    }
                    economic_data.append(econ)
                except ValueError:
                    continue

        # Look for trade/shipping data
        shipping_pattern = r"(?:total tonnage|tonnage).*?(\d+(?:,\d+)?)\s*tons"
        for match in re.finditer(shipping_pattern, text, re.IGNORECASE):
            try:
                tonnage = int(match.group(1).replace(",", ""))

                econ = {
                    "id": self.generate_id("economic", f"{colony_name}_shipping"),
                    "type": "shipping",
                    "location": colony_name,
                    "year": self.year,
                    "data": {
                        "category": "shipping_tonnage",
                        "value": tonnage,
                        "unit": "tons"
                    }
                }
                economic_data.append(econ)
            except ValueError:
                continue

        return economic_data

    def extract_infrastructure(self, text: str, colony_name: str) -> List[Dict[str, Any]]:
        """Extract infrastructure information (railways, telegraphs, ports, etc.)"""
        infrastructure = []

        # Look for railway information
        railway_patterns = [
            r"(?:railway|railroad).*?(\d+)\s*miles?",
            r"(\d+)\s*miles?.*?(?:railway|railroad)"
        ]

        for pattern in railway_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                try:
                    length = int(match.group(1))

                    infra = {
                        "id": self.generate_id("infrastructure", f"{colony_name}_railway"),
                        "type": "railway",
                        "location": colony_name,
                        "year": self.year,
                        "specifications": {
                            "length": {
                                "value": length,
                                "unit": "miles"
                            }
                        }
                    }
                    infrastructure.append(infra)
                except ValueError:
                    continue

        # Look for telegraph/communication infrastructure
        if "telegraph" in text.lower():
            infra = {
                "id": self.generate_id("infrastructure", f"{colony_name}_telegraph"),
                "type": "telegraph",
                "location": colony_name,
                "year": self.year
            }
            infrastructure.append(infra)

        # Look for ports/harbors
        harbor_keywords = ["harbour", "harbor", "port", "dock", "anchorage"]
        if any(kw in text.lower() for kw in harbor_keywords):
            infra = {
                "id": self.generate_id("infrastructure", f"{colony_name}_harbor"),
                "type": "harbor",
                "location": colony_name,
                "year": self.year
            }
            infrastructure.append(infra)

        return infrastructure

    def extract_demographics(self, text: str, colony_name: str) -> List[Dict[str, Any]]:
        """Extract demographic information"""
        demographics = []

        # Look for population figures
        pop_patterns = [
            r"population\s+(?:of\s+)?(\d+(?:,\d+)?)",
            r"total\s+population[:\s]+(\d+(?:,\d+)?)",
            r"census.*?(\d+(?:,\d+)?)",
        ]

        for pattern in pop_patterns:
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                try:
                    pop_count = int(match.group(1).replace(",", ""))

                    demo = {
                        "id": self.generate_id("demographic", f"{colony_name}_population"),
                        "location": colony_name,
                        "year": self.year,
                        "total_population": pop_count
                    }
                    demographics.append(demo)
                    break  # Only take first population figure per colony
                except ValueError:
                    continue

        return demographics

    def extract_events(self, text: str, colony_name: str) -> List[Dict[str, Any]]:
        """Extract historical events mentioned in the text"""
        events = []

        # Look for key event indicators
        event_keywords = [
            (r"ceded.*?(\d{4})", "cession"),
            (r"treaty.*?(\d{4})", "treaty"),
            (r"established.*?(\d{4})", "establishment"),
            (r"discovered.*?(\d{4})", "establishment"),
            (r"took possession.*?(\d{4})", "transfer"),
            (r"opened.*?(\d{4})", "establishment"),
        ]

        for pattern, event_type in event_keywords:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                year_mentioned = match.group(1)
                event_context = text[max(0, match.start()-100):min(len(text), match.end()+100)]

                event = {
                    "id": self.generate_id("event", f"{colony_name}_{event_type}_{year_mentioned}"),
                    "type": event_type,
                    "description": event_context.strip(),
                    "year_mentioned": self.year,
                    "locations": [self.generate_id("place", colony_name)]
                }

                events.append(event)

        return events

    def process_colony_file(self, filepath: str) -> None:
        """Process a single colony file and extract all entities"""

        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Extract colony name from filename
        filename = os.path.basename(filepath)
        colony_name = filename.replace(".md", "").replace("_", " ")

        print(f"Processing {colony_name}...")
        self.colonies_processed.append(colony_name)

        # Extract different entity types
        places = self.extract_geographic_entities(content, colony_name)
        self.entities["places"].extend(places)

        # Extract people (improved parsing)
        people = self.extract_people_and_positions(content, colony_name)
        self.entities["people"].extend(people)

        # Extract economic data
        econ = self.extract_economic_data(content, colony_name)
        self.entities["economic_data"].extend(econ)

        # Extract infrastructure
        infra = self.extract_infrastructure(content, colony_name)
        self.entities["infrastructure"].extend(infra)

        # Extract demographics
        demo = self.extract_demographics(content, colony_name)
        self.entities["demographics"].extend(demo)

        # Extract events
        evts = self.extract_events(content, colony_name)
        self.entities["events"].extend(evts)

        # Create relationships
        colony_place_id = self.generate_id("place", colony_name)

        # People -> Location relationships
        for person in people:
            for position in person.get("positions", []):
                rel = {
                    "source_id": person["id"],
                    "relationship_type": "GOVERNED_BY",
                    "target_id": colony_place_id,
                    "properties": {
                        "year": self.year,
                        "position": position.get("title", "")
                    }
                }
                self.relationships.append(rel)

        # Sub-location -> Colony relationships
        for place in places:
            if place.get("parent_location") and place["id"] != colony_place_id:
                rel = {
                    "source_id": place["id"],
                    "relationship_type": "LOCATED_IN",
                    "target_id": colony_place_id,
                    "properties": {"year": self.year}
                }
                self.relationships.append(rel)

    def build_output(self) -> Dict[str, Any]:
        """Build the complete output JSON structure"""

        output = {
            "metadata": {
                "year": self.year,
                "source_directory": self.source_dir,
                "extraction_date": datetime.now().isoformat(),
                "colonies_processed": sorted(list(set(self.colonies_processed))),
                "processing_notes": "Comprehensive extraction from Colonial Office List 1931. Entities include geographic locations, administrative personnel with positions and salaries, institutions, economic data, infrastructure, demographic information, and historical events mentioned in the documents."
            },
            "entities": self.entities,
            "relationships": self.relationships
        }

        return output

    def deduplicate_entities(self) -> None:
        """Remove duplicate entities based on name and type"""

        # Deduplicate people
        seen_people = {}
        unique_people = []
        for person in self.entities["people"]:
            key = (person["name"], tuple(person.get("titles", [])))
            if key not in seen_people:
                seen_people[key] = person
                unique_people.append(person)
            else:
                # Merge positions if same person appears multiple times
                existing = seen_people[key]
                if "positions" in person:
                    existing.setdefault("positions", []).extend(person["positions"])

        self.entities["people"] = unique_people

        # Deduplicate places
        seen_places = {}
        unique_places = []
        for place in self.entities["places"]:
            key = (place["name"], place["type"])
            if key not in seen_places:
                seen_places[key] = place
                unique_places.append(place)

        self.entities["places"] = unique_places

        # Deduplicate economic data
        seen_econ = {}
        unique_econ = []
        for econ in self.entities["economic_data"]:
            key = (econ["location"], econ["type"], econ["data"].get("category"))
            if key not in seen_econ:
                seen_econ[key] = econ
                unique_econ.append(econ)

        self.entities["economic_data"] = unique_econ

    def run_extraction(self) -> None:
        """Run the complete extraction process"""

        # Get all colony files
        colony_files = sorted(Path(self.source_dir).glob("*.md"))

        if not colony_files:
            print(f"No files found in {self.source_dir}")
            return

        print(f"Found {len(colony_files)} colony files to process")

        # Process each file
        for filepath in colony_files:
            try:
                self.process_colony_file(str(filepath))
            except Exception as e:
                print(f"Error processing {filepath}: {e}")
                continue

        # Deduplicate and clean up
        self.deduplicate_entities()

        # Build final output
        output = self.build_output()

        # Write to file
        os.makedirs(OUTPUT_DIR, exist_ok=True)
        with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        print(f"\nExtraction complete!")
        print(f"Output written to: {OUTPUT_FILE}")

        # Print summary statistics
        self.print_summary(output)

    def print_summary(self, output: Dict[str, Any]) -> None:
        """Print summary statistics"""
        print("\n" + "="*60)
        print("EXTRACTION SUMMARY - 1931 COLONIAL OFFICE LIST")
        print("="*60)
        print(f"\nColonies/Territories Processed: {len(output['metadata']['colonies_processed'])}")
        print(f"  {', '.join(output['metadata']['colonies_processed'][:10])}...")

        print(f"\nEntity Counts by Type:")
        print(f"  Geographic Places: {len(output['entities']['places'])}")
        print(f"  People: {len(output['entities']['people'])}")
        print(f"  Institutions: {len(output['entities']['institutions'])}")
        print(f"  Economic Data Points: {len(output['entities']['economic_data'])}")
        print(f"  Infrastructure: {len(output['entities']['infrastructure'])}")
        print(f"  Demographics: {len(output['entities']['demographics'])}")
        print(f"  Historical Events: {len(output['entities']['events'])}")

        print(f"\nRelationships: {len(output['relationships'])}")
        print(f"\nExtraction Date: {output['metadata']['extraction_date']}")
        print("="*60)

if __name__ == "__main__":
    extractor = KnowledgeGraphExtractor(YEAR, SOURCE_DIR)
    extractor.run_extraction()
