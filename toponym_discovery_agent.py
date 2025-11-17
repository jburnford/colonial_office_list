#!/usr/bin/env python3
"""
Toponym Discovery Agent for Colonial Office List Knowledge Graph
Comprehensive extraction of ALL geographic entities from source documents
Years: 1918, 1919, 1921, 1922, 1923, 1924, 1925, 1927
"""

import json
import os
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Set, Tuple
from collections import defaultdict

# Years to process (1920 unavailable)
YEARS = [1918, 1919, 1921, 1922, 1923, 1924, 1925, 1927]

class ToponymDiscoveryAgent:
    """Agent for discovering and extracting all toponyms from Colonial Office Lists"""

    def __init__(self, base_dir: str = "/home/user/colonial_office_list"):
        self.base_dir = Path(base_dir)
        self.output_dir = self.base_dir / "knowledge_graph_extracts_v3"
        self.output_dir.mkdir(exist_ok=True)

        # Comprehensive patterns for geographic entities
        self.toponym_patterns = {
            'island': [
                r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+[Ii]sland[s]?\b',
                r'\b[Ii]sland[s]?\s+of\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b',
            ],
            'city': [
                r'\b(?:city|town|village|settlement)\s+of\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b',
                r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:city|town|village|port)\b',
                r'\bPort\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b',
                r'\bSt\.\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b',
                r'\bSaint\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b',
            ],
            'river': [
                r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+[Rr]iver\b',
                r'\bRiver\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b',
            ],
            'mountain': [
                r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+[Mm]ountain[s]?\b',
                r'\bMount\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b',
                r'\bMt\.\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b',
                r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+[Pp]eak\b',
            ],
            'harbor': [
                r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+[Hh]arbo[u]?r\b',
                r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+[Bb]ay\b',
                r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+[Cc]ove\b',
            ],
            'district': [
                r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+[Dd]istrict\b',
                r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+[Pp]arish\b',
                r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+[Pp]rovince\b',
                r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+[Dd]ivision\b',
            ],
            'colony': [
                r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+[Cc]olony\b',
                r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+[Pp]rotectorate\b',
                r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+[Tt]erritory\b',
                r'\b[Dd]ominion\s+of\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b',
            ],
            'geographic_feature': [
                r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+[Ll]agoon\b',
                r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+[Ss]trait[s]?\b',
                r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+[Cc]hannel\b',
                r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+[Pp]eninsula\b',
                r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+[Cc]ape\b',
                r'\bCape\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b',
            ],
        }

        # Exclude non-British colonial toponyms and common false positives
        self.exclusions = {
            'United States', 'America', 'France', 'Spain', 'Portugal', 'Germany',
            'Belgium', 'Netherlands', 'Holland', 'Italy', 'Russia', 'Japan',
            'China', 'Seville', 'London', 'England', 'Scotland', 'Wales', 'Ireland',
            'Europe', 'Africa', 'Asia', 'Middlesex', 'Surrey', 'Kent',
            'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday',
            'January', 'February', 'March', 'April', 'May', 'June', 'July',
            'August', 'September', 'October', 'November', 'December',
            'British', 'Colonial', 'Imperial', 'Royal', 'Crown', 'Government',
            'Council', 'Legislative', 'Executive', 'Supreme', 'High', 'General',
        }

        # Statistics
        self.stats = defaultdict(lambda: {
            'existing_places': 0,
            'discovered_toponyms': 0,
            'new_toponyms': 0,
            'by_type': defaultdict(int)
        })

    def load_existing_extraction(self, year: int) -> Dict:
        """Load existing v2 extraction for comparison"""
        v2_file = self.base_dir / "knowledge_graph_extracts_v2" / f"{year}_extracted.json"
        if v2_file.exists():
            with open(v2_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {'entities': {'places': []}}

    def get_source_files(self, year: int) -> List[Path]:
        """Get all source markdown files for a year"""
        source_dir = self.base_dir / "output_2" / f"{year}_manual_parsed"
        if source_dir.exists():
            return sorted(source_dir.glob("*.md"))
        return []

    def extract_toponyms_from_text(self, text: str, source_file: str) -> List[Dict]:
        """Extract all toponyms from text with provenance"""
        toponyms = []
        lines = text.split('\n')

        for pattern_type, patterns in self.toponym_patterns.items():
            for pattern in patterns:
                for line_num, line in enumerate(lines, start=1):
                    matches = re.finditer(pattern, line)
                    for match in matches:
                        name = match.group(1).strip()

                        # Skip exclusions and very short names
                        if name in self.exclusions or len(name) < 3:
                            continue

                        # Skip if it's all caps (likely an acronym or section header)
                        if name.isupper() and len(name) > 2:
                            continue

                        toponym = {
                            'name': name,
                            'type': pattern_type,
                            'context': line.strip(),
                            'provenance': {
                                'source_file': source_file,
                                'line_number': line_num,
                                'matched_pattern': pattern
                            }
                        }
                        toponyms.append(toponym)

        return toponyms

    def process_year(self, year: int) -> Dict:
        """Process all source files for a year and extract toponyms"""
        print(f"\n{'='*80}")
        print(f"Processing Year {year}")
        print(f"{'='*80}")

        # Load existing extraction
        existing = self.load_existing_extraction(year)
        existing_places = {p['name'].upper() for p in existing.get('entities', {}).get('places', [])}

        print(f"Existing places in v2: {len(existing_places)}")

        # Get source files
        source_files = self.get_source_files(year)
        print(f"Source files found: {len(source_files)}")

        # Extract toponyms from all files
        all_toponyms = []

        for source_file in source_files:
            colony_name = source_file.stem
            print(f"  Scanning: {colony_name}")

            with open(source_file, 'r', encoding='utf-8') as f:
                text = f.read()

            toponyms = self.extract_toponyms_from_text(text, colony_name)
            all_toponyms.extend(toponyms)
            print(f"    Found {len(toponyms)} toponym mentions")

        # Deduplicate and categorize
        unique_toponyms = {}
        for toponym in all_toponyms:
            name_upper = toponym['name'].upper()
            if name_upper not in unique_toponyms:
                unique_toponyms[name_upper] = {
                    'name': toponym['name'],
                    'type': toponym['type'],
                    'mentions': []
                }
            unique_toponyms[name_upper]['mentions'].append({
                'source_file': toponym['provenance']['source_file'],
                'line_number': toponym['provenance'].get('line_number'),
                'context': toponym['context'][:100]
            })

        # Find new toponyms
        new_toponyms = {
            name: data for name, data in unique_toponyms.items()
            if name not in existing_places
        }

        print(f"\nDiscovery Summary:")
        print(f"  Total unique toponyms found: {len(unique_toponyms)}")
        print(f"  Already in v2 extraction: {len(unique_toponyms) - len(new_toponyms)}")
        print(f"  NEW toponyms discovered: {len(new_toponyms)}")

        # Update statistics
        self.stats[year]['existing_places'] = len(existing_places)
        self.stats[year]['discovered_toponyms'] = len(unique_toponyms)
        self.stats[year]['new_toponyms'] = len(new_toponyms)

        for toponym_data in unique_toponyms.values():
            self.stats[year]['by_type'][toponym_data['type']] += 1

        return {
            'year': year,
            'existing_extraction': existing,
            'all_toponyms': unique_toponyms,
            'new_toponyms': new_toponyms
        }

    def generate_enhanced_kg(self, year_data: Dict) -> Dict:
        """Generate enhanced knowledge graph with new toponyms"""
        year = year_data['year']
        existing = year_data['existing_extraction']
        new_toponyms = year_data['new_toponyms']

        # Start with existing data
        enhanced_kg = existing.copy()

        # Ensure entities structure exists
        if 'entities' not in enhanced_kg:
            enhanced_kg['entities'] = {}
        if 'places' not in enhanced_kg['entities']:
            enhanced_kg['entities']['places'] = []

        # Get next ID
        existing_ids = [p.get('id', '') for p in enhanced_kg['entities']['places']]
        max_id = 0
        for pid in existing_ids:
            if pid.startswith('place_'):
                try:
                    max_id = max(max_id, int(pid.split('_')[1]))
                except:
                    pass

        # Add new toponyms as place entities
        new_place_entities = []
        for idx, (name_upper, toponym_data) in enumerate(sorted(new_toponyms.items()), start=max_id+1):
            place_entity = {
                'id': f'place_{idx:04d}',
                'name': toponym_data['name'],
                'type': toponym_data['type'],
                'year': str(year),
                'discovery_method': 'comprehensive_toponym_scan',
                'mentions': toponym_data['mentions'][:5],
                'mention_count': len(toponym_data['mentions'])
            }
            new_place_entities.append(place_entity)

        # Update metadata
        if 'metadata' not in enhanced_kg:
            enhanced_kg['metadata'] = {}

        enhanced_kg['metadata'].update({
            'year': str(year),
            'version': 'v3_toponym_discovery',
            'extraction_date': datetime.now().isoformat() + 'Z',
            'toponym_discovery': {
                'existing_places': len(enhanced_kg['entities']['places']),
                'new_toponyms_discovered': len(new_place_entities),
                'total_places_v3': len(enhanced_kg['entities']['places']) + len(new_place_entities)
            }
        })

        # Add new places
        enhanced_kg['entities']['places'].extend(new_place_entities)

        # Update entity counts
        if 'entity_count_summary' not in enhanced_kg['metadata']:
            enhanced_kg['metadata']['entity_count_summary'] = {}

        enhanced_kg['metadata']['entity_count_summary']['places'] = len(enhanced_kg['entities']['places'])

        return enhanced_kg

    def save_enhanced_kg(self, year: int, enhanced_kg: Dict):
        """Save enhanced knowledge graph to v3 directory"""
        output_file = self.output_dir / f"{year}_extracted_toponyms.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(enhanced_kg, f, indent=2, ensure_ascii=False)
        print(f"Saved: {output_file}")

    def generate_discovery_report(self):
        """Generate comprehensive discovery report"""
        report_file = self.base_dir / "reports" / "phase_c" / "toponym_discovery_1918_1927.md"

        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# Toponym Discovery Report: Colonial Office Lists 1918-1927\n\n")
            f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("**Mission:** Comprehensive discovery and extraction of ALL toponyms from source documents\n\n")

            f.write("## Executive Summary\n\n")

            total_existing = sum(s['existing_places'] for s in self.stats.values())
            total_discovered = sum(s['discovered_toponyms'] for s in self.stats.values())
            total_new = sum(s['new_toponyms'] for s in self.stats.values())

            f.write(f"- **Years Processed:** {len(YEARS)} ({', '.join(map(str, YEARS))})\n")
            f.write(f"- **Existing Places (v2):** {total_existing}\n")
            f.write(f"- **Total Toponyms Discovered:** {total_discovered}\n")
            f.write(f"- **NEW Toponyms Extracted:** {total_new}\n")
            f.write(f"- **Discovery Rate:** {(total_new/total_discovered*100):.1f}% new toponyms\n\n")

            f.write("## Year-by-Year Analysis\n\n")

            for year in YEARS:
                stats = self.stats[year]
                f.write(f"### {year}\n\n")
                f.write(f"- Existing places (v2): {stats['existing_places']}\n")
                f.write(f"- Total toponyms found: {stats['discovered_toponyms']}\n")
                f.write(f"- **NEW toponyms: {stats['new_toponyms']}**\n")
                f.write(f"- Coverage increase: {(stats['new_toponyms']/max(1,stats['existing_places'])*100):.1f}%\n\n")

                if stats['by_type']:
                    f.write("**Toponyms by Type:**\n\n")
                    for ttype, count in sorted(stats['by_type'].items(), key=lambda x: x[1], reverse=True):
                        f.write(f"- {ttype}: {count}\n")
                    f.write("\n")

            f.write("## Discovery Methodology\n\n")
            f.write("### Pattern-Based Extraction\n\n")
            f.write("Comprehensive regex patterns for:\n")
            f.write("- Islands and archipelagos\n")
            f.write("- Cities, towns, and villages\n")
            f.write("- Rivers and waterways\n")
            f.write("- Mountains and peaks\n")
            f.write("- Harbors, bays, and coves\n")
            f.write("- Districts, parishes, and provinces\n")
            f.write("- Colonies and territories\n")
            f.write("- Geographic features (lagoons, straits, capes, etc.)\n\n")

            f.write("### Exclusions\n\n")
            f.write("Filtered out non-British colonial toponyms:\n")
            f.write("- Non-British countries and territories\n")
            f.write("- British Isles locations (London, England, etc.)\n")
            f.write("- Temporal references (months, days)\n")
            f.write("- Generic administrative terms\n\n")

            f.write("## Provenance\n\n")
            f.write("Every discovered toponym includes:\n")
            f.write("- Source file (colony document)\n")
            f.write("- Exact line number\n")
            f.write("- Context (surrounding text)\n")
            f.write("- Extraction method/pattern\n")
            f.write("- Mention count across documents\n\n")

            f.write("## Output Files\n\n")
            f.write("Enhanced knowledge graphs saved to:\n")
            f.write("```\n")
            f.write("knowledge_graph_extracts_v3/\n")
            for year in YEARS:
                f.write(f"  {year}_extracted_toponyms.json\n")
            f.write("```\n\n")

            f.write("## Next Steps\n\n")
            f.write("1. **Manual Review:** Validate high-mention-count toponyms\n")
            f.write("2. **Relationship Mapping:** Link toponyms to parent colonies/territories\n")
            f.write("3. **Type Refinement:** Further categorize place entities\n")
            f.write("4. **Cross-Year Analysis:** Track toponym changes over time\n")
            f.write("5. **Geographic Validation:** Cross-reference with historical gazetteers\n\n")

            f.write("---\n")
            f.write(f"*Report generated by Toponym Discovery Agent - {datetime.now().isoformat()}*\n")

        print(f"\nReport saved: {report_file}")

    def run(self):
        """Execute full toponym discovery mission"""
        print("="*80)
        print("TOPONYM DISCOVERY AGENT")
        print("Colonial Office List Knowledge Graph Project")
        print("="*80)
        print(f"\nProcessing {len(YEARS)} years: {', '.join(map(str, YEARS))}")
        print(f"Output directory: {self.output_dir}")
        print()

        all_year_data = []

        # Process each year
        for year in YEARS:
            year_data = self.process_year(year)
            all_year_data.append(year_data)

            # Generate and save enhanced KG
            enhanced_kg = self.generate_enhanced_kg(year_data)
            self.save_enhanced_kg(year, enhanced_kg)

        # Generate comprehensive report
        self.generate_discovery_report()

        print("\n" + "="*80)
        print("MISSION COMPLETE")
        print("="*80)
        print(f"\nTotal years processed: {len(YEARS)}")
        print(f"Enhanced KG files: {len(all_year_data)}")
        print(f"Discovery report: reports/phase_c/toponym_discovery_1918_1927.md")
        print()

if __name__ == "__main__":
    agent = ToponymDiscoveryAgent()
    agent.run()
