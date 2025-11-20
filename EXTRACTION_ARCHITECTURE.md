# Colonial Office List - People Data Extraction Architecture

## Design Philosophy

**Core Principle:** Use Python for reproducibility and structure, use LLM agents for intelligence and handling irregularities.

### Why Hybrid?

**Python Strengths:**
- Reproducible, deterministic
- No hallucination risk
- Fast batch processing
- Clear audit trail
- Easy to version control

**Python Limitations:**
- Regex can't handle all variations
- Can't adapt to OCR errors
- Struggles with context-dependent extraction
- Brittle with format changes

**LLM Agent Strengths:**
- Handles OCR errors intelligently
- Understands context and structure
- Adapts to format variations
- Can resolve ambiguities
- Natural language understanding

**LLM Agent Limitations:**
- Non-deterministic (can vary between runs)
- Potential hallucinations
- Slower than regex
- Harder to debug
- Cost at scale

### Solution: Divide & Conquer

**Python handles:**
1. File management and orchestration
2. Simple, regular patterns (90% of extractions)
3. Data validation and filtering
4. JSON output and provenance tracking
5. Batch processing workflow

**LLM agents handle:**
1. File structure analysis (per file)
2. Complex list parsing
3. OCR error correction
4. Ambiguity resolution
5. Quality validation

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                    EXTRACTION ORCHESTRATOR                   │
│                         (Python)                             │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  PHASE 1: File-Level Analysis (LLM Agent via Task)          │
│  - Detect people section boundaries                         │
│  - Identify department/province structure                   │
│  - Extract format patterns used in this file                │
│  - Generate file-specific extraction rules                  │
│  Output: FileAnalysis JSON                                  │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  PHASE 2: Pattern-Based Extraction (Python)                 │
│  - Apply file-specific patterns from Phase 1                │
│  - Extract 80-90% of people using regex                     │
│  - Tag extractions by confidence (high/medium/low)          │
│  - Flag problematic sections for LLM review                 │
│  Output: PreliminaryExtractions + FlaggedSections           │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  PHASE 3: LLM-Assisted Extraction (LLM Agent via Task)      │
│  - Process flagged sections (lists, OCR errors, ambiguous)  │
│  - Extract people from complex formats                      │
│  - Resolve "ditto" and role inheritance                     │
│  - Validate and clean names                                 │
│  Output: AdditionalExtractions                              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│  PHASE 4: Validation & Merging (Python + LLM Agent)         │
│  - Merge preliminary + additional extractions               │
│  - Python: Remove obvious false positives                   │
│  - LLM Agent: Quality check sample (5-10%)                  │
│  - Generate confidence scores                               │
│  Output: FinalExtractions JSON                              │
└─────────────────────────────────────────────────────────────┘
```

## Component Design

### 1. FileAnalyzer (LLM Agent)

**Input:** Single colony file (text)
**Output:** FileAnalysis JSON

```json
{
  "file": "output_3/1867_manual_parsed/ceylon.txt",
  "colony": "CEYLON",
  "year": 1867,
  "people_section": {
    "start_line": 160,
    "end_line": 464,
    "start_marker": "Civil Establishment"
  },
  "structure": {
    "has_departments": true,
    "has_provinces": true,
    "departments": [
      "Colonial Secretary's Office",
      "Treasurer's Department",
      "Audit Office",
      "Surveyor General's Department",
      "Customs Department",
      "Government Agents",
      "Judicial Establishment",
      "Medical Department",
      "Police",
      "Ecclesiastical Department"
    ],
    "provinces": [
      "Western Province",
      "North Western Province",
      "Southern Province",
      "Eastern Province",
      "Northern Province",
      "Central Province"
    ]
  },
  "patterns_detected": {
    "primary_format": "Role, Name, Salary",
    "has_lists": true,
    "list_examples": [
      {
        "line_range": [172, 174],
        "type": "comma_separated_names",
        "header": "Writers, commencing at 200l. per annum",
        "count": 16
      }
    ],
    "salary_format": "£ sterling (e.g., 7,000l.)",
    "common_separators": [",", ";"],
    "has_ditto": true,
    "ocr_quality": "good"
  },
  "extraction_strategy": {
    "use_regex_for": ["standard_role_name_salary", "department_headers"],
    "use_llm_for": ["lists", "ditto_resolution", "ambiguous_cases"],
    "confidence_thresholds": {
      "high": 0.9,
      "medium": 0.7,
      "low": 0.5
    }
  }
}
```

### 2. PatternExtractor (Python)

**Input:** File text + FileAnalysis
**Output:** PreliminaryExtractions + FlaggedSections

Uses regex patterns but informed by FileAnalysis:
- Apply file-specific patterns
- Track department/province context
- Mark high-confidence extractions
- Flag complex sections for LLM

```python
class PatternExtractor:
    def extract(self, file_text, file_analysis):
        extractions = []
        flagged = []

        # Use analysis to guide extraction
        patterns = self._get_patterns(file_analysis.patterns_detected)

        for line_num, line in enumerate(file_text.lines):
            # Try patterns in priority order
            for pattern in patterns:
                match = pattern.match(line)
                if match:
                    person = self._create_person(match, confidence=0.9)
                    extractions.append(person)
                    break
            else:
                # No pattern matched - flag for LLM
                if self._looks_like_person_data(line):
                    flagged.append({
                        'line_num': line_num,
                        'content': line,
                        'reason': 'no_pattern_match'
                    })

        return extractions, flagged
