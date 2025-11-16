# Colonial Office List Knowledge Graph Extraction Methodology

## Overview
This document describes the comprehensive methodology for extracting structured information from the Colonial Office Lists (1867-present) to build a knowledge graph of the British Empire.

## Data Source
- **Location**: `output_2/` directory
- **Format**: Yearly directories containing colony-specific files (`.txt` or `.md`)
- **Coverage**: 61 years of colonial administrative records
- **Structure**: Each year contains parsed data for individual colonies/territories

## Extraction Approach

### 1. Processing Strategy
- **Year-by-Year Processing**: Each year is processed independently using dedicated LLM agents
- **Quality Over Speed**: Comprehensive extraction with high accuracy is prioritized
- **No Synthesis**: Extract only information explicitly present in the source documents
- **Historical Fidelity**: Preserve original spelling and terminology; note modern equivalents separately

### 2. Entity Types for Knowledge Graph

#### A. Geographic Entities
**Primary Focus: Toponyms (Place Names)**
- Colony/Territory names (official and colloquial)
- Cities, towns, settlements
- Regions, districts, parishes
- Geographic features (rivers, mountains, harbors, bays)
- Dependencies and associated territories
- Coordinates (latitude/longitude when available)
- Modern name equivalents (as separate annotation, not replacement)
- Distance relationships between locations

**Attributes to Extract**:
- Historical names (preserve exact spelling)
- Modern equivalents (if identifiable without speculation)
- Coordinates (exact format from source)
- Area measurements
- Physical descriptions
- Administrative relationships

#### B. People (Prosopography)
**Individual Persons with Roles in Colonial Administration**
- Full names (with titles, honors, military ranks)
- Official positions/roles
- Salary information
- Location of posting
- Allowances and benefits
- Dates of service/appointment
- Military ranks and decorations
- Acting vs. permanent appointments
- Multiple simultaneous positions

**Attributes to Extract**:
- Name (exact as written, including initials)
- Titles (Sir, Rev., Dr., Major-General, etc.)
- Honors (K.C.M.G., C.B., etc.)
- Position title
- Department/office
- Salary (with currency)
- Allowances (quarters, horse, table money, etc.)
- Location (colony, city)
- Year of record
- Special notes (acting, temporary, vacant positions)

#### C. Institutions
**Governmental and Administrative Bodies**
- Executive Councils
- Legislative Councils
- Courts (Supreme Court, Vice-Admiralty, Police Courts, etc.)
- Departments (Colonial Secretary, Treasury, Survey, etc.)
- Military units and garrisons
- Police forces
- Educational institutions
- Medical services
- Religious establishments
- Banks and financial institutions
- Postal services
- Public works departments

**Attributes to Extract**:
- Official name
- Type/category
- Composition (number and types of members)
- Location
- Function/jurisdiction
- Establishment date (if mentioned)
- Budget/funding (if mentioned)

#### D. Economic & Trade Information
**Commercial and Financial Data**
- Revenue (by year, by source)
- Expenditure (by year, by category)
- Trade volumes (imports/exports)
- Shipping statistics (vessels, tonnage)
- Currency information
- Exchange rates
- Major commodities (exports/imports)
- Industries and production
- Infrastructure (docks, railways, telegraphs)
- Banking and financial systems
- Land use and agriculture

**Attributes to Extract**:
- Numerical values (preserve exact figures and units)
- Currency denominations
- Time periods
- Categories/classifications
- Comparative data (year-over-year)
- Sources (parliamentary grants, local revenue, etc.)

#### E. Infrastructure
**Communication and Transportation**
- Railways (routes, distances, costs, revenue)
- Telegraph lines (stations, mileage)
- Postal routes
- Shipping routes and schedules
- Roads and bridges
- Docks and harbors
- Public buildings

**Attributes to Extract**:
- Type of infrastructure
- Location/route
- Dimensions/capacity
- Construction dates and costs
- Operational data (revenue, usage)
- Connections to other locations

