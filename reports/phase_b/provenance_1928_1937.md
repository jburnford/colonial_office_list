# Provenance Linking Report: 1928-1937

**Generated:** 2025-11-17 02:41:19

**Agent:** provenance_linker_1928_1937

## Executive Summary

- **Total Entities Processed:** 45,150
- **Entities with Provenance:** 45,150
- **Coverage:** 100.00%
- **Years Processed:** 8

## Year-by-Year Statistics

### 1928

- **Total Entities:** 10,127
- **With Provenance:** 10,127
- **Coverage:** 100.00%

**By Entity Type:**

- demographics: 12
- economic_data: 2,786
- events: 1,438
- infrastructure: 129
- institutions: 145
- people: 5,569
- places: 48

**By Confidence Level:**

- good_0.85-0.94: 898
- high_0.95+: 196
- low_<0.70: 1,748
- medium_0.70-0.84: 7,285

### 1929

- **Total Entities:** 2,029
- **With Provenance:** 2,029
- **Coverage:** 100.00%

**By Entity Type:**

- demographics: 18
- economic_data: 179
- events: 496
- infrastructure: 184
- institutions: 171
- people: 468
- places: 513

**By Confidence Level:**

- good_0.85-0.94: 395
- high_0.95+: 124
- medium_0.70-0.84: 1,510

### 1930

- **Total Entities:** 1,922
- **With Provenance:** 1,922
- **Coverage:** 100.00%

**By Entity Type:**

- demographics: 33
- economic_data: 72
- infrastructure: 104
- institutions: 326
- people: 978
- places: 409

**By Confidence Level:**

- good_0.85-0.94: 3
- high_0.95+: 29
- low_<0.70: 239
- medium_0.70-0.84: 1,651

### 1931

- **Total Entities:** 20,739
- **With Provenance:** 20,739
- **Coverage:** 100.00%

**By Entity Type:**

- demographics: 58
- economic_data: 17
- events: 409
- infrastructure: 235
- people: 19,359
- places: 661

**By Confidence Level:**

- good_0.85-0.94: 243
- high_0.95+: 45
- low_<0.70: 401
- medium_0.70-0.84: 20,050

### 1932

- **Total Entities:** 3,778
- **With Provenance:** 3,778
- **Coverage:** 100.00%

**By Entity Type:**

- demographics: 10
- economic_data: 2
- events: 257
- infrastructure: 504
- institutions: 591
- people: 2,238
- places: 176

**By Confidence Level:**

- good_0.85-0.94: 721
- high_0.95+: 426
- medium_0.70-0.84: 2,631

### 1933

- **Total Entities:** 4,114
- **With Provenance:** 4,114
- **Coverage:** 100.00%

**By Entity Type:**

- demographics: 29
- economic_data: 55
- events: 211
- infrastructure: 753
- institutions: 811
- people: 1,676
- places: 579

**By Confidence Level:**

- good_0.85-0.94: 369
- high_0.95+: 297
- low_<0.70: 991
- medium_0.70-0.84: 2,457

### 1936

- **Total Entities:** 117
- **With Provenance:** 117
- **Coverage:** 100.00%

**By Entity Type:**

- demographics: 18
- economic_data: 11
- events: 39
- infrastructure: 10
- institutions: 8
- people: 16
- places: 15

**By Confidence Level:**

- low_<0.70: 47
- medium_0.70-0.84: 70

### 1937

- **Total Entities:** 2,324
- **With Provenance:** 2,324
- **Coverage:** 100.00%

**By Entity Type:**

- demographics: 1
- events: 115
- infrastructure: 174
- institutions: 481
- people: 1,509
- places: 44

**By Confidence Level:**

- good_0.85-0.94: 89
- high_0.95+: 183
- low_<0.70: 345
- medium_0.70-0.84: 1,707

## Confidence Score Distribution

| Confidence Range | Count | Percentage |
|-----------------|-------|------------|
| high 0.95+ | 1,300 | 2.88% |
| good 0.85-0.94 | 2,718 | 6.02% |
| medium 0.70-0.84 | 37,361 | 82.75% |
| low <0.70 | 3,771 | 8.35% |

## Entity Type Distribution

| Entity Type | Count | Percentage |
|------------|-------|------------|
| people | 31,813 | 70.46% |
| economic_data | 3,122 | 6.91% |
| events | 2,965 | 6.57% |
| institutions | 2,533 | 5.61% |
| places | 2,445 | 5.42% |
| infrastructure | 2,093 | 4.64% |
| demographics | 179 | 0.40% |

## Methodology

### Provenance Linking Process

1. **Entity Identification:** Each entity in the knowledge graph was analyzed to determine:
   - Its associated colony/territory
   - Relevant search terms (names, titles, positions)
   - Expected source section

2. **Source File Mapping:** Entities were mapped to source markdown files in:
   - `output_2/{YEAR}_manual_parsed/{COLONY}.md`

3. **Text Matching:** For each entity:
   - Search terms were used to locate mentions in source files
   - Line numbers of matches were recorded
   - Confidence scores were assigned based on match quality

4. **Confidence Scoring:**
   - **0.95-1.0:** Exact text match with multiple occurrences
   - **0.85-0.94:** Strong contextual match
   - **0.70-0.84:** Inferred from metadata or single match
   - **< 0.70:** Flag for human review

### Provenance Schema

Each entity now includes:

```json
{
  "provenance": {
    "source_file": "output_2/YEAR_manual_parsed/COLONY.md",
    "source_lines": "50-75",
    "source_section": "Government Establishment",
    "extraction_confidence": 0.95,
    "extraction_date": "2025-11-17",
    "extraction_agent": "provenance_linker_1928_1937",
    "verification_status": "automated"
  }
}
```

## Output Files

Enhanced knowledge graph files with provenance:

- `knowledge_graph_extracts_v3/1928_extracted.json`
- `knowledge_graph_extracts_v3/1929_extracted.json`
- `knowledge_graph_extracts_v3/1930_extracted.json`
- `knowledge_graph_extracts_v3/1931_extracted.json`
- `knowledge_graph_extracts_v3/1932_extracted.json`
- `knowledge_graph_extracts_v3/1933_extracted.json`
- `knowledge_graph_extracts_v3/1936_extracted.json`
- `knowledge_graph_extracts_v3/1937_extracted.json`

## Next Steps

1. **Human Review:** Entities with confidence < 0.70 should be manually verified
2. **Source Validation:** Random sampling to verify provenance accuracy
3. **Integration:** Use provenance links for ground truth analysis
4. **Extension:** Apply same methodology to remaining years

---

*Report generated by provenance_linker_1928_1937 on 2025-11-17*
