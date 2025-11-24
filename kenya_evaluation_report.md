# Independent Quality Evaluation Report
## Kenya Colonial Office List Extraction

**Evaluator:** Independent Quality Agent
**Date:** 2025-11-23
**Dataset:** kenya_all_years_v1.json
**Sample Size:** 25 records (randomly sampled from 10,325 total)
**Coverage:** 1922-1963 (15 years represented)

---

## Executive Summary

**Overall Quality Score: 49.2/100** ⚠️ **SIGNIFICANT QUALITY ISSUES FOUND**

The Kenya extraction suffers from **severe systematic errors** that make approximately **88% of sampled records unusable or requiring significant correction**. Only **3 out of 25 records (12%)** were extracted perfectly.

### Critical Issues Identified:

1. **Non-Person Extractions (24%)** - 6 of 25 records are not people at all
2. **Name Contamination (32%)** - 8 of 25 records have departments/locations in name field
3. **Role Context Inheritance (64%)** - 16 of 25 records have wrong roles from other sections
4. **Multiple People per Record (8%)** - 2 records contain multiple people
5. **Confidence Score Inaccuracy** - 6 records rated 0.9 confidence have major errors

---

## Detailed Analysis by Error Category

### 1. Non-Person Extractions (6 records, 24%)

These records extracted text that is not a person's name at all:

#### Example 1: Academic Qualification as Person
- **Extracted:** "B.A. (1st class Hons.) (Lond.)"
- **Year:** 1931, Confidence: 0.8
- **Source Line 270:** `Inspector of Schools, H. L. Bradshaw, G. E. Webb, B.A. (Hons.) (Oxon.), R. H. W. Wisdom, B.A. (1st class Hons.) (Lond.), 600l. to 720l.`
- **Issue:** The qualification of R. H. W. Wisdom was extracted as a separate person
- **Correct:** Should be part of "R. H. W. Wisdom" record

#### Example 2: Descriptive Text as Person
- **Extracted:** "most important towns are St. John (Antigua)"
- **Year:** 1948, Confidence: 0.75
- **Source Lines 732-734:**
```
**Chief Towns**

The most important towns are St. John (Antigua), 11,000; Basseterre (St. Kitts), 12,000.
```
- **Issue:** Extracted descriptive text from geography section
- **Correct:** This entire section should be ignored - not a personnel listing

#### Example 3: Table Fragment as Person
- **Extracted:** "K.C.M.G.) |"
- **Year:** 1948, Confidence: 0.7
- **Source:** `| 1873 | H. T. Irving, C.M.G. (later Sir H. T. Irving, K.C.M.G.) |`
- **Issue:** Extracted table formatting and post-nominal letters as a person
- **Correct:** The person is "H. T. Irving", not the qualification

#### Example 4: Descriptive Prefix as Person
- **Extracted:** "Grade I—V. de V. Allen; J. H. Daly; E. B. Dove; Capt. J. H. Frank"
- **Year:** 1950, Confidence: 0.9 ⚠️
- **Source:** `Superintendents and Assistant Superintendents, Grade I—V. de V. Allen; J. H. Daly; E. B. Dove; Capt. J. H. Frank, M.C.; F. A. Martin, M.C.; Commdr. W. R. Fenton, R.N. (retd.); G. C. M. Phillips; G. H. C. Thacker; R. H. Timmis; G. M. Young. £550–1,025.`
- **Issue:**
  - Included "Grade I" classification in name
  - Combined 4 people into one record
  - Ignored 6 additional people in the same list
- **Correct:** Should be 10 separate records, each without the "Grade I" prefix

#### Example 5: Appointment Description as Person
- **Extracted:** "Members appointed for 4 years—J. L. Riddoch"
- **Year:** 1960, Confidence: 0.75
- **Source:** `Members appointed for 4 years—J. L. Riddoch, C.B.E.; Dr. S. D. Karve, O.B.E.; W. Kimemia, M.B.E.`
- **Issue:** Included appointment description in name field
- **Correct:** Should be "J. L. Riddoch" only (and separate records for the other 2 people)

