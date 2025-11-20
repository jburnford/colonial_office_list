#!/usr/bin/env python3
"""
Verify that the Fiji fix correctly swapped name/role fields.
"""

import json
import os
import re

def read_line_from_source(year, line_number):
    """Read a specific line from the source file."""
    # Try different possible file locations
    possible_paths = [
        f'/home/user/colonial_office_list/output_3/{year}/fiji_{year}.txt',
        f'/home/user/colonial_office_list/output_3/{year}/fiji.txt',
        f'/home/user/colonial_office_list/output_3/{year}/FIJI.txt',
    ]

    for path in possible_paths:
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if 0 <= line_number - 1 < len(lines):
                    return lines[line_number - 1].strip()
    return None

def verify_samples(fixed_file, num_samples=10):
    """Verify fixed records against source files."""

    print("Loading fixed data...")
    with open(fixed_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    people = data['people']

    # Get sample of fixed records
    fixed_records = [p for p in people if p.get('extraction_method') == 'task_pattern_extraction_fixed']

    print(f"Total fixed records: {len(fixed_records)}")
    print(f"\nVerifying {num_samples} samples against source files...\n")
    print("="*100)

    verified_count = 0
    correct_count = 0

    for i, person in enumerate(fixed_records[:num_samples], 1):
        year = person.get('year')
        line_num = person.get('line_number')
        name = person.get('name')
        role = person.get('role')
        salary = person.get('salary')

        # Try to read source line
        source_line = read_line_from_source(year, line_num)

        print(f"\n{i}. Year {year}, Line {line_num}")
        print(f"   Extracted: name=\"{name}\", role=\"{role}\", salary=\"{salary}\"")

        if source_line:
            print(f"   Source:    \"{source_line}\"")
            verified_count += 1

            # Check if name appears in source
            name_in_source = name in source_line if name else False
            role_in_source = role in source_line if role else False

            # Simple heuristic: name should look like a person name (capitals, possibly initials)
            # role should look like a job title or department
            name_looks_correct = bool(re.search(r'[A-Z][a-z]+', name)) if name else False

            print(f"   Validation:")
            print(f"     - Name \"{name}\" in source: {'✅' if name_in_source else '❌'}")
            print(f"     - Role \"{role}\" in source: {'✅' if role_in_source else '❌'}")
            print(f"     - Name looks like person: {'✅' if name_looks_correct else '⚠️'}")

            if name_in_source and name_looks_correct:
                print(f"   Status: ✅ CORRECT")
                correct_count += 1
            else:
                print(f"   Status: ⚠️ NEEDS REVIEW")
        else:
            print(f"   Source:    [File not found]")
            print(f"   Status: ❓ CANNOT VERIFY")

    print("\n" + "="*100)
    print("VERIFICATION SUMMARY:")
    print("="*100)
    print(f"Samples checked: {num_samples}")
    print(f"Source files found: {verified_count}/{num_samples}")
    print(f"Corrections verified correct: {correct_count}/{verified_count if verified_count > 0 else num_samples}")

    if verified_count > 0:
        accuracy = 100 * correct_count / verified_count
        print(f"Verification accuracy: {accuracy:.1f}%")

    return correct_count, verified_count

def compare_before_after():
    """Compare original and fixed files to show the impact."""

    print("\n" + "="*100)
    print("BEFORE/AFTER COMPARISON:")
    print("="*100)

    # Load both files
    with open('/home/user/colonial_office_list/fiji_all_years_v2.json', 'r') as f:
        original_data = json.load(f)

    with open('/home/user/colonial_office_list/fiji_all_years_v3_fixed.json', 'r') as f:
        fixed_data = json.load(f)

    original_people = original_data['people']
    fixed_people = fixed_data['people']

    # Find some task_pattern_extraction records and compare
    count = 0
    for orig, fixed in zip(original_people, fixed_people):
        if orig.get('extraction_method') == 'task_pattern_extraction':
            if count < 5:  # Show first 5
                print(f"\nYear {orig['year']}, Line {orig.get('line_number')}")
                print(f"  BEFORE: name=\"{orig['name']}\", role=\"{orig['role']}\"")
                print(f"  AFTER:  name=\"{fixed['name']}\", role=\"{fixed['role']}\"")
                count += 1
            else:
                break

if __name__ == '__main__':
    compare_before_after()
    print()
    verify_samples('/home/user/colonial_office_list/fiji_all_years_v3_fixed.json', num_samples=10)
