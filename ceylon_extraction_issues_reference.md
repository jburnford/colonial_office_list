# Ceylon Extraction Issues - Quick Reference Guide

This document provides specific examples with source file line numbers for quick verification.

---

## FALSE NEGATIVES - Missed People

### Issue 1: Writers List (1867)

**Source:** `/home/user/colonial_office_list/output_3/1867_manual_parsed/ceylon.txt`

**Lines 171-174:**
```
Writers, commencing at 200l. per annum.
L. F. Lee, Æ. King, G. W. Templer, R. Massie,
J. W. Gibson, A. Mainwaring, A. Jumeaux.
R. Reid, P. W. Conolly, A. H. Turner, A. B. Mason, T. W. R. Davids, A. Pennycuick, R. Dawson, C. A. Murray, F. C. Fisher, C. E.
```

**Expected:** 16 people (all Writers at 200l. per annum)
**Extracted:** 1 person (R. Reid with role "Unknown")
**Missing:** 15 Writers

**GitHub:** https://github.com/jburnford/colonial_office_list/blob/main/output_3/1867_manual_parsed/ceylon.txt#L171

---

### Issue 2: Cadets List (1920)

**Source:** `/home/user/colonial_office_list/output_3/1920_manual_parsed/CEYLON.md`

**Lines 330-331:**
```
Cadets, commencing at 300l. per annum:—
†R. E. Harvey, M. K. T. Sandys, †H. H. Gardiner, P. Saravanamuttu, R. S. V. Poulier, E. W. Kannangara, T. D. Perera, S. Phillipson, R. Jones Bateman.
```

**Expected:** 9 Cadets (all at 300l. per annum)
**Extracted:** 0 people
**Missing:** 9 Cadets

**GitHub:** https://github.com/jburnford/colonial_office_list/blob/main/output_3/1920_manual_parsed/CEYLON.md#L330

---

## FALSE POSITIVES - Non-People Extracted

### Issue 3: Professional Qualifications (1910)

**Extracted 10 times as a person:**
- Name: "A.M.I.C.E."
- Role: varies

**Examples from data:**
```json
{
  "name": "A.M.I.C.E.",
  "role": "R. F. Morris",
  "full_string": "R. F. Morris, A.M.I.C.E., 500l."
}
```

**Problem:** A.M.I.C.E. is a professional qualification (Associate Member of the Institution of Civil Engineers), not a person.

---

### Issue 4: Location Names (1867)

**Source:** Line 258

**Extracted:**
```json
{
  "name": "Colombo",
  "role": "Master Attendant",
  "full_string": "Master Attendant, Colombo, 600l.",
  "line_number": 258
}
```

**Problem:** "Colombo" is a city, not a person. The Master Attendant position at Colombo appears to be vacant or the name is on the next line.

---

### Issue 5: Placeholder Text (1914, 1915)

**Extracted:**
```json
{
  "name": "Ditto",
  "role": "Unknown",
  "full_string": "Ditto, 500l. to 600l. (vacant)."
}
```

**Problem:** "Ditto" is a placeholder, not a person name. Position is vacant.

---

## ROLE EXTRACTION ERRORS

### Issue 6: Role in Full String But Not Extracted (1867)

**Source:** Lines 139, 149, 180

**Extracted:**
```json
{
  "name": "G. Vane",
  "role": "Unknown",
  "full_string": "G. Vane, Treasurer.",
  "line_number": 139
}
```

**Problem:** Role is clearly "Treasurer" in the full_string, but extracted as "Unknown".

**Note:** G. Vane appears 3 times:
- Line 139: Executive Council member (shows as "G. Vane, Treasurer")
- Line 149: Legislative Council member (shows as "G. Vane, Treasurer")
- Line 180: Actually listed as Treasurer with salary (correctly extracted)

---

### Issue 7: "Ditto" Not Resolved (1867)

**Source:** Line 168

**Extracted:**
```json
{
  "name": "J. Swan",
  "role": "Second ditto",
  "full_string": "Second ditto, J. Swan, 600l."
}
```

**Context:** Previous line (167) was:
```
Principal Assistant, F. B. Templer, 1,000l.
```

**Problem:** "Second ditto" should be resolved to "Second Assistant" or "Assistant Colonial Secretary"

---

## NAME PARSING ERRORS

### Issue 8: Multiple People in Single Entry (1907)

**Extracted:**
```json
{
  "name": "H. O. Fox, Rs. 11,250; J. M. Davies, 425l.; W. E. Wait",
  "role": "Assistant Officers",
  "full_string": "Assistant Officers, H. O. Fox, Rs. 11,250; J. M. Davies, 425l.; W. E. Wait, 350l."
}
```

**Problem:** This is 3 different people collapsed into one entry.

**Should be:**
1. H. O. Fox (Assistant Officer, Rs. 11,250)
2. J. M. Davies (Assistant Officer, 425l)
3. W. E. Wait (Assistant Officer, 350l)

---

### Issue 9: Honorific Prefix Error (1867)

**Source:** Line 161

**Extracted:**
```json
{
  "name": "&c., Sir H. G. Robinson, Knt.",
  "role": "Governor",
  "full_string": "Governor, &c., Sir H. G. Robinson, Knt., 7,000l."
}
```

**Problem:** "&c." (abbreviation for "et cetera") should not be part of the name.

**Should be:** "Sir H. G. Robinson" or "Sir H. G. Robinson, Knt."

---

### Issue 10: Role Prefix in Name (1934)

