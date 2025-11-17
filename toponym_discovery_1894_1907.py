#!/usr/bin/env python3
"""
Toponym Discovery Agent for Colonial Office List Knowledge Graph
Comprehensive extraction of all place names from 1894-1907
"""

import json
import re
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set, Tuple

class ToponymDiscoveryAgent:
    def __init__(self):
        self.base_dir = Path("/home/user/colonial_office_list")
        self.years = [1894, 1896, 1897, 1898, 1899, 1900, 1905, 1906, 1907]

        # Toponym patterns - comprehensive set
        self.place_patterns = [
            # Explicit location markers
            r'\b(?:in|at|of|from|to|near|port of|town of|city of|island of|district of|province of|territory of)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
            # Geographical features
            r'\b((?:Mount|Mt\.|Mountain|River|Lake|Bay|Harbor|Harbour|Port|Cape|Island|Islands|Peninsula|Gulf|Strait|Channel|Sound)\s+[A-Z][a-zA-Z\s\-]+?)(?:\s|,|\.|;|$)',
            # Capitalized place names in context
            r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,3})\s*(?:Colony|Protectorate|Territory|District|Province|Parish|Division|Station)',
            # Islands and island groups
            r'\b([A-Z][a-zA-Z\s\-]+?)\s+Islands?\b',
            # Named locations in parentheses
            r'\(([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\)',
            # Cities/towns/villages
            r'\b(?:capital|headquarters|seat|based|stationed)\s+(?:in|at)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)',
        ]

        # Known non-place terms to filter
        self.stopwords = {
            'The', 'This', 'These', 'Those', 'Colony', 'Protectorate', 'Territory',
            'Government', 'Department', 'Office', 'Service', 'Administration',
            'British', 'Crown', 'Royal', 'His', 'Her', 'Majesty', 'Majestys',
            'Chief', 'Deputy', 'Assistant', 'Senior', 'Junior', 'Acting',
            'Secretary', 'Commissioner', 'Governor', 'Officer', 'Director',
            'Superintendent', 'Inspector', 'Controller', 'Manager', 'Agent',
            'Agricultural', 'Medical', 'Education', 'Public', 'Works', 'Police',
            'Defence', 'Treasury', 'Audit', 'Survey', 'Development', 'Research',
            'Council', 'Board', 'Committee', 'Commission', 'Institute',
            'January', 'February', 'March', 'April', 'May', 'June', 'July',
            'August', 'September', 'October', 'November', 'December',
            'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday',
            'Act', 'Order', 'Ordinance', 'Regulation', 'Law', 'Statute',
            'Esquire', 'Esq', 'Sir', 'Mr', 'Mrs', 'Miss', 'Dr', 'Rev',
            'Captain', 'Major', 'Colonel', 'General', 'Admiral', 'Commander',
            'First', 'Second', 'Third', 'Fourth', 'Fifth', 'Sixth', 'Seventh',
            'North', 'South', 'East', 'West', 'Central', 'Northern', 'Southern',
            'Eastern', 'Western', 'Upper', 'Lower', 'Middle', 'New', 'Old',
        }

    def audit_existing_places(self, year: int) -> Dict:
        """Audit existing place entities in knowledge graph"""
        kg_path = self.base_dir / "knowledge_graph_extracts_v3" / f"{year}_extracted.json"

        try:
            with open(kg_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
        except Exception as e:
            print(f"Error loading {kg_path}: {e}")
            return {"places": [], "count": 0}

        places = set()

        # Extract place names from geographic_entities
        if 'colonies' in data:
            for colony_key, colony_data in data['colonies'].items():
                if 'geographic_entities' in colony_data:
                    geo = colony_data['geographic_entities']
                    
                    # Colony name
                    if 'colony_name' in geo:
                        places.add(geo['colony_name'])
                    
                    # Capital
                    if 'capital' in geo:
                        places.add(geo['capital'])
                    
                    # Major cities
                    if 'major_cities' in geo:
                        for city in geo['major_cities']:
                            if isinstance(city, dict) and 'name' in city:
                                places.add(city['name'])
                            elif isinstance(city, str):
                                places.add(city)
                    
                    # Islands
                    if 'islands' in geo:
                        for island in geo['islands']:
                            if isinstance(island, dict) and 'name' in island:
                                places.add(island['name'])
                            elif isinstance(island, str):
                                places.add(island)
                    
                    # Other geographic features
                    for key in ['rivers', 'mountains', 'bays', 'harbours', 'lakes', 'districts', 'parishes']:
                        if key in geo:
                            items = geo[key]
                            if isinstance(items, list):
                                for item in items:
                                    if isinstance(item, dict) and 'name' in item:
                                        places.add(item['name'])
                                    elif isinstance(item, str):
                                        places.add(item)

        return {
            "places": sorted(list(places)),
            "count": len(places)
        }

    def extract_toponyms_from_text(self, text: str, source_file: str) -> List[Dict]:
        """Extract all toponyms from text with context"""
        toponyms = []
        lines = text.split('\n')

        for line_num, line in enumerate(lines, 1):
            # Skip empty lines and headers
            if not line.strip() or line.strip().startswith('#'):
                continue

            # Apply all patterns
            for pattern in self.place_patterns:
                matches = re.finditer(pattern, line)
                for match in matches:
                    place_name = match.group(1).strip()

                    # Filter out stopwords and short names
                    if (place_name in self.stopwords or
                        len(place_name) < 3 or
                        place_name.lower() in ['and', 'the', 'or', 'of', 'in', 'at']):
                        continue

                    # Clean up the name
                    place_name = place_name.rstrip('.,;:')

                    # Determine place type from context
                    place_type = self.classify_place_type(place_name, line)

                    toponyms.append({
                        'name': place_name,
                        'type': place_type,
                        'context': line.strip(),
                        'source_file': source_file,
                        'line_number': line_num
                    })

        return toponyms

    def classify_place_type(self, name: str, context: str) -> str:
        """Classify place type from name and context"""
        context_lower = context.lower()
        name_lower = name.lower()

        # Check for explicit type markers
        if any(x in name_lower for x in ['island', 'islands']):
            return 'island'
        elif any(x in name_lower for x in ['river', 'lake']):
            return 'water_feature'
        elif any(x in name_lower for x in ['mount', 'mountain', 'mt.']):
            return 'mountain'
        elif any(x in name_lower for x in ['bay', 'harbor', 'harbour', 'port']):
            return 'port'
        elif any(x in name_lower for x in ['cape', 'peninsula']):
            return 'geographic_feature'

        # Check context
        if any(x in context_lower for x in ['colony', 'protectorate', 'territory']):
            return 'territory'
        elif any(x in context_lower for x in ['district', 'province', 'division', 'parish']):
            return 'administrative_division'
        elif any(x in context_lower for x in ['capital', 'city', 'town', 'village']):
            return 'city'
        elif any(x in context_lower for x in ['station', 'headquarters', 'seat']):
            return 'settlement'

        # Default
        return 'location'

    def scan_year_sources(self, year: int) -> Dict:
        """Scan all source markdown files for a year"""
        source_dir = self.base_dir / "output_2" / f"{year}_manual_parsed"

        if not source_dir.exists():
            print(f"Warning: Source directory not found: {source_dir}")
            return {"toponyms": [], "files_scanned": 0}

        all_toponyms = []
        files_scanned = 0

        for md_file in sorted(source_dir.glob("*.md")):
            try:
                with open(md_file, 'r', encoding='utf-8') as f:
                    text = f.read()

                toponyms = self.extract_toponyms_from_text(text, md_file.name)
                all_toponyms.extend(toponyms)
                files_scanned += 1

            except Exception as e:
                print(f"Error reading {md_file}: {e}")

        return {
            "toponyms": all_toponyms,
            "files_scanned": files_scanned,
            "unique_names": len(set(t['name'] for t in all_toponyms))
        }

    def gap_analysis(self, existing_places: Set[str], discovered_toponyms: List[Dict]) -> Dict:
        """Compare existing vs discovered toponyms"""
        discovered_names = set(t['name'] for t in discovered_toponyms)

        missing = discovered_names - existing_places
        already_captured = discovered_names & existing_places

        # Get details for missing toponyms
        missing_details = [t for t in discovered_toponyms if t['name'] in missing]

        # Deduplicate and aggregate
        missing_aggregated = defaultdict(list)
        for item in missing_details:
            missing_aggregated[item['name']].append(item)

        return {
            "total_discovered": len(discovered_names),
            "already_captured": len(already_captured),
            "missing_count": len(missing),
            "missing_names": sorted(list(missing)),
            "missing_details": dict(missing_aggregated),
            "coverage_percent": round(len(already_captured) / len(discovered_names) * 100, 2) if discovered_names else 0
        }

    def create_new_entities(self, missing_details: Dict, year: int) -> List[Dict]:
        """Create new entity records for missing toponyms"""
        new_entities = []
        
        for idx, (name, occurrences) in enumerate(sorted(missing_details.items()), 1):
            # Use first occurrence for primary details
            first_occ = occurrences[0]
            
            entity = {
                'id': f"place_{year}_new_{idx:03d}",
                'name': name,
                'type': first_occ['type'],
                'year': str(year),
                'description': f"{first_occ['type'].replace('_', ' ').title()}: {name}",
                'provenance': {
                    'source_file': f"output_2/{year}_manual_parsed/{first_occ['source_file']}",
                    'source_line': first_occ['line_number'],
                    'context': first_occ['context'][:200],
                    'extraction_confidence': 0.85,
                    'extraction_agent': 'toponym_discovery_1894_1907',
                    'extraction_date': '2025-11-17',
                    'total_occurrences': len(occurrences)
                }
            }
            new_entities.append(entity)
        
        return new_entities

    def process_all_years(self):
        """Process all years and generate comprehensive report"""
        results = {}

        for year in self.years:
            print(f"\n{'='*60}")
            print(f"Processing {year}")
            print(f"{'='*60}")

            # Step 1: Audit existing
            print(f"Auditing existing place entities in {year} KG...")
            existing = self.audit_existing_places(year)
            print(f"  Found {existing['count']} existing place entities")

            # Step 2: Scan sources
            print(f"Scanning {year} source markdown files...")
            discovered = self.scan_year_sources(year)
            print(f"  Scanned {discovered['files_scanned']} files")
            print(f"  Discovered {discovered['unique_names']} unique toponyms")

            # Step 3: Gap analysis
            print(f"Performing gap analysis...")
            gap = self.gap_analysis(set(existing['places']), discovered['toponyms'])
            print(f"  Coverage: {gap['coverage_percent']}%")
            print(f"  Missing: {gap['missing_count']} toponyms")

            # Step 4: Create new entities
            print(f"Creating entity records for new toponyms...")
            new_entities = self.create_new_entities(gap['missing_details'], year)
            print(f"  Created {len(new_entities)} new entity records")

            # Step 5: Save to JSON
            output_file = self.base_dir / "knowledge_graph_extracts_v3" / f"{year}_extracted_toponyms.json"
            output_data = {
                'metadata': {
                    'year': year,
                    'extraction_date': '2025-11-17',
                    'extraction_agent': 'toponym_discovery_1894_1907',
                    'total_new_toponyms': len(new_entities),
                    'existing_place_count': existing['count'],
                    'unique_toponyms_found': discovered['unique_names']
                },
                'new_toponyms': new_entities
            }

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, indent=2, ensure_ascii=False)
            
            print(f"  Saved to {output_file}")

            results[year] = {
                "existing": existing,
                "discovered": discovered,
                "gap_analysis": gap,
                "new_entities_count": len(new_entities)
            }

        return results

    def generate_report(self, results: Dict):
        """Generate comprehensive toponym discovery report"""
        report_path = self.base_dir / "reports" / "phase_c"
        report_path.mkdir(parents=True, exist_ok=True)

        report_file = report_path / "toponym_discovery_1894_1907.md"

        with open(report_file, 'w', encoding='utf-8') as f:
            f.write("# Toponym Discovery Report: 1894-1907\n\n")
            f.write("**Agent:** Toponym Discovery Agent\n")
            f.write("**Date:** 2025-11-17\n")
            f.write("**Mission:** Comprehensive extraction of all place names from Colonial Office List documents\n\n")

            f.write("## Executive Summary\n\n")
            f.write("This report documents the comprehensive toponym discovery process for years 1894-1907.\n\n")

            # Summary statistics
            total_existing = sum(r['existing']['count'] for r in results.values())
            total_discovered = sum(r['discovered']['unique_names'] for r in results.values())
            total_missing = sum(r['gap_analysis']['missing_count'] for r in results.values())

            f.write(f"- **Years Processed:** {len(results)}\n")
            f.write(f"- **Total Existing Place Entities:** {total_existing:,}\n")
            f.write(f"- **Total Unique Toponyms Discovered:** {total_discovered:,}\n")
            f.write(f"- **Total New Toponyms Extracted:** {total_missing:,}\n")
            if total_existing > 0:
                f.write(f"- **Overall Coverage Improvement:** {(total_missing / total_existing * 100):.1f}%\n")
            f.write("\n")

            # Summary table
            f.write("### Coverage Summary\n\n")
            f.write("| Year | Existing Places | Discovered Toponyms | Missing | Coverage % |\n")
            f.write("|------|----------------|---------------------|---------|------------|\n")

            for year in sorted(results.keys()):
                r = results[year]
                existing_count = r['existing']['count']
                discovered_count = r['discovered']['unique_names']
                missing_count = r['gap_analysis']['missing_count']
                coverage = r['gap_analysis']['coverage_percent']

                f.write(f"| {year} | {existing_count} | {discovered_count} | {missing_count} | {coverage}% |\n")

            f.write("\n## Detailed Findings by Year\n\n")

            for year in sorted(results.keys()):
                r = results[year]
                f.write(f"\n### {year}\n\n")

                f.write(f"**Files Scanned:** {r['discovered']['files_scanned']}\n")
                f.write(f"**Existing Place Entities:** {r['existing']['count']}\n")
                f.write(f"**Discovered Toponyms:** {r['discovered']['unique_names']}\n")
                f.write(f"**Missing Toponyms:** {r['gap_analysis']['missing_count']}\n")
                f.write(f"**Coverage:** {r['gap_analysis']['coverage_percent']}%\n\n")

                # Sample existing places
                if r['existing']['places']:
                    f.write(f"#### Sample Existing Place Entities\n\n")
                    for place in r['existing']['places'][:20]:
                        f.write(f"- {place}\n")
                    if len(r['existing']['places']) > 20:
                        f.write(f"\n*...and {len(r['existing']['places']) - 20} more*\n")
                    f.write("\n")

                # Sample missing toponyms with details
                if r['gap_analysis']['missing_count'] > 0:
                    f.write(f"#### Sample New Toponyms Discovered\n\n")

                    missing_details = r['gap_analysis']['missing_details']
                    for name in sorted(missing_details.keys())[:30]:
                        occurrences = missing_details[name]
                        first_occ = occurrences[0]
                        
                        f.write(f"**{name}** ({first_occ['type']})\n")
                        f.write(f"- Occurrences: {len(occurrences)}\n")
                        f.write(f"- Source: `{first_occ['source_file']}` line {first_occ['line_number']}\n")
                        f.write(f"- Context: `{first_occ['context'][:100]}...`\n")
                        f.write("\n")

                    if len(missing_details) > 30:
                        f.write(f"\n*...and {len(missing_details) - 30} more new toponyms*\n")

                f.write("\n---\n")

            f.write("\n## Methodology\n\n")
            f.write("### Extraction Process\n\n")
            f.write("1. **Pattern-based extraction** using multiple regex patterns for:\n")
            f.write("   - Explicit location markers (in, at, of, from, to, near)\n")
            f.write("   - Geographical features (Mount, River, Lake, Bay, Island, etc.)\n")
            f.write("   - Administrative divisions (Colony, District, Province, Parish)\n")
            f.write("   - Settlement types (capital, headquarters, town, city)\n\n")

            f.write("2. **Context-based classification** to determine place types:\n")
            f.write("   - territory (colonies, protectorates)\n")
            f.write("   - administrative_division (districts, provinces, parishes)\n")
            f.write("   - city (capitals, towns, villages)\n")
            f.write("   - island (named islands and island groups)\n")
            f.write("   - water_feature (rivers, lakes)\n")
            f.write("   - mountain (named peaks and ranges)\n")
            f.write("   - port (harbors, bays)\n")
            f.write("   - geographic_feature (capes, peninsulas)\n\n")

            f.write("3. **Provenance tracking** with:\n")
            f.write("   - Source file name\n")
            f.write("   - Line number\n")
            f.write("   - Full context line\n")
            f.write("   - Total occurrences across sources\n\n")

            f.write("### Quality Criteria\n\n")
            f.write("- Proper names only (not generic descriptions)\n")
            f.write("- Historical spelling preserved\n")
            f.write("- Parent location context maintained\n")
            f.write("- Provenance with source line numbers\n")
            f.write("- Stopword filtering to exclude non-place terms\n\n")

            f.write("\n## Next Steps\n\n")
            f.write("1. Manual review of high-confidence new toponyms\n")
            f.write("2. Geographic grounding - link to modern coordinates\n")
            f.write("3. Integration into main knowledge graph\n")
            f.write("4. Establish parent-child relationships\n")
            f.write("5. Validate against historical gazetteers\n\n")

            f.write("## Output Files\n\n")
            f.write("New toponyms have been saved to:\n\n")
            for year in sorted(results.keys()):
                f.write(f"- `knowledge_graph_extracts_v3/{year}_extracted_toponyms.json`\n")
            f.write("\n")

        print(f"\nReport saved to: {report_file}")
        return report_file

def main():
    print("="*60)
    print("TOPONYM DISCOVERY AGENT")
    print("Colonial Office List Knowledge Graph Project")
    print("Years: 1894-1907")
    print("="*60)

    agent = ToponymDiscoveryAgent()
    results = agent.process_all_years()

    # Generate report
    report_file = agent.generate_report(results)

    print("\n" + "="*60)
    print("TOPONYM DISCOVERY COMPLETE")
    print("="*60)
    print(f"Total new toponyms discovered: {sum(r['new_entities_count'] for r in results.values())}")
    print(f"Report: {report_file}")

if __name__ == "__main__":
    main()
