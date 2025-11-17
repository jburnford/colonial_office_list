#!/usr/bin/env python3
"""
Comprehensive error analysis using both detailed errors and summary statistics.
"""

import json
from collections import defaultdict

def analyze_comprehensive():
    """Use summary statistics from audit files for accurate totals."""

    # Load audit files
    with open("/home/user/colonial_office_list/reports/audit_1867_1900.json") as f:
        audit_1867_1900 = json.load(f)

    with open("/home/user/colonial_office_list/reports/audit_1901_1930.json") as f:
        audit_1901_1930 = json.load(f)

    with open("/home/user/colonial_office_list/reports/audit_1931_1966.json") as f:
        audit_1931_1966 = json.load(f)

    # Consolidated error categories
    error_catalog = defaultdict(int)

    # From 1867-1900: need to manually count (no summary provided)
    # We'll use detailed error parsing
    for result in audit_1867_1900.get("results", []):
        for error in result.get("errors", []):
            if "missing: Field required" in error:
                field = error.split(" -> ")[-1].split("]")[0]
                if field == "longitude":
                    error_catalog["missing_longitude"] += 1
                elif field == "latitude":
                    error_catalog["missing_latitude"] += 1
                elif field in ["source_id", "target_id"]:
                    error_catalog["missing_relationship_ids"] += 1
                elif field == "year":
                    error_catalog["missing_year_metadata"] += 1
                elif field == "source_directory":
                    error_catalog["missing_source_directory"] += 1
                elif field == "location":
                    error_catalog["missing_location"] += 1
                else:
                    error_catalog["missing_other_fields"] += 1

            elif "enum:" in error:
                if "relationship_type" in error:
                    error_catalog["invalid_relationship_type_enum"] += 1
                elif "-> type]" in error:
                    error_catalog["invalid_type_enum"] += 1
                else:
                    error_catalog["invalid_other_enum"] += 1

            elif "float_type:" in error or "int_type:" in error or "Input should be a valid number" in error:
                error_catalog["type_number_expected"] += 1

            elif "string_type:" in error or "Input should be a valid string" in error:
                error_catalog["type_string_expected"] += 1

            elif "list_type:" in error or "Input should be a valid list" in error:
                error_catalog["type_list_expected"] += 1

            elif "string_pattern_mismatch:" in error:
                error_catalog["string_pattern_mismatch"] += 1

            elif "string_too_short:" in error or "at least 1 character" in error:
                error_catalog["string_too_short"] += 1

            elif "greater_than:" in error or "Value must be greater than" in error:
                error_catalog["value_must_be_positive"] += 1

            elif "model_type:" in error:
                error_catalog["model_type_error"] += 1

            else:
                error_catalog["other_errors"] += 1

    # From 1901-1930: use provided error_patterns
    patterns_1901_1930 = audit_1901_1930.get("error_patterns", {})
    error_catalog["type_list_expected"] += patterns_1901_1930.get("Type mismatch (list expected)", 0)
    error_catalog["missing_required_fields"] += patterns_1901_1930.get("Missing required field", 0)
    error_catalog["invalid_enum_values"] += patterns_1901_1930.get("Invalid enum value", 0)
    error_catalog["type_string_expected"] += patterns_1901_1930.get("Other: string_type", 0)
    error_catalog["unreasonably_high_salary"] += patterns_1901_1930.get("Unreasonably high salary", 0)
    error_catalog["string_pattern_mismatch"] += patterns_1901_1930.get("Other: string_pattern_mismatch", 0)
    error_catalog["model_type_error"] += patterns_1901_1930.get("Other: model_type", 0)
    error_catalog["value_must_be_positive"] += patterns_1901_1930.get("Value must be greater than 0", 0)
    error_catalog["string_too_short"] += patterns_1901_1930.get("Other: string_too_short", 0)
    error_catalog["type_number_expected"] += patterns_1901_1930.get("Type mismatch (number expected)", 0)

    # From 1931-1966: use provided error_analysis
    error_categories_1931_1966 = audit_1931_1966.get("error_analysis", {}).get("error_categories", [])
    for cat in error_categories_1931_1966:
        category_name = cat.get("category", "")
        count = cat.get("count", 0)

        if "Invalid list type" in category_name:
            error_catalog["type_list_expected"] += count
        elif "Invalid enum value: type" in category_name:
            error_catalog["invalid_type_enum"] += count
        elif "Invalid salary amount" in category_name:
            error_catalog["invalid_salary_amount"] += count
        elif "Value must be greater than 0" in category_name:
            error_catalog["value_must_be_positive"] += count
        elif "Invalid string type" in category_name:
            error_catalog["type_string_expected"] += count
        elif "String too short" in category_name:
            error_catalog["string_too_short"] += count
        elif "Missing required field: longitude" in category_name:
            error_catalog["missing_longitude"] += count
        elif "Missing required field: latitude" in category_name:
            error_catalog["missing_latitude"] += count
        elif "String pattern mismatch" in category_name:
            error_catalog["string_pattern_mismatch"] += count

    # Calculate totals
    total_errors = sum(error_catalog.values())

    # Summary from audit files
    total_1867_1900 = audit_1867_1900.get("summary", {}).get("total_errors", 0)
    total_1901_1930 = audit_1901_1930.get("summary", {}).get("total_errors", 0)
    total_1931_1966 = audit_1931_1966.get("summary_statistics", {}).get("total_errors", 0)
    grand_total = total_1867_1900 + total_1901_1930 + total_1931_1966

    print("="*80)
    print("COMPREHENSIVE ERROR ANALYSIS")
    print("="*80)
    print(f"\nTotal Errors by Period:")
    print(f"  1867-1900: {total_1867_1900:,}")
    print(f"  1901-1930: {total_1901_1930:,}")
    print(f"  1931-1966: {total_1931_1966:,}")
    print(f"  GRAND TOTAL: {grand_total:,}")

    print(f"\n" + "="*80)
    print("ERROR CATEGORIES (sorted by count)")
    print("="*80)

    for category in sorted(error_catalog.keys(), key=lambda x: error_catalog[x], reverse=True):
        count = error_catalog[category]
        percentage = (count / grand_total * 100) if grand_total > 0 else 0
        print(f"{category:45s} {count:7,} ({percentage:5.2f}%)")

    return {
        "grand_total": grand_total,
        "error_catalog": dict(error_catalog),
        "by_period": {
            "1867-1900": total_1867_1900,
            "1901-1930": total_1901_1930,
            "1931-1966": total_1931_1966
        }
    }

if __name__ == "__main__":
    results = analyze_comprehensive()

    with open("/home/user/colonial_office_list/reports/comprehensive_error_catalog.json", 'w') as f:
        json.dump(results, f, indent=2)

    print("\n" + "="*80)
    print(f"Results saved to: /home/user/colonial_office_list/reports/comprehensive_error_catalog.json")
