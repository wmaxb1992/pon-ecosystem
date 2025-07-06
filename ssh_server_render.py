#!/usr/bin/env python3
"""
SSH Server for Render.com Deployment
====================================
Provides SSH access to the Epic Terminal UI on Render.com
"""

import asyncio
import asyncssh
import os
import sys
import subprocess
import signal
import pty
from pathlib import Path
import logging
import json
import time

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class EpicTerminalSSHServer:
    """SSH server that provides access to the Epic Terminal UI"""
    
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
            terminal_script = Path(__file__).parent / "epic_terminal_ui.py"
            
            # Run the terminal UI
            proc = await asyncio.create_subprocess_exec(
                python_executable, str(terminal_script),
                stdin=process.stdin,
                stdout=process.stdout,
                stderr=process.stderr
            )
            
            await proc.wait()
            
        except Exception as e:
            logger.error(f"Error running terminal UI: {e}")
            process.stdout.write(f"❌ Error: {e}\n")
        finally:
            logger.info("SSH client disconnected")
    
    def get_authorized_keys(self):
        """Get authorized SSH keys from environment"""
        # You can set SSH_AUTHORIZED_KEYS in Render.com environment variables
        auth_keys = os.getenv('SSH_AUTHORIZED_KEYS', '')
        if auth_keys:
            return auth_keys.split('\n')
        
        # Default: allow password authentication for demo
        return []
    
    async def auth_password(self, username, password):
        """Simple password authentication"""
        # Set SSH_PASSWORD in Render.com environment variables
        expected_password = os.getenv('SSH_PASSWORD', 'epic-ai-terminal')
        return password == expected_password
    
    async def auth_public_key(self, username, key):
        """Public key authentication"""
        authorized_keys = self.get_authorized_keys()
        key_string = key.export_public_key().decode()
        
        for auth_key in authorized_keys:
            if auth_key.strip() == key_string.strip():
                return True
        return False
    
    async def start_server(self):
        """Start the SSH server"""
        logger.info(f"Starting Epic Terminal SSH server on {self.host}:{self.port}")
        
        try:
            server = await asyncssh.create_server(
                self.handle_client,
                host=self.host,
                port=self.port,
                server_host_keys=[self.ssh_key_path],
                auth_methods=['password', 'publickey'],
                password_auth=self.auth_password,
                public_key_auth=self.auth_public_key,
                process_factory=asyncssh.SSHServerProcess,
            )
            
            logger.info("🚀 Epic Terminal SSH server is running!")
            logger.info(f"📡 Connect with: ssh -p {self.port} user@your-render-app.onrender.com")
            logger.info(f"🔑 Default password: {os.getenv('SSH_PASSWORD', 'epic-ai-terminal')}")
            
            await server.wait_closed()
            
        except Exception as e:
            logger.error(f"Failed to start SSH server: {e}")
            raise

async def main():
    """Main entry point"""
    # Install dependencies if needed
    try:
        import rich
        import asyncssh
    except ImportError:
        logger.info("Installing required packages...")
        subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 'requirements_render.txt'], check=True)
    
    # Start SSH server
    server = EpicTerminalSSHServer()
    await server.start_server()

if __name__ == "__main__":
    asyncio.run(main())
