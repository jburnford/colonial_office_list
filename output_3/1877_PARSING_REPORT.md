# 1877 Colonial Office List - Parsing Report

## Extraction Summary

- **Year:** 1877
- **Parser:** Manual LLM boundary identification
- **Total entries:** 47
- **Full colony sections:** 34
- **Redirect entries:** 13
- **Failed extractions:** 0
- **Output directory:** `/home/user/colonial_office_list/output_3/1877_manual_parsed`
- **Metadata file:** `/home/user/colonial_office_list/output_3/1877_manual_parsed.json`

## Methodology

Colonies were extracted using manual boundary identification:

1. Read the entire 1877 OCR results file in sections
2. Manually identified colony section headers by searching for patterns
3. Determined section boundaries by reading actual content
4. Cross-referenced with 1867 and 1878 lists to verify completeness
5. Created extraction script with verified boundaries
6. Extracted each colony to individual text files
7. Removed line number prefixes from extracted text

## Colonies Extracted

| # | Colony Name | Lines | Characters | Type |
|---|-------------|-------|------------|------|
| 1 | ANTIGUA | 3 | 40 | Redirect |
| 2 | ANGUILLA | 3 | 43 | Redirect |
| 3 | BAHAMAS | 263 | 11,127 | Full |
| 4 | BARBADOS | 6 | 49 | Redirect |
| 5 | BERMUDAS | 231 | 12,356 | Full |
| 6 | BRITISH_COLUMBIA_AND_VANCOUVER_ISLAND | 3 | 73 | Redirect |
| 7 | BRITISH_HONDURAS | 3 | 44 | Redirect |
| 8 | BRITISH_GUIANA | 636 | 29,021 | Full |
| 9 | DOMINION_OF_CANADA | 1867 | 99,422 | Full |
| 10 | CAPE_OF_GOOD_HOPE | 1289 | 50,034 | Full |
| 11 | CEYLON | 571 | 26,657 | Full |
| 12 | DOMINICA | 4 | 42 | Redirect |
| 13 | FALKLAND_ISLANDS | 120 | 6,955 | Full |
| 14 | FIJI | 55 | 7,254 | Full |
| 15 | GIBRALTAR | 83 | 4,847 | Full |
| 16 | THE_GOLD_COAST_COLONY | 575 | 32,262 | Full |
| 17 | GRENADA | 6 | 48 | Redirect |
| 18 | GRIQUALAND_WEST | 314 | 17,816 | Full |
| 19 | HELIGOLAND | 38 | 2,407 | Full |
| 20 | HONDURAS | 176 | 11,665 | Full |
| 21 | HONG_KONG | 265 | 12,936 | Full |
| 22 | JAMAICA | 666 | 28,892 | Full |
| 23 | LABUAN | 96 | 4,379 | Full |
| 24 | THE_LEEWARD_ISLANDS | 1248 | 58,861 | Full |
| 25 | MALTA | 403 | 13,970 | Full |
| 26 | MAURITIUS | 735 | 32,102 | Full |
| 27 | NATAL | 328 | 19,814 | Full |
| 28 | NEVIS | 3 | 38 | Redirect |
| 29 | NEWFOUNDLAND | 664 | 33,352 | Full |
| 30 | NEW_SOUTH_WALES | 620 | 15,996 | Full |
| 31 | NEW_ZEALAND | 571 | 22,146 | Full |
| 32 | QUEENSLAND | 350 | 28,333 | Full |
| 33 | ST_VINCENT | 6 | 90 | Redirect |
| 34 | SIERRA_LEONE | 3 | 55 | Redirect |
| 35 | ST_CHRISTOPHER_NEVIS_AND_ANGUILLA | 3 | 69 | Redirect |
| 36 | ST_HELENA | 105 | 4,235 | Full |
| 37 | SOUTH_AUSTRALIA | 748 | 26,824 | Full |
| 38 | STRAITS_SETTLEMENTS | 341 | 17,831 | Full |
| 39 | TASMANIA | 308 | 16,170 | Full |
| 40 | TOBAGO | 4 | 42 | Redirect |
| 41 | TRINIDAD | 553 | 23,207 | Full |
| 42 | TURKS_AND_CAICOS_ISLANDS | 80 | 3,780 | Full |
| 43 | VICTORIA | 727 | 24,645 | Full |
| 44 | VIRGIN_ISLANDS | 4 | 48 | Redirect |
| 45 | WESTERN_AUSTRALIA | 220 | 10,581 | Full |
| 46 | WEST_AFRICA_SETTLEMENTS | 393 | 18,897 | Full |
| 47 | THE_WINDWARD_ISLANDS | 1259 | 77,123 | Full |

## Notes

### Redirect Entries

Some colonies are redirect entries pointing to their parent colony or a grouped section:

- **ANTIGUA**: Redirect to Leeward Islands, p. 89
- **ANGUILLA**: Redirect to Leeward Islands, page 95
- **BARBADOS**: Redirect to Windward Islands, p. 161
- **BRITISH_COLUMBIA_AND_VANCOUVER_ISLAND**: Redirect to Dominion of Canada, p. 29
- **BRITISH_HONDURAS**: Redirect to Honduras, page 75
- **DOMINICA**: Redirect to Leeward Islands, p. 96
- **GRENADA**: Redirect to Windward Islands, p. 169
- **NEVIS**: Redirect to Leeward Islands, p. 94
- **ST_VINCENT**: Redirect to Windward Islands, p. 166
- **SIERRA_LEONE**: Redirect to West African Settlements, p. 158
- **ST_CHRISTOPHER_NEVIS_AND_ANGUILLA**: Redirect to Leeward Islands, p. 86
- **TOBAGO**: Redirect to Windward Islands
- **VIRGIN_ISLANDS**: Redirect to Leeward Islands

### Colony Groupings

- **Leeward Islands** contains: Antigua, Montserrat, St. Christopher, Nevis, Dominica, Anguilla, Virgin Islands
- **Windward Islands** contains: Barbados, Grenada, St. Vincent, St. Lucia, Tobago
- **West Africa Settlements** contains: Sierra Leone, Gambia
- **Gold Coast Colony** includes Lagos

### Section Boundaries

- Colonies section starts at line 1306 (header: 'COLONIES')
- Colonies section ends at line 18252 (followed by 'PART III. EMIGRATION' at line 18253)
- All colony boundaries were manually verified by reading the OCR content
- Line numbers in the source file use the format '  123→text'
