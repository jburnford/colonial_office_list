# Ceylon People Extraction - Quality Review (V2 Hybrid System)

**Review Date:** 2025-11-20
**Extraction File:** `ceylon_1867_v2_fixed.json`
**Source File:** `output_3/1867_manual_parsed/ceylon.txt`
**Reviewer:** Automated Quality Assessment + Manual Verification

---

## Executive Summary

The Ceylon 1867 extraction using the v2 hybrid system shows **significant quality issues** with an estimated overall accuracy of **56.6%**. While the system successfully extracted 175 people from 464 source lines, approximately **76 people (43.4%) have identifiable errors** in their extracted data, primarily in the role field.

**Overall Quality Score: 57/100**

### Key Findings:
- ✅ **Strengths:** Good salary extraction (100% coverage), consistent metadata tracking
- ❌ **Critical Issues:** High error rate in role extraction, locations/qualifications misidentified as roles
- ⚠️ **Method Performance:** regex_pattern1 is most reliable (84.3% accuracy), task-based methods have severe issues (0-5% accuracy)

---

## Summary Statistics

| Metric | Value |
|--------|-------|
| **Total People Extracted** | 175 |
| **Year Covered** | 1867 |
| **Source Lines** | 464 |
| **Pattern Extraction** | 155 people |
| **LLM Extraction** | 59 people |
| **Average Confidence** | 0.799 |
| **Estimated Accuracy** | 56.6% |

### Extraction Method Distribution

| Method | Count | % of Total | Error Rate |
|--------|-------|------------|------------|
| regex_pattern1 | 83 | 47.4% | **15.7%** ✅ |
| regex_pattern2 | 54 | 30.9% | **64.8%** ❌ |
| task_pattern_extraction | 22 | 12.6% | **~95%** ❌ |
| task_list_extraction | 16 | 9.1% | **100%** ❌ |

### Confidence Distribution

| Level | Count | Percentage |
|-------|-------|------------|
| High (≥ 0.9) | 83 | 47.4% |
| Medium (0.7-0.9) | 92 | 52.6% |
| Low (< 0.7) | 0 | 0.0% |

**Note:** High confidence scores do not correlate with accuracy - many high-confidence extractions contain errors.

---

## Issue Analysis

### Issue 1: Locations Mistaken for Roles ⚠️ CRITICAL

**Severity:** HIGH
**Occurrences:** ~20 instances

#### Description:
Location names are being extracted as job roles, particularly in judicial and customs departments.

#### Examples:

| Name | Extracted Role | Correct Role | Line |
|------|---------------|--------------|------|
| T. Berwick | Kandy ❌ | Deputy Queen's Advocate | 333 |
| H. Muttukristna | Jaffna ❌ | Deputy Queen's Advocate | 334 |
| O. W. C. Morgan | Galle ❌ | Deputy Queen's Advocate | 335 |
| T. Steele | Kandy ❌ | Commissioner of Requests and Police Magistrate | 351 |
| T. C. Power | Badulla ❌ | District Judge, Commissioner of Requests, and Police Magistrate | 346 |

#### Source Pattern:
```
Deputy ditto, Kandy, T. Berwick, 400l.
Commissioners of Requests and Police Magistrates at:
Kandy, T. Steele, 600l.
```

#### Root Cause:
The extraction pattern treats the first element before a name as the role, but in these cases, it's the location where the person serves.

---

### Issue 2: Person Names Mistaken for Roles ⚠️ CRITICAL

**Severity:** HIGH
**Occurrences:** ~14 instances

#### Description:
Other people's names are being used as roles, particularly in the Medical Department where pattern matching fails.

#### Examples:

| Name | Extracted Role | Correct Role | Line |
|------|---------------|--------------|------|
| F. Keyt | J. L. Vanderstraaten ❌ | Medical Assistant | 408 |
| A. E. Tap | J. L. Vanderstraaten ❌ | Medical Assistant | 411 |
| W. A. Woutersz | J. L. Vanderstraaten ❌ | Medical Assistant | 412 |
| C. A. Kriekenbeek | J. Loos ❌ | Assistant Colonial Surgeon | 397 |

