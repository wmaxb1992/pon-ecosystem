#!/bin/bash

# PON Ecosystem Deployment Status Checker
# ========================================
# This script helps you check the status of your PON ecosystem deployment

echo "🔍 PON Ecosystem Deployment Status Checker"
echo "=========================================="
echo ""

# Check if we can reach the main services
echo "📡 Checking Service Endpoints..."

# Main application
echo -n "Main App (pon-ecosystem): "
if curl -s --connect-timeout 10 https://pon-ecosystem.onrender.com/health > /dev/null 2>&1; then
    echo "✅ LIVE"
else
    echo "⏳ PENDING/BUILDING"
fi

# AI Terminal
echo -n "AI Terminal (instant-grok-terminal): "
if curl -s --connect-timeout 10 https://instant-grok-terminal.onrender.com/ > /dev/null 2>&1; then
    echo "✅ LIVE"
else
    echo "⏳ PENDING/BUILDING"
fi

echo ""
echo "🛠️ Manual Check Instructions:"
echo "=========================================="
echo ""
echo "1. Go to your Render.com Dashboard:"
echo "   https://dashboard.render.com/"
echo ""
echo "2. Look for these services and their status:"
echo "   ✓ pon-ecosystem (Web Service) - Main app"
echo "   ✓ ceo-ai-bot (Background Worker) - AI orchestration"
echo "   ✓ ai-code-worker (Background Worker) - Code generation"
echo "   ✓ ai-code-worker-2 (Background Worker) - Code generation backup"
echo "   ✓ ai-quality-worker (Background Worker) - Quality assurance"
echo "   ✓ ai-memory-worker (Background Worker) - Memory management"
echo "   ✓ instant-grok-terminal (Web Service) - AI terminal"
echo "   ✓ pon-redis (Key Value Store) - Cache/queue"
echo "   ✓ pon-database (PostgreSQL) - Main database"
echo ""
echo "3. Status Indicators:"
echo "   🟢 Live = Service is running successfully"
echo "   🟡 Building = Service is being built/deployed"
echo "   🔴 Failed = Service encountered an error"
echo "   ⏸️ Sleeping = Free tier service is inactive"
echo ""
echo "4. Expected Timeline:"
echo "   • Databases (Redis, PostgreSQL): 2-5 minutes"
echo "   • Background Workers: 5-8 minutes"
echo "   • Web Services: 8-15 minutes"
echo ""
echo "5. When ALL services show 'Live':"
echo "   🎉 Your PON Ecosystem is fully deployed!"
echo "   🌐 Main App: https://pon-ecosystem.onrender.com"
echo "   🤖 AI Terminal: https://instant-grok-terminal.onrender.com"
echo ""
echo "6. Troubleshooting:"
echo "   • Click on any service to view build logs"
echo "   • Check for error messages in the logs"
echo "   • Verify environment variables are set correctly"
echo ""
echo "📊 Current GitHub Status:"
git log --oneline -1
echo ""
echo "🔗 Quick Links:"
echo "   • Render Dashboard: https://dashboard.render.com/"
echo "   • GitHub Repository: https://github.com/wmaxb1992/cream"
echo "   • Deployment Guide: See DEPLOYMENT_GUIDE.md in your repo"
