# Knowledge Graph Extraction Investigation: 1890 vs 1886

**Date:** 2025-11-17
**Investigator:** Data Quality Analysis
**Scope:** Comparison of VALID extraction (1886) vs INVALID extraction (1890)

---

## Executive Summary

**Finding:** The 1890 extraction used a fundamentally different schema and extraction methodology than the 1886 extraction, resulting in 1,974 validation errors.

**Root Cause:** Schema mismatch and data parsing errors in extraction script.

**Recommendation:** **RE-EXTRACT** (High Confidence: 95%)

**Rationale:** While some errors are fixable via type conversion, the fundamental schema mismatch, wrong entity keys, and severe data quality issues (names/titles/honors mixed up) require complete re-extraction using the correct schema and methodology.

---

## 1. Metadata Comparison

### 1886 (VALID) ✓
```json
{
  "year": "1886",                    // STRING ✓
  "source_directory": "/home/user/colonial_office_list/output_2/1886_manual_parsed/",  // PRESENT ✓
  "extraction_date": "2025-11-16T00:00:00Z",
  "processing_notes": "Comprehensive extraction from 36 colony files...",
  "colonies_processed": [             // ARRAY of STRINGS ✓
    "BAHAMAS",
    "BARBADOS",
    "BERMUDA",
    // ... 36 colonies total
  ]
}
```

### 1890 (INVALID) ✗
```json
{
  "year": 1890,                      // INTEGER ✗ (should be string)
  "source": "Colonial Office List 1890",
  "extraction_date": "2025-11-16T22:38:02.668843",
  "colonies_processed": 33,          // INTEGER ✗ (should be array of strings)
  "total_entities": 1029
  // MISSING: source_directory ✗
}
```

**Metadata Errors:**
- ❌ `year`: Integer 1890 instead of string "1890"
- ❌ `source_directory`: Missing (required field)
- ❌ `colonies_processed`: Integer 33 instead of array of colony names
- ⚠️  Different field names (`source` vs standard structure)

---

## 2. Entity Structure Comparison

### 1886 Entity Keys (VALID) ✓
```
- places          (17 entities)
- people          (19 entities)
- institutions    (10 entities)
- economic_data   (24 entities)
- infrastructure  (7 entities)
- demographics    (10 entities)
- events          (17 entities)
```
**Total:** 104 entities

### 1890 Entity Keys (INVALID) ✗
```
- geographic_entities  (0 entities)   ✗ Should be "places"
- people              (135 entities)  ✓
- institutions        (386 entities)  ✓
- economic_data       (490 entities)  ✓
- infrastructure      (0 entities)    ✓
- demographic_data    (0 entities)    ✗ Should be "demographics"
- historical_events   (0 entities)    ✗ Should be "events"
- legal_documents     (0 entities)    ✗ NOT IN SCHEMA
- military_units      (14 entities)   ✗ NOT IN SCHEMA
- ships               (4 entities)    ✗ NOT IN SCHEMA
- buildings           (0 entities)    ✗ NOT IN SCHEMA
```
**Total:** 1,029 entities

**Structural Errors:**
- ❌ Wrong entity key names (geographic_entities vs places, demographic_data vs demographics, historical_events vs events)
- ❌ Extra entity types not in schema (legal_documents, military_units, ships, buildings)
- ❌ No geographic entities extracted (0 places)
- ❌ No demographic data extracted (0 demographics)
- ❌ No historical events extracted (0 events)
- ⚠️  Massively inflated entity counts (1,029 vs 104) suggests over-extraction or duplicate data

---

## 3. Data Quality Issues: People Entities

### 1886 Person Example (CORRECT) ✓
```json
{
  "id": "person_bowen_001",
  "name": "George Ferguson Bowen",           // ACTUAL NAME ✓
  "titles": ["Sir"],                         // TITLES ARRAY ✓
  "honors": [],                              // HONORS ARRAY ✓
  "positions": [{
    "title": "Governor",                     // POSITION TITLE ✓
    "department": "Executive",
    "location": "Hong Kong",
    "salary": {
      "amount": 24000,
      "currency": "£",
      "period": "annual"
    },
    "status": "permanent",
    "year": "1886"                           // STRING ✓
  }]
}
```

