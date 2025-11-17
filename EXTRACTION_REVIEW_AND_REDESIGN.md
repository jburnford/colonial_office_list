# Knowledge Graph Extraction Review & Redesign

## Date: 2025-11-17

## Executive Summary

After reviewing `knowledge_graph_extracts_v3/1905_extracted.json` and the extraction methodology, we've identified critical gaps that prevent effective knowledge graph construction and entity disambiguation. This document outlines the problems and proposes a comprehensive redesign.

---

## Critical Problems Identified

### 1. **Coarse Provenance / Missing Line Numbers**
**Current State:**
```json
"provenance": {
  "source_file": "output_2/1905_manual_parsed/ANTIGUA.md",
  "source_lines": "1-240",  // TOO BROAD!
  "source_section": "General Information"
}
```

**Problem:** Line ranges like "1-240" are useless for:
- Finding the exact location of an entity in the source
- Verifying extraction accuracy
- Building precise entity links
- Human review and validation

**Impact:** Cannot trace "St. John" back to line 15 of ANTIGUA.md where it appears

---

### 2. **Missing Context Text**
**Current State:** No field capturing the actual text from which the entity was extracted

**Example - Current:**
```json
{
  "name": "St. John",
  "type": "town",
  "description": "The chief town, has a population of 9,262, and is a port of registry"
}
```

**What We Need:**
```json
{
  "name": "St. John",
  "type": "town",
  "description": "The chief town, has a population of 9,262, and is a port of registry",
  "context_text": "St. John, the chief town, has a population of 9,262, and is a port of registry, having on 31st December, 1903, 45 sailing vessels registered, with a total tonnage of 669."
}
```

