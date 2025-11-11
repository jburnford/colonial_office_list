#!/usr/bin/env python3
"""Quick structural analysis of a Colonial Office List year"""
import json
import sys
from pathlib import Path

def analyze_year(json_path):
    with open(json_path) as f:
        data = json.load(f)

    # Get text
    if isinstance(data, list) and len(data) > 0:
        if len(data) == 1 and 'text' in data[0] and len(data[0]['text']) > 100000:
            text = data[0]['text']
        else:
            texts = [page['text'] for page in data if 'text' in page]
            text = '\n'.join(texts)
    else:
        text = ""

    lines = text.split('\n')

    # Check for cross-references
    cross_refs = [(i, lines[i].strip()) for i, line in enumerate(lines)
                  if '(See ' in line and ', p. ' in line]

    # Check for PART markers (first 5000 lines)
    part_markers = [(i, lines[i].strip()) for i, line in enumerate(lines[:5000])
                    if 'PART ' in line.strip()[:20] and line.strip()]

    # Find BARBADOS occurrences
    barbados = []
    for i, line in enumerate(lines):
        stripped = line.strip().rstrip('.')
        if stripped == 'BARBADOS':
            next_lines = []
            for j in range(1, min(5, len(lines)-i)):
                if lines[i+j].strip():
                    next_lines.append(lines[i+j].strip()[:80])
                    if len(next_lines) >= 2:
                        break
            barbados.append((i, next_lines))

    return {
        'total_lines': len(lines),
        'cross_refs': cross_refs[:5],  # First 5
        'cross_ref_count': len(cross_refs),
        'part_markers': part_markers[:5],  # First 5
        'part_count': len(part_markers),
        'barbados': barbados[:3],  # First 3
        'barbados_count': len(barbados)
    }

if __name__ == '__main__':
    json_path = sys.argv[1]
    result = analyze_year(json_path)

    print(f"  Total lines: {result['total_lines']:,}")
    print(f"  Cross-references: {result['cross_ref_count']}")
    print(f"  PART markers: {result['part_count']}")
    print(f"  BARBADOS occurrences: {result['barbados_count']}")

    if result['barbados']:
        barb = result['barbados'][0]
        print(f"\n  First BARBADOS at line {barb[0]:,}:")
        for next_line in barb[1]:
            print(f"    {next_line}")

    if result['cross_refs']:
        print(f"\n  Sample cross-references:")
        for line_num, text in result['cross_refs'][:3]:
            print(f"    Line {line_num:,}: {text}")

    if result['part_markers']:
        print(f"\n  Sample PART markers:")
        for line_num, text in result['part_markers'][:3]:
            print(f"    Line {line_num:,}: {text}")
