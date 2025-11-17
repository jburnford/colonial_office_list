#!/usr/bin/env python3
"""
Toponym Discovery Agent for Colonial Office List Knowledge Graph
Comprehensive extraction of ALL toponyms from 1950-1959 source documents
"""

import json
import re
import os
from pathlib import Path
from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Set, Tuple

# Years to process
TARGET_YEARS = [1950, 1951, 1953, 1954, 1956, 1957, 1959]

# Base paths
BASE_DIR = Path("/home/user/colonial_office_list")
SOURCE_DIR = BASE_DIR / "output_2"
KG_V3_DIR = BASE_DIR / "knowledge_graph_extracts_v3"
OUTPUT_DIR = BASE_DIR / "knowledge_graph_extracts_v3"
REPORT_DIR = BASE_DIR / "reports" / "phase_c"

# Ensure directories exist
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
REPORT_DIR.mkdir(parents=True, exist_ok=True)


class ToponymDiscoveryAgent:
    """Agent for comprehensive toponym discovery"""

    def __init__(self, year: int):
        self.year = year
        self.source_path = SOURCE_DIR / f"{year}_manual_parsed"
        self.existing_kg_path = KG_V3_DIR / f"{year}_extracted.json"
        self.existing_places = {}
        self.existing_place_names = set()
        self.discovered_toponyms = []
        self.statistics = {
            'existing_places': 0,
            'source_files_scanned': 0,
            'new_toponyms_found': 0,
            'total_toponyms': 0
        }

    def load_existing_kg(self):
        """Load existing knowledge graph to identify already-extracted places"""
        if not self.existing_kg_path.exists():
            print(f"Warning: No existing KG found for {self.year}")
            return

        with open(self.existing_kg_path, 'r', encoding='utf-8') as f:
            kg_data = json.load(f)

        places = kg_data.get('entities', {}).get('places', [])
        self.statistics['existing_places'] = len(places)

        for place in places:
            place_id = place.get('id', '')
            name = place.get('name', '')
            self.existing_places[place_id] = place
            # Normalize name for matching
            self.existing_place_names.add(name.lower().strip())

        print(f"Loaded {len(places)} existing places for {self.year}")

    def extract_toponyms_from_text(self, text: str, source_file: str) -> List[Dict]:
        """Extract all toponyms from text using comprehensive pattern matching"""
        toponyms = []

        # Pattern 1: Capitalized words and phrases (proper nouns)
        # Match sequences of capitalized words
        proper_noun_pattern = r'\b[A-Z][a-z]*(?:\s+[A-Z][a-z]*)*(?:\s+[A-Z][A-Z]+)*\b'

        # Pattern 2: Geographic indicators
        geo_indicators = [
            r'(?:Island|Islands|Isle|Isles)\s+of\s+([A-Z][a-zA-Z\s]+)',
            r'([A-Z][a-zA-Z\s]+)\s+(?:Island|Islands|Isle|Isles)',
            r'(?:Mount|Mt\.?|Mountain)\s+([A-Z][a-zA-Z\s]+)',
            r'([A-Z][a-zA-Z\s]+)\s+(?:Mountain|Mountains|Range)',
            r'(?:River|R\.)\s+([A-Z][a-zA-Z\s]+)',
            r'([A-Z][a-zA-Z\s]+)\s+River',
            r'(?:Bay|Gulf|Sound|Strait|Straits)\s+of\s+([A-Z][a-zA-Z\s]+)',
            r'([A-Z][a-zA-Z\s]+)\s+(?:Bay|Gulf|Sound|Harbour|Harbor)',
            r'(?:Lake|Loch)\s+([A-Z][a-zA-Z\s]+)',
            r'([A-Z][a-zA-Z\s]+)\s+Lake',
            r'(?:District|Province|Territory|Region|State)\s+of\s+([A-Z][a-zA-Z\s]+)',
            r'([A-Z][a-zA-Z\s]+)\s+(?:District|Province|Territory|Region|State)',
            r'(?:Colony|Protectorate)\s+of\s+([A-Z][a-zA-Z\s]+)',
            r'([A-Z][a-zA-Z\s]+)\s+(?:Colony|Protectorate)',
            r'(?:Peninsula|Peninsulas)\s+of\s+([A-Z][a-zA-Z\s]+)',
            r'([A-Z][a-zA-Z\s]+)\s+Peninsula',
            r'(?:Coast)\s+of\s+([A-Z][a-zA-Z\s]+)',
            r'([A-Z][a-zA-Z\s]+)\s+Coast',
            r'(?:Port)\s+(?:of\s+)?([A-Z][a-zA-Z\s]+)',
            r'(?:Cape)\s+([A-Z][a-zA-Z\s]+)',
            r'([A-Z][a-zA-Z\s]+)\s+Point',
        ]

        # Extract using geographic indicators
        for pattern in geo_indicators:
            matches = re.finditer(pattern, text, re.MULTILINE)
            for match in matches:
                full_match = match.group(0)
                toponyms.append({
                    'name': full_match.strip(),
                    'source_file': source_file,
                    'context': self._get_context(text, match.start(), match.end())
                })

        # Pattern 3: Words following "in", "at", "near", "from", "to" that are capitalized
        location_preposition_pattern = r'\b(?:in|at|near|from|to|via|between)\s+([A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+){0,3})'
        matches = re.finditer(location_preposition_pattern, text)
        for match in matches:
            name = match.group(1).strip()
            if len(name) > 2:  # Filter out very short matches
                toponyms.append({
                    'name': name,
                    'source_file': source_file,
                    'context': self._get_context(text, match.start(), match.end())
                })

        # Pattern 4: Words in sections about geography, history, administration
        lines = text.split('\n')
        in_geo_section = False
        for i, line in enumerate(lines):
            line_lower = line.lower()
            # Detect geographic sections
            if any(keyword in line_lower for keyword in ['situation', 'area', 'geography', 'climate', 'general description', 'divisions', 'population', 'districts', 'provinces', 'islands']):
                in_geo_section = True
            elif line.isupper() and len(line) > 5:  # New section header
                in_geo_section = False

            if in_geo_section:
                # Extract capitalized terms
                words = re.findall(r'\b[A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)*\b', line)
                for word in words:
                    if len(word) > 2 and word not in ['The', 'A', 'An', 'In', 'At', 'Of', 'On', 'To', 'From']:
                        toponyms.append({
                            'name': word,
                            'source_file': source_file,
                            'context': line.strip(),
                            'line_number': i + 1
                        })

        return toponyms

    def _get_context(self, text: str, start: int, end: int, window: int = 100) -> str:
        """Get context around a match"""
        context_start = max(0, start - window)
        context_end = min(len(text), end + window)
        context = text[context_start:context_end]
        return context.strip()

    def classify_toponym_type(self, name: str, context: str) -> str:
        """Classify toponym by type based on name and context"""
        name_lower = name.lower()
        context_lower = context.lower()

        # Island types
        if any(word in name_lower for word in ['island', 'isle']) or \
           any(word in context_lower for word in ['island', 'isle', 'archipelago']):
            return 'island'

        # Water bodies
        if any(word in name_lower for word in ['river', 'bay', 'gulf', 'strait', 'sound', 'harbour', 'harbor', 'lake', 'sea']):
            return 'water_body'
        if any(word in context_lower for word in ['river', 'bay', 'gulf', 'strait', 'sound', 'harbour', 'harbor', 'lake']):
            return 'water_body'

        # Mountains/topographic features
        if any(word in name_lower for word in ['mount', 'mountain', 'hill', 'peak', 'range', 'jabal', 'jebel']):
            return 'mountain'
        if any(word in context_lower for word in ['mountain', 'hill', 'peak', 'summit', 'elevation', 'feet high']):
            return 'mountain'

        # Administrative divisions
        if any(word in name_lower for word in ['district', 'province', 'territory', 'region', 'state', 'colony', 'protectorate', 'division']):
            return 'administrative_division'
        if any(word in context_lower for word in ['district', 'province', 'territory', 'administered', 'government']):
            return 'administrative_division'

        # Settlements/towns/cities
        if any(word in name_lower for word in ['town', 'city', 'village', 'settlement']):
            return 'settlement'
        if any(word in context_lower for word in ['town', 'city', 'village', 'settlement', 'population', 'inhabitants']):
            return 'settlement'

        # Geographic features
        if any(word in name_lower for word in ['peninsula', 'cape', 'point', 'coast', 'shore', 'beach']):
            return 'geographic_feature'
        if any(word in context_lower for word in ['peninsula', 'cape', 'point', 'coast']):
            return 'geographic_feature'

        # Ports/harbours
        if any(word in name_lower for word in ['port', 'harbour', 'harbor', 'wharf', 'pier']):
            return 'port'

        # Default
        return 'place'

    def is_likely_place_name(self, name: str, context: str) -> bool:
        """Filter out non-geographic proper nouns"""
        name_lower = name.lower()

        # Exclude common non-place proper nouns
        exclude_patterns = [
            r'^(Mr|Mrs|Miss|Ms|Dr|Sir|Lady|Lord|Duke|Earl|Baron|His|Her|The|A|An|In|On|At|To|From|With|By|For)$',
            r'^(January|February|March|April|May|June|July|August|September|October|November|December)$',
            r'^(Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)$',
            r'^(British|English|French|German|Dutch|Spanish|Portuguese|Italian|American|European|Asian|African)$',
            r'^(Government|Department|Ministry|Office|Council|Committee|Board|Commission|Authority|Trust|Company|Association)$',
            r'^(Act|Order|Ordinance|Law|Regulation|Instructions|Code|Treaty)$',
            r'^(Majesty|Highness|Excellency|Honour|Honor)$',
            r'^\d+$',  # Pure numbers
        ]

        for pattern in exclude_patterns:
            if re.match(pattern, name, re.IGNORECASE):
                return False

        # Must be at least 3 characters
        if len(name) < 3:
            return False

        # Check if it appears in a geographic context
        geo_keywords = ['situated', 'located', 'lies', 'extends', 'coast', 'island', 'river', 'mountain',
                       'district', 'territory', 'colony', 'protectorate', 'town', 'city', 'village',
                       'port', 'harbour', 'bay', 'peninsula', 'latitude', 'longitude', 'area', 'population']

        context_lower = context.lower()
        has_geo_context = any(keyword in context_lower for keyword in geo_keywords)

        return has_geo_context or any(word in name_lower for word in ['island', 'mount', 'cape', 'port', 'bay', 'river'])

    def scan_all_sources(self):
        """Scan all source files for the year"""
        if not self.source_path.exists():
            print(f"Warning: Source path not found: {self.source_path}")
            return

        all_raw_toponyms = []

        # Get all .md files
        source_files = list(self.source_path.glob("*.md"))
        self.statistics['source_files_scanned'] = len(source_files)

        print(f"\nScanning {len(source_files)} source files for {self.year}...")

        for source_file in source_files:
            try:
                with open(source_file, 'r', encoding='utf-8') as f:
                    text = f.read()

                # Extract toponyms
                toponyms = self.extract_toponyms_from_text(text, source_file.name)
                all_raw_toponyms.extend(toponyms)

            except Exception as e:
                print(f"Error reading {source_file.name}: {e}")

        print(f"Extracted {len(all_raw_toponyms)} raw toponym mentions")

        # Deduplicate and filter
        toponym_dict = defaultdict(lambda: {'sources': [], 'contexts': []})

        for topo in all_raw_toponyms:
            name = topo['name']
            normalized_name = name.strip()

            # Check if likely a place name
            if self.is_likely_place_name(normalized_name, topo.get('context', '')):
                toponym_dict[normalized_name]['sources'].append(topo['source_file'])
                toponym_dict[normalized_name]['contexts'].append(topo.get('context', ''))

        print(f"Identified {len(toponym_dict)} unique potential toponyms")

        # Check against existing places
        for name, info in toponym_dict.items():
            name_lower = name.lower()

            # Check if already in KG
            if name_lower not in self.existing_place_names:
                # New toponym!
                # Get best context for classification
                context = info['contexts'][0] if info['contexts'] else ''
                toponym_type = self.classify_toponym_type(name, context)

                self.discovered_toponyms.append({
                    'name': name,
                    'type': toponym_type,
                    'year': str(self.year),
                    'sources': list(set(info['sources'])),
                    'mention_count': len(info['sources']),
                    'sample_context': context[:200] if context else ''
                })

        self.statistics['new_toponyms_found'] = len(self.discovered_toponyms)
        self.statistics['total_toponyms'] = len(toponym_dict)

        print(f"Found {len(self.discovered_toponyms)} NEW toponyms not in existing KG")

    def generate_enhanced_kg(self) -> Dict:
        """Generate enhanced knowledge graph with new toponyms"""
        # Load existing KG
        if self.existing_kg_path.exists():
            with open(self.existing_kg_path, 'r', encoding='utf-8') as f:
                kg_data = json.load(f)
        else:
            kg_data = {
                'metadata': {
                    'year': str(self.year),
                    'extraction_date': datetime.now().isoformat(),
                },
                'entities': {
                    'places': [],
                    'people': [],
                    'organizations': [],
                    'events': []
                }
            }

        # Add new toponyms
        existing_places = kg_data['entities'].get('places', [])
        new_place_id_start = len(existing_places) + 1

        for i, toponym in enumerate(self.discovered_toponyms):
            place_id = f"place_discovered_{new_place_id_start + i}_{toponym['name'].lower().replace(' ', '_').replace(',', '').replace('.', '')}"

            new_place = {
                'id': place_id,
                'name': toponym['name'],
                'type': toponym['type'],
                'year': toponym['year'],
                'parent_location': None,  # Will need manual linking
                'description': f"Discovered from comprehensive toponym scan. Context: {toponym['sample_context']}",
                'provenance': {
                    'source_files': toponym['sources'],
                    'mention_count': toponym['mention_count'],
                    'extraction_confidence': 0.75,  # Medium confidence for automated discovery
                    'extraction_date': datetime.now().strftime('%Y-%m-%d'),
                    'extraction_agent': 'toponym_discovery_agent',
                    'verification_status': 'automated_discovery',
                    'notes': 'Discovered via comprehensive toponym scanning - requires manual verification'
                }
            }

            existing_places.append(new_place)

        kg_data['entities']['places'] = existing_places

        # Update metadata
        kg_data['metadata']['toponym_discovery'] = {
            'discovery_date': datetime.now().isoformat(),
            'new_toponyms_added': len(self.discovered_toponyms),
            'total_places': len(existing_places),
            'discovery_agent': 'toponym_discovery_agent_v1'
        }

        return kg_data

    def save_enhanced_kg(self, kg_data: Dict):
        """Save enhanced knowledge graph"""
        output_file = OUTPUT_DIR / f"{self.year}_extracted_toponyms.json"

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(kg_data, f, indent=2, ensure_ascii=False)

        print(f"Saved enhanced KG to {output_file}")

    def get_summary(self) -> Dict:
        """Get summary statistics"""
        return {
            'year': self.year,
            **self.statistics,
            'new_toponyms_sample': self.discovered_toponyms[:10] if self.discovered_toponyms else []
        }


