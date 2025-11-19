#!/usr/bin/env python3
"""
Script to identify colony section boundaries in the 1962 Colonial Office List
by scanning for major section headers.
"""

import re

def find_colony_boundaries(file_path):
    """
    Read through the file and identify major colony section boundaries.
    """
    colonies = []
    current_colony = None

    with open(file_path, 'r', encoding='utf-8') as f:
        for line_num, line in enumerate(f, 1):
            # Skip Part I and table of contents
            if line_num < 3075:
                continue

            # Stop at Part III staff listings
            if line_num > 17500:
                break

            # Look for major section headers that indicate new colonies
            # These are typically ALL CAPS lines with specific patterns
            stripped = line.strip()

            # Check for major colony headers
            if re.match(r'^STATE OF SINGAPORE$', stripped):
                if current_colony:
                    current_colony['end_line'] = line_num - 1
                    colonies.append(current_colony)
                current_colony = {'name': 'State of Singapore', 'start_line': line_num}
                print(f"Found: State of Singapore at line {line_num}")

            elif re.match(r'^ADEN COLONY$', stripped):
                if current_colony:
                    current_colony['end_line'] = line_num - 1
                    colonies.append(current_colony)
                current_colony = {'name': 'Aden Colony', 'start_line': line_num}
                print(f"Found: Aden Colony at line {line_num}")

            elif re.match(r'^BAHAMA ISLANDS$', stripped):
                if current_colony:
                    current_colony['end_line'] = line_num - 1
                    colonies.append(current_colony)
                current_colony = {'name': 'Bahama Islands', 'start_line': line_num}
                print(f"Found: Bahama Islands at line {line_num}")

            elif re.match(r'^BERMUDA$', stripped):
                if current_colony:
                    current_colony['end_line'] = line_num - 1
                    colonies.append(current_colony)
                current_colony = {'name': 'Bermuda', 'start_line': line_num}
                print(f"Found: Bermuda at line {line_num}")

            elif re.match(r'^BRITISH GUIANA$', stripped):
                if current_colony:
                    current_colony['end_line'] = line_num - 1
                    colonies.append(current_colony)
                current_colony = {'name': 'British Guiana', 'start_line': line_num}
                print(f"Found: British Guiana at line {line_num}")

            elif re.match(r'^BRITISH HONDURAS$', stripped):
                if current_colony:
                    current_colony['end_line'] = line_num - 1
                    colonies.append(current_colony)
                current_colony = {'name': 'British Honduras', 'start_line': line_num}
                print(f"Found: British Honduras at line {line_num}")

            elif re.match(r'^BRUNEI$', stripped):
                if current_colony:
                    current_colony['end_line'] = line_num - 1
                    colonies.append(current_colony)
                current_colony = {'name': 'Brunei', 'start_line': line_num}
                print(f"Found: Brunei at line {line_num}")

            elif re.match(r'^THE CAMEROONS$', stripped):
                if current_colony:
                    current_colony['end_line'] = line_num - 1
                    colonies.append(current_colony)
                current_colony = {'name': 'The Cameroons', 'start_line': line_num}
                print(f"Found: The Cameroons at line {line_num}")

            elif re.match(r'^FALKLAND ISLANDS AND DEPENDENCIES$', stripped):
                if current_colony:
                    current_colony['end_line'] = line_num - 1
                    colonies.append(current_colony)
                current_colony = {'name': 'Falkland Islands and Dependencies', 'start_line': line_num}
                print(f"Found: Falkland Islands and Dependencies at line {line_num}")

            elif re.match(r'^### Fiji \(and the Pitcairn Islands Group\)$', stripped):
                if current_colony:
                    current_colony['end_line'] = line_num - 1
                    colonies.append(current_colony)
                current_colony = {'name': 'Fiji (and Pitcairn Islands Group)', 'start_line': line_num}
                print(f"Found: Fiji (and Pitcairn Islands Group) at line {line_num}")

            elif re.match(r'^THE GAMBIA$', stripped):
                if current_colony:
                    current_colony['end_line'] = line_num - 1
                    colonies.append(current_colony)
                current_colony = {'name': 'The Gambia', 'start_line': line_num}
                print(f"Found: The Gambia at line {line_num}")

            elif re.match(r'^GIBRALTAR$', stripped):
                if current_colony:
                    current_colony['end_line'] = line_num - 1
                    colonies.append(current_colony)
                current_colony = {'name': 'Gibraltar', 'start_line': line_num}
                print(f"Found: Gibraltar at line {line_num}")

            elif re.match(r'^HONG KONG$', stripped):
                if current_colony:
                    current_colony['end_line'] = line_num - 1
                    colonies.append(current_colony)
                current_colony = {'name': 'Hong Kong', 'start_line': line_num}
                print(f"Found: Hong Kong at line {line_num}")

            elif re.match(r'^KENYA$', stripped):
                if current_colony:
                    current_colony['end_line'] = line_num - 1
                    colonies.append(current_colony)
                current_colony = {'name': 'Kenya', 'start_line': line_num}
                print(f"Found: Kenya at line {line_num}")

            elif re.match(r'^MALTA, G\.C\.$', stripped):
                if current_colony:
                    current_colony['end_line'] = line_num - 1
                    colonies.append(current_colony)
                current_colony = {'name': 'Malta', 'start_line': line_num}
                print(f"Found: Malta at line {line_num}")

            elif re.match(r'^MAURITIUS$', stripped):
                if current_colony:
                    current_colony['end_line'] = line_num - 1
                    colonies.append(current_colony)
                current_colony = {'name': 'Mauritius', 'start_line': line_num}
                print(f"Found: Mauritius at line {line_num}")

            elif re.match(r'^NORTH BORNEO$', stripped):
                if current_colony:
                    current_colony['end_line'] = line_num - 1
                    colonies.append(current_colony)
                current_colony = {'name': 'North Borneo', 'start_line': line_num}
                print(f"Found: North Borneo at line {line_num}")

            elif re.match(r'^THE FEDERATION OF RHODESIA AND NYASALAND$', stripped):
                if current_colony:
                    current_colony['end_line'] = line_num - 1
                    colonies.append(current_colony)
                current_colony = {'name': 'Federation of Rhodesia and Nyasaland', 'start_line': line_num}
                print(f"Found: Federation of Rhodesia and Nyasaland at line {line_num}")

            elif re.match(r'^NORTHERN RHODESIA$', stripped):
                if current_colony:
                    current_colony['end_line'] = line_num - 1
                    colonies.append(current_colony)
                current_colony = {'name': 'Northern Rhodesia', 'start_line': line_num}
                print(f"Found: Northern Rhodesia at line {line_num}")

            elif re.match(r'^NYASALAND PROTECTORATE$', stripped):
                if current_colony:
                    current_colony['end_line'] = line_num - 1
                    colonies.append(current_colony)
                current_colony = {'name': 'Nyasaland Protectorate', 'start_line': line_num}
                print(f"Found: Nyasaland Protectorate at line {line_num}")

            elif re.match(r'^ST\. HELENA$', stripped):
                if current_colony:
                    current_colony['end_line'] = line_num - 1
                    colonies.append(current_colony)
                current_colony = {'name': 'St. Helena', 'start_line': line_num}
                print(f"Found: St. Helena at line {line_num}")

            elif re.match(r'^SEYCHELLES$', stripped):
                if current_colony:
                    current_colony['end_line'] = line_num - 1
                    colonies.append(current_colony)
                current_colony = {'name': 'Seychelles', 'start_line': line_num}
                print(f"Found: Seychelles at line {line_num}")

            elif re.match(r'^\*\*SARAWAK\*\*$', stripped):
                if current_colony:
                    current_colony['end_line'] = line_num - 1
                    colonies.append(current_colony)
                current_colony = {'name': 'Sarawak', 'start_line': line_num}
                print(f"Found: Sarawak at line {line_num}")

            elif re.match(r'^SIERRA LEONE$', stripped):
                if current_colony:
                    current_colony['end_line'] = line_num - 1
                    colonies.append(current_colony)
                current_colony = {'name': 'Sierra Leone', 'start_line': line_num}
                print(f"Found: Sierra Leone at line {line_num}")

            elif re.match(r'^TANGANYIKA$', stripped):
                if current_colony:
                    current_colony['end_line'] = line_num - 1
                    colonies.append(current_colony)
                current_colony = {'name': 'Tanganyika', 'start_line': line_num}
                print(f"Found: Tanganyika at line {line_num}")

            elif re.match(r'^KINGDOM OF TONGA$', stripped):
                if current_colony:
                    current_colony['end_line'] = line_num - 1
                    colonies.append(current_colony)
                current_colony = {'name': 'Tonga', 'start_line': line_num}
                print(f"Found: Tonga at line {line_num}")

            elif re.match(r'^\*\*UGANDA\*\*$', stripped):
                if current_colony:
                    current_colony['end_line'] = line_num - 1
                    colonies.append(current_colony)
                current_colony = {'name': 'Uganda', 'start_line': line_num}
                print(f"Found: Uganda at line {line_num}")

            elif re.match(r'^VIRGIN ISLANDS$', stripped):
                if current_colony:
                    current_colony['end_line'] = line_num - 1
                    colonies.append(current_colony)
                current_colony = {'name': 'Virgin Islands', 'start_line': line_num}
                print(f"Found: Virgin Islands at line {line_num}")

            elif re.match(r'^THE WEST INDIES \(FEDERATION\)$', stripped):
                if current_colony:
                    current_colony['end_line'] = line_num - 1
                    colonies.append(current_colony)
                current_colony = {'name': 'The West Indies (Federation)', 'start_line': line_num}
                print(f"Found: The West Indies (Federation) at line {line_num}")

            elif re.match(r'^THE WEST INDIES—BARBADOS$', stripped):
                if current_colony:
                    current_colony['end_line'] = line_num - 1
                    colonies.append(current_colony)
                current_colony = {'name': 'The West Indies - Barbados', 'start_line': line_num}
                print(f"Found: The West Indies - Barbados at line {line_num}")

            elif re.match(r'^THE WEST INDIES—TRINIDAD AND TOBAGO:$', stripped):
                if current_colony:
                    current_colony['end_line'] = line_num - 1
                    colonies.append(current_colony)
                current_colony = {'name': 'The West Indies - Trinidad and Tobago', 'start_line': line_num}
                print(f"Found: The West Indies - Trinidad and Tobago at line {line_num}")

            elif re.match(r'^WESTERN PACIFIC HIGH COMMISSION$', stripped):
                if current_colony:
                    current_colony['end_line'] = line_num - 1
                    colonies.append(current_colony)
                current_colony = {'name': 'Western Pacific High Commission', 'start_line': line_num}
                print(f"Found: Western Pacific High Commission at line {line_num}")

            elif re.match(r'^ZANZIBAR : THE HIGH COMMISSION TERRITORIES$', stripped):
                if current_colony:
                    current_colony['end_line'] = line_num - 1
                    colonies.append(current_colony)
                current_colony = {'name': 'Zanzibar and High Commission Territories', 'start_line': line_num}
                print(f"Found: Zanzibar and High Commission Territories at line {line_num}")

            elif re.match(r'^MISCELLANEOUS ISLANDS$', stripped):
                if current_colony:
                    current_colony['end_line'] = line_num - 1
                    colonies.append(current_colony)
                current_colony = {'name': 'Miscellaneous Islands', 'start_line': line_num}
                print(f"Found: Miscellaneous Islands at line {line_num}")

            elif re.match(r'^THE HIGH COMMISSION TERRITORIES$', stripped):
                if current_colony:
                    current_colony['end_line'] = line_num - 1
                    colonies.append(current_colony)
                current_colony = {'name': 'The High Commission Territories', 'start_line': line_num}
                print(f"Found: The High Commission Territories at line {line_num}")

            elif re.match(r'^BASUTOLAND$', stripped):
                if current_colony:
                    current_colony['end_line'] = line_num - 1
                    colonies.append(current_colony)
                current_colony = {'name': 'Basutoland', 'start_line': line_num}
                print(f"Found: Basutoland at line {line_num}")

            elif re.match(r'^THE BECHUANALAND PROTECTORATE$', stripped):
                if current_colony:
                    current_colony['end_line'] = line_num - 1
                    colonies.append(current_colony)
                current_colony = {'name': 'The Bechuanaland Protectorate', 'start_line': line_num}
                print(f"Found: The Bechuanaland Protectorate at line {line_num}")

            elif re.match(r'^SWAZILAND$', stripped):
                if current_colony:
                    current_colony['end_line'] = line_num - 1
                    colonies.append(current_colony)
                current_colony = {'name': 'Swaziland', 'start_line': line_num}
                print(f"Found: Swaziland at line {line_num}")

    # Close the last colony
    if current_colony:
        current_colony['end_line'] = 17380  # Approximate end before government agencies section
        colonies.append(current_colony)

    return colonies

