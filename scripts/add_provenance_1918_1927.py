#!/usr/bin/env python3
"""
Provenance Linking Agent for Colonial Office List Knowledge Graph

Mission: Add source document provenance to all entities in KG files for years 1918-1927.
"""

import json
import os
import re
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
from collections import defaultdict

# Base paths
BASE_DIR = Path("/home/user/colonial_office_list")
KG_V2_DIR = BASE_DIR / "knowledge_graph_extracts_v2"
KG_V3_DIR = BASE_DIR / "knowledge_graph_extracts_v3"
OUTPUT_2_DIR = BASE_DIR / "output_2"
REPORTS_DIR = BASE_DIR / "reports" / "phase_b"

# Processing configuration
YEARS_TO_PROCESS = [1918, 1919, 1921, 1922, 1923, 1924, 1925, 1927]
EXTRACTION_DATE = datetime.now().strftime("%Y-%m-%d")
EXTRACTION_AGENT = "provenance_linker_1918_1927"


def normalize_colony_name(name: str) -> str:
    """Normalize colony names for file matching."""
    # Convert to uppercase and replace spaces with underscores
    normalized = name.upper().replace(" ", "_").replace(".", "")
    # Handle special cases
    replacements = {
        "ST_": "ST.",
        "THE_": "",
    }
    for old, new in replacements.items():
        if normalized.startswith(old):
            normalized = new + normalized[len(old):]
    return normalized


def find_source_file(colony_name: str, source_dir: Path) -> Optional[Path]:
    """Find the markdown source file for a given colony."""
    normalized = normalize_colony_name(colony_name)

    # Try exact match first
    candidate = source_dir / f"{normalized}.md"
    if candidate.exists():
        return candidate

    # Try variations
    variations = [
        colony_name.upper() + ".md",
        colony_name.replace(" ", "_").upper() + ".md",
        colony_name.replace(" ", "_") + ".md",
        colony_name.replace(" ", "") + ".md",
    ]

    for var in variations:
        candidate = source_dir / var
        if candidate.exists():
            return candidate

    return None


def read_file_with_lines(file_path: Path) -> List[Tuple[int, str]]:
    """Read a file and return list of (line_number, line_content) tuples."""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return list(enumerate(f.readlines(), start=1))
    except Exception as e:
        print(f"Error reading {file_path}: {e}")
        return []


def search_text_in_file(search_terms: List[str], file_lines: List[Tuple[int, str]],
                        context_lines: int = 5) -> Tuple[List[int], float]:
    """
    Search for terms in file and return line numbers and confidence score.

    Returns:
        Tuple of (line_numbers, confidence_score)
    """
    if not search_terms or not file_lines:
        return [], 0.0

    found_lines = set()
    matches_found = 0

    for term in search_terms:
        if not term:
            continue

        # Escape special regex characters but keep the term searchable
        escaped_term = re.escape(term)
        pattern = re.compile(escaped_term, re.IGNORECASE)

        for line_num, line_text in file_lines:
            if pattern.search(line_text):
                matches_found += 1
                # Add the line and surrounding context
                for offset in range(-context_lines, context_lines + 1):
                    context_line = line_num + offset
                    if 1 <= context_line <= len(file_lines):
                        found_lines.add(context_line)

    # Calculate confidence based on matches
    if not found_lines:
        return [], 0.0

    # Higher confidence for more matches relative to search terms
    match_ratio = min(matches_found / len(search_terms), 1.0)

    if match_ratio >= 0.8:
        confidence = 0.95  # Exact/strong match
    elif match_ratio >= 0.5:
        confidence = 0.90  # Good match
    elif match_ratio >= 0.3:
        confidence = 0.85  # Moderate match
    else:
        confidence = 0.80  # Weak match

    sorted_lines = sorted(found_lines)
    return sorted_lines, confidence


