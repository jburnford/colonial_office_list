#!/usr/bin/env python3
"""
Independent evaluation of Canada extraction quality.
"""

import json
import random
import re
from pathlib import Path
from typing import List, Dict, Tuple

def load_extraction_data(json_path: str) -> Dict:
    """Load the extraction JSON file."""
    print(f"Loading {json_path}...")
    with open(json_path, 'r') as f:
        data = json.load(f)
    print(f"Loaded {data['metadata']['total_people']} people from {data['metadata']['total_files']} files")
    return data

def sample_records(data: Dict, sample_size: int = 25) -> List[Dict]:
    """
    Sample records for evaluation with specific criteria:
    - Mix of years (early £ period, later $ period)
    - Include multi-role entries (CRITICAL for bug check)
    - Mix of departments
    """
    people = data['people']

    # Separate into categories
    early_period = [p for p in people if p['year'] <= 1880]  # £ currency
    later_period = [p for p in people if p['year'] >= 1890]  # $ currency
    multi_role = [p for p in people if p.get('multi_role_id')]

    print(f"\nSampling strategy:")
    print(f"  Early period (£): {len(early_period)} records available")
    print(f"  Later period ($): {len(later_period)} records available")
    print(f"  Multi-role entries: {len(multi_role)} records available")

    # Sample composition:
    # - 8 early period
    # - 8 later period
    # - 9 multi-role (CRITICAL - checking for name truncation bug)

    sample = []

    # Early period
    if early_period:
        sample.extend(random.sample(early_period, min(8, len(early_period))))

    # Later period
    if later_period:
        sample.extend(random.sample(later_period, min(8, len(later_period))))

    # Multi-role (CRITICAL)
    if multi_role:
        # Sample multi-role entries from different years
        multi_role_sample = random.sample(multi_role, min(9, len(multi_role)))
        sample.extend(multi_role_sample)

    # Shuffle to mix them up
    random.shuffle(sample)

    return sample[:sample_size]

def find_source_file(person: Dict) -> str:
    """Find the source file for a person record."""
    year = person['year']

    # Try different patterns
    patterns = [
        f"output_3/*{year}*/canada.txt",
        f"output_3/*{year}*/CANADA.txt",
        f"output_3/*{year}*/dominion_of_canada.txt",
        f"output_3/*{year}*/DOMINION_OF_CANADA.txt",
        f"output_3/*{year}*/DOMINION_OF_CANADA.md",
    ]

    import glob
    for pattern in patterns:
        files = glob.glob(pattern)
        if files:
            return files[0]

    return None

