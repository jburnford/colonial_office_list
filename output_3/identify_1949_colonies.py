#!/usr/bin/env python3
"""
Identify colony sections in the 1949 Colonial Office List
by scanning for potential colony headings between PART II and PART III
"""

import re

# Read the file
with open('/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1949/olmocr_results.md', 'r') as f:
    lines = f.readlines()

# Find boundaries
start_line = None
end_line = None

for i, line in enumerate(lines, 1):
    if line.strip() == 'ADEN' and i > 3000 and i < 5000:
        start_line = i
        print(f"Found start at line {i}: ADEN")
        break

for i, line in enumerate(lines, 1):
    if line.strip() == 'PART III' and i > 29000:
        end_line = i
        print(f"Found end at line {i}: PART III")
        break

if not start_line or not end_line:
    print("Could not find boundaries")
    exit(1)

print(f"\nScanning lines {start_line} to {end_line}")
print("=" * 80)

# Look for potential colony headings
# These are lines that are:
# 1. All uppercase
# 2. Not too long (< 60 chars)
# 3. Not just a section header like "ADMINISTRATION", "POPULATION" etc.

excluded_headers = {
    'SITUATION AND AREA', 'CLIMATE', 'GENERAL DESCRIPTION', 'POPULATION',
    'RELIGION', 'HISTORY', 'CONSTITUTION', 'ADMINISTRATION', 'JUDICIAL',
    'LEGAL', 'MEDICAL', 'POLICE', 'POSTS', 'PRISON', 'PUBLIC WORKS',
    'TREASURY', 'EDUCATION', 'AGRICULTURE', 'AUDIT', 'COMMUNICATIONS',
    'CUSTOMS', 'DEFENCE', 'FORESTRY', 'GEOLOGICAL SURVEY', 'GOVERNMENT RAILWAY',
    'GOVERNMENT CHEMIST', 'LABOUR', 'LANDS AND MINES', 'MARINE', 'METEOROLOGICAL',
    'MINES', 'PENSIONS', 'PRINTING', 'SECRETARIAT', 'SURVEY', 'TRADE',
    'TRANSPORT', 'VETERINARY', 'WATER SUPPLY', 'WIRELESS', 'FISHERIES',
    'TELECOMMUNICATIONS', 'IMPERIAL LIGHTHOUSE SERVICE', 'PROBATION',
    'MISCELLANEOUS', 'REGISTRAR GENERAL', 'WEIGHTS AND MEASURES',
    'INFORMATION SERVICES', 'TOWN PLANNING', 'GOVERNMENT INFORMATION SERVICES',
    'COLONIAL SECRETARY', 'CHIEF SECRETARY', 'FINANCIAL SECRETARY',
    'GOVERNOR', 'LIEUTENANT-GOVERNOR', 'HIGH COMMISSIONER', 'RESIDENT COMMISSIONER',
    'STATISTICS', 'SAVINGS BANK', 'CO-OPERATIVE DEVELOPMENT', 'SOCIAL WELFARE',
    'DEVELOPMENT', 'BROADCASTING', 'CIVIL AVIATION', 'ELECTRICITY',
    'INCOME TAX', 'FIRE BRIGADE', 'GOVERNMENT STOCK FARM', 'GOVERNMENT ANALYST',
    'TSETSE CONTROL', 'GAME DEPARTMENT', 'IMMIGRATION', 'HARBOUR',
    'GOVERNMENT PRINTING', 'ARCHIVES', 'EXAMINATIONS', 'CURRENCY',
    'GOVERNMENT FACTORIES', 'COTTAGE INDUSTRIES', 'SHIPPING',
    'PUBLIC RELATIONS', 'RENT CONTROL', 'SUPPLY', 'LOCAL GOVERNMENT',
    'ASSISTANT COLONIAL SECRETARY', 'ASSISTANT COLONIAL SECRETARIES',
    'EXECUTIVE COUNCIL', 'LEGISLATIVE COUNCIL', 'MUNICIPAL COUNCIL',
    'BRITISH SOLOMON ISLANDS PROTECTORATE', 'COLONIAL DEVELOPMENT CORPORATION',
    'COLONIAL SECRETARY FOR DEVELOPMENT', 'COMMISSIONER OF PRISONS',
    'COMMISSIONER OF CO-OPERATIVE DEVELOPMENT', 'CENTRAL AFRICAN COUNCIL',
    'ASSISTANT CHIEF SECRETARY', 'COMPTROLLER OF CUSTOMS', 'DEPUTY COLONIAL SECRETARY'
}

potential_colonies = []
in_colony_section = False

for i in range(start_line - 1, end_line - 1):
    line_num = i + 1
    line_text = lines[i].strip()

    # Check if it's an all-caps line
    if line_text and line_text.isupper() and len(line_text) < 80:
        # Skip if it's a known section header
        if line_text not in excluded_headers:
            # Check if it might be a colony name
            # Colony names often contain certain keywords or patterns
            potential_colony = True

            # Skip very short lines (< 4 chars) unless they're specific names
            if len(line_text) < 4 and line_text not in ['ADEN', 'FIJI', 'MALTA']:
                potential_colony = False

            if potential_colony:
                # Get some context
                context_before = lines[max(0, i-2):i]
                context_after = lines[i+1:min(len(lines), i+4)]

                potential_colonies.append({
                    'line': line_num,
                    'text': line_text,
                    'before': ''.join(context_before),
                    'after': ''.join(context_after)
                })

# Print results
print(f"\nFound {len(potential_colonies)} potential colony headings:\n")
for item in potential_colonies:
    print(f"Line {item['line']:5d}: {item['text']}")

print("\n" + "=" * 80)
print("Saving detailed output to file...")

with open('/home/user/colonial_office_list/output_3/1949_potential_colonies_detailed.txt', 'w') as f:
    for item in potential_colonies:
        f.write(f"\n{'=' * 80}\n")
        f.write(f"Line {item['line']}: {item['text']}\n")
        f.write(f"{'=' * 80}\n")
        f.write(f"BEFORE:\n{item['before']}\n")
        f.write(f"AFTER:\n{item['after']}\n")

print(f"Detailed output saved to 1949_potential_colonies_detailed.txt")
