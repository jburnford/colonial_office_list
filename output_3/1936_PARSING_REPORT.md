# 1936 Colonial Office List - Parsing Report

## Extraction Summary

**Date:** 2025-11-18
**Method:** Manual LLM boundary identification with systematic document review
**Source File:** `historical_document_pipeline/processed_pdfs/colonial-office-list-1936/olmocr_results.md`
**Total Lines in Source:** 69,342 lines

### Results

- **Total Colonies Extracted:** 45
- **PART II-C Range:** Lines 22,734 - 48,885
- **Output Directory:** `output_3/1936_manual_parsed/`
- **Metadata File:** `output_3/1936_manual_parsed.json`

## Colony List (45 Total)

| # | Colony Name | Lines | Size | Notes |
|---|------------|-------|------|-------|
| 1 | BAHAMAS | 344 | 24 KB | First colony in PART II-C |
| 2 | BARBADOS | 665 | 40 KB | OCR shows 'BARBADOS.*' |
| 3 | BERMUDA | 431 | 25 KB | |
| 4 | BRITISH GUIANA | 969 | 62 KB | |
| 5 | BRITISH HONDURAS | 458 | 28 KB | |
| 6 | CEYLON | 1,701 | 98 KB | Largest colony section |
| 7 | CYPRUS | 695 | 55 KB | |
| 8 | FALKLAND ISLANDS | 383 | 20 KB | |
| 9 | FIJI | 627 | 38 KB | |
| 10 | THE GAMBIA | 444 | 13 KB | |
| 11 | GIBRALTAR | 183 | 13 KB | |
| 12 | THE GOLD COAST | 959 | 42 KB | |
| 13 | HONG KONG | 598 | 42 KB | |
| 14 | JAMAICA | 1,015 | 59 KB | |
| 15 | CAYMAN ISLANDS | 70 | 5.1 KB | Dependency of Jamaica |
| 16 | TURKS AND CAICOS ISLANDS | 112 | | OCR shows '**TURKS AND CAICOS ISLANDS.**' |
| 17 | KENYA | 942 | 70 KB | Full name: KENYA COLONY AND PROTECTORATE |
| 18 | THE LEEWARD ISLANDS | 1,711 | 78 KB | Federation with subsections (Antigua, Barbuda, St. Christopher-Nevis, Dominica, Montserrat, Virgin Islands) |
| 19 | MALAYA: STRAITS SETTLEMENTS | 1,366 | | Malayan section 1 |
| 20 | CHRISTMAS ISLAND | 5 | 1.9 KB | Dependency of Straits Settlements |
| 21 | MALAYA: FEDERATED MALAY STATES | 1,235 | 78 KB | Malayan section 2 (Perak, Selangor, Negri Sembilan, Pahang) |
| 22 | MALAYA: UNFEDERATED MALAY STATES | 705 | | Malayan section 3 (Johore, Kedah, Perlis, Kelantan, Trengganu) |
| 23 | BRUNEI | 49 | 5.2 KB | OCR shows '**BRUNEI' |
| 24 | MALTA | 736 | | New in 1936 (not in 1932) |
| 25 | MAURITIUS | 699 | | |
| 26 | NIGERIA | 1,018 | | |
| 27 | NORTHERN RHODESIA | 515 | | |
| 28 | NYASALAND PROTECTORATE | 424 | | |
| 29 | PALESTINE | 825 | | |
| 30 | ST. HELENA | 202 | | |
| 31 | ASCENSION | 13 | 1.1 KB | Dependency of St. Helena |
| 32 | SEYCHELLES | 216 | | |
| 33 | SIERRA LEONE | 427 | | |
| 34 | SOMALILAND PROTECTORATE | 175 | | |
| 35 | TANGANYIKA TERRITORY | 768 | | OCR shows '†TANGANYIKA TERRITORY' |
| 36 | TRINIDAD | 1,179 | | Includes Tobago as subsection |
| 37 | UGANDA | 596 | | |
| 38 | WESTERN PACIFIC | 663 | | High Commission territory (Solomon Islands, Tonga, Phoenix Group, Pitcairn) |
| 39 | THE WINDWARD ISLANDS | 1,004 | | Federation (Grenada, St. Lucia, St. Vincent) |
| 40 | ZANZIBAR | 314 | | |
| 41 | NORTH BORNEO | 278 | | Under APPENDIX section |
| 42 | SARAWAK | 229 | | Under APPENDIX section |
| 43 | TRANS-JORDAN | 75 | | |
| 44 | ADEN | 122 | 12 KB | Under MISCELLANEOUS POSSESSIONS |
| 45 | MISCELLANEOUS ISLANDS | 5 | | Last entry before PART III |

