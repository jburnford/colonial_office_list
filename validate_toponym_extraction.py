#!/usr/bin/env python3
"""
Validation and Gap Analysis for Toponym Extraction
Analyzes the comprehensiveness of toponym extraction across all years
"""

import json
import os
import re
from pathlib import Path
from collections import defaultdict, Counter

class ToponymValidator:
    def __init__(self, year: int):
        self.year = year
        self.source_dir = Path(f"/home/user/colonial_office_list/output_2/{year}_manual_parsed")
        self.v3_file = Path(f"/home/user/colonial_office_list/knowledge_graph_extracts_v3/{year}_extracted_toponyms.json")
        self.original_file = Path(f"/home/user/colonial_office_list/knowledge_graph_extracts/{year}_extracted.json")

    def load_data(self):
        """Load all relevant data files"""
        # Load v3 (enhanced) file
        if self.v3_file.exists():
            with open(self.v3_file, 'r', encoding='utf-8') as f:
                self.v3_data = json.load(f)
        else:
            self.v3_data = None

        # Load original file
        if self.original_file.exists():
            with open(self.original_file, 'r', encoding='utf-8') as f:
                self.original_data = json.load(f)
        else:
            self.original_data = None

    def analyze_coverage(self):
        """Analyze toponym extraction coverage"""
        results = {
            'year': self.year,
            'original_places': 0,
            'v3_places': 0,
            'new_places': 0,
            'place_types': {},
            'colonies_covered': [],
            'extraction_agents': {},
            'sample_toponyms': []
        }

        if self.original_data:
            results['original_places'] = len(self.original_data.get('entities', {}).get('places', []))

        if self.v3_data:
            places = self.v3_data.get('entities', {}).get('places', [])
            results['v3_places'] = len(places)
            results['new_places'] = results['v3_places'] - results['original_places']

            # Analyze place types
            type_counter = Counter([p.get('type', 'unknown') for p in places])
            results['place_types'] = dict(type_counter)

            # Analyze extraction agents
            agent_counter = Counter([p.get('provenance', {}).get('extraction_agent', 'unknown') for p in places])
            results['extraction_agents'] = dict(agent_counter)

            # Get sample toponyms by colony
            colonies = {}
            for p in places:
                parent = p.get('parent_location', 'unknown')
                if parent not in colonies:
                    colonies[parent] = []
                colonies[parent].append(p['name'])

            results['colonies_covered'] = list(colonies.keys())
            results['colonies_count'] = len(colonies)

            # Sample toponyms (first 10 from largest colonies)
            sorted_colonies = sorted(colonies.items(), key=lambda x: len(x[1]), reverse=True)
            for colony, toponyms in sorted_colonies[:3]:
                results['sample_toponyms'].append({
                    'colony': colony,
                    'count': len(toponyms),
                    'examples': toponyms[:10]
                })

        return results

    def scan_for_potential_gaps(self):
        """Scan source files for potential missing toponyms"""
        if not self.source_dir.exists():
            return []

        # Load extracted place names
        extracted_names = set()
        if self.v3_data:
            places = self.v3_data.get('entities', {}).get('places', [])
            for p in places:
                extracted_names.add(p['name'].lower())
                # Also add variants
                extracted_names.add(p['name'].lower().replace('st.', 'saint'))
                extracted_names.add(p['name'].lower().replace('saint', 'st.'))

        # Scan source files for potential place names
        potential_gaps = []
        geographic_keywords = [
            'town', 'city', 'village', 'island', 'bay', 'river', 'mountain', 'mount',
            'port', 'cape', 'district', 'parish', 'county', 'fort', 'point', 'valley',
            'hill', 'estate', 'settlement', 'harbor', 'harbour'
        ]

        colony_files = sorted(self.source_dir.glob("*.md"))[:5]  # Sample first 5 colonies

        for colony_file in colony_files:
            try:
                with open(colony_file, 'r', encoding='utf-8') as f:
                    text = f.read()

                # Find lines with geographic keywords
                lines = text.split('\n')
                for line_num, line in enumerate(lines, 1):
                    line_lower = line.lower()

                    # Check for geographic keywords
                    if any(kw in line_lower for kw in geographic_keywords):
                        # Extract capitalized phrases
                        cap_phrases = re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})\b', line)

                        for phrase in cap_phrases:
                            phrase_lower = phrase.lower()

                            # Check if NOT already extracted
                            if phrase_lower not in extracted_names and len(phrase) > 5:
                                # Check if it looks like a place name
                                if any(kw in line_lower for kw in geographic_keywords):
                                    potential_gaps.append({
                                        'name': phrase,
                                        'colony': colony_file.stem,
                                        'context': line.strip()[:100],
                                        'line': line_num
                                    })

            except Exception as e:
                continue

        # Deduplicate
        seen = set()
        unique_gaps = []
        for gap in potential_gaps:
            if gap['name'].lower() not in seen:
                seen.add(gap['name'].lower())
                unique_gaps.append(gap)

        return unique_gaps[:20]  # Return top 20 potential gaps


