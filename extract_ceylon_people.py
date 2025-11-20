#!/usr/bin/env python3
"""
Colonial Office List - Ceylon People Extraction System (Specialized V3)

Specialized extractor designed to fix quality issues in the generic v2 system.

Ceylon-Specific Challenges:
1. Location-as-role errors (20 instances in v2): "Kandy, T. Berwick, 400l."
   - Solution: Ceylon location dictionary + pattern detection

2. Name-as-role errors (14 instances): Person names from previous lines
   - Solution: Name pattern detection + better context tracking

3. Qualification-as-role errors (4 instances): "Assoc. Inst. C.E."
   - Solution: Qualification dictionary + filtering

4. Complex list structures with semi-colons and location prefixes
   - Solution: Smart list parsing with location awareness

Target: 90-95% accuracy (from current 57/100 quality score)

Architecture based on: extract_fiji_people.py (proven 100/100 quality)

Usage:
    python extract_ceylon_people.py --year 1867
    python extract_ceylon_people.py --test
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
    province: Optional[str] = None
    salary: Optional[str] = None
    full_string: str = ""
    source_file: str = ""
    line_number: int = 0
    confidence: float = 0.0
    extraction_method: str = "unknown"
    notes: str = ""
    qualifications: Optional[str] = None  # Ceylon-specific: track qualifications


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
    provinces: List[str] = field(default_factory=list)
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


# Ceylon-specific constants
CEYLON_LOCATIONS = {
    # Major cities
    'Colombo', 'Kandy', 'Galle', 'Jaffna', 'Trincomalee', 'Batticaloa',
    'Matara', 'Nuwara Eliya', 'Badulla', 'Kurunegala', 'Ratnapura',
    'Anuradhapura', 'Hambantota', 'Kalutara', 'Negombo', 'Chilaw',
    'Puttalam', 'Mannar', 'Vavuniya', 'Mullaittivu', 'Kilinochchi', 'Ampara',

    # Districts and regions from source
    'Karnegalle', 'Ratnapoora', 'Matelle', 'Dambool', 'Keigalle', 'Avishavelle',
    'Gamoola', 'Pantura', 'Harispattu', 'Dumbera', 'Cultura', 'Tangalle',
    'Matura', 'Humbantotte', 'Ballepittymodere', 'Nunnerakalawila',
    'Point Pedro', 'Chavagacherry', 'Cayts', 'Calpentyn', 'Mullitivoo',
    'Morottoo', 'St. John\'s River', 'Nuwera Ellia',

    # Combined locations
    'Matelle and Dambool', 'Keigalle and Avishavelle', 'Upper and Lower Dumbera',
    'Kandy Districts', 'Western Province', 'Southern Province', 'Central Province',
    'Northern Province', 'Eastern Province', 'North-Western Province',
    'North-Central Province', 'Uva Province', 'Sabaragamuwa Province'
}

CEYLON_PROVINCES = [
    'Western Province', 'Southern Province', 'Central Province',
    'Northern Province', 'Eastern Province', 'North-Western Province',
    'North-Central Province', 'Uva Province', 'Sabaragamuwa Province'
]

CEYLON_DEPARTMENTS = [
    'Civil Establishment', 'Colonial Secretary\'s Office', 'Treasurer\'s Department',
    'Audit Office', 'Surveyor General\'s Department', 'Customs Department',
    'Medical Department', 'Judicial Department', 'Police Department',
    'Education Department', 'Public Works Department', 'Railway Department',
    'Postal Department', 'Telegraph Department'
]

# Qualifications that are NOT roles
CEYLON_QUALIFICATIONS = {
    'M.D.', 'M.R.C.S.', 'M.R.C.S.E.', 'F.R.C.S.', 'F.R.C.S. Edin.',
    'M. Inst. C.E.', 'M.I.C.E.', 'Assoc. Inst. C.E.', 'A.M.I.C.E.',
    'B.A.', 'M.A.', 'LL.D.', 'LL.B.', 'Q.C.', 'K.C.',
    'C.M.G.', 'K.C.M.G.', 'C.B.', 'K.C.B.',
    'R.E.', 'R.N.', 'C.M.', 'M. Insl. C.E.'
}

# Plural-to-Singular role mappings for normalization
PLURAL_TO_SINGULAR_ROLES = {
    # Explicit mappings for Ceylon-specific roles
    'Superintending Officers': 'Superintending Officer',
    'Assistant Colonial Surgeons': 'Assistant Colonial Surgeon',
    'Colonial Surgeons': 'Colonial Surgeon',
    'Assistant Surveyors': 'Assistant Surveyor',
    'Surveyors': 'Surveyor',
    'Government Agents': 'Government Agent',
    'Medical Assistants': 'Medical Assistant',
    'Draftsmen and Estimates': 'Draftsman',  # Special case
    'Writers': 'Writer',
    'Officers': 'Officer',
    'Assistants': 'Assistant',
    'Agents': 'Agent',
    'Clerks': 'Clerk',
    'Inspectors': 'Inspector',
}


class CeylonExtractionOrchestrator:
    """Main orchestrator for Ceylon specialized extraction."""

    def __init__(self, github_base_url: str = "https://github.com/jburnford/colonial_office_list/blob/main"):
        self.github_base_url = github_base_url
        self.analysis_cache = {}

    def extract_from_file(self, file_path: str, colony: str, year: int, use_cache: bool = True) -> Tuple[List[Person], Dict]:
        """
        Extract all people from a single file using specialized Ceylon approach.

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
            'ceylon_specific': {
                'locations_filtered': 0,
                'qualifications_filtered': 0,
                'names_filtered': 0,
                'vacant_positions': 0
            }
        }

        # PHASE 1: File Analysis
        print("\nPHASE 1: Analyzing file structure...")
        file_analysis = self._analyze_file_structure(lines, colony, year, file_path, use_cache)
        metadata['phases']['analysis'] = {
            'people_section': f"lines {file_analysis.people_section_start}-{file_analysis.people_section_end}",
            'departments': len(file_analysis.departments),
            'provinces': len(file_analysis.provinces)
        }

        # PHASE 2: Pattern-based extraction (Python)
        print("\nPHASE 2: Pattern-based extraction (Ceylon-specific)...")
        pattern_extractor = CeylonPatternExtractor(self.github_base_url)
        preliminary, flagged = pattern_extractor.extract(
            lines, file_analysis, colony, year
        )
        print(f"  Extracted {len(preliminary)} people via patterns")
        print(f"  Flagged {len(flagged)} sections for manual review")

        metadata['phases']['pattern_extraction'] = {
            'extracted': len(preliminary),
            'flagged_sections': len(flagged)
        }

        # PHASE 3: LLM extraction DISABLED (0-5% accuracy in v2)
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

        # Update Ceylon-specific stats from validator
        validator = CeylonValidator()
        metadata['ceylon_specific'] = validator.stats

        metadata['phases']['validation'] = {
            'total': len(validated),
            'avg_confidence': sum(p.confidence for p in validated) / len(validated) if validated else 0,
            'filtered_out': len(all_people) - len(validated)
        }

        return validated, metadata

    def _analyze_file_structure(self, lines: List[str], colony: str, year: int,
                                file_path: str, use_cache: bool) -> FileAnalysis:
        """
        Phase 1: Analyze file structure for Ceylon.
        """
        # Find people section - look for "Civil Establishment"
        start_idx = -1
        for i, line in enumerate(lines):
            if re.search(r'Civil Establishment', line, re.IGNORECASE):
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

        # Detect departments and provinces
        departments = set()
        provinces = set()

        for line in lines[start_idx:]:
            # Check for known Ceylon departments
            for dept in CEYLON_DEPARTMENTS:
                if dept.lower() in line.lower():
                    departments.add(dept)

            # Check for known Ceylon provinces
            for prov in CEYLON_PROVINCES:
                if prov.lower() in line.lower():
                    provinces.add(prov)

        return FileAnalysis(
            file_path=file_path,
            colony=colony,
            year=year,
            people_section_start=start_idx,
            people_section_end=len(lines),
            start_marker="Civil Establishment (detected)",
            departments=sorted(list(departments))[:30],
            provinces=sorted(list(provinces)),
            primary_format="Role, Name, Salary (with location variations)",
            has_lists=True,
            has_ditto=True,
            salary_currency="£ sterling",
            ocr_quality="good"
        )

    def _llm_extract_flagged(self, flagged: List[FlaggedSection],
                            file_analysis: FileAnalysis,
                            lines: List[str]) -> List[Person]:
        """
        Phase 3: LLM extraction - DISABLED for Ceylon due to poor accuracy.

        V2 Results:
        - task_pattern_extraction: ~95% error rate
        - task_list_extraction: 100% error rate

        Solution: Rely only on pattern extraction with Ceylon-specific filters.
        """
        print("  Task-based extraction DISABLED (0-5% accuracy in v2)")
        print("  Relying on pattern-based extraction with validation")
        return []

    def _validate_and_merge(self, people: List[Person], lines: List[str],
                           file_analysis: FileAnalysis) -> List[Person]:
        """
        Phase 4: Validate and merge extractions.
        """
        validator = CeylonValidator()
        return validator.validate(people, lines, file_analysis)


