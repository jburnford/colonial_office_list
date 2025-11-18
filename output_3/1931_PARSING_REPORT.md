# 1931 Colonial Office List - Extraction Report

**Extraction Date:** 2025-11-18
**Source File:** historical_document_pipeline/processed_pdfs/colonial-office-list-1931/olmocr_results.md
**Total Colonies Extracted:** 36

## Methodology

All colony boundaries were manually identified by:
1. Locating PART II-C header (line 25064)
2. Identifying PART III start (line 52580)
3. Systematically reading through the section to find all colony headers
4. Cross-referencing with 1928 and 1930 lists to ensure completeness
5. Handling OCR errors and variations in colony name formatting
6. Identifying subsections and island groupings

## Extraction Summary

Extracted 36 main colonies/territories from PART II-C (Colonial Office territories):

- **BAHAMAS** (lines 25066-25431, 366 lines)
- **BARBADOS** (lines 25432-26088, 657 lines)
- **BERMUDA** (lines 26089-26540, 452 lines)
- **BRITISH GUIANA** (lines 26541-27353, 813 lines)
- **BRITISH HONDURAS** (lines 27354-27994, 641 lines)
- **CEYLON** (lines 27995-30020, 2026 lines)
- **FALKLAND ISLANDS** (lines 30021-30388, 368 lines)
- **FIJI** (lines 30389-31216, 828 lines)
- **THE GAMBIA** (lines 31217-31635, 419 lines)
- **GIBRALTAR** (lines 31636-31839, 204 lines)
- **THE GOLD COAST** (lines 31840-33198, 1359 lines)
  - Note: Includes Ashanti subsection
- **HONG KONG** (lines 33199-34114, 916 lines)
- **JAMAICA** (lines 34115-35724, 1610 lines)
  - Note: Includes Cayman Islands and Turks and Caicos
- **KENYA** (lines 35725-36325, 601 lines)
- **THE LEEWARD ISLANDS** (lines 36326-38101, 1776 lines)
  - Note: Includes Antigua, Barbuda, St. Christopher-Nevis, Dominica, Montserrat, Virgin Islands
- **MALTA** (lines 38102-38845, 744 lines)
- **MAURITIUS** (lines 38846-39585, 740 lines)
  - Note: Includes Rodrigues
- **NIGERIA** (lines 39586-40846, 1261 lines)
- **NORTHERN RHODESIA** (lines 40847-41602, 756 lines)
- **NYASALAND PROTECTORATE** (lines 41603-41940, 338 lines)
- **PALESTINE** (lines 41941-42558, 618 lines)
- **ST. HELENA** (lines 42559-42769, 211 lines)
  - Note: Includes Ascension
- **SEYCHELLES** (lines 42770-43017, 248 lines)
- **SIERRA LEONE** (lines 43018-43921, 904 lines)
- **STRAITS SETTLEMENTS** (lines 43922-46574, 2653 lines)
  - Note: Includes Singapore, Malacca, Penang, Labuan
- **UNFEDERATED MALAY STATES** (lines 46575-48351, 1777 lines)
  - Note: Includes Johore, Kedah, Kelantan, Trengganu, Perlis
- **TRINIDAD AND TOBAGO** (lines 48352-49405, 1054 lines)
  - Note: Includes Tobago subsection
- **UGANDA** (lines 49406-50460, 1055 lines)
- **TONGA** (lines 50461-50589, 129 lines)
- **THE WINDWARD ISLANDS** (lines 50590-51415, 826 lines)
  - Note: Includes Grenada, St. Lucia, St. Vincent
- **ZANZIBAR** (lines 51416-51705, 290 lines)
- **IRAQ** (lines 51706-51900, 195 lines)
- **NORTH BORNEO** (lines 51901-52110, 210 lines)
- **SARAWAK** (lines 52111-52431, 321 lines)
- **TRANS-JORDAN** (lines 52432-52512, 81 lines)
- **ADEN** (lines 52513-52579, 67 lines)


## Notes

- PART II-C covers colonies administered by the Colonial Office
- PART II-B (Dominions) contains territories under Dominions Office - NOT extracted
- Some colony headers may have OCR errors
- Line number prefixes (format: '12345→') were removed from extracted text
- Island groupings include:
  - **Leeward Islands**: Antigua, Barbuda, St. Christopher-Nevis, Dominica, Montserrat, Virgin Islands
  - **Windward Islands**: Grenada, St. Lucia, St. Vincent
  - **Straits Settlements**: Singapore, Malacca, Penang, Labuan
- Some colonies include administrative subsections (e.g., Gold Coast includes Ashanti)

## Output Files

- Individual colony files: `output_3/1931_manual_parsed/[COLONY_NAME].txt`
- Metadata JSON: `output_3/1931_manual_parsed.json`
- This report: `output_3/1931_PARSING_REPORT.md`

## Comparison with Other Years

- 1928: 40 colonies extracted
- 1931: 36 colonies extracted

The count includes main administrative units and may differ from other years due to administrative reorganization.
