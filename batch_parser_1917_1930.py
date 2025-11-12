#!/usr/bin/env python3
"""
Colonial Office List Batch Parser for 1917-1930
Post-WWI era including League of Nations mandates
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict

# Expanded colony names for 1917-1930 (includes post-WWI mandates and changes)
KNOWN_COLONIES = {
    # Pre-existing colonies
    'ADEN', 'ANTIGUA', 'ASCENSION', 'AUSTRALIA',
    'BAHAMAS', 'BARBADOS', 'BASUTOLAND', 'BECHUANALAND', 'BERMUDA',
    'BRITISH BECHUANALAND', 'BRITISH CENTRAL AFRICA', 'BRITISH COLUMBIA',
    'BRITISH EAST AFRICA', 'BRITISH GUIANA', 'BRITISH HONDURAS',
    'BRITISH NEW GUINEA', 'BRITISH NORTH BORNEO',
    'CANADA', 'CAPE OF GOOD HOPE', 'CAYMAN ISLANDS', 'CEYLON', 'CYPRUS',
    'DOMINICA', 'EAST AFRICA', 'FALKLAND ISLANDS', 'FIJI',
    'GAMBIA', 'THE GAMBIA', 'GIBRALTAR', 'GOLD COAST', 'GRENADA',
    'HONG KONG', 'JAMAICA', 'KENYA', 'LABUAN', 'LAGOS', 'LEEWARD ISLANDS',
    'MALTA', 'MAURITIUS', 'MONTSERRAT',
    'NATAL', 'NEVIS', 'NEWFOUNDLAND', 'NIGER COAST PROTECTORATE', 'NIGERIA', 'NORTH BORNEO',
    'NORTHERN RHODESIA', 'NYASALAND',
    'PALESTINE', 'QUEENSLAND', 'RHODESIA',
    'ST. CHRISTOPHER', 'ST. HELENA', 'ST. KITTS', 'ST. LUCIA', 'ST. VINCENT',
    'SEYCHELLES', 'SIERRA LEONE', 'SOMALILAND', 'SOUTHERN RHODESIA', 'STRAITS SETTLEMENTS',
    'SWAZILAND', 'TANGANYIKA', 'TASMANIA', 'TOBAGO', 'TRANSVAAL', 'TRINIDAD',
    "TRISTAN D'ACUNHA", 'TURKS AND CAICOS ISLANDS', 'TURKS ISLANDS',
    'UGANDA', 'VICTORIA', 'WEIHAIWEI', 'WESTERN AUSTRALIA', 'WINDWARD ISLANDS',
    'ZANZIBAR', 'ZULULAND',
    # Post-WWI additions (League of Nations mandates)
    'CAMEROONS', 'TOGOLAND', 'TANGANYIKA TERRITORY',
    'SOUTH WEST AFRICA', 'IRAQ', 'TRANSJORDAN',
    # Administrative reorganizations
    'EAST AFRICA PROTECTORATE', 'KENYA COLONY', 'KENYA AND UGANDA',
}

# Subsections to aggressively filter (NOT colonies)
SUBSECTION_PATTERNS = {
    'EXPORTS', 'IMPORTS', 'RAILWAYS', 'RAILWAY', 'SHIPPING',
    'THE PARLIAMENT', 'PARLIAMENT', 'EXECUTIVE COUNCIL', 'LEGISLATIVE COUNCIL',
    'JUDICIARY', 'FINANCE', 'EDUCATION', 'PUBLIC WORKS',
    'AGRICULTURE', 'MEDICAL', 'POSTAL', 'TELEGRAPH',
    'CUSTOMS', 'HARBOURS', 'POLICE', 'PRISONS',
    'ADMINISTRATION', 'GOVERNMENT', 'CLIMATE', 'GEOGRAPHY',
    'POPULATION', 'TRADE', 'REVENUE', 'EXPENDITURE',
    'CURRENCY', 'WEIGHTS AND MEASURES', 'LEGISLATION',
}


@dataclass
class ColonySection:
    """Represents a colony section"""
    colony_name: str
    year: int
    start_line: int
    end_line: int
    char_count: int
    line_count: int
    filename: str

    def to_dict(self):
        return asdict(self)


class ColonialOfficeParser1917_1930:
    """Parser for 1917-1930 Colonial Office Lists from markdown"""

    def __init__(self, year: int, base_path: str = '/home/user/colonial_office_list'):
        self.year = year
        self.base_path = Path(base_path)
        self.input_path = self.base_path / 'historical_document_pipeline' / 'processed_pdfs' / f'colonial-office-list-{year}' / 'olmocr_results.md'
        self.output_dir = self.base_path / 'output' / f'{year}_manual_parsed'
        self.output_json = self.base_path / 'output' / f'{year}_manual_parsed.json'
        self.text = None
        self.lines = []

    def load(self):
        """Load markdown file"""
        with open(self.input_path, 'r', encoding='utf-8') as f:
            self.text = f.read()
        self.lines = self.text.split('\n')
        print(f"Loaded {len(self.lines)} lines from {self.year}")

    def is_subsection_header(self, line: str) -> bool:
        """Check if this is a subsection header (not a colony)"""
        line_clean = line.strip().rstrip('.')
        return line_clean in SUBSECTION_PATTERNS

    def is_page_header(self, line_num: int) -> bool:
        """Check if this appears to be a page header (repeated colony name)"""
        # Simple heuristic: check if surrounded by list-format text
        if line_num < 5 or line_num > len(self.lines) - 5:
            return False

        # Check if nearby lines have employee-list patterns
        context = 3
        list_indicators = 0
        for i in range(max(0, line_num - context), min(len(self.lines), line_num + context + 1)):
            if i == line_num:
                continue
            if re.search(r'£\d+|\d+l\.|Esq\.|C\.M\.G\.|K\.C\.M\.G\.', self.lines[i]):
                list_indicators += 1

        # If surrounded by list text, it's likely a page header
        return list_indicators >= 3

    def find_all_colony_headers(self) -> List[Tuple[str, int]]:
        """Find all colony headers in the document"""
        found = []
        seen_colonies = {}  # Track first occurrence of each colony

        # Find where Part II begins (colony section)
        part_ii_start = 0
        for i, line in enumerate(self.lines):
            if re.match(r'^PART (II|2)[\.:—\s]', line.strip()):
                part_ii_start = i
                print(f"Part II starts at line {i}")
                break

        # Find where Part III begins (end of colonies)
        part_iii_start = len(self.lines)
        for i in range(part_ii_start + 1000, len(self.lines)):
            line = self.lines[i].strip()
            if re.match(r'^PART (III|3)[\.:—\s]', line) or line == 'PART III':
                # Check not a TOC entry
                if '...' not in line and not re.search(r'\d{2,}$', line):
                    part_iii_start = i
                    print(f"Part III starts at line {i}")
                    break

        print(f"Searching for colonies between lines {part_ii_start} and {part_iii_start}")

        # Search for colony headers
        for i in range(part_ii_start, part_iii_start):
            line = self.lines[i].strip().rstrip('.')

            # Check if it matches a known colony
            if line in KNOWN_COLONIES:
                # Filter subsections
                if self.is_subsection_header(line):
                    print(f"  Filtered subsection: {line:40s} at line {i}")
                    continue

                # Filter page headers (duplicates)
                if self.is_page_header(i):
                    print(f"  Filtered page header: {line:40s} at line {i}")
                    continue

                # Check if we've already seen this colony
                if line in seen_colonies:
                    # This is likely a duplicate/page header
                    print(f"  Filtered duplicate: {line:40s} at line {i} (first at {seen_colonies[line]})")
                    continue

                # Record this colony
                seen_colonies[line] = i
                found.append((line, i))
                print(f"  Found colony: {line:40s} at line {i}")

        print(f"\nFound {len(found)} unique colonies")
        return found

    def find_colony_end(self, start_line: int, next_start: Optional[int]) -> int:
        """Find where a colony section ends"""
        # Default: use next colony start or end of document
        search_end = next_start if next_start else len(self.lines)

        # Look for natural breaks
        # 1. Next colony header
        # 2. Significant whitespace
        # 3. Format change

        return search_end

    def parse_all_colonies(self) -> List[ColonySection]:
        """Parse all colonies"""
        headers = self.find_all_colony_headers()
        colonies = []

        for idx, (name, start) in enumerate(headers):
            # Find end of this colony section
            next_start = headers[idx + 1][1] if idx + 1 < len(headers) else None
            end = self.find_colony_end(start, next_start)

            # Extract text
            colony_text = '\n'.join(self.lines[start:end])
            char_count = len(colony_text)
            line_count = end - start

            # Create filename
            filename = f"{name.replace(' ', '_')}.md"

            colony = ColonySection(
                colony_name=name,
                year=self.year,
                start_line=start,
                end_line=end,
                char_count=char_count,
                line_count=line_count,
                filename=filename
            )

            colonies.append(colony)

        print(f"\nTotal: {len(colonies)} colonies parsed")
        return colonies

    def export_colonies(self, colonies: List[ColonySection]):
        """Export colony texts and metadata"""
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # Export individual colony files
        for colony in colonies:
            colony_text = '\n'.join(self.lines[colony.start_line:colony.end_line])
            filepath = self.output_dir / colony.filename
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(colony_text)

        print(f"Exported {len(colonies)} colony files to {self.output_dir}")

        # Export JSON metadata
        output_data = {
            'year': self.year,
            'source_file': str(self.input_path),
            'total_colonies': len(colonies),
            'colonies': [c.to_dict() for c in colonies],
            'processing_notes': {
                'parser': 'Batch parser for 1917-1930 (Post-WWI era)',
                'date': '2025-11-12',
                'method': 'Pattern-based colony detection with aggressive subsection filtering',
            }
        }

        with open(self.output_json, 'w', encoding='utf-8') as f:
            json.dump(output_data, f, indent=2)

        print(f"Exported metadata to {self.output_json}")


def process_year(year: int):
    """Process a single year"""
    print(f"\n{'='*70}")
    print(f"Processing {year}")
    print('='*70)

    parser = ColonialOfficeParser1917_1930(year)
    parser.load()
    colonies = parser.parse_all_colonies()

    # Show summary
    print("\n=== Colony Summary ===")
    for c in colonies:
        print(f"{c.colony_name:40s} lines {c.start_line:5d}-{c.end_line:5d} ({c.line_count:4d} lines)")

    parser.export_colonies(colonies)

    return len(colonies)


def main():
    """Process all years 1917-1930"""
    years = [1917, 1918, 1919, 1920, 1921, 1922, 1923, 1924, 1925, 1927, 1928, 1929, 1930]

    results = {}
    for year in years:
        try:
            count = process_year(year)
            results[year] = {'status': 'success', 'colonies': count}
        except Exception as e:
            print(f"\nERROR processing {year}: {e}")
            results[year] = {'status': 'error', 'message': str(e)}

    # Print summary
    print(f"\n{'='*70}")
    print("BATCH PROCESSING SUMMARY")
    print('='*70)
    for year, result in results.items():
        if result['status'] == 'success':
            print(f"{year}: ✓ {result['colonies']} colonies")
        else:
            print(f"{year}: ✗ ERROR - {result['message']}")


if __name__ == '__main__':
    main()
