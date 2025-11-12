# Year 1905 - Complete Entry Classification
## Systematic Analysis of 91 Extracted "Colonies"

**Goal:** Identify ~45-50 legitimate colonies from 91 entries
**Method:** Manual verification by reading OCR source at each line range
**Date:** November 12, 2025

---

## Entry List with Initial Classification

### AUSTRALIA FEDERATION COMPLEX (Lines 2639-8695)

| # | Name | Lines | Count | Initial Classification |
|---|------|-------|-------|----------------------|
| 1 | THE COMMONWEALTH | 2639-3449 | 811 | ⚠️ VERIFY - Federal Australia govt |
| 2 | NEW SOUTH WALES | 3451-4830 | 1380 | ✅ KEEP - Australian state/colony |
| 3 | QUEENSLAND | 4832-5097 | 266 | ⚠️ VERIFY - Seems short for full colony |
| 4 | **EXPORTS** | 5099-5485 | 387 | ❌ DELETE - Trade section |
| 5 | SOUTH AUSTRALIA | 5487-5741 | 255 | ⚠️ VERIFY - Seems short |
| 6 | **THE PARLIAMENT** | 5743-6311 | 569 | ❌ DELETE - Admin subsection |
| 7 | TASMANIA | 6313-6999 | 687 | ✅ KEEP - Australian state/colony |
| 8 | VICTORIA | 7000-7266 | 267 | ⚠️ VERIFY - Seems short |
| 9 | **PARLIAMENT OF VICTORIA** | 7268-8695 | 1428 | ❌ MERGE - Part of VICTORIA |

### CARIBBEAN AND ATLANTIC (Lines 8696-10164)

| # | Name | Lines | Count | Initial Classification |
|---|------|-------|-------|----------------------|
| 10 | BAHAMAS | 8696-8996 | 301 | ✅ KEEP - Verified colony |
| 11 | BARBADOS | 8998-9611 | 614 | ✅ KEEP - Should be colony (verify) |
| 12 | BERMUDA | 9613-9842 | 230 | ✅ KEEP - Colony (1st instance) |
| 13 | **BERMUDA** | 9843-9977 | 135 | ❌ MERGE - Duplicate, merge with #12 |
| 14 | BRITISH CENTRAL AFRICA PROTECTORATE | 9978-10164 | 187 | ✅ KEEP |

### SOUTH AMERICA / SHIPPING (Lines 10166-10798)

| # | Name | Lines | Count | Initial Classification |
|---|------|-------|-------|----------------------|
| 15 | BRITISH GUIANA | 10166-10323 | 158 | ✅ KEEP |
| 16 | **SHIPPING ENTERED AND CLEARED** | 10325-10798 | 474 | ❌ DELETE - Trade section |

### CENTRAL AMERICA (Lines 10799-11133)

| # | Name | Lines | Count | Initial Classification |
|---|------|-------|-------|----------------------|
| 17 | BRITISH HONDURAS | 10799-10925 | 127 | ✅ KEEP (1st instance) |
| 18 | **BRITISH HONDURAS** | 10926-11133 | 208 | ❌ MERGE - Duplicate, merge with #17 |

### CANADA DOMINION COMPLEX (Lines 11135-14059)

