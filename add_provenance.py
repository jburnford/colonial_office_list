#!/usr/bin/env python3
"""
Provenance Linking Agent for Colonial Office List Knowledge Graph
Adds source document provenance to all entities in KG files for years 1908-1917.
"""

import json
import os
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Tuple, Optional

# Configuration
BASE_DIR = Path("/home/user/colonial_office_list")
KG_V2_DIR = BASE_DIR / "knowledge_graph_extracts_v2"
KG_V3_DIR = BASE_DIR / "knowledge_graph_extracts_v3"
OUTPUT2_DIR = BASE_DIR / "output_2"
REPORTS_DIR = BASE_DIR / "reports/phase_b"

YEARS = [1908, 1909, 1910, 1911, 1912, 1913, 1914, 1915, 1917]
ENTITY_TYPES = ["people", "places", "institutions", "economic_data", "infrastructure", "demographics", "events"]

class ProvenanceLinker:
    def __init__(self):
        self.stats = {
            "years_processed": 0,
            "entities_processed": 0,
            "entities_with_provenance": 0,
            "high_confidence": 0,  # 0.95-1.0
            "medium_confidence": 0,  # 0.85-0.94
            "low_confidence": 0,  # 0.70-0.84
            "flagged_for_review": 0,  # < 0.70
            "errors": [],
            "year_stats": {}
        }

    def normalize_filename(self, colony_name: str) -> str:
        """Convert colony name to expected filename format."""
        if not colony_name:
            return None
        # Replace spaces with underscores, remove special chars, uppercase
        filename = colony_name.strip().upper()
        filename = filename.replace(" ", "_")
        filename = filename.replace(".", "")
        filename = filename.replace(",", "")
        filename = filename.replace("'", "")
        filename = re.sub(r'[^\w_]', '', filename)
        return f"{filename}.md"

    def find_text_in_file(self, filepath: Path, search_text: str) -> Tuple[Optional[str], float]:
        """
        Find text in source file and return line numbers.
        Returns (line_range, confidence_score)
        """
        if not filepath.exists():
            return None, 0.0

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # Clean search text for matching
            clean_search = search_text.strip()[:200]  # Use first 200 chars

            # Strategy 1: Exact match
            for i, line in enumerate(lines):
                if clean_search in line:
                    return f"{i+1}", 0.98

            # Strategy 2: Split search into words and find lines containing multiple words
            search_words = [w for w in clean_search.split() if len(w) > 3][:5]
            best_match_line = None
            best_match_count = 0

            for i, line in enumerate(lines):
                match_count = sum(1 for word in search_words if word.lower() in line.lower())
                if match_count > best_match_count:
                    best_match_count = match_count
                    best_match_line = i + 1

            if best_match_count >= 2:
                confidence = 0.85 if best_match_count >= 3 else 0.75
                return f"{best_match_line}", confidence

            # Strategy 3: Look for key identifiers (names, positions)
            # Extract potential names or identifiers
            if "," in clean_search:
                key_term = clean_search.split(",")[0].strip()
                for i, line in enumerate(lines):
                    if key_term in line:
                        return f"{i+1}", 0.80

            return None, 0.0

        except Exception as e:
            print(f"  Error reading {filepath}: {e}")
            return None, 0.0

    def get_source_section(self, entity: Dict) -> str:
        """Determine the source section from entity metadata."""
        # Try to infer section from entity type and data
        if "position" in entity:
            return "Government Officials"
        elif "type" in entity and entity["type"] == "place":
            return "Geographical Information"
        elif "population" in entity:
            return "Demographics"
        elif "value" in entity or "amount" in entity:
            return "Economic Data"
        return "General Information"

    def add_provenance_to_entity(self, entity: Dict, year: int, metadata: Dict, source_dir: Path) -> Dict:
        """Add provenance information to a single entity."""
        # Get colony name
        colony = entity.get("colony", "")
        if not colony:
            # Try alternative fields
            colony = entity.get("location", entity.get("place", ""))

        if not colony:
            # Can't determine source without colony/location
            return entity

        # Find source file
        filename = self.normalize_filename(colony)
        if not filename:
            return entity

        source_file = source_dir / filename
        relative_source = f"output_2/{year}_manual_parsed/{filename}"

        # Find text in source
        source_text = entity.get("source_text", entity.get("name", ""))
        line_numbers, confidence = self.find_text_in_file(source_file, source_text)

        if line_numbers is None:
            # File doesn't exist or text not found
            # Try to use metadata boundaries if available
            if metadata and "colonies" in metadata:
                for col_info in metadata["colonies"]:
                    if col_info["filename"] == filename:
                        line_numbers = f"{col_info['start_line']}-{col_info['end_line']}"
                        confidence = 0.70  # Low confidence - metadata inference
                        break

        if line_numbers is None:
            # Still no match - flag for review
            line_numbers = "unknown"
            confidence = 0.50

        # Add provenance
        entity["provenance"] = {
            "source_file": relative_source,
            "source_lines": line_numbers,
            "source_section": self.get_source_section(entity),
            "extraction_confidence": confidence,
            "extraction_date": datetime.now().strftime("%Y-%m-%d"),
            "extraction_agent": "provenance_linker_1908_1917",
            "verification_status": "automated"
        }

        # Update stats
        self.stats["entities_with_provenance"] += 1
        if confidence >= 0.95:
            self.stats["high_confidence"] += 1
        elif confidence >= 0.85:
            self.stats["medium_confidence"] += 1
        elif confidence >= 0.70:
            self.stats["low_confidence"] += 1
        else:
            self.stats["flagged_for_review"] += 1

        return entity

    def process_year(self, year: int) -> bool:
        """Process a single year's KG file."""
        print(f"\n{'='*60}")
        print(f"Processing Year {year}")
        print(f"{'='*60}")

        # Load KG file
        kg_file = KG_V2_DIR / f"{year}_extracted.json"
        if not kg_file.exists():
            print(f"  WARNING: KG file not found: {kg_file}")
            self.stats["errors"].append(f"{year}: KG file not found")
            return False

        print(f"  Loading KG file: {kg_file}")
        with open(kg_file, 'r', encoding='utf-8') as f:
            kg_data = json.load(f)

        # Load metadata
        metadata_file = OUTPUT2_DIR / f"{year}_manual_parsed.json"
        metadata = None
        if metadata_file.exists():
            print(f"  Loading metadata: {metadata_file}")
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
        else:
            print(f"  WARNING: Metadata file not found: {metadata_file}")

        # Determine source directory
        source_dir = OUTPUT2_DIR / f"{year}_manual_parsed"
        if not source_dir.exists():
            print(f"  ERROR: Source directory not found: {source_dir}")
            self.stats["errors"].append(f"{year}: Source directory not found")
            return False

        print(f"  Source directory: {source_dir}")

        # Process entities
        year_entity_count = 0
        year_provenance_count = 0

        entities = kg_data.get("entities", {})

        for entity_type in ENTITY_TYPES:
            if entity_type not in entities:
                continue

            entity_list = entities[entity_type]
            print(f"  Processing {len(entity_list)} {entity_type}...")

            for i, entity in enumerate(entity_list):
                self.stats["entities_processed"] += 1
                year_entity_count += 1

                # Add provenance
                entities[entity_type][i] = self.add_provenance_to_entity(
                    entity, year, metadata, source_dir
                )

                if "provenance" in entities[entity_type][i]:
                    year_provenance_count += 1

                # Progress indicator
                if (i + 1) % 100 == 0:
                    print(f"    Processed {i+1}/{len(entity_list)} {entity_type}...")

        # Save enhanced KG
        output_file = KG_V3_DIR / f"{year}_extracted.json"
        print(f"\n  Saving enhanced KG to: {output_file}")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(kg_data, f, indent=2, ensure_ascii=False)

        # Record year stats
        self.stats["year_stats"][year] = {
            "total_entities": year_entity_count,
            "entities_with_provenance": year_provenance_count,
            "coverage": f"{(year_provenance_count/year_entity_count*100):.1f}%" if year_entity_count > 0 else "0%"
        }

        self.stats["years_processed"] += 1
        print(f"  ✓ Year {year} complete: {year_provenance_count}/{year_entity_count} entities enhanced")

        return True

    def generate_report(self):
        """Generate provenance coverage report."""
        report_file = REPORTS_DIR / "provenance_1908_1917.md"

        report = f"""# Provenance Linking Report: 1908-1917
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

## Summary Statistics

- **Years Processed**: {self.stats['years_processed']} / {len([y for y in YEARS if (KG_V2_DIR / f"{y}_extracted.json").exists()])}
- **Total Entities Processed**: {self.stats['entities_processed']:,}
- **Entities with Provenance**: {self.stats['entities_with_provenance']:,}
- **Overall Coverage**: {(self.stats['entities_with_provenance']/self.stats['entities_processed']*100):.1f}%

## Confidence Distribution

| Confidence Level | Count | Percentage |
|-----------------|-------|------------|
| High (0.95-1.0) | {self.stats['high_confidence']:,} | {(self.stats['high_confidence']/self.stats['entities_with_provenance']*100):.1f}% |
| Medium (0.85-0.94) | {self.stats['medium_confidence']:,} | {(self.stats['medium_confidence']/self.stats['entities_with_provenance']*100):.1f}% |
| Low (0.70-0.84) | {self.stats['low_confidence']:,} | {(self.stats['low_confidence']/self.stats['entities_with_provenance']*100):.1f}% |
| Flagged for Review (<0.70) | {self.stats['flagged_for_review']:,} | {(self.stats['flagged_for_review']/self.stats['entities_with_provenance']*100):.1f}% |

## Year-by-Year Breakdown

| Year | Total Entities | With Provenance | Coverage |
|------|---------------|-----------------|----------|
"""

        for year in sorted(self.stats["year_stats"].keys()):
            ystats = self.stats["year_stats"][year]
            report += f"| {year} | {ystats['total_entities']:,} | {ystats['entities_with_provenance']:,} | {ystats['coverage']} |\n"

        if self.stats["errors"]:
            report += f"\n## Errors and Warnings\n\n"
            for error in self.stats["errors"]:
                report += f"- {error}\n"

        report += f"""
## Provenance Schema

Each entity now includes a `provenance` object with the following structure:

```json
{{
  "provenance": {{
    "source_file": "output_2/YYYY_manual_parsed/COLONY_NAME.md",
    "source_lines": "120-145",
    "source_section": "Government Officials",
    "extraction_confidence": 0.95,
    "extraction_date": "2025-11-17",
    "extraction_agent": "provenance_linker_1908_1917",
    "verification_status": "automated"
  }}
}}
```

## Confidence Scoring Methodology

- **0.95-1.0**: Exact text match found in source file
- **0.85-0.94**: Strong contextual match (3+ keywords matched)
- **0.70-0.84**: Inferred from metadata or 2 keywords matched
- **< 0.70**: Flagged for human review (text not found, missing source)

## Next Steps

1. Review entities flagged for manual verification (confidence < 0.70)
2. Validate provenance links for sample entities
3. Use provenance for ground truth analysis and data quality checks
4. Extend provenance linking to remaining years

## Files Generated

Enhanced KG files created in: `knowledge_graph_extracts_v3/`
"""

        print(f"\n{'='*60}")
        print(f"Saving report to: {report_file}")
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"{'='*60}\n")
        return report

