#!/usr/bin/env python3
"""
Verify sampled Kenya records against source files
"""

import json
import re
from pathlib import Path

# Load samples
with open('/home/user/colonial_office_list/kenya_sample_25.json', 'r') as f:
    samples = json.load(f)

print("="*80)
print("KENYA EXTRACTION QUALITY VERIFICATION")
print("="*80)
print()

# Track quality metrics
total_records = len(samples)
perfect_extractions = 0
name_errors = 0
role_errors = 0
location_errors = 0
confidence_issues = []

# Categories of errors
non_person_names = []
contaminated_names = []  # Names with extra info (department, role, etc.)
multiple_people = []      # Multiple people in one record
wrong_roles = []
wrong_locations = []
role_context_issues = []

print(f"Analyzing {total_records} sampled records...")
print()

for i, sample in enumerate(samples, 1):
    print(f"\n{'='*80}")
    print(f"RECORD {i}/{total_records}")
    print(f"{'='*80}")

    year = sample['year']
    name = sample['name']
    role = sample.get('role', 'N/A')
    location = sample.get('location', 'N/A')
    department = sample.get('department', 'N/A')
    confidence = sample.get('confidence', 0)
    full_string = sample.get('full_string', '')

    print(f"Year: {year}")
    print(f"Extracted Name: {name}")
    print(f"Extracted Role: {role}")
    print(f"Extracted Location/Dept: {location}")
    print(f"Confidence: {confidence}")
    print(f"Full String: {full_string[:150]}...")
    print()

    # Analyze for errors
    has_error = False
    errors_found = []

    # Check 1: Is this actually a person's name?
    # Red flags: starts with lowercase, contains phrases, academic degrees as name
    if name.startswith(('most ', 'The ', 'Grade ', 'Members ', 'Permanent ')):
        errors_found.append("❌ NOT A PERSON - descriptive text")
        non_person_names.append(sample)
        has_error = True
    elif name == "B.A. (1st class Hons.) (Lond.)":
        errors_found.append("❌ NOT A PERSON - this is a qualification, not a name")
        non_person_names.append(sample)
        has_error = True
    elif "K.C.M.G.) |" in name:
        errors_found.append("❌ NOT A PERSON - table fragment")
        non_person_names.append(sample)
        has_error = True

    # Check 2: Does name contain department/location/role prefix?
    if "—" in name or " Department" in name or " School" in name or " District" in name:
        errors_found.append("❌ CONTAMINATED NAME - contains department/location/role prefix")
        contaminated_names.append(sample)
        has_error = True

    # Check 3: Multiple people in one record?
    if ";" in name and len(name.split(";")) > 1:
        count = len(name.split(";"))
        errors_found.append(f"❌ MULTIPLE PEOPLE - {count} people in one record")
        multiple_people.append(sample)
        has_error = True

    # Check 4: Role context inheritance issue
    # The role doesn't match what we see in full_string
    if role and full_string:
        # Extract actual role from full_string
        if full_string.startswith(role):
            # Good - role is at start
            pass
        elif "," in full_string:
            actual_role = full_string.split(",")[0]
            if role != actual_role and role not in actual_role:
                errors_found.append(f"⚠️  ROLE CONTEXT ISSUE - role '{role}' doesn't match context in source")
                role_context_issues.append(sample)

    # Check 5: Confidence accuracy
    # High confidence (0.9) but has obvious errors
    if confidence >= 0.9 and has_error:
        errors_found.append(f"⚠️  CONFIDENCE MISMATCH - confidence {confidence} too high for quality")
        confidence_issues.append({
            'sample': sample,
            'reason': 'High confidence with clear errors'
        })

    # Print analysis
    if errors_found:
        print("ISSUES FOUND:")
        for error in errors_found:
            print(f"  {error}")
        name_errors += 1
    else:
        # Try to determine if it's a good extraction
        # Good extraction criteria:
        # - Name looks like "FirstInit. MiddleInit. Lastname" or "Full Name"
        # - No prefixes or suffixes
        # - Single person
        name_pattern = r'^[A-Z]\. ?([A-Z]\. ?)*[A-Z][a-z]+|^[A-Z][a-z]+ [A-Z]\. [A-Z][a-z]+'
        if re.match(name_pattern, name):
            print("✓ APPEARS CORRECT - name format is standard")
            perfect_extractions += 1
        else:
            print("? UNCERTAIN - needs manual verification")

    print()

# Summary report
print("\n" + "="*80)
print("QUALITY EVALUATION SUMMARY")
print("="*80)
print()

print(f"Total Records Evaluated: {total_records}")
print(f"Perfect Extractions: {perfect_extractions} ({perfect_extractions/total_records*100:.1f}%)")
print(f"Records with Name Errors: {name_errors} ({name_errors/total_records*100:.1f}%)")
print()

print("ERROR BREAKDOWN:")
print(f"  Non-Person Names (not people at all): {len(non_person_names)}")
print(f"  Contaminated Names (dept/location in name): {len(contaminated_names)}")
print(f"  Multiple People in One Record: {len(multiple_people)}")
print(f"  Role Context Issues: {len(role_context_issues)}")
print(f"  Confidence Mismatches: {len(confidence_issues)}")
print()

# Calculate quality score
# Scoring:
# - Perfect extraction: 100 points
# - Non-person name: 0 points (critical failure)
# - Contaminated name: 40 points (recoverable but needs cleanup)
# - Multiple people: 30 points (needs splitting)
# - Role context issue: 70 points (mostly correct)

score_sum = 0
for sample in samples:
    record_score = 100  # Start with perfect

    if sample in non_person_names:
        record_score = 0
    elif sample in multiple_people:
        record_score = 30
    elif sample in contaminated_names:
        record_score = 40
    elif sample in role_context_issues:
        record_score = 70

    score_sum += record_score

overall_quality = score_sum / total_records
print(f"OVERALL QUALITY SCORE: {overall_quality:.1f}/100")
print()

# Detailed examples
if non_person_names:
    print("\nEXAMPLES OF NON-PERSON NAMES:")
    for ex in non_person_names[:5]:
        print(f"  - '{ex['name']}' (Year: {ex['year']})")
        print(f"    Full: {ex['full_string'][:100]}...")

if contaminated_names:
    print("\nEXAMPLES OF CONTAMINATED NAMES:")
    for ex in contaminated_names[:5]:
        print(f"  - '{ex['name']}' (Year: {ex['year']})")
        print(f"    Should be: {ex['name'].split('—')[-1] if '—' in ex['name'] else 'unclear'}")

if multiple_people:
    print("\nEXAMPLES OF MULTIPLE PEOPLE RECORDS:")
    for ex in multiple_people[:3]:
        print(f"  - '{ex['name'][:80]}...' (Year: {ex['year']})")
        print(f"    Contains {len(ex['name'].split(';'))} people")

print("\n" + "="*80)