class CeylonPatternExtractor:
    """
    Ceylon-specific pattern extractor.

    Handles:
    - Location-Name-Salary format
    - Qualification filtering
    - Name pattern detection
    - Complex list structures
    """

    def __init__(self, github_base_url: str):
        self.github_base_url = github_base_url
        self.current_department = None
        self.current_province = None
        self.last_role = None
        self.last_full_role = None  # Track full role for context
        self.stats = {
            'pattern1_extractions': 0,
            'pattern2_extractions': 0,
            'pattern3_extractions': 0,
            'location_name_pairs': 0,
            'list_extractions': 0
        }

    def extract(self, lines: List[str], file_analysis: FileAnalysis,
                colony: str, year: int) -> Tuple[List[Person], List[FlaggedSection]]:
        """Extract people using Ceylon-specific patterns."""

        people = []
        flagged = []

        start = file_analysis.people_section_start
        end = file_analysis.people_section_end

        for i in range(start, min(end, len(lines))):
            line = lines[i].strip()

            if not line:
                continue

            # Update context (department, province, role headers)
            self._update_context(line, file_analysis)

            # Try to extract person(s)
            extracted = self._extract_from_line(line, i, colony, year, file_analysis)

            if extracted:
                people.extend(extracted)
            elif self._looks_like_people_data(line) and not self._is_section_header(line):
                # Flag for manual review (not LLM - just for reporting)
                flagged.append(FlaggedSection(
                    line_start=i,
                    line_end=i,
                    lines=[line],
                    reason="pattern_match_failed",
                    context={
                        'department': self.current_department,
                        'province': self.current_province,
                        'last_role': self.last_role
                    }
                ))

        return people, flagged

    def _update_context(self, line: str, file_analysis: FileAnalysis):
        """Update department/province/role context."""
        # Check if this is a department header
        for dept in file_analysis.departments:
            if dept.lower() in line.lower() and len(line) < 100:
                self.current_department = dept
                return

        # Check if this is a province marker
        for prov in file_analysis.provinces:
            if prov.lower() in line.lower():
                self.current_province = prov
                return

        # Check if this is a role header (section header without salary)
        # e.g., "Assistant Surveyors", "Writers", "Medical Assistant"
        # BUT: Skip if it's a standalone role without a name (orphaned header)
        if self._is_role_header(line) and len(line) > 10:
            # Clean up plural forms
            role = line.strip().rstrip(',.:;')
            # Convert plural to singular for consistency
            role = self._singularize_role(role)
            # Expand "ditto" if present
            role = self._expand_ditto(role)
            self.last_full_role = role

    def _is_role_header(self, line: str) -> bool:
        """
        Check if line is a role header (section title).

        Role headers are lines that:
        - Don't have salaries
        - Don't have obvious name patterns
        - Are typically job titles
        """
        # Has salary? Not a header
        if re.search(r'\d+l\.', line):
            return False

        # Has obvious name pattern (Initial. Surname)? Not a header
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
            'Superintendent', 'Director', 'Engineer', 'Architect'
        ]

        if any(kw.lower() in line.lower() for kw in job_keywords):
            # Probably a role header
            return len(line) < 80 and line.count(',') <= 1

        return False

    def _singularize_role(self, role: str) -> str:
        """Convert plural role names to singular."""
        # Simple rule-based singularization
        role = role.strip()

        # Special cases
        if role == 'Writers':
            return 'Writer'
        if role.endswith('Surveyors'):
            return role.replace('Surveyors', 'Surveyor')
        if role.endswith('Assistants'):
            return role.replace('Assistants', 'Assistant')
        if role.endswith('Officers'):
            return role.replace('Officers', 'Officer')

        return role

    def _expand_ditto(self, role: str) -> str:
        """Expand 'ditto' references in role names."""
        # If role contains "ditto" and we have a previous role, expand it
        if 'ditto' in role.lower() and self.last_role:
            # "Second ditto" -> "Second <last_role>"
            # "Deputy ditto" -> "Deputy <last_role>"
            # "Assistant ditto" -> "Assistant <last_role>"

            # Extract prefix (e.g., "Deputy", "Second", "Assistant")
            prefix_match = re.match(r'^(Deputy|Second|Assistant|Third)\s+ditto', role, re.IGNORECASE)
            if prefix_match:
                prefix = prefix_match.group(1)
                return f"{prefix} {self.last_role}"

            # Just "ditto" alone -> use last_role
            if role.lower().strip() == 'ditto':
                return self.last_role

        return role

    def _extract_from_line(self, line: str, line_num: int,
                          colony: str, year: int,
                          file_analysis: FileAnalysis) -> List[Person]:
        """
        Extract person(s) from a line using Ceylon-specific patterns.
        """
        people = []

        # Pattern 1: Role, Name, Qualifications, Salary
        # e.g., "Office Assistant, J. A. Caley, M. Inst. C.E., 750l."
        pattern1 = self._extract_pattern1(line, line_num, colony, year, file_analysis)
        if pattern1:
            people.extend(pattern1)
            return people

        # Pattern 2: Location, Name, Salary (location-name pairs)
        # e.g., "Kandy, T. Berwick, 400l."
        pattern2 = self._extract_location_name_salary(line, line_num, colony, year, file_analysis)
        if pattern2:
            people.extend(pattern2)
            return people

        # Pattern 3: Name, Salary (role from context)
        # e.g., "J. Winzer, 650l." (under "Assistant Surveyors" header)
        pattern3 = self._extract_name_salary(line, line_num, colony, year, file_analysis)
        if pattern3:
            people.extend(pattern3)
            return people

        # Pattern 4: Comma-separated name list
        # e.g., "L. F. Lee, Æ. King, G. W. Templer, R. Massie,"
        pattern4 = self._extract_name_list(line, line_num, colony, year, file_analysis)
        if pattern4:
            people.extend(pattern4)
            return people

        return people

    def _extract_pattern1(self, line: str, line_num: int,
                         colony: str, year: int,
                         file_analysis: FileAnalysis) -> Optional[List[Person]]:
        """
        Pattern 1: Role, Name, [Qualifications,] Salary

        Examples:
        - "Colonial Secretary, W. G. Gibson, 2,000l."
        - "Office Assistant, J. A. Caley, M. Inst. C.E., 750l."
        - "Private Secretary, H. C. Stewart, 300l."
        """
        # Pattern: Role, Name, possibly qualifications, Salary
        # Role must start with capital, be at least 4 chars, and not be a location
        # Salary pattern handles: 750l., 2,000l., Rs. 1000, etc.
        pattern = r'^([A-Z][^,]{3,60}?),\s+([A-Z][^,]+?),\s+(?:([A-Z][^,]+?),\s+)?(\d[\d,]*l\.?|Rs\.?\s*\d+)'

        match = re.search(pattern, line)
        if not match:
            return None

        potential_role = match.group(1).strip()
        name = match.group(2).strip()
        potential_qual = match.group(3).strip() if match.group(3) else None
        salary = match.group(4).strip()

        # Check if "role" is actually a location
        if potential_role in CEYLON_LOCATIONS:
            return None  # Will be handled by location-name pattern

        # Check if "role" looks like a person name (e.g., "J. L. Vanderstraaten")
        if self._looks_like_name(potential_role):
            return None

        # Check if potential_qual is actually a qualification
        qualifications = None
        role = potential_role

        if potential_qual:
            if potential_qual in CEYLON_QUALIFICATIONS or self._looks_like_qualification(potential_qual):
                # It's a qualification, not part of the name
                qualifications = potential_qual
            else:
                # It might be part of a longer name or role, skip this pattern
                return None

        # Extract any qualifications embedded in the name
        name_cleaned, name_quals = self._extract_qualifications_from_name(name)
        if name_quals:
            qualifications = name_quals if not qualifications else f"{qualifications}, {name_quals}"
            name = name_cleaned

        # Expand "ditto" in role if present
        role = self._expand_ditto(role)

        # Create person
        person = self._create_person(
            name,
            role,
            salary,
            line, line_num, colony, year,
            confidence=0.9,
            method='ceylon_pattern1',
            qualifications=qualifications
        )

        self.stats['pattern1_extractions'] += 1
        # Update last_role for context (store base role for ditto expansion)
        # Extract the base role (last significant word or phrase)
        if 'deputy' in role.lower() or 'second' in role.lower() or 'assistant' in role.lower():
            # For "Deputy Queen's Advocate", store "Queen's Advocate"
            # For "Second Colonial Secretary", store "Colonial Secretary"
            parts = role.split(maxsplit=1)
            if len(parts) == 2:
                self.last_role = parts[1]
            else:
                self.last_role = role
        else:
            self.last_role = role

        return [person]

    def _extract_location_name_salary(self, line: str, line_num: int,
                                      colony: str, year: int,
                                      file_analysis: FileAnalysis) -> Optional[List[Person]]:
        """
        Pattern 2: Location, Name, Salary

        Examples:
        - "Kandy, T. Berwick, 400l."
        - "Galle, O. W. C. Morgan, 400l."
        - "Matelle and Dambool, J. A. H. De Saram, 450l."

        Key: First element is a known location, use last_full_role as the actual role.
        """
        # Pattern: Location, Name, Salary
        # Salary pattern handles: 750l., 2,000l., Rs. 1000, etc.
        pattern = r'^([^,]+?),\s+([A-Z][^,]+?),\s+(\d[\d,]*l\.?|Rs\.?\s*\d+)'

        match = re.search(pattern, line)
        if not match:
            return None

        potential_location = match.group(1).strip()
        name = match.group(2).strip()
        salary = match.group(3).strip()

        # Must be a known location
        if potential_location not in CEYLON_LOCATIONS:
            # Check partial matches (e.g., "Upper and Lower Dumbera" contains "Dumbera")
            is_location = False
            for loc in CEYLON_LOCATIONS:
                if loc.lower() in potential_location.lower() or potential_location.lower() in loc.lower():
                    is_location = True
                    break
            if not is_location:
                return None

        # Name should look like a name
        if not self._looks_like_name(name):
            return None

        # Use last_full_role as the role (from section header)
        role = self.last_full_role if self.last_full_role else self.last_role
        if not role:
            role = "Unknown"

        # Expand "ditto" in role if present
        role = self._expand_ditto(role)

        # Create person with location info
        person = self._create_person(
            name,
            role,
            salary,
            line, line_num, colony, year,
            confidence=0.85,
            method='ceylon_location_name',
            notes=f"Location: {potential_location}"
        )

        # Override location with specific location
        person.location = f"{colony} - {potential_location}"

        self.stats['location_name_pairs'] += 1

        return [person]

    def _extract_name_salary(self, line: str, line_num: int,
                            colony: str, year: int,
                            file_analysis: FileAnalysis) -> Optional[List[Person]]:
        """
        Pattern 3: Name, Salary (role from context)

        Examples:
        - "J. Winzer, 650l."
        - "E. Dalton, 400l."

        Used when there's a section header like "Assistant Surveyors" above.
        """
        # Pattern: Name, Salary
        # Salary pattern handles: 750l., 2,000l., Rs. 1000, etc.
        pattern = r'^([A-Z][^,]{2,40}?),\s+(\d[\d,]*l\.?|Rs\.?\s*\d+)'

        match = re.search(pattern, line)
        if not match:
            return None

        name = match.group(1).strip()
        salary = match.group(2).strip()

        # Name must look like a name
        if not self._looks_like_name(name):
            return None

        # Must have a role from context
        role = self.last_full_role if self.last_full_role else self.last_role
        if not role or role == "Unknown":
            # Low confidence without context
            role = "Unknown"
            confidence = 0.5
        else:
            confidence = 0.75

        # Expand "ditto" in role if present
        role = self._expand_ditto(role)

        # Extract qualifications from name if present
        name_cleaned, qualifications = self._extract_qualifications_from_name(name)

        # Create person
        person = self._create_person(
            name_cleaned,
            role,
            salary,
            line, line_num, colony, year,
            confidence=confidence,
            method='ceylon_name_salary',
            qualifications=qualifications
        )

        self.stats['pattern3_extractions'] += 1

        return [person]

    def _extract_name_list(self, line: str, line_num: int,
                          colony: str, year: int,
                          file_analysis: FileAnalysis) -> Optional[List[Person]]:
        """
        Pattern 4: Comma-separated name list

        Examples:
        - "L. F. Lee, Æ. King, G. W. Templer, R. Massie,"
        - "J. W. Gibson, A. Mainwaring, A. Jumeaux."

        Used for lists under a section header with no individual salaries.
        """
        # Only process if we have a valid role from context
        if not self.last_full_role and not self.last_role:
            return None

        # Line should have multiple names separated by commas
        # Must NOT have salary indicators
        if re.search(r'\d+l\.', line):
            return None  # Has salary, use other patterns

        # Split by commas and look for name-like patterns
        parts = [p.strip() for p in line.split(',')]

        # Filter to likely names (at least 2 chars, starts with capital)
        names = []
        for part in parts:
            if len(part) >= 2 and part[0].isupper():
                # Clean up trailing punctuation
                part = part.rstrip('.,;:')
                if self._looks_like_name(part):
                    names.append(part)

        # Need at least 2 names to consider this a list
        if len(names) < 2:
            return None

        # Create person records for each name
        people = []
        role = self.last_full_role if self.last_full_role else self.last_role

        # Expand "ditto" in role if present
        role = self._expand_ditto(role)

        for name in names:
            person = self._create_person(
                name,
                role,
                None,  # No salary in list
                line, line_num, colony, year,
                confidence=0.7,
                method='ceylon_name_list'
            )
            people.append(person)

        self.stats['list_extractions'] += len(people)

        return people if people else None

    def _extract_qualifications_from_name(self, name: str) -> Tuple[str, Optional[str]]:
        """
        Extract qualifications embedded in name field.

        Returns: (cleaned_name, qualifications)
        """
        qualifications = []
        remaining_parts = []

        # Split by commas
        parts = [p.strip() for p in name.split(',')]

        for part in parts:
            if part in CEYLON_QUALIFICATIONS or self._looks_like_qualification(part):
                qualifications.append(part)
            else:
                remaining_parts.append(part)

        cleaned_name = ', '.join(remaining_parts) if remaining_parts else name
        quals_str = ', '.join(qualifications) if qualifications else None

        return cleaned_name, quals_str

    def _looks_like_qualification(self, text: str) -> bool:
        """Check if text looks like a professional qualification."""
        # Pattern: Abbrev. Abbrev. (e.g., "M.D.", "B.A.")
        if re.match(r'^[A-Z]\.[A-Z]\.', text):
            return True

        # Pattern: Multiple capitals with periods
        if re.match(r'^[A-Z\.]+$', text) and '.' in text:
            return True

        return False

    def _looks_like_name(self, text: str) -> bool:
        """
        Check if text looks like a person name.

        True for: "J. Smith", "T. Berwick", "A. B. Fyers"
        False for: "Kandy", "Assistant Surveyor", "M.D."
        """
        # Contains role keywords? NOT a name
        # Check this FIRST before other patterns
        role_keywords = ['Assistant', 'Surveyor', 'Secretary', 'Commissioner', 'Magistrate',
                        'Officer', 'Inspector', 'Collector', 'Agent', 'Treasurer', 'Auditor',
                        'Registrar', 'Engineer', 'Architect', 'Clerk', 'Surgeon', 'Writer']
        if any(kw in text for kw in role_keywords):
            return False

        # Single word all caps (likely abbreviation/qualification)
        if text.isupper() and ' ' not in text:
            return False

        # Pattern: Initial(s) and surname (MOST COMMON in this dataset)
        # E.g., "J. Smith", "A. B. Fyers", "T. L. Gibson"
        if re.search(r'\b[A-Z]\.\s+[A-Z][a-z]+', text):
            return True

        # Has comma? Might be "Surname, First" or part of a name-qual pattern
        if ',' in text:
            parts = text.split(',')
            if len(parts) == 2:
                # Check if second part looks like initials or first name
                if re.search(r'^[A-Z]\.', parts[1].strip()):
                    return True

        # Default: if it has at least one period and a capital letter, might be a name
        # This catches cases like "W.H. Someone"
        return '.' in text and any(c.isupper() for c in text)

    def _is_section_header(self, line: str) -> bool:
        """Check if line is a section header."""
        # Same as _is_role_header
        return self._is_role_header(line)

    def _create_person(self, name: str, role: str, salary: Optional[str],
                      line: str, line_num: int, colony: str, year: int,
                      confidence: float, method: str,
                      qualifications: Optional[str] = None,
                      notes: str = "") -> Person:
        """Create a Person object with Ceylon-specific fields."""
        # Build location
        location_parts = [colony]
        if self.current_province:
            location_parts.append(self.current_province)
        if self.current_department:
            location_parts.append(self.current_department)

        # Update last_role for context
        if role != "Unknown":
            self.last_role = role

        return Person(
            name=name,
            role=role,
            location=' - '.join(location_parts),
            colony=colony,
            year=year,
            department=self.current_department,
            province=self.current_province,
            salary=salary,
            full_string=line,
            source_file=self._generate_github_url(line_num),
            line_number=line_num + 1,
            confidence=confidence,
            extraction_method=method,
            notes=notes,
            qualifications=qualifications
        )

    def _generate_github_url(self, line_number: int) -> str:
        """Generate GitHub URL placeholder."""
        return f"{self.github_base_url}/[file]#L{line_number + 1}"

    def _looks_like_people_data(self, line: str) -> bool:
        """Check if line looks like it might contain people data."""
        # Has a name-like pattern
        has_name = bool(re.search(r'[A-Z][a-z]+', line))

        # Has a salary or number
        has_money = bool(re.search(r'(\d{2,}[l\.]|Rs\.)', line))

        # Not a header or table row
        not_header = not re.search(r'^(Year|Total|Male|Female|\||Table|Import|Export|Revenue)', line)

        return has_name and (has_money or len(line) > 40) and not_header


