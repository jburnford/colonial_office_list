#!/usr/bin/env python3
"""
Refine toponym extractions by filtering false positives
"""

import json
from pathlib import Path
from collections import defaultdict

# Extended exclusion list for false positives
FALSE_POSITIVES = {
    'The', 'Assistant', 'Colony', 'Town', 'Cape', 'District', 'Parish',
    'Island', 'River', 'Mountain', 'Harbor', 'Harbour', 'Bay', 'North',
    'South', 'East', 'West', 'Northern', 'Southern', 'Eastern', 'Western',
    'Central', 'Upper', 'Lower', 'New', 'Old', 'Great', 'Little', 'Big',
    'Chief', 'First', 'Second', 'Third', 'Fourth', 'Fifth',
    'Medical', 'Officer', 'Secretary', 'Governor', 'Commissioner',
    'Inspector', 'Superintendent', 'Director', 'Manager', 'Agent',
    'President', 'Chairman', 'Member', 'Clerk', 'Treasurer',
    'Council', 'Court', 'Office', 'Department', 'Board', 'Commission',
    'Company', 'Corporation', 'Society', 'Association', 'Club',
    'Church', 'School', 'College', 'University', 'Hospital', 'Prison',
    'Police', 'Military', 'Naval', 'Army', 'Navy', 'Force', 'Regiment',
    'Treasury', 'Customs', 'Post', 'Telegraph', 'Railway', 'Works',
    'Public', 'Private', 'Local', 'Federal', 'National', 'Imperial',
    'Acting', 'Deputy', 'Junior', 'Senior', 'Head', 'Sub',
}

# Common partial place names that need parent context
PARTIAL_NAMES = {
    'John', 'George', 'Louis', 'Vincent', 'Lucia', 'Helena', 'Kitts',
    'James', 'Thomas', 'Andrew', 'Peter', 'Paul', 'Michael',
}

def refine_toponyms(year: int):
    """Refine toponyms for a specific year"""
    base_dir = Path("/home/user/colonial_office_list")
    file_path = base_dir / "knowledge_graph_extracts_v3" / f"{year}_extracted_toponyms.json"
    
    with open(file_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    # Get places
    places = data['entities']['places']
    
    # Separate existing and new places
    existing_places = [p for p in places if p.get('discovery_method') != 'comprehensive_toponym_scan']
    new_places = [p for p in places if p.get('discovery_method') == 'comprehensive_toponym_scan']
    
    print(f"\nYear {year}:")
    print(f"  Existing places: {len(existing_places)}")
    print(f"  New toponyms before filtering: {len(new_places)}")
    
    # Filter new places
    filtered_places = []
    removed_count = defaultdict(int)
    
    for place in new_places:
        name = place['name']
        
        # Check if it's a false positive
        if name in FALSE_POSITIVES:
            removed_count['false_positive'] += 1
            continue
        
        # Check if it's a partial name (St. John, St. George, etc.)
        # These should only be kept if they have "St." or "Saint" prefix in context
        if name in PARTIAL_NAMES:
            # Check contexts for St./Saint prefix
            has_prefix = False
            if place.get('mentions'):
                for mention in place['mentions']:
                    context = mention.get('context', '')
                    if f'St. {name}' in context or f'Saint {name}' in context or f'St.{name}' in context:
                        has_prefix = True
                        break
            
            if not has_prefix:
                removed_count['partial_name'] += 1
                continue
        
        # Keep if it passes filters
        filtered_places.append(place)
    
    print(f"  Removed - false positives: {removed_count['false_positive']}")
    print(f"  Removed - partial names: {removed_count['partial_name']}")
    print(f"  New toponyms after filtering: {len(filtered_places)}")
    
    # Combine existing and filtered new places
    all_places = existing_places + filtered_places
    
    # Update data
    data['entities']['places'] = all_places
    data['metadata']['toponym_discovery']['new_toponyms_discovered'] = len(filtered_places)
    data['metadata']['toponym_discovery']['total_places_v3'] = len(all_places)
    data['metadata']['toponym_discovery']['false_positives_removed'] = sum(removed_count.values())
    data['metadata']['entity_count_summary']['places'] = len(all_places)
    
    # Save refined version
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"  Saved refined extraction")
    
    return {
        'year': year,
        'before': len(new_places),
        'after': len(filtered_places),
        'removed': sum(removed_count.values())
    }

if __name__ == "__main__":
    years = [1918, 1919, 1921, 1922, 1923, 1924, 1925, 1927]
    
    print("=" * 80)
    print("REFINING TOPONYM EXTRACTIONS")
    print("=" * 80)
    
    results = []
    for year in years:
        result = refine_toponyms(year)
        results.append(result)
    
    print("\n" + "=" * 80)
    print("REFINEMENT SUMMARY")
    print("=" * 80)
    
    total_before = sum(r['before'] for r in results)
    total_after = sum(r['after'] for r in results)
    total_removed = sum(r['removed'] for r in results)
    
    print(f"\nTotal new toponyms before: {total_before}")
    print(f"Total removed: {total_removed}")
    print(f"Total new toponyms after: {total_after}")
    print(f"Precision improvement: {(total_removed/total_before*100):.1f}% false positives removed")
    print()

