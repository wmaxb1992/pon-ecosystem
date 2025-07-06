#!/usr/bin/env python3
"""
Enhanced SSH Server for Render.com Deployment
=============================================
Provides comprehensive SSH access to the Epic Terminal system on Render.com
"""

import asyncio
import os
import sys
import subprocess
import signal
import time
import logging
import shutil
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EpicTerminalSSHServer:
    """Enhanced SSH server that provides access to the complete Epic Terminal system"""
    
    def __init__(self, host='0.0.0.0', port=2222):
        self.host = host
        self.port = int(os.getenv('SSH_PORT', port))
        self.password = os.getenv('SSH_PASSWORD', 'epic-ai-terminal-2025')
        self.running_sessions = {}
        
    def check_password(self, username, password):
        """Authenticate SSH connections"""
        return password == self.password
    
    async def handle_client(self, process):
        """Handle SSH client connection with full terminal access"""
        client_info = process.get_extra_info('peername')
        session_id = f"{client_info[0]}:{client_info[1]}:{int(time.time())}"
        
        logger.info(f"🔐 SSH client connected: {session_id}")
        
        try:
            # Send welcome message
            await self.send_welcome(process)
            
            # Show main menu
            await self.show_main_menu(process)
            
            # Start interactive loop
            await self.interactive_loop(process, session_id)
            
        except Exception as e:
            logger.error(f"❌ Error in SSH session {session_id}: {e}")
            await process.stdout.write(f"\n❌ Session error: {e}\n")
        finally:
            if session_id in self.running_sessions:
                del self.running_sessions[session_id]
            logger.info(f"🔚 SSH session ended: {session_id}")
    
    async def send_welcome(self, process):
        """Send welcome screen"""
        welcome = """
\033[2J\033[H\033[1;36m
╔══════════════════════════════════════════════════════════════════════════════╗
║                    🚀 EPIC AI TERMINAL - RENDER.COM 🚀                      ║
║                        Live AI System via SSH Access                        ║
╚══════════════════════════════════════════════════════════════════════════════╝
\033[0m

\033[1;32m✅ Connected to Render.com deployment\033[0m
\033[1;33m🤖 Grok AI integration ready\033[0m
\033[1;35m🔥 Multi-worker system available\033[0m
\033[1;34m📊 Epic Terminal UI loaded\033[0m

"""
        await process.stdout.write(welcome)
    
    async def show_main_menu(self, process):
        """Display main menu options"""
        menu = """
\033[1;37m═══════════════════════════════════════════════════════════════════════════════
                                MAIN MENU
═══════════════════════════════════════════════════════════════════════════════\033[0m

\033[1;36m1. 🎨 Epic Terminal UI\033[0m          - Full Rich-based interface
\033[1;36m2. 🤖 Live AI Terminal\033[0m         - Core AI interaction system  
\033[1;36m3. 👥 Multi-Worker Terminal\033[0m    - Distributed AI workers
\033[1;36m4. 📊 System Status\033[0m           - Check all services
\033[1;36m5. 🔧 System Diagnostics\033[0m      - Debug information
\033[1;36m6. 📚 Documentation\033[0m           - View system docs
\033[1;36m7. 🐚 Shell Access\033[0m            - Direct bash shell
\033[1;36m8. 🔄 Restart Services\033[0m        - Restart AI workers
\033[1;36m9. 📝 View Logs\033[0m               - System log files
\033[1;31mq. 🚪 Quit\033[0m                   - Exit SSH session

\033[1;33mEnter your choice (1-9 or q): \033[0m"""
        
        await process.stdout.write(menu)
    
    async def interactive_loop(self, process, session_id):
        """Main interactive loop"""
        self.running_sessions[session_id] = {'process': process, 'active': True}
        
        while self.running_sessions.get(session_id, {}).get('active', False):
            try:
                # Get user input
                choice = await process.stdin.readline()
                choice = choice.strip().lower()
                
                if choice == 'q' or choice == 'quit':
                    await process.stdout.write("\n👋 Goodbye! Closing SSH session...\n")
                    break
                elif choice == '1':
                    await self.launch_epic_terminal(process)
                elif choice == '2':
                    await self.launch_live_ai_terminal(process)
                elif choice == '3':
                    await self.launch_multi_worker_terminal(process)
                elif choice == '4':
                    await self.show_system_status(process)
                elif choice == '5':
                    await self.show_diagnostics(process)
                elif choice == '6':
                    await self.show_documentation(process)
                elif choice == '7':
                    await self.launch_shell(process)
                elif choice == '8':
                    await self.restart_services(process)
                elif choice == '9':
                    await self.view_logs(process)
                else:
                    await process.stdout.write(f"\n❌ Invalid choice: {choice}")
                
                # Show menu again
                await process.stdout.write("\n\nPress Enter to continue...")
                await process.stdin.readline()
                await self.show_main_menu(process)
                
            except Exception as e:
                logger.error(f"Error in interactive loop: {e}")
                await process.stdout.write(f"\n❌ Error: {e}\n")
                break
    
    async def launch_epic_terminal(self, process):
        """Launch the Epic Terminal UI"""
        await process.stdout.write("\n🎨 Launching Epic Terminal UI...\n")
        try:
            # Try to import and run Epic Terminal
            from epic_terminal_ui import EpicTerminalUI
            terminal = EpicTerminalUI()
            await terminal.run()
        except ImportError as e:
            await process.stdout.write(f"❌ Could not import Epic Terminal UI: {e}\n")
            await process.stdout.write("📝 Running fallback terminal...\n")
            await self.run_fallback_terminal(process)
        except Exception as e:
            await process.stdout.write(f"❌ Error running Epic Terminal: {e}\n")
    
    async def launch_live_ai_terminal(self, process):
        """Launch the Live AI Terminal"""
        await process.stdout.write("\n🤖 Launching Live AI Terminal...\n")
        try:
            from live_ai_terminal import LiveAITerminal
            terminal = LiveAITerminal()
            await terminal.run()
        except ImportError as e:
            await process.stdout.write(f"❌ Could not import Live AI Terminal: {e}\n")
        except Exception as e:
            await process.stdout.write(f"❌ Error running Live AI Terminal: {e}\n")
    
    async def launch_multi_worker_terminal(self, process):
        """Launch the Multi-Worker Terminal"""
        await process.stdout.write("\n👥 Launching Multi-Worker Terminal...\n")
        try:
            from multi_worker_terminal import MultiWorkerTerminal
            terminal = MultiWorkerTerminal()
            await terminal.run()
        except ImportError as e:
            await process.stdout.write(f"❌ Could not import Multi-Worker Terminal: {e}\n")
        except Exception as e:
            await process.stdout.write(f"❌ Error running Multi-Worker Terminal: {e}\n")
    
    async def show_system_status(self, process):
        """Show system status"""
        await process.stdout.write("\n📊 SYSTEM STATUS\n")
        await process.stdout.write("="*50 + "\n")
        
        # Check Python
        await process.stdout.write(f"🐍 Python: {sys.version.split()[0]}\n")
        
        # Check Redis
        try:
            import redis
            redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379')
            r = redis.from_url(redis_url)
            r.ping()
            await process.stdout.write("✅ Redis: Connected\n")
        except Exception as e:
            await process.stdout.write(f"❌ Redis: {e}\n")
        
        # Check Grok API
        grok_key = os.getenv('GROK_API_KEY', 'Not set')
        if grok_key and grok_key != 'Not set':
            await process.stdout.write("✅ Grok API: Key configured\n")
        else:
            await process.stdout.write("❌ Grok API: No key found\n")
        
        # Check disk space
        total, used, free = shutil.disk_usage("/")
        await process.stdout.write(f"💾 Disk: {free // (1024**3)}GB free / {total // (1024**3)}GB total\n")
        
        # Check memory
        try:
            import psutil
            memory = psutil.virtual_memory()
            await process.stdout.write(f"🧠 Memory: {memory.available // (1024**2)}MB available / {memory.total // (1024**2)}MB total\n")
        except ImportError:
            await process.stdout.write("🧠 Memory: psutil not available\n")
    
    async def show_diagnostics(self, process):
        """Show system diagnostics"""
        await process.stdout.write("\n🔧 SYSTEM DIAGNOSTICS\n")
        await process.stdout.write("="*50 + "\n")
        
        # Environment variables
        important_vars = ['GROK_API_KEY', 'REDIS_URL', 'SSH_PASSWORD', 'PORT']
        for var in important_vars:
            value = os.getenv(var, 'Not set')
            if var == 'GROK_API_KEY' and value != 'Not set':
                value = f"{value[:10]}...{value[-10:]}"  # Mask API key
            await process.stdout.write(f"🔑 {var}: {value}\n")
        
        # Process information
        await process.stdout.write(f"🔢 Process ID: {os.getpid()}\n")
        await process.stdout.write(f"📁 Working Dir: {os.getcwd()}\n")
        
        # Python modules
        modules = ['rich', 'redis', 'celery', 'asyncssh', 'psutil']
        await process.stdout.write("\n📦 Module Status:\n")
        for module in modules:
            try:
                __import__(module)
                await process.stdout.write(f"✅ {module}: Available\n")
            except ImportError:
                await process.stdout.write(f"❌ {module}: Not available\n")
    
    async def show_documentation(self, process):
        """Show documentation"""
        await process.stdout.write("\n📚 EPIC AI TERMINAL DOCUMENTATION\n")
        await process.stdout.write("="*50 + "\n")
        
        docs = """
🚀 EPIC AI TERMINAL SYSTEM
==========================

The Epic AI Terminal is a comprehensive AI-powered development environment
that runs on Render.com with full SSH access.

🎯 KEY FEATURES:
- Rich-based Epic Terminal UI with advanced graphics
- Live AI integration with Grok AI
- Multi-worker distributed processing system
- Real-time code editing and error fixing
- Log monitoring and self-improvement
- SSH access for remote development

🔧 SYSTEM COMPONENTS:
1. Epic Terminal UI (epic_terminal_ui.py)
   - Advanced Rich-based interface
   - Interactive menus and dashboards
   - Real-time AI chat

2. Live AI Terminal (live_ai_terminal.py)
   - Core AI interaction system
   - Automatic error detection/fixing
   - Self-improvement engine

3. Multi-Worker System (ai_multi_worker.py)
   - Distributed Celery workers
   - Code generation worker
   - Quality/linting worker
   - Memory/indexing worker

🌐 RENDER.COM DEPLOYMENT:
- Web service for HTTP access
- Background workers for AI processing
- Redis for task queuing
- SSH server for terminal access

📞 SUPPORT:
- GitHub: Check repository for latest updates
- Logs: Use option 9 to view system logs
- Status: Use option 4 for system health

"""
        await process.stdout.write(docs)
    
    async def launch_shell(self, process):
        """Launch bash shell"""
        await process.stdout.write("\n🐚 Launching shell access...\n")
        await process.stdout.write("Type 'exit' to return to main menu.\n\n")
        
        try:
            # Simple shell emulation
            while True:
                await process.stdout.write("epic-terminal$ ")
                command = await process.stdin.readline()
                command = command.strip()
                
                if command == 'exit':
                    break
                elif command == '':
                    continue
                else:
                    try:
                        result = subprocess.run(command, shell=True, capture_output=True, text=True, timeout=30)
                        if result.stdout:
                            await process.stdout.write(result.stdout)
                        if result.stderr:
                            await process.stdout.write(result.stderr)
                    except subprocess.TimeoutExpired:
                        await process.stdout.write("❌ Command timed out (30s limit)\n")
                    except Exception as e:
                        await process.stdout.write(f"❌ Error: {e}\n")
        except Exception as e:
            await process.stdout.write(f"❌ Shell error: {e}\n")
    
    async def restart_services(self, process):
        """Restart services"""
        await process.stdout.write("\n🔄 Restarting services...\n")
        await process.stdout.write("Note: This is a simulation in the SSH environment.\n")
        await process.stdout.write("On Render.com, services restart automatically on deployment.\n")
    
    async def view_logs(self, process):
        """View system logs"""
        await process.stdout.write("\n📝 SYSTEM LOGS\n")
        await process.stdout.write("="*50 + "\n")
        
        log_files = ['/tmp/epic_terminal.log', 'logs/ai_workflow.log', 'logs/backend.log']
        
        for log_file in log_files:
            if os.path.exists(log_file):
                await process.stdout.write(f"\n📄 {log_file}:\n")
                try:
                    with open(log_file, 'r') as f:
                        lines = f.readlines()
                        # Show last 10 lines
                        for line in lines[-10:]:
                            await process.stdout.write(line)
                except Exception as e:
                    await process.stdout.write(f"❌ Error reading {log_file}: {e}\n")
            else:
                await process.stdout.write(f"📄 {log_file}: Not found\n")
    
    async def run_fallback_terminal(self, process):
        """Fallback terminal if Epic UI fails"""
        await process.stdout.write("\n🤖 FALLBACK AI TERMINAL\n")
        await process.stdout.write("="*50 + "\n")
        
        while True:
            await process.stdout.write("\nAI> ")
            user_input = await process.stdin.readline()
            user_input = user_input.strip()
            
            if user_input.lower() in ['quit', 'exit', 'q']:
                break
            elif user_input.lower() == 'status':
                await self.show_system_status(process)
            else:
                await process.stdout.write(f"You said: {user_input}\n")
                await process.stdout.write("(AI response would go here with Grok integration)\n")