class CeylonValidator:
    """Validate and clean extracted Ceylon people."""

    def __init__(self):
        self.stats = {
            'locations_filtered': 0,
            'qualifications_filtered': 0,
            'names_filtered': 0,
            'vacant_positions': 0,
            'duplicates_removed': 0,
            'plural_roles_fixed': 0
        }

    def singularize_role(self, role: str) -> str:
        """
        Convert plural role names to singular.

        Handles both explicit mappings and generic patterns.

        Args:
            role (str): Role name that might be plural

        Returns:
            str: Singular version of the role

        Examples:
            >>> singularize_role("Superintending Officers")
            'Superintending Officer'
            >>> singularize_role("Colonial Surgeons")
            'Colonial Surgeon'
            >>> singularize_role("Principal Collector")  # Already singular
            'Principal Collector'
        """
        original_role = role

        # Check explicit mapping first
        if role in PLURAL_TO_SINGULAR_ROLES:
            self.stats['plural_roles_fixed'] += 1
            return PLURAL_TO_SINGULAR_ROLES[role]

        # Generic plural → singular for compound roles
        # Don't touch single-word roles (might be surnames like "Williams")
        if ' ' in role:
            # Get the last word
            words = role.split()
            last_word = words[-1]

            # Check if it's a common plural pattern
            # Exclude words that naturally end in 's' but aren't plural
            SINGULAR_EXCEPTIONS = ['Mistress', 'Empress', 'Princess', 'Assistant']

            if last_word not in SINGULAR_EXCEPTIONS and last_word.endswith('s'):
                # Common patterns:
                # "Officers" → "Officer"
                # "Surgeons" → "Surgeon"
                # "Agents" → "Agent"
                # "Surveyors" → "Surveyor"

                if last_word.endswith('ors'):  # Officers, Surveyors
                    words[-1] = last_word[:-1]  # Remove 's'
                    self.stats['plural_roles_fixed'] += 1
                    return ' '.join(words)

                elif last_word.endswith('ons'):  # Surgeons
                    words[-1] = last_word[:-1]
                    self.stats['plural_roles_fixed'] += 1
                    return ' '.join(words)

                elif last_word.endswith('nts'):  # Agents (but we exclude Assistant)
                    words[-1] = last_word[:-1]
                    self.stats['plural_roles_fixed'] += 1
                    return ' '.join(words)

                elif last_word.endswith('ies'):  # Secretaries → Secretary
                    words[-1] = last_word[:-3] + 'y'
                    self.stats['plural_roles_fixed'] += 1
                    return ' '.join(words)

        # Return unchanged if no plural pattern detected
        return role

    def validate(self, people: List[Person], lines: List[str],
                file_analysis: FileAnalysis) -> List[Person]:
        """Validate and filter people."""

        validated = []

        for person in people:
            # Filter false positives
            if self._is_false_positive(person):
                continue

            # Clean name and role
            person.name = self._clean_name(person.name)
            person.role = self._clean_role(person.role)

            # Validate completeness
            if not person.name or len(person.name) < 2:
                continue

            # Validate name doesn't look like a location
            if person.name in CEYLON_LOCATIONS:
                self.stats['vacant_positions'] += 1
                continue

            validated.append(person)

        # Remove duplicates
        validated = self._deduplicate(validated)

        return validated

    def _is_false_positive(self, person: Person) -> bool:
        """
        Check if extraction is a false positive.

        This is the KEY filter for Ceylon quality improvement.
        """
        name = person.name.strip()
        role = person.role.strip()

        # FILTER 1: Role is a location (FIXES 20 ERRORS)
        if role in CEYLON_LOCATIONS:
            self.stats['locations_filtered'] += 1
            return True

        # FILTER 2: Role is a qualification (FIXES 4 ERRORS)
        if role in CEYLON_QUALIFICATIONS:
            self.stats['qualifications_filtered'] += 1
            return True

        # FILTER 3: Role looks like a person name (FIXES 14 ERRORS)
        if self._looks_like_name(role):
            self.stats['names_filtered'] += 1
            return True

        # FILTER 4: Name is a location
        if name in CEYLON_LOCATIONS:
            self.stats['locations_filtered'] += 1
            return True

        # FILTER 5: Name is a qualification
        if name in CEYLON_QUALIFICATIONS:
            self.stats['qualifications_filtered'] += 1
            return True

        # FILTER 6: Single word all caps (likely abbreviation)
        if len(name.split()) == 1 and name.isupper() and len(name) < 6:
            return True

        # FILTER 7: Placeholder values
        placeholders = {'Ditto', 'ditto', 'vacant', 'Vacant', 'Unknown', 'Esq.'}
        if name in placeholders or role in placeholders:
            return True

        return False

    def _looks_like_name(self, text: str) -> bool:
        """Check if text looks like a person name (used in validation)."""
        # Pattern: Initial(s) and surname
        if re.search(r'\b[A-Z]\.\s+[A-Z][a-z]+', text):
            return True

        # Pattern: Multiple initials (J. L. Vanderstraaten)
        if re.match(r'^[A-Z]\.\s+[A-Z]\.\s+[A-Z]', text):
            return True

        return False

    def _clean_name(self, name: str) -> str:
        """Clean up name field."""
        # Remove common prefixes
        name = re.sub(r'^(&c\.,|Ditto,|The|Esq\.,?)\s+', '', name)

        # Remove trailing titles and qualifications
        name = re.sub(r',?\s*(Esq\.?|K\.C\.M\.G\.?|C\.M\.G\.?|M\.D\.?|R\.E\.?)$', '', name)

        # Remove footnote markers
        name = re.sub(r'[†*]', '', name)

        # Remove extra whitespace
        name = ' '.join(name.split())

        return name.strip()

    def _clean_role(self, role: str) -> str:
        """Clean up role field."""
        # Remove trailing punctuation
        role = role.rstrip('.,;:')

        # Expand "ditto" if it's at the start
        if role.lower().startswith('ditto'):
            # This should have been handled by context tracking
            pass

        # Remove extra whitespace
        role = ' '.join(role.split())

        # Singularize plural roles (Fix #1)
        role = self.singularize_role(role)

        return role.strip()

    def _deduplicate(self, people: List[Person]) -> List[Person]:
        """
        Remove duplicate entries.
        """
        seen = set()
        deduped = []

        for person in people:
            # Standard deduplication key
            key = (person.name.lower(), person.role.lower(), person.year)

            if key not in seen:
                seen.add(key)
                deduped.append(person)
            else:
                self.stats['duplicates_removed'] += 1

        return deduped


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Extract people from Ceylon Colonial Office Lists (Specialized V3)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python extract_ceylon_people.py --year 1867
  python extract_ceylon_people.py --test
  python extract_ceylon_people.py --year-range 1867-1900

