#!/usr/bin/env python3
"""
Independent Quality Evaluation for Kenya Colonial Office List Extraction
"""

import json
import random
import re
from pathlib import Path
from collections import defaultdict

# Load the JSON data
print("Loading kenya_all_years_v1.json...")
with open('/home/user/colonial_office_list/kenya_all_years_v1.json', 'r') as f:
    data = json.load(f)

metadata = data['metadata']
people = data['people']

print(f"Total people: {len(people)}")
print(f"Year range: {metadata['year_range']}")
print(f"Total files: {metadata['total_files']}")
print()

# Group people by year
people_by_year = defaultdict(list)
for person in people:
    year = person['year']
    people_by_year[year].append(person)

years = sorted(people_by_year.keys())
print(f"Years with data: {len(years)} years from {min(years)} to {max(years)}")
print()

# Sample 25 records distributed across the time range
# We want good coverage across different years
sample_size = 25
samples = []

# Divide the year range into segments and sample from each
year_segments = [
    (1922, 1930),  # Early period
    (1931, 1940),  # Pre-war
    (1946, 1955),  # Post-war
    (1956, 1964),  # Late period
]

samples_per_segment = sample_size // len(year_segments)
extra = sample_size % len(year_segments)

random.seed(42)  # For reproducibility

for i, (start_year, end_year) in enumerate(year_segments):
    segment_years = [y for y in years if start_year <= y <= end_year]
    segment_people = []
    for year in segment_years:
        segment_people.extend(people_by_year[year])

    # Sample from this segment
    n_samples = samples_per_segment + (1 if i < extra else 0)
    if len(segment_people) >= n_samples:
        segment_samples = random.sample(segment_people, n_samples)
        samples.extend(segment_samples)

print(f"Sampled {len(samples)} records for verification")
print()

# Save samples to a JSON file for easy review
with open('/home/user/colonial_office_list/kenya_sample_25.json', 'w') as f:
    json.dump(samples, f, indent=2)

# Print sample summary
print("Sample distribution by year:")
year_counts = defaultdict(int)
for s in samples:
    year_counts[s['year']] += 1

for year in sorted(year_counts.keys()):
    print(f"  {year}: {year_counts[year]} records")
print()

# Print the samples with key information
print("="*80)
print("SAMPLED RECORDS FOR VERIFICATION")
print("="*80)
print()

for i, sample in enumerate(samples, 1):
    print(f"Sample {i}:")
    print(f"  Year: {sample['year']}")
    print(f"  Source: {sample['source_file']}")
    print(f"  Name: {sample['name']}")
    print(f"  Role: {sample.get('role', 'N/A')}")
    print(f"  Location: {sample.get('location', 'N/A')}")
    print(f"  Confidence: {sample.get('confidence', 'N/A')}")
    print(f"  Original line: {sample.get('original_line', 'N/A')[:100]}...")
    print()

print("Samples saved to: /home/user/colonial_office_list/kenya_sample_25.json")