def format_line_ranges(line_numbers: List[int]) -> str:
    """Convert list of line numbers to compact range format (e.g., '10-15,20,25-27')."""
    if not line_numbers:
        return ""

    ranges = []
    start = line_numbers[0]
    end = line_numbers[0]

    for num in line_numbers[1:]:
        if num == end + 1:
            end = num
        else:
            if start == end:
                ranges.append(str(start))
            else:
                ranges.append(f"{start}-{end}")
            start = end = num

    # Add the last range
    if start == end:
        ranges.append(str(start))
    else:
        ranges.append(f"{start}-{end}")

    return ",".join(ranges)


def extract_search_terms(entity: Dict[str, Any], entity_type: str) -> List[str]:
    """Extract relevant search terms from an entity based on its type."""
    terms = []

    # Always include the name if present
    if "name" in entity:
        terms.append(entity["name"])

    # Type-specific term extraction
    if entity_type == "places":
        if "alternative_names" in entity:
            terms.extend(entity.get("alternative_names", []))
        if "capital" in entity:
            terms.append(entity["capital"])

    elif entity_type == "people":
        # For people, include full name and position
        if "position" in entity:
            terms.append(entity["position"])
        if "title" in entity:
            terms.append(entity["title"])

    elif entity_type == "institutions":
        if "type" in entity:
            terms.append(entity["type"])
        if "functions" in entity:
            if isinstance(entity["functions"], list):
                terms.extend(entity["functions"])
            else:
                terms.append(str(entity["functions"]))

    elif entity_type == "economic_data":
        if "commodity" in entity:
            terms.append(entity["commodity"])
        if "category" in entity:
            terms.append(entity["category"])

    elif entity_type == "infrastructure":
        if "infrastructure_type" in entity:
            terms.append(entity["infrastructure_type"])

    elif entity_type == "demographics":
        if "demographic_type" in entity:
            terms.append(entity["demographic_type"])

    # Filter out empty terms and duplicates
    terms = [t for t in terms if t and isinstance(t, str) and len(t.strip()) > 0]
    return list(set(terms))


def determine_entity_colony(entity: Dict[str, Any], entity_type: str,
                            colonies_list: List[str]) -> Optional[str]:
    """Determine which colony an entity belongs to."""

    # Check explicit colony field
    if "colony" in entity:
        return entity["colony"]

    # For places that ARE colonies
    if entity_type == "places" and entity.get("type") in ["colony", "territory", "protectorate"]:
        return entity.get("name")

    # Check location field
    if "location" in entity:
        location = entity["location"]
        if isinstance(location, str):
            # Check if location matches any colony
            for colony in colonies_list:
                if colony.upper() in location.upper():
                    return colony

    # Check related_to field
    if "related_to" in entity:
        related = entity["related_to"]
        if isinstance(related, str):
            for colony in colonies_list:
                if colony.upper() in related.upper():
                    return colony

    return None


def add_provenance_to_entity(entity: Dict[str, Any], entity_type: str,
                             source_dir: Path, colonies_list: List[str],
                             year: int) -> Dict[str, Any]:
    """Add provenance information to a single entity."""

    # Determine which colony this entity belongs to
    colony = determine_entity_colony(entity, entity_type, colonies_list)

    if not colony:
        # If we can't determine the colony, add minimal provenance
        entity["provenance"] = {
            "source_file": None,
            "source_lines": None,
            "source_section": "Unknown",
            "extraction_confidence": 0.50,
            "extraction_date": EXTRACTION_DATE,
            "extraction_agent": EXTRACTION_AGENT,
            "verification_status": "needs_review",
            "notes": "Could not determine source colony"
        }
        return entity

    # Find the source file
    source_file = find_source_file(colony, source_dir)

    if not source_file:
        entity["provenance"] = {
            "source_file": None,
            "source_lines": None,
            "source_section": colony,
            "extraction_confidence": 0.60,
            "extraction_date": EXTRACTION_DATE,
            "extraction_agent": EXTRACTION_AGENT,
            "verification_status": "source_not_found",
            "notes": f"Source file for {colony} not found"
        }
        return entity

    # Read the source file
    file_lines = read_file_with_lines(source_file)

    # Extract search terms and find in source
    search_terms = extract_search_terms(entity, entity_type)
    line_numbers, confidence = search_text_in_file(search_terms, file_lines)

    # Determine verification status
    if confidence >= 0.90:
        verification_status = "automated"
    elif confidence >= 0.70:
        verification_status = "automated_low_confidence"
    else:
        verification_status = "needs_review"

    # Build relative source file path
    relative_source = str(source_file.relative_to(BASE_DIR))

    # Add provenance
    entity["provenance"] = {
        "source_file": relative_source,
        "source_lines": format_line_ranges(line_numbers) if line_numbers else None,
        "source_section": colony,
        "extraction_confidence": round(confidence, 2),
        "extraction_date": EXTRACTION_DATE,
        "extraction_agent": EXTRACTION_AGENT,
        "verification_status": verification_status
    }

    if not line_numbers:
        entity["provenance"]["notes"] = "Entity terms not found in source file"

    return entity