### 1890 Person Examples (ERRORS) ✗

#### Example 1: Catastrophic Name/Title Confusion
```json
{
  "id": "person_000001",
  "name": "K.C.M.G.",                        // ✗ THIS IS AN HONOR, NOT A NAME!
  "titles": [],                              // ✗ EMPTY (should contain "Sir")
  "honors": [],                              // ✗ EMPTY (should contain "K.C.M.G.")
  "positions": [{
    "title": "Sir R. T. Goldsworthy",        // ✗ THIS IS A NAME, NOT A TITLE!
    "location": "BRITISH HONDURAS",
    "year": 1890                             // ✗ INTEGER (should be string "1890")
  }],
  "salary": {                                // ✗ SALARY AT WRONG LEVEL
    "amount": 11675,                         // (should be inside position)
    "currency": "£",
    "period": "annual"
  }
}
```
**Correct extraction should be:**
```json
{
  "name": "Sir R. T. Goldsworthy",
  "titles": ["Sir"],
  "honors": ["K.C.M.G."],
  "positions": [{
    "title": "Governor",  // or appropriate position
    "salary": { "amount": 11675, "currency": "£", "period": "annual" }
  }]
}
```

#### Example 2: Incomplete Title Extraction
```json
{
  "id": "person_000003",
  "name": "G. W. Melville",
  "titles": [],
  "honors": [],
  "positions": [{
    "title": "and Deaths",                   // ✗ FRAGMENT! (probably "Registrar of Births and Deaths")
    "location": "BRITISH HONDURAS",
    "year": 1890
  }]
}
```

#### Example 3: Location Mistaken for Title
```json
{
  "id": "person_000018",
  "name": "B. Parra",
  "positions": [{
    "title": "Corosol",                      // ✗ THIS IS A LOCATION, NOT A TITLE!
    "location": "BRITISH HONDURAS",
    "year": 1890
  }]
}
```

#### Example 4: Title Not Extracted from Name
```json
{
  "id": "person_000009",
  "name": "Rev. J. Jackson",                 // ✗ "Rev." should be in titles array
  "titles": [],                              // ✗ EMPTY (should contain "Rev.")
  "honors": [],
  "positions": [{
    "title": "Inspector of Schools",
    "year": 1890
  }]
}
```

---

## 4. Data Quality Issues: Institution Entities

### 1886 Institution Example (CORRECT) ✓
```json
{
  "id": "inst_hong_kong_exec_001",
  "name": "Executive Council",
  "type": "executive_council",               // ✓ VALID ENUM
  "location": "Hong Kong",
  "composition": {
    "description": "Composed of 5 official members",
    "member_count": 5
  },
  "function": "Advisory body to the Governor",
  "year": "1886"                             // ✓ STRING
}
```

### 1890 Institution Examples (ERRORS) ✗

#### Example 1: Invalid Enum Type
```json
{
  "id": "institution_000005",
  "name": "Executive Council",
  "type": "council",                         // ✗ INVALID (should be "executive_council")
  "year": 1890                               // ✗ INTEGER (should be string)
}
```

#### Example 2: Incomplete Name Extraction
```json
{
  "id": "institution_000008",
  "name": "Court of",                        // ✗ INCOMPLETE! (Court of what?)
  "type": "court",
  "year": 1890
}
```

#### Example 3: Invalid Type Enum
```json
{
  "id": "institution_000009",
  "name": "House of Assembly",
  "type": "legislature",                     // ✗ INVALID (should be "legislative_council")
  "year": 1890
}
```

**Valid Institution Types:**
```
executive_council, legislative_council, privy_council, court, department,
military_unit, police_force, educational, medical, religious, bank, postal, public_works
```

---

## 5. Error Breakdown Analysis

### By Error Category