if __name__ == '__main__':
    source_file = '/home/user/colonial_office_list/historical_document_pipeline/processed_pdfs/colonial-office-list-1962/olmocr_results.md'

    print("Scanning for colony sections in 1962 Colonial Office List...")
    print("=" * 80)
    colonies = find_colony_boundaries(source_file)

    print("\n" + "=" * 80)
    print(f"\nFound {len(colonies)} colony sections:\n")
    for i, colony in enumerate(colonies, 1):
        num_lines = colony['end_line'] - colony['start_line'] + 1
        print(f"{i:2d}. {colony['name']:50s} Lines {colony['start_line']:5d}-{colony['end_line']:5d} ({num_lines:4d} lines)")

    # Save results
    import json
    with open('/home/user/colonial_office_list/output_3/1962_colonies_found.txt', 'w') as f:
        for i, colony in enumerate(colonies, 1):
            num_lines = colony['end_line'] - colony['start_line'] + 1
            f.write(f"{i:2d}. {colony['name']:50s} Lines {colony['start_line']:5d}-{colony['end_line']:5d} ({num_lines:4d} lines)\n")

    with open('/home/user/colonial_office_list/output_3/1962_colonies_boundaries.json', 'w') as f:
        json.dump(colonies, f, indent=2)

    print(f"\nResults saved to:")
    print("  - /home/user/colonial_office_list/output_3/1962_colonies_found.txt")
    print("  - /home/user/colonial_office_list/output_3/1962_colonies_boundaries.json")
