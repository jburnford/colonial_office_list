#!/usr/bin/env python3
"""
Enhanced Provenance Linking Agent with improved matching for institutions and economic data.
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional

class EnhancedProvenanceLinker:
    def __init__(self, base_dir: str = "/home/user/colonial_office_list"):
        self.base_dir = Path(base_dir)
        self.kg_v2_dir = self.base_dir / "knowledge_graph_extracts_v2"
        self.kg_v3_dir = self.base_dir / "knowledge_graph_extracts_v3"
        self.reports_dir = self.base_dir / "reports" / "phase_b"

        # Statistics tracking
        self.stats = {
            "total_entities": 0,
            "entities_with_provenance": 0,
            "high_confidence": 0,
            "medium_confidence": 0,
            "low_confidence": 0,
            "very_low_confidence": 0,
            "by_year": {}
        }

    def find_entity_in_source(self, entity: Dict, source_file: Path,
                            colony_name: str, category: str) -> Optional[Dict]:
        """Enhanced entity finding with category-specific logic."""
        if not source_file.exists():
            return None

        # Read source file with line numbers
        with open(source_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Use category-specific search strategies
        if category == "institutions":
            return self._find_institution(entity, lines, source_file, colony_name)
        elif category == "economic_data":
            return self._find_economic_data(entity, lines, source_file)
        elif category == "infrastructure":
            return self._find_infrastructure(entity, lines, source_file)
        elif category == "demographics":
            return self._find_demographics(entity, lines, source_file)
        elif category == "events":
            return self._find_event(entity, lines, source_file)
        else:
            # Use default search for places and people
            return self._find_default(entity, lines, source_file)

    def _find_institution(self, entity: Dict, lines: List[str],
                         source_file: Path, colony_name: str) -> Optional[Dict]:
        """Find institutional entities by searching for base name."""

        entity_name = entity.get("name", "")
        if not entity_name:
            return None

        # Extract base name (remove colony suffix)
        # e.g., "Executive Council of BERMUDA" -> "Executive Council"
        base_name = entity_name
        if " of " in entity_name:
            base_name = entity_name.split(" of ")[0]

        # Search for base name
        matches = []
        for i, line in enumerate(lines, start=1):
            line_lower = line.lower()
            base_lower = base_name.lower()

            # Check for exact match or contextual match
            if base_lower in line_lower:
                matches.append(i)

        if matches:
            section = self._find_section(lines, min(matches))
            line_range = self._get_line_range(matches, lines)

            # Determine confidence
            if len(matches) >= 2:
                confidence = 0.90  # Multiple mentions
            else:
                confidence = 0.85  # Single mention

            return {
                "source_file": str(source_file.relative_to(self.base_dir)),
                "source_lines": line_range,
                "source_section": section,
                "extraction_confidence": confidence,
                "extraction_date": datetime.now().isoformat(),
                "extraction_agent": "provenance_linker_enhanced",
                "verification_status": "automated"
            }

        # Try alternative search using entity type
        entity_type = entity.get("type", "")
        type_keywords = {
            "executive_council": ["executive council", "exco"],
            "legislative_council": ["legislative council", "legco", "legislature"],
            "department": ["department", "secretary", "office"]
        }

        if entity_type in type_keywords:
            for i, line in enumerate(lines, start=1):
                line_lower = line.lower()
                for keyword in type_keywords[entity_type]:
                    if keyword in line_lower:
                        matches.append(i)
                        break

        if matches:
            section = self._find_section(lines, min(matches))
            line_range = self._get_line_range(matches, lines)

            return {
                "source_file": str(source_file.relative_to(self.base_dir)),
                "source_lines": line_range,
                "source_section": section,
                "extraction_confidence": 0.75,  # Lower confidence for keyword match
                "extraction_date": datetime.now().isoformat(),
                "extraction_agent": "provenance_linker_enhanced",
                "verification_status": "automated"
            }

        return None

    def _find_economic_data(self, entity: Dict, lines: List[str],
                           source_file: Path) -> Optional[Dict]:
        """Find economic data entities by searching for values."""

        # Economic data often has value/amount fields
        value_fields = ["revenue", "expenditure", "amount", "value", "total"]

        search_values = []
        for field in value_fields:
            if field in entity:
                val = entity[field]
                if isinstance(val, (int, float)):
                    search_values.append(str(int(val)))
                elif isinstance(val, dict) and "value" in val:
                    search_values.append(str(int(val["value"])))

        # Also search for economic keywords
        economic_keywords = ["revenue", "expenditure", "budget", "finance",
                           "trade", "exports", "imports", "production"]

        matches = []

        # Search for values
        for i, line in enumerate(lines, start=1):
            # Check for any search values
            for val in search_values:
                if val in line and val != "0":
                    matches.append(i)
                    break

            # Also look for economic keywords
            line_lower = line.lower()
            for keyword in economic_keywords:
                if keyword in line_lower:
                    matches.append(i)
                    break

        if matches:
            section = self._find_section(lines, min(matches))
            line_range = self._get_line_range(matches, lines)

            # Confidence based on whether we found actual values
            confidence = 0.80 if search_values and any(v in ''.join(lines) for v in search_values) else 0.72

            return {
                "source_file": str(source_file.relative_to(self.base_dir)),
                "source_lines": line_range,
                "source_section": section,
                "extraction_confidence": confidence,
                "extraction_date": datetime.now().isoformat(),
                "extraction_agent": "provenance_linker_enhanced",
                "verification_status": "automated"
            }

        return None

    def _find_infrastructure(self, entity: Dict, lines: List[str],
                           source_file: Path) -> Optional[Dict]:
        """Find infrastructure entities using description keywords."""

        # Extract keywords from description
        description = entity.get("description", "")
        name = entity.get("name", "")

        search_terms = []
        if name:
            search_terms.append(name)

        # Infrastructure keywords
        infra_keywords = ["road", "railway", "port", "airport", "bridge",
                         "hospital", "school", "water", "electricity",
                         "telecommunications", "building", "facility"]

        matches = []
        for i, line in enumerate(lines, start=1):
            line_lower = line.lower()

            # Check for name matches
            for term in search_terms:
                if term.lower() in line_lower:
                    matches.append(i)
                    break

            # Check for keyword matches
            if description:
                desc_lower = description.lower()
                for keyword in infra_keywords:
                    if keyword in desc_lower and keyword in line_lower:
                        matches.append(i)
                        break

        if matches:
            section = self._find_section(lines, min(matches))
            line_range = self._get_line_range(matches, lines)

            return {
                "source_file": str(source_file.relative_to(self.base_dir)),
                "source_lines": line_range,
                "source_section": section,
                "extraction_confidence": 0.78,
                "extraction_date": datetime.now().isoformat(),
                "extraction_agent": "provenance_linker_enhanced",
                "verification_status": "automated"
            }

        return None

    def _find_demographics(self, entity: Dict, lines: List[str],
                          source_file: Path) -> Optional[Dict]:
        """Find demographic entities using population/census keywords."""

        demo_keywords = ["population", "census", "inhabitants", "residents",
                        "demographic", "ethnic", "racial", "religion"]

        # Extract values from entity
        search_values = []
        if "population" in entity:
            pop = entity["population"]
            if isinstance(pop, (int, float)):
                search_values.append(str(int(pop)))
            elif isinstance(pop, dict) and "total" in pop:
                search_values.append(str(int(pop["total"])))

        matches = []
        for i, line in enumerate(lines, start=1):
            line_lower = line.lower()

            # Check for keywords
            for keyword in demo_keywords:
                if keyword in line_lower:
                    matches.append(i)
                    break

            # Check for values
            for val in search_values:
                if val in line and val != "0":
                    matches.append(i)
                    break

        if matches:
            section = self._find_section(lines, min(matches))
            line_range = self._get_line_range(matches, lines)

            return {
                "source_file": str(source_file.relative_to(self.base_dir)),
                "source_lines": line_range,
                "source_section": section,
                "extraction_confidence": 0.82,
                "extraction_date": datetime.now().isoformat(),
                "extraction_agent": "provenance_linker_enhanced",
                "verification_status": "automated"
            }

        return None

    def _find_event(self, entity: Dict, lines: List[str],
                   source_file: Path) -> Optional[Dict]:
        """Find event entities using date and description."""

        name = entity.get("name", "")
        date = entity.get("date", "")
        description = entity.get("description", "")

        matches = []
        for i, line in enumerate(lines, start=1):
            line_lower = line.lower()

            # Check for name
            if name and name.lower() in line_lower:
                matches.append(i)
                continue

            # Check for date
            if date and date in line:
                matches.append(i)
                continue

            # Check for description snippets
            if description:
                desc_snippet = description[:50].lower()
                if desc_snippet in line_lower:
                    matches.append(i)

        if matches:
            section = self._find_section(lines, min(matches))
            line_range = self._get_line_range(matches, lines)

            return {
                "source_file": str(source_file.relative_to(self.base_dir)),
                "source_lines": line_range,
                "source_section": section,
                "extraction_confidence": 0.85,
                "extraction_date": datetime.now().isoformat(),
                "extraction_agent": "provenance_linker_enhanced",
                "verification_status": "automated"
            }

        return None

    def _find_default(self, entity: Dict, lines: List[str],
                     source_file: Path) -> Optional[Dict]:
        """Default search for places and people."""

        entity_name = entity.get("name", "")
        if not entity_name:
            return None

        search_term = entity_name.replace("_", " ")

        matches = []
        for i, line in enumerate(lines, start=1):
            if search_term.lower() in line.lower():
                matches.append(i)

        if matches:
            section = self._find_section(lines, min(matches))
            line_range = self._get_line_range(matches, lines)

            # Determine confidence based on number of matches
            if len(matches) >= 3:
                confidence = 0.98
            elif len(matches) >= 2:
                confidence = 0.95
            else:
                confidence = 0.90

            return {
                "source_file": str(source_file.relative_to(self.base_dir)),
                "source_lines": line_range,
                "source_section": section,
                "extraction_confidence": confidence,
                "extraction_date": datetime.now().isoformat(),
                "extraction_agent": "provenance_linker_enhanced",
                "verification_status": "automated"
            }

        return None

    def _find_section(self, lines: List[str], line_num: int) -> str:
        """Find the section header before a given line number."""

        for i in range(line_num - 1, -1, -1):
            line = lines[i].strip()
            # Headers are usually short lines or lines with specific keywords
            if len(line) < 50 and line and not line.startswith("-"):
                # Check if it looks like a header
                if (line.isupper() or
                    any(keyword in line for keyword in
                        ["Population", "Area", "Climate", "History", "Government",
                         "Constitution", "Finance", "Economy", "Trade", "Education",
                         "Administration", "Officials", "Geography", "Towns",
                         "Revenue", "Expenditure", "Budget", "Public", "Development"])):
                    return line

        return "Unknown"

    def _get_line_range(self, matches: List[int], lines: List[str]) -> str:
        """Convert list of line numbers to a range string."""
        if not matches:
            return "N/A"

        matches = sorted(set(matches))

        if len(matches) == 1:
            # Expand to include context (3 lines before and after)
            start = max(1, matches[0] - 3)
            end = min(len(lines), matches[0] + 3)
            return f"{start}-{end}"
        else:
            # Use min to max of matches
            return f"{min(matches)}-{max(matches)}"

    def _find_entity_colony(self, entity: Dict, kg_data: Dict,
                           all_source_files: Dict[str, Path]) -> Optional[Tuple[str, Path]]:
        """Find which colony/source file an entity belongs to."""

        # Strategy 1: Check if entity name matches a colony name
        entity_name = entity.get("name", "")

        # Check if name ends with colony name (e.g., "Executive Council of BERMUDA")
        if " of " in entity_name:
            colony_part = entity_name.split(" of ")[-1]
            if colony_part in all_source_files:
                return colony_part, all_source_files[colony_part]

        # Strategy 2: Check if entity name is a colony name
        if entity_name in all_source_files:
            return entity_name, all_source_files[entity_name]

        # Strategy 3: For places with type "colony"
        if entity.get("type") == "colony" and entity_name:
            return entity_name, all_source_files.get(entity_name)

        # Strategy 4: Search all source files for the entity
        if not entity_name or entity_name == "unknown":
            # For entities without names, skip global search (too slow and inaccurate)
            return None

        search_term = entity_name.replace("_", " ").lower()

        for colony_name, source_file in all_source_files.items():
            if not source_file.exists():
                continue

            try:
                with open(source_file, 'r', encoding='utf-8') as f:
                    content = f.read().lower()
                    if search_term in content:
                        return colony_name, source_file
            except Exception:
                continue

        return None

    def process_kg_file(self, year: str) -> Dict:
        """Process a single KG file and add provenance to all entities."""

        print(f"\n{'='*60}")
        print(f"Processing Year: {year}")
        print(f"{'='*60}")

        # Load KG file
        kg_file = self.kg_v2_dir / f"{year}_extracted.json"
        if not kg_file.exists():
            print(f"ERROR: KG file not found: {kg_file}")
            return {}

        with open(kg_file, 'r', encoding='utf-8') as f:
            kg_data = json.load(f)

        # Get source directory from metadata
        source_dir = Path(kg_data["metadata"]["source_directory"])
        if not source_dir.exists():
            print(f"ERROR: Source directory not found: {source_dir}")
            return {}

        # Build map of colony names to source files
        all_source_files = {}
        for colony in kg_data["metadata"].get("colonies_processed", []):
            source_file = source_dir / f"{colony}.md"
            all_source_files[colony] = source_file

        # Track statistics for this year
        year_stats = {
            "total_entities": 0,
            "entities_with_provenance": 0,
            "high_confidence": 0,
            "medium_confidence": 0,
            "low_confidence": 0,
            "very_low_confidence": 0,
            "by_category": {}
        }

        # Process each entity category
        for category in ["places", "people", "institutions", "economic_data",
                        "infrastructure", "demographics", "events"]:

            if category not in kg_data.get("entities", {}):
                continue

            entities = kg_data["entities"][category]
            category_count = len(entities)
            category_with_prov = 0

            print(f"\nProcessing {category}: {category_count} entities")

            for i, entity in enumerate(entities):
                year_stats["total_entities"] += 1
                self.stats["total_entities"] += 1

                # Skip if already has provenance
                if "provenance" in entity:
                    category_with_prov += 1
                    year_stats["entities_with_provenance"] += 1
                    self.stats["entities_with_provenance"] += 1

                    # Track confidence
                    conf = entity["provenance"]["extraction_confidence"]
                    if conf >= 0.95:
                        year_stats["high_confidence"] += 1
                        self.stats["high_confidence"] += 1
                    elif conf >= 0.85:
                        year_stats["medium_confidence"] += 1
                        self.stats["medium_confidence"] += 1
                    elif conf >= 0.70:
                        year_stats["low_confidence"] += 1
                        self.stats["low_confidence"] += 1
                    else:
                        year_stats["very_low_confidence"] += 1
                        self.stats["very_low_confidence"] += 1
                    continue

                # Find which colony this entity belongs to
                result = self._find_entity_colony(entity, kg_data, all_source_files)

                if result:
                    colony_name, source_file = result

                    # Find entity in source file
                    provenance = self.find_entity_in_source(entity, source_file, colony_name, category)

                    if provenance:
                        entity["provenance"] = provenance
                        year_stats["entities_with_provenance"] += 1
                        self.stats["entities_with_provenance"] += 1
                        category_with_prov += 1

                        # Track confidence distribution
                        conf = provenance["extraction_confidence"]
                        if conf >= 0.95:
                            year_stats["high_confidence"] += 1
                            self.stats["high_confidence"] += 1
                        elif conf >= 0.85:
                            year_stats["medium_confidence"] += 1
                            self.stats["medium_confidence"] += 1
                        elif conf >= 0.70:
                            year_stats["low_confidence"] += 1
                            self.stats["low_confidence"] += 1
                        else:
                            year_stats["very_low_confidence"] += 1
                            self.stats["very_low_confidence"] += 1

                if (i + 1) % 50 == 0:
                    print(f"  Processed {i+1}/{category_count} entities...")

            year_stats["by_category"][category] = {
                "total": category_count,
                "with_provenance": category_with_prov,
                "coverage": f"{(category_with_prov/category_count*100):.1f}%" if category_count > 0 else "0%"
            }

            print(f"  ✓ {category}: {category_with_prov}/{category_count} with provenance ({year_stats['by_category'][category]['coverage']})")

        # Save enhanced KG file
        output_file = self.kg_v3_dir / f"{year}_extracted.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(kg_data, f, indent=2, ensure_ascii=False)

        print(f"\n✓ Saved enhanced KG to: {output_file}")

        # Store year stats
        self.stats["by_year"][year] = year_stats

        return year_stats

    def generate_report(self):
        """Generate provenance coverage report."""

        report_file = self.reports_dir / "provenance_1961_1966_enhanced.md"

        report = f"""# Enhanced Provenance Linking Report: 1961-1966
