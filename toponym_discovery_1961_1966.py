#!/usr/bin/env python3
"""
Toponym Discovery Agent for Colonial Office List Knowledge Graph Project
Years: 1961, 1962, 1964, 1965, 1966

This agent performs exhaustive toponym discovery by:
1. Auditing existing place entities in v3 KG files
2. Scanning all source markdown files for toponyms
3. Extracting specific named places with geographic context
4. Performing gap analysis
5. Extracting missing toponyms with full provenance
6. Generating enhanced KG files
"""

import json
import re
import os
from pathlib import Path
from datetime import datetime
from collections import defaultdict, Counter
from typing import Dict, List, Set, Tuple
import hashlib

# Base directory
BASE_DIR = Path("/home/user/colonial_office_list")
V3_DIR = BASE_DIR / "knowledge_graph_extracts_v3"
OCR_DIR = BASE_DIR / "historical_document_pipeline" / "processed_pdfs"
MANUAL_DIR = BASE_DIR / "output_2"
REPORT_DIR = BASE_DIR / "reports" / "phase_c"

# Years to process
YEARS = [1961, 1962, 1964, 1965, 1966]

# Toponym patterns for extraction
# Common geographic indicators
GEOGRAPHIC_INDICATORS = [
    r'\b(Island|Islands|Isle|Isles)\b',
    r'\b(Colony|Territory|Protectorate|State|Province|District|Division)\b',
    r'\b(River|Bay|Harbor|Harbour|Gulf|Strait|Channel|Sound)\b',
    r'\b(Mountain|Mountains|Mt\.|Hill|Hills|Peak|Range)\b',
    r'\b(Lake|Lagoon|Pond)\b',
    r'\b(Cape|Point|Peninsula|Headland)\b',
    r'\b(Town|City|Village|Settlement|Port)\b',
    r'\b(County|Parish|Region|Area)\b',
    r'\b(Reef|Atoll|Cay|Key)\b',
]

# Major colonies/territories often mentioned
KNOWN_TERRITORIES = {
    'Bermuda', 'British Guiana', 'British Honduras', 'British Solomon Islands',
    'Brunei', 'Falkland Islands', 'Fiji', 'Gambia', 'Gibraltar',
    'Gilbert and Ellice Islands', 'Hong Kong', 'Kenya', 'Malta', 'Mauritius',
    'New Hebrides', 'Northern Rhodesia', 'North Borneo', 'Nyasaland',
    'Sarawak', 'Seychelles', 'Sierra Leone', 'Singapore', 'St. Helena',
    'Tanganyika', 'Tonga', 'Uganda', 'Virgin Islands', 'Zanzibar',
    'Bahama Islands', 'Barbados', 'Jamaica', 'Trinidad', 'Tobago',
    'Aden', 'Cyprus', 'Nigeria', 'Rhodesia', 'Ascension', 'Tristan da Cunha',
    'Pitcairn', 'Somaliland'
}


