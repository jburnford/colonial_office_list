# Colonial Office List 1922 - Parsing Report

## Summary

**Parsing Date:** November 18, 2025  
**Source Document:** `historical_document_pipeline/processed_pdfs/colonial-office-list-1922/olmocr_results.md`  
**Output Directory:** `output_3/1922_manual_parsed/`  
**Total Colonies Identified:** 40

## Colonies Extracted

1. **AUSTRALIA** (Commonwealth) - 7,947 lines
2. **BAHAMAS** - 449 lines
3. **BARBADOS** - 570 lines
4. **BERMUDA** - 359 lines
5. **BRITISH GUIANA** - 1,014 lines
6. **BRITISH HONDURAS** - 360 lines
7. **CANADA** (Dominion) - 3,486 lines
8. **CEYLON** - 1,356 lines
9. **CYPRUS** - 638 lines
10. **FALKLAND ISLANDS** - 300 lines
11. **FIJI** - 656 lines
12. **GAMBIA** (The) - 478 lines
13. **GIBRALTAR** - 310 lines
14. **GOLD COAST** (The) - 1,062 lines
15. **HONG KONG** - 600 lines
16. **JAMAICA** - 1,201 lines
17. **KENYA** (Colony and Protectorate) - 766 lines
18. **LEEWARD ISLANDS** (The) - 1,649 lines
19. **MALTA** - 585 lines
20. **MAURITIUS** - 1,303 lines
21. **NEW ZEALAND** - 1,349 lines
22. **NIGERIA** - 695 lines
23. **NYASALAND PROTECTORATE** - 479 lines
24. **SEYCHELLES** - 256 lines
25. **SIERRA LEONE** - 472 lines
26. **SOMALILAND PROTECTORATE** - 168 lines
27. **SOUTH AFRICA** (Union of) - 2,333 lines
28. **BASUTOLAND** - 171 lines
29. **BECHUANALAND PROTECTORATE** - 112 lines
30. **SWAZILAND** - 828 lines
31. **NORTHERN RHODESIA** - 60 lines
32. **STRAITS SETTLEMENTS** - 836 lines
33. **FEDERATED MALAY STATES** (The) - 944 lines
34. **TANGANYIKA TERRITORY** - 463 lines
35. **TRINIDAD AND TOBAGO** - 1,676 lines
36. **UGANDA** - 424 lines
37. **WEIHAIWEI** - 64 lines
38. **WESTERN PACIFIC** (High Commission) - 303 lines
39. **WINDWARD ISLANDS** (The) - 2,205 lines
40. **ADEN** - 1,001 lines

## Historical Context: 1922 Independence Events

### Egypt (February 28, 1922)
- **Status:** Egypt declared independent on February 28, 1922
- **Impact on Colonial Office List:** Egypt does NOT appear in the 1922 Colonial Office List as a colony
- **Note:** Britain had established a protectorate over Egypt in 1914, but Egypt was granted nominal independence in 1922, though Britain retained control over defense, foreign affairs, and the Suez Canal until 1956

### Irish Free State (December 6, 1922)
- **Status:** Irish Free State officially established December 6, 1922 (after publication of this list)
- **Impact on Colonial Office List:** Ireland does NOT appear in the 1922 Colonial Office List
- **Note:** The Anglo-Irish Treaty was signed December 6, 1921, and the Irish Free State came into being on December 6, 1922, ending direct British rule over most of Ireland. Northern Ireland remained part of the United Kingdom.

## Post-WWI Mandates

Several territories appear in this 1922 list as newly acquired mandates under the League of Nations following Germany's defeat in WWI:

1. **TANGANYIKA TERRITORY** - Former German East Africa, now under British mandate
2. **CAMEROONS** - Mentioned within Gold Coast section as British Cameroons
3. **TOGOLAND** - British-administered portion (French administered the larger portion)
4. **WESTERN SAMOA** - Under New Zealand mandate (mentioned in New Zealand section)
5. **SOUTH WEST AFRICA** - Under South African mandate (mentioned in South Africa section)
6. **NEW GUINEA TERRITORY** - Under Australian mandate (mentioned in Australia section)
7. **NAURU** - Joint British-Australian-New Zealand mandate (mentioned in Western Pacific section)

## Notable Observations

1. **Dominion Status:** Canada, Australia, New Zealand, and South Africa appear with enhanced self-governing status as Dominions
2. **Protectorates vs. Colonies:** Several territories are designated as "Protectorates" (Kenya, Nyasaland, Somaliland, Bechuanaland) rather than full colonies
3. **Island Groups:** Several Caribbean and Pacific island groups are administered collectively (Leeward Islands, Windward Islands, Western Pacific)
4. **Comprehensive Coverage:** The 1922 list includes detailed administrative, financial, and personnel information for each territory

## Files Generated

- **40 individual colony text files** in `output_3/1922_manual_parsed/`
- **Summary JSON file:** `output_3/1922_manual_parsed.json`
- **This report:** `output_3/1922_PARSING_REPORT.md`

## Technical Notes

- Source OCR file: 59,136 lines total
- Colony sections begin at line 4,542 (Australia)
- Last colony section ends around line 44,469 (Aden)
- Each colony file contains the complete text from the original OCR, preserving all administrative details, personnel lists, financial data, and historical information
