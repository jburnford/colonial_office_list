#!/usr/bin/env python3
"""
Colonial Office List - Hybrid Python-LLM People Extraction System (v2)

This version uses LLM agents (via Tasks) for intelligent analysis and extraction,
while Python handles orchestration, validation, and reproducibility.

Architecture:
1. FileAnalyzer (LLM) - Analyzes file structure and patterns
2. PatternExtractor (Python) - Applies regex patterns guided by analysis
3. LLMExtractor (LLM) - Handles complex cases flagged by Python
4. Validator (Python + LLM) - Validates and merges results

Usage:
    python extract_people_v2.py --colony CEYLON --year 1867
    python extract_people_v2.py --colony CEYLON --year-range 1867-1920
    python extract_people_v2.py --colony CEYLON --all
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


class ExtractionOrchestrator:
    """Main orchestrator for hybrid extraction."""

    def __init__(self, github_base_url: str = "https://github.com/jburnford/colonial_office_list/blob/main"):
        self.github_base_url = github_base_url
        self.analysis_cache = {}  # Cache file analyses

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
            'phases': {}
        }

        # PHASE 1: File Analysis (will be LLM via Task)
        print("\nPHASE 1: Analyzing file structure...")
        file_analysis = self._analyze_file_structure(lines, colony, year, file_path, use_cache)
        metadata['phases']['analysis'] = {
            'people_section': f"lines {file_analysis.people_section_start}-{file_analysis.people_section_end}",
            'departments': len(file_analysis.departments),
            'provinces': len(file_analysis.provinces)
        }

        # PHASE 2: Pattern-based extraction (Python)
        print("\nPHASE 2: Pattern-based extraction...")
        pattern_extractor = PatternExtractor(self.github_base_url)
        preliminary, flagged = pattern_extractor.extract(
            lines, file_analysis, colony, year
        )
        print(f"  Extracted {len(preliminary)} people via patterns")
        print(f"  Flagged {len(flagged)} sections for LLM review")
        metadata['phases']['pattern_extraction'] = {
            'extracted': len(preliminary),
            'flagged_sections': len(flagged)
        }

        # PHASE 3: LLM extraction for flagged sections (will be LLM via Task)
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
        Phase 1: Analyze file structure.
        For now, uses simple heuristics. Will be replaced with LLM Task.
        """
        # Simple implementation for now - will be replaced with LLM Task
        # This is the PLACEHOLDER for Task-based analysis

        # Find people section
        start_idx = -1
        for i, line in enumerate(lines):
            if re.search(r'(Civil Establishment|Executive Council|Legislative Council)', line, re.IGNORECASE):
                start_idx = i
                break

        if start_idx == -1:
            start_idx = len(lines) // 2  # Fallback

        # Simple department detection
        departments = []
        provinces = []
        for line in lines[start_idx:]:
            # Department patterns
            if re.search(r"(Secretary'?s? Office|Department|Establishment)", line):
                dept = line.strip().rstrip('.')
                if dept and len(dept) < 80:
                    departments.append(dept)

            # Province patterns
            if re.search(r"Province", line, re.IGNORECASE):
                prov = line.strip().rstrip('.')
                if prov and len(prov) < 50:
                    provinces.append(prov)

        return FileAnalysis(
            file_path=file_path,
            colony=colony,
            year=year,
            people_section_start=start_idx,
            people_section_end=len(lines),
            start_marker="Civil Establishment (detected)",
            departments=list(set(departments))[:20],  # Dedupe and limit
            provinces=list(set(provinces)),
            primary_format="Role, Name, Salary",
            has_lists=True,  # Assume yes
            has_ditto=True,  # Assume yes
            salary_currency="£ sterling" if year < 1870 else "Rs. (rupees)",
            ocr_quality="good"
        )

    def _llm_extract_flagged(self, flagged: List[FlaggedSection],
                            file_analysis: FileAnalysis,
                            lines: List[str]) -> List[Person]:
        """
        Phase 3: Use Tasks (Claude Code itself) to extract from flagged sections.

        This uses Claude Code's Task tool, so I (Claude) do the extraction
        work directly without needing external API calls.
        """
        if not flagged:
            print("  No sections flagged for LLM extraction")
            return []

        print(f"  Using Claude Code Tasks for extraction (no external API needed)")

        # Use the Task-based extractor
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
            # Fallback to original llm_extractor if task version not available
            try:
                from llm_extractor import extract_from_flagged_sections
                import os

                backend = os.environ.get('LLM_BACKEND', 'placeholder')
                print(f"  Fallback: Using LLM backend: {backend}")

                return extract_from_flagged_sections(
                    flagged_sections=flagged,
                    file_analysis=file_analysis,
                    all_lines=lines,
                    colony=file_analysis.colony,
                    year=file_analysis.year,
                    llm_backend=backend
                )
            except Exception as e:
                print(f"  Warning: LLM extraction failed: {e}")
                return []
        except Exception as e:
            print(f"  Error in Task extraction: {e}")
            return []

    def _validate_and_merge(self, people: List[Person], lines: List[str],
                           file_analysis: FileAnalysis) -> List[Person]:
        """
        Phase 4: Validate and merge extractions.
        """
        validator = Validator()
        return validator.validate(people, lines, file_analysis)