#### Source Pattern:
```
Medical Assistant
Acting Assistant Colonial Surgeon, E. L. Koch, 150l.
W. Dias, M.D., 150l.
J. L. Vanderstraaten, M.D., 150l.
F. Keyt, 150l.
```

#### Root Cause:
Pattern matching incorrectly carries forward the previous person's name as the role for subsequent people in a list.

---

### Issue 3: Qualifications Mistaken for Roles ⚠️ MODERATE

**Severity:** MEDIUM
**Occurrences:** 4 instances

#### Description:
Professional qualifications (Assoc. Inst. C.E., M. Inst. C.E.) are extracted as roles instead of the actual job title.

#### Examples:

| Name | Extracted Role | Correct Role | Line |
|------|---------------|--------------|------|
| R. A. Spearling | Assoc. Inst. C.E. ❌ | Superintending Officers | 214 |
| J. A. Caley | M. Inst. C.E. ❌ | Office Assistant | 198 |
| J. F. Churchhill | Assoc. Inst. C.E. ❌ | Provincial Assistant | 204 |
| A. C. Folkard | Assoc. Inst. C.E. ❌ | Provincial Assistant | 206 |

#### Source Pattern:
```
Office Assistant, J. A. Caley, M. Inst. C.E., 750l.
Superintending Officers, R. A. Spearling, Assoc. Inst. C.E., 400l.
```

#### Root Cause:
The extraction pattern treats qualifications as the last element before salary as part of the role.

---

### Issue 4: Name-Location Swaps ⚠️ CRITICAL

**Severity:** HIGH
**Occurrences:** 2 instances

#### Description:
The person's name and location are completely swapped, with the location appearing in the name field and the person's name in the role field.

#### Examples:

| Extracted Name | Extracted Role | Source Line | Correct Interpretation |
|----------------|----------------|-------------|------------------------|
| Morottoo ❌ | A. Mendis ❌ | `A. Mendis, Morottoo, 125l.` | Name: A. Mendis, Location: Morottoo |
| Kandy Districts ❌ | W. F. Kelly ❌ | `Kandy Districts, 200l.` | Name: W. F. Kelly, Location: Kandy Districts |

#### Root Cause:
Incorrect parsing order in regex pattern assumes location-name order instead of name-location order.

---

### Issue 5: Plural Role Names ⚠️ MINOR

**Severity:** LOW
**Occurrences:** 35 instances

#### Description:
Role names are plural (e.g., "Writers", "Assistant Surveyors") when they should be singular for individual person records.

#### Examples:
- "Writers" (16 instances) → should be "Writer"
- "Assistant Surveyors" (8 instances) → should be "Assistant Surveyor"

#### Impact:
Minor data consistency issue; doesn't affect accuracy of person identification but complicates role aggregation and analysis.

---

### Issue 6: False Positives ⚠️ MODERATE

**Severity:** MEDIUM
**Occurrences:** 2-3 instances

#### Examples:
- **Name:** "Keigalle and Avishavelle" (Line 353) - This appears to be two locations, not a person
- **Name:** "Pantura" (Line 356) - Location name only
- **Name:** "Harispattu" (Line 357) - Location name only

#### Source Context:
```
Commissioners of Requests and Police Magistrates at:
Kandy, T. Steele, 600l.
Matelle and Dambool, J. A. H. De Saram, 450l.
Keigalle and Avishavelle, 350l.
```

These lines list only locations with salaries but no person names, likely indicating vacant positions.

---

## Sample Verification Results

**Method:** Random stratified sampling of 10 records across different extraction methods and confidence levels.

### Verification Table

