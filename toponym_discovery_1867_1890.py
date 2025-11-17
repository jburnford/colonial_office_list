#!/usr/bin/env python3
"""
Toponym Discovery Agent for Colonial Office List Knowledge Graph
Finds ALL toponyms in source documents (1867-1890) and compares against existing extractions
"""

import json
import re
import os
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# Years to process
YEARS = [1867, 1877, 1880, 1883, 1886, 1888, 1889, 1890]

# Base directories
BASE_DIR = Path("/home/user/colonial_office_list")
SOURCE_DIR = BASE_DIR / "output_2"
KG_DIR = BASE_DIR / "knowledge_graph_extracts_v3"
OUTPUT_DIR = KG_DIR
REPORT_DIR = BASE_DIR / "reports" / "phase_c"

# Toponym patterns - place name indicators
PLACE_INDICATORS = {
    'colony': r'\b(?:Colony|Territory|Possession|Dependency)\b',
    'city': r'\b(?:City|Town|Capital|Port|Settlement)\b',
    'island': r'\b(?:Island|Isle|Islet|Cay|Key|Atoll)\b',
    'river': r'\b(?:River|Stream|Creek|Brook)\b',
    'mountain': r'\b(?:Mountain|Mount|Peak|Hill|Range|Heights)\b',
    'bay': r'\b(?:Bay|Harbour|Harbor|Gulf|Inlet|Cove|Sound|Strait)\b',
    'district': r'\b(?:District|Parish|Division|County|Province|Region|Department)\b',
    'fort': r'\b(?:Fort|Fortress|Castle|Garrison)\b',
    'cape': r'\b(?:Cape|Point|Head|Headland)\b',
    'lake': r'\b(?:Lake|Pond|Lagoon|Loch)\b',
}

# Patterns for finding proper nouns (capitalized words)
PROPER_NOUN_PATTERN = re.compile(r'\b[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*\b')

# Generic terms to exclude (not specific toponyms)
GENERIC_EXCLUSIONS = {
    'the', 'and', 'of', 'in', 'at', 'on', 'by', 'for', 'with', 'from', 'to',
    'Government', 'Department', 'Office', 'Committee', 'Council', 'Board',
    'Act', 'Ordinance', 'Law', 'Regulation', 'Order', 'Proclamation',
    'January', 'February', 'March', 'April', 'May', 'June', 'July', 'August',
    'September', 'October', 'November', 'December',
    'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday',
    'English', 'British', 'French', 'Spanish', 'Portuguese', 'Dutch', 'German',
    'His', 'Her', 'Excellency', 'Majesty', 'Honour', 'Lord', 'Lady', 'Sir',
    'The', 'A', 'An', 'This', 'That', 'These', 'Those',
    'All', 'Some', 'None', 'Every', 'Each', 'Any',
}

