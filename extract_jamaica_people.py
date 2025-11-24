#!/usr/bin/env python3
"""
Colonial Office List - Jamaica People Extraction System (Specialized V1)

Specialized extractor for Jamaica based on proven Ceylon extractor architecture.

Jamaica-Specific Features:
1. 14 parishes: Kingston, St. Andrew, Portland, St. Thomas, St. Catherine,
   St. James, Trelawny, St. Ann, St. Mary, Clarendon, Manchester,
   St. Elizabeth, Westmoreland, Hanover
2. Major towns as location markers
3. Parish-based organization for Rectors, Magistrates, etc.
4. Salary formats: "1,500l." (early) to "1,350l. to 1,500l." (later)
5. Multiple people per line with semicolons
6. Dependencies: Cayman Islands

Target: 90-95% accuracy

Architecture based on: extract_ceylon_people.py (proven 96.2/100 quality)

Usage:
    python extract_jamaica_people.py --year 1867
    python extract_jamaica_people.py --test
"""

import os
import re
import json
import argparse
from pathlib import Path
from typing import List, Dict, Optional, Tuple, Set
from dataclasses import dataclass, asdict, field
from datetime import datetime


@dataclass
class Person:
    """Extracted person record."""
    name: str
    role: str
    location: str
    colony: str
    year: int
    department: Optional[str] = None
    parish: Optional[str] = None
    salary: Optional[str] = None
    full_string: str = ""
    source_file: str = ""
    line_number: int = 0
    confidence: float = 0.0
    extraction_method: str = "unknown"
    notes: str = ""
    qualifications: Optional[str] = None


@dataclass
class FileAnalysis:
    """File structure analysis."""
    file_path: str
    colony: str
    year: int
    people_section_start: int
    people_section_end: int
    start_marker: str
    departments: List[str] = field(default_factory=list)
    parishes: List[str] = field(default_factory=list)
    primary_format: str = ""
    has_lists: bool = False
    has_ditto: bool = False
    salary_currency: str = ""
    ocr_quality: str = "unknown"
    extraction_notes: List[str] = field(default_factory=list)

    def to_dict(self):
        return asdict(self)


@dataclass
class FlaggedSection:
    """Section flagged for manual review."""
    line_start: int
    line_end: int
    lines: List[str]
    reason: str
    context: Dict = field(default_factory=dict)


# Jamaica-specific constants
JAMAICA_PARISHES = {
    'Kingston', 'St. Andrew', "St. Andrew's", 'Portland', 'St. Thomas',
    'St. Thomas ye East', 'St. Thomas-in-the-East', 'St. Thomas ye Vale',
    'St. Thomas-in-the-Vale', 'St. Catherine', "St. Catharine", 'St. James',
    'Trelawny', 'Trelawney', 'St. Ann', "St. Ann's", 'St. Mary',
    'Clarendon', 'Manchester', 'St. Elizabeth', 'Westmoreland', 'Hanover',
    'St. Dorothy', 'St. David', 'St. John', 'St. George', 'Vere', 'Metcalfe',
    'Port Royal'  # Special status
}

JAMAICA_TOWNS = {
    # Major cities
    'Kingston', 'Spanish Town', 'Port Royal', 'Montego Bay', 'Falmouth',
    'Port Maria', 'Port Antonio', 'Savanna la Mar', 'Savanna-la-mar',
    'Black River', 'Morant Bay', 'May Pen', 'Lucea', 'Mandeville',
    'Christiana', 'Buff Bay', 'Annotto Bay', 'Port Morant', 'Alligator Pond',
    'Old Harbour', 'Rio Bueno', 'Dry Harbour', 'St. Ann\'s Bay',
    'Montego Bay', 'Brown\'s Town', 'Linestead', 'Ocho Rios',

    # Other locations
    'Newcastle', 'Gordon Town', 'Half Way Tree', 'Bog Walk', 'Ewarton',
    'Porus', 'Clarendon Park', 'Vere', 'Manchioneal', 'Bath',
    'Port Morant', 'Linstead', 'Blue Mountain Valley', 'Stony Gut',
    'Point Hill', 'Chapelton'
}

JAMAICA_LOCATIONS = JAMAICA_PARISHES | JAMAICA_TOWNS

