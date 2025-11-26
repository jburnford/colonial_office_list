#!/usr/bin/env python3
"""
Validate knowledge graph extracts against raw OCR to identify false positives.
Only identifies issues - does not create parsers or new data.
"""

import json
import os
import re
from pathlib import Path
from collections import defaultdict
from difflib import SequenceMatcher


def load_ocr_data(year):
    """Load raw OCR data for a given year."""
    ocr_path = f"historical_document_pipeline/processed_pdfs/colonial-office-list-{year}/olmocr_results.json"
    if not os.path.exists(ocr_path):
        return None

    try:
        with open(ocr_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            # Extract all text from OCR results
            all_text = ""
            if isinstance(data, dict) and 'pages' in data:
                for page in data['pages']:
                    if 'text' in page:
                        all_text += page['text'] + "\n"
            elif isinstance(data, list):
                for page in data:
                    if 'text' in page:
                        all_text += page['text'] + "\n"
            return all_text
    except Exception as e:
        print(f"Error loading OCR for {year}: {e}")
        return None


def load_extracted_data(year):
    """Load extracted markdown files for a given year."""
    extracted_dir = f"output_2/{year}_manual_parsed"
    if not os.path.exists(extracted_dir):
        return None

    extracted_files = list(Path(extracted_dir).glob("*.md"))
    return extracted_files


def normalize_text(text):
    """Normalize text for comparison (remove extra whitespace, lowercase)."""
    # Remove multiple spaces and newlines
    text = re.sub(r'\s+', ' ', text)
    # Lowercase for case-insensitive comparison
    text = text.lower()
    # Remove common OCR artifacts
    text = re.sub(r'[^\w\s\.,;:\-£$€]', '', text)
    return text.strip()


def extract_key_facts(md_file):
    """Extract key factual claims from markdown files."""
    with open(md_file, 'r', encoding='utf-8') as f:
        content = f.read()

    facts = []

    # Extract names with titles (Sir, Dr., Rev., etc.)
    names_with_titles = re.findall(r'\b(?:Sir|Dr\.|Rev\.|Major|Captain|Colonel|General|Admiral|Hon\.)\s+[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*', content)
    for name in names_with_titles:
        facts.append(('name', name, md_file.name))

    # Extract salary information (£ amounts)
    salaries = re.findall(r'£[\d,]+', content)
    for salary in salaries:
        facts.append(('salary', salary, md_file.name))

    # Extract years/dates
    years = re.findall(r'\b(1[678]\d{2}|19\d{2})\b', content)
    for year in set(years):  # deduplicate
        facts.append(('year', year, md_file.name))

    # Extract geographic coordinates
    coords = re.findall(r'\d+°\s*\d+\'?\s*[NS]\s*lat\.?|longitude', content, re.IGNORECASE)
    for coord in coords:
        facts.append(('coordinate', coord, md_file.name))

    # Extract population numbers
    population = re.findall(r'population[:\s]+[\d,]+', content, re.IGNORECASE)
    for pop in population:
        facts.append(('population', pop, md_file.name))

    # Extract area measurements
    areas = re.findall(r'\d+(?:,\d{3})*\s+(?:square\s+miles|acres)', content, re.IGNORECASE)
    for area in areas:
        facts.append(('area', area, md_file.name))

    return facts


def check_fact_in_ocr(fact_value, ocr_text, threshold=0.7):
    """
    Check if a fact appears in OCR text.
    Returns (found, similarity_score, matching_context)
    """
    normalized_fact = normalize_text(fact_value)
    normalized_ocr = normalize_text(ocr_text)

    # Direct substring match
    if normalized_fact in normalized_ocr:
        # Extract context around the match
        idx = normalized_ocr.find(normalized_fact)
        context_start = max(0, idx - 100)
        context_end = min(len(normalized_ocr), idx + len(normalized_fact) + 100)
        context = normalized_ocr[context_start:context_end]
        return (True, 1.0, context)

    # Fuzzy matching for names and longer strings
    if len(normalized_fact) > 10:
        # Look for approximate matches
        words = normalized_fact.split()
        if len(words) >= 2:
            # Check if key words appear
            found_words = sum(1 for word in words if len(word) > 3 and word in normalized_ocr)
            similarity = found_words / len(words)
            if similarity >= threshold:
                return (True, similarity, f"Found {found_words}/{len(words)} words")

    return (False, 0.0, "")


def analyze_year(year):
    """Analyze extracts for a specific year."""
    print(f"\n{'='*80}")
    print(f"Analyzing year: {year}")
    print(f"{'='*80}")

    ocr_text = load_ocr_data(year)
    if ocr_text is None:
        print(f"⚠️  No OCR data found for {year}")
        return None

    extracted_files = load_extracted_data(year)
    if not extracted_files:
        print(f"⚠️  No extracted files found for {year}")
        return None

    print(f"✓ Found {len(extracted_files)} extracted files")
    print(f"✓ OCR text length: {len(ocr_text)} characters")

    issues = {
        'missing_facts': [],
        'low_confidence': [],
        'suspicious_patterns': []
    }

    total_facts = 0
    facts_found = 0

    for md_file in extracted_files[:5]:  # Sample first 5 files
        print(f"\nChecking: {md_file.name}")
        facts = extract_key_facts(md_file)
        total_facts += len(facts)

        for fact_type, fact_value, source in facts[:10]:  # Sample first 10 facts per file
            found, confidence, context = check_fact_in_ocr(fact_value, ocr_text)

            if found:
                facts_found += 1
                if confidence < 0.85:
                    issues['low_confidence'].append({
                        'year': year,
                        'file': source,
                        'type': fact_type,
                        'value': fact_value,
                        'confidence': confidence,
                        'context': context[:200]
                    })
            else:
                issues['missing_facts'].append({
                    'year': year,
                    'file': source,
                    'type': fact_type,
                    'value': fact_value
                })

    # Calculate statistics
    if total_facts > 0:
        match_rate = (facts_found / total_facts) * 100
        print(f"\n📊 Statistics:")
        print(f"   Total facts checked: {total_facts}")
        print(f"   Facts found in OCR: {facts_found}")
        print(f"   Match rate: {match_rate:.1f}%")
        print(f"   Missing facts: {len(issues['missing_facts'])}")
        print(f"   Low confidence: {len(issues['low_confidence'])}")

    return issues


def main():
    """Main validation routine."""
    print("Knowledge Graph Extract Validation")
    print("="*80)

    # Get all available years
    kg_files = list(Path("knowledge_graph_extracts_v3").glob("*_extracted.json"))
    years = sorted([f.stem.split('_')[0] for f in kg_files])

    print(f"Found {len(years)} years to validate: {years[0]} to {years[-1]}")

    # Sample years across different periods
    sample_years = [
        years[0],      # Earliest
        years[len(years)//4],  # Early period
        years[len(years)//2],  # Middle period
        years[3*len(years)//4],  # Late period
        years[-1]      # Latest
    ]

    print(f"\nSampling years: {sample_years}")

    all_issues = defaultdict(list)

    for year in sample_years:
        issues = analyze_year(year)
        if issues:
            for issue_type, issue_list in issues.items():
                all_issues[issue_type].extend(issue_list)

    # Generate summary report
    print(f"\n{'='*80}")
    print("VALIDATION SUMMARY")
    print(f"{'='*80}")

    for issue_type, issue_list in all_issues.items():
        print(f"\n{issue_type.upper().replace('_', ' ')}: {len(issue_list)}")
        if issue_list and len(issue_list) <= 10:
            for issue in issue_list[:10]:
                print(f"  - {issue['year']}/{issue['file']}: {issue['value']}")

    # Save detailed report
    output_file = "extract_validation_report.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(dict(all_issues), f, indent=2, ensure_ascii=False)

    print(f"\n✓ Detailed report saved to: {output_file}")

    # Identify top issues for LLM review
    priority_issues = []

    # Prioritize missing facts that look suspicious
    for issue in all_issues['missing_facts']:
        if issue['type'] in ['name', 'salary']:
            priority_issues.append(issue)

    if priority_issues:
        print(f"\n⚠️  {len(priority_issues[:20])} high-priority issues identified for LLM review")
        priority_file = "priority_issues_for_review.json"
        with open(priority_file, 'w', encoding='utf-8') as f:
            json.dump(priority_issues[:20], f, indent=2, ensure_ascii=False)
        print(f"✓ Priority issues saved to: {priority_file}")


if __name__ == "__main__":
    main()
