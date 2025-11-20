#!/usr/bin/env python3
"""
LLM-based extraction for complex/flagged sections of Colonial Office Lists.

This module handles sections that are too complex for regex patterns,
using LLM intelligence to extract structured people data.

Usage:
    from llm_extractor import extract_from_flagged_sections

    people = extract_from_flagged_sections(
        flagged_sections=flagged,
        file_analysis=analysis,
        all_lines=lines,
        colony="CEYLON",
        year=1867
    )
"""

import json
import re
import os
from typing import List, Dict, Optional, Any
from dataclasses import dataclass, field

# Import Person and related classes from extract_people_v2
# In production, these would be imported, but included here for clarity
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


@dataclass
class FlaggedSection:
    """Section flagged for LLM extraction."""
    line_start: int
    line_end: int
    lines: List[str]
    reason: str
    context: Dict = field(default_factory=dict)


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


class LLMExtractor:
    """Extract people from complex sections using LLM intelligence."""

    def __init__(self, llm_backend: str = "placeholder"):
        """
        Initialize LLM extractor.

        Args:
            llm_backend: Backend to use ('anthropic', 'ollama', 'openai', 'placeholder')
        """
        self.llm_backend = llm_backend
        self.extraction_stats = {
            'total_sections': 0,
            'successful_extractions': 0,
            'failed_extractions': 0,
            'total_people_extracted': 0
        }

    def extract_from_flagged_sections(
        self,
        flagged_sections: List[FlaggedSection],
        file_analysis: FileAnalysis,
        all_lines: List[str],
        colony: str,
        year: int
    ) -> List[Person]:
        """
        Main function: Extract people from all flagged sections.

        Args:
            flagged_sections: List of sections that need LLM extraction
            file_analysis: File structure analysis
            all_lines: Complete file content (for context)
            colony: Colony name
            year: Year

        Returns:
            List of Person objects extracted from flagged sections
        """
        print(f"\n  Processing {len(flagged_sections)} flagged sections...")

        all_extracted = []

        for idx, section in enumerate(flagged_sections, 1):
            print(f"    Section {idx}/{len(flagged_sections)}: {section.reason} (lines {section.line_start}-{section.line_end})")

            try:
                # Extract people from this section
                people = self._extract_from_section(
                    section=section,
                    file_analysis=file_analysis,
                    all_lines=all_lines,
                    colony=colony,
                    year=year
                )

                all_extracted.extend(people)
                self.extraction_stats['successful_extractions'] += 1
                self.extraction_stats['total_people_extracted'] += len(people)

                print(f"      → Extracted {len(people)} people")

            except Exception as e:
                print(f"      → Failed: {str(e)}")
                self.extraction_stats['failed_extractions'] += 1

        self.extraction_stats['total_sections'] = len(flagged_sections)

        return all_extracted

    def _extract_from_section(
        self,
        section: FlaggedSection,
        file_analysis: FileAnalysis,
        all_lines: List[str],
        colony: str,
        year: int
    ) -> List[Person]:
        """Extract people from a single flagged section."""

        # Build context-aware prompt based on flag reason
        prompt = self._build_prompt(
            section=section,
            file_analysis=file_analysis,
            all_lines=all_lines,
            colony=colony,
            year=year
        )

        # Call LLM with prompt
        llm_response = self._call_llm(prompt)

        # Parse LLM response into Person objects
        people = self._parse_llm_response(
            response=llm_response,
            section=section,
            colony=colony,
            year=year,
            file_analysis=file_analysis
        )

        return people

    def _build_prompt(
        self,
        section: FlaggedSection,
        file_analysis: FileAnalysis,
        all_lines: List[str],
        colony: str,
        year: int
    ) -> str:
        """
        Build a context-aware prompt for LLM extraction.

        The prompt includes:
        - Context (department, province, last_role)
        - Surrounding lines for additional context
        - Specific instructions based on flag reason
        - Expected JSON output format
        """

        # Get context from section
        context = section.context
        department = context.get('department', 'Unknown')
        province = context.get('province', '')
        last_role = context.get('last_role', '')
        header = context.get('header', '')

        # Get surrounding context (2-3 lines before/after)
        context_before = self._get_context_lines(
            all_lines,
            section.line_start - 3,
            section.line_start
        )
        context_after = self._get_context_lines(
            all_lines,
            section.line_end + 1,
            section.line_end + 4
        )

        # Build section text with line numbers
        section_text = ""
        for i, line in enumerate(section.lines):
            line_num = section.line_start + i + 1  # 1-indexed
            section_text += f"Line {line_num}: {line}\n"

        # Build prompt based on flag reason
        if section.reason == "comma_separated_list":
            instruction = self._build_list_instruction(header, last_role)
        elif section.reason == "pattern_match_failed":
            instruction = self._build_pattern_failed_instruction(last_role)
        else:
            instruction = "Extract all people mentioned with their roles and salaries."

        # Construct full prompt
        prompt = f"""Extract all people from this section of a Colonial Office List from {colony} ({year}).

**CONTEXT:**
Colony: {colony}
Year: {year}
Department: {department}
Province: {province}
{f'Section Header: {header}' if header else ''}
{f'Previous Role: {last_role}' if last_role else ''}

**LINES BEFORE (for context):**
{context_before}

**SECTION TO EXTRACT (lines {section.line_start + 1}-{section.line_end + 1}):**
{section_text}

**LINES AFTER (for context):**
{context_after}

**INSTRUCTIONS:**
{instruction}

**IMPORTANT NOTES:**
1. Handle OCR errors: "Æ." or "Ae." often means "A.", "tbe" means "the"
2. Names may have qualifications in parentheses like "(M.D.)" - include them
3. Salaries may be in format: "2,000l." or "Rs. 1,500" or "£200"
4. If a role continues across multiple lines, combine them
5. "Ditto" or repeated commas mean "same as above" - use the previous role
6. Each person must have at minimum: name and role (salary optional)

**OUTPUT FORMAT:**
Return ONLY a JSON array with this exact structure (no other text):

[
  {{
    "name": "Full Name (with any qualifications)",
    "role": "Job Title or Position",
    "salary": "Salary if mentioned, empty string otherwise",
    "line_number": line_number_where_found
  }}
]

If no people can be extracted, return an empty array: []

**JSON OUTPUT:**"""

        return prompt

    def _build_list_instruction(self, header: str, last_role: str) -> str:
        """Build instruction for comma-separated list sections."""
        return f"""This is a COMMA-SEPARATED LIST of names under the header: "{header}"

Each person in the list should be assigned the role from the header or context.
The list may span multiple lines - treat all names as part of the same list.

Example: If the header says "Writers, commencing at 200l." and the lines contain:
  "A. B. Smith, C. D. Jones, E. F. Brown,"
  "G. H. Wilson, I. J. Taylor."

Extract 5 people, all with role="Writer" and salary="£200" (or appropriate format).

Split by commas and extract each individual name."""

    def _build_pattern_failed_instruction(self, last_role: str) -> str:
        """Build instruction for pattern match failed sections."""
        instruction = """This line contains people data but didn't match standard patterns.

Try to identify:
1. Person's name (usually capitalized, may have initials)
2. Their role/position (may be stated or implied from context)
3. Their salary (if mentioned)"""

        if last_role:
            instruction += f"\n\nThe previous role was: {last_role}\nIf no role is stated, this person might have the same role."

        return instruction

    def _get_context_lines(
        self,
        all_lines: List[str],
        start: int,
        end: int
    ) -> str:
        """Get context lines with line numbers."""
        if start < 0:
            start = 0
        if end > len(all_lines):
            end = len(all_lines)

        context = ""
        for i in range(start, end):
            if i < len(all_lines):
                context += f"Line {i + 1}: {all_lines[i]}"

        return context.strip() if context else "(no additional context)"

    def _call_llm(self, prompt: str) -> str:
        """
        Call LLM with the prompt and return response.

        This is the main integration point for different LLM backends.

        Supported backends:
        - 'anthropic': Use Anthropic API (requires API key)
        - 'ollama': Use local Ollama instance
        - 'openai': Use OpenAI API
        - 'placeholder': Return sample response for testing

        To implement a new backend:
        1. Add environment variable for configuration
        2. Import the appropriate library
        3. Make the API call
        4. Return the text response
        """

        if self.llm_backend == "anthropic":
            return self._call_anthropic(prompt)
        elif self.llm_backend == "ollama":
            return self._call_ollama(prompt)
        elif self.llm_backend == "openai":
            return self._call_openai(prompt)
        else:
            # Placeholder implementation for testing/demonstration
            return self._call_placeholder(prompt)

    def _call_anthropic(self, prompt: str) -> str:
        """
        Call Anthropic API (Claude).

        Requires:
            pip install anthropic
            export ANTHROPIC_API_KEY=your_key_here
        """
        try:
            import anthropic

            api_key = os.environ.get("ANTHROPIC_API_KEY")
            if not api_key:
                raise ValueError("ANTHROPIC_API_KEY not set")

            client = anthropic.Anthropic(api_key=api_key)

            response = client.messages.create(
                model="claude-3-5-sonnet-20241022",  # or claude-3-opus, etc.
                max_tokens=2000,
                temperature=0,  # Deterministic for data extraction
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            return response.content[0].text

        except ImportError:
            raise RuntimeError("anthropic library not installed. Run: pip install anthropic")
        except Exception as e:
            raise RuntimeError(f"Anthropic API call failed: {str(e)}")

    def _call_ollama(self, prompt: str) -> str:
        """
        Call local Ollama instance.

        Requires:
            - Ollama running locally: https://ollama.ai/
            - A model pulled, e.g.: ollama pull llama2
            - pip install ollama
        """
        try:
            import ollama

            model = os.environ.get("OLLAMA_MODEL", "llama2")

            response = ollama.chat(
                model=model,
                messages=[{
                    'role': 'user',
                    'content': prompt
                }],
                options={
                    'temperature': 0,  # Deterministic
                }
            )

            return response['message']['content']

        except ImportError:
            raise RuntimeError("ollama library not installed. Run: pip install ollama")
        except Exception as e:
            raise RuntimeError(f"Ollama call failed: {str(e)}")

    def _call_openai(self, prompt: str) -> str:
        """
        Call OpenAI API (GPT-4, etc.).

        Requires:
            pip install openai
            export OPENAI_API_KEY=your_key_here
        """
        try:
            import openai

            api_key = os.environ.get("OPENAI_API_KEY")
            if not api_key:
                raise ValueError("OPENAI_API_KEY not set")

            client = openai.OpenAI(api_key=api_key)

            response = client.chat.completions.create(
                model="gpt-4",  # or gpt-4-turbo, gpt-3.5-turbo
                temperature=0,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            return response.choices[0].message.content

        except ImportError:
            raise RuntimeError("openai library not installed. Run: pip install openai")
        except Exception as e:
            raise RuntimeError(f"OpenAI API call failed: {str(e)}")

    def _call_placeholder(self, prompt: str) -> str:
        """
        Placeholder LLM call for testing/demonstration.

        This simulates an LLM response for development and testing.
        In production, replace this with actual LLM backend.
        """
        # Check what type of section this is from the prompt
        if "comma_separated_list" in prompt.lower() or "commencing at" in prompt.lower():
            # Simulate extracting from a comma-separated list
            return '''[
  {
    "name": "A. B. Smith",
    "role": "Writer",
    "salary": "£200",
    "line_number": 145
  },
  {
    "name": "C. D. Jones",
    "role": "Writer",
    "salary": "£200",
    "line_number": 145
  }
]'''
        else:
            # Simulate extracting from a complex line
            return '''[
  {
    "name": "J. Wilson (M.D.)",
    "role": "Medical Officer",
    "salary": "Rs. 1,500",
    "line_number": 203
  }
]'''

    def _parse_llm_response(
        self,
        response: str,
        section: FlaggedSection,
        colony: str,
        year: int,
        file_analysis: FileAnalysis
    ) -> List[Person]:
        """
        Parse LLM JSON response into Person objects.

        Handles:
        - JSON extraction from response
        - Validation of required fields
        - Creation of Person objects with full metadata
        - Error recovery (returns empty list on failure)
        """

        try:
            # Extract JSON from response (LLM might include explanation text)
            json_str = self._extract_json_from_text(response)

            if not json_str:
                print(f"        Warning: No JSON found in LLM response")
                return []

            # Parse JSON
            data = json.loads(json_str)

            if not isinstance(data, list):
                print(f"        Warning: LLM response is not a JSON array")
                return []

            # Convert to Person objects
            people = []
            for item in data:
                person = self._create_person_from_json(
                    json_data=item,
                    section=section,
                    colony=colony,
                    year=year,
                    file_analysis=file_analysis
                )

                if person:
                    people.append(person)

            return people

        except json.JSONDecodeError as e:
            print(f"        Warning: JSON parse error: {str(e)}")
            return []
        except Exception as e:
            print(f"        Warning: Failed to parse LLM response: {str(e)}")
            return []

    def _extract_json_from_text(self, text: str) -> Optional[str]:
        """
        Extract JSON array from LLM response text.

        LLMs sometimes return JSON wrapped in markdown code blocks or with
        explanatory text before/after. This function extracts just the JSON.
        """

        # Remove markdown code blocks
        text = re.sub(r'```json\s*', '', text)
        text = re.sub(r'```\s*', '', text)

        # Find JSON array
        # Look for [ ... ] pattern
        match = re.search(r'\[\s*\{.*?\}\s*\]', text, re.DOTALL)
        if match:
            return match.group(0)

        # Try to find just []
        match = re.search(r'\[\s*\]', text)
        if match:
            return match.group(0)

        # If no brackets found, maybe the whole thing is JSON?
        if text.strip().startswith('['):
            return text.strip()

        return None

    def _create_person_from_json(
        self,
        json_data: Dict[str, Any],
        section: FlaggedSection,
        colony: str,
        year: int,
        file_analysis: FileAnalysis
    ) -> Optional[Person]:
        """
        Create a Person object from parsed JSON data.

        Validates required fields and adds context from section.
        """

        # Validate required fields
        if 'name' not in json_data or not json_data['name']:
            return None

        name = json_data['name'].strip()
        role = json_data.get('role', 'Unknown').strip()
        salary = json_data.get('salary', '').strip()
        line_number = json_data.get('line_number', section.line_start + 1)

        # Skip invalid names
        if len(name) < 2 or name.lower() in ['ditto', 'vacant', 'acting']:
            return None

        # Get context
        context = section.context
        department = context.get('department', '')
        province = context.get('province', '')

        # Build location
        location_parts = [colony]
        if province:
            location_parts.append(province)
        if department:
            location_parts.append(department)
        location = ' - '.join(location_parts)

        # Build full string (for reference)
        full_string = f"{role}, {name}"
        if salary:
            full_string += f", {salary}"

        # Create Person object
        person = Person(
            name=name,
            role=role,
            location=location,
            colony=colony,
            year=year,
            department=department,
            province=province,
            salary=salary,
            full_string=full_string,
            source_file=file_analysis.file_path,
            line_number=line_number,
            confidence=0.8,  # LLM extraction, slightly lower than perfect regex match
            extraction_method=f"llm_{section.reason}",
            notes=f"Extracted from flagged section: {section.reason}"
        )

        return person

    def get_stats(self) -> Dict[str, int]:
        """Get extraction statistics."""
        return self.extraction_stats.copy()


# Main extraction function (convenience wrapper)
def extract_from_flagged_sections(
    flagged_sections: List[FlaggedSection],
    file_analysis: FileAnalysis,
    all_lines: List[str],
    colony: str,
    year: int,
    llm_backend: str = "placeholder"
) -> List[Person]:
    """
    Extract people from flagged sections using LLM.

    This is the main entry point for LLM extraction.

    Args:
        flagged_sections: List of sections that need LLM extraction
        file_analysis: File structure analysis
        all_lines: Complete file content (for context)
        colony: Colony name
        year: Year
        llm_backend: LLM backend to use ('anthropic', 'ollama', 'openai', 'placeholder')

    Returns:
        List of Person objects extracted from flagged sections

    Example:
        >>> from llm_extractor import extract_from_flagged_sections
        >>> people = extract_from_flagged_sections(
        ...     flagged_sections=flagged,
        ...     file_analysis=analysis,
        ...     all_lines=lines,
        ...     colony="CEYLON",
        ...     year=1867,
        ...     llm_backend="anthropic"  # or "ollama" or "placeholder"
        ... )
    """

    extractor = LLMExtractor(llm_backend=llm_backend)
    people = extractor.extract_from_flagged_sections(
        flagged_sections=flagged_sections,
        file_analysis=file_analysis,
        all_lines=all_lines,
        colony=colony,
        year=year
    )

    # Print statistics
    stats = extractor.get_stats()
    if stats['total_sections'] > 0:
        success_rate = (stats['successful_extractions'] / stats['total_sections']) * 100
        print(f"\n  LLM Extraction Stats:")
        print(f"    Sections processed: {stats['total_sections']}")
        print(f"    Successful: {stats['successful_extractions']} ({success_rate:.1f}%)")
        print(f"    Failed: {stats['failed_extractions']}")
        print(f"    People extracted: {stats['total_people_extracted']}")

    return people


# Example usage and testing
if __name__ == "__main__":
    """
    Example usage demonstrating how to use the LLM extractor.

    To run with real LLM backend:
        export ANTHROPIC_API_KEY=your_key_here
        python llm_extractor.py
    """

    # Create sample data for testing
    sample_flagged = [
        FlaggedSection(
            line_start=144,
            line_end=145,
            lines=[
                "Writers, commencing at 200l.:",
                "A. B. Smith, C. D. Jones, E. F. Brown, G. H. Wilson."
            ],
            reason="comma_separated_list",
            context={
                'department': "Secretary's Office",
                'province': '',
                'last_role': 'Writer',
                'header': 'Writers, commencing at 200l.:'
            }
        )
    ]

    sample_analysis = FileAnalysis(
        file_path="/path/to/file.txt",
        colony="CEYLON",
        year=1867,
        people_section_start=100,
        people_section_end=500,
        start_marker="Civil Establishment",
        departments=["Secretary's Office"],
        primary_format="Role, Name, Salary"
    )

    sample_lines = [""] * 200  # Mock file content

    # Test extraction with placeholder backend
    print("Testing LLM Extractor with placeholder backend...\n")
    people = extract_from_flagged_sections(
        flagged_sections=sample_flagged,
        file_analysis=sample_analysis,
        all_lines=sample_lines,
        colony="CEYLON",
        year=1867,
        llm_backend="placeholder"
    )

    print(f"\n{'='*70}")
    print("EXTRACTED PEOPLE:")
    print('='*70)
    for person in people:
        print(f"  {person.name} - {person.role} - {person.salary}")
        print(f"    Method: {person.extraction_method}, Confidence: {person.confidence}")

    print(f"\n{'='*70}")
    print("INTEGRATION GUIDE:")
    print('='*70)
    print("""
To integrate with extract_people_v2.py:

1. Import the extractor:
   from llm_extractor import extract_from_flagged_sections

2. Replace the placeholder in _llm_extract_flagged():

   def _llm_extract_flagged(self, flagged, file_analysis, lines):
       from llm_extractor import extract_from_flagged_sections

       # Choose backend based on environment
       backend = os.environ.get('LLM_BACKEND', 'placeholder')

       return extract_from_flagged_sections(
           flagged_sections=flagged,
           file_analysis=file_analysis,
           all_lines=lines,
           colony=file_analysis.colony,
           year=file_analysis.year,
           llm_backend=backend
       )

3. Set environment variable to choose LLM backend:
   export LLM_BACKEND=anthropic    # Use Claude
   export LLM_BACKEND=ollama        # Use local Ollama
   export LLM_BACKEND=placeholder   # Use mock responses

4. Set API key if using cloud service:
   export ANTHROPIC_API_KEY=your_key_here
   export OPENAI_API_KEY=your_key_here
    """)
