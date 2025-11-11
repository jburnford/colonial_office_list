#!/usr/bin/env python3
"""
Colonial Office List Parser - Modern Format (1932-1936)
Handles Dominions Office / Colonial Office merged format:
- Part II.B: Dominions (Australia, Canada, New Zealand, etc.)
- Part II.C: Crown Colonies and Protectorates
- Part III: Miscellaneous Lists
- Filters page headers
- Uses Part III as hard boundary
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
    'GAMBIA', 'THE GAMBIA', 'GIBRALTAR', 'GOLD COAST', 'GRENADA',
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
    'TASMANIA', 'TOBAGO', 'TRANSVAAL', 'TRINIDAD', "TRISTAN D'ACUNHA",
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


class ModernFormatParser:
    """Parser for modern format (1932-1936) with Dominions/Colonies split"""

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
        """Load JSON data - handles both old format (single object) and new format (array of pages)"""
        with open(self.json_path, 'r') as f:
            self.data = json.load(f)

        # Handle two different JSON formats:
        # Old format (1896): [{"text": "full document", ...}]
        # New format (other years): [{"id": "...", "text": "page 1"}, {"id": "...", "text": "page 2"}, ...]

        if isinstance(self.data, list) and len(self.data) > 0:
            # Check if it's already a list of lines (converted format)
            if isinstance(self.data[0], str):
                # Already a list of lines
                self.lines = self.data
            elif 'text' in self.data[0]:
                # Check if it's the old format (single large text) or new format (multiple pages)
                if len(self.data) == 1 and len(self.data[0]['text']) > 100000:
                    # Old format: single object with full document
                    self.text = self.data[0]['text']
                else:
                    # New format: concatenate all page texts
                    texts = []
                    for page in self.data:
                        if 'text' in page:
                            texts.append(page['text'])
                    self.text = '\n'.join(texts)
                self.lines = self.text.split('\n')
            else:
                raise ValueError("No 'text' field found in JSON data")
        else:
            raise ValueError("Unexpected JSON structure: not a list or empty")
        print(f"Loaded {len(self.lines)} lines from {self.json_path.name}")

    def is_list_format(self, line: str) -> bool:
        """
        Detect if a line is in list format (employee records, etc.)
        List formats typically have:
        - Names followed by comma and salary/amount (e.g., "John Smith, 500l.")
        - Titles/positions with abbreviations (e.g., "C.C. and R.M.")
        - Multiple entries on one line separated by semicolons
        - Division/department headers (e.g., "DIVISION OF X", "PORT OF X")
        """
        line = line.strip()
        if not line:
            return False

        # Patterns indicating list format
        list_indicators = [
            r'£\d+',  # Salary amounts with pound sign
            r'\d+l\.',  # Salary amounts like "500l."
            r'\$\d+',  # Dollar amounts
            r',\s*\d+l\.',  # Name, salary pattern
            r',\s*\d+\s*years',  # Position for X years
            r'Esq\.',  # Esquire title
            r';.*,.*\d+l\.',  # Multiple entries with salaries
            r'^[A-Z][A-Z\s\&\.]+,\s+[A-Z]',  # Position, Name pattern
            r'^DIVISION OF',  # Division headers
            r'^PORT OF',  # Port headers
            r'^DEPARTMENT OF',  # Department headers
            r'C\.C\. and R\.M\.',  # Civil Commissioner and Resident Magistrate
            r'Clerk[s]?,',  # Clerk entries
            r'Assistant',  # Assistant positions
            r'Asst\.',  # Assistant abbreviation
            r'allce\.',  # Allowance
            r'and qrs\.',  # and quarters
            r'Constituency\.',  # Constituency tables
            r'Constituencies\.',  # Constituencies tables
            r'Members\.',  # Member lists
            r'\.\s+\.\s+\.',  # Dot leaders pattern (e.g., "Somerset East . . . George Palmer")
            r'^[A-Z][a-z]+\s+[A-Z]',  # Name, Initial pattern (e.g., "Buddo, D.")
            r',\s+[A-Z]\.$',  # Comma followed by initial (e.g., ", D.")
            r'[*†]',  # Footnote markers often in lists
            r'salary|allowance',  # Salary/allowance references (case-insensitive handled below)
        ]

        for pattern in list_indicators:
            if re.search(pattern, line):
                return True

        return False

    def is_paragraph_format(self, line: str) -> bool:
        """
        Detect if a line is paragraph/descriptive text
        Paragraphs typically:
        - Are longer sentences
        - Don't have salary amounts
        - Form coherent prose
        """
        line = line.strip()
        if not line or len(line) < 40:
            return False

        # Not a list if it's long and doesn't have list indicators
        if not self.is_list_format(line):
            # Contains typical paragraph words
            paragraph_words = ['the', 'and', 'which', 'was', 'were', 'is', 'are', 'by', 'of', 'in']
            word_count = sum(1 for word in paragraph_words if word in line.lower())
            if word_count >= 3:
                return True

        return False

    def is_page_header(self, line_num: int, colony_name: str) -> bool:
        """
        Determine if this colony name occurrence is a page header
        Page headers appear in the middle of lists, surrounded by list-format lines
        """
        # Check lines before and after
        context_range = 5

        list_lines_before = 0
        list_lines_after = 0

        # Check lines before
        for i in range(max(0, line_num - context_range), line_num):
            if self.is_list_format(self.lines[i]):
                list_lines_before += 1

        # Check lines after
        for i in range(line_num + 1, min(len(self.lines), line_num + 1 + context_range)):
            if self.is_list_format(self.lines[i]):
                list_lines_after += 1

        # If surrounded by list format, it's likely a page header
        # Strong evidence: lists on both sides
        if list_lines_before >= 2 and list_lines_after >= 2:
            return True

        # Moderate evidence: at least one list before and multiple after
        if list_lines_before >= 1 and list_lines_after >= 3:
            return True

        return False

    def get_section_preview(self, start_line: int, num_lines: int = 20) -> str:
        """Get a preview of lines following a colony header for duplicate detection"""
        preview_lines = []
        for i in range(start_line + 1, min(start_line + 1 + num_lines, len(self.lines))):
            # Normalize text for comparison (remove extra spaces, lowercase)
            line = ' '.join(self.lines[i].split()).lower()
            if line:  # Only include non-empty lines
                preview_lines.append(line)
        return ' '.join(preview_lines[:10])  # First 10 non-empty lines

    def is_duplicate_section(self, colony_name: str, line_num: int, seen_colonies: Dict[str, List[Tuple[int, str]]]) -> bool:
        """
        Check if this colony occurrence is a duplicate based on content similarity
        """
        if colony_name not in seen_colonies:
            return False

        # Get preview of this section
        this_preview = self.get_section_preview(line_num)

        # Compare with previous occurrences of same colony
        for prev_line, prev_preview in seen_colonies[colony_name]:
            # Calculate similarity (simple word overlap)
            this_words = set(this_preview.split())
            prev_words = set(prev_preview.split())

            if len(this_words) == 0 or len(prev_words) == 0:
                continue

            overlap = len(this_words & prev_words)
            total = len(this_words | prev_words)
            similarity = overlap / total if total > 0 else 0

            # If >70% similar, it's likely a duplicate
            if similarity > 0.7:
                return True

        return False

    def find_all_colony_headers(self) -> List[Tuple[str, int]]:
        """
        Find all colony headers, filtering out page headers and duplicate sections
        Returns: [(colony_name, line_number)]
        """
        found = []
        seen_colonies = {}  # colony_name -> [(line_num, preview)]

        for i, line in enumerate(self.lines):
            line_stripped = line.strip().rstrip('.')

            # Check if this line matches a known colony
            if line_stripped in KNOWN_COLONIES:
                # Check if it's a page header (in middle of lists)
                if self.is_page_header(i, line_stripped):
                    print(f"  Skipping page header: {line_stripped:35s} at line {i}")
                    continue

                # Check if it's a duplicate section (same content as previous)
                if self.is_duplicate_section(line_stripped, i, seen_colonies):
                    print(f"  Skipping duplicate section: {line_stripped:35s} at line {i}")
                    continue

                # Record this occurrence
                preview = self.get_section_preview(i)
                if line_stripped not in seen_colonies:
                    seen_colonies[line_stripped] = []
                seen_colonies[line_stripped].append((i, preview))

                found.append((line_stripped, i))
                print(f"  Found colony: {line_stripped:35s} at line {i}")

        print(f"\nFound {len(found)} colony headers (after filtering)")
        return found

    def find_part_iii_boundary(self) -> Optional[int]:
        """
        Find where Part III begins (end of Part II.C)

        Strategy:
        - Find Part II.C content start (Crown Colonies section, not Dominions)
        - Look for PART III marker after Part II.C content
        - Verify it's followed by substantial content (not just a reference)
        """
        # First, find where Part II.C actual content starts (Crown Colonies)
        part_ii_c_content_start = 0
        for i in range(1000, min(30000, len(self.lines))):
            line = self.lines[i].strip()
            # Look for Part II.C content markers (Crown Colonies section)
            # Format: "PART II.—C. HISTORICAL AND STATISTICAL ACCOUNT"
            if (('PART II' in line and ('.C.' in line or '.—C.' in line or '—C' in line)) or
                ('PART II' in line and 'COLONIES' in line and 'TERRITORIES' in line)):
                part_ii_c_content_start = i
                print(f"Part II.C content starts at line {i}")
                break

        # If we didn't find Part II.C marker, look for regular Part II marker
        # (fallback for standard format)
        if part_ii_c_content_start == 0:
            for i in range(1000, min(10000, len(self.lines))):
                line = self.lines[i].strip()
                if ('PART II' in line and ('INTRODUCTION' in line or 'HISTORICAL' in line)):
                    part_ii_c_content_start = i
                    print(f"Part II content starts at line {i} (standard format)")
                    break

        # If we didn't find Part II content marker, assume TOC ends around line 2500
        search_start = max(2500, part_ii_c_content_start)

        for i in range(search_start, len(self.lines)):
            line = self.lines[i].strip()

            # Match Part III in various formats
            # Look for Part III as section header (with period, colon, or alone)
            if re.match(r'^PART (III|3)[\.:—\s]', line) or line == 'PART III' or line == 'PART 3':
                # Skip if this looks like a table of contents entry
                # (TOC entries typically have page numbers or "..." leaders)
                if '...' in line or re.search(r'\d{2,}$', line):
                    print(f"Skipping Part III TOC entry at line {i}")
                    continue

                # Verify this is actual content, not a reference
                # Check that it's followed by substantial text (section headers, content)
                has_content = False
                for j in range(i + 1, min(i + 50, len(self.lines))):
                    check_line = self.lines[j].strip()
                    # Look for section headers or substantial content
                    if len(check_line) > 30 or (check_line and check_line[0].isdigit()):
                        has_content = True
                        break

                if has_content:
                    print(f"Found Part III at line {i}")
                    return i
                else:
                    print(f"Skipping Part III reference at line {i} (no content follows)")

        print("Part III not found (will use end of document as boundary)")
        return None

    def find_colony_end(self, start_line: int, next_colony_start: Optional[int], part_iii_line: Optional[int]) -> int:
        """
        Find where a colony section ends

        Strategy:
        1. Look for Foreign Consuls marker
        2. After Foreign Consuls, continue until we see paragraph format (next colony start)
        3. If no Foreign Consuls, look for format change from list to paragraph
        4. Hard boundary: next colony start or Part III
        """
        # Determine search boundary
        search_end = len(self.lines)
        if next_colony_start:
            search_end = next_colony_start
        if part_iii_line and part_iii_line < search_end:
            search_end = part_iii_line

        # Look for Foreign Consuls marker
        foreign_consuls_line = None
        for i in range(start_line, search_end):
            if re.match(r'^Foreign Consuls?\.?$', self.lines[i].strip()):
                foreign_consuls_line = i
                break

        if foreign_consuls_line:
            # After Foreign Consuls, look for end of lists (military/naval officers, etc.)
            # Colony ends when we see paragraph format again (next colony)
            for i in range(foreign_consuls_line + 10, search_end):
                # Check if we're seeing paragraph text (next colony starting)
                if self.is_paragraph_format(self.lines[i]):
                    # Look back a bit to find where lists ended
                    for j in range(i - 1, foreign_consuls_line, -1):
                        if self.is_list_format(self.lines[j]) or not self.lines[j].strip():
                            continue
                        else:
                            # Found transition point
                            return j + 1
                    return i

            # If no paragraph found, end at search boundary
            return search_end

        # No Foreign Consuls found - look for next section or Part III
        return search_end

    def parse_all_colonies(self) -> List[ColonySection]:
        """
        Parse all colonies

        For modern format (1932-1936):
        - Only include colonies from Part II.C (Crown Colonies)
        - Skip colonies from Part II.B (Dominions)
        """
        headers = self.find_all_colony_headers()
        part_iii_line = self.find_part_iii_boundary()

        # Find Part II.C start to filter out Dominions (Part II.B)
        part_ii_c_start = 0
        for i in range(1000, min(30000, len(self.lines))):
            line = self.lines[i].strip()
            if (('PART II' in line and ('.C.' in line or '.—C.' in line or '—C' in line)) or
                ('PART II' in line and 'COLONIES' in line and 'TERRITORIES' in line)):
                part_ii_c_start = i
                print(f"Filtering: Only including colonies after Part II.C at line {i}")
                break

        # Filter headers to only include those in Part II.C (after part_ii_c_start, before part_iii_line)
        if part_ii_c_start > 0 and part_iii_line:
            filtered_headers = [(name, start) for name, start in headers
                              if start >= part_ii_c_start and start < part_iii_line]
            print(f"Filtered: {len(headers)} -> {len(filtered_headers)} colonies (removed Dominions from Part II.B and appendix entries after Part III)")
            headers = filtered_headers
        elif part_ii_c_start > 0:
            filtered_headers = [(name, start) for name, start in headers if start >= part_ii_c_start]
            print(f"Filtered: {len(headers)} -> {len(filtered_headers)} colonies (removed Dominions from Part II.B)")
            headers = filtered_headers
        elif part_iii_line:
            filtered_headers = [(name, start) for name, start in headers if start < part_iii_line]
            print(f"Filtered: {len(headers)} -> {len(filtered_headers)} colonies (removed appendix entries after Part III)")
            headers = filtered_headers

        colonies = []

        for idx, (name, start) in enumerate(headers):
            # Determine end
            next_start = headers[idx + 1][1] if idx + 1 < len(headers) else None
            end = self.find_colony_end(start, next_start, part_iii_line)

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
        description='Parse Colonial Office List - Modern Format (1932-1936) with Dominions/Colonies split'
    )
    parser.add_argument('input_file', help='Path to Colonial Office List JSON file')
    parser.add_argument('-o', '--output', help='Output JSON file', default=None)
    parser.add_argument('--export-text', help='Export each colony as separate text file', action='store_true')

    args = parser.parse_args()

    if args.output is None:
        input_path = Path(args.input_file)
        args.output = input_path.parent.parent / "output" / f"{input_path.stem}_parsed_modern.json"

    # Parse
    col_parser = ModernFormatParser(args.input_file)
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