class PatternExtractor:
    """Extract people using regex patterns guided by file analysis."""

    def __init__(self, github_base_url: str):
        self.github_base_url = github_base_url
        self.current_department = None
        self.current_province = None
        self.last_role = None

    def extract(self, lines: List[str], file_analysis: FileAnalysis,
                colony: str, year: int) -> Tuple[List[Person], List[FlaggedSection]]:
        """Extract people using patterns, flag complex sections for LLM."""

        people = []
        flagged = []

        start = file_analysis.people_section_start
        end = file_analysis.people_section_end

        # Process people section
        for i in range(start, min(end, len(lines))):
            line = lines[i].strip()

            if not line:
                continue

            # Check for context markers
            self._update_context(line, file_analysis)

            # Try to extract person
            person = self._extract_person_from_line(
                line, i, colony, year, file_analysis
            )

            if person:
                people.append(person)
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

        # Detect multi-line list sections
        list_sections = self._detect_list_sections(lines, start, end)
        flagged.extend(list_sections)

        return people, flagged

    def _update_context(self, line: str, file_analysis: FileAnalysis):
        """Update department/province context."""
        # Check if this is a department header
        for dept in file_analysis.departments:
            if dept.lower() in line.lower():
                self.current_department = dept
                return

        # Check if this is a province marker
        for prov in file_analysis.provinces:
            if prov.lower() in line.lower():
                self.current_province = prov
                return

    def _extract_person_from_line(self, line: str, line_num: int,
                                  colony: str, year: int,
                                  file_analysis: FileAnalysis) -> Optional[Person]:
        """Try to extract a person from a line using regex patterns."""

        # Pattern 1: Role, Name (with quals), Salary
        # e.g., "Colonial Secretary, W. G. Gibson, 2,000l."
        pattern1 = r'^([A-Z][^,]{3,50}?),\s+([A-Z][^,]+?),\s+([0-9,]+[l\.]|Rs\.\s*[0-9,]+)'
        match = re.search(pattern1, line)
        if match:
            role, name, salary = match.groups()
            return self._create_person(
                name.strip(),
                role.strip(),
                salary.strip(),
                line, line_num, colony, year,
                confidence=0.9,
                method='regex_pattern1'
            )

        # Pattern 2: Name, Salary (role from context)
        # e.g., "J. Swan, 600l."
        pattern2 = r'^([A-Z][^,]{2,40}?),\s+([0-9,]+[l\.]|Rs\.\s*[0-9,]+)'
        match = re.search(pattern2, line)
        if match:
            name, salary = match.groups()
            role = self.last_role if self.last_role else "Unknown"
            return self._create_person(
                name.strip(),
                role,
                salary.strip(),
                line, line_num, colony, year,
                confidence=0.7 if self.last_role else 0.5,
                method='regex_pattern2'
            )

        return None

    def _create_person(self, name: str, role: str, salary: str,
                      line: str, line_num: int, colony: str, year: int,
                      confidence: float, method: str) -> Person:
        """Create a Person object."""
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
            extraction_method=method
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
        not_header = not re.search(r'^(Year|Total|Male|Female|\|)', line)

        return has_name and has_money and not_header and len(line) > 15

    def _detect_list_sections(self, lines: List[str], start: int, end: int) -> List[FlaggedSection]:
        """Detect multi-line list sections that need LLM extraction."""
        flagged = []

        # Look for list headers like "Writers, commencing at..."
        list_pattern = r'^(Writers|Cadets|Clerks|Officers|Assistants)[,\s]+(commencing|at)'

        for i in range(start, end):
            if re.search(list_pattern, lines[i], re.IGNORECASE):
                # Found a list header - flag next 3-5 lines
                list_lines = []
                for j in range(i + 1, min(i + 6, end)):
                    if lines[j].strip() and not re.search(r'^\w+.*Office|Department', lines[j]):
                        list_lines.append(lines[j])
                    else:
                        break

                if list_lines:
                    flagged.append(FlaggedSection(
                        line_start=i + 1,
                        line_end=i + len(list_lines),
                        lines=list_lines,
                        reason="comma_separated_list",
                        context={'header': lines[i].strip()}
                    ))

        return flagged


