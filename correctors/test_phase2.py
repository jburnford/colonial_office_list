#!/usr/bin/env python3
"""
Comprehensive test of Phase 2 Enum Mapper

Demonstrates all capabilities including:
- Detection of enum errors
- Semantic mapping with confidence scores
- Auto-apply, review, and flagging decisions
- Python validation
"""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))

from correctors.phase2_enum_mapper import EnumMapper


def test_comprehensive():
    """Comprehensive test showing all features"""

    print("=" * 80)
    print("COMPREHENSIVE PHASE 2 ENUM MAPPER TEST")
    print("=" * 80)
    print()

    mapper = EnumMapper()

    # Test on a file with enum errors
    test_file = "/home/user/colonial_office_list/knowledge_graph_extracts/1877_extracted.json"

    print(f"Testing on: {test_file}")
    print(f"Mode: Rule-based mapping (LLM-ready)")
    print()

    # Process in dry-run mode
    result = mapper.process_file(test_file, dry_run=True)

    print("\n" + "=" * 80)
    print("RESULTS SUMMARY")
    print("=" * 80)
    print()
    print(f"Total enum errors found: {result.get('total_enum_errors', 0)}")
    print(f"Auto-applied (≥90% confidence): {len(result.get('auto_applied', []))}")
    print(f"Review queue (70-90% confidence): {len(result.get('review_queue', []))}")
    print(f"Flagged (<70% confidence): {len(result.get('flagged', []))}")
    print()

    # Show auto-apply decisions
    if result.get('auto_applied'):
        print("\n" + "-" * 80)
        print("AUTO-APPLY DECISIONS (High Confidence ≥90%)")
        print("-" * 80)
        for i, mapping in enumerate(result['auto_applied'][:5], 1):
            print(f"\n{i}. '{mapping['original_value']}' → '{mapping['recommended_value']}'")
            print(f"   Confidence: {mapping['confidence']:.2f}")
            print(f"   Entity: {mapping['entity_name'] or 'N/A'} ({mapping['year'] or 'N/A'})")
            print(f"   Reasoning: {mapping['reasoning']}")

    # Show review queue
    if result.get('review_queue'):
        print("\n" + "-" * 80)
        print("REVIEW QUEUE (Medium Confidence 70-90%)")
        print("-" * 80)
        for i, mapping in enumerate(result['review_queue'][:5], 1):
            print(f"\n{i}. '{mapping['original_value']}' → '{mapping['recommended_value']}'")
            print(f"   Confidence: {mapping['confidence']:.2f}")
            print(f"   Entity: {mapping['entity_name'] or 'N/A'} ({mapping['year'] or 'N/A'})")
            print(f"   Reasoning: {mapping['reasoning']}")

    # Show flagged items
    if result.get('flagged'):
        print("\n" + "-" * 80)
        print("FLAGGED FOR HUMAN REVIEW (Low Confidence <70%)")
        print("-" * 80)
        for i, mapping in enumerate(result['flagged'][:5], 1):
            print(f"\n{i}. '{mapping['original_value']}' → '{mapping['recommended_value']}'")
            print(f"   Confidence: {mapping['confidence']:.2f}")
            print(f"   Entity: {mapping['entity_name'] or 'N/A'} ({mapping['year'] or 'N/A'})")
            print(f"   Reasoning: {mapping['reasoning']}")

    # Breakdown by confidence
    print("\n" + "=" * 80)
    print("CONFIDENCE DISTRIBUTION")
    print("=" * 80)

    all_mappings = (
        result.get('auto_applied', []) +
        result.get('review_queue', []) +
        result.get('flagged', [])
    )

    if all_mappings:
        confidences = [m['confidence'] for m in all_mappings]
        avg_confidence = sum(confidences) / len(confidences)

        high = len([c for c in confidences if c >= 0.9])
        medium = len([c for c in confidences if 0.7 <= c < 0.9])
        low = len([c for c in confidences if c < 0.7])

        print(f"\nAverage confidence: {avg_confidence:.2f}")
        print(f"High confidence (≥0.90): {high} ({high/len(confidences)*100:.1f}%)")
        print(f"Medium confidence (0.70-0.89): {medium} ({medium/len(confidences)*100:.1f}%)")
        print(f"Low confidence (<0.70): {low} ({low/len(confidences)*100:.1f}%)")

    print("\n" + "=" * 80)
    print("MAPPING TYPES")
    print("=" * 80)

    # Group by enum type
    type_counts = {}
    for mapping in all_mappings:
        field = mapping.get('field_path', '')
        if 'relationship_type' in field:
            enum_type = "RelationshipType"
        elif 'institutions' in field and 'type' in field:
            enum_type = "InstitutionType"
        elif 'places' in field and 'type' in field:
            enum_type = "PlaceType"
        else:
            enum_type = "Other"

        type_counts[enum_type] = type_counts.get(enum_type, 0) + 1

    for enum_type, count in sorted(type_counts.items(), key=lambda x: -x[1]):
        print(f"  {enum_type}: {count}")

    print("\n" + "=" * 80)
    print("VALIDATION FEATURES")
    print("=" * 80)
    print("""
This implementation includes:

✓ LLM-powered semantic understanding (when API key available)
✓ Rule-based fallback with historical knowledge
✓ Confidence scoring (0-1 scale)
✓ Three-tier decision making:
  - Auto-apply (≥90% confidence)
  - Review queue (70-90% confidence)
  - Flag for human review (<70% confidence)
✓ Python validation before/after changes
✓ Automatic rollback if validation worsens
✓ Detailed logging of all decisions
✓ Context-aware mapping using entity name, description, year

To enable full LLM mode:
  export ANTHROPIC_API_KEY=your_key_here
  python correctors/phase2_enum_mapper.py --file <path> --apply
    """)

    # Save detailed results
    output_file = "/home/user/colonial_office_list/reports/phase2_test_results.json"
    with open(output_file, 'w') as f:
        json.dump(result, f, indent=2)

    print(f"\nDetailed results saved to: {output_file}")
    print("\n" + "=" * 80)


if __name__ == "__main__":
    test_comprehensive()