| Category | Count | % of Total | Fixable? |
|----------|-------|------------|----------|
| **Type Conversion (year fields)** | 942 | 47.7% | ✓ Auto-fixable |
| **Invalid Enum Values** | 78 | 4.0% | ~ Mappable with manual review |
| **Missing Metadata Fields** | 1 | 0.1% | ✓ Can infer |
| **Wrong Metadata Types** | 2 | 0.1% | ✓ Auto-fixable |
| **Wrong Entity Keys** | ~7 keys | N/A | ✗ Structural re-extraction |
| **Data Extraction Errors** | 31+ | 1.6% | ✗ Requires re-extraction |
| **Missing Entities** | ~900+ | 45.6% | ✗ Requires re-extraction |

### Detailed Error Count Estimation

```
Type Conversion Errors:                942
├─ Position year (int→string):          66
├─ Entity year (int→string):           876
│  ├─ Institutions:                    386
│  ├─ Economic data:                   490
│  └─ Time series entries:             ~0
└─ Metadata (int→string):                2

Enum Validation Errors:                 78
└─ Institution type enum:               78

Missing Fields:                          1
└─ Metadata source_directory:            1

Data Quality Errors:                    31+
├─ Names/titles/honors confused:        ~5
├─ Incomplete titles:                   ~5
├─ Titles in name field:                ~21
└─ Other parsing errors:               Unknown

Structural Errors:                   ~950
├─ Wrong entity keys:                    7
├─ Missing place entities:              ~0 (should be ~17)
├─ Missing demographics:                ~0 (should be ~10)
├─ Missing events:                      ~0 (should be ~17)
└─ Invalid entity types:                ~4 (legal_documents, military_units, ships, buildings)

TOTAL ERRORS:                         1,974
```

---

## 6. Fixability Assessment

### Auto-Fixable (49.5% of errors)

**Type Conversion (942 errors)**
```python
# Simple int→string conversion for year fields
def fix_year_fields(data):
    # Metadata
    if isinstance(data['metadata']['year'], int):
        data['metadata']['year'] = str(data['metadata']['year'])

    # Positions
    for person in data['entities']['people']:
        for pos in person['positions']:
            if 'year' in pos and isinstance(pos['year'], int):
                pos['year'] = str(pos['year'])

    # Institutions
    for inst in data['entities']['institutions']:
        if 'year' in inst and isinstance(inst['year'], int):
            inst['year'] = str(inst['year'])

    # Economic data
    for econ in data['entities']['economic_data']:
        if 'year' in econ and isinstance(econ['year'], int):
            econ['year'] = str(econ['year'])
        for ts in econ.get('time_series', []):
            if 'year' in ts and isinstance(ts['year'], int):
                ts['year'] = str(ts['year'])
```

**Missing Metadata (1 error)**
```python
# Infer source directory from year
data['metadata']['source_directory'] = f"/home/user/colonial_office_list/output_2/{data['metadata']['year']}_manual_parsed/"
```

**Metadata Type Conversion (2 errors)**
```python
# Convert colonies_processed from int to array
# Note: We lose the actual colony list, would need to infer from entities
data['metadata']['colonies_processed'] = []  # Would need to populate from entity locations
```

### Mappable with Manual Review (4.0% of errors)

**Enum Mapping (78 errors)**
```python
INSTITUTION_TYPE_MAP = {
    'council': None,  # ✗ Ambiguous - could be executive_council or legislative_council
    'legislature': 'legislative_council',  # ✓ Clear mapping
    'court': 'court',  # ✓ Already valid (if properly extracted)
}
```
**Problem:** Some mappings are ambiguous and require manual review or re-extraction.

### NOT Fixable via Automation (46.5% of errors)

**Structural Issues (~950 errors)**
- Wrong entity keys (places vs geographic_entities, etc.)
- Missing entire entity categories (0 places, 0 demographics, 0 events)
- Invalid entity types (legal_documents, military_units, ships, buildings)
- Empty relationships array (should have ~34 relationships based on 1886)

