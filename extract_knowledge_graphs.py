#!/usr/bin/env python3
"""
Comprehensive Knowledge Graph Extraction from Colonial Office Lists
Processes years 1963-1966 following EXTRACTION_METHODOLOGY.md
"""

import json
import os
import glob
from datetime import datetime
from pathlib import Path
import re
from collections import defaultdict

class ColonialOfficeExtractor:
    def __init__(self, year):
        self.year = str(year)
        self.source_dir = f"/home/user/colonial_office_list/output_2/{year}_manual_parsed"
        self.output_dir = "/home/user/colonial_office_list/knowledge_graph_extracts"
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
        self.entity_ids = defaultdict(list)
        self.id_counter = 0

    def generate_id(self, prefix):
        """Generate unique entity IDs"""
        self.id_counter += 1
        return f"{prefix}_{self.year}_{self.id_counter}"

    def extract_from_text(self, text, colony_name):
        """Extract entities from colony text following methodology"""

        # Extract geographic entities
        self.extract_geographic_entities(text, colony_name)

        # Extract demographic data
        self.extract_demographics(text, colony_name)

        # Extract economic data
        self.extract_economic_data(text, colony_name)

        # Extract infrastructure
        self.extract_infrastructure(text, colony_name)

        # Extract institutions
        self.extract_institutions(text, colony_name)

        # Extract events
        self.extract_events(text, colony_name)

    def extract_geographic_entities(self, text, colony_name):
        """Extract places, coordinates, areas"""
        place_id = self.generate_id("place")

        # Add main colony as place
        place_entity = {
            "id": place_id,
            "name": colony_name,
            "type": "colony",
            "year": self.year
        }

        # Extract area information
        area_match = re.search(r'(?:area|Area).*?(\d+(?:,\d+)?(?:\.\d+)?)\s*square\s*miles', text, re.IGNORECASE)
        if area_match:
            place_entity["area"] = {
                "value": float(area_match.group(1).replace(',', '')),
                "unit": "square miles"
            }

        # Extract coordinates if present
        coord_match = re.search(r'(\d+°\s*\d+\'?)\s*([NS])\s*,?\s*(\d+°\s*\d+\'?)\s*([EW])', text)
        if coord_match:
            place_entity["coordinates"] = {
                "latitude": f"{coord_match.group(1)}{coord_match.group(2)}",
                "longitude": f"{coord_match.group(3)}{coord_match.group(4)}"
            }

        # Extract description
        geo_section = re.search(r'(?:Geographical Features|Principal Towns|Geography)(.*?)(?:\n\n[A-Z]|\Z)', text, re.DOTALL | re.IGNORECASE)
        if geo_section:
            place_entity["description"] = geo_section.group(1).strip()[:500]

        self.entities["places"].append(place_entity)
        self.entity_ids["place"].append(place_id)

    def extract_demographics(self, text, colony_name):
        """Extract population data and breakdowns"""
        demo_id = self.generate_id("demo")

        demo_entity = {
            "id": demo_id,
            "location": colony_name,
            "year": self.year,
            "breakdowns": []
        }

        # Extract total population
        pop_match = re.search(r'total\s*population.*?(\d+(?:,\d+)*)', text, re.IGNORECASE)
        if pop_match:
            demo_entity["total_population"] = int(pop_match.group(1).replace(',', ''))

        # Extract population breakdowns from tables and text
        # Look for percentage tables
        lines = text.split('\n')
        in_pop_section = False
        breakdowns_found = []

        for i, line in enumerate(lines):
            if 'Population' in line or 'population' in line.lower():
                in_pop_section = True

            if in_pop_section and '|' in line:
                # Parse table rows
                parts = [p.strip() for p in line.split('|')[1:-1]]
                if len(parts) >= 2:
                    category = parts[0]
                    # Try to extract number or percentage
                    for p in parts[1:]:
                        num_match = re.search(r'(\d+(?:[,\.]\d+)?)\s*(%)?', p)
                        if num_match:
                            breakdowns_found.append({
                                "category": category,
                                "count": float(num_match.group(1).replace(',', '.')) if '.' in num_match.group(1) or '%' in p else int(num_match.group(1).replace(',', ''))
                            })
                            break

        demo_entity["breakdowns"] = breakdowns_found[:10]  # Limit to 10

        if demo_entity.get("total_population") or demo_entity["breakdowns"]:
            self.entities["demographics"].append(demo_entity)
            self.entity_ids["demo"].append(demo_id)

    def extract_economic_data(self, text, colony_name):
        """Extract revenue, expenditure, trade, and production data"""

        # Extract financial tables
        finance_pattern = r'(?:Public Finance|Revenue|Expenditure)(.*?)(?:\n\n[A-Z]|\Z)'
        finance_section = re.search(finance_pattern, text, re.DOTALL | re.IGNORECASE)

        if finance_section:
            lines = finance_section.group(1).split('\n')
            for line in lines:
                if '|' in line and ('£' in line or '$' in line):
                    parts = line.split('|')
                    if len(parts) >= 3:
                        category = parts[1].strip()

                        # Extract revenue
                        for i, p in enumerate(parts[2:]):
                            amount_match = re.search(r'[£$]\s*(\d+(?:,\d+)*)', p)
                            if amount_match:
                                econ_id = self.generate_id("econ")
                                econ_entity = {
                                    "id": econ_id,
                                    "type": "revenue" if "revenue" in category.lower() else "expenditure",
                                    "location": colony_name,
                                    "year": self.year,
                                    "data": {
                                        "category": category,
                                        "value": int(amount_match.group(1).replace(',', '')),
                                        "currency": "£" if "£" in p else "$"
                                    }
                                }
                                self.entities["economic_data"].append(econ_entity)
                                break

        # Extract trade data
        trade_pattern = r'(?:Trade|Exports|Imports)(.*?)(?:\n\n[A-Z]|\Z)'
        trade_section = re.search(trade_pattern, text, re.DOTALL | re.IGNORECASE)

        if trade_section:
            trade_text = trade_section.group(1)
            # Extract numerical trade values
            for match in re.finditer(r'(\d+(?:,\d+)*)\s*(?:ton|£|$)', trade_text):
                econ_id = self.generate_id("econ")
                econ_entity = {
                    "id": econ_id,
                    "type": "trade_export",
                    "location": colony_name,
                    "year": self.year,
                    "data": {
                        "value": int(match.group(1).replace(',', ''))
                    }
                }
                self.entities["economic_data"].append(econ_entity)

    def extract_infrastructure(self, text, colony_name):
        """Extract railways, telegraphs, roads, ports, etc."""

        infrastructure_types = {
            r'(?:railway|rail)': 'railway',
            r'(?:telegraph|telephone)': 'telegraph',
            r'(?:road|highway)': 'road',
            r'(?:port|dock|harbor|harbour)': 'dock',
            r'(?:airport|aerodrome|airfield)': 'postal_route',
            r'(?:bridge)': 'bridge'
        }

        for pattern, infra_type in infrastructure_types.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                # Extract specifications near the match
                start = max(0, match.start() - 200)
                end = min(len(text), match.end() + 300)
                context = text[start:end]

                # Look for length/distance
                length_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:miles|km|feet|feet)', context)

                if length_match:
                    infra_id = self.generate_id("infra")
                    infra_entity = {
                        "id": infra_id,
                        "type": infra_type,
                        "location": colony_name,
                        "year": self.year,
                        "specifications": {}
                    }

                    if length_match:
                        infra_entity["specifications"]["length"] = {
                            "value": float(length_match.group(1)),
                            "unit": "miles"
                        }

                    self.entities["infrastructure"].append(infra_entity)

    def extract_institutions(self, text, colony_name):
        """Extract councils, courts, departments, etc."""

        institution_patterns = {
            r'Executive Council': 'executive_council',
            r'Legislative Council': 'legislative_council',
            r'Privy Council': 'privy_council',
            r'(?:Supreme|Vice-Admiralty|Police)\s*Court': 'court',
            r'(?:Colonial Secretary|Treasury|Survey|Military)\s*Department': 'department'
        }

        for pattern, inst_type in institution_patterns.items():
            matches = re.finditer(pattern, text, re.IGNORECASE)
            for match in matches:
                inst_id = self.generate_id("inst")
                inst_entity = {
                    "id": inst_id,
                    "name": match.group(0),
                    "type": inst_type,
                    "location": colony_name,
                    "year": self.year,
                    "composition": {
                        "description": ""
                    }
                }

                # Extract composition info
                start = match.end()
                end = min(len(text), start + 400)
                context = text[start:end]

                member_match = re.search(r'(?:consist|compose|members?).*?(\d+).*?(?:member|official)', context, re.IGNORECASE)
                if member_match:
                    inst_entity["composition"]["member_count"] = int(member_match.group(1))

                self.entities["institutions"].append(inst_entity)

    def extract_events(self, text, colony_name):
        """Extract historical events, establishment dates, etc."""

        event_keywords = {
            'established': 'establishment',
            'founded': 'establishment',
            'treaty': 'treaty',
            'cession': 'cession',
            'rebellion': 'rebellion',
            'constitution': 'constitutional_change'
        }

        for keyword, event_type in event_keywords.items():
            pattern = rf'({keyword}.*?)(?:\.|$)'
            matches = re.finditer(pattern, text, re.IGNORECASE | re.DOTALL)

            for match in matches:
                event_text = match.group(1)[:200]

                # Try to extract a date
                date_match = re.search(r'(\d{1,2}\s+(?:January|February|March|April|May|June|July|August|September|October|November|December|Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)?\s*\d{4}|\d{4})', event_text)

                event_id = self.generate_id("event")
                event_entity = {
                    "id": event_id,
                    "description": event_text,
                    "type": event_type,
                    "locations": [colony_name],
                    "year_mentioned": self.year
                }

                if date_match:
                    event_entity["date"] = date_match.group(1)

                self.entities["events"].append(event_entity)

    def process_colonies(self):
        """Process all colony files in the year directory"""

        colony_files = sorted(glob.glob(os.path.join(self.source_dir, '*.md')))
        colonies_processed = []

        for file_path in colony_files:
            colony_name = Path(file_path).stem.replace('_', ' ')
            colonies_processed.append(colony_name)

            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    text = f.read()
                    self.extract_from_text(text, colony_name)
            except Exception as e:
                print(f"Error processing {colony_name}: {e}")

        return colonies_processed

    def create_output(self, colonies_processed):
        """Create final JSON output"""

        output = {
            "metadata": {
                "year": self.year,
                "source_directory": self.source_dir,
                "extraction_date": datetime.utcnow().isoformat() + "Z",
                "processing_notes": f"Extracted from {len(colonies_processed)} colony files using pattern-based entity recognition",
                "colonies_processed": sorted(colonies_processed)
            },
            "entities": self.entities,
            "relationships": self.relationships
        }

        return output

    def save_output(self, output):
        """Save extracted data to JSON file"""

        os.makedirs(self.output_dir, exist_ok=True)
        output_file = os.path.join(self.output_dir, f"{self.year}_extracted.json")

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(output, f, indent=2, ensure_ascii=False)

        return output_file

    def get_entity_counts(self):
        """Get counts of extracted entities"""
        return {
            "places": len(self.entities["places"]),
            "people": len(self.entities["people"]),
            "institutions": len(self.entities["institutions"]),
            "economic_data": len(self.entities["economic_data"]),
            "infrastructure": len(self.entities["infrastructure"]),
            "demographics": len(self.entities["demographics"]),
            "events": len(self.entities["events"]),
            "total": sum(len(v) for v in self.entities.values())
        }

    def extract(self):
        """Main extraction pipeline"""
        print(f"\n{'='*60}")
        print(f"Processing Year {self.year}")
        print(f"{'='*60}")

        colonies_processed = self.process_colonies()
        print(f"Processed {len(colonies_processed)} colonies")

        output = self.create_output(colonies_processed)
        output_file = self.save_output(output)

        counts = self.get_entity_counts()
        print(f"\nEntity Extraction Summary for {self.year}:")
        for entity_type, count in counts.items():
            print(f"  {entity_type}: {count}")

        return output_file, counts

