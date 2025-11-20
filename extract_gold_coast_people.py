#!/usr/bin/env python3
"""
Extract people data from Gold Coast Colonial Office List files.
Handles unique Gold Coast format including markdown tables.

Gold Coast specifics:
- Markdown table format: |Rank|Name|Salary|Allowances|Remarks|
- Currency: £ sterling (l. notation)
- Geographic organization: Settlement-based (Accra, Cape Coast, Elmina, Lagos, etc.)
- Allowances column: "Free quarters", "+House", "+Horse", "+Hammock"
- Lagos section: Separate administration within colony
"""

import re
import json
import os
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict


@dataclass
class Person:
    """Data structure for a person extracted from Colonial Office List."""
    name: str
    role: str
    location: str  # Colony + department/province if applicable
    colony: str
    year: int
    department: Optional[str] = None
    province: Optional[str] = None
    salary: Optional[str] = None
    allowances: Optional[str] = None
    remarks: Optional[str] = None
    full_string: str = ""
    source_file: str = ""
    line_number: int = 0
    confidence: float = 0.0
    extraction_method: str = "unknown"  # 'table', 'narrative', 'hybrid'
    notes: str = ""
    # Fiji-specific attributes (for compatibility)
    is_acting: bool = False
    multi_role_id: Optional[str] = None

    def to_dict(self):
        return asdict(self)


