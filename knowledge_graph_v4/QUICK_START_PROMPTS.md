# Quick Start Extraction Prompts for Claude Code Online

## Instructions
1. Copy each prompt below
2. Paste into Claude Code Online
3. It will create a Task and process the colony
4. Repeat for all 20 colonies in Batch 1

---

## ✅ 1. MALTA (COMPLETED - Test Success!)
Status: ✓ Complete (46 years, 98.7% confidence)
Skip this one - already done!

---

## 2. CEYLON

```
Extract knowledge graph for CEYLON across all years (1867-1966).

Source: /home/jic823/colonialofficelist/output_2/{YEAR}_manual_parsed/CEYLON.md
Schema: /home/jic823/colonialofficelist/knowledge_graph_extracts_v3/schema_v2.json
Vocabulary: /home/jic823/colonialofficelist/knowledge_graph_extracts_v3/master_vocabulary_filtered.json
Example: /home/jic823/colonialofficelist/knowledge_graph_extracts_v3/example_1950_CEYLON.json

Task:
1. Find all years where CEYLON appears (check 1867-1966)
2. For each year, extract entities following schema v2.0:
   - Colony info (capital: Colombo, area, population)
   - Places (cities, districts)
   - People (Governor, Colonial Secretary, judges, officials with salaries)
   - Institutions (Executive Council, Legislative Council, courts, departments)
   - Economic data (revenue, expenditure, trade)
   - Infrastructure (Ceylon Government Railway, ports, telegraph)
   - Events (1815 annexation, constitutional changes)
   - Relationships (person-position, reports_to, institution hierarchy)

3. Use controlled vocabularies:
   - Honors: KCMG, CMG, OBE (exclude BA, MA, MD degrees)
   - Titles: Sir, Hon, Rev, Dr
   - Positions: Governor, Colonial Secretary, Chief Justice, etc.

4. Quality requirements:
   - Full provenance with original text snippets (required!)
   - Extraction confidence >0.85
   - Location context with certainty levels
   - Coordinates only if stated in source

Output: /home/jic823/colonialofficelist/knowledge_graph_v4/CEYLON/{year}_CEYLON.json

Return summary: years processed, total entities, sample people extracted, quality metrics.
```

---

## 3. JAMAICA

```
Extract knowledge graph for JAMAICA across all years (1867-1966).

Source: /home/jic823/colonialofficelist/output_2/{YEAR}_manual_parsed/JAMAICA.md
Schema: /home/jic823/colonialofficelist/knowledge_graph_extracts_v3/schema_v2.json
Vocabulary: /home/jic823/colonialofficelist/knowledge_graph_extracts_v3/master_vocabulary_filtered.json
Example: /home/jic823/colonialofficelist/knowledge_graph_extracts_v3/example_1950_CEYLON.json

Task:
1. Find all years where JAMAICA appears
2. Extract entities following schema v2.0 (see CEYLON prompt for details)
3. Key features for Jamaica:
   - Capital: Kingston
   - Important officials: Governor, Colonial Secretary, Chief Justice
   - Economic: Sugar production, exports
   - Infrastructure: Railways, ports

Output: /home/jic823/colonialofficelist/knowledge_graph_v4/JAMAICA/{year}_JAMAICA.json

Follow same quality requirements as CEYLON extraction.
```

---

## 4. BARBADOS

```
Extract knowledge graph for BARBADOS across all years (1867-1966).

Source: /home/jic823/colonialofficelist/output_2/{YEAR}_manual_parsed/BARBADOS.md
Schema: /home/jic823/colonialofficelist/knowledge_graph_extracts_v3/schema_v2.json
Vocabulary: /home/jic823/colonialofficelist/knowledge_graph_extracts_v3/master_vocabulary_filtered.json
Example: /home/jic823/colonialofficelist/knowledge_graph_extracts_v3/example_1950_CEYLON.json

Task:
1. Find all years where BARBADOS appears
2. Extract entities following schema v2.0
3. Key features:
   - Capital: Bridgetown
   - Small island colony
   - Focus on government structure, officials, economic data

Output: /home/jic823/colonialofficelist/knowledge_graph_v4/BARBADOS/{year}_BARBADOS.json

Same quality requirements apply.
```