**Extracted:**
```json
{
  "name": "Sanskrit & Pali, G. P. Malasekera, M.A., Ph.D. (London)",
  "role": "Lecturer in Sinhalese",
  "full_string": "Lecturer in Sinhalese, Sanskrit & Pali, G. P. Malasekera, M.A., Ph.D. (London), 650l."
}
```

**Problem:** "Sanskrit & Pali" is part of the role description, not the name.

**Should be:**
- Name: "G. P. Malasekera"
- Role: "Lecturer in Sinhalese, Sanskrit & Pali"

---

### Issue 11: Location in Name (1867)

**Extracted:**
```json
{
  "name": "Colombo, G. W. Paterson",
  "role": "Assistant ditto ditto",
  "full_string": "Assistant ditto ditto, Colombo, G. W. Paterson, 450l."
}
```

**Problem:** "Colombo" is the location, not part of the name.

**Should be:**
- Name: "G. W. Paterson"
- Location: "Colombo"
- Role: "Assistant Government Agent"

---

### Issue 12: Footnote Markers (1920)

**Extracted:**
```json
{
  "name": "†J. L. Whitty",
  "role": "Second Assistant Accountant",
  "full_string": "Second Assistant Accountant, †J. L. Whitty, 500l.; W. E. Granier (acting), 400l."
}
```

**Problem:** "†" is a footnote marker (indicates person is on war service, leave, etc.), should be stripped.

**Should be:** "J. L. Whitty" with metadata indicating footnote marker present

---

## DEPARTMENT ASSIGNMENT ERRORS

### Issue 13: Person Name as Department (1867)

**Extracted:**
```json
{
  "name": "M. Coomaraswamy",
  "role": "Unknown",
  "department": "P. W. Braybrooke, Government Agent, Central Province",
  "full_string": "M. Coomaraswamy."
}
```

**Problem:** Department field contains a person's name and role, not a department name.

**Context:** This appears in the Legislative Council listing where M. Coomaraswamy is a council member. "P. W. Braybrooke, Government Agent, Central Province" is another council member listed earlier, not a department.

---

## DATA QUALITY ISSUES BY YEAR

### Years with Zero Extractions

| Year | Files Processed | People Extracted | Issue |
|------|----------------|------------------|-------|
| 1899 | Yes | 0 | Complete extraction failure |
| 1933 | Yes | 0 | Complete extraction failure |
| 1946 | Yes | 0 | Complete extraction failure |

**Action needed:** Review source files for these years to determine why extraction failed completely.

---

### Years with Suspiciously Low Counts

| Year | People Extracted | Expected | Gap |
|------|-----------------|----------|-----|
| 1877 | 18 | ~150-200 | Missing ~130-180 |
| 1878 | 37 | ~150-200 | Missing ~110-160 |
| 1888 | 4 | ~150-200 | Missing ~145-195 |
| 1889 | 6 | ~150-200 | Missing ~140-190 |
| 1890 | 6 | ~150-200 | Missing ~140-190 |
| 1894 | 4 | ~150-200 | Missing ~145-195 |
| 1896 | 4 | ~150-200 | Missing ~145-195 |
| 1898 | 4 | ~150-200 | Missing ~145-195 |
| 1900 | 4 | ~150-200 | Missing ~145-195 |

**Pattern:** Years 1877-1900 have consistently low extraction rates, suggesting systematic parsing issues with source file formatting from this era.

---

## VALIDATION CHECKLIST

Use this checklist when reviewing fixes:

### For Each Source File:
- [ ] Count list headers ("Writers, commencing at...", "Cadets, commencing at...")
- [ ] Manually count people in lists
- [ ] Compare manual count vs. extraction count
- [ ] Target: >95% extraction rate

### For Random Sample of Entries:
- [ ] Name field contains only person name (no roles, locations, salaries)
- [ ] No multiple people in single entry
- [ ] No footnote markers in name
- [ ] Role field is meaningful (not "Unknown" or "Ditto")
- [ ] Department field contains department name (not person names)
- [ ] No locations or qualifications extracted as people

### Statistical Validation:
- [ ] Total people >6,000 (currently 4,801, missing ~1,000-1,500)
- [ ] "Unknown" role <5% (currently 17.2%)
- [ ] False positives <1% (currently ~2%)
- [ ] Average confidence >0.90 (currently 0.83)
- [ ] No years with zero extractions

---

## QUICK FIX VERIFICATION

After implementing fixes, run these checks:

```bash
# Count Unknown roles (should be <5%)
jq -r '.people[] | select(.role == "Unknown") | .role' ceylon_people_data.json | wc -l

# Count entries with semicolons in name (should be 0)
jq -r '.people[] | select(.name | contains(";"))' ceylon_people_data.json | wc -l

# Count location names extracted as people (should be 0)
jq -r '.people[] | select(.name == "Colombo" or .name == "Kandy" or .name == "Ditto")' ceylon_people_data.json | wc -l

# Count professional qualifications as names (should be 0)
jq -r '.people[] | select(.name == "A.M.I.C.E." or .name == "M.D.")' ceylon_people_data.json | wc -l

# Check confidence distribution
jq '.people | group_by(.confidence) | map({confidence: .[0].confidence, count: length})' ceylon_people_data.json

# People per year (no zeros)
jq '.metadata.people_per_year' ceylon_people_data.json
```

---

**Last Updated:** 2025-11-19
**Related:** ceylon_extraction_quality_report.md