class GoldCoastPatternExtractor:
    """Extract people data from Gold Coast Colonial Office List files."""

    def __init__(self, github_base_url: str = "https://github.com/jburnford/colonial_office_list/blob/main"):
        self.github_base_url = github_base_url
        self.current_department = None
        self.current_province = None
        self.current_settlement = None
        self.last_role = None
        self.last_allowances = None

        # Gold Coast settlement names (should NOT be extracted as people)
        self.settlement_names = {
            'Accra', 'Cape Coast', 'Elmina', 'Lagos', 'Dixcove', 'Axim',
            'Quittah', 'Winnebah', 'Saltpond', 'Anamaboe', 'Addah', 'Addafia',
            'Prampram', 'Appam', 'Mumford', 'Chamah', 'Secondee', 'Adjuah',
            'Apolonia', 'Half Assinee', 'New Town', 'Jellah Coffee', 'Attokoo',
            'Comendah', 'Wassaw', 'Krepi', 'Kwahu', 'Volta River', 'Pram', 'Ada',
            'Kwitta', 'Badagry', 'Palma', 'Leckie'
        }

        # Location names (not person names)
        self.location_names = self.settlement_names.union({
            'Gold Coast', 'THE GOLD COAST', 'GOLD COAST COLONY',
            'THE GOLD COAST COLONY', 'LAGOS', 'The Gold Coast Proper',
            'Western Province', 'Central Province', 'Eastern Province'
        })

        # Known false positives
        self.skip_terms = {
            'Ditto', 'ditto', 'vacant', 'Vacant', 'acting', 'Acting',
            'Grade I', 'Grade II', 'Grade III', 'Total', 'Male', 'Female',
            'Privates', 'Officers', 'Native Officers', 'The Governor',
            'The Colonial Secretary', 'The Queen\'s Advocate',
            'The Collector and Treasurer', 'The Officer Commanding Troops',
            'The Chief Justice', 'The Administrator of Lagos',
            '—', '–', '...'
        }

        # Common section headers that indicate start of people data
        self.people_section_headers = [
            r"^Civil Establishment",
            r"^CIVIL ESTABLISHMENT",
            r"^Executive Council",
            r"^Legislative Council",
            r"STATEMENT of the Establishment",
        ]

        # Department/section headers
        self.department_headers = [
            r"Colonial Secretary'?s? Office",
            r"Governor'?s? Office",
            r"Treasury",
            r"Customs and Treasury",
            r"Customs",
            r"Audit Office",
            r"Post Office",
            r"Printing Office",
            r"Judicial Department",
            r"Queen'?s? Advocate",
            r"Ecclesiastical Department",
            r"Educational",
            r"District Commissioners?",
            r"Constabulary",
            r"Medical Department",
            r"Public Works",
            r"Telegraph Department",
        ]

    def find_people_section_start(self, lines: List[str]) -> int:
        """Find where the people data starts in the file."""
        for i, line in enumerate(lines):
            for pattern in self.people_section_headers:
                if re.search(pattern, line.strip(), re.IGNORECASE):
                    return i
        # Fallback: look for first table with rank/name columns
        for i, line in enumerate(lines):
            if '|' in line and re.search(r'Rank.*Name', line, re.IGNORECASE):
                return i - 1 if i > 0 else i
        return -1

    def is_department_header(self, line: str) -> Optional[str]:
        """Check if line is a department header and return department name."""
        line_stripped = line.strip().rstrip('.')
        if not line_stripped or len(line_stripped) < 3:
            return None

        # Skip table rows (they have multiple | separators)
        if line_stripped.count('|') > 2:
            return None

        # Check for markdown table section headers (bold formatting)
        if re.match(r'^\*\*[^*]+\*\*$', line_stripped):
            dept = line_stripped.strip('*').strip()
            if dept and len(dept) < 60:
                return dept

        # Check for plain text department headers (not in tables)
        if '|' not in line_stripped:
            for pattern in self.department_headers:
                if re.search(pattern, line_stripped, re.IGNORECASE):
                    return line_stripped

        return None

    def is_settlement_marker(self, line: str) -> Optional[str]:
        """Check if line is a settlement marker."""
        line_stripped = line.strip().rstrip('.:')

        # Check if it's just a settlement name
        if line_stripped in self.settlement_names:
            return line_stripped

        # Check if it starts with a settlement name
        for settlement in self.settlement_names:
            if line_stripped.startswith(settlement):
                return settlement

        return None

    def detect_table_format(self, line: str) -> bool:
        """Check if line is part of a markdown table."""
        return '|' in line and line.strip().startswith('|')

    def parse_table_header(self, line: str) -> Dict[str, int]:
        """Parse markdown table header to get column indices."""
        columns = {}
        parts = [p.strip() for p in line.split('|')]

        for idx, part in enumerate(parts):
            part_lower = part.lower()
            if 'rank' in part_lower or 'office' in part_lower:
                columns['rank'] = idx
            elif 'name' in part_lower:
                columns['name'] = idx
            elif 'salary' in part_lower or 'annual' in part_lower:
                columns['salary'] = idx
            elif 'allowance' in part_lower:
                columns['allowances'] = idx
            elif 'remark' in part_lower:
                columns['remarks'] = idx

        return columns

    def parse_table_row(self, line: str, columns: Dict[str, int],
                       line_num: int, colony: str, year: int) -> Optional[Person]:
        """Parse a markdown table row and extract person data."""
        if not line.strip() or line.strip().startswith('|---'):
            return None

        parts = [p.strip() for p in line.split('|')]

        # Extract values based on column indices
        rank = parts[columns.get('rank', -1)] if 'rank' in columns and columns['rank'] < len(parts) else ""
        name = parts[columns.get('name', -1)] if 'name' in columns and columns['name'] < len(parts) else ""
        salary = parts[columns.get('salary', -1)] if 'salary' in columns and columns['salary'] < len(parts) else ""
        allowances = parts[columns.get('allowances', -1)] if 'allowances' in columns and columns['allowances'] < len(parts) else ""
        remarks = parts[columns.get('remarks', -1)] if 'remarks' in columns and columns['remarks'] < len(parts) else ""

        # Check if this is a department header row (only rank column has content, others are empty)
        if rank and not name and not salary:
            # This is likely a department/section header within the table
            dept = self.is_department_header(rank)
            if dept:
                return None  # Will be handled by caller
            # Even if not matched, if rank looks like a header, store it as department context
            if len(rank) > 5 and '.' in rank:  # Headers often end with periods
                return None

        # Clean up values
        rank = rank.strip('*').strip()
        name = name.strip('*').strip()
        salary = salary.strip('£').strip()

        # Handle "ditto" in table cells
        if name.lower() in ['ditto', '"', '„', '—', '–']:
            return None  # Skip ditto rows for now (could be enhanced to carry forward)

        # Validate that this looks like a person
        if not name or len(name) < 2:
            return None

        # Skip if name is a known false positive
        if name in self.skip_terms or name in self.location_names:
            return None

        # Skip if name is just a number or punctuation
        if re.match(r'^[\d\s\-–—.,;:]+$', name):
            return None

        # Skip if this is a section header row
        if rank and not name and not salary:
            return None

        # Use rank as role, or inherit from context
        role = rank if rank else self.last_role
        if not role or role in ['—', '–', '']:
            role = "Unknown"

        # Update context
        if rank and rank not in ['—', '–', '']:
            self.last_role = rank
        if allowances and allowances not in ['—', '–', '']:
            self.last_allowances = allowances

        # Build location string
        location_parts = [colony]
        if self.current_settlement:
            location_parts.append(self.current_settlement)
        if self.current_department:
            location_parts.append(self.current_department)
        location = ' - '.join(location_parts)

        # Extract salary value
        salary_clean = self._clean_salary(salary)

        # Create person object
        person = Person(
            name=self._clean_name(name),
            role=role,
            location=location,
            colony=colony,
            year=year,
            department=self.current_department,
            province=self.current_province,
            salary=salary_clean,
            allowances=allowances if allowances and allowances not in ['—', '–', ''] else None,
            remarks=remarks if remarks and remarks not in ['—', '–', ''] else None,
            full_string=line.strip(),
            source_file=self._generate_github_url(line_num),
            line_number=line_num + 1,
            confidence=0.85,  # Table format is quite reliable
            extraction_method='table'
        )

        return person

    def extract_from_narrative(self, line: str, line_num: int,
                              colony: str, year: int) -> Optional[Person]:
        """Extract person from narrative format (non-table lines)."""
        line_stripped = line.strip()

        # Skip empty or very short lines
        if not line_stripped or len(line_stripped) < 10:
            return None

        # Pattern 1: Rank, Name, Salary
        # e.g., "Colonial Secretary, Capt. O. A. Moloney, 1,000l."
        pattern1 = r'^([A-Z][^,]{3,50}?),\s+([^,]+?),\s+([0-9,]+l\.?)'
        match = re.search(pattern1, line_stripped)
        if match:
            role, name, salary = match.groups()
            return self._create_person(
                name.strip(),
                role.strip(),
                salary.strip(),
                line_stripped,
                line_num,
                colony,
                year,
                confidence=0.9,
                method='narrative_pattern1'
            )

        # Pattern 2: Name, Salary (role from context)
        # e.g., "J. Swan, 600l."
        pattern2 = r'^([A-Z][^,]{2,40}?),\s+([0-9,]+l\.?)'
        match = re.search(pattern2, line_stripped)
        if match:
            name, salary = match.groups()
            role = self.last_role if self.last_role else "Unknown"
            return self._create_person(
                name.strip(),
                role,
                salary.strip(),
                line_stripped,
                line_num,
                colony,
                year,
                confidence=0.7 if self.last_role else 0.5,
                method='narrative_pattern2'
            )

        # Pattern 3: Modern format (1946-1957): Role—Name (em-dash, no salary)
        # e.g., "Prime Minister—K. Nkrumah." or "Director of Agriculture—E. W. Leach."
        # Handles both em-dash (—) and en-dash (–)
        pattern3 = r'^([A-Z].+?)\u2014(.+)\.$'
        match = re.search(pattern3, line_stripped)
        if match:
            role, names = match.groups()
            role = role.strip()
            names = names.strip()

            # Skip if this looks like a sentence (too long, contains "and" followed by long text)
            if len(line_stripped) > 200:
                return None

            # Skip if role contains sentence-like patterns
            if ' consist of ' in role or ' consists of ' in role:
                return None

            # Skip if role starts with common false positive patterns
            false_positive_role_starts = [
                'The Legislative', 'The 75 elected', 'Elected Members',
                'Ex-Officio Members', 'Special Members', 'Southern Section',
                'Representing'
            ]
            if any(role.startswith(fp) for fp in false_positive_role_starts):
                return None

            # Skip if names contain multiple complete role descriptions (comma-separated roles)
            if names.count(',') > 3:  # More than 3 commas suggests a list of things, not a person
                return None

            # Handle multiple names separated by semicolons
            # e.g., "Deputy Directors—J. R. Marshall; Vacant."
            name_list = [n.strip() for n in names.split(';')]

            # Return first valid person (or could return list, but single for now)
            for name in name_list:
                # Skip "Vacant" entries
                if name.lower() in ['vacant', '(vacant)']:
                    continue

                # Skip if name contains "the" (likely a role description, not a name)
                if ' the ' in name.lower():
                    continue

                # Create person with no salary
                person = self._create_person_no_salary(
                    name.strip(),
                    role,
                    line_stripped,
                    line_num,
                    colony,
                    year,
                    confidence=0.75,  # Medium confidence without salary
                    method='modern_format'
                )

                # Store role for potential context
                self.last_role = role

                return person  # Return first valid person

        return None

    def _create_person(self, name: str, role: str, salary: str,
                      line: str, line_num: int, colony: str, year: int,
                      confidence: float, method: str) -> Person:
        """Create a Person object from extracted data."""
        # Build location
        location_parts = [colony]
        if self.current_settlement:
            location_parts.append(self.current_settlement)
        if self.current_department:
            location_parts.append(self.current_department)

        return Person(
            name=self._clean_name(name),
            role=role,
            location=' - '.join(location_parts),
            colony=colony,
            year=year,
            department=self.current_department,
            province=self.current_province,
            salary=self._clean_salary(salary),
            full_string=line,
            source_file=self._generate_github_url(line_num),
            line_number=line_num + 1,
            confidence=confidence,
            extraction_method=method
        )

    def _create_person_no_salary(self, name: str, role: str,
                                 line: str, line_num: int, colony: str, year: int,
                                 confidence: float, method: str) -> Person:
        """Create a Person object from extracted data without salary."""
        # Build location
        location_parts = [colony]
        if self.current_settlement:
            location_parts.append(self.current_settlement)
        if self.current_department:
            location_parts.append(self.current_department)

        return Person(
            name=self._clean_name(name),
            role=role,
            location=' - '.join(location_parts),
            colony=colony,
            year=year,
            department=self.current_department,
            province=self.current_province,
            salary=None,  # No salary in modern format
            full_string=line,
            source_file=self._generate_github_url(line_num),
            line_number=line_num + 1,
            confidence=confidence,
            extraction_method=method
        )

    def _clean_name(self, name: str) -> str:
        """Clean up name field."""
        # Remove common prefixes
        name = re.sub(r'^(&c\.,|Ditto,|The)\s+', '', name)

        # Remove footnote markers
        name = re.sub(r'[†*]', '', name)

        # Remove extra whitespace
        name = ' '.join(name.split())

        return name.strip()

    def _clean_salary(self, salary: str) -> str:
        """Clean up salary field."""
        if not salary:
            return ""

        # Remove currency symbols and clean
        salary = salary.strip('£').strip()

        # Standardize format
        salary = re.sub(r'\s+', ' ', salary)

        return salary

    def _generate_github_url(self, line_number: int) -> str:
        """Generate GitHub URL placeholder."""
        return f"{self.github_base_url}/[file]#L{line_number + 1}"

    def is_false_positive(self, person: Person) -> bool:
        """Check if extraction is a false positive."""
        name = person.name.strip()

        # Check against known false positives
        if name in self.skip_terms or name in self.location_names:
            return True

        # Single word that's all caps (likely abbreviation)
        if len(name.split()) == 1 and name.isupper():
            return True

        # Name is too short
        if len(name) < 2:
            return True

        # Name contains only numbers/punctuation
        if re.match(r'^[\d\s\-–—.,;:]+$', name):
            return True

        # Name contains personnel counts like "800 Privates"
        if re.search(r'\d+\s+(Privates|Officers|Native|Men|Troops)', name, re.IGNORECASE):
            return True

        return False

    def extract_from_file(self, file_path: str, colony: str, year: int) -> List[Person]:
        """
        Extract all people from a Gold Coast file.
        Handles both markdown table format and narrative format.
        """
        print(f"\n{'='*70}")
        print(f"Processing {colony} {year}: {file_path}")
        print('='*70)

        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        people = []
        start_idx = self.find_people_section_start(lines)

        if start_idx == -1:
            print("Warning: Could not find people section start")
            start_idx = 0
        else:
            print(f"People section starts at line {start_idx}")

        # Track table parsing state
        in_table = False
        table_columns = {}

        for i in range(start_idx, len(lines)):
            line = lines[i]
            line_stripped = line.strip()

            if not line_stripped:
                in_table = False
                continue

            # Check for department/section headers
            dept = self.is_department_header(line_stripped)
            if dept:
                self.current_department = dept
                print(f"  Department: {dept}")
                in_table = False
                continue

            # Check for settlement markers
            settlement = self.is_settlement_marker(line_stripped)
            if settlement:
                self.current_settlement = settlement
                print(f"  Settlement: {settlement}")
                continue

            # Check if this is a table line
            if self.detect_table_format(line):
                # Check if this is a header row
                if re.search(r'Rank.*Name|Name.*Salary', line, re.IGNORECASE):
                    table_columns = self.parse_table_header(line)
                    in_table = True
                    print(f"  Found table with columns: {list(table_columns.keys())}")
                    continue

                # Parse table row
                if in_table and table_columns:
                    # First check if this row is a department header within the table
                    parts = [p.strip() for p in line.split('|')]
                    if 'rank' in table_columns and table_columns['rank'] < len(parts):
                        rank_value = parts[table_columns['rank']].strip()
                        name_value = parts[table_columns.get('name', -1)].strip() if 'name' in table_columns and table_columns['name'] < len(parts) else ""
                        salary_value = parts[table_columns.get('salary', -1)].strip() if 'salary' in table_columns and table_columns['salary'] < len(parts) else ""

                        # Check if this is a section header (only rank has content)
                        if rank_value and not name_value and not salary_value:
                            # Clean the rank value
                            clean_rank = rank_value.strip('.').strip()

                            # Filter out false positive departments
                            false_positive_depts = [
                                'The Governor', 'The Colonial Secretary', 'The Administrator',
                                'The Officer Commanding', 'The Chief Justice', 'The Queen\'s Advocate',
                                'The Collector and Treasurer'
                            ]
                            if any(clean_rank.startswith(fp) for fp in false_positive_depts):
                                continue

                            # Check if it's a known department pattern
                            dept = self.is_department_header(clean_rank)
                            if dept:
                                self.current_department = dept.strip('.').strip()
                                print(f"  Department (from table): {self.current_department}")
                                continue

                            # Even if not matched by pattern, might be a department
                            if len(clean_rank) > 5:
                                if any(pattern_match in clean_rank for pattern_match in ['Office', 'Department', 'Council', 'Establishment']):
                                    self.current_department = clean_rank
                                    print(f"  Department (detected): {clean_rank}")
                                    continue

                    person = self.parse_table_row(
                        line, table_columns, i, colony, year
                    )
                    if person and not self.is_false_positive(person):
                        people.append(person)
                continue
            else:
                # Not in table anymore
                in_table = False

            # Try narrative extraction for non-table lines
            person = self.extract_from_narrative(line, i, colony, year)
            if person and not self.is_false_positive(person):
                people.append(person)

        print(f"\nExtracted {len(people)} people from {colony} {year}")
        return people

    def deduplicate(self, people: List[Person]) -> List[Person]:
        """Remove duplicate entries."""
        seen = set()
        deduped = []

        for person in people:
            # Create a key from name + role + year
            key = (person.name.lower(), person.role.lower(), person.year)

            if key not in seen:
                seen.add(key)
                deduped.append(person)

        return deduped


