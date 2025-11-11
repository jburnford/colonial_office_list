"""
Colonial Office List Subsection Parser

Breaks colony sections into subsections based on identified header patterns.
"""

import json
import re
from pathlib import Path
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, asdict

@dataclass
class Subsection:
    """Represents a subsection within a colony"""
    title: str
    start_line: int
    end_line: int
    line_count: int
    char_count: int
    category: str  # Geographic, Administrative, Trade, etc.

    def to_dict(self):
        return asdict(self)

class SubsectionParser:
    """Parse colony sections into subsections"""

    # Keywords for categorizing subsections
    CATEGORIES = {
        'Geographic': ['situation', 'area', 'climate', 'geography', 'extent', 'boundaries', 'location'],
        'Historical': ['history', 'historical', 'discovery', 'settlement'],
        'Constitutional': ['constitution', 'legislature', 'council', 'assembly', 'government'],
        'Administrative': ['establishment', 'department', 'office', 'secretary', 'medical',
                          'police', 'court', 'justice', 'governor', 'administration'],
        'Financial': ['finance', 'revenue', 'treasury', 'expenditure', 'budget', 'debt'],
        'Trade': ['trade', 'export', 'import', 'commerce', 'shipping', 'customs'],
        'Population': ['population', 'census', 'demographic', 'inhabitants'],
        'Education': ['education', 'school', 'college', 'university'],
        'Religion': ['ecclesiastical', 'church', 'religion', 'mission'],
        'Military': ['military', 'defence', 'garrison', 'forces'],
        'Infrastructure': ['railway', 'road', 'port', 'harbor', 'public works'],
        'Agriculture': ['agriculture', 'farming', 'cultivation', 'produce'],
        'Statistics': ['statistics', 'statistical', 'tables'],
    }

    def __init__(self, lines: List[str]):
        self.lines = lines

    def is_subsection_header(self, line: str, prev_line: str = "", next_line: str = "") -> bool:
        """
        Determine if a line is a subsection header

        Patterns:
        1. **Bold markdown headers**
        2. Capitalized standalone headers
        3. Department/Office names
        4. Section titles followed by period/colon
        """
        stripped = line.strip()

        if not stripped or len(stripped) < 3:
            return False

        # Pattern 1: Bold markdown
        if stripped.startswith('**') and stripped.endswith('**'):
            return True

        # Pattern 2: ALL CAPS short headers
        if stripped.isupper() and 5 < len(stripped) < 50:
            # Avoid page headers and place names
            if not any(word in stripped for word in ['PAGE', 'CONTINUED', 'PART II', 'PART III']):
                return True

        # Pattern 3: Capitalized section names (Title Case)
        if (len(stripped) < 80 and
            stripped[0].isupper() and
            not stripped.isupper() and
            (stripped.endswith('.') or stripped.endswith(':') or
             any(kw in stripped.lower() for kw in ['situation', 'history', 'constitution',
                                                     'government', 'finance', 'trade',
                                                     'population', 'education']))):

            # Check it's not a regular sentence
            words = stripped.split()
            if len(words) <= 6:  # Short enough to be a header
                # Check for keyword presence
                for category_keywords in self.CATEGORIES.values():
                    if any(kw in stripped.lower() for kw in category_keywords):
                        return True

        # Pattern 4: Office/Department headers
        if any(term in stripped for term in ["'s Office", "'s Department", "Office.", "Department."]):
            if len(stripped) < 100:
                return True

        # Pattern 5: Section markers with specific formatting
        # e.g., "Civil Establishment." or "Exports."
        if (stripped.endswith('.') and
            len(stripped) < 50 and
            len(stripped.split()) <= 4 and
            stripped[0].isupper()):
            # Not a sentence if it's short and capitalized
            if not any(char.isdigit() for char in stripped[:20]):  # No numbers at start
                return True

        return False

    def categorize_subsection(self, title: str) -> str:
        """Categorize a subsection based on its title"""
        title_lower = title.lower()

        for category, keywords in self.CATEGORIES.items():
            if any(kw in title_lower for kw in keywords):
                return category

        return 'Other'

    def parse_subsections(self, colony_start: int, colony_end: int, colony_name: str) -> List[Subsection]:
        """
        Parse subsections within a colony section

        Args:
            colony_start: Starting line of colony
            colony_end: Ending line of colony
            colony_name: Name of colony

        Returns:
            List of Subsection objects
        """
        subsections = []
        current_subsection_start = None
        current_subsection_title = None

        for i in range(colony_start, colony_end):
            line = self.lines[i]

            # Skip colony name header itself
            if i == colony_start:
                continue

            # Get context
            prev_line = self.lines[i-1] if i > colony_start else ""
            next_line = self.lines[i+1] if i < colony_end - 1 else ""

            if self.is_subsection_header(line, prev_line, next_line):
                # Found a new subsection header

                # Save previous subsection if exists
                if current_subsection_start is not None and current_subsection_title:
                    # Calculate metrics
                    end = i
                    line_count = end - current_subsection_start
                    char_count = sum(len(self.lines[j]) + 1 for j in range(current_subsection_start, end))

                    if line_count > 0:  # Only add if has content
                        subsection = Subsection(
                            title=current_subsection_title,
                            start_line=current_subsection_start,
                            end_line=end,
                            line_count=line_count,
                            char_count=char_count,
                            category=self.categorize_subsection(current_subsection_title)
                        )
                        subsections.append(subsection)

                # Start new subsection
                current_subsection_title = line.strip().strip('*').strip('.').strip(':').strip()
                current_subsection_start = i + 1  # Content starts on next line

        # Add final subsection
        if current_subsection_start is not None and current_subsection_title:
            end = colony_end
            line_count = end - current_subsection_start
            char_count = sum(len(self.lines[j]) + 1 for j in range(current_subsection_start, end))

            if line_count > 0:
                subsection = Subsection(
                    title=current_subsection_title,
                    start_line=current_subsection_start,
                    end_line=end,
                    line_count=line_count,
                    char_count=char_count,
                    category=self.categorize_subsection(current_subsection_title)
                )
                subsections.append(subsection)

        return subsections