| # | Name | Role | Method | Conf. | Line | Status | Issues |
|---|------|------|--------|-------|------|--------|--------|
| 1 | Morottoo | A. Mendis | regex_pattern1 | 0.9 | 456 | ❌ WRONG | Name-location swap |
| 2 | T. Steele | Kandy | regex_pattern1 | 0.9 | 351 | ❌ WRONG | Location as role |
| 3 | I. Gould | J. L. Vanderstraaten | regex_pattern2 | 0.7 | 420 | ❌ WRONG | Person name as role |
| 4 | R. A. Spearling | Assoc. Inst. C.E. | task_pattern | 0.7 | 214 | ❌ WRONG | Qualification as role |
| 5 | R. Massie | Writers | task_list | 0.75 | 172 | ⚠️ PARTIAL | Plural role (minor) |
| 6 | F. Roosmulecoco | Second Assistant | regex_pattern2 | 0.7 | 222 | ❌ WRONG | Wrong role (should be Superintending Officers) |
| 7 | W. Skeen | Government Printer | regex_pattern1 | 0.9 | 176 | ✅ CORRECT | None |
| 8 | R. W. D. Moir | Landing Surveyor at St. John's River | regex_pattern1 | 0.9 | 243 | ✅ CORRECT | None |
| 9 | L. F. Lee | Writers | task_list | 0.75 | 172 | ⚠️ PARTIAL | Plural role (minor) |
| 10 | F. Vine | Second Assistant | regex_pattern2 | 0.7 | 209 | ❌ WRONG | Wrong role (should be Draftsmen and Estimates) |

**Results:**
- ✅ Fully Correct: 2/10 (20%)
- ⚠️ Partially Correct: 2/10 (20%) - Minor issues only
- ❌ Wrong: 6/10 (60%) - Major errors

---

## Role Distribution Analysis

### Top 15 Extracted Roles

| Role | Count | Assessment |
|------|-------|------------|
| Second Assistant | 21 | ⚠️ Many incorrect - context-dependent errors |
| Writers | 16 | ⚠️ Should be singular "Writer" |
| J. L. Vanderstraaten | 14 | ❌ **FALSE** - This is a person's name |
| Assistant Surveyors | 8 | ⚠️ Should be singular |
| Government Agent | 7 | ✅ Correct |
| J. Loos | 5 | ❌ **FALSE** - This is a person's name |
| Galle | 4 | ❌ **FALSE** - This is a location |
| Gamoola | 4 | ❌ **FALSE** - This is a location |
| Private Secretary | 3 | ✅ Correct |
| Deputy ditto | 3 | ⚠️ "ditto" should be expanded |
| Assoc. Inst. C.E. | 3 | ❌ **FALSE** - This is a qualification |
| Assistant ditto | 2 | ⚠️ "ditto" should be expanded |
| Secretary | 2 | ✅ Correct |
| Kandy | 2 | ❌ **FALSE** - This is a location |
| Jaffna | 2 | ❌ **FALSE** - This is a location |

**Critical Finding:** Of the top 15 roles, **8 contain errors** (53%), including completely false roles (person names, locations, qualifications).

---

## Extraction Method Performance

### regex_pattern1 ✅ BEST PERFORMER
- **Accuracy:** ~84.3% (13 errors out of 83 extractions)
- **Strengths:** Handles standard "Role, Name, Salary" pattern well
- **Weaknesses:** Still fails on "Location, Name, Salary" patterns
- **Recommendation:** Primary method for simple patterns

### regex_pattern2 ❌ POOR
- **Accuracy:** ~35.2% (35 errors out of 54 extractions)
- **Strengths:** None identified
- **Weaknesses:** Frequently loses role context, carries forward wrong values
- **Recommendation:** Requires complete redesign or elimination

### task_pattern_extraction ❌ VERY POOR
- **Accuracy:** ~5% (21 errors out of 22 extractions)
- **Strengths:** Can handle complex patterns in theory
- **Weaknesses:** In practice, produces highly inaccurate results
- **Recommendation:** Current implementation should not be used

### task_list_extraction ❌ COMPLETE FAILURE
- **Accuracy:** 0% (16 errors out of 16 extractions)
- **Strengths:** Successfully splits comma-separated lists
- **Weaknesses:** All extractions have plural role issues
- **Recommendation:** Fix plural role assignment