#### F. Demographic Information
**Population Data**
- Total population
- Breakdowns by ethnicity/origin
- Gender distributions
- Urban vs. rural
- Occupational categories

**Attributes to Extract**:
- Population counts
- Categories used (preserve historical terminology)
- Year/date of census
- Location

#### G. Historical Events & Dates
**Significant Events Mentioned**
- Establishment dates
- Treaties and cessions
- Constitutional changes
- Major incidents (rebellions, disasters)
- Transfers of power

**Attributes to Extract**:
- Date (exact format from source)
- Event description
- Locations involved
- People involved
- Legal/administrative outcomes

### 3. Relationship Types

#### Geographic Relationships
- `PART_OF`: Territory A is part of Territory B
- `DEPENDENCY_OF`: Territory A is a dependency of Territory B
- `DISTANCE_FROM`: Distance between two locations
- `BORDERS`: Adjacent territories
- `LOCATED_IN`: City located in colony/region

#### Administrative Relationships
- `GOVERNED_BY`: Person holds position in location
- `MEMBER_OF`: Person is member of institution
- `REPORTS_TO`: Hierarchical reporting structure
- `ADMINISTERS`: Institution governs location

#### Economic Relationships
- `TRADES_WITH`: Trading relationships between locations
- `EXPORTS`: Location exports commodity
- `IMPORTS`: Location imports commodity
- `CONNECTS`: Transportation route connects locations

#### Temporal Relationships
- `PRECEDED_BY`: Sequential office holders
- `SUCCEEDED_BY`: Sequential office holders
- `DURING_YEAR`: Event/fact tied to specific year

### 4. JSON Output Schema

Each year's extraction will produce a JSON file with the following structure:

```json
{
  "metadata": {
    "year": "YYYY",
    "source_directory": "path/to/source",
    "extraction_date": "ISO-8601 timestamp",
    "processing_notes": "Any caveats or special notes"
  },
  "entities": {
    "places": [
      {
        "id": "unique_id",
        "name": "Historical Name (exact spelling)",
        "modern_name": "Modern equivalent (if identifiable)",
        "type": "colony|territory|city|town|region|feature",
        "coordinates": {
          "latitude": "as written in source",
          "longitude": "as written in source"
        },
        "area": {
          "value": number,
          "unit": "square miles|acres|etc"
        },
        "description": "Textual description from source",
        "year": "YYYY"
      }
    ],
    "people": [
      {
        "id": "unique_id",
        "name": "Full Name (as written)",
        "titles": ["Sir", "Dr.", etc],
        "honors": ["K.C.M.G.", "C.B.", etc],
        "positions": [
          {
            "title": "Position Title",
            "department": "Department Name",
            "location": "Colony/City",
            "salary": {
              "amount": number,
              "currency": "$|£|etc",
              "period": "annual|etc"
            },
            "allowances": [
              {
                "type": "quarters|table money|horse|etc",
                "amount": number,
                "currency": "$|£|etc"
              }
            ],
            "status": "permanent|acting|temporary",
            "year": "YYYY"
          }
        ]
      }
    ],
    "institutions": [
      {
        "id": "unique_id",
        "name": "Official Name",
        "type": "council|court|department|military|etc",
        "location": "Colony/City",
        "composition": {
          "description": "Text description",
          "members": ["person_id references"]
        },
        "function": "Description of role",
        "year": "YYYY"
      }
    ],
    "economic_data": [
      {
        "id": "unique_id",
        "type": "revenue|expenditure|trade|shipping|etc",
        "location": "Colony",
        "year": "YYYY",
        "data": {
          "category": "specific category",
          "value": number,
          "currency": "$|£|etc",
          "unit": "if applicable"
        },
        "notes": "Any contextual information"
      }
    ],
    "infrastructure": [
      {
        "id": "unique_id",
        "type": "railway|telegraph|postal|dock|etc",
        "name": "Name/Description",
        "location": "Colony/City",
        "specifications": {
          "length": {"value": number, "unit": "miles|etc"},
          "stations": number,
          "cost": {"value": number, "currency": "$|£|etc"},
          "revenue": {"value": number, "currency": "$|£|etc", "year": "YYYY"},
          "expenses": {"value": number, "currency": "$|£|etc", "year": "YYYY"}
        },
        "connections": ["location_id references"],
        "year": "YYYY"
      }
    ],
    "demographics": [
      {
        "id": "unique_id",
        "location": "Colony/City",
        "year": "YYYY",
        "total_population": number,
        "breakdowns": [
          {
            "category": "category as written in source",
            "count": number,
            "subcategories": {}
          }
        ]
      }
    ],
    "events": [
      {
        "id": "unique_id",
        "date": "as written in source",
        "type": "treaty|establishment|rebellion|etc",
        "description": "Event description",
        "locations": ["location_id references"],
        "people": ["person_id references"],
        "year_mentioned": "YYYY"
      }
    ]
  },
  "relationships": [
    {
      "source_id": "entity_id",
      "relationship_type": "type from list above",
      "target_id": "entity_id",
      "properties": {
        "year": "YYYY",
        "additional_context": "any relevant details"
      }
    }
  ]
}
```