#### Example 6: Job Title as Person
- **Extracted:** "Permanent Secretaries—G. J. Ellerton"
- **Year:** 1960, Confidence: 0.75
- **Source:** `Permanent Secretaries—G. J. Ellerton, M.B.E.; T. Neil, T.D.; R. O. Hennings, C.M.G.; A. J. Walker; R. E. Luyt, D.C.M.; T. C. Colchester, C.M.G.; J. J. Adie; V. A. Maddison; C. F. Atkins; M. N. Evans; J. L. H. Webster.`
- **Issue:** Included job title in name field
- **Correct:** Should be "G. J. Ellerton" only (plus 10 separate records for others)

---

### 2. Name Contamination (8 records, 32%)

These records have department names, locations, or role descriptors incorrectly included in the name field:

#### Example 1: Institution in Name
- **Extracted:** "Kabete Technical and Trade School—A. E. Talbot"
- **Year:** 1950, Confidence: 0.9 ⚠️ (HIGH CONFIDENCE BUT WRONG)
- **Source:** `Principal, Kabete Technical and Trade School—A. E. Talbot, M.B.E. £970–1,320.`
- **Correct Name:** "A. E. Talbot"
- **Correct Role:** "Principal, Kabete Technical and Trade School"

#### Example 2: Department in Name
- **Extracted:** "Mines and Surveys—G. J. Robbins"
- **Year:** 1946, Confidence: 0.9 ⚠️
- **Source:** `Commissioner for Lands, Mines and Surveys—G. J. Robbins, C.B.E.`
- **Correct Name:** "G. J. Robbins"
- **Correct Role:** "Commissioner for Lands, Mines and Surveys"

#### Example 3: Department in Name (repeated issue)
- **Extracted:** "Police Department—C. Campbell"
- **Year:** 1958, Confidence: 0.9 ⚠️
- **Source:** `Civil Secretary, Police Department—C. Campbell, O.B.E.`
- **Correct Name:** "C. Campbell"
- **Correct Role:** "Civil Secretary, Police Department"
- **Note:** Same person appears in 1961 with identical error

#### Example 4: Location in Name
- **Extracted:** "Nairobi Extra-Provincial District—R. A. Wilkinson"
- **Year:** 1963, Confidence: 0.9 ⚠️
- **Source:** `Officer-in-Charge, Nairobi Extra-Provincial District—R. A. Wilkinson, O.B.E.`
- **Correct Name:** "R. A. Wilkinson"
- **Correct Role:** "Officer-in-Charge, Nairobi Extra-Provincial District"

---

### 3. Role Context Inheritance Issue (16 records, 64%)

**This is the most pervasive systematic error.** The extractor assigns roles from completely different sections or previous context rather than the actual role from the source.

#### Example 1: Forester Misidentified
- **Person:** E. A. Holyoak (1930)
- **Extracted Role:** "9 European Clerk"
- **Extracted Department:** "Forestry"
- **Source:** `Foresters, J. L. Moon, A. Wye, A. M. Cooper, W. Munro, G. A. Hoult, R. R. Stock, G. Fairbairn, H. H. G. Deakin, T. A. Angus, H. McIntyre, A. C. Sprunt, E. A. Holyoak, H. H. Anstey, G. R. Gibbons, J. H. Echalaz, B. M. Fuller, 300l. to 500l.`
- **Correct Role:** "Forester"
- **Analysis:** The role "9 European Clerk" appears nowhere in the source and seems inherited from elsewhere

#### Example 2: Senior Medical Officer Misidentified
- **Person:** C. J. Wilson (1923)
- **Extracted Role:** "Assistant District and Resident Commissioners"
- **Extracted Department:** "Medical"
- **Source:** `Senior Medical Officers, F. L. Henderson, G. R. H. Chell, J. Pugh, C. J. Wilson, M.C., N. P. Jewell, M.C., 800l. by 25l. to 900l.`
- **Correct Role:** "Senior Medical Officer"
- **Analysis:** Role is from Provincial Administration section, not Medical where person actually appears

#### Example 3: Land Assistant Misidentified
- **Person:** C. K. Mortimer (1925)
- **Extracted Role:** "Senior Inspector of Schools (vacant)"
- **Extracted Department:** "Lands"
- **Source:** `Land Assistants, H. W. Borrow, H. R. Harris, R. Elliott, C. K. Mortimer, M. Solomons, 400l. by 25l. to 500l.`
- **Correct Role:** "Land Assistant"
- **Analysis:** Role is from Education department, not Lands where person actually appears