| # | Name | Lines | Count | Initial Classification |
|---|------|-------|-------|----------------------|
| 19 | THE DOMINION | 11135-11506 | 372 | ⚠️ VERIFY - Federal Canada govt |
| 20 | **THE CABINET** | 11508-11609 | 102 | ❌ DELETE - Admin subsection |
| 21 | **THE SENATE OF CANADA** | 11611-11677 | 67 | ❌ DELETE - Admin subsection |
| 22 | PROVINCE OF ONTARIO | 11679-12163 | 485 | ⚠️ VERIFY - Canadian province |
| 23 | NORTH-WEST TERRITORIES | 12165-12254 | 90 | ⚠️ VERIFY - Canadian territory |
| 24 | **RAILWAYS AND CANALS** | 12256-12430 | 175 | ❌ DELETE - Infrastructure section |
| 25 | ONTARIO AND QUEBEC (OLD CANADA) | 12432-12534 | 103 | ❌ DELETE - Historical reference |
| 26 | **EXECUTIVE COUNCIL** | 12536-12831 | 296 | ❌ DELETE - Admin subsection |
| 27 | **EXECUTIVE COUNCIL** | 12833-13034 | 202 | ❌ DELETE - Duplicate admin |
| 28 | NOVA SCOTIA | 13036-13270 | 235 | ⚠️ VERIFY - Canadian province |
| 29 | NEW BRUNSWICK | 13272-13431 | 160 | ⚠️ VERIFY - Canadian province |
| 30 | MANITOBA AND KEEWATIN | 13433-13582 | 150 | ⚠️ VERIFY - Canadian province |
| 31 | BRITISH COLUMBIA | 13583-13805 | 223 | ⚠️ VERIFY - Canadian province |
| 32 | PRINCE EDWARD ISLAND | 13806-13916 | 111 | ⚠️ VERIFY - Canadian province |
| 33 | THE NORTH-WEST TERRITORIES | 13917-14059 | 143 | ⚠️ VERIFY - Duplicate of #23? |

### SOUTH AFRICA COMPLEX (Lines 14061-17395)

| # | Name | Lines | Count | Initial Classification |
|---|------|-------|-------|----------------------|
| 34 | CAPE OF GOOD HOPE | 14061-14459 | 399 | ✅ KEEP (1st instance) |
| 35 | **CAPE OF GOOD HOPE** | 14460-16313 | 1854 | ❌ MERGE - Duplicate, merge with #34 |
| 36 | **ADELAIDE** | 16315-16431 | 117 | ❌ DELETE - City, not colony |
| 37 | **DURBANVILLE** | 16433-16519 | 87 | ❌ DELETE - Town in Cape Colony |
| 38 | **KEISKAMA HOEK** | 16521-16831 | 311 | ❌ DELETE - District in Cape Colony |
| 39 | **URBAN POLICE DISTRICT, CAPE TOWN** | 16833-17075 | 243 | ❌ DELETE - District in Cape Colony |
| 40 | **RAILWAYS** | 17077-17395 | 319 | ❌ DELETE - Infrastructure section |

### INDIAN OCEAN (Lines 17397-18842)