def verify_record(person: Dict, source_file: str) -> Dict:
    """
    Verify a single record against source file.

    Returns verification result with status:
    - "PERFECT": All fields match exactly
    - "MINOR_ERROR": Small discrepancies (titles, punctuation)
    - "MAJOR_ERROR": Name truncation, wrong person, missing data
    - "NOT_FOUND": Line doesn't exist or no match
    """
    result = {
        'person': person,
        'status': 'UNKNOWN',
        'issues': [],
        'source_line': None,
        'verification_notes': []
    }

    try:
        with open(source_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        line_num = person['line_number'] - 1  # Convert to 0-based

        if line_num < 0 or line_num >= len(lines):
            result['status'] = 'NOT_FOUND'
            result['issues'].append(f"Line {person['line_number']} out of range (file has {len(lines)} lines)")
            return result

        source_line = lines[line_num].strip()
        result['source_line'] = source_line

        # Check if name appears in line
        name = person['name']

        # CRITICAL: Check for name truncation bug
        if len(name) <= 3 and person.get('multi_role_id'):
            result['status'] = 'MAJOR_ERROR'
            result['issues'].append(f"NAME TRUNCATION BUG: Name is only '{name}' (multi-role entry)")
            return result

        # Check if name appears in line (case-insensitive, flexible)
        name_parts = name.split()
        name_found = False

        # Try full name
        if name.lower() in source_line.lower():
            name_found = True
            result['verification_notes'].append("Full name found in source")
        # Try last name
        elif len(name_parts) >= 2 and name_parts[-1].lower() in source_line.lower():
            name_found = True
            result['verification_notes'].append("Last name found in source")
        # Try initials + last name pattern
        elif len(name_parts) >= 2:
            # Look for patterns like "J. A. Macdonald" or "Sir J. A. Macdonald"
            last_name = name_parts[-1]
            if last_name.lower() in source_line.lower():
                name_found = True
                result['verification_notes'].append("Last name found (may have different initials)")

        if not name_found:
            result['status'] = 'MAJOR_ERROR'
            result['issues'].append(f"Name '{name}' not found in source line")
            return result

        # Check if role appears (flexible matching)
        role = person['role'].lower()
        role_words = role.split()
        role_found = any(word in source_line.lower() for word in role_words if len(word) > 3)

        if not role_found:
            result['issues'].append(f"Role '{person['role']}' not clearly visible in source")

        # Check if salary appears (if present)
        if person.get('salary'):
            salary = person['salary'].replace(',', '').replace('$', '').replace('£', '').replace('l', '').replace('.', '').strip()
            if salary and salary not in source_line.replace(',', '').replace('$', '').replace('£', '').replace('l', '').replace('.', ''):
                result['issues'].append(f"Salary '{person['salary']}' not found in source")

        # Determine status
        if not result['issues']:
            result['status'] = 'PERFECT'
        elif len(result['issues']) == 1 and 'not clearly visible' in result['issues'][0]:
            result['status'] = 'MINOR_ERROR'
        else:
            result['status'] = 'MAJOR_ERROR' if any('not found' in i.lower() for i in result['issues']) else 'MINOR_ERROR'

        # Check currency correctness
        year = person['year']
        if year <= 1869 and person.get('salary'):
            if '£' in person['salary'] or 'l' in person['salary']:
                result['verification_notes'].append("Currency: £ (correct for early period)")
            else:
                result['issues'].append("Currency: Expected £ for pre-1870")
        elif year >= 1890 and person.get('salary'):
            if '$' in person['salary']:
                result['verification_notes'].append("Currency: $ (correct for later period)")
            else:
                result['issues'].append("Currency: Expected $ for post-1890")

    except Exception as e:
        result['status'] = 'ERROR'
        result['issues'].append(f"Verification error: {e}")

    return result

def calculate_quality_score(results: List[Dict]) -> Dict:
    """Calculate quality score from verification results."""
    total = len(results)
    perfect = sum(1 for r in results if r['status'] == 'PERFECT')
    minor = sum(1 for r in results if r['status'] == 'MINOR_ERROR')
    major = sum(1 for r in results if r['status'] == 'MAJOR_ERROR')
    not_found = sum(1 for r in results if r['status'] == 'NOT_FOUND')

    # Calculate score (similar to other evaluations)
    # Perfect = 100%, Minor = 90%, Major = 50%, Not found = 0%
    score = (perfect * 100 + minor * 90 + major * 50 + not_found * 0) / total if total > 0 else 0

    return {
        'total_checked': total,
        'perfect': perfect,
        'minor_errors': minor,
        'major_errors': major,
        'not_found': not_found,
        'score': round(score, 1),
        'percent_perfect': round(perfect / total * 100, 1) if total > 0 else 0,
        'percent_minor': round(minor / total * 100, 1) if total > 0 else 0,
        'percent_major': round(major / total * 100, 1) if total > 0 else 0,
        'percent_not_found': round(not_found / total * 100, 1) if total > 0 else 0
    }

def check_name_truncation_bug(results: List[Dict]) -> Dict:
    """
    CRITICAL: Check if name truncation bug is fixed.

    Look for multi-role entries with truncated names.
    """
    multi_role_results = [r for r in results if r['person'].get('multi_role_id')]

    truncated = []
    for r in multi_role_results:
        name = r['person']['name']
        if len(name) <= 3:  # Truncated to 2-3 characters
            truncated.append({
                'name': name,
                'role': r['person']['role'],
                'line': r['person']['line_number'],
                'source_line': r['source_line']
            })

    return {
        'total_multi_role_checked': len(multi_role_results),
        'truncated_names_found': len(truncated),
        'bug_fixed': len(truncated) == 0,
        'examples': truncated[:5]  # Show up to 5 examples
    }

def main():
    """Main evaluation."""
    random.seed(42)  # For reproducibility

    # Load extraction data
    data = load_extraction_data('/home/user/colonial_office_list/canada_all_years_v2_fixed.json')

    # Sample records
    print(f"\nSampling {25} records for evaluation...")
    sample = sample_records(data, 25)

    # Verify each record
    print(f"\nVerifying {len(sample)} records against source files...")
    results = []

    for i, person in enumerate(sample):
        print(f"  [{i+1}/{len(sample)}] Verifying {person['name']} ({person['year']})...", end=' ')

        source_file = find_source_file(person)
        if not source_file:
            print(f"SOURCE NOT FOUND")
            results.append({
                'person': person,
                'status': 'NOT_FOUND',
                'issues': ['Source file not found'],
                'source_line': None,
                'verification_notes': []
            })
            continue

        result = verify_record(person, source_file)
        results.append(result)
        print(result['status'])

    # Calculate quality score
    quality = calculate_quality_score(results)

    # Check name truncation bug
    bug_check = check_name_truncation_bug(results)

    # Print summary
    print(f"\n{'='*70}")
    print("CANADA EXTRACTION QUALITY EVALUATION")
    print('='*70)
    print(f"\nSample Size: {quality['total_checked']} records")
    print(f"Perfect: {quality['perfect']} ({quality['percent_perfect']}%)")
    print(f"Minor Errors: {quality['minor_errors']} ({quality['percent_minor']}%)")
    print(f"Major Errors: {quality['major_errors']} ({quality['percent_major']}%)")
    print(f"Not Found: {quality['not_found']} ({quality['percent_not_found']}%)")
    print(f"\n{'='*70}")
    print(f"QUALITY SCORE: {quality['score']}/100")
    print('='*70)

    print(f"\n{'='*70}")
    print("NAME TRUNCATION BUG CHECK (CRITICAL)")
    print('='*70)
    print(f"Multi-role entries checked: {bug_check['total_multi_role_checked']}")
    print(f"Truncated names found: {bug_check['truncated_names_found']}")
    print(f"Bug fixed: {'YES' if bug_check['bug_fixed'] else 'NO'}")

    if bug_check['examples']:
        print("\nExamples of truncated names:")
        for ex in bug_check['examples']:
            print(f"  - '{ex['name']}' ({ex['role']}) at line {ex['line']}")

    # Save detailed results
    output = {
        'summary': {
            'evaluation_date': '2025-11-20',
            'sample_size': quality['total_checked'],
            'quality_score': quality['score'],
            'claimed_score': 95,
            'accurate_claim': abs(quality['score'] - 95) <= 5
        },
        'quality_breakdown': quality,
        'bug_check': bug_check,
        'detailed_results': results
    }

    with open('/home/user/colonial_office_list/canada_evaluation_results.json', 'w') as f:
        json.dump(output, f, indent=2)

    print(f"\nDetailed results saved to canada_evaluation_results.json")

    return results, quality, bug_check

if __name__ == '__main__':
    main()
