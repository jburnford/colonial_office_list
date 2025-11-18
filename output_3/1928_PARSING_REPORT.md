# 1928 Colonial Office List - Extraction Report

**Extraction Date:** 2025-11-18
**Source File:** historical_document_pipeline/processed_pdfs/colonial-office-list-1928/olmocr_results.md
**Total Colonies Extracted:** 40

## Methodology

All colony boundaries were manually identified by:
1. Locating PART II-C header (line 26391)
2. Identifying PART III start (line 54680)
3. Systematically reading through the section to find all colony headers
4. Cross-referencing with 1927 list to ensure completeness
5. Handling OCR errors and variations in colony name formatting

## Extraction Summary

Extracted 40 colonies from PART II-C (Colonial Office territories):

- **BAHAMAS** (lines 26393-26767, 375 lines)
- **BARBADOS** (lines 26768-27671, 904 lines)
  - Note: OCR shows 'BarBADOS.*'
- **BERMUDA** (lines 27672-28084, 413 lines)
- **BRITISH GUIANA** (lines 28085-29312, 1228 lines)
- **BRITISH HONDURAS** (lines 29313-29908, 596 lines)
- **CEYLON** (lines 29909-32307, 2399 lines)
- **FALKLAND ISLANDS** (lines 32308-32585, 278 lines)
- **FIJI** (lines 32586-33362, 777 lines)
- **THE GAMBIA** (lines 33363-34104, 742 lines)
- **GIBRALTAR** (lines 34105-34544, 440 lines)
- **THE GOLD COAST** (lines 34545-35901, 1357 lines)
  - Note: Full name: THE GOLD COAST COLONY
- **HONG KONG** (lines 35902-36584, 683 lines)
- **JAMAICA** (lines 36585-37492, 908 lines)
  - Note: OCR shows '*JAMAICA.'
- **CAYMAN ISLANDS** (lines 37493-37541, 49 lines)
- **TURKS AND CAICOS ISLANDS** (lines 37542-37730, 189 lines)
- **KENYA** (lines 37731-38582, 852 lines)
  - Note: Full name: KENYA COLONY AND PROTECTORATE
- **THE LEEWARD ISLANDS** (lines 38583-41265, 2683 lines)
  - Note: OCR shows '*THE LEEWARD ISLANDS.*'
- **MAURITIUS** (lines 41266-42030, 765 lines)
- **NIGERIA** (lines 42031-43407, 1377 lines)
- **NORTHERN RHODESIA** (lines 43408-43863, 456 lines)
- **NYASALAND PROTECTORATE** (lines 43864-44238, 375 lines)
  - Note: OCR shows 'NYASALAND PROTECTORATE.†'
- **PALESTINE** (lines 44239-44801, 563 lines)
- **ST. HELENA** (lines 44802-45013, 212 lines)
- **ASCENSION** (lines 45014-45031, 18 lines)
- **SEYCHELLES** (lines 45032-45272, 241 lines)
- **SIERRA LEONE** (lines 45273-45998, 726 lines)
- **STRAITS SETTLEMENTS** (lines 45999-49476, 3478 lines)
- **TRINIDAD AND TOBAGO** (lines 49477-50623, 1147 lines)
  - Note: Includes TRINIDAD (49479) and TOBAGO subsections
- **UGANDA** (lines 50624-51102, 479 lines)
- **WEIHAIWEI** (lines 51103-52052, 950 lines)
- **ST. LUCIA** (lines 52053-52386, 334 lines)
- **ST. VINCENT** (lines 52387-52678, 292 lines)
- **GRENADA** (lines 52679-53554, 876 lines)
- **ZANZIBAR** (lines 53555-53827, 273 lines)
- **IRAQ** (lines 53828-53998, 171 lines)
- **NORTH BORNEO** (lines 53999-54579, 581 lines)
- **TRANS-JORDAN** (lines 54580-54632, 53 lines)
- **ADEN** (lines 54633-54655, 23 lines)
- **TRISTAN DA CUNHA** (lines 54656-54670, 15 lines)
- **MISCELLANEOUS ISLANDS** (lines 54671-54679, 9 lines)
  - Note: Last colony in PART II-C


## Notes

- PART II-C covers colonies administered by the Colonial Office
- PART II-B (Dominions) contains BASUTOLAND, BECHUANALAND, SWAZILAND, SOUTHERN RHODESIA (lines 25066-25711) - NOT extracted as they are High Commission Territories
- Some colony headers have OCR errors (e.g., 'BarBADOS.*' instead of 'BARBADOS')
- Line number prefixes (format: '12345→') were removed from extracted text

## Output Files

- Individual colony files: `output_3/1928_manual_parsed/[COLONY_NAME].txt`
- Metadata JSON: `output_3/1928_manual_parsed.json`
- This report: `output_3/1928_PARSING_REPORT.md`

## Comparison with 1927

1927 had 46 colonies (including Dominions Office territories).
1928 has 40 colonies in PART II-C (Colonial Office only).

The decrease is due to administrative restructuring where some territories
(BASUTOLAND, SWAZILAND, SOUTHERN RHODESIA, etc.) were moved to High Commissioner/Dominions Office oversight.