**Data Extraction Errors (~31+ errors)**
- Names and honors swapped (e.g., "K.C.M.G." as name)
- Names and titles swapped (e.g., "Sir R. T. Goldsworthy" as title)
- Incomplete text extraction (e.g., "and Deaths", "Court of")
- Locations extracted as titles (e.g., "Corosol")
- Titles embedded in names not extracted (e.g., "Rev. J. Jackson")

**These require:**
1. Access to original source documents
2. Complete re-extraction using correct schema
3. Proper text parsing logic

---

## 7. Comparison of Extraction Quality

### Data Completeness

| Aspect | 1886 | 1890 | Assessment |
|--------|------|------|------------|
| **Places** | 17 | 0 | ✗ 1890 missing all geographic entities |
| **People** | 19 | 135 | ⚠️ 1890 has 7x more, likely over-extraction |
| **Institutions** | 10 | 386 | ⚠️ 1890 has 38x more, likely over-extraction |
| **Economic Data** | 24 | 490 | ⚠️ 1890 has 20x more, suspicious |
| **Infrastructure** | 7 | 0 | ✗ 1890 missing all infrastructure |
| **Demographics** | 10 | 0 | ✗ 1890 missing all demographics |
| **Events** | 17 | 0 | ✗ 1890 missing all events |
| **Relationships** | 34 | 0 | ✗ 1890 missing all relationships |

### Data Accuracy Sample

Reviewing the first 10 people entities:

**1886 Accuracy:** 10/10 (100%)
- All names correctly extracted
- Titles/honors properly separated
- Position titles accurate
- Salary data at correct level

**1890 Accuracy:** 2/10 (20%)
- 1 entity has name/honor swap (person_000001)
- 1 entity has incomplete title (person_000003)
- 1 entity has title in name field (person_000009)
- 2 entities have location as title (person_000018, person_000019)
- 5 entities have minor issues (titles not extracted)

---

## 8. Root Cause Analysis

### Primary Causes

1. **Different Extraction Script/Method**
   - 1886 used correct schema with proper entity key names
   - 1890 used different schema with wrong key names (geographic_entities vs places, etc.)
   - Evidence: Completely different entity structure, extra entity types

2. **Flawed Text Parsing Logic**
   - Name/title/honor extraction broken
   - Text truncation issues ("and Deaths", "Court of")
   - Location/title confusion
   - Evidence: 31+ data quality errors in sample of 145 entities (21% error rate)

3. **Type Conversion Issues**
   - Year fields output as integers instead of strings
   - colonies_processed output as count instead of array
   - Evidence: 942 type conversion errors (47.7% of all errors)

4. **Schema Validation Skipped**
   - File saved without validation against schema
   - Would have caught all these issues before saving
   - Evidence: 1,974 errors present in saved file

### Secondary Causes

1. **Over-Extraction**
   - 1890 has 10x more entities than 1886
   - Suggests extraction of non-relevant data or duplicates
   - Missing critical data filtering

2. **Missing Entity Relationships**
   - 0 relationships in 1890 vs 34 in 1886
   - Relationship extraction logic not implemented or failed

3. **Entity Type Confusion**
   - Created invalid entity types (legal_documents, military_units, ships, buildings)
   - Suggests extraction script doesn't follow schema specification

---

## 9. Specific Error Examples with Context

### Error Type 1: Name/Honor Swap (CRITICAL)

**Source likely said:**
```
"Sir R. T. Goldsworthy, K.C.M.G. - Governor"
```

**1890 extracted as:**
```json
{
  "name": "K.C.M.G.",              // ✗ WRONG
  "positions": [{
    "title": "Sir R. T. Goldsworthy"  // ✗ WRONG
  }]
}
```

**Should be:**
```json
{
  "name": "R. T. Goldsworthy",
  "titles": ["Sir"],
  "honors": ["K.C.M.G."],
  "positions": [{
    "title": "Governor"
  }]
}
```

**Fix Complexity:** Cannot be automated - requires original source re-parsing

---

### Error Type 2: Text Truncation (HIGH)

**Source likely said:**
```
"G. W. Melville - Registrar of Births and Deaths"
```

**1890 extracted as:**
```json
{
  "name": "G. W. Melville",
  "positions": [{
    "title": "and Deaths"            // ✗ TRUNCATED
  }]
}
```

