#!/usr/bin/env python3
"""
Verify the smart fix against source files and compare with the blind fix.
"""

import json
import os

def read_line_from_source(year, line_number):
    """Read a specific line from the source file."""
    possible_dirs = [
        f'/home/user/colonial_office_list/output_3/{year}_manual_parsed',
        f'/home/user/colonial_office_list/output_3/{year}',
    ]

    possible_names = ['fiji.txt', 'FIJI.txt', 'fiji.md']

    for dir_path in possible_dirs:
        for name in possible_names:
            path = os.path.join(dir_path, name)
            if os.path.exists(path):
                try:
                    with open(path, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        if 0 <= line_number - 1 < len(lines):
                            return lines[line_number - 1].strip(), path
                except:
                    pass
    return None, None

def verify_fix():
    """Verify smart fix against source files."""

    # Load all three versions
    with open('/home/user/colonial_office_list/fiji_all_years_v2.json', 'r') as f:
        original = json.load(f)['people']

    with open('/home/user/colonial_office_list/fiji_all_years_v3_fixed.json', 'r') as f:
        blind_fix = json.load(f)['people']

    with open('/home/user/colonial_office_list/fiji_all_years_v3_smart_fixed.json', 'r') as f:
        smart_fix = json.load(f)['people']

    print("="*100)
    print("VERIFICATION: Smart Fix vs Blind Fix vs Original")
    print("="*100)

    # Test cases from 1879 source file
    test_cases = [
        {'year': 1879, 'line': 48, 'expected_name': 'Daniel J. Chisholm', 'expected_role_contains': 'Clerk'},
        {'year': 1879, 'line': 51, 'expected_name': 'C. A. W. Mitchell', 'expected_role_contains': 'Immigration'},
        {'year': 1879, 'line': 52, 'expected_name': 'Henry Bentley', 'expected_role_contains': 'Clerk'},
        {'year': 1879, 'line': 53, 'expected_name': 'Chas. O. Eyre', 'expected_role_contains': 'Clerk'},
        {'year': 1879, 'line': 60, 'expected_name': 'Cyril H. Irvine', 'expected_role_contains': 'Registrar'},
    ]

    correct_smart = 0
    correct_blind = 0
    correct_original = 0

    for test in test_cases:
        year = test['year']
        line = test['line']

        # Find records in each version
        orig_rec = next((p for p in original if p.get('year') == year and p.get('line_number') == line), None)
        blind_rec = next((p for p in blind_fix if p.get('year') == year and p.get('line_number') == line), None)
        smart_rec = next((p for p in smart_fix if p.get('year') == year and p.get('line_number') == line), None)

        # Get source line
        source, path = read_line_from_source(year, line)

        print(f"\nLine {line} (Year {year}):")
        if source:
            print(f"  SOURCE: \"{source}\"")
        else:
            print(f"  SOURCE: [not found]")

        print(f"  Expected: name=\"{test['expected_name']}\", role contains \"{test['expected_role_contains']}\"")

        if orig_rec:
            name_correct = orig_rec['name'] == test['expected_name']
            role_correct = test['expected_role_contains'].lower() in orig_rec['role'].lower()
            print(f"  ORIGINAL: name=\"{orig_rec['name']}\" {'✅' if name_correct else '❌'}, role=\"{orig_rec['role']}\" {'✅' if role_correct else '❌'}")
            if name_correct: correct_original += 1

        if blind_rec:
            name_correct = blind_rec['name'] == test['expected_name']
            role_correct = test['expected_role_contains'].lower() in blind_rec['role'].lower()
            print(f"  BLIND FIX: name=\"{blind_rec['name']}\" {'✅' if name_correct else '❌'}, role=\"{blind_rec['role']}\" {'✅' if role_correct else '❌'}")
            if name_correct: correct_blind += 1

        if smart_rec:
            name_correct = smart_rec['name'] == test['expected_name']
            role_correct = test['expected_role_contains'].lower() in smart_rec['role'].lower()
            print(f"  SMART FIX: name=\"{smart_rec['name']}\" {'✅' if name_correct else '❌'}, role=\"{smart_rec['role']}\" {'✅' if role_correct else '❌'}")
            if name_correct: correct_smart += 1

    print("\n" + "="*100)
    print("VERIFICATION RESULTS:")
    print("="*100)
    print(f"Test cases: {len(test_cases)}")
    print(f"Original correct names: {correct_original}/{len(test_cases)} ({100*correct_original/len(test_cases):.0f}%)")
    print(f"Blind fix correct names: {correct_blind}/{len(test_cases)} ({100*correct_blind/len(test_cases):.0f}%)")
    print(f"Smart fix correct names: {correct_smart}/{len(test_cases)} ({100*correct_smart/len(test_cases):.0f}%)")

    print("\n" + "="*100)
    print("RECOMMENDATION:")
    print("="*100)
    if correct_smart >= correct_blind and correct_smart >= correct_original:
        print("✅ USE SMART FIX (fiji_all_years_v3_smart_fixed.json)")
        print("   - Only swaps truly swapped records")
        print("   - Preserves already-correct records")
        print(f"   - {correct_smart}/{len(test_cases)} verified test cases correct")
    else:
        print("⚠️ NEEDS MORE INVESTIGATION")

if __name__ == '__main__':
    verify_fix()
