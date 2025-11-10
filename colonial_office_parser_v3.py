#!/usr/bin/env python3
"""
Colonial Office List Parser V3
Uses "Foreign Consuls" as reliable end markers and works backwards to find colony names
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict
import argparse


@dataclass
class ColonySection:
    """Represents a colony section"""
    colony_name: str
    year: int
    start_line: int
    end_line: int
    has_foreign_consuls: bool
    text_preview: str  # First 500 chars

    def to_dict(self):
        return asdict(self)


class ColonialOfficeParserV3:
    """Parser using Foreign Consuls as anchors"""

    def __init__(self, json_path: str):
        self.json_path = Path(json_path)
        self.data = None
        self.text = None
        self.lines = []
        self.year = self._extract_year_from_filename()

    def _extract_year_from_filename(self) -> int:
        match = re.search(r'(\d{4})', self.json_path.name)
        return int(match.group(1)) if match else 0

    def load(self):
        """Load JSON data"""
        with open(self.json_path, 'r') as f:
            self.data = json.load(f)

        if isinstance(self.data, list) and len(self.data) > 0:
            self.text = self.data[0]['text']
        else:
            raise ValueError("Unexpected JSON structure")

        self.lines = self.text.split('\n')
        print(f"Loaded {len(self.lines)} lines from {self.json_path.name}")

    def find_foreign_consuls_markers(self) -> List[int]:
        """Find all 'Foreign Consuls' lines"""
        markers = []
        for i, line in enumerate(self.lines):
            # Look for Foreign Consuls (with variations)
            if re.match(r'^Foreign Consuls?\.?$', line.strip()):
                markers.append(i)

        print(f"Found {len(markers)} 'Foreign Consuls' markers")
        return markers

    def find_colony_name_before(self, end_line: int, search_start: int = 0) -> Tuple[Optional[str], int]:
        """
        Search backwards from end_line to find the colony name
        Returns: (colony_name, start_line) or (None, -1)
        """
        # Search backwards from end_line
        for i in range(end_line - 1, search_start, -1):
            line = self.lines[i].strip()

            # Skip empty lines
            if not line:
                continue

            # Colony names are ALL CAPS with period, relatively short
            # Examples: "CANADA.", "CAPE OF GOOD HOPE.", "NEW SOUTH WALES."
            if re.match(r'^[A-Z][A-Z\s\'\-\.]{2,40}\.$', line):
                # Further validation: shouldn't contain too many lowercase
                if line.count(line.lower()) < len(line) * 0.3:  # Less than 30% lowercase
                    colony_name = line.rstrip('.')

                    # Skip if it looks like a section header
                    skip_patterns = [
                        'GOVERNMENT', 'DEPARTMENT', 'ESTABLISHMENT', 'MINISTRY',
                        'OFFICE', 'SERVICE', 'RAILWAYS', 'POSTAL', 'JUDICIAL',
                        'ECCLESIASTICAL', 'MILITARY', 'NAVAL', 'FOREIGN CONSULS',
                        'PART', 'CONTENTS', 'INDEX'
                    ]

                    is_skip = False
                    for pattern in skip_patterns:
                        if pattern in colony_name:
                            is_skip = True
                            break

                    if not is_skip:
                        return (colony_name, i)

        return (None, -1)

    def find_colony_boundaries(self) -> List[ColonySection]:
        """
        Find colony boundaries using Foreign Consuls as end markers
        """
        foreign_consuls_lines = self.find_foreign_consuls_markers()

        colonies = []
        search_start = 0

        for fc_line in foreign_consuls_lines:
            # Find colony name before this Foreign Consuls marker
            colony_name, start_line = self.find_colony_name_before(fc_line, search_start)

            if colony_name:
                # Create colony section
                # End is after the Foreign Consuls section (look ahead ~50 lines for the consuls list)
                end_line = min(fc_line + 50, len(self.lines))

                # Get text preview
                section_text = '\n'.join(self.lines[start_line:end_line])
                text_preview = section_text[:500]

                colony = ColonySection(
                    colony_name=colony_name,
                    year=self.year,
                    start_line=start_line,
                    end_line=end_line,
                    has_foreign_consuls=True,
                    text_preview=text_preview
                )

                colonies.append(colony)
                print(f"  {colony_name}: lines {start_line}-{end_line} ({end_line-start_line} lines)")

                # Next search starts from this end
                search_start = end_line

        # Now refine boundaries: each colony ends where next one starts
        for i in range(len(colonies) - 1):
            colonies[i].end_line = colonies[i+1].start_line

        # Last colony: extend to Part V or end of Part II
        if colonies:
            # Look for "PART V" or "PART III" as end of Part II
            for i in range(colonies[-1].end_line, len(self.lines)):
                if re.match(r'^PART (V|III|3|5)', self.lines[i]):
                    colonies[-1].end_line = i
                    break

        print(f"\nFound {len(colonies)} colonies with Foreign Consuls markers")
        return colonies

    def find_colonies_without_foreign_consuls(self, known_colonies: List[ColonySection]) -> List[ColonySection]:
        """
        Find colonies that don't have Foreign Consuls sections
        These are typically within the gaps between known colonies
        """
        additional = []

        # Check gaps between known colonies
        for i in range(len(known_colonies) - 1):
            start = known_colonies[i].end_line
            end = known_colonies[i+1].start_line

            # If there's a significant gap, look for colony headers
            if end - start > 100:  # Minimum 100 lines to be a colony
                for line_num in range(start, end):
                    line = self.lines[line_num].strip()

                    # Look for ALL-CAPS colony-like headers
                    if re.match(r'^[A-Z][A-Z\s\'\-\.]{2,40}\.$', line):
                        # Validate it's not a section header
                        colony_name = line.rstrip('.')

                        skip_patterns = [
                            'GOVERNMENT', 'DEPARTMENT', 'ESTABLISHMENT', 'MINISTRY',
                            'OFFICE', 'SERVICE', 'RAILWAYS', 'POSTAL', 'JUDICIAL',
                            'ECCLESIASTICAL', 'MILITARY', 'NAVAL', 'FOREIGN CONSULS',
                            'PART', 'CONTENTS', 'INDEX'
                        ]

                        is_skip = False
                        for pattern in skip_patterns:
                            if pattern in colony_name:
                                is_skip = True
                                break

                        if not is_skip:
                            # Found a potential colony - add it
                            # End is either next colony or end of gap
                            colony_end = end

                            # Look for next potential colony header
                            for next_line in range(line_num + 1, end):
                                next = self.lines[next_line].strip()
                                if re.match(r'^[A-Z][A-Z\s\'\-\.]{2,40}\.$', next):
                                    next_name = next.rstrip('.')
                                    is_next_skip = False
                                    for pattern in skip_patterns:
                                        if pattern in next_name:
                                            is_next_skip = True
                                            break
                                    if not is_next_skip:
                                        colony_end = next_line
                                        break

                            text_preview = '\n'.join(self.lines[line_num:colony_end])[:500]

                            colony = ColonySection(
                                colony_name=colony_name,
                                year=self.year,
                                start_line=line_num,
                                end_line=colony_end,
                                has_foreign_consuls=False,
                                text_preview=text_preview
                            )

                            additional.append(colony)
                            print(f"  {colony_name} (no FC): lines {line_num}-{colony_end} ({colony_end-line_num} lines)")

        print(f"\nFound {len(additional)} additional colonies without Foreign Consuls")
        return additional

    def parse_all_colonies(self) -> List[ColonySection]:
        """Parse all colonies"""
        # First, find colonies with Foreign Consuls markers (reliable)
        colonies_with_fc = self.find_colony_boundaries()

        # Then, find colonies without Foreign Consuls in the gaps
        colonies_without_fc = self.find_colonies_without_foreign_consuls(colonies_with_fc)

        # Combine and sort by start_line
        all_colonies = colonies_with_fc + colonies_without_fc
        all_colonies.sort(key=lambda c: c.start_line)

        print(f"\nTotal: {len(all_colonies)} colonies")
        return all_colonies

    def export_to_json(self, colonies: List[ColonySection], output_path: str):
        """Export parsed data"""
        output_data = {
            'source_file': str(self.json_path),
            'year': self.year,
            'total_colonies': len(colonies),
            'colonies': [c.to_dict() for c in colonies]
        }

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(output_data, f, indent=2)

        print(f"\nExported to {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description='Parse Colonial Office List JSON files (V3 - Foreign Consuls anchoring)'
    )
    parser.add_argument('input_file', help='Path to Colonial Office List JSON file')
    parser.add_argument('-o', '--output', help='Output JSON file', default=None)

    args = parser.parse_args()

    if args.output is None:
        input_path = Path(args.input_file)
        args.output = input_path.parent.parent / "output" / f"{input_path.stem}_parsed_v3.json"

    # Parse
    col_parser = ColonialOfficeParserV3(args.input_file)
    col_parser.load()

    print("\n=== Finding Colony Boundaries ===")
    colonies = col_parser.parse_all_colonies()

    # Show summary
    print("\n=== Colony Summary ===")
    for c in colonies:
        fc_marker = "✓" if c.has_foreign_consuls else "✗"
        print(f"{fc_marker} {c.colony_name:30s} lines {c.start_line:5d}-{c.end_line:5d} ({c.end_line-c.start_line:4d} lines)")

    # Export
    col_parser.export_to_json(colonies, args.output)


if __name__ == '__main__':
    main()