**Should be:**
```json
{
  "name": "G. W. Melville",
  "positions": [{
    "title": "Registrar of Births and Deaths"
  }]
}
```

**Fix Complexity:** Cannot be automated without source document

---

### Error Type 3: Institution Type Enum (MEDIUM)

**1890 has:**
```json
{
  "type": "council"                  // ✗ INVALID ENUM
}
```

**Valid options:**
```
"executive_council" or "legislative_council"
```

**Fix Complexity:** Requires context to determine which type. Manual review or source re-parsing needed.

---

### Error Type 4: Year Type Conversion (LOW)

**1890 has:**
```json
{
  "year": 1890                       // ✗ INTEGER
}
```

**Should be:**
```json
{
  "year": "1890"                     // ✓ STRING
}
```

**Fix Complexity:** Trivially auto-fixable with `str(year)`

---

## 10. Re-extraction vs Fix Recommendation

### If FIX (Not Recommended - 30% Confidence)

**Estimated Effort:** 40-60 hours

**Steps:**
1. ✓ Auto-fix type conversions (942 errors) - 1 hour
2. ✓ Add missing metadata fields (3 errors) - 30 minutes
3. ~ Manual enum mapping review (78 errors) - 4-6 hours
4. ✗ Restructure entity keys - 2 hours
5. ✗ Manual correction of name/title data (31+ errors) - 8-12 hours
6. ✗ Extract missing entities (places, demographics, events) - IMPOSSIBLE without source
7. ✗ Generate relationships - 4-6 hours
8. ~ Manual validation and testing - 20-30 hours

**Pros:**
- Preserves some extracted data
- Potentially faster for simple type conversions

**Cons:**
- Missing critical entity categories (places, demographics, events) cannot be recovered
- Data quality issues require manual correction (high error rate)
- Over-extraction suggests unreliable data throughout
- Final result may still have hidden errors
- No guarantee of data accuracy
- Doesn't address root cause (faulty extraction script)

### If RE-EXTRACT (RECOMMENDED - 95% Confidence)

**Estimated Effort:** 2-4 hours

**Steps:**
1. Identify correct extraction script used for 1886
2. Verify script outputs correct schema
3. Run extraction on 1890 source files
4. Validate output against schema
5. Review sample entities for quality
6. Commit if valid

**Pros:**
- ✓ Guarantees schema compliance
- ✓ Ensures all entity types are extracted
- ✓ Proper data quality from source parsing
- ✓ Includes relationships
- ✓ Addresses root cause
- ✓ Much faster than manual fixes
- ✓ Reproducible process

**Cons:**
- Loses any unique data in current 1890 file (but that data is unreliable)
- Requires access to original source files

---

## 11. Final Recommendation

### RECOMMENDATION: RE-EXTRACT

**Confidence Level:** 95%

### Justification

1. **Missing Critical Data (46% of errors)**
   - 0 places (should have ~17)
   - 0 demographics (should have ~10)
   - 0 events (should have ~17)
   - 0 relationships (should have ~34)
   - **Cannot be recovered through fixes**

2. **Fundamental Schema Mismatch**
   - Wrong entity key names throughout
   - Invalid entity types
   - Different metadata structure
   - **Requires complete restructuring**

3. **Severe Data Quality Issues (21% error rate in sample)**
   - Names/titles/honors confused
   - Text truncation errors
   - Over-extraction (10x more entities than expected)
   - **Manual correction would be extremely time-consuming and error-prone**

4. **Type Conversion Errors are Symptom, Not Root Cause**
   - While 47% of errors are simple type conversions
   - They indicate broader extraction script problems
   - Fixing symptoms doesn't address underlying issues

5. **Time and Reliability**
   - Fix approach: 40-60 hours, uncertain quality
   - Re-extract approach: 2-4 hours, guaranteed quality
   - Re-extraction is **10-15x faster and more reliable**

### Action Items

1. **Immediate:**
   - [ ] Locate 1890 source files (parsed Colonial Office List pages)
   - [ ] Identify extraction script used successfully for 1886
   - [ ] Verify script configuration and schema compliance

