#!/usr/bin/env python3
"""
Knowledge Graph Builder for Colonial Office Lists
Combines multi-year employee data to track career progressions.
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Set, Tuple, Optional
from collections import defaultdict
from dataclasses import dataclass
import argparse


@dataclass
class PersonRecord:
    """Represents a unique person across multiple years"""
    canonical_name: str
    name_variants: Set[str]
    positions: List[Dict]  # List of {year, colony, position, salary, honors}
    career_span: Tuple[int, int]  # (first_year, last_year)

    def to_dict(self):
        return {
            'canonical_name': self.canonical_name,
            'name_variants': list(self.name_variants),
            'positions': sorted(self.positions, key=lambda x: x['year']),
            'career_span': self.career_span,
            'total_positions': len(self.positions),
            'colonies_served': list(set(p['colony'] for p in self.positions))
        }


class KnowledgeGraphBuilder:
    """Build knowledge graph from parsed Colonial Office List data"""

    def __init__(self):
        self.persons: Dict[str, PersonRecord] = {}
        self.all_employees: List[Dict] = []
        self.name_to_person_id: Dict[str, str] = {}

    def load_parsed_data(self, file_paths: List[str]):
        """Load multiple parsed JSON files"""
        print(f"Loading {len(file_paths)} files...")

        for path in sorted(file_paths):
            path = Path(path)
            print(f"  Loading {path.name}...")

            with open(path, 'r') as f:
                data = json.load(f)

            year = data['year']

            for colony in data['colonies']:
                colony_name = colony['colony_name']

                for employee in colony['employees']:
                    self.all_employees.append({
                        'year': year,
                        'colony': colony_name,
                        'name': employee['name'],
                        'position': employee['position'],
                        'salary': employee.get('salary'),
                        'honors': employee.get('honors'),
                        'raw_text': employee.get('raw_text', '')
                    })

        print(f"Loaded {len(self.all_employees)} employee records")

    def normalize_name(self, name: str) -> str:
        """Normalize a name for matching (handle initials, etc.)"""
        # Remove common prefixes/suffixes
        name = re.sub(r'\b(Sir|Hon|Rev|Dr|Prof|Col|Lieut|Capt|Major|Gen)\b\.?', '', name, flags=re.IGNORECASE)

        # Remove punctuation except spaces and hyphens
        name = re.sub(r'[^\w\s\-]', '', name)

        # Normalize whitespace
        name = ' '.join(name.split())

        # Lowercase for comparison
        return name.strip().lower()

    def extract_surname(self, name: str) -> str:
        """Extract likely surname from a name"""
        # Normalize first
        norm = self.normalize_name(name)

        # Simple heuristic: last word is usually surname
        parts = norm.split()
        if parts:
            return parts[-1]
        return norm

    def names_match(self, name1: str, name2: str) -> bool:
        """
        Determine if two names likely refer to the same person.
        Handles initials, partial names, etc.
        """
        norm1 = self.normalize_name(name1)
        norm2 = self.normalize_name(name2)

        # Exact match
        if norm1 == norm2:
            return True

        # Same surname?
        surname1 = self.extract_surname(name1)
        surname2 = self.extract_surname(name2)

        if not surname1 or not surname2 or surname1 != surname2:
            return False

        # Same surname - check if first name/initials compatible
        parts1 = norm1.split()
        parts2 = norm2.split()

        # Extract everything before surname
        first1 = ' '.join(p for p in parts1[:-1])
        first2 = ' '.join(p for p in parts2[:-1])

        if not first1 or not first2:
            return True  # One has only surname

        # Check if initials match
        # E.g., "J Smith" matches "John Smith"
        if len(first1) == 1 or len(first2) == 1:
            return first1[0] == first2[0]

        # Check if one is contained in the other (handles middle names)
        if first1 in first2 or first2 in first1:
            return True

        # Check first letter match
        if first1[0] == first2[0]:
            return True

        return False

    def find_similar_persons(self, name: str, threshold: int = 2) -> List[str]:
        """Find person IDs with similar names"""
        matches = []

        for person_id, person in self.persons.items():
            # Check canonical name
            if self.names_match(name, person.canonical_name):
                matches.append(person_id)
                continue

            # Check name variants
            for variant in person.name_variants:
                if self.names_match(name, variant):
                    matches.append(person_id)
                    break

        return matches

    def merge_persons(self, person_id1: str, person_id2: str):
        """Merge two person records"""
        if person_id1 not in self.persons or person_id2 not in self.persons:
            return

        person1 = self.persons[person_id1]
        person2 = self.persons[person_id2]

        # Merge into person1
        person1.name_variants.update(person2.name_variants)
        person1.positions.extend(person2.positions)

        # Update career span
        all_years = [p['year'] for p in person1.positions]
        person1.career_span = (min(all_years), max(all_years))

        # Update name mappings
        for variant in person2.name_variants:
            self.name_to_person_id[variant] = person_id1

        # Remove person2
        del self.persons[person_id2]

    def build_person_records(self):
        """Build PersonRecord objects by matching employees across years"""
        print("\nBuilding person records...")

        for emp in self.all_employees:
            name = emp['name']

            # Find existing person or create new
            similar = self.find_similar_persons(name)

            if similar:
                # Add to existing person
                person_id = similar[0]
                person = self.persons[person_id]

                person.name_variants.add(name)
                person.positions.append({
                    'year': emp['year'],
                    'colony': emp['colony'],
                    'position': emp['position'],
                    'salary': emp['salary'],
                    'honors': emp['honors']
                })

                # Update career span
                years = [p['year'] for p in person.positions]
                person.career_span = (min(years), max(years))

                # Map this name variant to person
                self.name_to_person_id[name] = person_id

                # If multiple matches, merge them
                if len(similar) > 1:
                    for pid in similar[1:]:
                        self.merge_persons(person_id, pid)

            else:
                # Create new person
                person_id = f"person_{len(self.persons):06d}"

                person = PersonRecord(
                    canonical_name=name,
                    name_variants={name},
                    positions=[{
                        'year': emp['year'],
                        'colony': emp['colony'],
                        'position': emp['position'],
                        'salary': emp['salary'],
                        'honors': emp['honors']
                    }],
                    career_span=(emp['year'], emp['year'])
                )

                self.persons[person_id] = person
                self.name_to_person_id[name] = person_id

        print(f"Created {len(self.persons)} unique person records")

    def analyze_careers(self) -> Dict:
        """Analyze career patterns"""
        stats = {
            'total_persons': len(self.persons),
            'multi_year_careers': 0,
            'multi_colony_careers': 0,
            'longest_career_span': 0,
            'most_positions': 0,
            'career_length_distribution': defaultdict(int),
            'colonies_per_person': defaultdict(int),
            'common_position_progressions': defaultdict(int)
        }

        for person in self.persons.values():
            career_length = person.career_span[1] - person.career_span[0] + 1

            if career_length > 1:
                stats['multi_year_careers'] += 1

            colonies = set(p['colony'] for p in person.positions)
            if len(colonies) > 1:
                stats['multi_colony_careers'] += 1

            stats['longest_career_span'] = max(stats['longest_career_span'], career_length)
            stats['most_positions'] = max(stats['most_positions'], len(person.positions))

            stats['career_length_distribution'][career_length] += 1
            stats['colonies_per_person'][len(colonies)] += 1

            # Track position progressions (consecutive positions)
            sorted_positions = sorted(person.positions, key=lambda x: x['year'])
            for i in range(len(sorted_positions) - 1):
                progression = (sorted_positions[i]['position'], sorted_positions[i+1]['position'])
                stats['common_position_progressions'][progression] += 1

        # Convert defaultdicts to regular dicts for JSON serialization
        stats['career_length_distribution'] = dict(stats['career_length_distribution'])
        stats['colonies_per_person'] = dict(stats['colonies_per_person'])
        stats['common_position_progressions'] = {
            f"{p[0]} -> {p[1]}": count
            for p, count in sorted(stats['common_position_progressions'].items(),
                                  key=lambda x: x[1], reverse=True)[:20]
        }

        return stats

    def export_knowledge_graph(self, output_path: str):
        """Export knowledge graph to JSON"""
        print(f"\nExporting knowledge graph to {output_path}...")

        stats = self.analyze_careers()

        output_data = {
            'metadata': {
                'total_persons': len(self.persons),
                'total_positions': len(self.all_employees),
                'analysis': stats
            },
            'persons': {
                person_id: person.to_dict()
                for person_id, person in self.persons.items()
            }
        }

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(output_data, f, indent=2)

        print(f"Exported {len(self.persons)} persons to {output_path}")

    def generate_report(self) -> str:
        """Generate analysis report"""
        stats = self.analyze_careers()

        report = []
        report.append("=" * 70)
        report.append("COLONIAL OFFICE CAREER PROGRESSION KNOWLEDGE GRAPH")
        report.append("=" * 70)
        report.append("")

        report.append(f"Total Unique Persons: {stats['total_persons']}")
        report.append(f"Total Position Records: {len(self.all_employees)}")
        report.append(f"Multi-Year Careers: {stats['multi_year_careers']} ({stats['multi_year_careers']/stats['total_persons']*100:.1f}%)")
        report.append(f"Multi-Colony Careers: {stats['multi_colony_careers']} ({stats['multi_colony_careers']/stats['total_persons']*100:.1f}%)")
        report.append(f"Longest Career Span: {stats['longest_career_span']} years")
        report.append(f"Most Positions Held: {stats['most_positions']}")

        report.append("\n" + "=" * 70)
        report.append("CAREER LENGTH DISTRIBUTION")
        report.append("=" * 70)
        for length in sorted(stats['career_length_distribution'].keys()):
            count = stats['career_length_distribution'][length]
            report.append(f"  {length:2d} years: {count:4d} persons {'█' * int(count/10)}")

        report.append("\n" + "=" * 70)
        report.append("COLONIES PER PERSON")
        report.append("=" * 70)
        for num_colonies in sorted(stats['colonies_per_person'].keys()):
            count = stats['colonies_per_person'][num_colonies]
            report.append(f"  {num_colonies:2d} colonies: {count:4d} persons {'█' * int(count/10)}")

        report.append("\n" + "=" * 70)
        report.append("TOP POSITION PROGRESSIONS")
        report.append("=" * 70)
        for progression, count in list(stats['common_position_progressions'].items())[:10]:
            report.append(f"  {progression}: {count} times")

        report.append("\n" + "=" * 70)
        report.append("SAMPLE CAREER PATHS")
        report.append("=" * 70)

        # Show some interesting careers
        interesting = sorted(self.persons.values(),
                           key=lambda p: len(p.positions), reverse=True)[:5]

        for person in interesting:
            report.append(f"\n{person.canonical_name}")
            report.append(f"  Career span: {person.career_span[0]}-{person.career_span[1]}")
            report.append(f"  Colonies: {', '.join(set(p['colony'] for p in person.positions))}")
            report.append("  Positions:")
            for pos in sorted(person.positions, key=lambda x: x['year']):
                salary = f" ({pos['salary']})" if pos['salary'] else ""
                report.append(f"    {pos['year']}: {pos['position']} in {pos['colony']}{salary}")

        return "\n".join(report)


def main():
    parser = argparse.ArgumentParser(
        description='Build knowledge graph from parsed Colonial Office List data'
    )
    parser.add_argument(
        'input_files',
        nargs='+',
        help='Parsed JSON files from colonial_office_parser.py'
    )
    parser.add_argument(
        '-o', '--output',
        help='Output knowledge graph JSON file',
        default='output/knowledge_graph.json'
    )
    parser.add_argument(
        '-r', '--report',
        help='Generate analysis report to this file',
        default=None
    )

    args = parser.parse_args()

    # Build knowledge graph
    kg = KnowledgeGraphBuilder()
    kg.load_parsed_data(args.input_files)
    kg.build_person_records()

    # Export
    kg.export_knowledge_graph(args.output)

    # Generate report
    report = kg.generate_report()
    if args.report:
        with open(args.report, 'w') as f:
            f.write(report)
        print(f"Report saved to {args.report}")
    else:
        print("\n" + report)


if __name__ == '__main__':
    main()
