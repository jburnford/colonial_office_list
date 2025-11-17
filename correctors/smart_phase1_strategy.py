"""
Smart Phase 1 Strategy: Only fix files worth fixing

Based on investigation findings:
- Category D files (re-extract list): SKIP Phase 1, mark for re-extraction
- Category A-C files (fixable): Apply Phase 1 corrections

Re-extraction List (from investigation):
- 1890: 1,974 errors - fundamental data quality issues
- 1920: 14,219 errors - garbage extraction (words as entities)
- 1909: 5,777 errors - structural issues
- 1928: 2,485 errors - structural issues
- 1949: 1,044 errors - list type structural issues
"""

# Files that MUST be re-extracted (don't waste time on Phase 1)
RE_EXTRACT_FILES = {
    "1890_extracted.json",  # Data quality catastrophe
    "1920_extracted.json",  # Worst offender - 14K errors, garbage data
    "1909_extracted.json",  # 5.7K errors - structural
    "1928_extracted.json",  # 2.5K errors - structural
    "1949_extracted.json",  # 1K errors - list type structural
}

# Files worth fixing with Phase 1 + Phase 2
# These have mostly type/enum/missing field errors that are fixable
FIXABLE_FILES = [
    # All other files not in RE_EXTRACT_FILES
]


def classify_file(filename: str, error_count: int) -> str:
    """
    Classify file into correction strategy.

    Args:
        filename: File name
        error_count: Number of validation errors

    Returns:
        "re_extract", "phase1_phase2", or "valid"
    """
    if filename in RE_EXTRACT_FILES:
        return "re_extract"
    elif error_count == 0:
        return "valid"
    elif error_count > 500:
        # High error count - likely needs re-extraction
        return "re_extract_candidate"
    else:
        # Fixable with Phase 1 + Phase 2
        return "phase1_phase2"


def generate_strategy_report(audit_dir: str = "reports"):
    """Generate strategic correction plan based on audit results"""
    import json
    from pathlib import Path

    # Load audit results
    audit_files = [
        "reports/audit_1867_1900.json",
        "reports/audit_1901_1930.json",
        "reports/audit_1931_1966.json"
    ]

    all_files = []
    for audit_file in audit_files:
        try:
            with open(audit_file, 'r') as f:
                data = json.load(f)
                all_files.extend(data.get("results", []))
        except FileNotFoundError:
            continue

    # Classify files
    strategy = {
        "valid": [],
        "phase1_phase2": [],
        "re_extract_confirmed": [],
        "re_extract_candidate": []
    }

    for file_info in all_files:
        filename = Path(file_info["file_path"]).name
        error_count = file_info["error_count"]
        classification = classify_file(filename, error_count)

        if classification == "valid":
            strategy["valid"].append(filename)
        elif classification == "re_extract":
            strategy["re_extract_confirmed"].append({
                "file": filename,
                "errors": error_count,
                "reason": "Investigation confirmed re-extraction needed"
            })
        elif classification == "re_extract_candidate":
            strategy["re_extract_candidate"].append({
                "file": filename,
                "errors": error_count,
                "reason": f"High error count (>{error_count}) suggests re-extraction"
            })
        else:
            strategy["phase1_phase2"].append({
                "file": filename,
                "errors": error_count
            })

    # Generate report
    report = []
    report.append("=" * 80)
    report.append("SMART CORRECTION STRATEGY")
    report.append("=" * 80)
    report.append("")
    report.append(f"Total files: {len(all_files)}")
    report.append(f"Valid (no action needed): {len(strategy['valid'])}")
    report.append(f"Phase 1 + 2 (fixable): {len(strategy['phase1_phase2'])}")
    report.append(f"Re-extract (confirmed): {len(strategy['re_extract_confirmed'])}")
    report.append(f"Re-extract (candidate): {len(strategy['re_extract_candidate'])}")
    report.append("")

    report.append("-" * 80)
    report.append("RE-EXTRACTION REQUIRED (5 files)")
    report.append("-" * 80)
    for item in strategy["re_extract_confirmed"]:
        report.append(f"  {item['file']:30s} - {item['errors']:5d} errors - {item['reason']}")

    report.append("")
    report.append("-" * 80)
    report.append("FIXABLE WITH PHASE 1 + 2 (Top 10 by error count)")
    report.append("-" * 80)
    fixable_sorted = sorted(strategy["phase1_phase2"], key=lambda x: x["errors"], reverse=True)[:10]
    for item in fixable_sorted:
        report.append(f"  {item['file']:30s} - {item['errors']:5d} errors")

    report.append("")
    report.append("-" * 80)
    report.append("RECOMMENDATION")
    report.append("-" * 80)
    report.append("1. SKIP Phase 1 for re-extraction files (waste of time)")
    report.append("2. Apply Phase 1 to fixable files only")
    report.append("3. Apply Phase 2 (LLM) to fixable files")
    report.append("4. Re-extract the 5 confirmed files with improved methodology")
    report.append("")

    print("\n".join(report))

    # Save to file
    with open("reports/SMART_CORRECTION_STRATEGY.txt", 'w') as f:
        f.write("\n".join(report))

    with open("reports/correction_strategy.json", 'w') as f:
        json.dump(strategy, f, indent=2)

    return strategy


if __name__ == "__main__":
    generate_strategy_report()