JAMAICA_DEPARTMENTS = [
    'Civil Establishment', 'Colonial Secretary\'s Office', 'Treasurer\'s Department',
    'Finance Office', 'Financial Secretary\'s Office', 'Audit Office', 'Audit-Office',
    'Public Works', 'Public Works Department', 'Roads and Bridges',
    'Customs', 'Customs Department', 'Revenue Department', 'Public Treasury',
    'Medical Department', 'Judicial Establishment', 'Judicial Department',
    'Police', 'Police Department', 'Constabulary',
    'Education Department', 'Post Office', 'Post-Office',
    'Immigration', 'Ecclesiastical Department',
    'Geological Survey', 'Botanical Establishment',
    'Privy Council', 'Legislative Council', 'Executive Council'
]

# Qualifications that are NOT roles
JAMAICA_QUALIFICATIONS = {
    'M.D.', 'M.R.C.S.', 'M.R.C.S.E.', 'F.R.C.S.', 'F.R.C.S. Edin.',
    'M. Inst. C.E.', 'M.I.C.E.', 'Assoc. Inst. C.E.', 'A.M.I.C.E.',
    'A.R.I.B.A.', 'A.M.I.Mech.E.',
    'B.A.', 'M.A.', 'LL.D.', 'LL.B.', 'D.C.L.', 'Q.C.', 'K.C.', 'P.C.',
    'C.M.G.', 'K.C.M.G.', 'G.C.M.G.', 'C.B.', 'K.C.B.', 'G.C.B.',
    'K.B.E.', 'O.B.E.', 'M.B.E.', 'C.I.E.',
    'R.E.', 'R.N.', 'C.M.', 'J.P.'
}

# Plural-to-Singular role mappings
PLURAL_TO_SINGULAR_ROLES = {
    'Clerks': 'Clerk',
    'Assistants': 'Assistant',
    'Officers': 'Officer',
    'Inspectors': 'Inspector',
    'Agents': 'Agent',
    'Surveyors': 'Surveyor',
    'Engineers': 'Engineer',
    'Magistrates': 'Magistrate',
    'Rectors': 'Rector',
    'Curates': 'Curate',
    'Writers': 'Writer',
    'Superintendents': 'Superintendent',
    'Sub-Collectors': 'Sub-Collector',
    'Landing Waiters': 'Landing Waiter',
    'Landing Surveyors': 'Landing Surveyor',
}