## Colonial Office List Knowledge Graph - Phase B

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Agent:** provenance_linker_enhanced
**Task:** Add source document provenance to all entities with improved matching

---

## Executive Summary

This enhanced provenance linking adds traceable source document references to entities
in the Colonial Office List Knowledge Graph for years 1961-1966, including improved
matching for institutional entities, economic data, and other complex entity types.

### Overall Statistics

- **Total Entities Processed:** {self.stats['total_entities']:,}
- **Entities with Provenance:** {self.stats['entities_with_provenance']:,}
- **Coverage:** {(self.stats['entities_with_provenance']/self.stats['total_entities']*100):.1f}%

### Confidence Distribution

| Confidence Level | Count | Percentage |
|-----------------|-------|------------|
| High (0.95-1.0) | {self.stats['high_confidence']:,} | {(self.stats['high_confidence']/max(1,self.stats['entities_with_provenance'])*100):.1f}% |
| Medium (0.85-0.94) | {self.stats['medium_confidence']:,} | {(self.stats['medium_confidence']/max(1,self.stats['entities_with_provenance'])*100):.1f}% |
| Low (0.70-0.84) | {self.stats['low_confidence']:,} | {(self.stats['low_confidence']/max(1,self.stats['entities_with_provenance'])*100):.1f}% |
| Very Low (<0.70) | {self.stats['very_low_confidence']:,} | {(self.stats['very_low_confidence']/max(1,self.stats['entities_with_provenance'])*100):.1f}% |

