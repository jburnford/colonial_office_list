# Toponym Discovery Quick Reference

## Files Created

### Enhanced Knowledge Graphs (v3)
Location: `/home/user/colonial_office_list/knowledge_graph_extracts_v3/`

**Target Years (1918-1927):**
- `1918_extracted_toponyms.json` - 938 places (897 new)
- `1919_extracted_toponyms.json` - 782 places (709 new)  
- `1921_extracted_toponyms.json` - 1,226 places (704 new)
- `1922_extracted_toponyms.json` - 803 places (752 new)
- `1923_extracted_toponyms.json` - 1,171 places (1,130 new)
- `1924_extracted_toponyms.json` - 1,104 places (980 new)
- `1925_extracted_toponyms.json` - 1,014 places (975 new)
- `1927_extracted_toponyms.json` - 989 places (943 new)

**Total: 8,027 place entities (7,090 newly discovered)**

### Reports
- `/home/user/colonial_office_list/reports/phase_c/toponym_discovery_1918_1927.md` - Full discovery report
- `/home/user/colonial_office_list/reports/phase_c/TOPONYM_DISCOVERY_QUICK_REFERENCE.md` - This file

### Scripts
- `/home/user/colonial_office_list/toponym_discovery_agent.py` - Main extraction agent
- `/home/user/colonial_office_list/refine_toponyms.py` - False positive filtering script

## JSON Structure

Each enhanced knowledge graph file contains:

```json
{
  "metadata": {
    "year": "1918",
    "version": "v3_toponym_discovery",
    "toponym_discovery": {
      "existing_places": 41,
      "new_toponyms_discovered": 897,
      "total_places_v3": 938,
      "false_positives_removed": 38
    }
  },
  "entities": {
    "places": [
      {
        "id": "place_0042",
        "name": "Orange River",
        "type": "river",
        "year": "1918",
        "discovery_method": "comprehensive_toponym_scan",
        "mentions": [
          {
            "source_file": "BASUTOLAND",
            "line_number": 42,
            "context": "The climate is good for Europeans..."
          }
        ],
        "mention_count": 22
      }
    ]
  }
}
```

## Toponym Types

- **island** - Islands, archipelagos (e.g., Virgin Islands, Cook Islands)
- **city** - Cities, towns, villages (e.g., St. John, Georgetown)
- **river** - Rivers, waterways (e.g., Orange River, Niger River)
- **mountain** - Mountains, peaks (e.g., Table Mountain, Blue Mountains)
- **harbor** - Harbors, bays, coves (e.g., Montego Bay, Table Bay)
- **district** - Districts, parishes, provinces (e.g., Electoral District)
- **colony** - Colonies, protectorates, territories (e.g., Bechuanaland Protectorate)
- **geographic_feature** - Other features (capes, straits, peninsulas)

## Usage Examples

### Python: Load and Query Toponyms

```python
import json

# Load a year
with open('knowledge_graph_extracts_v3/1923_extracted_toponyms.json') as f:
    data = json.load(f)

# Get all newly discovered places
new_places = [
    p for p in data['entities']['places'] 
    if p.get('discovery_method') == 'comprehensive_toponym_scan'
]

# Find all islands
islands = [p for p in new_places if p['type'] == 'island']
print(f"Found {len(islands)} islands")

# Find high-mention toponyms
high_mention = [
    p for p in new_places 
    if p.get('mention_count', 0) >= 10
]
high_mention.sort(key=lambda x: x['mention_count'], reverse=True)

for place in high_mention[:10]:
    print(f"{place['name']}: {place['mention_count']} mentions")

# Search by name
search_term = "Orange"
matches = [
    p for p in new_places 
    if search_term.lower() in p['name'].lower()
]
```

### Bash: Quick Statistics

```bash
# Count total places per year
for year in 1918 1919 1921 1922 1923 1924 1925 1927; do
  count=$(jq '.entities.places | length' \
    knowledge_graph_extracts_v3/${year}_extracted_toponyms.json)
  echo "$year: $count places"
done

# Find all rivers in 1923
jq '.entities.places[] | select(.type == "river") | .name' \
  knowledge_graph_extracts_v3/1923_extracted_toponyms.json

# Count toponyms by type for 1923
jq '.entities.places[] | select(.discovery_method == "comprehensive_toponym_scan") | .type' \
  knowledge_graph_extracts_v3/1923_extracted_toponyms.json | \
  sort | uniq -c | sort -rn
```

## Key Findings

### Most Discovered Toponym Types
1. **Districts** (1,520 total) - Administrative divisions
2. **Islands** (1,488 total) - Island territories and dependencies
3. **Cities** (1,371 total) - Urban centers and towns
4. **Rivers** (1,230 total) - Major waterways

### Cross-Year Consistency
These toponyms appear in ALL 8 years:
- Orange River (South African boundary)
- St. John / St. John's (Antigua capital)
- St. George (multiple locations)
- Electoral District (administrative divisions)

### Highest Coverage Increase
- **1923:** 2,756.1% increase (41 → 1,171 places)
- **1925:** 2,500.0% increase (39 → 1,014 places)
- **1918:** 2,187.8% increase (41 → 976 places)

## Quality Assurance

### False Positive Removal
- **Total removed:** 302 toponyms (4.1%)
- **Final precision:** 95.9%

### Filtered Terms
- Generic words (The, Town, Colony)
- Administrative titles (Assistant, Officer, Secretary)
- Directional adjectives without proper nouns (Northern, Western)

### Validation Methods
- Cross-year appearance frequency
- Mention count thresholds
- Context verification
- Pattern matching validation

## Next Steps

1. **Relationship Mapping**
   - Link cities to parent colonies
   - Map districts to provinces
   - Connect islands to island groups

2. **Geographic Enrichment**
   - Add latitude/longitude coordinates
   - Link to modern place names
   - Add historical context

3. **Temporal Analysis**
   - Track name changes over time
   - Identify boundary modifications
   - Map territorial transfers

4. **Integration**
   - Merge with existing v2 knowledge graphs
   - Create unified multi-year timeline
   - Build queryable geographic database

## Support

For questions or issues:
- Review full report: `reports/phase_c/toponym_discovery_1918_1927.md`
- Check extraction logs in script output
- Validate against source files in `output_2/{YEAR}_manual_parsed/`

---
**Colonial Office List Knowledge Graph Project**  
**Phase C: Toponym Discovery Agent**  
**November 2025**
