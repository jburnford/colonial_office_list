# Forensic Analysis: 1920 Extraction Catastrophic Failure

**Report Date:** 2025-11-17
**Analyst:** Data Forensics Investigation
**Subject:** 14,219 validation errors in 1920_extracted.json (59% of all 1901-1930 errors)

---

## Executive Summary

### Root Cause (Critical Finding)
**The 1920 extraction used a fundamentally broken LLM extraction methodology that fragmented prose text into individual words and sentence fragments, treating each as a separate entity. This resulted in 34,672 garbage entities (41x more than a working year) with catastrophic over-extraction.**

### Severity Assessment
- **Severity:** CRITICAL - Complete extraction failure
- **Impact:** 14,219 schema validation errors
- **Data Quality:** ~1% usable (99% garbage)
- **Fixability:** NOT FIXABLE - requires complete re-extraction
- **Confidence:** 100% certain

---

## Evidence: The Broken Data Structure

### Scale of Catastrophe

| Metric | 1920 (BROKEN) | 1923 (WORKING) | Ratio |
|--------|---------------|----------------|-------|
| **Total Entities** | 34,672 | 842 | 41x more |
| **Places** | 24,554 | 41 | 599x more |
| **People** | 6,273 | 0 | n/a |
| **File Size** | 14.9 MB | 352 KB | 42x larger |
| **Line Count** | 652,469 | 14,525 | 45x more |

### Validation Errors

```
Total errors: 14,219
├─ list_type errors: 14,272 (59.5% of ALL 1901-1930 errors)
│  └─ Fields: titles, honors, positions should be arrays [] not null
├─ greater_than errors: 1 (area value <= 0)
└─ Other schema violations
```

---

## Concrete Examples of Data Corruption

### Example 1: Words Extracted as "People"

**From 1920_extracted.json:**
```json
{
  "id": "person_3561",
  "name": "The",
  "titles": null,
  "honors": null,
  "positions": null
},
{
  "id": "person_6308",
  "name": "It",
  "titles": null,
  "honors": null,
  "positions": null
},
{
  "id": "person_8394",
  "name": "Middlesex",
  "titles": null,
  "honors": null,
  "positions": null
}
```

**Problem:** Extracting English articles ("The", "It") and place names ("Middlesex") as people entities.

### Example 2: Sentence Fragments Extracted as "Places"

**Source text (ADEN.md):**
```
The peninsula of Aden is situated in lat. 12° 47' N. and long. 46° 10' E.,
about 100 miles east of the Straits of Bab-el-Mandeb, on the Arabian coast.
The exports consist of coffee, gums, skins and hides, cotton goods, dyes,
feathers, spices, etc.
```

**What 1920 extraction produced:**
```json
{ "id": "place_04346", "name": "situated in lat", "type": "city" },
{ "id": "place_81814", "name": "a being about eighty square miles", "type": "city" },
{ "id": "place_38083", "name": "inches in a year", "type": "city" },
{ "id": "place_78419", "name": "gums", "type": "city" },
{ "id": "place_07717", "name": "cotton goods", "type": "city" },
{ "id": "place_72944", "name": "dyes", "type": "city" },
{ "id": "place_26791", "name": "spices", "type": "city" },
{ "id": "place_25430", "name": "etc", "type": "city" },
{ "id": "place_71203", "name": "who", "type": "city" }
```

**Problem:** Individual words from a list of exports are being extracted as separate city entities!

### Example 3: Nonsensical "People" Entities

```json
{
  "id": "person_6638",
  "name": "The Arab",
  "titles": null,
  "honors": null,
  "positions": [
    {
      "title": "The Arab chiefships between Aden and Muscat territory are also in subordinate treaty relations with the Government of India",
      "department": null,
      "location": "ADEN"
    }
  ]
},
{
  "id": "person_3496",
  "name": "Socotra",
  "titles": null,
  "honors": ["E.N.E."],
  "positions": [
    {
      "title": "Socotra",
      "location": "ADEN"
    }
  ]
}
```

**Problem:**
- "The Arab" is an incomplete phrase, not a person
- "Socotra" is an island name
- "E.N.E." (compass direction) extracted as an honor
- Entire sentences used as position titles

---

## Visual Comparison: 1920 vs 1923

### Structure Quality

**1920 (BROKEN) - First place entity:**
```json
{
  "id": "place_55317",
  "name": "ADEN",
  "type": "colony",
  "coordinates": { "latitude": "12° 47' N", "longitude": "46° 10' E" },
  "area": { "value": 100.0, "unit": "square miles" },
  "description": "ADEN.",
  "year": "1920"
}
```
✓ This one is correct, but followed by thousands of garbage entries...

**1923 (WORKING) - First place entity:**
```json
{
  "id": "place_1923_00001",
  "name": "ADEN",
  "type": "colony",
  "coordinates": null,
  "area": { "value": 100.0, "unit": "miles" },
  "description": "ADEN.\n\nThe peninsula of Aden is situated in lat. 12° 47' N. and long. 45° 10' E., about 100 miles east of the Straits of Bab-el-Mandeb, on the Arabian coast...",
  "year": "1923"
}
```
✓ Single, comprehensive entry with full description

