#!/usr/bin/env python3
"""
Colonial Office List - LLM-Based File Structure Analyzer

This module uses Claude AI to analyze the structure of Colonial Office List text files
and extract metadata about:
- People section boundaries (start/end line numbers)
- Departments and provinces
- Format patterns for how people are listed
- Presence of lists, ditto references, salary information
- OCR quality assessment

Usage:
    from file_analyzer_llm import analyze_file_structure

    analysis = analyze_file_structure(
        file_path="/path/to/CEYLON.txt",
        colony="CEYLON",
        year=1889
    )

    print(f"People section: lines {analysis['people_section_start']}-{analysis['people_section_end']}")
    print(f"Departments: {analysis['departments']}")

Environment:
    Requires ANTHROPIC_API_KEY environment variable to be set.
"""

import os
import json
import re
from typing import Dict, List, Optional, Any
from pathlib import Path
import anthropic


# Constants
DEFAULT_MODEL = "claude-sonnet-4-5-20250929"
MAX_TOKENS = 4000
TEMPERATURE = 0.0  # Use deterministic responses for structured analysis


def analyze_file_structure(
    file_path: str,
    colony: str,
    year: int,
    model: str = DEFAULT_MODEL,
    verbose: bool = False
) -> Dict[str, Any]:
    """
    Analyze a Colonial Office List file structure using Claude AI.

    This function reads a text file containing Colonial Office List data and uses
    Claude to intelligently identify:
    - Where the people/personnel section starts and ends
    - What departments are mentioned
    - What provinces/regions are listed
    - The format pattern used for listing people
    - Presence of lists, ditto marks, and salary information
    - OCR quality

    Args:
        file_path: Path to the text file to analyze
        colony: Name of the colony (e.g., "CEYLON", "JAMAICA")
        year: Year of the Colonial Office List
        model: Claude model to use (default: claude-sonnet-4-5)
        verbose: If True, print detailed progress information

    Returns:
        Dictionary matching the FileAnalysis dataclass structure with keys:
        - file_path: str - Path to the analyzed file
        - colony: str - Colony name
        - year: int - Year
        - people_section_start: int - Starting line number of people section
        - people_section_end: int - Ending line number of people section
        - start_marker: str - Text/pattern that marks the start
        - departments: List[str] - List of departments found
        - provinces: List[str] - List of provinces found
        - primary_format: str - Description of how people are formatted
        - has_lists: bool - Whether comma-separated name lists exist
        - has_ditto: bool - Whether ditto marks are used
        - salary_currency: str - Currency format for salaries
        - ocr_quality: str - Assessment of OCR quality (good/fair/poor)
        - extraction_notes: List[str] - Additional notes about the structure

    Raises:
        FileNotFoundError: If file_path doesn't exist
        ValueError: If API key is not set or response is invalid
        anthropic.APIError: If there's an API communication error

    Example:
        >>> analysis = analyze_file_structure(
        ...     file_path="/home/user/colonial_office_list/output_3/1889_manual_parsed/CEYLON.txt",
        ...     colony="CEYLON",
        ...     year=1889
        ... )
        >>> print(f"People section: lines {analysis['people_section_start']}-{analysis['people_section_end']}")
        People section: lines 402-837
        >>> print(f"Found {len(analysis['departments'])} departments")
        Found 12 departments
        >>> print(f"Currency: {analysis['salary_currency']}")
        Currency: Rs (rupees)
    """
    # Validate inputs
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"File not found: {file_path}")

    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        raise ValueError(
            "ANTHROPIC_API_KEY environment variable not set. "
            "Please set it with your Claude API key."
        )

    # Read the file
    if verbose:
        print(f"Reading file: {file_path}")

    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    total_lines = len(lines)
    file_content = ''.join(lines)

    if verbose:
        print(f"File contains {total_lines} lines")
        print(f"Analyzing with Claude model: {model}")

    # Create the analysis prompt
    prompt = _create_analysis_prompt(file_content, colony, year, total_lines)

    # Call Claude API
    client = anthropic.Anthropic(api_key=api_key)

    try:
        if verbose:
            print("Sending request to Claude API...")

        message = client.messages.create(
            model=model,
            max_tokens=MAX_TOKENS,
            temperature=TEMPERATURE,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        response_text = message.content[0].text

        if verbose:
            print(f"Received response ({len(response_text)} characters)")

    except anthropic.APIError as e:
        raise anthropic.APIError(f"Claude API error: {str(e)}")

    # Parse the JSON response
    try:
        analysis_data = _parse_response(response_text, file_path, colony, year, verbose)
    except (json.JSONDecodeError, KeyError, ValueError) as e:
        raise ValueError(f"Failed to parse Claude response: {str(e)}\nResponse: {response_text[:500]}")

    # Validate the response
    analysis_data = _validate_and_fix_analysis(analysis_data, total_lines, verbose)

    if verbose:
        print("\nAnalysis complete!")
        print(f"  People section: lines {analysis_data['people_section_start']}-{analysis_data['people_section_end']}")
        print(f"  Departments: {len(analysis_data['departments'])}")
        print(f"  Provinces: {len(analysis_data['provinces'])}")
        print(f"  Primary format: {analysis_data['primary_format']}")

    return analysis_data


def _create_analysis_prompt(file_content: str, colony: str, year: int, total_lines: int) -> str:
    """
    Create a structured prompt for Claude to analyze the file.

    The prompt is designed to be specific and request JSON output with all
    the required fields for the FileAnalysis dataclass.
    """
    # Truncate file if too long (Claude has context limits)
    # Keep first 30% and last 70% to ensure we capture intro and people sections
    max_chars = 150000  # Leave room for prompt and response

    if len(file_content) > max_chars:
        split_point = int(total_lines * 0.3)
        lines = file_content.split('\n')
        truncated_content = '\n'.join(lines[:split_point] +
                                      ["\n[... middle section truncated ...]\n"] +
                                      lines[split_point:])
        file_content = truncated_content[:max_chars]

    prompt = f"""Analyze this Colonial Office List document for {colony} ({year}) and extract structural information.

The document contains general information about the colony followed by a section listing government personnel (people).

Your task is to identify:
1. WHERE the people/personnel section starts (line number) - look for sections like "Executive Council", "Legislative Council", "Civil Establishment", "GOVERNMENT", etc.
2. WHERE the people section ends (line number) - usually end of file or before appendices
3. What MARKER text indicates the start of the people section
4. List of DEPARTMENTS mentioned (e.g., "Colonial Secretary's Office", "Department of Public Works")
5. List of PROVINCES or regions (e.g., "Western Province", "Central Province")
6. PRIMARY FORMAT pattern for how people are listed (e.g., "Role, Name, Salary" or "Name, Role" or "List format: role followed by comma-separated names")
7. Whether comma-separated LISTS of names exist (e.g., "Cadets: J. Smith, R. Brown, T. Wilson")
8. Whether DITTO marks or abbreviations are used to reference previous entries
9. SALARY CURRENCY format (e.g., "£ sterling", "Rs (rupees)", "dollars")
10. OCR QUALITY assessment (good/fair/poor) - look for obvious errors, garbled text, or formatting issues
11. Any important NOTES about the structure that would help extraction

Document to analyze ({total_lines} total lines):

{file_content}

Please respond with ONLY a JSON object (no additional text) in this exact format:

{{
  "people_section_start": <line_number>,
  "people_section_end": <line_number>,
  "start_marker": "<text that marks the beginning>",
  "departments": ["Department 1", "Department 2", ...],
  "provinces": ["Province 1", "Province 2", ...],
  "primary_format": "<description of format>",
  "has_lists": true|false,
  "has_ditto": true|false,
  "salary_currency": "<currency format>",
  "ocr_quality": "good|fair|poor",
  "extraction_notes": ["Note 1", "Note 2", ...]
}}

Be precise with line numbers. If uncertain about any field, make your best educated guess based on the document structure.
If departments or provinces aren't clearly listed, return empty arrays.
For extraction_notes, include anything that would help automated extraction (formatting quirks, special cases, etc.)."""

    return prompt


def _parse_response(response_text: str, file_path: str, colony: str, year: int, verbose: bool) -> Dict[str, Any]:
    """
    Parse Claude's response and extract the JSON data.

    Handles cases where Claude might include extra text before/after the JSON.
    """
    # Try to extract JSON from the response
    # Sometimes Claude adds explanation text, so we need to find the JSON block

    # First, try direct JSON parsing
    try:
        data = json.loads(response_text)
        if verbose:
            print("Successfully parsed JSON directly")
        return _build_analysis_dict(data, file_path, colony, year)
    except json.JSONDecodeError:
        pass

    # Try to find JSON block in the text
    # Look for {...} pattern
    json_match = re.search(r'\{[\s\S]*\}', response_text)
    if json_match:
        try:
            data = json.loads(json_match.group(0))
            if verbose:
                print("Extracted JSON from response text")
            return _build_analysis_dict(data, file_path, colony, year)
        except json.JSONDecodeError:
            pass

    # Try to find JSON code block (```json ... ```)
    code_block_match = re.search(r'```(?:json)?\s*(\{[\s\S]*?\})\s*```', response_text)
    if code_block_match:
        try:
            data = json.loads(code_block_match.group(1))
            if verbose:
                print("Extracted JSON from code block")
            return _build_analysis_dict(data, file_path, colony, year)
        except json.JSONDecodeError:
            pass

    raise ValueError("Could not find valid JSON in Claude's response")


def _build_analysis_dict(data: Dict[str, Any], file_path: str, colony: str, year: int) -> Dict[str, Any]:
    """
    Build the final analysis dictionary with all required fields.

    Ensures the response matches the FileAnalysis dataclass structure.
    """
    return {
        "file_path": file_path,
        "colony": colony,
        "year": year,
        "people_section_start": int(data.get("people_section_start", 0)),
        "people_section_end": int(data.get("people_section_end", 0)),
        "start_marker": str(data.get("start_marker", "")),
        "departments": list(data.get("departments", [])),
        "provinces": list(data.get("provinces", [])),
        "primary_format": str(data.get("primary_format", "")),
        "has_lists": bool(data.get("has_lists", False)),
        "has_ditto": bool(data.get("has_ditto", False)),
        "salary_currency": str(data.get("salary_currency", "")),
        "ocr_quality": str(data.get("ocr_quality", "unknown")),
        "extraction_notes": list(data.get("extraction_notes", []))
    }


def _validate_and_fix_analysis(analysis: Dict[str, Any], total_lines: int, verbose: bool) -> Dict[str, Any]:
    """
    Validate the analysis results and fix common issues.

    This ensures the line numbers are valid and makes sense.
    """
    # Validate line numbers
    if analysis["people_section_start"] < 0:
        if verbose:
            print("Warning: Invalid start line (< 0), setting to 0")
        analysis["people_section_start"] = 0

    if analysis["people_section_end"] > total_lines:
        if verbose:
            print(f"Warning: End line ({analysis['people_section_end']}) > total lines ({total_lines}), adjusting")
        analysis["people_section_end"] = total_lines

    if analysis["people_section_start"] >= analysis["people_section_end"]:
        if verbose:
            print("Warning: Start >= End, using fallback (middle of file to end)")
        analysis["people_section_start"] = total_lines // 2
        analysis["people_section_end"] = total_lines
        analysis["extraction_notes"].append("Line numbers were invalid and were auto-corrected to default values")

    # Validate OCR quality
    valid_ocr_values = ["good", "fair", "poor", "unknown"]
    if analysis["ocr_quality"] not in valid_ocr_values:
        if verbose:
            print(f"Warning: Invalid OCR quality '{analysis['ocr_quality']}', setting to 'unknown'")
        analysis["ocr_quality"] = "unknown"

    # Deduplicate departments and provinces (case-insensitive)
    analysis["departments"] = _dedupe_list(analysis["departments"])
    analysis["provinces"] = _dedupe_list(analysis["provinces"])

    # Limit to reasonable numbers
    if len(analysis["departments"]) > 50:
        if verbose:
            print(f"Warning: Too many departments ({len(analysis['departments'])}), keeping top 50")
        analysis["departments"] = analysis["departments"][:50]

    if len(analysis["provinces"]) > 30:
        if verbose:
            print(f"Warning: Too many provinces ({len(analysis['provinces'])}), keeping top 30")
        analysis["provinces"] = analysis["provinces"][:30]

    return analysis


def _dedupe_list(items: List[str]) -> List[str]:
    """
    Deduplicate a list of strings (case-insensitive) while preserving order.
    """
    seen = set()
    result = []
    for item in items:
        item_lower = item.lower().strip()
        if item_lower and item_lower not in seen:
            seen.add(item_lower)
            result.append(item.strip())
    return result


def analyze_file_structure_batch(
    file_paths: List[str],
    colony: str,
    years: List[int],
    verbose: bool = False
) -> List[Dict[str, Any]]:
    """
    Analyze multiple files in batch.

    Args:
        file_paths: List of file paths to analyze
        colony: Colony name (same for all files)
        years: List of years corresponding to each file
        verbose: Print progress information

    Returns:
        List of analysis dictionaries

    Example:
        >>> files = ["ceylon_1889.txt", "ceylon_1890.txt"]
        >>> years = [1889, 1890]
        >>> results = analyze_file_structure_batch(files, "CEYLON", years, verbose=True)
        >>> print(f"Analyzed {len(results)} files")
    """
    if len(file_paths) != len(years):
        raise ValueError("file_paths and years must have the same length")

    results = []

    for i, (file_path, year) in enumerate(zip(file_paths, years)):
        if verbose:
            print(f"\n{'='*70}")
            print(f"Analyzing file {i+1}/{len(file_paths)}: {os.path.basename(file_path)}")
            print('='*70)

        try:
            analysis = analyze_file_structure(file_path, colony, year, verbose=verbose)
            results.append(analysis)
        except Exception as e:
            if verbose:
                print(f"ERROR: Failed to analyze {file_path}: {str(e)}")
            # Add error placeholder
            results.append({
                "file_path": file_path,
                "colony": colony,
                "year": year,
                "error": str(e),
                "people_section_start": 0,
                "people_section_end": 0,
                "start_marker": "ERROR",
                "departments": [],
                "provinces": [],
                "primary_format": "",
                "has_lists": False,
                "has_ditto": False,
                "salary_currency": "",
                "ocr_quality": "unknown",
                "extraction_notes": [f"Analysis failed: {str(e)}"]
            })

    return results


def save_analysis(analysis: Dict[str, Any], output_path: str) -> None:
    """
    Save analysis results to a JSON file.

    Args:
        analysis: Analysis dictionary from analyze_file_structure()
        output_path: Path where to save the JSON file

    Example:
        >>> analysis = analyze_file_structure("ceylon.txt", "CEYLON", 1889)
        >>> save_analysis(analysis, "ceylon_1889_analysis.json")
    """
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, indent=2, ensure_ascii=False)