class JamaicaExtractionOrchestrator:
    """Main orchestrator for Jamaica specialized extraction."""

    def __init__(self, github_base_url: str = "https://github.com/jburnford/colonial_office_list/blob/main"):
        self.github_base_url = github_base_url
        self.analysis_cache = {}

    def extract_from_file(self, file_path: str, colony: str, year: int, use_cache: bool = True) -> Tuple[List[Person], Dict]:
        """
        Extract all people from a single file using specialized Jamaica approach.

        Returns:
            (people, metadata) tuple
        """
        print(f"\n{'='*70}")
        print(f"Processing {colony} {year}: {file_path}")
        print('='*70)

        # Read file
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        metadata = {
            'file': file_path,
            'colony': colony,
            'year': year,
            'total_lines': len(lines),
            'phases': {},
            'jamaica_specific': {
                'locations_filtered': 0,
                'qualifications_filtered': 0,
                'names_filtered': 0,
                'vacant_positions': 0,
                'parishes_detected': 0
            }
        }

        # PHASE 1: File Analysis
        print("\nPHASE 1: Analyzing file structure...")
        file_analysis = self._analyze_file_structure(lines, colony, year, file_path, use_cache)
        metadata['phases']['analysis'] = {
            'people_section': f"lines {file_analysis.people_section_start}-{file_analysis.people_section_end}",
            'departments': len(file_analysis.departments),
            'parishes': len(file_analysis.parishes)
        }

        # PHASE 2: Pattern-based extraction (Python)
        print("\nPHASE 2: Pattern-based extraction (Jamaica-specific)...")
        pattern_extractor = JamaicaPatternExtractor(self.github_base_url)
        preliminary, flagged = pattern_extractor.extract(
            lines, file_analysis, colony, year
        )
        print(f"  Extracted {len(preliminary)} people via patterns")
        print(f"  Flagged {len(flagged)} sections for manual review")

        metadata['phases']['pattern_extraction'] = {
            'extracted': len(preliminary),
            'flagged_sections': len(flagged)
        }

        # PHASE 3: LLM extraction DISABLED (following Ceylon model)
        print("\nPHASE 3: LLM extraction...")
        additional = self._llm_extract_flagged(flagged, file_analysis, lines)
        print(f"  Extracted {len(additional)} additional people via LLM")
        metadata['phases']['llm_extraction'] = {
            'extracted': len(additional),
            'note': 'Task-based extraction disabled for quality - rely on patterns only'
        }

        # PHASE 4: Validate and filter
        print("\nPHASE 4: Validation and filtering...")
        all_people = preliminary + additional
        validated = self._validate_and_merge(all_people, lines, file_analysis)
        print(f"  Final count: {len(validated)} people")

        # Update Jamaica-specific stats from validator
        validator = JamaicaValidator()
        metadata['jamaica_specific'] = validator.stats

        metadata['phases']['validation'] = {
            'total': len(validated),
            'avg_confidence': sum(p.confidence for p in validated) / len(validated) if validated else 0,
            'filtered_out': len(all_people) - len(validated)
        }

        return validated, metadata

    def _analyze_file_structure(self, lines: List[str], colony: str, year: int,
                                file_path: str, use_cache: bool) -> FileAnalysis:
        """
        Phase 1: Analyze file structure for Jamaica.
        """
        # Find people section - look for "Civil Establishment" or "Governors"
        start_idx = -1
        for i, line in enumerate(lines):
            if re.search(r'Civil Establishment|^Governors', line, re.IGNORECASE):
                start_idx = i
                break

        if start_idx == -1:
            # Fallback: look for first salary mention
            for i, line in enumerate(lines):
                if re.search(r'\d+l\.', line):
                    start_idx = max(0, i - 10)
                    break

        if start_idx == -1:
            start_idx = len(lines) // 2  # Final fallback

        # Detect departments and parishes
        departments = set()
        parishes = set()

        for line in lines[start_idx:]:
            # Check for known Jamaica departments
            for dept in JAMAICA_DEPARTMENTS:
                if dept.lower() in line.lower():
                    departments.add(dept)

            # Check for known Jamaica parishes
            for parish in JAMAICA_PARISHES:
                if parish.lower() in line.lower():
                    parishes.add(parish)

        return FileAnalysis(
            file_path=file_path,
            colony=colony,
            year=year,
            people_section_start=start_idx,
            people_section_end=len(lines),
            start_marker="Civil Establishment (detected)",
            departments=sorted(list(departments))[:30],
            parishes=sorted(list(parishes)),
            primary_format="Role, Name, Salary (with parish/location variations)",
            has_lists=True,
            has_ditto=True,
            salary_currency="£ sterling",
            ocr_quality="good"
        )

    def _llm_extract_flagged(self, flagged: List[FlaggedSection],
                            file_analysis: FileAnalysis,
                            lines: List[str]) -> List[Person]:
        """
        Phase 3: LLM extraction - DISABLED for Jamaica (following Ceylon model).
        """
        print("  Task-based extraction DISABLED (following Ceylon model)")
        print("  Relying on pattern-based extraction with validation")
        return []

    def _validate_and_merge(self, people: List[Person], lines: List[str],
                           file_analysis: FileAnalysis) -> List[Person]:
        """
        Phase 4: Validate and merge extractions.
        """
        validator = JamaicaValidator()
        return validator.validate(people, lines, file_analysis)


