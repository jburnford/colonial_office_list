#!/usr/bin/env python3
"""
Canada Phase 1 Quality Analysis Script
Analyzes extraction quality for federal departments only
"""

import json
import random
from collections import Counter, defaultdict

# Load extraction files
with open('canada_1867_test.json', 'r') as f:
    data_1867 = json.load(f)

with open('canada_1890_test.json', 'r') as f:
    data_1890 = json.load(f)

print("=" * 80)
print("CANADA PHASE 1 EXTRACTION - QUALITY ANALYSIS")
print("=" * 80)
print()

# 1. OVERALL STATISTICS
print("1. OVERALL STATISTICS")
print("-" * 80)
print(f"\n1867 Extraction:")
print(f"  Total records: {len(data_1867['people'])}")
print(f"  Average confidence: {data_1867['metadata']['phases']['validation']['avg_confidence']:.3f}")
print(f"  Multi-role entries: {data_1867['metadata']['canada_specific']['multi_role_entries']}")
print(f"  Acting officials: {data_1867['metadata']['canada_specific']['acting_officials']}")
print(f"  Skip sections detected: {data_1867['metadata']['canada_specific']['skip_sections_detected']}")
print(f"  Currency: {data_1867['metadata']['canada_specific']['currency']}")

print(f"\n1890 Extraction:")
print(f"  Total records: {len(data_1890['people'])}")
print(f"  Average confidence: {data_1890['metadata']['phases']['validation']['avg_confidence']:.3f}")
print(f"  Multi-role entries: {data_1890['metadata']['canada_specific']['multi_role_entries']}")
print(f"  Acting officials: {data_1890['metadata']['canada_specific']['acting_officials']}")
print(f"  Skip sections detected: {data_1890['metadata']['canada_specific']['skip_sections_detected']}")
print(f"  Currency: {data_1890['metadata']['canada_specific']['currency']}")

# 2. CONFIDENCE DISTRIBUTION
print("\n\n2. CONFIDENCE DISTRIBUTION")
print("-" * 80)

def analyze_confidence(people, year):
    confidences = [p['confidence'] for p in people]
    bins = {
        '0.90-1.00': 0,
        '0.85-0.89': 0,
        '0.70-0.84': 0,
        '< 0.70': 0
    }
    for c in confidences:
        if c >= 0.90:
            bins['0.90-1.00'] += 1
        elif c >= 0.85:
            bins['0.85-0.89'] += 1
        elif c >= 0.70:
            bins['0.70-0.84'] += 1
        else:
            bins['< 0.70'] += 1

    print(f"\n{year}:")
    total = len(confidences)
    for range_label, count in bins.items():
        pct = (count / total * 100) if total > 0 else 0
        print(f"  {range_label}: {count:3d} ({pct:5.1f}%)")

analyze_confidence(data_1867['people'], '1867')
analyze_confidence(data_1890['people'], '1890')

# 3. ROLE ANALYSIS
print("\n\n3. UNKNOWN ROLES ANALYSIS")
print("-" * 80)

def count_unknown_roles(people, year):
    unknown_patterns = ['unknown', 'ditto', 'West', 'East', 'Section']
    unknown = [p for p in people if any(pattern.lower() in p['role'].lower() for pattern in unknown_patterns)]
    print(f"\n{year}:")
    print(f"  Unknown/unclear roles: {len(unknown)} ({len(unknown)/len(people)*100:.1f}%)")
    if len(unknown) > 0:
        print(f"  Examples:")
        for p in unknown[:5]:
            print(f"    - {p['name']}: {p['role']} (line {p['line_number']})")

count_unknown_roles(data_1867['people'], '1867')
count_unknown_roles(data_1890['people'], '1890')

# 4. DEPARTMENT DISTRIBUTION
print("\n\n4. DEPARTMENT DISTRIBUTION")
print("-" * 80)

def analyze_departments(people, year):
    dept_counts = Counter(p['department'] for p in people)
    print(f"\n{year}:")
    for dept, count in dept_counts.most_common():
        print(f"  {dept}: {count}")

analyze_departments(data_1867['people'], '1867')
analyze_departments(data_1890['people'], '1890')

# 5. PROVINCE DISTRIBUTION
print("\n\n5. PROVINCE/FEDERAL DISTRIBUTION")
print("-" * 80)

def analyze_provinces(people, year):
    province_counts = Counter(p['province'] if p['province'] else 'Federal' for p in people)
    print(f"\n{year}:")
    for prov, count in sorted(province_counts.items()):
        print(f"  {prov}: {count}")

analyze_provinces(data_1867['people'], '1867')
analyze_provinces(data_1890['people'], '1890')

# 6. EXTRACTION METHOD BREAKDOWN
print("\n\n6. EXTRACTION METHOD BREAKDOWN")
print("-" * 80)

def analyze_methods(people, year):
    method_counts = Counter(p['extraction_method'] for p in people)
    print(f"\n{year}:")
    for method, count in method_counts.most_common():
        print(f"  {method}: {count}")

