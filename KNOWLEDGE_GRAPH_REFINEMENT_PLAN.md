# Knowledge Graph Refinement Plan
## Building a State-of-the-Art Historical Knowledge Graph

**Version:** 1.0
**Date:** 2025-11-17
**Status:** Planning Phase

---

## Executive Summary

This plan addresses the critical refinements needed to transform our existing 61-year knowledge graph extraction (1867-1966) into a robust, academically rigorous, and computationally useful dataset. Based on expert review, we focus on five key areas:

1. **Data Validation & Quality Assurance** - Python-based schema validation and error detection
2. **Schema Enhancement** - Adding provenance, normalized dates, and LOD recommendations
3. **Entity Resolution Strategy** - Preparing for human-in-the-loop inter-year linking
4. **Linked Open Data Integration** - Recommendations for Wikidata/Geonames with human verification
5. **LINCS Dataset Preparation** - Building PID dataset for entities lacking existing identifiers

**Guiding Principle:** Accuracy over speed. No false positives. Human verification for critical decisions.

---

## Part 1: Python Validation & Quality Assurance Framework

### 1.1 Schema Validation System

**Objective:** Ensure 100% of extracted JSON files conform to schema and catch structural errors.

**Implementation:**
- Use **Pydantic** for strict schema validation with type checking
- Validate all 61 existing extraction files
- Generate detailed error reports for each file
- Create automatic fix suggestions where possible

**Deliverables:**
1. `schemas/kg_schema.py` - Pydantic models matching JSON schema
2. `validators/schema_validator.py` - Validation engine
3. `reports/validation_report_[year].json` - Per-year validation results
4. `reports/VALIDATION_SUMMARY.md` - Aggregated quality metrics

**Quality Checks:**
- Required fields present
- Data types correct (strings, numbers, arrays)
- Enum values valid
- ID format consistency
- Relationship integrity (source/target IDs exist)
- No orphaned entities
- Currency/unit format validation
- Date format validation

### 1.2 Data Quality Auditing

**Objective:** Identify inconsistencies, anomalies, and potential errors in extracted data.

**Checks to Implement:**

**A. Entity-Level Checks**
- Duplicate entity detection (same name, location, year)
- Suspicious salary values (outliers, negative numbers, missing currency)
- Invalid coordinate formats
- Person records without positions
- Positions without location or year
- Institutions without members or composition

**B. Relationship Checks**
- Dangling references (relationship points to non-existent entity)
- Circular relationships
- Duplicate relationships
- Missing temporal information
- Geographically impossible relationships (e.g., person governs two distant colonies simultaneously)

**C. Cross-Year Consistency**
- Colony name spelling variations across years
- Position title variations (normalize for analysis)
- Currency standardization issues
- Geographic entity name drift

**D. Statistical Anomaly Detection**
- Unusual entity counts per year
- Salary distributions with extreme outliers
- Missing data patterns

**Deliverables:**
1. `auditors/entity_auditor.py` - Entity-level quality checks
2. `auditors/relationship_auditor.py` - Relationship integrity checks
3. `auditors/cross_year_auditor.py` - Inter-year consistency analysis
4. `reports/QUALITY_AUDIT_REPORT.md` - Comprehensive quality report
5. `reports/anomalies_[year].json` - Flagged issues requiring review

### 1.3 Automated Correction System

**Objective:** Fix deterministic errors programmatically without introducing false positives.

**Safe Corrections:**
- Standardize date formats (preserve original in provenance)
- Normalize currency symbols (£ vs GBP, $ vs USD)
- Fix obvious typos in enum values (e.g., "coloney" → "colony")
- Add missing metadata fields (extraction_date, source_directory)
- Generate missing IDs following consistent pattern
- Remove exact duplicates

**Human-Review Required:**
- Entity merging/deduplication
- Ambiguous date interpretations
- Geographic coordinate corrections
- Person name disambiguation
- Relationship type corrections

**Deliverables:**
1. `correctors/safe_corrector.py` - Automated fixes only
2. `correctors/review_queue.py` - Generate human review queue
3. `reports/corrections_applied.json` - Log of automated changes
4. `human_review/review_queue.json` - Issues requiring manual review

---

## Part 2: Enhanced Schema with Provenance & LOD

