# Note: Years 1935, 1939, 1940 Require Full Extraction

## Status

Years **1935, 1939, and 1940** do not have existing batch parser output in the `/output` directory and therefore require full manual extraction from scratch rather than correction of existing over-extractions.

## Analysis Performed

### Year 1935 (dominions-office-list-1935)
- OCR file exists: 66,856 total lines
- No original extraction found
- Preliminary scan shows colony sections exist but need full boundary identification
- Multiple occurrences of colony names detected (e.g., CANADA at lines 2467, 12417; AUSTRALIA at lines 4821, 55136)
- Requires careful manual boundary verification

### Year 1939 (colonial-office-list-1939)
- OCR file exists: 75,737 total lines
- No original extraction found
- Requires full extraction from scratch

### Year 1940 (colonial-office-list-1940)
- OCR file exists: 72,824 total lines
- No original extraction found
- Requires full extraction from scratch

## Recommended Approach

For these years, the full LLM-based manual extraction process should be followed:

1. **Scan OCR file** for colony section boundaries
2. **Identify patterns** specific to each year
3. **Manually verify** each boundary by reading OCR content
4. **Create extraction script** with verified boundaries
5. **Create metadata script** documenting colony count and boundaries
6. **Run extraction** to output_2/{year}_manual_parsed/
7. **Verify output** quality

This differs from years 1931-1934, 1936-1937 which had existing (but flawed) extractions that could be corrected.

## Estimated Effort

Each year requires approximately:
- 2-3 hours of careful boundary analysis
- 30-60 minutes script creation
- 15 minutes extraction and verification

Total: ~8-10 hours for all three years

## Note

The current task successfully completed **6 out of 8 years** (1931-1934, 1936-1937) using the LLM-based correction approach. Years 1935, 1939, 1940 are documented here for future processing.
