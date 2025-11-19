# 1951 Colonial Office List - Parsing Report

**Extraction Date:** 2025-11-19 01:16:43

**Source File:** `/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1951/olmocr_results.md`

**Total Colonies Extracted:** 37

## Colony List

| # | Colony Name | Start Line | End Line | Lines | Characters |
|---|-------------|------------|----------|-------|------------|
| 1 | Aden | 5176 | 6251 | 1076 | 82,175 |
| 2 | Bahamas | 6252 | 6448 | 197 | 4,838 |
| 3 | Barbados | 6449 | 6981 | 533 | 35,913 |
| 4 | Bermuda | 6982 | 7542 | 561 | 32,401 |
| 5 | British Guiana | 7543 | 8478 | 936 | 76,651 |
| 6 | British Honduras | 8479 | 8954 | 476 | 28,506 |
| 7 | Brunei | 8955 | 9215 | 261 | 16,211 |
| 8 | Cyprus | 9216 | 10028 | 813 | 70,906 |
| 9 | Falkland Islands | 10029 | 10412 | 384 | 23,346 |
| 10 | Fiji | 10413 | 11527 | 1115 | 90,709 |
| 11 | Gambia | 11528 | 11719 | 192 | 6,130 |
| 12 | Gibraltar | 11720 | 12846 | 1127 | 120,657 |
| 13 | Gold Coast | 12847 | 13766 | 920 | 43,300 |
| 14 | Hong Kong | 13767 | 14697 | 931 | 66,762 |
| 15 | Jamaica | 14698 | 16035 | 1338 | 95,392 |
| 16 | Kenya | 16036 | 17232 | 1197 | 87,102 |
| 17 | Leeward Islands | 17233 | 18374 | 1142 | 59,227 |
| 18 | Federation of Malaya | 18375 | 19829 | 1455 | 116,638 |
| 19 | Malta | 19830 | 20394 | 565 | 33,769 |
| 20 | Mauritius | 20395 | 21393 | 999 | 65,427 |
| 21 | Nigeria | 21394 | 23173 | 1780 | 154,989 |
| 22 | North Borneo | 23174 | 23660 | 487 | 26,424 |
| 23 | Northern Rhodesia | 23661 | 24796 | 1136 | 78,917 |
| 24 | Nyasaland Protectorate | 24797 | 25301 | 505 | 41,441 |
| 25 | St. Helena | 25302 | 25660 | 359 | 21,222 |
| 26 | Sarawak | 25661 | 26218 | 558 | 44,960 |
| 27 | Seychelles | 26219 | 26634 | 416 | 24,082 |
| 28 | Sierra Leone | 26635 | 27415 | 781 | 49,926 |
| 29 | Singapore | 27416 | 28564 | 1149 | 80,782 |
| 30 | Somaliland Protectorate | 28565 | 28846 | 282 | 20,976 |
| 31 | Tanganyika | 28847 | 29554 | 708 | 59,829 |
| 32 | Trinidad and Tobago | 29555 | 30475 | 921 | 60,184 |
| 33 | Uganda | 30476 | 31230 | 755 | 53,243 |
| 34 | Western Pacific | 31231 | 32638 | 1408 | 103,042 |
| 35 | Windward Islands | 32639 | 33669 | 1031 | 49,825 |
| 36 | Zanzibar | 33670 | 34087 | 418 | 33,193 |
| 37 | Miscellaneous Islands | 34088 | 34417 | 330 | 19,964 |

## Extraction Method

Manual boundary identification was used to extract colonies from the 1951 Colonial Office List.

Each colony section was identified by:
1. Reading the OCR results file
2. Manually locating each colony section based on headers and content
3. Verifying boundaries against the table of contents
4. Cross-referencing with 1950 (37 colonies) to ensure no colonies were missed

## Files Generated

- `/home/user/colonial_office_list/output_3/1951_manual_parsed/` - Directory containing 37 individual colony text files
- `/home/user/colonial_office_list/output_3/1951_manual_parsed.json` - JSON metadata with extraction details
- `/home/user/colonial_office_list/output_3/1951_PARSING_REPORT.md` - This parsing report