Specialized Features:
  - Location filtering (fixes 20 errors)
  - Qualification filtering (fixes 4 errors)
  - Name pattern detection (fixes 14 errors)
  - LLM extraction disabled (0-5% accuracy)
  - Pattern-based extraction with validation (84% accuracy)

Target: 90-95% accuracy (vs. 57% in v2)
        """
    )
    parser.add_argument('--year', type=int, help='Specific year')
    parser.add_argument('--year-range', help='Year range (e.g., 1867-1900)')
    parser.add_argument('--all', action='store_true', help='Process all available years')
    parser.add_argument('--output', help='Output file (default: ceylon_YEAR_v3_specialized.json)')
    parser.add_argument('--test', action='store_true', help='Test mode: run on 1867 only')

    args = parser.parse_args()

    orchestrator = CeylonExtractionOrchestrator()

    # Test mode
    if args.test or not (args.year or args.year_range or args.all):
        print("Running in TEST mode (1867)...")
        test_file = "/home/user/colonial_office_list/output_3/1867_manual_parsed/ceylon.txt"

        if not os.path.exists(test_file):
            print(f"Error: Test file not found: {test_file}")
            return

        people, metadata = orchestrator.extract_from_file(
            test_file, "CEYLON", 1867
        )

        print(f"\n{'='*70}")
        print("EXTRACTION COMPLETE (TEST)")
        print('='*70)
        print(f"Extracted {len(people)} people")
        print(f"Average confidence: {metadata['phases']['validation']['avg_confidence']:.2f}")
        print(f"\nCeylon-specific stats:")
        print(f"  Plural roles fixed: {metadata['ceylon_specific']['plural_roles_fixed']}")
        print(f"  Locations filtered: {metadata['ceylon_specific']['locations_filtered']}")
        print(f"  Qualifications filtered: {metadata['ceylon_specific']['qualifications_filtered']}")
        print(f"  Names filtered: {metadata['ceylon_specific']['names_filtered']}")
        print(f"  Vacant positions: {metadata['ceylon_specific']['vacant_positions']}")
        print(f"  Total filtered out: {metadata['phases']['validation']['filtered_out']}")

        # Show extraction method distribution
        method_counts = {}
        for person in people:
            method = person.extraction_method
            method_counts[method] = method_counts.get(method, 0) + 1

        print(f"\nExtraction method distribution:")
        for method, count in sorted(method_counts.items(), key=lambda x: x[1], reverse=True):
            print(f"  {method}: {count} ({count/len(people)*100:.1f}%)")

        # Show sample records
        print(f"\nSample records:")
        for i, person in enumerate(people[:5], 1):
            print(f"\n{i}. {person.name}")
            print(f"   Role: {person.role}")
            print(f"   Location: {person.location}")
            print(f"   Salary: {person.salary}")
            print(f"   Method: {person.extraction_method}")
            if person.qualifications:
                print(f"   Qualifications: {person.qualifications}")
            if person.notes:
                print(f"   Notes: {person.notes}")

        # Show comparison to v3 baseline
        print(f"\n{'='*70}")
        print("QUALITY IMPROVEMENT - FIX #1")
        print('='*70)
        print(f"V3 Baseline (ceylon_1867_v3_specialized.json):")
        print(f"  - 150 people extracted")
        print(f"  - 85.6/100 quality score")
        print(f"  - ~25 plural role errors (16.7%)")
        print(f"  - Main issue: 'Superintending Officers' etc.")
        print(f"\nV3 Fix #1 Results (this run):")
        print(f"  - {len(people)} people extracted")
        print(f"  - Plural roles fixed: {metadata['ceylon_specific']['plural_roles_fixed']}")
        print(f"  - Locations filtered: {metadata['ceylon_specific']['locations_filtered']}")
        print(f"  - Names filtered: {metadata['ceylon_specific']['names_filtered']}")
        print(f"  - Qualifications filtered: {metadata['ceylon_specific']['qualifications_filtered']}")
        print(f"  - Expected quality: ~90/100 (+4-5 points)")

        # Save results
        results = {
            'metadata': metadata,
            'people': [asdict(p) for p in people]
        }

        output_file = args.output if args.output else 'ceylon_1867_v3_fix1.json'
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"\nSaved to {output_file}")
        return

    # Process specific year
    if args.year:
        import glob
        file_pattern = f"output_3/*{args.year}*/ceylon*"
        files = glob.glob(file_pattern)

        if files:
            people, metadata = orchestrator.extract_from_file(
                files[0], "CEYLON", args.year
            )

            print(f"\n{'='*70}")
            print("EXTRACTION COMPLETE")
            print('='*70)
            print(f"Extracted {len(people)} people")
            print(f"Average confidence: {metadata['phases']['validation']['avg_confidence']:.2f}")

            # Save results
            results = {
                'metadata': metadata,
                'people': [asdict(p) for p in people]
            }

            output_file = args.output if args.output else f'ceylon_{args.year}_v3_specialized.json'
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2)

            print(f"Saved to {output_file}")
        else:
            print(f"No file found for CEYLON {args.year}")

    else:
        print("Use --year, --year-range, --all, or --test")


if __name__ == "__main__":
    main()
