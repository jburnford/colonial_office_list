#!/bin/bash

# Phase 1: Smart Correction Strategy
# Only process files worth fixing, skip confirmed re-extraction candidates

echo "================================================================================"
echo "PHASE 1: SMART SAFE CORRECTIONS"
echo "================================================================================"
echo ""
echo "Strategy: Process only fixable files (<500 errors)"
echo "Skipping: 1890, 1920, 1909, 1928, 1949 (confirmed re-extraction needed)"
echo ""

# Create output directory
mkdir -p knowledge_graph_extracts_v2

# Files to SKIP (confirmed re-extraction)
SKIP_FILES="1890|1920|1909|1928|1949"

# Count files
TOTAL=$(ls knowledge_graph_extracts/*_extracted.json | wc -l)
SKIP_COUNT=$(ls knowledge_graph_extracts/*_extracted.json | grep -E "$SKIP_FILES" | wc -l)
PROCESS_COUNT=$((TOTAL - SKIP_COUNT))

echo "Total files: $TOTAL"
echo "Skipping (re-extraction): $SKIP_COUNT"
echo "Processing: $PROCESS_COUNT"
echo ""
echo "================================================================================"
echo ""

# Process all files EXCEPT skip list
python3 correctors/phase1_safe_corrections.py \
    knowledge_graph_extracts/ \
    knowledge_graph_extracts_v2/

echo ""
echo "================================================================================"
echo "NEXT STEPS:"
echo "================================================================================"
echo "1. Review correction log: knowledge_graph_extracts_v2/phase1_correction_log.json"
echo "2. Validate results with: python3 validators/schema_validator.py knowledge_graph_extracts_v2/"
echo "3. Proceed to Phase 2 (LLM agents) for remaining errors"
echo "4. Re-extract the 5 confirmed files with improved methodology"
echo ""
