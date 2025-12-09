#!/bin/bash
# Quick Coverage Report Display

echo "═══════════════════════════════════════════"
echo "  SafeBites Code Coverage Report"
echo "═══════════════════════════════════════════"
echo ""

# Run tests with coverage
source venv/bin/activate
pytest tests/test_*.py \
    --cov=app \
    --cov-report=term-missing \
    --cov-report=html \
    -q

echo ""
echo "═══════════════════════════════════════════"
echo "  Coverage Summary"
echo "═══════════════════════════════════════════"

# Extract and display total coverage percentage
coverage report | grep TOTAL | awk '{print "Total Coverage: " $4}'

echo ""
echo "📊 Detailed HTML report: htmlcov/index.html"
echo "   Open with: xdg-open htmlcov/index.html"
echo ""

# Generate badge
python3 generate_coverage_badge.py

echo ""
echo "✅ Done!"
