#!/usr/bin/env python3
"""
Demonstration script for file_analyzer_llm.py

This script shows how to use the file_analyzer_llm module to analyze
Colonial Office List files and integrate with the extraction pipeline.

It provides examples of:
1. Single file analysis
2. Batch processing
3. Saving and loading analysis results
4. Integration with extract_people_v2.py
"""

import os
import sys
import json
from pathlib import Path

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from file_analyzer_llm import (
        analyze_file_structure,
        analyze_file_structure_batch,
        save_analysis,
        load_analysis
    )
except ImportError as e:
    print(f"Error importing file_analyzer_llm: {e}")
    print("Make sure file_analyzer_llm.py is in the same directory")
    sys.exit(1)


def demo_single_file_analysis():
    """
    Demonstrate analyzing a single file.
    """
    print("\n" + "="*70)
    print("DEMO 1: Single File Analysis")
    print("="*70)

    file_path = "output_3/1889_manual_parsed/CEYLON.txt"

    if not os.path.exists(file_path):
        print(f"Demo file not found: {file_path}")
        print("Please run this from the colonial_office_list directory")
        return None

    print(f"\nAnalyzing: {file_path}")
    print("Colony: CEYLON")
    print("Year: 1889")

    try:
        # Analyze the file
        analysis = analyze_file_structure(
            file_path=file_path,
            colony="CEYLON",
            year=1889,
            verbose=True
        )

        # Print results
        print("\n" + "-"*70)
        print("Results Summary:")
        print("-"*70)
        print(f"People section: lines {analysis['people_section_start']}-{analysis['people_section_end']}")
        print(f"Start marker: '{analysis['start_marker']}'")
        print(f"Departments found: {len(analysis['departments'])}")
        print(f"Provinces found: {len(analysis['provinces'])}")
        print(f"Primary format: {analysis['primary_format']}")
        print(f"Has lists: {analysis['has_lists']}")
        print(f"Has ditto: {analysis['has_ditto']}")
        print(f"Currency: {analysis['salary_currency']}")
        print(f"OCR quality: {analysis['ocr_quality']}")

        return analysis

    except Exception as e:
        print(f"\nError during analysis: {e}")
        return None


def demo_batch_analysis():
    """
    Demonstrate batch processing multiple files.
    """
    print("\n" + "="*70)
    print("DEMO 2: Batch Analysis")
    print("="*70)

    # Find multiple Ceylon files
    files = [
        "output_3/1889_manual_parsed/CEYLON.txt",
        "output_3/1890_manual_parsed/ceylon.txt",
        "output_3/1894_manual_parsed/ceylon.txt"
    ]

    # Filter to only existing files
    existing_files = [f for f in files if os.path.exists(f)]

    if not existing_files:
        print("No demo files found")
        return []

    years = [1889, 1890, 1894][:len(existing_files)]

    print(f"\nAnalyzing {len(existing_files)} files...")

    try:
        results = analyze_file_structure_batch(
            file_paths=existing_files,
            colony="CEYLON",
            years=years,
            verbose=True
        )

        print("\n" + "-"*70)
        print("Batch Results Summary:")
        print("-"*70)

        for result in results:
            print(f"\n{result['year']}: Lines {result['people_section_start']}-{result['people_section_end']}, "
                  f"{len(result['departments'])} depts, {len(result['provinces'])} provinces")

        return results

    except Exception as e:
        print(f"\nError during batch analysis: {e}")
        return []


def demo_save_load():
    """
    Demonstrate saving and loading analysis results.
    """
    print("\n" + "="*70)
    print("DEMO 3: Save and Load Analysis")
    print("="*70)

    # Create a sample analysis (or use real one if available)
    sample_analysis = {
        "file_path": "output_3/1889_manual_parsed/CEYLON.txt",
        "colony": "CEYLON",
        "year": 1889,
        "people_section_start": 402,
        "people_section_end": 837,
        "start_marker": "Executive Council",
        "departments": [
            "Colonial Secretary's Office",
            "Auditor-General's Department",
            "Treasury"
        ],
        "provinces": [
            "Western Province",
            "North Western Province",
            "Southern Province"
        ],
        "primary_format": "Role, Name, Salary",
        "has_lists": True,
        "has_ditto": True,
        "salary_currency": "Rs (rupees)",
        "ocr_quality": "good",
        "extraction_notes": [
            "Clear section boundaries",
            "Consistent formatting throughout"
        ]
    }

    output_file = "demo_analysis_output.json"

    print(f"\nSaving analysis to: {output_file}")
    save_analysis(sample_analysis, output_file)

    print(f"Loading analysis from: {output_file}")
    loaded = load_analysis(output_file)

    print("\nLoaded data:")
    print(json.dumps(loaded, indent=2))

    # Clean up
    if os.path.exists(output_file):
        os.remove(output_file)
        print(f"\nCleaned up demo file: {output_file}")


def demo_integration_with_extractor():
    """
    Demonstrate how to integrate with extract_people_v2.py
    """
    print("\n" + "="*70)
    print("DEMO 4: Integration with Extraction Pipeline")
    print("="*70)

    print("""
The file_analyzer_llm module is designed to replace the _analyze_file_structure
method in extract_people_v2.py's ExtractionOrchestrator class.

Example integration:

    from file_analyzer_llm import analyze_file_structure

    class ExtractionOrchestrator:
        def _analyze_file_structure(self, lines, colony, year, file_path, use_cache):
            # Use LLM-based analysis
            analysis_dict = analyze_file_structure(
                file_path=file_path,
                colony=colony,
                year=year,
                verbose=False
            )

            # Convert dict to FileAnalysis dataclass
            from dataclasses import asdict
            return FileAnalysis(**analysis_dict)

Benefits:
1. More accurate section boundary detection
2. Better department and province identification
3. Format pattern recognition
4. OCR quality assessment
5. Structured notes for downstream processing

The analysis can be cached to avoid repeated API calls:

    # Cache by year and colony
    cache_key = f"{colony}_{year}"
    if cache_key in self.analysis_cache and use_cache:
        return self.analysis_cache[cache_key]

    analysis = analyze_file_structure(...)
    self.analysis_cache[cache_key] = analysis
    return analysis
""")


def main():
    """
    Run all demonstrations.
    """
    print("\n" + "#"*70)
    print("# File Analyzer LLM - Demonstration Script")
    print("#"*70)

    print("\nThis script demonstrates the file_analyzer_llm module.")
    print("Note: Requires ANTHROPIC_API_KEY environment variable to be set.")

    # Check for API key
    if not os.environ.get("ANTHROPIC_API_KEY"):
        print("\nWARNING: ANTHROPIC_API_KEY not set!")
        print("Live API demos will not work.")
        print("Running demonstrations with sample data instead...\n")

        # Run non-API demos
        demo_save_load()
        demo_integration_with_extractor()

    else:
        print("\nAPI key found. Running all demonstrations...\n")

        # Run all demos
        demo_single_file_analysis()
        demo_batch_analysis()
        demo_save_load()
        demo_integration_with_extractor()

    print("\n" + "#"*70)
    print("# Demonstrations Complete")
    print("#"*70)


if __name__ == "__main__":
    main()
