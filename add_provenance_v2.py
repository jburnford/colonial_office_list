#!/usr/bin/env python3
"""
Provenance Linking Agent V2 - Enhanced with cross-file search
Adds source document provenance to all entities, including those without colony fields.
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

class ProvenanceLinkerV2:
    def __init__(self):
        self.stats = {
            "years_processed": 0,
            "entities_processed": 0,
            "entities_with_provenance": 0,
            "high_confidence": 0,
            "medium_confidence": 0,
            "low_confidence": 0,
            "flagged_for_review": 0,
            "cross_file_matches": 0,
            "errors": [],
            "year_stats": {}
        }
        self.file_cache = {}  # Cache file contents

    def normalize_filename(self, colony_name: str) -> str:
        """Convert colony name to expected filename format."""
        if not colony_name:
            return None
        filename = colony_name.strip().upper()
        filename = filename.replace(" ", "_")
        filename = filename.replace(".", "")
        filename = filename.replace(",", "")
        filename = filename.replace("'", "")
        filename = re.sub(r'[^\w_]', '', filename)
        return f"{filename}.md"

    def load_file_with_cache(self, filepath: Path) -> List[str]:
        """Load file contents with caching."""
        if str(filepath) in self.file_cache:
            return self.file_cache[str(filepath)]

        if not filepath.exists():
            return []

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            self.file_cache[str(filepath)] = lines
            return lines
        except:
            return []

    def find_text_in_file(self, filepath: Path, search_text: str) -> Tuple[Optional[str], float]:
        """Find text in source file and return line numbers."""
        lines = self.load_file_with_cache(filepath)
        if not lines:
            return None, 0.0

        clean_search = search_text.strip()[:200]

        # Strategy 1: Exact match
        for i, line in enumerate(lines):
            if clean_search in line:
                return f"{i+1}", 0.98

        # Strategy 2: Multi-word match
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

        # Strategy 3: Key term match
        if "," in clean_search:
            key_term = clean_search.split(",")[0].strip()
            for i, line in enumerate(lines):
                if key_term in line:
                    return f"{i+1}", 0.80

        return None, 0.0

    def search_all_files(self, source_dir: Path, search_text: str) -> Tuple[Optional[str], Optional[str], float]:
        """Search across all markdown files in directory. Returns (filename, line_numbers, confidence)."""
        if not search_text or len(search_text) < 5:
            return None, None, 0.0

        md_files = list(source_dir.glob("*.md"))

        best_match = None
        best_confidence = 0.0
        best_file = None

        for md_file in md_files:
            line_numbers, confidence = self.find_text_in_file(md_file, search_text)
            if confidence > best_confidence:
                best_confidence = confidence
                best_match = line_numbers
                best_file = md_file.name

        if best_match:
            self.stats["cross_file_matches"] += 1
            return best_file, best_match, best_confidence

        return None, None, 0.0

    def get_source_section(self, entity: Dict) -> str:
        """Determine the source section from entity metadata."""
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
            colony = entity.get("location", entity.get("place", ""))

        # Get search text
        source_text = entity.get("source_text", entity.get("name", entity.get("description", "")))

        if not source_text or len(source_text) < 3:
            # Can't search without text
            return entity

        filename = None
        line_numbers = None
        confidence = 0.0

        # Try direct colony lookup first
        if colony:
            filename = self.normalize_filename(colony)
            if filename:
                source_file = source_dir / filename
                line_numbers, confidence = self.find_text_in_file(source_file, source_text)

        # If no match, search all files
        if line_numbers is None:
            filename, line_numbers, confidence = self.search_all_files(source_dir, source_text)

        # Last resort: use metadata boundaries
        if line_numbers is None and metadata and "colonies" in metadata and colony:
            colony_filename = self.normalize_filename(colony)
            for col_info in metadata["colonies"]:
                if col_info["filename"] == colony_filename:
                    filename = colony_filename
                    line_numbers = f"{col_info['start_line']}-{col_info['end_line']}"
                    confidence = 0.70
                    break

        # If still no match, skip this entity
        if not filename or not line_numbers:
            return entity

        relative_source = f"output_2/{year}_manual_parsed/{filename}"

        # Add provenance
        entity["provenance"] = {
            "source_file": relative_source,
            "source_lines": line_numbers,
            "source_section": self.get_source_section(entity),
            "extraction_confidence": confidence,
            "extraction_date": datetime.now().strftime("%Y-%m-%d"),
            "extraction_agent": "provenance_linker_v2_1908_1917",
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

        # Clear cache for new year
        self.file_cache = {}

        kg_file = KG_V2_DIR / f"{year}_extracted.json"
        if not kg_file.exists():
            print(f"  WARNING: KG file not found: {kg_file}")
            self.stats["errors"].append(f"{year}: KG file not found")
            return False

        print(f"  Loading KG file: {kg_file}")
        with open(kg_file, 'r', encoding='utf-8') as f:
            kg_data = json.load(f)

        metadata_file = OUTPUT2_DIR / f"{year}_manual_parsed.json"
        metadata = None
        if metadata_file.exists():
            print(f"  Loading metadata: {metadata_file}")
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)

        source_dir = OUTPUT2_DIR / f"{year}_manual_parsed"
        if not source_dir.exists():
            print(f"  ERROR: Source directory not found: {source_dir}")
            self.stats["errors"].append(f"{year}: Source directory not found")
            return False

        print(f"  Source directory: {source_dir}")
        print(f"  Pre-loading {len(list(source_dir.glob('*.md')))} source files...")

        # Pre-load all source files
        for md_file in source_dir.glob("*.md"):
            self.load_file_with_cache(md_file)

        year_entity_count = 0
        year_provenance_count = 0
        entities = kg_data.get("entities", {})

        for entity_type in ENTITY_TYPES:
            if entity_type not in entities:
                continue

            entity_list = entities[entity_type]
            if len(entity_list) == 0:
                continue

            print(f"  Processing {len(entity_list)} {entity_type}...")

            for i, entity in enumerate(entity_list):
                self.stats["entities_processed"] += 1
                year_entity_count += 1

                entities[entity_type][i] = self.add_provenance_to_entity(
                    entity, year, metadata, source_dir
                )

                if "provenance" in entities[entity_type][i]:
                    year_provenance_count += 1

                if (i + 1) % 500 == 0:
                    print(f"    Processed {i+1}/{len(entity_list)} {entity_type}...")

        output_file = KG_V3_DIR / f"{year}_extracted.json"
        print(f"\n  Saving enhanced KG to: {output_file}")
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(kg_data, f, indent=2, ensure_ascii=False)

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
        report_file = REPORTS_DIR / "provenance_1908_1917_v2.md"

        total_prov = self.stats['entities_with_provenance']
        total_ent = self.stats['entities_processed']

        report = f"""# Provenance Linking Report V2: 1908-1917
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
Agent: provenance_linker_v2 (Enhanced with cross-file search)

