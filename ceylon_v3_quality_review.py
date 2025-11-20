#!/usr/bin/env python3
"""
Quality Review Script for Ceylon v3 Specialized Extractor
"""

import json
import random
from collections import Counter, defaultdict
import re

# Load the v3 extraction
with open('/home/user/colonial_office_list/ceylon_1867_v3_specialized.json', 'r') as f:
    v3_data = json.load(f)

# Load source file
with open('/home/user/colonial_office_list/output_3/1867_manual_parsed/ceylon.txt', 'r') as f:
    source_lines = f.readlines()

print("="*80)
print("CEYLON V3 EXTRACTION QUALITY REVIEW")
print("="*80)
print()

# 1. OVERVIEW STATISTICS
print("1. OVERVIEW STATISTICS")
print("-" * 80)
metadata = v3_data['metadata']
people = v3_data['people']

print(f"Total people extracted: {len(people)}")
print(f"Filtered out: {metadata['phases']['validation']['filtered_out']}")
print(f"Average confidence: {metadata['phases']['validation']['avg_confidence']:.3f}")
print()

# Count by extraction method
method_counts = Counter(p['extraction_method'] for p in people)
print("Extraction methods:")
for method, count in sorted(method_counts.items()):
    print(f"  {method}: {count} ({count/len(people)*100:.1f}%)")
print()

# Confidence distribution
confidences = [p['confidence'] for p in people]
print("Confidence distribution:")
print(f"  High (>= 0.9): {sum(1 for c in confidences if c >= 0.9)} ({sum(1 for c in confidences if c >= 0.9)/len(confidences)*100:.1f}%)")
print(f"  Medium (0.7-0.89): {sum(1 for c in confidences if 0.7 <= c < 0.9)} ({sum(1 for c in confidences if 0.7 <= c < 0.9)/len(confidences)*100:.1f}%)")
print(f"  Low (< 0.7): {sum(1 for c in confidences if c < 0.7)} ({sum(1 for c in confidences if c < 0.7)/len(confidences)*100:.1f}%)")
print()

# Ceylon-specific filters applied
print("Ceylon-specific filters:")
for key, value in metadata['ceylon_specific'].items():
    print(f"  {key}: {value}")
print()

# 2. SAMPLE RANDOM RECORDS
print("\n2. SAMPLE VERIFICATION (20 Random Records)")
print("="*80)

# Sample 20 random records - stratified by confidence and method
high_conf = [p for p in people if p['confidence'] >= 0.9]
med_conf = [p for p in people if 0.7 <= p['confidence'] < 0.9]
low_conf = [p for p in people if p['confidence'] < 0.7]

# Sample proportionally
sample_size = min(20, len(people))
sample = []
if high_conf:
    sample.extend(random.sample(high_conf, min(12, len(high_conf))))
if med_conf:
    sample.extend(random.sample(med_conf, min(6, len(med_conf))))
if low_conf:
    sample.extend(random.sample(low_conf, min(2, len(low_conf))))

# Limit to 20
sample = sample[:sample_size]

# Error tracking
error_categories = defaultdict(list)
perfect_count = 0
minor_error_count = 0
major_error_count = 0

# Common location names to check for
CEYLON_LOCATIONS = [
    'Colombo', 'Kandy', 'Galle', 'Jaffna', 'Trincomalee', 'Batticaloa',
    'Matura', 'Hambantotte', 'Ratnapoora', 'Negombo', 'Chilaw', 'Manaar',
    'Western Province', 'Central Province', 'Southern Province',
    'Northern Province', 'Eastern Province', 'North Western Province',
    'Kurnegalle', 'Putlam', 'Mulletivoe', 'Nuwakalawiya', 'Matella',
    'Badulla', 'Nuwera Ellia', 'Kaugalle'
]

# Common qualifications
QUALIFICATIONS = [
    'M.D.', 'M.R.C.S.', 'F.R.C.S.', 'B.A.', 'M.A.', 'M. Inst. C.E.',
    'Assoc. Inst. C.E.', 'R.E.', 'Knt.', 'K.C.B.', 'G.C.B.'
]

# Common role keywords that should NOT be roles
WRONG_ROLE_KEYWORDS = ['Province', 'Circuit', 'Department']

print("\nSample #  | Name | Role | Confidence | Issues")
print("-" * 80)

for i, person in enumerate(sample, 1):
    line_num = person['line_number']

    # Get source line (adjust for 0-indexing)
    source_line = source_lines[line_num - 1].strip() if line_num <= len(source_lines) else ""

    issues = []

    # Check 1: Role is actually a location
    role = person['role']
    if any(loc in role for loc in CEYLON_LOCATIONS):
        issues.append("LOCATION_AS_ROLE")
        error_categories['location_as_role'].append({
            'name': person['name'],
            'role': role,
            'line': line_num
        })

    # Check 2: Role is actually a qualification
    if any(qual in role for qual in QUALIFICATIONS):
        issues.append("QUALIFICATION_AS_ROLE")
        error_categories['qualification_as_role'].append({
            'name': person['name'],
            'role': role,
            'line': line_num
        })

    # Check 3: Role contains wrong keywords
    if any(keyword in role for keyword in WRONG_ROLE_KEYWORDS):
        issues.append("WRONG_CONTEXT")
        error_categories['wrong_context'].append({
            'name': person['name'],
            'role': role,
            'line': line_num
        })

    # Check 4: Plural roles (e.g., "Writers")
    if role.endswith('s') and role not in ['Empress', 'Princess', 'Assistant', 'Mistress']:
        # Common plural endings
        issues.append("PLURAL_ROLE")
        error_categories['plural_role'].append({
            'name': person['name'],
            'role': role,
            'line': line_num
        })

    # Check 5: Name appears to be a role word
    name = person['name']
    if any(word in name.lower() for word in ['general', 'governor', 'secretary', 'agent', 'officer']):
        issues.append("NAME_AS_ROLE")
        error_categories['name_as_role'].append({
            'name': name,
            'role': role,
            'line': line_num
        })

    # Check 6: Verify name actually appears in source
    if name not in source_line:
        issues.append("NAME_NOT_IN_SOURCE")
        error_categories['name_not_in_source'].append({
            'name': name,
            'source': source_line,
            'line': line_num
        })

    # Categorize error severity
    if not issues:
        perfect_count += 1
        status = "✓ PERFECT"
    elif len(issues) == 1 and issues[0] in ['PLURAL_ROLE']:
        minor_error_count += 1
        status = "~ MINOR"
    else:
        major_error_count += 1
        status = "✗ MAJOR"

    # Print sample
    issues_str = ", ".join(issues) if issues else "None"
    print(f"{i:2d}.       | {name[:20]:20s} | {role[:30]:30s} | {person['confidence']:.2f} | {issues_str}")
    if issues:
        print(f"          Source: {source_line[:75]}")
        print()

