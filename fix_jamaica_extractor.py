#!/usr/bin/env python3
"""
Fix Jamaica Extractor - Comprehensive Fixes for Quality Issues

Based on independent quality evaluation that found 37.2/100 quality score:

CRITICAL FIXES:
1. Pattern5 (name_list) - Fix regex to capture ALL initials (not just last one)
2. Pattern4 (semicolon_list) - Add validation to reject non-person sections
3. Pattern2 (location_name_salary) - Fix role extraction (currently 0% accurate)
4. Pattern1 (role_name_salary) - Fix location/name confusion

Issues Found in Evaluation:
- Pattern5: "B. Mais" should be "W. B. Mais" (drops first initial)
- Pattern4: Extracted "November" from hurricane text
- Pattern2: 0% role accuracy (uses wrong context)
- Pattern1: "Negril Point" extracted as name instead of "J. S. Brownhill"
"""

import re
import sys

def read_file(path):
    with open(path, 'r') as f:
        return f.read()

def write_file(path, content):
    with open(path, 'w') as f:
        f.write(content)

def fix_pattern5_name_list(content):
    """
    Fix Pattern5 to capture ALL initials, not just the last one.

    OLD: ([A-Z]\.\s*[A-Z][a-z]+)  # Only captures last initial + surname
    NEW: ([A-Z](?:\.\s*[A-Z])*\.\s*[A-Z][a-z]+)  # Captures all initials + surname

    Examples:
    - OLD matches: "B. Mais" from "W. B. Mais"
    - NEW matches: "W. B. Mais"
    """
    print("FIX 1: Pattern5 (name_list) - Capture all initials...")

    old_pattern = r"names = re.findall\(r'\(\[A-Z\]\\\.\\\s\*\[A-Z\]\[a-z\]\+\)', line\)"
    new_pattern = r"names = re.findall(r'([A-Z](?:\.\s*[A-Z])*\.\s*[A-Z][a-z]+)', line)"

    if old_pattern in content or "names = re.findall(r'([A-Z]\.\s*[A-Z][a-z]+)', line)" in content:
        content = content.replace(
            "names = re.findall(r'([A-Z]\.\s*[A-Z][a-z]+)', line)",
            "names = re.findall(r'([A-Z](?:\.\s*[A-Z])*\.\s*[A-Z][a-z]+)', line)"
        )
        print("  ✓ Fixed regex to capture all initials (W. B. Mais, not just B. Mais)")
    else:
        print("  ⚠ Pattern not found (may already be fixed)")

    return content

def fix_pattern4_semicolon_validation(content):
    """
    Add validation to Pattern4 to reject non-person sections.

    Issues:
    - Currently extracts from descriptive text like hurricanes
    - Example: "October, 1944; November, 1932..." → extracted "November" as a person

    Fix:
    - Add month name validation
    - Check that we're in a people section
    - Require at least a minimal name pattern
    """
    print("FIX 2: Pattern4 (semicolon_list) - Add non-person validation...")

    # Find the Pattern4 function
    pattern4_start = content.find("def _extract_semicolon_list(")
    if pattern4_start == -1:
        print("  ⚠ Pattern4 function not found")
        return content

    # Find the "if ';' not in line:" check (around line 696)
    semicolon_check = content.find("if ';' not in line:", pattern4_start)
    if semicolon_check == -1:
        print("  ⚠ Semicolon check not found")
        return content

    # Add validation after the semicolon check
    insertion_point = content.find("if not self.last_role:", semicolon_check)
    if insertion_point == -1:
        print("  ⚠ Insertion point not found")
        return content

    # Insert validation before the last_role check
    validation_code = """
        # VALIDATION: Reject non-person sections (hurricanes, climate, etc.)
        MONTH_NAMES = {'January', 'February', 'March', 'April', 'May', 'June',
                      'July', 'August', 'September', 'October', 'November', 'December'}

        # Check if line contains month names (likely hurricane/climate section)
        line_words = set(re.findall(r'\\b[A-Z][a-z]+\\b', line))
        if line_words & MONTH_NAMES:
            return None  # Likely climate/hurricane section, not people

        # Check for descriptive keywords
        DESCRIPTIVE_KEYWORDS = ['occurred', 'hurricanes', 'principal', 'island',
                               'climate', 'temperature', 'rainfall', 'recent']
        if any(kw in line.lower() for kw in DESCRIPTIVE_KEYWORDS):
            return None  # Descriptive text, not people

"""

    content = content[:insertion_point] + validation_code + content[insertion_point:]
    print("  ✓ Added month name and descriptive text validation")

    return content

