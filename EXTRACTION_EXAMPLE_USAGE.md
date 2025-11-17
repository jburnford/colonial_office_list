# Example: Using the Entity Extraction Template

## Practical Guide for Extracting Entities from ANTIGUA 1905

This document shows how to use the `ENTITY_EXTRACTION_PROMPT_TEMPLATE.md` for a real extraction task.

---

## Step 1: Identify Source File and Variables

**Source File**: `/home/user/colonial_office_list/output_2/1905_manual_parsed/ANTIGUA.md`

**Variables to fill in:**
- `{{COLONY_NAME}}`: `ANTIGUA`
- `{{YEAR}}`: `1905`
- `{{FILE_PATH}}`: `/home/user/colonial_office_list/output_2/1905_manual_parsed/ANTIGUA.md`
- `{{COLONY_NAME_LOWER}}`: `antigua`
- `{{Human Readable Name}}`: `Antigua`
- `{{ISO_TIMESTAMP}}`: `2025-11-17T16:00:00Z`

---

## Step 2: Fill Template and Create Prompt

Replace all placeholders in the template to create the working prompt:

### Filled Prompt (excerpt):

```
# Knowledge Graph Entity Extraction: ANTIGUA (1905)

## Task Overview
Extract ALL structured entities from the Colonial Office List file for ANTIGUA in 1905, with COMPLETE provenance tracking including exact line numbers and context text.

## Source File
**Path**: /home/user/colonial_office_list/output_2/1905_manual_parsed/ANTIGUA.md
**Colony**: ANTIGUA
**Year**: 1905

## CRITICAL REQUIREMENTS

### Provenance Rules (NON-NEGOTIABLE)
1. **EVERY entity MUST include exact line number(s)** where it appears in source
2. **EVERY entity MUST include context_text** - the actual sentence(s) from the source
3. **EVERY entity MUST include colony field** set to "ANTIGUA"
4. **Entity IDs MUST follow format**: `{type}_antigua_1905_{sequential_number}`

...
[rest of template with all variables replaced]
```

---

## Step 3: Launch Task Agent

Use the Task tool to launch an extraction agent:

```python
Task(
  subagent_type="general-purpose",
  model="sonnet",  # Use sonnet for complex extraction
  description="Extract KG entities: ANTIGUA 1905",
  prompt="""[PASTE FILLED TEMPLATE HERE]"""
)
```

Or from command line / Claude Code:

```
I need you to extract entities from ANTIGUA 1905 using the template in ENTITY_EXTRACTION_PROMPT_TEMPLATE.md.

Fill in these variables:
- COLONY_NAME: ANTIGUA
- YEAR: 1905
- FILE_PATH: /home/user/colonial_office_list/output_2/1905_manual_parsed/ANTIGUA.md

Use a Task agent with subagent_type="general-purpose" and save the output to:
knowledge_graph_extracts_v4/1905/ANTIGUA_extracted.json
```

---

## Step 4: Expected Output Structure

The agent should return JSON like:

