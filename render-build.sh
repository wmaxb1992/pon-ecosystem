# Render.com Build Script
#!/bin/bash
set -e

echo "🚀 Building Epic AI Terminal for Render.com"
echo "=========================================="

# Install system dependencies
echo "📦 Installing system packages..."
apt-get update
apt-get install -y openssh-client redis-tools

# Install Python dependencies
echo "🐍 Installing Python packages..."
pip install --upgrade pip
pip install -r requirements_render.txt

# Set up SSH keys (optional)
echo "🔐 Setting up SSH configuration..."
mkdir -p ~/.ssh
chmod 700 ~/.ssh

# Create startup script
echo "📝 Creating startup script..."
cat > start.sh << 'EOF'
#!/bin/bash

echo "🚀 Starting Epic AI Terminal..."

# Start Redis if not available (for development)
if ! redis-cli ping > /dev/null 2>&1; then
    echo "⚠️ Redis not available, using mock mode"
fi

# Start the main application
python render_main.py
EOF

chmod +x start.sh

echo "✅ Build complete!"
echo "🚀 Ready to deploy on Render.com"
