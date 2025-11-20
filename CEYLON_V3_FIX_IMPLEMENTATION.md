# Ceylon v3 Quality Fixes - Implementation Guide

**Based on:** CEYLON_V3_QUALITY_REVIEW.md
**Target:** Improve from 85.6/100 to 90-95/100

---

## Quick Reference

| Fix | Priority | Effort | Impact | Score After |
|-----|----------|--------|--------|-------------|
| Plural Roles | HIGH | 2-3 hours | +4-5 points | ~90/100 ✓ |
| Location Stripping | MEDIUM | 3-4 hours | +2-3 points | ~92/100 ✓ |
| Context Inference | MEDIUM | 5-6 hours | +2-3 points | ~95/100 ✓ |

---

## Fix #1: Singularize Plural Roles (HIGH PRIORITY)

**Impact:** Fixes ~25/150 records (16.7%)
**Effort:** 2-3 hours
**Improvement:** +4-5 points → 90/100

### Current Issues

```
"Superintending Officers" (14 instances)
"Assistant Colonial Surgeons" (5 instances)
"Surveyors" (7 instances)
"Assistant Surveyors" (1 instance)
```

### Implementation

Add to `/home/user/colonial_office_list/scripts/ceylon_pattern_extractor.py`:

```python
# Add at top of file after imports
PLURAL_TO_SINGULAR_ROLES = {
    # Explicit mappings for Ceylon-specific roles
    'Superintending Officers': 'Superintending Officer',
    'Assistant Colonial Surgeons': 'Assistant Colonial Surgeon',
    'Colonial Surgeons': 'Colonial Surgeon',
    'Assistant Surveyors': 'Assistant Surveyor',
    'Surveyors': 'Surveyor',
    'Government Agents': 'Government Agent',
    'Medical Assistants': 'Medical Assistant',
    'Draftsmen and Estimates': 'Draftsman',  # Special case
}

def singularize_role(role):
    """
    Convert plural role names to singular.

    Handles both explicit mappings and generic patterns.

    Args:
        role (str): Role name that might be plural

    Returns:
        str: Singular version of the role

    Examples:
        >>> singularize_role("Superintending Officers")
        'Superintending Officer'
        >>> singularize_role("Colonial Surgeons")
        'Colonial Surgeon'
        >>> singularize_role("Principal Collector")  # Already singular
        'Principal Collector'
    """
    # Check explicit mapping first
    if role in PLURAL_TO_SINGULAR_ROLES:
        return PLURAL_TO_SINGULAR_ROLES[role]

    # Generic plural → singular for compound roles
    # Don't touch single-word roles (might be surnames like "Williams")
    if ' ' in role:
        # Get the last word
        words = role.split()
        last_word = words[-1]

        # Check if it's a common plural pattern
        # Exclude words that naturally end in 's' but aren't plural
        SINGULAR_EXCEPTIONS = ['Mistress', 'Empress', 'Princess', 'Assistant']

        if last_word not in SINGULAR_EXCEPTIONS and last_word.endswith('s'):
            # Common patterns:
            # "Officers" → "Officer"
            # "Surgeons" → "Surgeon"
            # "Agents" → "Agent"
            # "Surveyors" → "Surveyor"

            if last_word.endswith('ors'):  # Officers, Surveyors
                words[-1] = last_word[:-1]  # Remove 's'
                return ' '.join(words)

            elif last_word.endswith('ons'):  # Surgeons
                words[-1] = last_word[:-1]
                return ' '.join(words)

            elif last_word.endswith('nts'):  # Agents, Assistants (but we exclude Assistant)
                words[-1] = last_word[:-1]
                return ' '.join(words)

            elif last_word.endswith('ies'):  # Secretaries → Secretary
                words[-1] = last_word[:-3] + 'y'
                return ' '.join(words)

    # Return unchanged if no plural pattern detected
    return role
```

### Apply to All Extraction Methods

Modify each pattern extraction function to use singularization:

```python
# In extract_ceylon_pattern1(), extract_ceylon_name_salary(), etc.

# BEFORE (current code):
person_data = {
    'name': name,
    'role': role,
    # ... other fields
}

# AFTER (with singularization):
person_data = {
    'name': name,
    'role': singularize_role(role),  # ← ADD THIS
    # ... other fields
}
```

### Test Cases