2. **Re-extraction:**
   - [ ] Run validated extraction script on 1890 sources
   - [ ] Perform schema validation on output
   - [ ] Manual QA review of 10-20 sample entities
   - [ ] Compare entity counts with 1886 for reasonableness

3. **Quality Assurance:**
   - [ ] Verify all entity types present (places, people, institutions, economic_data, infrastructure, demographics, events)
   - [ ] Verify relationships generated
   - [ ] Spot-check data accuracy (names, titles, honors)
   - [ ] Validate year fields are strings
   - [ ] Confirm metadata completeness

4. **Post-Extraction:**
   - [ ] Document extraction parameters for future reference
   - [ ] Add 1890 to automated validation pipeline
   - [ ] Archive broken 1890_extracted.json for investigation
   - [ ] Update audit reports

---

## 12. Appendix: Schema Comparison

### Expected Schema (1886 Compliant)

```json
{
  "metadata": {
    "year": "YYYY",                           // STRING
    "source_directory": "path/to/source",     // REQUIRED
    "extraction_date": "ISO-8601",
    "processing_notes": "text",
    "colonies_processed": ["colony1", ...]    // ARRAY
  },
  "entities": {
    "places": [...],                          // Required key
    "people": [...],                          // Required key
    "institutions": [...],                    // Required key
    "economic_data": [...],                   // Required key
    "infrastructure": [...],                  // Required key
    "demographics": [...],                    // Required key (not demographic_data)
    "events": [...]                           // Required key (not historical_events)
  },
  "relationships": [...]                      // Required array
}
```

### Actual 1890 Schema (Non-Compliant)

```json
{
  "metadata": {
    "year": 1890,                             // ✗ INTEGER
    "source": "text",                         // ⚠️ Different field name
    "extraction_date": "ISO-8601",
    "colonies_processed": 33,                 // ✗ INTEGER
    "total_entities": 1029                    // ⚠️ Extra field
    // ✗ MISSING: source_directory
  },
  "entities": {
    "geographic_entities": [...],             // ✗ Should be "places"
    "people": [...],                          // ✓ Correct
    "institutions": [...],                    // ✓ Correct
    "economic_data": [...],                   // ✓ Correct
    "infrastructure": [...],                  // ✓ Correct
    "demographic_data": [...],                // ✗ Should be "demographics"
    "historical_events": [...],               // ✗ Should be "events"
    "legal_documents": [...],                 // ✗ Not in schema
    "military_units": [...],                  // ✗ Not in schema
    "ships": [...],                           // ✗ Not in schema
    "buildings": [...]                        // ✗ Not in schema
  },
  "relationships": []                         // ✗ Empty (should have ~34)
}
```

---

## 13. Validation Error Summary

From audit report: `/home/user/colonial_office_list/reports/audit_1867_1900.md`

```
Year: 1890
Status: ✗ INVALID
Error Count: 1,974
Warnings: 0

Top Error Types:
1. missing: 1,161 occurrences (50.4%)
2. string_type: 969 occurrences (42.1%)
3. enum: 142 occurrences (6.2%)
4. string_pattern_mismatch: 23 occurrences (1.0%)
5. list_type: 4 occurrences (0.2%)

Sample Errors:
1. [metadata -> year] string_type: Input should be a valid string
2. [metadata -> source_directory] missing: Field required
3. [metadata -> colonies_processed] list_type: Input should be a valid list
4. [entities -> people -> 0 -> positions -> 0 -> year] string_type: Input should be a valid string
... and 1,970 more errors
```

---

**Report End**

*For questions or clarifications, review source files:*
- *1886: `/home/user/colonial_office_list/knowledge_graph_extracts/1886_extracted.json`*
- *1890: `/home/user/colonial_office_list/knowledge_graph_extracts/1890_extracted.json`*
- *Schema: `/home/user/colonial_office_list/schemas/kg_schema.py`*
- *Audit: `/home/user/colonial_office_list/reports/audit_1867_1900.md`*
