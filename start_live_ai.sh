#!/bin/bash
"""
LIVE AI TERMINAL LAUNCHER
========================
Launches the live AI terminal with proper environment setup
"""

echo "🚀 Starting Live AI Terminal with Grok Integration..."

# Check if we're in the right directory
if [[ ! -f "live_ai_terminal.py" ]]; then
    echo "❌ Error: live_ai_terminal.py not found in current directory"
    echo "Please run this script from the project root directory"
    exit 1
fi

# Check for GROK_API_KEY
if [[ -z "$GROK_API_KEY" ]]; then
    echo "⚠️  Warning: GROK_API_KEY environment variable not set"
    echo "Please set your Grok API key:"
    echo "export GROK_API_KEY='your-api-key-here'"
    echo ""
    read -p "Continue anyway? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Install required dependencies if needed
echo "📦 Checking dependencies..."
python3 -m pip install requests asyncio --quiet

# Create logs directory if it doesn't exist
mkdir -p logs

# Clear terminal and start
clear

echo "╔════════════════════════════════════════════════════════════════════════════════╗"
echo "║                            LIVE AI TERMINAL STARTING                          ║"  
echo "║                                                                                ║"
echo "║  🤖 Grok AI Integration                                                        ║"
echo "║  🧠 Real-time Thought Processing                                               ║"
echo "║  📊 Live Log Monitoring                                                        ║"
echo "║  🔧 Automatic Error Fixing                                                     ║"
echo "║                                                                                ║"
echo "║  Press Ctrl+C to exit at any time                                             ║"
echo "╚════════════════════════════════════════════════════════════════════════════════╝"
echo ""

# Start the live AI terminal
python3 live_ai_terminal.py