class JamaicaPatternExtractor:
    """
    Jamaica-specific pattern extractor.

    Handles:
    - Role, Name, Salary format
    - Parish/Location-Name-Salary format
    - Qualification filtering
    - Complex list structures with semicolons
    - Salary ranges ("1,350l. to 1,500l.")
    """

    def __init__(self, github_base_url: str):
        self.github_base_url = github_base_url
        self.current_department = None
        self.current_parish = None
        self.last_role = None
        self.last_full_role = None
        self.stats = {
            'pattern1_extractions': 0,
            'pattern2_extractions': 0,
            'pattern3_extractions': 0,
            'location_name_pairs': 0,
            'list_extractions': 0
        }

    def extract(self, lines: List[str], file_analysis: FileAnalysis,
                colony: str, year: int) -> Tuple[List[Person], List[FlaggedSection]]:
        """Extract people using Jamaica-specific patterns."""

        people = []
        flagged = []

        start = file_analysis.people_section_start
        end = file_analysis.people_section_end

        for i in range(start, min(end, len(lines))):
            line = lines[i].strip()

            if not line:
                continue

            # Update context (department, parish, role headers)
            self._update_context(line, file_analysis)

            # Try to extract person(s)
            extracted = self._extract_from_line(line, i, colony, year, file_analysis)

            if extracted:
                people.extend(extracted)
            elif self._looks_like_people_data(line) and not self._is_section_header(line):
                # Flag for manual review
                flagged.append(FlaggedSection(
                    line_start=i,
                    line_end=i,
                    lines=[line],
                    reason="pattern_match_failed",
                    context={
                        'department': self.current_department,
                        'parish': self.current_parish,
                        'last_role': self.last_role
                    }
                ))

        return people, flagged

    def _update_context(self, line: str, file_analysis: FileAnalysis):
        """Update department/parish/role context."""
        # Check if this is a department header
        for dept in file_analysis.departments:
            if dept.lower() in line.lower() and len(line) < 100:
                self.current_department = dept
                return

        # Check if this is a parish marker
        for parish in file_analysis.parishes:
            if parish.lower() in line.lower():
                self.current_parish = parish
                return

        # Check if this is a role header
        if self._is_role_header(line) and len(line) > 10:
            role = line.strip().rstrip(',.:;')
            role = self._singularize_role(role)
            role = self._expand_ditto(role)
            self.last_full_role = role

    def _is_role_header(self, line: str) -> bool:
        """Check if line is a role header (section title)."""
        # Has salary? Not a header
        if re.search(r'\d+l\.', line):
            return False

        # Has obvious name pattern? Not a header
        if re.search(r'\b[A-Z]\.\s+[A-Z][a-z]+\b', line):
            return False

        # Contains multiple comma-separated items? Not a header
        if line.count(',') >= 3:
            return False

        # Short line with job-like words
        job_keywords = [
            'Assistant', 'Surveyor', 'Writer', 'Officer', 'Clerk', 'Surgeon',
            'Magistrate', 'Commissioner', 'Inspector', 'Collector', 'Agent',
            'Secretary', 'Treasurer', 'Auditor', 'Registrar', 'Governor',
            'Medical', 'Colonial', 'Civil', 'Principal', 'Deputy', 'Chief',
            'Superintendent', 'Director', 'Engineer', 'Architect', 'Rector',
            'Judge', 'Justice', 'Bishop', 'Archdeacon', 'Curate',
            'Comptroller', 'Receiver', 'Postmaster', 'Marshal'
        ]

        if any(kw.lower() in line.lower() for kw in job_keywords):
            return len(line) < 80 and line.count(',') <= 1

        return False

    def _singularize_role(self, role: str) -> str:
        """Convert plural role names to singular."""
        role = role.strip()
        for plural, singular in PLURAL_TO_SINGULAR_ROLES.items():
            if plural in role:
                role = role.replace(plural, singular)
        return role

    def _expand_ditto(self, role: str) -> str:
        """Expand 'ditto' references in role names."""
        if 'ditto' in role.lower() and self.last_role:
            prefix_match = re.match(r'^(Deputy|Second|Assistant|Third|Sub|Chief)\s+ditto', role, re.IGNORECASE)
            if prefix_match:
                prefix = prefix_match.group(1)
                return f"{prefix} {self.last_role}"
            if role.lower().strip() == 'ditto':
                return self.last_role
        return role

    def _extract_from_line(self, line: str, line_num: int,
                          colony: str, year: int,
                          file_analysis: FileAnalysis) -> List[Person]:
        """Extract person(s) from a line using Jamaica-specific patterns."""
        people = []

        # Pattern 1: Role, Name, Qualifications, Salary
        pattern1 = self._extract_pattern1(line, line_num, colony, year, file_analysis)
        if pattern1:
            people.extend(pattern1)
            return people

        # Pattern 2: Parish/Location, Name, Salary
        pattern2 = self._extract_location_name_salary(line, line_num, colony, year, file_analysis)
        if pattern2:
            people.extend(pattern2)
            return people

        # Pattern 3: Name, Salary (role from context)
        pattern3 = self._extract_name_salary(line, line_num, colony, year, file_analysis)
        if pattern3:
            people.extend(pattern3)
            return people

        # Pattern 4: Semicolon-separated list (Jamaica-specific)
        pattern4 = self._extract_semicolon_list(line, line_num, colony, year, file_analysis)
        if pattern4:
            people.extend(pattern4)
            return people

        # Pattern 5: Comma-separated name list
        pattern5 = self._extract_name_list(line, line_num, colony, year, file_analysis)
        if pattern5:
            people.extend(pattern5)
            return people

        return people

    def _extract_pattern1(self, line: str, line_num: int,
                         colony: str, year: int,
                         file_analysis: FileAnalysis) -> Optional[List[Person]]:
        """
        Pattern 1: Role, Name, [Qualifications,] Salary [to Salary]

        Examples:
        - "Colonial Secretary, The Hon. H. T. Irving, 1,500l."
        - "Chief Clerk, John C. Mack Glashan."
        - "Director, N. Roots, A.M.I.C.E., 500l. to 600l."
        """
        # Pattern with optional salary range
        pattern = r'^([A-Z][^,]{3,60}?),\s+([A-Z][^,]+?(?:\s+[A-Z][^,]*?)?),\s+(?:([A-Z][^,]+?),\s+)?(\d[\d,]*l\.?(?:\s+(?:to|by)\s+\d[\d,]*l\.?)?)?'

        match = re.search(pattern, line)
        if not match:
            return None

        potential_role = match.group(1).strip()
        name = match.group(2).strip()
        potential_qual = match.group(3).strip() if match.group(3) else None
        salary = match.group(4).strip() if match.group(4) else None

        # FIX: Check if group(2) is actually a location, not a name
        # Example: "Superintendent, Negril Point, J. S. Brownhill, 150l."
        # Should extract "J. S. Brownhill" as name, not "Negril Point"
        if name in JAMAICA_LOCATIONS and potential_qual:
            # Swap: group(2) is location, group(3) is actual name
            actual_location = name
            name = potential_qual
            potential_qual = None  # Already used as name
            # Update parish if we found a specific location
            if actual_location in JAMAICA_PARISHES:
                self.current_parish = actual_location

        # Check if "role" is actually a location
        if potential_role in JAMAICA_LOCATIONS:
            return None  # Will be handled by location-name pattern

        # Check if "role" is actually a qualification
        if potential_role in JAMAICA_QUALIFICATIONS:
            return None

        # Check if "role" is actually a person's name (from previous line)
        if re.match(r'^[A-Z]\.\s+[A-Z][a-z]+$', potential_role):
            return None

        # Check if potential_qual is actually a qualification (not a name)
        qualifications = None
        if potential_qual:
            # Common qualification patterns
            if any(qual in potential_qual for qual in JAMAICA_QUALIFICATIONS):
                qualifications = potential_qual
                potential_qual = None
            elif re.match(r'^[A-Z]\.?(?:\s*[A-Z]\.?)+$', potential_qual):
                # Looks like initials, keep as part of qualifications
                qualifications = potential_qual
                potential_qual = None

        # Clean up name
        name = self._clean_name(name)

        # Skip if name looks invalid
        if not self._is_valid_name(name):
            return None

        # Skip vacant positions
        if 'vacant' in name.lower():
            return None

        # Store role for context
        self.last_role = potential_role

        person = Person(
            name=name,
            role=potential_role,
            location=self.current_parish or "Jamaica",
            colony=colony,
            year=year,
            department=self.current_department,
            parish=self.current_parish,
            salary=salary,
            qualifications=qualifications,
            full_string=line,
            source_file=file_analysis.file_path,
            line_number=line_num,
            confidence=0.9,
            extraction_method="pattern1_role_name_salary"
        )

        self.stats['pattern1_extractions'] += 1
        return [person]

    def _extract_location_name_salary(self, line: str, line_num: int,
                                     colony: str, year: int,
                                     file_analysis: FileAnalysis) -> Optional[List[Person]]:
        """
        Pattern 2: Parish/Location, Name, Salary

        Examples:
        - "Falmouth, J. S. Buckingham, 400l."
        - "Kingston, M. Laidman, 300l."
        """
        # Check if line starts with a known location
        parts = line.split(',')
        if len(parts) < 2:
            return None

        potential_location = parts[0].strip()
        if potential_location not in JAMAICA_LOCATIONS:
            return None

        # Extract name and salary from remaining parts
        pattern = r'([A-Z][^,]+?),\s+(\d[\d,]*l\.?(?:\s+(?:to|by)\s+\d[\d,]*l\.?)?)?'
        rest = ','.join(parts[1:])
        match = re.search(pattern, rest)

        if not match:
            return None

        name = match.group(1).strip()
        salary = match.group(2).strip() if match.group(2) else None

        name = self._clean_name(name)

        if not self._is_valid_name(name):
            return None

        if 'vacant' in name.lower():
            return None

        # FIX: Use last_role from context, but mark as location-based if uncertain
        # If last_role looks like a location (not a role), use conservative default
        role = self.last_role if self.last_role else "Officer (location-based)"
        if role and role in JAMAICA_LOCATIONS:
            role = "Officer (location-based)"

        person = Person(
            name=name,
            role=role,
            location=potential_location,
            colony=colony,
            year=year,
            department=self.current_department,
            parish=potential_location if potential_location in JAMAICA_PARISHES else self.current_parish,
            salary=salary,
            full_string=line,
            source_file=file_analysis.file_path,
            line_number=line_num,
            confidence=0.85,
            extraction_method="pattern2_location_name_salary"
        )

        self.stats['pattern2_extractions'] += 1
        self.stats['location_name_pairs'] += 1
        return [person]

    def _extract_name_salary(self, line: str, line_num: int,
                            colony: str, year: int,
                            file_analysis: FileAnalysis) -> Optional[List[Person]]:
        """
        Pattern 3: Name, Salary (role from context)

        Examples:
        - "J. Winzer, 650l." (under a role header)
        - "W. J. E. Hall."
        """
        if not self.last_role:
            return None

        # Pattern: Name, optional salary
        pattern = r'^([A-Z][^,]+?),?\s+(\d[\d,]*l\.?(?:\s+(?:to|by)\s+\d[\d,]*l\.?)?)?\.?$'
        match = re.search(pattern, line)

        if not match:
            return None

        name = match.group(1).strip()
        salary = match.group(2).strip() if match.group(2) else None

        name = self._clean_name(name)

        if not self._is_valid_name(name):
            return None

        if 'vacant' in name.lower():
            return None

        person = Person(
            name=name,
            role=self.last_role,
            location=self.current_parish or "Jamaica",
            colony=colony,
            year=year,
            department=self.current_department,
            parish=self.current_parish,
            salary=salary,
            full_string=line,
            source_file=file_analysis.file_path,
            line_number=line_num,
            confidence=0.80,
            extraction_method="pattern3_name_salary_context"
        )

        self.stats['pattern3_extractions'] += 1
        return [person]

    def _extract_semicolon_list(self, line: str, line_num: int,
                                colony: str, year: int,
                                file_analysis: FileAnalysis) -> Optional[List[Person]]:
        """
        Pattern 4: Semicolon-separated list (Jamaica-specific)

        Examples:
        - "J. Parry, 600l.; F. Dawson, 600l."
        - "A. Nairn, 350l.; J. Palache, 180l.; T. P. Hart, 200l."
        """
        if ';' not in line:
            return None

        # FIX: Reject non-person sections (hurricanes, climate descriptions, etc.)
        MONTH_NAMES = {'January', 'February', 'March', 'April', 'May', 'June',
                      'July', 'August', 'September', 'October', 'November', 'December'}
        line_words = set(re.findall(r'\b[A-Z][a-z]+\b', line))
        if line_words & MONTH_NAMES:
            return None  # Likely climate/hurricane section

        # Check for descriptive keywords
        DESCRIPTIVE_KEYWORDS = ['occurred', 'hurricanes', 'principal', 'island',
                               'climate', 'temperature', 'rainfall', 'recent']
        if any(kw in line.lower() for kw in DESCRIPTIVE_KEYWORDS):
            return None  # Descriptive text

        if not self.last_role:
            return None

        people = []
        entries = line.split(';')

        for entry in entries:
            entry = entry.strip()
            if not entry:
                continue

            # Try to extract Name, Salary
            pattern = r'([A-Z][^,]+?),\s+(\d[\d,]*l\.?(?:\s+(?:to|by)\s+\d[\d,]*l\.?)?)?'
            match = re.search(pattern, entry)

            if not match:
                continue

            name = match.group(1).strip()
            salary = match.group(2).strip() if match.group(2) else None

            name = self._clean_name(name)

            if not self._is_valid_name(name):
                continue

            if 'vacant' in name.lower():
                continue

            person = Person(
                name=name,
                role=self.last_role,
                location=self.current_parish or "Jamaica",
                colony=colony,
                year=year,
                department=self.current_department,
                parish=self.current_parish,
                salary=salary,
                full_string=line,
                source_file=file_analysis.file_path,
                line_number=line_num,
                confidence=0.85,
                extraction_method="pattern4_semicolon_list"
            )

            people.append(person)

        if people:
            self.stats['list_extractions'] += 1

        return people if people else None

    def _extract_name_list(self, line: str, line_num: int,
                          colony: str, year: int,
                          file_analysis: FileAnalysis) -> Optional[List[Person]]:
        """
        Pattern 5: Comma-separated name list (without salaries)

        Examples:
        - "R. Chamberlaine. H. Kent."
        - "D. Ewart. R. Hill."
        """
        if not self.last_role:
            return None

        # Check if line looks like a list of names (multiple short names separated by periods or commas)
        # Pattern: Name. Name. Name. (captures ALL initials, not just last one)
        # FIX: Changed from ([A-Z]\.\s*[A-Z][a-z]+) to capture W. B. Mais, not just B. Mais
        names = re.findall(r'([A-Z](?:\.\s*[A-Z])*\.\s*[A-Z][a-z]+)', line)

        if len(names) < 2:
            return None

        people = []
        for name in names:
            name = self._clean_name(name)

            if not self._is_valid_name(name):
                continue

            person = Person(
                name=name,
                role=self.last_role,
                location=self.current_parish or "Jamaica",
                colony=colony,
                year=year,
                department=self.current_department,
                parish=self.current_parish,
                salary=None,
                full_string=line,
                source_file=file_analysis.file_path,
                line_number=line_num,
                confidence=0.75,
                extraction_method="pattern5_name_list"
            )

            people.append(person)

        if people:
            self.stats['list_extractions'] += 1

        return people if people else None

    def _clean_name(self, name: str) -> str:
        """Clean and normalize a person's name."""
        # Remove honorifics
        name = re.sub(r'\b(The Hon\.|Hon\.|Rev\.|Dr\.|Sir|Major-Gen\.|Lieut\.|Lt\.-Col\.|Colonel|Capt\.|Captain|Major|Rt\. Rev\.|Archdeacon|Bishop)\s*', '', name)

        # Remove trailing qualifications
        for qual in JAMAICA_QUALIFICATIONS:
            name = name.replace(f', {qual}', '').replace(f' {qual}', '')

        # Remove trailing periods and commas
        name = name.rstrip('.,;:')

        return name.strip()

    def _is_valid_name(self, name: str) -> bool:
        """Check if string looks like a valid person's name."""
        if not name or len(name) < 2:
            return False

        # Must start with capital letter
        if not name[0].isupper():
            return False

        # Reject if all uppercase (likely a header)
        if name.isupper() and len(name) > 3:
            return False

        # Must contain at least one letter
        if not re.search(r'[A-Za-z]', name):
            return False

        # Reject common non-name patterns
        invalid_patterns = [
            r'^\d+$',  # Just numbers
            r'^[IVX]+$',  # Roman numerals alone
            r'^(vacant)$',  # Vacant
            r'^(and)$',  # Conjunction
        ]

        for pattern in invalid_patterns:
            if re.match(pattern, name, re.IGNORECASE):
                return False

        return True

    def _looks_like_people_data(self, line: str) -> bool:
        """Check if line might contain people data."""
        # Has a name pattern and/or salary
        has_name = bool(re.search(r'\b[A-Z]\.\s+[A-Z][a-z]+\b', line))
        has_salary = bool(re.search(r'\d+l\.', line))
        has_role_keyword = bool(re.search(
            r'\b(Secretary|Clerk|Officer|Inspector|Agent|Surveyor|Engineer|Magistrate|Rector|Judge)\b',
            line, re.IGNORECASE
        ))

        return has_name or (has_salary and has_role_keyword)

    def _is_section_header(self, line: str) -> bool:
        """Check if line is a section header."""
        # All caps or markdown headers
        if line.isupper() or line.startswith('#'):
            return True

        # Common section headers
        section_patterns = [
            r'^[A-Z][a-z]+\s+Establishment\.?$',
            r'^[A-Z][a-z]+\s+Department\.?$',
            r'^Governors?\.?$',
            r'^Population\.?$',
            r'^History\.?$',
        ]

        for pattern in section_patterns:
            if re.match(pattern, line):
                return True

        return False


