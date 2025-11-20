#!/usr/bin/env python3
"""
Comprehensive quality assessment of Fiji extraction (v2 hybrid system)
Focuses on Fiji-specific features: multi-role support, acting officials, provinces
"""

import json
import random
from collections import defaultdict, Counter
from pathlib import Path
import re

def load_extraction_data(filepath):
    """Load the Fiji extraction JSON file"""
    with open(filepath, 'r', encoding='utf-8') as f:
        full_data = json.load(f)
        # Return metadata, people data, and year_stats
        return full_data.get('metadata', {}), full_data.get('people', []), full_data.get('year_stats', {})

def calculate_statistics(data):
    """Calculate comprehensive statistics on the extraction"""
    stats = {
        'total_people': len(data),
        'years': set(),
        'confidence_distribution': Counter(),
        'unknown_roles': 0,
        'multi_role_entries': 0,
        'acting_officials': 0,
        'provinces': Counter(),
        'roles': Counter(),
        'multi_role_ids': set(),
        'files': set(),
    }

    for person in data:
        # Year tracking
        year = person.get('year')
        if year:
            stats['years'].add(year)

        # File tracking
        source_file = person.get('source_file')
        if source_file:
            stats['files'].add(source_file)

        # Confidence
        confidence = person.get('confidence', 'unknown')
        stats['confidence_distribution'][confidence] += 1

        # Unknown roles
        role = person.get('role', '')
        if role.lower() in ['unknown', '', 'unclear', 'not specified']:
            stats['unknown_roles'] += 1
        stats['roles'][role] += 1

        # Multi-role entries
        multi_role_id = person.get('multi_role_id')
        if multi_role_id:
            stats['multi_role_entries'] += 1
            stats['multi_role_ids'].add(multi_role_id)

        # Acting officials
        if person.get('is_acting'):
            stats['acting_officials'] += 1

        # Provinces
        province = person.get('province')
        if province:
            stats['provinces'][province] += 1

    # Convert sets to counts
    stats['year_count'] = len(stats['years'])
    stats['file_count'] = len(stats['files'])
    stats['unique_multi_role_groups'] = len(stats['multi_role_ids'])
    stats['years_list'] = sorted(list(stats['years']))

    return stats

def sample_records(data, count=15):
    """
    Sample records with specific criteria:
    - Multi-role entries
    - Acting officials
    - Different provinces
    - Native titles (Bulis, Roko Tuis)
    """
    samples = {
        'multi_role': [],
        'acting': [],
        'provinces': defaultdict(list),
        'native_titles': [],
        'random': []
    }

    # Categorize all records
    for person in data:
        if person.get('multi_role_id'):
            samples['multi_role'].append(person)
        if person.get('is_acting'):
            samples['acting'].append(person)
        province = person.get('province')
        if province:
            samples['provinces'][province].append(person)
        role = person.get('role', '').lower()
        if any(title in role for title in ['buli', 'roko tui', 'turaga']):
            samples['native_titles'].append(person)

    # Sample from each category
    selected = []

    # Get 3-4 multi-role entries
    if samples['multi_role']:
        selected.extend(random.sample(samples['multi_role'], min(4, len(samples['multi_role']))))

    # Get 2-3 acting officials
    if samples['acting']:
        acting_sample = random.sample(samples['acting'], min(3, len(samples['acting'])))
        selected.extend([p for p in acting_sample if p not in selected])

    # Get 1-2 from different provinces (try to get variety)
    province_list = list(samples['provinces'].keys())
    if province_list:
        for _ in range(min(3, len(province_list))):
            prov = random.choice(province_list)
            if samples['provinces'][prov]:
                candidate = random.choice(samples['provinces'][prov])
                if candidate not in selected:
                    selected.append(candidate)
                province_list.remove(prov)

    # Get 1-2 native titles
    if samples['native_titles']:
        native_sample = random.sample(samples['native_titles'], min(2, len(samples['native_titles'])))
        selected.extend([p for p in native_sample if p not in selected])

    # Fill remaining with random samples
    remaining = [p for p in data if p not in selected]
    if remaining and len(selected) < count:
        selected.extend(random.sample(remaining, min(count - len(selected), len(remaining))))

    return selected[:count]