def main():
    """Main execution function."""
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║    PROVENANCE LINKING AGENT: 1908-1917                       ║
║    Colonial Office List Knowledge Graph                      ║
╚══════════════════════════════════════════════════════════════╝

Mission: Add source document provenance to all entities
Years: 1908, 1909, 1910, 1911, 1912, 1913, 1914, 1915, 1917
    """)

    # Create output directories
    KG_V3_DIR.mkdir(exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    # Initialize linker
    linker = ProvenanceLinker()

    # Process each year
    available_years = []
    for year in YEARS:
        if (KG_V2_DIR / f"{year}_extracted.json").exists():
            available_years.append(year)

    print(f"Found {len(available_years)} years to process: {available_years}")

    for year in available_years:
        success = linker.process_year(year)
        if not success:
            print(f"  ✗ Failed to process year {year}")

    # Generate report
    print("\nGenerating final report...")
    report = linker.generate_report()

    # Print summary
    print("\n" + "="*60)
    print("PROVENANCE LINKING COMPLETE")
    print("="*60)
    print(f"Years processed: {linker.stats['years_processed']}")
    print(f"Total entities: {linker.stats['entities_processed']:,}")
    print(f"With provenance: {linker.stats['entities_with_provenance']:,}")
    print(f"Coverage: {(linker.stats['entities_with_provenance']/linker.stats['entities_processed']*100):.1f}%")
    print(f"\nHigh confidence: {linker.stats['high_confidence']:,}")
    print(f"Medium confidence: {linker.stats['medium_confidence']:,}")
    print(f"Low confidence: {linker.stats['low_confidence']:,}")
    print(f"Flagged for review: {linker.stats['flagged_for_review']:,}")
    print("\nOutput directory: knowledge_graph_extracts_v3/")
    print(f"Report: reports/phase_b/provenance_1908_1917.md")
    print("="*60)

if __name__ == "__main__":
    main()
