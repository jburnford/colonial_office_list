# Colonial Office List Knowledge Graph Extracts (1957-1962)

Complete structured knowledge graph extraction from the Colonial Office Lists covering the years 1957 through 1962.

## Files Included

### Extracted Knowledge Graphs
- **1957_extracted.json** (592.5 KB) - 1,437 entities from 25 colonies
- **1958_extracted.json** (529.7 KB) - 1,227 entities from 20 colonies
- **1959_extracted.json** (472.4 KB) - 1,060 entities from 30 colonies
- **1960_extracted.json** (256.7 KB) - 615 entities from 30 colonies
- **1961_extracted.json** (522.9 KB) - 1,281 entities from 28 colonies
- **1962_extracted.json** (632.5 KB) - 1,497 entities from 64 colonies

### Documentation
- **EXTRACTION_SUMMARY_1957-1962.md** - Comprehensive extraction report with detailed statistics and methodology notes
- **README.md** - This file

## Aggregate Statistics

- **Total Years:** 6 (1957-1962)
- **Total Colonies/Territories:** 197
- **Total Entities:** 7,117
- **Total Relationships:** 4,413
- **Total Output Size:** 2.94 MB

## Entity Breakdown (All Years Combined)

| Entity Type | Count |
|------------|-------|
| Places (Geographic) | 336 |
| People (Officials) | 3,593 |
| Institutions (Governmental Bodies) | 1,220 |
| Economic Data | 1,906 |
| Infrastructure | 191 |
| Demographics | 11 |
| Events (Historical) | 160 |

## JSON Schema

Each extracted file follows the official schema defined in `/home/user/colonial_office_list/json_schema_template.json` with the following structure:

```
{
  "metadata": {
    "year": "YYYY",
    "source_directory": "path/to/source",
    "extraction_date": "ISO-8601 timestamp",
    "processing_notes": "Notes about extraction",
    "colonies_processed": ["Colony1", "Colony2", ...]
  },
  "entities": {
    "places": [...],
    "people": [...],
    "institutions": [...],
    "economic_data": [...],
    "infrastructure": [...],
    "demographics": [...],
    "events": [...]
  },
  "relationships": [...]
}
```

## Data Characteristics

### Places (Geographic Entities)
- Colony and territory names with exact historical spelling
- Principal cities and towns with population data
- Geographic features (rivers, mountains, bays, harbors, islands)
- Area measurements in square miles
- Hierarchical relationships (towns within colonies)

### People (Colonial Officials)
- Full names with titles (Sir, Rev., Dr., Major-General, etc.)
- Honors and decorations (K.C.M.G., C.B., O.B.E., etc.)
- Official positions and departments
- Location/colony of posting
- Salary information in British pounds (£)
- Allowances (quarters, table money, horse, etc.)
- Employment status (permanent, acting, temporary, vacant)

### Institutions
- Executive and Legislative Councils
- Courts (Supreme, Vice-Admiralty, Police Courts)
- Government departments
- Military units and garrisons
- Police forces
- Educational and medical institutions
- Postal and public works departments

### Economic Data
- Government revenue by year
- Budget expenditures by department
- Trade volumes (exports/imports)
- Shipping statistics
- Currency information
- Banking and financial institutions
- Production data

### Infrastructure
- Railway systems (routes, lengths, costs, revenue)
- Telegraph lines and communications
- Port and harbor facilities
- Roads and bridges
- Postal routes
- Water and sanitation systems

### Demographics
- Total population figures by colony
- Population breakdowns by origin/ethnicity (historical categorization)
- Urban vs. rural distributions
- Census dates and collection methods

### Events
- Establishment and founding dates
- Treaties and cessions
- Constitutional changes
- Rebellions and incidents
- Transfers of power and administration
- Significant appointments

## Historical Fidelity

All data has been extracted with strict adherence to historical accuracy:
- **Exact Spelling Preservation:** Place names and personal names extracted exactly as written in source documents
- **Currency Preservation:** Original currency denominations (£) maintained
- **Numerical Precision:** All financial figures, populations, and measurements preserved with exact values
- **Historical Terminology:** Period-accurate categories and classifications maintained (including historical terminology for ethnic/origin classifications)

## Methodology

Extraction followed the detailed methodology documented in `/home/user/colonial_office_list/EXTRACTION_METHODOLOGY.md`:

1. Year-by-year independent processing
2. Colony-by-colony sequential extraction
3. Entity-type-specific pattern recognition
4. Automatic relationship inference
5. Schema validation and verification

