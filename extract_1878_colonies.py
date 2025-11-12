#!/usr/bin/env python3
"""
Extract all colony sections from the 1878 Colonial Office List.
This script identifies colony boundaries and extracts each to a separate file.
"""

import re
import json
import os

# Read the OCR file
ocr_file = "/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1878/olmocr_results.md"

with open(ocr_file, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Manually identified colony sections based on document inspection
# Format: (colony_name, start_line, end_line)
# These boundaries were determined by manual inspection of the document

colonies = [
    # Line 1343 BAHAMAS starts
    ("BAHAMAS", 1343, 1576),

    # Lines 1579-1581 BARBADOS is just a reference, skip

    # Line 1585 BERMUDAS starts
    ("BERMUDAS", 1585, 1846),

    # Lines 1847-1848 BRITISH COLUMBIA reference, skip
    # Lines 1850-1851 BRITISH HONDURAS reference, skip

    # Line 1853 BRITISH GUIANA starts
    ("BRITISH_GUIANA", 1853, 2474),

    # Line 2475 DOMINION OF CANADA starts
    ("DOMINION_OF_CANADA", 2475, 4263),

    # Line 4264 CAPE OF GOOD HOPE starts
    ("CAPE_OF_GOOD_HOPE", 4264, 5589),

    # Line 5590 CEYLON starts
    ("CEYLON", 5590, 6162),

    # Line 6163 FALKLAND ISLANDS starts
    ("FALKLAND_ISLANDS", 6163, 6270),

    # Line 6271 FIJI starts (marked as **FIJI.**)
    ("FIJI", 6271, 6357),

    # Line 6358 GIBRALTAR starts
    ("GIBRALTAR", 6358, 6464),

    # Line 6465 THE GOLD COAST COLONY starts
    ("THE_GOLD_COAST_COLONY", 6465, 7268),

    # Line 7269 HELIGOLAND starts
    ("HELIGOLAND", 7269, 7309),

    # Line 7310 HONDURAS starts
    ("HONDURAS", 7310, 7525),

    # Line 7526 HONG KONG starts
    ("HONG_KONG", 7526, 7794),

    # Line 7795 JAMAICA starts
    ("JAMAICA", 7795, 8437),

    # Line 8438 LABUAN starts
    ("LABUAN", 8438, 8454),

    # Line 8455 might have LEEWARD ISLANDS header
    # Let me check what's at 8455
]

# Let me first identify where sections transition by looking at the potential headers
# I'll read around key line numbers to identify exact boundaries

print("Checking key transition points...")

# Check line 8455
print(f"\nLines 8450-8460:")
for i in range(8450, 8461):
    if i <= len(lines):
        print(f"{i}: {lines[i-1].rstrip()}")

# Check line 8811
print(f"\nLines 8808-8818:")
for i in range(8808, 8819):
    if i <= len(lines):
        print(f"{i}: {lines[i-1].rstrip()}")

# Check line 10213
print(f"\nLines 10210-10220:")
for i in range(10210, 10221):
    if i <= len(lines):
        print(f"{i}: {lines[i-1].rstrip()}")

# Check line 10815
print(f"\nLines 10812-10822:")
for i in range(10812, 10823):
    if i <= len(lines):
        print(f"{i}: {lines[i-1].rstrip()}")

# Check line 10891
print(f"\nLines 10888-10898:")
for i in range(10888, 10899):
    if i <= len(lines):
        print(f"{i}: {lines[i-1].rstrip()}")

# Check line 11286
print(f"\nLines 11283-11293:")
for i in range(11283, 11294):
    if i <= len(lines):
        print(f"{i}: {lines[i-1].rstrip()}")

# Check line 11521 (NEW SOUTH WALES)
print(f"\nLines 11518-11528:")
for i in range(11518, 11529):
    if i <= len(lines):
        print(f"{i}: {lines[i-1].rstrip()}")

# Check line 12285 (NEW ZEALAND)
print(f"\nLines 12282-12292:")
for i in range(12282, 12293):
    if i <= len(lines):
        print(f"{i}: {lines[i-1].rstrip()}")

# Check line 12801 (QUEENSLAND)
print(f"\nLines 12798-12808:")
for i in range(12798, 12809):
    if i <= len(lines):
        print(f"{i}: {lines[i-1].rstrip()}")

# Check line 13290 (SOUTH AUSTRALIA)
print(f"\nLines 13287-13297:")
for i in range(13287, 13298):
    if i <= len(lines):
        print(f"{i}: {lines[i-1].rstrip()}")

# Check line 14172 (STRAITS SETTLEMENTS)
print(f"\nLines 14169-14179:")
for i in range(14169, 14180):
    if i <= len(lines):
        print(f"{i}: {lines[i-1].rstrip()}")

# Check around line 15107 (TRANSVAAL)
print(f"\nLines 15104-15114:")
for i in range(15104, 15115):
    if i <= len(lines):
        print(f"{i}: {lines[i-1].rstrip()}")

# Check around line 15206 (TRINIDAD)
print(f"\nLines 15203-15213:")
for i in range(15203, 15214):
    if i <= len(lines):
        print(f"{i}: {lines[i-1].rstrip()}")

# Check around line 15868 (TURKS AND CAICOS)
print(f"\nLines 15865-15875:")
for i in range(15865, 15876):
    if i <= len(lines):
        print(f"{i}: {lines[i-1].rstrip()}")

# Check around line 16642 (WESTERN AUSTRALIA)
print(f"\nLines 16639-16649:")
for i in range(16639, 16650):
    if i <= len(lines):
        print(f"{i}: {lines[i-1].rstrip()}")

# Check around line 16877 (WEST AFRICA)
print(f"\nLines 16874-16884:")
for i in range(16874, 16885):
    if i <= len(lines):
        print(f"{i}: {lines[i-1].rstrip()}")

# Check around line 17272 (WINDWARD ISLANDS)
print(f"\nLines 17269-17279:")
for i in range(17269, 17280):
    if i <= len(lines):
        print(f"{i}: {lines[i-1].rstrip()}")

# Check around line 18180 (TOBAGO)
print(f"\nLines 18177-18187:")
for i in range(18177, 18188):
    if i <= len(lines):
        print(f"{i}: {lines[i-1].rstrip()}")
