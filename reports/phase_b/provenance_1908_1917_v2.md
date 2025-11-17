# Provenance Linking Report V2: 1908-1917
Generated: 2025-11-17 02:47:31
Agent: provenance_linker_v2 (Enhanced with cross-file search)

## Summary Statistics

- **Years Processed**: 6 / 6
- **Total Entities Processed**: 26,061
- **Entities with Provenance**: 24,250
- **Overall Coverage**: 93.1%
- **Cross-File Matches**: 13,887 (entities found via full-text search)

## Confidence Distribution

| Confidence Level | Count | Percentage |
|-----------------|-------|------------|
| High (0.95-1.0) | 23,557 | 97.1% |
| Medium (0.85-0.94) | 176 | 0.7% |
| Low (0.70-0.84) | 517 | 2.1% |
| Flagged for Review (<0.70) | 0 | 0.0% |

## Year-by-Year Breakdown

| Year | Total Entities | With Provenance | Coverage |
|------|---------------|-----------------|----------|
| 1908 | 8,492 | 8,492 | 100.0% |
| 1909 | 1,476 | 1,202 | 81.4% |
| 1910 | 78 | 57 | 73.1% |
| 1911 | 123 | 86 | 69.9% |
| 1915 | 4,685 | 4,193 | 89.5% |
| 1917 | 11,207 | 10,220 | 91.2% |

## Improvements in V2

1. **Cross-File Search**: When colony field is missing, searches all source files
2. **Better Text Matching**: Enhanced multi-strategy text search
3. **File Caching**: Pre-loads all source files for faster processing
4. **Broader Coverage**: Can link entities without explicit colony assignments

## Provenance Schema

Each entity now includes a `provenance` object:

```json
{
  "provenance": {
    "source_file": "output_2/YYYY_manual_parsed/COLONY_NAME.md",
    "source_lines": "120-145",
    "source_section": "Government Officials",
    "extraction_confidence": 0.95,
    "extraction_date": "2025-11-17",
    "extraction_agent": "provenance_linker_v2_1908_1917",
    "verification_status": "automated"
  }
}
```

## Confidence Scoring Methodology

- **0.95-1.0**: Exact text match found in source file
- **0.85-0.94**: Strong contextual match (3+ keywords matched)
- **0.70-0.84**: Inferred from metadata or 2 keywords matched
- **< 0.70**: Flagged for human review

## Next Steps

1. Validate sample entities from each year
2. Review flagged entities (confidence < 0.70)
3. Use provenance for ground truth validation
4. Extend to remaining years

## Output

Enhanced KG files: `knowledge_graph_extracts_v3/`
