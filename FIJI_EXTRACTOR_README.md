# Fiji People Extractor

A specialized people extraction system for Fiji Colonial Office Lists, adapted from the Ceylon v2 extraction system to handle Fiji-specific challenges.

## File Location

`/home/user/colonial_office_list/extract_fiji_people.py`

## Key Features

### 1. Multi-Role Entry Detection

Fiji officials often held multiple concurrent positions. The extractor creates separate Person records for each role while linking them together.

**Example:**
```
Stipendiary Magistrate, Rewa, and Commissioner, Naitasiri, R. M. Booth, 400l.
```

**Extracts as:**
- R. M. Booth - Stipendiary Magistrate in Rewa (400l)
- R. M. Booth - Commissioner in Naitasiri (400l)

Both records share a `multi_role_id` to indicate they represent the same person.

### 2. Acting Official Detection

When a permanent official is on leave, the extractor captures both the permanent and acting officials.

**Example:**
```
Attorney-General, A. Elhrhardt (on leave, C. A. Brough acting), 700l.
```

**Extracts as:**
- A. Elhrhardt - Attorney-General (700l) - ON LEAVE
- C. A. Brough - Attorney-General (700l) - ACTING

Each record includes an `is_acting` flag and linked via `multi_role_id`.

### 3. Aggregate Statement Flagging

Statements about groups of officials without individual names are flagged for manual review.

**Examples:**
- "9 Roko Tuis, or Native Administrators of Provinces, with salaries varying from 50l.-340l."
- "There are also 180 Bulis, or Administrators of Districts, and a number of other native officers with small salaries."

These are **flagged but not extracted** as Person records, since we don't have individual names.

### 4. Fiji-Specific Context

The extractor recognizes:
- **17 Provinces:** Ba, Bua, Cakaudrove, Kadavu, Lau, Lomaiviti, Macuata, Nadroga, Naitasiri, Namosi, Ra, Rewa, Serua, Tailevu, Colo North, Colo East, Colo West, Rotuma
- **Native Titles:** Roko Tui, Roko Tuis, Buli, Bulis, Ratu
- **Departments:** Colonial Secretary, Medical Department, Native Department, Fiji Constabulary, etc.
- **Currency:** £ sterling (same as Ceylon)

## Usage

### Test Mode (1909)

```bash
python extract_fiji_people.py --test
```

Runs extraction on the 1909 Fiji file and outputs detailed statistics.

### Extract Specific Year

```bash
python extract_fiji_people.py --year 1909 --output fiji_1909.json
```

### Extract Year Range

```bash
python extract_fiji_people.py --year-range 1879-1920 --output fiji_1879_1920.json
```

### Extract All Available Years

```bash
python extract_fiji_people.py --all --output fiji_all_years.json
```

## Test Results (1909)

### Overall Statistics
- **Total people extracted:** 76
- **Average confidence:** 82.61%
- **Multi-role entries:** 3 (6 person records)
- **Acting officials:** 6 (3 positions with acting/permanent pairs)
- **Aggregate statements flagged:** 2

### Extraction Methods Breakdown
- `fiji_pattern1`: 38 records (standard Role, Name, Salary pattern)
- `task_pattern_extraction`: 26 records (LLM extraction for complex cases)
- `fiji_multi_role`: 6 records (multi-role officials)
- `fiji_acting_permanent`: 3 records (permanent officials on leave)
- `fiji_acting_official`: 3 records (acting officials)

## Data Model

Each Person record includes:

### Standard Fields
- `name`: Person's name
- `role`: Position/title
- `location`: Full location (Colony - Province - Department)
- `colony`: "FIJI"
- `year`: Year of the record
- `department`: Department name (if applicable)
- `province`: Province name (if applicable)
- `salary`: Salary amount
- `full_string`: Complete source text
- `source_file`: GitHub URL to source line
- `line_number`: Line number in source file
- `confidence`: Extraction confidence (0.0-1.0)
- `extraction_method`: Method used for extraction
- `notes`: Additional notes

### Fiji-Specific Fields
- `is_acting`: Boolean flag for acting officials
- `multi_role_id`: Identifier linking related records (multi-role or acting)

## Architecture

The system uses a hybrid approach combining:

1. **Pattern-based extraction (Python)**: Fast regex-based extraction for standard formats
2. **LLM-based extraction (Tasks)**: Intelligent extraction for complex cases via Claude Code Tasks
3. **Validation and deduplication**: Filters false positives and removes duplicates

### Processing Phases

1. **File Analysis**: Detect section boundaries, departments, provinces
2. **Pattern Extraction**: Apply Fiji-specific regex patterns
3. **LLM Extraction**: Process flagged sections requiring interpretation
4. **Validation**: Clean, filter, and deduplicate results

## Fiji vs Ceylon Differences

| Feature | Ceylon | Fiji |
|---------|--------|------|
| Multi-role entries | Rare | Common |
| Acting officials | Some | Frequent |
| Aggregate statements | Few | Multiple (Bulis, Roko Tuis) |
| Native administration | Limited | Extensive (180 Bulis, 9 Roko Tuis) |
| Provinces | ~10 | 17 |
| Currency | £ sterling | £ sterling |

## Example Outputs

### Multi-Role Official
```json
{
  "name": "R. M. Booth",
  "role": "Stipendiary Magistrate",
  "province": "Rewa",
  "salary": "400l",
  "multi_role_id": "multi_455",
  "notes": "Multi-role: Stipendiary Magistrate (Rewa) and Commissioner (Naitasiri)"
},
{
  "name": "R. M. Booth",
  "role": "Commissioner",
  "province": "Naitasiri",
  "salary": "400l",
  "multi_role_id": "multi_455",
  "notes": "Multi-role: Stipendiary Magistrate (Rewa) and Commissioner (Naitasiri)"
}
```

### Acting Official
```json
{
  "name": "A. Elhrhardt",
  "role": "Attorney-General",
  "salary": "700l",
  "is_acting": false,
  "multi_role_id": "acting_444",
  "notes": "On leave"
},
{
  "name": "C. A. Brough",
  "role": "Attorney-General",
  "salary": "700l",
  "is_acting": true,
  "multi_role_id": "acting_444",
  "notes": "Acting"
}
```

## Future Enhancements

1. **Aggregate statement expansion**: Research native administration records to populate the 180 Bulis and 9 Roko Tuis individually
2. **Cross-reference validation**: Link acting officials to verify they don't hold conflicting positions
3. **Salary analysis**: Track changes in salaries and allowances over time
4. **Province-level aggregation**: Generate statistics by province
5. **Native title recognition**: Enhanced parsing for Fijian titles and names

## Dependencies

- Python 3.x
- `extract_people_v2.py` - Base extraction architecture
- `llm_extractor_task.py` - LLM-based extraction via Claude Code Tasks

## Notes

- The extractor preserves all source information for verification
- Multi-role and acting entries are NOT deduplicated (they represent distinct role assignments)
- Aggregate statements are flagged but require manual research to populate individual records
- Confidence scores reflect the reliability of the extraction method used