#### Example 4: Senior Medical Officer Misidentified Again
- **Person:** T. H. Massey (1925)
- **Extracted Role:** "Registrar-General's Department"
- **Extracted Department:** "Medical"
- **Source:** `Senior Medical Officers, J. Pugh, N. P. Jewell, M.C., A. D. J. B. Williams, O.B.E., T. H. Massey, M.C., 800l. by 25l. to 900l.`
- **Correct Role:** "Senior Medical Officer"
- **Analysis:** The role "Registrar-General's Department" is not a role but a department name from elsewhere

#### Example 5: District Officer Misidentified
- **Person:** G. R. B. Brown (1932)
- **Extracted Role:** "Finger-Print Officer"
- **Extracted Department:** "Provincial Administration"
- **Source:** `District Officers, C. H. Adams, F. M. Lamb, T. D. Butler, H. E. Welby, S. H. Fazan, O.B.E., C. B. Thompson, G. M. Castle-Smith, G. H. C. Boulderson, M. R. R. Vidal, H. G. Evans, H. H. Trafford, R. W. Lambert, A. A. Seldon, E. B. Hoaking, O.B.E., E. J. Waddington, O.B.E., V. G. Glenday, O.B.E., J. M. Silvester, S. O. V. Hodge, J. L. B. L. Llewellin, J. W. K. Poase, J. W. E. Wightman, R. Pedraza, C. J. W. Lydekker, C. J. J. T. Barton, H. Izard, C. Tomkinson, S. V. Cooke, H. E. L. Brailsford, J. D. McKean, J. G. Hopkins, W. S. Marchant, H. B. Sharpe, K. L. Hunter, W. Slade-Hawkins, F. G. Jennings, Lieut. H. E. Lambert, H. G. Oldfield, D. O. Brumage, J. G. Hamilton Ross, R.N.R., Lieut.-Col. E. L. B. Anderson, D.S.O., Major J. V. Dawson, D.S.O., Capt. E. G. S. Tisdall, M.C., Major C. E. V. Buxton, M.C., Capt. C. T. Davenport, Lieut. I. R. Gillespie, Capt. W. R. Kidd, M.C., Capt. G. B. Rimington, M.C., Major A. W. Sutcliffe, D.S.O., M.C., Capt. C. G. Usher, M.C., Major B. W. Bond, M.C., Lieut. D. Storra-Fox, Capt. J. H. Clive, Capt. V. M. McKeag, A. N. Ballard, C. W. Hayes-Sadler, Lieut. C. A. Cornell, E. D. Emley, K. G. Lindsay, L. A. Weaving, V. G. Cole, H. L. G. Gurney, Sir H. G. Elphinstone, Bt., S. R. Lowder, Lt.-Comdr. D. McKay, R.N. (Retired), Capt. F. D. Hislop, Major J. L. Willcocks, D.S.O., M.C., G. Reece, H. E. Bader, W. A. Perreau, R. T. Lambert, J. H. B. Murphy, G. B. Stooke, R.N., C. P. G. Norman, H. A. Carr, G. R. B. Brown, ...475l. to 920l.`
- **Correct Role:** "District Officer"
- **Analysis:** "Finger-Print Officer" is from a different section entirely

**Pattern:** In 64% of sampled records, the role field contains information from a different section of the document, often from many lines away from where the person actually appears. This systematic error makes the role data largely unreliable.

---

### 4. Multiple People in One Record (2 records, 8%)