```json
{
  "metadata": {
    "colony": "ANTIGUA",
    "colony_normalized": "Antigua",
    "year": "1905",
    "source_file": "/home/user/colonial_office_list/output_2/1905_manual_parsed/ANTIGUA.md",
    "extraction_date": "2025-11-17T16:00:00Z",
    "total_lines_in_source": 240,
    "processing_notes": "Complete extraction from all sections including civil establishment, financial data, and demographic tables"
  },

  "entity_counts": {
    "places": 8,
    "people": 45,
    "institutions": 5,
    "economic_data": 67,
    "infrastructure": 3,
    "demographics": 4,
    "events": 2,
    "total": 134
  },

  "entities": {
    "places": [
      {
        "id": "place_antigua_1905_001",
        "entity_type": "place",
        "colony": "ANTIGUA",
        "colony_normalized": "Antigua",
        "year": "1905",
        "source_location": {
          "file": "/home/user/colonial_office_list/output_2/1905_manual_parsed/ANTIGUA.md",
          "line_start": 3,
          "line_end": 3
        },
        "context_text": "Antigua is situated in W. long. 61° 45', and N. lat. 17° 6'. It is about 54 miles in circumference, and its area is 108 square miles, about half the size of Middlesex.",
        "name": "Antigua",
        "modern_name": "Antigua",
        "type": "colony",
        "coordinates": {
          "latitude": "17° 6' N",
          "longitude": "61° 45' W"
        },
        "area": {
          "value": 108,
          "unit": "square miles"
        },
        "population": null,
        "description": "About 54 miles in circumference, about half the size of Middlesex",
        "parent_location": null,
        "provenance": {
          "extraction_date": "2025-11-17T16:00:00Z",
          "extraction_method": "llm_direct",
          "confidence": 0.98,
          "extraction_notes": "Main colony description with precise coordinates and area"
        }
      },
      {
        "id": "place_antigua_1905_002",
        "entity_type": "place",
        "colony": "ANTIGUA",
        "colony_normalized": "Antigua",
        "year": "1905",
        "source_location": {
          "file": "/home/user/colonial_office_list/output_2/1905_manual_parsed/ANTIGUA.md",
          "line_start": 5,
          "line_end": 5
        },
        "context_text": "Barbuda lies about 25 miles due north of the main island, with an area of 62 miles, is very flat, with a large lagoon on the west side, separated from the sea by a spit of sand.",
        "name": "Barbuda",
        "modern_name": "Barbuda",
        "type": "dependency",
        "coordinates": null,
        "area": {
          "value": 62,
          "unit": "square miles"
        },
        "population": 775,
        "description": "Very flat, with a large lagoon on the west side, separated from the sea by a spit of sand. Produces salt and phosphates, adapted for cattle grazing and horse rearing",
        "parent_location": "ANTIGUA",
        "provenance": {
          "extraction_date": "2025-11-17T16:00:00Z",
          "extraction_method": "llm_direct",
          "confidence": 0.98,
          "extraction_notes": "Dependency of Antigua, 25 miles north"
        }
      },
      {
        "id": "place_antigua_1905_003",
        "entity_type": "place",
        "colony": "ANTIGUA",
        "colony_normalized": "Antigua",
        "year": "1905",
        "source_location": {
          "file": "/home/user/colonial_office_list/output_2/1905_manual_parsed/ANTIGUA.md",
          "line_start": 5,
          "line_end": 5
        },
        "context_text": "Redonda, lying between Montserrat and Nevis, 25 miles S.W. of Antigua, in 25° 6' N. lat., 61° 35' W. long., 1 mile by ¼ mile, 1,000 feet high, is valuable for its phosphate of alumina mines",
        "name": "Redonda",
        "modern_name": "Redonda",
        "type": "dependency",
        "coordinates": {
          "latitude": "25° 6' N",
          "longitude": "61° 35' W"
        },
        "area": {
          "value": 0.25,
          "unit": "square miles"
        },
        "population": 120,
        "description": "1 mile by ¼ mile, 1,000 feet high, valuable for phosphate of alumina mines discovered in 1865, worked by Redonda Phosphate Company",
        "parent_location": "ANTIGUA",
        "provenance": {
          "extraction_date": "2025-11-17T16:00:00Z",
          "extraction_method": "llm_direct",
          "confidence": 0.98,
          "extraction_notes": "Small dependency with mining operations"
        }
      },
      {
        "id": "place_antigua_1905_004",
        "entity_type": "place",
        "colony": "ANTIGUA",
        "colony_normalized": "Antigua",
        "year": "1905",
        "source_location": {
          "file": "/home/user/colonial_office_list/output_2/1905_manual_parsed/ANTIGUA.md",
          "line_start": 15,
          "line_end": 15
        },
        "context_text": "St. John, the chief town, has a population of 9,262, and is a port of registry, having on 31st December, 1903, 45 sailing vessels registered, with a total tonnage of 669.",
        "name": "St. John",
        "modern_name": "Saint John's",
        "type": "town",
        "coordinates": null,
        "area": null,
        "population": 9262,
        "description": "The chief town, port of registry with 45 sailing vessels (669 tons total) as of Dec 31, 1903",
        "parent_location": "ANTIGUA",
        "provenance": {
          "extraction_date": "2025-11-17T16:00:00Z",
          "extraction_method": "llm_direct",
          "confidence": 0.95,
          "extraction_notes": "Chief town with specific population and shipping registry data"
        }
      }
    ],

    "people": [
      {
        "id": "person_antigua_1905_001",
        "entity_type": "person",
        "colony": "ANTIGUA",
        "colony_normalized": "Antigua",
        "year": "1905",
        "source_location": {
          "file": "/home/user/colonial_office_list/output_2/1905_manual_parsed/ANTIGUA.md",
          "line_start": 104,
          "line_end": 104
        },
        "context_text": "Colonial Secretary and Attorney-General, Hon. E. St. J. Branch.",
        "name": "E. St. J. Branch",
        "titles": ["Hon."],
        "honors": [],
        "positions": [
          {
            "title": "Colonial Secretary and Attorney-General",
            "department": "Colonial Administration",
            "location": "ANTIGUA",
            "salary": null,
            "allowances": [],
            "status": "permanent",
            "year": "1905"
          }
        ],
        "provenance": {
          "extraction_date": "2025-11-17T16:00:00Z",
          "extraction_method": "llm_direct",
          "confidence": 0.95,
          "extraction_notes": "Legislative Council official member"
        }
      },
      {
        "id": "person_antigua_1905_002",
        "entity_type": "person",
        "colony": "ANTIGUA",
        "colony_normalized": "Antigua",
        "year": "1905",
        "source_location": {
          "file": "/home/user/colonial_office_list/output_2/1905_manual_parsed/ANTIGUA.md",
          "line_start": 129,
          "line_end": 129
        },
        "context_text": "Treasurer and Collector of Customs, W. D. Auchinleck, 500l., and fees as Registrar of Shipping.",
        "name": "W. D. Auchinleck",
        "titles": ["Hon."],
        "honors": [],
        "positions": [
          {
            "title": "Treasurer and Collector of Customs",
            "department": "Customs and Treasury",
            "location": "ANTIGUA",
            "salary": {
              "amount": 500,
              "currency": "£",
              "period": "annual"
            },
            "allowances": [
              {
                "type": "fees",
                "amount": null,
                "currency": "£",
                "description": "fees as Registrar of Shipping"
              }
            ],
            "status": "permanent",
            "year": "1905"
          }
        ],
        "provenance": {
          "extraction_date": "2025-11-17T16:00:00Z",
          "extraction_method": "llm_direct",
          "confidence": 0.98,
          "extraction_notes": "Civil establishment entry with salary and fees"
        }
      }
    ],

    "economic_data": [
      {
        "id": "economic_antigua_1905_001",
        "entity_type": "economic_data",
        "colony": "ANTIGUA",
        "colony_normalized": "Antigua",
        "year": "1905",
        "source_location": {
          "file": "/home/user/colonial_office_list/output_2/1905_manual_parsed/ANTIGUA.md",
          "line_start": 21,
          "line_end": 21
        },
        "context_text": "| 1894 | 53,933  | 55,756      | 487,712         | 501,886       |",
        "data_type": "revenue",
        "category": "Total Revenue",
        "value": 53933,
        "unit": "£",
        "currency": "£",
        "time_period": "1894",
        "notes": "From Finances table",
        "provenance": {
          "extraction_date": "2025-11-17T16:00:00Z",
          "extraction_method": "llm_direct",
          "confidence": 1.0,
          "extraction_notes": "Table row extraction from Finances section"
        }
      }
    ]
  }
}
```

