#!/bin/bash

# Lines where "Situation and Area" or "Situation and Description" appear
lines=(25068 25153 25340 25498 26395 26770 27674 28087 28157 29315 29911 30217 32310 32588 33365 33639 34107 34285 35904 35971 36587 37544 38585 41268 43410 43866 45275 46003 49481 49694 52055 52389 53269 53557 54001 54046)

OCR_FILE="/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1928/olmocr_results.md"

echo "Colony sections found in 1928:"
echo "=============================="

for line in "${lines[@]}"; do
    # Read 5 lines before to find colony name
    start=$((line - 5))
    sed -n "${start},${line}p" "$OCR_FILE" | grep -E "^[A-Z*].*\.$" | head -1 || echo "Line $line: [colony name not found]"
done
