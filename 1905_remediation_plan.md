# Year 1905 Manual Remediation Plan

## Current Status
**91 entries extracted** (should be ~45-50 legitimate colonies)

## Methodology for Manual Analysis

### Step 1: Identify Legitimate Colony Sections
A legitimate colony has:
- ✅ Standard header: "COLONY_NAME." followed by blank line
- ✅ Standard sections: "Situation and Area", "History", "Constitution", etc.
- ✅ Multi-page content (typically 200+ lines unless very small territory)
- ✅ Ends with standard sections like "Foreign Consuls" or before next colony header

### Step 2: Identify Non-Colony Entries to Remove/Merge
- ❌ **Duplicates**: Same colony appearing multiple times
- ❌ **Admin subsections**: "EXECUTIVE COUNCIL", "LEGISLATIVE COUNCIL", "THE CABINET"
- ❌ **Trade sections**: "EXPORTS", "SHIPPING", "RAILWAYS"
- ❌ **Regional subdivisions**: City/district names that are part of larger colonies
- ❌ **Person names**: Like "LOUIS BOTHA"
- ❌ **Appendices**: "APPENDIX TO PART II"
- ❌ **Advertisement entries**: Bank branches, company listings

### Step 3: Special Cases - Australian Federation
The Commonwealth of Australia (formed 1901) complicates 1905:
- THE COMMONWEALTH = Federal government section
- Individual states (NEW SOUTH WALES, QUEENSLAND, SOUTH AUSTRALIA, TASMANIA, VICTORIA, WESTERN AUSTRALIA) follow
- Need to determine: Are these separate colonies or subsections of THE COMMONWEALTH?
- **Decision needed**: Treat as separate entries or merge under AUSTRALIA?

### Step 4: Verification Checklist for Each Entry
For each of the 91 entries, classify as:
1. **KEEP** - Legitimate colony
2. **MERGE** - Subsection to merge with parent colony
3. **DELETE** - Duplicate, appendix, or non-colony content

## Initial Findings

### Line 8696: BAHAMAS - ✅ LEGITIMATE COLONY
- Has proper header
- Standard sections (Situation/Area, History, Climate, Trade, etc.)
- Clean colony structure

### Line 1063: BARBADOS - ❌ DELETE (Advertisement)
- Part of bank "BRANCHES AND AGENCIES" listing
- Not a colony section

### Lines 2637-2639: AUSTRALIA / THE COMMONWEALTH
- Complex federal structure
- Need to analyze carefully

## Next Steps
1. Read through document systematically
2. Map all 91 entries with line ranges
3. Classify each entry
4. Determine correct boundaries for legitimate colonies
5. Create extraction script

**Status:** Analysis in progress
**Analyst:** Claude (Sonnet 4.5)
**Date:** November 12, 2025