### 5. Extraction Guidelines

#### Data Fidelity Rules
1. **Never Invent Data**: If information is not explicitly stated, do not include it
2. **Preserve Historical Spelling**: Extract toponyms and names exactly as written
3. **Note Modern Equivalents Separately**: Add modern names as `modern_name` field, not as replacement
4. **Maintain Ambiguity**: If source is unclear, note this rather than guessing
5. **Extract Complete Context**: For people, include ALL positions, salaries, and allowances mentioned
6. **Preserve Numerical Precision**: Extract exact figures, units, and currency symbols

#### Special Cases
- **Vacant Positions**: Record position with status "vacant"
- **Acting Appointments**: Mark with status "acting"
- **Multiple Positions**: One person may hold multiple simultaneous positions
- **Historical Terminology**: Preserve terms like "coolies", "natives", etc. as written (historical record)
- **Currency Variations**: Note exact currency symbols ($, £, etc.) and denominations
- **Incomplete Data**: Tables or lists with missing data should note gaps

### 6. Quality Assurance

Each extraction should:
1. Cross-reference person names across departments (same person may appear multiple times)
2. Validate that all geographic references are captured
3. Ensure numerical data includes units and currency
4. Maintain entity ID consistency within the year
5. Document any unusual patterns or unclear passages

### 7. Processing Workflow

For each year:
1. **Inventory**: List all colony files in the year directory
2. **Sequential Processing**: Process each colony file thoroughly
3. **Entity Extraction**: Extract all entities per schema
4. **Relationship Mapping**: Identify relationships between entities
5. **Consolidation**: Merge data from all colonies in the year
6. **Quality Check**: Verify completeness and accuracy
7. **JSON Output**: Generate structured JSON file

### 8. Output Organization

```
knowledge_graph_extracts/
  ├── 1867_extracted.json
  ├── 1877_extracted.json
  ├── 1880_extracted.json
  ├── ...
  └── extraction_log.md
```

### 9. Extraction Log

Each year's processing should be logged with:
- Colonies/territories processed
- Entity counts by type
- Notable patterns or anomalies
- Processing time
- Any issues or uncertainties

## Notes on Historical Context

- Terminology reflects Victorian-era imperial perspectives
- Administrative structures evolved significantly over time
- Currency and measurements vary by colony and period
- Some data may reflect incomplete records or estimates
- Population categories reflect historical (often problematic) classification systems

## Tools and Methods

- **LLM Agents**: Specialized Task agents process each year independently
- **Parallel Processing**: Multiple years can be processed simultaneously
- **No Python**: Pure LLM-based extraction and JSON generation
- **Human Review**: Critical for quality assurance of complex extractions