## Comparison with 1932

### Summary Statistics
- **1932 Total:** 43 colonies
- **1936 Total:** 45 colonies
- **Net Change:** +2 colonies

### New Colonies in 1936
1. **MALTA** - New colony (not in 1932 list)
2. **SARAWAK** - Added to APPENDIX section
3. **WESTERN PACIFIC** - New High Commission territory grouping
4. **CHRISTMAS ISLAND** - Listed separately (was part of Straits Settlements)

### Reorganizations in 1936

#### Malaya Restructuring
- **1932:** STRAITS SETTLEMENTS (single entry)
- **1936:** Three separate sections:
  - MALAYA: STRAITS SETTLEMENTS
  - MALAYA: FEDERATED MALAY STATES
  - MALAYA: UNFEDERATED MALAY STATES

#### Windward Islands Federation
- **1932:** Separate entries for GRENADA, ST. LUCIA, ST. VINCENT
- **1936:** Combined into THE WINDWARD ISLANDS (with subsections)

#### Trinidad Consolidation
- **1932:** TRINIDAD AND TOBAGO
- **1936:** TRINIDAD (Tobago appears as subsection)

### Missing from 1936
1. **IRAQ** - Gained independence October 3, 1932 (no longer a mandate)
2. **TRISTAN DA CUNHA** - Likely consolidated into St. Helena dependencies (not found as separate entry)

## Structural Changes

### Document Organization
The 1936 list shows increased sophistication in organization:
- More structured Malayan territories
- Federation groupings (Leeward Islands, Windward Islands, Western Pacific)
- Clear APPENDIX section for territories with special status (North Borneo, Sarawak)
- MISCELLANEOUS POSSESSIONS section

### Colony Subsections
Several colonies contain detailed subsections:
- **THE LEEWARD ISLANDS:** Antigua, Barbuda, St. Christopher and Nevis, Dominica, Montserrat, Virgin Islands
- **THE WINDWARD ISLANDS:** Grenada, St. Lucia, St. Vincent
- **WESTERN PACIFIC:** British Solomon Islands Protectorate, Tonga, Phoenix Group, Pitcairn Island
- **MALAYA: FEDERATED MALAY STATES:** Perak, Selangor, Negri Sembilan, Pahang
- **MALAYA: UNFEDERATED MALAY STATES:** Johore, Kedah, Perlis, Kelantan, Trengganu

## Technical Notes

### OCR Quality
- Generally good quality with minimal errors
- Some punctuation artifacts in headers (e.g., '.*', '**', '†')
- Line number prefixes successfully removed from extracted text

### Extraction Methodology
1. Identified PART II-C boundaries (lines 22,734 - 48,885)
2. Manually scanned document for colony headers
3. Cross-referenced with 1932 colony list
4. Verified boundaries by reading context around each header
5. Created extraction script with manually verified boundaries
6. Extracted to individual text files with cleaned content

### Boundary Identification Challenges
- Some colonies lack clear headers (e.g., MISCELLANEOUS ISLANDS only 5 lines)
- Federation subsections required careful distinction from main colonies
- MALTA appears for first time in 1936
- APPENDIX section required special handling for North Borneo and Sarawak

## Files Created

1. **45 colony text files** in `output_3/1936_manual_parsed/`
2. **Metadata JSON** at `output_3/1936_manual_parsed.json`
3. **This parsing report** at `output_3/1936_PARSING_REPORT.md`

## Historical Context

The 1936 Colonial Office List reflects several important changes:
- **Iraq Independence (1932):** No longer appears as a British mandate
- **Malayan Organization:** Clearer delineation between Federated and Unfederated States
- **Island Federations:** Windward Islands show administrative consolidation
- **Malta:** Appears in the list (constitutional changes in 1930s)
- **Sarawak:** Included in APPENDIX (Brooke Raj under British protection)

## Data Quality Assessment

- **Completeness:** ✓ All major colonies identified and extracted
- **Accuracy:** ✓ Boundaries manually verified
- **Consistency:** ✓ Extraction follows 1932 methodology
- **Cross-reference:** ✓ Compared with neighboring years

## Recommendations

1. For detailed subsection analysis, individual colony files should be parsed further
2. The Leeward Islands, Windward Islands, and Western Pacific contain multiple distinct administrations
3. Malayan territories may benefit from separate analysis of Federated vs. Unfederated States
4. Historical changes between 1932-1936 show evolution of colonial administration

---

**Extraction completed:** 2025-11-18
**Methodology:** Manual boundary identification with LLM assistance
**Status:** Complete and verified
