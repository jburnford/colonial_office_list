"""
Schema validator for Colonial Office List Knowledge Graph extracts.

Validates JSON files against Pydantic schema and generates detailed error reports.
"""

import json
import sys
from pathlib import Path
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime
from pydantic import ValidationError

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from schemas.kg_schema import KnowledgeGraphExtract


class ValidationResult:
    """Container for validation results"""

    def __init__(self, file_path: str):
        self.file_path = file_path
        self.year = None
        self.valid = False
        self.errors: List[str] = []
        self.warnings: List[str] = []
        self.entity_counts: Dict[str, int] = {}
        self.validation_time: Optional[float] = None

    def add_error(self, error: str):
        """Add an error message"""
        self.errors.append(error)

    def add_warning(self, warning: str):
        """Add a warning message"""
        self.warnings.append(warning)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON export"""
        return {
            "file_path": self.file_path,
            "year": self.year,
            "valid": self.valid,
            "error_count": len(self.errors),
            "warning_count": len(self.warnings),
            "errors": self.errors,
            "warnings": self.warnings,
            "entity_counts": self.entity_counts,
            "validation_time_seconds": self.validation_time
        }


class SchemaValidator:
    """Validates knowledge graph JSON files against Pydantic schema"""

    def __init__(self):
        self.results: List[ValidationResult] = []

    def validate_file(self, file_path: str) -> ValidationResult:
        """
        Validate a single JSON file.

        Args:
            file_path: Path to JSON file to validate

        Returns:
            ValidationResult object with validation details
        """
        start_time = datetime.now()
        result = ValidationResult(file_path)

        try:
            # Load JSON file
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Extract year from metadata if available
            if isinstance(data, dict) and 'metadata' in data:
                result.year = data.get('metadata', {}).get('year')

            # Validate against Pydantic schema
            try:
                kg_extract = KnowledgeGraphExtract(**data)
                result.valid = True
                result.entity_counts = kg_extract.get_entity_counts()

                # Check for data quality warnings
                self._check_quality_warnings(kg_extract, result)

            except ValidationError as e:
                result.valid = False
                # Parse Pydantic validation errors
                for error in e.errors():
                    loc = " -> ".join(str(l) for l in error['loc'])
                    msg = error['msg']
                    error_type = error['type']
                    result.add_error(f"[{loc}] {error_type}: {msg}")

        except json.JSONDecodeError as e:
            result.add_error(f"Invalid JSON: {str(e)}")
        except FileNotFoundError:
            result.add_error(f"File not found: {file_path}")
        except Exception as e:
            result.add_error(f"Unexpected error: {str(e)}")

        end_time = datetime.now()
        result.validation_time = (end_time - start_time).total_seconds()

        self.results.append(result)
        return result

    def _check_quality_warnings(self, kg_extract: KnowledgeGraphExtract, result: ValidationResult):
        """Check for data quality issues that don't violate schema but might be problematic"""

        # Check for empty entity collections
        entity_counts = kg_extract.get_entity_counts()
        total_entities = sum(v for k, v in entity_counts.items() if k != 'relationships')

        if total_entities == 0:
            result.add_warning("No entities extracted (all entity collections are empty)")

        # Check for people without positions
        people_without_positions = sum(1 for p in kg_extract.entities.people if not p.positions)
        if people_without_positions > 0:
            result.add_warning(
                f"{people_without_positions} person entities have no positions recorded"
            )

        # Check for positions without location
        positions_without_location = 0
        for person in kg_extract.entities.people:
            for pos in person.positions:
                if not pos.location:
                    positions_without_location += 1
        if positions_without_location > 0:
            result.add_warning(
                f"{positions_without_location} positions missing location information"
            )

        # Check for positions without salary
        positions_without_salary = 0
        for person in kg_extract.entities.people:
            for pos in person.positions:
                if not pos.salary:
                    positions_without_salary += 1
        if positions_without_salary > 10:  # Only warn if significant number
            pct = (positions_without_salary / sum(len(p.positions) for p in kg_extract.entities.people)) * 100
            result.add_warning(
                f"{positions_without_salary} positions ({pct:.1f}%) missing salary information"
            )

        # Check for duplicate entity IDs
        all_ids = []
        for entity_list in [
            kg_extract.entities.places,
            kg_extract.entities.people,
            kg_extract.entities.institutions,
            kg_extract.entities.economic_data,
            kg_extract.entities.infrastructure,
            kg_extract.entities.demographics,
            kg_extract.entities.events
        ]:
            all_ids.extend(e.id for e in entity_list)

        duplicates = [id for id in set(all_ids) if all_ids.count(id) > 1]
        if duplicates:
            result.add_warning(f"Duplicate entity IDs found: {', '.join(duplicates[:10])}")
            if len(duplicates) > 10:
                result.add_warning(f"... and {len(duplicates) - 10} more duplicates")

        # Check for relationships pointing to non-existent entities
        # (This is already handled by Pydantic validation, but we can add more context)

    def validate_directory(self, directory: str, pattern: str = "*_extracted.json") -> List[ValidationResult]:
        """
        Validate all matching JSON files in a directory.

        Args:
            directory: Directory path
            pattern: Glob pattern for files to validate

        Returns:
            List of ValidationResult objects
        """
        directory_path = Path(directory)
        if not directory_path.exists():
            raise FileNotFoundError(f"Directory not found: {directory}")

        files = sorted(directory_path.glob(pattern))

        print(f"Found {len(files)} files to validate in {directory}")

        for file_path in files:
            print(f"Validating {file_path.name}...", end=" ")
            result = self.validate_file(str(file_path))
            if result.valid:
                print(f"✓ VALID ({result.entity_counts.get('people', 0)} people, "
                      f"{result.entity_counts.get('places', 0)} places)")
            else:
                print(f"✗ INVALID ({len(result.errors)} errors)")

        return self.results

    def generate_summary_report(self) -> str:
        """Generate a summary report of all validation results"""

        if not self.results:
            return "No validation results available."

        total_files = len(self.results)
        valid_files = sum(1 for r in self.results if r.valid)
        invalid_files = total_files - valid_files

        total_errors = sum(len(r.errors) for r in self.results)
        total_warnings = sum(len(r.warnings) for r in self.results)

        report = []
        report.append("=" * 80)
        report.append("KNOWLEDGE GRAPH VALIDATION SUMMARY REPORT")
        report.append("=" * 80)
        report.append(f"Generated: {datetime.now().isoformat()}")
        report.append("")
        report.append(f"Total files validated: {total_files}")
        report.append(f"Valid files: {valid_files} ({valid_files/total_files*100:.1f}%)")
        report.append(f"Invalid files: {invalid_files} ({invalid_files/total_files*100:.1f}%)")
        report.append(f"Total errors: {total_errors}")
        report.append(f"Total warnings: {total_warnings}")
        report.append("")

        if invalid_files > 0:
            report.append("-" * 80)
            report.append("FILES WITH ERRORS:")
            report.append("-" * 80)
            for result in self.results:
                if not result.valid:
                    report.append(f"\n{result.file_path} (Year: {result.year})")
                    report.append(f"  Errors: {len(result.errors)}")
                    for error in result.errors[:5]:  # Show first 5 errors
                        report.append(f"    - {error}")
                    if len(result.errors) > 5:
                        report.append(f"    ... and {len(result.errors) - 5} more errors")

        if total_warnings > 0:
            report.append("\n" + "-" * 80)
            report.append("DATA QUALITY WARNINGS:")
            report.append("-" * 80)

            # Group warnings by type
            warning_counts = {}
            for result in self.results:
                for warning in result.warnings:
                    # Extract warning type (first part before numbers)
                    warning_type = warning.split()[0:5]  # First few words
                    warning_key = " ".join(warning_type)
                    warning_counts[warning_key] = warning_counts.get(warning_key, 0) + 1

            for warning_type, count in sorted(warning_counts.items(), key=lambda x: -x[1]):
                report.append(f"  {count} files: {warning_type}...")

        # Entity statistics for valid files
        if valid_files > 0:
            report.append("\n" + "-" * 80)
            report.append("ENTITY STATISTICS (Valid Files Only):")
            report.append("-" * 80)

            entity_totals = {
                "places": 0,
                "people": 0,
                "institutions": 0,
                "economic_data": 0,
                "infrastructure": 0,
                "demographics": 0,
                "events": 0,
                "relationships": 0
            }

            for result in self.results:
                if result.valid:
                    for entity_type, count in result.entity_counts.items():
                        entity_totals[entity_type] = entity_totals.get(entity_type, 0) + count

            report.append(f"  Total places: {entity_totals['places']:,}")
            report.append(f"  Total people: {entity_totals['people']:,}")
            report.append(f"  Total institutions: {entity_totals['institutions']:,}")
            report.append(f"  Total economic data points: {entity_totals['economic_data']:,}")
            report.append(f"  Total infrastructure: {entity_totals['infrastructure']:,}")
            report.append(f"  Total demographics: {entity_totals['demographics']:,}")
            report.append(f"  Total events: {entity_totals['events']:,}")
            report.append(f"  Total relationships: {entity_totals['relationships']:,}")

        report.append("\n" + "=" * 80)

        return "\n".join(report)

    def export_results_json(self, output_file: str):
        """Export detailed validation results to JSON"""
        results_data = {
            "validation_date": datetime.now().isoformat(),
            "total_files": len(self.results),
            "valid_files": sum(1 for r in self.results if r.valid),
            "results": [r.to_dict() for r in self.results]
        }

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results_data, f, indent=2, ensure_ascii=False)

        print(f"Detailed results exported to: {output_file}")


