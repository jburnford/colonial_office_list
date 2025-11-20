#!/usr/bin/env python3
"""
Colonial Office List - Fiji People Extraction System

Adapted from the Ceylon v2 extraction system to handle Fiji-specific challenges:

1. Multi-role entries: "Stipendiary Magistrate, Rewa, and Commissioner, Naitasiri"
   - Creates separate Person records for each role

2. Acting designations: "(on leave, Acting Name, acting)"
   - Extracts both permanent and acting officials

3. 17 provinces with heavy native administration
   - Fiji-specific province list
   - Native titles (Bulis, Roko Tuis)

4. Aggregate statements: "180 Bulis with salaries varying 50l.-340l."
   - Flags these for manual review

5. Same currency as Ceylon (£ sterling)

Usage:
    python extract_fiji_people.py --year 1909
    python extract_fiji_people.py --year-range 1879-1920
    python extract_fiji_people.py --all
"""

import os
import re
import json
import argparse
from pathlib import Path
from typing import List, Dict, Optional, Tuple
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
    extraction_method: str = "unknown"  # 'regex', 'llm', 'hybrid'
    notes: str = ""
    is_acting: bool = False  # Fiji-specific: track acting officials
    multi_role_id: Optional[str] = None  # Fiji-specific: link multi-role entries


@dataclass
class FileAnalysis:
    """File structure analysis from LLM."""
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
    """Section flagged for LLM extraction."""
    line_start: int
    line_end: int
    lines: List[str]
    reason: str
    context: Dict = field(default_factory=dict)


# Fiji-specific constants
FIJI_PROVINCES = [
    'Ba', 'Bua', 'Cakaudrove', 'Kadavu', 'Lau', 'Lomaiviti', 'Macuata',
    'Nadroga', 'Naitasiri', 'Namosi', 'Ra', 'Rewa', 'Serua', 'Tailevu',
    'Colo North', 'Colo East', 'Colo West', 'Rotuma', 'Rotumah'
]

FIJI_NATIVE_TITLES = [
    'Roko Tui', 'Roko Tuis', 'Buli', 'Bulis', 'Ratu'
]

FIJI_DEPARTMENTS = [
    'Colonial Secretary', 'Audit Department', 'Receiver-General',
    'Postal Department', 'Medical Department', 'Registrar-General',
    'Department of Justice', 'Native Department', 'Department of Agriculture',
    'Fiji Constabulary', 'Printing Office', 'Leper Asylum', 'Colonial Hospital'
]