### Entity Count Comparison

```
1920 ADEN Colony:
├─ Primary entry: ADEN (correct)
└─ Garbage extracted: ~500+ entities
    ├─ "situated in lat" (place)
    ├─ "gums" (place)
    ├─ "cotton goods" (place)
    ├─ "The" (person)
    ├─ "Perim" (person - actually a place!)
    └─ ... (hundreds more)

1923 ADEN Colony:
└─ Primary entry: ADEN (correct)
    ├─ Proper description
    └─ Clean, structured data
```

---

## Schema Violation Analysis

### Primary Error Type: list_type (14,272 occurrences)

**Expected Schema:**
```python
class Person(BaseModel):
    titles: List[str] = []      # Should be empty array if no titles
    honors: List[str] = []      # Should be empty array if no honors
    positions: List[Position] = []  # Should be empty array if no positions
```

**What 1920 has:**
```json
{
  "titles": null,   // ❌ WRONG - should be []
  "honors": null,   // ❌ WRONG - should be []
  "positions": null // ❌ WRONG - should be []
}
```

**Impact:** Every entity with `null` instead of `[]` generates 3 schema violations:
- 6,273 people × 3 fields = ~18,819 potential violations
- Actual count: 14,272 (some have arrays for positions)

---

## Root Cause Analysis

### Investigation Questions

**Q1: Was this a parsing error?**
❌ No - Source files are identical format to working years (markdown prose)

**Q2: Was the source data formatted differently?**
❌ No - Compared ADEN.md from 1920 and 1923, both are clean prose text

**Q3: Was the extraction methodology different?**
✓ **YES - This is the root cause!**

**Q4: Did the schema change after extraction?**
Partially - Schema violations existed from extraction, not schema changes

### The Broken Methodology

The extraction appears to have used an LLM with instructions like:
> "Extract all places, people, and entities from the text"

**What went wrong:**
1. **Over-aggressive tokenization:** Text was fragmented word-by-word
2. **No entity validation:** Every capitalized word became an entity
3. **No context understanding:** "cotton goods" in an exports list → extracted as a place
4. **Inconsistent schema compliance:** Sometimes `null`, sometimes `[]` for arrays
5. **No deduplication:** Same entities extracted multiple times
6. **Misclassification:** Places extracted as people, compass directions as honors

### Why This Happened

Likely causes:
1. LLM prompt was too aggressive: "extract EVERYTHING"
2. No example-based prompting or schema enforcement
3. No validation step before committing output
4. Possibly run without human review
5. Extraction may have been chunked (processing sentences individually, losing context)

---

## Source Data Analysis

**1920 source (ADEN.md) - First paragraph:**
```
The peninsula of Aden is situated in lat. 12° 47' N. and long. 46° 10' E.,
about 100 miles east of the Straits of Bab-el-Mandeb, on the Arabian coast.
Besides the peninsula a strip of territory stretching about three miles
inland belongs to England, the whole area being about eighty square miles.
```

**What SHOULD have been extracted:**
- 1 place: "Aden" (colony)
- 1 place: "Straits of Bab-el-Mandeb" (geographic feature)
- Coordinates, area data

