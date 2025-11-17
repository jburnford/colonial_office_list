#!/usr/bin/env python3
"""
Toponym Quality Refinement for 1950-1959
Remove false positives and improve toponym quality
"""

import json
from pathlib import Path
from datetime import datetime

class ToponymRefiner:
    def __init__(self, base_dir: str = "/home/user/colonial_office_list"):
        self.base_dir = Path(base_dir)
        self.kg_dir = self.base_dir / "knowledge_graph_extracts_v3"
        self.years = [1950, 1951, 1953, 1954, 1956, 1957, 1959]

        # Terms to exclude (false positives)
        self.false_positives = {
            # Articles and conjunctions
            'THE', 'IN', 'OF', 'AND', 'OR', 'AT', 'TO', 'FROM', 'BY', 'WITH',
            'IN THE', 'OF THE', 'AND THE', 'AT THE', 'TO THE', 'FROM THE',

            # Month names
            'JANUARY', 'FEBRUARY', 'MARCH', 'APRIL', 'MAY', 'JUNE',
            'JULY', 'AUGUST', 'SEPTEMBER', 'OCTOBER', 'NOVEMBER', 'DECEMBER',

            # Generic section headers
            'GENERAL DESCRIPTION', 'SITUATION', 'CLIMATE', 'HISTORY',
            'CONSTITUTION', 'ADMINISTRATION', 'POPULATION', 'RELIGION',
            'EDUCATION', 'FINANCE', 'TRADE', 'COMMUNICATIONS', 'TRANSPORT',
            'SOCIAL SERVICES', 'PUBLIC WORKS', 'MEDICAL SERVICES',
            'JUDICIAL', 'LEGISLATIVE', 'EXECUTIVE', 'AGRICULTURE',
            'FORESTRY', 'MINING', 'INDUSTRY', 'LABOUR', 'LANDS',
            'SURVEYS', 'AUDIT', 'POSTS', 'CUSTOMS', 'POLICE',
            'PRISONS', 'DEFENCE', 'MISCELLANEOUS', 'GENERAL',

            # Generic terms
            'GOVERNMENT', 'COUNCIL', 'BOARD', 'COMMITTEE', 'COMMISSION',
            'DEPARTMENT', 'OFFICE', 'BRANCH', 'DIVISION', 'SECTION',
            'DIRECTORATE', 'AUTHORITY', 'SERVICE', 'SERVICES',

            # Government positions (commonly capitalized)
            'GOVERNOR', 'LIEUTENANT GOVERNOR', 'CHIEF SECRETARY',
            'ATTORNEY GENERAL', 'FINANCIAL SECRETARY', 'TREASURER',
            'GOVERNOR AND PERSONAL STAFF', 'PERSONAL STAFF',
            'ADMINISTRATOR', 'COMMISSIONER', 'RESIDENT',

            # Currency and units
            'RS', 'RE', 'RUPEES', 'RUPEE', 'DOLLARS', 'POUNDS', 'STERLING',

            # Other common false positives
            'TOTAL', 'ANNUAL', 'MONTHLY', 'WEEKLY', 'DAILY',
            'AREA', 'POPULATION', 'CENSUS', 'ESTIMATE', 'FIGURE',
            'SUMMARY', 'INTRODUCTION', 'CONCLUSION', 'APPENDIX',
            'TABLE', 'NOTES', 'REFERENCES', 'INDEX',

            # Additional section headers
            'FORESTS', 'FORESTRY', 'CIVIL ESTABLISHMENT',
            'SHORT SELECT BIBLIOGRAPHY', 'BIBLIOGRAPHY', 'SELECT BIBLIOGRAPHY',
            'FOREIGN CONSULAR OFFICERS', 'CONSULAR OFFICERS',
            'CURRENCY AND BANKING', 'BANKING', 'CURRENCY',
            'INLAND REVENUE', 'REVENUE', 'TAXATION',
            'VETERINARY SERVICES', 'VETERINARY',
            'SECONDED FROM', 'SECONDED',
            'MEDICAL AND HEALTH', 'HEALTH', 'MEDICAL',
            'WELFARE', 'HOUSING', 'WATER SUPPLY',
            'ELECTRICITY', 'SEWERAGE', 'DRAINAGE',
            'POSTS AND TELEGRAPHS', 'TELEGRAPHS', 'TELEGRAPH',
            'PRODUCTION AND TRADE', 'PRODUCTION',
            'FISHERIES', 'FISHING', 'MARINE',
            'PRISON', 'PRISONS', 'ACCOUNTANT', 'STORES',
            'POLICE AND PRISONS', 'CIVIL SUPPLIES',
            'PORT AND MARINE', 'PRINTING', 'STATIONERY',
            'PRINTING AND STATIONERY', 'REGISTRY', 'MACHINERY',
            'TRADE AND CUSTOMS',

            # Titles
            'MR', 'MRS', 'MISS', 'MS', 'DR', 'PROF', 'HON', 'SIR',
            'SENIOR', 'JUNIOR',

            # Nationalities/Languages (generic)
            'FRENCH', 'ENGLISH', 'SPANISH', 'PORTUGUESE', 'DUTCH',
            'GERMAN', 'ITALIAN', 'GREEK', 'ARABIC', 'CHINESE',

            # Roman numerals
            'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X',
            'XI', 'XII', 'XIII', 'XIV', 'XV', 'XVI', 'XVII', 'XVIII', 'XIX', 'XX',

            # Directional modifiers alone
            'NORTHERN', 'SOUTHERN', 'EASTERN', 'WESTERN', 'CENTRAL',
            'UPPER', 'LOWER', 'MIDDLE', 'INNER', 'OUTER',
            'NORTH', 'SOUTH', 'EAST', 'WEST',

            # Generic geographic terms alone
            'ISLAND', 'ISLANDS', 'LAKE', 'RIVER', 'MOUNTAIN', 'MOUNTAINS',
            'BAY', 'HARBOUR', 'HARBOR', 'PORT', 'COAST', 'PENINSULA',
            'VALLEY', 'PLAIN', 'PLATEAU', 'RANGE', 'HILL', 'HILLS',

            # Administrative terms alone
            'PROVINCE', 'DISTRICT', 'COUNTY', 'TOWNSHIP', 'MUNICIPALITY',
            'COLONY', 'PROTECTORATE', 'TERRITORY', 'DOMINION',
        }

        # Common non-toponym words that indicate false positives
        self.sentence_indicators = {
            # Articles and determiners
            'THE', 'A', 'AN', 'THIS', 'THAT', 'THESE', 'THOSE',
            # Prepositions
            'IN', 'ON', 'AT', 'TO', 'FROM', 'BY', 'WITH', 'OF', 'FOR',
            'UNDER', 'OVER', 'BETWEEN', 'AMONG', 'THROUGH', 'DURING',
            # Conjunctions
            'AND', 'OR', 'BUT', 'AS', 'THAN', 'WHEN', 'WHERE',
            # Verbs (common)
            'IS', 'ARE', 'WAS', 'WERE', 'BE', 'BEEN', 'BEING',
            'HAS', 'HAVE', 'HAD', 'WILL', 'WOULD', 'CAN', 'COULD',
            'SITUATED', 'LOCATED', 'BOUNDED', 'ADMINISTERED', 'CONSTITUTED',
            # Possessives
            'ITS', 'THEIR', 'HIS', 'HER',
        }

        # Patterns indicating false positives
        self.false_positive_patterns = [
            lambda name: len(name) < 3,  # Too short (< 3 chars)
            lambda name: len(name) > 100,  # Too long (likely sentence fragment)
            lambda name: name.replace(' ', '').isdigit(),  # Just numbers
            lambda name: name.upper() in self.false_positives,  # In exclusion list
            lambda name: name.count(' ') > 8,  # Too many words (likely sentence)
            lambda name: len(name.split()) > 0 and name.split()[0].upper() in self.sentence_indicators,  # Starts with non-toponym word
            lambda name: len(name.split()) > 0 and name.split()[-1].upper() in {'THE', 'OF', 'IN', 'ON', 'AT', 'TO', 'FROM', 'BY'},  # Ends with preposition
            lambda name: len(name.split()) > 0 and sum(1 for word in name.split() if word.upper() in self.sentence_indicators) > len(name.split()) // 2,  # More than half are common words
            lambda name: name.replace(' ', '').upper() in {'I', 'II', 'III', 'IV', 'V', 'VI', 'VII', 'VIII', 'IX', 'X'},  # Roman numerals
        ]

    def is_false_positive(self, name: str) -> bool:
        """Check if a toponym is a false positive"""
        for pattern in self.false_positive_patterns:
            if pattern(name):
                return True
        return False

    def refine_kg(self, year: int):
        """Refine KG file for a year"""
        kg_file = self.kg_dir / f"{year}_extracted_toponyms.json"

        print(f"\nRefining {year}...")

        with open(kg_file, 'r', encoding='utf-8') as f:
            kg_data = json.load(f)

        places = kg_data.get("entities", {}).get("places", [])
        initial_count = len(places)

        # Filter out false positives
        filtered_places = []
        removed_count = 0

        for place in places:
            name = place.get("name", "")

            if self.is_false_positive(name):
                removed_count += 1
                print(f"  Removing: {name} ({place.get('type', 'unknown')})")
            else:
                filtered_places.append(place)

        # Update KG
        kg_data["entities"]["places"] = filtered_places

        # Update metadata
        if "toponym_discovery" not in kg_data["metadata"]:
            kg_data["metadata"]["toponym_discovery"] = {}

        kg_data["metadata"]["toponym_discovery"]["refinement_date"] = datetime.now().isoformat()
        kg_data["metadata"]["toponym_discovery"]["false_positives_removed"] = removed_count
        kg_data["metadata"]["toponym_discovery"]["final_count"] = len(filtered_places)

        # Save refined KG
        with open(kg_file, 'w', encoding='utf-8') as f:
            json.dump(kg_data, f, indent=2, ensure_ascii=False)

        print(f"  Initial: {initial_count} places")
        print(f"  Removed: {removed_count} false positives")
        print(f"  Final: {len(filtered_places)} places")

        return removed_count

    def run(self):
        """Refine all years"""
        print("="*80)
        print("TOPONYM QUALITY REFINEMENT: 1950-1959")
        print("="*80)

        total_removed = 0

        for year in self.years:
            removed = self.refine_kg(year)
            total_removed += removed

        print("\n" + "="*80)
        print(f"REFINEMENT COMPLETE")
        print(f"Total false positives removed: {total_removed}")
        print("="*80)


if __name__ == "__main__":
    refiner = ToponymRefiner()
    refiner.run()
