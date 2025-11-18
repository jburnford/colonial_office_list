#!/usr/bin/env python3
"""Compare 1932 and 1933 colony lists"""
import json

# Read 1932
with open('output_3/1932_manual_parsed.json') as f:
    data_1932 = json.load(f)

# Read 1933
with open('output_3/1933_manual_parsed.json') as f:
    data_1933 = json.load(f)

colonies_1932 = set([c['colony_name'] for c in data_1932['colonies']])
colonies_1933 = set([c['colony_name'] for c in data_1933['colonies']])

print(f"1932: {len(colonies_1932)} colonies")
print(f"1933: {len(colonies_1933)} colonies")
print()

# Find differences
only_1932 = colonies_1932 - colonies_1933
only_1933 = colonies_1933 - colonies_1932

if only_1932:
    print(f"Only in 1932 ({len(only_1932)}):")
    for c in sorted(only_1932):
        print(f"  - {c}")
    print()

if only_1933:
    print(f"Only in 1933 ({len(only_1933)}):")
    for c in sorted(only_1933):
        print(f"  - {c}")
    print()

# Common colonies
common = colonies_1932 & colonies_1933
print(f"Common to both years: {len(common)} colonies")