### 2.1 Provenance Tracking

**Rationale:** Every extracted fact must be traceable to its source for academic rigor.

**Schema Additions:**

```json
{
  "provenance": {
    "source_file": "output_2/1890/british_honduras.md",
    "section": "Civil Establishment - Colonial Secretary",
    "line_range": "45-52",
    "extraction_confidence": "high",
    "extraction_method": "llm_agent_gpt4",
    "extracted_date": "2025-11-17T10:30:00Z",
    "verified_by_human": false,
    "verification_date": null,
    "notes": "Salary extracted from tabular format"
  }
}
```

**Application:** Add provenance field to:
- Every entity (people, places, institutions, etc.)
- Every relationship
- Every economic data point
- Every event

**Implementation Strategy:**
- Retroactive provenance inference from extraction patterns
- Re-extraction with provenance capture for ambiguous cases
- Agent-based provenance annotation where automated inference insufficient

### 2.2 Normalized Dates

**Rationale:** Enable computational analysis while preserving historical authenticity.

**Schema Enhancement:**

```json
{
  "date": "21st day of January, 1872",
  "normalized_date": {
    "iso8601": "1872-01-21",
    "precision": "day",
    "certainty": "explicit",
    "parsing_notes": "Full date provided in source"
  }
}
```

**Date Precision Levels:**
- `year` - Only year known (1890)
- `month` - Month and year (1890-06)
- `day` - Full date (1890-06-15)
- `circa` - Approximate (~1890)
- `range` - Date range (1889-1891)

**Implementation:**
- Python date parser (dateutil) for automated normalization
- Preserve ALL original date strings
- Flag ambiguous dates for human review (e.g., "6/7/1890" - UK vs US format)
- Add certainty field for inferred dates

### 2.3 Linked Open Data (LOD) Recommendations

**Rationale:** Ground entities to global identifiers where possible, enabling cross-dataset research.

**Schema Addition:**

```json
{
  "lod_recommendations": {
    "wikidata": {
      "qid": "Q191",
      "label": "British Honduras / Belize",
      "confidence": 0.95,
      "match_method": "name_exact",
      "verified_by_human": false,
      "verification_date": null
    },
    "geonames": {
      "geonames_id": "3582678",
      "name": "Belize",
      "latitude": 17.25,
      "longitude": -88.75,
      "confidence": 0.92,
      "verified_by_human": false
    },
    "lincs_candidate": false,
    "review_priority": "medium"
  }
}
```

**Target Entities for LOD Linking:**
1. **Places** (Priority 1)
   - Colonies/territories → Wikidata + Geonames
   - Cities/towns → Geonames
   - Geographic features → Wikidata

2. **People** (Priority 2)
   - Notable officials → Wikidata (governors, chief justices, etc.)
   - LINCS candidates for prosopography

3. **Institutions** (Priority 3)
   - Major institutions → Wikidata
   - Courts, councils → Wikidata

**Matching Strategy:**
1. **Automated Matching** (Recommendations Only)
   - Exact name match → High confidence (0.8-1.0)
   - Fuzzy name match + context (location, dates) → Medium confidence (0.5-0.8)
   - Name match with conflicts → Low confidence (< 0.5, flag for review)

2. **Context Enrichment**
   - Use temporal constraints (entity must exist in time period)
   - Use geographic constraints (must be in correct region)
   - Use administrative constraints (colony must be British in period)

3. **Human Verification Queue**
   - High confidence matches → Optional verification
   - Medium confidence → Recommended verification
   - Low confidence → Required verification
   - Conflicting matches → Required human decision

**Implementation:**
1. `linkers/wikidata_linker.py` - Query Wikidata SPARQL endpoint
2. `linkers/geonames_linker.py` - Query Geonames API
3. `linkers/confidence_scorer.py` - Calculate match confidence
4. `human_review/lod_review_queue.json` - Verification queue
5. `reports/LOD_LINKING_REPORT.md` - Coverage statistics

### 2.4 LINCS Dataset Preparation

**Objective:** Build a dataset of colonial entities for LINCS (Linked Infrastructure for Networked Cultural Scholarship).