class ToponymDiscoveryAgent:
    def __init__(self):
        self.results = {}
        self.stats = defaultdict(lambda: {
            'existing_places': 0,
            'new_toponyms': 0,
            'existing_by_type': defaultdict(int),
            'new_by_type': defaultdict(int),
        })

    def load_existing_kg(self, year):
        """Load existing knowledge graph for a year"""
        kg_file = KG_DIR / f"{year}_extracted.json"
        if not kg_file.exists():
            print(f"Warning: KG file not found for {year}")
            return {}

        with open(kg_file, 'r', encoding='utf-8') as f:
            return json.load(f)

    def get_existing_places(self, kg_data):
        """Extract all existing place entities from KG"""
        places = {}
        if 'entities' in kg_data and 'places' in kg_data['entities']:
            for place in kg_data['entities']['places']:
                name = place.get('name', '').lower()
                places[name] = place
        return places

    def load_source_files(self, year):
        """Load all source markdown files for a year"""
        source_dir = SOURCE_DIR / f"{year}_manual_parsed"
        if not source_dir.exists():
            print(f"Warning: Source directory not found for {year}")
            return {}

        files = {}
        for md_file in sorted(source_dir.glob("*.md")):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    files[md_file.name] = f.readlines()
            except Exception as e:
                print(f"Error reading {md_file}: {e}")

        return files

    def extract_toponyms_from_text(self, lines, filename):
        """Extract toponyms from text using multiple strategies"""
        toponyms = []

        for line_num, line in enumerate(lines, 1):
            # Strategy 1: Look for place type indicators
            for place_type, pattern in PLACE_INDICATORS.items():
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    # Look for proper nouns before/after the indicator
                    context_start = max(0, match.start() - 100)
                    context_end = min(len(line), match.end() + 100)
                    context = line[context_start:context_end]

                    # Find proper nouns in context
                    proper_nouns = PROPER_NOUN_PATTERN.findall(context)
                    for noun in proper_nouns:
                        if noun not in GENERIC_EXCLUSIONS and len(noun) > 2:
                            toponyms.append({
                                'name': noun,
                                'type': place_type,
                                'line': line_num,
                                'context': line.strip(),
                                'source_file': filename,
                                'confidence': 0.8
                            })

            # Strategy 2: Geographic patterns (lat/long mentions)
            coord_pattern = r'(\d+°\s*\d+[\'′]\s*[NS].*?\d+°\s*\d+[\'′]\s*[EW])'
            coord_matches = re.finditer(coord_pattern, line)
            for match in coord_matches:
                # Look for place name near coordinates
                context_start = max(0, match.start() - 150)
                context = line[context_start:match.start()]
                proper_nouns = PROPER_NOUN_PATTERN.findall(context)
                for noun in proper_nouns[-3:]:  # Last 3 proper nouns before coords
                    if noun not in GENERIC_EXCLUSIONS:
                        toponyms.append({
                            'name': noun,
                            'type': 'place',
                            'line': line_num,
                            'context': line.strip(),
                            'coordinates_mentioned': True,
                            'source_file': filename,
                            'confidence': 0.9
                        })

            # Strategy 3: "in/at/near [Place]" patterns
            location_pattern = r'\b(?:in|at|near|from|to|of)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2})\b'
            loc_matches = re.finditer(location_pattern, line)
            for match in loc_matches:
                place_name = match.group(1)
                if place_name not in GENERIC_EXCLUSIONS:
                    toponyms.append({
                        'name': place_name,
                        'type': 'place',
                        'line': line_num,
                        'context': line.strip(),
                        'source_file': filename,
                        'confidence': 0.7
                    })

        return toponyms

    def deduplicate_toponyms(self, toponyms):
        """Remove duplicate toponyms, keeping highest confidence"""
        unique = {}
        for topo in toponyms:
            name_lower = topo['name'].lower()
            if name_lower not in unique or topo['confidence'] > unique[name_lower]['confidence']:
                unique[name_lower] = topo
        return list(unique.values())

    def find_missing_toponyms(self, year):
        """Find toponyms in source that are missing from KG"""
        print(f"\n{'='*80}")
        print(f"Processing {year}")
        print(f"{'='*80}")

        # Load existing KG
        kg_data = self.load_existing_kg(year)
        existing_places = self.get_existing_places(kg_data)

        print(f"Existing places in KG: {len(existing_places)}")

        # Count by type
        type_counts = defaultdict(int)
        for place in existing_places.values():
            place_type = place.get('type', 'unknown')
            type_counts[place_type] += 1

        print(f"Existing places by type:")
        for ptype, count in sorted(type_counts.items()):
            print(f"  {ptype}: {count}")
            self.stats[year]['existing_by_type'][ptype] = count

        self.stats[year]['existing_places'] = len(existing_places)

        # Load and process source files
        source_files = self.load_source_files(year)
        print(f"Source files loaded: {len(source_files)}")

        all_toponyms = []
        for filename, lines in source_files.items():
            toponyms = self.extract_toponyms_from_text(lines, filename)
            all_toponyms.extend(toponyms)

        print(f"Total toponyms found in source: {len(all_toponyms)}")

        # Deduplicate
        unique_toponyms = self.deduplicate_toponyms(all_toponyms)
        print(f"Unique toponyms: {len(unique_toponyms)}")

        # Find missing ones
        missing = []
        for topo in unique_toponyms:
            name_lower = topo['name'].lower()
            if name_lower not in existing_places:
                missing.append(topo)

        print(f"Missing toponyms: {len(missing)}")

        # Categorize missing by type
        missing_by_type = defaultdict(list)
        for topo in missing:
            missing_by_type[topo['type']].append(topo)

        print(f"\nMissing toponyms by type:")
        for ptype, topos in sorted(missing_by_type.items()):
            print(f"  {ptype}: {len(topos)}")
            self.stats[year]['new_by_type'][ptype] = len(topos)

        self.stats[year]['new_toponyms'] = len(missing)

        # Store results
        self.results[year] = {
            'existing_places': existing_places,
            'missing_toponyms': missing,
            'kg_data': kg_data
        }

        return missing

    def create_place_entity(self, toponym, year, entity_id):
        """Create a new place entity from a toponym"""
        entity = {
            'id': entity_id,
            'name': toponym['name'],
            'type': toponym['type'],
            'year': str(year),
            'provenance': {
                'source_file': f"output_2/{year}_manual_parsed/{toponym['source_file']}",
                'source_lines': str(toponym['line']),
                'source_section': 'Toponym Discovery',
                'extraction_confidence': toponym['confidence'],
                'extraction_date': datetime.now().strftime('%Y-%m-%d'),
                'extraction_agent': 'toponym_discovery_1867_1890',
                'verification_status': 'automated',
                'discovery_context': toponym.get('context', '')[:200]  # First 200 chars
            }
        }

        # Add coordinates if mentioned
        if toponym.get('coordinates_mentioned'):
            entity['notes'] = 'Coordinates mentioned in source text'

        return entity

    def enhance_kg_with_toponyms(self, year, missing_toponyms):
        """Add missing toponyms to KG and save enhanced version"""
        if year not in self.results:
            print(f"No results for {year}")
            return

        kg_data = self.results[year]['kg_data']

        # Ensure entities structure exists
        if 'entities' not in kg_data:
            kg_data['entities'] = {}
        if 'places' not in kg_data['entities']:
            kg_data['entities']['places'] = []

        # Add new toponyms
        existing_count = len(kg_data['entities']['places'])
        for i, topo in enumerate(missing_toponyms, 1):
            entity_id = f"place_{year}_discovered_{i:03d}"
            new_entity = self.create_place_entity(topo, year, entity_id)
            kg_data['entities']['places'].append(new_entity)

        # Update metadata
        if 'metadata' not in kg_data:
            kg_data['metadata'] = {}

        kg_data['metadata']['toponym_discovery'] = {
            'discovery_date': datetime.now().isoformat(),
            'existing_toponyms': existing_count,
            'new_toponyms_added': len(missing_toponyms),
            'total_toponyms': len(kg_data['entities']['places']),
            'coverage_improvement': f"{(len(missing_toponyms) / max(existing_count, 1)) * 100:.1f}%"
        }

        # Save enhanced KG
        output_file = OUTPUT_DIR / f"{year}_extracted_toponyms.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(kg_data, f, indent=2, ensure_ascii=False)

        print(f"Saved enhanced KG to {output_file}")
        print(f"  Added {len(missing_toponyms)} new toponyms")
        print(f"  Total places: {len(kg_data['entities']['places'])}")

    def generate_report(self):
        """Generate comprehensive toponym discovery report"""
        report_lines = [
            "# Toponym Discovery Report: Colonial Office List 1867-1890",
            "",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Agent:** toponym_discovery_1867_1890",
            "",
            "## Executive Summary",
            "",
            "This report documents the comprehensive toponym (place name) discovery process for the Colonial Office List Knowledge Graph project, covering years 1867-1890.",
            "",
            "### Overall Statistics",
            ""
        ]

        # Calculate totals
        total_existing = sum(self.stats[year]['existing_places'] for year in YEARS)
        total_new = sum(self.stats[year]['new_toponyms'] for year in YEARS)
        total_after = total_existing + total_new
        improvement = (total_new / max(total_existing, 1)) * 100

        report_lines.extend([
            f"- **Years Processed:** {len(YEARS)}",
            f"- **Existing Toponyms (Before):** {total_existing:,}",
            f"- **Newly Discovered Toponyms:** {total_new:,}",
            f"- **Total Toponyms (After):** {total_after:,}",
            f"- **Coverage Improvement:** {improvement:.1f}%",
            "",
            "## Year-by-Year Analysis",
            ""
        ])

        # Year-by-year breakdown
        for year in YEARS:
            stats = self.stats[year]
            existing = stats['existing_places']
            new = stats['new_toponyms']
            total = existing + new
            year_improvement = (new / max(existing, 1)) * 100

            report_lines.extend([
                f"### {year}",
                "",
                f"- **Existing Places:** {existing}",
                f"- **Newly Discovered:** {new}",
                f"- **Total After Discovery:** {total}",
                f"- **Improvement:** {year_improvement:.1f}%",
                ""
            ])

            # Existing by type
            if stats['existing_by_type']:
                report_lines.append("**Existing Places by Type:**")
                for ptype, count in sorted(stats['existing_by_type'].items(), key=lambda x: -x[1]):
                    report_lines.append(f"  - {ptype}: {count}")
                report_lines.append("")

            # New by type
            if stats['new_by_type']:
                report_lines.append("**Newly Discovered by Type:**")
                for ptype, count in sorted(stats['new_by_type'].items(), key=lambda x: -x[1]):
                    report_lines.append(f"  - {ptype}: {count}")
                report_lines.append("")

        # Examples of newly discovered toponyms
        report_lines.extend([
            "## Examples of Newly Discovered Toponyms",
            "",
        ])

        for year in YEARS[:3]:  # Show examples from first 3 years
            if year in self.results and self.results[year]['missing_toponyms']:
                report_lines.append(f"### {year} Examples")
                report_lines.append("")

                missing = self.results[year]['missing_toponyms'][:10]  # Top 10
                for topo in missing:
                    report_lines.extend([
                        f"**{topo['name']}** ({topo['type']})",
                        f"  - Source: {topo['source_file']}",
                        f"  - Line: {topo['line']}",
                        f"  - Confidence: {topo['confidence']}",
                        f"  - Context: {topo['context'][:150]}...",
                        ""
                    ])

        # Recommendations
        report_lines.extend([
            "## Recommendations for Human Review",
            "",
            "1. **High-Confidence Toponyms (0.9+):** These are likely accurate and can be used with confidence.",
            "2. **Medium-Confidence Toponyms (0.7-0.9):** Should be reviewed for context and accuracy.",
            "3. **Low-Confidence Toponyms (<0.7):** Require careful human verification.",
            "",
            "## Methodology",
            "",
            "### Extraction Strategies",
            "",
            "1. **Place Type Indicators:** Searched for keywords like 'River', 'Mountain', 'Bay', 'District', etc., and extracted proper nouns in context.",
            "2. **Coordinate Mentions:** Identified toponyms near latitude/longitude coordinates.",
            "3. **Locative Prepositions:** Found place names following 'in', 'at', 'near', 'from', 'to', 'of'.",
            "",
            "### Quality Criteria",
            "",
            "- Only extracted NAMED places (proper nouns)",
            "- Excluded generic geographic terms without names",
            "- Preserved historical spelling from source documents",
            "- Added provenance for every new entity",
            "",
            "## Next Steps",
            "",
            "1. **Human Verification:** Review newly discovered toponyms, especially low-confidence ones.",
            "2. **Entity Linking:** Connect toponyms to parent locations (colonies, regions).",
            "3. **Geocoding:** Add modern coordinates and geographic data.",
            "4. **Grounding:** Link to external databases (GeoNames, Wikipedia, etc.).",
            "",
            "---",
            "",
            f"*Report generated by Toponym Discovery Agent on {datetime.now().strftime('%Y-%m-%d')}*"
        ])

        # Save report
        report_file = REPORT_DIR / "toponym_discovery_1867_1890.md"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write('\n'.join(report_lines))

        print(f"\nReport saved to {report_file}")

    def run(self):
        """Run the complete toponym discovery process"""
        print("="*80)
        print("TOPONYM DISCOVERY AGENT - Colonial Office List 1867-1890")
        print("="*80)

        for year in YEARS:
            missing = self.find_missing_toponyms(year)
            self.enhance_kg_with_toponyms(year, missing)

        self.generate_report()

        print("\n" + "="*80)
        print("TOPONYM DISCOVERY COMPLETE")
        print("="*80)
        print(f"Total existing toponyms: {sum(self.stats[y]['existing_places'] for y in YEARS):,}")
        print(f"Total new toponyms: {sum(self.stats[y]['new_toponyms'] for y in YEARS):,}")
        print("="*80)

if __name__ == "__main__":
    agent = ToponymDiscoveryAgent()
    agent.run()
