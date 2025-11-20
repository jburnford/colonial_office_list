#!/usr/bin/env python3
"""
Colonial Office List - Canada People Extraction System (Phase 1: Federal)

Canada is the most complex colony with 3,000+ lines per file, two-tier government,
and extensive legislative branches. This extractor implements Phase 1 focusing on
federal departments and basic structure.

PHASES:
- Phase 1 (THIS FILE): Federal departments, Cabinet, Supreme Court, basic structure
- Phase 2 (FUTURE): Legislative lists (Senate, House of Commons)
- Phase 3 (FUTURE): Provincial governments (7-10 provinces)

KEY CANADA-SPECIFIC FEATURES:
1. Section Detection - Skip tariff/statistics sections (detect "per cent", "per ton")
2. Currency Detection - Handle both £ (1867) and $ (1890+)
3. Federal Department Patterns - Ceylon-style "Role, Name, Salary"
4. Province Markers - Detect "PROVINCE OF ONTARIO" etc. and track context
5. Title Extraction - Handle "Rt. Hon.", "Sir", "Hon.", "P.C.", "G.C.M.G.", etc.
6. Multi-role Detection - Some officials hold multiple positions

LOCATION STRUCTURE:
- Federal: "CANADA - Federal - [Department]"
- Provincial: "CANADA - [Province] - [Department]" (Phase 3)

Usage:
    python extract_canada_people.py --year 1867
    python extract_canada_people.py --year 1890 --test
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
    extraction_method: str = "unknown"
    notes: str = ""  # For storing title information, multi-role info, etc.
    # Canada-specific fields
    is_acting: bool = False
    multi_role_id: Optional[str] = None  # Link multi-role entries


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
    """Section flagged for LLM extraction."""
    line_start: int
    line_end: int
    lines: List[str]
    reason: str
    context: Dict = field(default_factory=dict)


# Canada-specific constants
CANADA_PROVINCES = [
    'ONTARIO', 'QUEBEC', 'NOVA SCOTIA', 'NEW BRUNSWICK', 'MANITOBA',
    'BRITISH COLUMBIA', 'PRINCE EDWARD ISLAND', 'SASKATCHEWAN', 'ALBERTA',
    'UPPER CANADA', 'LOWER CANADA', 'CANADA EAST', 'CANADA WEST'
]

CANADA_FEDERAL_DEPARTMENTS = [
    'Cabinet', 'Privy Council', 'Executive Council',
    'Governor-General', 'Provincial Secretary', 'Finance Minister',
    'Customs Department', 'Public Works', 'General Post-Office',
    'Crown Law Department', 'Crown Lands', 'Bureau of Agriculture',
    'Militia Department', 'Geological Department', 'Legislature',
    'Supreme Court', 'Court of Exchequer', 'Admiralty Court'
]

# Titles that should be extracted and stored in notes field
CANADA_TITLES = [
    'Rt. Hon.', 'Right Hon.', 'Hon.', 'Sir', 'Kt.', 'K.C.M.G.', 'G.C.M.G.',
    'C.M.G.', 'C.B.', 'P.C.', 'Q.C.', 'K.C.', 'LL.D.', 'D.C.L.', 'M.D.',
    'Lt.-Col.', 'Colonel', 'Major-General', 'Captain', 'Rev.', 'Very Rev.',
    'Ven.', 'Right Rev.', 'Rt. Rev.', 'D.D.', 'Bart.', 'Esq.'
]

# Section headers that indicate non-people data to skip
SKIP_SECTION_MARKERS = [
    'Customs Tariff', 'Revenue and Expenditure', 'Exports', 'Imports',
    'Public Debt', 'Finances', 'Shipping Entered', 'Railways', 'Telegraphs',
    'Canals', 'Currency and Banking', 'Post Office', 'Defence', 'Chief Towns',
    'Population of Dominion', 'Industry', 'Situation and Area', 'History',
    'Constitution', 'Local Government'
]


class CanadaExtractionOrchestrator:
    """Main orchestrator for Canada hybrid extraction."""

    def __init__(self, github_base_url: str = "https://github.com/jburnford/colonial_office_list/blob/main"):
        self.github_base_url = github_base_url
        self.analysis_cache = {}

    def extract_from_file(self, file_path: str, colony: str, year: int, use_cache: bool = True) -> Tuple[List[Person], Dict]:
        """
        Extract all people from a single Canada file using hybrid approach.

        Returns:
            (people, metadata) tuple
        """
        print(f"\n{'='*70}")
        print(f"Processing {colony} {year}: {file_path}")
        print(f"PHASE 1: Federal departments only (Cabinet, Courts, Departments)")
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
            'canada_specific': {
                'multi_role_entries': 0,
                'acting_officials': 0,
                'skip_sections_detected': 0,
                'currency': '£' if year < 1870 else '$'
            }
        }

        # PHASE 1: File Analysis
        print("\nPHASE 1: Analyzing file structure...")
        file_analysis = self._analyze_file_structure(lines, colony, year, file_path, use_cache)
        metadata['phases']['analysis'] = {
            'people_section': f"lines {file_analysis.people_section_start}-{file_analysis.people_section_end}",
            'departments': len(file_analysis.departments),
            'provinces': len(file_analysis.provinces),
            'currency': file_analysis.salary_currency
        }

        # PHASE 2: Pattern-based extraction (Canada-specific)
        print("\nPHASE 2: Pattern-based extraction (Canada Federal)...")
        pattern_extractor = CanadaPatternExtractor(self.github_base_url)
        preliminary, flagged = pattern_extractor.extract(
            lines, file_analysis, colony, year
        )
        print(f"  Extracted {len(preliminary)} people via patterns")
        print(f"  - Multi-role entries: {pattern_extractor.stats['multi_role_entries']}")
        print(f"  - Acting officials: {pattern_extractor.stats['acting_officials']}")
        print(f"  - Skip sections: {pattern_extractor.stats['skip_sections']}")
        print(f"  Flagged {len(flagged)} sections for LLM review")

        metadata['canada_specific']['multi_role_entries'] = pattern_extractor.stats['multi_role_entries']
        metadata['canada_specific']['acting_officials'] = pattern_extractor.stats['acting_officials']
        metadata['canada_specific']['skip_sections_detected'] = pattern_extractor.stats['skip_sections']
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
        Phase 1: Analyze Canada file structure.

        Canada files have extensive preamble and statistics. We need to:
        1. Find where people data starts (usually "Cabinet" or "Civil Establishment")
        2. Identify sections to skip (tariffs, statistics)
        3. Detect currency (£ vs $)
        """
        # Find people section - look for "Cabinet" or "Civil Establishment"
        start_idx = -1
        start_marker = ""

        for i, line in enumerate(lines):
            # Look for Cabinet section
            if re.search(r'^Cabinet\s*\.$', line.strip(), re.IGNORECASE):
                start_idx = i
                start_marker = "Cabinet"
                break
            # Or Civil Establishment
            if re.search(r'^Civil Establishment', line.strip(), re.IGNORECASE):
                start_idx = i
                start_marker = "Civil Establishment"
                break
            # Or Executive Council
            if re.search(r'^Executive Council', line.strip(), re.IGNORECASE):
                start_idx = i
                start_marker = "Executive Council"
                break

        if start_idx == -1:
            # Fallback: look for first mention of Governor-General
            for i, line in enumerate(lines):
                if re.search(r'Governor-General', line, re.IGNORECASE):
                    start_idx = max(0, i - 5)
                    start_marker = "Governor-General (detected)"
                    break

        if start_idx == -1:
            start_idx = len(lines) // 2  # Final fallback

        # Detect departments and provinces mentioned in file
        departments = set()
        provinces = set()

        for line in lines[start_idx:]:
            # Check for known departments
            for dept in CANADA_FEDERAL_DEPARTMENTS:
                if dept.lower() in line.lower():
                    departments.add(dept)

            # Check for province markers
            for prov in CANADA_PROVINCES:
                # Look for "PROVINCE OF X" or just province name in headers
                if re.search(rf'\b{prov}\b', line, re.IGNORECASE):
                    provinces.add(prov)

        # Detect currency from sample of lines
        currency = "£ sterling"
        for line in lines[start_idx:min(start_idx + 200, len(lines))]:
            if re.search(r'\$\d+', line):
                currency = "$ (Canadian dollars)"
                break

        return FileAnalysis(
            file_path=file_path,
            colony=colony,
            year=year,
            people_section_start=start_idx,
            people_section_end=len(lines),
            start_marker=start_marker,
            departments=sorted(list(departments))[:30],
            provinces=sorted(list(provinces)),
            primary_format="Role, Name, Salary (with multi-role patterns)",
            has_lists=True,
            has_ditto=True,
            salary_currency=currency,
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
        validator = CanadaValidator()
        return validator.validate(people, lines, file_analysis)


class CanadaPatternExtractor:
    """
    Canada-specific pattern extractor.

    Handles:
    - Multi-role entries ("Attorney-General and Minister of Militia")
    - Acting officials
    - Title extraction
    - Statistical section filtering
    - Currency detection (£ vs $)
    """

    def __init__(self, github_base_url: str):
        self.github_base_url = github_base_url
        self.current_department = None
        self.current_province = None
        self.last_role = None
        self.in_skip_section = False
        self.stats = {
            'multi_role_entries': 0,
            'acting_officials': 0,
            'skip_sections': 0
        }

    def extract(self, lines: List[str], file_analysis: FileAnalysis,
                colony: str, year: int) -> Tuple[List[Person], List[FlaggedSection]]:
        """Extract people using Canada-specific patterns."""

        people = []
        flagged = []

        start = file_analysis.people_section_start
        end = file_analysis.people_section_end

        for i in range(start, min(end, len(lines))):
            line = lines[i].strip()

            if not line:
                continue

            # Check if we're entering a skip section
            if self._should_skip_section(line):
                self.in_skip_section = True
                self.stats['skip_sections'] += 1
                continue

            # Check if we're exiting a skip section (entering a people section)
            if self.in_skip_section and self._is_people_section_start(line):
                self.in_skip_section = False

            # Skip lines in skip sections
            if self.in_skip_section:
                continue

            # Update context (department, province)
            self._update_context(line, file_analysis)

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

    def _should_skip_section(self, line: str) -> bool:
        """
        Detect if we're entering a section to skip (tariffs, statistics, etc.).

        Key patterns:
        - Section headers like "Customs Tariff", "Revenue and Expenditure"
        - Lines with "per cent", "per ton", "per lb" (tariff data)
        - Table headers with multiple "|" characters
        """
        # Check for skip section headers
        for marker in SKIP_SECTION_MARKERS:
            if marker.lower() in line.lower() and len(line) < 100:
                return True

        # Check for tariff patterns
        if re.search(r'per cent|per ton|per lb|per oz|p\. c\.t\.|p\. lb', line, re.IGNORECASE):
            return True

        # Check for table headers (multiple | characters)
        if line.count('|') >= 3:
            return True

        # Check for year columns (like "| 1879 | 1880 |")
        if re.search(r'\|\s*\d{4}\s*\|', line):
            return True

        return False

    def _is_people_section_start(self, line: str) -> bool:
        """
        Detect if we're entering a people section (exiting skip section).

        Look for section headers that indicate people data.
        """
        people_markers = [
            'Cabinet', 'Civil Establishment', 'Governor-General',
            'Provincial Secretary', 'Finance Minister', 'Customs Department',
            'Public Works', 'Post-Office', 'Crown Law', 'Crown Lands',
            'Militia Department', 'Legislature', 'Judicial', 'Legal Department',
            'Ecclesiastical Establishment', 'Supreme Court', 'Privy Council'
        ]

        for marker in people_markers:
            if marker.lower() in line.lower() and len(line) < 100:
                return True

        return False

    def _update_context(self, line: str, file_analysis: FileAnalysis):
        """Update department/province context."""
        # Check if this is a department header
        # Canada department headers are often short lines ending with "."
        if len(line) < 80 and line.endswith('.'):
            for dept in file_analysis.departments:
                if dept.lower() in line.lower():
                    self.current_department = dept
                    return

        # Check if this is a province marker
        # Pattern: "PROVINCE OF ONTARIO" or just "ONTARIO"
        for prov in file_analysis.provinces:
            if re.search(rf'\bPROVINCE OF {prov}\b', line, re.IGNORECASE):
                self.current_province = prov
                return
            # Also check for standalone province names in section headers
            if prov in ['CANADA EAST', 'CANADA WEST', 'UPPER CANADA', 'LOWER CANADA']:
                if prov in line.upper():
                    self.current_province = prov
                    return

    def _extract_from_line(self, line: str, line_num: int,
                          colony: str, year: int,
                          file_analysis: FileAnalysis) -> List[Person]:
        """
        Extract person(s) from a line.

        Returns a list because multi-role entries create multiple Person records.
        """
        people = []

        # First check for multi-role entries
        # e.g., "John A. Macdonald, Attorney-General of Upper Canada and Minister of Militia"
        multi_role = self._extract_multi_role(line, line_num, colony, year, file_analysis)
        if multi_role:
            people.extend(multi_role)
            return people

        # Check for acting officials
        # e.g., "Acting Governor, Sir John Michel"
        acting = self._extract_acting_official(line, line_num, colony, year, file_analysis)
        if acting:
            people.extend(acting)
            return people

        # Standard patterns
        standard = self._extract_standard_patterns(line, line_num, colony, year, file_analysis)
        if standard:
            people.extend(standard)

        return people

    def _extract_multi_role(self, line: str, line_num: int,
                           colony: str, year: int,
                           file_analysis: FileAnalysis) -> Optional[List[Person]]:
        """
        Extract multi-role entries like:
        "John A. Macdonald, Attorney-General of Upper Canada and Minister of Militia."
        "Premier and Attorney-General, Hon. O. Mowat, Q.C."

        Creates separate Person records for each role.
        """
        if ' and ' not in line:
            return None

        # Pattern 1: Name, Role1 and Role2, Salary
        # e.g., "John A. Macdonald, Attorney-General of Upper Canada and Minister of Militia, 1,250l."
        # FIX: Use greedy matching for name and extract titles
        pattern1 = r'^([A-Z][^,]+),\s+([^,\.]+\s+and\s+[^,\.]+)(?:[,\.]?\s*([£\$\d,]+[l\.]?))?'
        match = re.search(pattern1, line)

        if match:
            name_with_titles = match.group(1).strip()
            combined_role = match.group(2).strip()
            salary = match.group(3).strip() if match.group(3) else None

            # Check if combined_role contains role keywords
            if self._contains_role_keywords(combined_role):
                # Extract titles from name (like standard patterns do)
                clean_name, titles = self._extract_titles(name_with_titles)

                # Split on " and "
                roles = re.split(r'\s+and\s+', combined_role, flags=re.IGNORECASE)

                if len(roles) >= 2:
                    people = []
                    multi_role_id = f"multi_{line_num}"

                    # Build notes with titles and multi-role info
                    notes_parts = [f"Multi-role: {combined_role}"]
                    if titles:
                        notes_parts.append(f"Titles: {', '.join(titles)}")
                    notes = "; ".join(notes_parts)

                    for role in roles:
                        role = role.strip()
                        person = self._create_person(
                            clean_name,  # Use clean name without titles
                            role,
                            salary,
                            line, line_num, colony, year,
                            confidence=0.88,
                            method='canada_multi_role',
                            multi_role_id=multi_role_id,
                            notes=notes
                        )
                        people.append(person)

                    self.stats['multi_role_entries'] += 1
                    return people

        # Pattern 2: Role1 and Role2, Name, Salary
        # e.g., "Premier and Attorney-General, Hon. O. Mowat, Q.C., 1,500l."
        # FIX: Use .+? with end anchor to capture full name including titles with commas
        pattern2 = r'^([^,]+\s+and\s+[^,]+),\s+([A-Z].+?)(?:,\s*([£\$]?\s*[\d,]+[l\.]?)\s*)?\s*\.?\s*$'
        match = re.search(pattern2, line)

        if match:
            combined_role = match.group(1).strip()
            name_with_titles = match.group(2).strip()
            salary = match.group(3).strip() if match.group(3) else None

            # Check if combined_role contains role keywords
            if self._contains_role_keywords(combined_role):
                # Extract titles from name (like standard patterns do)
                clean_name, titles = self._extract_titles(name_with_titles)

                # Split on " and "
                roles = re.split(r'\s+and\s+', combined_role, flags=re.IGNORECASE)

                if len(roles) >= 2:
                    people = []
                    multi_role_id = f"multi_{line_num}"

                    # Build notes with titles and multi-role info
                    notes_parts = [f"Multi-role: {combined_role}"]
                    if titles:
                        notes_parts.append(f"Titles: {', '.join(titles)}")
                    notes = "; ".join(notes_parts)

                    for role in roles:
                        role = role.strip()
                        person = self._create_person(
                            clean_name,  # Use clean name without titles
                            role,
                            salary,
                            line, line_num, colony, year,
                            confidence=0.88,
                            method='canada_multi_role',
                            multi_role_id=multi_role_id,
                            notes=notes
                        )
                        people.append(person)

                    self.stats['multi_role_entries'] += 1
                    return people

        return None

    def _contains_role_keywords(self, text: str) -> bool:
        """Check if text contains role keywords."""
        role_keywords = [
            'Attorney-General', 'Minister', 'Secretary', 'Commissioner', 'Chief',
            'Judge', 'Justice', 'Premier', 'Governor', 'President', 'Director',
            'Inspector', 'Clerk', 'Deputy', 'Assistant', 'Receiver', 'Auditor',
            'Accountant', 'Superintendent', 'Postmaster', 'Speaker', 'Chaplain',
            'Bishop', 'Dean', 'Archdeacon', 'Adjutant'
        ]

        return any(kw.lower() in text.lower() for kw in role_keywords)

    def _extract_acting_official(self, line: str, line_num: int,
                                colony: str, year: int,
                                file_analysis: FileAnalysis) -> Optional[List[Person]]:
        """
        Extract acting officials like:
        "Acting Governor, Sir John Michel."
        """
        # Pattern: "Acting Role, Name"
        pattern = r'^Acting\s+([^,]+?),\s+([A-Z][^,\.]+)'
        match = re.search(pattern, line, re.IGNORECASE)

        if match:
            role = match.group(1).strip()
            name = match.group(2).strip()

            person = self._create_person(
                name,
                role,
                None,
                line, line_num, colony, year,
                confidence=0.85,
                method='canada_acting',
                is_acting=True,
                notes="Acting"
            )

            self.stats['acting_officials'] += 1
            return [person]

        return None

    def _extract_standard_patterns(self, line: str, line_num: int,
                                   colony: str, year: int,
                                   file_analysis: FileAnalysis) -> List[Person]:
        """Extract using standard Canada patterns."""
        people = []

        # Pattern 1: Role, Name (with titles), Salary
        # e.g., "Colonial Secretary, Eyre Hutson, 750l."
        # e.g., "Governor-General, Viscount Monck, 7,000l."
        # e.g., "Chief Justice Queen's Bench, J. F. J. Duval, 1,250l."
        pattern1 = r'^([A-Z][^,]{3,70}?),\s+([A-Z][^,]+?),\s+([£\$]?\s*[\d,]+[l\.]?)'
        match = re.search(pattern1, line)
        if match:
            role, name, salary = match.groups()

            # Extract titles from name
            clean_name, titles = self._extract_titles(name.strip())

            person = self._create_person(
                clean_name,
                role.strip(),
                salary.strip(),
                line, line_num, colony, year,
                confidence=0.9,
                method='canada_pattern1',
                notes=f"Titles: {', '.join(titles)}" if titles else ""
            )
            people.append(person)
            return people

        # Pattern 2: Name, Salary (role from context)
        # e.g., "J. Swan, 600l."
        pattern2 = r'^([A-Z][^,]{2,40}?),\s+([£\$]?\s*[\d,]+[l\.]?)'
        match = re.search(pattern2, line)
        if match:
            name, salary = match.groups()
            role = self.last_role if self.last_role else "Unknown"

            clean_name, titles = self._extract_titles(name.strip())

            person = self._create_person(
                clean_name,
                role,
                salary.strip(),
                line, line_num, colony, year,
                confidence=0.7 if self.last_role else 0.5,
                method='canada_pattern2',
                notes=f"Titles: {', '.join(titles)}" if titles else ""
            )
            people.append(person)
            return people

        # Pattern 3: Role, Name (no salary listed)
        # e.g., "Bishop of Quebec, Right Rev. J. W. Williams, D.D."
        # e.g., "Puisne Judges, ditto, J. C. Morrison, J. H. Hagarty, 1,000l. each."
        pattern3 = r'^([A-Z][^,]{3,60}?),\s+([A-Z][^,\.]+?)(?:,\s+([£\$]?\s*[\d,]+[l\.]?|each))?'
        match = re.search(pattern3, line)
        if match and not re.search(r'(Department|Office|Establishment|Province)', line):
            role, name, salary = match.groups()

            # Skip if name looks like it might be a continuation of role
            if len(name.split()) >= 2 or salary:
                clean_name, titles = self._extract_titles(name.strip())

                person = self._create_person(
                    clean_name,
                    role.strip(),
                    salary.strip() if salary and salary != 'each' else None,
                    line, line_num, colony, year,
                    confidence=0.75,
                    method='canada_pattern3',
                    notes=f"Titles: {', '.join(titles)}" if titles else ""
                )
                people.append(person)
                return people

        return people

    def _extract_titles(self, name: str) -> Tuple[str, List[str]]:
        """
        Extract titles from a name string.

        Returns:
            (clean_name, list_of_titles)
        """
        titles = []

        # Check for each known title
        # Note: Don't use \b after title because it doesn't work with periods
        for title in CANADA_TITLES:
            # Use word boundary only at start to avoid partial matches
            pattern = rf'\b{re.escape(title)}'
            if re.search(pattern, name, re.IGNORECASE):
                titles.append(title)

        # Remove titles from name
        # Process longer titles first to avoid partial matches (e.g., K.C.M.G. before K.C.)
        clean_name = name
        for title in sorted(CANADA_TITLES, key=len, reverse=True):
            pattern = rf'\b{re.escape(title)}[,\s]*'
            clean_name = re.sub(pattern, '', clean_name, flags=re.IGNORECASE)

        # Clean up extra whitespace and punctuation
        clean_name = re.sub(r'\s+', ' ', clean_name).strip().rstrip(',.')

        return clean_name, titles

    def _create_person(self, name: str, role: str, salary: Optional[str],
                      line: str, line_num: int, colony: str, year: int,
                      confidence: float, method: str,
                      is_acting: bool = False,
                      multi_role_id: Optional[str] = None,
                      notes: str = "") -> Person:
        """Create a Person object with Canada-specific fields."""
        # Build location
        location_parts = [colony]

        # Add "Federal" for federal positions (unless it's provincial)
        if not self.current_province or self.current_province in ['UPPER CANADA', 'LOWER CANADA']:
            location_parts.append('Federal')
        elif self.current_province:
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

        # Has a salary or number that looks like salary
        has_money = bool(re.search(r'(\d{2,}[l\.]|[£\$]\s*\d+)', line))

        # Not a header or table row
        not_header = not re.search(r'^(Year|Total|Male|Female|\||Table|Import|Export|Province)', line)

        # Not a skip section
        not_skip = not self._should_skip_section(line)

        return has_name and (has_money or len(line) > 40) and not_header and not_skip


class CanadaValidator:
    """Validate and clean extracted Canada people."""

    def __init__(self):
        # Known false positive patterns for Canada
        self.location_names = {
            'Ottawa', 'Montreal', 'Toronto', 'Quebec', 'Halifax', 'Vancouver',
            'Winnipeg', 'Ontario', 'Manitoba', 'Alberta', 'Victoria',
            'Kingston', 'Hamilton', 'London', 'St. John', 'Charlottetown'
        }
        self.qualifications = {
            'M.D.', 'M.R.C.S.', 'F.R.C.S.', 'A.M.I.C.E.', 'M.I.C.E.',
            'B.A.', 'M.A.', 'LL.D.', 'Q.C.', 'K.C.', 'C.M.G.', 'K.C.M.G.',
            'D.C.L.', 'D.D.', 'P.C.', 'G.C.M.G.', 'C.B.'
        }
        self.placeholders = {
            'Ditto', 'ditto', 'vacant', 'Vacant', 'acting', 'Acting',
            'Grade I', 'Grade II', 'Grade III', 'Esq.', 'each'
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

        # Check if name is just a number or currency
        if re.match(r'^[\d,£\$\.l]+$', name):
            return True

        return False

    def _clean_name(self, name: str) -> str:
        """Clean up name field."""
        # Remove common prefixes
        name = re.sub(r'^(&c\.,|Ditto,|The|Esq\.,?)\s+', '', name)

        # Remove trailing punctuation
        name = name.rstrip('.,;')

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
            if person.multi_role_id:
                key = (person.name.lower(), person.role.lower(), person.year, person.multi_role_id)
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
        description='Extract people from Canada Colonial Office Lists (Phase 1: Federal)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python extract_canada_people.py --year 1867
  python extract_canada_people.py --year 1890
  python extract_canada_people.py --test
        """
    )
    parser.add_argument('--year', type=int, help='Specific year')
    parser.add_argument('--output', default='canada_people_extracted.json', help='Output file')
    parser.add_argument('--test', action='store_true', help='Test mode: run on 1867 only')

    args = parser.parse_args()

    orchestrator = CanadaExtractionOrchestrator()

    # Test mode - use 1867 file (simplest)
    if args.test or not args.year:
        print("Running in TEST mode (1867 - simplest Canada file)...")
        test_file = "/home/user/colonial_office_list/output_3/1867_manual_parsed/canada.txt"

        if not os.path.exists(test_file):
            print(f"Error: Test file not found: {test_file}")
            return

        people, metadata = orchestrator.extract_from_file(
            test_file, "CANADA", 1867
        )

        print(f"\n{'='*70}")
        print("EXTRACTION COMPLETE (TEST - 1867)")
        print('='*70)
        print(f"Extracted {len(people)} people")
        print(f"Average confidence: {metadata['phases']['validation']['avg_confidence']:.2f}")
        print(f"\nCanada-specific stats:")
        print(f"  Currency: {metadata['canada_specific']['currency']}")
        print(f"  Multi-role entries: {metadata['canada_specific']['multi_role_entries']}")
        print(f"  Acting officials: {metadata['canada_specific']['acting_officials']}")
        print(f"  Skip sections detected: {metadata['canada_specific']['skip_sections_detected']}")

        # Show sample records
        print(f"\nSample records (showing variety):")

        # Group by department to show variety
        by_dept = {}
        for person in people:
            dept = person.department or "General"
            if dept not in by_dept:
                by_dept[dept] = []
            by_dept[dept].append(person)

        shown = 0
        for dept, persons in sorted(by_dept.items()):
            if shown >= 10:
                break
            print(f"\n--- {dept} ---")
            for person in persons[:2]:  # Show 2 per department
                if shown >= 10:
                    break
                shown += 1
                print(f"{shown}. {person.name}")
                print(f"   Role: {person.role}")
                print(f"   Location: {person.location}")
                print(f"   Salary: {person.salary}")
                print(f"   Method: {person.extraction_method}")
                if person.notes:
                    print(f"   Notes: {person.notes}")

        # Save results
        results = {
            'metadata': metadata,
            'people': [asdict(p) for p in people]
        }

        output_file = 'canada_1867_test.json'
        with open(output_file, 'w') as f:
            json.dump(results, f, indent=2)

        print(f"\nSaved to {output_file}")
        return

    # Process specific year
    if args.year:
        import glob

        # Try different patterns for Canada files
        patterns = [
            f"output_3/*{args.year}*/canada.txt",
            f"output_3/*{args.year}*/canada.md",
            f"output_3/*{args.year}*/dominion_of_canada.txt",
            f"output_3/*{args.year}*/CANADA.txt"
        ]

        files = []
        for pattern in patterns:
            found = glob.glob(pattern)
            if found:
                files.extend(found)
                break

        if files:
            people, metadata = orchestrator.extract_from_file(
                files[0], "CANADA", args.year
            )

            print(f"\n{'='*70}")
            print("EXTRACTION COMPLETE")
            print('='*70)
            print(f"Extracted {len(people)} people")
            print(f"Average confidence: {metadata['phases']['validation']['avg_confidence']:.2f}")
            print(f"\nCanada-specific stats:")
            print(f"  Currency: {metadata['canada_specific']['currency']}")
            print(f"  Multi-role entries: {metadata['canada_specific']['multi_role_entries']}")
            print(f"  Acting officials: {metadata['canada_specific']['acting_officials']}")

            # Save results
            results = {
                'metadata': metadata,
                'people': [asdict(p) for p in people]
            }

            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2)

            print(f"Saved to {args.output}")
        else:
            print(f"No file found for CANADA {args.year}")
            print("Tried patterns:", patterns)

    else:
        print("Use --year YYYY or --test")


if __name__ == "__main__":
    main()