**Candidates for LINCS:**
- Historical place names without modern Wikidata/Geonames entries
- Colonial officials without existing PIDs
- Historical institutions specific to colonial administration
- Administrative divisions and boundaries

**LINCS Record Format:**

```json
{
  "lincs_entity": {
    "entity_type": "person|place|institution",
    "canonical_name": "Normalized name form",
    "variant_names": ["Historical spelling 1", "Historical spelling 2"],
    "temporal_extent": {
      "start_year": 1867,
      "end_year": 1905,
      "certainty": "mentioned_in_sources"
    },
    "geographic_context": "British Honduras",
    "description": "Brief description from sources",
    "evidence": [
      {
        "source": "Colonial Office List 1890",
        "citation": "output_2/1890/british_honduras.md, lines 45-52"
      }
    ],
    "relationships": ["Related entity IDs"],
    "proposed_pid": "lincs:colonial_office_person_001234"
  }
}
```

**Deliverables:**
1. `lincs/candidate_generator.py` - Identify LINCS candidates
2. `lincs/lincs_exporter.py` - Export to LINCS-compatible format
3. `lincs_candidates/` - Directory of candidate entities
4. `reports/LINCS_PROPOSAL.md` - Dataset proposal for LINCS integration

---

## Part 3: Entity Resolution Strategy

### 3.1 The Challenge

**Problem:** Is "Governor F. Smith" in 1870 the same person as "Governor Frederick Smith, K.C.M.G." in 1875?

**Scale:** ~50,000+ person entities across 61 years requiring potential linkage.

### 3.2 Intra-Year Resolution (Automated)

**Within a single year:** Same person mentioned in multiple departments should have same ID.

**Current Status:** Already handled in extraction process (single year = single ID space).

**Verification:** Audit for missed intra-year duplicates.

**Implementation:**
1. `resolvers/intra_year_resolver.py` - Find same person in different departments
2. Matching criteria: Exact name + same location + same year
3. Auto-merge if criteria met

### 3.3 Inter-Year Resolution (Human-in-the-Loop)

**Approach:** Prepare high-quality candidate matches for human review.

**Phase 1: Candidate Generation (Automated)**

**A. Simple Matches (High Confidence)**
- Exact name + consecutive years + same colony + same/similar position
- Example: "Governor John Smith" in Jamaica 1890 → "Governor John Smith" in Jamaica 1891

**B. Probable Matches (Medium Confidence)**
- Similar name + consecutive years + same colony + position progression
- Example: "Acting Governor J. Smith" 1890 → "Governor John Smith, K.C.M.G." 1891

**C. Possible Matches (Low Confidence)**
- Name similarity + overlapping locations + plausible career trajectory
- Example: "Lt. Frederick Jones" (Military) 1885 → "Major F. Jones" (Colonial Secretary) 1895

**Matching Signals:**
1. **Name similarity** (Levenshtein distance, initials matching)
2. **Temporal proximity** (consecutive or nearby years)
3. **Geographic continuity** (same colony or regional transfer)
4. **Career plausibility** (promotion patterns, age constraints)
5. **Honors accumulation** (new honors added, never removed)
6. **Unique names** (rare surnames = higher confidence)

**Phase 2: Human Review Interface**

**Review Queue Format:**

```json
{
  "candidate_match": {
    "match_id": "match_candidate_12345",
    "confidence": 0.75,
    "entity_1": {
      "id": "person_1890_000234",
      "name": "F. Smith",
      "year": 1890,
      "position": "Acting Governor",
      "location": "Jamaica",
      "honors": []
    },
    "entity_2": {
      "id": "person_1891_000189",
      "name": "Frederick Smith",
      "year": 1891,
      "position": "Governor",
      "location": "Jamaica",
      "honors": ["K.C.M.G."]
    },
    "matching_evidence": {
      "name_similarity": 0.85,
      "temporal_proximity": 1,
      "geographic_match": true,
      "career_plausibility": 0.9,
      "unique_name": false
    },
    "review_status": "pending",
    "reviewer_decision": null,
    "canonical_id": null,
    "review_notes": ""
  }
}
```

**Review Workflow:**
1. System generates candidate matches sorted by confidence
2. Human reviewer sees side-by-side comparison
3. Reviewer marks as: SAME_PERSON | DIFFERENT_PERSON | UNCERTAIN
4. System assigns canonical ID for confirmed matches
5. Uncertain cases flagged for further research

