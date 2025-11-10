#!/usr/bin/env python3
"""
Colonial Office List Parser
Extracts colony sections and employee records from Colonial Office List JSON files.
Designed to work across multiple years (1883-1915+) with minimal adjustments.
"""

import json
import re
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional, Tuple
from pathlib import Path
import argparse


@dataclass
class EmployeeRecord:
    """Represents an individual employee record"""
    name: str
    position: str
    salary: Optional[str] = None
    location: Optional[str] = None
    honors: Optional[List[str]] = None
    raw_text: str = ""

    def to_dict(self):
        return asdict(self)


@dataclass
class ColonySection:
    """Represents a colony section with metadata and employee records"""
    colony_name: str
    year: int
    start_char: int
    end_char: int
    text: str
    employees: List[EmployeeRecord]
    departments: List[str]

    def to_dict(self):
        return {
            'colony_name': self.colony_name,
            'year': self.year,
            'start_char': self.start_char,
            'end_char': self.end_char,
            'text': self.text,
            'employees': [e.to_dict() for e in self.employees],
            'departments': self.departments
        }


class ColonialOfficeParser:
    """Parser for Colonial Office List documents"""

    # Known colony name patterns (can be extended)
    COLONY_PATTERNS = [
        # Main colonies
        r'^(CANADA|AUSTRALIA|NEW SOUTH WALES|VICTORIA|QUEENSLAND|SOUTH AUSTRALIA|WESTERN AUSTRALIA|TASMANIA)\.$',
        r'^(NEW ZEALAND|CAPE OF GOOD HOPE|NATAL|CEYLON|HONG KONG|STRAITS SETTLEMENTS)\.$',
        r'^(JAMAICA|BARBADOS|TRINIDAD|BRITISH GUIANA|BRITISH HONDURAS)\.$',
        r'^(BERMUDA|BAHAMAS|FIJI|MAURITIUS|SEYCHELLES)\.$',
        r'^(SIERRA LEONE|GAMBIA|GOLD COAST|LAGOS|NIGERIA)\.$',
        r'^(MALTA|GIBRALTAR|CYPRUS|ADEN|ST\. HELENA)\.$',
        r'^(ANTIGUA|DOMINICA|GRENADA|ST\. LUCIA|ST\. VINCENT|TOBAGO)\.$',
        r'^(LEEWARD ISLANDS|WINDWARD ISLANDS|TURKS ISLANDS|CAYMAN ISLANDS)\.$',
        r'^(FALKLAND ISLANDS|BASUTOLAND|BECHUANALAND|ZULULAND|RHODESIA)\.$',
        r'^(BRITISH EAST AFRICA|BRITISH CENTRAL AFRICA|BRITISH NORTH BORNEO)\.$',
        r'^(LABUAN|SARAWAK|WEI-HAI-WEI|ASCENSION|TRISTAN D\'ACUNHA)\.$'
    ]

    # Patterns for department/section headers
    DEPARTMENT_PATTERNS = [
        r'^DEPARTMENT OF ',
        r'^MINISTRY OF ',
        r'^OFFICE OF ',
        r'^[A-Z][A-Z\s&]+DEPARTMENT\.$',
        r'^GOVERNMENT\.$',
        r'^ESTABLISHMENT\.$',
        r'^PUBLIC OFFICES\.$',
        r'^ECCLESIASTICAL\.$',
        r'^JUDICIAL\.$',
        r'^EDUCATION\.$',
        r'^MEDICAL\.$',
        r'^POLICE\.$',
        r'^RAILWAY\.$',
        r'^POSTAL\.$'
    ]

    # Common position/title keywords that indicate an employee record
    POSITION_KEYWORDS = [
        'Governor', 'Lieutenant', 'Commissioner', 'Administrator', 'Resident',
        'Minister', 'Secretary', 'Under-Secretary', 'Assistant', 'Deputy',
        'Chief', 'Clerk', 'Officer', 'Inspector', 'Superintendent', 'Director',
        'Judge', 'Magistrate', 'Attorney', 'Solicitor', 'Treasurer', 'Auditor',
        'Collector', 'Controller', 'Comptroller', 'Surveyor', 'Engineer',
        'Architect', 'Surgeon', 'Medical', 'Doctor', 'Chaplain', 'Bishop',
        'Archbishop', 'Registrar', 'Postmaster', 'Commandant', 'Captain',
        'Major', 'Colonel', 'General', 'Admiral', 'Commodore', 'Agent',
        'Consul', 'Protector', 'Warden', 'Keeper', 'Custodian', 'Curator',
        'Librarian', 'Archivist', 'Accountant', 'Cashier', 'Manager',
        'Principal', 'Headmaster', 'Professor', 'Examiner', 'Coroner',
        'Sheriff', 'Marshal', 'Bailiff', 'Harbourmaster', 'Pilot',
        'Messenger', 'Interpreter', 'Translator', 'Typist', 'Stenographer'
    ]

    # Pattern for employee records
    # Format: Position, Name [Honors], $Salary
    # or: Position, Name [Honors]
    EMPLOYEE_PATTERNS = [
        # With salary: "Position, Name, $Amount" or "Position, Name, £Amount"
        r'^([^,]{3,80}),\s+([^,]{3,50}?),\s+([$£]\d[\d,]+)',
        # Without salary: "Position, Name" - but name must end with period
        r'^([^,]{3,80}),\s+([^,\.]{3,50})\.',
    ]

    # Honors/titles to extract
    HONORS_PATTERN = r'\b(K\.C\.M\.G\.|G\.C\.M\.G\.|C\.M\.G\.|K\.C\.B\.|G\.C\.B\.|C\.B\.|M\.V\.O\.|O\.B\.E\.|M\.B\.E\.|D\.S\.O\.|M\.C\.|Bart\.|Sir|Hon\.|Rev\.|Rt\.?\s*Rev\.|Most\s+Rev\.|D\.D\.|LL\.D\.|M\.A\.|B\.A\.|Q\.C\.|M\.P\.|R\.N\.|Col\.|Lieut\.|Capt\.|Major|General|Admiral)\b'

    def __init__(self, json_path: str):
        """Initialize parser with path to Colonial Office List JSON file"""
        self.json_path = Path(json_path)
        self.data = None
        self.text = None
        self.year = self._extract_year_from_filename()

    def _extract_year_from_filename(self) -> int:
        """Extract year from filename"""
        match = re.search(r'(\d{4})', self.json_path.name)
        return int(match.group(1)) if match else 0

    def load(self):
        """Load JSON data"""
        with open(self.json_path, 'r') as f:
            self.data = json.load(f)

        # Extract text from the JSON structure
        if isinstance(self.data, list) and len(self.data) > 0:
            self.text = self.data[0]['text']
        else:
            raise ValueError("Unexpected JSON structure")

        print(f"Loaded {len(self.text)} characters from {self.json_path.name}")

    def find_colony_boundaries(self) -> List[Tuple[str, int, int]]:
        """
        Find all colony section boundaries in the text.
        Returns list of (colony_name, start_pos, end_pos)
        """
        colonies = []
        lines = self.text.split('\n')

        # Track positions in original text
        current_pos = 0
        line_positions = []
        for line in lines:
            line_positions.append(current_pos)
            current_pos += len(line) + 1  # +1 for newline

        # Find all colony headers
        colony_starts = []
        for i, line in enumerate(lines):
            for pattern in self.COLONY_PATTERNS:
                if re.match(pattern, line.strip()):
                    colony_name = line.strip().rstrip('.')
                    colony_starts.append((colony_name, i, line_positions[i]))
                    print(f"Found colony: {colony_name} at line {i}")
                    break

        # Create boundaries (start of one colony to start of next)
        for i in range(len(colony_starts)):
            colony_name, line_num, start_pos = colony_starts[i]

            # End position is start of next colony or end of text
            if i + 1 < len(colony_starts):
                end_pos = colony_starts[i + 1][2]
            else:
                end_pos = len(self.text)

            colonies.append((colony_name, start_pos, end_pos))

        print(f"\nFound {len(colonies)} colony sections")
        return colonies

    def extract_departments(self, text: str) -> List[str]:
        """Extract department names from colony text"""
        departments = []
        for line in text.split('\n'):
            line = line.strip()
            for pattern in self.DEPARTMENT_PATTERNS:
                if re.search(pattern, line):
                    departments.append(line.rstrip('.'))
                    break
        return departments

    def extract_honors(self, text: str) -> List[str]:
        """Extract honors and titles from text"""
        return re.findall(self.HONORS_PATTERN, text)

    def _looks_like_position(self, text: str) -> bool:
        """Check if text looks like a position/title"""
        # Check for position keywords
        for keyword in self.POSITION_KEYWORDS:
            if keyword.lower() in text.lower():
                return True

        # Additional heuristics: starts with certain patterns
        position_patterns = [
            r'^(Acting|Deputy|Assistant|Chief|Senior|Junior|Sub-|Vice-)',
            r'(in Charge|of the|and |for )',
        ]
        for pattern in position_patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return True

        return False

    def _looks_like_name(self, text: str) -> bool:
        """Check if text looks like a person's name"""
        # Remove honors first
        clean_text = text
        for honor in re.findall(self.HONORS_PATTERN, text):
            clean_text = clean_text.replace(honor, '').strip()

        # Names should have at least one capital letter followed by lowercase
        if not re.search(r'[A-Z][a-z]', clean_text):
            return False

        # Names shouldn't be too long (probably not a name if > 50 chars after honors removed)
        if len(clean_text) > 50:
            return False

        # Names shouldn't contain certain words
        invalid_words = ['and ', 'or ', 'the ', 'is ', 'are ', 'was ', 'were ',
                        'in ', 'of ', 'to ', 'for ', 'with ', 'by ', 'at ']
        clean_lower = clean_text.lower()
        for word in invalid_words:
            if word in clean_lower and len(clean_text) > 20:
                return False

        # Check if it has typical name structure (initials, surnames, etc.)
        # Examples: "John Smith", "J. Smith", "Sir John Smith", "Smith, J."
        name_patterns = [
            r'^[A-Z][a-z]+(?:\s+[A-Z]\.?\s*)+[A-Z][a-z]+',  # First Last or First I. Last
            r'^[A-Z]\.?\s*[A-Z][a-z]+',  # I. Last
            r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)+',  # First Last or First Middle Last
        ]
        for pattern in name_patterns:
            if re.search(pattern, clean_text):
                return True

        # If none of the above, but short and has caps, might still be a name
        if len(clean_text) < 30 and re.search(r'[A-Z]', clean_text):
            return True

        return False

    def parse_employee_record(self, line: str, context: str = "") -> Optional[EmployeeRecord]:
        """
        Parse a single line to extract employee information.
        Context can be used for department/location information.
        """
        line = line.strip()

        # Skip empty lines and obvious non-employee lines
        if not line or len(line) < 10:
            return None

        # Skip section headers and other structural elements
        if re.match(r'^[A-Z\s]{10,}\.$', line):  # All caps headers
            return None
        if line.startswith('(') or line.startswith('[') or line.startswith('|'):
            return None

        # Try different employee record patterns
        for pattern in self.EMPLOYEE_PATTERNS:
            match = re.match(pattern, line)
            if match:
                groups = match.groups()

                # Determine which fields we captured
                if len(groups) == 3:  # position, name, salary
                    position, name, salary = groups
                elif len(groups) == 2:  # position, name
                    position, name = groups
                    salary = None
                else:
                    continue

                # Validate that position looks like a position
                if not self._looks_like_position(position):
                    continue

                # Validate that name looks like a name
                if not self._looks_like_name(name):
                    continue

                # Extract honors from name
                honors = self.extract_honors(name)

                # Clean up name (remove honors)
                clean_name = name
                for honor in honors:
                    clean_name = clean_name.replace(honor, '').strip()
                clean_name = re.sub(r'\s+', ' ', clean_name).strip(' ,.')

                # Final validation on clean name
                if len(clean_name) < 2:
                    continue

                return EmployeeRecord(
                    name=clean_name,
                    position=position.strip(),
                    salary=salary.strip() if salary else None,
                    honors=honors if honors else None,
                    raw_text=line
                )

        return None

    def parse_colony_section(self, colony_name: str, start: int, end: int) -> ColonySection:
        """Parse a single colony section to extract all employee records"""
        section_text = self.text[start:end]

        # Extract departments
        departments = self.extract_departments(section_text)

        # Extract employees
        employees = []
        current_department = ""
        current_location = ""

        for line in section_text.split('\n'):
            # Track current department for context
            for pattern in self.DEPARTMENT_PATTERNS:
                if re.search(pattern, line.strip()):
                    current_department = line.strip().rstrip('.')
                    break

            # Try to parse employee record
            employee = self.parse_employee_record(line, context=current_department)
            if employee:
                employee.location = current_location or colony_name
                employees.append(employee)

        print(f"  {colony_name}: Found {len(employees)} employees, {len(departments)} departments")

        return ColonySection(
            colony_name=colony_name,
            year=self.year,
            start_char=start,
            end_char=end,
            text=section_text[:5000],  # Store first 5000 chars for reference
            employees=employees,
            departments=departments
        )

    def parse_all_colonies(self) -> List[ColonySection]:
        """Parse all colony sections in the document"""
        boundaries = self.find_colony_boundaries()

        colonies = []
        for colony_name, start, end in boundaries:
            colony_section = self.parse_colony_section(colony_name, start, end)
            colonies.append(colony_section)

        return colonies

    def export_to_json(self, colonies: List[ColonySection], output_path: str):
        """Export parsed data to JSON"""
        output_data = {
            'source_file': str(self.json_path),
            'year': self.year,
            'total_colonies': len(colonies),
            'total_employees': sum(len(c.employees) for c in colonies),
            'colonies': [c.to_dict() for c in colonies]
        }

        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            json.dump(output_data, f, indent=2)

        print(f"\nExported to {output_path}")
        print(f"  Total colonies: {output_data['total_colonies']}")
        print(f"  Total employees: {output_data['total_employees']}")

    def generate_summary_report(self, colonies: List[ColonySection]) -> str:
        """Generate a text summary report"""
        report = []
        report.append(f"Colonial Office List Parser Report - Year {self.year}")
        report.append("=" * 60)
        report.append(f"\nTotal Colonies: {len(colonies)}")
        report.append(f"Total Employees: {sum(len(c.employees) for c in colonies)}\n")

        report.append("\nColonies by Employee Count:")
        report.append("-" * 40)

        sorted_colonies = sorted(colonies, key=lambda c: len(c.employees), reverse=True)
        for colony in sorted_colonies:
            report.append(f"  {colony.colony_name:30s} : {len(colony.employees):4d} employees")

        # Sample some employee records
        report.append("\n\nSample Employee Records:")
        report.append("-" * 40)
        for colony in colonies[:3]:  # First 3 colonies
            if colony.employees:
                report.append(f"\n{colony.colony_name}:")
                for emp in colony.employees[:5]:  # First 5 employees
                    salary_str = f" ({emp.salary})" if emp.salary else ""
                    honors_str = f" [{', '.join(emp.honors)}]" if emp.honors else ""
                    report.append(f"  - {emp.name}{honors_str}: {emp.position}{salary_str}")

        return "\n".join(report)


