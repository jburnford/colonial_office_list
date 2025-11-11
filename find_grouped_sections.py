#!/usr/bin/env python3
"""Find grouped colony sections and their cross-references"""
import json
import sys
import re
from pathlib import Path

def find_groups(json_path):
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

    # Find all cross-references and extract what they point to
    cross_refs = {}
    for i, line in enumerate(lines):
        if '(See ' in line and ', p. ' in line:
            match = re.search(r'\(See ([^,]+), p\. (\d+)\)', line)
            if match:
                target = match.group(1).strip()
                page = match.group(2)

                # Get the colony name from previous line
                colony = None
                for j in range(i-1, max(0, i-10), -1):
                    stripped = lines[j].strip().rstrip('.')
                    if stripped and len(stripped) < 50 and stripped.isupper():
                        colony = stripped
                        break

                if colony:
                    if target not in cross_refs:
                        cross_refs[target] = []
                    cross_refs[target].append((colony, i, page))

    # Find group headers (all caps headers with "THE" or plural forms)
    group_headers = []
    for i, line in enumerate(lines):
        stripped = line.strip().rstrip('.')

        # Look for group patterns
        if (re.match(r'^THE [A-Z\s]+ISLANDS?$', stripped) or
            re.match(r'^[A-Z\s]+ ISLANDS?$', stripped) or
            re.match(r'^DOMINION OF [A-Z\s]+$', stripped) or
            re.match(r'^[A-Z\s]+SETTLEMENTS?$', stripped)):

            # Check if it's followed by colony content
            has_content = False
            for j in range(i+1, min(i+20, len(lines))):
                if lines[j].strip() and len(lines[j].strip()) > 40:
                    has_content = True
                    break

            if has_content:
                group_headers.append((i, stripped))

    return cross_refs, group_headers

if __name__ == '__main__':
    json_path = sys.argv[1]
    cross_refs, group_headers = find_groups(json_path)

    print("=== Cross-Reference Targets ===")
    for target, colonies in sorted(cross_refs.items()):
        print(f"\n{target}:")
        for colony, line_num, page in colonies:
            print(f"  - {colony:30s} (line {line_num:,}, references p. {page})")

    print("\n\n=== Grouped Section Headers ===")
    for line_num, header in group_headers:
        print(f"Line {line_num:,}: {header}")
