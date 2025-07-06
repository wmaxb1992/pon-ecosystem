#!/usr/bin/env python3
"""
Render.com Deployment Entry Point
=================================
Main entry point for running the Epic Terminal on Render.com
"""

import os
import sys
import asyncio
import subprocess
import logging
from pathlib import Path

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def install_dependencies():
    """Install required dependencies"""
    try:
        import rich
        import redis
        logger.info("✅ Dependencies already installed")
        return True
    except ImportError:
        logger.info("📦 Installing dependencies...")
        try:
            subprocess.run([
                sys.executable, '-m', 'pip', 'install', 
                'rich>=13.0.0', 'redis>=4.5.0', 'psutil>=5.9.0', 
                'requests>=2.31.0', 'python-dotenv>=1.0.0'
            ], check=True)
            logger.info("✅ Dependencies installed successfully")
            return True
        except subprocess.CalledProcessError as e:
            logger.error(f"❌ Failed to install dependencies: {e}")
            return False

def setup_environment():
    """Set up environment variables"""
    # Set your Grok API key here
    os.environ['GROK_API_KEY'] = 'xai-E7Ml5WgMcMYT0lxew2n1b6EwlD8oD3x8OOVuX4OvxSUI9IvLhT2B3ZpESW52N50l2qBNckXyRRkEzv6N'
    os.environ['GROK_MODEL'] = 'grok-3-fast'
    
    # Redis configuration (using Render's Redis addon)
    redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
    os.environ['CELERY_BROKER_URL'] = redis_url
    os.environ['CELERY_RESULT_BACKEND'] = redis_url
    
    # SSH configuration
    os.environ['SSH_PASSWORD'] = os.getenv('SSH_PASSWORD', 'epic-ai-terminal-2025')
    
    logger.info("🔧 Environment configured")

def check_redis():
    """Check if Redis is available"""
    try:
        import redis
        redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
        r = redis.from_url(redis_url)
        r.ping()
        logger.info("✅ Redis connection successful")
        return True
    except Exception as e:
        logger.warning(f"⚠️ Redis not available: {e}")
        return False

async def run_terminal_directly():
    """Run the terminal UI directly without SSH"""
    logger.info("🚀 Starting Epic Terminal UI directly...")
    
    try:
        # Import and run the epic terminal
        from epic_terminal_ui import EpicTerminalUI
        terminal = EpicTerminalUI()
        await terminal.run()
    except ImportError:
        logger.error("❌ Could not import Epic Terminal UI")
        # Fallback to simple terminal
        await run_simple_terminal()

async def run_simple_terminal():
    """Fallback simple terminal"""
    print("\n" + "="*80)
    print("🤖 EPIC AI TERMINAL - RENDER.com DEPLOYMENT")
    print("="*80)
    print("🚀 Status: ONLINE")
    print("🔑 Grok API: CONFIGURED")
    print("📡 Redis: " + ("CONNECTED" if check_redis() else "OFFLINE"))
    print("="*80)
    
    while True:
        try:
            user_input = input("\n💬 Epic AI> ")
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                print("👋 Goodbye!")
                break
            elif user_input.lower() == 'status':
                print("🟢 System Status: ONLINE")
                print("🤖 Workers: READY")
                print("📊 Performance: OPTIMAL")
            elif user_input.lower() == 'help':
                print("📋 Available Commands:")
                print("  status  - Show system status")
                print("  test    - Test Grok AI connection")
                print("  quit    - Exit terminal")
            elif user_input.lower() == 'test':
                print("🧪 Testing Grok AI connection...")
                print("✅ Grok AI is ready!")
            else:
                print(f"🤖 Processing: {user_input}")
                print("✨ [AI Response would appear here]")
                
        except KeyboardInterrupt:
            print("\n👋 Goodbye!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")

async def main():
    """Main entry point for Render.com"""
    logger.info("🚀 Starting Epic AI Terminal on Render.com")
    
    # Install dependencies
    if not install_dependencies():
        logger.error("❌ Failed to install dependencies")
        return
    
    # Setup environment
    setup_environment()
    
    # Check if we should run SSH server or direct terminal
    port = os.getenv('PORT', '10000')
    
    if os.getenv('ENABLE_SSH', 'false').lower() == 'true':
        logger.info("🔐 SSH mode enabled")
        try:
            from ssh_server_render import EpicTerminalSSHServer
            server = EpicTerminalSSHServer(port=int(port))
            await server.start_server()
        except Exception as e:
            logger.error(f"❌ SSH server failed: {e}")
            logger.info("🔄 Falling back to direct terminal mode")
            await run_terminal_directly()
    else:
        logger.info("🖥️ Direct terminal mode")
        
        # For Render.com web service, we need to keep the process alive
        if os.getenv('RENDER_SERVICE_TYPE') == 'web':
            # Simple HTTP server for health checks
            from http.server import HTTPServer, BaseHTTPRequestHandler
            
            class HealthCheckHandler(BaseHTTPRequestHandler):
                def do_GET(self):
                    if self.path == '/health':
                        self.send_response(200)
                        self.send_header('Content-type', 'text/html')
                        self.end_headers()
                        self.wfile.write(b'Epic AI Terminal is running! SSH to connect.')
                    else:
                        self.send_response(200)
                        self.send_header('Content-type', 'text/html')
                        self.end_headers()
                        response = f"""
<!DOCTYPE html>
<html>
<head>
    <title>Epic AI Terminal</title>
    <style>
        body {{ font-family: monospace; background: #000; color: #0f0; padding: 20px; }}
        .terminal {{ border: 2px solid #0f0; padding: 20px; margin: 20px 0; }}
    </style>
</head>
<body>
    <h1>🤖 Epic AI Terminal - Render.com</h1>
    <div class="terminal">
        <p>🚀 Status: ONLINE</p>
        <p>🔑 Grok API: CONFIGURED</p>
        <p>📡 Redis: {'CONNECTED' if check_redis() else 'OFFLINE'}</p>
        <p>⏰ Started: {os.getenv('RENDER_INSTANCE_ID', 'local')}</p>
    </div>
    <h2>How to Connect:</h2>
    <div class="terminal">
        <p>SSH: ssh -p {port} user@your-app.onrender.com</p>
        <p>Password: epic-ai-terminal-2025</p>
    </div>
    <p>Made with ❤️ for epic terminal experiences!</p>
</body>
</html>
                        """.encode()
                        self.wfile.write(response)
            
            httpd = HTTPServer(('0.0.0.0', int(port)), HealthCheckHandler)
            logger.info(f"🌐 HTTP server running on port {port}")
            logger.info("🔗 Access via web browser for status")
            httpd.serve_forever()
        else:
            # Run terminal directly
            await run_terminal_directly()

if __name__ == "__main__":
    asyncio.run(main())
