# Massive LLM-Powered Knowledge Graph Improvement Plan
## Maximizing $600 in Credits for Colonial Office List KG Enhancement

**Created:** 2025-11-17
**Status:** READY FOR EXECUTION
**Budget:** $600 in free LLM credits
**Time Remaining:** < 2 days
**Focus:** LLM-powered improvements (Python/Human-in-loop deferred)

---

## Executive Summary

This plan transforms the existing 62-year knowledge graph (68MB, 1867-1966) into a production-grade historical dataset through **massive parallel LLM agent deployment**. We will launch **80+ parallel agent tasks** across 8 improvement categories, prioritizing:

1. **Provenance Linking** - Every entity traceable to source document
2. **Toponym Grounding** - Link all groundable place names to Wikidata/Geonames
3. **Entity Extraction Enhancement** - Fill missing data, improve quality
4. **Relationship Validation** - Verify and enrich all entity relationships
5. **Error Correction** - LLM-powered enum mapping and validation fixes
6. **Data Enrichment** - Add historical context, normalize dates, identify honors
7. **Cross-year Consistency** - Standardize naming across 62 years
8. **Quality Validation** - Comprehensive LLM-based quality checks

**Current State:**
- ✅ 62 KG files extracted (68MB total)
- ✅ Phase 1 Python corrections complete (54% error reduction)
- ⚠ Phase 2 LLM enum mapper built but not executed
- ❌ NO provenance linking (critical gap)
- ❌ Toponym grounding incomplete
- ⚠ 12,951 validation errors remaining
- ⚠ Source document linking missing

**Target State:**
- ✅ 100% entities linked to source documents (file + line numbers)
- ✅ 90%+ toponyms grounded to Wikidata/Geonames
- ✅ 95%+ validation errors resolved
- ✅ Enhanced schema with provenance, normalized dates, LOD recommendations
- ✅ Cross-year entity suggestions for human review
- ✅ Comprehensive quality reports

---

## Part 1: Immediate Provenance Linking (HIGHEST PRIORITY)

### Why This Matters
**"Every piece of extracted knowledge needs an easy link back to the source document for ground truth analysis"** - User requirement #1

Currently, entities have NO source traceability beyond year-level metadata. We need entity-level provenance.

### Strategy: Retroactive Provenance Inference

For each entity in each KG file:
1. Use LLM to locate the entity in the source markdown file
2. Extract exact line numbers where entity information appears
3. Add provenance object to entity with source file path and line range
4. Confidence score for provenance accuracy

### Enhanced Schema Addition

```json
{
  "id": "place_aden_001",
  "name": "Aden",
  "provenance": {
    "source_file": "output_2/1896_manual_parsed/ADEN.md",
    "source_lines": "15-28",
    "source_section": "Situation and Area",
    "extraction_confidence": 0.95,
    "extraction_date": "2025-11-17",
    "extraction_agent": "provenance_linker_v1",
    "verification_status": "automated"
  },
  ...
}
```

### Parallel Execution Plan: 8 Agents

**Agent 1: Provenance Linker 1867-1880** (8 years)
- Link entities in: 1867, 1877, 1880, 1883, 1886, 1888, 1889, 1890
- Source: `output_2/YEAR_manual_parsed/`
- For each entity: find source file, locate content, record lines

**Agent 2: Provenance Linker 1894-1907** (7 years)
- Link entities in: 1894, 1896, 1897, 1898, 1899, 1900, 1905, 1906, 1907

**Agent 3: Provenance Linker 1908-1917** (9 years)
- Link entities in: 1908, 1909, 1910, 1911, 1912, 1913, 1914, 1915, 1917

**Agent 4: Provenance Linker 1918-1927** (9 years)
- Link entities in: 1918, 1919, 1920, 1921, 1922, 1923, 1924, 1925, 1927

**Agent 5: Provenance Linker 1928-1937** (8 years)
- Link entities in: 1928, 1929, 1930, 1931, 1932, 1933, 1935, 1936, 1937

**Agent 6: Provenance Linker 1938-1949** (8 years)
- Link entities in: 1938, 1939, 1940, 1946, 1948, 1949

**Agent 7: Provenance Linker 1950-1959** (8 years)
- Link entities in: 1950, 1951, 1953, 1954, 1956, 1957, 1959

**Agent 8: Provenance Linker 1961-1966** (6 years)
- Link entities in: 1961, 1962, 1964, 1965, 1966

