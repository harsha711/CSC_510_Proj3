#!/usr/bin/env python3
"""
Generate Coverage Badge

This script generates a coverage badge based on pytest coverage results.

Requirements:
    pip install coverage-badge

Usage:
    python generate_coverage_badge.py

Output:
    - coverage.svg (badge image)
    - Displays coverage percentage
"""

import subprocess
import sys
import re
import os

def get_coverage_percentage():
    """Extract coverage percentage from coverage report"""
    try:
        # Run coverage report
        result = subprocess.run(
            ['coverage', 'report', '--precision=2'],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(__file__)
        )

        if result.returncode != 0:
            print("❌ Error running coverage report")
            print(result.stderr)
            return None

        # Parse the output to find TOTAL line
        lines = result.stdout.split('\n')
        for line in lines:
            if 'TOTAL' in line:
                # Extract percentage (last column)
                parts = line.split()
                for part in parts:
                    if '%' in part:
                        percentage = part.rstrip('%')
                        return float(percentage)

        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def generate_badge(percentage):
    """Generate coverage badge SVG"""
    try:
        # Determine color based on percentage
        if percentage >= 80:
            color = 'brightgreen'
        elif percentage >= 60:
            color = 'green'
        elif percentage >= 40:
            color = 'yellow'
        elif percentage >= 20:
            color = 'orange'
        else:
            color = 'red'

        # Generate badge using shields.io style SVG
        badge_svg = f'''<svg xmlns="http://www.w3.org/2000/svg" width="120" height="20">
    <linearGradient id="b" x2="0" y2="100%">
        <stop offset="0" stop-color="#bbb" stop-opacity=".1"/>
        <stop offset="1" stop-opacity=".1"/>
    </linearGradient>
    <mask id="a">
        <rect width="120" height="20" rx="3" fill="#fff"/>
    </mask>
    <g mask="url(#a)">
        <path fill="#555" d="M0 0h63v20H0z"/>
        <path fill="#{get_color_hex(color)}" d="M63 0h57v20H63z"/>
        <path fill="url(#b)" d="M0 0h120v20H0z"/>
    </g>
    <g fill="#fff" text-anchor="middle" font-family="DejaVu Sans,Verdana,Geneva,sans-serif" font-size="11">
        <text x="31.5" y="15" fill="#010101" fill-opacity=".3">coverage</text>
        <text x="31.5" y="14">coverage</text>
        <text x="90.5" y="15" fill="#010101" fill-opacity=".3">{percentage:.1f}%</text>
        <text x="90.5" y="14">{percentage:.1f}%</text>
    </g>
</svg>'''

        # Write badge
        with open('coverage.svg', 'w') as f:
            f.write(badge_svg)

        print(f"✅ Badge generated: coverage.svg ({color})")
        return True

    except Exception as e:
        print(f"❌ Error generating badge: {e}")
        return False

def get_color_hex(color_name):
    """Get hex color code"""
    colors = {
        'brightgreen': '4c1',
        'green': '97CA00',
        'yellow': 'dfb317',
        'orange': 'fe7d37',
        'red': 'e05d44'
    }
    return colors.get(color_name, '9f9f9f')

def main():
    print("=" * 50)
    print("SafeBites Coverage Badge Generator")
    print("=" * 50)

    # Check if coverage data exists
    if not os.path.exists('.coverage'):
        print("\n❌ No coverage data found!")
        print("Run tests with coverage first:")
        print("  pytest tests/ --cov=app --cov-report=html")
        return 1

    # Get coverage percentage
    print("\n📊 Calculating coverage...")
    percentage = get_coverage_percentage()

    if percentage is None:
        print("❌ Could not extract coverage percentage")
        return 1

    print(f"\n✅ Coverage: {percentage:.2f}%")

    # Generate badge
    print("\n🎨 Generating badge...")
    if generate_badge(percentage):
        print(f"\n✅ Done! Coverage badge saved to: coverage.svg")
        print(f"   Add to README: ![Coverage](./coverage.svg)")
    else:
        return 1

    # Display coverage breakdown
    print("\n" + "=" * 50)
    print("Coverage Breakdown:")
    print("=" * 50)
    subprocess.run(['coverage', 'report', '--precision=2'])

    return 0

if __name__ == '__main__':
    sys.exit(main())
