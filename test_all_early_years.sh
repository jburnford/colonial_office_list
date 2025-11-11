#!/bin/bash
# Test early grouped parser on multiple years

for year in 1878 1879 1880 1883; do
  echo "=== Testing $year ==="
  python3 early_grouped_parser.py \
    historical_document_pipeline/processed_pdfs/colonial-office-list-$year/olmocr_results.json \
    -o output/${year}_parsed_grouped.json 2>&1 | grep "=== Total:"
  echo
done
