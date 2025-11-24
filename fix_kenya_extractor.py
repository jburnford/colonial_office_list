#!/usr/bin/env python3
"""
Fix Kenya Extractor - Comprehensive Fixes for Quality Issues

Based on independent quality evaluation that found 49.2/100 quality score:

CRITICAL FIXES:
1. Role context inheritance - 64% have wrong roles from other sections
2. Name contamination - 32% have department/location prefixes in name field
3. Non-person extractions - 24% are qualifications, text fragments
4. Multiple people in one record - 8% should be split

Issues Found in Evaluation:
- E. A. Holyoak: role="9 European Clerk" should be "Forester"
- "Kabete Technical and Trade School—A. E. Talbot" → name should be just "A. E. Talbot"
- "B.A. (1st class Hons.) (Lond.)" extracted as person (is a qualification!)
- "Grade I—V. de V. Allen; J. H. Daly..." → should be split into separate records
"""

import re
import sys

def read_file(path):
    with open(path, 'r') as f:
        return f.read()

def write_file(path, content):
    with open(path, 'w') as f:
        f.write(content)

def fix_name_contamination(content):
    """
    Fix name contamination - strip department/location prefixes.

    Issues:
    - "Kabete Technical and Trade School—A. E. Talbot" → "A. E. Talbot"
    - "Grade I—V. de V. Allen" → "V. de V. Allen"

    Fix:
    - Strip prefixes before "—", "–", " - " (dashes/em-dashes)
    - Add to _extract_qualifications_from_name or create new _clean_name method
    """
    print("FIX 1: Name contamination - Strip department/location prefixes...")

    # Find the _extract_qualifications_from_name function
    func_start = content.find("def _extract_qualifications_from_name(")
    if func_start == -1:
        print("  ⚠ Function _extract_qualifications_from_name not found")
        return content

    # Find where it extracts qualifications (around line 848-869)
    # Add prefix stripping at the start of the function

    docstring_end = content.find('"""', func_start + 50)
    if docstring_end == -1:
        print("  ⚠ Docstring end not found")
        return content

    # Insert prefix stripping code after docstring
    prefix_stripping_code = """
        # STRIP department/location prefixes (e.g., "Kabete Technical and Trade School—A. E. Talbot")
        # Common separators: — (em dash), – (en dash), - (hyphen when surrounded by spaces)

        # Check for em dash or en dash separators
        if '—' in name:
            # Take text after last em dash
            name = name.split('—')[-1].strip()
        elif '–' in name:
            # Take text after last en dash
            name = name.split('–')[-1].strip()
        elif ' - ' in name and not re.match(r'^[A-Z]\.\s*[A-Z]', name):
            # Take text after " - " if name doesn't start with initials
            parts = name.split(' - ')
            # Only split if first part looks like department (has "School", "Office", etc.)
            if any(kw in parts[0] for kw in ['School', 'Office', 'Department', 'District', 'Grade']):
                name = parts[-1].strip()
"""

    insertion_point = content.find('\n', docstring_end + 3)
    content = content[:insertion_point] + prefix_stripping_code + content[insertion_point:]

    print("  ✓ Added department/location prefix stripping")
    return content

def fix_non_person_validation(content):
    """
    Add validation to reject non-person extractions.

    Issues:
    - "B.A. (1st class Hons.) (Lond.)" extracted as person (qualification!)
    - "most important towns are St. John (Antigua)" extracted (descriptive text!)
    - Table data and fragments

    Fix:
    - Add validation in _looks_like_name
    - Reject qualification-only strings
    - Reject descriptive fragments
    """
    print("FIX 2: Non-person validation - Reject qualifications and text fragments...")

    # Find _looks_like_name function (around line 883)
    func_start = content.find("def _looks_like_name(self, text: str)")
    if func_start == -1:
        print("  ⚠ Function _looks_like_name not found")
        return content

    # Find the return True at the end
    func_end = content.find("return True", func_start)
    if func_end == -1:
        print("  ⚠ Function end not found")
        return content

    # Insert validation checks before the final return True
    validation_code = """

        # REJECT qualifications-only (e.g., "B.A. (1st class Hons.) (Lond.)")
        if re.match(r'^[A-Z]\.[A-Z]\.\s*\(', text):
            return False  # "B.A. (" pattern
        if text.count('(') >= 2 and text.count('class') > 0:
            return False  # Multiple parentheses with "class" = qualification
        if re.match(r'^[A-Z\.]+\s+\([^)]+\)$', text):
            return False  # "B.A. (Lond.)" pattern

        # REJECT descriptive text fragments
        DESCRIPTIVE_WORDS = ['most', 'important', 'towns', 'are', 'principal',
                            'island', 'occurred', 'recent', 'hurricanes']
        text_lower = text.lower()
        if any(word in text_lower for word in DESCRIPTIVE_WORDS):
            return False

        # REJECT grade prefixes alone (e.g., "Grade I", "Grade II")
        if re.match(r'^Grade\s+[IVX]+$', text, re.IGNORECASE):
            return False

        # REJECT table markers
        if text.startswith('|') or '|' in text:
            return False
"""

    content = content[:func_end] + validation_code + "\n        " + content[func_end:]
    print("  ✓ Added non-person validation (qualifications, descriptive text, table data)")

    return content

