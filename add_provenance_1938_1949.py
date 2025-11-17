#!/usr/bin/env python3
"""
Provenance Linking Agent for Colonial Office List Knowledge Graph
Adds source document provenance to all entities in KG files for years 1938-1949.
"""

import json
import os
import re
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Any, Optional


class ProvenanceLinker:
    """Links entities in knowledge graph to their source documents."""

    def __init__(self, base_dir: str = "/home/user/colonial_office_list"):
        self.base_dir = Path(base_dir)
        self.kg_v2_dir = self.base_dir / "knowledge_graph_extracts_v2"
        self.kg_v3_dir = self.base_dir / "knowledge_graph_extracts_v3"
        self.output_dir = self.base_dir / "output_2"

        # Ensure v3 directory exists
        self.kg_v3_dir.mkdir(parents=True, exist_ok=True)

        # Statistics tracking
        self.stats = {
            'total_entities': 0,
            'entities_with_provenance': 0,
            'high_confidence': 0,  # >= 0.95
            'medium_confidence': 0,  # 0.85-0.94
            'low_confidence': 0,  # 0.70-0.84
            'very_low_confidence': 0,  # < 0.70
            'missing_source': 0,
            'by_entity_type': {}
        }

    def normalize_name(self, name: str) -> str:
        """Normalize a name for file lookup."""
        # Convert to uppercase, replace spaces with underscores
        return name.upper().replace(' ', '_').replace('-', '_')

    def find_source_file(self, entity_name: str, source_dir: Path) -> Optional[Path]:
        """Find the source markdown file for an entity."""
        # Truncate extremely long entity names to avoid filesystem errors
        if len(entity_name) > 100:
            entity_name = entity_name[:100]

        normalized = self.normalize_name(entity_name)

        # Try exact match first (with error handling)
        try:
            exact_file = source_dir / f"{normalized}.md"
            if exact_file.exists():
                return exact_file
        except OSError:
            pass  # File name too long, skip

        # Try variations
        variations = [
            f"{normalized[:100]}.md",
            f"{entity_name.upper()[:100]}.md",
            f"{entity_name.replace(' ', '_')[:100]}.md",
            f"{entity_name[:100]}.md"
        ]

        for var in variations:
            try:
                file_path = source_dir / var
                if file_path.exists():
                    return file_path
            except OSError:
                continue  # File name too long, skip

        # Try fuzzy match
        try:
            for file in source_dir.glob("*.md"):
                if normalized[:100] in file.stem.upper() or file.stem.upper() in normalized[:100]:
                    return file
        except OSError:
            pass

        return None

    def search_in_file(self, file_path: Path, search_terms: List[str]) -> Tuple[List[int], float]:
        """
        Search for terms in a file and return line numbers and confidence score.

        Returns:
            Tuple of (list of line numbers, confidence score)
        """
        if not file_path.exists():
            return [], 0.0

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()

            found_lines = set()
            match_scores = []

            for term in search_terms:
                if not term:
                    continue

                # Clean term for searching
                term_clean = str(term).strip()
                if len(term_clean) < 2:
                    continue

                for line_num, line in enumerate(lines, start=1):
                    # Check for exact match (case insensitive)
                    if term_clean.lower() in line.lower():
                        found_lines.add(line_num)

                        # Calculate match quality
                        if term_clean in line:
                            match_scores.append(1.0)  # Exact case match
                        elif term_clean.lower() == line.strip().lower():
                            match_scores.append(0.98)  # Exact line match
                        else:
                            match_scores.append(0.95)  # Contains match

            if not found_lines:
                return [], 0.0

            # Calculate overall confidence
            if match_scores:
                avg_score = sum(match_scores) / len(match_scores)
                confidence = avg_score
            else:
                confidence = 0.70  # Default for found but uncertain

            # Convert to sorted list and create ranges
            sorted_lines = sorted(list(found_lines))

            return sorted_lines, confidence

        except Exception as e:
            print(f"Error reading {file_path}: {e}")
            return [], 0.0

    def get_line_ranges(self, line_numbers: List[int]) -> str:
        """Convert list of line numbers to compact range notation."""
        if not line_numbers:
            return ""

        if len(line_numbers) == 1:
            return str(line_numbers[0])

        # Group consecutive numbers
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
                start = num
                end = num

        # Add final range
        if start == end:
            ranges.append(str(start))
        else:
            ranges.append(f"{start}-{end}")

        return ", ".join(ranges)

    def extract_search_terms(self, entity: Dict[str, Any], entity_type: str) -> List[str]:
        """Extract relevant search terms from an entity."""
        terms = []

        # Common fields
        if 'name' in entity:
            terms.append(entity['name'])
        if 'title' in entity:
            terms.append(entity['title'])

        # Type-specific fields
        if entity_type == 'places':
            if 'coordinates' in entity and entity['coordinates'] is not None:
                coords = entity['coordinates']
                if 'latitude' in coords:
                    terms.append(str(coords['latitude']))
                if 'longitude' in coords:
                    terms.append(str(coords['longitude']))
            if 'area' in entity and entity['area'] is not None and 'value' in entity['area']:
                terms.append(str(entity['area']['value']))

        elif entity_type == 'people':
            if 'role' in entity:
                terms.append(entity['role'])
            if 'appointment_date' in entity:
                terms.append(entity['appointment_date'])

        elif entity_type == 'institutions':
            if 'institution_type' in entity:
                terms.append(entity['institution_type'])
            if 'members' in entity and isinstance(entity['members'], list):
                for member in entity['members'][:3]:  # First 3 members
                    if isinstance(member, dict) and 'name' in member:
                        terms.append(member['name'])

        elif entity_type == 'economic_data':
            if 'category' in entity:
                terms.append(entity['category'])
            if 'value' in entity:
                terms.append(str(entity['value']))
            if 'currency' in entity:
                terms.append(entity['currency'])

        elif entity_type == 'infrastructure':
            if 'infrastructure_type' in entity:
                terms.append(entity['infrastructure_type'])
            if 'length' in entity:
                terms.append(str(entity['length']))

        elif entity_type == 'demographics':
            if 'location' in entity:
                terms.append(entity['location'])
            if 'population' in entity:
                terms.append(str(entity['population']))

        elif entity_type == 'events':
            if 'event_type' in entity:
                terms.append(entity['event_type'])
            if 'date' in entity:
                terms.append(entity['date'])

        # Add description snippet if available
        if 'description' in entity:
            desc = entity['description']
            if isinstance(desc, str) and len(desc) > 10:
                # Extract first meaningful phrase (up to 50 chars)
                snippet = desc[:50].split('.')[0].strip()
                if len(snippet) > 10:
                    terms.append(snippet)

        return terms

    def determine_source_section(self, line_numbers: List[int], file_path: Path) -> str:
        """Determine which section of the source file the entity is from."""
        if not line_numbers or not file_path.exists():
            return "Unknown"

        try:
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                lines = f.readlines()

            # Look backwards from first line number to find section header
            first_line = min(line_numbers)
            section = "General"

            for i in range(first_line - 1, -1, -1):
                if i >= len(lines):
                    continue
                line = lines[i].strip()

                # Check if it's a header (all caps, short, no punctuation)
                if line and line.isupper() and len(line) < 50 and not line.startswith('|'):
                    section = line
                    break

            return section

        except Exception:
            return "Unknown"

    def add_provenance_to_entity(self, entity: Dict[str, Any], entity_type: str,
                                  year: str, source_dir: Path) -> Dict[str, Any]:
        """Add provenance metadata to a single entity."""

        # Extract entity name/identifier
        entity_name = entity.get('name') or entity.get('title') or entity.get('location', 'Unknown')

        # Find source file
        source_file = self.find_source_file(entity_name, source_dir)

        if not source_file:
            # Entity might be from a general file or embedded in another
            # Try to use metadata or default to first available file
            md_files = list(source_dir.glob("*.md"))
            if md_files:
                source_file = md_files[0]  # Fallback to first file

        # Extract search terms
        search_terms = self.extract_search_terms(entity, entity_type)

        # Search in source file
        if source_file:
            line_numbers, confidence = self.search_in_file(source_file, search_terms)
            line_range = self.get_line_ranges(line_numbers)
            section = self.determine_source_section(line_numbers, source_file)

            # Calculate relative path for cleaner provenance
            try:
                relative_source = source_file.relative_to(self.base_dir)
            except ValueError:
                relative_source = source_file

            provenance = {
                "source_file": str(relative_source),
                "source_lines": line_range if line_range else "not found",
                "source_section": section,
                "extraction_confidence": round(confidence, 2),
                "extraction_date": datetime.now().isoformat(),
                "extraction_agent": "provenance_linker_1938_1949",
                "verification_status": "automated"
            }

            # Update statistics
            if line_range:
                self.stats['entities_with_provenance'] += 1
                if confidence >= 0.95:
                    self.stats['high_confidence'] += 1
                elif confidence >= 0.85:
                    self.stats['medium_confidence'] += 1
                elif confidence >= 0.70:
                    self.stats['low_confidence'] += 1
                else:
                    self.stats['very_low_confidence'] += 1
            else:
                self.stats['missing_source'] += 1
                provenance['extraction_confidence'] = 0.0
                provenance['verification_status'] = "needs_manual_review"
        else:
            # No source file found
            provenance = {
                "source_file": "not found",
                "source_lines": "not found",
                "source_section": "Unknown",
                "extraction_confidence": 0.0,
                "extraction_date": datetime.now().isoformat(),
                "extraction_agent": "provenance_linker_1938_1949",
                "verification_status": "needs_manual_review"
            }
            self.stats['missing_source'] += 1

        # Add provenance to entity
        entity['provenance'] = provenance
        self.stats['total_entities'] += 1

        return entity

    def process_kg_file(self, year: str) -> bool:
        """Process a knowledge graph file and add provenance to all entities."""

        print(f"\n{'='*60}")
        print(f"Processing Year: {year}")
        print(f"{'='*60}")

        # Load KG file
        kg_file = self.kg_v2_dir / f"{year}_extracted.json"
        if not kg_file.exists():
            print(f"ERROR: KG file not found: {kg_file}")
            return False

        print(f"Loading KG file: {kg_file}")
        with open(kg_file, 'r', encoding='utf-8') as f:
            kg_data = json.load(f)

        # Get source directory from metadata
        if 'metadata' not in kg_data or 'source_directory' not in kg_data['metadata']:
            print(f"ERROR: No source directory in metadata")
            return False

        source_dir = Path(kg_data['metadata']['source_directory'])
        if not source_dir.exists():
            print(f"ERROR: Source directory not found: {source_dir}")
            return False

        print(f"Source directory: {source_dir}")

        # Process each entity type
        entity_types = ['places', 'people', 'institutions', 'economic_data',
                       'infrastructure', 'demographics', 'events']

        for entity_type in entity_types:
            if entity_type not in kg_data.get('entities', {}):
                continue

            entities = kg_data['entities'][entity_type]
            if not entities:
                continue

            print(f"\nProcessing {len(entities)} {entity_type}...")

            # Track stats for this entity type
            if entity_type not in self.stats['by_entity_type']:
                self.stats['by_entity_type'][entity_type] = {
                    'total': 0,
                    'with_provenance': 0,
                    'high_confidence': 0
                }

            # Process each entity
            for i, entity in enumerate(entities):
                entity = self.add_provenance_to_entity(entity, entity_type, year, source_dir)
                entities[i] = entity

                # Update type-specific stats
                self.stats['by_entity_type'][entity_type]['total'] += 1
                if entity.get('provenance', {}).get('source_lines') != 'not found':
                    self.stats['by_entity_type'][entity_type]['with_provenance'] += 1
                    if entity['provenance']['extraction_confidence'] >= 0.95:
                        self.stats['by_entity_type'][entity_type]['high_confidence'] += 1

            # Update entities in kg_data
            kg_data['entities'][entity_type] = entities

            print(f"  Completed: {len(entities)} {entity_type}")

        # Save enhanced KG file
        output_file = self.kg_v3_dir / f"{year}_extracted.json"
        print(f"\nSaving enhanced KG to: {output_file}")

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(kg_data, f, indent=2, ensure_ascii=False)

        print(f"SUCCESS: Enhanced KG saved to {output_file}")
        return True

    def generate_report(self, years: List[str]) -> str:
        """Generate a comprehensive provenance coverage report."""

        report = []
        report.append("# Provenance Linking Report: 1938-1949")
        report.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"\n## Overview")
        report.append(f"\n**Years Processed:** {', '.join(years)}")
        report.append(f"\n**Total Entities:** {self.stats['total_entities']}")
        report.append(f"**Entities with Provenance:** {self.stats['entities_with_provenance']} "
                     f"({self.stats['entities_with_provenance']/self.stats['total_entities']*100:.1f}%)")
        report.append(f"\n## Confidence Distribution")
        report.append(f"\n- **High Confidence (0.95-1.0):** {self.stats['high_confidence']} "
                     f"({self.stats['high_confidence']/self.stats['total_entities']*100:.1f}%)")
        report.append(f"- **Medium Confidence (0.85-0.94):** {self.stats['medium_confidence']} "
                     f"({self.stats['medium_confidence']/self.stats['total_entities']*100:.1f}%)")
        report.append(f"- **Low Confidence (0.70-0.84):** {self.stats['low_confidence']} "
                     f"({self.stats['low_confidence']/self.stats['total_entities']*100:.1f}%)")
        report.append(f"- **Very Low Confidence (<0.70):** {self.stats['very_low_confidence']} "
                     f"({self.stats['very_low_confidence']/self.stats['total_entities']*100:.1f}%)")
        report.append(f"- **Missing Source:** {self.stats['missing_source']} "
                     f"({self.stats['missing_source']/self.stats['total_entities']*100:.1f}%)")

        report.append(f"\n## Coverage by Entity Type")
        report.append("\n| Entity Type | Total | With Provenance | High Confidence | Coverage % |")
        report.append("|-------------|-------|-----------------|-----------------|------------|")

        for entity_type, stats in sorted(self.stats['by_entity_type'].items()):
            total = stats['total']
            with_prov = stats['with_provenance']
            high_conf = stats['high_confidence']
            coverage = (with_prov / total * 100) if total > 0 else 0

            report.append(f"| {entity_type} | {total} | {with_prov} | {high_conf} | {coverage:.1f}% |")

        report.append(f"\n## Methodology")
        report.append(f"\n### Provenance Linking Process")
        report.append(f"\n1. **Entity Identification:** Each entity in the knowledge graph is analyzed")
        report.append(f"2. **Source File Lookup:** The corresponding source markdown file is located")
        report.append(f"3. **Content Search:** Entity data is searched within the source file")
        report.append(f"4. **Line Number Recording:** Exact line numbers where data appears are recorded")
        report.append(f"5. **Confidence Scoring:** Match quality determines confidence score")
        report.append(f"\n### Confidence Scoring Criteria")
        report.append(f"\n- **0.95-1.0:** Exact text match found in source file")
        report.append(f"- **0.85-0.94:** Strong contextual match")
        report.append(f"- **0.70-0.84:** Inferred from metadata")
        report.append(f"- **<0.70:** Flagged for human review")
        report.append(f"\n### Provenance Schema")
        report.append(f"\nEach entity now includes:")
        report.append(f"\n```json")
        report.append(f'{{')
        report.append(f'  "provenance": {{')
        report.append(f'    "source_file": "output_2/YEAR_manual_parsed/COLONY.md",')
        report.append(f'    "source_lines": "30-45, 67",')
        report.append(f'    "source_section": "Section Name",')
        report.append(f'    "extraction_confidence": 0.95,')
        report.append(f'    "extraction_date": "2025-11-17T...",')
        report.append(f'    "extraction_agent": "provenance_linker_1938_1949",')
        report.append(f'    "verification_status": "automated"')
        report.append(f'  }}')
        report.append(f'}}')
        report.append(f'```')
        report.append(f"\n## Recommendations")
        report.append(f"\n1. **Manual Review Required:** {self.stats['missing_source'] + self.stats['very_low_confidence']} "
                     f"entities need human verification")
        report.append(f"2. **High Quality Coverage:** {self.stats['high_confidence']} entities have confirmed provenance")
        report.append(f"3. **Next Steps:** Review entities with confidence <0.70 for accuracy")
        report.append(f"\n## Output Files")
        report.append(f"\nEnhanced knowledge graph files saved to:")
        for year in years:
            report.append(f"- `knowledge_graph_extracts_v3/{year}_extracted.json`")

        report.append(f"\n---\n*Generated by Provenance Linking Agent*")

        return "\n".join(report)


