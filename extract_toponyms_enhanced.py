#!/usr/bin/env python3
"""
Enhanced Toponym Extraction for Colonial Office List Knowledge Graph
Creates detailed toponym entities with full provenance
"""

import json
import re
from pathlib import Path
from collections import defaultdict
from typing import Dict, List, Set, Tuple

class EnhancedToponymExtractor:
    def __init__(self):
        self.base_dir = Path("/home/user/colonial_office_list")
        self.years = [1946, 1948, 1949]

        # Comprehensive stopword list - things that are NOT places
        self.stopwords = {
            # Titles and honorifics
            'His', 'Her', 'Majesty', 'Majestys', 'Highness', 'Excellency',
            'Sir', 'Mr', 'Mrs', 'Miss', 'Dr', 'Rev', 'Esquire', 'Esq',
            'Captain', 'Major', 'Colonel', 'General', 'Admiral', 'Commander',
            'Chief', 'Deputy', 'Assistant', 'Senior', 'Junior', 'Acting',
            'Governor', 'Commissioner', 'Secretary', 'Officer', 'Director',
            'Superintendent', 'Inspector', 'Controller', 'Manager', 'Agent',

            # Government/admin terms
            'Government', 'Department', 'Office', 'Service', 'Administration',
            'Colony', 'Protectorate', 'Territory', 'Crown', 'Royal', 'British',
            'Council', 'Board', 'Committee', 'Commission', 'Institute',
            'Legislative', 'Executive', 'Judicial', 'Supreme', 'High',
            'Court', 'Tribunal', 'Magistrate', 'Attorney', 'Solicitor',

            # Generic descriptors
            'The', 'This', 'These', 'Those', 'A', 'An', 'Each', 'Every',
            'State', 'Province', 'District', 'Division', 'Section',
            'Department', 'Bureau', 'Agency', 'Authority', 'Trust',

            # Job functions
            'Agricultural', 'Medical', 'Education', 'Public', 'Works',
            'Police', 'Defence', 'Treasury', 'Audit', 'Survey',
            'Development', 'Research', 'Welfare', 'Labour', 'Trade',

            # Months and days
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December',
            'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday',

            # Directions (unless part of a place name)
            'North', 'South', 'East', 'West', 'Central', 'Northern',
            'Southern', 'Eastern', 'Western', 'Upper', 'Lower', 'Middle',
            'First', 'Second', 'Third', 'Fourth', 'Fifth', 'Sixth',

            # Legal/administrative
            'Act', 'Order', 'Ordinance', 'Regulation', 'Law', 'Statute',
            'Amendment', 'Provision', 'Section', 'Clause', 'Article',
            'Treaty', 'Agreement', 'Convention', 'Protocol',

            # Misc
            'Principal', 'Secretaries', 'Instructions', 'Warrant',
            'Manual', 'Signet', 'Seal', 'Instrument', 'Document',
        }

        # Stopwords that should be excluded as standalone but OK in compounds
        self.partial_stopwords = {
            'Island', 'Islands', 'Bay', 'River', 'Lake', 'Mount', 'Mountain',
            'Port', 'Cape', 'Point', 'Town', 'City', 'Village', 'Colony',
            'Protectorate', 'District', 'Province', 'Division', 'Territory'
        }

        # Known valid places from Colonial Office Lists
        self.known_places = self.load_known_places()

        # Place type indicators
        self.place_indicators = {
            'island': ['Island', 'Islands', 'Atoll', 'Cay', 'Key'],
            'water': ['River', 'Lake', 'Bay', 'Harbor', 'Harbour', 'Gulf', 'Strait', 'Straits', 'Sound', 'Sea', 'Ocean'],
            'mountain': ['Mount', 'Mt.', 'Mountain', 'Peak', 'Range', 'Hill', 'Hills', 'Jabal'],
            'settlement': ['Town', 'City', 'Village', 'Township', 'Settlement', 'Port'],
            'administrative': ['District', 'Province', 'Division', 'Parish', 'State', 'Region', 'Area'],
            'feature': ['Cape', 'Point', 'Peninsula', 'Coast', 'Shore'],
        }

    def load_known_places(self) -> Set[str]:
        """Load known places from existing KG files and curated lists"""
        known = set()

        # Major colonial cities and capitals
        known.update([
            # Africa
            'Accra', 'Lagos', 'Freetown', 'Bathurst', 'Sekondi', 'Takoradi', 'Kumasi',
            'Ibadan', 'Kano', 'Kaduna', 'Enugu', 'Port Harcourt', 'Calabar',
            'Nairobi', 'Mombasa', 'Kisumu', 'Nakuru', 'Entebbe', 'Kampala',
            'Dar es Salaam', 'Tanga', 'Mwanza', 'Dodoma', 'Zanzibar', 'Pemba',
            'Lusaka', 'Ndola', 'Livingstone', 'Zomba', 'Blantyre', 'Lilongwe',
            'Salisbury', 'Bulawayo', 'Gwelo', 'Umtali',

            # Asia/Pacific
            'Singapore', 'Hong Kong', 'Victoria', 'Kowloon', 'Colombo', 'Kandy', 'Galle',
            'Kuala Lumpur', 'Penang', 'Ipoh', 'Kuching', 'Sibu', 'Miri',
            'Jesselton', 'Sandakan', 'Labuan', 'Suva', 'Lautoka', 'Levuka',
            'Port Moresby', 'Rabaul', 'Lae', 'Madang',

            # Caribbean
            'Kingston', 'Port of Spain', 'Bridgetown', 'Nassau', 'Georgetown',
            'Castries', 'Kingstown', 'St. Georges', 'Roseau', 'Basseterre',
            'Plymouth', 'Road Town', 'Belize City',

            # Middle East
            'Aden', 'Crater', 'Steamer Point', 'Sheikh Othman', 'Little Aden',
            'Nicosia', 'Famagusta', 'Limassol', 'Larnaca', 'Jerusalem', 'Haifa', 'Jaffa',
            'Valletta', 'Sliema', 'Mdina',

            # Other
            'Gibraltar', 'Hamilton', 'St. Georges', 'Jamestown', 'Stanley',
        ])

        # Load from existing KG files
        for year in self.years:
            kg_path = self.base_dir / "knowledge_graph_extracts_v3" / f"{year}_extracted.json"
            try:
                with open(kg_path, 'r') as f:
                    data = json.load(f)
                    if 'entities' in data and isinstance(data['entities'], dict):
                        if 'places' in data['entities']:
                            for place in data['entities']['places']:
                                if isinstance(place, dict):
                                    name = place.get('name', '')
                                    if name:
                                        known.add(name)
            except Exception as e:
                print(f"Warning: Could not load {kg_path}: {e}")

        return known

    def is_valid_toponym(self, name: str, context: str = "") -> bool:
        """Determine if a name is likely a valid toponym"""
        # Strip whitespace
        name = name.strip()

        # Reject if too short or too long
        if len(name) < 3 or len(name) > 100:
            return False

        # Reject if all uppercase or all lowercase (likely acronym or generic term)
        if name.isupper() and len(name) > 2:
            # Exception for known places that are all caps
            if name not in self.known_places:
                return False

        # Reject exact stopword matches
        if name in self.stopwords:
            return False

        # Reject standalone partial stopwords
        if name in self.partial_stopwords:
            return False

        # Reject if it looks like a person's name (has Esq, Sir, etc.)
        if any(x in name for x in ['Esq.', 'K.C.M.G.', 'K.B.E.', 'C.B.E.', 'O.B.E.', 'M.B.E.']):
            return False

        # Reject if it looks like a title
        title_patterns = [
            r'^(The|His|Her)\s+',
            r'^(Mr|Mrs|Miss|Dr|Rev)\.',
            r'(Chief|Secretary|Commissioner|Governor|Director)$',
        ]
        for pattern in title_patterns:
            if re.search(pattern, name):
                return False

        # Accept if in known places
        if name in self.known_places:
            return True

        # Accept if has a place indicator
        for category, indicators in self.place_indicators.items():
            for indicator in indicators:
                if indicator in name:
                    return True

        # Accept if has coordinates nearby in context
        if re.search(r'\d+[°]\s*\d+[′\']', context):
            return True

        # Accept if mentioned with location prepositions
        location_pattern = r'\b(in|at|of|from|to|near|port of|town of|city of|capital of|island of|district of)\s+' + re.escape(name)
        if re.search(location_pattern, context, re.IGNORECASE):
            return True

        # Reject if it contains obvious non-place words
        reject_phrases = [
            'government', 'department', 'council', 'committee', 'act',
            'ordinance', 'regulation', 'his majesty', 'her majesty',
            'instruction', 'warrant', 'seal', 'amendment'
        ]
        name_lower = name.lower()
        if any(phrase in name_lower for phrase in reject_phrases):
            return False

        # Default: accept if it's capitalized properly and not too generic
        words = name.split()
        if all(w[0].isupper() for w in words if w):
            # Check it's not just directional words
            directional = {'North', 'South', 'East', 'West', 'Northern', 'Southern', 'Eastern', 'Western'}
            if all(w in directional for w in words):
                return False
            return True

        return False

    def classify_toponym(self, name: str, context: str) -> str:
        """Classify toponym into specific type"""
        name_lower = name.lower()
        context_lower = context.lower()

        # Check name-based indicators
        for ptype, indicators in self.place_indicators.items():
            for indicator in indicators:
                if indicator.lower() in name_lower:
                    return ptype.upper()

        # Check context-based indicators
        if any(x in context_lower for x in ['colony', 'protectorate', 'territory', 'dominion']):
            return 'COLONY'
        elif any(x in context_lower for x in ['capital', 'headquarters', 'seat of government']):
            return 'CAPITAL'
        elif any(x in context_lower for x in ['town', 'city', 'municipality']):
            return 'SETTLEMENT'
        elif any(x in context_lower for x in ['district', 'province', 'division', 'parish', 'region']):
            return 'ADMINISTRATIVE_DIVISION'
        elif any(x in context_lower for x in ['port', 'harbor', 'harbour']):
            return 'PORT'

        return 'PLACE'

    def extract_toponyms_from_file(self, filepath: Path, colony_name: str, year: int) -> List[Dict]:
        """Extract all valid toponyms from a source file"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                text = f.read()
        except Exception as e:
            print(f"Error reading {filepath}: {e}")
            return []

        toponyms = []
        lines = text.split('\n')

        # Comprehensive extraction patterns
        patterns = [
            # Places with explicit location markers
            (r'\b(?:in|at|of|from|to|near|off)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,3})\b', 'location_marker'),
            # Named geographic features
            (r'\b([A-Z][a-zA-Z\s\-]+?)\s+(Island|Islands|Bay|River|Lake|Mountain|Mount|Cape|Point|Peninsula|Strait|Straits|Gulf|Sound)\b', 'feature'),
            # Settlement patterns
            (r'\b(?:town|city|village|capital|port) of\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2})\b', 'settlement'),
            # District/province patterns
            (r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2})\s+(District|Province|Division|Parish|Region)\b', 'administrative'),
            # Places in parenthetical statements
            (r'\(([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2})\)', 'parenthetical'),
            # Coordinates pattern (captures place near coordinates)
            (r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+){0,2})\s+is\s+situated\s+(?:in|at)', 'situated'),
        ]

        seen = set()

        for line_num, line in enumerate(lines, 1):
            # Skip empty lines and section headers (all caps)
            if not line.strip() or line.strip().isupper():
                continue

            for pattern, pattern_type in patterns:
                matches = re.finditer(pattern, line, re.IGNORECASE)
                for match in matches:
                    # Extract the place name
                    if pattern_type == 'feature':
                        place_name = (match.group(1) + ' ' + match.group(2)).strip()
                    else:
                        place_name = match.group(1).strip()

                    # Clean up
                    place_name = place_name.rstrip('.,;:')

                    # Validate
                    if not self.is_valid_toponym(place_name, line):
                        continue

                    # Deduplicate within file
                    key = (place_name, colony_name)
                    if key in seen:
                        continue
                    seen.add(key)

                    # Classify
                    place_type = self.classify_toponym(place_name, line)

                    # Create entity
                    entity_id = f"toponym_{year}_{len(toponyms)}"

                    toponyms.append({
                        'id': entity_id,
                        'name': place_name,
                        'type': place_type,
                        'parent_territory': colony_name,
                        'year': year,
                        'provenance': {
                            'source_file': filepath.name,
                            'source_path': str(filepath.relative_to(self.base_dir)),
                            'line_number': line_num,
                            'context': line.strip()[:200],  # First 200 chars
                            'extraction_pattern': pattern_type
                        },
                        'metadata': {
                            'extraction_date': '2025-11-17',
                            'extraction_method': 'enhanced_toponym_extractor',
                            'confidence': 'high' if place_name in self.known_places else 'medium'
                        }
                    })

        return toponyms

    def extract_year(self, year: int) -> Dict:
        """Extract all toponyms for a given year"""
        source_dir = self.base_dir / "output_2" / f"{year}_manual_parsed"

        if not source_dir.exists():
            print(f"Warning: Source directory not found: {source_dir}")
            return {"toponyms": [], "count": 0}

        all_toponyms = []

        for md_file in sorted(source_dir.glob("*.md")):
            colony_name = md_file.stem.replace('_', ' ').title()
            print(f"  Processing {colony_name}...")

            toponyms = self.extract_toponyms_from_file(md_file, colony_name, year)
            all_toponyms.extend(toponyms)

        # Deduplicate across colonies (keep first occurrence)
        seen_names = {}
        unique_toponyms = []

        for topo in all_toponyms:
            name = topo['name']
            if name not in seen_names:
                seen_names[name] = topo
                unique_toponyms.append(topo)
            else:
                # Add cross-reference
                existing = seen_names[name]
                if 'also_found_in' not in existing:
                    existing['also_found_in'] = []
                existing['also_found_in'].append({
                    'territory': topo['parent_territory'],
                    'source': topo['provenance']['source_file']
                })

        return {
            "toponyms": unique_toponyms,
            "count": len(unique_toponyms),
            "total_extractions": len(all_toponyms)
        }

    def generate_enhanced_kg(self, year: int, toponyms: List[Dict]) -> Path:
        """Generate enhanced knowledge graph file with toponyms"""
        # Load existing KG
        existing_kg_path = self.base_dir / "knowledge_graph_extracts_v3" / f"{year}_extracted.json"

        try:
            with open(existing_kg_path, 'r') as f:
                kg_data = json.load(f)
        except Exception as e:
            print(f"Error loading existing KG: {e}")
            kg_data = {"entities": {}, "relationships": []}

        # Add toponyms to entities
        if 'entities' not in kg_data:
            kg_data['entities'] = {}

        if not isinstance(kg_data['entities'], dict):
            # Convert to dict format
            old_entities = kg_data['entities']
            kg_data['entities'] = {'original': old_entities}

        # Add toponyms category
        kg_data['entities']['toponyms'] = toponyms

        # Update metadata
        if 'metadata' not in kg_data:
            kg_data['metadata'] = {}

        kg_data['metadata']['toponym_extraction'] = {
            'date': '2025-11-17',
            'count': len(toponyms),
            'method': 'enhanced_toponym_extractor',
            'coverage': 'comprehensive'
        }

        # Save enhanced KG
        output_path = self.base_dir / "knowledge_graph_extracts_v3" / f"{year}_extracted_toponyms.json"

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(kg_data, f, indent=2, ensure_ascii=False)

        print(f"  Enhanced KG saved: {output_path}")
        return output_path

    def process_all_years(self):
        """Process all years"""
        results = {}

        for year in self.years:
            print(f"\n{'='*60}")
            print(f"Extracting toponyms for {year}")
            print(f"{'='*60}")

            extracted = self.extract_year(year)
            print(f"  Extracted {extracted['count']} unique toponyms")
            print(f"  ({extracted['total_extractions']} total extractions)")

            # Generate enhanced KG
            kg_path = self.generate_enhanced_kg(year, extracted['toponyms'])

            results[year] = {
                'unique_count': extracted['count'],
                'total_extractions': extracted['total_extractions'],
                'kg_file': str(kg_path),
                'sample_toponyms': [t['name'] for t in extracted['toponyms'][:50]]
            }

        return results

def main():
    print("="*60)
    print("ENHANCED TOPONYM EXTRACTION")
    print("Colonial Office List Knowledge Graph Project")
    print("="*60)

    extractor = EnhancedToponymExtractor()
    results = extractor.process_all_years()

    # Save results summary
    summary_path = extractor.base_dir / "toponym_extraction_summary.json"
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)

    print(f"\n{'='*60}")
    print("EXTRACTION COMPLETE")
    print(f"{'='*60}")
    print(f"\nResults summary saved to: {summary_path}")

    for year, data in results.items():
        print(f"\n{year}:")
        print(f"  Unique toponyms: {data['unique_count']}")
        print(f"  Enhanced KG: {data['kg_file']}")

if __name__ == "__main__":
    main()
