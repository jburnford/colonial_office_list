#!/usr/bin/env python3
"""Comprehensive structural analysis of all Colonial Office List years"""
import json
import re
from pathlib import Path
from collections import defaultdict

def analyze_year(json_path: Path):
    """Analyze a single year's structure"""
    year = re.search(r'(\d{4})', json_path.parent.name)
    if not year:
        year = re.search(r'(\d{4})', json_path.name)
    year = int(year.group(1)) if year else 0

    with open(json_path) as f:
        data = json.load(f)

    # Get text
    if isinstance(data, list) and len(data) > 0:
        if 'text' in data[0]:
            if len(data) == 1 and len(data[0]['text']) > 100000:
                text = data[0]['text']
                num_pages = 1
            else:
                texts = [page['text'] for page in data if 'text' in page]
                text = '\n'.join(texts)
                num_pages = len(texts)
        else:
            return None
    else:
        return None

    lines = text.split('\n')

    # Count various structural markers
    cross_refs = len([l for l in lines if '(See ' in l and ', p. ' in l])

    # PART markers
    part_i = len([l for l in lines[:5000] if re.match(r'^\s*PART\s+(I|1)[^IV]', l)])
    part_ii = len([l for l in lines[:5000] if re.match(r'^\s*PART\s+(II|2)', l)])
    part_iii = len([l for l in lines[:5000] if re.match(r'^\s*PART\s+(III|3)', l)])

    # Section markers
    situation_area = len([l for l in lines if re.match(r'^\s*Situation and Area', l)])
    extent_boundaries = len([l for l in lines if re.match(r'^\s*Extent and Boundaries', l)])
    general_description = len([l for l in lines if re.match(r'^\s*General Description', l)])

    # Colony name appearances
    colony_names = ['BARBADOS', 'JAMAICA', 'CEYLON', 'HONG KONG', 'MALTA', 'GIBRALTAR']
    colony_counts = {name: len([l for l in lines if l.strip().rstrip('.') == name])
                     for name in colony_names}

    # Check for new format indicators
    dominions = len([l for l in lines[:10000] if 'DOMINION' in l and 'STATUS' in l])
    mandated_territories = len([l for l in lines[:10000] if 'MANDATED TERRITOR' in l])
    protectorates = len([l for l in lines[:10000] if 'PROTECTORATE' in l])

    return {
        'year': year,
        'num_pages': num_pages,
        'total_lines': len(lines),
        'cross_refs': cross_refs,
        'part_i': part_i,
        'part_ii': part_ii,
        'part_iii': part_iii,
        'situation_area': situation_area,
        'extent_boundaries': extent_boundaries,
        'general_description': general_description,
        'barbados_count': colony_counts['BARBADOS'],
        'jamaica_count': colony_counts['JAMAICA'],
        'dominions': dominions,
        'mandated_territories': mandated_territories,
        'protectorates': protectorates,
    }

def main():
    base_dir = Path('historical_document_pipeline/processed_pdfs')

    results = []
    for year_dir in sorted(base_dir.glob('colonial-office-list-*')):
        if not year_dir.is_dir():
            continue

        json_file = year_dir / 'olmocr_results.json'
        if not json_file.exists():
            continue

        print(f"Analyzing {year_dir.name}...")
        analysis = analyze_year(json_file)
        if analysis:
            results.append(analysis)

    # Print table
    print("\n" + "="*120)
    print(f"{'Year':<6} {'Lines':>7} {'Cross':>5} {'P-I':>4} {'P-II':>4} {'P-III':>5} "
          f"{'Sit&A':>5} {'Ext&B':>5} {'GenD':>5} {'BARB':>4} {'JAM':>4} {'Dom':>4} {'Mand':>4} {'Prot':>4}")
    print("="*120)

    for r in results:
        print(f"{r['year']:<6} {r['total_lines']:>7,} {r['cross_refs']:>5} "
              f"{r['part_i']:>4} {r['part_ii']:>4} {r['part_iii']:>5} "
              f"{r['situation_area']:>5} {r['extent_boundaries']:>5} {r['general_description']:>5} "
              f"{r['barbados_count']:>4} {r['jamaica_count']:>4} "
              f"{r['dominions']:>4} {r['mandated_territories']:>4} {r['protectorates']:>4}")

    # Identify format clusters
    print("\n" + "="*120)
    print("FORMAT CLUSTERS:")
    print("="*120)

    for r in results:
        year = r['year']

        # Determine format
        if r['cross_refs'] > 5:
            fmt = "GROUPED (cross-refs)"
        elif r['part_ii'] > 0 and r['situation_area'] > 20:
            if r['mandated_territories'] > 0 or r['dominions'] > 5:
                fmt = "MODERN (Part II + new categories)"
            else:
                fmt = "STANDARD (Part II + Situation&Area)"
        elif r['cross_refs'] == 0 and r['part_i'] == 0:
            fmt = "DIRECT (no parts, no refs)"
        else:
            fmt = "TRANSITION"

        print(f"{year}: {fmt}")

    # Export to JSON
    output_file = Path('output/all_years_structural_analysis.json')
    output_file.parent.mkdir(exist_ok=True, parents=True)
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2)
    print(f"\n\nDetailed results exported to {output_file}")

if __name__ == '__main__':
    main()