### Deliverables
- 62 enhanced KG files with provenance objects on every entity
- Provenance coverage report (% entities with source links)
- Confidence distribution (how many high/medium/low confidence links)

**Estimated Cost:** ~$80-120 (highest priority)

---

## Part 2: Toponym Grounding & LOD Linking

### Objective
Ground all specific, historically significant place names to Wikidata and Geonames. Focus on:
- ✅ Colonies/territories (e.g., "British Honduras" → Q192209)
- ✅ Cities/towns (e.g., "Bridgetown" → GeoNames:3374333)
- ✅ Geographic features with historical significance (e.g., "Table Mountain")
- ❌ NOT generic locations ("the hill", "the river")

### Enhanced Schema

```json
{
  "id": "place_bridgetown_001",
  "name": "Bridgetown",
  "lod_links": {
    "wikidata": {
      "qid": "Q36168",
      "label": "Bridgetown",
      "url": "https://www.wikidata.org/wiki/Q36168",
      "confidence": 0.98,
      "match_method": "exact_name_coords",
      "matched_claims": ["P31:city", "P17:Barbados", "P625:13.1N,59.6W"]
    },
    "geonames": {
      "geonames_id": "3374333",
      "name": "Bridgetown",
      "country": "Barbados",
      "latitude": 13.09619,
      "longitude": -59.60893,
      "confidence": 0.99,
      "url": "http://www.geonames.org/3374333/"
    },
    "match_notes": "Exact coordinate match within 0.1 degrees, name exact match, historical timeframe validated"
  }
}
```

### Parallel Execution Plan: 8 Agents

Each agent processes ~8 years, focusing on grounding:

**Agent 1: Toponym Grounder 1867-1880**
- Process all "places" entities in these years
- Query Wikidata SPARQL for colonies, cities
- Query Geonames API for geographic entities
- Use coordinates + names + temporal constraints for matching
- Add confidence scores

**Agent 2-8: Toponym Grounders** (similar division)
- Each covers ~8 years
- Same grounding process
- Focus on high-value targets (colonies, major cities, named geographic features)

### Grounding Rules
1. **High Confidence (0.9+):** Exact name + coordinates within 0.1° + temporal overlap
2. **Medium Confidence (0.7-0.9):** Name match + geographic region match + plausible timeframe
3. **Low Confidence (0.5-0.7):** Fuzzy name match, needs human review
4. **Flag for Review (<0.5):** Conflicting matches or no clear match

### Deliverables
- Enhanced KG files with LOD links on all groundable places
- Grounding coverage report (% places linked)
- Human review queue (medium/low confidence matches)
- LINCS candidate list (entities without existing Wikidata/Geonames IDs)

**Estimated Cost:** ~$100-150

---

## Part 3: Phase 2 Enum Mapping Execution

### Status
- ✅ LLM enum mapper built (`correctors/phase2_enum_mapper.py`)
- ✅ Tested on sample (66.7% auto-apply rate)
- ❌ Not executed across all 62 files

### Current Errors
- 4,760 enum errors remaining (36.8% of 12,951 total errors)
- Expected fix rate: 66% auto-apply = ~3,142 errors fixed

### Execution Plan: Single Sequential Agent

**Agent: Phase 2 Enum Executor**
- Run phase2_enum_mapper.py on all 62 files sequentially
- LLM provides semantic understanding of invalid enum values
- Map to closest valid enum with confidence scores
- Apply mappings with confidence ≥ 0.9 automatically
- Flag 0.7-0.9 for review
- Generate report of all mappings

### Deliverables
- 62 KG files with enum errors reduced by ~66%
- Mapping log (what was changed and why)
- Review queue (medium-confidence mappings)

**Estimated Cost:** ~$40-60

---

## Part 4: Entity Extraction Enhancement

### Objective
Use LLMs to fill missing data and improve extraction quality by re-reading source documents with targeted prompts.

### Target Improvements

**A. Missing Required Fields**
- 6,551 missing field errors (50.6% of remaining errors)
- Common: missing position status, missing institution type, missing dates

**B. Salary & Economic Data Extraction**
- Many people entities missing salary information
- Economic data incomplete (missing currency, missing years)

**C. Honors & Titles Extraction**
- Systematically extract honors (K.C.M.G., C.B., etc.)
- Build honors vocabulary and accumulation tracking

**D. Relationship Extraction**
- Many implicit relationships not captured
- Example: "Governor Smith succeeded Governor Jones" → succession relationship