## Summary Statistics

- **Years Processed**: {self.stats['years_processed']} / {len([y for y in YEARS if (KG_V2_DIR / f"{y}_extracted.json").exists()])}
- **Total Entities Processed**: {total_ent:,}
- **Entities with Provenance**: {total_prov:,}
- **Overall Coverage**: {(total_prov/total_ent*100):.1f}%
- **Cross-File Matches**: {self.stats['cross_file_matches']:,} (entities found via full-text search)

## Confidence Distribution

| Confidence Level | Count | Percentage |
|-----------------|-------|------------|
| High (0.95-1.0) | {self.stats['high_confidence']:,} | {(self.stats['high_confidence']/total_prov*100):.1f}% |
| Medium (0.85-0.94) | {self.stats['medium_confidence']:,} | {(self.stats['medium_confidence']/total_prov*100):.1f}% |
| Low (0.70-0.84) | {self.stats['low_confidence']:,} | {(self.stats['low_confidence']/total_prov*100):.1f}% |
| Flagged for Review (<0.70) | {self.stats['flagged_for_review']:,} | {(self.stats['flagged_for_review']/total_prov*100):.1f}% |

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
## Improvements in V2

1. **Cross-File Search**: When colony field is missing, searches all source files
2. **Better Text Matching**: Enhanced multi-strategy text search
3. **File Caching**: Pre-loads all source files for faster processing
4. **Broader Coverage**: Can link entities without explicit colony assignments

## Provenance Schema

Each entity now includes a `provenance` object:

```json
{{
  "provenance": {{
    "source_file": "output_2/YYYY_manual_parsed/COLONY_NAME.md",
    "source_lines": "120-145",
    "source_section": "Government Officials",
    "extraction_confidence": 0.95,
    "extraction_date": "2025-11-17",
    "extraction_agent": "provenance_linker_v2_1908_1917",
    "verification_status": "automated"
  }}
}}
```

## Confidence Scoring Methodology

- **0.95-1.0**: Exact text match found in source file
- **0.85-0.94**: Strong contextual match (3+ keywords matched)
- **0.70-0.84**: Inferred from metadata or 2 keywords matched
- **< 0.70**: Flagged for human review

## Next Steps

1. Validate sample entities from each year
2. Review flagged entities (confidence < 0.70)
3. Use provenance for ground truth validation
4. Extend to remaining years

## Output

Enhanced KG files: `knowledge_graph_extracts_v3/`
"""

        print(f"\n{'='*60}")
        print(f"Saving report to: {report_file}")
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)

def main():
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║    PROVENANCE LINKING AGENT V2: 1908-1917                    ║
║    Enhanced with Cross-File Search                           ║
╚══════════════════════════════════════════════════════════════╝

Mission: Add source document provenance to ALL entities
Features: Cross-file search, better text matching, file caching
    """)

    KG_V3_DIR.mkdir(exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    linker = ProvenanceLinkerV2()

    available_years = [y for y in YEARS if (KG_V2_DIR / f"{y}_extracted.json").exists()]
    print(f"Found {len(available_years)} years to process: {available_years}")

    for year in available_years:
        linker.process_year(year)

    linker.generate_report()

    print("\n" + "="*60)
    print("PROVENANCE LINKING V2 COMPLETE")
    print("="*60)
    print(f"Years processed: {linker.stats['years_processed']}")
    print(f"Total entities: {linker.stats['entities_processed']:,}")
    print(f"With provenance: {linker.stats['entities_with_provenance']:,}")
    print(f"Coverage: {(linker.stats['entities_with_provenance']/linker.stats['entities_processed']*100):.1f}%")
    print(f"Cross-file matches: {linker.stats['cross_file_matches']:,}")
    print(f"\nHigh confidence: {linker.stats['high_confidence']:,}")
    print(f"Medium confidence: {linker.stats['medium_confidence']:,}")
    print(f"Low confidence: {linker.stats['low_confidence']:,}")
    print(f"Flagged: {linker.stats['flagged_for_review']:,}")
    print("\nOutput: knowledge_graph_extracts_v3/")
    print("="*60)

if __name__ == "__main__":
    main()
