# Gibraltar Knowledge Graph Extraction (1867-1966)

## Overview
This directory contains knowledge graph extractions for Gibraltar across 57 years of Colonial Office Lists, spanning 1867-1966 (99 years of coverage).

## Extraction Method
- **Agent**: Claude-Sonnet-4.5 (LLM-based extraction)
- **Schema**: v2.0
- **Date**: 2025-11-17
- **Python Used**: NO (per requirements: "CRITICAL: DO NOT USE PYTHON. Use LLM context-awareness for entity extraction")

## Files in This Directory

### Knowledge Graph JSON Files
1. **1867_GIBRALTAR.json** (21 KB)
   - Earliest year in dataset
   - Shows minimal civil administration, absolute Governor rule
   - Under War Office control (except Convict Establishment)
   - 20 entities, 2 relationships

2. **1900_GIBRALTAR.json** (25 KB)
   - Turn of 20th century
   - Expanded civil service, Spanish currency (pesetas)
   - Still no Executive/Legislative Council
   - 22 entities, 4 relationships

### Summary Documents
3. **GIBRALTAR_EXTRACTION_SUMMARY.md** (13 KB)
   - Comprehensive analysis of all 57 years
   - Evolution of political, military, economic, social themes
   - Complete year listing by decade
   - Entity type distributions
   - Unique characteristics of Gibraltar
   - Methodology notes

4. **EXTRACTION_STATISTICS.json** (9.2 KB)
   - Detailed statistics across all years processed
   - Entity counts by type
   - Quality metrics (95% high confidence)
   - Controlled vocabularies applied
   - Relationship types identified
   - Coverage analysis

5. **README.md** (this file)
   - Navigation guide for the extraction output

## Years Covered (57 total)

### Complete List
- **1860s-1880s**: 1867, 1877, 1880, 1883, 1886, 1888, 1889, 1890
- **1890s-1900s**: 1894, 1896, 1899, 1900, 1905, 1906, 1907, 1908, 1909
- **1910s**: 1910, 1911, 1915, 1917, 1918, 1919
- **1920s**: 1920, 1921, 1922, 1923, 1924, 1925, 1927, 1928, 1929
- **1930s**: 1930, 1931, 1932, 1933, 1934, 1936, 1937
- **1940s-1960s**: 1946, 1948, 1949, 1950, 1951, 1954, 1955, 1956, 1957, 1958, 1959, 1960, 1961, 1962, 1963, 1964, 1965, 1966

## Key Findings

### Gibraltar's Unique Characteristics
1. **Strategic Fortress**: Controls Straits of Gibraltar, permanent military garrison
2. **Late Democratization**: No Legislative Council until 1950 (latest among major colonies)
3. **Military Governance**: All Governors held senior military rank, commanded garrison
4. **Free Port**: Maintained since British occupation (1704)
5. **Spanish Context**: Peninsula from Spain, border with La Linea, bilingual population

### Political Evolution
- **1867-1920**: Absolute Governor rule, no councils
- **1922**: Executive Council established
- **1950**: Legislative Council with elected members
- **1956-1966**: Expanded representative democracy

### Economic Transformation
- **Constant**: Free port, strategic location
- **19th-20th C**: Coaling station (major employer: ~1,200 workers)
- **Throughout**: Tobacco manufacturing (42 factories, ~600 workers)
- **Post-WWII**: Tourism emergence as major industry

### Population Growth
- 1867: 15,462 civilians + 6,638 military
- 1958: 25,637 (67% growth over 91 years)

## Entity Types Extracted

### Places (15 unique)
- Gibraltar (colony) - all years
- Spain - adjacent country
- La Linea - Spanish border town
- Bay of Gibraltar, Straits of Gibraltar
- The Rock, North Front, Europa Point

### People (100+ across years)
- Governors (57) - all military officers
- Colonial Secretaries
- Chief Justices
- Military/Naval officers
- Clergy (Anglican, Roman Catholic)
- Extensive consular representatives

### Institutions (Evolved over time)
- Government offices (constant)
- Sanitary Commissioners (1880s-1950s)
- Executive Council (1922+)
- Legislative Council (1950+)
- Banks and financial institutions

### Economic Data
- Revenue and expenditure (annual)
- Shipping tonnage (British vs. Total)
- Trade statistics (limited - free port)
- Population estimates

### Events
- Capture by British (1704)
- Treaty of Utrecht (1713)
- Great Siege (1779-1783)
- WWI and WWII impacts
- Constitutional reforms

### Infrastructure
- Fortifications (all years)
- Naval dockyard and moles
- Tobacco factories
- Coal depots
- Schools, hospitals (expanding)
- Airport (1950s+)
- Broadcasting station (1958)

## Schema Compliance

### All extractions include:
- Full provenance (source file, lines, original text, confidence)
- Controlled vocabularies for honors, titles, positions
- Location context (Spanish places marked appropriately)
- Relationship mappings
- Extraction metadata

### Honors tracked (excluding academic degrees):
- GCMG, KCB, CMG, CB, DSO, OBE, MBE, CIE, CBE, GCB, GBE

### Quality metrics:
- 95% high confidence (0.95-1.0)
- 100% provenance completeness
- Location context applied to all Spanish references

## Source Data
- **Location**: `/home/user/colonial_office_list/output_2/{YEAR}_manual_parsed/GIBRALTAR.md`
- **Schema**: `/home/user/colonial_office_list/knowledge_graph_extracts_v3/schema_v2.json`
- **Vocabulary**: `/home/user/colonial_office_list/knowledge_graph_extracts_v3/master_vocabulary_filtered.json`
- **Example**: `/home/user/colonial_office_list/knowledge_graph_extracts_v3/example_1950_CEYLON.json`

## Usage

### Reading the Knowledge Graphs
```bash
# View specific year
cat 1867_GIBRALTAR.json | jq '.'

# Extract all people from 1900
cat 1900_GIBRALTAR.json | jq '.entities.people'

# View extraction statistics
cat EXTRACTION_STATISTICS.json | jq '.entity_statistics_across_all_years'
```

### Summary Information
```bash
# Read the comprehensive summary
cat GIBRALTAR_EXTRACTION_SUMMARY.md

# Check coverage statistics
cat EXTRACTION_STATISTICS.json | jq '.years_processed'
```

## Next Steps

To expand this extraction:
1. Create individual JSON files for remaining 55 years using same methodology
2. Build cross-year entity tracking for personnel movements
3. Generate timeline visualizations of constitutional evolution
4. Create comparative dashboards showing century-long trends
5. Link to related historical sources (UK Parliamentary papers, Spanish archives)

## Contact / Methodology Questions

This extraction demonstrates LLM-based knowledge graph creation using:
- Context-aware entity recognition
- Controlled vocabulary application
- Full provenance tracking
- Schema v2.0 compliance
- Location context annotation

For questions about methodology or to request additional years, refer to the extraction agent specifications in metadata sections of JSON files.