### Parallel Execution Plan: 8 Agents

**Agent 1: Entity Enhancer 1867-1880**
- For each entity with missing fields:
  - Re-read source document section
  - Extract missing information with LLM
  - Add to entity with provenance
  - Validate against schema

**Agent 2-8: Entity Enhancers** (similar division)

### Specific Enhancement Tasks

Each agent performs:
1. **Missing Field Extraction**: Target entities with validation errors
2. **Salary Extraction**: Re-read position listings for salary data
3. **Honors Extraction**: Systematic scan for honors in person names/descriptions
4. **Date Normalization**: Convert historical date strings to ISO-8601
5. **Relationship Discovery**: Identify succession, administrative hierarchy, etc.

### Deliverables
- Enhanced KG files with 80%+ missing fields filled
- Validation error count reduced by 50%+
- Comprehensive honors index
- Normalized date coverage report

**Estimated Cost:** ~$100-150

---

## Part 5: Relationship Validation & Enhancement

### Current State
Relationships exist but may be incomplete or incorrect. Need LLM validation.

### Validation Checks

**A. Relationship Integrity**
- Do source and target entities exist?
- Is relationship type semantically correct?
- Is temporal information consistent?

**B. Missing Relationships**
- Administrative hierarchies (Governor → Colonial Secretary)
- Geographic containment (City → Colony)
- Succession chains (Governor A → Governor B)
- Infrastructure ownership (Railway → Government)

**C. Relationship Enrichment**
- Add temporal bounds (start_year, end_year)
- Add source provenance
- Add confidence scores

### Parallel Execution Plan: 8 Agents

**Agent 1: Relationship Validator 1867-1880**
- Validate all relationships in these years
- Check entity references
- Verify relationship types
- Discover missing relationships from text

**Agent 2-8: Relationship Validators** (similar division)

### Deliverables
- Validated relationships with provenance
- New relationships discovered from text
- Relationship validation report
- Relationship density metrics (relationships per entity)

**Estimated Cost:** ~$60-80

---

## Part 6: Cross-Year Consistency & Entity Resolution Prep

### Objective
Prepare for inter-year entity resolution by standardizing naming and flagging candidates.

### Tasks

**A. Name Standardization**
- Colony names: "THE GAMBIA" vs "GAMBIA" vs "Gambia"
- Person names: "F. Smith" vs "Frederick Smith" vs "Smith, F."
- Institution names: "Executive Council" vs "Exec. Council"

**B. Variant Detection**
- Use LLM to identify name variants across years
- Build canonical name mapping table
- Flag for human review

**C. Entity Resolution Candidates**
- Find potential same-person matches across years
- Criteria: similar name + overlapping location + plausible career progression
- Generate review queue with confidence scores

### Parallel Execution Plan: 8 Agents

**Agent 1: Consistency Checker 1867-1880**
- Extract all entity names (places, people, institutions)
- Identify variants
- Suggest canonical forms
- Find cross-year match candidates

**Agent 2-8: Consistency Checkers** (similar division)

### Deliverables
- Name variant mapping table
- Canonical name recommendations
- Cross-year entity match candidates (for future human review)
- Naming consistency report

**Estimated Cost:** ~$50-70

---

## Part 7: Quality Validation & Audit

### Objective
Use LLMs to perform comprehensive quality checks beyond schema validation.

### Quality Checks

**A. Semantic Validity**
- Do coordinates match described locations?
- Are salary values plausible for positions/time periods?
- Are dates historically accurate?
- Do population numbers match area sizes?

**B. Historical Accuracy**
- Cross-reference events with known historical facts
- Validate colonial administrative structures
- Check for anachronisms

**C. Data Completeness**
- Which entities have sparse information?
- Which colonies are under-represented?
- Which years have data quality issues?

**D. Extraction Quality**
- Random sampling of entities
- LLM re-reads source and verifies extraction accuracy
- Identify systematic extraction errors

### Parallel Execution Plan: 8 Agents

**Agent 1: Quality Auditor 1867-1880**
- Sample 10% of entities randomly
- Re-read source documents
- Verify extracted data accuracy
- Flag discrepancies

**Agent 2-8: Quality Auditors** (similar division)

### Deliverables
- Quality audit report per year
- Accuracy metrics (% entities verified correct)
- Discrepancy log (what needs correction)
- Systematic error pattern identification

**Estimated Cost:** ~$60-80

---

## Part 8: Data Enrichment (If Budget Remains)

### Optional Enhancements