#### Example 1: Four Judges Combined
- **Extracted:** "Q.C.; J. S. Templeton; B. R. Miles; A. D. Farrell"
- **Year:** 1958
- **Source:** `Puisne Judges—G. B. W. Rudd; C. P. Connell; T. H. Mayers, Q.C.; J. L. MacDuff, M.C.; E. A. J. Edmonds; J. P. Murphy, Q.C.; J. S. Templeton; B. R. Miles; A. D. Farrell.`
- **Issue:** Captured last 4 people (including previous person's qualification) as one record
- **Correct:** Should be 9 separate records
- **People missed:** G. B. W. Rudd, C. P. Connell, T. H. Mayers, J. L. MacDuff, E. A. J. Edmonds

#### Example 2: Ten Prison Officers as One (already discussed in Non-Person section)
- Contains 10 people but extracted as 1 record with 4 names

---

### 5. Confidence Score Inaccuracy (6 records with 0.9 confidence but major errors)

The extractor assigned **high confidence scores (0.9) to records with obvious errors:**

| Record | Issue | Confidence | Should Be |
|--------|-------|------------|-----------|
| Kabete Technical and Trade School—A. E. Talbot | Name contamination | 0.9 | 0.4 |
| Mines and Surveys—G. J. Robbins | Name contamination | 0.9 | 0.4 |
| Grade I—V. de V. Allen; J. H. Daly... | Multiple people + contamination | 0.9 | 0.1 |
| Police Department—C. Campbell | Name contamination | 0.9 | 0.4 |
| Nairobi Extra-Provincial District—R. A. Wilkinson | Name contamination | 0.9 | 0.4 |

**Analysis:** The confidence scoring mechanism does not accurately reflect extraction quality. Records with obvious contamination and formatting issues are marked as high confidence.

---

## Perfect Extractions (3 records, 12%)

Only these 3 records were extracted correctly:

1. **E. A. Shelver (1922)** - Valuer-Keeper, Customs
   - Source: `Valuer-Keeper, E. A. Shelver, 250l. by 15l. to 350l.`
   - ✓ Name correct, ✓ Role correct, ✓ Salary extracted

2. **G. H. Allison (1931)** - Chief Quantity Surveyor, Survey
   - Source: `Chief Quantity Surveyor, G. H. Allison, F.S.I., 1,120l.`
   - ✓ Name correct, ✓ Role correct, ✓ Qualifications extracted, ✓ Salary extracted

3. **R. A. W. Procter (1937)** - Senior Medical Officer, Medical
   - Source: `Senior Medical Officers, R. A. W. Procter, M.C., M.A., B.Ch. (Cantab.), M.R.C.S. (Eng.), L.R.C.P. (Lond.), D.T.M. & H. (Lond.), D.P.H. (Cantab.), R. P. Cormack, ...`
   - ✓ Name correct, ✓ Role correct, ✓ Qualifications extracted

**Pattern:** The extractor works best with "pattern1" format: `Role, Name Qualifications, Salary.`

---

## Quality Metrics Summary

| Metric | Value | Target | Status |
|--------|-------|--------|--------|
| **Overall Quality Score** | **49.2/100** | 90+ | ❌ **FAIL** |
| Perfect Extractions | 12.0% | 95%+ | ❌ **FAIL** |
| Name Accuracy | 76.0% | 98%+ | ❌ **FAIL** |
| Role Accuracy | 36.0% | 95%+ | ❌ **FAIL** |
| Confidence Accuracy | N/A | Should correlate with quality | ❌ **FAIL** |
| Non-Person Rate | 24.0% | <1% | ❌ **FAIL** |
| Contamination Rate | 32.0% | <2% | ❌ **FAIL** |

### Calculation Methodology

Quality scores assigned per record:
- Perfect extraction: 100 points
- Role context issue only: 70 points (name correct but role wrong)
- Name contamination: 40 points (recoverable with cleanup)
- Multiple people: 30 points (needs splitting)
- Non-person name: 0 points (critical failure)

**Overall Quality = Sum of individual scores / Total records = 1,230 / 25 = 49.2**

---

## Comparison: Claimed vs. Actual Confidence

The metadata claims "73.6% medium confidence due to role context inheritance" but the actual issues are far more severe:

### Claimed Issues:
- Medium confidence due to role context inheritance

### Actual Issues Found:
- ❌ 24% complete failures (non-person extractions)
- ❌ 32% name contamination requiring cleanup
- ❌ 64% role context inheritance (confirmed)
- ❌ 8% multiple people in one record
- ❌ Confidence scores are unreliable (high scores on bad data)

**The claimed issue (role context) is confirmed, but many additional critical issues were not mentioned.**

---

## Systematic Error Analysis

### Root Causes Identified:

1. **Pattern Matching Issues:**
   - The extractor uses multiple patterns (kenya_pattern1, kenya_name_list, kenya_semicolon_list, kenya_name_salary)
   - "pattern1" works well (high accuracy when used)
   - "name_list" and "name_salary" patterns have severe issues
   - Semicolon-based splitting can separate qualifications from names

2. **Context Window Problems:**
   - Role information is not properly associated with the current line
   - The extractor appears to "remember" roles from earlier in the document
   - No validation that the role matches the current section

3. **Lack of Validation:**
   - No check if extracted name looks like a person's name
   - No check if name contains prefixes like "Department—" or "Grade—"
   - No check if name contains multiple people (semicolons)
   - Confidence scores don't reflect actual quality

4. **Department Assignment Issues:**
   - Department is assigned at file/section level
   - When a person appears in wrong section (e.g., table from different colony)
   - They get assigned to that colony/department

---

## Impact Assessment

### Data Usability by Category:

| Category | Records | Usability | Action Needed |
|----------|---------|-----------|---------------|
| Perfect | 3 (12%) | ✓ Ready to use | None |
| Role issues only | 5 (20%) | ⚠️ Partial | Fix roles |
| Name contamination | 8 (32%) | ⚠️ Partial | Clean names |
| Multiple people | 2 (8%) | ❌ Unusable | Re-extract |
| Non-person | 6 (24%) | ❌ Unusable | Delete |
| **Total Unusable** | **8 (32%)** | ❌ | **Delete/Re-extract** |
| **Needs Correction** | **14 (56%)** | ⚠️ | **Fix fields** |

### Estimated Dataset Quality:

If the sample is representative of the full dataset:
- **10,325 total records**
- ~1,238 (12%) are perfect ✓
- ~3,304 (32%) should be deleted ❌
- ~5,782 (56%) need correction ⚠️

**Effective usable data: ~1,238 records (12% of claimed total)**

---

## Recommendations

### Immediate Actions Required:

1. **❌ DO NOT USE this dataset in production** - Quality is below acceptable threshold

2. **Review extraction logic:**
   - Fix role context inheritance (most critical issue)
   - Add validation for person name format
   - Add detection for contaminated names (regex for "—", "Department", etc.)
   - Implement multi-person detection and splitting
   - Fix confidence scoring to reflect actual quality

3. **Add filtering rules:**
   ```python
   # Reject if name contains:
   - "—" followed by uppercase (Department/Location prefix)
   - Starts with "Grade", "Members", "Permanent", "most", "The"
   - Contains "| Year |" or markdown table syntax
   - Contains semicolons (multiple people)
   - Is entirely uppercase + punctuation (like "K.C.M.G.) |")
   - Contains words like "Department", "School", "District" before "—"
   ```

4. **Improve role extraction:**
   ```python
   # Role should be:
   - From the SAME line or previous line only
   - Not from a different department section
   - Validated against a list of known roles
   - Marked with lower confidence if context unclear
   ```

5. **Re-run extraction with fixes** on all Kenya files

6. **Verify high-confidence records** - current 0.9 confidence records have 50%+ error rate

### Long-term Improvements:

1. **Implement quality checks:**
   - Name format validation (regex patterns)
   - Role-department consistency checks
   - Duplicate detection (same person in multiple years)
   - Cross-reference with known colonial officials

2. **Add extraction modes:**
   - Conservative mode: Only extract high-certainty records
   - Comprehensive mode: Extract all with quality flags
   - Manual review queue for medium-confidence records

3. **Improve pattern matching:**
   - Learn from the 3 perfect extractions (pattern1 format)
   - Develop separate handlers for list formats vs. individual entries
   - Better handling of qualifications vs. names

4. **Add manual verification:**
   - Flag records for human review
   - Build training set from verified records
   - Improve patterns based on corrections

---

## Conclusion

The Kenya extraction has **severe quality issues** that make it unsuitable for use without major corrections. The **49.2/100 quality score** reflects:

- ✓ The core extraction technology can work (12% perfect rate)
- ❌ Systematic errors affect 88% of records
- ❌ Role context inheritance affects 64% of records (confirmed)
- ❌ Name contamination affects 32% of records (not previously identified)
- ❌ 24% of records are not people at all (critical issue)
- ❌ Confidence scores are unreliable

**Recommended Action:** **REJECT** this extraction and re-run with improved logic addressing the identified issues.

---

## Appendix: Complete Sample Verification Results

[Full list of 25 samples with individual verdicts available in kenya_sample_25.json]

**Sample Distribution:**
- 1920s: 7 records
- 1930s: 7 records
- 1940s: 3 records
- 1950s: 3 records
- 1960s: 5 records

**Extraction Methods Used:**
- kenya_pattern1: 8 records (37.5% of which are perfect)
- kenya_name_list: 12 records (0% perfect)
- kenya_semicolon_list: 2 records (0% perfect)
- kenya_name_salary: 3 records (0% perfect)

**Key Finding:** The "pattern1" extraction method has significantly higher accuracy than other methods.

---

*Report prepared by Independent Quality Evaluation Agent*
*Evaluation completed: 2025-11-23*
