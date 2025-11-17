# Error Categorization and Remediation Roadmap

**Analysis Date:** 2025-11-17
**Total Errors:** 28,150
**Files Affected:** 61 files (across 3 periods: 1867-1900, 1901-1930, 1931-1966)

---

## Executive Summary

This report categorizes all 28,150 validation errors across 61 knowledge graph extraction files and provides a phased remediation roadmap. Errors are categorized by fixability and confidence level, ranging from fully automated Python corrections to cases requiring complete re-extraction.

### Key Findings

- **73.0%** of errors require re-extraction (structural/missing data issues)
- **17.3%** can be fixed by LLM with high confidence (semantic mapping)
- **5.2%** require LLM with human review (complex inference)
- **4.5%** can be safely automated with Python (type conversions)

---

## Error Distribution by Period

| Period | Files | Errors | Avg Errors/File | Success Rate |
|--------|-------|--------|-----------------|--------------|
| 1867-1900 | 14 | 2,302 | 164.4 | 7.1% |
| 1901-1930 | 22 | 24,000 | 1,090.9 | 9.1% |
| 1931-1966 | 26 | 1,848 | 71.1 | 3.8% |
| **TOTAL** | **62** | **28,150** | **453.2** | **6.5%** |

---

## Complete Error Categorization Table

| Error Type | Count | % of Total | Category | Confidence | Method |
|------------|-------|------------|----------|------------|--------|
| type_list_expected | 14,949 | 53.10% | **D** | <50% | Re-extraction |
| missing_required_fields | 5,395 | 19.17% | **D** | <50% | Re-extraction |
| invalid_enum_values | 4,060 | 14.42% | **B** | 90% | LLM semantic mapping |
| type_string_expected | 1,122 | 3.99% | **A** | 100% | Python automation |
| missing_location | 876 | 3.11% | **C** | 70% | LLM + human review |
| invalid_type_enum | 668 | 2.37% | **B** | 90% | LLM semantic mapping |
| invalid_salary_amount | 427 | 1.52% | **C** | 60% | LLM + human review |
| missing_relationship_ids | 150 | 0.53% | **D** | <50% | Re-extraction |
| value_must_be_positive | 118 | 0.42% | **C** | 70% | LLM + human review |
| missing_year_metadata | 72 | 0.26% | **A** | 100% | Python automation |
| string_pattern_mismatch | 66 | 0.23% | **A** | 100% | Python automation |
| unreasonably_high_salary | 59 | 0.21% | **B** | 85% | LLM validation |
| missing_other_fields | 54 | 0.19% | **D** | <50% | Re-extraction |
| string_too_short | 46 | 0.16% | **B** | 80% | LLM field population |
| invalid_relationship_type_enum | 40 | 0.14% | **B** | 90% | LLM semantic mapping |
| model_type_error | 26 | 0.09% | **C** | 50% | LLM + human review |
| missing_longitude | 9 | 0.03% | **C** | 60% | LLM geocoding |
| type_number_expected | 6 | 0.02% | **A** | 100% | Python automation |
| missing_source_directory | 6 | 0.02% | **A** | 100% | Python automation |
| missing_latitude | 1 | 0.00% | **C** | 60% | LLM geocoding |

---

## Category A: Safe Python Automation (100% Confident)

**Total Errors:** 1,272 (4.52%)
**Expected Success Rate:** 98-100%
**Risk:** Minimal - purely mechanical transformations

### Error Types

1. **type_string_expected** (1,122 errors)
   - **Issue:** Field contains non-string value (likely number or object)
   - **Fix:** Convert to string using `str()` function
   - **Example:** `year: 1905` → `year: "1905"`

2. **missing_year_metadata** (72 errors)
   - **Issue:** Metadata year field missing
   - **Fix:** Extract from filename pattern `YYYY_extracted.json`
   - **Example:** `1905_extracted.json` → `metadata.year = 1905`

