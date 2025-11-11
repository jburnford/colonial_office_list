#!/usr/bin/env python3
"""
Colonial Office List Parser - Early Grouped Format (1877-1883)
Handles grouped colonies with cross-references
Example: "BARBADOS. (See Windward Islands, p. 161.)"
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict
import argparse


# Known colony names for 1877-1883 era
KNOWN_COLONIES_1877 = {
    'ADEN', 'ANTIGUA', 'ASCENSION', 'AUSTRALIA',
    'BAHAMAS', 'BARBADOS', 'BASUTOLAND', 'BECHUANALAND', 'BERMUDA',
    'BRITISH COLUMBIA', 'BRITISH GUIANA', 'BRITISH HONDURAS',
    'CANADA', 'CAPE OF GOOD HOPE', 'CAYMAN ISLANDS', 'CEYLON', 'CYPRUS',
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
    'SEYCHELLES', 'SIERRA LEONE', 'SOUTH AUSTRALIA', 'STRAITS SETTLEMENTS',
    'TASMANIA', 'TOBAGO', 'TRANSVAAL', 'TRINIDAD',
    'TURKS ISLANDS',
    'VANCOUVER ISLAND', 'VICTORIA', 'VIRGIN ISLANDS',
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
    grouped: bool = False  # True if found via group reference
    group_name: Optional[str] = None  # Parent group if grouped

    def to_dict(self):
        return asdict(self)


class EarlyGroupedParser:
    """Parser for early grouped format with cross-references (1877-1883)"""

    def __init__(self, json_path: str):
        self.json_path = Path(json_path)
        self.data = None
        self.text = None
        self.lines = []
        self.year = self._extract_year_from_filename()

        # Cross-reference mapping: colony_name -> (target_group, page_number, line_num)
        self.cross_refs: Dict[str, Tuple[str, str, int]] = {}

        # Group headers: group_name -> line_num
        self.group_headers: Dict[str, int] = {}

    def _extract_year_from_filename(self) -> int:
        match = re.search(r'(\d{4})', str(self.json_path))
        return int(match.group(1)) if match else 0

    def load(self):
        """Load JSON data"""
        with open(self.json_path, 'r') as f:
            self.data = json.load(f)

        # Handle JSON format
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

    def find_cross_references(self):
        """Find all cross-references and build mapping"""
        print("\n=== Finding Cross-References ===")

        for i, line in enumerate(self.lines):
            # Look for pattern: (See GroupName, p. XXX.) - note the period before closing paren
            match = re.search(r'\(See ([^,]+), p\. (\d+)\.\)', line)
            if not match:
                # Try without the period (some years may vary)
                match = re.search(r'\(See ([^,]+), p\. (\d+)\)', line)

            if match:
                target_group = match.group(1).strip()
                page_num = match.group(2)

                # Find the colony name (should be on previous non-empty line)
                colony_name = None
                for j in range(i-1, max(0, i-10), -1):
                    stripped = self.lines[j].strip().rstrip('.')
                    if stripped and stripped in KNOWN_COLONIES_1877:
                        colony_name = stripped
                        break

                if colony_name:
                    self.cross_refs[colony_name] = (target_group, page_num, i)
                    print(f"  {colony_name:30s} -> {target_group} (p. {page_num})")

        print(f"Found {len(self.cross_refs)} cross-references")

    def find_group_headers(self):
        """Find all group section headers"""
        print("\n=== Finding Group Headers ===")

        for i, line in enumerate(self.lines):
            stripped = line.strip().rstrip('.')

            # Look for group patterns
            is_group = False
            if (re.match(r'^THE [A-Z\s]+ISLANDS?$', stripped) or
                re.match(r'^DOMINION OF [A-Z\s]+$', stripped) or
                re.match(r'^[A-Z\s]+ SETTLEMENTS?$', stripped)):
                is_group = True

            if is_group:
                # Verify it's followed by colony content (not just a reference)
                has_content = False
                for j in range(i+1, min(i+30, len(self.lines))):
                    if len(self.lines[j].strip()) > 50:
                        has_content = True
                        break

                if has_content:
                    self.group_headers[stripped] = i
                    print(f"  Line {i:,}: {stripped}")

        print(f"Found {len(self.group_headers)} group headers")

    def find_colonies_in_group(self, group_name: str, group_start: int) -> List[ColonySection]:
        """Extract individual colonies from within a group section"""
        colonies = []

        # Determine where this group ends (next group or reasonable distance)
        group_end = len(self.lines)
        for other_group, other_start in self.group_headers.items():
            if other_start > group_start and other_start < group_end:
                group_end = other_start

        # Limit search to reasonable distance
        search_end = min(group_start + 5000, group_end)

        # Find colonies within this group
        found_in_group = []
        for i in range(group_start + 1, search_end):
            line = self.lines[i].strip().rstrip('.')

            if line in KNOWN_COLONIES_1877:
                # Check if it's a real section start
                has_content = False
                for j in range(i+1, min(i+20, search_end)):
                    content = self.lines[j].strip()
                    if len(content) > 40:
                        has_content = True
                        break

                if has_content:
                    found_in_group.append((line, i))

        # Create sections for each colony found
        for idx, (colony_name, start_line) in enumerate(found_in_group):
            # Determine end (next colony in group or group end)
            end_line = found_in_group[idx + 1][1] if idx + 1 < len(found_in_group) else search_end

            # Calculate character count
            start_char = sum(len(self.lines[j]) + 1 for j in range(start_line))
            end_char = sum(len(self.lines[j]) + 1 for j in range(end_line))

            colony = ColonySection(
                colony_name=colony_name,
                year=self.year,
                start_line=start_line,
                end_line=end_line,
                char_count=end_char - start_char,
                grouped=True,
                group_name=group_name
            )
            colonies.append(colony)

        return colonies

    def find_direct_colonies(self) -> List[ColonySection]:
        """Find colonies that don't have cross-references (direct format)"""
        colonies = []
        found = []

        # Get colonies that have cross-references
        grouped_colonies = set(self.cross_refs.keys())

        # Build set of line ranges that are within groups (to exclude them)
        group_ranges = []
        for group_name, group_start in self.group_headers.items():
            # Determine where this group ends
            group_end = len(self.lines)
            for other_name, other_start in self.group_headers.items():
                if other_start > group_start and other_start < group_end:
                    group_end = other_start
            # Limit to reasonable distance
            group_end = min(group_start + 5000, group_end)
            group_ranges.append((group_start, group_end))

        for i, line in enumerate(self.lines):
            line_stripped = line.strip().rstrip('.')

            if line_stripped in KNOWN_COLONIES_1877:
                # Skip if this line is within a group section
                in_group = False
                for group_start, group_end in group_ranges:
                    if group_start <= i < group_end:
                        in_group = True
                        break
                if in_group:
                    continue

                # Skip if this colony has a cross-reference
                if line_stripped in grouped_colonies:
                    continue

                # Check if it's a real section start
                has_content = False
                for j in range(i+1, min(i+20, len(self.lines))):
                    content = self.lines[j].strip()
                    if (content.startswith('Is situated') or
                        content.startswith('The ') or
                        'latitude' in content.lower() or
                        len(content) > 50):
                        has_content = True
                        break

                if has_content:
                    # Check if not a duplicate (within 500 lines of previous)
                    is_duplicate = False
                    for prev_name, prev_line in found:
                        if prev_name == line_stripped and (i - prev_line) < 500:
                            is_duplicate = True
                            break

                    if not is_duplicate:
                        found.append((line_stripped, i))

        # Create sections
        for idx, (name, start) in enumerate(found):
            # Determine end
            next_start = found[idx + 1][1] if idx + 1 < len(found) else len(self.lines)
            end = next_start

            # Calculate character count
            start_char = sum(len(self.lines[j]) + 1 for j in range(start))
            end_char = sum(len(self.lines[j]) + 1 for j in range(end))

            colony = ColonySection(
                colony_name=name,
                year=self.year,
                start_line=start,
                end_line=end,
                char_count=end_char - start_char,
                grouped=False
            )
            colonies.append(colony)

        return colonies

    def parse_all_colonies(self) -> List[ColonySection]:
        """Parse all colonies"""
        # Step 1: Find cross-references
        self.find_cross_references()

        # Step 2: Find group headers
        self.find_group_headers()

        # Step 3: Extract colonies from groups
        print("\n=== Extracting Colonies from Groups ===")
        grouped_colonies = []
        for group_name, group_start in self.group_headers.items():
            print(f"\nProcessing group: {group_name}")
            colonies_in_group = self.find_colonies_in_group(group_name, group_start)
            for colony in colonies_in_group:
                print(f"  Found: {colony.colony_name:30s} lines {colony.start_line:,}-{colony.end_line:,}")
            grouped_colonies.extend(colonies_in_group)

        # Step 4: Find direct colonies (not in groups)
        print("\n=== Finding Direct Colonies ===")
        direct_colonies = self.find_direct_colonies()
        for colony in direct_colonies:
            print(f"  Found: {colony.colony_name:30s} lines {colony.start_line:,}-{colony.end_line:,}")

        # Combine and sort by start line
        all_colonies = grouped_colonies + direct_colonies
        all_colonies.sort(key=lambda c: c.start_line)

        print(f"\n=== Total: {len(all_colonies)} colonies ===")
        print(f"  Grouped: {len(grouped_colonies)}")
        print(f"  Direct: {len(direct_colonies)}")

        return all_colonies

    def export_to_json(self, colonies: List[ColonySection], output_path: str):
        """Export parsed data"""
        output_data = {
            'source_file': str(self.json_path),
            'year': self.year,
            'format': 'early_grouped',
            'total_colonies': len(colonies),
            'grouped_count': sum(1 for c in colonies if c.grouped),
            'direct_count': sum(1 for c in colonies if not c.grouped),
            'cross_references': {name: {'group': group, 'page': page}
                                for name, (group, page, _) in self.cross_refs.items()},
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

            suffix = f"_[{colony.group_name}]" if colony.grouped else ""
            filename = f"{self.year}_{colony.colony_name.replace(' ', '_')}{suffix}.txt"
            filepath = output_dir / filename

            with open(filepath, 'w') as f:
                f.write(colony_text)

        print(f"Exported {len(colonies)} colony text files to {output_dir}")


def main():
    parser = argparse.ArgumentParser(
        description='Parse Colonial Office List - Early Grouped Format (1877-1883)'
    )
    parser.add_argument('input_file', help='Path to Colonial Office List JSON file')
    parser.add_argument('-o', '--output', help='Output JSON file', default=None)
    parser.add_argument('--export-text', help='Export each colony as separate text file', action='store_true')

    args = parser.parse_args()

    if args.output is None:
        input_path = Path(args.input_file)
        year_match = re.search(r'(\d{4})', str(input_path))
        year = year_match.group(1) if year_match else 'unknown'
        args.output = Path("output") / f"{year}_parsed_early_grouped.json"

    # Parse
    col_parser = EarlyGroupedParser(args.input_file)
    col_parser.load()

    colonies = col_parser.parse_all_colonies()

    # Show summary
    print("\n=== Colony Summary ===")
    for c in colonies:
        group_str = f" [{c.group_name}]" if c.grouped else " [direct]"
        print(f"{c.colony_name:35s} lines {c.start_line:5d}-{c.end_line:5d} ({c.end_line-c.start_line:4d} lines){group_str}")

    # Export
    col_parser.export_to_json(colonies, args.output)

    if args.export_text:
        text_dir = Path(args.output).parent / f"{Path(args.output).stem}_texts"
        col_parser.export_full_text(colonies, text_dir)


if __name__ == '__main__':
    main()