---

## Common Failure Patterns

### Pattern 1: Location-Name-Salary Format
```
Source: "Kandy, T. Steele, 600l."
Expected: Name="T. Steele", Role=[from section header], Location="Kandy"
Actual: Name="T. Steele", Role="Kandy", Location="CEYLON - Central Province - [dept]"
```

### Pattern 2: Section Header Context Loss
```
Source:
  "Superintending Officers, R. A. Spearling, Assoc. Inst. C.E., 400l."
  "E. Dalton, 400l."
  "F. Vine, 400l."
Expected: All should have Role="Superintending Officers"
Actual: First correct, subsequent entries lose role context
```

### Pattern 3: Qualification Confusion
```
Source: "Office Assistant, J. A. Caley, M. Inst. C.E., 750l."
Expected: Name="J. A. Caley", Role="Office Assistant", Qualifications="M. Inst. C.E."
Actual: Name="J. A. Caley", Role="M. Inst. C.E."
```

### Pattern 4: List Continuation
```
Source:
  "J. L. Vanderstraaten, M.D., 150l."
  "F. Keyt, 150l."
Expected: Both should have Role="Medical Assistant" (from section header)
Actual: F. Keyt gets Role="J. L. Vanderstraaten"
```

---

## Recommendations

### 1. HIGH PRIORITY: Fix Location-as-Role Pattern ⚠️

**Issue:** 20+ instances where locations are extracted as roles

**Solution:**
- Maintain a location name dictionary (Kandy, Galle, Jaffna, Colombo, etc.)
- When location detected in role field, look back to section header for actual role
- Update extraction pattern to handle "Location, Name, Salary" format

**Implementation:**
```python
CEYLON_LOCATIONS = ['Kandy', 'Galle', 'Jaffna', 'Colombo', 'Trincomalee',
                    'Batticaloa', 'Matella', 'Badulla', 'Ratnapoora',
                    'Matura', 'Hambantotte', 'Manaar', 'Negombo',
                    'Morottoo', 'Gamoola', ...]

if extracted_role in CEYLON_LOCATIONS:
    actual_location = extracted_role
    actual_role = get_role_from_section_header(line_number)
```

### 2. HIGH PRIORITY: Improve Context Tracking ⚠️

**Issue:** Subsequent entries in lists lose role context

**Solution:**
- Implement section header tracking that persists across multiple lines
- When extracting person without explicit role, use last valid section header
- Add validation to detect when role looks like a person's name

**Implementation:**
- Track current department/section as state
- Validate role field doesn't match person name pattern (Initial. Surname)
- Look back up to 20 lines for last section header if needed

### 3. MEDIUM PRIORITY: Separate Qualifications from Roles

**Issue:** 4 instances where qualifications extracted as roles

**Solution:**
- Create qualification dictionary (Assoc. Inst. C.E., M. Inst. C.E., M.D., M.R.C.S.E., etc.)
- Extract qualifications to separate field
- When qualification found in role position, use actual role from pattern

**Implementation:**
```python
QUALIFICATIONS = ['Assoc. Inst. C.E.', 'M. Inst. C.E.', 'M.D.',
                  'M.R.C.S.E.', 'M.R.C.S.', 'F.R.C.S. Edin.', ...]

# In extraction logic
if extracted_role in QUALIFICATIONS:
    person['qualifications'] = extracted_role
    person['role'] = get_role_from_pattern(line)
```

### 4. MEDIUM PRIORITY: Expand "ditto" References

**Issue:** 3-5 instances where "ditto" not expanded

**Solution:**
- Track last full role/title
- When "ditto" encountered, replace with last value
- Improves data usability and clarity

### 5. LOW PRIORITY: Convert Plural Roles to Singular

**Issue:** 35 instances (20% of extractions)