def main():
    """Process all target years"""

    target_years = [1963, 1964, 1965, 1966]
    results = {}
    total_counts = defaultdict(int)

    for year in target_years:
        extractor = ColonialOfficeExtractor(year)
        output_file, counts = extractor.extract()
        results[year] = {
            "file": output_file,
            "counts": counts
        }

        for entity_type, count in counts.items():
            total_counts[entity_type] += count

    # Print summary report
    print(f"\n{'='*60}")
    print("EXTRACTION SUMMARY REPORT")
    print(f"{'='*60}")

    print("\nYears Processed:", ", ".join(str(y) for y in target_years))
    print("\nOutput Files Created:")
    for year, data in sorted(results.items()):
        print(f"  {year}: {data['file']}")

    print("\nTotal Entity Counts Across All Years:")
    for entity_type in ["places", "people", "institutions", "economic_data", "infrastructure", "demographics", "events", "total"]:
        print(f"  {entity_type}: {total_counts[entity_type]}")

    print("\nDetailed Breakdown by Year:")
    for year in target_years:
        counts = results[year]["counts"]
        print(f"\n  Year {year}:")
        for entity_type, count in sorted(counts.items()):
            print(f"    {entity_type}: {count}")

    # Verify files exist
    print("\n" + "="*60)
    print("FILE CREATION VERIFICATION")
    print("="*60)

    for year in target_years:
        output_file = results[year]["file"]
        if os.path.exists(output_file):
            file_size = os.path.getsize(output_file)
            print(f"✓ {output_file}")
            print(f"  Size: {file_size:,} bytes")
        else:
            print(f"✗ {output_file} - NOT FOUND")

if __name__ == "__main__":
    main()
