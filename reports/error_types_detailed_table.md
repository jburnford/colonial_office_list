# Complete Error Type Breakdown

**Total Errors:** 28,150 across 61 files

---

## Category A: Safe Python Automation (100% Confident)

| # | Error Type | Count | % of Total | % of Category | Fix Method | Risk |
|---|------------|-------|------------|---------------|------------|------|
| 1 | type_string_expected | 1,122 | 3.99% | 88.2% | `str()` conversion | None |
| 2 | missing_year_metadata | 72 | 0.26% | 5.7% | Extract from filename | None |
| 3 | string_pattern_mismatch | 66 | 0.23% | 5.2% | Regex normalization | None |
| 4 | type_number_expected | 6 | 0.02% | 0.5% | Parse to int/float | None |
| 5 | missing_source_directory | 6 | 0.02% | 0.5% | Infer from path | None |
| **SUBTOTAL** | **Category A** | **1,272** | **4.52%** | **100%** | **Python script** | **Minimal** |

**Implementation:**
```python
# Fully automated, no human review needed
# Estimated time: 4-8 hours
# Expected success: 98-100% (1,246-1,272 fixes)
```

---

## Category B: LLM Agent with High Confidence (85-95% Confident)

| # | Error Type | Count | % of Total | % of Category | Fix Method | Confidence |
|---|------------|-------|------------|---------------|------------|------------|
| 1 | invalid_enum_values | 4,060 | 14.42% | 83.3% | LLM semantic mapping | 90% |
| 2 | invalid_type_enum | 668 | 2.37% | 13.7% | LLM semantic mapping | 90% |
| 3 | unreasonably_high_salary | 59 | 0.21% | 1.2% | LLM validation | 85% |
| 4 | string_too_short | 46 | 0.16% | 0.9% | LLM inference or "Unknown" | 80% |
| 5 | invalid_relationship_type_enum | 40 | 0.14% | 0.8% | LLM semantic mapping | 90% |
| **SUBTOTAL** | **Category B** | **4,873** | **17.31%** | **100%** | **LLM agent** | **85-95%** |

**Implementation:**
```python
# LLM-driven with automated validation
# Estimated time: 2-4 days
# Expected success: 85-95% (4,142-4,629 fixes)
# Human review: 5-10% of cases (~250-500 errors)
```

**Example Fixes:**
- `type: "Province"` → `type: "colony"` (semantic mapping)
- `relationship_type: "CONTROLLED_BY"` → `"GOVERNED_BY"` (closest match)
- `salary: 50000000` → `salary: 5000` (decimal correction)

---

## Category C: LLM Agent with Human Review (50-85% Confident)

| # | Error Type | Count | % of Total | % of Category | Fix Method | Confidence |
|---|------------|-------|------------|---------------|------------|------------|
| 1 | missing_location | 876 | 3.11% | 60.1% | LLM contextual inference | 70% |
| 2 | invalid_salary_amount | 427 | 1.52% | 29.3% | LLM format correction | 60% |
| 3 | value_must_be_positive | 118 | 0.42% | 8.1% | LLM value inference | 70% |
| 4 | model_type_error | 26 | 0.09% | 1.8% | LLM restructuring | 50% |
| 5 | missing_longitude | 9 | 0.03% | 0.6% | Geocoding | 60% |
| 6 | missing_latitude | 1 | 0.00% | 0.1% | Geocoding | 60% |
| **SUBTOTAL** | **Category C** | **1,457** | **5.18%** | **100%** | **LLM + review** | **50-85%** |

**Implementation:**
```python
# LLM-proposed fixes with mandatory human review
# Estimated time: 3-5 days
# Expected success: 50-85% (728-1,238 fixes)
# Human review: 100% of proposals, ~40-50% need manual correction
```

**Example Fixes:**
- Missing location for "Railway Station" near "Lagos" → Infer "Lagos"
- Salary "£500 per annum" → Parse to `{amount: 500, currency: "GBP"}`
- Missing coordinates for "Kingston, Jamaica" → Geocode to lat/lon

---

## Category D: Requires Re-extraction (<50% Confident for Automation)