3. **string_pattern_mismatch** (66 errors)
   - **Issue:** Year field doesn't match pattern `^\d{4}$`
   - **Fix:** Normalize year format, strip extra characters
   - **Example:** `"1905-1906"` → `"1905"` or `"c. 1905"` → `"1905"`

4. **type_number_expected** (6 errors)
   - **Issue:** Numeric field contains string
   - **Fix:** Parse and convert to number if valid
   - **Example:** `count: "123"` → `count: 123`

5. **missing_source_directory** (6 errors)
   - **Issue:** Metadata missing source directory
   - **Fix:** Infer from file path
   - **Example:** File path → `source_directory: "knowledge_graph_extracts"`

### Implementation Approach

```python
def fix_category_a_errors(data, filename):
    # 1. Fix type_string_expected
    # Convert all non-string fields to strings where required

    # 2. Fix missing_year_metadata
    year = extract_year_from_filename(filename)
    data['metadata']['year'] = year

    # 3. Fix string_pattern_mismatch
    # Normalize year formats using regex

    # 4. Fix type_number_expected
    # Parse numeric strings to numbers

    # 5. Fix missing_source_directory
    data['metadata']['source_directory'] = "knowledge_graph_extracts"

    return data
```

**Estimated Effort:** 4-8 hours
**Expected Error Reduction:** 1,272 errors (4.5%)

---

## Category B: LLM Agent with High Confidence (85%+ Confident)

**Total Errors:** 4,873 (17.31%)
**Expected Success Rate:** 85-95%
**Risk:** Low - clear semantic mappings with validation

### Error Types

1. **invalid_enum_values** (4,060 errors)
   - **Issue:** Values don't match allowed enum options
   - **Fix:** LLM maps invalid values to closest valid enum
   - **Example:**
     - `type: "Province"` → `type: "colony"`
     - `type: "Town"` → `type: "town"`
   - **Validation:** Check edit distance, semantic similarity

2. **invalid_type_enum** (668 errors)
   - **Issue:** Place/institution type doesn't match schema
   - **Fix:** Similar to #1, semantic mapping
   - **Example:** `type: "Fort"` → `type: "settlement"`

3. **invalid_relationship_type_enum** (40 errors)
   - **Issue:** Relationship type not in allowed list
   - **Fix:** Map to closest valid relationship type
   - **Example:** `"CONTROLLED_BY"` → `"GOVERNED_BY"`

4. **unreasonably_high_salary** (59 errors)
   - **Issue:** Salary exceeds reasonable threshold
   - **Fix:** LLM validates context, corrects if obvious error
   - **Example:** `salary: 50000000` → `salary: 5000` (likely decimal error)
   - **Human review:** Flag if unclear

5. **string_too_short** (46 errors)
   - **Issue:** Required field is empty string
   - **Fix:** LLM infers from context or marks as "Unknown"
   - **Example:** Empty title → Infer from position/context or use "Unknown"

### Implementation Approach

```python
def fix_category_b_errors_with_llm(data, error_list):
    for error in error_list:
        if error.type == "invalid_enum":
            # Use LLM to map value to valid enum
            prompt = f"Map '{error.value}' to one of: {error.valid_options}"
            corrected = llm.complete(prompt)
            # Validate mapping has high confidence
            if corrected.confidence > 0.85:
                apply_fix(data, error.path, corrected.value)
            else:
                flag_for_review(error)
    return data
```

**Estimated Effort:** 2-4 days
**Expected Error Reduction:** 4,140-4,630 errors (14.7-16.4%)
**Human Review Required:** ~5-10% of fixes (~250-500 cases)

---

## Category C: LLM Agent with Human Review (50-85% Confident)

**Total Errors:** 1,457 (5.18%)
**Expected Success Rate:** 50-85%
**Risk:** Medium - requires verification and may have false positives

### Error Types

1. **missing_location** (876 errors)
   - **Issue:** Infrastructure/institution missing location field
   - **Fix:** LLM infers from entity name, description, or related entities
   - **Example:** "Railway Station" near "Lagos" → location: "Lagos"
   - **Confidence:** 70% (needs validation)

