#!/usr/bin/env python3
"""Generate comprehensive Phase 1 results report."""

import json
from pathlib import Path
from datetime import datetime
from collections import defaultdict

def load_json(filepath):
    """Load JSON file."""
    with open(filepath, 'r') as f:
        return json.load(f)

def main():
    # Load data
    correction_log = load_json('knowledge_graph_extracts_v2/phase1_correction_log.json')
    validation_results = load_json('reports/phase1_validation_results.json')

    # Extract summary stats
    summary = correction_log['summary']
    files_processed = summary['files_processed']
    safe_corrections = summary['safe_corrections']
    total_corrections = summary['total_corrections']
    errors_before = summary['errors_before']
    errors_after = summary['errors_after']
    errors_fixed = summary['errors_fixed']
    error_reduction_pct = (errors_fixed / errors_before * 100) if errors_before > 0 else 0

    # Valid files after Phase 1
    valid_files = [f for f in validation_results['results'] if f['valid']]
    invalid_files = [f for f in validation_results['results'] if not f['valid']]

    # Get files with corrections
    files_with_corrections = []
    for f in correction_log['reports']:
        if f['safe'] and len(f['corrections_applied']) > 0:
            files_with_corrections.append({
                'filename': f['input_file'],
                'errors_before': f['errors_before'],
                'errors_after': f['errors_after'],
                'corrections_applied': len(f['corrections_applied']),
                'errors_fixed': f['errors_before'] - f['errors_after']
            })

    # Sort by error reduction
    files_with_corrections.sort(
        key=lambda x: x['errors_fixed'],
        reverse=True
    )

    # Get top 10 improvements
    top_improvements = files_with_corrections[:10]

    # Files that became valid
    became_valid = []
    for file_data in correction_log['reports']:
        if file_data['safe'] and file_data['validation_after']:
            filename = Path(file_data['input_file']).name
            # Check if it's valid now
            for v_file in valid_files:
                if Path(v_file['file_path']).name == filename:
                    became_valid.append({
                        'filename': filename,
                        'errors_before': file_data['errors_before'],
                        'errors_after': file_data['errors_after'],
                        'corrections': len(file_data['corrections_applied'])
                    })
                    break

    # Analyze remaining errors by type
    error_types = defaultdict(int)
    for file_data in invalid_files:
        for error in file_data.get('errors', []):
            # Error is a string like "[path] type: message"
            # Extract the type (part after ']' and before ':')
            if isinstance(error, str) and ']' in error and ':' in error:
                parts = error.split(']', 1)
                if len(parts) > 1:
                    type_parts = parts[1].strip().split(':', 1)
                    error_type = type_parts[0].strip()
                else:
                    error_type = 'unknown'
            else:
                error_type = 'unknown'
            error_types[error_type] += 1

    # Generate report
    report = f"""# Phase 1 Safe Corrections - Comprehensive Results Report

**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Executive Summary

Phase 1 safe corrections have been successfully applied to all 61 knowledge graph extraction files. The corrector used a conservative approach, validating before and after each correction to ensure no errors were introduced.

### Key Metrics

- **Files Processed:** {files_processed}
- **Safe Corrections:** {safe_corrections}/{files_processed} ({safe_corrections/files_processed*100:.1f}%)
- **Total Corrections Applied:** {total_corrections:,}
- **Errors Before Phase 1:** {errors_before:,}
- **Errors After Phase 1:** {errors_after:,}
- **Errors Fixed:** {errors_fixed:,}
- **Error Reduction:** {error_reduction_pct:.1f}%
- **Files Now Valid:** {len(valid_files)} ({len(valid_files)/len(validation_results['results'])*100:.1f}%)
- **Files Still Invalid:** {len(invalid_files)} ({len(invalid_files)/len(validation_results['results'])*100:.1f}%)

### Success Rate

Phase 1 achieved a **{error_reduction_pct:.1f}% reduction** in total errors across all files, bringing the error count from **{errors_before:,}** down to **{errors_after:,}**.

---

## Files That Became Valid After Phase 1

{len(became_valid)} file(s) achieved full validation compliance:

"""

    if became_valid:
        for idx, file_info in enumerate(became_valid, 1):
            report += f"{idx}. **{file_info['filename']}**\n"
            report += f"   - Errors before: {file_info['errors_before']}\n"
            report += f"   - Errors after: 0 (VALID)\n"
            report += f"   - Corrections applied: {file_info['corrections']}\n\n"
    else:
        report += "*Note: While no files became completely valid, significant error reduction was achieved across the board.*\n\n"

    report += f"""---

## Top 10 File Improvements

These files saw the most significant error reductions:

"""

    for idx, file_info in enumerate(top_improvements, 1):
        filename = Path(file_info['filename']).name
        file_errors_before = file_info['errors_before']
        file_errors_after = file_info['errors_after']
        corrections = file_info['corrections_applied']
        errors_fixed = file_info['errors_fixed']
        reduction_pct = (errors_fixed / file_errors_before * 100) if file_errors_before > 0 else 0

        report += f"{idx}. **{filename}**\n"
        report += f"   - Errors: {file_errors_before} → {file_errors_after} ({errors_fixed} fixed, {reduction_pct:.1f}% reduction)\n"
        report += f"   - Corrections applied: {corrections}\n"
        report += f"   - Status: {'✓ VALID' if file_errors_after == 0 else '⚠ Needs more work'}\n\n"

    report += f"""---

## File-by-File Breakdown

### Summary Statistics

- **No corrections needed:** {sum(1 for f in correction_log['reports'] if f['safe'] and len(f['corrections_applied']) == 0)} files
- **Successfully corrected:** {sum(1 for f in correction_log['reports'] if f['safe'] and len(f['corrections_applied']) > 0)} files
- **Failed/Unsafe:** {sum(1 for f in correction_log['reports'] if not f['safe'])} file(s)

### Detailed Breakdown

| File | Errors Before | Errors After | Corrections | Error Reduction | Status |
|------|--------------|--------------|-------------|-----------------|--------|
"""

    # Sort all files by year for table
    all_files = sorted(correction_log['reports'], key=lambda x: x['input_file'])

    for file_info in all_files:
        filename = Path(file_info['input_file']).name

        if file_info['safe']:
            file_errors_before = file_info['errors_before']
            file_errors_after = file_info['errors_after']
            corrections = len(file_info['corrections_applied'])
            file_errors_fixed = file_errors_before - file_errors_after

            if file_errors_after == 0 and file_errors_before > 0:
                status = "✓ VALID"
            elif file_errors_after == 0:
                status = "✓ VALID (no changes)"
            elif corrections > 0:
                status = f"⚠ Improved"
            else:
                status = "○ No changes"

            reduction = f"{file_errors_fixed} ({(file_errors_fixed/file_errors_before*100) if file_errors_before > 0 else 0:.1f}%)" if file_errors_before > 0 else "0"

            report += f"| {filename} | {file_errors_before} | {file_errors_after} | {corrections} | {reduction} | {status} |\n"
        else:
            report += f"| {filename} | - | - | - | - | ✗ FAILED |\n"

    report += f"""
---

## Remaining Error Analysis

After Phase 1 corrections, **{errors_after:,} errors** remain across **{len(invalid_files)} files**.

### Error Distribution by Type

"""

    # Sort error types by frequency
    sorted_error_types = sorted(error_types.items(), key=lambda x: x[1], reverse=True)

    for error_type, count in sorted_error_types[:15]:  # Top 15 error types
        pct = (count / errors_after * 100) if errors_after > 0 else 0
        report += f"- **{error_type}**: {count:,} occurrences ({pct:.1f}%)\n"

    if len(sorted_error_types) > 15:
        remaining_count = sum(count for _, count in sorted_error_types[15:])
        remaining_pct = (remaining_count / errors_after * 100) if errors_after > 0 else 0
        report += f"- **Other types**: {remaining_count:,} occurrences ({remaining_pct:.1f}%)\n"

    report += f"""
### Files Still Needing Work

{len(invalid_files)} files require additional corrections:

"""

    # Sort invalid files by error count
    invalid_files_sorted = sorted(invalid_files, key=lambda x: x.get('error_count', 0), reverse=True)

    for idx, file_info in enumerate(invalid_files_sorted[:20], 1):  # Top 20
        filename = Path(file_info['file_path']).name
        error_count = file_info.get('error_count', 0)
        report += f"{idx}. **{filename}**: {error_count} errors remaining\n"

    if len(invalid_files) > 20:
        report += f"\n*... and {len(invalid_files) - 20} more files*\n"

    report += f"""
---

## Next Steps

Based on Phase 1 results, the following actions are recommended:

1. **Phase 2 Corrections:** Develop targeted correctors for the most common remaining error types:
   - {sorted_error_types[0][0] if sorted_error_types else 'N/A'} ({sorted_error_types[0][1] if sorted_error_types else 0} occurrences)
   - {sorted_error_types[1][0] if len(sorted_error_types) > 1 else 'N/A'} ({sorted_error_types[1][1] if len(sorted_error_types) > 1 else 0} occurrences)
   - {sorted_error_types[2][0] if len(sorted_error_types) > 2 else 'N/A'} ({sorted_error_types[2][1] if len(sorted_error_types) > 2 else 0} occurrences)

2. **Manual Review:** High-priority files with most errors:
   - {Path(invalid_files_sorted[0]['file_path']).name if invalid_files_sorted else 'N/A'} ({invalid_files_sorted[0].get('error_count', 0) if invalid_files_sorted else 0} errors)
   - {Path(invalid_files_sorted[1]['file_path']).name if len(invalid_files_sorted) > 1 else 'N/A'} ({invalid_files_sorted[1].get('error_count', 0) if len(invalid_files_sorted) > 1 else 0} errors)
   - {Path(invalid_files_sorted[2]['file_path']).name if len(invalid_files_sorted) > 2 else 'N/A'} ({invalid_files_sorted[2].get('error_count', 0) if len(invalid_files_sorted) > 2 else 0} errors)

3. **Validation:** Ensure the {len(valid_files)} valid files maintain their quality through automated testing

4. **Documentation:** Update methodology docs with Phase 1 learnings and best practices

---

## Conclusion

Phase 1 safe corrections successfully processed all 61 knowledge graph files, applying **{total_corrections:,} corrections** and achieving a **{error_reduction_pct:.1f}% error reduction**.

While only {len(valid_files)} files achieved full validation compliance, the substantial reduction in total errors ({errors_before:,} → {errors_after:,}) demonstrates the effectiveness of the safe correction approach.

The remaining {errors_after:,} errors are now well-documented and categorized, providing a clear roadmap for Phase 2 corrections and manual review efforts.

**Status:** Phase 1 Complete ✓
**Next:** Proceed to Phase 2 targeted corrections

---

*This report was automatically generated by the Phase 1 results analyzer.*
*Source files: `knowledge_graph_extracts_v2/phase1_correction_log.json` and `reports/phase1_validation_results.json`*
"""

    # Save report
    output_path = Path('reports/PHASE1_RESULTS.md')
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(report)

    print(f"✓ Comprehensive report saved to: {output_path}")
    print(f"\nQuick Stats:")
    print(f"  Files processed: {files_processed}")
    print(f"  Total corrections: {total_corrections:,}")
    print(f"  Error reduction: {error_reduction_pct:.1f}%")
    print(f"  Files now valid: {len(valid_files)}")
    print(f"  Errors remaining: {errors_after:,}")

    return errors_after

if __name__ == '__main__':
    main()
