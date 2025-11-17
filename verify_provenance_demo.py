#!/usr/bin/env python3
"""
Demonstration: Using Provenance for Ground Truth Verification

This script shows how to use the provenance information to verify
entity data against source documents.
"""

import json
from pathlib import Path


def demonstrate_ground_truth_verification():
    """Show how to verify an entity against its source."""

    print("="*60)
    print("PROVENANCE GROUND TRUTH VERIFICATION DEMO")
    print("="*60)

    # Load a KG file
    kg_file = "/home/user/colonial_office_list/knowledge_graph_extracts_v3/1950_extracted.json"
    with open(kg_file, 'r') as f:
        kg_data = json.load(f)

    # Get a high-confidence person entity
    people = kg_data["entities"]["people"]
    high_conf_people = [p for p in people if p["provenance"]["extraction_confidence"] >= 0.90]

    if not high_conf_people:
        print("No high-confidence people found")
        return

    # Pick first one
    entity = high_conf_people[0]

    print("\n" + "-"*60)
    print("ENTITY DATA")
    print("-"*60)
    print(f"ID: {entity['id']}")
    print(f"Name: {entity['name']}")
    if entity.get('positions'):
        pos = entity['positions'][0]
        print(f"Position: {pos.get('title', 'N/A')}")
        print(f"Location: {pos.get('location', 'N/A')}")
        if pos.get('salary'):
            print(f"Salary: {pos['salary'].get('currency', '')}{pos['salary'].get('amount', 'N/A')}")

    # Get provenance
    prov = entity["provenance"]

    print("\n" + "-"*60)
    print("PROVENANCE DATA")
    print("-"*60)
    print(f"Source File: {prov['source_file']}")
    print(f"Source Lines: {prov['source_lines']}")
    print(f"Source Section: {prov['source_section']}")
    print(f"Confidence: {prov['extraction_confidence']}")
    print(f"Extraction Agent: {prov['extraction_agent']}")

    # Try to read source file
    source_path = Path("/home/user/colonial_office_list") / prov['source_file']

    if source_path.exists():
        print("\n" + "-"*60)
        print("SOURCE TEXT (Ground Truth)")
        print("-"*60)

        with open(source_path, 'r') as f:
            lines = f.readlines()

        # Parse line numbers (handle various formats)
        line_spec = prov['source_lines']

        if line_spec == "unknown":
            print("Line numbers unknown - cannot display source text")
        else:
            # Show first few lines mentioned
            line_parts = line_spec.split(', ')
            first_range = line_parts[0]

            if '-' in first_range:
                start, end = map(int, first_range.split('-'))
                start = max(1, start)
                end = min(len(lines), end)
            else:
                start = int(first_range)
                end = start

            # Show context (5 lines before and after)
            context_start = max(1, start - 5)
            context_end = min(len(lines), end + 5)

            print(f"\nShowing lines {context_start}-{context_end} (context around {start}-{end}):\n")

            for i in range(context_start-1, context_end):
                line_num = i + 1
                marker = ">>>" if start <= line_num <= end else "   "
                print(f"{marker} {line_num:4}: {lines[i].rstrip()}")
    else:
        print(f"\nWARNING: Source file not found: {source_path}")

    print("\n" + "="*60)
    print("VERIFICATION COMPLETE")
    print("="*60)
    print("\nThis demonstrates how provenance enables:")
    print("- Exact line-level traceability to source documents")
    print("- Verification of extracted data accuracy")
    print("- Quality assessment of extraction process")
    print("- Ground truth analysis for LLM corrections")


def show_statistics():
    """Show statistics about provenance quality."""

    print("\n\n" + "="*60)
    print("PROVENANCE STATISTICS BY ENTITY TYPE")
    print("="*60)

    kg_file = "/home/user/colonial_office_list/knowledge_graph_extracts_v3/1950_extracted.json"
    with open(kg_file, 'r') as f:
        kg_data = json.load(f)

    entity_types = ["places", "people", "institutions", "economic_data",
                   "infrastructure", "demographics", "events"]

    print(f"\nYear: 1950\n")

    for entity_type in entity_types:
        entities = kg_data["entities"].get(entity_type, [])
        if not entities:
            continue

        total = len(entities)
        high_conf = sum(1 for e in entities if e["provenance"]["extraction_confidence"] >= 0.90)
        medium_conf = sum(1 for e in entities if 0.70 <= e["provenance"]["extraction_confidence"] < 0.90)
        low_conf = sum(1 for e in entities if e["provenance"]["extraction_confidence"] < 0.70)

        print(f"{entity_type:20} | Total: {total:4} | High: {high_conf:4} ({high_conf/total*100:5.1f}%) | Med: {medium_conf:3} | Low: {low_conf:2}")


if __name__ == "__main__":
    demonstrate_ground_truth_verification()
    show_statistics()

    print("\n\n" + "="*60)
    print("For more examples, see:")
    print("  /home/user/colonial_office_list/reports/phase_b/provenance_1950_1959.md")
    print("="*60)