def main():
    """Main entry point for command-line usage"""
    import argparse

    parser = argparse.ArgumentParser(
        description="Validate Colonial Office List knowledge graph JSON files"
    )
    parser.add_argument(
        "path",
        help="Path to JSON file or directory containing JSON files"
    )
    parser.add_argument(
        "-p", "--pattern",
        default="*_extracted.json",
        help="Glob pattern for files (when validating directory)"
    )
    parser.add_argument(
        "-o", "--output",
        help="Output file for detailed JSON results"
    )
    parser.add_argument(
        "-r", "--report",
        help="Output file for summary report (text)"
    )

    args = parser.parse_args()

    validator = SchemaValidator()
    path = Path(args.path)

    # Validate file or directory
    if path.is_file():
        print(f"Validating file: {path}")
        result = validator.validate_file(str(path))
        if result.valid:
            print(f"✓ File is VALID")
            print(f"Entity counts: {result.entity_counts}")
        else:
            print(f"✗ File is INVALID")
            print(f"Errors ({len(result.errors)}):")
            for error in result.errors:
                print(f"  - {error}")
        if result.warnings:
            print(f"Warnings ({len(result.warnings)}):")
            for warning in result.warnings:
                print(f"  - {warning}")
    elif path.is_dir():
        print(f"Validating directory: {path}")
        validator.validate_directory(str(path), args.pattern)
    else:
        print(f"Error: Path does not exist: {path}")
        return 1

    # Generate and display summary
    print("\n")
    summary = validator.generate_summary_report()
    print(summary)

    # Export results if requested
    if args.output:
        validator.export_results_json(args.output)

    if args.report:
        with open(args.report, 'w', encoding='utf-8') as f:
            f.write(summary)
        print(f"Summary report written to: {args.report}")

    # Return exit code based on validation success
    if all(r.valid for r in validator.results):
        return 0
    else:
        return 1


if __name__ == "__main__":
    sys.exit(main())