**Why This Matters:**
- Context disambiguates entities (St. John in Antigua vs. St. John's in Newfoundland vs. St. John in Virgin Islands)
- Enables verification without re-reading entire source files
- Provides natural language context for LLM-based entity resolution
- Shows exactly what text was interpreted

---

### 3. **Ambiguous Colony/Territory Attribution**
**Current Problem:** "St. John" without clear colony reference is meaningless

**Example - Current:**
```json
{
  "id": "place_004",
  "name": "St. John",
  "parent_location": "place_001"  // What is place_001?
}
```

**What We Need:**
```json
{
  "id": "place_antigua_1905_004",
  "name": "St. John",
  "colony": "ANTIGUA",
  "colony_normalized": "Antigua",
  "parent_location": "ANTIGUA"
}
```

**Why This Matters:**
- "St. John" appears in multiple colonies
- Without explicit colony field, entities are ambiguous
- Cross-year analysis requires clear attribution
- Human-readable identifiers aid debugging

---

### 4. **Extraction Method Weaknesses**

**Current Approach (from `extract_knowledge_graphs_enhanced.py`):**
- Uses regex patterns on full text
- No line-by-line tracking
- Extraction happens in broad sweeps
- No context preservation

**Example:**
```python
coord_match = re.search(r'(\d+°\s*\d+\'?)\s*([NS])', text)
# Finds coordinate but not WHERE in the text
```

**Problems:**
- Cannot record specific line numbers
- Cannot capture surrounding context
- Regex matches may be ambiguous
- No way to verify against original

---

## Redesigned Entity Schema

### Enhanced Entity Structure (All Entity Types)

Every entity should have:

```json
{
  "id": "entity_type_colony_year_number",
  "colony": "EXACT_COLONY_NAME_FROM_FILENAME",
  "colony_normalized": "Human Readable Colony Name",
  "year": "1905",

  "source_location": {
    "file": "output_2/1905_manual_parsed/ANTIGUA.md",
    "line_start": 15,
    "line_end": 15,
    "char_start": 532,  // optional but helpful
    "char_end": 658     // optional but helpful
  },

  "context_text": "The exact sentence(s) from the source where this entity appears or is described",

  "extracted_data": {
    // Entity-specific fields (name, coordinates, salary, etc.)
  },

  "provenance": {
    "extraction_date": "2025-11-17T10:30:00Z",
    "extraction_method": "llm_direct|regex|manual",
    "confidence": 0.95,
    "verified": false
  }
}
```

### Example: Place Entity (Enhanced)

```json
{
  "id": "place_antigua_1905_004",
  "entity_type": "place",
  "colony": "ANTIGUA",
  "colony_normalized": "Antigua",
  "year": "1905",

  "source_location": {
    "file": "output_2/1905_manual_parsed/ANTIGUA.md",
    "line_start": 15,
    "line_end": 15
  },

  "context_text": "St. John, the chief town, has a population of 9,262, and is a port of registry, having on 31st December, 1903, 45 sailing vessels registered, with a total tonnage of 669.",

  "name": "St. John",
  "modern_name": "Saint John's",
  "type": "town",
  "coordinates": null,
  "area": null,
  "population": 9262,
  "description": "The chief town, port of registry with 45 sailing vessels (669 tons total) as of Dec 31, 1903",
  "parent_location": "ANTIGUA",

  "provenance": {
    "extraction_date": "2025-11-17T10:30:00Z",
    "extraction_method": "llm_direct",
    "confidence": 0.95,
    "verified": false
  }
}
```

### Example: Person Entity (Enhanced)

```json
{
  "id": "person_antigua_1905_023",
  "entity_type": "person",
  "colony": "ANTIGUA",
  "colony_normalized": "Antigua",
  "year": "1905",

  "source_location": {
    "file": "output_2/1905_manual_parsed/ANTIGUA.md",
    "line_start": 129,
    "line_end": 129
  },

  "context_text": "Treasurer and Collector of Customs, W. D. Auchinleck, 500l., and fees as Registrar of Shipping.",

  "name": "W. D. Auchinleck",
  "titles": ["Hon."],
  "honors": [],
  "positions": [
    {
      "title": "Treasurer and Collector of Customs",
      "department": "Customs",
      "location": "Antigua",
      "salary": {
        "amount": 500,
        "currency": "£",
        "period": "annual"
      },
      "allowances": [
        {
          "type": "fees",
          "description": "fees as Registrar of Shipping"
        }
      ],
      "status": "permanent",
      "year": "1905"
    }
  ],

  "provenance": {
    "extraction_date": "2025-11-17T10:30:00Z",
    "extraction_method": "llm_direct",
    "confidence": 0.95,
    "verified": false
  }
}
```

---

## Redesigned Extraction Approach

### Phase 1: Per-Colony Sequential Extraction

**Instead of:** Processing entire year at once with regex patterns
**Do:** Process each colony file line-by-line or section-by-section

### Extraction Strategy

1. **Load colony file with line numbers**
2. **Process sequentially:**
   - Identify section (General Info, Civil Establishment, Trade, etc.)
   - Extract entities from each relevant passage
   - **Record exact line number(s)**
   - **Capture context text (1-2 sentences)**
   - **Assign colony explicitly**
3. **Generate structured JSON per colony**
4. **Merge all colonies for the year**

---

## Extraction Prompt Template

### For Task Agents

```markdown
# Entity Extraction Task: {COLONY_NAME} - {YEAR}

## Source File
{FULL_PATH_TO_FILE}

## Instructions

You are extracting structured entities from this Colonial Office List file to build a knowledge graph.

### Critical Requirements

1. **ALWAYS record exact line numbers** where each entity appears
2. **ALWAYS capture context text** - the sentence(s) containing the entity
3. **ALWAYS set colony field** to the exact colony name: "{COLONY_NAME}"
4. **NEVER invent data** - extract only what is explicitly stated
5. **Preserve historical spelling** exactly as written

### Entity Types to Extract

#### 1. Places (Geographic Entities)
- Colony/territory name
- Cities, towns, settlements
- Geographic features (rivers, mountains, harbors)
- Dependencies

**For each place, extract:**
- Exact name (as written)
- Type (colony/city/town/region/feature)
- Coordinates (if present)
- Area (if present)
- Population (if present)
- Description
- **Line number(s)** where mentioned
- **Context text** (the full sentence)

#### 2. People (Personnel)
- Government officials
- Military officers
- Any named individual with a role

**For each person, extract:**
- Full name with titles (Sir, Rev., Dr., etc.)
- Honors (K.C.M.G., C.B., etc.)
- Position title(s)
- Department
- Salary and currency
- Allowances
- **Line number(s)** where mentioned
- **Context text** (the full entry)

#### 3. Institutions
- Councils (Executive, Legislative)
- Courts
- Departments
- Military units

**For each institution, extract:**
- Official name
- Type
- Composition (number of members, structure)
- **Line number(s)** where mentioned
- **Context text**

#### 4. Economic Data
- Revenue figures
- Expenditure
- Trade statistics
- Shipping data
- Crop/production data

**For each datum, extract:**
- Category
- Value and unit
- Currency
- Year/period
- **Line number(s)** from table or text
- **Context text**

#### 5. Infrastructure
- Railways (length, stations, revenue)
- Telegraph lines
- Roads
- Ports

**For each infrastructure item, extract:**
- Type
- Name/description
- Specifications (length, capacity, etc.)
- **Line number(s)**
- **Context text**

#### 6. Demographics
- Population totals
- Population breakdowns by category

**For each demographic entry, extract:**
- Total or category
- Count
- Year
- **Line number(s)** from table
- **Context text**

#### 7. Events
- Establishment dates
- Treaties
- Constitutional changes
- Historical events mentioned

**For each event, extract:**
- Date
- Type
- Description
- **Line number(s)**
- **Context text**

### Output Format

Return JSON with this structure:

```json
{
  "metadata": {
    "colony": "{COLONY_NAME}",
    "year": "{YEAR}",
    "source_file": "{FILE_PATH}",
    "extraction_date": "{ISO_TIMESTAMP}",
    "total_lines": number,
    "extraction_notes": "Any special observations"
  },
  "entities": {
    "places": [ {enhanced_schema} ],
    "people": [ {enhanced_schema} ],
    "institutions": [ {enhanced_schema} ],
    "economic_data": [ {enhanced_schema} ],
    "infrastructure": [ {enhanced_schema} ],
    "demographics": [ {enhanced_schema} ],
    "events": [ {enhanced_schema} ]
  }
}
```

### Quality Checklist

- [ ] Every entity has a line number
- [ ] Every entity has context_text field
- [ ] Every entity has colony field set to "{COLONY_NAME}"
- [ ] IDs follow pattern: `{type}_{colony}_{year}_{number}`
- [ ] Historical spelling preserved
- [ ] Numbers extracted with units and currency
- [ ] No invented data

### Example Entity

```json
{
  "id": "place_{COLONY_NAME_LOWER}_{YEAR}_001",
  "entity_type": "place",
  "colony": "{COLONY_NAME}",
  "colony_normalized": "{Human Readable Name}",
  "year": "{YEAR}",
  "source_location": {
    "file": "{FILE_PATH}",
    "line_start": 15,
    "line_end": 15
  },
  "context_text": "Exact text from source",
  "name": "Place Name",
  "type": "town",
  ...rest of fields
}
```

## Begin Extraction

Process the entire file systematically, section by section, extracting all entities with complete metadata.
```

---

## Implementation Plan

### Step 1: Test Extraction on Single Colony
- Select one colony file (e.g., ANTIGUA.md from 1905)
- Create Task agent with detailed prompt
- Review output for completeness
- Verify all entities have line numbers and context

### Step 2: Refine Prompt Based on Results
- Identify any missing fields
- Adjust prompt clarity
- Add examples if needed

### Step 3: Parallel Extraction
- Create separate Task agents for each colony in a year
- Run in parallel for efficiency
- Each agent processes one colony file

### Step 4: Merge and Validate
- Combine all colony extractions for the year
- Validate schema compliance
- Check for duplicate entities
- Generate quality report

### Step 5: Scale to All Years
- Apply refined process to all 62 years
- Track extraction metrics
- Document issues and resolutions

---

## Benefits of Redesigned Approach

1. **Traceable**: Every entity links to exact source location
2. **Verifiable**: Context text allows quick verification
3. **Disambiguated**: Colony field resolves entity confusion
4. **LLM-Ready**: Context text enables semantic entity resolution
5. **Human-Readable**: Clear provenance aids debugging and research
6. **Graph-Ready**: Precise attribution enables relationship building
7. **Auditable**: Can validate extraction quality programmatically

---

## Next Steps

1. Review this document and approve redesign
2. Create pilot extraction prompt for one colony
3. Run test extraction
4. Iterate on prompt and schema
5. Scale to full dataset
