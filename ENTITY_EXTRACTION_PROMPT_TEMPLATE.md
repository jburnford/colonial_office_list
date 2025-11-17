# Colonial Office List Entity Extraction Prompt Template

## Purpose
This prompt template is designed for Task agents to extract structured entities from individual colony files with complete provenance tracking.

---

## PROMPT TEMPLATE (Fill in variables before use)

```
# Knowledge Graph Entity Extraction: {{COLONY_NAME}} ({{YEAR}})

## Task Overview
Extract ALL structured entities from the Colonial Office List file for {{COLONY_NAME}} in {{YEAR}}, with COMPLETE provenance tracking including exact line numbers and context text.

## Source File
**Path**: {{FILE_PATH}}
**Colony**: {{COLONY_NAME}}
**Year**: {{YEAR}}

## CRITICAL REQUIREMENTS

### Provenance Rules (NON-NEGOTIABLE)
1. **EVERY entity MUST include exact line number(s)** where it appears in source
2. **EVERY entity MUST include context_text** - the actual sentence(s) from the source
3. **EVERY entity MUST include colony field** set to "{{COLONY_NAME}}"
4. **Entity IDs MUST follow format**: `{type}_{{COLONY_NAME_LOWER}}_{{YEAR}}_{sequential_number}`

### Extraction Rules
1. **NEVER invent or infer data** - extract only explicitly stated information
2. **PRESERVE historical spelling** exactly as written (do not modernize)
3. **PRESERVE original units** and currency symbols (£, $, square miles, tons, etc.)
4. **EXTRACT complete numerical data** with units (e.g., "500l." not just "500")
5. **CAPTURE titles and honors** exactly as formatted (K.C.M.G., Sir, Rev., etc.)
6. **NOTE ambiguities** - if source is unclear, note in extraction_notes

---

## Entity Types and Extraction Specifications

### 1. PLACES (Geographic Entities)

**Extract:**
- Colony/territory names
- Cities, towns, settlements
- Regions, districts, parishes
- Geographic features (rivers, mountains, bays, harbors)
- Dependencies and associated territories

**Required Fields:**
```json
{
  "id": "place_{{colony_lower}}_{{year}}_###",
  "entity_type": "place",
  "colony": "{{COLONY_NAME}}",
  "colony_normalized": "{{Human Readable Name}}",
  "year": "{{YEAR}}",

  "source_location": {
    "file": "{{FILE_PATH}}",
    "line_start": ###,
    "line_end": ###
  },

  "context_text": "The complete sentence(s) from the source where this place is mentioned or described",

  "name": "Exact name as written in source",
  "modern_name": "Modern equivalent if confidently identifiable, else null",
  "type": "colony|territory|city|town|settlement|region|district|parish|river|mountain|harbor|bay|island|dependency",

  "coordinates": {
    "latitude": "Exact format from source (e.g., '17° 6' N')",
    "longitude": "Exact format from source (e.g., '61° 45' W')"
  },

  "area": {
    "value": number,
    "unit": "exact unit from source"
  },

  "population": number or null,
  "description": "Any descriptive text from source",
  "parent_location": "Name of parent territory/region if mentioned",

  "provenance": {
    "extraction_date": "{{ISO_TIMESTAMP}}",
    "extraction_method": "llm_direct",
    "confidence": 0.0-1.0,
    "extraction_notes": "Any special notes about this extraction"
  }
}
```

**Examples to Extract:**
- "Antigua is situated in W. long. 61° 45', and N. lat. 17° 6'. It is about 54 miles in circumference, and its area is 108 square miles"
- "St. John, the chief town, has a population of 9,262"
- "Barbuda lies about 25 miles due north of the main island, with an area of 62 miles"

---

### 2. PEOPLE (Personnel/Prosopography)

**Extract:**
- All named individuals
- Government officials at all levels
- Military officers
- Clergy
- Professionals (doctors, engineers, etc.)

**Required Fields:**
```json
{
  "id": "person_{{colony_lower}}_{{year}}_###",
  "entity_type": "person",
  "colony": "{{COLONY_NAME}}",
  "colony_normalized": "{{Human Readable Name}}",
  "year": "{{YEAR}}",

  "source_location": {
    "file": "{{FILE_PATH}}",
    "line_start": ###,
    "line_end": ###
  },

  "context_text": "Complete text of the personnel entry, including position, name, salary, and allowances",

  "name": "Full name as written (e.g., 'W. D. Auchinleck')",
  "titles": ["Sir", "Rev.", "Dr.", "Hon.", "Major-General", etc.],
  "honors": ["K.C.M.G.", "C.B.", "C.M.G.", "I.S.O.", "C.E.", etc.],

  "positions": [
    {
      "title": "Exact position title from source",
      "department": "Department/office name if mentioned",
      "location": "{{COLONY_NAME}} or more specific location",
      "salary": {
        "amount": number,
        "currency": "£|$|etc",
        "period": "annual|monthly|etc"
      },
      "allowances": [
        {
          "type": "quarters|table_money|horse|travelling|house|fees",
          "amount": number or null,
          "currency": "£|$|etc",
          "description": "Any descriptive text (e.g., 'fees as Registrar')"
        }
      ],
      "status": "permanent|acting|temporary|vacant",
      "year": "{{YEAR}}"
    }
  ],

  "provenance": {
    "extraction_date": "{{ISO_TIMESTAMP}}",
    "extraction_method": "llm_direct",
    "confidence": 0.0-1.0,
    "extraction_notes": "Any special notes"
  }
}
```

**Parsing Rules for Personnel:**
- Format is typically: `Position—Name, Honors. Salary and allowances.`
- Extract salary amounts: "500l." → amount: 500, currency: "£"
- Extract allowances: "50l. horse allowance" → type: "horse", amount: 50
- Multiple positions for same person should be in same entity
- "Hon." is a title, not an honor
- Parse military ranks as titles: "Lieut.-General Sir Robert Stewart"

**Examples:**
- "Treasurer and Collector of Customs, W. D. Auchinleck, 500l., and fees as Registrar of Shipping."
- "Colonial Secretary and Attorney-General, Hon. E. St. J. Branch."
- "Auditor-General, Hon. E. A. Foster, I.S.O."

---

### 3. INSTITUTIONS

**Extract:**
- Executive Councils
- Legislative Councils
- Courts (Supreme, Vice-Admiralty, Police, etc.)
- Government departments
- Military units/garrisons
- Police forces
- Schools/colleges
- Medical facilities
- Banks
- Religious establishments

**Required Fields:**
```json
{
  "id": "institution_{{colony_lower}}_{{year}}_###",
  "entity_type": "institution",
  "colony": "{{COLONY_NAME}}",
  "colony_normalized": "{{Human Readable Name}}",
  "year": "{{YEAR}}",

  "source_location": {
    "file": "{{FILE_PATH}}",
    "line_start": ###,
    "line_end": ###
  },

  "context_text": "Text describing the institution",

  "name": "Official name",
  "type": "executive_council|legislative_council|privy_council|court|department|military|police|school|hospital|bank|church",
  "location": "{{COLONY_NAME}} or more specific",

  "composition": {
    "description": "Text description of composition",
    "member_count": number or null,
    "official_members": number or null,
    "unofficial_members": number or null,
    "members": ["List of member names if provided"]
  },

  "function": "Description of role/jurisdiction",
  "establishment_date": "If mentioned",

  "provenance": {
    "extraction_date": "{{ISO_TIMESTAMP}}",
    "extraction_method": "llm_direct",
    "confidence": 0.0-1.0,
    "extraction_notes": ""
  }
}
```

---

### 4. ECONOMIC DATA

**Extract:**
- Revenue (by year, by source/category)
- Expenditure (by year, by category)
- Trade volumes (imports/exports)
- Shipping statistics (vessels, tonnage)
- Customs revenue
- Public debt
- Production data (sugar, cotton, etc.)

**Required Fields:**
```json
{
  "id": "economic_{{colony_lower}}_{{year}}_###",
  "entity_type": "economic_data",
  "colony": "{{COLONY_NAME}}",
  "colony_normalized": "{{Human Readable Name}}",
  "year": "{{YEAR}}",

  "source_location": {
    "file": "{{FILE_PATH}}",
    "line_start": ###,
    "line_end": ###
  },

  "context_text": "Text or table row containing this data",

  "data_type": "revenue|expenditure|import|export|shipping|customs|debt|production|trade_balance",
  "category": "Specific category (e.g., 'Sugar exports', 'Revenue from UK', 'Total customs')",

  "value": number,
  "unit": "£|$|tons|vessels|etc",
  "currency": "£|$|etc if applicable",

  "time_period": "YYYY or 'YYYY-YY' for fiscal years",
  "subcategories": {
    "from_uk": number,
    "from_colonies": number,
    "from_elsewhere": number
  },

  "notes": "Any contextual information",

  "provenance": {
    "extraction_date": "{{ISO_TIMESTAMP}}",
    "extraction_method": "llm_direct",
    "confidence": 0.0-1.0,
    "extraction_notes": ""
  }
}
```

**Table Extraction:**
- Extract EACH row as separate entity
- Preserve year/time period for each entry
- Capture column headers in category field
- Note table structure in extraction_notes

---

### 5. INFRASTRUCTURE

**Extract:**
- Railways (routes, length, stations, revenue)
- Telegraph lines (stations, mileage)
- Postal routes
- Roads and bridges
- Ports and docks
- Public buildings
- Water supply systems

**Required Fields:**
```json
{
  "id": "infrastructure_{{colony_lower}}_{{year}}_###",
  "entity_type": "infrastructure",
  "colony": "{{COLONY_NAME}}",
  "colony_normalized": "{{Human Readable Name}}",
  "year": "{{YEAR}}",

  "source_location": {
    "file": "{{FILE_PATH}}",
    "line_start": ###,
    "line_end": ###
  },

  "context_text": "Text describing the infrastructure",

  "infrastructure_type": "railway|telegraph|postal_route|road|bridge|dock|port|building|water_supply",
  "name": "Name or description",
  "location": "{{COLONY_NAME}} or specific location",

  "specifications": {
    "length": {"value": number, "unit": "miles|km|feet"},
    "stations": number,
    "gauge": "If railway",
    "capacity": "Any capacity info",
    "cost": {"value": number, "currency": "£|$"},
    "construction_date": "If mentioned"
  },

  "operational_data": {
    "revenue": {"value": number, "currency": "£|$", "year": "YYYY"},
    "expenses": {"value": number, "currency": "£|$", "year": "YYYY"},
    "usage": "Any usage statistics"
  },

  "connections": ["Connected locations"],

  "provenance": {
    "extraction_date": "{{ISO_TIMESTAMP}}",
    "extraction_method": "llm_direct",
    "confidence": 0.0-1.0,
    "extraction_notes": ""
  }
}
```

---

### 6. DEMOGRAPHICS

**Extract:**
- Total population figures
- Population breakdowns by category
- Census data
- Gender distributions
- Urban vs. rural populations

**Required Fields:**
```json
{
  "id": "demographics_{{colony_lower}}_{{year}}_###",
  "entity_type": "demographics",
  "colony": "{{COLONY_NAME}}",
  "colony_normalized": "{{Human Readable Name}}",
  "year": "{{YEAR}}",

  "source_location": {
    "file": "{{FILE_PATH}}",
    "line_start": ###,
    "line_end": ###
  },

  "context_text": "Text or table containing population data",

  "location": "{{COLONY_NAME}} or more specific",
  "census_year": "YYYY if different from document year",
  "total_population": number or null,

  "breakdowns": [
    {
      "category": "Category as written in source (preserve historical terminology)",
      "count": number,
      "percentage": number or null
    }
  ],

  "provenance": {
    "extraction_date": "{{ISO_TIMESTAMP}}",
    "extraction_method": "llm_direct",
    "confidence": 0.0-1.0,
    "extraction_notes": "Note: Historical terminology preserved"
  }
}
```

**Important:** Preserve historical terminology exactly (White, Black, Coloured, Native, European, etc.). This is historical record.

---

### 7. EVENTS

**Extract:**
- Establishment/founding dates
- Treaties and cessions
- Constitutional changes
- Rebellions or conflicts
- Natural disasters
- Transfers of power
- Historical milestones mentioned

**Required Fields:**
```json
{
  "id": "event_{{colony_lower}}_{{year}}_###",
  "entity_type": "event",
  "colony": "{{COLONY_NAME}}",
  "colony_normalized": "{{Human Readable Name}}",
  "year": "{{YEAR}}",

  "source_location": {
    "file": "{{FILE_PATH}}",
    "line_start": ###,
    "line_end": ###
  },

  "context_text": "Text describing the event",

  "event_date": "Date as written in source (may be approximate)",
  "event_type": "establishment|treaty|cession|rebellion|constitutional_change|transfer|disaster|other",
  "description": "Event description from source",

  "locations_involved": ["{{COLONY_NAME}}", "other locations"],
  "people_involved": ["Names if mentioned"],
  "institutions_involved": ["Institutions if mentioned"],

  "year_mentioned": "{{YEAR}}",

  "provenance": {
    "extraction_date": "{{ISO_TIMESTAMP}}",
    "extraction_method": "llm_direct",
    "confidence": 0.0-1.0,
    "extraction_notes": ""
  }
}
```

---

## Output Format

Return a single JSON object:

```json
{
  "metadata": {
    "colony": "{{COLONY_NAME}}",
    "colony_normalized": "{{Human Readable Name}}",
    "year": "{{YEAR}}",
    "source_file": "{{FILE_PATH}}",
    "extraction_date": "{{ISO_TIMESTAMP}}",
    "total_lines_in_source": number,
    "processing_notes": "Any observations about the file structure or content"
  },

  "entity_counts": {
    "places": number,
    "people": number,
    "institutions": number,
    "economic_data": number,
    "infrastructure": number,
    "demographics": number,
    "events": number,
    "total": number
  },

  "entities": {
    "places": [ /* array of place entities */ ],
    "people": [ /* array of person entities */ ],
    "institutions": [ /* array of institution entities */ ],
    "economic_data": [ /* array of economic entities */ ],
    "infrastructure": [ /* array of infrastructure entities */ ],
    "demographics": [ /* array of demographic entities */ ],
    "events": [ /* array of event entities */ ]
  }
}
```

---

## Processing Approach

### Read and Process Systematically

1. **Read the entire source file** with line number awareness
2. **Process section by section:**
   - General Information / Geography
   - Population / Demographics
   - History / Events
   - Government Structure (Councils)
   - Civil Establishment (Personnel)
   - Financial data (Revenue, Expenditure, Trade)
   - Infrastructure (Railways, Telegraph, etc.)
   - Production / Crops

3. **For each entity identified:**
   - Record the exact line number(s)
   - Capture the full context text (1-3 sentences)
   - Extract all relevant fields
   - Set colony = "{{COLONY_NAME}}"
   - Generate unique ID

4. **Quality check:**
   - Every entity has line number
   - Every entity has context_text
   - Every entity has colony field
   - IDs are unique and properly formatted
   - Historical spelling preserved
   - No invented data

---

## Quality Assurance Checklist

Before finalizing extraction, verify:

- [ ] Every entity has `source_location.line_start` and `line_end`
- [ ] Every entity has `context_text` field with actual source text
- [ ] Every entity has `colony` field set to "{{COLONY_NAME}}"
- [ ] All entity IDs follow format: `{type}_{{colony_lower}}_{{year}}_###`
- [ ] Historical spelling and terminology preserved exactly
- [ ] All numerical values include units and currency where applicable
- [ ] No data invented or inferred beyond what's in source
- [ ] Table data extracted row-by-row with proper attribution
- [ ] metadata.entity_counts match actual counts
- [ ] JSON is valid and complete