**A. Historical Context Addition**
- Add brief historical context to events
- Link events to broader historical movements
- Add "significance" field with LLM-generated summaries

**B. Modern Equivalents**
- Currency conversion recommendations (historical £ → modern £)
- Modern place name mapping (Ceylon → Sri Lanka)
- Administrative structure equivalents

**C. Temporal Extent Inference**
- Infer start/end dates for positions from context
- Build career timelines
- Identify gaps in records

### Parallel Execution Plan: 8 Agents (if budget allows)

**Estimated Cost:** ~$40-60 (optional)

---

## Execution Timeline & Sequencing

### Phase A: Foundation (Run First) - ~3 hours
**Sequential execution required:**
1. Phase 2 Enum Mapping (must complete before other work)

### Phase B: Core Enhancements (Run in Parallel) - ~6-8 hours
**Launch all agents simultaneously:**
- 8 Provenance Linking agents
- 8 Entity Enhancement agents
- 8 Relationship Validation agents

### Phase C: Advanced Features (Run in Parallel) - ~4-6 hours
**Launch all agents simultaneously:**
- 8 Toponym Grounding agents
- 8 Consistency Checking agents

### Phase D: Quality Assurance (Run Last) - ~2-3 hours
**After all enhancements complete:**
- 8 Quality Audit agents

### Total Estimated Runtime: 15-20 hours (with parallelization)
### Total Estimated Cost: $530-$670

**Recommendation:** Stay within $600 budget by:
- Prioritizing Part 1 (Provenance) and Part 2 (Toponyms)
- Completing Part 3 (Enum Mapping)
- Executing Part 4 (Entity Enhancement) fully
- Executing Parts 5-7 based on remaining budget
- Skipping Part 8 (optional enrichment)

---

## Infrastructure & Tooling

### Required Files

```
colonial_office_list/
├── agents/
│   ├── provenance_linker.py          # NEW: Add provenance to entities
│   ├── toponym_grounder.py           # NEW: Link places to Wikidata/Geonames
│   ├── entity_enhancer.py            # NEW: Fill missing data
│   ├── relationship_validator.py     # NEW: Validate/enhance relationships
│   ├── consistency_checker.py        # NEW: Cross-year standardization
│   └── quality_auditor.py            # NEW: LLM-powered quality checks
├── correctors/
│   └── phase2_enum_mapper.py         # EXISTS: Ready to execute
├── schemas/
│   ├── kg_schema_v2.py              # NEW: Enhanced schema with provenance/LOD
│   └── kg_schema.py                  # EXISTS: Current schema
├── knowledge_graph_extracts_v2/      # EXISTS: Current KG files
├── knowledge_graph_extracts_v3/      # NEW: Enhanced output directory
├── reports/
│   ├── provenance_coverage.md        # NEW: Provenance linking results
│   ├── toponym_grounding.md          # NEW: LOD linking results
│   ├── entity_enhancement.md         # NEW: Missing data fill results
│   ├── relationship_validation.md    # NEW: Relationship quality
│   ├── consistency_report.md         # NEW: Cross-year standardization
│   ├── quality_audit.md              # NEW: Quality verification
│   └── FINAL_V3_SUMMARY.md          # NEW: Overall results
└── human_review/                     # NEW: Queues for post-credit review
    ├── lod_review_queue.json         # Medium-confidence matches
    ├── entity_resolution_queue.json  # Cross-year entity matches
    └── quality_flags.json            # Items needing manual review
```

### Python Dependencies

```bash
pip install anthropic pydantic requests SPARQLWrapper python-dateutil fuzzywuzzy
```

### API Keys Required
- `ANTHROPIC_API_KEY` - For all LLM agent work
- Wikidata SPARQL endpoint (free, no key)
- GeoNames API username (free tier, register at geonames.org)

---

## Success Metrics

### Provenance Coverage
- Target: **100%** of entities have source file + line numbers
- Metric: Count entities with provenance / total entities

### Toponym Grounding
- Target: **90%** of place entities linked to Wikidata/Geonames
- High confidence links: **70%+**
- Medium confidence (needs review): **20%**
- Low/no match (LINCS candidates): **10%**

### Validation Errors
- Current: 12,951 errors
- Target: **<2,000 errors** (85% reduction)
- Breakdown: enum errors -66%, missing fields -80%, other -50%

### Data Completeness
- Salary data: **80%+** of position entities have salary information
- Honors data: **90%+** of honors identified and extracted
- Normalized dates: **95%+** of dates converted to ISO-8601
- Relationships: **50%+** increase in relationship count

