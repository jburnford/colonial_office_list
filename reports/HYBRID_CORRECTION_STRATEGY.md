# Hybrid LLM + Python Correction Strategy

**Date:** 2025-11-17
**Approach:** Leverage LLM semantic understanding + Python determinism

---

## Core Principle: Best Tool for Each Job

### Python Excels At:
- ✅ Type conversion (int → string)
- ✅ Schema validation
- ✅ Pattern matching and consistency checks
- ✅ Batch processing with guarantees
- ✅ Rollback and audit logging

### LLM Agents Excel At:
- ✅ Semantic understanding (is "protectorate" a territory or colony?)
- ✅ Context-aware inference (inferring location from department names)
- ✅ Handling ambiguous data (salary ranges, partial dates)
- ✅ Historical terminology interpretation
- ✅ Entity type classification
- ✅ Quality assessment and anomaly detection

---

## Hybrid Correction Pipeline

### Stage 1: Python Safety Net (Deterministic Fixes)

**What:** Pure type/format corrections with zero semantic change

**Python Tasks:**
1. **Type Conversion**
   - Integer years → String years
   - Validate pattern: `^\d{4}$`

2. **Metadata Inference**
   - Extract year from filename
   - Build source_directory path
   - Add extraction_date from file mtime

3. **Validation Wrapper**
   - Validate before correction
   - Validate after correction
   - Rollback if validation worsens

**Confidence:** 99%
**Risk:** Minimal (no semantic changes)

---

### Stage 2: LLM Agent Semantic Corrections (Intelligent Fixes)

**What:** Use LLM agents to understand context and make intelligent corrections

#### Task 2A: Enum Value Mapping Agent

**Prompt Strategy:**
```
You are a historical data specialist. Given an entity with type "protectorate",
analyze the context (location, year, description) and determine the appropriate
schema-compliant type from: [colony, territory, dependency, ...]

Provide:
1. Recommended type
2. Confidence score (0-1)
3. Reasoning
4. Alternative if uncertain
```

**Process:**
- Agent analyzes each invalid enum value in context
- Generates correction suggestion with confidence
- High confidence (>0.9): Auto-apply
- Medium confidence (0.7-0.9): Review queue
- Low confidence (<0.7): Flag for human review

**Confidence:** 85% for auto-apply cases
**Risk:** Low (only high-confidence applied, all logged)

#### Task 2B: Missing Location Inference Agent

**Prompt Strategy:**
```
Given a position record with missing location:
- Person: "John Smith"
- Position: "Colonial Secretary"
- Department: "Colonial Secretary's Office"
- Year: 1890
- Available colonies in this year: [list from file metadata]

Infer the most likely location based on:
1. Other positions this person holds
2. Department name conventions
3. Historical context

Provide confidence score and reasoning.
```