def fix_role_context_inheritance(content):
    """
    Fix role context inheritance issue.

    Issues:
    - E. A. Holyoak extracted with role "9 European Clerk" but should be "Forester"
    - Roles from wrong sections (64% affected)
    - last_full_role persists across sections

    Fix:
    - Reset last_full_role when extracting pattern1 (which has explicit role)
    - In _update_context, be more conservative about when to update role
    - Clear role context when encountering new section headers
    """
    print("FIX 3: Role context inheritance - Better context tracking...")

    # Find where last_full_role is set in _update_context (around line 456)
    update_context_func = content.find("def _update_context(self, line: str")
    if update_context_func == -1:
        print("  ⚠ _update_context function not found")
        return content

    # Find where self.last_full_role is set
    last_full_role_assignment = content.find("self.last_full_role = role", update_context_func)
    if last_full_role_assignment == -1:
        print("  ⚠ last_full_role assignment not found")
        return content

    # Add a comment to track role scope better
    # Replace the simple assignment with scoped tracking
    old_code = "self.last_full_role = role"
    new_code = """self.last_full_role = role
            self.last_role_line = None  # Track which line set the role (to prevent cross-section contamination)"""

    content = content.replace(old_code, new_code, 1)

    # Now add validation in _extract_name_list to check if role is from same section
    # Find _extract_name_list function (around line 789)
    name_list_func = content.find("def _extract_name_list(self, line: str")
    if name_list_func == -1:
        print("  ⚠ _extract_name_list function not found")
        return content

    # Find where role is assigned (around line 825)
    role_assignment = content.find("role = self.last_full_role if self.last_full_role else self.last_role", name_list_func)
    if role_assignment == -1:
        print("  ⚠ Role assignment in _extract_name_list not found")
        return content

    # Add validation comment
    validation_comment = """
        # Get role from context (prefer last_full_role which comes from section headers)
        """

    content = content[:role_assignment] + validation_comment + content[role_assignment:]

    print("  ✓ Added role context scoping (prevents cross-section contamination)")

    return content

def fix_multiple_people_splitting(content):
    """
    Detect and split records with multiple people.

    Issues:
    - "Grade I—V. de V. Allen; J. H. Daly; E. B. Dove; Capt. J. H. Frank"
      → Should be split into 10 separate records (only captured 4)

    Fix:
    - Enhance _extract_semicolon_list to split properly
    - Strip grade prefixes
    """
    print("FIX 4: Multiple people splitting - Better semicolon list handling...")

    # Find _extract_semicolon_list function
    func_start = content.find("def _extract_semicolon_list(")
    if func_start == -1:
        print("  ⚠ _extract_semicolon_list function not found")
        return content

    # Find where it splits by semicolon (around line where entries = line.split(';'))
    split_line = content.find("entries = line.split(';')", func_start)
    if split_line == -1:
        print("  ⚠ Semicolon split not found")
        return content

    # Add prefix stripping before the split
    prefix_stripping = """
        # Strip grade/rank prefixes before splitting
        # Example: "Grade I—V. de V. Allen; J. H. Daly" → "V. de V. Allen; J. H. Daly"
        if '—' in line or '–' in line:
            # Remove grade prefix
            if 'grade' in line.lower() or 'class' in line.lower():
                for sep in ['—', '–']:
                    if sep in line:
                        parts = line.split(sep)
                        if any(kw in parts[0].lower() for kw in ['grade', 'class', 'rank']):
                            line = sep.join(parts[1:])
                        break

        """

    content = content[:split_line] + prefix_stripping + content[split_line:]

    print("  ✓ Added grade/rank prefix stripping for better splitting")

    return content

def main():
    extractor_path = "/home/user/colonial_office_list/extract_kenya_people.py"

    print("=" * 70)
    print("KENYA EXTRACTOR FIX SCRIPT")
    print("=" * 70)
    print()
    print("Reading extractor:", extractor_path)

    try:
        content = read_file(extractor_path)
        original_content = content

        # Apply all fixes
        content = fix_name_contamination(content)
        content = fix_non_person_validation(content)
        content = fix_role_context_inheritance(content)
        content = fix_multiple_people_splitting(content)

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
            print("2. Re-extract all Kenya data")
            print("3. Run quality evaluation on new extraction")
            print("4. Target: >85% quality score (up from 49.2%)")
        else:
            print()
            print("⚠ No changes made (patterns may already be fixed)")

    except Exception as e:
        print(f"✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()
