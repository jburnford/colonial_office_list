# Provenance Quick Reference Guide

## For Researchers Using the Knowledge Graph

### What is Provenance?

Every entity in the enhanced knowledge graph files now includes a `provenance` object that tells you:
- Which source file it came from
- The exact line number(s) in that file
- How confident we are in the link (0-1 scale)
- When and how it was linked

### File Locations

**Enhanced KG Files**: `/home/user/colonial_office_list/knowledge_graph_extracts_v3/`
**Years Available**: 1908, 1909, 1910, 1911, 1915, 1917

### Quick Verification

```python
# Load entity
import json
with open('knowledge_graph_extracts_v3/1908_extracted.json') as f:
    data = json.load(f)

# Get an entity
entity = data['entities']['people'][0]

# Check provenance
if 'provenance' in entity:
    print(f"Source: {entity['provenance']['source_file']}")
    print(f"Line: {entity['provenance']['source_lines']}")
    print(f"Confidence: {entity['provenance']['extraction_confidence']}")
```

### Confidence Levels

- **0.95-1.0**: EXACT MATCH - Use with confidence
- **0.85-0.94**: STRONG MATCH - Generally reliable
- **0.70-0.84**: MODERATE MATCH - Verify if critical
- **<0.70**: LOW CONFIDENCE - Review before use

### View Source Context

```bash
# Given an entity with provenance:
# source_file: "output_2/1908_manual_parsed/BAHAMAS.md"
# source_lines: "28"

# View the source:
sed -n '25,30p' output_2/1908_manual_parsed/BAHAMAS.md
```

### Coverage by Year

| Year | Coverage | Total Entities |
|------|----------|----------------|
| 1908 | 100% | 8,492 |
| 1909 | 81% | 1,476 |
| 1910 | 73% | 78 |
| 1911 | 70% | 123 |
| 1915 | 90% | 4,685 |
| 1917 | 91% | 11,207 |

### Filter by Confidence

```python
# Get only high-confidence entities
high_conf = [
    p for p in data['entities']['people']
    if 'provenance' in p and p['provenance']['extraction_confidence'] >= 0.95
]

print(f"High confidence entities: {len(high_conf)}")
```

### Common Use Cases

**1. Academic Citation**
```
"Lees, Sir C. C., Governor of Bahamas (1882)
Source: Colonial Office List 1908, Bahamas section, line 28"
```

**2. Verify Extraction**
```python
def verify(entity):
    prov = entity['provenance']
    with open(prov['source_file']) as f:
        lines = f.readlines()
        line_num = int(prov['source_lines'].split('-')[0])
        return lines[line_num - 1]
```

**3. Quality Filter**
```python
# Only use high-quality extractions
reliable_data = [
    e for e in entities
    if 'provenance' in e and e['provenance']['extraction_confidence'] > 0.90
]
```

### Reports

- **Main Report**: `reports/phase_b/provenance_1908_1917_v2.md`
- **Validation Examples**: `reports/phase_b/provenance_validation_samples.md`
- **Complete Summary**: `PROVENANCE_LINKING_COMPLETE.md`

### Questions?

- See full documentation in `PROVENANCE_LINKING_COMPLETE.md`
- Check sample entities in `provenance_validation_samples.md`
- Review technical details in `add_provenance_v2.py`
