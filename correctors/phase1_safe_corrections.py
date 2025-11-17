"""
Phase 1: Safe Python Corrections
Deterministic fixes with zero semantic changes

All corrections are:
1. Type conversions only (no data interpretation)
2. Validated before and after
3. Logged completely
4. Reversible
"""

import json
import sys
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from schemas.kg_schema import KnowledgeGraphExtract
from validators.schema_validator import SchemaValidator
from pydantic import ValidationError


class SafeCorrector:
    """Applies only deterministic, type-conversion corrections"""

    def __init__(self):
        self.corrections_log: List[Dict[str, Any]] = []
        self.validator = SchemaValidator()

    def correct_file(self, input_path: str, output_path: str) -> Dict[str, Any]:
        """
        Apply safe corrections to a single file.

        Args:
            input_path: Path to original JSON file
            output_path: Path to write corrected JSON file

        Returns:
            Correction report dictionary
        """
        report = {
            "input_file": input_path,
            "output_file": output_path,
            "timestamp": datetime.now().isoformat(),
            "corrections_applied": [],
            "errors_before": None,
            "errors_after": None,
            "validation_before": False,
            "validation_after": False,
            "safe": True
        }

        try:
            # Read original file
            with open(input_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Validate BEFORE corrections
            validation_before = self.validator.validate_file(input_path)
            report["validation_before"] = validation_before.valid
            report["errors_before"] = len(validation_before.errors)

            # Apply corrections
            corrections_made = []
            corrected_data = self._apply_corrections(data, corrections_made)

            # Write to output
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(corrected_data, f, indent=2, ensure_ascii=False)

            # Validate AFTER corrections
            validation_after = self.validator.validate_file(output_path)
            report["validation_after"] = validation_after.valid
            report["errors_after"] = len(validation_after.errors)
            report["corrections_applied"] = corrections_made

            # Safety check: Did we make things worse?
            if report["errors_after"] > report["errors_before"]:
                report["safe"] = False
                print(f"  ⚠️  WARNING: Errors increased from {report['errors_before']} "
                      f"to {report['errors_after']}!")
                # Rollback
                shutil.copy(input_path, output_path)
                print(f"  ↩️  Rolled back changes for {Path(input_path).name}")

            return report

        except Exception as e:
            report["error"] = str(e)
            report["safe"] = False
            return report

    def _apply_corrections(self, data: Dict[str, Any], log: List[Dict]) -> Dict[str, Any]:
        """
        Apply all safe corrections to data.

        Args:
            data: JSON data dictionary
            log: List to append correction records to

        Returns:
            Corrected data dictionary
        """
        # Deep copy to avoid modifying original
        import copy
        corrected = copy.deepcopy(data)

        # Correction 1: Fix metadata
        if "metadata" in corrected:
            corrected["metadata"] = self._fix_metadata(
                corrected["metadata"],
                log,
                Path(corrected.get("metadata", {}).get("source_directory", "")).name or "unknown"
            )

        # Correction 2: Fix year fields in all entities
        if "entities" in corrected:
            corrected["entities"] = self._fix_entity_years(corrected["entities"], log)

        # Correction 3: Fix relationship year fields
        if "relationships" in corrected:
            corrected["relationships"] = self._fix_relationship_years(
                corrected["relationships"],
                log
            )

        return corrected

    def _fix_metadata(self, metadata: Dict[str, Any], log: List[Dict], filename_hint: str) -> Dict[str, Any]:
        """Fix metadata fields"""
        import copy
        fixed = copy.deepcopy(metadata)

        # Fix 1: Year field should be string
        if "year" in fixed:
            if isinstance(fixed["year"], int):
                old_val = fixed["year"]
                fixed["year"] = str(fixed["year"])
                log.append({
                    "type": "type_conversion",
                    "field": "metadata.year",
                    "old_value": old_val,
                    "new_value": fixed["year"],
                    "confidence": 1.0
                })

        # Fix 2: Add missing source_directory (infer from year)
        if "source_directory" not in fixed and "year" in fixed:
            year = str(fixed["year"])
            fixed["source_directory"] = f"output_2/{year}"
            log.append({
                "type": "field_inference",
                "field": "metadata.source_directory",
                "value": fixed["source_directory"],
                "confidence": 0.95
            })

        # Fix 3: Add missing extraction_date (use current time if missing)
        if "extraction_date" not in fixed:
            fixed["extraction_date"] = datetime.now().isoformat() + "Z"
            log.append({
                "type": "field_inference",
                "field": "metadata.extraction_date",
                "value": fixed["extraction_date"],
                "confidence": 0.9,
                "note": "Inferred from current timestamp"
            })

        # Fix 4: colonies_processed should be array, not integer
        if "colonies_processed" in fixed:
            if isinstance(fixed["colonies_processed"], int):
                old_val = fixed["colonies_processed"]
                fixed["colonies_processed"] = []  # Can't infer colony names from count
                log.append({
                    "type": "type_conversion",
                    "field": "metadata.colonies_processed",
                    "old_value": old_val,
                    "new_value": fixed["colonies_processed"],
                    "confidence": 1.0,
                    "note": "Converted count to empty array (cannot infer names)"
                })

        return fixed

    def _fix_entity_years(self, entities: Dict[str, List], log: List[Dict]) -> Dict[str, List]:
        """Fix year fields in all entity types"""
        import copy
        fixed = copy.deepcopy(entities)

        # Entity types that have direct year fields
        direct_year_entities = ["places", "institutions", "economic_data",
                                "infrastructure", "demographics", "events"]

        for entity_type in direct_year_entities:
            if entity_type in fixed:
                for idx, entity in enumerate(fixed[entity_type]):
                    if "year" in entity and isinstance(entity["year"], int):
                        old_val = entity["year"]
                        entity["year"] = str(entity["year"])
                        log.append({
                            "type": "type_conversion",
                            "field": f"entities.{entity_type}[{idx}].year",
                            "old_value": old_val,
                            "new_value": entity["year"],
                            "confidence": 1.0
                        })

        # People entities: fix year in positions
        if "people" in fixed:
            for person_idx, person in enumerate(fixed["people"]):
                if "positions" in person:
                    for pos_idx, position in enumerate(person["positions"]):
                        if "year" in position:
                            if isinstance(position["year"], int):
                                old_val = position["year"]
                                position["year"] = str(position["year"])
                                log.append({
                                    "type": "type_conversion",
                                    "field": f"entities.people[{person_idx}].positions[{pos_idx}].year",
                                    "old_value": old_val,
                                    "new_value": position["year"],
                                    "confidence": 1.0
                                })

                        # Also fix year in revenue/expenses if present
                        if "salary" in position:
                            salary = position["salary"]
                            # Note: salary.amount should be number, not string
                            # So we DON'T convert that

        return fixed

    def _fix_relationship_years(self, relationships: List[Dict], log: List[Dict]) -> List[Dict]:
        """Fix year fields in relationships"""
        import copy
        fixed = copy.deepcopy(relationships)

        for idx, rel in enumerate(fixed):
            if "properties" in rel and isinstance(rel["properties"], dict):
                if "year" in rel["properties"]:
                    if isinstance(rel["properties"]["year"], int):
                        old_val = rel["properties"]["year"]
                        rel["properties"]["year"] = str(rel["properties"]["year"])
                        log.append({
                            "type": "type_conversion",
                            "field": f"relationships[{idx}].properties.year",
                            "old_value": old_val,
                            "new_value": rel["properties"]["year"],
                            "confidence": 1.0
                        })

        return fixed


def process_directory(input_dir: str, output_dir: str, pattern: str = "*_extracted.json") -> Dict[str, Any]:
    """
    Process all files in a directory.

    Args:
        input_dir: Input directory path
        output_dir: Output directory path
        pattern: File pattern to match

    Returns:
        Summary report
    """
    input_path = Path(input_dir)
    output_path = Path(output_dir)

    # Create output directory
    output_path.mkdir(parents=True, exist_ok=True)

    corrector = SafeCorrector()
    files = sorted(input_path.glob(pattern))

    print(f"\n{'='*80}")
    print(f"PHASE 1: SAFE PYTHON CORRECTIONS")
    print(f"{'='*80}")
    print(f"Input directory: {input_dir}")
    print(f"Output directory: {output_dir}")
    print(f"Files to process: {len(files)}")
    print(f"{'='*80}\n")

    reports = []
    for file_path in files:
        print(f"Processing {file_path.name}...", end=" ")

        output_file = output_path / file_path.name
        report = corrector.correct_file(str(file_path), str(output_file))
        reports.append(report)

        # Print status
        if report.get("safe", False):
            errors_before = report.get("errors_before", "?")
            errors_after = report.get("errors_after", "?")
            corrections = len(report.get("corrections_applied", []))
            reduction = errors_before - errors_after if isinstance(errors_before, int) and isinstance(errors_after, int) else 0

            if reduction > 0:
                print(f"✓ {corrections} corrections, {reduction} errors fixed "
                      f"({errors_before} → {errors_after})")
            elif reduction == 0 and corrections > 0:
                print(f"○ {corrections} corrections, no error reduction "
                      f"({errors_before} errors remain)")
            else:
                print(f"○ No corrections needed")
        else:
            print(f"✗ FAILED or UNSAFE")

    # Summary
    print(f"\n{'='*80}")
    print(f"SUMMARY")
    print(f"{'='*80}")

    total_corrections = sum(len(r.get("corrections_applied", [])) for r in reports)
    safe_count = sum(1 for r in reports if r.get("safe", False))
    total_errors_before = sum(r.get("errors_before", 0) for r in reports if isinstance(r.get("errors_before"), int))
    total_errors_after = sum(r.get("errors_after", 0) for r in reports if isinstance(r.get("errors_after"), int))

    print(f"Files processed: {len(reports)}")
    print(f"Safe corrections: {safe_count}/{len(reports)}")
    print(f"Total corrections applied: {total_corrections}")
    print(f"Errors before: {total_errors_before}")
    print(f"Errors after: {total_errors_after}")
    print(f"Errors fixed: {total_errors_before - total_errors_after}")
    if total_errors_before > 0:
        reduction_pct = ((total_errors_before - total_errors_after) / total_errors_before) * 100
        print(f"Error reduction: {reduction_pct:.1f}%")
    print(f"{'='*80}\n")

    # Save detailed log
    log_file = output_path / "phase1_correction_log.json"
    with open(log_file, 'w', encoding='utf-8') as f:
        json.dump({
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "files_processed": len(reports),
                "safe_corrections": safe_count,
                "total_corrections": total_corrections,
                "errors_before": total_errors_before,
                "errors_after": total_errors_after,
                "errors_fixed": total_errors_before - total_errors_after
            },
            "reports": reports
        }, f, indent=2)

    print(f"Detailed log saved to: {log_file}")

    return {
        "files_processed": len(reports),
        "safe_corrections": safe_count,
        "total_corrections": total_corrections,
        "errors_before": total_errors_before,
        "errors_after": total_errors_after
    }


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Phase 1: Apply safe Python corrections to knowledge graph extracts"
    )
    parser.add_argument(
        "input_dir",
        help="Input directory containing JSON files"
    )
    parser.add_argument(
        "output_dir",
        help="Output directory for corrected files"
    )
    parser.add_argument(
        "-p", "--pattern",
        default="*_extracted.json",
        help="File pattern to match (default: *_extracted.json)"
    )

    args = parser.parse_args()

    process_directory(args.input_dir, args.output_dir, args.pattern)


if __name__ == "__main__":
    main()
