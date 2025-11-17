#!/usr/bin/env python3
"""
Check all elements in OCR data to find actual colonial office content.
"""

import json
import os


def check_all_ocr_elements(year):
    """Check all elements in OCR data."""
    ocr_path = f"historical_document_pipeline/processed_pdfs/colonial-office-list-{year}/olmocr_results.json"

    print(f"\n{'='*80}")
    print(f"All OCR Elements for {year}")
    print(f"{'='*80}")

    with open(ocr_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    if isinstance(data, list):
        print(f"Total elements: {len(data)}\n")

        for i, element in enumerate(data):
            if isinstance(element, dict) and 'text' in element:
                text = element['text']
                print(f"Element {i}:")
                print(f"  Length: {len(text)} chars")
                print(f"  ID: {element.get('id', 'N/A')[:16]}...")
                print(f"  First 200 chars: {text[:200]}")

                # Check if this looks like colonial office content
                keywords = ['colony', 'governor', 'administration', 'territory', 'protectorate', 'aden', 'hong kong']
                keyword_count = sum(1 for kw in keywords if kw.lower() in text.lower())
                print(f"  Colonial keywords found: {keyword_count}/{len(keywords)}")

                # Look for specific content from extracted files
                if 'aden' in text.lower():
                    # Find context around 'aden'
                    idx = text.lower().find('aden')
                    context = text[max(0, idx-100):min(len(text), idx+200)]
                    print(f"  Context around 'Aden': ...{context}...")

                print()


def search_for_colony_in_ocr(year, colony_name):
    """Search for a specific colony in OCR."""
    ocr_path = f"historical_document_pipeline/processed_pdfs/colonial-office-list-{year}/olmocr_results.json"

    print(f"\n{'='*80}")
    print(f"Searching for '{colony_name}' in {year} OCR")
    print(f"{'='*80}")

    with open(ocr_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    found_in = []

    if isinstance(data, list):
        for i, element in enumerate(data):
            if isinstance(element, dict) and 'text' in element:
                text = element['text']
                if colony_name.lower() in text.lower():
                    found_in.append(i)
                    # Show context
                    idx = text.lower().find(colony_name.lower())
                    context_start = max(0, idx - 200)
                    context_end = min(len(text), idx + 300)
                    context = text[context_start:context_end]
                    print(f"\nFound in element {i}:")
                    print(f"Context: ...{context}...")

    if found_in:
        print(f"\n✓ '{colony_name}' found in elements: {found_in}")
    else:
        print(f"\n✗ '{colony_name}' NOT found in any element")

    return len(found_in) > 0


def main():
    """Run checks."""
    year = '1900'

    # Check all elements
    check_all_ocr_elements(year)

    # Search for specific colonies
    colonies = ['ADEN', 'HONG KONG', 'BARBADOS', 'GIBRALTAR']

    print(f"\n{'='*80}")
    print("Colony Search Results")
    print(f"{'='*80}")

    for colony in colonies:
        found = search_for_colony_in_ocr(year, colony)


if __name__ == "__main__":
    main()