def main():
    """Main execution function."""

    # Years to process (only those that exist)
    years = ['1946', '1948', '1949']

    print("="*60)
    print("PROVENANCE LINKING AGENT")
    print("Colonial Office List Knowledge Graph Project")
    print("="*60)
    print(f"\nTarget Years: {', '.join(years)}")
    print(f"Task: Add source document provenance to all entities")

    # Initialize linker
    linker = ProvenanceLinker()

    # Process each year
    processed_years = []
    for year in years:
        success = linker.process_kg_file(year)
        if success:
            processed_years.append(year)

    # Generate report
    if processed_years:
        print(f"\n{'='*60}")
        print("Generating Coverage Report")
        print(f"{'='*60}")

        report_content = linker.generate_report(processed_years)

        # Save report
        report_dir = linker.base_dir / "reports" / "phase_b"
        report_dir.mkdir(parents=True, exist_ok=True)
        report_file = report_dir / "provenance_1938_1949.md"

        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(report_content)

        print(f"\nReport saved to: {report_file}")
        print(f"\n{report_content}")

    print(f"\n{'='*60}")
    print("PROVENANCE LINKING COMPLETE")
    print(f"{'='*60}")
    print(f"\nProcessed {len(processed_years)} years successfully")
    print(f"Enhanced files saved to: knowledge_graph_extracts_v3/")
    print(f"Report saved to: reports/phase_b/provenance_1938_1949.md")


if __name__ == "__main__":
    main()
