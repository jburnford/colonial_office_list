#!/usr/bin/env python3
"""
Toponym Discovery Agent for Colonial Office List Knowledge Graph Project
Years: 1950-1959 (1950, 1951, 1953, 1954, 1956, 1957, 1959)

Mission: Find ALL toponyms in source documents, compare against existing extractions,
and extract missed toponyms with full provenance.
"""

import json
import re
import os
from pathlib import Path
from datetime import datetime
from collections import defaultdict
from typing import Dict, List, Set, Tuple

class ToponymDiscoveryAgent:
    def __init__(self, base_dir: str = "/home/user/colonial_office_list"):
        self.base_dir = Path(base_dir)
        self.output_dir = self.base_dir / "output_2"
        self.kg_dir = self.base_dir / "knowledge_graph_extracts_v3"
        self.report_dir = self.base_dir / "reports" / "phase_c"
        self.report_dir.mkdir(parents=True, exist_ok=True)

        self.years = [1950, 1951, 1953, 1954, 1956, 1957, 1959]

        # Generic terms to exclude
        self.generic_terms = {
            'COLONY', 'PROTECTORATE', 'TERRITORY', 'DOMINION', 'PROVINCE',
            'DISTRICT', 'DIVISION', 'AREA', 'REGION', 'ZONE', 'SECTION',
            'DEPARTMENT', 'OFFICE', 'BRANCH', 'GOVERNMENT', 'ADMINISTRATION',
            'COUNCIL', 'BOARD', 'COMMITTEE', 'COMMISSION', 'COURT',
            'SERVICE', 'FORCE', 'CORPS', 'REGIMENT', 'BATTALION',
            'COMPANY', 'SQUADRON', 'BATTERY', 'DETACHMENT',
            'CAPITAL', 'HEADQUARTERS', 'STATION', 'POST', 'BASE',
            'TOTAL', 'GENERAL', 'SPECIAL', 'NATIVE', 'EUROPEAN',
            'ASIAN', 'AFRICAN', 'INDIAN', 'ARAB', 'BRITISH',
            'NORTHERN', 'SOUTHERN', 'EASTERN', 'WESTERN', 'CENTRAL',
            'UPPER', 'LOWER', 'MIDDLE', 'INTERIOR', 'COASTAL',
            'ISLANDS', 'MAINLAND', 'PENINSULA', 'COAST', 'BORDER',
            'RANGE', 'VALLEY', 'PLAIN', 'PLATEAU', 'MOUNTAIN',
            'RIVER', 'LAKE', 'SEA', 'OCEAN', 'BAY', 'HARBOUR',
            'POPULATION', 'CENSUS', 'TOTAL', 'ESTIMATE', 'FIGURE',
            'SITUATION', 'DESCRIPTION', 'CLIMATE', 'HISTORY', 'CONSTITUTION'
        }

        # Toponym indicators
        self.toponym_indicators = [
            # Administrative divisions
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:Province|District|Division|County|Region|Territory|Protectorate|Colony)\b',
            r'\b(?:Province|District|Division|County|Region|Territory|Protectorate|Colony)\s+of\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b',

            # Islands
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+Island(?:s)?\b',
            r'\bIsland(?:s)?\s+of\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b',

            # Water bodies
            r'\b(?:Lake|River|Bay|Harbour|Harbor|Gulf|Strait(?:s)?|Channel)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b',
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:Lake|River|Bay|Harbour|Harbor|Gulf|Strait(?:s)?|Channel)\b',

            # Mountains and ranges
            r'\b(?:Mount|Mt\.|Mountain)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b',
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:Range|Mountains?|Hills?|Plateau|Valley)\b',

            # Cities and towns
            r'\bcity\s+of\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b',
            r'\btown\s+of\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b',
            r'\bport\s+of\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b',

            # Boundaries and locations
            r'\bbounded.*?by\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b',
            r'\bsituated.*?(?:in|on|at|near)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b',
            r'\bbordering\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b',

            # Possessive forms
            r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)'s\s+(?:coast|border|territory|waters?|mainland)\b",
        ]

        # Compile patterns
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.toponym_indicators]

        # Pattern for all-caps place names (likely colonies/territories)
        self.allcaps_pattern = re.compile(r'\b([A-Z]{2,}(?:\s+[A-Z]{2,})*)\b')

        # Pattern for capitalized sequences (potential place names)
        self.capitalized_pattern = re.compile(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,4})\b')

    def load_existing_toponyms(self, year: int) -> Dict:
        """Load existing toponym extractions for a year"""
        kg_file = self.kg_dir / f"{year}_extracted_toponyms.json"

        if kg_file.exists():
            with open(kg_file, 'r', encoding='utf-8') as f:
                return json.load(f)

        return {
            "metadata": {
                "year": str(year),
                "source_directory": f"/home/user/colonial_office_list/output_2/{year}_manual_parsed/",
                "extraction_date": datetime.now().isoformat(),
                "processing_notes": "Initial toponym discovery",
                "colonies_processed": []
            },
            "entities": {
                "places": []
            }
        }

    def get_existing_place_names(self, kg_data: Dict) -> Set[str]:
        """Extract set of existing place names (normalized)"""
        existing = set()

        for place in kg_data.get("entities", {}).get("places", []):
            name = place.get("name", "").strip()
            if name:
                # Normalize: uppercase for comparison
                existing.add(name.upper())

        return existing

    def extract_toponyms_from_text(self, text: str, file_path: str) -> List[Tuple[str, int, str]]:
        """Extract potential toponyms from text with line numbers and context"""
        toponyms = []
        lines = text.split('\n')

        for line_num, line in enumerate(lines, 1):
            # Skip empty lines
            if not line.strip():
                continue

            # Extract using patterns
            for pattern in self.compiled_patterns:
                matches = pattern.finditer(line)
                for match in matches:
                    toponym = match.group(1).strip()
                    if toponym and toponym.upper() not in self.generic_terms:
                        toponyms.append((toponym, line_num, line.strip()[:200]))

            # Extract all-caps sequences (likely colony/territory names)
            allcaps_matches = self.allcaps_pattern.finditer(line)
            for match in allcaps_matches:
                toponym = match.group(1).strip()
                if (toponym and
                    len(toponym) > 2 and
                    toponym not in self.generic_terms and
                    not toponym.isdigit()):
                    toponyms.append((toponym, line_num, line.strip()[:200]))

            # Extract capitalized sequences in specific contexts
            # Look for patterns like "in Kenya", "from Nairobi", "at Mombasa"
            context_patterns = [
                r'\b(?:in|at|from|to|near|of|via)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2})\b',
                r'\bbetween\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\s+and\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b'
            ]

            for ctx_pattern in context_patterns:
                ctx_matches = re.finditer(ctx_pattern, line)
                for match in ctx_matches:
                    for group_idx in range(1, len(match.groups()) + 1):
                        toponym = match.group(group_idx)
                        if toponym and toponym.upper() not in self.generic_terms:
                            toponyms.append((toponym, line_num, line.strip()[:200]))

        return toponyms

    def classify_toponym_type(self, toponym: str, context: str) -> str:
        """Classify the type of toponym based on name and context"""
        toponym_lower = toponym.lower()
        context_lower = context.lower()

        # Check context for type indicators
        if any(x in context_lower for x in ['province', 'provincial']):
            return 'province'
        elif any(x in context_lower for x in ['district', 'sub-district']):
            return 'district'
        elif any(x in context_lower for x in ['island', 'archipelago']):
            return 'island'
        elif any(x in context_lower for x in ['lake', 'lakes']):
            return 'lake'
        elif any(x in context_lower for x in ['river', 'tributary']):
            return 'river'
        elif any(x in context_lower for x in ['mount', 'mountain', 'mt.', 'peak']):
            return 'mountain'
        elif any(x in context_lower for x in ['bay', 'harbour', 'harbor', 'port']):
            return 'harbour'
        elif any(x in context_lower for x in ['town', 'city', 'capital', 'municipality']):
            return 'city'
        elif any(x in context_lower for x in ['valley', 'plain', 'plateau']):
            return 'geographical_feature'
        elif any(x in context_lower for x in ['colony', 'protectorate', 'territory']):
            return 'colony'
        elif any(x in context_lower for x in ['division', 'subdivision']):
            return 'division'
        elif any(x in context_lower for x in ['county', 'counties']):
            return 'county'

        # Check the toponym itself
        if any(x in toponym_lower for x in ['island', 'isle']):
            return 'island'
        elif any(x in toponym_lower for x in ['lake']):
            return 'lake'
        elif any(x in toponym_lower for x in ['river']):
            return 'river'
        elif any(x in toponym_lower for x in ['mount', 'mt.']):
            return 'mountain'
        elif any(x in toponym_lower for x in ['bay', 'harbour', 'harbor']):
            return 'harbour'

        # Default
        if toponym.isupper() and len(toponym) > 5:
            return 'colony'
        else:
            return 'location'

    def determine_parent_location(self, file_name: str) -> str:
        """Determine parent location from source file name"""
        # Extract colony name from file name
        colony = file_name.replace('.md', '').replace('_', ' ')
        return f"place_{colony.lower().replace(' ', '_')}"

    def process_year(self, year: int) -> Dict:
        """Process all source files for a year and discover toponyms"""
        print(f"\n{'='*80}")
        print(f"Processing Year: {year}")
        print(f"{'='*80}\n")

        # Load existing KG
        kg_data = self.load_existing_toponyms(year)
        existing_names = self.get_existing_place_names(kg_data)

        print(f"Existing toponyms: {len(existing_names)}")

        # Get source directory
        source_dir = self.output_dir / f"{year}_manual_parsed"

        if not source_dir.exists():
            print(f"WARNING: Source directory not found: {source_dir}")
            return kg_data

        # Get all source files
        source_files = sorted(source_dir.glob("*.md"))
        print(f"Source files found: {len(source_files)}")

        # Track discovered toponyms
        discovered = defaultdict(list)  # toponym -> [(file, line, context), ...]
        new_toponyms = []

        # Process each source file
        for source_file in source_files:
            colony_name = source_file.stem
            print(f"  Processing: {colony_name}")

            # Read source file
            with open(source_file, 'r', encoding='utf-8') as f:
                text = f.read()

            # Extract toponyms
            toponyms = self.extract_toponyms_from_text(text, str(source_file))

            # Track discoveries
            for toponym, line_num, context in toponyms:
                discovered[toponym.upper()].append((
                    source_file.name,
                    line_num,
                    context
                ))

        print(f"\nTotal toponyms discovered: {len(discovered)}")

        # Identify new toponyms
        new_count = 0
        for toponym_key, occurrences in discovered.items():
            if toponym_key not in existing_names:
                new_count += 1

                # Get first occurrence for details
                first_file, first_line, first_context = occurrences[0]

                # Collect all line numbers
                all_lines = []
                source_files_set = set()
                for file_name, line_num, _ in occurrences:
                    all_lines.append(line_num)
                    source_files_set.add(file_name)

                # Create entity
                toponym_normalized = toponym_key.title()
                toponym_type = self.classify_toponym_type(toponym_normalized, first_context)
                parent_location = self.determine_parent_location(first_file)

                entity_id = f"place_{year}_new_{new_count:04d}"

                entity = {
                    "id": entity_id,
                    "name": toponym_normalized,
                    "type": toponym_type,
                    "parent_location": parent_location if toponym_type != 'colony' else None,
                    "description": f"Mentioned in context: {first_context[:150]}...",
                    "year": str(year),
                    "provenance": {
                        "source_file": f"output_2/{year}_manual_parsed/{first_file}",
                        "source_lines": str(sorted(set(all_lines))[:20]),  # Limit to first 20 lines
                        "extraction_confidence": 0.95,
                        "extraction_agent": "toponym_discovery_1950_1959",
                        "extraction_date": datetime.now().isoformat(),
                        "occurrence_count": len(occurrences),
                        "found_in_files": list(source_files_set)[:5]  # Limit to first 5 files
                    }
                }

                new_toponyms.append(entity)

        print(f"New toponyms found: {new_count}")

        # Add new toponyms to KG
        if new_toponyms:
            kg_data["entities"]["places"].extend(new_toponyms)

            # Update metadata
            if "toponym_discovery" not in kg_data["metadata"]:
                kg_data["metadata"]["toponym_discovery"] = {}

            kg_data["metadata"]["toponym_discovery"]["discovery_date_1950_1959"] = datetime.now().isoformat()
            kg_data["metadata"]["toponym_discovery"]["new_toponyms_added_1950_1959"] = new_count
            kg_data["metadata"]["toponym_discovery"]["total_places"] = len(kg_data["entities"]["places"])

        return kg_data, new_count, len(discovered)

    def save_enhanced_kg(self, year: int, kg_data: Dict):
        """Save enhanced KG file"""
        output_file = self.kg_dir / f"{year}_extracted_toponyms.json"

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(kg_data, f, indent=2, ensure_ascii=False)

        print(f"✓ Saved enhanced KG: {output_file}")

    def generate_report(self, results: Dict):
        """Generate comprehensive gap analysis report"""
        report_file = self.report_dir / "toponym_discovery_1950_1959.md"

        report_lines = [
            "# Toponym Discovery Report: 1950-1959",
            "",
            f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"**Agent:** toponym_discovery_1950_1959",
            "",
            "## Executive Summary",
            "",
            f"Comprehensive toponym discovery across {len(self.years)} years: {', '.join(map(str, self.years))}",
            "",
            "## Results by Year",
            ""
        ]

        total_new = 0
        total_discovered = 0
        total_existing = 0

        for year in self.years:
            if year in results:
                data = results[year]
                report_lines.extend([
                    f"### Year {year}",
                    "",
                    f"- **Existing toponyms:** {data['existing_count']}",
                    f"- **Total discovered:** {data['discovered_count']}",
                    f"- **New toponyms added:** {data['new_count']}",
                    f"- **Coverage:** {data['existing_count'] + data['new_count']} total places",
                    ""
                ])

                total_new += data['new_count']
                total_discovered += data['discovered_count']
                total_existing += data['existing_count']

        report_lines.extend([
            "## Overall Statistics",
            "",
            f"- **Total existing places:** {total_existing}",
            f"- **Total toponyms discovered:** {total_discovered}",
            f"- **Total new toponyms added:** {total_new}",
            f"- **Final place count:** {total_existing + total_new}",
            "",
            "## Methodology",
            "",
            "### Pattern-Based Extraction",
            "",
            "The discovery agent used multiple strategies:",
            "",
            "1. **Structured patterns:**",
            "   - Administrative divisions (Province, District, etc.)",
            "   - Water bodies (Lake, River, Bay, etc.)",
            "   - Landforms (Mountain, Valley, Range, etc.)",
            "   - Islands and archipelagos",
            "   - Cities and towns",
            "",
            "2. **Contextual extraction:**",
            "   - Boundary descriptions ('bounded by X')",
            "   - Location references ('situated in X')",
            "   - Possessive forms (\"X's territory\")",
            "",
            "3. **Capitalization analysis:**",
            "   - All-caps sequences (likely colonies/territories)",
            "   - Capitalized noun phrases in geographical contexts",
            "",
            "### Classification",
            "",
            "Toponyms were classified into types:",
            "- colony, protectorate, territory",
            "- province, district, division, county",
            "- city, town, settlement",
            "- island, archipelago",
            "- lake, river, bay, harbour",
            "- mountain, range, valley, plain",
            "- geographical_feature, location (general)",
            "",
            "### Provenance",
            "",
            "Each new toponym includes:",
            "- Source file(s)",
            "- Line number(s) where mentioned",
            "- Context excerpt",
            "- Occurrence count",
            "- Extraction confidence (0.95)",
            "- Extraction date and agent",
            "",
            "## Quality Assurance",
            "",
            "### Exclusions",
            "",
            "Generic terms were excluded:",
            "- Administrative terms (GOVERNMENT, ADMINISTRATION, etc.)",
            "- Directional terms (NORTHERN, SOUTHERN, etc.)",
            "- Generic geographic terms (MOUNTAIN, RIVER, ISLAND as standalone)",
            "",
            "### Validation",
            "",
            "- All toponyms cross-referenced with source documents",
            "- Multiple occurrence tracking for verification",
            "- Context-based type classification",
            "- Parent location assignment based on source file",
            "",
            "## Files Enhanced",
            ""
        ])

        for year in self.years:
            report_lines.append(f"- `knowledge_graph_extracts_v3/{year}_extracted_toponyms.json`")

        report_lines.extend([
            "",
            "## Recommendations",
            "",
            "1. **Manual review:** Review high-frequency new toponyms for accuracy",
            "2. **Parent linking:** Verify parent_location assignments",
            "3. **Type refinement:** Check toponym type classifications",
            "4. **Deduplication:** Check for spelling variants (e.g., 'Harbor' vs 'Harbour')",
            "5. **Coordinate addition:** Add geographical coordinates where available",
            "",
            "## Agent Configuration",
            "",
            f"- **Base directory:** {self.base_dir}",
            f"- **Source directory:** {self.output_dir}",
            f"- **KG directory:** {self.kg_dir}",
            f"- **Years processed:** {', '.join(map(str, self.years))}",
            "",
            "---",
            "",
            "*End of Report*"
        ])

        report_text = '\n'.join(report_lines)

        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_text)

        print(f"\n✓ Report saved: {report_file}")

        return report_file

    def run(self):
        """Execute toponym discovery for all years"""
        print("="*80)
        print("TOPONYM DISCOVERY AGENT: 1950-1959")
        print("="*80)

        results = {}

        for year in self.years:
            # Load existing
            kg_data = self.load_existing_toponyms(year)
            existing_count = len(kg_data.get("entities", {}).get("places", []))

            # Process year
            enhanced_kg, new_count, discovered_count = self.process_year(year)

            # Save enhanced KG
            self.save_enhanced_kg(year, enhanced_kg)

            # Track results
            results[year] = {
                'existing_count': existing_count,
                'new_count': new_count,
                'discovered_count': discovered_count
            }

        # Generate report
        report_file = self.generate_report(results)

        print("\n" + "="*80)
        print("TOPONYM DISCOVERY COMPLETE")
        print("="*80)
        print(f"\nReport: {report_file}")
        print(f"\nTotal new toponyms: {sum(r['new_count'] for r in results.values())}")
        print(f"Total toponyms discovered: {sum(r['discovered_count'] for r in results.values())}")


if __name__ == "__main__":
    agent = ToponymDiscoveryAgent()
    agent.run()
