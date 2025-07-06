#!/bin/bash
set -e

# Live AI Terminal - Debian Package Builder
# ========================================

PACKAGE_NAME="live-ai-terminal"
PACKAGE_VERSION="1.0.0"
ARCHITECTURE="all"
PACKAGE_DIR="/Users/maxwoldenberg/Desktop/pon/debian-package"
BUILD_DIR="/Users/maxwoldenberg/Desktop/pon/build"

echo "🏗️  Building Live AI Terminal Debian Package"
echo "============================================="

# Clean previous build
echo "🧹 Cleaning previous build..."
rm -rf "$BUILD_DIR"
mkdir -p "$BUILD_DIR"

# Copy package structure
echo "📦 Copying package structure..."
cp -r "$PACKAGE_DIR" "$BUILD_DIR/${PACKAGE_NAME}_${PACKAGE_VERSION}_${ARCHITECTURE}"

# Set proper permissions
echo "🔧 Setting permissions..."
find "$BUILD_DIR/${PACKAGE_NAME}_${PACKAGE_VERSION}_${ARCHITECTURE}" -type f -name "*.py" -exec chmod 644 {} \;
find "$BUILD_DIR/${PACKAGE_NAME}_${PACKAGE_VERSION}_${ARCHITECTURE}" -type f -name "*.sh" -exec chmod 755 {} \;
chmod 755 "$BUILD_DIR/${PACKAGE_NAME}_${PACKAGE_VERSION}_${ARCHITECTURE}/usr/local/bin/live-ai-terminal"
chmod 755 "$BUILD_DIR/${PACKAGE_NAME}_${PACKAGE_VERSION}_${ARCHITECTURE}/DEBIAN/postinst"
chmod 755 "$BUILD_DIR/${PACKAGE_NAME}_${PACKAGE_VERSION}_${ARCHITECTURE}/DEBIAN/prerm"

# Update package size
echo "📏 Calculating package size..."
INSTALLED_SIZE=$(du -sk "$BUILD_DIR/${PACKAGE_NAME}_${PACKAGE_VERSION}_${ARCHITECTURE}" | cut -f1)
sed -i '' "s/Installed-Size: .*/Installed-Size: $INSTALLED_SIZE/" "$BUILD_DIR/${PACKAGE_NAME}_${PACKAGE_VERSION}_${ARCHITECTURE}/DEBIAN/control"

# Build the package
echo "🔨 Building Debian package..."
cd "$BUILD_DIR"
dpkg-deb --build "${PACKAGE_NAME}_${PACKAGE_VERSION}_${ARCHITECTURE}"

# Move to final location
FINAL_PACKAGE="$BUILD_DIR/${PACKAGE_NAME}_${PACKAGE_VERSION}_${ARCHITECTURE}.deb"
if [ -f "$FINAL_PACKAGE" ]; then
    echo "✅ Package built successfully!"
    echo "📍 Location: $FINAL_PACKAGE"
    echo "📊 Size: $(du -h "$FINAL_PACKAGE" | cut -f1)"
    
    # Package info
    echo ""
    echo "📋 Package Information:"
    dpkg-deb --info "$FINAL_PACKAGE"
    
    echo ""
    echo "🚀 Installation Commands:"
    echo "  sudo dpkg -i '$FINAL_PACKAGE'"
    echo "  sudo apt-get install -f  # If dependencies are missing"
    echo ""
    echo "🔧 After installation:"
    echo "  1. Configure: sudo nano /etc/live-ai-terminal/config.env"
    echo "  2. Run: live-ai-terminal"
    echo ""
else
    echo "❌ Package build failed!"
    exit 1
fi