**Solution:**
- Simple post-processing step: "Writers" → "Writer", "Assistant Surveyors" → "Assistant Surveyor"
- Or update list extraction to use singular form

### 6. CRITICAL: Disable or Fix Task-Based Extraction Methods

**Issue:** task_pattern_extraction (95% error) and task_list_extraction (100% error on role naming)

**Recommendation:**
- **Option A:** Disable these methods entirely until fixed
- **Option B:** Complete rewrite with better prompts and validation
- **Option C:** Use only for candidate generation, not final extraction

**Current State:** These methods are producing more harm than good

### 7. Add Validation Layer

**Implementation:**
```python
def validate_extraction(person):
    errors = []

    # Check 1: Role shouldn't be a known location
    if person['role'] in LOCATIONS:
        errors.append(f"Role '{person['role']}' is a location")

    # Check 2: Role shouldn't look like a person name
    if re.match(r'^[A-Z]\. [A-Z]', person['role']):
        errors.append(f"Role '{person['role']}' looks like a person name")

    # Check 3: Role shouldn't be a qualification
    if person['role'] in QUALIFICATIONS:
        errors.append(f"Role '{person['role']}' is a qualification")

    # Check 4: Name shouldn't be a location
    if person['name'] in LOCATIONS:
        errors.append(f"Name '{person['name']}' is a location")

    return errors
```

### 8. Re-extract with Improved System

After implementing fixes, re-run extraction and expect:
- **Target accuracy:** >85% (currently 56.6%)
- **Location-as-role errors:** 0 (currently 20)
- **Person-name-as-role errors:** 0 (currently 14)
- **Qualification-as-role errors:** 0 (currently 4)

---

## Comparison to V1 Quality

**Note:** V1 extraction data not available for direct comparison.

**Expected V1 issues** (based on typical regex-only extraction):
- Likely missed comma-separated lists entirely
- Probably lower coverage (~100-120 people vs 175)
- May have had higher accuracy on extracted records (simpler = fewer edge cases)

**V2 Hybrid Achievement:**
- ✅ Better coverage (175 people vs likely ~120 in V1)
- ❌ Lower accuracy due to more complex patterns attempted
- ⚠️ Need to balance coverage with accuracy

**Recommendation:** V2 has potential but needs significant refinement before it surpasses V1 quality.

---

## Testing Recommendations

### Before Next Production Run:

1. **Create Test Suite:**
   - 20-30 representative lines from Ceylon 1867
   - Include all error pattern types
   - Manually annotate expected outputs
   - Run extraction and measure accuracy

2. **Benchmark Targets:**
   - Overall accuracy: >85%
   - Location-as-role errors: 0%
   - False positives: <2%
   - Coverage: 160+ people (retain current level)

3. **Multi-Year Testing:**
   - Test on Ceylon 1877, 1888, 1900 to ensure consistency
   - Historical format may vary across years
   - Validate assumptions about structure

---

## Conclusion

The Ceylon 1867 extraction demonstrates that the v2 hybrid system has **significant potential** but currently suffers from **critical accuracy issues** that must be addressed before production use.

### Key Metrics:
- ✅ Coverage: Excellent (175 people from complex source)
- ❌ Accuracy: Poor (56.6% estimated)
- ⚠️ Method Performance: Highly variable (84% to 0%)

### Next Steps:
1. Implement HIGH PRIORITY fixes (location detection, context tracking)
2. Add validation layer to catch obvious errors
3. Disable or fix task-based extraction methods
4. Re-extract and re-evaluate
5. Create regression test suite
6. Only then proceed to other colonies/years

**Estimated effort to fix:** 2-3 days of development + testing

---

## Appendix: File Locations

- **Extraction File:** `/home/user/colonial_office_list/ceylon_1867_v2_fixed.json`
- **Source File:** `/home/user/colonial_office_list/output_3/1867_manual_parsed/ceylon.txt`
- **Verification Samples:** `/tmp/ceylon_samples.json`
- **Verification Results:** `/tmp/verification_results.json`

---

*End of Quality Review*
