#!/usr/bin/env python3
"""
Build relationships between entities in the knowledge graph.
"""

import json

def build_relationships(kg_file):
    """Add relationships between entities."""

    with open(kg_file, 'r') as f:
        kg = json.load(f)

    relationships = []
    relationship_id = 0

    # Build relationships between people and colonies
    for person in kg['entities']['people']:
        colony = person.get('colony')
        if colony:
            relationships.append({
                "id": f"rel_{relationship_id}",
                "type": "HOLDS_POSITION_IN",
                "source": person['id'],
                "target": f"place_{colony.replace(' ', '_')}",
                "attributes": {
                    "positions": person.get('positions', [])
                }
            })
            relationship_id += 1

    # Build relationships between institutions and colonies
    for inst in kg['entities']['institutions']:
        colony = inst.get('colony')
        if colony:
            relationships.append({
                "id": f"rel_{relationship_id}",
                "type": "LOCATED_IN",
                "source": inst['id'],
                "target": f"place_{colony.replace(' ', '_')}",
                "attributes": {
                    "institution_type": inst.get('type')
                }
            })
            relationship_id += 1

    # Build relationships between economic data and colonies
    for econ in kg['entities']['economic_data']:
        colony = econ.get('colony')
        if colony:
            relationships.append({
                "id": f"rel_{relationship_id}",
                "type": "FINANCIAL_DATA_FOR",
                "source": econ['id'],
                "target": f"place_{colony.replace(' ', '_')}",
                "attributes": {
                    "year": econ.get('year'),
                    "revenue": econ.get('revenue'),
                    "expenditure": econ.get('expenditure')
                }
            })
            relationship_id += 1

    # Build relationships between infrastructure and colonies
    for infra in kg['entities']['infrastructure']:
        colony = infra.get('colony')
        if colony:
            relationships.append({
                "id": f"rel_{relationship_id}",
                "type": "INFRASTRUCTURE_IN",
                "source": infra['id'],
                "target": f"place_{colony.replace(' ', '_')}",
                "attributes": {
                    "infrastructure_type": infra.get('type')
                }
            })
            relationship_id += 1

    # Build relationships between demographics and colonies
    for demo in kg['entities']['demographics']:
        colony = demo.get('colony')
        if colony:
            relationships.append({
                "id": f"rel_{relationship_id}",
                "type": "POPULATION_DATA_FOR",
                "source": demo['id'],
                "target": f"place_{colony.replace(' ', '_')}",
                "attributes": {
                    "year": demo.get('year'),
                    "population": demo.get('total_population')
                }
            })
            relationship_id += 1

    # Build relationships between events and colonies
    for event in kg['entities']['events']:
        colony = event.get('colony')
        if colony:
            relationships.append({
                "id": f"rel_{relationship_id}",
                "type": "EVENT_IN",
                "source": event['id'],
                "target": f"place_{colony.replace(' ', '_')}",
                "attributes": {
                    "year": event.get('year'),
                    "category": event.get('category')
                }
            })
            relationship_id += 1

    # Build relationships between trade data and colonies
    for trade in kg['entities']['trade_data']:
        colony = trade.get('colony')
        if colony:
            relationships.append({
                "id": f"rel_{relationship_id}",
                "type": "TRADE_DATA_FOR",
                "source": trade['id'],
                "target": f"place_{colony.replace(' ', '_')}",
                "attributes": {
                    "year": trade.get('year'),
                    "trade_type": trade.get('type')
                }
            })
            relationship_id += 1

    # Add relationships to knowledge graph
    kg['relationships'] = relationships

    # Save updated knowledge graph
    with open(kg_file, 'w') as f:
        json.dump(kg, f, indent=2, ensure_ascii=False)

    print(f"Built {len(relationships)} relationships")
    return len(relationships)

if __name__ == "__main__":
    kg_file = "/home/user/colonial_office_list/knowledge_graph_extracts/1909_extracted.json"
    count = build_relationships(kg_file)
    print(f"Relationships successfully added to: {kg_file}")
    print(f"Total relationships: {count}")
