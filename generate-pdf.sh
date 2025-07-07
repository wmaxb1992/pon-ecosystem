#!/bin/bash

# Professional PDF Generator Script
# Usage: ./generate-pdf.sh input.md [output-name]

INPUT_FILE="$1"
OUTPUT_NAME="${2:-output}"
OUTPUT_FILE="${OUTPUT_NAME}.pdf"

# Check if input file exists
if [ ! -f "$INPUT_FILE" ]; then
    echo "Error: Input file '$INPUT_FILE' not found"
    exit 1
fi

echo "🔄 Generating professional PDF from $INPUT_FILE..."

# Generate PDF with professional formatting
pandoc "$INPUT_FILE" -o "$OUTPUT_FILE" \
  --pdf-engine=xelatex \
  --toc \
  --toc-depth=3 \
  --number-sections \
  --variable=geometry:margin=1in \
  --variable=fontsize=11pt \
  --variable=documentclass=article \
  --variable=fontfamily=charter \
  --variable=linestretch=1.2

if [ $? -eq 0 ]; then
    echo "✅ PDF generated successfully: $OUTPUT_FILE"
    echo "📄 File size: $(ls -lh "$OUTPUT_FILE" | awk '{print $5}')"
    
    # Open the PDF (macOS)
    if command -v open &> /dev/null; then
        open "$OUTPUT_FILE"
    fi
else
    echo "❌ Error generating PDF"
    exit 1
fi