async def main():
    """Main SSH server function"""
    logger.info("🚀 Starting Epic Terminal SSH Server...")
    
    try:
        # Try to import asyncssh (if not available, use fallback)
        try:
            import asyncssh
            use_asyncssh = True
        except ImportError:
            logger.warning("⚠️ asyncssh not available, using fallback mode")
            use_asyncssh = False
        
        # Create SSH server
        server = EpicTerminalSSHServer()
        
        if use_asyncssh:
            # Start SSH server with asyncssh
            async with asyncssh.listen(
                server.host, 
                server.port,
                server_host_keys=['/tmp/ssh_host_key'],
                password_auth=True,
                password_auth_func=server.check_password,
                process_factory=server.handle_client
            ) as ssh_server:
                logger.info(f"🔐 SSH server listening on {server.host}:{server.port}")
                logger.info(f"🔑 SSH password: {server.password}")
                await ssh_server.wait_closed()
        else:
            # Fallback mode - just run the terminal directly
            logger.info("🔄 Running in fallback mode (direct terminal)")
            
            # Create a mock process for direct terminal access
            class MockProcess:
                def __init__(self):
                    self.stdin = sys.stdin
                    self.stdout = sys.stdout
                    self.stderr = sys.stderr
                
                def get_extra_info(self, key):
                    return ('local', 0)
            
            mock_process = MockProcess()
            await server.handle_client(mock_process)
            
    except ImportError as e:
        logger.error(f"❌ Missing required module: {e}")
        logger.info("📦 Install with: pip install asyncssh rich")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Failed to start SSH server: {e}")
        sys.exit(1)

if __name__ == "__main__":
    # Generate SSH host key if needed and asyncssh is available
    key_path = '/tmp/ssh_host_key'
    if not os.path.exists(key_path):
        logger.info("🔐 Generating SSH host key...")
        try:
            subprocess.run(['ssh-keygen', '-t', 'rsa', '-b', '2048', '-f', key_path, '-N', '', '-q'], check=True)
            logger.info("✅ SSH host key generated")
        except (subprocess.CalledProcessError, FileNotFoundError):
            logger.warning("⚠️ Could not generate SSH host key, continuing without SSH")
    
    # Run the SSH server
    asyncio.run(main())
