#!/usr/bin/env python3
import json

# Load v2 results
with open('/home/user/colonial_office_list/kenya_v2_evaluation_results.json', 'r') as f:
    v2_data = json.load(f)

evaluations = v2_data['evaluations']

# Detailed scoring similar to v1
scores = []
for eval_result in evaluations:
    if eval_result['is_perfect']:
        score = 100
    elif eval_result['severity'] == 'critical':
        # Check if it's non-person vs contamination
        issues_text = ' '.join(eval_result['issues'])
        if 'non-person' in issues_text.lower():
            score = 0  # Critical failure
        elif 'contamination' in issues_text.lower() or 'prefix' in issues_text.lower():
            score = 40  # Recoverable with cleanup
        else:
            score = 30  # Other critical issue
    elif eval_result['severity'] == 'major':
        score = 70  # Can't verify but likely usable
    elif eval_result['severity'] == 'minor':
        score = 85  # Minor issue
    else:
        score = 100

    scores.append(score)
    eval_result['quality_score'] = score

# Calculate overall quality
overall_quality = sum(scores) / len(scores)

# Detailed statistics
total = len(evaluations)
perfect = sum(1 for e in evaluations if e['is_perfect'])
critical = sum(1 for e in evaluations if e['severity'] == 'critical')
major = sum(1 for e in evaluations if e['severity'] == 'major')
minor = sum(1 for e in evaluations if e['severity'] == 'minor')

# Calculate usability categories
usable_as_is = perfect
needs_cleanup = sum(1 for e in evaluations if e['severity'] == 'critical' and
                   any('contamination' in i.lower() or 'prefix' in i.lower() for i in e['issues']))
must_delete = sum(1 for e in evaluations if e['severity'] == 'critical' and
                 any('non-person' in i.lower() for i in e['issues']))
uncertain = major

print("=" * 80)
print("KENYA V2 (FIXED) - COMPREHENSIVE QUALITY EVALUATION")
print("=" * 80)
print(f"\nOVERALL QUALITY SCORE: {overall_quality:.1f}/100")

if overall_quality >= 90:
    status = "✅ EXCELLENT - Production Ready"
elif overall_quality >= 80:
    status = "✓ GOOD - Research Grade"
elif overall_quality >= 70:
    status = "⚠️  ACCEPTABLE - Usable with Caveats"
elif overall_quality >= 50:
    status = "⚠️  POOR - Major Issues Remain"
else:
    status = "❌ FAIL - Unsuitable for Use"

print(f"STATUS: {status}")

print("\n" + "=" * 80)
print("QUALITY METRICS")
print("=" * 80)
print(f"\nPerfect extractions:        {perfect}/{total} ({perfect/total*100:.1f}%)")
print(f"Name contamination:         {v2_data['metadata']['name_contamination_rate']*100:.1f}%")
print(f"Non-person extraction:      {v2_data['metadata']['non_person_rate']*100:.1f}%")
print(f"Critical issues:            {critical}/{total} ({critical/total*100:.1f}%)")
print(f"Major issues:               {major}/{total} ({major/total*100:.1f}%)")

print("\n" + "=" * 80)
print("COMPARISON TO V1 (BEFORE FIXES)")
print("=" * 80)

v1_quality = 49.2
v1_perfect = 12.0
v1_contamination = 32.0
v1_non_person = 24.0

print(f"\n{'Metric':<30} {'V1 (Before)':<15} {'V2 (After)':<15} {'Change':<15}")
print("-" * 75)
print(f"{'Overall Quality':<30} {v1_quality:<15.1f} {overall_quality:<15.1f} {overall_quality - v1_quality:+.1f}")
print(f"{'Perfect Rate %':<30} {v1_perfect:<15.1f} {perfect/total*100:<15.1f} {perfect/total*100 - v1_perfect:+.1f}")
print(f"{'Name Contamination %':<30} {v1_contamination:<15.1f} {v2_data['metadata']['name_contamination_rate']*100:<15.1f} {v2_data['metadata']['name_contamination_rate']*100 - v1_contamination:+.1f}")
print(f"{'Non-Person Rate %':<30} {v1_non_person:<15.1f} {v2_data['metadata']['non_person_rate']*100:<15.1f} {v2_data['metadata']['non_person_rate']*100 - v1_non_person:+.1f}")