2. **invalid_salary_amount** (427 errors)
   - **Issue:** Salary format or value problematic
   - **Fix:** LLM corrects format, validates reasonableness
   - **Example:** `salary: "£500 per annum"` → `salary: 500, currency: "GBP"`
   - **Confidence:** 60% (historical context needed)

3. **value_must_be_positive** (118 errors)
   - **Issue:** Numeric field has zero or negative value
   - **Fix:** LLM infers correct value from context
   - **Confidence:** 70% (depends on field type)

4. **model_type_error** (26 errors)
   - **Issue:** Complex structural validation failure
   - **Fix:** LLM restructures data to match schema
   - **Confidence:** 50% (may need re-extraction)

5. **missing_longitude/latitude** (10 errors)
   - **Issue:** Coordinates incomplete
   - **Fix:** Geocode location name to get coordinates
   - **Confidence:** 60% (historical accuracy concerns)

### Implementation Approach

```python
def fix_category_c_errors_with_review(data, error_list):
    fixes = []
    for error in error_list:
        # Generate proposed fix with LLM
        proposed_fix = llm.propose_fix(error, context=data)

        # Flag for human review
        fixes.append({
            'error': error,
            'proposed_fix': proposed_fix,
            'confidence': proposed_fix.confidence,
            'requires_review': proposed_fix.confidence < 0.85
        })

    # Generate review report
    create_review_spreadsheet(fixes)
    return fixes
```

**Estimated Effort:** 3-5 days
**Expected Error Reduction:** 728-1,238 errors (2.6-4.4%)
**Human Review Required:** 100% review, ~40-50% may need manual correction

---

## Category D: Requires Re-extraction (<50% Confident)

**Total Errors:** 20,548 (73.00%)
**Expected Success Rate:** N/A (requires source re-processing)
**Risk:** High for automated fixes - better to re-extract

### Error Types

1. **type_list_expected** (14,949 errors)
   - **Issue:** Field should be list/array but is string or single value
   - **Fix:** Re-extract with corrected schema understanding
   - **Example:** `positions: "Governor"` → `positions: ["Governor"]`
   - **Why re-extract:** Data may be truncated, incomplete, or improperly parsed

2. **missing_required_fields** (5,395 errors)
   - **Issue:** Core schema fields completely absent
   - **Fix:** Re-extract ensuring all required fields populated
   - **Example:** Missing `entities` object entirely
   - **Why re-extract:** Indicates fundamental extraction failure

3. **missing_relationship_ids** (150 errors)
   - **Issue:** Relationship records missing source_id or target_id
   - **Fix:** Re-extract relationship data with proper ID linking
   - **Why re-extract:** Cannot infer IDs reliably without source context

4. **missing_other_fields** (54 errors)
   - **Issue:** Various required fields missing
   - **Fix:** Re-extract with complete schema validation
   - **Why re-extract:** Indicates incomplete extraction process

### Re-extraction Strategy

1. **Root Cause Analysis**
   - Review extraction prompts for schema clarity
   - Check if certain years/formats caused systematic issues
   - Identify LLM token limits or context window problems

2. **Improved Extraction Process**
   - Update extraction prompts with explicit schema requirements
   - Add validation during extraction (not just after)
   - Use structured output mode or JSON schema validation
   - Process in smaller chunks if token limits exceeded

3. **Prioritization**
   - Focus on high-value years first (e.g., 1901-1930 period)
   - Consider if some files are less critical

**Estimated Effort:** 4-8 weeks (depending on automation level)
**Expected Error Reduction:** 20,548 errors (73.0%)

---

## Phased Remediation Roadmap

### Phase 1: Python Safe Corrections (Week 1)

**Goal:** Eliminate all mechanically-fixable errors
**Errors Addressed:** 1,272 (Category A)
**Effort:** 4-8 hours
**Success Rate:** 98-100%

**Actions:**
1. Develop Python script for Category A fixes
2. Test on sample files (5-10 files)
3. Execute batch correction
4. Validate results
5. Commit corrected files

