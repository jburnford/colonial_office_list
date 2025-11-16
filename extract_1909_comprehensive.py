#!/usr/bin/env python3
"""
Comprehensive Knowledge Graph Extraction for Colonial Office List 1909
Enhanced version with detailed extraction patterns for all entity types.
"""

import json
import re
import glob
import os
from collections import defaultdict
from datetime import datetime

class ComprehensiveExtractor:
    def __init__(self, source_dir, schema_file):
        self.source_dir = source_dir
        self.schema = self.load_schema(schema_file)
        self.knowledge_graph = {
            "metadata": {
                "year": 1909,
                "source": "Colonial Office List 1909",
                "extraction_date": datetime.now().isoformat(),
                "files_processed": 0,
                "extraction_methodology": "Comprehensive extraction following EXTRACTION_METHODOLOGY.md",
                "completeness_note": "Extracts all explicitly stated information from source files"
            },
            "entities": {
                "places": [],
                "people": [],
                "institutions": [],
                "economic_data": [],
                "infrastructure": [],
                "demographics": [],
                "events": [],
                "trade_data": []
            },
            "relationships": [],
            "colonies": {}
        }

    def load_schema(self, schema_file):
        """Load the JSON schema template."""
        try:
            with open(schema_file, 'r') as f:
                return json.load(f)
        except:
            return {}

    def process_all_files(self):
        """Process all colony files in the source directory."""
        files = sorted(glob.glob(os.path.join(self.source_dir, "*.md")))
        print(f"Found {len(files)} colony files to process\n")

        for file_path in files:
            colony_name = os.path.basename(file_path).replace('.md', '').replace('_', ' ')
            print(f"Processing: {colony_name:50s}", end='')

            try:
                entities_extracted = self.process_colony_file(file_path)
                print(f" ✓ ({entities_extracted} entities)")
            except Exception as e:
                print(f" ✗ Error: {str(e)[:50]}")

        self.knowledge_graph["metadata"]["files_processed"] = len(files)
        return self.knowledge_graph

    def process_colony_file(self, file_path):
        """Extract all entities from a single colony file."""
        colony_name = os.path.basename(file_path).replace('.md', '').replace('_', ' ')

        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Initialize colony record
        self.knowledge_graph["colonies"][colony_name] = {
            "name": colony_name,
            "raw_text_length": len(content),
            "sections": []
        }

        entities_count = 0
        entities_count += self.extract_geographic_comprehensive(content, colony_name)
        entities_count += self.extract_people_comprehensive(content, colony_name)
        entities_count += self.extract_institutions_comprehensive(content, colony_name)
        entities_count += self.extract_economic_comprehensive(content, colony_name)
        entities_count += self.extract_infrastructure_comprehensive(content, colony_name)
        entities_count += self.extract_demographics_comprehensive(content, colony_name)
        entities_count += self.extract_events_comprehensive(content, colony_name)
        entities_count += self.extract_trade_comprehensive(content, colony_name)

        return entities_count

    def extract_geographic_comprehensive(self, content, colony_name):
        """Comprehensive extraction of geographic entities."""
        count = 0

        # Main colony entity
        place_entity = {
            "id": f"place_{colony_name.replace(' ', '_')}",
            "type": "colony",
            "name": colony_name,
            "historical_spelling": colony_name,
            "attributes": {}
        }

        # Extract coordinates - multiple patterns
        coord_patterns = [
            # Pattern: 13° 24' N. lat., 16° 36' W. long.
            r"(\d+)°\s*(\d+)?'?\s*([NS])\.?\s*lat\.?,?\s*(\d+)°\s*(\d+)?'?\s*([EW])\.?\s*long",
            # Pattern: between 51° and 53° S. lat., and between 57° and 62° W. long.
            r"between\s+(\d+)°.*?(\d+)°\s*([NS]).*?between\s+(\d+)°.*?(\d+)°\s*([EW])",
            # Pattern: 15° 10' and 15° 40' N. lat., and 61° 14' and 61° 30' W. long.
            r"(\d+)°\s*(\d+)'.*?(\d+)°\s*(\d+)'\s*([NS]).*?(\d+)°\s*(\d+)'.*?(\d+)°\s*(\d+)'\s*([EW])",
        ]

        for pattern in coord_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            if matches:
                place_entity["attributes"]["coordinates_raw"] = str(matches[0])
                break

        # Extract area with multiple patterns
        area_patterns = [
            r"area.*?of.*?(\d+[,\d]*)\s*square\s*miles",
            r"total area.*?(\d+[,\d]*)\s*square\s*miles",
            r"area.*?is.*?(\d+[,\d]*)\s*square\s*miles",
            r"(\d+[,\d]*)\s*square\s*miles.*?area",
        ]
        for pattern in area_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                place_entity["attributes"]["area_square_miles"] = match.group(1).replace(',', '')
                break

        # Extract climate information
        climate_patterns = [
            r"(mean temperature.*?\d+°)",
            r"(rainfall.*?\d+\.?\d*\s*inches)",
            r"(climate.*?(?:healthy|unhealthy|temperate|tropical))",
        ]
        climate_data = []
        for pattern in climate_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            climate_data.extend([m[:200] for m in matches[:2]])

        if climate_data:
            place_entity["attributes"]["climate"] = '; '.join(climate_data)

        # Extract description from "Situation and Area" section
        section_match = re.search(r"Situation and Area\.(.*?)(?=\n\n[A-Z][A-Z]|\Z)", content, re.DOTALL | re.IGNORECASE)
        if section_match:
            place_entity["attributes"]["situation_description"] = section_match.group(1).strip()[:1000]

        # Extract topographic information
        if re.search(r"mountain", content, re.IGNORECASE):
            place_entity["attributes"]["topography"] = "mountainous"
        elif re.search(r"flat|plain|low.?lying", content, re.IGNORECASE):
            place_entity["attributes"]["topography"] = "flat/low-lying"

        self.knowledge_graph["entities"]["places"].append(place_entity)
        count += 1

        # Extract dependencies and sub-territories
        dependency_patterns = [
            r"(dependencies|dependency).*?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)",
            r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*is a dependency",
        ]
        for pattern in dependency_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches[:5]:
                if isinstance(match, tuple) and len(match) > 1:
                    dep_name = match[1] if match[1] else match[0]
                    if len(dep_name.split()) <= 4:  # Avoid false positives
                        dependency = {
                            "id": f"place_{dep_name.replace(' ', '_')}",
                            "type": "dependency",
                            "name": dep_name,
                            "parent_colony": colony_name
                        }
                        self.knowledge_graph["entities"]["places"].append(dependency)
                        count += 1

        return count

    def extract_people_comprehensive(self, content, colony_name):
        """Comprehensive extraction of people with all details."""
        count = 0

        # Comprehensive patterns for extracting officials with salaries
        official_patterns = [
            # Pattern: Governor and Commander-in-Chief, Sir Name, K.C.M.G., 1,500l.
            r"(Governor.*?Chief|Colonial Secretary|Attorney[- ]General|Treasurer|Chief Justice|Puisne Judge|Medical Officer|Inspector|Commissioner|Administrator|Auditor|Postmaster|Engineer|Director|Superintendent|Magistrate|Registrar|Collector|Clerk|Captain|Lieutenant|Major|Colonel),\s*([A-Z][^,\n]{3,50}(?:,\s*[A-Z]\.[A-Z]\.?[A-Z]\.?[A-Z]\.?[A-Z]\.?)?),\s*(?:Rs\.|£)?(\d+[,\d]*l?\.?)",

            # Pattern: Title, Name (with possible honors), salary to max
            r"(Governor.*?|Secretary|Justice|Judge|Officer|Inspector|Commissioner|Director)\s+([A-Z][a-z]+(?:\s+[A-Z]\.?\s*)*[A-Z][a-z]+(?:,\s*[A-Z]\.[A-Z]\.?[A-Z]\.?[A-Z]\.?)?),\s*(\d+l\.?\s*to\s*\d+l\.?)",
        ]

        for pattern in official_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches[:100]:  # Limit to avoid excessive data
                if len(match) >= 3:
                    title, name, salary = match[0], match[1], match[2]

                    person = {
                        "id": f"person_{len(self.knowledge_graph['entities']['people'])}",
                        "name": name.strip(),
                        "colony": colony_name,
                        "positions": [{
                            "title": title.strip(),
                            "colony": colony_name,
                            "year": "1909"
                        }],
                        "compensation": {
                            "salary": salary.strip()
                        },
                        "honors": self.extract_honors_detailed(name)
                    }

                    # Extract allowances mentioned nearby
                    allowance_match = re.search(rf"{re.escape(name)}.*?(\d+l?\.?\s*allowance)", content[:content.find(name) + 200])
                    if allowance_match:
                        person["compensation"]["allowances"] = allowance_match.group(1)

                    self.knowledge_graph["entities"]["people"].append(person)
                    count += 1

        # Extract Governors specifically with more detail
        governor_section = re.search(r"Governors?\.(.*?)(?=\n\n[A-Z]|\Z)", content, re.DOTALL | re.IGNORECASE)
        if governor_section:
            governor_entries = re.findall(r"(\d{4})\s+([A-Z][^\n]{10,80})", governor_section.group(1))
            for year, gov_name in governor_entries[:20]:
                person = {
                    "id": f"person_gov_{len(self.knowledge_graph['entities']['people'])}",
                    "name": gov_name.strip(),
                    "colony": colony_name,
                    "positions": [{
                        "title": "Governor",
                        "colony": colony_name,
                        "year": year
                    }],
                    "honors": self.extract_honors_detailed(gov_name)
                }
                self.knowledge_graph["entities"]["people"].append(person)
                count += 1

        return count

    def extract_honors_detailed(self, name_text):
        """Extract honors and decorations with full names."""
        honors_mapping = {
            'K.C.M.G.': 'Knight Commander of St Michael and St George',
            'C.M.G.': 'Companion of St Michael and St George',
            'K.C.B.': 'Knight Commander of the Bath',
            'C.B.': 'Companion of the Bath',
            'D.S.O.': 'Distinguished Service Order',
            'M.V.O.': 'Member of the Royal Victorian Order',
            'I.S.O.': 'Imperial Service Order',
            'Kt.': 'Knight',
            'Sir': 'Knighthood',
            'Dame': 'Dame'
        }

        honors = []
        for abbrev, full_name in honors_mapping.items():
            if re.search(re.escape(abbrev), name_text):
                honors.append({"abbreviation": abbrev, "full_name": full_name})

        return honors

    def extract_institutions_comprehensive(self, content, colony_name):
        """Comprehensive extraction of institutions."""
        count = 0

        # Executive Council
        ec_match = re.search(r"Executive Council\.(.*?)(?=\n\n[A-Z][A-Z]|\Z)", content, re.DOTALL | re.IGNORECASE)
        if ec_match:
            institution = {
                "id": f"inst_exec_council_{colony_name.replace(' ', '_')}",
                "type": "Executive Council",
                "name": f"Executive Council of {colony_name}",
                "colony": colony_name,
                "members": [],
                "structure": "advisory body to Governor"
            }

            # Extract all member names
            member_lines = ec_match.group(1).split('\n')
            for line in member_lines[:30]:
                # Look for name patterns
                name_match = re.search(r"([A-Z][a-z]+(?:\s+[A-Z]\.?\s*)*[A-Z][a-z]+(?:,\s*[A-Z]\.[A-Z]\.?[A-Z]\.?[A-Z]\.?)?)", line)
                if name_match and len(line.strip()) < 100:
                    institution["members"].append(name_match.group(1).strip())

            self.knowledge_graph["entities"]["institutions"].append(institution)
            count += 1

        # Legislative Council
        lc_match = re.search(r"Legislative Council\.(.*?)(?=\n\n[A-Z][A-Z]|\Z)", content, re.DOTALL | re.IGNORECASE)
        if lc_match:
            institution = {
                "id": f"inst_leg_council_{colony_name.replace(' ', '_')}",
                "type": "Legislative Council",
                "name": f"Legislative Council of {colony_name}",
                "colony": colony_name,
                "members": [],
                "sections": {"official": [], "unofficial": [], "elective": []}
            }

            # Parse sections
            text = lc_match.group(1)
            if "Official Members" in text:
                official_section = re.search(r"Official Members\.(.*?)(?=Non-Official|Unofficial|Elective|\n\n)", text, re.DOTALL)
                if official_section:
                    names = re.findall(r"([A-Z][a-z]+(?:\s+[A-Z]\.?\s*)*[A-Z][a-z]+)", official_section.group(1))
                    institution["sections"]["official"] = [n.strip() for n in names[:20]]

            if re.search(r"Non-Official|Unofficial", text):
                unofficial_section = re.search(r"(?:Non-Official|Unofficial) Members\.(.*?)(?=Elective|Official|\n\n|\Z)", text, re.DOTALL)
                if unofficial_section:
                    names = re.findall(r"([A-Z][a-z]+(?:\s+[A-Z]\.?\s*)*[A-Z][a-z]+)", unofficial_section.group(1))
                    institution["sections"]["unofficial"] = [n.strip() for n in names[:20]]

            self.knowledge_graph["entities"]["institutions"].append(institution)
            count += 1

        # Extract Departments
        department_patterns = [
            r"(Medical|Police|Prison|Education|Post Office|Audit|Treasury|Customs|Public Works|Botanical|Railway|Transport|Printing|Judicial)\s+Department",
        ]

        for pattern in department_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for dept_name in set(matches[:10]):
                institution = {
                    "id": f"inst_dept_{colony_name.replace(' ', '_')}_{dept_name.lower()}",
                    "type": "Government Department",
                    "name": f"{dept_name} Department of {colony_name}",
                    "colony": colony_name,
                    "department_type": dept_name
                }
                self.knowledge_graph["entities"]["institutions"].append(institution)
                count += 1

        return count

    def extract_economic_comprehensive(self, content, colony_name):
        """Comprehensive extraction of economic data."""
        count = 0

        # Extract tabular revenue/expenditure data
        # Look for year + revenue + expenditure patterns
        table_pattern = r"(\d{4})\s+(?:£|Rs\.?)?\s*(\d+[,\d]*)\s+(?:£|Rs\.?)?\s*(\d+[,\d]*)"

        matches = re.findall(table_pattern, content)
        seen_years = set()

        for match in matches[:30]:  # Limit to avoid duplicates
            year, revenue, expenditure = match
            if year not in seen_years and 1850 <= int(year) <= 1910:
                seen_years.add(year)
                economic_data = {
                    "id": f"econ_{colony_name.replace(' ', '_')}_{year}",
                    "colony": colony_name,
                    "year": year,
                    "revenue": revenue.replace(',', ''),
                    "expenditure": expenditure.replace(',', ''),
                    "currency": self.detect_currency(content)
                }
                self.knowledge_graph["entities"]["economic_data"].append(economic_data)
                count += 1

        # Extract customs revenue
        customs_match = re.search(r"Customs revenue.*?(\d{4}).*?(\d+[,\d]*l?\.?)", content, re.IGNORECASE)
        if customs_match:
            economic_data = {
                "id": f"econ_customs_{colony_name.replace(' ', '_')}",
                "colony": colony_name,
                "year": customs_match.group(1),
                "customs_revenue": customs_match.group(2).replace(',', ''),
                "currency": self.detect_currency(content)
            }
            self.knowledge_graph["entities"]["economic_data"].append(economic_data)
            count += 1

        return count

    def extract_trade_comprehensive(self, content, colony_name):
        """Comprehensive extraction of trade data."""
        count = 0

        # Extract import/export tables
        import_section = re.search(r"IMPORTS\.(.*?)(?=\n\n[A-Z][A-Z]|EXPORTS|\Z)", content, re.DOTALL | re.IGNORECASE)
        if import_section:
            # Extract data from tables
            import_rows = re.findall(r"(\d{4})\s+(?:£|Rs\.?)?\s*(\d+[,\d]*)\s+(?:£|Rs\.?)?\s*(\d+[,\d]*)\s+(?:£|Rs\.?)?\s*(\d+[,\d]*)\s+(?:£|Rs\.?)?\s*(\d+[,\d]*)", import_section.group(1))

            for row in import_rows[:20]:
                year, uk, colonies, elsewhere, total = row
                trade_data = {
                    "id": f"trade_import_{colony_name.replace(' ', '_')}_{year}",
                    "colony": colony_name,
                    "year": year,
                    "type": "imports",
                    "from_uk": uk.replace(',', ''),
                    "from_colonies": colonies.replace(',', ''),
                    "from_elsewhere": elsewhere.replace(',', ''),
                    "total": total.replace(',', ''),
                    "currency": self.detect_currency(content)
                }
                self.knowledge_graph["entities"]["trade_data"].append(trade_data)
                count += 1

        # Extract export tables
        export_section = re.search(r"EXPORTS\.(.*?)(?=\n\n[A-Z][A-Z]|\Z)", content, re.DOTALL | re.IGNORECASE)
        if export_section:
            export_rows = re.findall(r"(\d{4})\s+(?:£|Rs\.?)?\s*(\d+[,\d]*)\s+(?:£|Rs\.?)?\s*(\d+[,\d]*)\s+(?:£|Rs\.?)?\s*(\d+[,\d]*)\s+(?:£|Rs\.?)?\s*(\d+[,\d]*)", export_section.group(1))

            for row in export_rows[:20]:
                year, uk, colonies, elsewhere, total = row
                trade_data = {
                    "id": f"trade_export_{colony_name.replace(' ', '_')}_{year}",
                    "colony": colony_name,
                    "year": year,
                    "type": "exports",
                    "to_uk": uk.replace(',', ''),
                    "to_colonies": colonies.replace(',', ''),
                    "to_elsewhere": elsewhere.replace(',', ''),
                    "total": total.replace(',', ''),
                    "currency": self.detect_currency(content)
                }
                self.knowledge_graph["entities"]["trade_data"].append(trade_data)
                count += 1

        # Extract principal products
        products_patterns = [
            r"principal (?:exports?|products?).*?(?:are|consist of).*?([a-z][^.]{10,200})",
            r"chief (?:exports?|products?).*?([a-z][^.]{10,200})",
        ]

        for pattern in products_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                products_text = match.group(1).strip()
                # Extract individual products
                products = [p.strip() for p in re.split(r',|;| and ', products_text) if len(p.strip()) > 2][:10]

                if products:
                    trade_data = {
                        "id": f"trade_products_{colony_name.replace(' ', '_')}",
                        "colony": colony_name,
                        "type": "principal_products",
                        "products": products
                    }
                    self.knowledge_graph["entities"]["trade_data"].append(trade_data)
                    count += 1
                break

        return count

    def detect_currency(self, content):
        """Detect the currency used in the colony."""
        currency_patterns = [
            (r"Rs\.|rupees|Rupees", "Indian Rupees"),
            (r"£|pounds sterling|sterling", "Pounds Sterling"),
            (r"\$|dollars", "Dollars"),
        ]

        for pattern, currency in currency_patterns:
            if re.search(pattern, content):
                return currency

        return "Pounds Sterling"  # Default

    def extract_infrastructure_comprehensive(self, content, colony_name):
        """Comprehensive extraction of infrastructure."""
        count = 0

        # Railways - multiple patterns
        railway_patterns = [
            r"(\d+[,\d]*)\s*miles?\s*of.*?railway.*?(?:in operation|constructed|completed)",
            r"railway.*?(\d+[,\d]*)\s*miles",
            r"(\d+[,\d]*)\s*miles.*?railway",
        ]

        for pattern in railway_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                infra = {
                    "id": f"infra_railway_{colony_name.replace(' ', '_')}",
                    "type": "railway",
                    "colony": colony_name,
                    "extent_miles": match.group(1).replace(',', ''),
                    "year": "1909"
                }

                # Try to extract cost
                cost_match = re.search(r"railway.*?(?:cost|expenditure).*?(?:£|Rs\.?)?\s*(\d+[,\d]*)", content, re.IGNORECASE)
                if cost_match:
                    infra["cost"] = cost_match.group(1).replace(',', '')

                # Try to extract gauge
                gauge_match = re.search(r"gauge.*?(\d+\s*ft\.?\s*\d+\s*in\.?)", content, re.IGNORECASE)
                if gauge_match:
                    infra["gauge"] = gauge_match.group(1)

                self.knowledge_graph["entities"]["infrastructure"].append(infra)
                count += 1
                break

        # Telegraphs
        telegraph_patterns = [
            r"(\d+[,\d]*)\s*miles?\s*of.*?telegraph",
            r"telegraph.*?(\d+[,\d]*)\s*miles",
        ]

        for pattern in telegraph_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                infra = {
                    "id": f"infra_telegraph_{colony_name.replace(' ', '_')}",
                    "type": "telegraph",
                    "colony": colony_name,
                    "extent_miles": match.group(1).replace(',', ''),
                    "year": "1909"
                }
                self.knowledge_graph["entities"]["infrastructure"].append(infra)
                count += 1
                break

        # Roads
        road_patterns = [
            r"(\d+[,\d]*)\s*miles?\s*of.*?road",
            r"road.*?(\d+[,\d]*)\s*miles",
        ]

        for pattern in road_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                infra = {
                    "id": f"infra_roads_{colony_name.replace(' ', '_')}",
                    "type": "roads",
                    "colony": colony_name,
                    "extent_miles": match.group(1).replace(',', ''),
                    "year": "1909"
                }
                self.knowledge_graph["entities"]["infrastructure"].append(infra)
                count += 1
                break

        # Postal service
        if re.search(r"post office|postal|postmaster", content, re.IGNORECASE):
            infra = {
                "id": f"infra_postal_{colony_name.replace(' ', '_')}",
                "type": "postal_service",
                "colony": colony_name,
                "year": "1909",
                "exists": True
            }

            # Extract postage rates
            postage_match = re.search(r"postage.*?(\d+d\.?.*?(?:oz|ounce))", content, re.IGNORECASE)
            if postage_match:
                infra["postage_rate"] = postage_match.group(1)

            self.knowledge_graph["entities"]["infrastructure"].append(infra)
            count += 1

        # Harbors and ports
        if re.search(r"harbour|harbor|port", content, re.IGNORECASE):
            harbor_names = re.findall(r"(?:harbour|harbor|port)\s+(?:of\s+)?([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)", content, re.IGNORECASE)
            for name in set(harbor_names[:5]):
                if len(name) < 30:
                    infra = {
                        "id": f"infra_port_{name.replace(' ', '_')}",
                        "type": "port",
                        "colony": colony_name,
                        "name": name,
                        "year": "1909"
                    }
                    self.knowledge_graph["entities"]["infrastructure"].append(infra)
                    count += 1

        return count

    def extract_demographics_comprehensive(self, content, colony_name):
        """Comprehensive extraction of demographics."""
        count = 0

        # Census data - multiple patterns
        census_patterns = [
            r"(?:population|census).*?(\d{4}).*?(\d+[,\d]+)",
            r"(\d{4}).*?census.*?(\d+[,\d]+)",
            r"census.*?taken.*?in.*?(\d{4}).*?(\d+[,\d]+)",
        ]

        seen_years = set()
        for pattern in census_patterns:
            matches = re.findall(pattern, content, re.IGNORECASE)
            for match in matches[:10]:
                year, population = match
                if year not in seen_years and 1850 <= int(year) <= 1910:
                    seen_years.add(year)
                    demographic = {
                        "id": f"demo_{colony_name.replace(' ', '_')}_{year}",
                        "colony": colony_name,
                        "year": year,
                        "total_population": population.replace(',', ''),
                        "source": "census",
                        "breakdowns": {}
                    }
                    self.knowledge_graph["entities"]["demographics"].append(demographic)
                    count += 1

        # Population table with breakdown
        pop_section = re.search(r"Population\.(.*?)(?=\n\n[A-Z][A-Z]|\Z)", content, re.DOTALL | re.IGNORECASE)
        if pop_section:
            # Extract breakdowns by race/ethnicity
            race_patterns = [
                r"European[s]?.*?(\d+[,\d]+)",
                r"Asiatic[s]?.*?(\d+[,\d]+)",
                r"African[s]?.*?(\d+[,\d]+)",
                r"Native[s]?.*?(\d+[,\d]+)",
                r"Chinese.*?(\d+[,\d]+)",
                r"Indian[s]?.*?(\d+[,\d]+)",
            ]

            breakdowns = {}
            for pattern in race_patterns:
                match = re.search(pattern, pop_section.group(1), re.IGNORECASE)
                if match:
                    category = pattern.split('[')[0].replace('\\', '')
                    breakdowns[category] = match.group(1).replace(',', '')

            if breakdowns:
                demographic = {
                    "id": f"demo_breakdown_{colony_name.replace(' ', '_')}",
                    "colony": colony_name,
                    "year": "1909",
                    "breakdowns": breakdowns
                }
                self.knowledge_graph["entities"]["demographics"].append(demographic)
                count += 1

        # Birth and death rates
        vital_stats_pattern = r"birth[- ]rate.*?(\d+\.?\d*)\s*per\s*1,?000|death[- ]rate.*?(\d+\.?\d*)\s*per\s*1,?000"
        matches = re.findall(vital_stats_pattern, content, re.IGNORECASE)

        if matches:
            vital_stats = {}
            for match in matches[:5]:
                if match[0]:
                    vital_stats["birth_rate_per_1000"] = match[0]
                if match[1]:
                    vital_stats["death_rate_per_1000"] = match[1]

            if vital_stats:
                demographic = {
                    "id": f"demo_vital_{colony_name.replace(' ', '_')}",
                    "colony": colony_name,
                    "year": "1909",
                    "vital_statistics": vital_stats
                }
                self.knowledge_graph["entities"]["demographics"].append(demographic)
                count += 1

        return count

    def extract_events_comprehensive(self, content, colony_name):
        """Comprehensive extraction of historical events."""
        count = 0

        # Extract from History section
        history_section = re.search(r"History\.(.*?)(?=\n\n[A-Z][A-Z]|\Z)", content, re.DOTALL | re.IGNORECASE)
        if history_section:
            history_text = history_section.group(1)

            # Pattern: "In 1840" or "1840 -" followed by description
            event_patterns = [
                r"In\s+(\d{4})[,\s]+(.*?)(?:\.|;|\n\n)",
                r"(\d{4})[,\s]+(.*?)(?:\.|;|\n\n)",
                r"On.*?(\d{1,2}(?:st|nd|rd|th)?.*?(?:January|February|March|April|May|June|July|August|September|October|November|December),?\s+\d{4})[,\s]+(.*?)(?:\.|;|\n\n)",
            ]

            for pattern in event_patterns:
                matches = re.findall(pattern, history_text, re.IGNORECASE)
                for match in matches[:50]:
                    if len(match) >= 2:
                        date, description = match[0], match[1]

                        # Try to extract year from various date formats
                        year_match = re.search(r'(\d{4})', date)
                        year = year_match.group(1) if year_match else date

                        if len(description.strip()) > 10 and len(description) < 500:
                            event = {
                                "id": f"event_{len(self.knowledge_graph['entities']['events'])}",
                                "colony": colony_name,
                                "date": date.strip() if len(date) < 50 else year,
                                "year": year if year.isdigit() else None,
                                "description": description.strip()[:300],
                                "category": self.categorize_event(description)
                            }
                            self.knowledge_graph["entities"]["events"].append(event)
                            count += 1

        # Extract discovery/founding events
        discovery_patterns = [
            r"(discovered|found).*?in.*?(\d{4}).*?by\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)",
            r"([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+discovered.*?in.*?(\d{4})",
        ]

        for pattern in discovery_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                if len(match.groups()) >= 3:
                    verb, year, discoverer = match.groups()
                    description = f"Discovered in {year} by {discoverer}"
                elif len(match.groups()) == 2:
                    discoverer, year = match.groups()
                    description = f"Discovered by {discoverer} in {year}"
                else:
                    continue

                event = {
                    "id": f"event_discovery_{colony_name.replace(' ', '_')}",
                    "colony": colony_name,
                    "year": year,
                    "description": description,
                    "category": "discovery"
                }
                self.knowledge_graph["entities"]["events"].append(event)
                count += 1
                break

        return count

    def categorize_event(self, description):
        """Categorize event based on keywords in description."""
        keywords = {
            "political": r"treaty|annexed|ceded|independence|constitution|government",
            "military": r"war|battle|captured|invasion|rebellion|mutiny|conflict",
            "natural_disaster": r"hurricane|earthquake|flood|drought|volcano|eruption",
            "economic": r"trade|commerce|industry|agriculture|plantation",
            "discovery": r"discovered|explored|expedition",
            "administrative": r"established|formed|created|appointed|governor"
        }

        for category, pattern in keywords.items():
            if re.search(pattern, description, re.IGNORECASE):
                return category

        return "general"

    def save_knowledge_graph(self, output_file):
        """Save the knowledge graph to JSON file."""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(self.knowledge_graph, f, indent=2, ensure_ascii=False)

        file_size = os.path.getsize(output_file)
        print(f"\n{'='*80}")
        print(f"Knowledge graph saved to: {output_file}")
        print(f"File size: {file_size:,} bytes ({file_size/1024/1024:.2f} MB)")
        print(f"{'='*80}")

