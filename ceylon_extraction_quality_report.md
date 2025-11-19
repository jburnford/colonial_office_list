# Ceylon People Data Extraction - Quality Assessment Report

**Date:** 2025-11-19
**Analyst:** Claude Code
**Data Source:** ceylon_people_data.json (4,801 people extracted from 47 files, 1867-1946)

---

## Executive Summary

The Ceylon people data extraction has **significant quality issues** affecting accuracy and completeness. While 4,801 people were extracted with an average confidence of 0.83, the data contains:

- **HIGH FALSE NEGATIVE RATE:** Hundreds to 1,000+ people missed (estimated 30-50% miss rate)
- **MODERATE FALSE POSITIVE RATE:** ~50-100 non-people incorrectly extracted
- **HIGH ROLE EXTRACTION ERROR RATE:** 827 entries (17.2%) have "Unknown" role
- **CRITICAL NAME PARSING ERRORS:** Multiple people collapsed into single entries, locations/qualifications extracted as names

**Recommendation:** Major script improvements needed before using data for analysis.

---

## 1. FALSE NEGATIVES (People Missed)

### Issue: List Formats Not Handled

**Problem:** When multiple people are listed on a single line or across multiple lines with a shared role header, only the first person (or none) is extracted.

**Frequency:** VERY HIGH - affects dozens of list sections across all years

**Examples:**

| Year | Source Line | Content | Extracted | Missed |
|------|-------------|---------|-----------|--------|
| 1867 | Lines 172-174 | "L. F. Lee, Æ. King, G. W. Templer, R. Massie, J. W. Gibson, A. Mainwaring, A. Jumeaux. R. Reid, P. W. Conolly, A. H. Turner, A. B. Mason, T. W. R. Davids, A. Pennycuick, R. Dawson, C. A. Murray, F. C. Fisher, C. E." | 1 (R. Reid) | 15 Writers |
| 1920 | Line 331 | "†R. E. Harvey, M. K. T. Sandys, †H. H. Gardiner, P. Saravanamuttu, R. S. V. Poulier, E. W. Kannangara, T. D. Perera, S. Phillipson, R. Jones Bateman." | 0 | 9 Cadets |
| 1930 | Multiple | "Grade II, P. C. Fernando, D. J. Unwin, H. H. Jansen" | 1 (all 3 in one entry) | 2 people |

**Root Cause:**
- Pattern 3 regex (`r'^([A-Z][^,]+?),\s+(\d+[,\d]*l\.?)(?:\s|$)'`) only matches single "Name, Salary" format
- Pattern 4 (`r'^([A-Z]\.\s+[A-Z][a-z]+)(?:,|\.|$)'`) only extracts first name from lists
- No logic to handle comma-separated lists of names under a shared role header

**Impact:**
- 1867: Extracted 182 people, likely should be 250-300+
- 1920: Extracted 166 people, likely should be 200-250+
- **Estimated total missed:** 800-1,500+ people across all years (30-50% miss rate)

**Suggested Fix:**
1. Add logic to detect list headers ("Writers, commencing at...", "Cadets, commencing at...")
2. For lines following list headers, split on commas and extract each name
3. Apply the header role to all names in the list
4. Handle multi-line lists that continue until next section header

---

## 2. FALSE POSITIVES (Non-People Extracted as People)

### Issue A: Professional Qualifications as Names

**Frequency:** 17 instances

**Examples:**
- "A.M.I.C.E." extracted as name 10 times in 1910, 7 times in 1911
- Full string shows these are qualifications after real names: "J. A. Balfour, A.M.I.C.E., 475l."

**Root Cause:** Pattern matching captures qualification as a separate person when it follows a name

### Issue B: Location Names as People

**Frequency:** ~10-15 instances

**Examples:**
| Year | Name Extracted | Role | Full String |
|------|----------------|------|-------------|
| 1867 | Colombo | Master Attendant | "Master Attendant, Colombo, 600l." |
| 1867 | Kandy | Unknown | "Kandy, 300l." |
| 1867 | Nuwera Ellia | Unknown | (location name) |
| 1867 | Wohendahl Church, Colombo | Unknown | (church name) |
| 1867 | Kandy Districts | Unknown | (administrative region) |

**Root Cause:**
- Pattern 2 treats "Role, Location, Name, Salary" but sometimes location appears where name is expected
- `_looks_like_name()` validation too permissive - doesn't filter well-known location names

### Issue C: Placeholder Text as Names

**Frequency:** ~20-30 instances

**Examples:**
| Name | Count | Context |
|------|-------|---------|
| Ditto | 4 | "Ditto, 500l. to 600l. (vacant)" |
| (vacant) | 10+ | Various vacant positions |
| Grade I | Multiple | Grade designations |
| Grade II | Multiple | Grade designations |

