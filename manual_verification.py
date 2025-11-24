#!/usr/bin/env python3
"""
Manual verification script for Jamaica extraction samples
"""

import json
import random
from pathlib import Path

# Load the data
with open('/home/user/colonial_office_list/jamaica_all_years_v1.json', 'r') as f:
    full_data = json.load(f)
    people = full_data['people']

# Set seed for reproducibility
random.seed(42)

# Sample records evenly across years
from collections import defaultdict
by_year = defaultdict(list)
for record in people:
    by_year[record['year']].append(record)

years = sorted(by_year.keys())
sample_size = 25
years_to_sample = sorted(random.sample(years, min(sample_size, len(years))))

samples = []
for year in years_to_sample:
    if len(samples) < sample_size and by_year[year]:
        record = random.choice(by_year[year])
        samples.append(record)

# Output detailed verification data
print("SAMPLED RECORDS FOR MANUAL VERIFICATION")
print("=" * 100)

verifications = []

for i, record in enumerate(samples, 1):
    print(f"\n{'='*100}")
    print(f"RECORD {i}/25")
    print(f"{'='*100}")

    name = record.get('name', '')
    role = record.get('role', '')
    location = record.get('location', '')
    year = record.get('year', '')
    confidence = record.get('confidence', 0)
    full_string = record.get('full_string', '')
    source_file = record.get('source_file', '')
    line_number = record.get('line_number', 0)
    extraction_method = record.get('extraction_method', '')

    print(f"Year: {year}")
    print(f"Name: {name}")
    print(f"Role: {role}")
    print(f"Location: {location}")
    print(f"Confidence: {confidence}")
    print(f"Full String: {full_string}")
    print(f"Source File: {source_file}")
    print(f"Line Number: {line_number}")
    print(f"Extraction Method: {extraction_method}")

    # Try to read source context
    source_path = f"/home/user/colonial_office_list/{source_file}"
    if Path(source_path).exists():
        with open(source_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Get context around the line
        start = max(0, line_number - 5)
        end = min(len(lines), line_number + 5)

        print(f"\nSOURCE CONTEXT (lines {start+1}-{end}):")
        print("-" * 100)
        for j in range(start, end):
            marker = " >>> " if j == line_number - 1 else "     "
            print(f"{marker}Line {j+1}: {lines[j].rstrip()}")
        print("-" * 100)
    else:
        print(f"\n⚠️  Source file not found: {source_path}")

    # Initialize verification record
    v = {
        'record_num': i,
        'year': year,
        'name': name,
        'role': role,
        'location': location,
        'confidence': confidence,
        'full_string': full_string,
        'extraction_method': extraction_method
    }

    verifications.append(v)

# Save verification template
output = {
    'total_samples': len(samples),
    'verifications': verifications
}

with open('/home/user/colonial_office_list/verification_results.json', 'w') as f:
    json.dump(output, f, indent=2)

print(f"\n\n{'='*100}")
print("VERIFICATION COMPLETE")
print(f"{'='*100}")
print(f"Total samples: {len(samples)}")
print(f"Results saved to: /home/user/colonial_office_list/verification_results.json")
