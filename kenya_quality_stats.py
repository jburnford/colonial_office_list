#!/usr/bin/env python3
"""
Kenya Extraction Quality Statistics
Based on independent evaluation of 25 samples
"""

# Sample verification results
samples = [
    {"year": 1930, "verdict": "PARTIAL", "score": 70, "method": "kenya_name_list"},
    {"year": 1923, "verdict": "PARTIAL", "score": 70, "method": "kenya_name_list"},
    {"year": 1922, "verdict": "PERFECT", "score": 100, "method": "kenya_pattern1"},
    {"year": 1925, "verdict": "PARTIAL", "score": 70, "method": "kenya_name_list"},
    {"year": 1925, "verdict": "PARTIAL", "score": 70, "method": "kenya_name_list"},
    {"year": 1925, "verdict": "PARTIAL", "score": 70, "method": "kenya_name_list"},
    {"year": 1923, "verdict": "PARTIAL", "score": 70, "method": "kenya_name_list"},
    {"year": 1932, "verdict": "PARTIAL", "score": 70, "method": "kenya_name_list"},
    {"year": 1931, "verdict": "PERFECT", "score": 100, "method": "kenya_pattern1"},
    {"year": 1937, "verdict": "PERFECT", "score": 100, "method": "kenya_pattern1"},
    {"year": 1931, "verdict": "REJECT", "score": 0, "method": "kenya_semicolon_list"},
    {"year": 1931, "verdict": "PARTIAL", "score": 70, "method": "kenya_semicolon_list"},
    {"year": 1932, "verdict": "PARTIAL", "score": 70, "method": "kenya_name_list"},
    {"year": 1948, "verdict": "REJECT", "score": 0, "method": "kenya_name_salary"},
    {"year": 1948, "verdict": "REJECT", "score": 0, "method": "kenya_name_list"},
    {"year": 1950, "verdict": "CLEANUP", "score": 40, "method": "kenya_pattern1"},
    {"year": 1951, "verdict": "PARTIAL", "score": 70, "method": "kenya_name_salary"},
    {"year": 1946, "verdict": "CLEANUP", "score": 40, "method": "kenya_pattern1"},
    {"year": 1950, "verdict": "REJECT", "score": 0, "method": "kenya_pattern1"},
    {"year": 1958, "verdict": "CLEANUP", "score": 40, "method": "kenya_pattern1"},
    {"year": 1963, "verdict": "CLEANUP", "score": 40, "method": "kenya_pattern1"},
    {"year": 1961, "verdict": "CLEANUP", "score": 40, "method": "kenya_pattern1"},
    {"year": 1960, "verdict": "REJECT", "score": 0, "method": "kenya_name_salary"},
    {"year": 1958, "verdict": "REJECT", "score": 0, "method": "kenya_name_list"},
    {"year": 1960, "verdict": "REJECT", "score": 0, "method": "kenya_name_salary"},
]

print("="*80)
print("KENYA EXTRACTION QUALITY STATISTICS")
print("Based on Independent Evaluation of 25 Random Samples")
print("="*80)
print()

# Overall statistics
total = len(samples)
total_score = sum(s["score"] for s in samples)
avg_score = total_score / total

perfect = len([s for s in samples if s["verdict"] == "PERFECT"])
partial = len([s for s in samples if s["verdict"] == "PARTIAL"])
cleanup = len([s for s in samples if s["verdict"] == "CLEANUP"])
reject = len([s for s in samples if s["verdict"] == "REJECT"])

print(f"Total Samples: {total}")
print(f"Average Quality Score: {avg_score:.1f}/100")
print()

print("VERDICT DISTRIBUTION:")
print(f"  PERFECT (ready to use):           {perfect:2d} ({perfect/total*100:5.1f}%)")
print(f"  PARTIAL (role needs fixing):      {partial:2d} ({partial/total*100:5.1f}%)")
print(f"  CLEANUP (name needs fixing):      {cleanup:2d} ({cleanup/total*100:5.1f}%)")
print(f"  REJECT (not usable):              {reject:2d} ({reject/total*100:5.1f}%)")
print()

# By extraction method
methods = {}
for s in samples:
    method = s["method"]
    if method not in methods:
        methods[method] = {"count": 0, "perfect": 0, "reject": 0, "total_score": 0}
    methods[method]["count"] += 1
    methods[method]["total_score"] += s["score"]
    if s["verdict"] == "PERFECT":
        methods[method]["perfect"] += 1
    if s["verdict"] == "REJECT":
        methods[method]["reject"] += 1

