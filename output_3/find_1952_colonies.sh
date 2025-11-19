#!/bin/bash

OCR_FILE="/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1952/olmocr_results.md"

echo "Searching for colony headers in 1952..."
echo ""

colonies=(
  "ADEN"
  "BAHAMA ISLANDS"
  "BARBADOS"
  "BERMUDA"
  "BRITISH GUIANA"
  "BRITISH HONDURAS"
  "BRUNEI"
  "CYPRUS"
  "FALKLAND ISLANDS"
  "FIJI"
  "THE GAMBIA"
  "GAMBIA"
  "GIBRALTAR"
  "THE GOLD COAST"
  "GOLD COAST"
  "HONG KONG"
  "JAMAICA"
  "KENYA"
  "THE LEEWARD ISLANDS"
  "LEEWARD ISLANDS"
  "FEDERATION OF MALAYA"
  "MALAYA"
  "MALTA"
  "MAURITIUS"
  "NIGERIA"
  "NORTH BORNEO"
  "NORTHERN RHODESIA"
  "NYASALAND PROTECTORATE"
  "NYASALAND"
  "ST. HELENA"
  "SARAWAK"
  "SEYCHELLES"
  "SIERRA LEONE"
  "SINGAPORE AND DEPENDENCIES"
  "SINGAPORE"
  "SOMALILAND PROTECTORATE"
  "SOMALILAND"
  "TANGANYIKA"
  "TRINIDAD AND TOBAGO"
  "TRINIDAD"
  "UGANDA"
  "WESTERN PACIFIC"
  "THE WINDWARD ISLANDS"
  "WINDWARD ISLANDS"
  "ZANZIBAR"
  "MISCELLANEOUS ISLANDS"
)

for colony in "${colonies[@]}"; do
  result=$(grep -n "^${colony}$" "$OCR_FILE" 2>/dev/null)
  if [ -n "$result" ]; then
    echo "$result" | while read line; do
      echo "$colony: $line"
    done
  fi
done
