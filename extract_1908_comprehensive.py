#!/usr/bin/env python3
"""
Comprehensive Knowledge Graph Extraction for Colonial Office List 1908
Enhanced version with detailed entity extraction
"""

import json
import re
import os
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from collections import defaultdict
from datetime import datetime

class ComprehensiveExtractor:
    def __init__(self, source_dir: str):
        self.source_dir = Path(source_dir)
        self.entity_counter = defaultdict(int)
        self.all_people = []
        self.all_places = []
        self.all_institutions = []
        self.all_events = []
        self.all_economic_data = []
        self.all_demographic_data = []
        self.all_infrastructure = []
        self.all_trade_data = []
        self.relationships = []

    def generate_id(self, entity_type: str, name: str) -> str:
        """Generate unique entity ID"""
        clean_name = re.sub(r'[^a-zA-Z0-9]', '_', name)[:40]
        self.entity_counter[entity_type] += 1
        return f"1908_{entity_type}_{clean_name}_{self.entity_counter[entity_type]}"

    def parse_person_line(self, line: str, colony: str) -> Optional[Dict]:
        """Parse a person entry with all details"""
        # Skip if line is too short or doesn't contain relevant markers
        if len(line) < 10:
            return None

        person = {
            "id": "",
            "name": "",
            "full_title": "",
            "position": "",
            "honors": [],
            "salary_pounds": "",
            "salary_dollars": "",
            "allowances": [],
            "colony": colony,
            "source_text": line.strip()
        }

        # Extract honors (K.C.M.G., C.M.G., etc.)
        honor_pattern = r'\b([A-Z]\.(?:[A-Z]\.)*[A-Z]\.(?:M\.G\.|C\.B\.|M\.D\.|M\.A\.|B\.A\.|D\.D\.|Ph\.D\.|LL\.D\.|I\.S\.O\.|D\.S\.O\.|K\.C\.|D\.C\.L\.))\b'
        honors = re.findall(honor_pattern, line)
        person['honors'] = honors

        # Extract salaries in pounds
        pound_patterns = [
            r'£([\d,]+)',
            r'(\d+)l\.',
        ]
        for pattern in pound_patterns:
            match = re.search(pattern, line)
            if match:
                person['salary_pounds'] = match.group(1).replace(',', '')
                break

        # Extract salaries in dollars
        dollar_pattern = r'\$([\d,]+)'
        dollar_match = re.search(dollar_pattern, line)
        if dollar_match:
            person['salary_dollars'] = dollar_match.group(1).replace(',', '')

        # Extract allowances
        allowance_patterns = [
            r'(entertainment allowance)',
            r'(house allowance)',
            r'(horse allowance)',
            r'(forage allowance)',
            r'(personal allowance)',
            r'(travelling allowance)',
            r'(quarters)',
            r'(ration allowance)',
        ]
        for pattern in allowance_patterns:
            if re.search(pattern, line, re.IGNORECASE):
                person['allowances'].append(re.search(pattern, line, re.IGNORECASE).group(1))

        # Try to extract name and position
        # Pattern: Position, Name (with titles), honors, salary
        main_patterns = [
            r'^([A-Z][A-Za-z\s\-&,\.]+?),\s*((?:Sir|Hon\.|Rev\.|Dr\.|Captain|Major|Colonel|Lieutenant|Lieut\.|Lt\.|Brigadier|General|Rt\.\s*Rev\.|Very\s*Rev\.|Most\s*Rev\.)\s*[A-Z][A-Za-z\.\s\-\']+)',
            r'^([A-Z][A-Za-z\s\-&,\.]+?),\s*([A-Z][A-Za-z\.\s\-\']+)',
        ]

        for pattern in main_patterns:
            match = re.search(pattern, line.strip())
            if match:
                person['position'] = match.group(1).strip()
                person['name'] = match.group(2).strip()
                person['full_title'] = f"{person['position']}, {person['name']}"
                if person['honors']:
                    person['full_title'] += ', ' + ', '.join(person['honors'])
                break

        # Only return if we found a name
        if person['name']:
            person['id'] = self.generate_id('person', person['name'])
            return person

        return None

    def extract_coordinates(self, text: str) -> List[Dict]:
        """Extract geographic coordinates"""
        coords = []
        # Pattern for coordinates
        coord_pattern = r'(?:lat\.|latitude)\s*(\d+°?\s*\d+\'?\s*(?:\d+"?)?\s*[NS]).*?(?:long\.|longitude)\s*(\d+°?\s*\d+\'?\s*(?:\d+"?)?\s*[EW])'

        for match in re.finditer(coord_pattern, text, re.IGNORECASE):
            coords.append({
                "latitude": match.group(1),
                "longitude": match.group(2),
                "source_text": match.group(0)
            })

        return coords

    def extract_areas(self, text: str) -> List[Dict]:
        """Extract area measurements"""
        areas = []
        area_patterns = [
            r'area\s+(?:of\s+)?(\d+[\d,]*)\s+(square miles|sq\. miles|acres)',
            r'containing\s+(?:an\s+)?(?:area\s+of\s+)?(\d+[\d,]*)\s+(square miles|acres)',
        ]

        for pattern in area_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                areas.append({
                    "area": match.group(1).replace(',', ''),
                    "unit": match.group(2),
                    "source_text": match.group(0)
                })

        return areas

    def extract_population_data(self, text: str, colony: str) -> List[Dict]:
        """Extract detailed population statistics"""
        pop_data = []

        # Look for census tables and population statements
        lines = text.split('\n')

        for i, line in enumerate(lines):
            if re.search(r'census|population|inhabitants', line, re.IGNORECASE):
                # Check for numbers in this line or nearby lines
                number_pattern = r'(\d+[\d,]*)'
                numbers = re.findall(number_pattern, line)

                if numbers:
                    data = {
                        "colony": colony,
                        "type": "population",
                        "value": numbers[0].replace(',', ''),
                        "source_text": line.strip(),
                        "context": []
                    }

                    # Get context lines
                    if i > 0:
                        data['context'].append(lines[i-1].strip())
                    if i < len(lines) - 1:
                        data['context'].append(lines[i+1].strip())

                    pop_data.append(data)

        return pop_data

    def extract_economic_statistics(self, text: str, colony: str) -> List[Dict]:
        """Extract revenue, expenditure, trade data"""
        econ_data = []

        lines = text.split('\n')
        for line in lines:
            # Pattern for financial data
            patterns = {
                'revenue': r'Revenue[:\s]*£?\$?([\d,]+)',
                'expenditure': r'Expenditure[:\s]*£?\$?([\d,]+)',
                'exports': r'Exports?[:\s]*£?\$?([\d,]+)',
                'imports': r'Imports?[:\s]*£?\$?([\d,]+)',
                'customs': r'Customs[:\s]*£?\$?([\d,]+)',
                'debt': r'(?:Public\s+)?Debt[:\s]*£?\$?([\d,]+)',
            }

            for data_type, pattern in patterns.items():
                match = re.search(pattern, line, re.IGNORECASE)
                if match:
                    currency = '£' if '£' in line else '$' if '$' in line else ''
                    econ_data.append({
                        "colony": colony,
                        "type": data_type,
                        "amount": match.group(1).replace(',', ''),
                        "currency": currency,
                        "source_text": line.strip()
                    })

        return econ_data

    def extract_infrastructure(self, text: str, colony: str) -> List[Dict]:
        """Extract railway, telegraph, postal infrastructure"""
        infrastructure = []

        # Railway patterns
        railway_patterns = [
            r'(\d+[\d,]*)\s+miles?\s+of\s+railway',
            r'railway.*?(\d+[\d,]*)\s+miles?',
        ]

        for pattern in railway_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                infrastructure.append({
                    "colony": colony,
                    "type": "railway",
                    "length": match.group(1).replace(',', ''),
                    "unit": "miles",
                    "source_text": match.group(0)
                })

        # Telegraph patterns
        telegraph_patterns = [
            r'(\d+[\d,]*)\s+miles?\s+of\s+telegraph',
            r'telegraph.*?(\d+[\d,]*)\s+miles?',
        ]

        for pattern in telegraph_patterns:
            for match in re.finditer(pattern, text, re.IGNORECASE):
                infrastructure.append({
                    "colony": colony,
                    "type": "telegraph",
                    "length": match.group(1).replace(',', ''),
                    "unit": "miles",
                    "source_text": match.group(0)
                })

        return infrastructure

    def extract_historical_events(self, text: str, colony: str) -> List[Dict]:
        """Extract historical events and dates"""
        events = []

        # Look for year patterns with context
        year_pattern = r'\b(1\d{3})\b'

        lines = text.split('\n')
        for i, line in enumerate(lines):
            # Look in History section
            if 'history' in line.lower() or i > 0 and 'history' in lines[i-1].lower():
                years = re.findall(year_pattern, line)
                if years:
                    for year in years:
                        events.append({
                            "id": self.generate_id('event', f"{colony}_{year}"),
                            "colony": colony,
                            "year": year,
                            "description": line.strip(),
                            "source_text": line.strip()
                        })

        return events

    def process_colony_file(self, file_path: Path) -> Dict:
        """Process a single colony file with comprehensive extraction"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                text = f.read()

            colony_name = file_path.stem.replace('_', ' ').title()
            print(f"Processing: {colony_name}")

            # Extract all entity types
            people = []
            lines = text.split('\n')
            for line in lines:
                person = self.parse_person_line(line, colony_name)
                if person:
                    people.append(person)

            coordinates = self.extract_coordinates(text)
            areas = self.extract_areas(text)
            population = self.extract_population_data(text, colony_name)
            economics = self.extract_economic_statistics(text, colony_name)
            infrastructure = self.extract_infrastructure(text, colony_name)
            events = self.extract_historical_events(text, colony_name)

            # Store in class attributes
            self.all_people.extend(people)
            self.all_demographic_data.extend(population)
            self.all_economic_data.extend(economics)
            self.all_infrastructure.extend(infrastructure)
            self.all_events.extend(events)

            # Create place record for this colony
            if coordinates or areas:
                place = {
                    "id": self.generate_id('place', colony_name),
                    "name": colony_name,
                    "coordinates": coordinates,
                    "areas": areas,
                    "colony": colony_name
                }
                self.all_places.append(place)

            return {
                "colony": colony_name,
                "people_count": len(people),
                "has_coordinates": len(coordinates) > 0,
                "has_area_data": len(areas) > 0,
                "population_entries": len(population),
                "economic_entries": len(economics),
                "infrastructure_entries": len(infrastructure),
                "historical_events": len(events)
            }

        except Exception as e:
            print(f"Error processing {file_path}: {e}")
            return {"colony": file_path.stem, "error": str(e)}

    def process_all_files(self):
        """Process all colony files"""
        md_files = list(self.source_dir.glob('*.md'))

        # Exclude non-colony files
        exclude_patterns = ['APPENDIX', 'BISHOPS', 'COUNCIL', 'EXECUTIVE',
                          'LEGISLATIVE', 'MAIL', 'LANDS_FOR']

        colony_files = [
            f for f in md_files
            if not any(pattern in f.stem for pattern in exclude_patterns)
        ]

        print(f"Found {len(colony_files)} colony files to process\n")

        summaries = []
        for file_path in sorted(colony_files):
            summary = self.process_colony_file(file_path)
            summaries.append(summary)

        return summaries

    def build_knowledge_graph(self) -> Dict:
        """Build final knowledge graph structure"""
        return {
            "metadata": {
                "year": 1908,
                "source": "Colonial Office List 1908",
                "extraction_date": datetime.now().isoformat(),
                "extractor_version": "2.0_comprehensive"
            },
            "entities": {
                "people": self.all_people,
                "places": self.all_places,
                "institutions": self.all_institutions,
                "events": self.all_events
            },
            "statistics": {
                "economic_data": self.all_economic_data,
                "demographic_data": self.all_demographic_data,
                "trade_data": self.all_trade_data,
                "infrastructure_data": self.all_infrastructure
            },
            "relationships": self.relationships,
            "summary": {
                "total_people": len(self.all_people),
                "total_places": len(self.all_places),
                "total_institutions": len(self.all_institutions),
                "total_events": len(self.all_events),
                "total_economic_records": len(self.all_economic_data),
                "total_demographic_records": len(self.all_demographic_data),
                "total_infrastructure_records": len(self.all_infrastructure)
            }
        }

    def save_knowledge_graph(self, output_path: str):
        """Save knowledge graph to JSON"""
        kg = self.build_knowledge_graph()

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(kg, f, indent=2, ensure_ascii=False)

        print(f"\n{'='*60}")
        print(f"Knowledge Graph saved to: {output_path}")
        print(f"{'='*60}")
        print(f"\nExtraction Summary:")
        print(f"  Total People: {kg['summary']['total_people']}")
        print(f"  Total Places: {kg['summary']['total_places']}")
        print(f"  Total Events: {kg['summary']['total_events']}")
        print(f"  Economic Records: {kg['summary']['total_economic_records']}")
        print(f"  Demographic Records: {kg['summary']['total_demographic_records']}")
        print(f"  Infrastructure Records: {kg['summary']['total_infrastructure_records']}")
        print(f"{'='*60}\n")


def main():
    source_dir = '/home/user/colonial_office_list/output_2/1908_manual_parsed'
    output_path = '/home/user/colonial_office_list/knowledge_graph_extracts/1908_extracted.json'

    print("Colonial Office List 1908 - Comprehensive Knowledge Graph Extraction")
    print("="*60)

    extractor = ComprehensiveExtractor(source_dir)
    extractor.process_all_files()
    extractor.save_knowledge_graph(output_path)


if __name__ == '__main__':
    main()
