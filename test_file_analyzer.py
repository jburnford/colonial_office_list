#!/usr/bin/env python3
"""
Unit tests for file_analyzer_llm.py

Run with: python test_file_analyzer.py
"""

import os
import sys
import json
import tempfile
import unittest
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from file_analyzer_llm import (
    _build_analysis_dict,
    _validate_and_fix_analysis,
    _dedupe_list,
    _parse_response,
    save_analysis,
    load_analysis
)


class TestFileAnalyzerLLM(unittest.TestCase):
    """Test suite for file_analyzer_llm module."""

    def test_build_analysis_dict(self):
        """Test building analysis dictionary."""
        data = {
            "people_section_start": 100,
            "people_section_end": 500,
            "start_marker": "Executive Council",
            "departments": ["Dept 1", "Dept 2"],
            "provinces": ["Province 1"],
            "primary_format": "Role, Name, Salary",
            "has_lists": True,
            "has_ditto": False,
            "salary_currency": "Rs",
            "ocr_quality": "good",
            "extraction_notes": ["Note 1"]
        }

        result = _build_analysis_dict(data, "/path/to/file.txt", "CEYLON", 1889)

        self.assertEqual(result["file_path"], "/path/to/file.txt")
        self.assertEqual(result["colony"], "CEYLON")
        self.assertEqual(result["year"], 1889)
        self.assertEqual(result["people_section_start"], 100)
        self.assertEqual(result["people_section_end"], 500)
        self.assertEqual(result["departments"], ["Dept 1", "Dept 2"])
        self.assertTrue(result["has_lists"])
        self.assertFalse(result["has_ditto"])

    def test_build_analysis_dict_with_defaults(self):
        """Test building analysis dict with missing fields."""
        data = {}  # Empty data

        result = _build_analysis_dict(data, "/path/to/file.txt", "CEYLON", 1889)

        self.assertEqual(result["people_section_start"], 0)
        self.assertEqual(result["people_section_end"], 0)
        self.assertEqual(result["start_marker"], "")
        self.assertEqual(result["departments"], [])
        self.assertEqual(result["provinces"], [])
        self.assertFalse(result["has_lists"])
        self.assertFalse(result["has_ditto"])

    def test_validate_and_fix_analysis(self):
        """Test validation and fixing of analysis results."""
        analysis = {
            "people_section_start": 100,
            "people_section_end": 500,
            "departments": ["Dept 1", "Dept 2"],
            "provinces": ["Province 1"],
            "ocr_quality": "good",
            "extraction_notes": []
        }

        result = _validate_and_fix_analysis(analysis, total_lines=1000, verbose=False)

        self.assertEqual(result["people_section_start"], 100)
        self.assertEqual(result["people_section_end"], 500)

    def test_validate_and_fix_analysis_invalid_lines(self):
        """Test fixing invalid line numbers."""
        analysis = {
            "people_section_start": -10,  # Invalid: negative
            "people_section_end": 2000,   # Invalid: exceeds total
            "departments": [],
            "provinces": [],
            "ocr_quality": "good",
            "extraction_notes": []
        }

        result = _validate_and_fix_analysis(analysis, total_lines=1000, verbose=False)

        self.assertEqual(result["people_section_start"], 0)  # Fixed to 0
        self.assertEqual(result["people_section_end"], 1000)  # Fixed to total

    def test_validate_and_fix_analysis_inverted_lines(self):
        """Test fixing inverted line numbers (start >= end)."""
        analysis = {
            "people_section_start": 800,
            "people_section_end": 400,  # Start > End - invalid
            "departments": [],
            "provinces": [],
            "ocr_quality": "good",
            "extraction_notes": []
        }

        result = _validate_and_fix_analysis(analysis, total_lines=1000, verbose=False)

        # Should use fallback: middle to end
        self.assertEqual(result["people_section_start"], 500)  # 1000 // 2
        self.assertEqual(result["people_section_end"], 1000)
        self.assertIn("auto-corrected", result["extraction_notes"][0])

    def test_validate_ocr_quality(self):
        """Test OCR quality validation."""
        # Valid OCR quality
        analysis = {
            "people_section_start": 100,
            "people_section_end": 500,
            "departments": [],
            "provinces": [],
            "ocr_quality": "good",
            "extraction_notes": []
        }
        result = _validate_and_fix_analysis(analysis, total_lines=1000, verbose=False)
        self.assertEqual(result["ocr_quality"], "good")

        # Invalid OCR quality
        analysis["ocr_quality"] = "excellent"  # Not in valid values
        result = _validate_and_fix_analysis(analysis, total_lines=1000, verbose=False)
        self.assertEqual(result["ocr_quality"], "unknown")  # Should default to unknown

    def test_dedupe_list(self):
        """Test list deduplication."""
        items = ["Dept A", "Dept B", "dept a", "DEPT A", "Dept C", "Dept B"]
        result = _dedupe_list(items)

        self.assertEqual(len(result), 3)  # Should have 3 unique items
        self.assertIn("Dept A", result)
        self.assertIn("Dept B", result)
        self.assertIn("Dept C", result)

    def test_dedupe_list_preserves_order(self):
        """Test that deduplication preserves order."""
        items = ["First", "Second", "first", "Third"]
        result = _dedupe_list(items)

        self.assertEqual(result, ["First", "Second", "Third"])

    def test_parse_response_direct_json(self):
        """Test parsing response with direct JSON."""
        response = json.dumps({
            "people_section_start": 100,
            "people_section_end": 500,
            "start_marker": "Test",
            "departments": [],
            "provinces": [],
            "primary_format": "Test",
            "has_lists": False,
            "has_ditto": False,
            "salary_currency": "Rs",
            "ocr_quality": "good",
            "extraction_notes": []
        })

        result = _parse_response(response, "/path/to/file.txt", "CEYLON", 1889, verbose=False)

        self.assertEqual(result["people_section_start"], 100)
        self.assertEqual(result["colony"], "CEYLON")
        self.assertEqual(result["year"], 1889)

    def test_parse_response_with_markdown(self):
        """Test parsing response with JSON in markdown code block."""
        json_data = {
            "people_section_start": 100,
            "people_section_end": 500,
            "start_marker": "Test",
            "departments": [],
            "provinces": [],
            "primary_format": "Test",
            "has_lists": False,
            "has_ditto": False,
            "salary_currency": "Rs",
            "ocr_quality": "good",
            "extraction_notes": []
        }

        response = f"""Here is the analysis:

```json
{json.dumps(json_data, indent=2)}
```

I hope this helps!"""

        result = _parse_response(response, "/path/to/file.txt", "CEYLON", 1889, verbose=False)

        self.assertEqual(result["people_section_start"], 100)
        self.assertEqual(result["colony"], "CEYLON")

    def test_parse_response_with_text_around_json(self):
        """Test parsing response with text around JSON."""
        json_data = {
            "people_section_start": 100,
            "people_section_end": 500,
            "start_marker": "Test",
            "departments": [],
            "provinces": [],
            "primary_format": "Test",
            "has_lists": False,
            "has_ditto": False,
            "salary_currency": "Rs",
            "ocr_quality": "good",
            "extraction_notes": []
        }

        response = f"""I analyzed the document and found the following structure:

{json.dumps(json_data)}

This should help with extraction."""

        result = _parse_response(response, "/path/to/file.txt", "CEYLON", 1889, verbose=False)

        self.assertEqual(result["people_section_start"], 100)

    def test_save_and_load_analysis(self):
        """Test saving and loading analysis results."""
        analysis = {
            "file_path": "/path/to/file.txt",
            "colony": "CEYLON",
            "year": 1889,
            "people_section_start": 100,
            "people_section_end": 500,
            "start_marker": "Test",
            "departments": ["Dept 1"],
            "provinces": ["Province 1"],
            "primary_format": "Test",
            "has_lists": True,
            "has_ditto": False,
            "salary_currency": "Rs",
            "ocr_quality": "good",
            "extraction_notes": ["Note 1"]
        }

        # Create temp file
        with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.json') as f:
            temp_file = f.name

        try:
            # Save
            save_analysis(analysis, temp_file)

            # Load
            loaded = load_analysis(temp_file)

            # Compare
            self.assertEqual(loaded["colony"], "CEYLON")
            self.assertEqual(loaded["year"], 1889)
            self.assertEqual(loaded["people_section_start"], 100)
            self.assertEqual(loaded["departments"], ["Dept 1"])
            self.assertTrue(loaded["has_lists"])

        finally:
            # Clean up
            if os.path.exists(temp_file):
                os.remove(temp_file)

    def test_validate_departments_limit(self):
        """Test that too many departments are limited."""
        # Create 100 departments
        departments = [f"Department {i}" for i in range(100)]

        analysis = {
            "people_section_start": 100,
            "people_section_end": 500,
            "departments": departments,
            "provinces": [],
            "ocr_quality": "good",
            "extraction_notes": []
        }

        result = _validate_and_fix_analysis(analysis, total_lines=1000, verbose=False)

        # Should be limited to 50
        self.assertEqual(len(result["departments"]), 50)

    def test_validate_provinces_limit(self):
        """Test that too many provinces are limited."""
        # Create 50 provinces
        provinces = [f"Province {i}" for i in range(50)]

        analysis = {
            "people_section_start": 100,
            "people_section_end": 500,
            "departments": [],
            "provinces": provinces,
            "ocr_quality": "good",
            "extraction_notes": []
        }

        result = _validate_and_fix_analysis(analysis, total_lines=1000, verbose=False)

        # Should be limited to 30
        self.assertEqual(len(result["provinces"]), 30)


def main():
    """Run the tests."""
    print("\n" + "="*70)
    print("Running File Analyzer LLM Unit Tests")
    print("="*70 + "\n")

    # Run tests
    suite = unittest.TestLoader().loadTestsFromTestCase(TestFileAnalyzerLLM)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    # Print summary
    print("\n" + "="*70)
    if result.wasSuccessful():
        print("✓ All tests passed!")
    else:
        print("✗ Some tests failed")
    print("="*70 + "\n")

    return 0 if result.wasSuccessful() else 1


if __name__ == "__main__":
    sys.exit(main())
