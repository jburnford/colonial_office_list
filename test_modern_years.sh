#!/bin/bash
# Test modern format parser on years 1932-1936

echo "Testing modern format parser (1932-1936)"
echo "=" | tr '=' '='| head -c 80; echo

success=0
fail=0
total=0

for year in 1932 1933 1934 1936; do

  total=$((total + 1))

  printf "%-6s " "$year"

  # Run parser
  result=$(python3 modern_format_parser.py \
    historical_document_pipeline/processed_pdfs/colonial-office-list-$year/olmocr_results.json \
    -o output/${year}_parsed_modern.json 2>&1)

  # Check for success indicators
  if echo "$result" | grep -q "Exported to"; then
    # Count colonies
    colony_count=$(echo "$result" | grep "Total:" | grep -oE '[0-9]+' | head -1)
    if [ -z "$colony_count" ]; then
      colony_count=$(grep -c '"colony_name"' output/${year}_parsed_modern.json)
    fi

    # Check for negative line counts (failure indicator)
    if grep -q '"-[0-9]' output/${year}_parsed_modern.json; then
      echo "❌ FAIL (negative line counts)"
      fail=$((fail + 1))
    else
      echo "✅ OK ($colony_count colonies)"
      success=$((success + 1))
    fi
  else
    echo "❌ FAIL (parser error)"
    fail=$((fail + 1))
  fi
done

echo
echo "=" | tr '=' '=' | head -c 80; echo
echo "Results: $success/$total successful, $fail failed"
echo "Coverage: $(( success * 100 / total ))%"
