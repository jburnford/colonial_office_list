#!/usr/bin/env python3
"""
Employee Record Extractor
Hybrid approach: Python regex + LLM fallback for Colonial Office Lists
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, asdict
import argparse


@dataclass
class Employee:
    """Represents a single employee record"""
    name: str
    position: str
    salary: Optional[str] = None
    honors: Optional[List[str]] = None
    department: Optional[str] = None
    location: str = ""  # Colony name
    year: int = 0
    extraction_method: str = "regex"  # "regex" or "llm"
    confidence: float = 1.0
    raw_text: str = ""

    def to_dict(self):
        return asdict(self)


class EmployeeExtractor:
    """Extract employee records using regex patterns"""

    # Honors/titles pattern
    HONORS_PATTERN = r'\b(K\.?C\.?M\.?G\.?|G\.?C\.?M\.?G\.?|C\.?M\.?G\.?|K\.?C\.?B\.?|G\.?C\.?B\.?|C\.?B\.?|M\.V\.O\.|O\.B\.E\.|M\.B\.E\.|D\.S\.O\.|M\.C\.|Bart\.|Sir|Hon\.|Rev\.|Rt\.?\s*Rev\.|Most\s+Rev\.|D\.D\.|LL\.?D\.|M\.A\.|B\.A\.|M\.B\.|C\.M\.|Q\.C\.|M\.P\.|R\.N\.|R\.A\.|Col\.|Lieut\.|Capt\.|Major|General|Admiral|F\.S\.I\.|M\.D\.|Esq\.)\b'

    # Salary patterns
    SALARY_PATTERN = r'([\d,]+l\.|[$£][\d,]+|each\s+[\d,]+l\.)'

    # Department headers
    DEPARTMENT_HEADERS = [
        r"^(.+)'s Office\.$",
        r"^(.+) Department\.$",
        r"^(Customs|Police|Post Office|Judicial Establishment|Civil Establishment)\.$"
    ]

    def __init__(self, colony_name: str, year: int):
        self.colony_name = colony_name
        self.year = year
        self.current_department = None

    def extract_honors(self, text: str) -> List[str]:
        """Extract honors and titles from text"""
        honors = re.findall(self.HONORS_PATTERN, text)
        return list(set(honors)) if honors else []

    def clean_name(self, name: str, honors: List[str]) -> str:
        """Remove honors from name and clean up"""
        clean = name
        for honor in honors:
            clean = clean.replace(honor, '').strip()
        # Clean up extra whitespace and trailing punctuation
        clean = re.sub(r'\s+', ' ', clean).strip(' ,.')
        return clean

    def is_department_header(self, line: str) -> Optional[str]:
        """Check if line is a department header"""
        for pattern in self.DEPARTMENT_HEADERS:
            match = re.match(pattern, line.strip())
            if match:
                return match.group(1) if match.lastindex else match.group(0).rstrip('.')
        return None

    def looks_like_position(self, text: str) -> bool:
        """Check if text looks like a job position"""
        position_keywords = [
            'Governor', 'Secretary', 'Clerk', 'Officer', 'Inspector', 'Superintendent',
            'Director', 'Judge', 'Magistrate', 'Attorney', 'Treasurer', 'Auditor',
            'Controller', 'Comptroller', 'Surveyor', 'Engineer', 'Surgeon', 'Medical',
            'Chaplain', 'Bishop', 'Registrar', 'Postmaster', 'Commissioner', 'Agent',
            'Collector', 'Chief', 'Assistant', 'Deputy', 'Minister', 'Lieutenant',
            'Captain', 'Major', 'Colonel', 'General', 'Admiral', 'President',
            'Administrator', 'Librarian', 'Accountant', 'Manager', 'Superintendent',
            'Master', 'Keeper', 'Warden', 'Provost', 'Marshal', 'Harbour', 'Health',
            'Actuary', 'Admeasurer', 'Examiner', 'Coroner', 'Sheriff', 'Chaplain'
        ]

        text_lower = text.lower()
        return any(keyword.lower() in text_lower for keyword in position_keywords)

    def looks_like_name(self, text: str) -> bool:
        """Check if text looks like a person's name"""
        # Should have capitals and not be too long
        if len(text) > 60:
            return False

        # Should have at least one capital followed by lowercase (proper name)
        if not re.search(r'[A-Z][a-z]', text):
            return False

        # Shouldn't be narrative text
        narrative_words = [
            'the', 'and which', 'was', 'were', 'has', 'have',
            'is situated', 'are', 'to', 'from', 'with', 'by',
            'in latitude', 'contains', 'about', 'nearly'
        ]

        text_lower = text.lower()
        for phrase in narrative_words:
            if phrase in text_lower:
                return False

        # Should be relatively short for a name
        word_count = len(text.split())
        if word_count > 8:
            return False

        return True

    def parse_simple_record(self, line: str) -> List[Employee]:
        """
        Parse simple format: Position, Name, Salary
        Examples:
        - Colonial Secretary, G. R. Le Hunte, M.A., 885l.
        - Chief Clerk, W. H. Bailey, 300l.
        """
        employees = []
        line = line.strip()

        # Must have a salary to be considered
        if not re.search(self.SALARY_PATTERN, line):
            return []

        # Handle semicolon-separated multiple entries
        segments = [s.strip() for s in line.split(';')]

        for segment in segments:
            if not segment or len(segment) < 15:
                continue

            # Pattern: Position, Name, [Honors,] Salary
            # Look for: text, text, number
            pattern = r'^([^,]+),\s+([^,]+?)(?:,\s+(.+?))?(?:,\s*(' + self.SALARY_PATTERN + r'))?\s*\.?$'
            match = re.match(pattern, segment)

            if match:
                position = match.group(1).strip()
                name_part = match.group(2).strip()
                middle = match.group(3) if match.group(3) else ""
                salary = match.group(4) if match.group(4) else None

                # Validate position and name
                if not self.looks_like_position(position):
                    continue

                # Extract honors
                full_name = name_part + (", " + middle if middle else "")

                if not self.looks_like_name(full_name):
                    continue

                honors = self.extract_honors(full_name)
                clean_name = self.clean_name(full_name, honors)

                # Skip if name is too short
                if len(clean_name) < 3:
                    continue

                employees.append(Employee(
                    name=clean_name,
                    position=position,
                    salary=salary.strip() if salary else None,
                    honors=honors if honors else None,
                    department=self.current_department,
                    location=self.colony_name,
                    year=self.year,
                    extraction_method="regex",
                    confidence=0.9,
                    raw_text=segment
                ))

        return employees

    def parse_multi_person_line(self, line: str) -> List[Employee]:
        """
        Parse lines with multiple people and shared salaries
        Example: Customs Officers, W. Everard, A. D. Bynoe, each 300l.; G. B. King, 240l.
        """
        employees = []
        line = line.strip()

        # Check for "each" pattern
        if 'each' in line.lower():
            # Pattern: Position, Name1, Name2, each Salary; Name3, Salary
            # This is complex - mark for LLM processing
            return []

        return employees

    def parse_constituency_table(self, line: str) -> List[Employee]:
        """
        Parse constituency table format
        Example: Bridgetown . . E. T. Grannum and J. C. Lynch.
        """
        employees = []

        # Pattern: Location . . Name and Name
        pattern = r'^([A-Z][^.]+)\s+\.\s+\.\s+(.+?)\s+and\s+(.+)\.$'
        match = re.match(pattern, line.strip())

        if match:
            constituency = match.group(1).strip()
            name1 = match.group(2).strip()
            name2 = match.group(3).strip()

            for name in [name1, name2]:
                honors = self.extract_honors(name)
                clean = self.clean_name(name, honors)

                employees.append(Employee(
                    name=clean,
                    position=f"Member for {constituency}",
                    honors=honors if honors else None,
                    department=self.current_department or "House of Assembly",
                    location=self.colony_name,
                    year=self.year,
                    extraction_method="regex",
                    confidence=0.85,
                    raw_text=line.strip()
                ))

        return employees

    def extract_from_text(self, text: str) -> Tuple[List[Employee], List[str]]:
        """
        Extract all employees from colony text
        Returns: (employees, lines_needing_llm)
        """
        employees = []
        llm_needed = []
        lines = text.split('\n')

        for i, line in enumerate(lines):
            line = line.strip()

            # Skip empty lines and pure narrative
            if not line or len(line) < 10:
                continue

            # Check if it's a department header
            dept = self.is_department_header(line)
            if dept:
                self.current_department = dept
                continue

            # Skip obvious non-employee content
            skip_patterns = [
                r'^[A-Z\s]+\.$',  # All caps headers
                r'^The ',  # Narrative text
                r'^\|',  # Tables
                r'^\d{4}',  # Years/dates
                r'^History\.',
                r'^Situation and Area\.',
                r'^General Description\.',
            ]

            should_skip = False
            for pattern in skip_patterns:
                if re.match(pattern, line):
                    should_skip = True
                    break

            if should_skip:
                continue

            # Try parsing methods
            parsed = []

            # Method 1: Simple record
            parsed = self.parse_simple_record(line)
            if parsed:
                employees.extend(parsed)
                continue

            # Method 2: Constituency table
            parsed = self.parse_constituency_table(line)
            if parsed:
                employees.extend(parsed)
                continue

            # Method 3: Multi-person with "each"
            parsed = self.parse_multi_person_line(line)
            if parsed:
                employees.extend(parsed)
                continue

            # If line looks like it has names/salaries but wasn't parsed, flag for LLM
            if (re.search(self.SALARY_PATTERN, line) or
                re.search(r'[A-Z]\.\s+[A-Z]', line)):  # Initials pattern
                llm_needed.append(line)

        return employees, llm_needed


