#!/bin/bash

# PON Ecosystem Deployment Test Script
# ====================================
# Run this after your Render.com deployment completes

echo "🧪 Testing PON Ecosystem Deployment..."
echo "======================================"

# Main app health check
echo "🔍 Testing main application..."
if curl -s https://pon-ecosystem.onrender.com/health > /dev/null; then
    echo "✅ Main app is responding"
else
    echo "⏳ Main app still starting up (this is normal)"
fi

# AI Terminal check
echo "🔍 Testing AI terminal..."
if curl -s https://instant-grok-terminal.onrender.com/ > /dev/null; then
    echo "✅ AI terminal is responding"
else
    echo "⏳ AI terminal still starting up (this is normal)"
fi

echo ""
echo "🌐 Your PON Ecosystem URLs:"
echo "   Main App: https://pon-ecosystem.onrender.com"
echo "   AI Terminal: https://instant-grok-terminal.onrender.com"
echo ""
echo "📊 Monitor deployment progress:"
echo "   https://dashboard.render.com/"
echo ""
echo "💡 Note: First deployment takes 10-15 minutes"
echo "   Services start in this order:"
echo "   1. Redis + PostgreSQL databases"
echo "   2. AI workers connect to Redis"
echo "   3. Web services come online"
echo ""
echo "🎉 Once all services show 'Live' status, your PON ecosystem is ready!"
