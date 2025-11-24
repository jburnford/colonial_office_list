#!/usr/bin/env python3
"""
Independent Quality Evaluation Agent for FIXED Jamaica Colonial Office List extraction (v2)
"""

import json
import random
import re
from pathlib import Path
from collections import defaultdict

def load_json_data(filepath):
    """Load the JSON data file"""
    print(f"Loading data from {filepath}...")
    with open(filepath, 'r', encoding='utf-8') as f:
        full_data = json.load(f)

    # Extract people array
    people = full_data.get('people', full_data.get('data', []))
    metadata = full_data.get('metadata', {})

    print(f"Loaded {len(people)} records")
    print(f"Metadata: {metadata.get('total_people', 'N/A')} people from {metadata.get('total_files', 'N/A')} files")
    print(f"Year range: {metadata.get('year_range', 'N/A')}")

    return people, metadata

def get_source_file(year, base_path="/home/user/colonial_office_list/output_3"):
    """Get the source file path for a given year"""
    pattern = f"{year}_manual_parsed/jamaica.txt"
    for path in Path(base_path).glob(f"{year}*/jamaica.txt"):
        return str(path)
    return None

def read_source_context(filepath, name, role=None, location=None, context_lines=3):
    """Read context around a person's entry in the source file"""
    if not filepath or not Path(filepath).exists():
        return None

    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    # Search for the name in the file
    for i, line in enumerate(lines):
        if name.split()[-1] in line:  # Search by last name
            start = max(0, i - context_lines)
            end = min(len(lines), i + context_lines + 1)
            return ''.join(lines[start:end])

    return None

def extract_initials_from_name(name):
    """Extract all initials from a name"""
    # Find all single letters followed by periods
    initials = re.findall(r'\b([A-Z])\.\s*', name)
    return initials

def check_all_initials_present(name):
    """Check if a name appears to have all initials (not truncated)"""
    initials = extract_initials_from_name(name)
    # If we have initials, check that there's no pattern suggesting truncation
    # This is a heuristic - we'll verify manually against source
    return len(initials) > 0

def is_non_person_data(record):
    """Check if a record appears to be non-person data (months, hurricanes, etc.)"""
    name = record.get('name', '').lower()
    role = record.get('role', '').lower()

    # Check for month names
    months = ['january', 'february', 'march', 'april', 'may', 'june',
              'july', 'august', 'september', 'october', 'november', 'december']
    if any(month in name for month in months):
        return True

    # Check for hurricane/climate indicators
    climate_keywords = ['hurricane', 'rainfall', 'drought', 'storm', 'climate',
                       'temperature', 'weather', 'inches', 'feet']
    if any(keyword in name or keyword in role for keyword in climate_keywords):
        return True

    # Check for numeric-heavy names (likely data)
    if len(re.findall(r'\d+', name)) > 2:
        return True

    return False

def sample_records(data, sample_size=25):
    """Sample records evenly across different years"""
    # Group by year
    by_year = defaultdict(list)
    for record in data:
        year = record.get('year', 'unknown')
        by_year[year].append(record)

    # Sort years
    years = sorted([y for y in by_year.keys() if y != 'unknown'])
    print(f"Data spans {len(years)} years: {years[0]} to {years[-1]}")

    # Sample evenly across years
    samples = []
    years_to_sample = sorted(random.sample(years, min(sample_size, len(years))))

    for year in years_to_sample:
        if len(samples) < sample_size and by_year[year]:
            record = random.choice(by_year[year])
            record['_sampled_from_year'] = year
            samples.append(record)

    # If we need more samples, add random ones
    while len(samples) < sample_size and len(samples) < len(data):
        record = random.choice(data)
        if record not in samples:
            samples.append(record)

    print(f"Sampled {len(samples)} records from {len(set(s.get('year') for s in samples))} different years")
    return samples