class Validator:
    """Validate and clean extracted people."""

    def __init__(self):
        # Known false positive patterns
        self.location_names = {
            'Colombo', 'Kandy', 'Galle', 'Jaffna', 'Trincomalee',
            'Negombo', 'Nuwera Ellia', 'Batticaloa'
        }
        self.qualifications = {
            'M.D.', 'M.R.C.S.', 'F.R.C.S.', 'A.M.I.C.E.', 'M.I.C.E.',
            'B.A.', 'M.A.', 'LL.D.', 'Q.C.', 'K.C.'
        }
        self.placeholders = {
            'Ditto', 'ditto', 'vacant', 'Vacant', 'acting', 'Acting',
            'Grade I', 'Grade II', 'Grade III'
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

        # Remove duplicates
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
        if len(name.split()) == 1 and name.isupper():
            return True

        return False

    def _clean_name(self, name: str) -> str:
        """Clean up name field."""
        # Remove common prefixes
        name = re.sub(r'^(&c\.,|Ditto,|The)\s+', '', name)

        # Remove footnote markers
        name = re.sub(r'[†*]', '', name)

        # Remove extra whitespace
        name = ' '.join(name.split())

        return name.strip()

    def _deduplicate(self, people: List[Person]) -> List[Person]:
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


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description='Extract people from Colonial Office Lists')
    parser.add_argument('--colony', required=True, help='Colony name (e.g., CEYLON)')
    parser.add_argument('--year', type=int, help='Specific year')
    parser.add_argument('--year-range', help='Year range (e.g., 1867-1920)')
    parser.add_argument('--all', action='store_true', help='Process all years')
    parser.add_argument('--output', default='people_data_v2.json', help='Output file')

    args = parser.parse_args()

    orchestrator = ExtractionOrchestrator()

    # For now, just demonstrate with one file
    if args.year:
        # Find file for this year
        file_pattern = f"output_3/*{args.year}*/*{args.colony.lower()}*"
        import glob
        files = glob.glob(file_pattern)

        if files:
            people, metadata = orchestrator.extract_from_file(
                files[0], args.colony, args.year
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

            with open(args.output, 'w') as f:
                json.dump(results, f, indent=2)

            print(f"Saved to {args.output}")
        else:
            print(f"No file found for {args.colony} {args.year}")

    else:
        print("Please specify --year, --year-range, or --all")


if __name__ == "__main__":
    main()