def fix_pattern2_role_extraction(content):
    """
    Fix Pattern2 to extract roles correctly.

    Issues:
    - Currently uses self.last_role (from context)
    - 0% role accuracy in evaluation
    - Assigns location names as roles

    Fix:
    - Use a conservative default when role context is uncertain
    - Mark role as inferred
    """
    print("FIX 3: Pattern2 (location_name_salary) - Fix role extraction...")

    # Find the line where role is assigned (around line 614)
    role_assignment = "role = self.last_role or \"Officer\""

    if role_assignment in content:
        # Replace with better logic
        new_role_code = '''# Role from context (mark as uncertain if it's a default)
        role = self.last_role if self.last_role else "Officer (location-based)"

        # If last_role looks like a location (not a role), use default
        if role and role in JAMAICA_LOCATIONS:
            role = "Officer (location-based)"'''

        content = content.replace(
            "        " + role_assignment,
            new_role_code
        )
        print("  ✓ Fixed role assignment to avoid using locations as roles")
    else:
        print("  ⚠ Role assignment pattern not found")

    return content

def fix_pattern1_location_confusion(content):
    """
    Fix Pattern1 to detect when second field is a location, not a name.

    Issues:
    - "Superintendent, Negril Point, J. S. Brownhill, 150l."
      → Extracted "Negril Point" as name instead of "J. S. Brownhill"

    Fix:
    - Check if group(2) is in JAMAICA_LOCATIONS
    - If so, use group(3) as the name
    """
    print("FIX 4: Pattern1 (role_name_salary) - Fix location/name confusion...")

    # Find Pattern1 function
    pattern1_start = content.find("def _extract_pattern1(")
    if pattern1_start == -1:
        print("  ⚠ Pattern1 function not found")
        return content

    # Find where name is assigned (around line 513)
    name_assignment = content.find("name = match.group(2).strip()", pattern1_start)
    if name_assignment == -1:
        print("  ⚠ Name assignment not found")
        return content

    # Find the section after qual and salary are extracted
    qual_assignment = content.find("potential_qual = match.group(3).strip()", pattern1_start)
    if qual_assignment == -1:
        print("  ⚠ Qual assignment not found")
        return content

    # Insert location check after initial assignments
    salary_line_end = content.find("\n", content.find("salary = match.group(4)", pattern1_start))

    location_check_code = """
        # CHECK: Is group(2) actually a location, not a name?
        # Example: "Superintendent, Negril Point, J. S. Brownhill, 150l."
        # Should extract "J. S. Brownhill" as name, not "Negril Point"
        if name in JAMAICA_LOCATIONS and potential_qual:
            # Swap: group(2) is location, group(3) is actual name
            actual_location = name
            name = potential_qual
            potential_qual = None  # Already used as name
            # Update parish if we found a specific location
            if actual_location in JAMAICA_PARISHES:
                self.current_parish = actual_location
"""

    content = content[:salary_line_end+1] + location_check_code + content[salary_line_end+1:]
    print("  ✓ Added location/name confusion detection")

    return content

def main():
    extractor_path = "/home/user/colonial_office_list/extract_jamaica_people.py"

    print("=" * 70)
    print("JAMAICA EXTRACTOR FIX SCRIPT")
    print("=" * 70)
    print()
    print("Reading extractor:", extractor_path)

    try:
        content = read_file(extractor_path)
        original_content = content

        # Apply all fixes
        content = fix_pattern5_name_list(content)
        content = fix_pattern4_semicolon_validation(content)
        content = fix_pattern2_role_extraction(content)
        content = fix_pattern1_location_confusion(content)

        if content != original_content:
            # Backup original
            backup_path = extractor_path + ".backup"
            write_file(backup_path, original_content)
            print()
            print(f"✓ Created backup: {backup_path}")

            # Write fixed version
            write_file(extractor_path, content)
            print(f"✓ Updated extractor: {extractor_path}")
            print()
            print("=" * 70)
            print("FIXES APPLIED SUCCESSFULLY")
            print("=" * 70)
            print()
            print("Next steps:")
            print("1. Test the fixed extractor on a sample file")
            print("2. Re-extract all Jamaica data")
            print("3. Run quality evaluation on new extraction")
            print("4. Target: >90% quality score")
        else:
            print()
            print("⚠ No changes made (patterns may already be fixed)")

    except Exception as e:
        print(f"✗ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