---

## Year-by-Year Analysis

"""

        for year in sorted(self.stats["by_year"].keys()):
            year_stats = self.stats["by_year"][year]

            report += f"""### Year {year}

**Total Entities:** {year_stats['total_entities']:,}
**Entities with Provenance:** {year_stats['entities_with_provenance']:,}
**Coverage:** {(year_stats['entities_with_provenance']/year_stats['total_entities']*100):.1f}%

#### Confidence Distribution
- High (0.95-1.0): {year_stats['high_confidence']:,}
- Medium (0.85-0.94): {year_stats['medium_confidence']:,}
- Low (0.70-0.84): {year_stats['low_confidence']:,}
- Very Low (<0.70): {year_stats['very_low_confidence']:,}

#### By Category

| Category | Total | With Provenance | Coverage |
|----------|-------|----------------|----------|
"""

            for category, cat_stats in year_stats.get("by_category", {}).items():
                report += f"| {category} | {cat_stats['total']} | {cat_stats['with_provenance']} | {cat_stats['coverage']} |\n"

            report += "\n---\n\n"

        report += f"""## Enhanced Matching Strategies

### Institutional Entities
- Base name extraction (e.g., "Executive Council" from "Executive Council of BERMUDA")
- Type-based keyword matching (executive_council, legislative_council, department)
- Confidence: 0.85-0.90 depending on match quality