**Root Cause:** Extraction doesn't filter placeholder/administrative text

**Suggested Fix:**
1. Add location names to skip list in `_looks_like_name()`: ["Colombo", "Kandy", "Jaffna", "Galle", etc.]
2. Add qualifications to skip list: ["A.M.I.C.E.", "M.D.", "F.R.C.S.", etc.]
3. Add placeholder text to skip patterns: "Ditto", "vacant", "Grade I", "Grade II", "acting"
4. Improve validation to reject single-word capitalized entries that don't look like surnames

---

## 3. ROLE EXTRACTION ERRORS

### Issue: 17.2% of Entries Have "Unknown" Role

**Frequency:** 827 out of 4,801 entries (17.2%)

**Example Patterns:**

#### Pattern A: Simple Name-Salary Lines
Many entries have clear roles in the full string but extracted as "Unknown":

| Name | Full String | Should Be |
|------|-------------|-----------|
| G. Vane | "G. Vane, Treasurer." | Treasurer |
| J. Winzer | "J. Winzer, 650l." | Assistant Surveyor (from context) |
| Captain Oldfield | "Captain Oldfield, 400l." | Superintending Officer (from context) |

#### Pattern B: "Ditto" Roles Not Resolved
"Ditto" appears in role field but is not resolved to the actual role from previous line:

| Year | Name | Role | Full String |
|------|------|------|-------------|
| 1867 | J. Swan | Second ditto | "Second ditto, J. Swan, 600l." |
| 1914 | Ditto | Unknown | "Ditto, 500l. to 600l. (vacant)" |

**Root Cause:**
- Pattern 3 matches "Name, Salary" but has no way to infer role from context
- No logic to track and apply "ditto" references
- Department tracking doesn't help when role is "ditto" within same department

**Impact:**
- Reduces data usefulness for role-based analysis
- 827 entries require manual review/correction

**Suggested Fix:**
1. Track "last_role" variable within each department section
2. When role is "ditto" or "Unknown", inherit from last_role
3. For Pattern 3 matches, try to infer role from:
   - Section header if within 5 lines
   - Previous person's role if in same department
4. Add post-processing step to resolve "ditto" references

---

## 4. NAME PARSING ISSUES

### Issue A: Multiple People in Single Name Field

**Frequency:** ~50-100 instances (CRITICAL ISSUE)

**Examples:**

| Year | Name Field | Role | Full String |
|------|------------|------|-------------|
| 1907 | H. O. Fox, Rs. 11,250; J. M. Davies, 425l.; W. E. Wait | Assistant Officers | "Assistant Officers, H. O. Fox, Rs. 11,250; J. M. Davies, 425l.; W. E. Wait, 350l." |
| 1909 | E. B. Alexander, Rs. 9,562-50; C. L. Tranchell, 500l.; F. G. Tyrrell | Superintendents | "Superintendents, E. B. Alexander, Rs. 9,562-50; C. L. Tranchell, 500l.; F. G. Tyrrell, 550l. to 700l.; H. Thornhill, 475l.; G. F. Forrest." |
| 1910 | J. B. Misso, 300l.; S. Davies, 300l.; W. A. Coradin | Assistant Engineers | "Assistant Engineers, J. B. Misso, 300l.; S. Davies, 300l.; W. A. Coradin, 300l." |
| 1918 | A. L. Cook*, 500l.; C. W. Lund, 500l.; V. W. Goss* | Assistant Engineers | (multiple people with salaries) |

**Impact:**
- 3-5 people collapsed into single entry
- Impossible to analyze these individuals
- Significantly undercounts actual people extracted

**Root Cause:** Pattern matching captures entire list as "name" when format is "Role, Name1 Salary; Name2 Salary; Name3 Salary"

### Issue B: Honorifics and Titles Incorrectly Included

**Examples:**
- "&c., Sir H. G. Robinson, Knt." (should be "Sir H. G. Robinson")
- "etc., W. J. Sendall, B.A." (should be "W. J. Sendall")

**Root Cause:** Pattern doesn't strip "&c." or "etc." prefix before extracting name

### Issue C: Role/Description Prefixes in Name

**Examples:**
- "and Joint Commissioner of Requests of Jaffna, J. Morphey" (should be "J. Morphey")
- "Sanskrit & Pali, G. P. Malasekera" (should be "G. P. Malasekera")
- "Grade II, P. C. Fernando, D. J. Unwin, H. H. Jansen" (should be 3 separate people)
- "Royal College, L. H. W. Sampson" (should be "L. H. W. Sampson")

**Root Cause:** Pattern captures too much text before the actual name