def process_kg_file(year: int) -> Dict[str, Any]:
    """Process a single KG file and add provenance to all entities."""

    print(f"\n{'='*60}")
    print(f"Processing Year: {year}")
    print(f"{'='*60}")

    # Load the KG file
    kg_file = KG_V2_DIR / f"{year}_extracted.json"

    if not kg_file.exists():
        print(f"ERROR: KG file not found: {kg_file}")
        return {"error": f"File not found: {kg_file}"}

    with open(kg_file, 'r', encoding='utf-8') as f:
        kg_data = json.load(f)

    # Get metadata
    metadata = kg_data.get("metadata", {})
    source_dir_str = metadata.get("source_directory", "")
    source_dir = Path(source_dir_str) if source_dir_str else OUTPUT_2_DIR / f"{year}_manual_parsed"

    colonies_list = metadata.get("colonies_processed", [])

    print(f"Source directory: {source_dir}")
    print(f"Colonies: {len(colonies_list)}")

    if not source_dir.exists():
        print(f"WARNING: Source directory not found: {source_dir}")

    # Process entities
    stats = {
        "total_entities": 0,
        "entities_with_provenance": 0,
        "by_type": defaultdict(lambda: {"total": 0, "with_source": 0, "without_source": 0}),
        "by_confidence": defaultdict(int),
        "by_verification_status": defaultdict(int)
    }

    entities = kg_data.get("entities", {})

    for entity_type in ["places", "people", "institutions", "economic_data",
                       "infrastructure", "demographics", "events"]:

        entity_list = entities.get(entity_type, [])

        if not entity_list:
            continue

        print(f"\nProcessing {len(entity_list)} {entity_type}...")

        for i, entity in enumerate(entity_list):
            stats["total_entities"] += 1
            stats["by_type"][entity_type]["total"] += 1

            # Add provenance
            entity = add_provenance_to_entity(entity, entity_type, source_dir,
                                             colonies_list, year)

            # Update stats
            if "provenance" in entity:
                stats["entities_with_provenance"] += 1

                confidence = entity["provenance"].get("extraction_confidence", 0)
                verification = entity["provenance"].get("verification_status", "unknown")

                if entity["provenance"].get("source_file"):
                    stats["by_type"][entity_type]["with_source"] += 1
                else:
                    stats["by_type"][entity_type]["without_source"] += 1

                # Confidence buckets
                if confidence >= 0.95:
                    stats["by_confidence"]["0.95-1.0"] += 1
                elif confidence >= 0.85:
                    stats["by_confidence"]["0.85-0.94"] += 1
                elif confidence >= 0.70:
                    stats["by_confidence"]["0.70-0.84"] += 1
                else:
                    stats["by_confidence"]["<0.70"] += 1

                stats["by_verification_status"][verification] += 1

            # Update the entity in the list
            entity_list[i] = entity

            # Progress indicator
            if (i + 1) % 50 == 0:
                print(f"  Processed {i + 1}/{len(entity_list)} {entity_type}")

        # Update entities back
        entities[entity_type] = entity_list

    # Update metadata
    metadata["provenance_added"] = True
    metadata["provenance_date"] = EXTRACTION_DATE
    metadata["provenance_agent"] = EXTRACTION_AGENT
    metadata["version"] = "v3"

    kg_data["metadata"] = metadata
    kg_data["entities"] = entities

    # Save the enhanced file
    output_file = KG_V3_DIR / f"{year}_extracted.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(kg_data, f, indent=2, ensure_ascii=False)

    print(f"\n✓ Saved enhanced file: {output_file}")
    print(f"\nStats for {year}:")
    print(f"  Total entities: {stats['total_entities']}")
    print(f"  With provenance: {stats['entities_with_provenance']}")
    print(f"  By confidence:")
    for bucket, count in sorted(stats["by_confidence"].items()):
        print(f"    {bucket}: {count}")
    print(f"  By verification status:")
    for status, count in sorted(stats["by_verification_status"].items()):
        print(f"    {status}: {count}")

    return stats


