# 1933 Colonial Office List - Extraction Report

**Extraction Date:** 2025-11-18
**Source File:** historical_document_pipeline/processed_pdfs/colonial-office-list-1933/olmocr_results.md
**Total Colonies Extracted:** 44

## Methodology

All colony boundaries were manually identified by:
1. Locating PART II-C header (line 23437)
2. Identifying PART III start (line 49061)
3. Systematically reading through the section to find all colony headers
4. Cross-referencing with 1932 list (43 colonies) to ensure completeness
5. Handling OCR errors and variations in colony name formatting
6. Identifying subsections, island groupings, and dependencies

## Extraction Summary

Extracted 44 colonies/territories from PART II-C (Colonial Office territories):

- **BAHAMAS** (lines 23439-24017, 579 lines)
- **BARBADOS** (lines 24018-24441, 424 lines)
- **BERMUDA** (lines 24442-24847, 406 lines)
- **BRITISH GUIANA** (lines 24848-25693, 846 lines)
- **BRITISH HONDURAS** (lines 25694-26176, 483 lines)
- **CEYLON** (lines 26177-27423, 1247 lines)
- **CYPRUS** (lines 27424-28192, 769 lines)
- **FALKLAND ISLANDS** (lines 28193-28550, 358 lines)
- **FIJI** (lines 28551-29123, 573 lines)
- **THE GAMBIA** (lines 29124-29493, 370 lines)
- **GIBRALTAR** (lines 29494-29754, 261 lines)
- **THE GOLD COAST** (lines 29755-30862, 1108 lines)
  - Note: Includes Ashanti, Northern Territories, and Togoland subsections
- **HONG KONG** (lines 30863-31698, 836 lines)
- **JAMAICA** (lines 31699-32562, 864 lines)
  - Note: OCR shows '*JAMAICA'
- **CAYMAN ISLANDS** (lines 32563-32621, 59 lines)
  - Note: Dependency of Jamaica
- **TURKS AND CAICOS ISLANDS** (lines 32622-32898, 277 lines)
  - Note: Dependency of Jamaica
- **KENYA** (lines 32899-33905, 1007 lines)
  - Note: Full name: KENYA COLONY AND PROTECTORATE
- **THE LEEWARD ISLANDS** (lines 33906-35320, 1415 lines)
  - Note: OCR shows '*THE LEEWARD ISLANDS.*' - Includes Antigua, Barbuda, St. Christopher-Nevis, Dominica, Montserrat, Virgin Islands
- **STRAITS SETTLEMENTS** (lines 35321-37879, 2559 lines)
  - Note: Includes Singapore, Malacca, Penang, Labuan, Christmas Island
- **UNFEDERATED MALAY STATES** (lines 37880-38518, 639 lines)
  - Note: Includes Johore, Kedah, Perlis, Kelantan, Trengganu
- **BRUNEI** (lines 38519-38573, 55 lines)
  - Note: Protected state
- **MALTA** (lines 38574-39304, 731 lines)
- **MAURITIUS** (lines 39305-40616, 1312 lines)
- **NIGERIA** (lines 40617-41355, 739 lines)
- **NORTHERN RHODESIA** (lines 41356-41952, 597 lines)
- **NYASALAND PROTECTORATE** (lines 41953-42335, 383 lines)
  - Note: OCR shows 'NYASALAND PROTECTORATE.†'
- **PALESTINE** (lines 42336-43093, 758 lines)
- **ST. HELENA** (lines 43094-43299, 206 lines)
- **ASCENSION** (lines 43300-43314, 15 lines)
  - Note: Dependency of St. Helena
- **SEYCHELLES** (lines 43315-43595, 281 lines)
- **SIERRA LEONE** (lines 43596-44038, 443 lines)
- **SOMALILAND PROTECTORATE** (lines 44039-44191, 153 lines)
- **TANGANYIKA TERRITORY** (lines 44192-44984, 793 lines)
  - Note: Mandate territory
- **TRINIDAD AND TOBAGO** (lines 44985-46106, 1122 lines)
  - Note: Includes Tobago subsection
- **UGANDA** (lines 46107-46671, 565 lines)
- **WESTERN PACIFIC** (lines 46672-47162, 491 lines)
  - Note: Includes Gilbert and Ellice Islands, British Solomon Islands, Tonga, New Hebrides, Phoenix Group, Pitcairn
- **THE WINDWARD ISLANDS** (lines 47163-48115, 953 lines)
  - Note: OCR shows '**THE WINDWARD ISLANDS.**' - Includes Grenada, St. Lucia, St. Vincent
- **ZANZIBAR** (lines 48116-48418, 303 lines)
- **NORTH BORNEO** (lines 48419-48635, 217 lines)
  - Note: Under Appendix
- **SARAWAK** (lines 48636-48877, 242 lines)
  - Note: Protected state under Appendix
- **TRANS-JORDAN** (lines 48878-48944, 67 lines)
  - Note: OCR shows '**TRANS-JORDAN.**'
- **ADEN** (lines 48945-49036, 92 lines)
- **TRISTAN DA CUNHA** (lines 49037-49051, 15 lines)
- **MISCELLANEOUS ISLANDS** (lines 49052-49060, 9 lines)
  - Note: Last section before PART III


## Notes

- PART II-C covers colonies administered by the Colonial Office
- PART II-B (Dominions) contains territories under Dominions Office - NOT extracted
- Some colony headers may have OCR errors
- Line number prefixes (format: '12345→') were removed from extracted text
- Island groupings include:
  - **Leeward Islands**: Antigua, Barbuda, St. Christopher-Nevis, Dominica, Montserrat, Virgin Islands
  - **Windward Islands**: Grenada, St. Lucia, St. Vincent
  - **Straits Settlements**: Singapore, Malacca, Penang, Labuan, Christmas Island
  - **Western Pacific**: Gilbert and Ellice Islands, British Solomon Islands, Tonga, New Hebrides, Pitcairn
- Some colonies include administrative subsections (e.g., Gold Coast includes Ashanti and Northern Territories)
- Dependencies extracted separately: Cayman Islands and Turks and Caicos Islands (Jamaica), Ascension (St. Helena)

## Output Files

- Individual colony files: `output_3/1933_manual_parsed/[COLONY_NAME].txt`
- Metadata JSON: `output_3/1933_manual_parsed.json`
- This report: `output_3/1933_PARSING_REPORT.md`

## Comparison with Other Years

- 1932: 43 colonies extracted
- 1933: 44 colonies extracted

### Changes from 1932 to 1933

**New in 1933 (5):**
- **THE WINDWARD ISLANDS** - Consolidated group including Grenada, St. Lucia, St. Vincent (which were separate in 1932)
- **MALTA** - Added to Colonial Office list
- **SARAWAK** - Added as protected state under Appendix
- **UNFEDERATED MALAY STATES** - Added as administrative grouping (Johore, Kedah, Perlis, Kelantan, Trengganu)
- **WESTERN PACIFIC** - Added as administrative grouping (Gilbert & Ellice Islands, British Solomon Islands, Tonga, etc.)

**Removed from 1932 (4):**
- **GRENADA** - Now part of THE WINDWARD ISLANDS grouping
- **ST. LUCIA** - Now part of THE WINDWARD ISLANDS grouping
- **ST. VINCENT** - Now part of THE WINDWARD ISLANDS grouping
- **IRAQ** - Gained independence in 1932; British mandate ended

The count differences reflect administrative reorganization with island group consolidation and the independence of Iraq.
