#!/usr/bin/env python3
"""
Colonial Office List Parser - Early Direct Format (1867)
Simplified parser for early years with direct colony descriptions
No PART markers, no cross-references
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict
import argparse


# Known colony names for 1867 era
KNOWN_COLONIES_1867 = {
    'ADEN', 'ANTIGUA', 'ASCENSION', 'AUSTRALIA',
    'BAHAMAS', 'BARBADOS', 'BASUTOLAND', 'BECHUANALAND', 'BERMUDA',
    'BRITISH COLUMBIA', 'BRITISH GUIANA', 'BRITISH HONDURAS',
    'CANADA', 'CAPE OF GOOD HOPE', 'CEYLON', 'CYPRUS',
    'DOMINICA', 'EAST AFRICA',
    'FALKLAND ISLANDS', 'FIJI',
    'GAMBIA', 'THE GAMBIA', 'GIBRALTAR', 'GOLD COAST', 'GRENADA',
    'HONG KONG',
    'JAMAICA',
    'LABUAN', 'LAGOS', 'LEEWARD ISLANDS',
    'MALTA', 'MANITOBA', 'MAURITIUS', 'MONTSERRAT',
    'NATAL', 'NEVIS', 'NEW BRUNSWICK', 'NEW SOUTH WALES', 'NEW ZEALAND',
    'NEWFOUNDLAND', 'NOVA SCOTIA',
    'PRINCE EDWARD ISLAND', 'QUEENSLAND',
    'ST. CHRISTOPHER', 'ST. HELENA', 'ST. KITTS', 'ST. LUCIA', 'ST. VINCENT',
    'SEYCHELLES', 'SIERRA LEONE', 'SOUTH AUSTRALIA',
    'TASMANIA', 'TOBAGO', 'TRINIDAD',
    'TURKS ISLANDS',
    'VANCOUVER ISLAND', 'VICTORIA',
    'WESTERN AUSTRALIA', 'WINDWARD ISLANDS',
}


@dataclass
class ColonySection:
    """Represents a colony section"""
    colony_name: str
    year: int
    start_line: int
    end_line: int
    char_count: int

    def to_dict(self):
        return asdict(self)


class EarlyDirectParser:
    """Parser for early direct format (1867)"""

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

        # Handle JSON format (should be new format for 1867)
        if isinstance(self.data, list) and len(self.data) > 0:
            if 'text' in self.data[0]:
                if len(self.data) == 1 and len(self.data[0]['text']) > 100000:
                    # Old format: single object
                    self.text = self.data[0]['text']
                else:
                    # New format: multiple pages
                    texts = [page['text'] for page in self.data if 'text' in page]
                    self.text = '\n'.join(texts)
            else:
                raise ValueError("No 'text' field found in JSON data")
        else:
            raise ValueError("Unexpected JSON structure")

        self.lines = self.text.split('\n')
        print(f"Loaded {len(self.lines)} lines from {self.json_path.name}")

    def is_likely_section_start(self, line_num: int, colony_name: str, previous_headers: List[Tuple[str, int]]) -> bool:
        """
        Check if this looks like a genuine colony section start
        (not a page header or reference)
        """
        if line_num + 5 >= len(self.lines):
            return False

        # Check if we already have this colony within the last 500 lines
        # If so, this is likely a page header
        for prev_name, prev_line in previous_headers:
            if prev_name == colony_name and (line_num - prev_line) < 500:
                return False

        # Check next few lines for descriptive content
        has_descriptive_content = False
        for i in range(line_num + 1, min(line_num + 10, len(self.lines))):
            line = self.lines[i].strip()

            # Skip empty lines
            if not line:
                continue

            # Look for typical opening phrases
            if (line.startswith('Is situated') or
                line.startswith('The ') or
                'latitude' in line.lower() or
                'longitude' in line.lower() or
                'area' in line.lower() or
                'miles' in line.lower()):
                has_descriptive_content = True
                break

            # Stop if we hit another colony header
            if line.rstrip('.') in KNOWN_COLONIES_1867:
                break

        return has_descriptive_content

    def find_all_colony_headers(self) -> List[Tuple[str, int]]:
        """
        Find all colony headers
        Returns: [(colony_name, line_number)]
        """
        found = []

        for i, line in enumerate(self.lines):
            line_stripped = line.strip().rstrip('.')

            # Check if this line matches a known colony
            if line_stripped in KNOWN_COLONIES_1867:
                # Verify it's a real section start
                if self.is_likely_section_start(i, line_stripped, found):
                    found.append((line_stripped, i))
                    print(f"  Found colony: {line_stripped:35s} at line {i}")
                else:
                    print(f"  Skipping page header/duplicate: {line_stripped:35s} at line {i}")

        print(f"\nFound {len(found)} colony headers")
        return found

    def find_colony_end(self, start_line: int, next_colony_start: Optional[int]) -> int:
        """
        Find where a colony section ends

        In direct format:
        - Colony ends at next colony header, or
        - End of meaningful content (before indices/tables)
        """
        if next_colony_start:
            return next_colony_start

        # If no next colony, look for end of document content
        # This might be before "INDEX" or "APPENDIX" sections
        search_start = start_line + 50  # Skip ahead to avoid false positives
        for i in range(search_start, len(self.lines)):
            line = self.lines[i].strip()

            # Look for document end markers
            if (line.startswith('INDEX') or
                line.startswith('APPENDIX') or
                line == 'END'):
                return i

        # Default to end of file
        return len(self.lines)

    def parse_all_colonies(self) -> List[ColonySection]:
        """Parse all colonies"""
        headers = self.find_all_colony_headers()

        colonies = []

        for idx, (name, start) in enumerate(headers):
            # Determine end
            next_start = headers[idx + 1][1] if idx + 1 < len(headers) else None
            end = self.find_colony_end(start, next_start)

            # Get character positions
            start_char = sum(len(self.lines[i]) + 1 for i in range(start))
            end_char = sum(len(self.lines[i]) + 1 for i in range(end))

            colony = ColonySection(
                colony_name=name,
                year=self.year,
                start_line=start,
                end_line=end,
                char_count=end_char - start_char
            )

            colonies.append(colony)

        print(f"\nTotal: {len(colonies)} colonies parsed")
        return colonies

    def export_to_json(self, colonies: List[ColonySection], output_path: str):
        """Export parsed data"""
        output_data = {
            'source_file': str(self.json_path),
            'year': self.year,
            'format': 'early_direct',
            'total_colonies': len(colonies),
            'colonies': [c.to_dict() for c in colonies]
        }

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(output_data, f, indent=2)

        print(f"\nExported to {output_path}")

    def export_full_text(self, colonies: List[ColonySection], output_dir: str):
        """Export each colony's full text to separate files"""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        for colony in colonies:
            colony_text = '\n'.join(self.lines[colony.start_line:colony.end_line])

            filename = f"{self.year}_{colony.colony_name.replace(' ', '_')}.txt"
            filepath = output_dir / filename

            with open(filepath, 'w') as f:
                f.write(colony_text)

        print(f"Exported {len(colonies)} colony text files to {output_dir}")


