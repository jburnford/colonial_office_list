# Priority Fixes for Knowledge Graph Extracts

**Generated**: 2025-11-17
**Urgency**: These issues should be addressed before production KG construction

---

## 🚨 CRITICAL (Fix Immediately)

### 1. Hong Kong 1900: Impossible Historical Dates
**File**: `output_2/1900_manual_parsed/HONG_KONG.md`
**Lines**: 127-128
**Issue**: Financial data for years 1839-1840, but Hong Kong wasn't British until 1841

**Current (WRONG)**:
```
| 1839 | $1,845,549 | $1,833,718 | 6,500,869 | 12,389,321 |
| 1840 | $1,655,220 | $1,615,850 | 6,904,919 | 13,076,236 |
```

**Should be**:
```
| 1889 | $1,845,549 | $1,833,718 | 6,500,869 | 12,389,321 |
| 1890 | $1,655,220 | $1,615,850 | 6,904,919 | 13,076,236 |
```

**Verification**: Tonnage values (6,500,869 and 12,389,321) match 1899 file's 1889 data exactly
**Root cause**: OCR digit confusion (8→3)
**Impact**: Creates historically impossible data that could corrupt temporal knowledge graphs

---

## ⚠️ MODERATE (Fix Soon)

### 2. Jamaica 1910: Incomplete Extraction
**File**: `output_2/1910_manual_parsed/JAMAICA.md`
**Issue**: File ends at line 247 after Privy Council section
**Missing**: ~60% of Civil Establishment content (Colonial Secretary's Office, Public Works, Railways, Agriculture, Audit, etc.)
**Impact**: Incomplete data for 1910 Jamaica
**Action**: Complete extraction from OCR source

### 3. Malta 1921: Location Name Duplication
**File**: `output_2/1921_manual_parsed/MALTA.md`
**Line**: 401
**Issue**: "St. Julian's and St. Julian's, S. F. Darmanin, M.D. †"
**Root cause**: OCR text duplication
**Action**: Determine correct second location name from OCR

---

## 📋 MINOR (Review When Convenient)

### 4. Hong Kong 1900: Duplicate Legislative Council Entry
**File**: `output_2/1900_manual_parsed/HONG_KONG.md`
**Issue**: "Dr. Ho Kai, E. R. Belilos, C.M.G." listed twice in Legislative Council
**Impact**: Inflates council member count
**Action**: Remove duplicate

### 5. Hong Kong 1900: Malformed Salary
**File**: `output_2/1900_manual_parsed/HONG_KONG.md`
**Issue**: Police 1st Clerk salary shows "$1,1200 to $1,800"
**Should be**: "$1,200 to $1,800"
**Root cause**: OCR extra digit
**Action**: Correct to $1,200

### 6. Hong Kong 1900: Name Initial Inconsistency
**File**: `output_2/1900_manual_parsed/HONG_KONG.md`
**Issue**: Same person as "C. P. Chater" and "O. P. Chater"
**Root cause**: OCR character confusion (C↔O)
**Action**: Verify correct initials and normalize

### 7. Ceylon 1867: Colonial Secretary Name Variant
**File**: `output_2/1867_manual_parsed/CEYLON.md`
**Issue**: "W. C. Gibson" (2×) vs "W. G. Gibson" (1×)
**Likely correct**: W. G. Gibson (from salary record)
**Action**: Normalize to consistent initials

### 8. Fiji 1928: Paragraph Duplication
**File**: `output_2/1928_manual_parsed/FIJI.md`
**Lines**: 67-106
**Issue**: History and Climate sections repeat verbatim
**Root cause**: OCR scanning artifact
**Action**: Remove duplicate paragraphs

### 9. Malta 1921: A. Cremona Duplicate (Investigate)
**File**: `output_2/1921_manual_parsed/MALTA.md`
**Lines**: 385, 407
**Issue**: A. Cremona, M.D. appears as Medical Officer for Gozo AND District Medical Officer for Zabbar
**Possible**: Legitimate dual appointment
**Action**: Verify against OCR if this is one person with two positions or duplicate entry

---

## ✅ VALIDATED AS CORRECT (No Action Needed)

The following were flagged for review but are **historically accurate**:

- **Historical spellings** (SOOTRA, Keshin, Abdal Kute): Period-accurate, preserve as-is
- **Aden 1923 page header insertion**: OCR artifact but doesn't affect data quality
- **Ceylon 1867 truncated name "C. E."**: OCR truncation in source
- **Multiple appointments**: Gibraltar 1915 personnel holding 2+ roles across departments is legitimate

---

## Summary

| Priority | Count | Estimated Effort |
|----------|-------|------------------|
| Critical | 1 | 2 minutes |
| Moderate | 2 | 30-60 minutes |
| Minor | 7 | 10-30 minutes |
| **Total** | **10 issues** | **~1-2 hours** |

**Files affected**: 5 out of 8 reviewed (62.5%)
**Most issues**: Hong Kong 1900 (5 issues)
**Clean files**: Aden 1923, Barbados 1948, Nigeria 1930, Gibraltar 1915

---

## Recommended Fix Order

1. **Hong Kong 1900 date fix** (critical, 2 min)
2. **Jamaica 1910 completion** (moderate, 30-60 min)
3. **Malta 1921 location duplication** (moderate, 5 min)
4. **Batch minor fixes** for Hong Kong 1900 (30 min)
5. **Review remaining minor issues** (30 min)

**Total time investment**: ~1-2 hours to achieve 100% quality across all reviewed files
