#!/usr/bin/env python3
"""
Generate category summary statistics and verification report.
"""

import json

# Error categorization based on analysis
CATEGORY_A = {
    "type_string_expected": 1122,
    "missing_year_metadata": 72,
    "string_pattern_mismatch": 66,
    "type_number_expected": 6,
    "missing_source_directory": 6
}

CATEGORY_B = {
    "invalid_enum_values": 4060,
    "invalid_type_enum": 668,
    "invalid_relationship_type_enum": 40,
    "unreasonably_high_salary": 59,
    "string_too_short": 46
}

CATEGORY_C = {
    "missing_location": 876,
    "invalid_salary_amount": 427,
    "value_must_be_positive": 118,
    "model_type_error": 26,
    "missing_longitude": 9,
    "missing_latitude": 1
}

CATEGORY_D = {
    "type_list_expected": 14949,
    "missing_required_fields": 5395,
    "missing_relationship_ids": 150,
    "missing_other_fields": 54
}

def calculate_statistics():
    """Calculate comprehensive statistics for each category."""

    total_a = sum(CATEGORY_A.values())
    total_b = sum(CATEGORY_B.values())
    total_c = sum(CATEGORY_C.values())
    total_d = sum(CATEGORY_D.values())
    grand_total = total_a + total_b + total_c + total_d

    print("="*80)
    print("ERROR CATEGORIZATION SUMMARY")
    print("="*80)
    print(f"\nTotal Errors: {grand_total:,}\n")

    # Category A
    print("CATEGORY A: Safe Python Automation (100% Confident)")
    print("-" * 80)
    print(f"Total: {total_a:,} errors ({total_a/grand_total*100:.2f}%)")
    print(f"Confidence: 100%")
    print(f"Expected Success Rate: 98-100%")
    print(f"Expected Fixes: {int(total_a * 0.99)}-{total_a}")
    print("\nError Types:")
    for error_type, count in sorted(CATEGORY_A.items(), key=lambda x: x[1], reverse=True):
        print(f"  • {error_type}: {count:,}")

    # Category B
    print("\n" + "="*80)
    print("CATEGORY B: LLM Agent with High Confidence (85%+ Confident)")
    print("-" * 80)
    print(f"Total: {total_b:,} errors ({total_b/grand_total*100:.2f}%)")
    print(f"Confidence: 85-95%")
    print(f"Expected Success Rate: 85-95%")
    print(f"Expected Fixes: {int(total_b * 0.85)}-{int(total_b * 0.95)}")
    print("\nError Types:")
    for error_type, count in sorted(CATEGORY_B.items(), key=lambda x: x[1], reverse=True):
        print(f"  • {error_type}: {count:,}")

    # Category C
    print("\n" + "="*80)
    print("CATEGORY C: LLM Agent with Human Review (50-85% Confident)")
    print("-" * 80)
    print(f"Total: {total_c:,} errors ({total_c/grand_total*100:.2f}%)")
    print(f"Confidence: 50-85%")
    print(f"Expected Success Rate: 50-85%")
    print(f"Expected Fixes: {int(total_c * 0.50)}-{int(total_c * 0.85)}")
    print("\nError Types:")
    for error_type, count in sorted(CATEGORY_C.items(), key=lambda x: x[1], reverse=True):
        print(f"  • {error_type}: {count:,}")

    # Category D
    print("\n" + "="*80)
    print("CATEGORY D: Requires Re-extraction (<50% Confident)")
    print("-" * 80)
    print(f"Total: {total_d:,} errors ({total_d/grand_total*100:.2f}%)")
    print(f"Confidence: <50% for automated fixes")
    print(f"Expected Success Rate: 90-95% (after re-extraction)")
    print(f"Expected Fixes: {int(total_d * 0.90)}-{int(total_d * 0.95)}")
    print("\nError Types:")
    for error_type, count in sorted(CATEGORY_D.items(), key=lambda x: x[1], reverse=True):
        print(f"  • {error_type}: {count:,}")

    # Cumulative impact
    print("\n" + "="*80)
    print("CUMULATIVE ERROR REDUCTION BY PHASE")
    print("="*80)

    phase1_min = int(total_a * 0.98)
    phase1_max = total_a
    phase2_min = int(total_b * 0.85)
    phase2_max = int(total_b * 0.95)
    phase3_min = int(total_c * 0.50)
    phase3_max = int(total_c * 0.85)
    phase4_min = int(total_d * 0.90)
    phase4_max = int(total_d * 0.95)

    cumulative_min = 0
    cumulative_max = 0

    print(f"\nPhase 1 (Python Automation):")
    cumulative_min += phase1_min
    cumulative_max += phase1_max
    print(f"  Fixed: {phase1_min:,} - {phase1_max:,}")
    print(f"  Cumulative: {cumulative_min:,} - {cumulative_max:,} ({cumulative_min/grand_total*100:.1f}% - {cumulative_max/grand_total*100:.1f}%)")
    print(f"  Remaining: {grand_total-cumulative_max:,} - {grand_total-cumulative_min:,}")

    print(f"\nPhase 2 (LLM High Confidence):")
    cumulative_min += phase2_min
    cumulative_max += phase2_max
    print(f"  Fixed: {phase2_min:,} - {phase2_max:,}")
    print(f"  Cumulative: {cumulative_min:,} - {cumulative_max:,} ({cumulative_min/grand_total*100:.1f}% - {cumulative_max/grand_total*100:.1f}%)")
    print(f"  Remaining: {grand_total-cumulative_max:,} - {grand_total-cumulative_min:,}")

    print(f"\nPhase 3 (LLM + Human Review):")
    cumulative_min += phase3_min
    cumulative_max += phase3_max
    print(f"  Fixed: {phase3_min:,} - {phase3_max:,}")
    print(f"  Cumulative: {cumulative_min:,} - {cumulative_max:,} ({cumulative_min/grand_total*100:.1f}% - {cumulative_max/grand_total*100:.1f}%)")
    print(f"  Remaining: {grand_total-cumulative_max:,} - {grand_total-cumulative_min:,}")

    print(f"\nPhase 4 (Re-extraction):")
    cumulative_min += phase4_min
    cumulative_max += phase4_max
    print(f"  Fixed: {phase4_min:,} - {phase4_max:,}")
    print(f"  Cumulative: {cumulative_min:,} - {cumulative_max:,} ({cumulative_min/grand_total*100:.1f}% - {cumulative_max/grand_total*100:.1f}%)")
    print(f"  Remaining: {grand_total-cumulative_max:,} - {grand_total-cumulative_min:,}")

    print("\n" + "="*80)
    print("FINAL EXPECTED OUTCOME")
    print("="*80)
    print(f"Total Errors Fixed: {cumulative_min:,} - {cumulative_max:,}")
    print(f"Percentage Resolved: {cumulative_min/grand_total*100:.1f}% - {cumulative_max/grand_total*100:.1f}%")
    print(f"Remaining Errors: {grand_total-cumulative_max:,} - {grand_total-cumulative_min:,}")
    print(f"Final Success Rate: {85 + (cumulative_max/grand_total*100/10):.0f}% - {95 + (cumulative_max/grand_total*100/20):.0f}%")

    # Save results
    results = {
        "total_errors": grand_total,
        "categories": {
            "A": {
                "name": "Safe Python Automation",
                "total": total_a,
                "percentage": round(total_a/grand_total*100, 2),
                "confidence": "100%",
                "expected_fixes": [phase1_min, phase1_max],
                "errors": CATEGORY_A
            },
            "B": {
                "name": "LLM High Confidence",
                "total": total_b,
                "percentage": round(total_b/grand_total*100, 2),
                "confidence": "85-95%",
                "expected_fixes": [phase2_min, phase2_max],
                "errors": CATEGORY_B
            },
            "C": {
                "name": "LLM + Human Review",
                "total": total_c,
                "percentage": round(total_c/grand_total*100, 2),
                "confidence": "50-85%",
                "expected_fixes": [phase3_min, phase3_max],
                "errors": CATEGORY_C
            },
            "D": {
                "name": "Re-extraction Required",
                "total": total_d,
                "percentage": round(total_d/grand_total*100, 2),
                "confidence": "<50% (automated), 90-95% (re-extraction)",
                "expected_fixes": [phase4_min, phase4_max],
                "errors": CATEGORY_D
            }
        },
        "cumulative_impact": {
            "total_fixes": [cumulative_min, cumulative_max],
            "percentage_resolved": [
                round(cumulative_min/grand_total*100, 1),
                round(cumulative_max/grand_total*100, 1)
            ],
            "remaining_errors": [grand_total-cumulative_max, grand_total-cumulative_min]
        }
    }

    with open("/home/user/colonial_office_list/reports/category_summary.json", 'w') as f:
        json.dump(results, f, indent=2)

    print(f"\n\nResults saved to: /home/user/colonial_office_list/reports/category_summary.json")

if __name__ == "__main__":
    calculate_statistics()