---

## 5. TRINIDAD (may appear as TRINIDAD_AND_TOBAGO)

```
Extract knowledge graph for TRINIDAD (and TRINIDAD_AND_TOBAGO) across all years (1867-1966).

Source: /home/jic823/colonialofficelist/output_2/{YEAR}_manual_parsed/TRINIDAD*.md
Check both TRINIDAD.md and TRINIDAD_AND_TOBAGO.md

Schema: /home/jic823/colonialofficelist/knowledge_graph_extracts_v3/schema_v2.json
Vocabulary: /home/jic823/colonialofficelist/knowledge_graph_extracts_v3/master_vocabulary_filtered.json
Example: /home/jic823/colonialofficelist/knowledge_graph_extracts_v3/example_1950_CEYLON.json

Task:
1. Find all years where TRINIDAD or TRINIDAD_AND_TOBAGO appears
2. Extract entities following schema v2.0
3. Key features:
   - Capital: Port of Spain
   - Two islands: Trinidad and Tobago
   - Mark Tobago locations with location_context

Output: /home/jic823/colonialofficelist/knowledge_graph_v4/TRINIDAD/{year}_TRINIDAD.json

Same quality requirements.
```

---

## 6. HONG_KONG

```
Extract knowledge graph for HONG_KONG across all years (1867-1966).

Source: /home/jic823/colonialofficelist/output_2/{YEAR}_manual_parsed/HONG_KONG.md
Schema: /home/jic823/colonialofficelist/knowledge_graph_extracts_v3/schema_v2.json
Vocabulary: /home/jic823/colonialofficelist/knowledge_graph_extracts_v3/master_vocabulary_filtered.json
Example: /home/jic823/colonialofficelist/knowledge_graph_extracts_v3/example_1950_CEYLON.json

Task:
1. Find all years where HONG_KONG appears
2. Extract entities following schema v2.0
3. Key features:
   - Capital: Victoria
   - Major trading port
   - Interactions with China (mark with location_context when Chinese locations mentioned)

Output: /home/jic823/colonialofficelist/knowledge_graph_v4/HONG_KONG/{year}_HONG_KONG.json

Same quality requirements.
```

---

## 7. FIJI

```
Extract knowledge graph for FIJI across all years (1867-1966).

Source: /home/jic823/colonialofficelist/output_2/{YEAR}_manual_parsed/FIJI*.md
Schema: /home/jic823/colonialofficelist/knowledge_graph_extracts_v3/schema_v2.json
Vocabulary: /home/jic823/colonialofficelist/knowledge_graph_extracts_v3/master_vocabulary_filtered.json
Example: /home/jic823/colonialofficelist/knowledge_graph_extracts_v3/example_1950_CEYLON.json

Task:
1. Find all years where FIJI appears
2. Extract entities following schema v2.0
3. Key features:
   - Capital: Suva
   - Pacific colony
   - Multiple islands

Output: /home/jic823/colonialofficelist/knowledge_graph_v4/FIJI/{year}_FIJI.json

Same quality requirements.
```

---

## 8. MAURITIUS

```
Extract knowledge graph for MAURITIUS across all years (1867-1966).

Source: /home/jic823/colonialofficelist/output_2/{YEAR}_manual_parsed/MAURITIUS.md
Schema: /home/jic823/colonialofficelist/knowledge_graph_extracts_v3/schema_v2.json
Vocabulary: /home/jic823/colonialofficelist/knowledge_graph_extracts_v3/master_vocabulary_filtered.json
Example: /home/jic823/colonialofficelist/knowledge_graph_extracts_v3/example_1950_CEYLON.json

Task:
1. Find all years where MAURITIUS appears
2. Extract entities following schema v2.0
3. Key features:
   - Capital: Port Louis
   - Indian Ocean island
   - French colonial heritage (may mention French locations)

Output: /home/jic823/colonialofficelist/knowledge_graph_v4/MAURITIUS/{year}_MAURITIUS.json

Same quality requirements.
```

