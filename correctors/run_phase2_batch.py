#!/usr/bin/env python3
"""
Batch processor for Phase 2 Enum Mapping across all KG files

Runs the LLM-powered enum mapper on all 62 knowledge graph extraction files.
"""

import json
import sys
from pathlib import Path
from datetime import datetime
import subprocess

# Configuration
INPUT_DIR = Path("knowledge_graph_extracts_v2")
OUTPUT_DIR = Path("knowledge_graph_extracts_v3")
REPORTS_DIR = Path("reports")

def get_all_kg_files():
    """Get all KG extraction files"""
    files = sorted(INPUT_DIR.glob("*_extracted.json"))
    return files

def run_phase2_on_file(input_file: Path) -> dict:
    """Run Phase 2 enum mapper on a single file"""
    output_file = OUTPUT_DIR / input_file.name

    print(f"\n{'='*80}")
    print(f"Processing: {input_file.name}")
    print(f"{'='*80}")

    # Run the phase2 enum mapper
    cmd = [
        "python3",
        "correctors/phase2_enum_mapper.py",
        "--file", str(input_file),
        "--output", str(output_file),
        "--apply"
    ]

    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=600  # 10 minute timeout per file
        )

        success = result.returncode == 0

        return {
            "file": input_file.name,
            "success": success,
            "stdout": result.stdout,
            "stderr": result.stderr,
            "output_file": str(output_file) if success else None
        }

    except subprocess.TimeoutExpired:
        return {
            "file": input_file.name,
            "success": False,
            "error": "Timeout (>10 minutes)",
            "output_file": None
        }
    except Exception as e:
        return {
            "file": input_file.name,
            "success": False,
            "error": str(e),
            "output_file": None
        }

def main():
    """Main batch processing function"""

    # Create output directory
    OUTPUT_DIR.mkdir(exist_ok=True)
    REPORTS_DIR.mkdir(exist_ok=True)

    # Get all files
    files = get_all_kg_files()
    total_files = len(files)

    print(f"\n{'#'*80}")
    print(f"# Phase 2 Enum Mapping - Batch Processing")
    print(f"# Total files: {total_files}")
    print(f"# Input: {INPUT_DIR}")
    print(f"# Output: {OUTPUT_DIR}")
    print(f"{'#'*80}\n")

    # Process each file
    results = []
    successful = 0
    failed = 0

    for i, file_path in enumerate(files, 1):
        print(f"\n[{i}/{total_files}] Processing {file_path.name}...")

        result = run_phase2_on_file(file_path)
        results.append(result)

        if result["success"]:
            successful += 1
            print(f"✅ SUCCESS: {file_path.name}")
        else:
            failed += 1
            print(f"❌ FAILED: {file_path.name}")
            if "error" in result:
                print(f"   Error: {result['error']}")

    # Generate summary report
    summary = {
        "batch_run_date": datetime.now().isoformat(),
        "total_files": total_files,
        "successful": successful,
        "failed": failed,
        "success_rate": f"{(successful/total_files)*100:.1f}%",
        "results": results
    }

    # Save summary
    summary_file = REPORTS_DIR / "phase2_batch_results.json"
    with open(summary_file, 'w') as f:
        json.dump(summary, f, indent=2)

    # Print final summary
    print(f"\n{'#'*80}")
    print(f"# Batch Processing Complete")
    print(f"#")
    print(f"# Total files: {total_files}")
    print(f"# Successful: {successful}")
    print(f"# Failed: {failed}")
    print(f"# Success rate: {(successful/total_files)*100:.1f}%")
    print(f"#")
    print(f"# Results saved to: {summary_file}")
    print(f"{'#'*80}\n")

    return 0 if failed == 0 else 1

if __name__ == "__main__":
    sys.exit(main())