## Usage

These knowledge graphs can be:
- Queried directly using JSON tools
- Ingested into databases (relational or graph databases)
- Used for historical research and comparative analysis
- Visualized as networks or timelines
- Cross-referenced with other historical datasets

### Example Queries

- Who governed a specific colony in a given year?
- What was the population and demographic breakdown of a territory?
- What revenue/expenditure did a colony have in a specific year?
- How many institutions administered a territory?
- What infrastructure connected colonies?
- When were treaties or significant events executed?

## File Structure

Each extracted file is a valid JSON document containing:
- Comprehensive metadata about the extraction
- 7 categories of entities (places, people, institutions, economic data, infrastructure, demographics, events)
- Relationship mappings connecting entities (source→target with relationship type)

## Data Quality

All files have been verified for:
- Valid JSON syntax
- Required metadata fields
- Complete entity arrays
- Relationship integrity
- Unique entity IDs
- Schema compliance

## References

- **Extraction Methodology:** `/home/user/colonial_office_list/EXTRACTION_METHODOLOGY.md`
- **JSON Schema:** `/home/user/colonial_office_list/json_schema_template.json`
- **Extraction Script:** `/home/user/colonial_office_list/extract_knowledge_graph.py`

## Year-Specific Coverage

### 1957
25 colonies: Aden, Ascension, Barbados, Bermuda, British Guiana, British Honduras, Cayman Islands, Cyprus, Dominica, Fiji, Gibraltar, Hong Kong, Jamaica, Leeward Islands, Mauritius, Montserrat, North Borneo, Seychelles, St. Helena, St. Lucia, St. Vincent, The Gambia, Turks and Caicos Islands, Uganda, Zanzibar

### 1958
20 colonies: Aden, Ascension, Barbados, Basutoland, Bermuda, British Guiana, British Honduras, Cyprus, Fiji, Gibraltar, Hong Kong, Jamaica, Mauritius, North Borneo, Seychelles, Sierra Leone, St. Helena, The Gambia, Turks and Caicos Islands, Uganda

### 1959
30 colonies: Aden, Antigua, Bahamas, Bermuda, British Guiana, British Honduras, Cayman Islands, Cyprus, Dominica, Falkland Islands, Fiji, Gibraltar, Grenada, Hong Kong, Jamaica, Leeward Islands, Malta, Mauritius, Montserrat, Seychelles, Sierra Leone, Somaliland, St. Helena, St. Lucia, St. Vincent, The Gambia, Trinidad, Turks and Caicos Islands, Uganda, Windward Islands

### 1960
30 colonies: Antigua, Ascension, Bahamas, Barbados, Basutoland, Bermuda, British Guiana, British Honduras, Cyprus, Dominica, Fiji, Gambia, Gibraltar, Grenada, Hong Kong, Jamaica, Leeward Islands, Malta, Mauritius, Montserrat, North Borneo, Seychelles, Sierra Leone, St. Lucia, St. Vincent, The Gambia, Trinidad, Uganda, Windward Islands, Zanzibar

### 1961
28 colonies: Bermuda, British Guiana, British Honduras, British Solomon Islands, Brunei, Falkland Islands, Fiji, Gambia, Gibraltar, Gilbert and Ellice Islands, Hong Kong, Kenya, Malta, Mauritius, New Hebrides, Northern Rhodesia, North Borneo, Nyasaland, Sarawak, Seychelles, Sierra Leone, State of Singapore, St. Helena, Tanganyika, Tonga, Uganda, Virgin Islands, Zanzibar

### 1962
64 territories including civil service records, regional groupings, international organizations, and: Aden Colony, Bahamas, Basutoland, Bermuda, British Guiana, British Honduras, British Solomon Islands, Brunei, Falkland Islands, Gambia, Gibraltar, Gilbert and Ellice Islands, Hong Kong, Kenya, Malta, Mauritius, Northern Rhodesia, North Borneo, Nyasaland, Sarawak, Seychelles, Sierra Leone, State of Singapore, St. Helena, Tanganyika, Tonga, Uganda, Virgin Islands, Zanzibar

## Extraction Date

Extraction completed: November 16, 2025

## Version

Knowledge Graph Extract Format Version 1.0 (following json_schema_template.json)

---

For detailed information about the extraction process, entity counts, and methodology, see **EXTRACTION_SUMMARY_1957-1962.md**.