print("\n" + "=" * 80)
print("DATA USABILITY BREAKDOWN")
print("=" * 80)
print(f"\n✓ Usable as-is:             {usable_as_is}/{total} ({usable_as_is/total*100:.1f}%)")
print(f"⚠️  Needs cleanup:            {needs_cleanup}/{total} ({needs_cleanup/total*100:.1f}%)")
print(f"❌ Must delete:              {must_delete}/{total} ({must_delete/total*100:.1f}%)")
print(f"? Uncertain (can't verify): {uncertain}/{total} ({uncertain/total*100:.1f}%)")

print("\n" + "=" * 80)
print("PROJECTED DATASET QUALITY (10,180 total records)")
print("=" * 80)
total_records = 10180
print(f"\n✓ Perfect extractions:      ~{int(total_records * perfect/total):,} ({perfect/total*100:.1f}%)")
print(f"⚠️  Needs cleanup:           ~{int(total_records * needs_cleanup/total):,} ({needs_cleanup/total*100:.1f}%)")
print(f"❌ Should be deleted:       ~{int(total_records * must_delete/total):,} ({must_delete/total*100:.1f}%)")
print(f"? Uncertain:                ~{int(total_records * uncertain/total):,} ({uncertain/total*100:.1f}%)")
print(f"\n{'='*80}")
print(f"Effective usable data:      ~{int(total_records * usable_as_is/total):,} records ({usable_as_is/total*100:.1f}%)")

print("\n" + "=" * 80)
print("IMPROVEMENT ANALYSIS")
print("=" * 80)
print(f"\nQuality Score Improvement:  {v1_quality:.1f}/100 → {overall_quality:.1f}/100 ({overall_quality - v1_quality:+.1f} points)")
print(f"Perfect Rate Improvement:   {v1_perfect:.1f}% → {perfect/total*100:.1f}% ({perfect/total*100 - v1_perfect:+.1f} percentage points)")
print(f"Non-Person Reduction:       {v1_non_person:.1f}% → {v2_data['metadata']['non_person_rate']*100:.1f}% ({v2_data['metadata']['non_person_rate']*100 - v1_non_person:.1f} pp)")
print(f"Name Contamination Reduction: {v1_contamination:.1f}% → {v2_data['metadata']['name_contamination_rate']*100:.1f}% ({v2_data['metadata']['name_contamination_rate']*100 - v1_contamination:.1f} pp)")

# Calculate percentage improvements
quality_improvement = ((overall_quality - v1_quality) / v1_quality) * 100
perfect_improvement = ((perfect/total*100 - v1_perfect) / v1_perfect) * 100 if v1_perfect > 0 else 0
non_person_reduction = ((v1_non_person - v2_data['metadata']['non_person_rate']*100) / v1_non_person) * 100 if v1_non_person > 0 else 0

print(f"\nRelative Improvements:")
print(f"  Quality score:            {quality_improvement:+.1f}% improvement")
print(f"  Perfect rate:             {perfect_improvement:+.1f}% improvement")
print(f"  Non-person rate:          {non_person_reduction:.1f}% reduction")

# Save comprehensive results
comprehensive_results = {
    'overall_quality_score': overall_quality,
    'status': status,
    'comparison_to_v1': {
        'v1_quality': v1_quality,
        'v2_quality': overall_quality,
        'improvement': overall_quality - v1_quality,
        'v1_perfect_rate': v1_perfect,
        'v2_perfect_rate': perfect/total*100,
        'v1_contamination_rate': v1_contamination,
        'v2_contamination_rate': v2_data['metadata']['name_contamination_rate']*100,
        'v1_non_person_rate': v1_non_person,
        'v2_non_person_rate': v2_data['metadata']['non_person_rate']*100,
    },
    'evaluations': evaluations,
    'sample_size': total,
}

with open('/home/user/colonial_office_list/kenya_v2_comprehensive_results.json', 'w') as f:
    json.dump(comprehensive_results, f, indent=2)

print("\n\nComprehensive results saved to: kenya_v2_comprehensive_results.json")