```python
# Add to test file or run interactively
test_cases = [
    ("Superintending Officers", "Superintending Officer"),
    ("Assistant Colonial Surgeons", "Assistant Colonial Surgeon"),
    ("Surveyors", "Surveyor"),
    ("Colonial Secretary", "Colonial Secretary"),  # No change
    ("Principal Assistant", "Principal Assistant"),  # No change
]

for input_role, expected in test_cases:
    result = singularize_role(input_role)
    status = "✓" if result == expected else "✗"
    print(f"{status} {input_role} → {result} (expected: {expected})")
```

---

## Fix #2: Strip Locations from Roles (MEDIUM PRIORITY)

**Impact:** Fixes ~16/150 records (10.7%)
**Effort:** 3-4 hours
**Improvement:** +2-3 points → 92/100

### Current Issues

```
"District Judge of Colombo" → should be role="District Judge", location="Colombo"
"Registrar Central Province" → should be role="Registrar", location="Central Province"
"Bishop of Colombo" → should be role="Bishop", location="Colombo"
```

### Implementation

Add to `/home/user/colonial_office_list/scripts/ceylon_pattern_extractor.py`:

```python
# Add location lists at top of file
CEYLON_LOCATIONS = [
    'Colombo', 'Kandy', 'Galle', 'Jaffna', 'Trincomalee', 'Batticaloa',
    'Matura', 'Hambantotte', 'Ratnapoora', 'Negombo', 'Chilaw', 'Manaar',
    'Kaugalle', 'Matella', 'Badulla', 'Nuwera Ellia', 'Kurnegalle', 'Putlam',
    'Mulletivoe', 'Nuwakalawiya', 'Point Pedro', 'Chavagacherry', 'Cayts',
    'Calpentyn', 'Tangalle', 'Cultura', 'Pantura', 'Harispattu', 'Dambool',
    'Keigalle', 'Avishavelle', 'Gamoola', 'Ballepittymodere'
]

CEYLON_PROVINCES = [
    'Western Province', 'Central Province', 'Southern Province',
    'Northern Province', 'Eastern Province', 'North Western Province'
]

CEYLON_REGIONS = [
    'Midland Circuit', 'Southern Circuit', 'Northern Circuit',
    'Upper and Lower Dumbera'
]

def extract_location_from_role(role_string):
    """
    Separate embedded location from role string.

    Returns:
        tuple: (clean_role, extracted_location)
            - clean_role: Role with location removed, or None if role is ONLY location
            - extracted_location: The location found, or None

    Examples:
        >>> extract_location_from_role("District Judge of Colombo")
        ('District Judge', 'Colombo')

        >>> extract_location_from_role("Registrar Central Province")
        ('Registrar', 'Central Province')

        >>> extract_location_from_role("Bishop of Colombo")
        ('Bishop', 'Colombo')

        >>> extract_location_from_role("North Western Province")
        (None, 'North Western Province')  # Role is ONLY location - needs context

        >>> extract_location_from_role("Colonial Secretary")
        ('Colonial Secretary', None)  # No location embedded
    """
    original_role = role_string
    extracted_location = None

    # Pattern 1: "Role of Location" (e.g., "District Judge of Colombo")
    for location in CEYLON_LOCATIONS:
        pattern = f" of {location}"
        if pattern in role_string:
            clean_role = role_string.replace(pattern, '').strip()
            return clean_role, location

    # Pattern 2: "Role Location" where location is at the end (e.g., "Registrar Central Province")
    for province in CEYLON_PROVINCES:
        if role_string.endswith(province):
            # Remove province from end
            clean_role = role_string[:-len(province)].strip()
            # Check if anything is left
            if clean_role:
                return clean_role, province
            else:
                # Role was ONLY the province
                return None, province

    # Pattern 3: Check if entire string is just a location/province
    all_locations = CEYLON_LOCATIONS + CEYLON_PROVINCES + CEYLON_REGIONS
    if role_string in all_locations:
        return None, role_string

    # No location found
    return role_string, None
```

### Handle Missing Roles

When role is None (only location found), need to infer from context:

```python
def infer_role_from_context(section_header, last_explicit_role):
    """
    When only a location is found, infer the role from context.

    Args:
        section_header: The current department/section name
        last_explicit_role: The last explicitly stated role in this section

    Returns:
        str: Inferred role, or "Unknown" if cannot infer

    Example:
        >>> # In "Judicial Establishment" section, after "Deputy Queen's Advocate"
        >>> infer_role_from_context("Judicial Establishment", "Deputy Queen's Advocate")
        'Deputy Queen\'s Advocate'
    """
    # If we have a recent explicit role in same section, use it
    if last_explicit_role:
        # Check if it's a "ditto" pattern (Deputy ditto, Second ditto, etc.)
        # If so, we're continuing the same role
        return last_explicit_role

    # Otherwise, mark as needing manual review
    return "Unknown - Location Only"
```