def read_source_line(year, line_number, year_stats, base_path='/home/user/colonial_office_list'):
    """Read a specific line from a source file using year to find the file"""
    try:
        # Get filename from year_stats
        if str(year) not in year_stats:
            return f"ERROR: Year {year} not found in year_stats"

        filename = year_stats[str(year)].get('file')
        if not filename:
            return f"ERROR: No file specified for year {year}"

        # Construct the filepath
        # Format: output_3/{year}_manual_parsed/{filename}
        filepath = Path(base_path) / 'output_3' / f'{year}_manual_parsed' / filename

        # Read the file
        # Note: line_number in JSON is 1-indexed (matching grep -n output)
        # but Python list indexing is 0-indexed, so we subtract 1
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = f.readlines()
            line_index = line_number - 1  # Convert to 0-based index
            if 0 <= line_index < len(lines):
                return lines[line_index].strip()
            else:
                return f"ERROR: Line {line_number} out of range (file has {len(lines)} lines)"
    except FileNotFoundError:
        return f"ERROR: Source file not found: {filepath}"
    except Exception as e:
        return f"ERROR: {str(e)}"

def verify_record(person, year_stats):
    """Verify a single record against source file"""
    verification = {
        'person': person,
        'source_line': None,
        'checks': {},
        'issues': []
    }

    # Read source line using year
    year = person.get('year')
    line_number = person.get('line_number')

    if year and line_number is not None:
        source_line = read_source_line(year, line_number, year_stats)
        verification['source_line'] = source_line

        # Check if person name exists in source
        name = person.get('name', '')
        if name and name in source_line:
            verification['checks']['name_found'] = True
        else:
            verification['checks']['name_found'] = False
            verification['issues'].append(f"Name '{name}' not found in source line")

        # Check role
        role = person.get('role', '')
        # Role might be abbreviated or split, so do partial match
        if role and any(word.lower() in source_line.lower() for word in role.split() if len(word) > 3):
            verification['checks']['role_plausible'] = True
        else:
            verification['checks']['role_plausible'] = False
            verification['issues'].append(f"Role '{role}' not clearly found in source")

        # Check for "and" if multi-role
        if person.get('multi_role_id'):
            if ' and ' in source_line.lower():
                verification['checks']['multi_role_and_found'] = True
            else:
                verification['checks']['multi_role_and_found'] = False
                verification['issues'].append("Multi-role entry but no 'and' in source line")

        # Check for acting indicators
        if person.get('is_acting'):
            acting_indicators = ['acting', 'actg.', 'a.', '(a)']
            if any(ind in source_line.lower() for ind in acting_indicators):
                verification['checks']['acting_indicator_found'] = True
            else:
                verification['checks']['acting_indicator_found'] = False
                verification['issues'].append("is_acting=true but no acting indicator in source")

    else:
        verification['issues'].append("Missing year or line number")

    return verification