class GoldCoastExtractionOrchestrator:
    """
    Main orchestrator for Gold Coast extraction.
    Provides consistent interface with other colony extractors.
    """

    def __init__(self, github_base_url: str = "https://github.com/jburnford/colonial_office_list/blob/main"):
        self.github_base_url = github_base_url
        self.extractor = GoldCoastPatternExtractor(github_base_url)

    def extract_from_file(self, file_path: str, colony: str, year: int, use_cache: bool = True) -> Tuple[List[Person], Dict]:
        """
        Extract all people from a single file.

        Returns:
            (people, metadata) tuple
        """
        # Extract using pattern extractor
        people = self.extractor.extract_from_file(file_path, colony, year)

        # Deduplicate
        people = self.extractor.deduplicate(people)

        # Count extraction methods
        table_count = sum(1 for p in people if p.extraction_method == 'table')
        narrative_count = sum(1 for p in people if p.extraction_method == 'narrative')

        # Generate metadata
        metadata = {
            'file': file_path,
            'colony': colony,
            'year': year,
            'total_people': len(people),
            'extraction_methods': {
                'table': table_count,
                'narrative': narrative_count
            },
            'avg_confidence': sum(p.confidence for p in people) / len(people) if people else 0,
            'phases': {
                'pattern_extraction': {
                    'extracted': len(people),
                    'table_format': table_count,
                    'narrative_format': narrative_count
                },
                'validation': {
                    'total': len(people),
                    'avg_confidence': sum(p.confidence for p in people) / len(people) if people else 0
                }
            }
        }

        return people, metadata