def main():
    parser = argparse.ArgumentParser(
        description='Parse Colonial Office List - Early Direct Format (1867)'
    )
    parser.add_argument('input_file', help='Path to Colonial Office List JSON file')
    parser.add_argument('-o', '--output', help='Output JSON file', default=None)
    parser.add_argument('--export-text', help='Export each colony as separate text file', action='store_true')

    args = parser.parse_args()

    if args.output is None:
        input_path = Path(args.input_file)
        args.output = input_path.parent.parent / "output" / f"{input_path.stem}_parsed_early_direct.json"

    # Parse
    col_parser = EarlyDirectParser(args.input_file)
    col_parser.load()

    print("\n=== Finding Colony Headers ===")
    colonies = col_parser.parse_all_colonies()

    # Show summary
    print("\n=== Colony Summary ===")
    for c in colonies:
        print(f"{c.colony_name:35s} lines {c.start_line:5d}-{c.end_line:5d} ({c.end_line-c.start_line:4d} lines, {c.char_count:7d} chars)")

    # Export
    col_parser.export_to_json(colonies, args.output)

    if args.export_text:
        text_dir = Path(args.output).parent / f"{Path(args.output).stem}_texts"
        col_parser.export_full_text(colonies, text_dir)


if __name__ == '__main__':
    main()