---

## Example Complete Entity

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
    "extraction_date": "2025-11-17T15:30:00Z",
    "extraction_method": "llm_direct",
    "confidence": 0.95,
    "extraction_notes": "Clear reference to chief town with specific population and registry data"
  }
}
```

---

## Common Pitfalls to Avoid

1. ❌ Forgetting line numbers
2. ❌ Missing context_text field
3. ❌ Leaving colony field empty
4. ❌ Inventing modern equivalents without clear evidence
5. ❌ Modernizing historical spelling
6. ❌ Extracting numbers without units/currency
7. ❌ Combining multiple distinct entities into one
8. ❌ Skipping "minor" entities (extract everything!)
9. ❌ Parsing table data without preserving row-level detail
10. ❌ Not noting ambiguities or uncertainties

---

## Begin Extraction

Process the source file completely and systematically. Extract ALL entities of ALL types with COMPLETE provenance.

Return the JSON output following the exact schema specified above.
```

---

## Usage Instructions

1. Copy this template
2. Replace all `{{VARIABLE}}` placeholders:
   - `{{COLONY_NAME}}` - Exact colony name from filename (e.g., "ANTIGUA")
   - `{{YEAR}}` - Year being processed (e.g., "1905")
   - `{{FILE_PATH}}` - Full path to colony file
   - `{{COLONY_NAME_LOWER}}` - Lowercase version for IDs (e.g., "antigua")
   - `{{Human Readable Name}}` - Normalized name (e.g., "Antigua")
   - `{{ISO_TIMESTAMP}}` - Current timestamp in ISO 8601 format

3. Use with Task agent:
```python
Task(
  subagent_type="general-purpose",
  description="Extract entities from ANTIGUA 1905",
  prompt=filled_in_prompt_text
)
```

4. Save output as: `extracts_v4/{year}/{colony}_extracted.json`

---

## Notes

- This prompt is designed to be exhaustive and explicit
- The repetition is intentional to ensure consistency
- Line number tracking is the critical innovation
- Context text enables verification and disambiguation
- Colony field solves the "St. John" problem