### Apply to Extraction

```python
# Modify extraction functions:

def extract_ceylon_pattern1(line, line_num, department, province):
    """Extract: Role, Name Qualifications, Salary"""

    # ... existing pattern matching ...

    if match:
        role = match.group(1).strip()
        name = match.group(2).strip()

        # NEW: Extract location from role
        clean_role, location = extract_location_from_role(role)

        # If role is None, it was only a location - flag for review
        if clean_role is None:
            clean_role = "Unknown - Location Only"
            # Could also try to infer from context here

        # Singularize
        clean_role = singularize_role(clean_role)

        person_data = {
            'name': name,
            'role': clean_role,
            'location': location or f"CEYLON - {department}",  # Use extracted location if found
            # ... other fields
        }
```

### Test Cases

```python
test_cases = [
    ("District Judge of Colombo", "District Judge", "Colombo"),
    ("Registrar Central Province", "Registrar", "Central Province"),
    ("Bishop of Colombo", "Bishop", "Colombo"),
    ("North Western Province", None, "North Western Province"),
    ("Colonial Secretary", "Colonial Secretary", None),
]

for input_role, expected_role, expected_location in test_cases:
    role, location = extract_location_from_role(input_role)
    status = "✓" if (role == expected_role and location == expected_location) else "✗"
    print(f"{status} '{input_role}'")
    print(f"   → role='{role}', location='{location}'")
```

---

## Fix #3: Context-Aware Role Inference (MEDIUM PRIORITY)

**Impact:** Fixes ~8/150 records + handles "ditto" cases
**Effort:** 5-6 hours
**Improvement:** +2-3 points → 95/100

### Current Issues

```
Line 336: "North Western Province, G. F. Nell, 300l."
  Context: Previous lines show "Deputy Queen's Advocate" roles
  Current: role="North Western Province"
  Should be: role="Deputy Queen's Advocate", location="North Western Province"

Line 333: "Deputy ditto, C. H. Stewart, 1,000l."
  Context: Previous was "Queen's Advocate"
  Should expand: "Deputy ditto" → "Deputy Queen's Advocate"
```

### Implementation

Add stateful context tracking:

```python
class CeylonExtractor:
    """
    Stateful extractor that tracks context across lines.
    """

    def __init__(self):
        self.current_department = None
        self.current_province = None
        self.last_explicit_role = None  # Track for ditto expansion
        self.section_roles = []  # Track all roles in current section

    def expand_ditto(self, role_string):
        """
        Expand 'ditto' references.

        Examples:
            "Deputy ditto" + last_role="Queen's Advocate"
              → "Deputy Queen's Advocate"

            "Second ditto" + last_role="Assistant"
              → "Second Assistant"

            "ditto" + last_role="Government Agent"
              → "Government Agent"
        """
        if 'ditto' not in role_string.lower():
            # Not a ditto reference, save as last explicit role
            self.last_explicit_role = role_string
            return role_string

        # Extract any prefix before "ditto"
        prefix_match = re.match(r'(\w+)\s+ditto', role_string, re.IGNORECASE)

        if prefix_match:
            # Has modifier: "Deputy ditto", "Second ditto"
            prefix = prefix_match.group(1)
            if self.last_explicit_role:
                expanded = f"{prefix} {self.last_explicit_role}"
                return expanded
            else:
                # No context to expand
                return f"{prefix} [Unknown]"

        else:
            # Just "ditto" - use previous role as-is
            if self.last_explicit_role:
                return self.last_explicit_role
            else:
                return "[Unknown - Ditto]"

    def infer_role_when_missing(self, location):
        """
        When only location is extracted, infer role from context.

        Uses the last explicit role in the current section.
        """
        if self.last_explicit_role:
            # Use the last explicit role (likely continuing same role type)
            return self.last_explicit_role

        # Check if we're in a section with consistent roles
        if len(self.section_roles) > 0:
            # Use most common role in this section
            from collections import Counter
            role_counts = Counter(self.section_roles)
            most_common = role_counts.most_common(1)[0][0]
            return most_common

        # Cannot infer
        return "Unknown - Location Only"

    def process_line(self, line, line_num, department):
        """
        Process a single line with context awareness.
        """
        # Update current department/section
        if department != self.current_department:
            self.current_department = department
            self.last_explicit_role = None
            self.section_roles = []

        # Try pattern extraction
        person = self.extract_with_patterns(line, line_num)

        if person:
            role = person['role']

            # Expand ditto references
            role = self.expand_ditto(role)

            # Extract location
            clean_role, location = extract_location_from_role(role)

            # If role is None (was only location), infer from context
            if clean_role is None:
                clean_role = self.infer_role_when_missing(location)
                person['notes'] = 'Role inferred from context'

            # Singularize
            clean_role = singularize_role(clean_role)

            # Update person data
            person['role'] = clean_role
            if location:
                person['location'] = f"CEYLON - {location}"

            # Track for context
            self.section_roles.append(clean_role)

            return person

        return None
```

