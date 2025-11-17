# Colonial Office List Knowledge Graph Extraction Plan v2.0

## Overview

Extract structured knowledge graphs from Colonial Office List documents (1867-1966) with one JSON file per colony per year for maximum granularity and temporal tracking.

## File Structure

```
knowledge_graph_v4/
├── CEYLON/
│   ├── 1867_CEYLON.json
│   ├── 1880_CEYLON.json
│   ├── 1890_CEYLON.json
│   └── ... (one file per year where Ceylon appears)
├── JAMAICA/
│   ├── 1867_JAMAICA.json
│   └── ...
├── BARBADOS/
│   ├── 1867_BARBADOS.json
│   └── ...
└── [colony_name]/
    └── [year]_[COLONY_NAME].json
```

## Key Design Principles

### 1. **One JSON Per Colony Per Year**
- Enables temporal tracking of individual colonies
- Keeps file sizes manageable
- Facilitates parallel processing
- Supports cross-year entity matching per colony

### 2. **Standardized Schema (v2.0)**
- See `schema_v2.json` for complete JSON schema
- See `example_1950_CEYLON.json` for working example
- Consistent structure across all 54 years and all colonies

### 3. **Controlled Vocabularies**
- **Master vocabulary**: `master_vocabulary_filtered.json`
- Frequency-filtered from actual data (1867-1966)
- Curated British colonial administrative standards
- Use for validation and normalization

### 4. **Full Source Linking**
- Every entity includes provenance with:
  - Source file path
  - Page numbers
  - Line numbers
  - Section headings
  - **Original text snippet** (critical for verification)
  - Extraction confidence score
- Enables researchers to verify and cite sources

### 5. **Location Context with Certainty**
- Every place includes:
  - `mentioned_in_colony`: Which colony section it appears in
  - `actual_location_country`: Where it's actually located
  - `certainty`: definite | probable | uncertain
  - `reasoning`: Explanation for attribution
- **Example**: School in India mentioned in Ceylon section

### 6. **Coordinates Only From Source**
- Include lat/long **only** if explicitly stated in source document
- No external gazetteer lookups at extraction stage
- Preserves historical accuracy

## Controlled Vocabularies Summary

### British Honors (31 standard)
**High frequency in data:**
- CMG (389 occurrences, 15 years)
- KCMG (284 occurrences, 18 years)
- DSO (259 occurrences, 9 years)
- OBE, MC, CB, GCMG, KCB, MBE, CBE

**Note:** Filter out academic degrees (BA, MA, MD, LLD) - not honors

### Titles (33 standard)
- Nobility: Sir, Dame, Lord, Lady, Hon, Earl, Baron, etc.
- Religious: Rev, Canon, Bishop, Archdeacon
- Military: Major, Captain, Colonel, General, Admiral
- Academic: Dr, Prof

### Positions (36 high-frequency + curated)
**Top positions by frequency:**
1. Governor (280 occurrences)
2. Chief Justice (129)
3. Colonial Secretary (103)
4. Governor and Commander-in-Chief (83)
5. Private Secretary (60)

**Hierarchy levels:**
- 1: Governor-General
- 2: Governor, Lieutenant-Governor, Chief Justice
- 3: Colonial Secretary, Attorney-General, Bishop
- 4-7: Department heads, clerks, assistants

### Institution Types (23 standard)
- Executive: Executive Council, Government
- Legislative: Legislative Council, Legislative Assembly
- Judicial: Supreme Court, Court of Appeal, Magistrates' Court
- Administrative: Colonial Secretariat, Treasury, Police, etc.

## Extraction Process

### Phase 1: Per-Colony-Year Extraction

For each year (1867-1966):
  For each colony in that year:
    1. Read markdown file: `output_2/{year}_manual_parsed/{COLONY}.md`
    2. Extract entities using controlled vocabularies
    3. Build relationships
    4. Deduplicate within colony-year
    5. Add full provenance
    6. Output: `knowledge_graph_v4/{COLONY}/{year}_{COLONY}.json`

### Entity Extraction Guidelines

#### People
- **Name**: Full name without titles/honors
- **Titles**: Use controlled vocabulary (Sir, Rev, Dr, etc.)
- **Honors**: Use controlled vocabulary (KCMG, CMG, etc.)
  - Filter out degrees (BA, MA, MD)
- **Positions**: Normalize to canonical forms
- **Salary**: Extract amount, currency, period, allowances
- **Duplicate detection**: Flag potential duplicates with confidence

#### Places
- **Location context**: Always include mentioned_in_colony, actual_location_country, certainty
- **Coordinates**: Only if explicitly in source
- **Population**: Include census year and breakdowns (preserve historical terminology)

#### Institutions
- **Type**: Use controlled vocabulary
- **Composition**: For councils - official/unofficial/elected members
- **Hierarchy**: Parent institution relationships

#### Economic Data
- **Validation**: Flag implausible values (revenue of £1 for a colony)
- **Fiscal year**: Distinguish from publication year
- **Currency**: Track historical currencies

#### Events
- **Date precision**: exact | month | year | circa | unknown
- **Distinguish**: event_date (when it happened) vs year_mentioned (when COL published)

### Relationships

Build within-year relationships:
- Person `HOLDS_POSITION` → Institution
- Person `REPORTS_TO` → Person (based on hierarchy)
- Institution `PART_OF` → Institution
- Place `LOCATED_IN` → Place
- Event `OCCURRED_IN` → Place
- Event `PARTICIPATED_IN` ← Person