### Issue D: Location Included in Name

**Examples:**
- "Colombo, G. W. Paterson" (should be "G. W. Paterson", location=Colombo)
- "Kandy, C. M. Drew" (should be "C. M. Drew", location=Kandy)
- "ditto, B. De Waas" (should be "B. De Waas")

**Root Cause:** Pattern 2 (`Role, Location, Name, Salary`) sometimes captures location as part of name

### Issue E: Footnote Markers Not Stripped

**Examples:**
- "†J. L. Whitty"
- "A. J. Bamford*"
- "†R. E. Harvey"

**Count:** ~20-30 instances

**Root Cause:** No cleaning step to remove †, *, ‡ markers

### Issue F: Salary/Numbers Included in Name

**Examples:**
- "300l.; W. W. A. Wall" (salary prefix)
- "1,050l. to 1,200l., vacant, F. J. S. Turner"

**Suggested Fix:**
1. Add name cleaning function to:
   - Strip prefixes: "&c.", "etc.", "ditto", location names
   - Remove footnote markers: †, *, ‡
   - Extract actual name from "Role, Name" or "Location, Name" patterns
   - Remove salary ranges and "(vacant)" text
2. Detect and split semicolon-separated lists: "Name1 Salary; Name2 Salary; Name3 Salary"
3. Add validation: reject names containing numbers/salaries
4. Improve Pattern 2 to correctly separate role/location/name components

---

## 5. DEPARTMENT ASSIGNMENT ERRORS

### Issue: People Assigned as Departments

**Frequency:** ~20-30 instances

**Examples:**

| Year | Name | Department | Issue |
|------|------|------------|-------|
| 1867 | M. Coomaraswamy | "P. W. Braybrooke, Government Agent, Central Province" | Person name in dept field |
| Various | Multiple | Contains commas and person names | Full person entries stored as departments |

**Root Cause:**
- `is_department_header()` not strict enough
- Captures lines with person names as department headers

**Impact:**
- Incorrect hierarchical relationships
- Department field polluted with non-department values

**Suggested Fix:**
1. Make department header detection stricter
2. Require department names to NOT contain salary amounts
3. Require department names to match known patterns only
4. Validate that department doesn't look like "Person, Role" pattern

---

## 6. DATA QUALITY STATISTICS

### Confidence Score Distribution
- **High confidence (0.9):** 3,974 entries (82.8%)
- **Low confidence (0.5):** 827 entries (17.2%)

This correlates exactly with "Unknown" role count - all low confidence entries have unknown roles.

### People Per Year Analysis

**Anomalies detected:**

| Year | Count | Issue |
|------|-------|-------|
| 1899 | 0 | No people extracted (likely parsing failure) |
| 1933 | 0 | No people extracted (likely parsing failure) |
| 1946 | 0 | No people extracted (likely parsing failure) |
| 1867 | 182 | Too high for first year (but missing ~100 from lists) |
| 1877-1900 | 4-48 | Very low counts suggest major extraction failures |

**Trend:** Later years (1920s) have better extraction (200+ people) but still miss list formats.

### Duplicate Entries

| Name-Year | Count | Issue |
|-----------|-------|-------|
| G. Vane (1867) | 3 | Same person extracted multiple times |
| A.M.I.C.E. (1910) | 10 | Qualification extracted as person |

**Estimated duplicates:** ~20-30 entries

---

## 7. PRIORITIZED IMPROVEMENT RECOMMENDATIONS

### CRITICAL (Must Fix Before Use)

1. **Fix List Format Extraction (FALSE NEGATIVES)**
   - Priority: CRITICAL
   - Impact: +800-1,500 people
   - Effort: High
   - Implement comma-separated name parsing
   - Detect and process list headers ("Writers, commencing at...")
   - Handle multi-line lists

2. **Fix Multiple-People-in-One-Name (DATA CORRUPTION)**
   - Priority: CRITICAL
   - Impact: Affects ~50-100 entries, each containing 3-5 people
   - Effort: Medium
   - Detect and split semicolon-separated entries
   - Create separate person records for each

3. **Fix False Positives (NON-PEOPLE)**
   - Priority: HIGH
   - Impact: ~50-100 spurious entries
   - Effort: Low
   - Add comprehensive skip list (locations, qualifications, placeholders)
   - Improve name validation

### HIGH (Significantly Improves Quality)

4. **Resolve "Unknown" Roles**
   - Priority: HIGH
   - Impact: 827 entries (17.2%)
   - Effort: Medium
   - Implement role inheritance/"ditto" resolution
   - Infer roles from context

5. **Clean Name Fields**
   - Priority: HIGH
   - Impact: All entries
   - Effort: Medium
   - Strip prefixes/suffixes (&c., etc., †, *, ‡)
   - Remove location/role text from names
   - Standardize name format

