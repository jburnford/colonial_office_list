#!/usr/bin/env python3
"""
Colonial Office List - Kenya People Extraction System (Specialized V1)

Specialized extractor for Kenya based on proven Ceylon extractor architecture (96.7/100 quality).

Kenya-Specific Features:
1. Provincial organization: Nyanza, Rift Valley, Central, Coast, Northern, Masai
2. Strong provincial administration hierarchy (Senior Commissioners, District Commissioners)
3. Salary format: "800l. by 50l. to 1,000l." (incremental ranges)
4. Currency: £ sterling → East African shillings (Shs.)
5. Military ranks and decorations (post-WWI)
6. Native administration roles

Target: 92-95% accuracy

Architecture based on: extract_ceylon_people.py (proven 96.7/100 quality)

Usage:
    python extract_kenya_people.py --year 1922
    python extract_kenya_people.py --test
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


# Kenya-specific constants
KENYA_LOCATIONS = {
    # Major cities
    'Nairobi', 'Mombasa', 'Kisumu', 'Nakuru', 'Eldoret', 'Nyeri',
    'Kitale', 'Thika', 'Malindi', 'Lamu', 'Nanyuki', 'Kericho',
    'Kakamega', 'Machakos', 'Embu', 'Meru', 'Kajiado', 'Narok',
    'Voi', 'Garissa', 'Isiolo', 'Marsabit', 'Moyale', 'Wajir',

    # Districts and towns
    'Fort Hall', 'Kiambu', 'Kyambu', 'Teita', 'Kitui', 'Tana River',
    'Kilifi', 'Kwale', 'Baringo', 'Laikipia', 'Nandi', 'Elgeyo',
    'Trans Nzoia', 'Trans-Nzoia', 'West Suk', 'Samburu', 'Turkana',
    'Kismayu', 'Mandera', 'Nanyuki', 'Rumuruti',

    # Districts (combined)
    'North Kavirondo', 'South Kavirondo', 'Central Kavirondo',
    'Lumbwa', 'Jubaland', 'Marakwet', 'Elgeyo-Marakwet',
    'Uasin Gishu', 'Usain-Gishu', 'St. Thomas-in-the-East',

    # Provinces
    'Nyanza Province', 'Rift Valley Province', 'Central Province',
    'Coast Province', 'Northern Province', 'Coastal Area',
    'Ukamba Province', 'Kikuyu Province', 'Masai Province',
    'Kerio Province', 'Masai Reserve', 'Masai District',
    'Northern Frontier District', 'Northern Frontier Province',
    'Kamasia and Suk Reserve'
}

KENYA_PROVINCES = [
    'Nyanza Province', 'Rift Valley Province', 'Central Province',
    'Coast Province', 'Northern Province', 'Coastal Area',
    'Ukamba Province', 'Kikuyu Province', 'Masai Province',
    'Kerio Province', 'Masai District', 'Northern Frontier District',
    'Kamasia and Suk Reserve'
]

KENYA_DEPARTMENTS = [
    'Secretariat',
    'Colonial Secretary\'s Office',
    'Government House',
    'Provincial Administration',
    'Native Affairs Department',
    'Chief Native Commissioner\'s Office',
    'Treasury', 'Treasury Department',
    'Customs', 'Customs Department',
    'Port and Marine',
    'Audit', 'Audit Department', 'Audit Office',
    'Judicial', 'Judicial Establishment',
    'Attorney General\'s Department',
    'Police', 'Police Department', 'Constabulary',
    'Prisons', 'Prison Service', 'Prisons Department',
    'Medical', 'Medical Department', 'Medical Services',
    'Education', 'Education Department',
    'Public Works', 'Public Works Department',
    'Agriculture', 'Agriculture Department',
    'Veterinary', 'Veterinary Services', 'Veterinary Department',
    'Forestry', 'Forest Department',
    'Survey', 'Survey Department', 'Surveyor General\'s Department',
    'Lands', 'Lands Department',
    'Post Office', 'Posts and Telegraphs',
    'Railways', 'Railway Department',
    'Labour', 'Labour Department',
    'Immigration',
    'Government Press',
    'Executive Council',
    'Legislative Council',
    'Local Government'
]

# Qualifications that are NOT roles
KENYA_QUALIFICATIONS = {
    # Medical
    'M.D.', 'M.R.C.S.', 'M.R.C.S.E.', 'F.R.C.S.', 'F.R.C.S. Edin.',
    'M.B.', 'Ch.B.', 'M.B., Ch.B.', 'L.R.C.P.', 'L.R.C.S.E.',

    # Engineering
    'M. Inst. C.E.', 'M.I.C.E.', 'Assoc. Inst. C.E.', 'A.M.I.C.E.',
    'A.R.I.B.A.', 'A.M.I.Mech.E.', 'R.E.',

    # Legal/Academic
    'B.A.', 'M.A.', 'LL.D.', 'LL.B.', 'D.C.L.', 'Q.C.', 'K.C.', 'P.C.', 'J.P.',

    # Honours - CMG Family
    'C.M.G.', 'K.C.M.G.', 'G.C.M.G.',

    # Honours - CB Family
    'C.B.', 'K.C.B.', 'G.C.B.',

    # Honours - BE Family
    'O.B.E.', 'M.B.E.', 'K.B.E.', 'G.B.E.', 'C.B.E.', 'D.B.E.',

    # Military decorations
    'D.S.O.', 'M.C.', 'D.F.C.', 'M.M.', 'D.C.M.', 'V.C.', 'D.F.M.',

    # Other
    'I.S.O.', 'C.I.E.', 'K.C.V.O.', 'C.V.O.', 'M.V.O.',
    'R.N.', 'R.F.A.', 'R.N.R.', 'I.A.'
}

# Plural-to-Singular role mappings
PLURAL_TO_SINGULAR_ROLES = {
    'Senior Commissioners': 'Senior Commissioner',
    'District Commissioners': 'District Commissioner',
    'Assistant District Commissioners': 'Assistant District Commissioner',
    'Cadets': 'Cadet',
    'Senior Assistant Secretaries': 'Senior Assistant Secretary',
    'Assistant Secretaries': 'Assistant Secretary',
    'Senior Assistants': 'Senior Assistant',
    'Assistant Treasurers': 'Assistant Treasurer',
    'Assistant Auditors': 'Assistant Auditor',
    'Superintendents': 'Superintendent',
    'Assistant Superintendents': 'Assistant Superintendent',
    'Inspectors': 'Inspector',
    'Assistant Inspectors': 'Assistant Inspector',
    'European Clerks': 'European Clerk',
    'Clerks': 'Clerk',
    'Writers': 'Writer',
    'Officers': 'Officer',
    'Assistants': 'Assistant',
    'Magistrates': 'Magistrate',
    'Pilots': 'Pilot',
    'Engineers': 'Engineer',
    'Surveyors': 'Surveyor'
}


class KenyaExtractionOrchestrator:
    """Main orchestrator for Kenya specialized extraction."""

    def __init__(self, github_base_url: str = "https://github.com/jburnford/colonial_office_list/blob/main"):
        self.github_base_url = github_base_url
        self.analysis_cache = {}

    def extract_from_file(self, file_path: str, colony: str, year: int, use_cache: bool = True) -> Tuple[List[Person], Dict]:
        """
        Extract all people from a single file using specialized Kenya approach.

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
            'kenya_specific': {
                'locations_filtered': 0,
                'qualifications_filtered': 0,
                'names_filtered': 0,
                'vacant_positions': 0,
                'plural_roles_fixed': 0
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
        print("\nPHASE 2: Pattern-based extraction (Kenya-specific)...")
        pattern_extractor = KenyaPatternExtractor(self.github_base_url)
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

        # Update Kenya-specific stats from validator
        validator = KenyaValidator()
        metadata['kenya_specific'] = validator.stats

        metadata['phases']['validation'] = {
            'total': len(validated),
            'avg_confidence': sum(p.confidence for p in validated) / len(validated) if validated else 0,
            'filtered_out': len(all_people) - len(validated)
        }

        return validated, metadata

    def _analyze_file_structure(self, lines: List[str], colony: str, year: int,
                                file_path: str, use_cache: bool) -> FileAnalysis:
        """
        Phase 1: Analyze file structure for Kenya.
        """
        # Find people section - look for "Civil Establishment" or "Government"
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

        # Detect departments and provinces
        departments = set()
        provinces = set()

        for line in lines[start_idx:]:
            # Check for known Kenya departments
            for dept in KENYA_DEPARTMENTS:
                if dept.lower() in line.lower():
                    departments.add(dept)

            # Check for known Kenya provinces
            for prov in KENYA_PROVINCES:
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
            primary_format="Role, Name, Qualifications, Salary (with ranges)",
            has_lists=True,
            has_ditto=True,
            salary_currency="£ sterling / East African shillings",
            ocr_quality="good"
        )

    def _llm_extract_flagged(self, flagged: List[FlaggedSection],
                            file_analysis: FileAnalysis,
                            lines: List[str]) -> List[Person]:
        """
        Phase 3: LLM extraction - DISABLED for Kenya (following Ceylon model).
        """
        print("  Task-based extraction DISABLED (following Ceylon model)")
        print("  Relying on pattern-based extraction with validation")
        return []

    def _validate_and_merge(self, people: List[Person], lines: List[str],
                           file_analysis: FileAnalysis) -> List[Person]:
        """
        Phase 4: Validate and merge extractions.
        """
        validator = KenyaValidator()
        return validator.validate(people, lines, file_analysis)