| # | Error Type | Count | % of Total | % of Category | Issue | Re-extraction Success |
|---|------------|-------|------------|---------------|-------|----------------------|
| 1 | type_list_expected | 14,949 | 53.10% | 72.8% | Data as string, not array | 90-95% |
| 2 | missing_required_fields | 5,395 | 19.17% | 26.2% | Core fields absent | 90-95% |
| 3 | missing_relationship_ids | 150 | 0.53% | 0.7% | IDs not linked | 90-95% |
| 4 | missing_other_fields | 54 | 0.19% | 0.3% | Various required fields | 90-95% |
| **SUBTOTAL** | **Category D** | **20,548** | **72.99%** | **100%** | **Structural issues** | **90-95%** |

**Why Re-extraction:**
- Automated fixes unreliable (<50% confidence)
- Data likely truncated or improperly parsed during initial extraction
- Risk of creating invalid data if "fixed" programmatically
- Re-extraction with improved methodology more cost-effective

**Implementation:**
```python
# Complete re-extraction with improved prompts and validation
# Estimated time: 4-8 weeks
# Expected success: 90-95% (18,493-19,520 fixes)
# Strategy: Incremental batches of 5 files, validate before proceeding
```

**Root Causes to Address:**
1. Schema not clearly communicated in extraction prompts
2. LLM token limits causing truncation
3. Insufficient validation during extraction
4. List/array fields extracted as comma-separated strings

---

## Summary Statistics

### By Category

| Category | Name | Errors | % | Confidence | Expected Fixes | Effort |
|----------|------|--------|---|------------|----------------|--------|
| **A** | Python Automation | 1,272 | 4.5% | 100% | 1,246-1,272 | 4-8 hrs |
| **B** | LLM High Confidence | 4,873 | 17.3% | 85-95% | 4,142-4,629 | 2-4 days |
| **C** | LLM + Review | 1,457 | 5.2% | 50-85% | 728-1,238 | 3-5 days |
| **D** | Re-extraction | 20,548 | 73.0% | 90-95% | 18,493-19,520 | 4-8 wks |
| **TOTAL** | **All Categories** | **28,150** | **100%** | **87-95%** | **24,609-26,659** | **12-15 wks** |

### Cumulative Impact

| After Phase | Errors Fixed | % Fixed | Remaining | Validation Success Rate |
|-------------|--------------|---------|-----------|------------------------|
| Initial State | 0 | 0% | 28,150 | 6.5% |
| Phase 1 | 1,246-1,272 | 4.4-4.5% | 26,878-26,904 | ~10% |
| Phase 2 | 5,388-5,901 | 19.1-21.0% | 22,249-22,762 | ~25% |
| Phase 3 | 6,116-7,139 | 21.7-25.4% | 21,011-22,034 | ~30% |
| Phase 4 | 24,609-26,659 | 87.4-94.7% | 1,491-3,541 | 85-95% |

---

## Error Type Examples

### Category A Examples (Python)
```json
// type_string_expected
"year": 1905  →  "year": "1905"

// missing_year_metadata (from filename: 1905_extracted.json)
"metadata": {}  →  "metadata": {"year": 1905}

// string_pattern_mismatch
"year": "1905-1906"  →  "year": "1905"
```

### Category B Examples (LLM High Confidence)
```json
// invalid_enum_values
"type": "Province"  →  "type": "colony"
"type": "Fort"  →  "type": "settlement"

// invalid_relationship_type_enum
"relationship_type": "CONTROLLED_BY"  →  "GOVERNED_BY"
```

### Category C Examples (LLM + Review)
```json
// missing_location (infer from context)
{
  "name": "Railway Station",
  "location": null,
  "nearby": ["Lagos"]
}
→
{
  "name": "Railway Station",
  "location": "Lagos",  // NEEDS REVIEW
  "nearby": ["Lagos"]
}

// invalid_salary_amount (parse complex format)
"salary": "£500 per annum"  →  "salary": 500, "currency": "GBP"
```

### Category D Examples (Re-extraction)
```json
// type_list_expected (fundamental structure wrong)
"positions": "Governor, Lieutenant-Governor"
→ NEEDS RE-EXTRACTION
→ "positions": ["Governor", "Lieutenant-Governor"]

// missing_required_fields (core data absent)
{
  "metadata": {},  // missing year, source_directory
  "relationships": [...]
}
→ NEEDS RE-EXTRACTION
```

---

**Last Updated:** 2025-11-17
**Full Roadmap:** `/home/user/colonial_office_list/reports/error_categorization_and_roadmap.md`
