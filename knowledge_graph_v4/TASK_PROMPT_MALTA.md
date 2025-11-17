# Task: Extract Knowledge Graph for MALTA (1867-1966)

## Objective
Extract structured knowledge graph data for the colony of MALTA across all years where it appears in the Colonial Office List, following schema v2.0.

## Input Files
- **Source directory**: `/home/jic823/colonialofficelist/output_2/`
- **Schema**: `/home/jic823/colonialofficelist/knowledge_graph_extracts_v3/schema_v2.json`
- **Controlled vocabulary**: `/home/jic823/colonialofficelist/knowledge_graph_extracts_v3/master_vocabulary_filtered.json`
- **Example output**: `/home/jic823/colonialofficelist/knowledge_graph_extracts_v3/example_1950_CEYLON.json`

## Malta Files Found
Malta appears in these years (46 total):
- 1867, 1883, 1889, 1898, 1905, 1915, 1917, 1922, 1924, 1929, 1933, 1934, 1936, 1946, 1949, 1950, 1951...

Files are located at patterns like:
- `/home/jic823/colonialofficelist/output_2/1950_manual_parsed/MALTA.md`
- `/home/jic823/colonialofficelist/output_2/1964_manual_parsed/STATE_OF_MALTA_GC.md`

## Output Structure
Create one JSON file per year:
```
/home/jic823/colonialofficelist/knowledge_graph_v4/MALTA/
├── 1867_MALTA.json
├── 1883_MALTA.json
├── 1889_MALTA.json
...
└── 1964_MALTA.json
```

## Instructions

### Step 1: Find all Malta files
Search through all year directories (1867-1966) and identify Malta markdown files. Note that Malta may appear as:
- `MALTA.md`
- `MALTA_GC.md` (post-1942, George Cross award)
- `STATE_OF_MALTA_GC.md` (1960s)

### Step 2: Process each year
For each Malta file found, extract the following following schema v2.0:

#### A. Colony Info (top-level)
```json
"colony_info": {
  "official_name": "Malta",
  "alternative_names": ["Malta GC" (if after 1942)],
  "colonial_status": "Crown Colony",
  "capital": "Valletta",
  "coordinates": {only if stated in source},
  "area": {only if stated in source},
  "population_census": {extract from source with year}
}
```

#### B. Places
Extract places mentioned:
- Malta (main island)
- Gozo (secondary island)
- Valletta (capital)
- Other cities/towns mentioned

**Critical**: Include location_context:
```json
{
  "id": "place_valletta",
  "name": "Valletta",
  "type": "city",
  "location_context": {
    "mentioned_in_colony": "MALTA",
    "actual_location_country": "Malta",
    "certainty": "definite",
    "reasoning": "Capital city of Malta"
  },
  "provenance": {full provenance with original text snippet}
}
```

#### C. People
Extract all people with positions:
- Governors
- Colonial Secretary
- Chief Justice
- Attorney-General
- All other officials listed

**Use controlled vocabulary for:**
- Titles: Sir, Dame, Hon, Rev, Dr (from vocabulary file)
- Honors: KCMG, CMG, OBE, etc. (from vocabulary file)
  - **Exclude academic degrees**: BA, MA, MD, LLD are NOT honors
- Positions: Normalize to canonical forms (Governor, Colonial Secretary, etc.)

**Extract salaries** if mentioned (amount, currency, period)

**Example person extraction:**
```json
{
  "id": "person_john_smith_1950",
  "name": "John Smith",
  "titles": ["Sir"],
  "honors": [{"honor": "KCMG", "full_name": "Knight Commander of the Order of St Michael and St George"}],
  "positions": [{
    "title": "Governor",
    "canonical_title": "Governor",
    "colony": "MALTA",
    "location": "Valletta",
    "salary": {"amount": 5000, "currency": "£", "period": "annual"}
  }],
  "provenance": {
    "source_file": "output_2/1950_manual_parsed/MALTA.md",
    "source_lines": "145-147",
    "source_section": "GOVERNMENT",
    "original_text": "Governor: Sir John Smith, K.C.M.G. Salary £5,000 per annum",
    "extraction_confidence": 0.95,
    "extraction_method": "direct_extraction"
  }
}
```

#### D. Institutions
Extract government institutions:
- Executive Council
- Legislative Council/Assembly
- Courts
- Departments (Medical, Education, Police, etc.)

Include composition if mentioned (number of members, official vs unofficial)

#### E. Economic Data
Extract financial data if present:
- Revenue (with year it applies to)
- Expenditure
- Trade statistics
- Validate plausibility (flag if suspiciously low/high)

#### F. Infrastructure
Extract mentions of:
- Railways
- Dockyard (Malta has major naval dockyard)
- Ports
- Telegraph/postal systems

#### G. Events
Extract historical events mentioned:
- 1814: British annexation
- 1942: George Cross award
- Constitutional changes
- Any other significant events

**Critical**: Distinguish `event_date` (when it happened) from `year_mentioned` (year of publication)

### Step 3: Build Relationships
Create relationships between entities:
- Person `HOLDS_POSITION` → Institution
- Person `REPORTS_TO` → Person (based on hierarchy: Colonial Secretary reports to Governor)
- Institution `PART_OF` → Institution (e.g., Department part of Government)
- Place `LOCATED_IN` → Place (e.g., Valletta located in Malta)

### Step 4: Deduplication
Within each year, check for duplicate people (same person mentioned multiple times with slight name variations). Flag as `duplicate_candidates` if found.

### Step 5: Quality Checks
- Ensure all entities have full provenance with original text snippets
- Check extraction confidence scores (should be >0.80 for most)
- Validate economic data plausibility
- Ensure honors vs academic degrees are properly separated

## Key Principles

1. **Extract exactly what's in the source** - don't add external knowledge
2. **Include coordinates ONLY if stated in source document**
3. **Full provenance for everything** - source file, lines, section, original text
4. **Use controlled vocabularies** for normalization
5. **Context awareness for locations** - if Malta text mentions "training in UK", mark UK as location with proper context
6. **Preserve historical terminology** in demographics/population breakdowns
7. **Original text snippets** in provenance for verification

## Output Format

Each year should produce a JSON file matching the schema v2.0 structure. See example_1950_CEYLON.json for reference.

## Success Criteria

- ✅ All 46 Malta years processed
- ✅ Average >10 people extracted per year
- ✅ All entities have full provenance with original text
- ✅ Extraction confidence >0.85 for majority of entities
- ✅ No academic degrees (BA, MA, MD) in honors field
- ✅ Relationships properly built (Governor → Government, etc.)

## Process

1. Read each Malta markdown file
2. Use your LLM context awareness to understand structure
3. Extract entities following the schema
4. Build relationships based on administrative hierarchy knowledge
5. Add full provenance for every extraction
6. Save to `/home/jic823/colonialofficelist/knowledge_graph_v4/MALTA/{year}_MALTA.json`

## Return Summary

When complete, provide:
- Years processed (list)
- Total entities extracted by type
- Sample of people extracted (5 examples with positions)
- Any data quality issues found
- Processing time

Begin extraction for MALTA across all available years!
