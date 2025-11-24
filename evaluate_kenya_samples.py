#!/usr/bin/env python3
import json
import re
from pathlib import Path

# Load samples
with open('/home/user/colonial_office_list/kenya_evaluation_samples.json', 'r') as f:
    samples = json.load(f)

# Evaluation categories
evaluations = []

# Mapping years to source files
year_to_file = {}
output_dirs = Path('/home/user/colonial_office_list/output_3').glob('*_manual_parsed')
for output_dir in output_dirs:
    kenya_files = list(output_dir.glob('kenya*.txt')) + list(output_dir.glob('KENYA*.txt'))
    for kenya_file in kenya_files:
        # Extract year from directory name
        year_match = re.search(r'(\d{4})', output_dir.name)
        if year_match:
            year = int(year_match.group(1))
            year_to_file[year] = str(kenya_file)

print(f"Found source files for {len(year_to_file)} years")
print(f"Evaluating {len(samples)} samples...\n")

for idx, sample in enumerate(samples, 1):
    person = sample['person']
    year = person['year']
    name = person['name']
    role = person['role']
    line_num = person['line_number']
    full_string = person['full_string']

    eval_result = {
        'sample_num': idx,
        'index': sample['index'],
        'year': year,
        'name': name,
        'role': role,
        'line_number': line_num,
        'full_string': full_string[:100] + '...' if len(full_string) > 100 else full_string,
        'issues': [],
        'severity': 'none',  # none, minor, major, critical
        'is_perfect': True
    }

    # Check 1: Name contamination (prefix with — or similar)
    if '—' in name or '–' in name:
        eval_result['issues'].append(f"Name contamination: Contains em-dash/en-dash separator")
        eval_result['severity'] = 'critical'
        eval_result['is_perfect'] = False

    # Check 2: Check if name looks like a non-person
    non_person_patterns = [
        r'^(B\.A\.|M\.A\.|Ph\.D\.|M\.B\.|Dr\.|Prof\.)',  # Qualifications
        r'(Province|District|Department|Office|Commission|Service|System|Ministry)$',  # Departments/Places
        r'^(St\.|Saint) [A-Z]',  # Places like St. Kitts
        r'^(The |A |An )',  # Descriptive text
        r'(Table|Grade|Class|Division)$',  # Table data
    ]

    for pattern in non_person_patterns:
        if re.search(pattern, name):
            eval_result['issues'].append(f"Non-person: Matches pattern '{pattern}'")
            eval_result['severity'] = 'critical'
            eval_result['is_perfect'] = False
            break

    # Check 3: Name should not contain common prefixes
    prefix_patterns = [
        r'^[A-Za-z\s]+(Technical School|College|Hospital|Office|Department)',
        r'^(Common Services|Civil Service|Game and Fisheries)',
        r'^(Masai|Ukamba|Nairobi|Mombasa)—',
    ]

    for pattern in prefix_patterns:
        if re.search(pattern, name):
            eval_result['issues'].append(f"Location/Department prefix: Matches '{pattern}'")
            eval_result['severity'] = 'critical'
            eval_result['is_perfect'] = False
            break

    # Check 4: Verify source file exists and read context
    if year in year_to_file:
        source_file = year_to_file[year]
        try:
            with open(source_file, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if 0 < line_num <= len(lines):
                    source_line = lines[line_num - 1].strip()
                    eval_result['source_line'] = source_line[:150] + '...' if len(source_line) > 150 else source_line

                    # Check if the name appears in source without prefix
                    clean_name = re.sub(r'^.*[—–]\s*', '', name)  # Remove prefix
                    if clean_name != name:
                        eval_result['issues'].append(f"Suggested clean name: '{clean_name}'")

                else:
                    eval_result['issues'].append(f"Line number {line_num} out of range (file has {len(lines)} lines)")
                    eval_result['severity'] = 'major'
                    eval_result['is_perfect'] = False
        except Exception as e:
            eval_result['issues'].append(f"Error reading source: {str(e)}")
            eval_result['severity'] = 'major'
            eval_result['is_perfect'] = False
    else:
        eval_result['issues'].append(f"No source file found for year {year}")
        eval_result['severity'] = 'major'
        eval_result['is_perfect'] = False

    evaluations.append(eval_result)

# Calculate statistics
total_samples = len(evaluations)
perfect_count = sum(1 for e in evaluations if e['is_perfect'])
critical_issues = sum(1 for e in evaluations if e['severity'] == 'critical')
major_issues = sum(1 for e in evaluations if e['severity'] == 'major')
minor_issues = sum(1 for e in evaluations if e['severity'] == 'minor')

name_contamination_count = sum(1 for e in evaluations if any('contamination' in i.lower() or 'prefix' in i.lower() for i in e['issues']))
non_person_count = sum(1 for e in evaluations if any('non-person' in i.lower() for i in e['issues']))

print("=" * 80)
print("KENYA EXTRACTION V2 - EVALUATION RESULTS")
print("=" * 80)
print(f"\nTotal samples evaluated: {total_samples}")
print(f"Perfect extractions: {perfect_count} ({perfect_count/total_samples*100:.1f}%)")
print(f"\nIssues by severity:")
print(f"  Critical: {critical_issues} ({critical_issues/total_samples*100:.1f}%)")
print(f"  Major: {major_issues} ({major_issues/total_samples*100:.1f}%)")
print(f"  Minor: {minor_issues} ({minor_issues/total_samples*100:.1f}%)")
print(f"\nSpecific problem types:")
print(f"  Name contamination: {name_contamination_count} ({name_contamination_count/total_samples*100:.1f}%)")
print(f"  Non-person extraction: {non_person_count} ({non_person_count/total_samples*100:.1f}%)")

print("\n" + "=" * 80)
print("DETAILED RESULTS")
print("=" * 80)

for eval_result in evaluations:
    print(f"\n[Sample {eval_result['sample_num']}] Year {eval_result['year']} - Index {eval_result['index']}")
    print(f"Name: {eval_result['name']}")
    print(f"Role: {eval_result['role']}")
    if eval_result['is_perfect']:
        print("✓ PERFECT")
    else:
        print(f"✗ ISSUES ({eval_result['severity'].upper()}):")
        for issue in eval_result['issues']:
            print(f"  - {issue}")
    if 'source_line' in eval_result:
        print(f"Source: {eval_result['source_line']}")

# Save detailed results
with open('/home/user/colonial_office_list/kenya_v2_evaluation_results.json', 'w') as f:
    json.dump({
        'metadata': {
            'total_samples': total_samples,
            'perfect_rate': perfect_count/total_samples,
            'critical_issues': critical_issues,
            'major_issues': major_issues,
            'minor_issues': minor_issues,
            'name_contamination_rate': name_contamination_count/total_samples,
            'non_person_rate': non_person_count/total_samples,
        },
        'evaluations': evaluations
    }, f, indent=2)

print("\n\nDetailed results saved to: kenya_v2_evaluation_results.json")
