#!/usr/bin/env python3
"""
Phase 2: LLM-Powered Enum Value Mapper

This intelligent agent uses semantic understanding to map invalid enum values
to valid schema enums based on historical context.

Author: Claude
Date: 2025-11-17
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime
import anthropic
import os

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from schemas.kg_schema import (
    PlaceType, InstitutionType, PositionStatus,
    EconomicDataType, InfrastructureType, EventType, RelationshipType,
    KnowledgeGraphExtract
)
from pydantic import ValidationError


@dataclass
class EnumMapping:
    """Result of an enum mapping operation"""
    original_value: str
    recommended_value: str
    confidence: float
    reasoning: str
    entity_type: str
    entity_name: Optional[str] = None
    entity_description: Optional[str] = None
    year: Optional[str] = None
    field_path: str = ""


@dataclass
class MappingDecision:
    """Decision about whether to apply a mapping"""
    should_apply: bool
    action: str  # "auto_apply", "review", "flag"
    mapping: EnumMapping


class EnumMapper:
    """LLM-powered semantic enum mapper"""

    # Valid enum values by type
    VALID_ENUMS = {
        "PlaceType": [e.value for e in PlaceType],
        "InstitutionType": [e.value for e in InstitutionType],
        "PositionStatus": [e.value for e in PositionStatus],
        "EconomicDataType": [e.value for e in EconomicDataType],
        "InfrastructureType": [e.value for e in InfrastructureType],
        "EventType": [e.value for e in EventType],
        "RelationshipType": [e.value for e in RelationshipType],
    }

    # Confidence thresholds
    AUTO_APPLY_THRESHOLD = 0.9
    REVIEW_THRESHOLD = 0.7

    def __init__(self, api_key: Optional[str] = None, use_llm: bool = True):
        """Initialize with Anthropic API key"""
        self.use_llm = use_llm
        self.api_key = api_key or os.environ.get("ANTHROPIC_API_KEY")

        if self.use_llm and not self.api_key:
            print("⚠ ANTHROPIC_API_KEY not set, falling back to rule-based mapping")
            self.use_llm = False

        if self.use_llm:
            self.client = anthropic.Anthropic(api_key=self.api_key)
        else:
            self.client = None

        self.mapping_log: List[MappingDecision] = []

    def get_enum_type_for_field(self, field_path: str) -> Optional[str]:
        """Determine enum type from field path"""
        if "places" in field_path and field_path.endswith("type"):
            return "PlaceType"
        elif "institutions" in field_path and field_path.endswith("type"):
            return "InstitutionType"
        elif "positions" in field_path and "status" in field_path:
            return "PositionStatus"
        elif "economic_data" in field_path and field_path.endswith("type"):
            return "EconomicDataType"
        elif "infrastructure" in field_path and field_path.endswith("type"):
            return "InfrastructureType"
        elif "events" in field_path and field_path.endswith("type"):
            return "EventType"
        elif "relationship_type" in field_path:
            return "RelationshipType"
        return None

    def extract_entity_context(self, data: Dict, error_loc: List) -> Dict[str, Any]:
        """Extract entity context from error location"""
        context = {
            "entity_type": None,
            "entity_name": None,
            "entity_description": None,
            "year": None,
            "field_path": " -> ".join(str(x) for x in error_loc)
        }

        # Determine entity type
        for i, loc in enumerate(error_loc):
            if loc == "entities" and i+1 < len(error_loc):
                context["entity_type"] = error_loc[i+1]
                break

        # Navigate to the entity (not the field)
        entity_data = data
        for i, loc in enumerate(error_loc[:-1]):  # Exclude the field itself
            if isinstance(entity_data, dict):
                entity_data = entity_data.get(loc, {})
            elif isinstance(entity_data, list) and isinstance(loc, int):
                if loc < len(entity_data):
                    entity_data = entity_data[loc]
                else:
                    break

        # Extract entity information
        if isinstance(entity_data, dict):
            context["entity_name"] = entity_data.get("name")
            context["entity_description"] = (
                entity_data.get("description") or
                entity_data.get("function") or
                entity_data.get("title")
            )
            context["year"] = entity_data.get("year") or entity_data.get("year_mentioned")

        # Get year from metadata if not found
        if not context["year"]:
            context["year"] = data.get("metadata", {}).get("year")

        return context

    def create_mapping_prompt(self,
                            invalid_value: str,
                            enum_type: str,
                            context: Dict[str, Any]) -> str:
        """Create LLM prompt for enum mapping"""

        valid_values = self.VALID_ENUMS.get(enum_type, [])

        prompt = f"""You are a historical data specialist analyzing Colonial Office List records from the British Empire.