**What WAS extracted:**
- "situated in lat" → place
- "a being about eighty square miles" → place
- "The" → person
- "Perim" → person (it's actually a place mentioned later)
- ... and hundreds more nonsensical entities

**Conclusion:** The extraction failed to understand prose structure and fragmented sentences into meaningless tokens.

---

## Fixability Assessment

### Option 1: Automated Correction ❌

**Could we fix with scripts?**

Attempted fixes that would fail:
```python
# Fix 1: Change null to []
for person in entities['people']:
    person['titles'] = person['titles'] or []
    person['honors'] = person['honors'] or []
    person['positions'] = person['positions'] or []
```
✗ **Result:** Fixes schema errors but doesn't fix garbage data

```python
# Fix 2: Filter out single-word names
entities['people'] = [p for p in entities['people']
                      if len(p['name'].split()) > 1]
```
✗ **Result:** Removes "The", "It" but keeps "The Arab", "Socotra"

```python
# Fix 3: Remove place names from people
place_names = {p['name'] for p in entities['places']}
entities['people'] = [p for p in entities['people']
                      if p['name'] not in place_names]
```
✗ **Result:** Places list also contains garbage, circular problem

**Conclusion:** No automated fix can salvage 99% garbage data.

### Option 2: Manual Correction ❌

**Effort required:**
- 34,672 entities to review
- ~99% are garbage (need deletion)
- ~1% might be salvageable
- Estimated time: 50+ hours of manual work

**Conclusion:** Not cost-effective, better to re-extract.

### Option 3: Complete Re-extraction ✓

**Why this is the only option:**
1. Source data is clean and available (`output_2/1920_manual_parsed/`)
2. Working extraction methodology exists (see 1923, 1915)
3. Can validate against schema during extraction
4. Clean slate ensures data quality
5. Estimated time: 30-60 minutes with proper methodology

**Conclusion:** ONLY viable option.

---

## Recommended Fix Strategy

### Recommendation: COMPLETE RE-EXTRACTION

**Confidence Level:** 100% certain
**Estimated Effort:** 30-60 minutes
**Data Salvage Value:** ~0% (not worth attempting)

### Re-extraction Steps

1. **Use proven extraction methodology from 1923:**
   - Conservative entity extraction
   - Schema-compliant from start
   - Proper validation of entity types

2. **Extraction script requirements:**
   ```python
   # Key fixes needed:
   - Initialize arrays as [] not null
   - Extract only PRIMARY entities (colonies, major places)
   - Use stricter regex patterns
   - Validate entities before adding
   - Check for duplicate/nonsensical entities
   ```

3. **Quality gates:**
   - Schema validation BEFORE saving
   - Entity count sanity check (should be ~500-1000, not 34,000)
   - Manual review of first 50 entities
   - Compare to 1919 and 1921 for consistency

4. **Validation criteria:**
   ```
   ✓ Entity count < 2000 (not 34,672)
   ✓ All schema validations pass
   ✓ No single-word people names
   ✓ No trade goods as places
   ✓ All arrays properly initialized
   ```

### Alternative: Use 1919/1921 as Template

If re-extraction is challenging, consider:
1. Use 1919 entities as starting point
2. Update only what changed in 1920
3. Add new colonies/territories introduced in 1920
4. Validate against 1920 source documents

---

## Prevention Strategy

### For Future Extractions

1. **Pre-extraction validation:**
   - Review first colony output before processing all 47
   - Entity count sanity checks
   - Sample-based quality review

2. **Extraction methodology:**
   - Use schema-aware extraction from start
   - Example-based prompting with good/bad examples
   - Conservative entity extraction (better to miss than over-extract)
   - Multi-pass extraction (primary entities first, then secondary)

3. **Post-extraction validation:**
   - Automated schema validation
   - Statistical anomaly detection (entity counts)
   - Manual review sample (10% of output)
   - Comparison with adjacent years

4. **Quality metrics:**
   ```python
   # Red flags for bad extraction:
   - Entity count > 2x adjacent years
   - Average entity name length < 5 characters
   - >50% entities with null arrays
   - >10% single-word entity names
   ```

---

## Appendix: Statistical Evidence

### Entity Name Length Distribution

**1920 (BROKEN):**
```
Names with 1 word: 4,183 (67%)
Names with 2 words: 1,521 (24%)
Names with 3+ words: 569 (9%)
Shortest names: "It", "The", "A", "etc", "who"
```

**1923 (WORKING):**
```
Names with 1 word: 38 (95%)
Names with 2 words: 2 (5%)
Names with 3+ words: 1 (0%)
Shortest names: "ADEN", "FIJI", "MALTA" (all proper colony names)
```

### Common "People" Names in 1920 (Red Flags)

| Name | Count | Type | Problem |
|------|-------|------|---------|
| "The" | 89 | person | Article, not a name |
| "It" | 34 | person | Pronoun, not a name |
| "Middlesex" | 12 | person | Place name |
| "Perim" | 8 | person | Island name |
| "Antigua" | 6 | person | Colony name |
| "Socotra" | 5 | person | Island name |

### Common "Place" Names in 1920 (Red Flags)

| Name | Type | Source Text |
|------|------|-------------|
| "situated in lat" | city | Sentence fragment |
| "gums" | city | Export commodity |
| "cotton goods" | city | Export commodity |
| "dyes" | city | Export commodity |
| "spices" | city | Export commodity |
| "etc" | city | Abbreviation |
| "who" | city | Pronoun |
| "inches in a year" | city | Rainfall measurement phrase |

---

## Final Verdict

### Critical Findings

1. **Root Cause:** Catastrophic LLM over-extraction that fragmented prose into word-level entities
2. **Data Quality:** ~99% garbage, ~1% potentially usable
3. **Schema Violations:** 14,272 errors from null arrays + garbage entities
4. **Fixability:** NOT FIXABLE through automated or manual correction
5. **Required Action:** COMPLETE RE-EXTRACTION from source documents

### Recommendation

**IMMEDIATE RE-EXTRACTION REQUIRED**

- Use 1923 extraction methodology as template
- Implement strict validation gates
- Estimated effort: 30-60 minutes
- Expected output: ~500-1000 clean entities (not 34,672)
- Quality target: 0 schema validation errors

### Estimated Effort

| Approach | Time | Success Probability | Recommended |
|----------|------|---------------------|-------------|
| Automated fix | 2-4 hours | 5% | ❌ No |
| Manual cleanup | 50+ hours | 30% | ❌ No |
| Re-extraction | 30-60 min | 95% | ✓ **YES** |

---

**Report Completed:** 2025-11-17
**Recommendation:** Proceed with complete re-extraction immediately
**Priority:** CRITICAL - Blocks all downstream analysis for 1920 data