class KenyaPatternExtractor:
    """
    Kenya-specific pattern extractor.

    Handles:
    - Role, Name, Qualifications, Salary format
    - Location-Name-Salary format (provinces/districts)
    - Qualification filtering
    - Complex list structures with semicolons
    - Salary ranges ("800l. by 50l. to 1,000l.")
    """

    def __init__(self, github_base_url: str):
        self.github_base_url = github_base_url
        self.current_department = None
        self.current_province = None
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
        """Extract people using Kenya-specific patterns."""

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
                # Flag for manual review
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
            'Commissioner', 'Secretary', 'Assistant', 'Officer', 'Clerk',
            'Magistrate', 'Inspector', 'Collector', 'Agent', 'Treasurer',
            'Auditor', 'Registrar', 'Governor', 'Chief', 'Principal',
            'Deputy', 'Superintendent', 'Director', 'Engineer', 'Surveyor',
            'Cadet', 'Pilot', 'Captain'
        ]

        if any(kw in line for kw in job_keywords):
            return len(line) < 100 and line.count(',') <= 1

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
        """Extract person(s) from a line using Kenya-specific patterns."""
        people = []

        # Pattern 1: Role, Name, Qualifications, Salary
        pattern1 = self._extract_pattern1(line, line_num, colony, year, file_analysis)
        if pattern1:
            people.extend(pattern1)
            return people

        # Pattern 2: Location, Name, Salary
        pattern2 = self._extract_location_name_salary(line, line_num, colony, year, file_analysis)
        if pattern2:
            people.extend(pattern2)
            return people

        # Pattern 3: Name, Salary (role from context)
        pattern3 = self._extract_name_salary(line, line_num, colony, year, file_analysis)
        if pattern3:
            people.extend(pattern3)
            return people

        # Pattern 4: Semicolon-separated list
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
        Pattern 1: Role, Name, [Qualifications,] Salary [ranges]

        Examples:
        - "Colonial Secretary, Sir C. C. Bowring, K.B.E., C.M.G., 1,800l."
        - "Governor and Commander-in-Chief, Major-General Sir E. Northey, K.C.M.G., C.B., 4,000l., and 1,500l. duty allowance."
        - "Assistant Colonial Secretary, G. A. S. Northcote, 800l. by 50l. to 1,000l."
        """
        # Pattern with optional salary range
        pattern = r'^([A-Z][^,]{3,80}?),\s+([A-Z][^,]+?),\s+(?:([A-Z][^,]+?),\s+)?(\d[\d,]*l\.?(?:[\s,]+(and|by|to)[\s,]+\d[\d,]*l\.?)*)?'

        match = re.search(pattern, line)
        if not match:
            return None

        potential_role = match.group(1).strip()
        name = match.group(2).strip()
        potential_qual = match.group(3).strip() if match.group(3) else None
        salary = match.group(4).strip() if match.group(4) else None

        # Check if "role" is actually a location
        if potential_role in KENYA_LOCATIONS:
            return None  # Will be handled by location-name pattern

        # Check if "role" is actually a qualification
        if potential_role in KENYA_QUALIFICATIONS:
            return None

        # Check if "role" looks like a person name
        if self._looks_like_name(potential_role):
            return None

        # Extract qualifications
        qualifications = None
        role = potential_role

        if potential_qual:
            if potential_qual in KENYA_QUALIFICATIONS or self._looks_like_qualification(potential_qual):
                qualifications = potential_qual
            else:
                # Might be part of name or complex role
                return None

        # Extract qualifications from name
        name_cleaned, name_quals = self._extract_qualifications_from_name(name)
        if name_quals:
            qualifications = name_quals if not qualifications else f"{qualifications}, {name_quals}"
            name = name_cleaned

        # Expand "ditto" in role
        role = self._expand_ditto(role)

        # Create person
        person = self._create_person(
            name,
            role,
            salary,
            line, line_num, colony, year,
            confidence=0.9,
            method='kenya_pattern1',
            qualifications=qualifications
        )

        self.stats['pattern1_extractions'] += 1

        # Update last_role for context
        if 'deputy' in role.lower() or 'second' in role.lower() or 'assistant' in role.lower():
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
        - "Nairobi, J. Smith, 500l."
        """
        pattern = r'^([^,]+?),\s+([A-Z][^,]+?),\s+(\d[\d,]*l\.?(?:[\s,]+(and|by|to)[\s,]+\d[\d,]*l\.?)*)?'

        match = re.search(pattern, line)
        if not match:
            return None

        potential_location = match.group(1).strip()
        name = match.group(2).strip()
        salary = match.group(3).strip() if match.group(3) else None

        # Must be a known location
        if potential_location not in KENYA_LOCATIONS:
            # Check partial matches
            is_location = False
            for loc in KENYA_LOCATIONS:
                if loc.lower() in potential_location.lower() or potential_location.lower() in loc.lower():
                    is_location = True
                    break
            if not is_location:
                return None

        # Name should look like a name
        if not self._looks_like_name(name):
            return None

        # Use last_full_role as the role
        role = self.last_full_role if self.last_full_role else self.last_role
        if not role:
            role = "Unknown"

        # Expand "ditto" in role
        role = self._expand_ditto(role)

        # Create person with location info
        person = self._create_person(
            name,
            role,
            salary,
            line, line_num, colony, year,
            confidence=0.85,
            method='kenya_location_name',
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
        - "G. H. Booth, 250l. by 15l. to 400l."
        """
        pattern = r'^([A-Z][^,]{2,50}?),\s+(\d[\d,]*l\.?(?:[\s,]+(and|by|to)[\s,]+\d[\d,]*l\.?)*)?'

        match = re.search(pattern, line)
        if not match:
            return None

        name = match.group(1).strip()
        salary = match.group(2).strip() if match.group(2) else None

        # Name must look like a name
        if not self._looks_like_name(name):
            return None

        # Must have a role from context
        role = self.last_full_role if self.last_full_role else self.last_role
        if not role or role == "Unknown":
            role = "Unknown"
            confidence = 0.5
        else:
            confidence = 0.75

        # Expand "ditto" in role
        role = self._expand_ditto(role)

        # Extract qualifications from name
        name_cleaned, qualifications = self._extract_qualifications_from_name(name)

        # Create person
        person = self._create_person(
            name_cleaned,
            role,
            salary,
            line, line_num, colony, year,
            confidence=confidence,
            method='kenya_name_salary',
            qualifications=qualifications
        )

        self.stats['pattern3_extractions'] += 1

        return [person]

    def _extract_semicolon_list(self, line: str, line_num: int,
                                colony: str, year: int,
                                file_analysis: FileAnalysis) -> Optional[List[Person]]:
        """
        Pattern 4: Semicolon-separated list

        Examples:
        - "C. E. Spencer, 700l. and 100l. personal; H. B. Kittermaster, O.B.E., J. E. S. Merrick, 600l. by 25l. to 700l."
        """
        if ';' not in line:
            return None

        if not self.last_role:
            return None

        # FIX: Strip grade/rank prefixes before splitting
        # Example: "Grade I—V. de V. Allen; J. H. Daly" → "V. de V. Allen; J. H. Daly"
        if '—' in line or '–' in line:
            if 'grade' in line.lower() or 'class' in line.lower():
                for sep in ['—', '–']:
                    if sep in line:
                        parts_prefix = line.split(sep)
                        if any(kw in parts_prefix[0].lower() for kw in ['grade', 'class', 'rank']):
                            line = sep.join(parts_prefix[1:])
                        break

        people = []
        entries = line.split(';')

        for entry in entries:
            entry = entry.strip()
            if not entry:
                continue

            # Try to extract Name(s), Salary
            # Handle multiple names before salary: "A, B, C, 500l."
            pattern = r'([A-Z][^,]+(?:,\s+[A-Z][^,]+)*),\s+(\d[\d,]*l\.?(?:[\s,]+(and|by|to)[\s,]+\d[\d,]*l\.?)*)'
            match = re.search(pattern, entry)

            if match:
                names_part = match.group(1)
                salary = match.group(2)

                # Split by commas to get individual names
                names = [n.strip() for n in names_part.split(',')]

                for name in names:
                    name_cleaned, quals = self._extract_qualifications_from_name(name)

                    if self._looks_like_name(name_cleaned):
                        person = self._create_person(
                            name_cleaned,
                            self.last_role,
                            salary,
                            line, line_num, colony, year,
                            confidence=0.80,
                            method='kenya_semicolon_list',
                            qualifications=quals
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
        - "G. H. Booth, G. Wedderburn, 250l. by 15l. to 400l."
        """
        if not self.last_full_role and not self.last_role:
            return None

        # Line should have multiple names separated by commas
        # Must NOT have salary indicators in first parts
        parts = [p.strip() for p in line.split(',')]

        # Filter to likely names
        names = []
        for i, part in enumerate(parts):
            # Skip if contains salary (unless it's the last part)
            if re.search(r'\d+l\.', part) and i < len(parts) - 1:
                continue
            if len(part) >= 2 and part[0].isupper():
                # Clean up trailing punctuation
                part = part.rstrip('.,;:')
                # Remove salary from last part if present
                part = re.sub(r',?\s*\d[\d,]*l\.?.*$', '', part)
                if self._looks_like_name(part):
                    names.append(part)

        # Need at least 2 names to consider this a list
        if len(names) < 2:
            return None

        # Create person records for each name
        people = []
        role = self.last_full_role if self.last_full_role else self.last_role

        # Expand "ditto" in role
        role = self._expand_ditto(role)

        for name in names:
            name_cleaned, quals = self._extract_qualifications_from_name(name)

            person = self._create_person(
                name_cleaned,
                role,
                None,  # No individual salary
                line, line_num, colony, year,
                confidence=0.7,
                method='kenya_name_list',
                qualifications=quals
            )
            people.append(person)

        self.stats['list_extractions'] += len(people)

        return people if people else None

    def _extract_qualifications_from_name(self, name: str) -> Tuple[str, Optional[str]]:
        """
        Extract qualifications embedded in name field.

        Returns: (cleaned_name, qualifications)
        """
        # FIX: Strip department/location prefixes (e.g., "Kabete Technical and Trade School—A. E. Talbot")
        if '—' in name:
            name = name.split('—')[-1].strip()
        elif '–' in name:
            name = name.split('–')[-1].strip()
        elif ' - ' in name and not re.match(r'^[A-Z]\.\s*[A-Z]', name):
            parts_dash = name.split(' - ')
            if any(kw in parts_dash[0] for kw in ['School', 'Office', 'Department', 'District', 'Grade']):
                name = parts_dash[-1].strip()

        qualifications = []
        remaining_parts = []

        # Split by commas
        parts = [p.strip() for p in name.split(',')]

        for part in parts:
            if part in KENYA_QUALIFICATIONS or self._looks_like_qualification(part):
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

        True for: "J. Smith", "Major-General Sir E. Northey", "A. B. Fyers"
        False for: "Nairobi", "Senior Commissioner", "K.C.M.G."
        """
        # Contains role keywords? NOT a name
        role_keywords = ['Commissioner', 'Secretary', 'Assistant', 'Officer',
                        'Inspector', 'Collector', 'Agent', 'Treasurer', 'Auditor',
                        'Registrar', 'Engineer', 'Surveyor', 'Clerk', 'Writer',
                        'Superintendent', 'Director']
        if any(kw in text for kw in role_keywords):
            return False

        # Single word all caps (likely abbreviation/qualification)
        if text.isupper() and ' ' not in text:
            return False

        # Pattern: Initial(s) and surname (MOST COMMON)
        if re.search(r'\b[A-Z]\.\s+[A-Z][a-z]+', text):
            return True

        # Has comma? Might be "Surname, First" or part of a name-qual pattern
        if ',' in text:
            parts = text.split(',')
            if len(parts) == 2:
                if re.search(r'^[A-Z]\.', parts[1].strip()):
                    return True

        # Military ranks followed by name
        if re.match(r'^(Major|Colonel|Captain|Lieutenant|Lieut|Lt|Brig|General|Sir)', text):
            return True

        # FIX: Reject qualifications-only (e.g., "B.A. (1st class Hons.) (Lond.)")
        if re.match(r'^[A-Z]\.[A-Z]\.\s*\(', text):
            return False  # "B.A. (" pattern
        if text.count('(') >= 2 and 'class' in text.lower():
            return False  # Multiple parentheses with "class" = qualification
        if re.match(r'^[A-Z\.]+\s+\([^)]+\)$', text):
            return False  # "B.A. (Lond.)" pattern

        # FIX: Reject descriptive text fragments
        DESCRIPTIVE_WORDS = ['most', 'important', 'towns', 'are', 'principal',
                            'island', 'occurred', 'recent', 'hurricanes']
        text_lower = text.lower()
        if any(word in text_lower for word in DESCRIPTIVE_WORDS):
            return False

        # FIX: Reject grade prefixes alone
        if re.match(r'^Grade\s+[IVX]+$', text, re.IGNORECASE):
            return False

        # FIX: Reject table markers
        if text.startswith('|') or '|' in text:
            return False

        # Default: if it has at least one period and a capital letter
        return '.' in text and any(c.isupper() for c in text)

    def _is_section_header(self, line: str) -> bool:
        """Check if line is a section header."""
        return self._is_role_header(line)

    def _create_person(self, name: str, role: str, salary: Optional[str],
                      line: str, line_num: int, colony: str, year: int,
                      confidence: float, method: str,
                      qualifications: Optional[str] = None,
                      notes: str = "") -> Person:
        """Create a Person object with Kenya-specific fields."""
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
        has_money = bool(re.search(r'(\d{2,}[l\.]|Shs\.)', line))

        # Not a header or table row
        not_header = not re.search(r'^(Year|Total|Male|Female|\||Table|Import|Export|Revenue)', line)

        return has_name and (has_money or len(line) > 40) and not_header


class KenyaValidator:
    """Validate and clean extracted Kenya people."""

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
        """Convert plural role names to singular."""
        original_role = role

        # Check explicit mapping first
        if role in PLURAL_TO_SINGULAR_ROLES:
            self.stats['plural_roles_fixed'] += 1
            return PLURAL_TO_SINGULAR_ROLES[role]

        # Generic plural → singular for compound roles
        if ' ' in role:
            words = role.split()
            last_word = words[-1]

            SINGULAR_EXCEPTIONS = ['Mistress', 'Empress', 'Princess', 'Assistant']

            if last_word not in SINGULAR_EXCEPTIONS and last_word.endswith('s'):
                if last_word.endswith('ors'):  # Officers, Commissioners
                    words[-1] = last_word[:-1]
                    self.stats['plural_roles_fixed'] += 1
                    return ' '.join(words)

                elif last_word.endswith('ons'):  # Surgeons
                    words[-1] = last_word[:-1]
                    self.stats['plural_roles_fixed'] += 1
                    return ' '.join(words)

                elif last_word.endswith('nts') and last_word != 'Assistant':
                    words[-1] = last_word[:-1]
                    self.stats['plural_roles_fixed'] += 1
                    return ' '.join(words)

                elif last_word.endswith('ies'):  # Secretaries
                    words[-1] = last_word[:-3] + 'y'
                    self.stats['plural_roles_fixed'] += 1
                    return ' '.join(words)

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
            if person.name in KENYA_LOCATIONS:
                self.stats['vacant_positions'] += 1
                continue

            validated.append(person)

        # Remove duplicates
        validated = self._deduplicate(validated)

        return validated

    def _is_false_positive(self, person: Person) -> bool:
        """Check if extraction is a false positive."""
        name = person.name.strip()
        role = person.role.strip()

        # FILTER 1: Role is a location
        if role in KENYA_LOCATIONS:
            self.stats['locations_filtered'] += 1
            return True

        # FILTER 2: Role is a qualification
        if role in KENYA_QUALIFICATIONS:
            self.stats['qualifications_filtered'] += 1
            return True

        # FILTER 3: Role looks like a person name
        if self._looks_like_name(role):
            self.stats['names_filtered'] += 1
            return True

        # FILTER 4: Name is a location
        if name in KENYA_LOCATIONS:
            self.stats['locations_filtered'] += 1
            return True

        # FILTER 5: Name is a qualification
        if name in KENYA_QUALIFICATIONS:
            self.stats['qualifications_filtered'] += 1
            return True

        # FILTER 6: Single word all caps (likely abbreviation)
        if len(name.split()) == 1 and name.isupper() and len(name) < 6:
            return True

        # FILTER 7: Placeholder values
        placeholders = {'Ditto', 'ditto', 'vacant', 'Vacant', 'Unknown', 'Esq.', 'one vacancy', 'two vacancies', 'vacancy'}
        if name in placeholders or role in placeholders:
            self.stats['vacant_positions'] += 1
            return True

        return False

    def _looks_like_name(self, text: str) -> bool:
        """Check if text looks like a person name (used in validation)."""
        # Pattern: Initial(s) and surname
        if re.search(r'\b[A-Z]\.\s+[A-Z][a-z]+', text):
            return True

        # Pattern: Multiple initials
        if re.match(r'^[A-Z]\.\s+[A-Z]\.\s+[A-Z]', text):
            return True

        return False

    def _clean_name(self, name: str) -> str:
        """Clean up name field."""
        # Remove common prefixes
        name = re.sub(r'^(&c\.,|Ditto,|The|Esq\.,?)\s+', '', name)

        # Remove trailing titles and qualifications
        for qual in KENYA_QUALIFICATIONS:
            name = name.replace(f', {qual}', '').replace(f' {qual}', '')

        # Remove footnote markers
        name = re.sub(r'[†*]', '', name)

        # Remove extra whitespace
        name = ' '.join(name.split())

        return name.strip()

    def _clean_role(self, role: str) -> str:
        """Clean up role field."""
        # Remove trailing punctuation
        role = role.rstrip('.,;:')

        # Remove extra whitespace
        role = ' '.join(role.split())

        # Singularize plural roles
        role = self.singularize_role(role)

        return role.strip()

    def _deduplicate(self, people: List[Person]) -> List[Person]:
        """Remove duplicate entries."""
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
        description='Extract people from Kenya Colonial Office Lists (Specialized V1)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python extract_kenya_people.py --year 1922
  python extract_kenya_people.py --test
  python extract_kenya_people.py --year-range 1922-1951

Specialized Features:
  - Provincial organization filtering
  - Military rank handling
  - Salary range parsing ("800l. by 50l. to 1,000l.")
  - Location filtering (provinces/districts)
  - Qualification filtering
  - Pattern-based extraction with validation

Target: 92-95% accuracy (based on Ceylon template 96.7/100)
        """
    )
    parser.add_argument('--year', type=int, help='Specific year')
    parser.add_argument('--year-range', help='Year range (e.g., 1922-1951)')
    parser.add_argument('--all', action='store_true', help='Process all available years')
    parser.add_argument('--output', help='Output file (default: kenya_YEAR_v1.json)')
    parser.add_argument('--test', action='store_true', help='Test mode: run on 1922 only')

    args = parser.parse_args()

    orchestrator = KenyaExtractionOrchestrator()

    # Test mode
    if args.test or not (args.year or args.year_range or args.all):
        print("Running in TEST mode (1922)...")
        test_file = "/home/user/colonial_office_list/output_3/1922_manual_parsed/KENYA.txt"

        if not os.path.exists(test_file):
            print(f"Error: Test file not found: {test_file}")
            return

        people, metadata = orchestrator.extract_from_file(
            test_file, "Kenya", 1922
        )

        print(f"\n{'='*70}")
        print("EXTRACTION COMPLETE (TEST)")
        print('='*70)
        print(f"Extracted {len(people)} people")
        print(f"Average confidence: {metadata['phases']['validation']['avg_confidence']:.2f}")
        print(f"\nKenya-specific stats:")
        print(f"  Plural roles fixed: {metadata['kenya_specific']['plural_roles_fixed']}")
        print(f"  Locations filtered: {metadata['kenya_specific']['locations_filtered']}")
        print(f"  Qualifications filtered: {metadata['kenya_specific']['qualifications_filtered']}")
        print(f"  Names filtered: {metadata['kenya_specific']['names_filtered']}")
        print(f"  Vacant positions: {metadata['kenya_specific']['vacant_positions']}")
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
        for i, person in enumerate(people[:10], 1):
            print(f"\n{i}. {person.name}")
            print(f"   Role: {person.role}")
            print(f"   Location: {person.location}")
            if person.salary:
                print(f"   Salary: {person.salary}")
            if person.qualifications:
                print(f"   Qualifications: {person.qualifications}")
            print(f"   Method: {person.extraction_method}")

        # Save results
        results = {
            'metadata': metadata,
            'people': [asdict(p) for p in people]
        }

        output_file = args.output if args.output else 'kenya_1922_test.json'
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"\nSaved to {output_file}")
        return

    # Process specific year
    if args.year:
        import glob
        # Try different case variations
        patterns = [
            f"/home/user/colonial_office_list/output_3/{args.year}_manual_parsed/KENYA.txt",
            f"/home/user/colonial_office_list/output_3/{args.year}_manual_parsed/kenya.txt",
            f"/home/user/colonial_office_list/output_3/{args.year}_manual_parsed/Kenya.txt"
        ]

        file_path = None
        for pattern in patterns:
            if os.path.exists(pattern):
                file_path = pattern
                break

        if file_path:
            people, metadata = orchestrator.extract_from_file(
                file_path, "Kenya", args.year
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

            output_file = args.output if args.output else f'kenya_{args.year}_v1.json'
            with open(output_file, 'w') as f:
                json.dump(results, f, indent=2)

            print(f"Saved to {output_file}")
        else:
            print(f"No file found for Kenya {args.year}")

    else:
        print("Use --year, --year-range, --all, or --test")


if __name__ == "__main__":
    main()
