#!/usr/bin/env python3
"""
Colonial Office List Parser V4
Uses known colony names and Foreign Consuls as reliable markers
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict
import argparse


# Known colony names across all years (1883-1915)
KNOWN_COLONIES = {
    'ADEN', 'ANTIGUA', 'ASCENSION', 'AUSTRALIA',
    'BAHAMAS', 'BARBADOS', 'BASUTOLAND', 'BECHUANALAND', 'BERMUDA',
    'BRITISH BECHUANALAND', 'BRITISH CENTRAL AFRICA', 'BRITISH COLUMBIA',
    'BRITISH EAST AFRICA', 'BRITISH GUIANA', 'BRITISH HONDURAS',
    'BRITISH NEW GUINEA', 'BRITISH NORTH BORNEO',
    'CANADA', 'CAPE OF GOOD HOPE', 'CAYMAN ISLANDS', 'CEYLON', 'CYPRUS',
    'DOMINICA', 'EAST AFRICA',
    'FALKLAND ISLANDS', 'FIJI',
    'GAMBIA', 'GIBRALTAR', 'GOLD COAST', 'GRENADA',
    'HONG KONG',
    'JAMAICA',
    'KEEWATIN', 'LABUAN', 'LAGOS', 'LEEWARD ISLANDS',
    'MALTA', 'MANITOBA', 'MANITOBA AND KEEWATIN', 'MAURITIUS', 'MONTSERRAT',
    'NATAL', 'NEVIS', 'NEW BRUNSWICK', 'NEW SOUTH WALES', 'NEW ZEALAND',
    'NEWFOUNDLAND', 'NIGER COAST PROTECTORATE', 'NORTH BORNEO',
    'NOVA SCOTIA', 'PRINCE EDWARD ISLAND', 'QUEENSLAND',
    'RHODESIA',
    'ST. CHRISTOPHER', 'ST. HELENA', 'ST. KITTS', 'ST. LUCIA', 'ST. VINCENT',
    'SEYCHELLES', 'SIERRA LEONE', 'SOMALILAND', 'SOUTH AUSTRALIA', 'STRAITS SETTLEMENTS',
    'TASMANIA', 'TOBAGO', 'TRANSVAAL', 'TRINIDAD', 'TRISTAN D\'ACUNHA',
    'TURKS AND CAICOS ISLANDS', 'TURKS ISLANDS', 'UGANDA',
    'VICTORIA',
    'WESTERN AUSTRALIA', 'WINDWARD ISLANDS',
    'ZANZIBAR', 'ZULULAND'
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


class ColonialOfficeParserV4:
    """Parser using known colony names"""

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

    def find_all_colony_headers(self) -> List[Tuple[str, int]]:
        """
        Find all colony headers by matching against known colony names
        Returns: [(colony_name, line_number)]
        """
        found = []

        for i, line in enumerate(self.lines):
            line_stripped = line.strip().rstrip('.')

            # Check if this line matches a known colony
            if line_stripped in KNOWN_COLONIES:
                found.append((line_stripped, i))
                print(f"  Found: {line_stripped:35s} at line {i}")

        print(f"\nFound {len(found)} colony headers")
        return found

    def find_colony_end(self, start_line: int, next_colony_start: Optional[int]) -> int:
        """
        Find where a colony section ends
        Priority: Foreign Consuls marker > next colony start > Part III
        """
        search_end = next_colony_start if next_colony_start else len(self.lines)

        # Look for "Foreign Consuls" marker
        for i in range(start_line, search_end):
            if re.match(r'^Foreign Consuls?\.?$', self.lines[i].strip()):
                # End is ~50 lines after Foreign Consuls (to include the consul list)
                return min(i + 50, search_end)

        # If no Foreign Consuls found, end at next colony or Part III
        for i in range(start_line + 100, search_end):
            if re.match(r'^PART (III|3)', self.lines[i]):
                return i

        return search_end

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
        description='Parse Colonial Office List JSON files (V4 - known colonies)'
    )
    parser.add_argument('input_file', help='Path to Colonial Office List JSON file')
    parser.add_argument('-o', '--output', help='Output JSON file', default=None)
    parser.add_argument('--export-text', help='Export each colony as separate text file', action='store_true')

    args = parser.parse_args()

    if args.output is None:
        input_path = Path(args.input_file)
        args.output = input_path.parent.parent / "output" / f"{input_path.stem}_parsed_v4.json"

    # Parse
    col_parser = ColonialOfficeParserV4(args.input_file)
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