def main():
    source_dir = "/home/user/colonial_office_list/output_2/1909_manual_parsed"
    schema_file = "/home/user/colonial_office_list/json_schema_template.json"
    output_file = "/home/user/colonial_office_list/knowledge_graph_extracts/1909_extracted.json"

    print("="*80)
    print("Colonial Office List 1909 - Comprehensive Knowledge Graph Extraction")
    print("="*80)
    print()

    extractor = ComprehensiveExtractor(source_dir, schema_file)
    knowledge_graph = extractor.process_all_files()
    extractor.save_knowledge_graph(output_file)

    # Print detailed summary statistics
    print("\n" + "="*80)
    print("EXTRACTION SUMMARY")
    print("="*80)
    print(f"Files Processed: {knowledge_graph['metadata']['files_processed']}")
    print(f"Year: {knowledge_graph['metadata']['year']}")
    print(f"Extraction Date: {knowledge_graph['metadata']['extraction_date']}")
    print(f"\nEntity Counts by Type:")
    print("-"*80)

    total_entities = 0
    for entity_type, entities in knowledge_graph['entities'].items():
        count = len(entities)
        total_entities += count
        print(f"  {entity_type.replace('_', ' ').title():30s}: {count:6d}")

    print("-"*80)
    print(f"  {'Total Entities':30s}: {total_entities:6d}")
    print("="*80)

    # Sample entities
    print("\nSample Extractions:")
    print("-"*80)
    if knowledge_graph['entities']['people']:
        print(f"\nSample Person: {json.dumps(knowledge_graph['entities']['people'][0], indent=2)[:300]}...")
    if knowledge_graph['entities']['economic_data']:
        print(f"\nSample Economic Data: {json.dumps(knowledge_graph['entities']['economic_data'][0], indent=2)[:300]}...")

    print("\n" + "="*80)
    print("Extraction complete!")
    print("="*80)

if __name__ == "__main__":
    main()