def verify_record(record, record_num):
    """Verify a single record against source"""
    print(f"\n{'='*80}")
    print(f"Record {record_num}/25")
    print(f"{'='*80}")

    name = record.get('name', '')
    role = record.get('role', '')
    location = record.get('location', '')
    year = record.get('year', '')
    confidence = record.get('confidence', 0)

    print(f"Year: {year}")
    print(f"Name: {name}")
    print(f"Role: {role}")
    print(f"Location: {location}")
    print(f"Confidence: {confidence}")

    # Initialize verification results
    verification = {
        'record_num': record_num,
        'year': year,
        'name': name,
        'role': role,
        'location': location,
        'confidence': confidence,
        'is_non_person': False,
        'has_all_initials': True,
        'name_accurate': None,
        'role_accurate': None,
        'location_accurate': None,
        'perfect': False,
        'issues': []
    }

    # Check for non-person data
    if is_non_person_data(record):
        verification['is_non_person'] = True
        verification['issues'].append("NON-PERSON DATA (month/hurricane/climate)")
        print("⚠️  WARNING: This appears to be non-person data!")

    # Check initials
    initials = extract_initials_from_name(name)
    if initials:
        verification['initials_found'] = initials
        print(f"Initials found: {', '.join(initials)}")

    # Get source file
    source_file = get_source_file(year)
    if source_file:
        print(f"\nSource file: {source_file}")
        context = read_source_context(source_file, name, role, location)
        if context:
            print(f"\nSource context:")
            print("-" * 80)
            print(context)
            print("-" * 80)
            verification['source_context'] = context
        else:
            print("⚠️  Could not find this entry in source file")
            verification['issues'].append("Not found in source file")
    else:
        print(f"⚠️  Source file not found for year {year}")
        verification['issues'].append("Source file not available")

    # Manual verification prompt
    print("\nMANUAL VERIFICATION NEEDED:")
    print("1. Name accurate (all initials)? (y/n/skip): ", end='')

    return verification

def calculate_metrics(verifications):
    """Calculate quality metrics from verifications"""
    total = len(verifications)

    metrics = {
        'total_records': total,
        'non_person_count': 0,
        'name_accurate': 0,
        'role_accurate': 0,
        'location_accurate': 0,
        'perfect_extractions': 0,
        'has_issues': 0
    }

    for v in verifications:
        if v['is_non_person']:
            metrics['non_person_count'] += 1
        if v.get('name_accurate'):
            metrics['name_accurate'] += 1
        if v.get('role_accurate'):
            metrics['role_accurate'] += 1
        if v.get('location_accurate'):
            metrics['location_accurate'] += 1
        if v.get('perfect'):
            metrics['perfect_extractions'] += 1
        if v.get('issues'):
            metrics['has_issues'] += 1

    # Calculate percentages
    if total > 0:
        metrics['non_person_rate'] = (metrics['non_person_count'] / total) * 100
        metrics['name_accuracy'] = (metrics['name_accurate'] / total) * 100
        metrics['role_accuracy'] = (metrics['role_accurate'] / total) * 100
        metrics['location_accuracy'] = (metrics['location_accurate'] / total) * 100
        metrics['perfect_rate'] = (metrics['perfect_extractions'] / total) * 100

    return metrics

def main():
    """Main evaluation process"""
    print("="*80)
    print("INDEPENDENT QUALITY EVALUATION: FIXED Jamaica Extraction (v2)")
    print("="*80)

    # Load data
    data, metadata = load_json_data('/home/user/colonial_office_list/jamaica_all_years_v1.json')

    # Sample records
    print(f"\nSampling 25 records for evaluation...")
    random.seed(42)  # For reproducibility
    samples = sample_records(data, 25)

    # Verify each sample
    verifications = []
    for i, record in enumerate(samples, 1):
        verification = verify_record(record, i)
        verifications.append(verification)

    print("\n" + "="*80)
    print("EVALUATION COMPLETE - Records displayed for manual verification")
    print("="*80)
    print("\nNext step: Review each record above and verify against source context")
    print("Then manually calculate final metrics based on verification results")

if __name__ == '__main__':
    main()