def main():
    """Main entry point - test on Gold Coast 1880."""
    import argparse

    parser = argparse.ArgumentParser(description='Extract people from Gold Coast Colonial Office Lists')
    parser.add_argument('--year', type=int, default=1880, help='Year to process')
    parser.add_argument('--output', default='gold_coast_people.json', help='Output file')

    args = parser.parse_args()

    # Find the Gold Coast file for the specified year
    base_dirs = [
        '/home/user/colonial_office_list/output',
        '/home/user/colonial_office_list/output_2',
        '/home/user/colonial_office_list/output_3'
    ]

    file_path = None
    for base_dir in base_dirs:
        pattern = f"{base_dir}/{args.year}_manual_parsed/*GOLD*"
        import glob
        files = glob.glob(pattern)
        if files:
            file_path = files[0]
            break

    if not file_path:
        print(f"Error: Could not find Gold Coast file for year {args.year}")
        return

    # Extract people
    extractor = GoldCoastPatternExtractor()
    people = extractor.extract_from_file(file_path, "GOLD_COAST", args.year)
    people = extractor.deduplicate(people)

    # Save results
    results = {
        'metadata': {
            'colony': 'GOLD_COAST',
            'year': args.year,
            'file': file_path,
            'total_people': len(people),
            'extraction_date': '2025-11-20'
        },
        'people': [p.to_dict() for p in people]
    }

    with open(args.output, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n{'='*70}")
    print(f"EXTRACTION COMPLETE")
    print('='*70)
    print(f"Total people extracted: {len(people)}")
    print(f"Saved to: {args.output}")

    # Show sample records
    print(f"\nSample records:")
    for person in people[:5]:
        print(f"  - {person.name} ({person.role}) - {person.salary}")


if __name__ == "__main__":
    main()
