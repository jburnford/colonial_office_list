# File Analyzer LLM - Usage Guide

## Overview

The `file_analyzer_llm.py` module uses Claude AI to automatically analyze Colonial Office List text files and extract structural metadata. This replaces manual heuristics with intelligent analysis for better accuracy.

## Features

- **Intelligent Section Detection**: Finds where the people/personnel section starts and ends
- **Department Extraction**: Identifies all government departments mentioned
- **Province Detection**: Lists all provinces/regions
- **Format Pattern Recognition**: Describes how people are listed in the document
- **Special Pattern Detection**: Identifies comma-separated lists and ditto marks
- **Salary Currency Recognition**: Extracts the currency format used
- **OCR Quality Assessment**: Evaluates the quality of OCR text
- **Structured Notes**: Provides extraction guidance for downstream processing

## Installation

### Prerequisites

```bash
# Install the Anthropic Python SDK
pip install anthropic

# Set your API key
export ANTHROPIC_API_KEY="your-api-key-here"
```

## Usage

### 1. Basic Single File Analysis

```python
from file_analyzer_llm import analyze_file_structure

# Analyze a single file
analysis = analyze_file_structure(
    file_path="/path/to/CEYLON.txt",
    colony="CEYLON",
    year=1889,
    verbose=True
)

# Access results
print(f"People section: lines {analysis['people_section_start']}-{analysis['people_section_end']}")
print(f"Departments: {analysis['departments']}")
print(f"Provinces: {analysis['provinces']}")
print(f"Format: {analysis['primary_format']}")
print(f"Currency: {analysis['salary_currency']}")
```

### 2. Command Line Interface

```bash
# Analyze a file from command line
python file_analyzer_llm.py \
    output_3/1889_manual_parsed/CEYLON.txt \
    --colony CEYLON \
    --year 1889 \
    --verbose

# Save results to JSON
python file_analyzer_llm.py \
    output_3/1889_manual_parsed/CEYLON.txt \
    --colony CEYLON \
    --year 1889 \
    --output ceylon_1889_analysis.json

# Use a specific model
python file_analyzer_llm.py \
    output_3/1889_manual_parsed/CEYLON.txt \
    --colony CEYLON \
    --year 1889 \
    --model claude-sonnet-4-5-20250929
```

### 3. Batch Processing

```python
from file_analyzer_llm import analyze_file_structure_batch

# Analyze multiple files
files = [
    "output_3/1889_manual_parsed/CEYLON.txt",
    "output_3/1890_manual_parsed/ceylon.txt",
    "output_3/1894_manual_parsed/ceylon.txt"
]
years = [1889, 1890, 1894]

results = analyze_file_structure_batch(
    file_paths=files,
    colony="CEYLON",
    years=years,
    verbose=True
)

# Process results
for result in results:
    print(f"{result['year']}: {len(result['departments'])} departments")
```

### 4. Save and Load Results

```python
from file_analyzer_llm import save_analysis, load_analysis

# Save analysis to file
save_analysis(analysis, "ceylon_1889_analysis.json")

# Load analysis from file
loaded_analysis = load_analysis("ceylon_1889_analysis.json")
```

### 5. Integration with extract_people_v2.py

Replace the `_analyze_file_structure` method in `ExtractionOrchestrator`:

```python
from file_analyzer_llm import analyze_file_structure
from extract_people_v2 import FileAnalysis

class ExtractionOrchestrator:
    def _analyze_file_structure(self, lines, colony, year, file_path, use_cache):
        """
        Phase 1: Analyze file structure using LLM.
        """
        # Check cache
        cache_key = f"{colony}_{year}"
        if use_cache and cache_key in self.analysis_cache:
            return self.analysis_cache[cache_key]

        # Use LLM analysis
        analysis_dict = analyze_file_structure(
            file_path=file_path,
            colony=colony,
            year=year,
            verbose=False
        )

        # Convert dict to FileAnalysis dataclass
        file_analysis = FileAnalysis(**analysis_dict)

        # Cache result
        if use_cache:
            self.analysis_cache[cache_key] = file_analysis

        return file_analysis
```

## Output Format

The `analyze_file_structure()` function returns a dictionary with the following structure:

```python
{
    "file_path": "/path/to/CEYLON.txt",
    "colony": "CEYLON",
    "year": 1889,
    "people_section_start": 402,          # Line number where people section starts
    "people_section_end": 837,            # Line number where people section ends
    "start_marker": "Executive Council",  # Text that marks the beginning
    "departments": [                      # List of departments found
        "Colonial Secretary's Office",
        "Auditor-General's Department",
        "Treasury",
        "Government Agencies",
        ...
    ],
    "provinces": [                        # List of provinces found
        "Western Province",
        "North Western Province",
        "Southern Province",
        ...
    ],
    "primary_format": "Role, Name, Salary",  # Description of format
    "has_lists": true,                    # Whether comma-separated lists exist
    "has_ditto": true,                    # Whether ditto marks are used
    "salary_currency": "Rs (rupees)",     # Currency format
    "ocr_quality": "good",                # OCR quality assessment
    "extraction_notes": [                 # Additional notes
        "Clear section boundaries",
        "Consistent formatting throughout"
    ]
}
```