**Deliverables:**
- `scripts/fix_category_a.py`
- Validation report showing before/after error counts
- Updated extraction files

**Risk Mitigation:**
- Backup original files before modification
- Validate JSON structure after changes
- Run audit again to confirm fixes

---

### Phase 2: LLM High-Confidence Fixes (Weeks 1-2)

**Goal:** Apply semantic corrections with validation
**Errors Addressed:** 4,873 (Category B)
**Effort:** 2-4 days
**Success Rate:** 85-95%
**Expected Reduction:** 4,140-4,630 errors

**Actions:**
1. Develop LLM-based correction agent
2. Implement confidence thresholds
3. Process errors with confidence > 85%
4. Generate review list for confidence < 85%
5. Human review of flagged cases (~250-500)
6. Apply approved fixes

**Deliverables:**
- `scripts/fix_category_b_llm.py`
- Review spreadsheet for low-confidence cases
- Updated extraction files
- Confidence score report

**Risk Mitigation:**
- Sample validation on 10% of fixes
- Human review for confidence < 85%
- Rollback mechanism for problematic fixes
- Track all changes with version control

---

### Phase 3: LLM with Human Review (Weeks 2-3)

**Goal:** Address complex inference cases
**Errors Addressed:** 1,457 (Category C)
**Effort:** 3-5 days
**Success Rate:** 50-85%
**Expected Reduction:** 728-1,238 errors

**Actions:**
1. Generate LLM-proposed fixes for all Category C errors
2. Create structured review interface/spreadsheet
3. Human review session (all 1,457 cases)
4. Apply approved fixes
5. Document patterns for future extraction improvement

**Deliverables:**
- `reports/category_c_review.csv` (all proposed fixes)
- Human review decisions
- Updated extraction files
- Pattern analysis document

**Risk Mitigation:**
- 100% human review required
- Two-reviewer system for complex cases
- Conservative approach: "when in doubt, leave it out"
- Document rationale for decisions

---

### Phase 4: Strategic Re-extraction (Weeks 4-12)

**Goal:** Re-extract files with structural issues
**Errors Addressed:** 20,548 (Category D)
**Effort:** 4-8 weeks
**Success Rate:** 90-95% (on re-extraction)
**Expected Reduction:** 18,493-19,520 errors

**Actions:**
1. Analyze root causes of extraction failures
2. Update extraction prompts and methodology
3. Implement in-process validation
4. Prioritize high-value/high-error files:
   - 1901-1930 period (24,000 errors, 22 files)
   - High-error files from other periods
5. Re-extract in batches with validation
6. Compare results to original extractions

**Deliverables:**
- `docs/extraction_methodology_v2.md`
- Updated extraction prompts
- `scripts/extract_with_validation.py`
- Re-extracted knowledge graph files
- Comparative analysis report

**Risk Mitigation:**
- Validate against original sources
- Keep original extractions for comparison
- Incremental approach (5 files at a time)
- Quality gates before proceeding to next batch

---

## Expected Cumulative Error Reduction

| Phase | Errors Fixed | Cumulative % Fixed | Remaining Errors | Success Rate |
|-------|--------------|-------------------|------------------|--------------|
| **Start** | 0 | 0.0% | 28,150 | 6.5% |
| **Phase 1** | 1,272 | 4.5% | 26,878 | ~10% |
| **Phase 2** | 4,140-4,630 | 19.2-21.0% | 21,248-22,738 | ~20-25% |
| **Phase 3** | 728-1,238 | 21.8-25.4% | 19,282-21,010 | ~25-30% |
| **Phase 4** | 18,493-19,520 | 87.4-90.7% | 630-2,817 | 85-95% |
| **Final** | **24,633-26,660** | **87.5-94.7%** | **1,490-3,517** | **85-95%** |

---

## Risk Assessment

### Low Risk (Phases 1-2)

- **Probability:** 5-10% of automation issues
- **Impact:** Easily reversible, version controlled
- **Mitigation:** Comprehensive testing, rollback capability

