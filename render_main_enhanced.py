#!/usr/bin/env python3
"""
Enhanced Render.com Deployment Entry Point
==========================================
Comprehensive entry point for the Epic Terminal system on Render.com
Supports web access, SSH access, and direct terminal modes
"""

import os
import sys
import asyncio
import subprocess
import logging
import threading
import time
from pathlib import Path

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EpicTerminalRenderService:
    """Main service class for Render.com deployment"""
    
    def __init__(self):
        self.setup_environment()
        self.install_dependencies()
        
    def setup_environment(self):
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
        os.environ['SSH_PORT'] = os.getenv('SSH_PORT', '2222')
        
        # Web service configuration
        os.environ['PORT'] = os.getenv('PORT', '8000')
        
        logger.info("🔧 Environment configured")

    def install_dependencies(self):
        """Install required dependencies"""
        try:
            import rich
            import redis
            logger.info("✅ Core dependencies already installed")
            return True
        except ImportError:
            logger.info("📦 Installing core dependencies...")
            try:
                subprocess.run([
                    sys.executable, '-m', 'pip', 'install', 
                    'rich>=13.0.0', 'redis>=4.5.0', 'psutil>=5.9.0', 
                    'requests>=2.31.0', 'python-dotenv>=1.0.0'
                ], check=True)
                logger.info("✅ Core dependencies installed successfully")
                return True
            except subprocess.CalledProcessError as e:
                logger.error(f"❌ Failed to install dependencies: {e}")
                return False

    def check_redis(self):
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

    async def run_web_server(self):
        """Run web server component"""
        logger.info("🌐 Starting web server...")
        
        from http.server import HTTPServer, BaseHTTPRequestHandler
        import json
        
        class EpicTerminalHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path == '/':
                    self.send_response(200)
                    self.send_header('Content-type', 'text/html')
                    self.end_headers()
                    
                    html_content = """
<!DOCTYPE html>
<html>
<head>
    <title>Epic AI Terminal - Render.com</title>
    <style>
        body { 
            font-family: 'Courier New', monospace; 
            background: #0a0a0a; 
            color: #00ff00; 
            margin: 0; 
            padding: 20px; 
        }
        .container { 
            max-width: 800px; 
            margin: 0 auto; 
            background: #111; 
            padding: 20px; 
            border-radius: 10px; 
            border: 1px solid #333; 
        }
        .ascii-art { 
            color: #00ffff; 
            text-align: center; 
            white-space: pre; 
            font-size: 12px; 
        }
        .status { 
            background: #222; 
            padding: 10px; 
            margin: 10px 0; 
            border-left: 4px solid #00ff00; 
        }
        .ssh-info { 
            background: #003300; 
            padding: 15px; 
            margin: 10px 0; 
            border-radius: 5px; 
        }
        .command { 
            background: #111; 
            color: #ffff00; 
            padding: 5px; 
            border-radius: 3px; 
            font-family: monospace; 
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="ascii-art">
╔══════════════════════════════════════════════════════════════════════════════╗
║                    🚀 EPIC AI TERMINAL - RENDER.COM 🚀                      ║
║                        Live AI System via SSH Access                        ║
╚══════════════════════════════════════════════════════════════════════════════╝
        </div>
        
        <div class="status">
            <h2>🎯 System Status</h2>
            <p>✅ Epic Terminal System: ONLINE</p>
            <p>🤖 Grok AI Integration: READY</p>
            <p>🔥 Multi-Worker System: AVAILABLE</p>
            <p>📊 Rich Terminal UI: LOADED</p>
        </div>
        
        <div class="ssh-info">
            <h2>🔐 SSH Access</h2>
            <p>Connect to the full Epic Terminal system via SSH:</p>
            <div class="command">ssh -p 2222 user@[YOUR_RENDER_URL]</div>
            <p><strong>Password:</strong> epic-ai-terminal-2025</p>
            
            <h3>Features Available via SSH:</h3>
            <ul>
                <li>🎨 Epic Terminal UI - Rich-based interface</li>
                <li>🤖 Live AI Terminal - Core AI system</li>
                <li>👥 Multi-Worker Terminal - Distributed processing</li>
                <li>🐚 Shell Access - Direct command line</li>
                <li>📊 System Monitoring - Status & diagnostics</li>
                <li>📝 Log Viewing - Real-time system logs</li>
            </ul>
        </div>
        
        <div class="status">
            <h2>🔧 System Components</h2>
            <p><strong>Epic Terminal UI:</strong> Advanced Rich-based interface with interactive menus</p>
            <p><strong>Live AI Terminal:</strong> Core AI interaction with Grok integration</p>
            <p><strong>Multi-Worker System:</strong> Distributed Celery workers for AI processing</p>
            <p><strong>SSH Server:</strong> Full terminal access via SSH protocol</p>
        </div>
        
        <div class="status">
            <h2>📚 Documentation</h2>
            <p>Access full documentation and usage examples via SSH connection.</p>
            <p>Use menu option 6 after connecting via SSH for complete docs.</p>
        </div>
    </div>
</body>
</html>
                    """
                    self.wfile.write(html_content.encode())
                    
                elif self.path == '/status':
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    
                    status = {
                        'status': 'online',
                        'grok_api': 'configured' if os.getenv('GROK_API_KEY') else 'missing',
                        'redis': 'connected' if self.server.parent.check_redis() else 'offline',
                        'ssh_port': os.getenv('SSH_PORT', '2222'),
                        'components': {
                            'epic_terminal_ui': 'available',
                            'live_ai_terminal': 'available',
                            'multi_worker_system': 'available',
                            'ssh_server': 'running'
                        }
                    }
                    
                    self.wfile.write(json.dumps(status, indent=2).encode())
                    
                else:
                    self.send_response(404)
                    self.end_headers()
                    self.wfile.write(b'Not Found')
            
            def log_message(self, format, *args):
                # Suppress default HTTP server logs
                pass
        
        port = int(os.getenv('PORT', 8000))
        server = HTTPServer(('0.0.0.0', port), EpicTerminalHandler)
        server.parent = self  # Reference to parent for status checks
        
        logger.info(f"🌐 Web server running on port {port}")
        
        # Run server in a separate thread
        def run_server():
            server.serve_forever()
        
        web_thread = threading.Thread(target=run_server, daemon=True)
        web_thread.start()
        
        return web_thread

    async def run_ssh_server(self):
        """Run SSH server component"""
        logger.info("🔐 Starting SSH server...")
        
        try:
            # Try to import the enhanced SSH server
            from ssh_server_render_enhanced import main as ssh_main
            
            # Run SSH server in background
            ssh_task = asyncio.create_task(ssh_main())
            return ssh_task
            
        except ImportError as e:
            logger.warning(f"⚠️ Could not import SSH server: {e}")
            logger.info("🔄 Running direct terminal mode instead")
            
            # Fallback to direct terminal
            await self.run_direct_terminal()

    async def run_direct_terminal(self):
        """Run terminal directly if SSH is not available"""
        logger.info("🚀 Starting Epic Terminal UI directly...")
        
        try:
            # Try Epic Terminal UI first
            from epic_terminal_ui import EpicTerminalUI
            terminal = EpicTerminalUI()
            await terminal.run()
            
        except ImportError:
            logger.warning("⚠️ Epic Terminal UI not available, trying Live AI Terminal...")
            
            try:
                from live_ai_terminal import LiveAITerminal
                terminal = LiveAITerminal()
                await terminal.run()
                
            except ImportError:
                logger.warning("⚠️ Live AI Terminal not available, using fallback...")
                await self.run_fallback_terminal()

    async def run_fallback_terminal(self):
        """Fallback simple terminal"""
        print("\n" + "="*80)
        print("🤖 EPIC AI TERMINAL - RENDER.COM DEPLOYMENT")
        print("="*80)
        print("🚀 Status: ONLINE")
        print("🔑 Grok API: CONFIGURED")
        print("📡 Redis: " + ("CONNECTED" if self.check_redis() else "OFFLINE"))
        print("🌐 Web Server: RUNNING")
        print("="*80)
        
        while True:
            try:
                user_input = input("\n💬 Epic AI> ")
                
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print("👋 Goodbye!")
                    break
                elif user_input.lower() == 'status':
                    print(f"🔧 System Status:")
                    print(f"  - Python: {sys.version.split()[0]}")
                    print(f"  - Redis: {'Connected' if self.check_redis() else 'Offline'}")
                    print(f"  - Grok API: {'Configured' if os.getenv('GROK_API_KEY') else 'Missing'}")
                elif user_input.lower() == 'help':
                    print("Available commands:")
                    print("  status - Show system status")
                    print("  help - Show this help")
                    print("  quit/exit/q - Exit terminal")
                else:
                    print(f"You said: {user_input}")
                    print("(Connect via SSH for full AI integration)")
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except EOFError:
                break

    async def start_background_workers(self):
        """Start Celery workers if Redis is available"""
        if self.check_redis():
            logger.info("🔄 Starting background workers...")
            
            try:
                # Start Celery workers
                worker_process = subprocess.Popen([
                    sys.executable, '-m', 'celery', '-A', 'ai_multi_worker', 
                    'worker', '--loglevel=info', '--concurrency=2'
                ])
                
                logger.info(f"✅ Background workers started (PID: {worker_process.pid})")
                return worker_process
                
            except Exception as e:
                logger.warning(f"⚠️ Could not start background workers: {e}")
                return None
        else:
            logger.info("ℹ️ Redis not available, skipping background workers")
            return None

    async def run_full_system(self):
        """Run the complete Epic Terminal system"""
        logger.info("🚀 Starting Epic Terminal System on Render.com...")
        
        # Start web server
        web_thread = await self.run_web_server()
        
        # Start background workers
        worker_process = await self.start_background_workers()
        
        # Determine the primary mode
        mode = os.getenv('EPIC_MODE', 'auto')
        
        if mode == 'web':
            # Web-only mode
            logger.info("🌐 Running in web-only mode")
            while True:
                await asyncio.sleep(60)  # Keep web server alive
                
        elif mode == 'ssh':
            # SSH mode
            logger.info("🔐 Running in SSH mode")
            await self.run_ssh_server()
            
        elif mode == 'terminal':
            # Direct terminal mode
            logger.info("🖥️ Running in direct terminal mode")
            await self.run_direct_terminal()
            
        else:
            # Auto mode - try SSH first, fallback to web
            logger.info("🔄 Running in auto mode")
            
            try:
                # Try SSH server
                ssh_task = await self.run_ssh_server()
                
                # Keep both web and SSH running
                await asyncio.gather(
                    ssh_task,
                    asyncio.sleep(float('inf'))  # Keep running
                )
                
            except Exception as e:
                logger.warning(f"⚠️ SSH server failed: {e}")
                logger.info("🌐 Falling back to web-only mode")
                
                # Keep web server running
                while True:
                    await asyncio.sleep(60)

async def main():
    """Main entry point"""
    try:
        service = EpicTerminalRenderService()
        await service.run_full_system()
        
    except KeyboardInterrupt:
        logger.info("👋 Shutting down Epic Terminal System...")
    except Exception as e:
        logger.error(f"❌ Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Show startup banner
    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    🚀 EPIC AI TERMINAL - RENDER.COM 🚀                      ║
║                        Starting Live AI System...                           ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """)
    
    # Run the system
    asyncio.run(main())