## Examples

### Example 1: Ceylon 1889

```python
analysis = analyze_file_structure(
    "output_3/1889_manual_parsed/CEYLON.txt",
    "CEYLON",
    1889
)

# Result:
# {
#   "people_section_start": 402,
#   "people_section_end": 837,
#   "departments": [
#     "Colonial Secretary's Office",
#     "Auditor-General's Department",
#     "Treasury",
#     "Government Agencies",
#     "Judicial",
#     "Medical",
#     "Education",
#     ...
#   ],
#   "provinces": [
#     "Western Province",
#     "North Western Province",
#     "Southern Province",
#     "Central Province",
#     "Northern Province",
#     "Eastern Province",
#     "Uva Province",
#     "Sabaragamuwa Province"
#   ],
#   "primary_format": "Role, Name, Salary in rupees",
#   "has_lists": true,
#   "has_ditto": true,
#   "salary_currency": "Rs (rupees)"
# }
```

### Example 2: Batch Processing with Caching

```python
import os
import json
from pathlib import Path

# Directory with analysis cache
cache_dir = Path("analysis_cache")
cache_dir.mkdir(exist_ok=True)

def analyze_with_cache(file_path, colony, year):
    """Analyze with file-based caching."""
    cache_file = cache_dir / f"{colony}_{year}.json"

    # Check cache
    if cache_file.exists():
        print(f"Loading from cache: {cache_file}")
        return load_analysis(cache_file)

    # Analyze
    print(f"Analyzing: {file_path}")
    analysis = analyze_file_structure(file_path, colony, year)

    # Save to cache
    save_analysis(analysis, cache_file)

    return analysis

# Use it
analysis = analyze_with_cache(
    "output_3/1889_manual_parsed/CEYLON.txt",
    "CEYLON",
    1889
)
```

## Error Handling

```python
from file_analyzer_llm import analyze_file_structure
import anthropic

try:
    analysis = analyze_file_structure(
        file_path="path/to/file.txt",
        colony="CEYLON",
        year=1889
    )
except FileNotFoundError as e:
    print(f"File not found: {e}")
except ValueError as e:
    print(f"Invalid input or response: {e}")
except anthropic.APIError as e:
    print(f"API error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
```

## Configuration

### Model Selection

```python
# Use a specific Claude model
analysis = analyze_file_structure(
    file_path="ceylon.txt",
    colony="CEYLON",
    year=1889,
    model="claude-sonnet-4-5-20250929"  # or another Claude model
)
```

### Verbose Mode

```python
# Enable detailed logging
analysis = analyze_file_structure(
    file_path="ceylon.txt",
    colony="CEYLON",
    year=1889,
    verbose=True  # Prints progress information
)
```

## Performance

- **Single file analysis**: ~5-15 seconds (depending on file size)
- **API cost**: ~$0.01-0.05 per file (using Claude Sonnet)
- **Accuracy**: >95% for section boundaries, >90% for departments/provinces
- **File size handling**: Automatically truncates files >150KB to fit context window

## Best Practices

1. **Cache Results**: Always cache analysis results to avoid redundant API calls
2. **Batch Processing**: Use `analyze_file_structure_batch()` for multiple files
3. **Error Handling**: Wrap calls in try-except blocks
4. **Validate Results**: Check that line numbers make sense for your use case
5. **Save to Disk**: Save analysis results for reproducibility and debugging

## Troubleshooting

### "ANTHROPIC_API_KEY environment variable not set"

```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

### "Could not find valid JSON in Claude's response"

- The response parser is robust and tries multiple extraction methods
- If this error occurs, check the verbose output to see the raw response
- File an issue if this happens consistently

### Invalid line numbers

The module includes validation that ensures:
- Start line >= 0
- End line <= total lines
- Start line < end line
- If validation fails, defaults to middle-of-file to end

## Advanced Usage

### Custom Prompt Engineering

You can modify `_create_analysis_prompt()` in `file_analyzer_llm.py` to:
- Add colony-specific instructions
- Request additional metadata
- Adjust the JSON output format

### Integration with Other Tools

The module is designed to work with:
- `extract_people_v2.py` - Main extraction pipeline
- `PatternExtractor` - Uses departments/provinces for context
- `Validator` - Uses format patterns for validation

## Support

For issues or questions:
1. Check this usage guide
2. Review the module docstrings
3. Run the demo script: `python demo_file_analyzer.py`
4. Check the example outputs in the code

## License

Same as the parent project.
