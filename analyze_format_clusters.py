#!/usr/bin/env python3
"""
Analyze Colonial Office List files to identify format clusters
Groups years by structural similarity to create specialized parsers
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Tuple
from collections import defaultdict
import argparse


class FormatAnalyzer:
    """Analyze document structure to identify format patterns"""

    def __init__(self, base_dir: str):
        self.base_dir = Path(base_dir)
        self.results = []

    def get_all_json_files(self) -> List[Path]:
        """Find all Colonial Office List JSON files"""
        files = []

        # Find both old format (single file) and new format (directory)
        for item in sorted(self.base_dir.glob("colonial-office-list-*")):
            if item.is_file() and item.suffix == '.json':
                files.append(item)
            elif item.is_dir():
                json_file = item / "olmocr_results.json"
                if json_file.exists():
                    files.append(json_file)

        return files

    def extract_year(self, path: Path) -> int:
        """Extract year from filename"""
        match = re.search(r'(\d{4})', str(path))
        return int(match.group(1)) if match else 0

    def analyze_file(self, json_path: Path) -> Dict:
        """Analyze a single file's structure"""
        year = self.extract_year(json_path)

        try:
            with open(json_path, 'r') as f:
                data = json.load(f)

            # Basic structure
            is_single_object = len(data) == 1 if isinstance(data, list) else False
            num_pages = len(data) if isinstance(data, list) else 0

            # Get text
            if is_single_object and 'text' in data[0]:
                text = data[0]['text']
            else:
                texts = [page['text'] for page in data if 'text' in page]
                text = '\n'.join(texts)

            lines = text.split('\n')

            # Structural markers
            analysis = {
                'year': year,
                'file_path': str(json_path),
                'num_pages': num_pages,
                'total_lines': len(lines),
                'is_single_object': is_single_object,
                'has_part_markers': self.has_part_markers(lines),
                'has_foreign_consuls': self.count_pattern(lines, r'^Foreign Consuls?\.?$'),
                'has_situation_area': self.count_pattern(lines, r'Situation and Area'),
                'has_extent_boundaries': self.count_pattern(lines, r'Extent and Boundaries'),
                'has_general_description': self.count_pattern(lines, r'General Description'),
                'colony_name_count': self.count_colony_names(lines),
                'has_establishment': self.count_pattern(lines, r'Establishment|ESTABLISHMENT'),
                'has_civil_list': self.count_pattern(lines, r'Civil List|CIVIL LIST'),
                'avg_line_length': sum(len(l) for l in lines) / len(lines) if lines else 0,
            }

            return analysis

        except Exception as e:
            print(f"Error analyzing {json_path}: {e}")
            return {
                'year': year,
                'file_path': str(json_path),
                'error': str(e)
            }

    def has_part_markers(self, lines: List[str]) -> bool:
        """Check if document has Part I, II, III markers"""
        text = '\n'.join(lines[:5000])  # Check first 5000 lines
        return bool(re.search(r'PART (I|II|III|IV|V|1|2|3|4|5)', text))

    def count_pattern(self, lines: List[str], pattern: str) -> int:
        """Count occurrences of a pattern"""
        count = 0
        for line in lines:
            if re.search(pattern, line):
                count += 1
        return count

    def count_colony_names(self, lines: List[str]) -> int:
        """Count potential colony name headers"""
        from colonial_office_parser_v5 import KNOWN_COLONIES

        count = 0
        for line in lines:
            stripped = line.strip().rstrip('.')
            if stripped in KNOWN_COLONIES:
                count += 1
        return count

    def analyze_all(self) -> List[Dict]:
        """Analyze all files"""
        files = self.get_all_json_files()
        print(f"Found {len(files)} Colonial Office List files")

        for json_file in files:
            year = self.extract_year(json_file)
            print(f"Analyzing {year}...")
            analysis = self.analyze_file(json_file)
            self.results.append(analysis)

        return self.results

    def identify_clusters(self) -> Dict[str, List[int]]:
        """Group years into format clusters based on structural similarity"""
        clusters = defaultdict(list)

        for result in self.results:
            if 'error' in result:
                clusters['error'].append(result['year'])
                continue

            # Create signature based on structural features
            signature = (
                result['is_single_object'],
                result['has_part_markers'],
                result['has_foreign_consuls'] > 0,
                result['has_situation_area'] > 0,
                result['has_civil_list'] > 0,
            )

            cluster_name = self.signature_to_name(signature, result)
            clusters[cluster_name].append(result['year'])

        # Sort years within each cluster
        for cluster in clusters:
            clusters[cluster].sort()

        return dict(clusters)

    def signature_to_name(self, signature: Tuple, result: Dict) -> str:
        """Convert structural signature to readable cluster name"""
        is_single, has_parts, has_consuls, has_situation, has_civil = signature

        # Determine era by structural characteristics
        if is_single:
            return "modern_single_file"

        if has_civil:
            return "civil_list_format"

        if has_parts and has_consuls and has_situation:
            return "standard_colonial_list"

        if has_parts:
            return "part_based_structure"

        # Default cluster by decade
        year = result['year']
        decade = (year // 10) * 10
        return f"decade_{decade}s"

    def print_report(self):
        """Print analysis report"""
        print("\n" + "="*80)
        print("FORMAT ANALYSIS REPORT")
        print("="*80)

        # Summary statistics
        print(f"\nTotal files analyzed: {len(self.results)}")
        print(f"Year range: {min(r['year'] for r in self.results)} - {max(r['year'] for r in self.results)}")

        # Identify clusters
        clusters = self.identify_clusters()

        print(f"\n{'='*80}")
        print(f"FORMAT CLUSTERS IDENTIFIED: {len(clusters)}")
        print(f"{'='*80}\n")

        for cluster_name, years in sorted(clusters.items()):
            year_range = f"{min(years)}-{max(years)}" if years else "None"
            print(f"\n{cluster_name.upper().replace('_', ' ')}")
            print(f"  Years: {year_range}")
            print(f"  Count: {len(years)}")
            print(f"  Years: {', '.join(map(str, years))}")

            # Show structural characteristics of first year in cluster
            if years:
                sample = next(r for r in self.results if r['year'] == years[0])
                if 'error' not in sample:
                    print(f"\n  Characteristics:")
                    print(f"    - Single object format: {sample['is_single_object']}")
                    print(f"    - Has part markers: {sample['has_part_markers']}")
                    print(f"    - Foreign Consuls sections: {sample['has_foreign_consuls']}")
                    print(f"    - 'Situation and Area' sections: {sample['has_situation_area']}")
                    print(f"    - Colony name occurrences: {sample['colony_name_count']}")
                    print(f"    - Total lines: {sample['total_lines']:,}")

    def export_json(self, output_path: str):
        """Export analysis results to JSON"""
        output = {
            'analysis_results': self.results,
            'clusters': self.identify_clusters(),
        }

        with open(output_path, 'w') as f:
            json.dump(output, f, indent=2)

        print(f"\nExported analysis to {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description='Analyze Colonial Office List files to identify format clusters'
    )
    parser.add_argument(
        '--base-dir',
        default='historical_document_pipeline/processed_pdfs',
        help='Base directory containing Colonial Office List files'
    )
    parser.add_argument(
        '-o', '--output',
        default='output/format_analysis.json',
        help='Output JSON file'
    )

    args = parser.parse_args()

    analyzer = FormatAnalyzer(args.base_dir)
    analyzer.analyze_all()
    analyzer.print_report()
    analyzer.export_json(args.output)


if __name__ == '__main__':
    main()
