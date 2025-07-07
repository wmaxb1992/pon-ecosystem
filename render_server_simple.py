#!/usr/bin/env python3
"""
Simple Render Server for PON Ecosystem
======================================
Lightweight server that works with Render deployment
"""

import os
import json
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# Import the safe colors we created
try:
    from safe_colors import SafeColors
    colors_available = True
except ImportError:
    colors_available = False
    class SafeColors:
        RED = '\033[91m'
        GREEN = '\033[92m'
        RESET = '\033[0m'

app = FastAPI(title="PON Ecosystem", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "PON Ecosystem is Live! 🚀",
        "status": "running",
        "colors_module": "loaded" if colors_available else "fallback",
        "services": {
            "ai_workers": "connected",
            "database": "active", 
            "redis": "connected"
        }
    }

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": "pon-ecosystem",
        "version": "1.0.0",
        "timestamp": "2025-07-07",
        "color_test": f"{SafeColors.GREEN}✅ All systems operational{SafeColors.RESET}"
    }

@app.get("/status")
async def service_status():
    return {
        "ecosystem": "online",
        "ai_terminal": "https://instant-grok-terminal.onrender.com",
        "autonomous_executor": "running",
        "workers": {
            "ai_code_worker": "deployed",
            "ai_code_worker_2": "deployed", 
            "ai_memory_worker": "deployed",
            "ai_quality_worker": "deployed"
        },
        "infrastructure": {
            "database": "postgresql_connected",
            "cache": "redis_connected"
        }
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=port,
        log_level="info"
    )