class JamaicaValidator:
    """Validator for Jamaica extractions."""

    def __init__(self):
        self.stats = {
            'locations_filtered': 0,
            'qualifications_filtered': 0,
            'names_filtered': 0,
            'vacant_positions': 0,
            'parishes_detected': 0
        }

    def validate(self, people: List[Person], lines: List[str],
                file_analysis: FileAnalysis) -> List[Person]:
        """Validate and filter extracted people."""
        validated = []
        seen_names = set()

        for person in people:
            # Filter 1: Check if role is actually a location
            if person.role in JAMAICA_LOCATIONS:
                self.stats['locations_filtered'] += 1
                continue

            # Filter 2: Check if role is actually a qualification
            if person.role in JAMAICA_QUALIFICATIONS:
                self.stats['qualifications_filtered'] += 1
                continue

            # Filter 3: Check if name is actually a role
            if person.name in JAMAICA_QUALIFICATIONS:
                self.stats['qualifications_filtered'] += 1
                continue

            # Filter 4: Check if name looks like a location
            if person.name in JAMAICA_LOCATIONS:
                self.stats['locations_filtered'] += 1
                continue

            # Filter 5: Skip vacant positions
            if 'vacant' in person.name.lower() or 'vacant' in person.role.lower():
                self.stats['vacant_positions'] += 1
                continue

            # Filter 6: Deduplicate by name+role+year
            key = f"{person.name}|{person.role}|{person.year}"
            if key in seen_names:
                continue
            seen_names.add(key)

            # Count parishes
            if person.parish and person.parish in JAMAICA_PARISHES:
                self.stats['parishes_detected'] += 1

            validated.append(person)

        return validated


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Extract people from Jamaica Colonial Office Lists')
    parser.add_argument('--year', type=int, help='Year to process (e.g., 1867)')
    parser.add_argument('--test', action='store_true', help='Run test extraction on 1867')
    parser.add_argument('--output', type=str, help='Output JSON file path')

    args = parser.parse_args()

    if args.test or not args.year:
        # Default test: extract 1867
        year = 1867
        file_path = f"/home/user/colonial_office_list/output_3/{year}_manual_parsed/jamaica.txt"
        output_path = f"/home/user/colonial_office_list/jamaica_{year}_test.json"
    else:
        year = args.year
        file_path = f"/home/user/colonial_office_list/output_3/{year}_manual_parsed/jamaica.txt"
        output_path = args.output or f"/home/user/colonial_office_list/jamaica_{year}_extracted.json"

    # Check if file exists
    if not os.path.exists(file_path):
        print(f"ERROR: File not found: {file_path}")
        return

    # Extract
    orchestrator = JamaicaExtractionOrchestrator()
    people, metadata = orchestrator.extract_from_file(file_path, "Jamaica", year)

    # Save results
    output = {
        'metadata': metadata,
        'people': [asdict(p) for p in people],
        'summary': {
            'total_people': len(people),
            'year': year,
            'colony': 'Jamaica',
            'extraction_date': datetime.now().isoformat()
        }
    }

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    print(f"\n{'='*70}")
    print(f"Extraction complete!")
    print(f"  Total people extracted: {len(people)}")
    print(f"  Output saved to: {output_path}")
    print('='*70)

    # Print sample records
    print("\nSample records:")
    for i, person in enumerate(people[:10]):
        print(f"\n{i+1}. {person.name}")
        print(f"   Role: {person.role}")
        print(f"   Location: {person.location}")
        if person.parish:
            print(f"   Parish: {person.parish}")
        if person.department:
            print(f"   Department: {person.department}")
        if person.salary:
            print(f"   Salary: {person.salary}")


if __name__ == '__main__':
    main()
