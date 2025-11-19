# 1950 Colonial Office List - Extraction Report

**Generated:** 2025-11-19
**Source File:** `/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1950/olmocr_results.md`
**Total Colonies Extracted:** 37

## Methodology

All colony boundaries were manually identified by:
1. Reading the OCR results file for 1950
2. Examining the table of contents (lines 4472-4508)
3. Verifying each colony section start by reading actual content
4. Cross-referencing with 1949 colonies to ensure completeness
5. Manually locating colonies with non-standard headers (MALTA, FALKLAND ISLANDS, etc.)

## Extracted Colonies

| # | Colony Name | Lines | Total Lines | Filename |
|---|-------------|-------|-------------|----------|
|  1 | ADEN                                          |  4509- 5262 |  754 | `aden.txt` |
|  2 | BAHAMA ISLANDS                                |  5263- 5792 |  530 | `bahama_islands.txt` |
|  3 | BARBADOS                                      |  5793- 6267 |  475 | `barbados.txt` |
|  4 | BERMUDA                                       |  6268- 6805 |  538 | `bermuda.txt` |
|  5 | BRITISH GUIANA                                |  6806- 7788 |  983 | `british_guiana.txt` |
|  6 | BRITISH HONDURAS                              |  7789- 8234 |  446 | `british_honduras.txt` |
|  7 | BRUNEI                                        |  8235- 8486 |  252 | `brunei.txt` |
|  8 | CYPRUS                                        |  8487- 9245 |  759 | `cyprus.txt` |
|  9 | FALKLAND ISLANDS AND DEPENDENCIES             |  9246- 9661 |  416 | `falkland_islands_and_dependencies.txt` |
| 10 | FIJI                                          |  9662-10419 |  758 | `fiji.txt` |
| 11 | THE GAMBIA                                    | 10420-10962 |  543 | `gambia.txt` |
| 12 | GIBRALTAR                                     | 10963-11324 |  362 | `gibraltar.txt` |
| 13 | THE GOLD COAST                                | 11325-12750 | 1426 | `gold_coast.txt` |
| 14 | HONG KONG                                     | 12751-13723 |  973 | `hong_kong.txt` |
| 15 | JAMAICA                                       | 13724-14856 | 1133 | `jamaica.txt` |
| 16 | KENYA                                         | 14857-16003 | 1147 | `kenya.txt` |
| 17 | THE LEEWARD ISLANDS                           | 16004-17107 | 1104 | `leeward_islands.txt` |
| 18 | FEDERATION OF MALAYA                          | 17108-18119 | 1012 | `federation_of_malaya.txt` |
| 19 | MALTA                                         | 18120-18792 |  673 | `malta.txt` |
| 20 | MAURITIUS                                     | 18793-19707 |  915 | `mauritius.txt` |
| 21 | NIGERIA                                       | 19708-21443 | 1736 | `nigeria.txt` |
| 22 | NORTH BORNEO                                  | 21444-21913 |  470 | `north_borneo.txt` |
| 23 | NORTHERN RHODESIA                             | 21914-23000 | 1087 | `northern_rhodesia.txt` |
| 24 | NYASALAND PROTECTORATE                        | 23001-23557 |  557 | `nyasaland_protectorate.txt` |
| 25 | ST. HELENA                                    | 23558-23923 |  366 | `st_helena.txt` |
| 26 | SARAWAK                                       | 23924-24475 |  552 | `sarawak.txt` |
| 27 | SEYCHELLES                                    | 24476-24887 |  412 | `seychelles.txt` |
| 28 | SIERRA LEONE                                  | 24888-25566 |  679 | `sierra_leone.txt` |
| 29 | SINGAPORE AND DEPENDENCIES                    | 25567-26601 | 1035 | `singapore_and_dependencies.txt` |
| 30 | SOMALILAND PROTECTORATE                       | 26602-26921 |  320 | `somaliland_protectorate.txt` |
| 31 | TANGANYIKA                                    | 26922-27658 |  737 | `tanganyika.txt` |
| 32 | TRINIDAD AND TOBAGO                           | 27659-28586 |  928 | `trinidad_and_tobago.txt` |
| 33 | UGANDA                                        | 28587-29378 |  792 | `uganda.txt` |
| 34 | GILBERT AND ELLICE ISLANDS COLONY             | 29379-30230 |  852 | `gilbert_and_ellice_islands.txt` |
| 35 | THE WINDWARD ISLANDS                          | 30231-31510 | 1280 | `windward_islands.txt` |
| 36 | ZANZIBAR                                      | 31511-31945 |  435 | `zanzibar.txt` |
| 37 | MISCELLANEOUS ISLANDS                         | 31946-32910 |  965 | `miscellaneous_islands.txt` |

## Summary Statistics

- **Total Colonies:** 37
- **Total Lines Extracted:** 28,402
- **Total Characters:** 2,019,316
- **Total Words:** 311,921
- **Average Lines per Colony:** 767.6

## Extraction Details

### Output Directory
`/home/user/colonial_office_list/output_3/1950_manual_parsed/`

### Metadata File
`/home/user/colonial_office_list/output_3/1950_manual_parsed.json`

### Individual Colony Files
Each colony was extracted to a separate text file with:
- Line number prefixes removed
- Original formatting preserved
- UTF-8 encoding

## Notes

1. **WESTERN PACIFIC HIGH COMMISSION**: This territory appears as "GILBERT AND ELLICE ISLANDS COLONY" (line 29379) in the document, which is part of the Western Pacific High Commission territories.

2. **Header Variations**: Some colonies had non-standard headers:
   - FALKLAND ISLANDS: Header was "Falkland Islands" (title case) at line 9246
   - MALTA: Header was "**MALTA**" (bold markdown) at line 18120
   - SINGAPORE: Full header was "SINGAPORE AND ITS DEPENDENCIES" at line 25567

3. **Part III Boundary**: Part III (Colonial Service section) begins at line 32911, marking the end of colony descriptions.

## Comparison with 1949

The 1950 list has 37 territories, similar to 1949. The main differences:
- Territory names and boundaries remain largely consistent
- Some administrative updates reflected in the content
- Gilbert and Ellice Islands explicitly named in 1950

## Issues Encountered

None. All 37 territories successfully extracted with manually verified boundaries.