### Deduplication

**Within colony-year only:**
- Same person multiple mentions: "Sir John Smith", "J. Smith", "John Smith, K.C.M.G."
- Normalize names, fuzzy match
- Flag uncertain duplicates with `duplicate_candidates` field

**Cross-year entity matching: NOT in this phase**
- That comes later as a separate linking phase
- Requires entity resolution across temporal data

## Data Quality Standards

### Extraction Confidence Levels
- **0.95-1.00**: Direct extraction, unambiguous
- **0.85-0.95**: Parsed from tables, minor interpretation
- **0.75-0.85**: Inferred from context
- **0.50-0.75**: Uncertain, needs verification
- **< 0.50**: Flag for manual review

### Validation Rules

**Economic Data:**
- Revenue should be £1,000 to £100,000,000 range
- Expenditure ≈ revenue (within reason)
- Flag if plausibility = "implausible"

**Positions:**
- Must match controlled vocabulary or be flagged
- Hierarchy level 1-7 (not 0 or >7)

**Dates:**
- Event dates should be ≤ publication year
- Check for OCR errors (1R15 instead of 1815)

### Provenance Requirements

**Every entity must have:**
- ✅ source_file
- ✅ source_pages (PDF page numbers)
- ✅ source_lines
- ✅ source_section (heading path)
- ✅ original_text (snippet for verification)
- ✅ extraction_confidence
- ✅ extraction_date
- ✅ extraction_agent
- ✅ extraction_method (direct_extraction | parsed_table | inferred | normalized)

## Parallel Processing Strategy

### Option A: One Task Per Colony-Year
```
Launch ~2,000+ tasks (54 years × ~40 avg colonies)
Pro: Maximum parallelism
Con: Many task invocations
```

### Option B: One Task Per Year
```
Launch 54 tasks, each processes all colonies for that year
Pro: Fewer tasks, shared vocabulary loading
Con: Slower per-task completion
```

### Option C: One Task Per Colony
```
Launch ~60 tasks (one per colony), each processes all years
Pro: Temporal continuity, easier cross-year analysis
Con: Some colonies only in a few years
```

**Recommendation**: Option C - one task per colony processing all years
- Easiest to track entity evolution
- Natural grouping for later cross-year linking
- ~60 parallel tasks is manageable

## Task Prompt Template

```
Extract knowledge graph for [COLONY] across all years 1867-1966.

Input:
- Source directory: output_2/{year}_manual_parsed/
- Master vocabulary: master_vocabulary_filtered.json
- Schema: schema_v2.json
- Example: example_1950_CEYLON.json

Process:
1. Find all years where [COLONY] appears (check for markdown files)
2. For each year:
   a. Extract entities following schema v2.0
   b. Normalize using controlled vocabularies
   c. Build intra-year relationships
   d. Deduplicate within year
   e. Add full provenance with original text snippets
   f. Validate data quality
   g. Output: knowledge_graph_v4/[COLONY]/{year}_[COLONY].json

3. Return summary:
   - Years processed
   - Total entities extracted by type
   - Data quality issues found
   - Processing time

Quality standards:
- Include coordinates ONLY if in source
- Add location context with certainty for all places
- Flag potential duplicates
- Extract original text snippets for verification
- Validate economic data plausibility
```

## Next Steps

### Immediate (Phase 1)
1. ✅ Define schema (schema_v2.json)
2. ✅ Create example (example_1950_CEYLON.json)
3. ✅ Extract master vocabularies (master_vocabulary_filtered.json)
4. **TODO**: Launch extraction tasks per colony
5. **TODO**: Validate sample outputs

### Phase 2: Cross-Year Entity Linking
- Match same person across years (John Smith 1890 → John Smith 1891)
- Track career trajectories
- Identify institutional evolution
- Build temporal relationship graphs

### Phase 3: Academic Enhancements
- External dataset linking (prosopography databases)
- GIS data integration
- Historical context annotations
- Citation generation

## Files Reference

- **Schema**: `schema_v2.json` - JSON schema definition
- **Example**: `example_1950_CEYLON.json` - Complete example
- **Vocabularies**: `master_vocabulary_filtered.json` - Frequency-filtered terms
- **Curated**: `master_vocabulary_curated.json` - Historical standards reference

## Success Metrics

### Data Completeness
- ✅ All 54 years processed
- ✅ All colonies extracted
- ✅ All entity types present (people, places, institutions, economic, infrastructure, events)

### Data Quality
- ✅ >95% entities have full provenance
- ✅ >90% extraction confidence >0.85
- ✅ <5% implausible economic values
- ✅ All positions match controlled vocabulary or flagged

### Academic Utility
- ✅ Source citations enable verification
- ✅ Historical terminology preserved
- ✅ Temporal relationships queryable
- ✅ Suitable for peer-reviewed publication

---

## Questions for Review

1. **Directory structure**: Create `knowledge_graph_v4/` or rename `knowledge_graph_extracts_v3/`?

2. **Processing strategy**: One task per colony (Option C) acceptable?

3. **Validation**: Auto-flag vs manual review for low confidence (<0.75)?

4. **Academic degrees**: Separate category from honors, or exclude entirely?

5. **Relationships**: Include inferred relationships (reports_to) or only explicit?

6. **Cross-references**: Should we extract references to other colonies (e.g., "trained in India" in Ceylon section)?