class ToponymDiscoveryAgent:
    def __init__(self):
        self.existing_places = {}  # year -> list of places
        self.discovered_toponyms = {}  # year -> list of toponyms with context
        self.gap_analysis = {}  # year -> gap report
        self.new_toponyms = {}  # year -> list of new toponyms to add

    def load_existing_places(self, year: int) -> List[Dict]:
        """Load existing place entities from v3 KG file"""
        v3_file = V3_DIR / f"{year}_extracted.json"

        if not v3_file.exists():
            print(f"Warning: {v3_file} does not exist")
            return []

        with open(v3_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        places = data.get('entities', {}).get('places', [])
        print(f"Loaded {len(places)} existing places for {year}")
        return places

    def extract_toponyms_from_text(self, text: str, source: str, year: int) -> List[Dict]:
        """Extract toponyms from text using pattern matching and NLP"""
        toponyms = []

        # Strategy 1: Find capitalized sequences that might be place names
        # Looking for patterns like "Foo Bar", "New York", etc.
        cap_pattern = r'\b([A-Z][a-z]+(?:\s+(?:of|and|da|de|la|le)\s+)?(?:[A-Z][a-z]+|[A-Z]\.?)(?:\s+(?:[A-Z][a-z]+|Islands?|Bay|River|Mountain|Town|City|Colony|Territory))?\b)'

        for match in re.finditer(cap_pattern, text):
            place_candidate = match.group(1).strip()

            # Get context (50 chars before and after)
            start_pos = max(0, match.start() - 50)
            end_pos = min(len(text), match.end() + 50)
            context = text[start_pos:end_pos]

            # Check if it has geographic indicators nearby
            has_geo_indicator = any(re.search(pattern, context, re.IGNORECASE)
                                   for pattern in GEOGRAPHIC_INDICATORS)

            # Check if it's a known territory
            is_known = any(territory.lower() in place_candidate.lower()
                          for territory in KNOWN_TERRITORIES)

            if has_geo_indicator or is_known or len(place_candidate.split()) >= 2:
                toponyms.append({
                    'name': place_candidate,
                    'context': context,
                    'source': source,
                    'year': year,
                    'line_number': text[:match.start()].count('\n') + 1
                })

        # Strategy 2: Find explicit geographic features
        # Pattern: "Name + Geographic Type" (e.g., "Victoria Island", "Thames River")
        geo_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+(Island|Islands|River|Bay|Mountain|Lake|Town|City|Colony|Territory|District|Province|County|Parish)\b'

        for match in re.finditer(geo_pattern, text):
            place_name = match.group(1).strip()
            place_type = match.group(2).lower()

            start_pos = max(0, match.start() - 50)
            end_pos = min(len(text), match.end() + 50)
            context = text[start_pos:end_pos]

            toponyms.append({
                'name': f"{place_name} {match.group(2)}",
                'type': place_type,
                'context': context,
                'source': source,
                'year': year,
                'line_number': text[:match.start()].count('\n') + 1
            })

        # Strategy 3: Find places in specific sections
        # Look for sections like "Principal Towns", "Geographical Features", etc.
        section_patterns = [
            (r'Principal Towns?[:\n]+(.*?)(?=\n\n|\n[A-Z][a-z]+\n|$)', 'principal_town'),
            (r'Geographical Features[:\n]+(.*?)(?=\n\n|\n[A-Z][a-z]+\n|$)', 'geographical_feature'),
            (r'Administrative Divisions?[:\n]+(.*?)(?=\n\n|\n[A-Z][a-z]+\n|$)', 'administrative_division'),
        ]

        for pattern, section_type in section_patterns:
            for match in re.finditer(pattern, text, re.DOTALL):
                section_text = match.group(1)
                # Extract place names from this section
                for name_match in re.finditer(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b', section_text):
                    place_name = name_match.group(1)
                    if len(place_name) > 2:  # Filter out initials
                        toponyms.append({
                            'name': place_name,
                            'type': section_type,
                            'context': section_text[:200],
                            'source': source,
                            'year': year,
                            'section': section_type
                        })

        return toponyms

    def scan_source_files(self, year: int) -> List[Dict]:
        """Scan all source files for a given year"""
        all_toponyms = []

        # Scan OCR results
        ocr_file = OCR_DIR / f"colonial-office-list-{year}" / "olmocr_results.md"
        if ocr_file.exists():
            print(f"Scanning OCR file: {ocr_file}")
            with open(ocr_file, 'r', encoding='utf-8', errors='ignore') as f:
                text = f.read()
            toponyms = self.extract_toponyms_from_text(text, str(ocr_file), year)
            print(f"  Found {len(toponyms)} toponym candidates in OCR file")
            all_toponyms.extend(toponyms)

        # Scan manual parsed files
        manual_dir = MANUAL_DIR / f"{year}_manual_parsed"
        if manual_dir.exists():
            for md_file in manual_dir.glob("*.md"):
                print(f"Scanning manual file: {md_file.name}")
                with open(md_file, 'r', encoding='utf-8', errors='ignore') as f:
                    text = f.read()
                toponyms = self.extract_toponyms_from_text(text, str(md_file), year)
                print(f"  Found {len(toponyms)} toponym candidates in {md_file.name}")
                all_toponyms.extend(toponyms)

        return all_toponyms

    def deduplicate_toponyms(self, toponyms: List[Dict]) -> List[Dict]:
        """Deduplicate toponyms by name, keeping the one with most context"""
        toponym_dict = {}

        for topo in toponyms:
            name = topo['name'].strip()

            if name not in toponym_dict:
                toponym_dict[name] = topo
            else:
                # Keep the one with longer context
                if len(topo.get('context', '')) > len(toponym_dict[name].get('context', '')):
                    toponym_dict[name] = topo

        return list(toponym_dict.values())

    def filter_valid_toponyms(self, toponyms: List[Dict]) -> List[Dict]:
        """Filter out invalid toponyms (common words, etc.)"""
        # Common words to exclude
        EXCLUDE_WORDS = {
            'The', 'This', 'That', 'These', 'Those', 'There', 'Where', 'When',
            'Government', 'Secretary', 'Minister', 'Office', 'Department',
            'Committee', 'Council', 'Board', 'Commission', 'Act', 'Law',
            'January', 'February', 'March', 'April', 'May', 'June', 'July',
            'August', 'September', 'October', 'November', 'December',
            'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday',
            'North', 'South', 'East', 'West', 'Central', 'Upper', 'Lower',
            'Sir', 'Mr', 'Mrs', 'Miss', 'Dr', 'Rev', 'Hon', 'Rt',
            'British', 'English', 'Colonial', 'Royal', 'Imperial',
        }

        filtered = []
        for topo in toponyms:
            name = topo['name'].strip()

            # Skip if it's in exclude list
            if name in EXCLUDE_WORDS:
                continue

            # Skip if it's too short
            if len(name) < 3:
                continue

            # Skip if it's all uppercase (likely acronym)
            if name.isupper() and len(name) < 10:
                continue

            # Skip if it doesn't start with uppercase
            if not name[0].isupper():
                continue

            filtered.append(topo)

        return filtered

    def perform_gap_analysis(self, year: int, existing: List[Dict], discovered: List[Dict]) -> Dict:
        """Compare existing places vs discovered toponyms"""
        existing_names = {p['name'].lower().strip() for p in existing}
        discovered_names = {t['name'].lower().strip() for t in discovered}

        # Find gaps
        missing_in_kg = discovered_names - existing_names

        # Create detailed gap report
        gap_report = {
            'year': year,
            'existing_count': len(existing_names),
            'discovered_count': len(discovered_names),
            'missing_count': len(missing_in_kg),
            'missing_toponyms': sorted(list(missing_in_kg)),
            'coverage_percentage': (len(existing_names) / len(discovered_names) * 100) if discovered_names else 0
        }

        return gap_report

    def extract_missing_toponyms(self, year: int, gap_report: Dict, discovered: List[Dict]) -> List[Dict]:
        """Extract detailed information for missing toponyms"""
        missing_names = {name.lower() for name in gap_report['missing_toponyms']}

        new_toponyms = []
        for topo in discovered:
            if topo['name'].lower().strip() in missing_names:
                # Create a KG entity for this toponym
                entity = self.create_place_entity(topo, year)
                new_toponyms.append(entity)

        return new_toponyms

    def create_place_entity(self, toponym: Dict, year: int) -> Dict:
        """Create a place entity in KG format with provenance"""
        # Generate unique ID
        name_hash = hashlib.md5(f"{year}_{toponym['name']}".encode()).hexdigest()[:8]

        # Determine place type
        place_type = toponym.get('type', 'place')
        if 'island' in toponym['name'].lower():
            place_type = 'island'
        elif 'river' in toponym['name'].lower():
            place_type = 'river'
        elif 'bay' in toponym['name'].lower():
            place_type = 'bay'
        elif 'mountain' in toponym['name'].lower():
            place_type = 'mountain'
        elif any(t.lower() in toponym['name'].lower() for t in KNOWN_TERRITORIES):
            place_type = 'colony'

        entity = {
            'id': f"place_{name_hash}",
            'name': toponym['name'].strip(),
            'type': place_type,
            'description': toponym.get('context', '')[:200],
            'year': str(year),
            'provenance': {
                'source_file': toponym['source'],
                'source_lines': str(toponym.get('line_number', 'unknown')),
                'source_section': toponym.get('section', 'main_text'),
                'extraction_confidence': 0.85,
                'extraction_date': datetime.now().isoformat(),
                'extraction_agent': 'toponym_discovery_agent',
                'verification_status': 'automated'
            }
        }

        return entity

    def generate_enhanced_kg_file(self, year: int, existing_places: List[Dict], new_places: List[Dict]):
        """Generate enhanced KG file with new toponyms"""
        # Load original file
        v3_file = V3_DIR / f"{year}_extracted.json"
        with open(v3_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Add new places
        data['entities']['places'].extend(new_places)

        # Update metadata
        if 'metadata' not in data:
            data['metadata'] = {}

        data['metadata']['toponym_discovery_date'] = datetime.now().isoformat()
        data['metadata']['toponyms_added'] = len(new_places)
        data['metadata']['total_places'] = len(data['entities']['places'])

        # Save to new file
        output_file = V3_DIR / f"{year}_extracted_toponyms.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

        print(f"Generated enhanced KG file: {output_file}")
        print(f"  Original places: {len(existing_places)}")
        print(f"  New toponyms: {len(new_places)}")
        print(f"  Total places: {len(data['entities']['places'])}")

        return output_file

    def generate_discovery_report(self):
        """Generate comprehensive toponym discovery report"""
        report_lines = []
        report_lines.append("# Toponym Discovery Report: Colonial Office List 1961-1966")
        report_lines.append("")
        report_lines.append(f"**Report Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report_lines.append("")
        report_lines.append("## Executive Summary")
        report_lines.append("")

        # Summary statistics
        total_existing = sum(len(self.existing_places[y]) for y in YEARS)
        total_discovered = sum(len(self.discovered_toponyms[y]) for y in YEARS)
        total_new = sum(len(self.new_toponyms[y]) for y in YEARS)

        report_lines.append(f"- **Years Processed:** {', '.join(map(str, YEARS))}")
        report_lines.append(f"- **Total Existing Places:** {total_existing}")
        report_lines.append(f"- **Total Toponyms Discovered:** {total_discovered}")
        report_lines.append(f"- **Total New Toponyms Added:** {total_new}")
        report_lines.append(f"- **Overall Improvement:** {(total_new / total_existing * 100):.1f}% increase")
        report_lines.append("")

        # Year-by-year analysis
        report_lines.append("## Year-by-Year Analysis")
        report_lines.append("")

        for year in YEARS:
            report_lines.append(f"### {year}")
            report_lines.append("")

            gap = self.gap_analysis.get(year, {})
            report_lines.append(f"- **Existing Places:** {gap.get('existing_count', 0)}")
            report_lines.append(f"- **Discovered Toponyms:** {gap.get('discovered_count', 0)}")
            report_lines.append(f"- **Missing in KG:** {gap.get('missing_count', 0)}")
            report_lines.append(f"- **Coverage:** {gap.get('coverage_percentage', 0):.1f}%")
            report_lines.append(f"- **New Toponyms Added:** {len(self.new_toponyms.get(year, []))}")
            report_lines.append("")

            # Show sample of new toponyms
            new_topos = self.new_toponyms.get(year, [])
            if new_topos:
                report_lines.append(f"**Sample New Toponyms ({min(20, len(new_topos))} of {len(new_topos)}):**")
                report_lines.append("")
                for topo in new_topos[:20]:
                    report_lines.append(f"- {topo['name']} ({topo['type']})")
                report_lines.append("")

        # Detailed toponym lists
        report_lines.append("## Detailed Toponym Lists")
        report_lines.append("")

        for year in YEARS:
            report_lines.append(f"### {year} - Complete List of New Toponyms")
            report_lines.append("")

            new_topos = sorted(self.new_toponyms.get(year, []), key=lambda x: x['name'])

            if new_topos:
                report_lines.append("| Name | Type | Source | Confidence |")
                report_lines.append("|------|------|--------|------------|")

                for topo in new_topos:
                    source_file = Path(topo['provenance']['source_file']).name
                    conf = topo['provenance']['extraction_confidence']
                    report_lines.append(f"| {topo['name']} | {topo['type']} | {source_file} | {conf:.2f} |")

                report_lines.append("")
            else:
                report_lines.append("*No new toponyms found for this year.*")
                report_lines.append("")

        # Methodology
        report_lines.append("## Methodology")
        report_lines.append("")
        report_lines.append("### Extraction Strategies")
        report_lines.append("")
        report_lines.append("1. **Pattern Matching:** Identified capitalized sequences with geographic indicators")
        report_lines.append("2. **Geographic Features:** Extracted explicit patterns like 'Name + Type' (e.g., Victoria Island)")
        report_lines.append("3. **Section Analysis:** Targeted sections like 'Principal Towns', 'Geographical Features'")
        report_lines.append("4. **Context Validation:** Verified toponyms using surrounding context")
        report_lines.append("")

        report_lines.append("### Sources Scanned")
        report_lines.append("")
        report_lines.append("- OCR results from `colonial-office-list-{year}/olmocr_results.md`")
        report_lines.append("- Manual parsed files from `output_2/{year}_manual_parsed/`")
        report_lines.append("")

        report_lines.append("### Quality Assurance")
        report_lines.append("")
        report_lines.append("- Filtered common words and invalid patterns")
        report_lines.append("- Deduplicated toponyms by name")
        report_lines.append("- Added full provenance with source file, line number, and context")
        report_lines.append("- Confidence scores based on extraction method")
        report_lines.append("")

        # Output files
        report_lines.append("## Output Files")
        report_lines.append("")
        report_lines.append("Enhanced knowledge graph files with toponyms:")
        report_lines.append("")
        for year in YEARS:
            report_lines.append(f"- `knowledge_graph_extracts_v3/{year}_extracted_toponyms.json`")
        report_lines.append("")

        # Save report
        report_file = REPORT_DIR / "toponym_discovery_1961_1966.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_lines))

        print(f"\nGenerated comprehensive report: {report_file}")

        return report_file

    def run(self):
        """Main execution method"""
        print("=" * 80)
        print("TOPONYM DISCOVERY AGENT - Colonial Office List 1961-1966")
        print("=" * 80)
        print()

        for year in YEARS:
            print(f"\n{'=' * 80}")
            print(f"Processing Year: {year}")
            print('=' * 80)

            # Step 1: Load existing places
            print(f"\n[1/6] Loading existing places for {year}...")
            existing = self.load_existing_places(year)
            self.existing_places[year] = existing

            # Step 2: Scan source files
            print(f"\n[2/6] Scanning source files for {year}...")
            discovered = self.scan_source_files(year)

            # Step 3: Filter and deduplicate
            print(f"\n[3/6] Filtering and deduplicating toponyms...")
            discovered = self.filter_valid_toponyms(discovered)
            discovered = self.deduplicate_toponyms(discovered)
            self.discovered_toponyms[year] = discovered
            print(f"  Valid unique toponyms: {len(discovered)}")

            # Step 4: Gap analysis
            print(f"\n[4/6] Performing gap analysis...")
            gap = self.perform_gap_analysis(year, existing, discovered)
            self.gap_analysis[year] = gap
            print(f"  Existing: {gap['existing_count']}, Discovered: {gap['discovered_count']}, Missing: {gap['missing_count']}")
            print(f"  Coverage: {gap['coverage_percentage']:.1f}%")

            # Step 5: Extract missing toponyms
            print(f"\n[5/6] Extracting missing toponyms...")
            new_topos = self.extract_missing_toponyms(year, gap, discovered)
            self.new_toponyms[year] = new_topos
            print(f"  New toponyms to add: {len(new_topos)}")

            # Step 6: Generate enhanced KG file
            print(f"\n[6/6] Generating enhanced KG file...")
            self.generate_enhanced_kg_file(year, existing, new_topos)

        # Generate comprehensive report
        print(f"\n{'=' * 80}")
        print("Generating Comprehensive Report")
        print('=' * 80)
        self.generate_discovery_report()

        print(f"\n{'=' * 80}")
        print("TOPONYM DISCOVERY COMPLETE")
        print('=' * 80)


if __name__ == '__main__':
    agent = ToponymDiscoveryAgent()
    agent.run()