class FijiExtractionOrchestrator:
    """Main orchestrator for Fiji hybrid extraction."""

    def __init__(self, github_base_url: str = "https://github.com/jburnford/colonial_office_list/blob/main"):
        self.github_base_url = github_base_url
        self.analysis_cache = {}

    def extract_from_file(self, file_path: str, colony: str, year: int, use_cache: bool = True) -> Tuple[List[Person], Dict]:
        """
        Extract all people from a single file using hybrid approach.

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
            'fiji_specific': {
                'multi_role_entries': 0,
                'acting_officials': 0,
                'aggregate_statements': 0
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
        print("\nPHASE 2: Pattern-based extraction (Fiji-specific)...")
        pattern_extractor = FijiPatternExtractor(self.github_base_url)
        preliminary, flagged = pattern_extractor.extract(
            lines, file_analysis, colony, year
        )
        print(f"  Extracted {len(preliminary)} people via patterns")
        print(f"  - Multi-role entries: {pattern_extractor.stats['multi_role_entries']}")
        print(f"  - Acting officials: {pattern_extractor.stats['acting_officials']}")
        print(f"  Flagged {len(flagged)} sections for LLM review")

        metadata['fiji_specific']['multi_role_entries'] = pattern_extractor.stats['multi_role_entries']
        metadata['fiji_specific']['acting_officials'] = pattern_extractor.stats['acting_officials']
        metadata['fiji_specific']['aggregate_statements'] = pattern_extractor.stats['aggregate_statements']
        metadata['phases']['pattern_extraction'] = {
            'extracted': len(preliminary),
            'flagged_sections': len(flagged)
        }

        # PHASE 3: LLM extraction for flagged sections
        print("\nPHASE 3: LLM extraction for flagged sections...")
        additional = self._llm_extract_flagged(flagged, file_analysis, lines)
        print(f"  Extracted {len(additional)} additional people via LLM")
        metadata['phases']['llm_extraction'] = {
            'extracted': len(additional)
        }

        # PHASE 4: Merge and validate
        print("\nPHASE 4: Validation and merging...")
        all_people = preliminary + additional
        validated = self._validate_and_merge(all_people, lines, file_analysis)
        print(f"  Final count: {len(validated)} people")
        metadata['phases']['validation'] = {
            'total': len(validated),
            'avg_confidence': sum(p.confidence for p in validated) / len(validated) if validated else 0
        }

        return validated, metadata

    def _analyze_file_structure(self, lines: List[str], colony: str, year: int,
                                file_path: str, use_cache: bool) -> FileAnalysis:
        """
        Phase 1: Analyze file structure for Fiji.
        """
        # Find people section - look for "Civil Establishment" or "Executive Council"
        start_idx = -1
        for i, line in enumerate(lines):
            if re.search(r'(Civil Establishment|Executive Council|Legislative Council)', line, re.IGNORECASE):
                start_idx = i
                break

        if start_idx == -1:
            # Fallback: look for first department mention
            for i, line in enumerate(lines):
                if re.search(r'(Colonial Secretary|Department|Establishment)', line):
                    start_idx = i
                    break

        if start_idx == -1:
            start_idx = len(lines) // 2  # Final fallback

        # Detect departments and provinces
        departments = set()
        provinces = set()

        for line in lines[start_idx:]:
            # Check for known Fiji departments
            for dept in FIJI_DEPARTMENTS:
                if dept.lower() in line.lower():
                    departments.add(dept)

            # Check for known Fiji provinces
            for prov in FIJI_PROVINCES:
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
            primary_format="Role, Name, Salary (with multi-role patterns)",
            has_lists=True,
            has_ditto=True,
            salary_currency="£ sterling",
            ocr_quality="good"
        )

    def _llm_extract_flagged(self, flagged: List[FlaggedSection],
                            file_analysis: FileAnalysis,
                            lines: List[str]) -> List[Person]:
        """
        Phase 3: Use Tasks to extract from flagged sections.
        """
        if not flagged:
            print("  No sections flagged for LLM extraction")
            return []

        print(f"  Using Claude Code Tasks for extraction")

        try:
            from llm_extractor_task import extract_from_flagged_sections

            return extract_from_flagged_sections(
                flagged_sections=flagged,
                file_analysis=file_analysis,
                all_lines=lines,
                colony=file_analysis.colony,
                year=file_analysis.year
            )
        except ImportError:
            print(f"  Warning: llm_extractor_task not available, skipping LLM extraction")
            return []
        except Exception as e:
            print(f"  Error in Task extraction: {e}")
            return []

    def _validate_and_merge(self, people: List[Person], lines: List[str],
                           file_analysis: FileAnalysis) -> List[Person]:
        """
        Phase 4: Validate and merge extractions.
        """
        validator = FijiValidator()
        return validator.validate(people, lines, file_analysis)


class FijiPatternExtractor:
    """
    Fiji-specific pattern extractor.

    Handles:
    - Multi-role entries
    - Acting officials
    - Native titles
    - Aggregate statements
    """

    def __init__(self, github_base_url: str):
        self.github_base_url = github_base_url
        self.current_department = None
        self.current_province = None
        self.last_role = None
        self.stats = {
            'multi_role_entries': 0,
            'acting_officials': 0,
            'aggregate_statements': 0
        }

    def extract(self, lines: List[str], file_analysis: FileAnalysis,
                colony: str, year: int) -> Tuple[List[Person], List[FlaggedSection]]:
        """Extract people using Fiji-specific patterns."""

        people = []
        flagged = []

        start = file_analysis.people_section_start
        end = file_analysis.people_section_end

        for i in range(start, min(end, len(lines))):
            line = lines[i].strip()

            if not line:
                continue

            # Update context
            self._update_context(line, file_analysis)

            # Check for aggregate statements first
            if self._is_aggregate_statement(line):
                flagged.append(FlaggedSection(
                    line_start=i,
                    line_end=i,
                    lines=[line],
                    reason="aggregate_statement",
                    context={
                        'department': self.current_department,
                        'province': self.current_province,
                        'note': 'Requires manual review - aggregate data without individual names'
                    }
                ))
                self.stats['aggregate_statements'] += 1
                continue

            # Try to extract person(s) - may return multiple for multi-role entries
            extracted = self._extract_from_line(line, i, colony, year, file_analysis)

            if extracted:
                people.extend(extracted)
            elif self._looks_like_people_data(line):
                # Flag for LLM extraction
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
        """Update department/province context."""
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

    def _is_aggregate_statement(self, line: str) -> bool:
        """
        Detect aggregate statements like:
        - "180 Bulis with salaries varying 50l.-340l."
        - "9 Roko Tuis, or Native Administrators of Provinces, with salaries varying from 50l.-340l."
        """
        # Pattern: number + title + varying/ranging
        aggregate_pattern = r'\d+\s+(Bulis|Roko Tuis|Native|officers|Officials).+(varying|ranging|from\s+\d+)'

        if re.search(aggregate_pattern, line, re.IGNORECASE):
            return True

        # Also catch "There are also N..."
        if re.search(r'There are also \d+', line, re.IGNORECASE):
            return True

        return False

    def _extract_from_line(self, line: str, line_num: int,
                          colony: str, year: int,
                          file_analysis: FileAnalysis) -> List[Person]:
        """
        Extract person(s) from a line.

        Returns a list because multi-role entries create multiple Person records.
        """
        people = []

        # First check for acting officials pattern
        # e.g., "Albert Elhardt (on leave, C. A. Brough acting), Attorney-General"
        acting_match = self._extract_acting_official(line, line_num, colony, year, file_analysis)
        if acting_match:
            people.extend(acting_match)
            return people

        # Check for multi-role entries
        # e.g., "Stipendiary Magistrate, Rewa, and Commissioner, Naitasiri, R. M. Booth, 400l."
        multi_role = self._extract_multi_role(line, line_num, colony, year, file_analysis)
        if multi_role:
            people.extend(multi_role)
            return people

        # Standard patterns
        standard = self._extract_standard_patterns(line, line_num, colony, year, file_analysis)
        if standard:
            people.extend(standard)

        return people

    def _extract_acting_official(self, line: str, line_num: int,
                                colony: str, year: int,
                                file_analysis: FileAnalysis) -> Optional[List[Person]]:
        """
        Extract both permanent and acting officials from patterns like:
        Pattern A: "Albert Elhardt (on leave, C. A. Brough acting), Attorney-General"
        Pattern B: "Attorney-General, A. Elhrhardt (on leave, C. A. Brough acting), 700l."
        """
        # Pattern B: Role, Name (on leave, Acting acting), Salary
        # This is the more common pattern in Fiji
        pattern_b = r'^([A-Z][^,]{3,50}?),\s+([A-Z][^(]+?)\s*\(on leave[,\s]+([^)]+?)\s+acting\)[,\s]*(\d+[l\.][\d,]*|Rs\.?\s*\d+)?'

        match = re.search(pattern_b, line, re.IGNORECASE)
        if match:
            role = match.group(1).strip().rstrip('.,')
            permanent_name = match.group(2).strip()
            acting_name = match.group(3).strip()
            salary = match.group(4).strip() if match.group(4) else None
        else:
            # Pattern A: Name (on leave, Acting acting), Role, Salary
            pattern_a = r'^([A-Z][^(]+?)\s*\(on leave[,\s]+([^)]+?)\s+acting\)[,\s]+([^,]+?)(?:,\s*(\d+[l\.][\d,]*|Rs\.?\s*\d+))?'

            match = re.search(pattern_a, line, re.IGNORECASE)
            if not match:
                return None

            permanent_name = match.group(1).strip()
            acting_name = match.group(2).strip()
            role = match.group(3).strip().rstrip('.,')
            salary = match.group(4).strip() if match.group(4) else None

        people = []
        multi_role_id = f"acting_{line_num}"

        # Create record for permanent official (on leave)
        permanent = self._create_person(
            permanent_name,
            role,
            salary,
            line, line_num, colony, year,
            confidence=0.85,
            method='fiji_acting_permanent',
            is_acting=False,
            multi_role_id=multi_role_id,
            notes="On leave"
        )
        people.append(permanent)

        # Create record for acting official
        acting = self._create_person(
            acting_name,
            role,
            salary,
            line, line_num, colony, year,
            confidence=0.85,
            method='fiji_acting_official',
            is_acting=True,
            multi_role_id=multi_role_id,
            notes="Acting"
        )
        people.append(acting)

        self.stats['acting_officials'] += 2
        return people

    def _extract_multi_role(self, line: str, line_num: int,
                           colony: str, year: int,
                           file_analysis: FileAnalysis) -> Optional[List[Person]]:
        """
        Extract multi-role entries like:
        "Stipendiary Magistrate, Rewa, and Commissioner, Naitasiri, R. M. Booth, 400l."

        Creates separate Person records for each role.
        """
        # Pattern: Role1, Location1, and Role2, Location2, Name, Salary
        # Look for "and" between roles
        if ' and ' not in line.lower():
            return None

        # Try to parse multi-role pattern
        # Pattern: Role1, Loc1, and Role2, Loc2, Name, Salary (with extra text after)
        # Updated to capture salary more flexibly
        pattern = r'^([A-Z][^,]+?),\s*([A-Z][^,]+?),\s+and\s+([A-Z][^,]+?),\s*([A-Z][^,]+?),\s+([A-Z][^,\(]+?)(?:,\s*(\d+[l\.][\d,]*)|Rs\.?\s*\d+)'

        match = re.search(pattern, line, re.IGNORECASE)
        if not match:
            return None

        role1 = match.group(1).strip()
        loc1 = match.group(2).strip()
        role2 = match.group(3).strip()
        loc2 = match.group(4).strip()
        name = match.group(5).strip()
        salary_match = re.search(r'(\d+[l\.][\d,]*|Rs\.?\s*\d+)', line)
        salary = salary_match.group(1) if salary_match else None

        # Validate this looks like a multi-role entry
        # Role1 should contain typical role words
        role_keywords = ['Magistrate', 'Commissioner', 'Inspector', 'Officer', 'Secretary', 'Assistant', 'Medical']
        if not any(kw.lower() in role1.lower() for kw in role_keywords):
            return None
        if not any(kw.lower() in role2.lower() for kw in role_keywords):
            return None

        # Validate name doesn't look like a role or location
        if any(kw.lower() in name.lower() for kw in role_keywords):
            return None

        people = []
        multi_role_id = f"multi_{line_num}"

        # Create first role record
        person1 = self._create_person(
            name,
            role1,
            salary,
            line, line_num, colony, year,
            confidence=0.88,
            method='fiji_multi_role',
            multi_role_id=multi_role_id,
            notes=f"Multi-role: {role1} ({loc1}) and {role2} ({loc2})"
        )
        # Override province/location for this role
        person1.province = loc1
        person1.location = f"{colony} - {loc1}"
        people.append(person1)

        # Create second role record
        person2 = self._create_person(
            name,
            role2,
            salary,
            line, line_num, colony, year,
            confidence=0.88,
            method='fiji_multi_role',
            multi_role_id=multi_role_id,
            notes=f"Multi-role: {role1} ({loc1}) and {role2} ({loc2})"
        )
        # Override province/location for this role
        person2.province = loc2
        person2.location = f"{colony} - {loc2}"
        people.append(person2)

        self.stats['multi_role_entries'] += 1
        return people

    def _extract_standard_patterns(self, line: str, line_num: int,
                                   colony: str, year: int,
                                   file_analysis: FileAnalysis) -> List[Person]:
        """Extract using standard patterns from Ceylon extractor."""
        people = []

        # Pattern 1: Role, Name, Salary
        # e.g., "Colonial Secretary, Eyre Hutson, 750l."
        pattern1 = r'^([A-Z][^,]{3,60}?),\s+([A-Z][^,]+?),\s+(\d+[l\.]|Rs\.?\s*\d+)'
        match = re.search(pattern1, line)
        if match:
            role, name, salary = match.groups()
            person = self._create_person(
                name.strip(),
                role.strip(),
                salary.strip(),
                line, line_num, colony, year,
                confidence=0.9,
                method='fiji_pattern1'
            )
            people.append(person)
            return people

        # Pattern 2: Name, Salary (role from context)
        # e.g., "R. H. Kirkwood, 300l."
        pattern2 = r'^([A-Z][^,]{2,40}?),\s+(\d+[l\.]|Rs\.?\s*\d+)'
        match = re.search(pattern2, line)
        if match:
            name, salary = match.groups()
            role = self.last_role if self.last_role else "Unknown"
            person = self._create_person(
                name.strip(),
                role,
                salary.strip(),
                line, line_num, colony, year,
                confidence=0.7 if self.last_role else 0.5,
                method='fiji_pattern2'
            )
            people.append(person)
            return people

        # Pattern 3: Role, Name (no salary listed)
        # e.g., "Warden, C. W. Campbell, 150l., with quarters."
        pattern3 = r'^([A-Z][^,]{3,50}?),\s+([A-Z][^,]+?)(?:,\s*(\d+[l\.]|Rs\.?\s*\d+))?'
        match = re.search(pattern3, line)
        if match and not re.search(r'(Department|Office|Establishment)', line):
            role, name, salary = match.groups()
            if salary or len(name.split()) >= 2:  # Either has salary or looks like a full name
                person = self._create_person(
                    name.strip(),
                    role.strip(),
                    salary.strip() if salary else None,
                    line, line_num, colony, year,
                    confidence=0.75,
                    method='fiji_pattern3'
                )
                people.append(person)
                return people

        return people

    def _create_person(self, name: str, role: str, salary: Optional[str],
                      line: str, line_num: int, colony: str, year: int,
                      confidence: float, method: str,
                      is_acting: bool = False,
                      multi_role_id: Optional[str] = None,
                      notes: str = "") -> Person:
        """Create a Person object with Fiji-specific fields."""
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
            is_acting=is_acting,
            multi_role_id=multi_role_id
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
        not_header = not re.search(r'^(Year|Total|Male|Female|\||Table|Import|Export)', line)

        # Not an aggregate statement
        not_aggregate = not self._is_aggregate_statement(line)

        return has_name and (has_money or len(line) > 40) and not_header and not_aggregate


class FijiValidator:
    """Validate and clean extracted Fiji people."""

    def __init__(self):
        # Known false positive patterns for Fiji
        self.location_names = {
            'Suva', 'Levuka', 'Lautoka', 'Ba', 'Rewa', 'Nadi',
            'Viti Levu', 'Vanua Levu', 'Rotuma', 'Rotumah'
        }
        self.qualifications = {
            'M.D.', 'M.R.C.S.', 'F.R.C.S.', 'A.M.I.C.E.', 'M.I.C.E.',
            'B.A.', 'M.A.', 'LL.D.', 'Q.C.', 'K.C.', 'C.M.G.', 'K.C.M.G.'
        }
        self.placeholders = {
            'Ditto', 'ditto', 'vacant', 'Vacant', 'acting', 'Acting',
            'Grade I', 'Grade II', 'Grade III', 'Esq.'
        }

    def validate(self, people: List[Person], lines: List[str],
                file_analysis: FileAnalysis) -> List[Person]:
        """Validate and filter people."""

        validated = []

        for person in people:
            # Filter false positives
            if self._is_false_positive(person):
                continue

            # Clean name
            person.name = self._clean_name(person.name)

            # Validate completeness
            if not person.name or len(person.name) < 2:
                continue

            validated.append(person)

        # Remove duplicates (but preserve multi-role entries)
        validated = self._deduplicate(validated)

        return validated

    def _is_false_positive(self, person: Person) -> bool:
        """Check if extraction is a false positive."""
        name = person.name.strip()

        # Check against known false positives
        if name in self.location_names:
            return True
        if name in self.qualifications:
            return True
        if name in self.placeholders:
            return True

        # Single word that's all caps (likely abbreviation)
        if len(name.split()) == 1 and name.isupper() and len(name) < 6:
            return True

        return False

    def _clean_name(self, name: str) -> str:
        """Clean up name field."""
        # Remove common prefixes
        name = re.sub(r'^(&c\.,|Ditto,|The|Esq\.,?)\s+', '', name)

        # Remove trailing titles
        name = re.sub(r',?\s*(Esq\.?|K\.C\.M\.G\.?|C\.M\.G\.?)$', '', name)

        # Remove footnote markers
        name = re.sub(r'[†*]', '', name)

        # Remove extra whitespace
        name = ' '.join(name.split())

        return name.strip()

    def _deduplicate(self, people: List[Person]) -> List[Person]:
        """
        Remove duplicate entries.

        Special handling for multi-role entries: these are NOT duplicates
        even if they have the same name and year.
        """
        seen = set()
        deduped = []

        for person in people:
            # For multi-role entries, use multi_role_id + role as key
            # Check if attribute exists (for compatibility with LLM-extracted records)
            multi_role_id = getattr(person, 'multi_role_id', None)
            if multi_role_id:
                key = (person.name.lower(), person.role.lower(), person.year, multi_role_id)
            else:
                # Standard deduplication
                key = (person.name.lower(), person.role.lower(), person.year)

            if key not in seen:
                seen.add(key)
                deduped.append(person)

        return deduped


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Extract people from Fiji Colonial Office Lists',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python extract_fiji_people.py --year 1909
  python extract_fiji_people.py --year-range 1879-1920
  python extract_fiji_people.py --all --output fiji_people_all.json
        """
    )
    parser.add_argument('--year', type=int, help='Specific year')
    parser.add_argument('--year-range', help='Year range (e.g., 1879-1920)')
    parser.add_argument('--all', action='store_true', help='Process all available years')
    parser.add_argument('--output', default='fiji_people_extracted.json', help='Output file')
    parser.add_argument('--test', action='store_true', help='Test mode: run on 1909 only')

    args = parser.parse_args()

    orchestrator = FijiExtractionOrchestrator()

    # Test mode
    if args.test or not (args.year or args.year_range or args.all):
        print("Running in TEST mode (1909)...")
        test_file = "/home/user/colonial_office_list/output_3/1909_manual_parsed/fiji.md"

        if not os.path.exists(test_file):
            print(f"Error: Test file not found: {test_file}")
            return

        people, metadata = orchestrator.extract_from_file(
            test_file, "FIJI", 1909
        )

        print(f"\n{'='*70}")
        print("EXTRACTION COMPLETE (TEST)")
        print('='*70)
        print(f"Extracted {len(people)} people")
        print(f"Average confidence: {metadata['phases']['validation']['avg_confidence']:.2f}")
        print(f"\nFiji-specific stats:")
        print(f"  Multi-role entries: {metadata['fiji_specific']['multi_role_entries']}")
        print(f"  Acting officials: {metadata['fiji_specific']['acting_officials']}")
        print(f"  Aggregate statements flagged: {metadata['fiji_specific']['aggregate_statements']}")

        # Show sample records
        print(f"\nSample records:")
        for i, person in enumerate(people[:5], 1):
            print(f"\n{i}. {person.name}")
            print(f"   Role: {person.role}")
            print(f"   Location: {person.location}")
            print(f"   Salary: {person.salary}")
            # Handle optional Fiji-specific fields
            is_acting = getattr(person, 'is_acting', False)
            print(f"   Acting: {is_acting}")
            print(f"   Method: {person.extraction_method}")
            if person.notes:
                print(f"   Notes: {person.notes}")

        # Save results
        results = {
            'metadata': metadata,
            'people': [asdict(p) for p in people]
        }

        output_file = 'fiji_1909_test.json'
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"\nSaved to {output_file}")
        return

    # Process specific year
    if args.year:
        import glob
        file_pattern = f"output_3/*{args.year}*/fiji*"
        files = glob.glob(file_pattern)

        if files:
            people, metadata = orchestrator.extract_from_file(
                files[0], "FIJI", args.year
            )

            print(f"\n{'='*70}")
            print("EXTRACTION COMPLETE")
            print('='*70)
            print(f"Extracted {len(people)} people")
            print(f"Average confidence: {metadata['phases']['validation']['avg_confidence']:.2f}")
            print(f"\nFiji-specific stats:")
            print(f"  Multi-role entries: {metadata['fiji_specific']['multi_role_entries']}")
            print(f"  Acting officials: {metadata['fiji_specific']['acting_officials']}")

            # Save results
            results = {
                'metadata': metadata,
                'people': [asdict(p) for p in people]
            }

            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2)

            print(f"Saved to {args.output}")
        else:
            print(f"No file found for FIJI {args.year}")

    else:
        print("Use --year, --year-range, --all, or --test")


if __name__ == "__main__":
    main()
