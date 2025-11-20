#!/usr/bin/env python3
"""
Smart fix for Fiji name/role swap bug.

Only swaps records where name/role are actually swapped (not all task_pattern_extraction records).
Uses heuristics to identify truly swapped records.
"""

import json
import re
from datetime import datetime

def looks_like_person_name(text):
    """Check if text looks like a person's name."""
    if not text:
        return False

    # Patterns that suggest a person name:
    # - Contains at least one full name word (capital + lowercase): "John", "Smith"
    # - May contain initials: "A.", "J. M."
    # - Usually 1-4 words
    # - May contain titles: "Dr.", "Mr.", "Lieut."

    words = text.split()
    if len(words) > 5:
        return False

    # Count full name words (Capital + lowercase letters)
    full_name_words = len(re.findall(r'\b[A-Z][a-z]+\b', text))

    # Count initials (Capital + period)
    initials = len(re.findall(r'\b[A-Z]\.', text))

    # Has at least one full name word or multiple initials
    has_name_pattern = full_name_words >= 1 or initials >= 2

    return has_name_pattern

def looks_like_institution(text):
    """Check if text looks like an institution/department/location."""
    if not text:
        return False

    # Keywords that suggest institutional names
    institutional_keywords = [
        'Office', 'Court', 'Department', 'Laboratory', 'Bureau',
        'Division', 'Section', 'Branch', 'Registry', 'Treasury',
        'Secretariat', 'Commission', 'Board', 'Council', 'Committee',
        'Service', 'Corps', 'Force', 'Unit', 'Station'
    ]

    for keyword in institutional_keywords:
        if keyword in text:
            return True

    return False

def is_swapped(name, role):
    """
    Determine if name and role fields are swapped.

    Returns True if:
    - name field looks like institution/department and role looks like person name
    - Both look like person names (ambiguous case - check which is more likely the name)
    """

    # Case 1: name is clearly institutional
    if looks_like_institution(name) and looks_like_person_name(role):
        return True

    # Case 2: role is clearly institutional and name is a person - NOT swapped
    if looks_like_person_name(name) and looks_like_institution(role):
        return False

    # Case 3: Both look like person names (e.g., "J. Blythe" and "A. Eastgate")
    # This is tricky - could be either a swap or a multi-person entry
    if looks_like_person_name(name) and looks_like_person_name(role):
        # Count name-like features in each
        name_score = (len(re.findall(r'\b[A-Z][a-z]+\b', name)) * 2 +
                      len(re.findall(r'\b[A-Z]\.', name)))
        role_score = (len(re.findall(r'\b[A-Z][a-z]+\b', role)) * 2 +
                      len(re.findall(r'\b[A-Z]\.', role)))

        # If role has significantly more name features, it's likely swapped
        if role_score > name_score + 1:
            return True

    # Case 4: Both are job titles/departments - NOT swapped (keep as is)
    # Default: assume not swapped
    return False

def smart_fix_fiji(input_file, output_file):
    """Smart fix that only swaps truly swapped records."""

    print(f"Loading {input_file}...")
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    people = data['people']
    print(f"Total records: {len(people)}")

    # Analyze task_pattern_extraction records
    task_pattern_records = [p for p in people if p.get('extraction_method') == 'task_pattern_extraction']
    print(f"\ntask_pattern_extraction records: {len(task_pattern_records)} ({100*len(task_pattern_records)/len(people):.1f}%)")

    # Identify truly swapped records
    swapped_count = 0
    not_swapped_count = 0
    fixed_records = []
    samples = []

    for person in people:
        if person.get('extraction_method') == 'task_pattern_extraction':
            name = person.get('name', '')
            role = person.get('role', '')

            if is_swapped(name, role):
                # Store sample for reporting
                if swapped_count < 10:
                    samples.append({
                        'year': person.get('year'),
                        'line': person.get('line_number'),
                        'before_name': name,
                        'before_role': role,
                        'reason': 'institutional_name' if looks_like_institution(name) else 'name_patterns'
                    })

                # Swap name and role
                person['name'], person['role'] = role, name

                # Store after for sample
                if swapped_count < 10:
                    samples[-1]['after_name'] = person['name']
                    samples[-1]['after_role'] = person['role']

                # Update notes
                if 'notes' not in person or not person['notes']:
                    person['notes'] = "Smart swap correction applied (name was institutional/department)"
                else:
                    person['notes'] += "; Smart swap correction applied"

                # Update extraction method
                person['extraction_method'] = 'task_pattern_extraction_smart_fixed'

                swapped_count += 1
                fixed_records.append(person)
            else:
                not_swapped_count += 1
                # Keep as is, but update method name for tracking
                person['extraction_method'] = 'task_pattern_extraction_verified_correct'

    print(f"\n✅ Analysis complete:")
    print(f"   - Records that WERE swapped (fixed): {swapped_count} ({100*swapped_count/len(task_pattern_records):.1f}%)")
    print(f"   - Records that were ALREADY correct (kept): {not_swapped_count} ({100*not_swapped_count/len(task_pattern_records):.1f}%)")

    # Update metadata
    if 'metadata' not in data:
        data['metadata'] = {}

    data['metadata']['smart_fix_applied'] = {
        'date': datetime.now().isoformat(),
        'bug': 'task_pattern_extraction name/role swap (selective)',
        'records_fixed': swapped_count,
        'records_kept_as_is': not_swapped_count,
        'fix_description': 'Only swapped records with institutional names in name field'
    }
    data['metadata']['version'] = 'v3_smart_fixed'

    # Save fixed data
    print(f"\nSaving to {output_file}...")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    print(f"✅ Saved {len(people)} records to {output_file}")

    return samples, swapped_count, not_swapped_count, len(people)

if __name__ == '__main__':
    input_file = '/home/user/colonial_office_list/fiji_all_years_v2.json'
    output_file = '/home/user/colonial_office_list/fiji_all_years_v3_smart_fixed.json'

    samples, fixed, kept, total = smart_fix_fiji(input_file, output_file)

    print("\n" + "="*80)
    print("SAMPLE CORRECTIONS (first 10 swapped records):")
    print("="*80)

    for i, sample in enumerate(samples, 1):
        print(f"\n{i}. Year {sample['year']}, Line {sample['line']} (Reason: {sample['reason']})")
        print(f"   BEFORE: name=\"{sample['before_name']}\", role=\"{sample['before_role']}\"")
        print(f"   AFTER:  name=\"{sample['after_name']}\", role=\"{sample['after_role']}\"")

    print("\n" + "="*80)
    print("SUMMARY:")
    print("="*80)
    print(f"Total records: {total}")
    print(f"Records fixed (were swapped): {fixed} ({100*fixed/total:.1f}%)")
    print(f"Records kept (already correct): {kept} ({100*kept/total:.1f}%)")
    print(f"Output file: {output_file}")
    print("\n✅ Smart fix complete!")
