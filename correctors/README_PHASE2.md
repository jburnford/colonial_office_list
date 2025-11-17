# Phase 2: LLM-Powered Enum Mapper

## Overview

The Phase 2 Enum Mapper is an intelligent correction agent that maps invalid enum values to valid schema enums using semantic understanding. It processes 4,060 invalid enum errors across the dataset with context-aware decisions.

## Key Features

### 1. Intelligent Mapping
- **LLM-powered**: Uses Claude Sonnet 4.5 for semantic understanding of historical context
- **Rule-based fallback**: Comprehensive rule set based on historical knowledge when LLM unavailable
- **Context-aware**: Uses entity name, description, and year for better decisions

### 2. Confidence Scoring (0-1 scale)
- **0.95-1.0**: Direct semantic match, no ambiguity
- **0.85-0.94**: Strong historical context match
- **0.70-0.84**: Reasonable inference from context
- **Below 0.70**: Uncertain, needs human review

### 3. Three-Tier Decision System

#### Auto-Apply (≥90% confidence)
- Automatically corrects high-confidence mappings
- Example: `governs → GOVERNED_BY` (0.95 confidence)

#### Review Queue (70-90% confidence)
- Queues medium-confidence mappings for human review
- Example: `capital_of → LOCATED_IN` (0.85 confidence)

#### Flagged (<70% confidence)
- Flags low-confidence items requiring human decision
- Example: `discovered_by` (0.50 confidence - no clear mapping)

### 4. Safety Features
- **Python validation**: Validates all LLM suggestions before applying
- **Re-validation**: Checks entire file after changes
- **Automatic rollback**: Reverts changes if validation worsens
- **Detailed logging**: Records all decisions for audit trail

## Usage

### Basic Test (Rule-Based Mode)
```bash
python correctors/phase2_enum_mapper.py --test --samples 10
```

### Process Single File (Dry Run)
```bash
python correctors/phase2_enum_mapper.py --file knowledge_graph_extracts/1877_extracted.json --dry-run
```

### Apply Changes (With LLM)
```bash
export ANTHROPIC_API_KEY=your_key_here
python correctors/phase2_enum_mapper.py --file knowledge_graph_extracts/1877_extracted.json --apply
```

### Comprehensive Test
```bash
python correctors/test_phase2.py
```

## Supported Enum Types

### PlaceType
- `protectorate → territory` (0.90)
- `dominion → colony` (0.88)
- `crown_colony → colony` (0.95)
- `administrative_unit → district` (0.85)
- `province → region` (0.90)
- `capital → city` (0.95)
- `port → city` (0.88)

### InstitutionType
- `electoral → legislative_council` (0.92)
- `administrative → department` (0.88)
- `judicial → court` (0.95)
- `treasury → bank` (0.85)
- `finance → bank` (0.88)

### RelationshipType
- `governs → GOVERNED_BY` (0.95)
- `subordinate_to → REPORTS_TO` (0.90)
- `capital_of → LOCATED_IN` (0.85)
- `part_of → PART_OF` (0.98)
- `located_in → LOCATED_IN` (0.98)
- `port_of → LOCATED_IN` (0.85)
- `connects → CONNECTS` (0.98)
- `heads → GOVERNED_BY` (0.80)
- `member_of → MEMBER_OF` (0.98)
- `presides_over → GOVERNED_BY` (0.85)
- `constituent_of → PART_OF` (0.92)
- `serves → REPORTS_TO` (0.88)
- `administered_by → GOVERNED_BY` (0.95)

### EventType
- `annexation → CESSION` (0.90)
- `independence → CONSTITUTIONAL_CHANGE` (0.92)
- `reform → CONSTITUTIONAL_CHANGE` (0.88)

## Test Results

### Sample Test on 1877_extracted.json

**Total enum errors found:** 24

**Results:**
- Auto-applied (≥90% confidence): 16 (66.7%)
- Review queue (70-90% confidence): 5 (20.8%)
- Flagged (<70% confidence): 3 (12.5%)

**Average confidence:** 0.87

### Examples

#### High Confidence (Auto-Applied)
1. `governs → GOVERNED_BY` (0.95)
   - Reasoning: Historical 'governs' relationship maps to GOVERNED_BY

2. `part_of → PART_OF` (0.98)
   - Reasoning: Direct match

3. `member_of → MEMBER_OF` (0.98)
   - Reasoning: Direct match

