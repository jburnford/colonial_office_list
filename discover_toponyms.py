#!/usr/bin/env python3
"""
Toponym Discovery Agent for Colonial Office List Knowledge Graph
Finds ALL toponyms in source documents and extracts missing ones.
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
from datetime import datetime

class ToponymDiscoveryAgent:
    def __init__(self, year: str, base_dir: str = "/home/user/colonial_office_list"):
        self.year = year
        self.base_dir = Path(base_dir)
        self.source_dir = self.base_dir / "output_2" / f"{year}_manual_parsed"
        self.kg_file = self.base_dir / "knowledge_graph_extracts_v3" / f"{year}_extracted.json"
        self.output_file = self.base_dir / "knowledge_graph_extracts_v3" / f"{year}_extracted_toponyms.json"

        # Place type indicators and patterns
        self.place_patterns = {
            'river': r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:River|river)\b',
            'bay': r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:Bay|bay)\b',
            'mountain': r'\b(?:Mount|Mt\.|Mountain)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b',
            'mountains': r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:Mountains|mountains|Range)\b',
            'island': r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:Island|island|Islands|islands)\b',
            'cape': r'\b(?:Cape|Point)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b',
            'district': r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:District|district|Province|province)\b',
            'town': r'\b(?:town of|city of|port of)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b',
            'parish': r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:Parish|parish)\b',
            'colony': r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:Colony|colony)\b',
            'protectorate': r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:Protectorate|protectorate)\b',
            'settlement': r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:Settlement|settlement)\b',
            'territory': r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:Territory|territory)\b',
            'lake': r'\b(?:Lake|lake)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b',
            'gulf': r'\b(?:Gulf of|gulf of)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b',
            'strait': r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:Strait|strait|Straits|straits)\b',
            'creek': r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:Creek|creek)\b',
            'falls': r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:Falls|falls|Waterfall|waterfall)\b',
            'harbor': r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:Harbor|Harbour|harbour|harbor)\b',
            'county': r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:County|county)\b',
            'coast': r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+(?:Coast|coast)\b',
        }

        # Generic references to exclude
        self.generic_exclusions = {
            'the', 'this', 'that', 'these', 'those', 'said', 'aforementioned',
            'main', 'principal', 'chief', 'central', 'eastern', 'western',
            'northern', 'southern', 'upper', 'lower', 'new', 'old', 'great',
            'little', 'small', 'large', 'same', 'present', 'former', 'latter'
        }

        self.existing_places = set()
        self.new_toponyms = []
        self.stats = {
            'existing_places': 0,
            'new_toponyms': 0,
            'files_scanned': 0,
            'source_files': []
        }

    def load_existing_kg(self) -> Dict:
        """Load existing knowledge graph extract."""
        if not self.kg_file.exists():
            print(f"Warning: KG file not found: {self.kg_file}")
            return {"entities": {"places": []}}

        with open(self.kg_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # Extract existing place names
        places = data.get('entities', {}).get('places', [])
        for place in places:
            name = place.get('name', '').strip()
            if name:
                self.existing_places.add(name.lower())

        self.stats['existing_places'] = len(self.existing_places)
        return data

    def scan_source_files(self) -> List[Tuple[str, str, int, str, str]]:
        """
        Scan all source markdown files for toponyms.
        Returns: List of (toponym_name, type, line_number, context, source_file)
        """
        discovered_toponyms = []

        if not self.source_dir.exists():
            print(f"Warning: Source directory not found: {self.source_dir}")
            return discovered_toponyms

        for md_file in sorted(self.source_dir.glob("*.md")):
            self.stats['files_scanned'] += 1
            self.stats['source_files'].append(md_file.name)

            with open(md_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            for line_num, line in enumerate(lines, 1):
                # Scan for each place type pattern
                for place_type, pattern in self.place_patterns.items():
                    matches = re.finditer(pattern, line)
                    for match in matches:
                        toponym = match.group(1).strip()

                        # Filter out generic references
                        first_word = toponym.split()[0].lower()
                        if first_word in self.generic_exclusions:
                            continue

                        # Skip if already exists
                        if toponym.lower() in self.existing_places:
                            continue

                        # Get context (current line and some surrounding text)
                        context = line.strip()
                        if len(context) > 150:
                            context = context[:150] + "..."

                        discovered_toponyms.append((
                            toponym,
                            place_type,
                            line_num,
                            context,
                            md_file.name
                        ))

        return discovered_toponyms

    def create_toponym_entities(self, toponyms: List[Tuple[str, str, int, str, str]]) -> List[Dict]:
        """Create entity objects for new toponyms."""
        entities = []
        seen = set()
        entity_counter = 1

        for toponym, place_type, line_num, context, source_file in toponyms:
            # Deduplicate
            key = (toponym.lower(), place_type, source_file)
            if key in seen:
                continue
            seen.add(key)

            # Infer parent colony from source file name
            parent_location = source_file.replace('.md', '').replace('_', ' ')

            entity = {
                "id": f"place_{self.year}_new_{entity_counter:03d}",
                "name": toponym,
                "type": place_type,
                "parent_location": parent_location,
                "description": context,
                "year": self.year,
                "provenance": {
                    "source_file": f"output_2/{self.year}_manual_parsed/{source_file}",
                    "source_lines": str(line_num),
                    "extraction_confidence": 0.95,
                    "extraction_agent": "toponym_discovery_1908_1917",
                    "extraction_date": datetime.now().strftime("%Y-%m-%d"),
                    "verification_status": "automated"
                }
            }

            entities.append(entity)
            entity_counter += 1

        self.new_toponyms = entities
        self.stats['new_toponyms'] = len(entities)
        return entities

    def save_enhanced_kg(self, existing_kg: Dict):
        """Save enhanced knowledge graph with new toponyms."""
        # Add new toponyms to existing places
        if 'entities' not in existing_kg:
            existing_kg['entities'] = {}
        if 'places' not in existing_kg['entities']:
            existing_kg['entities']['places'] = []

        existing_kg['entities']['places'].extend(self.new_toponyms)

        # Update metadata
        if 'metadata' in existing_kg:
            existing_kg['metadata']['toponym_discovery_date'] = datetime.now().isoformat()
            existing_kg['metadata']['toponyms_added'] = len(self.new_toponyms)

        # Save to file
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(existing_kg, f, indent=2, ensure_ascii=False)

        print(f"✓ Saved enhanced KG to {self.output_file}")

    def generate_report(self) -> Dict:
        """Generate discovery report for this year."""
        return {
            "year": self.year,
            "existing_places": self.stats['existing_places'],
            "new_toponyms_discovered": self.stats['new_toponyms'],
            "files_scanned": self.stats['files_scanned'],
            "source_files": self.stats['source_files'],
            "sample_new_toponyms": self.new_toponyms[:10] if self.new_toponyms else [],
            "discovery_date": datetime.now().isoformat()
        }

    def run(self) -> Dict:
        """Execute full toponym discovery pipeline."""
        print(f"\n{'='*60}")
        print(f"Toponym Discovery Agent - Year {self.year}")
        print(f"{'='*60}")

        # Step 1: Load existing KG
        print(f"1. Loading existing KG from {self.kg_file}...")
        existing_kg = self.load_existing_kg()
        print(f"   Found {self.stats['existing_places']} existing places")

        # Step 2: Scan source files
        print(f"2. Scanning source files in {self.source_dir}...")
        discovered = self.scan_source_files()
        print(f"   Scanned {self.stats['files_scanned']} files")
        print(f"   Discovered {len(discovered)} potential new toponyms")

        # Step 3: Create entities
        print(f"3. Creating toponym entities...")
        self.create_toponym_entities(discovered)
        print(f"   Created {len(self.new_toponyms)} new toponym entities")

        # Step 4: Save enhanced KG
        print(f"4. Saving enhanced knowledge graph...")
        self.save_enhanced_kg(existing_kg)

        # Step 5: Generate report
        print(f"5. Generating report...")
        report = self.generate_report()

        print(f"\n✓ Completed toponym discovery for {self.year}")
        print(f"  - Existing places: {self.stats['existing_places']}")
        print(f"  - New toponyms added: {self.stats['new_toponyms']}")

        return report


def main():
    """Process all target years."""
    years = ['1908', '1909', '1910', '1911', '1915', '1917']

    all_reports = []

    for year in years:
        agent = ToponymDiscoveryAgent(year)
        report = agent.run()
        all_reports.append(report)

    # Save consolidated report
    report_dir = Path("/home/user/colonial_office_list/reports/phase_c")
    report_dir.mkdir(parents=True, exist_ok=True)

    report_file = report_dir / "toponym_discovery_1908_1917.json"
    with open(report_file, 'w', encoding='utf-8') as f:
        json.dump(all_reports, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*60}")
    print(f"All Years Processed - Summary Report Saved")
    print(f"{'='*60}")
    print(f"Report saved to: {report_file}")

    # Print summary table
    print(f"\n{'Year':<10} {'Existing':<12} {'New Found':<12} {'Files':<8}")
    print(f"{'-'*50}")
    for report in all_reports:
        print(f"{report['year']:<10} {report['existing_places']:<12} "
              f"{report['new_toponyms_discovered']:<12} {report['files_scanned']:<8}")

    total_new = sum(r['new_toponyms_discovered'] for r in all_reports)
    print(f"{'-'*50}")
    print(f"{'TOTAL':<10} {'':<12} {total_new:<12}")


if __name__ == "__main__":
    main()
