# 1934 Colonial Office List - Extraction Report

**Extraction Date:** 2025-11-18
**Source File:** historical_document_pipeline/processed_pdfs/colonial-office-list-1934/olmocr_results.md
**Total Colonies Extracted:** 50

## Methodology

All colony boundaries were manually identified by:
1. Locating PART II-C header (line 22219)
2. Identifying PART III start (line 47341)
3. Systematically reading through the section to find all colony headers
4. Cross-referencing with 1932 list to ensure completeness
5. Handling OCR errors and variations in colony name formatting
6. Identifying subsections, island groupings, and Malayan territories
7. Searching for specific patterns and short lines with capital letters

## Key Findings

- **IRAQ**: Not present in 1934 list (gained independence in 1932)
- **HONG KONG**: Found without header at line 29770 - unusual format
- **Malaya**: Complex structure with Straits Settlements, Federated States, and Unfederated States
- **Protected States**: Brunei, North Borneo, Sarawak, Tonga, Zanzibar
- **Mandate Territories**: Palestine, Tanganyika, Trans-Jordan
- **Dependencies**: Cayman Islands, Turks and Caicos (under Jamaica), Ascension (under St. Helena)

## Extraction Summary

Extracted 50 main colonies/territories from PART II-C (Colonial Office territories):

- **BAHAMAS** (lines 22221-22635, 415 lines)
- **BARBADOS** (lines 22636-23299, 664 lines)
  - Note: OCR shows 'BARBADOS.*'
- **BERMUDA** (lines 23300-23714, 415 lines)
- **BRITISH GUIANA** (lines 23715-24564, 850 lines)
- **BRITISH HONDURAS** (lines 24565-25096, 532 lines)
- **CEYLON** (lines 25097-26577, 1481 lines)
  - Note: Large colony with multiple provinces
- **CYPRUS** (lines 26578-27315, 738 lines)
- **FALKLAND ISLANDS** (lines 27316-27633, 318 lines)
- **FIJI** (lines 27634-28183, 550 lines)
- **THE GAMBIA** (lines 28184-28624, 441 lines)
- **GIBRALTAR** (lines 28625-28814, 190 lines)
- **THE GOLD COAST** (lines 28815-29769, 955 lines)
  - Note: Includes Ashanti, Northern Territories, and Togoland sections
- **HONG KONG** (lines 29770-30410, 641 lines)
  - Note: No header line - starts directly with description
- **JAMAICA** (lines 30411-31371, 961 lines)
  - Note: OCR shows '*JAMAICA.*'
- **CAYMAN ISLANDS** (lines 31372-31433, 62 lines)
  - Note: Dependency of Jamaica
- **TURKS AND CAICOS ISLANDS** (lines 31434-31636, 203 lines)
  - Note: OCR shows '**TURKS AND CAICOS ISLANDS.**', dependency of Jamaica
- **KENYA** (lines 31637-32806, 1170 lines)
  - Note: Full name: KENYA COLONY AND PROTECTORATE
- **THE LEEWARD ISLANDS** (lines 32807-34176, 1370 lines)
  - Note: Includes Antigua, Barbuda, Dominica, Montserrat, Virgin Islands
- **MALAYA: STRAITS SETTLEMENTS** (lines 34177-35306, 1130 lines)
  - Note: Includes Singapore, Malacca, Penang, Labuan, Christmas Island
- **MALAYA: FEDERATED MALAY STATES** (lines 35307-36596, 1290 lines)
  - Note: Includes Perak, Selangor, Negri Sembilan, Pahang
- **MALAY STATES NOT INCLUDED IN THE FEDERATION** (lines 36597-36600, 4 lines)
  - Note: Header for unfederated states
- **JOHORE** (lines 36601-36907, 307 lines)
  - Note: Unfederated Malay State
- **KEDAH** (lines 36908-37011, 104 lines)
  - Note: Unfederated Malay State
- **PERLIS** (lines 37012-37111, 100 lines)
  - Note: OCR shows 'MALAYA : STATE OF PERLIS', unfederated state
- **KELANTAN** (lines 37112-37230, 119 lines)
  - Note: Unfederated Malay State
- **TRENGGANU** (lines 37231-37254, 24 lines)
  - Note: Unfederated Malay State
- **BRUNEI** (lines 37255-37304, 50 lines)
  - Note: Protected state
- **MALTA** (lines 37305-37984, 680 lines)
- **MAURITIUS** (lines 37985-39023, 1039 lines)
- **NIGERIA** (lines 39024-39693, 670 lines)
- **NORTHERN RHODESIA** (lines 39694-40199, 506 lines)
  - Note: OCR shows 'NORTHERN RHODESIA.†'
- **NYASALAND PROTECTORATE** (lines 40200-40614, 415 lines)
  - Note: OCR shows 'NYASALAND PROTECTORATE.†'
- **PALESTINE** (lines 40615-41384, 770 lines)
  - Note: Mandate territory
- **ST. HELENA** (lines 41385-41564, 180 lines)
- **ASCENSION** (lines 41565-41577, 13 lines)
  - Note: Dependency of St. Helena
- **SEYCHELLES** (lines 41578-41908, 331 lines)
- **SIERRA LEONE** (lines 41909-42370, 462 lines)
- **SOMALILAND PROTECTORATE** (lines 42371-42554, 184 lines)
- **TANGANYIKA TERRITORY** (lines 42555-43266, 712 lines)
  - Note: OCR shows '**TANGANYIKA TERRITORY.**', mandate territory
- **TRINIDAD AND TOBAGO** (lines 43267-44301, 1035 lines)
  - Note: OCR shows 'TRINIDAD.', includes Tobago subsection
- **UGANDA** (lines 44302-45211, 910 lines)
- **TONGA** (lines 45212-45362, 151 lines)
  - Note: Protected state
- **THE WINDWARD ISLANDS** (lines 45363-46316, 954 lines)
  - Note: OCR shows '**THE WINDWARD ISLANDS.**', includes Grenada, St. Lucia, St. Vincent
- **ZANZIBAR** (lines 46317-46620, 304 lines)
  - Note: Protectorate
- **NORTH BORNEO** (lines 46621-46898, 278 lines)
  - Note: Protected state
- **SARAWAK** (lines 46899-47144, 246 lines)
  - Note: Protected state
- **TRANS-JORDAN** (lines 47145-47213, 69 lines)
  - Note: Mandate territory
- **ADEN** (lines 47214-47316, 103 lines)
  - Note: Under MISCELLANEOUS POSSESSIONS section
- **TRISTAN DA CUNHA** (lines 47317-47333, 17 lines)
  - Note: Under MISCELLANEOUS POSSESSIONS
- **MISCELLANEOUS ISLANDS** (lines 47334-47340, 7 lines)
  - Note: Last entry in PART II-C


## Comparison with 1932

- 1932: 43 colonies extracted
- 1934: 50 colonies extracted

The 1934 list has 7 more entries (50 total vs 43 in 1932) primarily due to:
1. Separate listing of unfederated Malay States (Johore, Kedah, Perlis, Kelantan, Trengganu)
2. Separate section for "Malay States Not Included in the Federation"
3. Different organizational structure for Malayan territories

Notable differences:
- IRAQ removed (gained independence 1932)
- HONG KONG has no header line - starts directly with descriptive text
- More detailed breakdown of Malayan territories
- Addition of Hong Kong (previously may have been in a different section or missing in 1932)

## Output Files

- Individual colony files: `output_3/1934_manual_parsed/[COLONY_NAME].txt`
- Metadata JSON: `output_3/1934_manual_parsed.json`
- This report: `output_3/1934_PARSING_REPORT.md`
