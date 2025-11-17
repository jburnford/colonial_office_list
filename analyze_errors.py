#!/usr/bin/env python3
"""
Analyze error patterns across all audit reports to categorize and create remediation roadmap.
"""

import json
import re
from collections import defaultdict
from pathlib import Path

def load_audit_file(filepath):
    """Load and parse an audit JSON file."""
    with open(filepath, 'r') as f:
        return json.load(f)

def extract_error_pattern(error_msg):
    """
    Extract the error type from an error message.
    Returns a tuple of (error_category, specific_field, details)
    """
    # Parse the error message structure: [path] error_type: message

    # Extract path
    path_match = re.match(r'\[(.*?)\]\s+(.*)', error_msg)
    if not path_match:
        return ("unknown", "unknown", error_msg)

    path = path_match.group(1)
    error_part = path_match.group(2)

    # Determine error type
    if "missing: Field required" in error_part:
        field = path.split(" -> ")[-1]
        return ("missing_required_field", field, path)

    if "enum:" in error_part:
        field = path.split(" -> ")[-1]
        return ("invalid_enum_value", field, path)

    if "list_type:" in error_part or "Input should be a valid list" in error_part:
        field = path.split(" -> ")[-1]
        return ("type_mismatch_list_expected", field, path)

    if "float_type:" in error_part or "int_type:" in error_part or "Input should be a valid number" in error_part:
        field = path.split(" -> ")[-1]
        return ("type_mismatch_number_expected", field, path)

    if "string_type:" in error_part or "Input should be a valid string" in error_part:
        field = path.split(" -> ")[-1]
        return ("type_mismatch_string_expected", field, path)

    if "string_pattern_mismatch:" in error_part:
        field = path.split(" -> ")[-1]
        return ("string_pattern_mismatch", field, path)

    if "string_too_short:" in error_part or "at least 1 character" in error_part:
        field = path.split(" -> ")[-1]
        return ("string_too_short", field, path)

    if "greater_than:" in error_part or "Value must be greater than" in error_part:
        field = path.split(" -> ")[-1]
        return ("value_must_be_greater_than_zero", field, path)

    if "model_type:" in error_part:
        field = path.split(" -> ")[-1]
        return ("model_type_error", field, path)

    # Default
    return ("other", path.split(" -> ")[-1] if " -> " in path else "unknown", error_part)

def analyze_all_audits():
    """Analyze all three audit files."""

    audit_files = [
        "/home/user/colonial_office_list/reports/audit_1867_1900.json",
        "/home/user/colonial_office_list/reports/audit_1901_1930.json",
        "/home/user/colonial_office_list/reports/audit_1931_1966.json"
    ]

    # Collect all errors
    all_errors = []
    error_counts = defaultdict(int)
    error_by_field = defaultdict(lambda: defaultdict(int))
    files_analyzed = 0
    total_errors = 0

    for audit_file in audit_files:
        print(f"Analyzing {audit_file}...")
        data = load_audit_file(audit_file)

        # Handle different structures
        if "results" in data:
            # 1867-1900 format
            for result in data["results"]:
                if "errors" in result:
                    files_analyzed += 1
                    for error in result["errors"]:
                        all_errors.append({
                            "year": result.get("year"),
                            "error": error,
                            "file": result.get("file_path")
                        })
                        total_errors += 1

        elif "validation_results" in data:
            # 1901-1930 format
            if "invalid_years" in data["validation_results"]:
                for year_data in data["validation_results"]["invalid_years"]:
                    files_analyzed += 1
                    if "all_errors" in year_data:
                        for error in year_data["all_errors"]:
                            all_errors.append({
                                "year": year_data.get("year"),
                                "error": error,
                                "file": f"knowledge_graph_extracts/{year_data.get('year')}_extracted.json"
                            })
                            total_errors += 1
                    elif "sample_errors" in year_data:
                        # Only samples, use the count
                        error_count = year_data.get("error_count", 0)
                        total_errors += error_count
                        for error in year_data.get("sample_errors", []):
                            all_errors.append({
                                "year": year_data.get("year"),
                                "error": error,
                                "file": f"knowledge_graph_extracts/{year_data.get('year')}_extracted.json"
                            })

        elif "file_results" in data:
            # 1931-1966 format
            for file_result in data["file_results"]:
                if file_result.get("valid") == False:
                    files_analyzed += 1
                    for error in file_result.get("errors", []):
                        all_errors.append({
                            "year": file_result.get("year"),
                            "error": error,
                            "file": file_result.get("file_path")
                        })
                        total_errors += 1

    print(f"\nTotal files analyzed: {files_analyzed}")
    print(f"Total errors collected: {total_errors}")
    print(f"Detailed errors parsed: {len(all_errors)}")

    # Categorize all errors
    for error_data in all_errors:
        error_msg = error_data["error"]
        category, field, details = extract_error_pattern(error_msg)
        error_counts[category] += 1
        error_by_field[category][field] += 1

    # Print results
    print("\n" + "="*80)
    print("ERROR CATEGORIZATION SUMMARY")
    print("="*80)

    for category in sorted(error_counts.keys(), key=lambda x: error_counts[x], reverse=True):
        count = error_counts[category]
        percentage = (count / len(all_errors)) * 100 if all_errors else 0
        print(f"\n{category}: {count:,} ({percentage:.1f}%)")

        # Show top fields for this category
        fields = error_by_field[category]
        top_fields = sorted(fields.items(), key=lambda x: x[1], reverse=True)[:5]
        for field, field_count in top_fields:
            print(f"  - {field}: {field_count:,}")

    return {
        "total_errors": total_errors,
        "detailed_errors": len(all_errors),
        "error_counts": dict(error_counts),
        "error_by_field": {k: dict(v) for k, v in error_by_field.items()},
        "all_errors": all_errors
    }

if __name__ == "__main__":
    results = analyze_all_audits()

    # Save detailed results
    output_file = "/home/user/colonial_office_list/reports/error_analysis_detailed.json"
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n\nDetailed results saved to: {output_file}")