---

## Step 5: Validate Output

Check the output for:

1. **Line numbers present**: Every entity has `source_location.line_start`
2. **Context text present**: Every entity has `context_text` field
3. **Colony attribution**: Every entity has `colony: "ANTIGUA"`
4. **ID format**: All IDs like `place_antigua_1905_001`
5. **Historical fidelity**: Names and terms preserved as written
6. **No invention**: All data traceable to source
7. **Completeness**: All entities extracted (people, places, data, etc.)

---

## Step 6: Save and Document

Save the output:
```
mkdir -p knowledge_graph_extracts_v4/1905
# Save JSON output to:
knowledge_graph_extracts_v4/1905/ANTIGUA_extracted.json
```

Document in extraction log:
```markdown
## 1905 - ANTIGUA
- Extraction date: 2025-11-17
- Entities extracted: 134
  - Places: 8
  - People: 45
  - Institutions: 5
  - Economic data: 67
  - Infrastructure: 3
  - Demographics: 4
  - Events: 2
- Source file: output_2/1905_manual_parsed/ANTIGUA.md (240 lines)
- Notes: Complete extraction with full provenance. All entities traceable to source lines.
```

---

## Parallel Processing Multiple Colonies

To extract multiple colonies in parallel for a single year:

```
Launch the following Task agents in parallel to extract entities from all 1905 colonies:

1. ANTIGUA (use template with COLONY_NAME=ANTIGUA, YEAR=1905)
2. BAHAMAS (use template with COLONY_NAME=BAHAMAS, YEAR=1905)
3. BARBADOS (use template with COLONY_NAME=BARBADOS, YEAR=1905)
... (continue for all colonies in 1905)

Each agent should:
- Use subagent_type="general-purpose"
- Fill the ENTITY_EXTRACTION_PROMPT_TEMPLATE.md with colony-specific variables
- Save output to knowledge_graph_extracts_v4/1905/{COLONY}_extracted.json

Process all colonies simultaneously for efficiency.
```