def main():
    """Generate comprehensive validation report"""
    years = [1867, 1877, 1880, 1883, 1886, 1888, 1889, 1890]

    all_results = []
    total_original = 0
    total_v3 = 0

    print("="*80)
    print("TOPONYM EXTRACTION VALIDATION REPORT")
    print("Colonial Office List Knowledge Graph Project")
    print("Years: 1867-1890")
    print("="*80)
    print()

    for year in years:
        print(f"\nProcessing {year}...")
        validator = ToponymValidator(year)
        validator.load_data()
        results = validator.analyze_coverage()
        all_results.append(results)

        total_original += results['original_places']
        total_v3 += results['v3_places']

    # Print summary table
    print("\n" + "="*80)
    print("EXTRACTION COVERAGE SUMMARY")
    print("="*80)
    print(f"{'Year':<8} {'Original':<12} {'Enhanced':<12} {'New':<12} {'% Increase':<15} {'Colonies':<10}")
    print("-"*80)

    for result in all_results:
        pct = ((result['new_places'] / result['original_places']) * 100) if result['original_places'] > 0 else float('inf')
        pct_str = f"{pct:.1f}%" if pct != float('inf') else "NEW"

        print(f"{result['year']:<8} {result['original_places']:<12} {result['v3_places']:<12} "
              f"{result['new_places']:<12} {pct_str:<15} {result.get('colonies_count', 0):<10}")

    print("-"*80)
    print(f"{'TOTAL':<8} {total_original:<12} {total_v3:<12} {total_v3 - total_original:<12} "
          f"{((total_v3 - total_original) / total_original * 100):.1f}%")

    # Place type distribution
    print("\n" + "="*80)
    print("PLACE TYPE DISTRIBUTION (Sample from 1867)")
    print("="*80)

    if all_results:
        sample_year = all_results[0]
        sorted_types = sorted(sample_year['place_types'].items(), key=lambda x: x[1], reverse=True)
        for place_type, count in sorted_types[:15]:
            print(f"  {place_type:<20} {count:>6}")

    # Extraction agents
    print("\n" + "="*80)
    print("EXTRACTION AGENTS (Sample from 1867)")
    print("="*80)

    if all_results:
        sample_year = all_results[0]
        for agent, count in sample_year['extraction_agents'].items():
            print(f"  {agent:<50} {count:>6}")

    # Sample toponyms
    print("\n" + "="*80)
    print("SAMPLE TOPONYMS BY COLONY (1867)")
    print("="*80)

    if all_results and all_results[0]['sample_toponyms']:
        for sample in all_results[0]['sample_toponyms']:
            print(f"\n{sample['colony']} ({sample['count']} toponyms):")
            for name in sample['examples']:
                print(f"  - {name}")

    # Gap analysis
    print("\n" + "="*80)
    print("POTENTIAL GAPS ANALYSIS (Sample: 1867)")
    print("="*80)

    validator = ToponymValidator(1867)
    validator.load_data()
    gaps = validator.scan_for_potential_gaps()

    if gaps:
        print(f"\nFound {len(gaps)} potential missing toponyms in sample scan:")
        for gap in gaps[:10]:
            print(f"\n  {gap['name']} ({gap['colony']})")
            print(f"    Context: {gap['context']}")
    else:
        print("\nNo significant gaps found in sample scan. Extraction appears comprehensive.")

    # Save results
    output_file = Path("/home/user/colonial_office_list/toponym_validation_results.json")
    with open(output_file, 'w') as f:
        json.dump({
            'years_analyzed': years,
            'summary': {
                'total_original': total_original,
                'total_enhanced': total_v3,
                'total_new': total_v3 - total_original,
                'percent_increase': ((total_v3 - total_original) / total_original * 100) if total_original > 0 else 0
            },
            'yearly_results': all_results,
            'potential_gaps_sample': gaps[:20]
        }, f, indent=2)

    print(f"\n\nValidation results saved to: {output_file}")


if __name__ == "__main__":
    main()
