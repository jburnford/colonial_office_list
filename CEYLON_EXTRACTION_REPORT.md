# Ceylon People Data Extraction Report

## Overview
**Date:** 2025-11-19
**Colony:** Ceylon
**Total People Extracted:** 4,801
**Files Processed:** 47
**Year Range:** 1867-1946
**Average Confidence:** 0.83

## Methodology

### Hybrid Python-LLM Approach
- **Python:** Pattern-based extraction for bulk processing
- **Structure Analysis:** Automated detection of department headers, provinces, and people sections
- **Pattern Matching:** Multiple regex patterns for different data formats

### Patterns Detected
1. **Standard Format:** `Role, Name, Salary` (e.g., "Governor, Sir H. G. Robinson, Knt., 7,000l.")
2. **With Location:** `Role, Location, Name, Salary` (e.g., "Assistant Government Agent, Kandy, G. S. Williams, 450l.")
3. **Name and Salary Only:** `Name, Salary` (inherits role from context)
4. **Name Lists:** Lists following role descriptions

## Results by Decade

| Decade | Files | People | Avg/Year |
|--------|-------|--------|----------|
| 1860s  | 1     | 182    | 182      |
| 1870s  | 3     | 103    | 34       |
| 1880s  | 4     | 50     | 13       |
| 1890s  | 5     | 32     | 6        |
| 1900s  | 6     | 118    | 20       |
| 1910s  | 8     | 1,122  | 140      |
| 1920s  | 8     | 1,679  | 210      |
| 1930s  | 11    | 1,460  | 133      |
| 1940s  | 1     | 155    | 155      |

## Data Quality

### Confidence Distribution
- **High Confidence (0.9):** 4,076 people (85%)
- **Medium Confidence (0.5):** 725 people (15%)

### Common Issues
1. **Unknown Roles:** Some early years have incomplete role extraction where names appear in lists
2. **Format Variations:** Currency changed from £ (pounds) to Rs. (rupees) around 1870s
3. **Structural Changes:** 1946 shows "State Council" structure instead of "Civil Establishment"

## Sample Extractions

### 1867 (Early Colonial Period)
- Governor: Sir H. G. Robinson, Knt., 7,000l.
- Colonial Secretary: W. G. Gibson, 2,000l.
- Chief Justice: Sir E. S. Creasy, Knt., 2,500l.

### 1920 (Peak Colonial Administration)
- Colonial Secretary: Sir Graeme Thomson, K.C.B.
- Treasurer: B. Senior, C.M.G., I.S.O.
- Chief Justice: Sir Alexander Wood Renton, K.C.M.G.

### 1940 (Pre-Independence)
- Chief Secretary: M. M. Wedderburn, C.M.G.
- Financial Secretary: H. J. Huxham, C.M.G.

## Departments Identified

Common departments across years:
- Colonial Secretary's Office
- Treasury Department
- Audit Office
- Surveyor General's Department
- Customs Department
- Judicial Establishment
- Medical Department
- Police
- Public Works
- Ecclesiastical Department
- Government Agents (by Province)

## Provincial Structure

Ceylon was divided into provinces, each with Government Agents:
- Western Province
- Central Province
- Southern Province
- Northern Province
- Eastern Province
- North Western Province

## Data Schema

Each person record contains:
```json
{
  "name": "Person's name with titles/qualifications",
  "role": "Official position/title",
  "location": "Colony + Department + Province",
  "colony": "CEYLON",
  "year": 1867,
  "department": "Colonial Secretary's Office",
  "full_string": "Original line from source",
  "source_file": "GitHub URL with line number",
  "line_number": 166,
  "confidence": 0.90
}
```

## Next Steps for Refinement

1. **Handle "ditto" references:** Extract previous role when "ditto" appears
2. **Improve context tracking:** Better handling of role inheritance for name lists
3. **1946 State Council:** Add pattern for State Council structure
4. **Salary extraction:** Parse salary amounts and currency into separate fields
5. **Title normalization:** Standardize titles (Sir, K.C.M.G., etc.)

## Applications

This dataset enables research into:
- **Colonial administrative hierarchy** over 80 years
- **Career progression** of colonial officials
- **Salary structures** and changes over time
- **Departmental growth** and organizational changes
- **Geographic distribution** of officials across provinces
- **Transition to independence** (pre-1948 structure)

## Files Generated

1. **ceylon_people_data.json** - Complete extraction results
2. **extract_ceylon_people.py** - Extraction script
3. **CEYLON_EXTRACTION_REPORT.md** - This report

## Traceability

Every person record includes:
- Source file path
- Line number
- GitHub URL for verification

Example: `https://github.com/jburnford/colonial_office_list/blob/main/output_3/1867_manual_parsed/ceylon.txt#L161`
