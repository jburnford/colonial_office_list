#!/usr/bin/env python3
"""Compare 1927 and 1928 colony lists"""

import json

# Read 1927 metadata
with open('/home/user/colonial_office_list/output_3/1927_manual_parsed.json', 'r') as f:
    data_1927 = json.load(f)

# Read 1928 metadata
with open('/home/user/colonial_office_list/output_3/1928_manual_parsed.json', 'r') as f:
    data_1928 = json.load(f)

# Get colony names
colonies_1927 = set(c['colony_name'] for c in data_1927['colonies'])
colonies_1928 = set(c['colony_name'] for c in data_1928['colonies'])

print("="*80)
print("Comparison of 1927 and 1928 Colonial Office Lists")
print("="*80)
print()
print(f"1927: {len(colonies_1927)} colonies")
print(f"1928: {len(colonies_1928)} colonies")
print()

# Colonies in 1927 but not in 1928
missing_1928 = colonies_1927 - colonies_1928
if missing_1928:
    print(f"Colonies in 1927 but NOT in 1928 ({len(missing_1928)}):")
    for colony in sorted(missing_1928):
        print(f"  - {colony}")
    print()

# Colonies in 1928 but not in 1927
new_1928 = colonies_1928 - colonies_1927
if new_1928:
    print(f"Colonies in 1928 but NOT in 1927 ({len(new_1928)}):")
    for colony in sorted(new_1928):
        print(f"  - {colony}")
    print()

# Colonies in both
common = colonies_1927 & colonies_1928
print(f"Colonies in BOTH years ({len(common)}):")
for colony in sorted(common):
    print(f"  - {colony}")
print()
print("="*80)