analyze_methods(data_1867['people'], '1867')
analyze_methods(data_1890['people'], '1890')

# 7. MULTI-ROLE ANALYSIS
print("\n\n7. MULTI-ROLE OFFICIALS ANALYSIS")
print("-" * 80)

def analyze_multi_role(people, year):
    multi_role = [p for p in people if p['multi_role_id']]
    multi_role_groups = defaultdict(list)
    for p in multi_role:
        multi_role_groups[p['multi_role_id']].append(p)

    print(f"\n{year}:")
    print(f"  Multi-role groups: {len(multi_role_groups)}")
    print(f"  Total multi-role records: {len(multi_role)}")
    print(f"\n  Examples:")
    for group_id in list(multi_role_groups.keys())[:3]:
        group = multi_role_groups[group_id]
        print(f"\n    Group {group_id}:")
        print(f"      Name: {group[0]['name']}")
        print(f"      Roles: {', '.join([p['role'] for p in group])}")
        print(f"      Line: {group[0]['line_number']}")

analyze_multi_role(data_1867['people'], '1867')
analyze_multi_role(data_1890['people'], '1890')

# 8. TITLE EXTRACTION ANALYSIS
print("\n\n8. TITLE EXTRACTION ANALYSIS")
print("-" * 80)

def analyze_titles(people, year):
    with_titles = [p for p in people if p.get('notes') and 'Titles:' in p['notes']]
    print(f"\n{year}:")
    print(f"  Records with titles extracted: {len(with_titles)}")
    if len(with_titles) > 0:
        print(f"  Examples:")
        for p in with_titles[:5]:
            print(f"    - {p['name']}: {p['notes']} (line {p['line_number']})")

analyze_titles(data_1867['people'], '1867')
analyze_titles(data_1890['people'], '1890')

# 9. SAMPLE RANDOM RECORDS FOR VERIFICATION
print("\n\n9. RANDOM SAMPLE FOR VERIFICATION (10 from each year)")
print("-" * 80)

# Sample strategy: diverse coverage
def get_diverse_sample(people, n=10):
    """Get a diverse sample including different extraction types"""
    sample = []

    # Get multi-role examples
    multi_role = [p for p in people if p['multi_role_id']]
    if multi_role:
        sample.extend(random.sample(multi_role, min(2, len(multi_role))))

    # Get acting officials
    acting = [p for p in people if p['is_acting']]
    if acting:
        sample.extend(random.sample(acting, min(1, len(acting))))

    # Get people with titles
    with_titles = [p for p in people if p.get('notes') and 'Titles:' in p['notes']]
    if with_titles:
        sample.extend(random.sample(with_titles, min(2, len(with_titles))))

    # Get federal officials
    federal = [p for p in people if not p['province'] and p not in sample]
    if federal:
        sample.extend(random.sample(federal, min(3, len(federal))))

    # Get provincial officials
    provincial = [p for p in people if p['province'] and p not in sample]
    if provincial:
        sample.extend(random.sample(provincial, min(2, len(provincial))))

    # Fill remaining with random
    remaining = [p for p in people if p not in sample]
    if len(sample) < n and remaining:
        sample.extend(random.sample(remaining, min(n - len(sample), len(remaining))))

    return sample[:n]

print("\n1867 Sample:")
sample_1867 = get_diverse_sample(data_1867['people'], 10)
for i, p in enumerate(sample_1867, 1):
    print(f"\n  {i}. {p['name']} - {p['role']}")
    print(f"     Department: {p['department']}, Province: {p['province']}")
    print(f"     Salary: {p['salary']}, Line: {p['line_number']}")
    print(f"     Confidence: {p['confidence']}, Method: {p['extraction_method']}")
    if p.get('notes'):
        print(f"     Notes: {p['notes']}")
    print(f"     Full string: {p['full_string']}")

print("\n\n1890 Sample:")
sample_1890 = get_diverse_sample(data_1890['people'], 10)
for i, p in enumerate(sample_1890, 1):
    print(f"\n  {i}. {p['name']} - {p['role']}")
    print(f"     Department: {p['department']}, Province: {p['province']}")
    print(f"     Salary: {p['salary']}, Line: {p['line_number']}")
    print(f"     Confidence: {p['confidence']}, Method: {p['extraction_method']}")
    if p.get('notes'):
        print(f"     Notes: {p['notes']}")
    print(f"     Full string: {p['full_string']}")

# Save sample line numbers for manual verification
print("\n\n10. LINE NUMBERS FOR MANUAL VERIFICATION")
print("-" * 80)
print("\n1867 lines to check:")
print(", ".join(str(p['line_number']) for p in sample_1867))

print("\n1890 lines to check:")
print(", ".join(str(p['line_number']) for p in sample_1890))

print("\n" + "=" * 80)
print("Analysis complete!")
print("=" * 80)