### Medium Risk (Phase 3)

- **Probability:** 15-50% may need manual correction
- **Impact:** Time-consuming review process
- **Mitigation:** Two-reviewer system, conservative approach

### High Risk (Phase 4)

- **Probability:** 10-20% of re-extractions may fail
- **Impact:** Significant effort if methodology issues persist
- **Mitigation:**
  - Root cause analysis before starting
  - Incremental batch approach
  - Continuous validation
  - Keep original data for comparison

---

## Resource Requirements

### Personnel

- **Data Engineer:** Phases 1-2 (Python automation, LLM integration)
- **Domain Expert:** Phases 2-3 (review and validation)
- **ML Engineer:** Phase 4 (extraction methodology improvement)

### Tools & Infrastructure

- **Python:** pandas, pydantic, json manipulation
- **LLM API:** Claude/GPT-4 for semantic mapping (Phases 2-3)
- **Version Control:** Git for tracking all changes
- **Validation:** Automated testing framework
- **Review Interface:** Spreadsheet or custom web UI

### Estimated Costs

- **Phase 1:** ~$0 (pure Python)
- **Phase 2:** ~$50-100 (LLM API costs for 4,873 errors)
- **Phase 3:** ~$30-50 (LLM API costs for 1,457 errors)
- **Phase 4:** ~$500-1,000 (LLM costs for re-extraction of ~40 files)
- **Total:** ~$580-1,150 (excluding labor)

---

## Recommendations

### Immediate Actions (Week 1)

1. **Execute Phase 1** - Quick wins with minimal risk
2. **Set up validation infrastructure** - Automated testing framework
3. **Sample Phase 2 testing** - Validate LLM approach on 100 errors

### Short-term (Weeks 2-4)

1. **Complete Phases 2-3** - Address fixable semantic errors
2. **Root cause analysis for Phase 4** - Understand extraction failures
3. **Update extraction methodology** - Prepare for re-extraction

### Long-term (Weeks 5-12)

1. **Execute Phase 4** - Strategic re-extraction
2. **Continuous validation** - Ensure quality improvements
3. **Document lessons learned** - Prevent future issues

### Alternative Approach: Hybrid Strategy

If full re-extraction is not feasible:

1. **Execute Phases 1-3** (25% error reduction)
2. **Selective re-extraction** - Only re-extract highest-error files:
   - Files with >500 errors each (~10-15 files)
   - Would address ~60% of Category D errors
3. **Accept remaining errors** - Document known limitations

This would achieve **~70-80% error reduction** with **~50% less effort** than full Phase 4.

---

## Success Metrics

### Quantitative

- **Error Reduction Rate:** Target >85% overall
- **Validation Success Rate:** Target >90% valid files
- **Processing Efficiency:** <1 hour per file for Phases 1-3
- **Re-extraction Quality:** <5% error rate on re-extracted files

### Qualitative

- **Data Usability:** Knowledge graph can be loaded and queried
- **Schema Compliance:** All files pass validation
- **Completeness:** All required fields populated
- **Semantic Accuracy:** Enum values semantically correct

---

## Conclusion

The 28,150 errors fall into four distinct categories requiring different remediation strategies:

1. **4.5% can be automatically fixed** with simple Python scripts (Phase 1)
2. **17.3% can be fixed by LLM** with high confidence (Phase 2)
3. **5.2% need LLM + human review** for complex cases (Phase 3)
4. **73.0% require re-extraction** due to structural issues (Phase 4)

**Recommended approach:**

- **Execute Phases 1-3 immediately** (4 weeks, ~26% error reduction, low cost)
- **Evaluate re-extraction ROI** before committing to Phase 4
- **Consider hybrid approach** if full re-extraction is not feasible

This phased approach minimizes risk, provides quick wins, and allows for course correction based on early results.

---

**Document Version:** 1.0
**Last Updated:** 2025-11-17
**Next Review:** After Phase 1 completion
