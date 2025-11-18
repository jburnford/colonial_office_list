# 1932 Colonial Office List - Extraction Report

**Extraction Date:** 2025-11-18
**Source File:** historical_document_pipeline/processed_pdfs/colonial-office-list-1932/olmocr_results.md
**Total Colonies Extracted:** 43

## Methodology

All colony boundaries were manually identified by:
1. Locating PART II-C header (line 23134)
2. Identifying PART III start (line 49220)
3. Systematically reading through the section to find all colony headers
4. Cross-referencing with 1928 list to identify new/missing colonies
5. Handling OCR errors and variations in colony name formatting
6. Manually reading content where headers were missing or ambiguous

## Extraction Summary

Extracted 43 colonies from PART II-C (Colonial Office territories):

- **BAHAMAS** (lines 23136-23518, 383 lines)
  - Note: OCR shows 'BAHAMAS.'
- **BARBADOS** (lines 23519-24162, 644 lines)
  - Note: OCR shows 'BARBADOS.*'
- **BERMUDA** (lines 24163-24739, 577 lines)
  - Note: OCR shows 'BERMUDA.'
- **BRITISH GUIANA** (lines 24740-25622, 883 lines)
- **BRITISH HONDURAS** (lines 25623-26267, 645 lines)
- **CEYLON** (lines 26268-28530, 2263 lines)
- **CYPRUS** (lines 28531-29154, 624 lines)
  - Note: New colony not in 1928 list
- **FALKLAND ISLANDS** (lines 29155-29606, 452 lines)
- **FIJI** (lines 29607-30221, 615 lines)
- **THE GAMBIA** (lines 30222-30641, 420 lines)
- **GIBRALTAR** (lines 30642-30844, 203 lines)
- **THE GOLD COAST** (lines 30845-32151, 1307 lines)
- **HONG KONG** (lines 32152-32778, 627 lines)
- **JAMAICA** (lines 32779-33661, 883 lines)
  - Note: OCR shows '*JAMAICA'
- **CAYMAN ISLANDS** (lines 33662-33728, 67 lines)
- **TURKS AND CAICOS ISLANDS** (lines 33729-33878, 150 lines)
- **KENYA** (lines 33879-34744, 866 lines)
  - Note: Full name: KENYA COLONY AND PROTECTORATE
- **THE LEEWARD ISLANDS** (lines 34745-36946, 2202 lines)
- **MAURITIUS** (lines 36947-37573, 627 lines)
- **NIGERIA** (lines 37574-38642, 1069 lines)
- **NORTHERN RHODESIA** (lines 38643-39379, 737 lines)
  - Note: OCR shows 'NORTHERN RHODESIA.†'
- **NYASALAND PROTECTORATE** (lines 39380-39640, 261 lines)
- **PALESTINE** (lines 39641-40337, 697 lines)
- **ST. HELENA** (lines 40338-40546, 209 lines)
- **ASCENSION** (lines 40547-40561, 15 lines)
- **SEYCHELLES** (lines 40562-40804, 243 lines)
- **SIERRA LEONE** (lines 40805-41133, 329 lines)
- **SOMALILAND PROTECTORATE** (lines 41134-41307, 174 lines)
  - Note: New colony not in 1928 list
- **STRAITS SETTLEMENTS** (lines 41308-44071, 2764 lines)
  - Note: No clear header; starts with historical narrative about Malacca/Penang
- **TANGANYIKA TERRITORY** (lines 44072-44117, 46 lines)
  - Note: OCR shows '†TANGANYIKA TERRITORY.'
- **BRUNEI** (lines 44118-44767, 650 lines)
  - Note: New colony not in 1928 list
- **TRINIDAD AND TOBAGO** (lines 44768-46079, 1312 lines)
  - Note: No clear header; starts mid-sentence; includes TOBAGO subsection at 44977
- **UGANDA** (lines 46080-47193, 1114 lines)
- **GRENADA** (lines 47194-47482, 289 lines)
- **ST. LUCIA** (lines 47483-47767, 285 lines)
  - Note: OCR shows '**ST. LUCIA.**'
- **ST. VINCENT** (lines 47768-48040, 273 lines)
- **ZANZIBAR** (lines 48041-48328, 288 lines)
- **IRAQ** (lines 48329-48509, 181 lines)
- **NORTH BORNEO** (lines 48510-49076, 567 lines)
- **TRANS-JORDAN** (lines 49077-49157, 81 lines)
- **ADEN** (lines 49158-49194, 37 lines)
  - Note: Under MISCELLANEOUS POSSESSIONS section
- **TRISTAN DA CUNHA** (lines 49195-49210, 16 lines)
- **MISCELLANEOUS ISLANDS** (lines 49211-49219, 9 lines)
  - Note: Last colony in PART II-C


## Changes from 1928

### New Colonies in 1932:
- **CYPRUS** (line 28531) - New colony added
- **SOMALILAND PROTECTORATE** (line 41134) - New colony added
- **BRUNEI** (line 44118) - New colony added
- **TANGANYIKA TERRITORY** (line 44072) - Former German colony, now British mandate

### Colonies Removed from 1928:
- **WEIHAIWEI** - No longer in 1932 list (likely returned to China in 1930)

## Notable Issues

- **STRAITS SETTLEMENTS** (line 41308): No clear colony header. Section starts directly with historical narrative about Malacca and Penang.
- **TRINIDAD AND TOBAGO** (line 44768): No clear header. Section starts mid-sentence, possibly due to OCR error. Includes TOBAGO as subsection at line 44977.
- Several colonies have OCR errors in headers (e.g., 'BARBADOS.*' instead of 'BARBADOS')
- Some headers have special characters: '*JAMAICA', '†TANGANYIKA TERRITORY', 'NORTHERN RHODESIA.†'

## Output Files

- Individual colony files: `output_3/1932_manual_parsed/[COLONY_NAME].txt`
- Metadata JSON: `output_3/1932_manual_parsed.json`
- This report: `output_3/1932_PARSING_REPORT.md`

## Comparison with 1928

1928 had 40 colonies in PART II-C (Colonial Office only).
1932 has 43 colonies in PART II-C.

The increase reflects the addition of former German colonies (Tanganyika), protectorates (Somaliland), and other territories (Cyprus, Brunei).