def main():
    parser = argparse.ArgumentParser(
        description='Parse Colonial Office List JSON files to extract colony sections and employee records'
    )
    parser.add_argument(
        'input_file',
        help='Path to Colonial Office List JSON file'
    )
    parser.add_argument(
        '-o', '--output',
        help='Output JSON file path (default: input_name_parsed.json)',
        default=None
    )
    parser.add_argument(
        '-r', '--report',
        help='Generate summary report to this file',
        default=None
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Verbose output'
    )

    args = parser.parse_args()

    # Set default output path
    if args.output is None:
        input_path = Path(args.input_file)
        args.output = input_path.parent / f"{input_path.stem}_parsed.json"

    # Parse the document
    print(f"Parsing {args.input_file}...")
    col_parser = ColonialOfficeParser(args.input_file)
    col_parser.load()

    # Extract all colonies
    colonies = col_parser.parse_all_colonies()

    # Export results
    col_parser.export_to_json(colonies, args.output)

    # Generate report if requested
    if args.report:
        report = col_parser.generate_summary_report(colonies)
        with open(args.report, 'w') as f:
            f.write(report)
        print(f"Report saved to {args.report}")
    else:
        # Print summary to console
        print("\n" + col_parser.generate_summary_report(colonies))


if __name__ == '__main__':
    main()
