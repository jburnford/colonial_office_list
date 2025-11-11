#!/bin/bash
# Test V5 parser on standard format years

for year in 1888 1896 1905 1915 1920 1930; do
  echo "=== Testing V5 on $year ==="
  python3 colonial_office_parser_v5.py \
    historical_document_pipeline/processed_pdfs/colonial-office-list-$year/olmocr_results.json \
    -o output/${year}_parsed_v5.json 2>&1 | tail -15
  echo
done