**Implementation:**
1. `resolvers/candidate_matcher.py` - Generate match candidates
2. `resolvers/similarity_scorer.py` - Calculate match confidence
3. `human_review/entity_resolution_queue.json` - Review queue
4. `human_review/resolution_decisions.json` - Human decisions log
5. `resolvers/canonical_id_assigner.py` - Apply human decisions to assign canonical IDs

### 3.4 Canonical ID System

**Strategy:** Use persistent, hierarchical IDs that encode entity type and uniqueness.

**ID Format:**
- **Before resolution:** `person_1890_000234` (year-specific)
- **After resolution:** `canonical_person_000123` (cross-year)

**Properties:**
- Immutable once assigned
- Maps to all year-specific IDs for that entity
- Enables cross-year queries

**Mapping Table:**

```json
{
  "canonical_person_000123": {
    "entity_type": "person",
    "canonical_name": "Frederick Smith",
    "year_instances": [
      {
        "year": 1890,
        "id": "person_1890_000234",
        "name_variant": "F. Smith"
      },
      {
        "year": 1891,
        "id": "person_1891_000189",
        "name_variant": "Frederick Smith"
      }
    ],
    "resolution_confidence": 0.95,
    "verified_by_human": true,
    "verification_date": "2025-11-20"
  }
}
```

---

## Part 4: Implementation Roadmap

### Phase 1: Foundation (Week 1-2)

**Goals:** Set up validation infrastructure and audit existing data.

**Tasks:**
1. Create Python validation framework
   - Pydantic schema models
   - Validation engine
   - Error reporting

2. Run comprehensive audit of 61 extraction files
   - Schema compliance
   - Entity integrity
   - Relationship validity
   - Statistical anomalies

3. Generate quality reports
   - Per-year validation reports
   - Aggregated quality metrics
   - Prioritized fix list

**Deliverables:**
- Working validation system
- Complete quality audit report
- Prioritized issue list

**Agent Usage:**
- Agent 1: Audit years 1867-1900 (parallel)
- Agent 2: Audit years 1901-1930 (parallel)
- Agent 3: Audit years 1931-1966 (parallel)
- Agent 4: Aggregate results and generate summary report

### Phase 2: Schema Enhancement (Week 2-3)

**Goals:** Enhance schema and re-extract/annotate with provenance.

**Tasks:**
1. Update JSON schema with new fields
   - Provenance
   - Normalized dates
   - LOD recommendations
   - LINCS fields

2. Create schema migration scripts
   - Automated field additions
   - Provenance inference
   - Date normalization

3. Apply automated corrections
   - Fix deterministic errors
   - Standardize formats
   - Add missing metadata

**Deliverables:**
- Enhanced JSON schema v2.0
- Migration scripts
- Corrected extraction files
- Correction log

**Agent Usage:**
- Agent 1: Migrate early years (1867-1900) with provenance inference
- Agent 2: Migrate mid years (1901-1930) with provenance inference
- Agent 3: Migrate late years (1931-1966) with provenance inference
- Agent 4: Quality check migrated files

### Phase 3: LOD Linking (Week 3-4)

**Goals:** Generate LOD recommendations for all applicable entities.

**Tasks:**
1. Build LOD linking system
   - Wikidata SPARQL queries
   - Geonames API integration
   - Confidence scoring

2. Run automated linking
   - Link all places to Geonames/Wikidata
   - Link notable people to Wikidata
   - Link major institutions to Wikidata

3. Generate human review queue
   - Medium/low confidence matches
   - Conflicting matches
   - No-match candidates for LINCS

**Deliverables:**
- LOD linking system
- Enhanced extractions with LOD recommendations
- Human review queue (JSON)
- LOD coverage report

**Agent Usage:**
- Agent 1: Link geographic entities (places) to Wikidata + Geonames
- Agent 2: Link people entities to Wikidata (governors, chief justices)
- Agent 3: Link institutional entities to Wikidata
- Agent 4: Generate LINCS candidates for unmatched entities

### Phase 4: Entity Resolution Prep (Week 4-5)

**Goals:** Prepare entity resolution candidates for human review.