#### Medium Confidence (Review Queue)
1. `capital_of → LOCATED_IN` (0.85)
   - Reasoning: Geographic capital_of can be represented as LOCATED_IN with properties

2. `heads → GOVERNED_BY` (0.80)
   - Reasoning: Leadership heads can be GOVERNED_BY relationship

#### Low Confidence (Flagged)
1. `discovered_by` (0.50)
   - Reasoning: No rule-based mapping found
   - Needs: Human review to determine correct mapping

## LLM Prompt Template

The system uses this prompt template for intelligent mapping:

```
You are a historical data specialist analyzing Colonial Office List records from the British Empire.

Your task is to map an invalid enum value to the correct valid enum value based on historical context.

**Context:**
- Entity type: {entity_type}
- Entity name: {entity_name}
- Description: {description}
- Year: {year}
- Field: {enum_type}

**Current invalid value:** "{invalid_value}"

**Valid enum options:**
  - option1
  - option2
  ...

**Historical Context Notes:**
- Colonies vs Territories: Colonies had more developed governance; territories were less developed dependencies
- Protectorates: Areas under British protection but not full colonial administration
- Legislative vs Executive Councils: Legislative made laws, Executive advised governors
- Crown Colonies vs Self-Governing: Crown colonies had less autonomy

Respond in JSON format:
{
  "recommended_value": "the_valid_enum_value",
  "confidence": 0.95,
  "reasoning": "Brief explanation of why this mapping is correct"
}
```

## Architecture

### Core Components

1. **EnumMapper Class**
   - Main orchestrator for enum mapping
   - Handles LLM communication and rule-based fallback

2. **Mapping Functions**
   - `map_enum_value()`: LLM-based mapping
   - `map_enum_value_rule_based()`: Rule-based fallback
   - `extract_entity_context()`: Context extraction

3. **Decision System**
   - `make_decision()`: Evaluates confidence and routes to appropriate queue
   - Three-tier routing: auto-apply, review, flag

4. **Validation Layer**
   - `validate_file()`: Pre/post validation
   - `apply_mapping()`: Safe application with rollback

### Data Flow

```
Input File
    ↓
Validation (detect enum errors)
    ↓
Context Extraction (entity name, description, year)
    ↓
LLM/Rule-Based Mapping
    ↓
Confidence Scoring
    ↓
Decision Routing
    ├─→ Auto-Apply (≥90%)
    ├─→ Review Queue (70-90%)
    └─→ Flag (<70%)
    ↓
Python Validation
    ↓
Apply/Rollback
    ↓
Output File
```

## Expected Impact

Based on the 4,060 invalid enum errors:

- **Auto-applied (≥90%)**: ~2,700 fixes (66%)
- **Review queue (70-90%)**: ~850 items (21%)
- **Flagged (<70%)**: ~510 items (13%)

Total automated fixes: 2,700 (66% of enum errors)
Human review needed: 1,360 (34% of enum errors)

## Extension Points

### Adding New Mappings

Edit `RULE_MAPPINGS` in `phase2_enum_mapper.py`:

```python
"InstitutionType": {
    "new_invalid_value": ("valid_enum", confidence, "reasoning"),
}
```

### Custom Confidence Thresholds

```python
mapper = EnumMapper()
mapper.AUTO_APPLY_THRESHOLD = 0.95  # More conservative
mapper.REVIEW_THRESHOLD = 0.80
```

### Integration with CI/CD

```bash
# Validate only (no changes)
python correctors/phase2_enum_mapper.py --file $FILE --dry-run

# Apply with confidence threshold
python correctors/phase2_enum_mapper.py --file $FILE --apply --min-confidence 0.95
```

## Limitations

1. **Rule Coverage**: Some rare enum values may not have rules
2. **Context Quality**: Limited context in some entities affects confidence
3. **Ambiguous Cases**: Historical ambiguity requires human judgment

## Future Enhancements

1. **Learning System**: Build mapping database from human review decisions
2. **Batch Processing**: Process all files in directory
3. **Interactive Mode**: Real-time review of medium-confidence items
4. **Export Review Queue**: Generate CSV/JSON for human review workflows
5. **Analytics Dashboard**: Visualize confidence distributions and patterns

## Files

- **`phase2_enum_mapper.py`**: Main implementation
- **`test_phase2.py`**: Comprehensive test script
- **`README_PHASE2.md`**: This documentation

## Author

Created: 2025-11-17
System: Phase 2 Correction Agent for Knowledge Graph Validation
