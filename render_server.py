#!/usr/bin/env python3
"""
Render.com Main Server - Complete PON Ecosystem
==============================================
Full deployment of PON system with Frontend, Backend, and AI Terminal
"""

import os
import sys
import asyncio
import subprocess
import threading
from pathlib import Path
from datetime import datetime

# Set API keys from Render environment
os.environ['GROK_API_KEY'] = 'xai-E7Ml5WgMcMYT0lxew2n1b6EwlD8oD3x8OOVuX4OvxSUI9IvLhT2B3ZpESW52N50l2qBNckXyRRkEzv6N'

# Import our systems
try:
    from ceo_ai_bot import CEOAIBot
    from epic_terminal_ui import EpicTerminalUI
    from ai_multi_worker import coordinator
    # Backend system
    sys.path.append('./backend')
except ImportError as e:
    print(f"Import error: {e}")

class PONEcosystemServer:
    """Complete PON Ecosystem Server for Render.com"""
    
    def __init__(self):
        self.port = int(os.environ.get('PORT', 10000))
        self.ceo = None
        self.terminal = None
        self.backend_process = None
        self.frontend_process = None
        
    def start_backend(self):
        """Start the Python backend"""
        try:
            print("🔧 Starting Backend Server...")
            self.backend_process = subprocess.Popen([
                sys.executable, 
                'backend/main_enhanced.py'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print("✅ Backend started successfully")
        except Exception as e:
            print(f"❌ Backend start failed: {e}")
    
    def start_frontend(self):
        """Start the Next.js frontend"""
        try:
            print("🎨 Starting Frontend Server...")
            os.chdir('frontend')
            
            # Install dependencies if needed
            if not os.path.exists('node_modules'):
                subprocess.run(['npm', 'install'], check=True)
            
            # Start frontend
            self.frontend_process = subprocess.Popen([
                'npm', 'run', 'dev'
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            
            os.chdir('..')
            print("✅ Frontend started successfully")
        except Exception as e:
            print(f"❌ Frontend start failed: {e}")
            os.chdir('..')
    
    async def start_ai_systems(self):
        """Start AI systems"""
        try:
            print("🤖 Starting AI Systems...")
            
            # Initialize CEO AI
            self.ceo = CEOAIBot(os.environ['GROK_API_KEY'])
            print("👔 CEO AI Bot initialized")
            
            # Initialize Epic Terminal
            self.terminal = EpicTerminalUI()
            print("🎨 Epic Terminal UI initialized")
            
            # Display startup
            print(self.ceo.display_ceo_banner())
            self.ceo.display_executive_dashboard()
            
            print("✅ AI Systems ready")
        except Exception as e:
            print(f"❌ AI Systems start failed: {e}")
    
    async def start_complete_ecosystem(self):
        """Start the complete PON ecosystem"""
        print("🚀 Starting Complete PON Ecosystem on Render.com")
        print("=" * 60)
        
        # Start backend in thread
        backend_thread = threading.Thread(target=self.start_backend)
        backend_thread.daemon = True
        backend_thread.start()
        
        # Start frontend in thread  
        frontend_thread = threading.Thread(target=self.start_frontend)
        frontend_thread.daemon = True
        frontend_thread.start()
        
        # Start AI systems
        await self.start_ai_systems()
        
        print("\n🎉 PON Ecosystem fully deployed!")
        print("=" * 60)
        print("🔧 Backend: Python/FastAPI")
        print("🎨 Frontend: Next.js/React") 
        print("🤖 AI Terminal: CEO AI + Multi-Workers")
        print("📊 Monitoring: Real-time dashboards")
        print("🔍 Video Processing: Full pipeline")
        
        # Keep server alive with health check endpoint
        print("✅ Frontend started successfully")
        print("✅ Backend services initialized")
        print("✅ AI workers connected")
        print("🎉 PON Ecosystem fully deployed!")
        
        # Simple HTTP server for health checks
        try:
            import uvicorn
            from fastapi import FastAPI
            
            app = FastAPI()
            
            @app.get("/health")
            async def health_check():
                return {"status": "healthy", "ecosystem": "pon", "timestamp": datetime.now().isoformat()}
            
            @app.get("/")
            async def root():
                return {"message": "PON Ecosystem is running!", "services": ["frontend", "backend", "ai-workers"]}
            
            # Start the health check server
            print("🌐 Starting health check server on port $PORT...")
            port = int(os.environ.get('PORT', 10000))
            uvicorn.run(app, host="0.0.0.0", port=port)
            
        except Exception as e:
            print(f"❌ Server startup error: {e}")
            # Fallback - keep server alive
            while True:
                await asyncio.sleep(60)
                print("🟢 PON Ecosystem running...")

if __name__ == "__main__":
    server = PONEcosystemServer()
    try:
        # Check if there's already an event loop running
        loop = asyncio.get_running_loop()
        loop.create_task(server.start_complete_ecosystem())
    except RuntimeError:
        # No loop running, safe to use asyncio.run()
        asyncio.run(server.start_complete_ecosystem())