def generate_report(stats, samples, verifications, metadata, output_path):
    """Generate comprehensive markdown quality report"""

    report = []
    report.append("# FIJI EXTRACTION QUALITY REVIEW")
    report.append(f"\nGenerated: 2025-11-20")
    report.append(f"\nExtraction System: **v2 Hybrid System** (Task-based LLM + Regex patterns)")
    report.append("\n---\n")

    # Executive Summary
    report.append("## EXECUTIVE SUMMARY\n")
    report.append(f"- **Total People Extracted**: {stats['total_people']:,}")
    report.append(f"- **Expected (from metadata)**: {metadata.get('total_people', 'N/A'):,}")
    report.append(f"- **Years Covered**: {stats['year_count']} years ({min(stats['years_list'])} - {max(stats['years_list'])})")
    report.append(f"- **Source Files**: {stats['file_count']} (expected: {metadata.get('files_processed', 'N/A')})")
    report.append(f"- **Multi-Role Entries**: {stats['multi_role_entries']:,} entries ({stats['unique_multi_role_groups']:,} unique groups)")
    report.append(f"- **Acting Officials**: {stats['acting_officials']:,}")
    report.append(f"- **Unknown Roles**: {stats['unknown_roles']:,} ({stats['unknown_roles']/stats['total_people']*100:.1f}%)")
    report.append(f"- **Average Confidence (metadata)**: {metadata.get('avg_confidence', 0)*100:.1f}%")
    report.append("")

    # Overall Statistics
    report.append("## OVERALL STATISTICS\n")
    report.append("### Confidence Distribution")
    report.append("| Confidence | Count | Percentage |")
    report.append("|------------|-------|------------|")
    for conf, count in sorted(stats['confidence_distribution'].items()):
        pct = count / stats['total_people'] * 100
        report.append(f"| {conf} | {count:,} | {pct:.1f}% |")
    report.append("")

    # Years covered
    report.append("### Years Covered")
    report.append(f"**{stats['year_count']} years total**: {', '.join(map(str, stats['years_list'][:10]))}...")
    report.append("")

    # Fiji-Specific Features
    report.append("## FIJI-SPECIFIC FEATURES\n")

    report.append("### Multi-Role Support")
    report.append(f"- **Total multi-role entries**: {stats['multi_role_entries']:,}")
    report.append(f"- **Unique multi-role groups**: {stats['unique_multi_role_groups']:,}")
    report.append(f"- **Average entries per group**: {stats['multi_role_entries']/stats['unique_multi_role_groups']:.2f}")
    report.append("")

    report.append("### Acting Officials")
    report.append(f"- **Total acting officials**: {stats['acting_officials']:,}")
    report.append(f"- **Percentage of total**: {stats['acting_officials']/stats['total_people']*100:.2f}%")
    report.append("")

    report.append("### Provincial Distribution")
    report.append(f"- **Provinces tracked**: {len(stats['provinces'])}")
    report.append("\n**Top 10 Provinces by Entries**:")
    report.append("| Province | Count |")
    report.append("|----------|-------|")
    for province, count in stats['provinces'].most_common(10):
        report.append(f"| {province} | {count:,} |")
    report.append("")

    report.append("### Top 20 Roles")
    report.append("| Role | Count |")
    report.append("|------|-------|")
    for role, count in stats['roles'].most_common(20):
        role_display = role[:60] + "..." if len(role) > 60 else role
        report.append(f"| {role_display} | {count:,} |")
    report.append("")

    # Sample Verification
    report.append("## SAMPLE VERIFICATION\n")
    report.append(f"**{len(samples)} records sampled** for detailed verification\n")

    # Count issues
    total_issues = sum(len(v['issues']) for v in verifications)
    records_with_issues = sum(1 for v in verifications if v['issues'])

    report.append(f"- **Records with issues**: {records_with_issues}/{len(verifications)}")
    report.append(f"- **Total issues found**: {total_issues}")
    report.append("")

    # Detail each verification
    for i, verification in enumerate(verifications, 1):
        person = verification['person']
        report.append(f"### Sample {i}: {person.get('name', 'Unknown')}")
        report.append("")

        # Person details
        year = person.get('year', 'N/A')
        line_num = person.get('line_number', 'N/A')
        report.append("**Extracted Data**:")
        report.append(f"- **Name**: {person.get('name', 'N/A')}")
        report.append(f"- **Role**: {person.get('role', 'N/A')}")
        report.append(f"- **Year**: {year}")
        report.append(f"- **Province**: {person.get('province', 'N/A')}")
        report.append(f"- **Confidence**: {person.get('confidence', 'N/A')}")
        report.append(f"- **Multi-role ID**: {person.get('multi_role_id', 'N/A')}")
        report.append(f"- **Is Acting**: {person.get('is_acting', False)}")
        report.append(f"- **Source**: output_3/{year}_manual_parsed/ (line {line_num})")
        report.append("")

        # Source line
        if verification['source_line']:
            report.append("**Source Line**:")
            report.append(f"```")
            report.append(verification['source_line'][:200])
            report.append(f"```")
            report.append("")

        # Verification results
        report.append("**Verification**:")
        for check, result in verification['checks'].items():
            status = "✓" if result else "✗"
            report.append(f"- {status} {check}: {result}")
        report.append("")

        # Issues
        if verification['issues']:
            report.append("**Issues Found**:")
            for issue in verification['issues']:
                report.append(f"- ⚠️ {issue}")
            report.append("")
        else:
            report.append("**No issues found** ✓")
            report.append("")

        report.append("---\n")

    # Issue Analysis
    report.append("## ISSUE ANALYSIS\n")

    issue_types = defaultdict(int)
    for v in verifications:
        for issue in v['issues']:
            # Categorize issues
            if 'name' in issue.lower():
                issue_types['Name not found'] += 1
            elif 'role' in issue.lower():
                issue_types['Role not found'] += 1
            elif 'multi-role' in issue.lower():
                issue_types['Multi-role indicator missing'] += 1
            elif 'acting' in issue.lower():
                issue_types['Acting indicator missing'] += 1
            else:
                issue_types['Other'] += 1

    if issue_types:
        report.append("**Issue Type Breakdown**:")
        report.append("| Issue Type | Count |")
        report.append("|------------|-------|")
        for issue_type, count in sorted(issue_types.items(), key=lambda x: -x[1]):
            report.append(f"| {issue_type} | {count} |")
        report.append("")

    # Quality Assessment
    report.append("## QUALITY ASSESSMENT\n")

    # Calculate quality score
    accuracy_score = 100

    # Deduct for issues in sample
    if len(samples) > 0:
        sample_error_rate = records_with_issues / len(samples) * 100
        accuracy_score -= sample_error_rate * 0.5  # Weight sample errors

    # Deduct for unknown roles
    unknown_role_pct = stats['unknown_roles'] / stats['total_people'] * 100
    accuracy_score -= min(unknown_role_pct * 0.3, 10)  # Max 10 point deduction

    # Add points for good features
    if stats['multi_role_entries'] > 0:
        accuracy_score += 5  # Bonus for multi-role support
    if stats['acting_officials'] > 0:
        accuracy_score += 5  # Bonus for acting detection

    accuracy_score = max(0, min(100, accuracy_score))

    report.append(f"### Overall Quality Score: {accuracy_score:.1f}/100\n")

    if accuracy_score >= 90:
        grade = "A - Excellent"
    elif accuracy_score >= 80:
        grade = "B - Good"
    elif accuracy_score >= 70:
        grade = "C - Acceptable"
    elif accuracy_score >= 60:
        grade = "D - Needs Improvement"
    else:
        grade = "F - Poor"

    report.append(f"**Grade**: {grade}\n")

    # Strengths
    report.append("### Strengths\n")
    strengths = []

    if stats['multi_role_entries'] > 0:
        strengths.append(f"✓ Successfully extracted {stats['multi_role_entries']:,} multi-role entries ({stats['unique_multi_role_groups']:,} groups)")
    if stats['acting_officials'] > 0:
        strengths.append(f"✓ Identified {stats['acting_officials']:,} acting officials")
    if len(stats['provinces']) >= 10:
        strengths.append(f"✓ Tracked {len(stats['provinces'])} provinces (good coverage)")
    if stats['confidence_distribution'].get('high', 0) / stats['total_people'] > 0.7:
        strengths.append(f"✓ High confidence rate: {stats['confidence_distribution'].get('high', 0) / stats['total_people'] * 100:.1f}%")
    if stats['year_count'] >= 60:
        strengths.append(f"✓ Comprehensive temporal coverage: {stats['year_count']} years")

    for strength in strengths:
        report.append(strength)
    report.append("")

    # Weaknesses
    report.append("### Weaknesses\n")
    weaknesses = []

    if records_with_issues > 0:
        weaknesses.append(f"⚠️ {records_with_issues}/{len(samples)} sampled records had verification issues")
    if unknown_role_pct > 5:
        weaknesses.append(f"⚠️ High unknown role rate: {unknown_role_pct:.1f}%")
    if total_issues > 0:
        weaknesses.append(f"⚠️ {total_issues} total issues found in sample verification")

    if weaknesses:
        for weakness in weaknesses:
            report.append(weakness)
        report.append("")
    else:
        report.append("No significant weaknesses identified in sample ✓")
        report.append("")

    # Recommendations
    report.append("## RECOMMENDATIONS\n")

    recommendations = []

    if unknown_role_pct > 5:
        recommendations.append("1. **Reduce unknown roles**: Consider improving role extraction logic or providing more context to the LLM")

    if issue_types.get('Multi-role indicator missing', 0) > 0:
        recommendations.append("2. **Review multi-role detection**: Some multi-role entries may lack proper 'and' indicators in source")

    if issue_types.get('Acting indicator missing', 0) > 0:
        recommendations.append("3. **Review acting official detection**: Validate acting flag logic against various acting indicators")

    if len(stats['provinces']) < 17:
        recommendations.append(f"4. **Province coverage**: Only {len(stats['provinces'])} provinces found (expected ~17 Fiji provinces)")

    if not recommendations:
        recommendations.append("No major improvements needed. Extraction quality is good.")

    for rec in recommendations:
        report.append(rec)
    report.append("")

    # Conclusion
    report.append("## CONCLUSION\n")
    report.append(f"The Fiji extraction using the v2 hybrid system processed {stats['total_people']:,} people ")
    report.append(f"across {stats['year_count']} years with a quality score of {accuracy_score:.1f}/100. ")

    if accuracy_score >= 80:
        report.append("The extraction demonstrates **high quality** with strong support for Fiji-specific features ")
        report.append("including multi-role entries and acting officials. ")
    elif accuracy_score >= 70:
        report.append("The extraction demonstrates **good quality** with reasonable support for Fiji-specific features, ")
        report.append("though some improvements could be made. ")
    else:
        report.append("The extraction shows **moderate quality** and would benefit from refinement of extraction logic. ")

    if stats['multi_role_entries'] > 0:
        report.append(f"The multi-role support successfully split {stats['unique_multi_role_groups']:,} combined entries. ")

    report.append("")
    report.append("---")
    report.append("\n*Quality review completed with automated verification against source files*")

    # Write report
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(report))

    print(f"Quality report written to {output_path}")
    return accuracy_score