def main():
    parser = argparse.ArgumentParser(
        description='Extract employee records from Colonial Office List colony text files'
    )
    parser.add_argument('text_file', help='Path to colony text file')
    parser.add_argument('-o', '--output', help='Output JSON file', default=None)
    parser.add_argument('--show-llm-needed', action='store_true',
                       help='Show lines that need LLM processing')

    args = parser.parse_args()

    # Parse filename to get colony and year
    filename = Path(args.text_file).name
    match = re.match(r'(\d{4})_(.+)\.txt', filename)
    if match:
        year = int(match.group(1))
        colony = match.group(2).replace('_', ' ')
    else:
        year = 0
        colony = "Unknown"

    # Read text
    with open(args.text_file, 'r') as f:
        text = f.read()

    # Extract employees
    extractor = EmployeeExtractor(colony, year)
    employees, llm_needed = extractor.extract_from_text(text)

    # Show results
    print(f"\n=== {colony} ({year}) ===")
    print(f"Extracted {len(employees)} employees using regex")
    print(f"{len(llm_needed)} lines need LLM processing")

    print(f"\n=== Sample Employees ===")
    for emp in employees[:10]:
        salary_str = f", {emp.salary}" if emp.salary else ""
        dept_str = f" ({emp.department})" if emp.department else ""
        print(f"  {emp.name:30s} - {emp.position}{salary_str}{dept_str}")

    if args.show_llm_needed and llm_needed:
        print(f"\n=== Lines Needing LLM ({len(llm_needed)}) ===")
        for line in llm_needed[:20]:
            print(f"  {line[:100]}")

    # Export JSON
    if args.output:
        output_data = {
            'colony': colony,
            'year': year,
            'total_employees': len(employees),
            'regex_extracted': len(employees),
            'llm_needed': len(llm_needed),
            'employees': [e.to_dict() for e in employees],
            'llm_needed_lines': llm_needed
        }

        with open(args.output, 'w') as f:
            json.dump(output_data, f, indent=2)

        print(f"\nExported to {args.output}")


if __name__ == '__main__':
    main()
