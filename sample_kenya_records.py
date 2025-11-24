#!/usr/bin/env python3
import json
import random

# Load the data
with open('/home/user/colonial_office_list/kenya_all_years_v1.json', 'r') as f:
    data = json.load(f)

people = data['people']

# Group by year
by_year = {}
for idx, person in enumerate(people):
    year = person['year']
    if year not in by_year:
        by_year[year] = []
    by_year[year].append((idx, person))

# Sample strategy: get good coverage across time periods
# Early (1922-1930): 8 samples
# Middle (1931-1940): 7 samples
# Late (1946-1963): 10 samples

early_years = [1922, 1923, 1924, 1925, 1927, 1928, 1929, 1930]
middle_years = [1931, 1932, 1933, 1934, 1936, 1937, 1939, 1940]
late_years = [1946, 1948, 1950, 1951, 1953, 1955, 1957, 1958, 1960, 1961, 1963]

samples = []

# Sample from early period
for year in early_years:
    if year in by_year and len(by_year[year]) > 0:
        idx, person = random.choice(by_year[year])
        samples.append({'index': idx, 'person': person})

# Sample from middle period (7 samples from 8 years)
selected_middle = random.sample([y for y in middle_years if y in by_year], 7)
for year in selected_middle:
    if len(by_year[year]) > 0:
        idx, person = random.choice(by_year[year])
        samples.append({'index': idx, 'person': person})

# Sample from late period
for year in late_years:
    if year in by_year and len(by_year[year]) > 0:
        idx, person = random.choice(by_year[year])
        samples.append({'index': idx, 'person': person})

# Save samples
with open('/home/user/colonial_office_list/kenya_evaluation_samples.json', 'w') as f:
    json.dump(samples, f, indent=2)

print(f"Sampled {len(samples)} records")
print(f"Years covered: {sorted(set(s['person']['year'] for s in samples))}")