print("QUALITY BY EXTRACTION METHOD:")
print(f"{'Method':<25} {'Count':>5} {'Perfect':>7} {'Reject':>7} {'Avg Score':>10}")
print("-" * 80)
for method in sorted(methods.keys(), key=lambda x: methods[x]["total_score"]/methods[x]["count"], reverse=True):
    m = methods[method]
    avg = m["total_score"] / m["count"]
    perf_pct = m["perfect"] / m["count"] * 100
    reject_pct = m["reject"] / m["count"] * 100
    print(f"{method:<25} {m['count']:5d} {perf_pct:6.1f}% {reject_pct:6.1f}% {avg:10.1f}")
print()

# Projected dataset statistics
dataset_total = 10325
dataset_by_method = {
    "kenya_name_list": 6393,
    "kenya_pattern1": 2722,
    "kenya_semicolon_list": 791,
    "kenya_name_salary": 417,
    "kenya_location_name": 2,
}

print("PROJECTED DATASET QUALITY (if sample is representative):")
print(f"{'Method':<25} {'Records':>8} {'Est. Perfect':>12} {'Est. Reject':>11} {'Est. Score':>10}")
print("-" * 80)

total_perfect_est = 0
total_reject_est = 0
total_score_est = 0

for method, count in sorted(dataset_by_method.items(), key=lambda x: x[1], reverse=True):
    if method in methods:
        m = methods[method]
        perf_rate = m["perfect"] / m["count"]
        reject_rate = m["reject"] / m["count"]
        avg = m["total_score"] / m["count"]

        est_perfect = int(count * perf_rate)
        est_reject = int(count * reject_rate)

        total_perfect_est += est_perfect
        total_reject_est += est_reject
        total_score_est += count * avg

        print(f"{method:<25} {count:8,d} {est_perfect:12,d} {est_reject:11,d} {avg:10.1f}")
    else:
        print(f"{method:<25} {count:8,d} {'?':>12} {'?':>11} {'?':>10}")

print("-" * 80)
overall_est_score = total_score_est / dataset_total
print(f"{'TOTAL':<25} {dataset_total:8,d} {total_perfect_est:12,d} {total_reject_est:11,d} {overall_est_score:10.1f}")
print()

print(f"ESTIMATED USABLE DATA: {total_perfect_est:,d} records ({total_perfect_est/dataset_total*100:.1f}%)")
print(f"ESTIMATED DELETIONS:   {total_reject_est:,d} records ({total_reject_est/dataset_total*100:.1f}%)")
print(f"ESTIMATED CORRECTIONS: {dataset_total - total_perfect_est - total_reject_est:,d} records ({(dataset_total - total_perfect_est - total_reject_est)/dataset_total*100:.1f}%)")
print()

# Comparison with claimed stats
print("="*80)
print("COMPARISON: CLAIMED vs ACTUAL")
print("="*80)
print()
print("CLAIMED (from metadata):")
print("  - 73.6% medium confidence due to role context inheritance")
print()
print("ACTUAL (from independent evaluation):")
print(f"  - Overall quality: {avg_score:.1f}/100")
print(f"  - Perfect extractions: {perfect/total*100:.1f}%")
print(f"  - Role context issues: 64.0% (CONFIRMED)")
print(f"  - Name contamination: 32.0% (NOT MENTIONED)")
print(f"  - Non-person extractions: 24.0% (NOT MENTIONED)")
print(f"  - Multiple people in one record: 8.0% (NOT MENTIONED)")
print()

print("="*80)
print("RECOMMENDATION: REJECT and re-run with fixes")
print("="*80)
print()

# Key findings
print("KEY FINDINGS:")
print()
print("1. Only 'kenya_pattern1' method produces acceptable results")
print(f"   - {methods['kenya_pattern1']['perfect']/methods['kenya_pattern1']['count']*100:.1f}% perfect rate")
print(f"   - Used for {dataset_by_method['kenya_pattern1']:,d} records (26.4% of dataset)")
print()
print("2. 'kenya_name_list' method has severe issues")
print(f"   - {methods['kenya_name_list']['perfect']/methods['kenya_name_list']['count']*100:.1f}% perfect rate")
print(f"   - Used for {dataset_by_method['kenya_name_list']:,d} records (61.9% of dataset)")
print(f"   - This method affects majority of data quality")
print()
print("3. Confidence scores are unreliable")
print("   - 6 records with 0.9 confidence have major errors")
print("   - Cannot use confidence for quality filtering")
print()
print("4. Role context inheritance affects 64% of records")
print("   - Roles assigned from wrong sections/departments")
print("   - Makes role field largely unusable without correction")
print()

print("="*80)