**Tasks:**
1. Build candidate matching system
   - Name similarity algorithms
   - Career trajectory analysis
   - Temporal/geographic constraints

2. Generate match candidates
   - High confidence matches (auto-suggest)
   - Medium confidence (review recommended)
   - Low confidence (research needed)

3. Create human review interface spec
   - Review queue format
   - Decision capture format
   - Canonical ID assignment logic

**Deliverables:**
- Candidate matching system
- Entity resolution queue (JSON)
- Review interface specification
- Estimated review time/effort

**Agent Usage:**
- Agent 1: Generate person entity match candidates (high confidence)
- Agent 2: Generate place entity match candidates (handle name variations)
- Agent 3: Generate institution match candidates
- Agent 4: Score and prioritize review queue

### Phase 5: Quality Verification (Week 5-6)

**Goals:** Final validation and prepare for human review phases.

**Tasks:**
1. Run comprehensive validation on enhanced dataset
2. Generate final quality metrics
3. Create human review documentation
   - Review guidelines
   - Decision criteria
   - Example cases

4. Export review queues
   - Entity resolution queue
   - LOD verification queue
   - Anomaly review queue

**Deliverables:**
- Final quality report
- Human review documentation
- Review queue exports
- Dataset statistics

---

## Part 5: Quality Metrics & Success Criteria

### Validation Metrics

**Schema Compliance:**
- Target: 100% of files validate against schema
- Current: Unknown (to be measured)

**Entity Integrity:**
- Target: 0 orphaned entities
- Target: 0 dangling relationships
- Target: < 1% duplicate entities per year

**Provenance Coverage:**
- Target: 100% of entities have provenance
- Target: 100% of relationships have provenance

**Date Normalization:**
- Target: 95%+ of dates successfully normalized
- Target: < 5% requiring human disambiguation

### LOD Linking Metrics

**Place Entities:**
- Target: 90%+ colonies/territories linked to Wikidata + Geonames
- Target: 70%+ cities/towns linked to Geonames
- Target: < 10% LINCS candidates

**Person Entities:**
- Target: 80%+ governors linked to Wikidata
- Target: 50%+ senior officials linked to Wikidata
- Target: Remaining persons documented for LINCS

**Confidence Distribution:**
- High confidence (0.8-1.0): 60%+
- Medium confidence (0.5-0.8): 30%
- Low confidence (< 0.5): < 10%

### Entity Resolution Metrics

**Match Candidate Quality:**
- Target: 80%+ high confidence candidates are true matches (precision)
- Target: 90%+ true matches are in candidate set (recall)

**Human Review Efficiency:**
- Target: < 5 minutes per match decision
- Target: Clear decision criteria for 95%+ cases

---

## Part 6: Tooling & Infrastructure

### Python Dependencies

```python
# requirements.txt
pydantic==2.5.0           # Schema validation
python-dateutil==2.8.2    # Date parsing
requests==2.31.0          # API calls
fuzzywuzzy==0.18.0        # String similarity
python-Levenshtein==0.21.1 # Fast string distance
SPARQLWrapper==2.0.0      # Wikidata queries
jsonschema==4.20.0        # JSON validation
pandas==2.1.0             # Data analysis
numpy==1.24.0             # Numerical operations
```

### Project Structure