def main():
    print("Fiji Extraction Quality Assessment")
    print("=" * 60)

    # Load data
    print("\n1. Loading extraction data...")
    data_path = '/home/user/colonial_office_list/fiji_all_years_v2.json'
    metadata, data, year_stats = load_extraction_data(data_path)
    print(f"   Loaded {len(data):,} records")
    print(f"   Metadata says: {metadata.get('total_people', 'N/A')} people expected")
    print(f"   Year mappings: {len(year_stats)} years")

    # Calculate statistics
    print("\n2. Calculating statistics...")
    stats = calculate_statistics(data)
    print(f"   Years: {stats['year_count']}")
    print(f"   Multi-role entries: {stats['multi_role_entries']:,}")
    print(f"   Acting officials: {stats['acting_officials']:,}")
    print(f"   Provinces: {len(stats['provinces'])}")

    # Sample records
    print("\n3. Sampling records for verification...")
    samples = sample_records(data, count=15)
    print(f"   Selected {len(samples)} samples")
    print(f"   - Multi-role: {sum(1 for s in samples if s.get('multi_role_id'))}")
    print(f"   - Acting: {sum(1 for s in samples if s.get('is_acting'))}")
    print(f"   - With provinces: {sum(1 for s in samples if s.get('province'))}")

    # Verify samples
    print("\n4. Verifying samples against source files...")
    verifications = []
    for i, sample in enumerate(samples, 1):
        verification = verify_record(sample, year_stats)
        verifications.append(verification)
        issues = len(verification['issues'])
        status = "✓" if issues == 0 else f"✗ ({issues} issues)"
        print(f"   Sample {i:2d}: {sample.get('name', 'Unknown')[:30]:30s} {status}")

    # Generate report
    print("\n5. Generating quality report...")
    output_path = '/home/user/colonial_office_list/FIJI_QUALITY_REVIEW.md'
    quality_score = generate_report(stats, samples, verifications, metadata, output_path)

    print(f"\n{'='*60}")
    print(f"Quality Score: {quality_score:.1f}/100")
    print(f"Report saved to: {output_path}")
    print(f"{'='*60}")

if __name__ == '__main__':
    random.seed(42)  # For reproducibility
    main()
