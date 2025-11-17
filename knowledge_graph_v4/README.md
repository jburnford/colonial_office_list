# Colonial Office List Knowledge Graph Extraction v2.0

## ✅ READY FOR DEPLOYMENT

Malta test succeeded (98.7% confidence, 100% provenance). Ready to process all colonies.

---

## IMPORTANT: DO NOT USE PYTHON

**This extraction requires LLM context-awareness and Tasks, NOT Python parsing.**

Python parsers will fail on this historical OCR text. Use Claude's understanding of:
- Administrative hierarchies
- Historical terminology
- Context-aware entity extraction
- Relationship inference

---

## Required Files (Already in Repo)

All paths relative to `/home/jic823/colonialofficelist/`:

### Schema & Vocabularies
- `knowledge_graph_extracts_v3/schema_v2.json` - Complete entity schema
- `knowledge_graph_extracts_v3/master_vocabulary_filtered.json` - Controlled vocabularies
- `knowledge_graph_extracts_v3/example_1950_CEYLON.json` - Working example

### Source Data
- `output_2/{YEAR}_manual_parsed/{COLONY}.md` - OCR'd markdown files (1867-1966)

### Task Templates
- `knowledge_graph_v4/TASK_PROMPT_MALTA.md` - Detailed extraction instructions
- `knowledge_graph_v4/QUICK_START_PROMPTS.md` - Copy-paste ready prompts

### Output Directory
- `knowledge_graph_v4/{COLONY}/{YEAR}_{COLONY}.json` - Structured outputs

---

## ✅ Test Results: Malta 1950

Successfully extracted:
- 11 people (Governor, officials with full salaries & honors)
- 6 places (Malta, Valletta, Gozo with coordinates)
- 5 institutions (Government, Councils, Courts)
- 7 economic data points (revenue, expenditure validated)
- 98.7% average confidence
- 100% provenance with original text snippets

**File**: `knowledge_graph_v4/MALTA/1950_MALTA.json`

---

## Quick Start: Process All Colonies

### Batch 1: High Priority (20 colonies)

For each colony, use this Task prompt:

```
Extract knowledge graph for [COLONY_NAME] across all years (1867-1966).

IMPORTANT: DO NOT USE PYTHON. Use LLM context awareness for entity extraction.

Files:
- Source: /home/jic823/colonialofficelist/output_2/{YEAR}_manual_parsed/[COLONY_NAME].md
- Schema: /home/jic823/colonialofficelist/knowledge_graph_extracts_v3/schema_v2.json
- Vocabulary: /home/jic823/colonialofficelist/knowledge_graph_extracts_v3/master_vocabulary_filtered.json
- Example: /home/jic823/colonialofficelist/knowledge_graph_extracts_v3/example_1950_CEYLON.json

Instructions:
1. Find all years where [COLONY_NAME] appears in output_2/
2. For each year, extract following schema v2.0:
   - Colony info (capital, area, population from census)
   - Places (cities, islands with location_context)
   - People (officials with positions, salaries, honors)
   - Institutions (councils, courts, departments)
   - Economic data (revenue, expenditure with validation)
   - Infrastructure (railways, ports, telegraph)
   - Events (historical milestones with dates)
   - Relationships (person-position, hierarchy, reports_to)

3. Use controlled vocabularies:
   - Honors: KCMG, CMG, OBE (EXCLUDE BA, MA, MD - these are degrees, not honors)
   - Titles: Sir, Hon, Rev, Dr
   - Positions: Governor, Colonial Secretary, Chief Justice, etc.

4. Quality requirements:
   - Full provenance with original text snippets (REQUIRED)
   - Extraction confidence >0.85
   - Location context: mentioned_in_colony, actual_location_country, certainty
   - Coordinates ONLY if stated in source
   - Validate economic data (flag implausible values)

5. Output: /home/jic823/colonialofficelist/knowledge_graph_v4/[COLONY_NAME]/{year}_[COLONY_NAME].json

Return: years processed, total entities by type, sample extractions, quality metrics.

Use haiku model for efficiency.
```

### Colonies to Process (Priority Order)

**Copy each prompt from `QUICK_START_PROMPTS.md`:**

1. ✅ MALTA (done - 46 years)
2. CEYLON (~54 years)
3. JAMAICA (~52 years)
4. BARBADOS (~45 years)
5. TRINIDAD (~48 years)
6. HONG_KONG (~50 years)
7. FIJI (~45 years)
8. MAURITIUS (~48 years)
9. CYPRUS (~40 years)
10. GIBRALTAR (~52 years)
11. BERMUDA (~50 years)
12. BAHAMAS (~48 years)
13. BRITISH_GUIANA (~50 years)
14. BRITISH_HONDURAS (~48 years)
15. SEYCHELLES (~45 years)
16. ST_LUCIA (~48 years)
17. GRENADA (~48 years)
18. ANTIGUA (~48 years)
19. DOMINICA (~48 years)
20. MONTSERRAT (~45 years)

**Total**: ~950 colony-year files for Batch 1

---

## Resource Estimates

### Time (with Haiku, parallel processing)
- 20 colonies × ~45 years avg = 900 files
- Sequential: ~45 hours
- **20 parallel Tasks: ~3 hours wall-clock**
- **50 parallel Tasks: ~1 hour wall-clock**

### Cost (with $500 credit)
- Per colony: ~$2-5
- Batch 1 (20 colonies): ~$50-100
- All 100 colonies: ~$200-500
- **Your $500 expires tomorrow - use it!**

---

## Validation After Each Colony

```bash
# Count files
ls -1 /home/jic823/colonialofficelist/knowledge_graph_v4/CEYLON/*.json | wc -l

# Check JSON validity
python3 -c "
import json, glob
files = glob.glob('/home/jic823/colonialofficelist/knowledge_graph_v4/CEYLON/*.json')
for f in files[:3]:
    data = json.load(open(f))
    print(f'{f}: {len(data[\"entities\"][\"people\"])} people')
"
```

---

## Key Principles

1. **DO NOT USE PYTHON** - LLM context awareness required
2. **Full provenance** - Every entity needs original text snippet
3. **Controlled vocabularies** - Normalize honors/titles/positions
4. **Location context** - Always include mentioned_in vs actual_location
5. **Quality over speed** - Confidence >0.85, validate economic data

---

## File Structure

```
knowledge_graph_v4/
├── README.md (this file)
├── QUICK_START_PROMPTS.md (copy-paste ready)
├── TASK_PROMPT_MALTA.md (detailed template)
│
├── MALTA/              ✅ COMPLETED
│   ├── 1867_MALTA.json
│   ├── 1950_MALTA.json (validated example)
│   └── ... (46 files total)
│
├── CEYLON/             ← Process next
├── JAMAICA/
├── BARBADOS/
└── [other colonies]/
```

---

## Success Criteria for Batch 1

- ✅ 20 colonies processed
- ✅ ~950 colony-year JSON files
- ✅ ~25,000 entities extracted
- ✅ Average confidence >0.90
- ✅ 100% provenance coverage
- ✅ No academic degrees in honors field

---

## Ready to Run! 🚀

**On Claude Code Online:**

1. Open `knowledge_graph_v4/QUICK_START_PROMPTS.md`
2. Copy prompt for CEYLON
3. Paste into Claude Code Online
4. Repeat for remaining 19 colonies
5. Submit all in parallel if supported

**Expected completion: 3-5 hours for all 20 colonies**

---

**REMEMBER: DO NOT USE PYTHON - use Tasks with LLM context awareness!**

See `QUICK_START_PROMPTS.md` for ready-to-use extraction prompts.
