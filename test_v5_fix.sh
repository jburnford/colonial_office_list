#!/bin/bash
# Test fixed V5 parser across standard format years

for year in 1900 1905 1910 1915 1920 1925 1930; do
  echo "=== Testing $year ==="
  python3 colonial_office_parser_v5.py \
    historical_document_pipeline/processed_pdfs/colonial-office-list-$year/olmocr_results.json \
    -o output/${year}_parsed_v5_fixed.json 2>&1 | \
    grep -E "(Found Part III|Total colonies parsed)" | head -3

  # Show sample colonies
  tail -30 output/${year}_parsed_v5_fixed.json | grep -E "colony_name" | head -5
  echo
done