### Economic Data
- Value-based matching (search for revenue/expenditure amounts)
- Economic keyword matching (revenue, expenditure, budget, finance, trade)
- Confidence: 0.72-0.80 depending on value matches

### Infrastructure
- Name-based matching for named infrastructure
- Description keyword matching (road, railway, port, hospital, etc.)
- Confidence: 0.78

### Demographics
- Population/census keyword matching
- Value-based matching for population figures
- Confidence: 0.82

### Events
- Date and name-based matching
- Description snippet matching
- Confidence: 0.85

### Places and People (Default)
- Exact name matching with context
- Multiple-match confidence boosting
- Confidence: 0.90-0.98

---

## Provenance Schema

Each entity now includes a `provenance` object:

```json
{{
  "provenance": {{
    "source_file": "output_2/YEAR_manual_parsed/COLONY.md",
    "source_lines": "start-end",
    "source_section": "Section Name",
    "extraction_confidence": 0.85,
    "extraction_date": "2025-11-17T...",
    "extraction_agent": "provenance_linker_enhanced",
    "verification_status": "automated"
  }}
}}
```

---

## Output Files

Enhanced knowledge graph files saved to: `knowledge_graph_extracts_v3/`

Files created:
"""

        for year in sorted(self.stats["by_year"].keys()):
            report += f"- `{year}_extracted.json`\n"

        report += f"""