def main():
    """Main execution"""
    print("="*80)
    print("TOPONYM DISCOVERY AGENT - Colonial Office List Knowledge Graph")
    print("="*80)
    print(f"Processing years: {TARGET_YEARS}")
    print()

    all_summaries = []

    for year in TARGET_YEARS:
        print(f"\n{'='*80}")
        print(f"Processing year: {year}")
        print(f"{'='*80}")

        agent = ToponymDiscoveryAgent(year)

        # Load existing KG
        agent.load_existing_kg()

        # Scan sources for toponyms
        agent.scan_all_sources()

        # Generate enhanced KG
        enhanced_kg = agent.generate_enhanced_kg()

        # Save enhanced KG
        agent.save_enhanced_kg(enhanced_kg)

        # Get summary
        summary = agent.get_summary()
        all_summaries.append(summary)

        print(f"\nSummary for {year}:")
        print(f"  Existing places: {summary['existing_places']}")
        print(f"  Source files scanned: {summary['source_files_scanned']}")
        print(f"  Total toponyms identified: {summary['total_toponyms']}")
        print(f"  New toponyms discovered: {summary['new_toponyms_found']}")

    # Generate comprehensive report
    print(f"\n{'='*80}")
    print("Generating comprehensive report...")
    print(f"{'='*80}")

    report_file = REPORT_DIR / "toponym_discovery_1950_1959.md"

    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# Toponym Discovery Report: Colonial Office List 1950-1959\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"**Agent:** Toponym Discovery Agent v1.0\n\n")

        f.write("## Executive Summary\n\n")

        total_existing = sum(s['existing_places'] for s in all_summaries)
        total_new = sum(s['new_toponyms_found'] for s in all_summaries)
        total_files = sum(s['source_files_scanned'] for s in all_summaries)
        total_identified = sum(s['total_toponyms'] for s in all_summaries)

        f.write(f"- **Years Processed:** {', '.join(map(str, TARGET_YEARS))}\n")
        f.write(f"- **Source Files Scanned:** {total_files}\n")
        f.write(f"- **Existing Places in KG:** {total_existing}\n")
        f.write(f"- **Total Toponyms Identified:** {total_identified}\n")
        f.write(f"- **New Toponyms Discovered:** {total_new}\n")
        f.write(f"- **Discovery Rate:** {(total_new/total_identified*100):.1f}%\n\n")

        f.write("## Year-by-Year Breakdown\n\n")
        f.write("| Year | Existing Places | Files Scanned | Toponyms Identified | New Discoveries |\n")
        f.write("|------|----------------|---------------|---------------------|----------------|\n")

        for summary in all_summaries:
            f.write(f"| {summary['year']} | {summary['existing_places']} | {summary['source_files_scanned']} | {summary['total_toponyms']} | {summary['new_toponyms_found']} |\n")

        f.write("\n## Detailed Findings\n\n")

        for summary in all_summaries:
            f.write(f"### Year {summary['year']}\n\n")
            f.write(f"**Statistics:**\n")
            f.write(f"- Existing places: {summary['existing_places']}\n")
            f.write(f"- New discoveries: {summary['new_toponyms_found']}\n\n")

            if summary['new_toponyms_sample']:
                f.write(f"**Sample New Toponyms (first 10):**\n\n")
                for topo in summary['new_toponyms_sample']:
                    f.write(f"- **{topo['name']}** ({topo['type']})\n")
                    f.write(f"  - Sources: {', '.join(topo['sources'][:3])}\n")
                    f.write(f"  - Mentions: {topo['mention_count']}\n")
                    if topo['sample_context']:
                        f.write(f"  - Context: {topo['sample_context'][:150]}...\n")
                    f.write("\n")

            f.write("\n")

        f.write("## Methodology\n\n")
        f.write("### Extraction Approach\n\n")
        f.write("1. **Pattern-Based Extraction:**\n")
        f.write("   - Geographic indicators (Island, Bay, River, Mountain, etc.)\n")
        f.write("   - Locational prepositions (in, at, near, from, to)\n")
        f.write("   - Proper noun sequences in geographic contexts\n\n")

        f.write("2. **Classification:**\n")
        f.write("   - island, water_body, mountain, administrative_division\n")
        f.write("   - settlement, geographic_feature, port, place\n\n")

        f.write("3. **Filtering:**\n")
        f.write("   - Excluded non-geographic proper nouns\n")
        f.write("   - Required geographic context keywords\n")
        f.write("   - Minimum length requirements\n\n")

        f.write("4. **Deduplication:**\n")
        f.write("   - Compared against existing KG entities\n")
        f.write("   - Case-insensitive matching\n\n")

        f.write("## Output Files\n\n")
        f.write("Enhanced knowledge graph files generated:\n\n")
        for year in TARGET_YEARS:
            f.write(f"- `knowledge_graph_extracts_v3/{year}_extracted_toponyms.json`\n")

        f.write("\n## Next Steps\n\n")
        f.write("1. **Manual Verification:** Review automated discoveries for accuracy\n")
        f.write("2. **Parent Location Linking:** Establish hierarchical relationships\n")
        f.write("3. **Coordinate Enrichment:** Add geographic coordinates where possible\n")
        f.write("4. **Merge with Main KG:** Integrate verified toponyms into primary knowledge graph\n\n")

        f.write("## Notes\n\n")
        f.write("- All discovered toponyms marked with `verification_status: 'automated_discovery'`\n")
        f.write("- Extraction confidence set to 0.75 (medium) for automated discoveries\n")
        f.write("- Manual review recommended before final integration\n")

    print(f"\nReport saved to {report_file}")
    print("\n" + "="*80)
    print("TOPONYM DISCOVERY COMPLETE")
    print("="*80)


if __name__ == "__main__":
    main()