```

### 3. LLMExtractor (LLM Agent via Task)

**Input:** FlaggedSections + FileAnalysis
**Output:** AdditionalExtractions

Specialized extraction for complex cases:

**Task Prompt Template:**
```
You are extracting people from a Colonial Office List. You have been given
sections that regex extraction could not handle.

File: {file_name}
Year: {year}
Colony: {colony}

File Analysis Summary:
- Primary format: {primary_format}
- Has lists: {has_lists}
- Currency: {salary_format}

Extract all people from these flagged sections. For each person, return:
- name: Full name with titles/qualifications
- role: Official position
- salary: If present
- line_number: Source line number

Flagged Sections:
{flagged_sections}

Handle:
1. Comma-separated lists (extract each person)
2. OCR errors (correct obvious mistakes)
3. "Ditto" references (resolve to actual role)
4. Ambiguous entries (use context to determine)

Return JSON array of people.
```

### 4. Validator (Python + LLM)

**Python validation:**
- Remove duplicate entries
- Filter known false positives (location names, qualifications)
- Validate data completeness
- Check consistency

**LLM quality check:**
- Random sample 5-10% of extractions
- Verify against source
- Flag suspicious entries
- Calculate actual accuracy

## Workflow for Single File

```python
def extract_people_from_file(file_path, year, colony):
    # PHASE 1: Analyze file structure (LLM)
    file_analysis = Task(
        subagent_type="general-purpose",
        prompt=f"Analyze structure of {file_path}...",
        model="haiku"  # Fast for analysis
    )

    # PHASE 2: Pattern extraction (Python)
    extractor = PatternExtractor()
    preliminary, flagged = extractor.extract(
        read_file(file_path),
        file_analysis
    )

    # PHASE 3: LLM extraction for flagged (LLM)
    if flagged:
        additional = Task(
            subagent_type="general-purpose",
            prompt=f"Extract people from flagged sections...",
            model="sonnet"  # More capable for complex extraction
        )
    else:
        additional = []

    # PHASE 4: Merge and validate (Python + LLM)
    all_people = preliminary + additional
    validated = validate_extractions(all_people)

    # LLM quality check on sample
    sample = random.sample(validated, min(len(validated)//10, 50))
    quality_report = Task(
        subagent_type="general-purpose",
        prompt=f"Validate these extractions against source...",
        model="haiku"
    )

    return validated, quality_report
```

## Batch Processing Strategy

**For 47 Ceylon files:**

1. **Analyze all files first** (parallel LLM tasks)
   - Batch analyze 5-10 files at once
   - Identify common patterns across years
   - Build pattern library

2. **Group files by similarity**
   - Same format → same extraction strategy
   - Different formats → custom strategies

3. **Extract in batches**
   - Apply pattern extraction to all
   - Collect all flagged sections
   - Batch LLM extraction (more efficient)

4. **Validate incrementally**
   - Check quality after each decade
   - Refine patterns based on validation
   - Early stopping if quality degrades

## Cost Management

**Estimated LLM API calls for 47 files:**

- File analysis (Haiku): 47 calls × ~2K tokens = ~94K tokens
- LLM extraction (Sonnet): ~20-30 calls × ~5K tokens = ~150K tokens
- Quality validation (Haiku): 47 calls × ~3K tokens = ~141K tokens

**Total: ~385K tokens (~$0.50-1.00)**

**Optimization:**
- Use Haiku for analysis/validation (cheaper, faster)
- Use Sonnet only for complex extraction
- Cache file analyses (reuse for similar files)
- Batch operations where possible

## Quality Targets

**After improvements:**
- **Recall:** >95% (vs. 70-80% current)
- **Precision:** >98% (vs. 98% current)
- **Unknown roles:** <5% (vs. 17% current)
- **Confidence:** Average 0.92+ (vs. 0.83 current)

## Reusability for Other Colonies

**This architecture works for:**
- All medium-sized colonies (Barbados, Jamaica, Fiji, etc.)
- Small colonies (same patterns, less data)
- Large colonies (Canada, India - need province handling)

**Adaptations needed:**
- Adjust FileAnalyzer prompts for colony-specific terms
- Add new patterns to PatternExtractor library
- Update location/department filter lists

**No changes needed:**
- Overall workflow
- Validation logic
- Data schema
- Quality checking

## Implementation Plan

1. Build FileAnalyzer (LLM agent wrapper)
2. Enhance PatternExtractor with file-analysis guidance
3. Build LLMExtractor (Task wrapper for flagged sections)
4. Build Validator (Python + LLM quality check)
5. Create orchestrator script
6. Test on Ceylon 1867-1880 (14 files)
7. Validate quality improvements
8. Run full Ceylon extraction
9. Document patterns for reuse

## Success Metrics

**Quantitative:**
- Extract 6,000+ people from Ceylon (vs. 4,801)
- <5% unknown roles (vs. 17%)
- >95% recall verified on sample
- <2% false positives

**Qualitative:**
- Code is well-documented and modular
- Works with OCR errors
- Handles format variations
- Easy to adapt for other colonies
- Clear audit trail for all extractions
