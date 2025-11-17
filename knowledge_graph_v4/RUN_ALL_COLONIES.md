# Colonial Office List - Complete Knowledge Graph Extraction

## Overview
Extract structured knowledge graphs for all major British colonies (1867-1966) using Claude Code Online with parallel Task processing.

## Setup (One-Time)

### 1. Upload Required Files
Upload these to Claude Code Online workspace:
- `/knowledge_graph_extracts_v3/schema_v2.json` - JSON schema
- `/knowledge_graph_extracts_v3/master_vocabulary_filtered.json` - Controlled vocabularies
- `/knowledge_graph_extracts_v3/example_1950_CEYLON.json` - Reference example
- `/knowledge_graph_extracts_v3/example_1950_v2.json` - Alternative example
- `/knowledge_graph_v4/TASK_PROMPT_MALTA.md` - Task template
- `/knowledge_graph_v4/COLONIES_LIST.txt` - List of colonies to process

### 2. Source Data
Ensure you have access to:
- `/home/jic823/colonialofficelist/output_2/` - OCR'd markdown files

## Extraction Strategy

### Parallel Processing Plan
**Total Colonies: ~100 major territories**

**Batch 1: High Priority (20 colonies)**
These are large, consistently documented colonies:
1. CEYLON
2. JAMAICA
3. MALTA
4. BARBADOS
5. TRINIDAD
6. HONG_KONG
7. FIJI
8. MAURITIUS
9. CYPRUS
10. GIBRALTAR
11. BERMUDA
12. BAHAMAS
13. BRITISH_GUIANA
14. BRITISH_HONDURAS
15. SEYCHELLES
16. ST_LUCIA
17. GRENADA
18. ANTIGUA
19. DOMINICA
20. MONTSERRAT

**Batch 2: African Colonies (15)**
21. KENYA
22. UGANDA
23. TANGANYIKA
24. ZANZIBAR
25. NORTHERN_RHODESIA
26. SOUTHERN_RHODESIA
27. NYASALAND
28. NIGERIA
29. GOLD_COAST
30. SIERRA_LEONE
31. THE_GAMBIA
32. BASUTOLAND
33. BECHUANALAND_PROTECTORATE
34. SWAZILAND
35. BRITISH_SOMALILAND

**Batch 3: Asian/Pacific Colonies (15)**
36. FEDERATION_OF_MALAYA
37. SINGAPORE
38. BRUNEI
39. SARAWAK
40. NORTH_BORNEO
41. BRITISH_SOLOMON_ISLANDS
42. FIJI
43. TONGA
44. NEW_ZEALAND
45. NEW_SOUTH_WALES
46. VICTORIA
47. QUEENSLAND
48. TASMANIA
49. WESTERN_AUSTRALIA
50. GILBERT_AND_ELLICE_ISLANDS

**Batch 4: Historical/Smaller Territories (20)**
51. ADEN
52. CAPE_OF_GOOD_HOPE
53. NATAL
54. TRANSVAAL
55. LABUAN
56. LAGOS
57. NEWFOUNDLAND
58. NOVA_SCOTIA
59. NEW_BRUNSWICK
60. PRINCE_EDWARD_ISLAND
61. BRITISH_COLUMBIA
62. FALKLAND_ISLANDS
63. ST_HELENA
64. ASCENSION
65. TRISTAN_DA_CUNHA
66. CAYMAN_ISLANDS
67. TURKS_AND_CAICOS_ISLANDS
68. BRITISH_VIRGIN_ISLANDS
69. PROTECTORATE_OF_SOUTH_ARABIA
70. FEDERATION_OF_SOUTH_ARABIA

## Running Extractions on Claude Code Online

### Method 1: Individual Colony Tasks (Recommended)

For each colony, create a Task:

```
Task: Extract [COLONY_NAME] knowledge graph

Read task instructions from: /knowledge_graph_v4/TASK_PROMPT_MALTA.md
(Replace "MALTA" with colony name throughout)

Source directory: /home/jic823/colonialofficelist/output_2/
Output directory: /home/jic823/colonialofficelist/knowledge_graph_v4/[COLONY_NAME]/

Process all years where [COLONY_NAME] appears, following schema v2.0.
Include full provenance with original text snippets for all entities.

Use haiku model for efficiency.
```

### Method 2: Batch Script (For Automation)

Create a file `run_batch_extraction.sh`:

```bash
#!/bin/bash

# List of colonies to process (Batch 1)
COLONIES=(
    "CEYLON"
    "JAMAICA"
    "MALTA"
    "BARBADOS"
    "TRINIDAD"
    "HONG_KONG"
    "FIJI"
    "MAURITIUS"
    "CYPRUS"
    "GIBRALTAR"
    "BERMUDA"
    "BAHAMAS"
    "BRITISH_GUIANA"
    "BRITISH_HONDURAS"
    "SEYCHELLES"
    "ST_LUCIA"
    "GRENADA"
    "ANTIGUA"
    "DOMINICA"
    "MONTSERRAT"
)

for COLONY in "${COLONIES[@]}"; do
    echo "Processing $COLONY..."

    # Call Claude Code API or CLI to create Task
    # Replace with actual Claude Code task invocation method

    # Example (pseudo-code):
    # claude-code task create \
    #   --prompt "Extract knowledge graph for $COLONY following /knowledge_graph_v4/TASK_PROMPT_MALTA.md" \
    #   --model haiku \
    #   --output "/knowledge_graph_v4/$COLONY/"

    echo "  Submitted task for $COLONY"
done

echo "All batch 1 tasks submitted!"
```

