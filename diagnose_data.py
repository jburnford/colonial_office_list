#!/usr/bin/env python3
"""
Diagnostic script to understand data format mismatches.
"""

import json
import os
from pathlib import Path


def inspect_ocr_structure(year):
    """Inspect the actual structure of OCR data."""
    ocr_path = f"historical_document_pipeline/processed_pdfs/colonial-office-list-{year}/olmocr_results.json"
    if not os.path.exists(ocr_path):
        print(f"No OCR file at: {ocr_path}")
        return

    print(f"\n{'='*80}")
    print(f"OCR Structure for {year}")
    print(f"{'='*80}")

    with open(ocr_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"Top level type: {type(data)}")

    if isinstance(data, dict):
        print(f"Keys: {list(data.keys())[:20]}")
        for key in list(data.keys())[:3]:
            print(f"\nKey '{key}':")
            value = data[key]
            if isinstance(value, list):
                print(f"  Type: list, Length: {len(value)}")
                if value:
                    print(f"  First element type: {type(value[0])}")
                    if isinstance(value[0], dict):
                        print(f"  First element keys: {list(value[0].keys())[:10]}")
            elif isinstance(value, dict):
                print(f"  Type: dict, Keys: {list(value.keys())[:10]}")
            else:
                print(f"  Type: {type(value)}, Value preview: {str(value)[:200]}")

    elif isinstance(data, list):
        print(f"List length: {len(data)}")
        if data:
            print(f"First element type: {type(data[0])}")
            if isinstance(data[0], dict):
                print(f"First element keys: {list(data[0].keys())}")
                # Show first few fields
                for key in list(data[0].keys())[:5]:
                    val = data[0][key]
                    if isinstance(val, str):
                        print(f"  {key}: {val[:200]}")
                    else:
                        print(f"  {key}: {type(val)}")


def inspect_extract_sample(year):
    """Inspect a sample of extracted data."""
    extracted_dir = f"output_2/{year}_manual_parsed"
    if not os.path.exists(extracted_dir):
        print(f"No extracted dir at: {extracted_dir}")
        return

    print(f"\n{'='*80}")
    print(f"Extracted Data Sample for {year}")
    print(f"{'='*80}")

    files = list(Path(extracted_dir).glob("*.md"))
    if files:
        sample_file = files[0]
        print(f"Sample file: {sample_file.name}")
        with open(sample_file, 'r', encoding='utf-8') as f:
            content = f.read()
        print(f"Length: {len(content)} chars")
        print(f"\nFirst 500 chars:\n{content[:500]}")
        print(f"\n...Content from middle...\n{content[len(content)//2:len(content)//2+500]}")


def compare_specific_text(year):
    """Look for specific text in both OCR and extract."""
    print(f"\n{'='*80}")
    print(f"Text Comparison for {year}")
    print(f"{'='*80}")

    # Load OCR
    ocr_path = f"historical_document_pipeline/processed_pdfs/colonial-office-list-{year}/olmocr_results.json"
    with open(ocr_path, 'r', encoding='utf-8') as f:
        ocr_data = json.load(f)

    # Try to extract text from OCR in different ways
    print("\nAttempting to extract text from OCR...")

    text_found = False

    # Method 1: pages -> text
    if isinstance(ocr_data, dict) and 'pages' in ocr_data:
        print("✓ Found 'pages' key")
        if ocr_data['pages'] and 'text' in ocr_data['pages'][0]:
            sample = ocr_data['pages'][0]['text'][:300]
            print(f"  Sample text: {sample}")
            text_found = True

    # Method 2: direct list with text
    if isinstance(ocr_data, list):
        print("✓ OCR is a list")
        if ocr_data and isinstance(ocr_data[0], dict):
            print(f"  First element keys: {list(ocr_data[0].keys())}")
            if 'text' in ocr_data[0]:
                sample = ocr_data[0]['text'][:300]
                print(f"  Sample text: {sample}")
                text_found = True
            elif 'content' in ocr_data[0]:
                sample = str(ocr_data[0]['content'])[:300]
                print(f"  Sample content: {sample}")

    # Method 3: Check for other common keys
    if isinstance(ocr_data, dict):
        for key in ['content', 'full_text', 'ocr_text', 'extracted_text', 'results']:
            if key in ocr_data:
                print(f"✓ Found '{key}' key")
                val = ocr_data[key]
                if isinstance(val, str):
                    print(f"  Sample: {val[:300]}")
                    text_found = True
                elif isinstance(val, list) and val:
                    print(f"  List length: {len(val)}")

    if not text_found:
        print("⚠️  Could not find text in expected format")


def main():
    """Run diagnostics."""
    years = ['1900', '1923', '1948']

    for year in years:
        inspect_ocr_structure(year)
        inspect_extract_sample(year)
        compare_specific_text(year)


if __name__ == "__main__":
    main()