| # | Name | Lines | Count | Initial Classification |
|---|------|-------|-------|----------------------|
| 41 | CEYLON | 17397-17632 | 236 | ✅ KEEP |
| 42 | **EXPORTS** | 17634-18211 | 578 | ❌ DELETE - Trade section (#2) |
| 43 | CYPRUS | 18213-18842 | 630 | ✅ KEEP |

### SOUTH ATLANTIC / PACIFIC (Lines 18844-19859)

| # | Name | Lines | Count | Initial Classification |
|---|------|-------|-------|----------------------|
| 44 | FALKLAND ISLANDS | 18844-18967 | 124 | ✅ KEEP |
| 45 | **EXPORTS** | 18969-19031 | 63 | ❌ DELETE - Trade section (#3) |
| 46 | FIJI | 19033-19206 | 174 | ✅ KEEP (1st instance) |
| 47 | **FIJI** | 19207-19277 | 71 | ❌ MERGE - Duplicate, merge with #46 |
| 48 | **FIJI** | 19278-19859 | 582 | ❌ MERGE - Duplicate, merge with #46 |

### MEDITERRANEAN / WEST AFRICA (Lines 19861-21194)

| # | Name | Lines | Count | Initial Classification |
|---|------|-------|-------|----------------------|
| 49 | GIBRALTAR | 19861-20077 | 217 | ✅ KEEP |
| 50 | THE GOLD COAST COLONY | 20079-20145 | 67 | ⚠️ VERIFY - Seems very short |
| 51 | **MAIL AND STEAMSHIP SERVICES** | 20147-20313 | 167 | ❌ DELETE - Transport section |
| 52 | THE NORTHERN TERRITORIES | 20315-21194 | 880 | ⚠️ VERIFY - Part of Gold Coast? |

### JAMAICA / LABUAN (Lines 21196-22714)

| # | Name | Lines | Count | Initial Classification |
|---|------|-------|-------|----------------------|
| 53 | JAMAICA | 21196-21400 | 205 | ✅ KEEP |
| 54 | **LEGISLATIVE COUNCIL** | 21402-21989 | 588 | ❌ DELETE - Admin subsection |
| 55 | LABUAN | 21990-22714 | 725 | ✅ KEEP |

### LEEWARD ISLANDS (Lines 22715-23981)

| # | Name | Lines | Count | Initial Classification |
|---|------|-------|-------|----------------------|
| 56 | THE LEEWARD ISLANDS | 22715-22897 | 183 | ✅ KEEP - Federation |
| 57 | ANTIGUA | 22899-23203 | 305 | ⚠️ VERIFY - Part of Leewards or separate? |
| 58 | **EXPORTS** | 23205-23408 | 204 | ❌ DELETE - Trade section (#4) |
| 59 | DOMINICA | 23410-23659 | 250 | ⚠️ VERIFY - Part of Leewards or separate? |
| 60 | MONTSERRAT | 23661-23833 | 173 | ⚠️ VERIFY - Part of Leewards or separate? |
| 61 | VIRGIN ISLANDS | 23835-23981 | 147 | ⚠️ VERIFY - Part of Leewards or separate? |

### MALTA / MAURITIUS / NATAL (Lines 23983-26235)

| # | Name | Lines | Count | Initial Classification |
|---|------|-------|-------|----------------------|
| 62 | MALTA | 23983-24581 | 599 | ✅ KEEP |
| 63 | MAURITIUS | 24582-24951 | 370 | ✅ KEEP |
| 64 | **COUNCIL OF GOVERNMENT** | 24953-25255 | 303 | ❌ DELETE - Admin subsection (Mauritius) |
| 65 | **ROYAL ALFRED OBSERVATORY** | 25257-25471 | 215 | ❌ DELETE - Institution (Mauritius) |
| 66 | NATAL | 25473-25608 | 136 | ✅ KEEP |
| 67 | **DURBAN** | 25610-26235 | 626 | ❌ MERGE - City in Natal, merge with #66 |

### NEW ZEALAND / NIGERIA (Lines 26236-27836)

| # | Name | Lines | Count | Initial Classification |
|---|------|-------|-------|----------------------|
| 68 | NEWFOUNDLAND | 26236-26661 | 426 | ✅ KEEP |
| 69 | NEW ZEALAND | 26663-26981 | 319 | ✅ KEEP |
| 70 | PUKAPUKA, OR DANGER ISLAND, AND NASSAU | 26983-27508 | 526 | ⚠️ VERIFY - Part of NZ? |
| 71 | **HEADQUARTERS STAFF** | 27510-27657 | 148 | ❌ DELETE - Military admin |
| 72 | NORTHERN NIGERIA | 27658-27836 | 179 | ✅ KEEP |

### ORANGE RIVER / SOUTHERN AFRICA (Lines 27838-30061)

| # | Name | Lines | Count | Initial Classification |
|---|------|-------|-------|----------------------|
| 73 | ORANGE RIVER COLONY | 27838-28644 | 807 | ✅ KEEP |
| 74 | SEYCHELLES | 28646-28983 | 338 | ✅ KEEP |
| 75 | SIERRA LEONE | 28984-29427 | 444 | ✅ KEEP |
| 76 | BASUTOLAND | 29429-29562 | 134 | ✅ KEEP |
| 77 | BECHUANALAND PROTECTORATE | 29564-30061 | 498 | ✅ KEEP |
| 78 | SOUTHERN NIGERIA | 30062-30837 | 776 | ✅ KEEP |

### MALAYA (Lines 30839-31713)

| # | Name | Lines | Count | Initial Classification |
|---|------|-------|-------|----------------------|
| 79 | SINGAPORE | 30839-31062 | 224 | ⚠️ VERIFY - Part of Straits Settlements? |
| 80 | THE FEDERATED STATES OF THE MALAY PENINSULA | 31064-31381 | 318 | ✅ KEEP |
| 81 | **SELANGOR** | 31383-31713 | 331 | ❌ MERGE - State within Federated Malay |

### TRANSVAAL / TRINIDAD (Lines 31714-33445)

| # | Name | Lines | Count | Initial Classification |
|---|------|-------|-------|----------------------|
| 82 | **LOUIS BOTHA** | 31714-32349 | 636 | ❌ DELETE - Person name, not colony! |
| 83 | TRINIDAD | 32351-32773 | 423 | ✅ KEEP (1st instance) |
| 84 | **TRINIDAD AND TOBAGO** | 32774-33043 | 270 | ❌ MERGE - Duplicate, merge with #83 |
| 85 | **TRINIDAD AND TOBAGO** | 33044-33445 | 402 | ❌ MERGE - Duplicate, merge with #83 |

### MISC / WINDWARD ISLANDS (Lines 33447-34717)

| # | Name | Lines | Count | Initial Classification |
|---|------|-------|-------|----------------------|
| 86 | TURKS AND CAICOS ISLANDS | 33447-33591 | 145 | ✅ KEEP |
| 87 | WEIHAIWEI | 33592-33755 | 164 | ✅ KEEP |
| 88 | THE WINDWARD ISLANDS | 33756-33834 | 79 | ✅ KEEP - Federation |
| 89 | GRENADA | 33835-34568 | 734 | ⚠️ VERIFY - Part of Windwards or separate? |
| 90 | **EXPORTS** | 34570-34717 | 148 | ❌ DELETE - Trade section (#5) |
| 91 | **APPENDIX TO PART II** | 34718-34717 | 0 | ❌ DELETE - Empty appendix |

---

## Summary of Initial Classification

### ✅ DEFINITE KEEP (26 entries)
Verified or highly likely legitimate colonies

### ❌ DEFINITE DELETE (28 entries)
- Trade sections: EXPORTS (5x), SHIPPING, MAIL SERVICES, RAILWAYS (2x)
- Admin subsections: CABINET, SENATE, EXECUTIVE COUNCIL (2x), LEGISLATIVE COUNCIL, COUNCIL OF GOVERNMENT, PARLIAMENT (2x), HEADQUARTERS STAFF
- Cities/districts: ADELAIDE, DURBAN, DURBANVILLE, KEISKAMA HOEK, URBAN POLICE DISTRICT
- Person: LOUIS BOTHA
- Misc: ROYAL ALFRED OBSERVATORY, APPENDIX, ONTARIO AND QUEBEC (OLD CANADA)

### ❌ MERGE WITH PARENT (15 entries)
- Duplicates: BERMUDA, BRITISH HONDURAS, CAPE OF GOOD HOPE, FIJI (2x), TRINIDAD (2x), EXECUTIVE COUNCIL (2nd)
- Sub-regions: PARLIAMENT OF VICTORIA, SELANGOR, DURBAN

### ⚠️ VERIFY (22 entries)
Need detailed OCR source reading to determine:
- Australia states (short line counts - may be split incorrectly)
- Canada provinces/territories (determine if separate or subsections)
- Leeward/Windward island components
- Gold Coast / Northern Territories relationship
- Singapore vs Straits Settlements
- Pukapuka vs New Zealand

---

## Next Step

Read OCR source for each ⚠️ VERIFY entry to make final classification.
