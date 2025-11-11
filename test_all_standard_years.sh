#!/bin/bash
# Comprehensive test of V5 parser on all standard format years (1888-1930)

echo "Testing V5 parser across all standard format years (1888-1930)"
echo "=" | tr '=' '='| head -c 80; echo

success=0
fail=0
total=0

for year in 1888 1889 1890 1894 1896 1897 1898 1899 1900 \
            1905 1906 1907 1908 1909 1910 1911 1912 1913 1914 1915 \
            1917 1918 1919 1920 1921 1922 1923 1924 1925 1927 1928 1929 1930; do

  total=$((total + 1))

  printf "%-6s " "$year"

  # Run parser
  result=$(python3 colonial_office_parser_v5.py \
    historical_document_pipeline/processed_pdfs/colonial-office-list-$year/olmocr_results.json \
    -o output/${year}_parsed_v5_final.json 2>&1)

  # Check for success indicators
  if echo "$result" | grep -q "Exported to"; then
    # Count colonies
    colony_count=$(echo "$result" | grep "Total colonies parsed" | grep -oE '[0-9]+' | head -1)
    if [ -z "$colony_count" ]; then
      colony_count=$(grep -c '"colony_name"' output/${year}_parsed_v5_final.json)
    fi

    # Check for negative line counts (failure indicator)
    if grep -q '"-[0-9]' output/${year}_parsed_v5_final.json; then
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
