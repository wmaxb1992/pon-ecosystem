#!/bin/bash
set -e

# Live AI Terminal - Package Verification Script
# ==============================================

PACKAGE_DIR="/Users/maxwoldenberg/Desktop/pon/debian-package"

echo "🔍 Verifying Live AI Terminal Package Structure"
echo "==============================================="

# Check directory structure
echo "📁 Checking directory structure..."
if [ ! -d "$PACKAGE_DIR" ]; then
    echo "❌ Package directory not found: $PACKAGE_DIR"
    exit 1
fi

# Check DEBIAN files
echo "🔧 Checking DEBIAN control files..."
for file in control postinst prerm; do
    if [ ! -f "$PACKAGE_DIR/DEBIAN/$file" ]; then
        echo "❌ Missing DEBIAN file: $file"
        exit 1
    else
        echo "✅ Found: DEBIAN/$file"
    fi
done

# Check executable
echo "🚀 Checking main executable..."
if [ ! -f "$PACKAGE_DIR/usr/local/bin/live-ai-terminal" ]; then
    echo "❌ Missing main executable"
    exit 1
else
    echo "✅ Found: usr/local/bin/live-ai-terminal"
fi

# Check application files
echo "📦 Checking application files..."
APP_DIR="$PACKAGE_DIR/usr/share/live-ai-terminal"
required_files=(
    "live_ai_terminal.py"
    "ai_memory_system.py"
    "ai_thought_processor.py"
    "enhanced_grok_integration.py"
    "requirements.txt"
    "config.template.env"
    "README.md"
)

for file in "${required_files[@]}"; do
    if [ ! -f "$APP_DIR/$file" ]; then
        echo "❌ Missing application file: $file"
        exit 1
    else
        echo "✅ Found: $file"
    fi
done

# Check systemd service
echo "⚙️ Checking systemd service..."
if [ ! -f "$PACKAGE_DIR/etc/systemd/system/live-ai-terminal.service" ]; then
    echo "❌ Missing systemd service file"
    exit 1
else
    echo "✅ Found: systemd service file"
fi

# Check permissions
echo "🔒 Checking file permissions..."
if [ ! -x "$PACKAGE_DIR/usr/local/bin/live-ai-terminal" ]; then
    echo "⚠️  Main executable not executable, fixing..."
    chmod +x "$PACKAGE_DIR/usr/local/bin/live-ai-terminal"
fi

if [ ! -x "$PACKAGE_DIR/DEBIAN/postinst" ]; then
    echo "⚠️  postinst not executable, fixing..."
    chmod +x "$PACKAGE_DIR/DEBIAN/postinst"
fi

if [ ! -x "$PACKAGE_DIR/DEBIAN/prerm" ]; then
    echo "⚠️  prerm not executable, fixing..."
    chmod +x "$PACKAGE_DIR/DEBIAN/prerm"
fi

# Calculate package size
echo "📊 Calculating package statistics..."
TOTAL_SIZE=$(du -sh "$PACKAGE_DIR" | cut -f1)
FILE_COUNT=$(find "$PACKAGE_DIR" -type f | wc -l)

echo ""
echo "✅ Package verification complete!"
echo "================================="
echo "📦 Total size: $TOTAL_SIZE"
echo "📄 File count: $FILE_COUNT"
echo ""
echo "🏗️  Package contents:"
find "$PACKAGE_DIR" -type f | sed 's|^.*/debian-package/||' | sort

echo ""
echo "🐧 For Debian/Ubuntu systems, you can build with:"
echo "   cd '$PACKAGE_DIR/..' && dpkg-deb --build debian-package"
echo ""
echo "📚 Documentation:"
echo "   - System architecture: /Users/maxwoldenberg/Desktop/pon/SYSTEM_ARCHITECTURE.md"
echo "   - Package README: $APP_DIR/README.md"
echo ""

# Create a tar.gz archive for distribution
echo "📦 Creating distribution archive..."
cd "$(dirname "$PACKAGE_DIR")"
tar -czf "live-ai-terminal-1.0.0.tar.gz" -C "$PACKAGE_DIR" .
echo "✅ Created: $(pwd)/live-ai-terminal-1.0.0.tar.gz"
echo ""
echo "🚀 Ready for deployment!"
