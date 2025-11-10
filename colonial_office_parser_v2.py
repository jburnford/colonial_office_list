#!/usr/bin/env python3
"""
Colonial Office List Parser V2
Uses hardcoded structural markers for robust parsing
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict
import argparse


@dataclass
class BiographicalEntry:
    """Represents a person's complete career from Part V"""
    name: str
    honors: List[str]
    positions: List[Dict]  # [{position, location, date, description}]
    raw_text: str

    def to_dict(self):
        return asdict(self)


@dataclass
class ColonySection:
    """Represents a colony section from Part II"""
    colony_name: str
    year: int
    start_line: int
    end_line: int
    text: str

    def to_dict(self):
        return {
            'colony_name': self.colony_name,
            'year': self.year,
            'start_line': self.start_line,
            'end_line': self.end_line,
            'text_length': len(self.text)
        }


class ColonialOfficeParserV2:
    """Improved parser using structural markers"""

    # Markers for colony sections
    SITUATION_MARKERS = [
        'Situation and Area',
        'Situation and area',  # OCR variations
        'Situation And Area',
    ]

    END_MARKERS = [
        'Foreign Consuls',
        'Foreign Consul',  # OCR variations
    ]

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

    def find_part_v_boundaries(self) -> Tuple[int, int]:
        """Find the boundaries of Part V (biographical section)"""
        start = -1
        end = len(self.lines)

        for i, line in enumerate(self.lines):
            # Look for Part V start
            if start == -1 and 'PART V' in line:
                start = i
                print(f"Found Part V at line {i}")

            # Look for end markers (Part VI or similar)
            if start != -1 and i > start + 100:
                if re.match(r'^PART (VI|6)', line):
                    end = i
                    print(f"Found Part V end at line {i}")
                    break

        if start == -1:
            print("Warning: Could not find Part V")

        return (start, end)

    def parse_biographical_entry(self, text: str) -> Optional[BiographicalEntry]:
        """
        Parse a single biographical entry from Part V
        Format: NAME, HONORS.—position, location, date; position, location, date; ...
        """
        # Match pattern: NAME[, HONORS].—rest of text
        match = re.match(r'^([A-Z][A-Z\s\'\-]+?)(?:,\s+([^.—]+?))?\.?—(.+)$', text, re.DOTALL)

        if not match:
            return None

        name = match.group(1).strip()
        honors_text = match.group(2) if match.group(2) else ""
        career_text = match.group(3).strip()

        # Extract honors
        honor_pattern = r'\b(K\.?C\.?M\.?G\.?|G\.?C\.?M\.?G\.?|C\.?M\.?G\.?|K\.?C\.?B\.?|G\.?C\.?B\.?|C\.?B\.?|Kt\.?\s*Bach|Sir|Hon\.|Right Hon\.|Rt\.\s*Rev\.|Rev\.|M\.?D\.?|LL\.?D\.?|D\.?C\.?L\.?|M\.?A\.?|B\.?A\.?)\b'
        honors = re.findall(honor_pattern, honors_text + " " + career_text[:50])
        honors = list(set(honors))  # Deduplicate

        # Parse career positions (semicolon-separated)
        positions = []
        # Split on semicolons but be careful with abbreviations
        position_texts = re.split(r';\s*', career_text)

        for pos_text in position_texts:
            if not pos_text.strip():
                continue

            # Try to extract date, location, position from each segment
            # Look for patterns like: "position, location, date" or "position, date"
            position_dict = {
                'description': pos_text.strip(),
                'position': None,
                'location': None,
                'date': None
            }

            # Extract dates (various formats: 1884, Jan. 1884, 1st May 1884, etc.)
            date_patterns = [
                r'\b(\d{1,2}(?:st|nd|rd|th)?\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?,?\s+\d{4})\b',
                r'\b((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?,?\s+\d{4})\b',
                r'\b(\d{4})\b'
            ]

            for pattern in date_patterns:
                dates = re.findall(pattern, pos_text)
                if dates:
                    position_dict['date'] = dates[0] if isinstance(dates[0], str) else dates[0][0]
                    break

            positions.append(position_dict)

        return BiographicalEntry(
            name=name,
            honors=honors,
            positions=positions,
            raw_text=text
        )

    def parse_part_v(self) -> List[BiographicalEntry]:
        """Parse all biographical entries from Part V"""
        start, end = self.find_part_v_boundaries()

        if start == -1:
            return []

        entries = []
        current_entry = []

        for i in range(start, end):
            line = self.lines[i].strip()

            # Skip headers and blank lines
            if not line or line.startswith('PART V') or 'RECORD of the Public Services' in line:
                continue

            # Check if this is the start of a new entry (ALL CAPS name followed by .— or ,)
            if re.match(r'^[A-Z][A-Z\s\'\-]+[,.]', line):
                # Save previous entry
                if current_entry:
                    entry_text = ' '.join(current_entry)
                    bio_entry = self.parse_biographical_entry(entry_text)
                    if bio_entry:
                        entries.append(bio_entry)

                # Start new entry
                current_entry = [line]
            else:
                # Continuation of current entry
                if current_entry:
                    current_entry.append(line)

        # Don't forget last entry
        if current_entry:
            entry_text = ' '.join(current_entry)
            bio_entry = self.parse_biographical_entry(entry_text)
            if bio_entry:
                entries.append(bio_entry)

        print(f"Parsed {len(entries)} biographical entries from Part V")
        return entries

    def find_colony_boundaries(self) -> List[Tuple[str, int, int]]:
        """
        Find colony boundaries using "Situation and Area" marker
        Returns: [(colony_name, start_line, end_line)]
        """
        colonies = []

        for i, line in enumerate(self.lines):
            # Check if this line contains our situation marker
            is_situation = False
            for marker in self.SITUATION_MARKERS:
                if marker in line:
                    is_situation = True
                    break

            if not is_situation:
                continue

            # Found a situation marker - look back for colony name
            colony_name = None
            for j in range(1, 5):  # Look back up to 4 lines
                if i - j < 0:
                    break
                prev_line = self.lines[i - j].strip()

                # Colony names are typically ALL CAPS with period
                if prev_line and re.match(r'^[A-Z][A-Z\s\'\-]+\.$', prev_line):
                    colony_name = prev_line.rstrip('.')
                    start_line = i - j
                    break

            if colony_name:
                colonies.append((colony_name, start_line, i))

        # Now find end boundaries (Foreign Consuls or next colony)
        colonies_with_ends = []
        for idx, (name, start, situation_line) in enumerate(colonies):
            # Find end: either Foreign Consuls or start of next colony
            end = len(self.lines)

            # Look for Foreign Consuls
            for i in range(situation_line, len(self.lines)):
                is_end = False
                for marker in self.END_MARKERS:
                    if marker in self.lines[i]:
                        is_end = True
                        break

                if is_end:
                    end = i
                    break

                # Also check if we hit the next colony
                if idx + 1 < len(colonies):
                    next_start = colonies[idx + 1][1]
                    if i >= next_start:
                        end = next_start
                        break

            colonies_with_ends.append((name, start, end))

        return colonies_with_ends

    def parse_all_colonies(self) -> List[ColonySection]:
        """Parse all colony sections"""
        boundaries = self.find_colony_boundaries()

        colonies = []
        for name, start, end in boundaries:
            section_text = '\n'.join(self.lines[start:end])

            colony = ColonySection(
                colony_name=name,
                year=self.year,
                start_line=start,
                end_line=end,
                text=section_text
            )
            colonies.append(colony)
            print(f"  {name}: {end-start} lines")

        print(f"\nFound {len(colonies)} colony sections")
        return colonies

    def export_to_json(self, colonies: List[ColonySection],
                       bio_entries: List[BiographicalEntry],
                       output_path: str):
        """Export parsed data to JSON"""
        output_data = {
            'source_file': str(self.json_path),
            'year': self.year,
            'part_ii': {
                'total_colonies': len(colonies),
                'colonies': [c.to_dict() for c in colonies]
            },
            'part_v': {
                'total_entries': len(bio_entries),
                'entries': [e.to_dict() for e in bio_entries]
            }
        }

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(output_data, f, indent=2)

        print(f"\nExported to {output_path}")
        print(f"  Part II: {len(colonies)} colonies")
        print(f"  Part V: {len(bio_entries)} biographical entries")


def main():
    parser = argparse.ArgumentParser(
        description='Parse Colonial Office List JSON files (V2 - improved structure detection)'
    )
    parser.add_argument('input_file', help='Path to Colonial Office List JSON file')
    parser.add_argument('-o', '--output', help='Output JSON file', default=None)

    args = parser.parse_args()

    if args.output is None:
        input_path = Path(args.input_file)
        args.output = input_path.parent / f"{input_path.stem}_parsed_v2.json"

    # Parse
    col_parser = ColonialOfficeParserV2(args.input_file)
    col_parser.load()

    print("\n=== Parsing Part II (Colony Sections) ===")
    colonies = col_parser.parse_all_colonies()

    print("\n=== Parsing Part V (Biographical Entries) ===")
    bio_entries = col_parser.parse_part_v()

    # Export
    col_parser.export_to_json(colonies, bio_entries, args.output)


if __name__ == '__main__':
    main()