**Process:**
- Agent reads full file context
- Analyzes patterns (same person's other positions)
- Makes educated inference
- Only applies if confidence >0.95

**Confidence:** 75% for high-confidence cases
**Risk:** Medium (creates human review queue for verification)

#### Task 2C: Salary Parsing Agent

**Prompt Strategy:**
```
Parse this salary value into structured format:
- Input: "£500-600 per annum"
- Expected output: {
    amount: 550,  // midpoint for ranges
    currency: "£",
    period: "annual",
    notes: "range: £500-600"
  }

Handle:
- Ranges: take midpoint, note in metadata
- Circa/approximate: flag uncertainty
- Multiple currencies: preserve all
- Non-numeric: flag for human review
```

**Process:**
- Agent parses complex salary strings
- Extracts structured data
- Flags ambiguous cases
- Preserves original in notes field

**Confidence:** 80%
**Risk:** Low (original preserved, changes documented)

---

### Stage 3: Agent Cross-Validation (Quality Assurance)

**What:** Multiple agents review each other's work

**Process:**
1. **Correction Agent** makes changes
2. **Validation Agent** reviews changes independently
3. **Conflict Resolution Agent** handles disagreements

**Example:**
```
Agent 1: "Change 'protectorate' to 'territory'" (confidence: 0.85)
Agent 2: Reviews context and agrees/disagrees
If disagree: Flag for human review
If agree: Confidence boost to 0.95 → Auto-apply
```

**Confidence:** 90% (consensus increases reliability)
**Risk:** Very Low (multiple perspectives reduce errors)

---

### Stage 4: Critical Year Deep Analysis (Re-extraction via LLM)

**What:** For the 5 worst years (1920, 1909, 1928, 1949, 1890), use LLM agents to re-extract from source

**Why LLM Re-extraction:**
- Original extractions have structural issues
- LLMs can understand source format better than broken JSON
- Can apply lessons from valid years (1886, 1932)

**Process:**
1. **Analysis Agent** studies why extraction failed
2. **Template Agent** examines valid years (1886, 1932) for patterns
3. **Re-extraction Agent** processes source files with corrected methodology
4. **Validation Agent** ensures new extraction is schema-compliant

**Target Years:**
- 1920 (14,219 errors) - **Priority 1**
- 1909 (5,777 errors) - **Priority 2**
- 1928 (2,485 errors) - **Priority 3**
- 1949 (1,044 errors) - **Priority 4**
- 1890 (1,974 errors) - **Priority 5** (might be fixable with type conversion)

**Confidence:** 85% (LLMs excel at extraction)
**Risk:** Low (validate against schema before accepting)

---

## Comprehensive Workflow

### Phase 1: Investigation & Planning (Today)

**Parallel Agent Tasks:**

**Agent 1: Deep Dive - Compare 1890 (broken) vs 1886 (valid)**
- What's different?
- Why did 1890 fail?
- Is it fixable or needs re-extraction?

**Agent 2: Best Practices Analysis - Study Valid Years**
- Analyze 1886, 1915, 1923, 1932
- Document extraction patterns
- Create reference template

**Agent 3: Critical Year Forensics - Investigate 1920**
- Why 14,219 errors?
- What went wrong structurally?
- Can it be fixed or must re-extract?

**Agent 4: Error Pattern Analysis**
- Categorize all 28,150 errors
- Identify which are automatable (Python vs LLM vs manual)
- Build correction roadmap

**Deliverables:**
- Investigation reports for each critical year
- Best practices document from valid years
- Detailed correction roadmap with confidence levels

---

### Phase 2: Safe Corrections (Week 1)

**Python Pipeline:**
1. Type conversion (year fields)
2. Metadata population
3. Exact duplicate removal

**Validation:**
- Test on 4 valid years first (should remain valid)
- Test on 5 sample invalid years
- Manual review of changes

**Expected Impact:** ~2,500 errors fixed (9% reduction)

---

### Phase 3: LLM Semantic Corrections (Week 1-2)

**Agent-Based Pipeline:**

**Correction Agents (Parallel):**
- Enum mapping agent (process all invalid enum errors)
- Salary parsing agent (process all salary errors)
- Location inference agent (process missing locations)

**Each agent:**
1. Processes assigned error type
2. Generates correction suggestions
3. Assigns confidence scores
4. Creates review queue for uncertain items

**Validation Agents (Parallel):**
- Cross-validate high-confidence suggestions
- Flag conflicts for human review

**Expected Impact:** ~6,500 errors fixed (23% reduction)

---

### Phase 4: Critical Year Re-extraction (Week 2-3)

**LLM Re-extraction Pipeline:**

For each of 5 critical years:
1. **Analysis Agent** - Understand source data format
2. **Template Agent** - Apply lessons from valid years
3. **Extraction Agent** - Re-extract with correct methodology
4. **Validation Agent** - Validate against schema
5. **Comparison Agent** - Compare to original, flag major discrepancies

**Expected Impact:** ~19,000 errors fixed (67% reduction)

---

### Phase 5: Human Review Queue (Week 3-4)

**Items for Human Review:**
1. Low-confidence LLM suggestions (<0.7)
2. Agent disagreements
3. Unusual patterns flagged by validation
4. Remaining complex structural issues

**Interface:**
```json
{
  "review_item_id": "rev_001",
  "file": "1890_extracted.json",
  "issue_type": "enum_mapping",
  "current_value": "crown_colony_protectorate",
  "agent_suggestion": "territory",
  "confidence": 0.68,
  "reasoning": "Historical records indicate this was a protectorate...",
  "context": {
    "entity_name": "British Somaliland",
    "year": 1890
  },
  "human_decision": null,
  "requires_research": false
}
```

---

## Safety Mechanisms

### 1. Never Modify Originals
```
knowledge_graph_extracts/           (v1 - original, READ ONLY)
knowledge_graph_extracts_v2/        (v2 - corrected, working copy)
knowledge_graph_extracts_v2_backup/ (rollback point)
```

### 2. Complete Audit Trail
```json
{
  "correction_log": {
    "file": "1890_extracted.json",
    "timestamp": "2025-11-17T15:30:00Z",
    "corrections_applied": [
      {
        "type": "type_conversion",
        "field": "entities.people[0].positions[0].year",
        "old_value": 1890,
        "new_value": "1890",
        "method": "python_script",
        "confidence": 1.0
      },
      {
        "type": "enum_mapping",
        "field": "entities.places[5].type",
        "old_value": "protectorate",
        "new_value": "territory",
        "method": "llm_agent_semantic",
        "confidence": 0.92,
        "agent_reasoning": "..."
      }
    ]
  }
}
```

### 3. Validation at Every Step
```python
# Before ANY correction
validate_original()

# After EACH correction
validate_corrected()

# If validation worsens:
rollback()
log_failure()
add_to_human_review_queue()
```

### 4. Conservative Confidence Thresholds

| Confidence | Action |
|------------|--------|
| 0.95-1.0   | Auto-apply |
| 0.80-0.94  | Auto-apply + log for spot-check |
| 0.70-0.79  | Human review recommended |
| < 0.70     | Human review required |

---

## Expected Outcomes

### Error Reduction Projections

| Phase | Method | Errors Fixed | New Errors | Net Reduction |
|-------|--------|--------------|------------|---------------|
| Phase 2 | Python | 2,500 | 0 | 2,500 |
| Phase 3 | LLM Agents | 6,500 | ~100* | 6,400 |
| Phase 4 | Re-extraction | 19,000 | ~200* | 18,800 |
| **Total** | **Hybrid** | **28,000** | **~300** | **27,700** |

*Conservative estimate; likely lower with validation

### Validation Success Projection

| Metric | Current | After Corrections | Target |
|--------|---------|-------------------|--------|
| Valid files | 4 (6.6%) | 52 (85%) | 49 (80%) |
| Total errors | 28,150 | ~450 | <1,000 |
| Avg errors/file | 461 | 7 | <20 |

---

## Why This Hybrid Approach Works

### Python Provides:
- ✅ **Determinism** - Same input always produces same output
- ✅ **Speed** - Fast batch processing
- ✅ **Validation** - Strict schema enforcement
- ✅ **Audit Trail** - Every change logged

### LLM Agents Provide:
- ✅ **Semantic Understanding** - Interprets historical terminology
- ✅ **Context Awareness** - Understands relationships between entities
- ✅ **Flexibility** - Handles messy, ambiguous data
- ✅ **Explanation** - Provides reasoning for changes

### Together They Provide:
- ✅ **Best of Both Worlds** - Deterministic where possible, intelligent where needed
- ✅ **Safety** - Python validates LLM output
- ✅ **Transparency** - All changes explained and logged
- ✅ **Accuracy** - Human-level understanding with machine consistency

---

## Next Steps - Proposed Approach

**Today (Investigation Phase):**
1. ✅ Launch 4 parallel investigation agents
2. ✅ Deep dive: 1890 vs 1886 comparison
3. ✅ Forensics: Why did 1920 fail so badly?
4. ✅ Document best practices from valid years
5. ✅ Build detailed correction roadmap

**This Week (Implementation):**
1. Build Python safety pipeline
2. Build LLM correction agents
3. Test on samples (5 files)
4. Show you results before bulk processing

**Next Week (Execution):**
1. Apply Python corrections (with your approval)
2. Run LLM agents (with confidence thresholds)
3. Generate human review queue
4. Begin critical year re-extractions

---

**Ready to proceed?** I can launch the 4 investigation agents now to give us detailed insights before we start any corrections.