---

## Step 7: Merge Year Data

After all colonies for 1905 are extracted, merge into single year file:

```json
{
  "metadata": {
    "year": "1905",
    "extraction_date": "2025-11-17T16:00:00Z",
    "colonies_processed": ["ANTIGUA", "BAHAMAS", "BARBADOS", ...],
    "total_entities": 2847,
    "source_directory": "output_2/1905_manual_parsed/"
  },
  "colonies": {
    "ANTIGUA": { /* contents of ANTIGUA_extracted.json */ },
    "BAHAMAS": { /* contents of BAHAMAS_extracted.json */ },
    ...
  }
}
```

---

## Key Improvements Over Previous Extraction

### Before (v3):
```json
{
  "id": "place_004",
  "name": "St. John",
  "type": "town",
  "provenance": {
    "source_lines": "1-240"  // Useless!
  }
}
```

### After (v4):
```json
{
  "id": "place_antigua_1905_004",
  "entity_type": "place",
  "colony": "ANTIGUA",
  "year": "1905",
  "source_location": {
    "file": "output_2/1905_manual_parsed/ANTIGUA.md",
    "line_start": 15,
    "line_end": 15
  },
  "context_text": "St. John, the chief town, has a population of 9,262, and is a port of registry...",
  "name": "St. John",
  "type": "town",
  "population": 9262,
  "parent_location": "ANTIGUA"
}
```

**Benefits:**
- ✅ Can trace to exact line (15)
- ✅ Context disambiguates which "St. John"
- ✅ Colony field makes it clear (Antigua's St. John)
- ✅ Verifiable without re-reading entire file
- ✅ LLM can use context for entity resolution

---

## Troubleshooting

### Issue: Agent not including line numbers
**Solution**: Emphasize in prompt: "CRITICAL: You MUST include line_start and line_end for EVERY entity"

### Issue: Context text too short
**Solution**: Specify "Include 1-3 complete sentences that provide full context"

### Issue: Missing colony field
**Solution**: Pre-fill colony in template, make it explicit: "colony": "{{COLONY_NAME}}"

### Issue: Table data not extracted
**Solution**: Add explicit instruction: "Extract EACH table row as separate entity"

### Issue: Historical terms modernized
**Solution**: Emphasize: "PRESERVE exact spelling and terminology from source"

---

## Summary

This new extraction approach ensures:
1. **Every entity is traceable** to exact source location
2. **Context enables disambiguation** (no more "which St. John?")
3. **Colony attribution is explicit** and unambiguous
4. **Verification is fast** - no need to re-read entire files
5. **Knowledge graph construction is precise** with clear provenance

The extraction is more verbose but **infinitely more useful** for building an accurate, verifiable knowledge graph.