def generate_report(all_stats: Dict[int, Dict]) -> None:
    """Generate comprehensive provenance report."""

    report_file = REPORTS_DIR / "provenance_1918_1927.md"

    with open(report_file, 'w', encoding='utf-8') as f:
        f.write("# Provenance Linking Report: 1918-1927\n\n")
        f.write(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
        f.write(f"**Agent:** {EXTRACTION_AGENT}\n\n")

        f.write("## Mission\n\n")
        f.write("Add source document provenance to all entities in knowledge graph files ")
        f.write("for years 1918-1927, enabling easy links back to source documents for ")
        f.write("ground truth analysis.\n\n")

        f.write("## Summary\n\n")

        # Overall statistics
        total_entities = sum(stats.get("total_entities", 0) for stats in all_stats.values())
        total_with_prov = sum(stats.get("entities_with_provenance", 0) for stats in all_stats.values())

        f.write(f"- **Years Processed:** {len(all_stats)}\n")
        f.write(f"- **Total Entities:** {total_entities:,}\n")
        f.write(f"- **Entities with Provenance:** {total_with_prov:,}\n")
        f.write(f"- **Coverage:** {(total_with_prov/total_entities*100) if total_entities > 0 else 0:.1f}%\n\n")

        # By year table
        f.write("## Coverage by Year\n\n")
        f.write("| Year | Total Entities | With Provenance | Coverage |\n")
        f.write("|------|----------------|-----------------|----------|\n")

        for year in sorted(all_stats.keys()):
            stats = all_stats[year]
            total = stats.get("total_entities", 0)
            with_prov = stats.get("entities_with_provenance", 0)
            coverage = (with_prov / total * 100) if total > 0 else 0
            f.write(f"| {year} | {total:,} | {with_prov:,} | {coverage:.1f}% |\n")

        f.write("\n")

        # Confidence distribution
        f.write("## Confidence Score Distribution\n\n")
        f.write("| Confidence Range | Count | Percentage |\n")
        f.write("|------------------|-------|------------|\n")

        confidence_totals = defaultdict(int)
        for stats in all_stats.values():
            for bucket, count in stats.get("by_confidence", {}).items():
                confidence_totals[bucket] += count

        total_conf = sum(confidence_totals.values())
        for bucket in ["0.95-1.0", "0.85-0.94", "0.70-0.84", "<0.70"]:
            count = confidence_totals.get(bucket, 0)
            pct = (count / total_conf * 100) if total_conf > 0 else 0
            f.write(f"| {bucket} | {count:,} | {pct:.1f}% |\n")

        f.write("\n")

        # Verification status
        f.write("## Verification Status Distribution\n\n")
        f.write("| Status | Count | Percentage |\n")
        f.write("|--------|-------|------------|\n")

        status_totals = defaultdict(int)
        for stats in all_stats.values():
            for status, count in stats.get("by_verification_status", {}).items():
                status_totals[status] += count

        total_status = sum(status_totals.values())
        for status in sorted(status_totals.keys()):
            count = status_totals[status]
            pct = (count / total_status * 100) if total_status > 0 else 0
            f.write(f"| {status} | {count:,} | {pct:.1f}% |\n")

        f.write("\n")

        # Entity type breakdown
        f.write("## Entity Type Breakdown\n\n")
        f.write("| Entity Type | Total | With Source | Without Source |\n")
        f.write("|-------------|-------|-------------|----------------|\n")

        type_totals = defaultdict(lambda: {"total": 0, "with_source": 0, "without_source": 0})
        for stats in all_stats.values():
            for entity_type, counts in stats.get("by_type", {}).items():
                type_totals[entity_type]["total"] += counts.get("total", 0)
                type_totals[entity_type]["with_source"] += counts.get("with_source", 0)
                type_totals[entity_type]["without_source"] += counts.get("without_source", 0)

        for entity_type in sorted(type_totals.keys()):
            counts = type_totals[entity_type]
            f.write(f"| {entity_type} | {counts['total']:,} | {counts['with_source']:,} | {counts['without_source']:,} |\n")

        f.write("\n")

        # Detailed year-by-year analysis
        f.write("## Detailed Year-by-Year Analysis\n\n")

        for year in sorted(all_stats.keys()):
            stats = all_stats[year]
            f.write(f"### {year}\n\n")

            f.write(f"**Total Entities:** {stats.get('total_entities', 0):,}\n\n")

            f.write("**By Entity Type:**\n\n")
            for entity_type, counts in sorted(stats.get("by_type", {}).items()):
                f.write(f"- {entity_type}: {counts['total']} ")
                f.write(f"({counts['with_source']} with source, {counts['without_source']} without)\n")

            f.write("\n**Confidence Distribution:**\n\n")
            for bucket, count in sorted(stats.get("by_confidence", {}).items()):
                f.write(f"- {bucket}: {count}\n")

            f.write("\n")

        # Recommendations
        f.write("## Recommendations\n\n")

        needs_review = status_totals.get("needs_review", 0)
        if needs_review > 0:
            f.write(f"1. **Manual Review Required:** {needs_review:,} entities flagged for manual review\n")

        low_conf = confidence_totals.get("<0.70", 0)
        if low_conf > 0:
            f.write(f"2. **Low Confidence Entities:** {low_conf:,} entities with confidence < 0.70\n")

        without_source = sum(counts["without_source"] for counts in type_totals.values())
        if without_source > 0:
            f.write(f"3. **Missing Sources:** {without_source:,} entities without source file links\n")

        f.write("\n## Files Generated\n\n")
        f.write("Enhanced KG files saved to: `knowledge_graph_extracts_v3/`\n\n")
        for year in sorted(all_stats.keys()):
            f.write(f"- `{year}_extracted.json`\n")

        f.write("\n---\n\n")
        f.write("*End of Report*\n")

    print(f"\n✓ Report generated: {report_file}")


def main():
    """Main processing function."""

    print("="*70)
    print("PROVENANCE LINKING AGENT: 1918-1927")
    print("="*70)
    print(f"\nProcessing {len(YEARS_TO_PROCESS)} years...")
    print(f"Years: {YEARS_TO_PROCESS}")

    all_stats = {}

    for year in YEARS_TO_PROCESS:
        try:
            stats = process_kg_file(year)
            if "error" not in stats:
                all_stats[year] = stats
        except Exception as e:
            print(f"\nERROR processing {year}: {e}")
            import traceback
            traceback.print_exc()

    # Generate report
    if all_stats:
        print(f"\n{'='*70}")
        print("GENERATING REPORT")
        print(f"{'='*70}")
        generate_report(all_stats)

    print(f"\n{'='*70}")
    print("PROVENANCE LINKING COMPLETE")
    print(f"{'='*70}")
    print(f"\nProcessed {len(all_stats)} years successfully")
    print(f"Enhanced files saved to: {KG_V3_DIR}")
    print(f"Report saved to: {REPORTS_DIR / 'provenance_1918_1927.md'}")


if __name__ == "__main__":
    main()