### Method 3: Parallel Task Execution

If Claude Code Online supports parallel tasks, submit all 20 Batch 1 colonies simultaneously:

```python
# Pseudo-code for parallel submission
colonies_batch1 = [
    "CEYLON", "JAMAICA", "MALTA", "BARBADOS", "TRINIDAD",
    "HONG_KONG", "FIJI", "MAURITIUS", "CYPRUS", "GIBRALTAR",
    "BERMUDA", "BAHAMAS", "BRITISH_GUIANA", "BRITISH_HONDURAS",
    "SEYCHELLES", "ST_LUCIA", "GRENADA", "ANTIGUA", "DOMINICA", "MONTSERRAT"
]

tasks = []
for colony in colonies_batch1:
    task = create_task(
        prompt=f"Extract knowledge graph for {colony} following schema v2.0",
        model="haiku",
        files=["schema_v2.json", "master_vocabulary_filtered.json"]
    )
    tasks.append(task)

# Monitor completion
monitor_tasks(tasks)
```

## Generic Task Prompt Template

For each colony, use this template:

```markdown
# Extract Knowledge Graph for [COLONY_NAME]

## Input
- Source: /home/jic823/colonialofficelist/output_2/{YEAR}_manual_parsed/[COLONY_NAME].md
- Schema: /knowledge_graph_extracts_v3/schema_v2.json
- Vocabulary: /knowledge_graph_extracts_v3/master_vocabulary_filtered.json
- Example: /knowledge_graph_extracts_v3/example_1950_CEYLON.json

## Task
1. Find all years where [COLONY_NAME] appears in output_2/
2. For each year, extract following schema v2.0:
   - Colony info (area, population, capital)
   - Places (cities, islands, territories)
   - People (officials with positions, salaries, honors)
   - Institutions (councils, courts, departments)
   - Economic data (revenue, expenditure, trade)
   - Infrastructure (railways, ports, telegraph)
   - Events (historical milestones)
   - Relationships (person-position-institution, reports_to, etc.)

3. Quality requirements:
   - Full provenance with original text snippets
   - Extraction confidence >0.85
   - Use controlled vocabularies for honors/titles/positions
   - Coordinates ONLY if stated in source
   - Location context with certainty levels
   - No academic degrees (BA, MA, MD) in honors field

4. Output: /knowledge_graph_v4/[COLONY_NAME]/{year}_[COLONY_NAME].json

## Return
- Years processed
- Total entities by type
- Sample extractions (5 people with positions)
- Data quality metrics
```

## Monitoring & Quality Control

### Progress Tracking
Create a status file:

```json
{
  "extraction_status": {
    "MALTA": {"status": "complete", "years": 46, "entities": 1520},
    "CEYLON": {"status": "in_progress", "years_done": 23, "years_total": 54},
    "JAMAICA": {"status": "queued", "years_total": 52},
    ...
  }
}
```

### Quality Checks
After each colony:
1. Validate JSON schema
2. Check provenance completeness (should be 100%)
3. Verify extraction confidence (avg >0.85)
4. Count entities per year (should be >5 minimum)
5. Check for academic degrees in honors field (should be 0)

## Resource Estimation

**Per Colony Average:**
- Years present: 30-40
- Processing time: 2-5 minutes per year (haiku)
- Total per colony: 1-3 hours
- Output size: ~50-200KB per year

**Total Workload:**
- 100 colonies × 35 years avg = 3,500 colony-years
- At 3 min/year = 175 hours sequential
- With 20 parallel tasks = ~9 hours wall-clock time
- With 50 parallel tasks = ~3.5 hours wall-clock time

**Claude Code Credit Usage:**
- Haiku pricing: ~$0.25 per million input tokens, $1.25 per million output
- Estimated: ~500 tokens input + 2000 tokens output per colony-year
- 3,500 years × $0.0025 ≈ $8.75 for input, $43.75 for output
- **Total estimated cost: ~$50-$100 for complete extraction**

With your $500 credit, you can comfortably process all colonies!

## Validation After Completion

Run these checks:

```bash
# Count total files
find knowledge_graph_v4 -name "*.json" | wc -l

# Check for errors
find knowledge_graph_v4 -name "*.json" -exec python3 -m json.tool {} \; >/dev/null

# Generate summary
python3 generate_extraction_summary.py
```

Expected output:
```
Total colony-years: 3,500+
Total entities: 100,000+
Average extraction confidence: 0.92
Provenance completeness: 100%
```

## Next Steps After Extraction

1. **Cross-Year Entity Linking** - Match same people/institutions across years
2. **Data Aggregation** - Build temporal graphs showing career trajectories
3. **Validation** - Spot-check random samples for accuracy
4. **Export** - Generate Neo4j import, CSV, RDF formats
5. **Analysis** - Run historical queries on complete dataset

## Quick Start Commands

### Test with Malta (Already Done ✓)
```
Malta extraction completed successfully:
- 46 years processed
- 11 people per year average
- 98.7% extraction confidence
- 100% provenance coverage
```

### Run Batch 1 (High Priority - 20 colonies)
Submit 20 parallel tasks, one for each colony in Batch 1 list above.

### Monitor Progress
```bash
watch -n 60 'ls -1 knowledge_graph_v4/*/2*.json | wc -l'
```

### Validate Outputs
```bash
python3 validate_extraction.py --colony CEYLON --check-all
```

---

**Ready to extract!** Your Malta test succeeded, schema is proven, vocabularies are ready. Just launch the tasks and let Claude Code process all colonies in parallel!