Your task is to map an invalid enum value to the correct valid enum value based on historical context.

**Context:**
- Entity type: {context.get('entity_type', 'unknown')}
- Entity name: {context.get('entity_name', 'N/A')}
- Description: {context.get('entity_description', 'N/A')}
- Year: {context.get('year', 'N/A')}
- Field: {enum_type}

**Current invalid value:** "{invalid_value}"

**Valid enum options:**
{chr(10).join(f"  - {v}" for v in valid_values)}

**Historical Context Notes:**
- Colonies vs Territories: Colonies had more developed governance; territories were less developed dependencies
- Protectorates: Areas under British protection but not full colonial administration
- Legislative vs Executive Councils: Legislative made laws, Executive advised governors
- Crown Colonies vs Self-Governing: Crown colonies had less autonomy

Analyze the historical context and recommend the most appropriate enum value.

Respond in JSON format:
{{
  "recommended_value": "the_valid_enum_value",
  "confidence": 0.95,
  "reasoning": "Brief explanation of why this mapping is correct"
}}

Confidence scoring guide:
- 0.95-1.0: Direct semantic match, no ambiguity
- 0.85-0.94: Strong historical context match
- 0.70-0.84: Reasonable inference from context
- Below 0.70: Uncertain, needs human review"""

        return prompt

    def map_enum_value_rule_based(self,
                                  invalid_value: str,
                                  enum_type: str,
                                  context: Dict[str, Any]) -> EnumMapping:
        """Rule-based fallback for enum mapping"""

        # Common mappings based on historical knowledge
        RULE_MAPPINGS = {
            "RelationshipType": {
                "governs": ("GOVERNED_BY", 0.95, "Historical: 'governs' relationship maps to GOVERNED_BY"),
                "subordinate_to": ("REPORTS_TO", 0.90, "Organizational hierarchy: subordinate_to → REPORTS_TO"),
                "capital_of": ("LOCATED_IN", 0.85, "Geographic: capital_of can be represented as LOCATED_IN with properties"),
                "part_of": ("PART_OF", 0.98, "Direct match: part_of → PART_OF"),
                "located_in": ("LOCATED_IN", 0.98, "Direct match: located_in → LOCATED_IN"),
                "port_of": ("LOCATED_IN", 0.85, "Geographic: port_of can be LOCATED_IN"),
                "connects": ("CONNECTS", 0.98, "Direct match: connects → CONNECTS"),
                "heads": ("GOVERNED_BY", 0.80, "Leadership: heads can be GOVERNED_BY relationship"),
                "member_of": ("MEMBER_OF", 0.98, "Direct match: member_of → MEMBER_OF"),
                "presides_over": ("GOVERNED_BY", 0.85, "Leadership: presides_over maps to GOVERNED_BY"),
                "constituent_of": ("PART_OF", 0.92, "Structural: constituent_of maps to PART_OF"),
                "serves": ("REPORTS_TO", 0.88, "Organizational: serves maps to REPORTS_TO"),
                "administered_by": ("GOVERNED_BY", 0.95, "Colonial: administered_by maps to GOVERNED_BY"),
            },
            "InstitutionType": {
                "electoral": ("legislative_council", 0.92, "Electoral bodies typically map to legislative_council"),
                "administrative": ("department", 0.88, "Administrative units are typically departments"),
                "judicial": ("court", 0.95, "Judicial institutions are courts"),
                "treasury": ("bank", 0.85, "Treasury functions map to bank institution type"),
                "finance": ("bank", 0.88, "Finance institutions map to bank type"),
            },
            "PlaceType": {
                "protectorate": ("territory", 0.90, "Protectorates are classified as territories"),
                "dominion": ("colony", 0.88, "Dominions are self-governing colonies"),
                "crown_colony": ("colony", 0.95, "Crown colonies are colonies"),
                "administrative_unit": ("district", 0.85, "Administrative units are typically districts"),
                "province": ("region", 0.90, "Provinces are regions"),
                "capital": ("city", 0.95, "Capitals are cities"),
                "port": ("city", 0.88, "Ports are typically cities or towns"),
            },
            "EventType": {
                "annexation": ("CESSION", 0.90, "Annexation is a form of cession"),
                "independence": ("CONSTITUTIONAL_CHANGE", 0.92, "Independence is a constitutional change"),
                "reform": ("CONSTITUTIONAL_CHANGE", 0.88, "Reform typically involves constitutional change"),
            }
        }

        # Check if we have a rule for this mapping
        type_mappings = RULE_MAPPINGS.get(enum_type, {})
        if invalid_value.lower() in type_mappings:
            recommended, confidence, reasoning = type_mappings[invalid_value.lower()]
            return EnumMapping(
                original_value=invalid_value,
                recommended_value=recommended,
                confidence=confidence,
                reasoning=reasoning,
                entity_type=context.get("entity_type", "unknown"),
                entity_name=context.get("entity_name"),
                entity_description=context.get("entity_description"),
                year=context.get("year"),
                field_path=context.get("field_path", "")
            )

        # No rule found, return low confidence
        return EnumMapping(
            original_value=invalid_value,
            recommended_value=invalid_value,
            confidence=0.5,
            reasoning=f"No rule-based mapping found for '{invalid_value}' in {enum_type}",
            entity_type=context.get("entity_type", "unknown"),
            entity_name=context.get("entity_name"),
            entity_description=context.get("entity_description"),
            year=context.get("year"),
            field_path=context.get("field_path", "")
        )

    def map_enum_value(self,
                      invalid_value: str,
                      enum_type: str,
                      context: Dict[str, Any]) -> EnumMapping:
        """Use LLM to map invalid enum to valid enum"""

        # Use rule-based if LLM is not available
        if not self.use_llm:
            return self.map_enum_value_rule_based(invalid_value, enum_type, context)

        prompt = self.create_mapping_prompt(invalid_value, enum_type, context)

        try:
            response = self.client.messages.create(
                model="claude-sonnet-4-5-20250929",
                max_tokens=1024,
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            # Parse response
            response_text = response.content[0].text

            # Extract JSON from response
            import re
            json_match = re.search(r'\{[^}]+\}', response_text, re.DOTALL)
            if json_match:
                result = json.loads(json_match.group())
            else:
                result = json.loads(response_text)

            # Validate the recommended value is actually valid
            valid_values = self.VALID_ENUMS.get(enum_type, [])
            recommended = result.get("recommended_value", "")

            if recommended not in valid_values:
                # LLM gave invalid recommendation, lower confidence
                result["confidence"] = 0.0
                result["reasoning"] = f"LLM suggested invalid value: {recommended}"
                result["recommended_value"] = invalid_value  # Keep original

            return EnumMapping(
                original_value=invalid_value,
                recommended_value=result.get("recommended_value", invalid_value),
                confidence=float(result.get("confidence", 0.0)),
                reasoning=result.get("reasoning", "No reasoning provided"),
                entity_type=context.get("entity_type", "unknown"),
                entity_name=context.get("entity_name"),
                entity_description=context.get("entity_description"),
                year=context.get("year"),
                field_path=context.get("field_path", "")
            )

        except Exception as e:
            # Error in LLM call, fallback to rule-based
            print(f"  LLM error, falling back to rules: {str(e)}")
            return self.map_enum_value_rule_based(invalid_value, enum_type, context)

    def make_decision(self, mapping: EnumMapping) -> MappingDecision:
        """Decide whether to apply, review, or flag a mapping"""

        if mapping.confidence >= self.AUTO_APPLY_THRESHOLD:
            return MappingDecision(
                should_apply=True,
                action="auto_apply",
                mapping=mapping
            )
        elif mapping.confidence >= self.REVIEW_THRESHOLD:
            return MappingDecision(
                should_apply=False,
                action="review",
                mapping=mapping
            )
        else:
            return MappingDecision(
                should_apply=False,
                action="flag",
                mapping=mapping
            )

    def apply_mapping(self, data: Dict, error_loc: List, new_value: str) -> bool:
        """Apply a mapping to the data structure"""
        try:
            # Navigate to the parent of the field
            current = data
            for loc in error_loc[:-1]:
                if isinstance(current, dict):
                    current = current[loc]
                elif isinstance(current, list):
                    current = current[int(loc)]

            # Set the new value
            field_name = error_loc[-1]
            if isinstance(current, dict):
                current[field_name] = new_value
                return True

        except Exception as e:
            print(f"Error applying mapping: {e}")
            return False

        return False

    def validate_file(self, file_path: str) -> Tuple[bool, List[Dict]]:
        """Validate a file and return errors"""
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)

            try:
                KnowledgeGraphExtract(**data)
                return True, []
            except ValidationError as e:
                errors = []
                for error in e.errors():
                    errors.append({
                        "loc": error["loc"],
                        "type": error["type"],
                        "msg": error["msg"],
                        "input": error.get("input")
                    })
                return False, errors

        except Exception as e:
            return False, [{"error": str(e)}]

    def process_file(self, file_path: str, dry_run: bool = True) -> Dict[str, Any]:
        """Process a single file and map enum errors"""

        print(f"\n{'='*80}")
        print(f"Processing: {file_path}")
        print(f"{'='*80}\n")

        # Load file
        with open(file_path, 'r') as f:
            data = json.load(f)

        original_data = json.loads(json.dumps(data))  # Deep copy

        # Validate and get errors
        is_valid, errors = self.validate_file(file_path)

        if is_valid:
            print("✓ File is already valid!")
            return {
                "file": file_path,
                "already_valid": True,
                "mappings": []
            }

        # Filter enum errors
        enum_errors = [e for e in errors if "enum" in e.get("type", "")]

        print(f"Found {len(enum_errors)} enum errors")

        if not enum_errors:
            return {
                "file": file_path,
                "enum_errors": 0,
                "mappings": []
            }

        # Process each enum error
        results = {
            "file": file_path,
            "total_enum_errors": len(enum_errors),
            "auto_applied": [],
            "review_queue": [],
            "flagged": [],
            "errors": []
        }

        for i, error in enumerate(enum_errors):
            print(f"\nProcessing error {i+1}/{len(enum_errors)}...")

            error_loc = list(error["loc"])
            invalid_value = error.get("input", "")

            # Determine enum type
            enum_type = self.get_enum_type_for_field(" -> ".join(str(x) for x in error_loc))
            if not enum_type:
                print(f"  Cannot determine enum type for: {error_loc}")
                continue

            # Extract context
            context = self.extract_entity_context(data, error_loc)

            # Map the enum
            print(f"  Invalid value: '{invalid_value}'")
            print(f"  Entity: {context.get('entity_name', 'N/A')}")

            mapping = self.map_enum_value(invalid_value, enum_type, context)
            decision = self.make_decision(mapping)

            print(f"  → Recommended: '{mapping.recommended_value}' (confidence: {mapping.confidence:.2f})")
            print(f"  → Action: {decision.action}")
            print(f"  → Reasoning: {mapping.reasoning}")

            # Store decision
            self.mapping_log.append(decision)

            if decision.action == "auto_apply":
                results["auto_applied"].append(asdict(mapping))
                if not dry_run:
                    # Apply the mapping
                    if self.apply_mapping(data, error_loc, mapping.recommended_value):
                        print(f"  ✓ Applied mapping")
                    else:
                        print(f"  ✗ Failed to apply mapping")
                        results["errors"].append({
                            "mapping": asdict(mapping),
                            "error": "Failed to apply"
                        })
            elif decision.action == "review":
                results["review_queue"].append(asdict(mapping))
            else:
                results["flagged"].append(asdict(mapping))

        # If not dry run, save the file and re-validate
        if not dry_run and results["auto_applied"]:
            # Backup original
            backup_path = file_path + ".backup"
            with open(backup_path, 'w') as f:
                json.dump(original_data, f, indent=2)

            # Save modified file
            with open(file_path, 'w') as f:
                json.dump(data, f, indent=2)

            # Re-validate
            is_valid_after, errors_after = self.validate_file(file_path)

            results["validation_improved"] = len(errors_after) < len(errors)
            results["errors_before"] = len(errors)
            results["errors_after"] = len(errors_after)

            # Rollback if validation worsened
            if len(errors_after) > len(errors):
                print(f"\n⚠ Validation worsened! Rolling back...")
                with open(file_path, 'w') as f:
                    json.dump(original_data, f, indent=2)
                results["rolled_back"] = True
            else:
                print(f"\n✓ Validation improved: {len(errors)} → {len(errors_after)} errors")
                results["rolled_back"] = False

        return results

    def generate_report(self, results: List[Dict[str, Any]]) -> str:
        """Generate summary report"""

        total_auto = sum(len(r.get("auto_applied", [])) for r in results)
        total_review = sum(len(r.get("review_queue", [])) for r in results)
        total_flagged = sum(len(r.get("flagged", [])) for r in results)

        report = []
        report.append("=" * 80)
        report.append("PHASE 2: LLM ENUM MAPPING REPORT")
        report.append("=" * 80)
        report.append(f"Generated: {datetime.now().isoformat()}")
        report.append("")
        report.append(f"Files processed: {len(results)}")
        report.append(f"Auto-applied (≥90% confidence): {total_auto}")
        report.append(f"Review queue (70-90% confidence): {total_review}")
        report.append(f"Flagged (<70% confidence): {total_flagged}")
        report.append("")

        # Detailed breakdown
        for result in results:
            if result.get("total_enum_errors", 0) > 0:
                report.append(f"\n{result['file']}")
                report.append(f"  Total enum errors: {result.get('total_enum_errors', 0)}")
                report.append(f"  Auto-applied: {len(result.get('auto_applied', []))}")
                report.append(f"  Review queue: {len(result.get('review_queue', []))}")
                report.append(f"  Flagged: {len(result.get('flagged', []))}")

                if not result.get("rolled_back") and "errors_after" in result:
                    report.append(f"  Validation: {result['errors_before']} → {result['errors_after']} errors")

        report.append("\n" + "=" * 80)
        return "\n".join(report)


def test_sample_errors(num_samples: int = 10):
    """Test on sample enum errors"""

    print("=" * 80)
    print("TESTING ENUM MAPPER ON SAMPLE ERRORS")
    print("=" * 80)

    mapper = EnumMapper()

    # Find files with enum errors
    kg_dir = Path("/home/user/colonial_office_list/knowledge_graph_extracts")
    test_files = sorted(kg_dir.glob("*_extracted.json"))[:5]  # Test first 5 files

    all_mappings = []

    for file_path in test_files:
        print(f"\nChecking {file_path.name}...")

        with open(file_path) as f:
            data = json.load(f)

        # Get enum errors
        try:
            KnowledgeGraphExtract(**data)
            print("  No errors")
            continue
        except ValidationError as e:
            enum_errors = [err for err in e.errors() if "enum" in err.get("type", "")]

            if not enum_errors:
                continue

            print(f"  Found {len(enum_errors)} enum errors")

            # Process first few errors
            for error in enum_errors[:3]:  # Limit to 3 per file
                if len(all_mappings) >= num_samples:
                    break

                error_loc = list(error["loc"])
                invalid_value = error.get("input", "")

                enum_type = mapper.get_enum_type_for_field(" -> ".join(str(x) for x in error_loc))
                if not enum_type:
                    continue

                context = mapper.extract_entity_context(data, error_loc)

                print(f"\n  Processing: '{invalid_value}' ({enum_type})")
                mapping = mapper.map_enum_value(invalid_value, enum_type, context)

                all_mappings.append(mapping)

                print(f"    Original: {mapping.original_value}")
                print(f"    Recommended: {mapping.recommended_value}")
                print(f"    Confidence: {mapping.confidence:.2f}")
                print(f"    Reasoning: {mapping.reasoning}")

        if len(all_mappings) >= num_samples:
            break

    # Summary
    print("\n" + "=" * 80)
    print("SAMPLE RESULTS SUMMARY")
    print("=" * 80)

    for i, mapping in enumerate(all_mappings, 1):
        print(f"\n{i}. {mapping.original_value} → {mapping.recommended_value}")
        print(f"   Confidence: {mapping.confidence:.2f}")
        print(f"   Entity: {mapping.entity_name or 'N/A'}")
        print(f"   Year: {mapping.year or 'N/A'}")
        print(f"   Reasoning: {mapping.reasoning}")

    return all_mappings


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Phase 2: LLM Enum Mapper")
    parser.add_argument("--test", action="store_true", help="Run test on sample errors")
    parser.add_argument("--file", type=str, help="Process specific file")
    parser.add_argument("--dry-run", action="store_true", default=True, help="Don't modify files")
    parser.add_argument("--apply", action="store_true", help="Actually apply changes")
    parser.add_argument("--samples", type=int, default=10, help="Number of samples for test")

    args = parser.parse_args()

    if args.test:
        test_sample_errors(args.samples)
    elif args.file:
        mapper = EnumMapper()
        result = mapper.process_file(args.file, dry_run=not args.apply)
        print(json.dumps(result, indent=2))
    else:
        print("Use --test to test on samples or --file <path> to process a file")
        print("Add --apply to actually modify files (otherwise dry-run)")
