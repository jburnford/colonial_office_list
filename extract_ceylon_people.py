#!/usr/bin/env python3
"""
Extract people data from Ceylon Colonial Office List files.
Hybrid Python-LLM approach for robust extraction.
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
    department: Optional[str]
    full_string: str  # Original text for later analysis
    source_file: str  # GitHub URL
    line_number: int
    confidence: float  # 0-1 score

    def to_dict(self):
        return asdict(self)


class CeylonPeopleExtractor:
    """Extract people data from Ceylon Colonial Office List files."""

    def __init__(self, github_base_url: str = "https://github.com/jburnford/colonial_office_list/blob/main"):
        self.github_base_url = github_base_url
        self.current_department = None
        self.current_province = None

        # Common section headers that indicate start of people data
        self.people_section_headers = [
            r"^Civil Establishment",
            r"^CIVIL ESTABLISHMENT",
            r"^Executive Council",
            r"^Legislative Council",
        ]

        # Section headers for departments/categories
        self.department_headers = [
            r"Colonial Secretary'?s? Office",
            r"Treasurer'?s? Department",
            r"Audit Office",
            r"Surveyor General'?s? Department",
            r"Customs Department",
            r"Government Agents?",
            r"Judicial Establishment",
            r"Medical Department",
            r"Police",
            r"Ecclesiastical Department",
            r"Post-?Office",
            r"Education",
            r"Public Works",
        ]

        # Provincial markers
        self.province_markers = [
            r"Western Province",
            r"Central Province",
            r"Southern Province",
            r"Northern Province",
            r"Eastern Province",
            r"North Western Province",
            r"North-?Western Province",
        ]

        # Patterns for extracting person data
        self.person_patterns = [
            # Pattern 1: Role, Name (with titles/quals), Salary
            # e.g., "Governor, &c., Sir H. G. Robinson, Knt., 7,000l."
            r'^([A-Z][^,]+?),\s+(.+?),\s+(\d+[,\d]*l\.?)(?:\s|$)',

            # Pattern 2: Role, Location, Name, Salary
            # e.g., "Assistant Government Agent, Kandy, G. S. Williams, 450l."
            r'^([A-Z][^,]+?),\s+([A-Z][^,]+?),\s+(.+?),\s+(\d+[,\d]*l\.?)(?:\s|$)',

            # Pattern 3: Just name and salary (inherits role from context)
            # e.g., "J. Swan, 600l."
            r'^([A-Z][^,]+?),\s+(\d+[,\d]*l\.?)(?:\s|$)',

            # Pattern 4: Name only (from lists like "Writers, commencing at...")
            r'^([A-Z]\.\s+[A-Z][a-z]+)(?:,|\.|$)',
        ]

    def find_people_section_start(self, lines: List[str]) -> int:
        """Find where the people data starts in the file."""
        for i, line in enumerate(lines):
            for pattern in self.people_section_headers:
                if re.search(pattern, line.strip()):
                    return i
        # Fallback: look for "Civil Establishment" case-insensitive
        for i, line in enumerate(lines):
            if "civil establishment" in line.lower():
                return i
        return -1

    def is_department_header(self, line: str) -> Optional[str]:
        """Check if line is a department header and return department name."""
        line_stripped = line.strip()
        if not line_stripped or len(line_stripped) < 3:
            return None

        for pattern in self.department_headers:
            if re.search(pattern, line_stripped, re.IGNORECASE):
                return line_stripped.rstrip('.')
        return None

    def is_province_marker(self, line: str) -> Optional[str]:
        """Check if line is a province marker and return province name."""
        line_stripped = line.strip()
        for pattern in self.province_markers:
            if re.search(pattern, line_stripped, re.IGNORECASE):
                return line_stripped.rstrip('.')
        return None

    def extract_person_from_line(self, line: str, line_num: int) -> Optional[Tuple[Dict, float]]:
        """
        Try to extract person data from a line.
        Returns (person_dict, confidence) or None.
        """
        line_stripped = line.strip()

        # Skip empty lines, very short lines, or lines that look like headers
        if not line_stripped or len(line_stripped) < 10:
            return None

        # Skip lines that are clearly not people
        skip_patterns = [
            r'^Total',
            r'^Male',
            r'^Female',
            r'^\d+\s+[A-Z]',  # Year + name (from governor lists)
            r'^List of',
            r'^With the',
            r'^British Governors',
        ]
        for pattern in skip_patterns:
            if re.match(pattern, line_stripped):
                return None

        # Try each pattern
        for pattern_idx, pattern in enumerate(self.person_patterns):
            match = re.search(pattern, line_stripped)
            if match:
                groups = match.groups()

                # Pattern-specific extraction
                if pattern_idx == 0:  # Role, Name, Salary
                    role = groups[0].strip()
                    name = groups[1].strip()
                    salary_str = groups[2] if len(groups) > 2 else ""

                elif pattern_idx == 1:  # Role, Location, Name, Salary
                    role = groups[0].strip()
                    location = groups[1].strip()
                    name = groups[2].strip()
                    salary_str = groups[3] if len(groups) > 3 else ""

                elif pattern_idx == 2:  # Name, Salary
                    name = groups[0].strip()
                    role = "Unknown"  # Will need context
                    salary_str = groups[1]

                else:  # Name only
                    name = groups[0].strip()
                    role = "Unknown"
                    salary_str = ""

                # Basic validation: does this look like a real name?
                if self._looks_like_name(name):
                    confidence = 0.9 if pattern_idx < 2 else 0.5
                    return {
                        'name': name,
                        'role': role,
                        'salary_string': salary_str,
                        'department': self.current_department,
                        'province': self.current_province,
                    }, confidence

        return None

    def _looks_like_name(self, text: str) -> bool:
        """Check if text looks like a person's name."""
        # Must contain at least one capital letter
        if not re.search(r'[A-Z]', text):
            return False

        # Should not be too long (avoid picking up descriptions)
        if len(text) > 80:
            return False

        # Should not start with common non-name words
        non_name_starts = ['The', 'Members', 'List', 'Total', 'Revenue']
        for word in non_name_starts:
            if text.startswith(word):
                return False

        return True

    def extract_from_file(self, file_path: str, year: int) -> List[Person]:
        """Extract all people from a Ceylon Colonial Office List file."""
        people = []

        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Find where people section starts
        start_idx = self.find_people_section_start(lines)
        if start_idx == -1:
            print(f"Warning: Could not find people section in {file_path}")
            return people

        print(f"Processing {year}, people section starts at line {start_idx + 1}")

        # Process lines from start to end
        self.current_department = None
        self.current_province = None

        for i in range(start_idx, len(lines)):
            line = lines[i]
            line_stripped = line.strip()

            if not line_stripped:
                continue

            # Check for department header
            dept = self.is_department_header(line)
            if dept:
                self.current_department = dept
                self.current_province = None  # Reset province when new dept starts
                continue

            # Check for province marker
            prov = self.is_province_marker(line)
            if prov:
                self.current_province = prov
                continue

            # Try to extract person
            result = self.extract_person_from_line(line, i + 1)
            if result:
                person_dict, confidence = result

                # Build location string
                location_parts = ["Ceylon"]
                if self.current_province:
                    location_parts.append(self.current_province)
                if self.current_department and self.current_department != self.current_province:
                    location_parts.append(self.current_department)

                # Create Person object
                person = Person(
                    name=person_dict['name'],
                    role=person_dict['role'],
                    location=' - '.join(location_parts),
                    colony="CEYLON",
                    year=year,
                    department=self.current_department,
                    full_string=line_stripped,
                    source_file=self._generate_github_url(file_path, i + 1),
                    line_number=i + 1,
                    confidence=confidence
                )
                people.append(person)

        return people

    def _generate_github_url(self, file_path: str, line_number: int) -> str:
        """Generate GitHub URL for source line."""
        # Convert file path to relative path from repo root
        rel_path = file_path.replace('/home/user/colonial_office_list/', '')
        return f"{self.github_base_url}/{rel_path}#L{line_number}"

    def process_all_ceylon_files(self, output_3_dir: str = "output_3") -> Dict:
        """Process all Ceylon files and return extracted data."""
        ceylon_files = []

        # Find all Ceylon files
        for root, dirs, files in os.walk(output_3_dir):
            for file in files:
                if 'ceylon' in file.lower():
                    full_path = os.path.join(root, file)
                    # Extract year from directory name
                    dir_name = os.path.basename(root)
                    year_match = re.search(r'(\d{4})', dir_name)
                    if year_match:
                        year = int(year_match.group(1))
                        ceylon_files.append((year, full_path))

        # Sort by year
        ceylon_files.sort()

        all_people = []
        year_counts = {}

        for year, file_path in ceylon_files:
            print(f"\n{'='*60}")
            print(f"Processing {year}: {file_path}")
            print('='*60)

            people = self.extract_from_file(file_path, year)
            all_people.extend(people)
            year_counts[year] = len(people)

            print(f"Extracted {len(people)} people from {year}")

            # Show first few extractions as examples
            if people:
                print("\nSample extractions:")
                for person in people[:5]:
                    print(f"  - {person.name} | {person.role} | {person.department or 'N/A'}")

        # Generate summary
        summary = {
            "extraction_date": "2025-11-19",
            "colony": "CEYLON",
            "total_people": len(all_people),
            "files_processed": len(ceylon_files),
            "year_range": f"{min(year_counts.keys())}-{max(year_counts.keys())}",
            "people_per_year": year_counts,
            "avg_confidence": sum(p.confidence for p in all_people) / len(all_people) if all_people else 0,
        }

        return {
            "metadata": summary,
            "people": [p.to_dict() for p in all_people]
        }


def main():
    """Main entry point."""
    extractor = CeylonPeopleExtractor()

    # Process all Ceylon files
    results = extractor.process_all_ceylon_files()

    # Save results
    output_file = "ceylon_people_data.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*60}")
    print("EXTRACTION COMPLETE")
    print('='*60)
    print(f"Total people extracted: {results['metadata']['total_people']}")
    print(f"Files processed: {results['metadata']['files_processed']}")
    print(f"Year range: {results['metadata']['year_range']}")
    print(f"Average confidence: {results['metadata']['avg_confidence']:.2f}")
    print(f"Output saved to: {output_file}")
    print('='*60)


if __name__ == "__main__":
    main()
