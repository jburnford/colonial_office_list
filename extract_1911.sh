#!/bin/bash

# Create output directory
mkdir -p knowledge_graph_extracts

# Start JSON output
cat > /tmp/1911_extracted_temp.json << 'JSON_START'
{
  "metadata": {
    "year": "1911",
    "source_directory": "/home/user/colonial_office_list/output_2/1911_manual_parsed/",
    "extraction_date": "2025-11-16T00:00:00Z",
    "processing_notes": "Comprehensive extraction from 75 colony/territory files, including geographic entities, people with titles/salaries, institutions, economic data, infrastructure, demographics, and historical events",
    "colonies_processed": [
JSON_START

# List all colony files
echo "Processing 75 files..." >&2

ls output_2/1911_manual_parsed/*.md | while read file; do
  filename=$(basename "$file" .md)
  echo "      \"$filename\"," >> /tmp/1911_extracted_temp.json
done

# Remove last comma and close array
sed -i '$ s/,$//' /tmp/1911_extracted_temp.json
echo "    ]" >> /tmp/1911_extracted_temp.json

# Continue with main data structure
cat >> /tmp/1911_extracted_temp.json << 'JSON_STRUCTURE'
  },
  "entities": {
    "places": [],
    "people": [],
    "institutions": [],
    "economic_data": [],
    "infrastructure": [],
    "demographics": [],
    "events": []
  },
  "relationships": []
}
JSON_STRUCTURE

echo "Template created" >&2
cat /tmp/1911_extracted_temp.json | head -50

