#!/bin/bash

# Quick Local Deploy Script
# Uses existing start.sh but with online access options

set -e

echo "🚀 PON Ecosystem Quick Deploy"
echo "============================="

# Check if ngrok is available for online access
if command -v ngrok &> /dev/null; then
    echo "🌍 ngrok found - online access available"
    echo "Choose deployment mode:"
    echo "1. Local only (localhost)"
    echo "2. Local + Online (public URLs)"
    read -p "Enter choice (1 or 2): " choice
    
    if [ "$choice" = "2" ]; then
        echo "🌐 Starting with online access..."
        
        # Start the main application
        echo "🚀 Starting PON ecosystem..."
        ./start.sh &
        MAIN_PID=$!
        
        # Wait for services to start
        echo "⏳ Waiting for services to start..."
        sleep 10
        
        # Start ngrok tunnels
        echo "🔗 Creating public URLs..."
        ngrok http 8000 --log=stdout > /dev/null &
        NGROK_BACKEND_PID=$!
        
        ngrok http 3000 --log=stdout > /dev/null &
        NGROK_FRONTEND_PID=$!
        
        sleep 5
        
        echo "✅ Services started!"
        echo "📍 Local Access:"
        echo "   - Backend: http://localhost:8000"
        echo "   - Frontend: http://localhost:3000"
        echo "🌍 Online Access:"
        echo "   - Check ngrok dashboard: http://localhost:4040"
        
        # Keep running until interrupted
        echo "⚡ All services running... Press Ctrl+C to stop"
        trap 'echo "🛑 Stopping all services..."; kill $MAIN_PID $NGROK_BACKEND_PID $NGROK_FRONTEND_PID 2>/dev/null; exit' INT
        wait
    else
        echo "🏠 Starting locally only..."
        ./start.sh
    fi
else
    echo "⚠️ ngrok not found - running locally only"
    echo "💡 Install ngrok for online access: brew install ngrok"
    echo "🚀 Starting local deployment..."
    ./start.sh
fi