```
colonial_office_list/
├── schemas/
│   ├── kg_schema.py              # Pydantic models
│   └── kg_schema_v2.json         # Enhanced JSON schema
├── validators/
│   ├── schema_validator.py       # Schema validation
│   └── integrity_checker.py      # Relationship integrity
├── auditors/
│   ├── entity_auditor.py         # Entity-level checks
│   ├── relationship_auditor.py   # Relationship checks
│   └── cross_year_auditor.py     # Inter-year consistency
├── correctors/
│   ├── safe_corrector.py         # Automated fixes
│   └── review_queue_gen.py       # Generate human review queue
├── linkers/
│   ├── wikidata_linker.py        # Wikidata integration
│   ├── geonames_linker.py        # Geonames integration
│   └── confidence_scorer.py      # Match confidence scoring
├── resolvers/
│   ├── intra_year_resolver.py    # Within-year deduplication
│   ├── candidate_matcher.py      # Inter-year matching
│   ├── similarity_scorer.py      # Entity similarity
│   └── canonical_id_assigner.py  # ID assignment
├── lincs/
│   ├── candidate_generator.py    # LINCS entity identification
│   └── lincs_exporter.py         # LINCS format export
├── reports/
│   ├── VALIDATION_SUMMARY.md     # Overall quality metrics
│   ├── QUALITY_AUDIT_REPORT.md   # Detailed audit results
│   ├── LOD_LINKING_REPORT.md     # LOD coverage stats
│   └── LINCS_PROPOSAL.md         # LINCS dataset proposal
├── human_review/
│   ├── entity_resolution_queue.json  # Match candidates
│   ├── lod_review_queue.json         # LOD verifications
│   ├── anomaly_review_queue.json     # Flagged anomalies
│   └── resolution_decisions.json     # Human decisions log
├── knowledge_graph_extracts_v2/
│   ├── 1867_extracted_v2.json    # Enhanced extractions
│   ├── ...
│   └── canonical_entities/
│       ├── canonical_people.json
│       ├── canonical_places.json
│       └── canonical_institutions.json
└── migration/
    ├── v1_to_v2_migrator.py      # Schema migration
    └── migration_log.json         # Migration audit trail
```

---

## Part 7: Risk Mitigation

### Risk 1: Breaking Existing Data

**Mitigation:**
- Never modify original v1 extractions
- All enhancements create v2 versions
- Maintain complete audit trail of changes
- Ability to rollback to v1 at any time

### Risk 2: Introducing False Positives

**Mitigation:**
- Human verification required for all non-deterministic operations
- Clear confidence thresholds for automated suggestions
- Extensive testing on sample data before bulk processing
- Conservative matching criteria (prefer false negatives over false positives)

### Risk 3: LOD Linking Errors

**Mitigation:**
- All LOD links are "recommendations" only
- Confidence scores always provided
- Context validation (temporal, geographic)
- Human verification for medium/low confidence
- Ability to reject automated suggestions

### Risk 4: Entity Resolution Errors

**Mitigation:**
- No automated entity merging across years
- All inter-year linking requires human approval
- Preserve year-specific IDs even after canonical ID assignment
- Reversible decisions (can un-merge if error discovered)

### Risk 5: Schema Migration Failures

**Mitigation:**
- Comprehensive testing on sample files first
- Validation at every migration step
- Rollback capability
- Manual inspection of migrated samples

---

## Part 8: Next Steps

### Immediate Actions (This Session)

1. **Create Python validation framework** (Priority 1)
   - Set up project structure
   - Install dependencies
   - Create Pydantic schema models
   - Build basic validator

2. **Run initial quality audit** (Priority 2)
   - Validate 5-10 sample years
   - Identify common error patterns
   - Generate sample quality report

3. **Design enhanced schema v2** (Priority 3)
   - Add provenance fields
   - Add normalized date fields
   - Add LOD recommendation fields
   - Update JSON schema

### Short-term Goals (Next Session)

1. Complete validation of all 61 years
2. Build automated correction system
3. Implement date normalization
4. Begin LOD linking system development

### Long-term Goals

1. Complete schema migration to v2
2. Generate LOD recommendations for all entities
3. Create entity resolution candidate queue
4. Prepare comprehensive human review documentation
5. Export LINCS candidate dataset

---

## Conclusion

This plan transforms the existing knowledge graph extraction from a proof-of-concept into a production-grade, academically rigorous dataset suitable for:

- **Historical research** - Traceable provenance, preserved original data
- **Computational analysis** - Normalized dates, structured relationships
- **Cross-dataset integration** - LOD links to Wikidata/Geonames
- **Prosopographical research** - Entity resolution across time
- **Linked data ecosystem** - LINCS integration for unique entities

**Key Principles:**
✓ Accuracy over speed
✓ Human verification for critical decisions
✓ Provenance for every fact
✓ Preserve original data while adding computational structure
✓ No false positives - conservative automation

The combination of LLM extraction power with Python validation rigor creates a best-of-both-worlds approach: the flexibility and comprehension of AI with the determinism and reliability of code.

---

**Document Version:** 1.0
**Last Updated:** 2025-11-17
**Next Review:** After Phase 1 completion
