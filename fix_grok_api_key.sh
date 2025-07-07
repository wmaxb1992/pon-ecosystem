#!/bin/bash

# 🚨 URGENT: Grok API Key Security Fix
# ====================================
# Your Grok API key was blocked due to exposure. Here's how to fix it:

echo "🚨 GROK API KEY SECURITY INCIDENT - RESOLUTION GUIDE"
echo "=================================================="
echo
echo "📋 ISSUE: Your Grok API key was blocked due to public exposure"
echo "✅ SOLUTION: Generate new API key and update services"
echo

echo "🔧 STEP 1: Generate New Grok API Key"
echo "-----------------------------------"
echo "1. Go to: https://console.x.ai/api-keys"
echo "2. Login with your X.AI account"
echo "3. Delete the old API key (if visible)"
echo "4. Create a new API key"
echo "5. Copy the new key (starts with 'xai-')"
echo

echo "🔧 STEP 2: Update Local Environment"
echo "-----------------------------------"
echo "1. Edit your .env file:"
echo "   nano /Users/maxwoldenberg/Desktop/pon/.env"
echo "2. Replace the GROK_API_KEY line with your new key:"
echo "   GROK_API_KEY=your_new_key_here"
echo "3. Save the file"
echo

echo "🔧 STEP 3: Update Render Services"
echo "-----------------------------------"
echo "Run these commands to update all your AI workers:"
echo
echo "# Update each service with new API key"
echo "render env set GROK_API_KEY=your_new_key_here --service ai-code-worker"
echo "render env set GROK_API_KEY=your_new_key_here --service ai-code-worker-2"
echo "render env set GROK_API_KEY=your_new_key_here --service ai-memory-worker"
echo "render env set GROK_API_KEY=your_new_key_here --service ai-quality-worker"
echo "render env set GROK_API_KEY=your_new_key_here --service ceo-ai-bot"
echo "render env set GROK_API_KEY=your_new_key_here --service autonomous-executor"
echo "render env set GROK_API_KEY=your_new_key_here --service pon-ecosystem"
echo
echo "# Redeploy all services"
echo "render deploy --service ai-code-worker"
echo "render deploy --service ai-code-worker-2"
echo "render deploy --service ai-memory-worker"
echo "render deploy --service ai-quality-worker"
echo "render deploy --service ceo-ai-bot"
echo "render deploy --service autonomous-executor"
echo

echo "🔧 STEP 4: Security Best Practices"
echo "-----------------------------------"
echo "✅ Never commit API keys to git repositories"
echo "✅ Use environment variables for all secrets"
echo "✅ Regularly rotate API keys"
echo "✅ Monitor for API key leaks"
echo

echo "🚀 STEP 5: Test Connection"
echo "-----------------------------------"
echo "After updating, test with:"
echo "python3 live_ceo_chat.py"
echo

echo "📞 IMMEDIATE ACCESS ALTERNATIVES:"
echo "-----------------------------------"
echo "While fixing the API key, you can use:"
echo "1. OpenRouter API (backup provider already configured)"
echo "2. Local AI simulation mode"
echo "3. Manual coordination through Render dashboard"
echo

read -p "🔑 Do you have your new Grok API key ready? (y/n): " has_key

if [ "$has_key" = "y" ] || [ "$has_key" = "Y" ]; then
    read -p "🔑 Enter your new Grok API key: " new_api_key
    
    if [ ! -z "$new_api_key" ]; then
        echo "🔄 Updating local .env file..."
        sed -i.backup "s/GROK_API_KEY=.*/GROK_API_KEY=$new_api_key/" .env
        echo "✅ Local .env file updated!"
        
        echo "🚀 Updating Render services..."
        echo "⚠️  Please run these commands manually:"
        echo
        echo "render env set GROK_API_KEY=$new_api_key --service ai-code-worker"
        echo "render env set GROK_API_KEY=$new_api_key --service ai-code-worker-2"
        echo "render env set GROK_API_KEY=$new_api_key --service ai-memory-worker"
        echo "render env set GROK_API_KEY=$new_api_key --service ai-quality-worker"
        echo "render env set GROK_API_KEY=$new_api_key --service ceo-ai-bot"
        echo "render env set GROK_API_KEY=$new_api_key --service autonomous-executor"
        echo
        echo "🔄 Then redeploy services:"
        echo "render deploy --service ceo-ai-bot"
        echo
    else
        echo "❌ No API key provided. Please run this script again with your new key."
    fi
else
    echo "📝 Please get your new API key from: https://console.x.ai/api-keys"
    echo "🔄 Then run this script again"
fi

echo
echo "🎯 PRIORITY: Fix CEO AI Bot first with:"
echo "render env set GROK_API_KEY=your_new_key --service ceo-ai-bot"
echo "render deploy --service ceo-ai-bot"
