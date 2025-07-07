#!/bin/bash

# Complete Improvement Report Generator & PDF Creator
# Generates a comprehensive report of all PON ecosystem improvements

echo "🚀 PON Ecosystem Improvement Report Generator"
echo "=============================================="
echo ""

# Generate the improvement report
echo "📊 Step 1: Collecting improvement data..."
python3 generate_improvement_report.py

if [ $? -ne 0 ]; then
    echo "❌ Error generating improvement report"
    exit 1
fi

echo ""
echo "📄 Step 2: Converting to professional PDF..."

# Check if generate-pdf.sh exists and is executable
if [ ! -x "./generate-pdf.sh" ]; then
    echo "⚠️  Making generate-pdf.sh executable..."
    chmod +x generate-pdf.sh
fi

# Generate PDF with professional formatting
./generate-pdf.sh improvement_report.md "PON-Improvements-Report-$(date +%Y%m%d)"

if [ $? -eq 0 ]; then
    echo ""
    echo "🎉 SUCCESS! Complete improvement report generated:"
    echo "   📝 Markdown: improvement_report.md"
    echo "   📄 PDF: PON-Improvements-Report-$(date +%Y%m%d).pdf"
    echo ""
    echo "📋 Report includes:"
    echo "   ✅ Git commits from last 2 days"
    echo "   ✅ AI system activities & learning"
    echo "   ✅ Deployment history"
    echo "   ✅ Emergency fixes applied"
    echo "   ✅ System improvements"
    echo "   ✅ Current service status"
    echo ""
    echo "🔗 Quick links:"
    echo "   - AI Terminal: https://instant-grok-terminal.onrender.com"
    echo "   - Render Dashboard: https://dashboard.render.com/"
else
    echo "❌ Error generating PDF. Check that pandoc and xelatex are installed."
    echo "💡 Install with: brew install pandoc"
    exit 1
fi