def load_analysis(input_path: str) -> Dict[str, Any]:
    """
    Load analysis results from a JSON file.

    Args:
        input_path: Path to the JSON file

    Returns:
        Analysis dictionary

    Example:
        >>> analysis = load_analysis("ceylon_1889_analysis.json")
        >>> print(analysis['people_section_start'])
    """
    with open(input_path, 'r', encoding='utf-8') as f:
        return json.load(f)


# CLI Interface
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Analyze Colonial Office List file structure using Claude AI"
    )
    parser.add_argument("file_path", help="Path to the text file to analyze")
    parser.add_argument("--colony", required=True, help="Colony name (e.g., CEYLON)")
    parser.add_argument("--year", type=int, required=True, help="Year of the document")
    parser.add_argument("--output", "-o", help="Save analysis to JSON file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    parser.add_argument("--model", default=DEFAULT_MODEL, help=f"Claude model to use (default: {DEFAULT_MODEL})")

    args = parser.parse_args()

    # Run analysis
    print(f"\nAnalyzing {args.colony} {args.year}: {args.file_path}")
    print("="*70)

    try:
        analysis = analyze_file_structure(
            file_path=args.file_path,
            colony=args.colony,
            year=args.year,
            model=args.model,
            verbose=args.verbose
        )

        # Print summary
        print("\n" + "="*70)
        print("ANALYSIS RESULTS")
        print("="*70)
        print(f"People section: lines {analysis['people_section_start']}-{analysis['people_section_end']}")
        print(f"Start marker: {analysis['start_marker']}")
        print(f"\nDepartments ({len(analysis['departments'])}):")
        for dept in analysis['departments'][:10]:  # Show first 10
            print(f"  - {dept}")
        if len(analysis['departments']) > 10:
            print(f"  ... and {len(analysis['departments']) - 10} more")

        print(f"\nProvinces ({len(analysis['provinces'])}):")
        for prov in analysis['provinces']:
            print(f"  - {prov}")

        print(f"\nFormat: {analysis['primary_format']}")
        print(f"Has lists: {analysis['has_lists']}")
        print(f"Has ditto: {analysis['has_ditto']}")
        print(f"Currency: {analysis['salary_currency']}")
        print(f"OCR Quality: {analysis['ocr_quality']}")

        if analysis['extraction_notes']:
            print(f"\nExtraction Notes:")
            for note in analysis['extraction_notes']:
                print(f"  - {note}")

        # Save if requested
        if args.output:
            save_analysis(analysis, args.output)
            print(f"\nAnalysis saved to: {args.output}")
        else:
            # Print JSON
            print("\n" + "="*70)
            print("JSON OUTPUT")
            print("="*70)
            print(json.dumps(analysis, indent=2))

    except Exception as e:
        print(f"\nERROR: {str(e)}")
        import sys
        sys.exit(1)
