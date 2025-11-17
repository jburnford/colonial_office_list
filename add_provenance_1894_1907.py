#!/usr/bin/env python3
"""
Provenance Linking Agent for Colonial Office List Knowledge Graph

This script adds source document provenance to all entities in the knowledge graph
for years 1894-1907. It links each entity back to its source markdown file with
exact line numbers for ground truth analysis.
"""

import json
import os
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional


class ProvenanceLinker:
    """Links KG entities to source documents with line-level provenance."""

    def __init__(self, base_dir: str = "/home/user/colonial_office_list"):
        self.base_dir = Path(base_dir)
        self.kg_v2_dir = self.base_dir / "knowledge_graph_extracts_v2"
        self.kg_v3_dir = self.base_dir / "knowledge_graph_extracts_v3"
        self.source_dir = self.base_dir / "output_2"
        self.extraction_date = datetime.now().strftime("%Y-%m-%d")
        self.extraction_agent = "provenance_linker_1894_1907"

        # Statistics tracking
        self.stats = {
            "years_processed": 0,
            "colonies_processed": 0,
            "entities_with_provenance": 0,
            "entities_without_provenance": 0,
            "total_entities": 0,
            "confidence_distribution": {
                "high_0.95_1.0": 0,
                "good_0.85_0.94": 0,
                "fair_0.70_0.84": 0,
                "low_below_0.70": 0
            },
            "year_details": {}
        }

    def find_source_file(self, year: int, colony_key: str) -> Optional[Path]:
        """Find the source markdown file for a given colony."""
        year_dir = self.source_dir / f"{year}_manual_parsed"
        if not year_dir.exists():
            return None

        # Try direct match first
        md_file = year_dir / f"{colony_key}.md"
        if md_file.exists():
            return md_file

        # Try case variations
        for file in year_dir.glob("*.md"):
            if file.stem.upper() == colony_key.upper():
                return file

        return None

    def read_source_lines(self, source_file: Path) -> List[str]:
        """Read source markdown file into lines."""
        try:
            with open(source_file, 'r', encoding='utf-8', errors='replace') as f:
                return f.readlines()
        except Exception as e:
            print(f"Error reading {source_file}: {e}")
            return []

    def normalize_text(self, text: str) -> str:
        """Normalize text for comparison."""
        # Remove extra whitespace, normalize punctuation
        text = re.sub(r'\s+', ' ', text)
        text = text.strip().lower()
        # Remove common punctuation variations
        text = re.sub(r'[,;:\.\-]', '', text)
        return text

    def find_text_in_source(self, search_text: str, source_lines: List[str],
                           context_window: int = 5) -> Tuple[Optional[str], float]:
        """
        Find text in source file and return line range and confidence.

        Returns:
            Tuple of (line_range_string, confidence_score)
        """
        if not search_text or not source_lines:
            return None, 0.0

        normalized_search = self.normalize_text(str(search_text))

        # Try to find exact matches
        matches = []
        for i, line in enumerate(source_lines, 1):
            normalized_line = self.normalize_text(line)
            if normalized_search in normalized_line:
                matches.append(i)

        if matches:
            # Found exact match
            start = min(matches)
            end = max(matches)
            if start == end:
                return str(start), 0.97
            else:
                return f"{start}-{end}", 0.95

        # Try fuzzy matching with tokens
        search_tokens = set(normalized_search.split())
        if len(search_tokens) < 2:
            # Single word - try substring match
            for i, line in enumerate(source_lines, 1):
                if normalized_search in self.normalize_text(line):
                    return str(i), 0.90
            return None, 0.0

        # Multi-token fuzzy matching
        best_match_line = None
        best_match_score = 0.0

        for i, line in enumerate(source_lines, 1):
            line_tokens = set(self.normalize_text(line).split())
            if not line_tokens:
                continue

            # Calculate Jaccard similarity
            intersection = len(search_tokens & line_tokens)
            union = len(search_tokens | line_tokens)
            similarity = intersection / union if union > 0 else 0

            if similarity > best_match_score and similarity > 0.3:
                best_match_score = similarity
                best_match_line = i

        if best_match_line:
            confidence = 0.70 + (best_match_score * 0.15)  # 0.70-0.85 range
            return str(best_match_line), confidence

        return None, 0.0

    def find_entity_section(self, entity_type: str) -> str:
        """Map entity type to source document section."""
        section_mapping = {
            "geographic_entities": "Situation and Area",
            "location": "Situation and Area",
            "climate": "Climate",
            "population": "Population",
            "demographics": "Population",
            "history": "History",
            "economy": "Economic Information",
            "economic_data": "Economic Information",
            "industries": "Economic Information",
            "natural_resources": "Natural Resources",
            "constitution": "Constitution",
            "government": "Government",
            "officials": "Officials",
            "education": "Education",
            "finances": "Finances",
            "infrastructure": "Infrastructure",
            "events": "History"
        }
        return section_mapping.get(entity_type, "General Information")

    def add_provenance_to_entity(self, entity: Any, source_file: Path,
                                 source_lines: List[str], section: str,
                                 entity_key: str = None) -> Any:
        """Add provenance object to an entity."""
        if entity is None:
            return entity

        if isinstance(entity, dict):
            # Don't add provenance if it already exists
            if "provenance" in entity:
                return entity

            # Find representative text for this entity
            search_texts = []

            # Try to find good search text
            if entity_key:
                search_texts.append(entity_key)

            for key in ["name", "description", "event", "colony_name", "title"]:
                if key in entity and entity[key]:
                    search_texts.append(str(entity[key]))

            # Use first substantial value if no name/description
            if not search_texts:
                for key, value in entity.items():
                    if key != "provenance" and isinstance(value, (str, int, float)):
                        search_texts.append(str(value))
                        break

            # Find in source
            line_range = None
            confidence = 0.75  # Default for metadata-derived

            if search_texts:
                for search_text in search_texts:
                    found_range, found_conf = self.find_text_in_source(search_text, source_lines)
                    if found_range and found_conf > confidence:
                        line_range = found_range
                        confidence = found_conf
                        break

            # Add provenance
            entity["provenance"] = {
                "source_file": f"output_2/{source_file.parent.name}/{source_file.name}",
                "source_lines": line_range if line_range else "metadata",
                "source_section": section,
                "extraction_confidence": round(confidence, 2),
                "extraction_date": self.extraction_date,
                "extraction_agent": self.extraction_agent,
                "verification_status": "automated"
            }

            # Update stats
            self.stats["total_entities"] += 1
            if line_range:
                self.stats["entities_with_provenance"] += 1
            else:
                self.stats["entities_without_provenance"] += 1

            # Confidence distribution
            if confidence >= 0.95:
                self.stats["confidence_distribution"]["high_0.95_1.0"] += 1
            elif confidence >= 0.85:
                self.stats["confidence_distribution"]["good_0.85_0.94"] += 1
            elif confidence >= 0.70:
                self.stats["confidence_distribution"]["fair_0.70_0.84"] += 1
            else:
                self.stats["confidence_distribution"]["low_below_0.70"] += 1

        return entity

    def process_entity_structure(self, data: Any, source_file: Path,
                                 source_lines: List[str], parent_section: str = "",
                                 parent_key: str = None) -> Any:
        """Recursively process entity structure to add provenance."""
        if isinstance(data, dict):
            result = {}
            for key, value in data.items():
                # Determine section for this entity
                section = self.find_entity_section(key) if not parent_section else parent_section

                if isinstance(value, dict) and key not in ["metadata", "provenance"]:
                    # Check if this is an entity (has name, description, etc.) or a container
                    is_entity = any(k in value for k in ["name", "description", "event", "title", "year"])

                    if is_entity:
                        # Add provenance to this entity
                        result[key] = self.add_provenance_to_entity(
                            value, source_file, source_lines, section, key
                        )
                        # Process nested structures
                        for nested_key, nested_value in value.items():
                            if nested_key != "provenance":
                                result[key][nested_key] = self.process_entity_structure(
                                    nested_value, source_file, source_lines, section, nested_key
                                )
                    else:
                        # Container - recurse
                        result[key] = self.process_entity_structure(
                            value, source_file, source_lines, section, key
                        )
                elif isinstance(value, list):
                    # Process list items
                    result[key] = []
                    for item in value:
                        if isinstance(item, dict):
                            # Add provenance to list items that are entities
                            processed_item = self.add_provenance_to_entity(
                                item.copy(), source_file, source_lines, section, key
                            )
                            # Process nested structures in the item
                            for nested_key, nested_value in processed_item.items():
                                if nested_key != "provenance":
                                    processed_item[nested_key] = self.process_entity_structure(
                                        nested_value, source_file, source_lines, section, nested_key
                                    )
                            result[key].append(processed_item)
                        else:
                            result[key].append(item)
                else:
                    # Primitive value
                    result[key] = value
            return result
        elif isinstance(data, list):
            result = []
            for item in data:
                if isinstance(item, dict):
                    processed_item = self.add_provenance_to_entity(
                        item.copy(), source_file, source_lines, parent_section, parent_key
                    )
                    result.append(self.process_entity_structure(
                        processed_item, source_file, source_lines, parent_section, parent_key
                    ))
                else:
                    result.append(item)
            return result
        else:
            return data

    def normalize_colony_name(self, name: str) -> str:
        """Normalize colony name for file lookup."""
        # Convert to uppercase and replace spaces with underscores
        normalized = name.upper().replace(' ', '_')
        # Remove common variations
        normalized = normalized.replace('THE_', '')
        return normalized

    def build_entity_id_to_name_map(self, kg_data: Dict) -> Dict[str, str]:
        """Build a mapping from entity IDs to their names for resolving parent locations."""
        id_map = {}

        if "entities" not in kg_data:
            return id_map

        # Map place IDs to names
        if "places" in kg_data["entities"]:
            for place in kg_data["entities"]["places"]:
                if isinstance(place, dict) and "id" in place and "name" in place:
                    id_map[place["id"]] = place["name"]

        return id_map

    def get_colony_name_from_entity(self, entity: Dict[str, Any], id_map: Dict[str, str]) -> Optional[str]:
        """Extract colony name from an entity."""
        # If it's a colony itself, use its name
        if entity.get("type") == "colony":
            return entity.get("name")

        # If it has a parent_location, resolve it
        if "parent_location" in entity and entity["parent_location"]:
            parent_id = entity["parent_location"]
            if parent_id in id_map:
                return id_map[parent_id]

        # For people, check positions
        if "positions" in entity and isinstance(entity["positions"], list):
            for position in entity["positions"]:
                if isinstance(position, dict) and "location" in position:
                    location_id = position["location"]
                    if location_id in id_map:
                        return id_map[location_id]

        # Fallback: try direct name/colony fields
        for field in ['colony', 'location', 'name']:
            if field in entity and entity[field]:
                value = entity[field]
                # If it's a string, return it
                if isinstance(value, str):
                    return value

        return None

    def process_entity_type_based_structure(self, kg_data: Dict, year: int, year_stats: Dict):
        """Process KG files with entity-type-based structure (entities -> places/people/etc.)"""
        print(f"  Structure: entity-type-based (entities grouped by type)")

        # Build entity ID to name mapping for resolving parent locations
        id_map = self.build_entity_id_to_name_map(kg_data)
        print(f"  Built ID map with {len(id_map)} entries")

        # Track source files we've already loaded
        source_files_cache = {}

        if "entities" in kg_data:
            for entity_type, entities in kg_data["entities"].items():
                if not isinstance(entities, list):
                    continue

                print(f"  Processing {entity_type}: {len(entities)} entities")

                for i, entity in enumerate(entities):
                    if not isinstance(entity, dict):
                        continue

                    # Get colony name from entity
                    colony_name = self.get_colony_name_from_entity(entity, id_map)
                    if not colony_name:
                        # Add metadata-only provenance
                        entity["provenance"] = {
                            "source_file": f"output_2/{year}_manual_parsed/",
                            "source_lines": "metadata",
                            "source_section": self.find_entity_section(entity_type),
                            "extraction_confidence": 0.70,
                            "extraction_date": self.extraction_date,
                            "extraction_agent": self.extraction_agent,
                            "verification_status": "automated"
                        }
                        self.stats["total_entities"] += 1
                        self.stats["entities_without_provenance"] += 1
                        self.stats["confidence_distribution"]["fair_0.70_0.84"] += 1
                        continue

                    # Normalize colony name for file lookup
                    colony_key = self.normalize_colony_name(colony_name)

                    # Load source file if not already cached
                    if colony_key not in source_files_cache:
                        source_file = self.find_source_file(year, colony_key)
                        if source_file:
                            source_lines = self.read_source_lines(source_file)
                            source_files_cache[colony_key] = (source_file, source_lines)
                            year_stats["source_files_found"] += 1
                        else:
                            source_files_cache[colony_key] = None
                            year_stats["source_files_missing"] += 1

                    # Process entity with source file
                    if source_files_cache[colony_key]:
                        source_file, source_lines = source_files_cache[colony_key]
                        section = self.find_entity_section(entity_type)
                        entities[i] = self.add_provenance_to_entity(
                            entity, source_file, source_lines, section, colony_name
                        )
                        # Process nested structures
                        for key, value in entities[i].items():
                            if key != "provenance":
                                entities[i][key] = self.process_entity_structure(
                                    value, source_file, source_lines, section, key
                                )
                    else:
                        # Add metadata-only provenance
                        entity["provenance"] = {
                            "source_file": f"output_2/{year}_manual_parsed/{colony_key}.md",
                            "source_lines": "metadata",
                            "source_section": self.find_entity_section(entity_type),
                            "extraction_confidence": 0.70,
                            "extraction_date": self.extraction_date,
                            "extraction_agent": self.extraction_agent,
                            "verification_status": "automated"
                        }
                        self.stats["total_entities"] += 1
                        self.stats["entities_without_provenance"] += 1
                        self.stats["confidence_distribution"]["fair_0.70_0.84"] += 1

        year_stats["colonies"] = len(source_files_cache)

    def process_colony_based_structure(self, kg_data: Dict, year: int, year_stats: Dict):
        """Process KG files with colony-based structure (colonies -> COLONY_NAME -> data)"""
        print(f"  Structure: colony-based (data grouped by colony)")

        if "colonies" in kg_data:
            for colony_key, colony_data in kg_data["colonies"].items():
                print(f"  Processing colony: {colony_key}")
                year_stats["colonies"] += 1

                # Find source file
                source_file = self.find_source_file(year, colony_key)
                if source_file:
                    print(f"    Source file: {source_file.name}")
                    year_stats["source_files_found"] += 1

                    # Read source lines
                    source_lines = self.read_source_lines(source_file)

                    # Process all entities in this colony
                    kg_data["colonies"][colony_key] = self.process_entity_structure(
                        colony_data, source_file, source_lines
                    )
                else:
                    print(f"    WARNING: Source file not found for {colony_key}")
                    year_stats["source_files_missing"] += 1

    def process_year(self, year: int) -> bool:
        """Process all entities for a given year."""
        print(f"\n{'='*60}")
        print(f"Processing year {year}")
        print(f"{'='*60}")

        # Load KG file
        kg_file = self.kg_v2_dir / f"{year}_extracted.json"
        if not kg_file.exists():
            print(f"KG file not found: {kg_file}")
            return False

        with open(kg_file, 'r', encoding='utf-8') as f:
            kg_data = json.load(f)

        # Initialize year stats
        year_stats = {
            "colonies": 0,
            "entities_processed": 0,
            "entities_with_provenance": 0,
            "source_files_found": 0,
            "source_files_missing": 0
        }

        # Determine structure type and process accordingly
        if "colonies" in kg_data:
            self.process_colony_based_structure(kg_data, year, year_stats)
        elif "entities" in kg_data:
            self.process_entity_type_based_structure(kg_data, year, year_stats)
        else:
            print(f"  WARNING: Unknown KG structure for year {year}")
            print(f"  Top-level keys: {list(kg_data.keys())}")

        # Save enhanced KG file
        output_file = self.kg_v3_dir / f"{year}_extracted.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(kg_data, f, indent=2, ensure_ascii=False)

        print(f"\n  Saved enhanced KG to: {output_file}")
        print(f"  Colonies processed: {year_stats['colonies']}")
        print(f"  Source files found: {year_stats['source_files_found']}")
        print(f"  Source files missing: {year_stats['source_files_missing']}")

        self.stats["years_processed"] += 1
        self.stats["colonies_processed"] += year_stats["colonies"]
        self.stats["year_details"][year] = year_stats

        return True

    def generate_report(self):
        """Generate provenance coverage report."""
        report_path = self.base_dir / "reports/phase_b/provenance_1894_1907.md"

        # Calculate percentages
        total = self.stats["total_entities"]
        with_prov = self.stats["entities_with_provenance"]
        without_prov = self.stats["entities_without_provenance"]

        coverage_pct = (with_prov / total * 100) if total > 0 else 0

        report = f"""# Provenance Linking Report: 1894-1907
## Colonial Office List Knowledge Graph Project

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Agent:** {self.extraction_agent}

---

## Executive Summary

This report documents the automated addition of source document provenance to all entities in the Colonial Office List Knowledge Graph for years 1894-1907. The provenance linking enables ground truth analysis by connecting each extracted entity back to its source document with exact line numbers.

## Overall Statistics

- **Years Processed:** {self.stats['years_processed']}
- **Colonies Processed:** {self.stats['colonies_processed']}
- **Total Entities:** {total:,}
- **Entities with Source Lines:** {with_prov:,} ({coverage_pct:.1f}%)
- **Entities with Metadata Only:** {without_prov:,} ({(without_prov/total*100) if total > 0 else 0:.1f}%)

## Confidence Score Distribution

The confidence scores reflect the quality of the source-to-entity matching:

| Confidence Range | Count | Percentage | Description |
|-----------------|-------|------------|-------------|
| **0.95-1.0** (High) | {self.stats['confidence_distribution']['high_0.95_1.0']:,} | {(self.stats['confidence_distribution']['high_0.95_1.0']/total*100) if total > 0 else 0:.1f}% | Exact text match in source |
| **0.85-0.94** (Good) | {self.stats['confidence_distribution']['good_0.85_0.94']:,} | {(self.stats['confidence_distribution']['good_0.85_0.94']/total*100) if total > 0 else 0:.1f}% | Strong contextual match |
| **0.70-0.84** (Fair) | {self.stats['confidence_distribution']['fair_0.70_0.84']:,} | {(self.stats['confidence_distribution']['fair_0.70_0.84']/total*100) if total > 0 else 0:.1f}% | Inferred from context |
| **< 0.70** (Low) | {self.stats['confidence_distribution']['low_below_0.70']:,} | {(self.stats['confidence_distribution']['low_below_0.70']/total*100) if total > 0 else 0:.1f}% | Metadata-based |

## Year-by-Year Breakdown

"""

        # Add year details
        for year in sorted(self.stats["year_details"].keys()):
            details = self.stats["year_details"][year]
            report += f"""### Year {year}

- **Colonies:** {details['colonies']}
- **Source Files Found:** {details['source_files_found']}
- **Source Files Missing:** {details['source_files_missing']}

"""

        report += f"""## Provenance Schema

Each entity now includes a `provenance` object with the following structure:

```json
{{
  "provenance": {{
    "source_file": "output_2/YYYY_manual_parsed/COLONY_NAME.md",
    "source_lines": "15-28",
    "source_section": "Situation and Area",
    "extraction_confidence": 0.95,
    "extraction_date": "{self.extraction_date}",
    "extraction_agent": "{self.extraction_agent}",
    "verification_status": "automated"
  }}
}}
```

## Output Location

Enhanced knowledge graph files saved to:
- **Directory:** `knowledge_graph_extracts_v3/`
- **Files:** `{{year}}_extracted.json` for each year

## Usage

The provenance information enables:

1. **Ground Truth Verification:** Compare extracted entities against source documents
2. **Quality Assessment:** Confidence scores indicate extraction reliability
3. **Audit Trail:** Track when and how entities were extracted
4. **Source Attribution:** Link back to original historical documents
5. **Error Analysis:** Identify patterns in low-confidence extractions

## Methodology

The provenance linking process:

1. **Text Matching:** Searches for entity data in source markdown files
2. **Confidence Scoring:**
   - Exact match: 0.95-1.0
   - Fuzzy match: 0.85-0.94
   - Contextual inference: 0.70-0.84
   - Metadata-based: < 0.70
3. **Line Number Recording:** Records exact line ranges where entity data appears
4. **Section Mapping:** Maps entities to document sections (History, Geography, etc.)

## Notes

- All existing entity data preserved; only provenance field added
- Missing source files handled gracefully with metadata fallback
- Automated verification status indicates no manual review performed
- Human review recommended for entities with confidence < 0.70

---

**End of Report**
"""

        # Write report
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"\n{'='*60}")
        print(f"Report generated: {report_path}")
        print(f"{'='*60}")
        print(f"\nSummary:")
        print(f"  Total entities processed: {total:,}")
        print(f"  Entities with provenance: {with_prov:,} ({coverage_pct:.1f}%)")
        print(f"  High confidence (≥0.95): {self.stats['confidence_distribution']['high_0.95_1.0']:,}")


def main():
    """Main execution function."""
    # Years to process
    years = [1894, 1896, 1897, 1898, 1899, 1900, 1905, 1906, 1907]

    # Initialize linker
    linker = ProvenanceLinker()

    print("="*60)
    print("PROVENANCE LINKING AGENT")
    print("Colonial Office List Knowledge Graph 1894-1907")
    print("="*60)
    print(f"\nProcessing {len(years)} years...")

    # Process each year
    for year in years:
        try:
            linker.process_year(year)
        except Exception as e:
            print(f"\nERROR processing year {year}: {e}")
            import traceback
            traceback.print_exc()

    # Generate report
    print("\nGenerating coverage report...")
    linker.generate_report()

    print("\n" + "="*60)
    print("PROVENANCE LINKING COMPLETE")
    print("="*60)


if __name__ == "__main__":
    main()