### Test Scenario

```python
# Simulate processing the "Deputy Queen's Advocate" section:

extractor = CeylonExtractor()
extractor.current_department = "Judicial Establishment"

# Line 332
result = extractor.process_line("Deputy ditto, C. H. Stewart, 1,000l.", 332, "Judicial Establishment")
# Should expand to "Deputy Queen's Advocate"

# Line 336
result = extractor.process_line("North Western Province, G. F. Nell, 300l.", 336, "Judicial Establishment")
# Should infer role="Deputy Queen's Advocate", location="North Western Province"
```

---

## Integration Plan

### Step 1: Add Helper Functions (1 hour)

Add to `ceylon_pattern_extractor.py`:
- `singularize_role()`
- `extract_location_from_role()`

### Step 2: Test Helpers (30 min)

Create test file and verify:
```bash
python3 -m pytest tests/test_ceylon_fixes.py -v
```

### Step 3: Apply to Pattern Functions (1 hour)

Modify all pattern extraction functions to use helpers:
- `extract_ceylon_pattern1()`
- `extract_ceylon_name_salary()`
- `extract_ceylon_location_name()`
- `extract_ceylon_name_list()`

### Step 4: Refactor to Stateful Extractor (2-3 hours)

- Create `CeylonExtractor` class
- Migrate pattern functions to methods
- Add context tracking
- Implement ditto expansion

### Step 5: Re-run Extraction (10 min)

```bash
python3 scripts/run_ceylon_extraction.py
```

### Step 6: Quality Review (30 min)

```bash
python3 ceylon_v3_quality_review.py
# Should show improvement to 90-95/100
```

---

## Expected Results After All Fixes

### Quality Metrics
```
Overall Score:    95/100 (was 85.6/100)
Perfect Records:  85-90% (was 72.2%)
Major Errors:     2-3% (was 11.1%)
Minor Errors:     8-10% (was 16.7%)
```

### Error Reductions
```
Plural roles:          0 instances (was ~25)
Location as role:      0-2 instances (was ~16)
Ditto not expanded:    0 instances (was unknown)
Context inference:     90% success rate
```

### Confidence Distribution
```
High (≥ 0.9):   90+ records (was 59)
Medium (0.7-0.89): 55-60 records (was 91)
Low (< 0.7):    0 records (was 0)
```

---

## Validation Checklist

After implementing fixes, verify:

- [ ] No plural roles remain (check: "Officers", "Surgeons", "Agents")
- [ ] Locations extracted separately (check sample: "District Judge of Colombo")
- [ ] "Ditto" expanded correctly (check lines 332-336)
- [ ] Context inference working (check line 336 specifically)
- [ ] No new errors introduced
- [ ] All existing perfect records still perfect
- [ ] Quality score ≥ 90/100
- [ ] Confidence distribution improved

---

## Rollback Plan

If quality decreases:

1. Git revert to previous version
2. Review specific failing cases
3. Add targeted test cases
4. Re-implement with fixes

Keep backup:
```bash
cp ceylon_1867_v3_specialized.json ceylon_1867_v3_specialized_backup.json
```

---

**Implementation Priority:**
1. Fix #1 (Plural Roles) - Highest ROI, easiest implementation
2. Fix #2 (Location Stripping) - Medium ROI, medium complexity
3. Fix #3 (Context Inference) - Medium ROI, highest complexity

**Recommended approach:** Implement Fix #1 first, validate to 90/100, then decide if Fixes #2 and #3 are worth the additional effort.
