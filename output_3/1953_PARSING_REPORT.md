# 1953 Colonial Office List - Parsing Report

**Extraction Date:** 2025-11-19T01:20:25.424826
**Source File:** `/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1953/olmocr_results.md`
**Total Source Lines:** 20,638
**Total Colonies Extracted:** 37

---

## Extraction Summary

| # | Colony Name | Start Line | End Line | Lines | Size (bytes) | Filename |
|---|-------------|------------|----------|-------|--------------|----------|
| 1 | ADEN | 3002 | 3383 | 382 | 30,400 | `aden.txt` |
| 2 | BAHAMA_ISLANDS | 3384 | 3697 | 314 | 21,733 | `bahama_islands.txt` |
| 3 | BARBADOS | 3698 | 3948 | 251 | 17,151 | `barbados.txt` |
| 4 | BERMUDA | 3949 | 4173 | 225 | 16,196 | `bermuda.txt` |
| 5 | BRITISH_GUIANA | 4174 | 4459 | 286 | 23,041 | `british_guiana.txt` |
| 6 | BRITISH_HONDURAS | 4460 | 4691 | 232 | 18,728 | `british_honduras.txt` |
| 7 | BRUNEI | 4692 | 4841 | 150 | 14,888 | `brunei.txt` |
| 8 | CYPRUS | 4842 | 5140 | 299 | 24,331 | `cyprus.txt` |
| 9 | FALKLAND_ISLANDS_AND_DEPENDENCIES | 5141 | 5359 | 219 | 13,849 | `falkland_islands_and_dependencies.txt` |
| 10 | FIJI_AND_PITCAIRN_ISLANDS | 5360 | 5607 | 248 | 23,985 | `fiji_and_pitcairn_islands.txt` |
| 11 | GAMBIA | 5608 | 5881 | 274 | 21,337 | `gambia.txt` |
| 12 | GIBRALTAR | 5882 | 6039 | 158 | 10,458 | `gibraltar.txt` |
| 13 | GOLD_COAST | 6040 | 6470 | 431 | 33,488 | `gold_coast.txt` |
| 14 | HONG_KONG | 6471 | 6832 | 362 | 20,786 | `hong_kong.txt` |
| 15 | JAMAICA | 6833 | 7434 | 602 | 46,299 | `jamaica.txt` |
| 16 | KENYA | 7435 | 7868 | 434 | 32,877 | `kenya.txt` |
| 17 | LEEWARD_ISLANDS | 7869 | 8482 | 614 | 35,939 | `leeward_islands.txt` |
| 18 | FEDERATION_OF_MALAYA | 8483 | 9096 | 614 | 41,711 | `federation_of_malaya.txt` |
| 19 | MALTA | 9097 | 9480 | 384 | 23,852 | `malta.txt` |
| 20 | MAURITIUS | 9481 | 9802 | 322 | 23,783 | `mauritius.txt` |
| 21 | NIGERIA | 9803 | 10185 | 383 | 28,374 | `nigeria.txt` |
| 22 | NORTH_BORNEO | 10186 | 10438 | 253 | 21,415 | `north_borneo.txt` |
| 23 | NORTHERN_RHODESIA | 10439 | 10893 | 455 | 28,401 | `northern_rhodesia.txt` |
| 24 | NYASALAND_PROTECTORATE | 10894 | 11177 | 284 | 22,412 | `nyasaland_protectorate.txt` |
| 25 | ST_HELENA | 11178 | 11380 | 203 | 16,644 | `st_helena.txt` |
| 26 | SARAWAK | 11381 | 11672 | 292 | 23,442 | `sarawak.txt` |
| 27 | SEYCHELLES | 11673 | 11857 | 185 | 14,545 | `seychelles.txt` |
| 28 | SIERRA_LEONE | 11858 | 12158 | 301 | 24,994 | `sierra_leone.txt` |
| 29 | SINGAPORE_AND_DEPENDENCIES | 12159 | 12493 | 335 | 26,823 | `singapore_and_dependencies.txt` |
| 30 | SOMALILAND_PROTECTORATE | 12494 | 12669 | 176 | 12,189 | `somaliland_protectorate.txt` |
| 31 | TANGANYIKA | 12670 | 13129 | 460 | 33,891 | `tanganyika.txt` |
| 32 | TONGA | 13130 | 13234 | 105 | 9,361 | `tonga.txt` |
| 33 | TRINIDAD_AND_TOBAGO | 13235 | 13549 | 315 | 26,627 | `trinidad_and_tobago.txt` |
| 34 | UGANDA | 13550 | 13829 | 280 | 27,161 | `uganda.txt` |
| 35 | WESTERN_PACIFIC_HIGH_COMMISSION | 13830 | 14226 | 397 | 35,036 | `western_pacific_high_commission.txt` |
| 36 | WINDWARD_ISLANDS | 14227 | 14995 | 769 | 57,562 | `windward_islands.txt` |
| 37 | ZANZIBAR | 14996 | 15599 | 604 | 38,385 | `zanzibar.txt` |

---

## Statistics

- **Total lines extracted:** 12,598
- **Total size:** 942,094 bytes (920.0 KB)
- **Average lines per colony:** 340.5
- **Average size per colony:** 25462.0 bytes

- **Largest colony (by lines):** WINDWARD_ISLANDS (769 lines)
- **Smallest colony (by lines):** TONGA (105 lines)

---

## Methodology

This extraction was performed using **manually identified colony section boundaries**.
Each colony section was located by systematically reading through the OCR file
and identifying section headers and content boundaries.

### Process:

1. Systematic reading of the 1953 OCR file in sections
2. Manual identification of colony section start lines
3. Determination of section boundaries (end lines)
4. Extraction of text between boundaries
5. Removal of OCR line number prefixes (format: `line_number→content`)
6. Writing to individual colony files

---

## Notes

- All line numbers are based on the source OCR file line numbering
- Some colonies include dependencies and sub-territories
- Section boundaries were verified by reading content to ensure complete coverage
- The extraction includes all text from start line (inclusive) to end line (exclusive)
