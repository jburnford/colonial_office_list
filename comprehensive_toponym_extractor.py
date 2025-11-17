#!/usr/bin/env python3
"""
Comprehensive Toponym Extraction Agent for Colonial Office List Project
Extracts ALL toponyms from source documents for years 1867-1890
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Set, Tuple
from collections import defaultdict

class ToponymExtractor:
    def __init__(self, year: int):
        self.year = year
        self.source_dir = Path(f"/home/user/colonial_office_list/output_2/{year}_manual_parsed")
        self.v3_file = Path(f"/home/user/colonial_office_list/knowledge_graph_extracts_v3/{year}_extracted_toponyms.json")
        self.existing_places = {}
        self.new_places = []
        self.place_counter = 0

        # Toponym patterns - comprehensive list of place types
        self.place_type_keywords = {
            'bay': ['Bay', 'Bays', 'Harbor', 'Harbour', 'Gulf', 'Sound', 'Inlet'],
            'river': ['River', 'Creek', 'Stream', 'Brook'],
            'mountain': ['Mountain', 'Mountains', 'Mount', 'Mt.', 'Peak', 'Hill', 'Hills', 'Range', 'Ridge', 'Valley'],
            'island': ['Island', 'Islands', 'Isle', 'Isles', 'Cay', 'Cays', 'Key', 'Keys', 'Atoll'],
            'city': ['Town', 'City', 'Village', 'Settlement', 'Fort', 'Port'],
            'district': ['District', 'Division', 'Ward', 'Quarter', 'Region', 'Territory', 'Province'],
            'parish': ['Parish', 'County', 'Shire'],
            'estate': ['Estate', 'Plantation', 'Farm', 'Property'],
            'water': ['Lake', 'Pond', 'Lagoon', 'Swamp', 'Marsh'],
            'cape': ['Cape', 'Point', 'Head', 'Promontory'],
            'forest': ['Forest', 'Wood', 'Woods', 'Bush'],
        }

        # Common non-toponym terms to exclude
        self.exclude_terms = {
            'the', 'a', 'an', 'of', 'in', 'at', 'on', 'to', 'from', 'by', 'with',
            'General', 'Colonial', 'Royal', 'Imperial', 'British', 'Her Majesty',
            'Government', 'Office', 'Department', 'Assembly', 'Council', 'Court',
            'Regiment', 'Battalion', 'Company', 'Division', 'Force', 'Service',
            'Church', 'Chapel', 'Cathedral', 'Mission', 'School', 'Hospital',
            'Act', 'Bill', 'Law', 'Ordinance', 'Treaty', 'Agreement',
            'January', 'February', 'March', 'April', 'May', 'June', 'July',
            'August', 'September', 'October', 'November', 'December',
            'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'
        }

    def load_existing_kg(self):
        """Load existing v3 knowledge graph file"""
        if self.v3_file.exists():
            with open(self.v3_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for place in data.get('entities', {}).get('places', []):
                    self.existing_places[place['name'].lower()] = place
                self.data = data
                print(f"Loaded {len(self.existing_places)} existing places for {self.year}")
        else:
            print(f"No existing v3 file found for {self.year}")
            self.data = {
                "metadata": {
                    "year": str(self.year),
                    "source_directory": str(self.source_dir),
                    "extraction_date": "2025-11-17T00:00:00Z",
                    "processing_notes": f"Comprehensive toponym extraction for {self.year}",
                    "colonies_processed": []
                },
                "entities": {
                    "places": [],
                    "people": [],
                    "institutions": [],
                    "economic_data": [],
                    "infrastructure": [],
                    "demographics": [],
                    "events": []
                },
                "relationships": []
            }

    def extract_toponyms_from_text(self, text: str, source_file: str, colony: str) -> List[Dict]:
        """Extract toponyms from text using pattern matching"""
        toponyms = []
        lines = text.split('\n')

        for line_num, line in enumerate(lines, 1):
            # Skip very short lines
            if len(line.strip()) < 3:
                continue

            # Extract place patterns
            for place_type, keywords in self.place_type_keywords.items():
                for keyword in keywords:
                    # Pattern: [Proper Name] + [Type Keyword]
                    # e.g., "Blue Mountain Valley", "Morant Bay", "Port Antonio"
                    pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s+' + re.escape(keyword) + r'\b'
                    matches = re.finditer(pattern, line)

                    for match in matches:
                        place_name = f"{match.group(1)} {keyword}"

                        # Skip if already exists or is in exclude list
                        if place_name.lower() in self.existing_places:
                            continue
                        if any(excl in place_name for excl in self.exclude_terms):
                            continue
                        if len(place_name) < 3:
                            continue

                        # Extract context (50 chars before and after)
                        start = max(0, match.start() - 50)
                        end = min(len(line), match.end() + 50)
                        context = line[start:end].strip()

                        toponyms.append({
                            'name': place_name,
                            'type': place_type,
                            'context': context,
                            'line_number': line_num,
                            'source_file': source_file,
                            'parent_location': colony
                        })

            # Also look for standalone proper place names (capitalized multi-word phrases)
            # Pattern: [Capital Word] [Capital Word]+ that appear near geographic context
            geographic_context_words = [
                'situated', 'located', 'lies', 'extends', 'north', 'south', 'east', 'west',
                'miles', 'latitude', 'longitude', 'distance', 'boundary', 'border',
                'coast', 'inland', 'adjacent', 'near', 'opposite', 'between'
            ]

            if any(word in line.lower() for word in geographic_context_words):
                # Find capitalized phrases (potential place names)
                cap_pattern = r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+){1,3})\b'
                matches = re.finditer(cap_pattern, line)

                for match in matches:
                    place_name = match.group(1)

                    # Skip if already exists or in exclude list
                    if place_name.lower() in self.existing_places:
                        continue
                    if any(excl in place_name for excl in self.exclude_terms):
                        continue
                    if len(place_name) < 5:
                        continue

                    # Check if it's likely a place (near geographic keywords)
                    context_start = max(0, match.start() - 100)
                    context_end = min(len(line), match.end() + 100)
                    context = line[context_start:context_end].lower()

                    if any(word in context for word in geographic_context_words):
                        # Determine type based on context
                        place_type = 'settlement'
                        for ptype, keywords in self.place_type_keywords.items():
                            if any(kw.lower() in context for kw in keywords):
                                place_type = ptype
                                break

                        toponyms.append({
                            'name': place_name,
                            'type': place_type,
                            'context': line[context_start:context_end].strip(),
                            'line_number': line_num,
                            'source_file': source_file,
                            'parent_location': colony
                        })

        return toponyms

    def extract_from_colony_file(self, colony_file: Path) -> List[Dict]:
        """Extract toponyms from a single colony markdown file"""
        try:
            with open(colony_file, 'r', encoding='utf-8') as f:
                text = f.read()

            colony_name = colony_file.stem
            source_path = f"output_2/{self.year}_manual_parsed/{colony_file.name}"

            toponyms = self.extract_toponyms_from_text(text, source_path, colony_name)

            print(f"  {colony_name}: Found {len(toponyms)} potential toponyms")
            return toponyms

        except Exception as e:
            print(f"  ERROR reading {colony_file}: {e}")
            return []

    def deduplicate_toponyms(self, toponyms: List[Dict]) -> List[Dict]:
        """Remove duplicate toponyms, keeping the one with most context"""
        seen = {}
        for topo in toponyms:
            name_lower = topo['name'].lower()
            if name_lower not in seen or len(topo['context']) > len(seen[name_lower]['context']):
                seen[name_lower] = topo

        return list(seen.values())

    def create_place_entity(self, toponym: Dict) -> Dict:
        """Create a properly formatted place entity"""
        self.place_counter += 1

        # Generate ID
        parent = toponym['parent_location'].lower().replace(' ', '_')
        entity_id = f"place_{parent}_{self.year}_new_{self.place_counter:03d}"

        entity = {
            "id": entity_id,
            "name": toponym['name'],
            "type": toponym['type'],
            "parent_location": toponym['parent_location'],
            "description": toponym['context'],
            "year": str(self.year),
            "provenance": {
                "source_file": toponym['source_file'],
                "source_line": toponym['line_number'],
                "extraction_confidence": 0.90,
                "extraction_agent": "comprehensive_toponym_extractor_1867_1890",
                "extraction_date": "2025-11-17"
            }
        }

        return entity

    def process_year(self) -> Dict:
        """Process all colony files for the year"""
        print(f"\n{'='*60}")
        print(f"Processing year {self.year}")
        print(f"{'='*60}")

        # Load existing data
        self.load_existing_kg()

        # Get all colony markdown files
        if not self.source_dir.exists():
            print(f"ERROR: Source directory not found: {self.source_dir}")
            return None

        colony_files = sorted(self.source_dir.glob("*.md"))
        print(f"Found {len(colony_files)} colony files")

        # Extract toponyms from each file
        all_toponyms = []
        for colony_file in colony_files:
            toponyms = self.extract_from_colony_file(colony_file)
            all_toponyms.extend(toponyms)

        print(f"\nTotal potential toponyms found: {len(all_toponyms)}")

        # Deduplicate
        unique_toponyms = self.deduplicate_toponyms(all_toponyms)
        print(f"Unique toponyms after deduplication: {len(unique_toponyms)}")

        # Create entities for new toponyms
        new_entities = []
        for toponym in unique_toponyms:
            entity = self.create_place_entity(toponym)
            new_entities.append(entity)

        # Add to existing data
        original_count = len(self.data['entities']['places'])
        self.data['entities']['places'].extend(new_entities)

        print(f"\nResults:")
        print(f"  Original places: {original_count}")
        print(f"  New places added: {len(new_entities)}")
        print(f"  Total places: {len(self.data['entities']['places'])}")

        # Save enhanced file
        self.v3_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.v3_file, 'w', encoding='utf-8') as f:
            json.dump(self.data, f, indent=2, ensure_ascii=False)

        print(f"  Saved to: {self.v3_file}")

        return {
            'year': self.year,
            'original_count': original_count,
            'new_count': len(new_entities),
            'total_count': len(self.data['entities']['places']),
            'colonies_processed': len(colony_files)
        }


def main():
    """Main execution function"""
    years = [1867, 1877, 1880, 1883, 1886, 1888, 1889, 1890]

    results = []
    for year in years:
        extractor = ToponymExtractor(year)
        result = extractor.process_year()
        if result:
            results.append(result)

    # Print summary
    print(f"\n{'='*60}")
    print("EXTRACTION SUMMARY")
    print(f"{'='*60}")
    print(f"{'Year':<8} {'Original':<12} {'New':<12} {'Total':<12} {'% Increase':<12}")
    print("-" * 60)

    for result in results:
        pct_increase = (result['new_count'] / result['original_count'] * 100) if result['original_count'] > 0 else 0
        print(f"{result['year']:<8} {result['original_count']:<12} {result['new_count']:<12} "
              f"{result['total_count']:<12} {pct_increase:<12.1f}%")

    # Save summary
    summary_file = Path("/home/user/colonial_office_list/toponym_extraction_summary.json")
    with open(summary_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\nSummary saved to: {summary_file}")


if __name__ == "__main__":
    main()
