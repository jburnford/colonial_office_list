# Toponym Quality Refinement Report

**Report Generated:** 2025-11-17 03:04:51

## Overview

This report documents the quality refinement process applied to the
discovered toponyms, removing false positives and improving type classification.

## Summary by Year

| Year | Raw Count | Refined Count | Filtered Out | Retention Rate |
|------|-----------|---------------|--------------|----------------|
| 1961 | 3485 | 867 | 2618 | 24.9% |
| 1962 | 3210 | 801 | 2409 | 25.0% |
| 1964 | 2655 | 665 | 1990 | 25.0% |
| 1965 | 2380 | 583 | 1797 | 24.5% |
| 1966 | 2420 | 588 | 1832 | 24.3% |

## Total Across All Years

- **Raw Toponyms:** 14150
- **Refined Toponyms:** 3504
- **Filtered Out:** 10646
- **Overall Retention Rate:** 24.8%

## Quality Criteria Applied

### Inclusion Criteria

Toponyms were kept if they met ANY of the following:

1. **Known Valid Places:** Match list of known colonies and territories
2. **Strong Geographic Terms:** Contains terms like Island, River, Bay, Colony, etc.
3. **Valid Geographic Type:** Classified as colony, island, river, bay, mountain, etc.

### Exclusion Criteria

Toponyms were filtered out if they matched ANY of the following:

1. **Administrative Titles:** Secretary, Minister, Governor, Commissioner, etc.
2. **Departments:** Department, Office, Ministry, Board, Council, etc.
3. **Company Names:** Contains Ltd, Limited, Corporation, Bank of, etc.
4. **Document Sections:** Functions, Distribution, History, List of, etc.
5. **Generic Terms:** British, Colonial, Royal, Government, etc.
6. **Too Long:** Names over 50 characters
7. **Too Short:** Names under 3 characters

## Type Reclassification

Place types were improved using the following logic:

- **colony:** Contains 'colony', 'protectorate', 'territory', or is a known colony
- **island:** Contains 'island', 'isle', 'atoll'
- **river:** Contains 'river'
- **bay:** Contains 'bay', 'harbor', 'harbour'
- **mountain:** Contains 'mountain', 'mount', 'hill', 'peak', 'range'
- **lake:** Contains 'lake', 'lagoon', 'pond'
- **city/town:** Contains 'city' or 'town'
- **administrative_division:** Contains 'district', 'province', 'county', 'parish'