---

## 9. CYPRUS

```
Extract knowledge graph for CYPRUS across all years (1867-1966).

Source: /home/jic823/colonialofficelist/output_2/{YEAR}_manual_parsed/CYPRUS.md
Schema: /home/jic823/colonialofficelist/knowledge_graph_extracts_v3/schema_v2.json
Vocabulary: /home/jic823/colonialofficelist/knowledge_graph_extracts_v3/master_vocabulary_filtered.json
Example: /home/jic823/colonialofficelist/knowledge_graph_extracts_v3/example_1950_CEYLON.json

Task:
1. Find all years where CYPRUS appears
2. Extract entities following schema v2.0
3. Key features:
   - Capital: Nicosia
   - Mediterranean island
   - British protectorate from 1878

Output: /home/jic823/colonialofficelist/knowledge_graph_v4/CYPRUS/{year}_CYPRUS.json

Same quality requirements.
```

---

## 10. GIBRALTAR

```
Extract knowledge graph for GIBRALTAR across all years (1867-1966).

Source: /home/jic823/colonialofficelist/output_2/{YEAR}_manual_parsed/GIBRALTAR.md
Schema: /home/jic823/colonialofficelist/knowledge_graph_extracts_v3/schema_v2.json
Vocabulary: /home/jic823/colonialofficelist/knowledge_graph_extracts_v3/master_vocabulary_filtered.json
Example: /home/jic823/colonialofficelist/knowledge_graph_extracts_v3/example_1950_CEYLON.json

Task:
1. Find all years where GIBRALTAR appears
2. Extract entities following schema v2.0
3. Key features:
   - Small strategic territory
   - Military importance (may mention Royal Navy, Army)
   - Adjacent to Spain (mark Spanish locations appropriately)

Output: /home/jic823/colonialofficelist/knowledge_graph_v4/GIBRALTAR/{year}_GIBRALTAR.json

Same quality requirements.
```

---

## Batch Processing Script

If you want to submit all 20 colonies at once:

```python
colonies_batch1 = [
    "CEYLON", "JAMAICA", "BARBADOS", "TRINIDAD", "HONG_KONG",
    "FIJI", "MAURITIUS", "CYPRUS", "GIBRALTAR", "BERMUDA",
    "BAHAMAS", "BRITISH_GUIANA", "BRITISH_HONDURAS", "SEYCHELLES",
    "ST_LUCIA", "GRENADA", "ANTIGUA", "DOMINICA", "MONTSERRAT", "KENYA"
]

# For each colony, submit the extraction prompt as shown above
# Replace COLONY_NAME in the template with actual name
```

---

## Quality Check After Each Colony

Run this check:
```bash
python3 -c "
import json, glob
files = glob.glob('/home/jic823/colonialofficelist/knowledge_graph_v4/[COLONY]/*.json')
print(f'Files: {len(files)}')
for f in files[:3]:
    with open(f) as fp:
        data = json.load(fp)
        print(f'{f}: {len(data[\"entities\"][\"people\"])} people extracted')
"
```

---

## Notes

- **Model**: Use haiku for efficiency (fast, cheap, good quality)
- **Parallel**: Submit all 20 colonies simultaneously if Claude Code supports it
- **Time**: Each colony takes 1-3 hours, but running in parallel = ~3-5 hours total for Batch 1
- **Cost**: Estimated $2-5 per colony, ~$50-100 for all 20
- **Malta**: Already complete, use as reference!