def parse_colony_subsections(source_file: str, parsed_file: str, output_file: str):
    """
    Parse all colonies and extract subsections

    Args:
        source_file: Path to OCR results JSON
        parsed_file: Path to parsed colonies JSON
        output_file: Path to write subsections JSON
    """
    # Load source lines
    source_path = Path(source_file)
    with open(source_path, 'r') as f:
        data = json.load(f)

        if isinstance(data, list) and len(data) > 0:
            if isinstance(data[0], str):
                lines = data
            elif 'text' in data[0]:
                texts = [p['text'] for p in data if 'text' in p]
                lines = '\n'.join(texts).split('\n')
        else:
            lines = data

    # Load parsed colonies
    with open(parsed_file, 'r') as f:
        parsed = json.load(f)

    parser = SubsectionParser(lines)

    # Parse subsections for each colony
    results = {
        'source_file': source_file,
        'parsed_file': parsed_file,
        'year': parsed.get('year', 0),
        'total_colonies': len(parsed['colonies']),
        'colonies_with_subsections': []
    }

    total_subsections = 0

    for colony in parsed['colonies']:
        name = colony['colony_name']
        start = colony['start_line']
        end = colony['end_line']

        # Parse subsections
        subsections = parser.parse_subsections(start, end, name)

        if subsections:
            total_subsections += len(subsections)

            colony_result = {
                'colony_name': name,
                'start_line': start,
                'end_line': end,
                'total_subsections': len(subsections),
                'subsections': [s.to_dict() for s in subsections]
            }

            results['colonies_with_subsections'].append(colony_result)

    results['total_subsections'] = total_subsections

    # Write output
    output_path = Path(output_file)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, 'w') as f:
        json.dump(results, f, indent=2)

    print(f"Parsed {len(results['colonies_with_subsections'])} colonies with {total_subsections} subsections")
    print(f"Exported to {output_path}")

    return results

if __name__ == "__main__":
    import sys

    if len(sys.argv) != 4:
        print("Usage: python subsection_parser.py <source_json> <parsed_json> <output_json>")
        sys.exit(1)

    parse_colony_subsections(sys.argv[1], sys.argv[2], sys.argv[3])
