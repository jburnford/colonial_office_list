# Colonial Office List Parser

A Python tool for extracting structured data from Colonial Office Lists (1883-1915) to build a knowledge graph of British Empire employees and their career progressions.

## Overview

The Colonial Office Lists were annual publications detailing the administrative structure, personnel, and statistics of British colonial dependencies. This parser extracts:

- Colony sections and boundaries
- Employee records (names, positions, salaries, honors)
- Department structures
- Career progression data across multiple years

## Quick Start

### Parse a Single Document

```bash
python3 colonial_office_parser.py historical_document_pipeline/processed_pdfs/colonial-office-list-1896.json
```

### With Custom Output

```bash
python3 colonial_office_parser.py input.json \
  -o output/parsed.json \
  -r output/report.txt
```

## Features

### Colony Section Detection

Automatically identifies and segments ~50+ colony sections including:
- Major colonies (Canada, Australia, India, etc.)
- Caribbean colonies (Jamaica, Barbados, Trinidad, etc.)
- African colonies (Cape, Natal, Sierra Leone, etc.)
- Asian colonies (Ceylon, Hong Kong, Straits Settlements, etc.)
- Pacific colonies (Fiji, New Zealand, etc.)
- Mediterranean and other territories (Malta, Gibraltar, Cyprus, etc.)

### Employee Record Extraction

Extracts structured employee data:
- **Name**: Full name with honors/titles separated
- **Position**: Official title/role
- **Salary**: Compensation (when recorded)
- **Location**: Colony/territory
- **Honors**: K.C.M.G., C.B., etc.
- **Department**: Organizational unit

### Intelligent Parsing

- **Position validation**: Uses keyword matching to identify genuine positions
- **Name validation**: Distinguishes names from descriptive text
- **Honor extraction**: Automatically identifies and extracts titles/honors
- **Context tracking**: Maintains department context for employee records

## Output Format

### JSON Structure

```json
{
  "source_file": "colonial-office-list-1896.json",
  "year": 1896,
  "total_colonies": 52,
  "total_employees": 1110,
  "colonies": [
    {
      "colony_name": "CANADA",
      "year": 1896,
      "start_char": 123456,
      "end_char": 234567,
      "text": "...",
      "employees": [
        {
          "name": "Richard Pope",
          "position": "Deputy Commissioner of Patents",
          "salary": "$2,800",
          "location": "CANADA",
          "honors": null,
          "raw_text": "Deputy Commissioner of Patents, Richard Pope, $2,800."
        }
      ],
      "departments": ["DEPARTMENT OF MARINE AND FISHERIES", ...]
    }
  ]
}
```

### Summary Report

The parser generates a text report with:
- Total colonies and employees
- Employee count by colony
- Sample employee records
- Parsing statistics

## Building a Knowledge Graph

### Multi-Year Analysis

To track career progression across years:

```bash
# Parse all available years
for year in 1896 1897 1898 ...; do
  python3 colonial_office_parser.py \
    "historical_document_pipeline/processed_pdfs/colonial-office-list-${year}.json" \
    -o "output/parsed-${year}.json"
done

# Build knowledge graph
python3 build_knowledge_graph.py output/parsed-*.json
```

### Knowledge Graph Structure

The knowledge graph links:
- **Person nodes**: Individual employees
- **Position nodes**: Roles/titles
- **Colony nodes**: Territories
- **Year edges**: Temporal relationships
- **Career edges**: Position changes and promotions

See `build_knowledge_graph.py` for implementation.

## Data Quality

### Current Performance (1896 Colonial Office List)

- **Colonies identified**: 52
- **Employees extracted**: 1,110
- **Precision**: ~85-90% (based on manual sampling)
- **Recall**: ~70-80% (some records in unusual formats missed)

### Known Limitations

1. **Multiple entries**: Some colonies appear multiple times (cross-references)
2. **Incomplete names**: Titles like "Lieut." sometimes extracted without full name
3. **Complex records**: Multi-person entries (e.g., "Examiners: A, B, C...") partially supported
4. **Tables**: Employee data in table format may be missed
5. **Variations**: Each year may have slightly different formatting

### Improvement Strategies

For better results:
- Add year-specific patterns
- Enhance multi-person record parsing
- Implement table detection
- Add manual corrections for known issues
- Validate against reference data

## Extending the Parser

### Adding New Colony Patterns

Edit `COLONY_PATTERNS` in `colonial_office_parser.py`:

```python
COLONY_PATTERNS = [
    r'^(YOUR_COLONY_NAME)\.$',
    ...
]
```

### Adding New Position Keywords

Edit `POSITION_KEYWORDS`:

```python
POSITION_KEYWORDS = [
    'YourNewTitle', 'AnotherRole', ...
]
```

### Custom Employee Patterns

For unusual formats, add to `EMPLOYEE_PATTERNS`:

```python
EMPLOYEE_PATTERNS = [
    r'^your_custom_pattern$',
    ...
]
```

## Requirements

- Python 3.7+
- Standard library only (no external dependencies)

## File Structure

```
colonial_office_list/
├── colonial_office_parser.py    # Main parser script
├── build_knowledge_graph.py     # Knowledge graph builder (TODO)
├── README.md                     # This file
├── historical_document_pipeline/
│   └── processed_pdfs/
│       ├── colonial-office-list-1896.json
│       └── ...
└── output/
    ├── colonial-office-1896-parsed.json
    ├── colonial-office-1896-report.txt
    └── ...
```

## Future Work

### Phase 1: Complete Basic Parser ✓
- [x] Colony section detection
- [x] Employee record extraction
- [x] JSON export
- [x] Summary reports

### Phase 2: Knowledge Graph (In Progress)
- [ ] Person entity resolution (matching same person across years)
- [ ] Career path extraction
- [ ] Relationship mapping
- [ ] Graph database integration (Neo4j)

### Phase 3: Advanced Analysis
- [ ] Career progression patterns
- [ ] Colonial administration networks
- [ ] Geographic mobility analysis
- [ ] Promotion rates and career trajectories
- [ ] Social network analysis

### Phase 4: Web Interface
- [ ] Search interface
- [ ] Visual career timeline
- [ ] Network visualization
- [ ] Export to various formats

## Contributing

This parser is designed to work across 80+ Colonial Office List documents (1883-1915). When making improvements:

1. Test on multiple years
2. Maintain backward compatibility
3. Document year-specific quirks
4. Add regression tests

## References

- Colonial Office Lists: Annual publications 1862-1966
- This project focuses on 1883-1915 period
- Original PDFs OCR'd using OLMocr 0.3.4

## License

[Your License Here]

## Contact

[Your Contact Info]