print("\n" + "="*80)
print("3. ERROR ANALYSIS")
print("="*80)

if error_categories:
    for error_type, instances in sorted(error_categories.items()):
        print(f"\n{error_type.upper().replace('_', ' ')} ({len(instances)} instances):")
        for inst in instances[:3]:  # Show first 3 examples
            print(f"  - {inst['name']}: '{inst['role']}' (line {inst['line']})")
        if len(instances) > 3:
            print(f"  ... and {len(instances) - 3} more")
else:
    print("No errors detected in sample!")

print("\n" + "="*80)
print("4. QUALITY SCORE")
print("="*80)

total_sampled = len(sample)
perfect_pct = (perfect_count / total_sampled * 100) if total_sampled > 0 else 0
minor_pct = (minor_error_count / total_sampled * 100) if total_sampled > 0 else 0
major_pct = (major_error_count / total_sampled * 100) if total_sampled > 0 else 0

# Calculate overall quality score (0-100)
# Perfect = 100 points, Minor = 80 points, Major = 0 points
quality_score = (perfect_count * 100 + minor_error_count * 80) / total_sampled if total_sampled > 0 else 0

print(f"Sample size: {total_sampled}")
print(f"Perfect records: {perfect_count} ({perfect_pct:.1f}%)")
print(f"Minor errors: {minor_error_count} ({minor_pct:.1f}%)")
print(f"Major errors: {major_error_count} ({major_pct:.1f}%)")
print()
print(f"OVERALL QUALITY SCORE: {quality_score:.1f}/100")
print()

# Comparison to v2
print("COMPARISON TO V2:")
print(f"  v2: 57/100 (43% major errors)")
print(f"  v3: {quality_score:.1f}/100 ({major_pct:.1f}% major errors)")
if quality_score > 57:
    improvement = quality_score - 57
    print(f"  IMPROVEMENT: +{improvement:.1f} points")
else:
    decline = 57 - quality_score
    print(f"  DECLINE: -{decline:.1f} points")

print("\n" + "="*80)
print("5. TOP ISSUES TO FIX")
print("="*80)

# Rank issues by frequency and impact
issue_ranking = []
for error_type, instances in error_categories.items():
    # Estimate impact on full dataset
    sample_rate = len(instances) / total_sampled if total_sampled > 0 else 0
    estimated_total = int(sample_rate * len(people))

    # Severity score
    severity = {
        'location_as_role': 10,  # Major
        'qualification_as_role': 10,  # Major
        'name_as_role': 10,  # Major
        'wrong_context': 8,  # Major
        'plural_role': 5,  # Minor
        'name_not_in_source': 10  # Major
    }.get(error_type, 5)

    impact_score = estimated_total * severity

    issue_ranking.append({
        'type': error_type,
        'sample_count': len(instances),
        'estimated_total': estimated_total,
        'severity': severity,
        'impact': impact_score,
        'examples': instances[:2]
    })

# Sort by impact
issue_ranking.sort(key=lambda x: x['impact'], reverse=True)

for i, issue in enumerate(issue_ranking[:3], 1):
    print(f"\n{i}. {issue['type'].upper().replace('_', ' ')}")
    print(f"   Found in sample: {issue['sample_count']}/{total_sampled}")
    print(f"   Estimated in full dataset: ~{issue['estimated_total']}/{len(people)}")
    print(f"   Impact score: {issue['impact']:.0f}")
    print(f"   Examples:")
    for ex in issue['examples']:
        print(f"     - {ex['name']}: '{ex['role']}' (line {ex['line']})")

print("\n" + "="*80)
print("REVIEW COMPLETE")
print("="*80)

# Export detailed results for markdown report
results = {
    'metadata': metadata,
    'total_people': len(people),
    'sample_size': total_sampled,
    'perfect': perfect_count,
    'minor_errors': minor_error_count,
    'major_errors': major_error_count,
    'quality_score': quality_score,
    'error_categories': {k: len(v) for k, v in error_categories.items()},
    'top_issues': issue_ranking[:3],
    'sample_records': [
        {
            'name': p['name'],
            'role': p['role'],
            'line': p['line_number'],
            'confidence': p['confidence'],
            'method': p['extraction_method']
        } for p in sample
    ]
}

with open('/home/user/colonial_office_list/ceylon_v3_review_results.json', 'w') as f:
    json.dump(results, f, indent=2)

print("\nResults saved to: ceylon_v3_review_results.json")