### MEDIUM (Quality of Life)

6. **Fix Department Assignment**
   - Priority: MEDIUM
   - Impact: ~20-30 entries
   - Effort: Low
   - Stricter department header detection
   - Validate department names

7. **Investigate Zero-Extraction Years**
   - Priority: MEDIUM
   - Impact: 3 years (1899, 1933, 1946)
   - Effort: Low
   - Review source files
   - Fix parsing for these specific years

8. **Remove Duplicates**
   - Priority: MEDIUM
   - Impact: ~20-30 entries
   - Effort: Low
   - Post-processing deduplication
   - Identify same person extracted multiple times

### LOW (Nice to Have)

9. **Improve Confidence Scores**
   - Priority: LOW
   - Impact: Better metadata
   - Effort: Medium
   - More granular confidence levels
   - Factor in validation checks

---

## 8. ESTIMATED DATA QUALITY METRICS

Based on analysis:

| Metric | Estimate | Notes |
|--------|----------|-------|
| **True Positives** | ~4,700 | Correctly extracted people |
| **False Positives** | ~100 | Non-people extracted |
| **False Negatives** | ~1,000-1,500 | People missed |
| **Precision** | 98% | TP / (TP + FP) |
| **Recall** | 76-83% | TP / (TP + FN) |
| **F1 Score** | 0.86-0.90 | Harmonic mean |
| **Data Usability** | MEDIUM | Significant issues prevent reliable analysis |

---

## 9. SAMPLE FIXES NEEDED

### Example 1: Writers Section (1867, lines 172-174)

**Current Extraction:**
- 1 person: "R. Reid" (role: Unknown)

**Should Extract:**
```
L. F. Lee (Writer)
Æ. King (Writer)
G. W. Templer (Writer)
R. Massie (Writer)
J. W. Gibson (Writer)
A. Mainwaring (Writer)
A. Jumeaux (Writer)
R. Reid (Writer)
P. W. Conolly (Writer)
A. H. Turner (Writer)
A. B. Mason (Writer)
T. W. R. Davids (Writer)
A. Pennycuick (Writer)
R. Dawson (Writer)
C. A. Murray (Writer)
F. C. Fisher (Writer)
```
**Result:** 16 people instead of 1

### Example 2: Multiple People in One Entry (1907)

**Current Extraction:**
- Name: "H. O. Fox, Rs. 11,250; J. M. Davies, 425l.; W. E. Wait"
- Role: "Assistant Officers"

**Should Extract:**
```
1. H. O. Fox (Assistant Officer) - Rs. 11,250
2. J. M. Davies (Assistant Officer) - 425l
3. W. E. Wait (Assistant Officer) - 350l
```
**Result:** 3 people instead of 1

### Example 3: False Positive (1867)

**Current Extraction:**
- Name: "Colombo"
- Role: "Master Attendant"

**Should Extract:**
- Name: [No person - this is a location]
- OR if there's a person: Name: "[Unknown/Vacant]", Location: "Colombo"

**Result:** Remove false positive or extract correctly

---

## 10. CONCLUSION

The Ceylon people data extraction requires **major improvements** before the data can be reliably used for analysis. The most critical issues are:

1. **Missing 30-50% of people** due to list format handling failures
2. **Multiple people collapsed into single entries**, making individual analysis impossible
3. **17% of entries have unknown roles**, limiting analytical value

**Recommended Next Steps:**
1. Implement critical fixes (list parsing, name splitting)
2. Re-run extraction on all files
3. Validate sample of results against source files
4. Perform statistical comparison of counts between versions
5. Manual review of 10-20 random entries per year for quality assurance

**Estimated Effort:**
- Critical fixes: 2-3 days development + 1 day testing
- Re-extraction: 1-2 hours
- Validation: 1 day
- **Total:** ~4-5 days to production-quality data

---

## Appendix A: Files Analyzed

- ceylon_people_data.json (4,801 people, 57,672 lines)
- extract_ceylon_people.py (extraction script, 365 lines)
- output_3/1867_manual_parsed/ceylon.txt (sample source)
- output_3/1920_manual_parsed/CEYLON.md (sample source)

## Appendix B: Analysis Methods

1. Statistical analysis using jq queries
2. Pattern detection for common errors
3. Manual comparison against source files
4. Cross-validation of confidence scores vs. error types
5. Frequency analysis of anomalous entries

---

**Report prepared by:** Claude Code (AI Assistant)
**Analysis date:** 2025-11-19
**Total analysis time:** ~30 minutes
**Entries analyzed:** 4,801 total, ~200 manually inspected