### Quality Verification
- Sample validation accuracy: **95%+** (spot-check verification)
- Provenance accuracy: **90%+** (correct source line numbers)
- LOD match accuracy (high confidence): **95%+**

---

## Risk Mitigation

### Risk 1: LLM API Costs Exceed Budget
**Mitigation:**
- Track costs per agent task in real-time
- Prioritize high-value tasks (provenance, toponyms) first
- Stop lower-priority tasks if approaching budget limit
- Use Claude Haiku (cheaper) for simple tasks, Sonnet for complex

### Risk 2: LLM Hallucinations / Errors
**Mitigation:**
- All provenance links verified by attempting to read source file
- All LOD links require confidence scores
- Schema validation runs after every enhancement
- Quality audit agents sample-check other agents' work
- Human review queues for medium/low confidence items

### Risk 3: Processing Time Exceeds Available Time
**Mitigation:**
- Maximum parallelization (8 agents per phase)
- Start highest-priority tasks first
- Agents work independently (no blocking dependencies within phase)
- Save progress incrementally (can resume if interrupted)

### Risk 4: Breaking Existing Valid Data
**Mitigation:**
- Never modify original v1 files
- All enhancements create v3 files
- Schema validation before and after each modification
- Git commits after each phase completion
- Ability to rollback to v2 at any time

---

## Deliverables Checklist

**Code & Infrastructure:**
- [ ] 6 new agent scripts (provenance, toponym, entity, relationship, consistency, quality)
- [ ] Enhanced schema v3 with provenance/LOD fields
- [ ] Migration script (v2 → v3)
- [ ] Master orchestrator script (launch all agents)

**Enhanced Data:**
- [ ] 62 KG files (v3) with provenance on all entities
- [ ] 62 KG files with LOD links on groundable places
- [ ] 62 KG files with enum errors reduced 66%
- [ ] 62 KG files with missing fields reduced 80%
- [ ] 62 KG files with validated relationships

**Reports:**
- [ ] Provenance coverage report
- [ ] Toponym grounding report (with coverage stats)
- [ ] Entity enhancement report (missing fields filled)
- [ ] Relationship validation report
- [ ] Cross-year consistency report
- [ ] Quality audit report (accuracy verification)
- [ ] Final V3 summary (overall improvements)

**Human Review Queues:**
- [ ] LOD review queue (medium-confidence matches)
- [ ] Entity resolution queue (cross-year match candidates)
- [ ] Quality flags (items needing manual review)
- [ ] LINCS candidates (entities without existing PIDs)

---

## Next Steps (Immediate Actions)

1. **Review and approve this plan** with user
2. **Set up infrastructure**:
   - Create agent scripts directory
   - Create enhanced schema v3
   - Set up output directories
   - Verify API keys

3. **Execute Phase A** (Sequential):
   - Run Phase 2 enum mapper on all 62 files
   - Generate enum mapping report
   - Commit results

4. **Execute Phase B** (Parallel - 24 agents):
   - Launch 8 provenance linking agents
   - Launch 8 entity enhancement agents
   - Launch 8 relationship validation agents
   - Monitor progress and costs

5. **Execute Phase C** (Parallel - 16 agents):
   - Launch 8 toponym grounding agents
   - Launch 8 consistency checking agents

6. **Execute Phase D** (Parallel - 8 agents):
   - Launch 8 quality audit agents

7. **Generate final reports and commit**

---

## Conclusion

This plan transforms the Colonial Office List knowledge graph from a proof-of-concept extraction into a production-grade historical dataset suitable for academic research. By leveraging **massive LLM parallelization**, we achieve in 2 days what would take weeks of manual work:

✅ **Complete provenance** - Every fact traceable to source
✅ **Linked open data** - Integration with Wikidata/Geonames
✅ **High quality** - 85%+ error reduction
✅ **Entity resolution ready** - Cross-year match candidates prepared
✅ **Research-ready** - Human review queues for final verification

**The key principle:** Use LLMs for what they're best at (semantic understanding, pattern matching, text analysis) while maintaining rigor through validation, confidence scoring, and human review queues for uncertain decisions.

**Budget allocation:** $530-600 across 8 improvement categories, 80+ parallel agent tasks, processing 68MB of historical data across 62 years.

---

**Plan Status:** ✅ READY FOR EXECUTION
**Next:** User approval to begin
