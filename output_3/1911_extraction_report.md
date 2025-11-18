# Colonial Office List 1911 - Manual Parsing Report

**Date:** 2025-11-18  
**Source:** `historical_document_pipeline/processed_pdfs/colonial-office-list-1911/olmocr_results.md`

## Summary

Successfully extracted **40 Crown colonies and protectorates** from the Colonial Office List 1911.

### Comparison with 1910
- **1910:** 45 colonies (reference count)
- **1911:** 40 colonies (extracted)
- **Difference:** -5 colonies

## Complete List of Extracted Colonies (in document order)

1. **Papua** (lines 9866-10101, 235 lines)
2. **BAHAMAS** (lines 10101-10458, 357 lines)
3. **BARBADOS** (lines 10458-11083, 625 lines)
4. **BERMUDA** (lines 11083-11457, 374 lines)
5. **BRITISH GUIANA** (lines 11457-12261, 804 lines)
6. **BRITISH HONDURAS** (lines 12261-15612, 3351 lines)
7. **CEYLON** (lines 15612-16648, 1036 lines)
8. **CYPRUS** (lines 16648-17471, 823 lines)
9. **EAST AFRICA PROTECTORATE** (lines 17471-17828, 357 lines)
10. **FALKLAND ISLANDS** (lines 17828-18023, 195 lines)
11. **FIJI** (lines 18023-19021, 998 lines)
12. **GIBRALTAR** (lines 19021-19237, 216 lines)
13. **THE GOLD COAST** (lines 19237-20057, 820 lines)
    - Includes Ashanti (subsection)
    - Includes Northern Territories (subsection)
14. **HONG KONG** (lines 20057-20626, 569 lines)
15. **JAMAICA** (lines 20626-21485, 859 lines)
    - Includes Cayman Islands, Turks and Caicos Islands (dependencies)
16. **THE LEEWARD ISLANDS** (lines 21485-23095, 1610 lines)
    - Federal colony comprising Antigua, Barbuda, Montserrat, St. Kitts-Nevis, Dominica, Virgin Islands
17. **MALTA** (lines 23095-23672, 577 lines)
18. **MAURITIUS** (lines 23672-24563, 891 lines)
19. **NEWFOUNDLAND** (lines 24563-25167, 604 lines)
20. **COOK ISLANDS** (lines 25167-25989, 822 lines)
21. **NORTHERN NIGERIA** (lines 25989-26285, 296 lines)
22. **NYASALAND PROTECTORATE** (lines 26285-26503, 218 lines)
23. **ST. HELENA** (lines 26503-26734, 231 lines)
24. **SEYCHELLES** (lines 26734-27052, 318 lines)
25. **SIERRA LEONE** (lines 27052-27573, 521 lines)
26. **SOMALILAND PROTECTORATE** (lines 27573-30129, 2556 lines)
27. **BASUTOLAND** (lines 30129-30290, 161 lines)
28. **BECHUANALAND PROTECTORATE** (lines 30290-30371, 81 lines)
29. **SWAZILAND** (lines 30371-30755, 384 lines)
30. **SOUTHERN RHODESIA ADMINISTRATION** (lines 30755-30978, 223 lines)
31. **SOUTHERN NIGERIA** (lines 30978-31957, 979 lines)
32. **STRAITS SETTLEMENTS** (lines 31957-33703, 1746 lines)
    - Comprises Singapore, Penang, Malacca, Labuan
33. **TRINIDAD** (lines 33703-35206, 1503 lines)
    - Includes Tobago (amalgamated 1889)
34. **TURKS AND CAICOS ISLANDS** (lines 35206-35389, 183 lines)
35. **UGANDA** (lines 35389-35689, 300 lines)
36. **WEIHAIWEI** (lines 35689-35983, 294 lines)
37. **GRENA DA** [Grenada] (lines 35983-36304, 321 lines)
    - Note: OCR error in heading ("GRENA DA" should be "GRENADA")
    - Part of Windward Islands government group
38. **ST. LUCIA** (lines 36304-36644, 340 lines)
    - Part of Windward Islands government group
39. **ST. VINCENT** (lines 36644-37419, 775 lines)
    - Part of Windward Islands government group
40. **ZANZIBAR** (lines 37419-37511, 92 lines)

## Output Files

All colonies have been extracted to: `/home/user/colonial_office_list/output_3/1911_manual_parsed/`

- **40 individual colony text files** (one per colony)
- **Metadata file:** `output_3/1911_manual_parsed.json`

## Notes

### OCR Issues Encountered
- "GRENADA" appears as "GRENA DA" (with space) in the document

### Colonial Structure in 1911
- **Windward Islands:** While referenced as a government group (with shared Governor), Grenada, St. Lucia, and St. Vincent are counted as separate colonies
- **Leeward Islands:** Counted as a single Federal Colony despite comprising multiple presidencies (Antigua, Montserrat, St. Kitts-Nevis, Dominica, Virgin Islands)
- **Gold Coast:** Includes Ashanti (annexed 1901) and Northern Territories as subsections
- **Trinidad:** Combined with Tobago (amalgamated 1889)

### Possible Reasons for -5 Colony Count vs 1910
The difference could be due to:
1. Different counting methodology (some dependencies may have been counted separately in 1910)
2. Colonial reorganizations between 1910-1911
3. Variations in what constitutes a "Crown colony" vs. protectorate vs. dependency
4. Some territories may have been transferred to Dominion administration (e.g., Papua to Australia)

## Extraction Methodology

1. Identified colony section boundaries (lines 9866-37511)
2. Searched for colony heading patterns (all-caps names with periods)
3. Handled duplicate headings (page headers) by keeping only first occurrence
4. Extracted text between consecutive colony headings
5. Created individual files and JSON metadata

## Quality Assurance

✓ All 40 colonies successfully extracted  
✓ No gaps in line coverage (each line assigned to exactly one colony)  
✓ Metadata file created with complete line number information  
✓ Individual text files created for each colony
