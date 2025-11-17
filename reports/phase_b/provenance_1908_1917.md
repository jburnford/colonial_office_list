# Provenance Linking Report: 1908-1917
Generated: 2025-11-17 02:39:14

## Summary Statistics

- **Years Processed**: 6 / 6
- **Total Entities Processed**: 26,061
- **Entities with Provenance**: 11,403
- **Overall Coverage**: 43.8%

## Confidence Distribution

| Confidence Level | Count | Percentage |
|-----------------|-------|------------|
| High (0.95-1.0) | 10,736 | 94.2% |
| Medium (0.85-0.94) | 102 | 0.9% |
| Low (0.70-0.84) | 542 | 4.8% |
| Flagged for Review (<0.70) | 23 | 0.2% |

## Year-by-Year Breakdown

| Year | Total Entities | With Provenance | Coverage |
|------|---------------|-----------------|----------|
| 1908 | 8,492 | 8,492 | 100.0% |
| 1909 | 1,476 | 1,389 | 94.1% |
| 1910 | 78 | 37 | 47.4% |
| 1911 | 123 | 57 | 46.3% |
| 1915 | 4,685 | 854 | 18.2% |
| 1917 | 11,207 | 574 | 5.1% |

## Provenance Schema

Each entity now includes a `provenance` object with the following structure:

```json
{
  "provenance": {
    "source_file": "output_2/YYYY_manual_parsed/COLONY_NAME.md",
    "source_lines": "120-145",
    "source_section": "Government Officials",
    "extraction_confidence": 0.95,
    "extraction_date": "2025-11-17",
    "extraction_agent": "provenance_linker_1908_1917",
    "verification_status": "automated"
  }
}
```

## Confidence Scoring Methodology

- **0.95-1.0**: Exact text match found in source file
- **0.85-0.94**: Strong contextual match (3+ keywords matched)
- **0.70-0.84**: Inferred from metadata or 2 keywords matched
- **< 0.70**: Flagged for human review (text not found, missing source)

## Next Steps

1. Review entities flagged for manual verification (confidence < 0.70)
2. Validate provenance links for sample entities
3. Use provenance for ground truth analysis and data quality checks
4. Extend provenance linking to remaining years

## Files Generated

Enhanced KG files created in: `knowledge_graph_extracts_v3/`
