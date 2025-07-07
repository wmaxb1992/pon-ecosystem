#!/bin/bash

# Render CLI Emergency Fix Deployment Script
# Updates all failed services to use the fixed repository

echo "🚀 DEPLOYING EMERGENCY FIXES VIA RENDER CLI"
echo "============================================"

# Service IDs that need to be updated with fixes
FAILED_SERVICES=(
    "srv-d1l4g2be5dus73f7pe7g"  # ai-code-worker
    "srv-d1l4g2be5dus73f7pe6g"  # ai-code-worker-2
    "srv-d1l4g2be5dus73f7pe70"  # ai-memory-worker
    "srv-d1l4g2be5dus73f7pe80"  # ai-quality-worker
    "srv-d1l4gbbe5dus73f7pq30"  # pon-ecosystem
)

SERVICE_NAMES=(
    "ai-code-worker"
    "ai-code-worker-2"
    "ai-memory-worker"
    "ai-quality-worker"
    "pon-ecosystem"
)

# Deploy each failed service
for i in "${!FAILED_SERVICES[@]}"; do
    SERVICE_ID="${FAILED_SERVICES[$i]}"
    SERVICE_NAME="${SERVICE_NAMES[$i]}"
    
    echo "🔧 Triggering manual deploy for: $SERVICE_NAME"
    echo "   Service ID: $SERVICE_ID"
    
    render deploys create --service-id="$SERVICE_ID" --confirm
    
    if [ $? -eq 0 ]; then
        echo "✅ Deploy triggered for $SERVICE_NAME"
    else
        echo "❌ Failed to deploy $SERVICE_NAME"
    fi
    
    echo "---"
done

echo ""
echo "🎉 ALL DEPLOYMENTS TRIGGERED!"
echo "⏱️  Services should be fixed within 5-10 minutes"
echo "🔗 Monitor progress: https://dashboard.render.com/"