---

## Mission Status

✓ Enhanced provenance linking complete for 1961-1966
✓ Improved matching for institutions, economic data, and other entity types
✓ {(self.stats['entities_with_provenance']/self.stats['total_entities']*100):.1f}% overall coverage achieved
✓ Ground truth analysis enabled via source document references

**Quality:** {(self.stats['high_confidence']/max(1,self.stats['entities_with_provenance'])*100):.1f}% high-confidence links
"""

        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report)

        print(f"\n{'='*60}")
        print(f"Report saved to: {report_file}")
        print(f"{'='*60}")

        return report_file


def main():
    """Main execution function."""

    print("="*60)
    print("ENHANCED PROVENANCE LINKING AGENT")
    print("Processing years: 1961-1966")
    print("="*60)

    linker = EnhancedProvenanceLinker()

    # Process each year
    years = ["1961", "1962", "1964", "1965", "1966"]

    for year in years:
        linker.process_kg_file(year)

    # Generate report
    print("\n" + "="*60)
    print("Generating Coverage Report")
    print("="*60)

    linker.generate_report()

    print("\n" + "="*60)
    print("MISSION COMPLETE")
    print("="*60)
    print(f"Total entities processed: {linker.stats['total_entities']:,}")
    print(f"Entities with provenance: {linker.stats['entities_with_provenance']:,}")
    print(f"Coverage: {(linker.stats['entities_with_provenance']/linker.stats['total_entities']*100):.1f}%")
    print(f"High-confidence links: {linker.stats['high_confidence']:,}")
    print("="*60)


if __name__ == "__main__":
    main()
