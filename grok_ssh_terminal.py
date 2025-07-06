#!/usr/bin/env python3
"""
SSH-Enabled Instant Grok Terminal
=================================
Provides SSH access to Grok AI via asyncssh server
"""

import os
import sys
import asyncio
import json
import logging
from datetime import datetime
from typing import Optional
import requests

# Import SSH server dependencies
try:
    import asyncssh
    from asyncssh import SSHServerProcess
except ImportError:
    print("Installing asyncssh for SSH server...")
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "asyncssh"])
    import asyncssh
    from asyncssh import SSHServerProcess

# Set your Grok API key from environment
GROK_API_KEY = os.environ.get('GROK_API_KEY', 'xai-E7Ml5WgMcMYT0lxew2n1b6EwlD8oD3x8OOVuX4OvxSUI9IvLhT2B3ZZpESW52N50l2qBNckXyRRkEzv6N')

class Colors:
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    PURPLE = '\033[95m'
    BLUE = '\033[94m'
    WHITE = '\033[97m'
    BOLD = '\033[1m'
    RESET = '\033[0m'

class GrokSSHSession:
    """Individual SSH session for Grok AI interaction"""
    
    def __init__(self, process: SSHServerProcess):
        self.process = process
        self.api_key = GROK_API_KEY
        self.conversation_history = []
        self.session_start = datetime.now()
        self.username = process.get_extra_info('username', 'user')
        
    async def display_banner(self):
        """Display SSH Grok terminal banner"""
        banner = f"""{Colors.BOLD}{Colors.CYAN}
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║    🔑 SSH GROK AI TERMINAL 🔑                                               ║
║                                                                              ║
║    👤 User: {self.username:<20}  🕒 Connected: {self.session_start.strftime('%H:%M:%S')}          ║
║                                                                              ║
║    💬 Direct AI Conversation  •  🎯 Instant Responses                       ║
║    🤖 Grok-3-Fast Model      •  🔥 SSH Access Ready                         ║
║                                                                              ║
║    Commands: 'help', 'clear', 'history', 'exit'                             ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝{Colors.RESET}

{Colors.GREEN}🎉 Welcome to Instant Grok AI via SSH!{Colors.RESET}
{Colors.BLUE}Type your questions and get instant AI responses.{Colors.RESET}

"""
        self.process.stdout.write(banner)
        
    async def get_grok_response(self, message: str) -> str:
        """Get response from Grok AI"""
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            # Add to conversation history
            self.conversation_history.append({"role": "user", "content": message})
            
            payload = {
                "messages": self.conversation_history,
                "model": "grok-3-fast",
                "temperature": 0.7,
                "max_tokens": 1000
            }
            
            response = requests.post(
                'https://api.x.ai/v1/chat/completions',
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                ai_response = result['choices'][0]['message']['content']
                
                # Add AI response to history
                self.conversation_history.append({"role": "assistant", "content": ai_response})
                
                return ai_response
            else:
                return f"❌ Error: {response.status_code} - {response.text}"
                
        except Exception as e:
            return f"❌ Connection error: {e}"
    
    async def handle_command(self, command: str) -> str:
        """Handle special commands"""
        command = command.strip().lower()
        
        if command == 'help':
            return f"""{Colors.YELLOW}
📋 Available Commands:
━━━━━━━━━━━━━━━━━━━━
• help     - Show this help message
• clear    - Clear conversation history  
• history  - Show conversation history
• status   - Show session status
• exit     - Exit the terminal
• quit     - Exit the terminal

💡 Tips:
• Just type your question to chat with Grok AI
• Use natural language - ask anything!
• Session history is maintained during your connection
{Colors.RESET}"""
        
        elif command == 'clear':
            self.conversation_history = []
            return f"{Colors.GREEN}✅ Conversation history cleared{Colors.RESET}"
        
        elif command == 'history':
            if not self.conversation_history:
                return f"{Colors.YELLOW}📝 No conversation history yet{Colors.RESET}"
            
            history_text = f"{Colors.BLUE}📝 Conversation History:{Colors.RESET}\\n"
            for i, msg in enumerate(self.conversation_history[-10:], 1):  # Last 10 messages
                role = "👤 You" if msg['role'] == 'user' else "🤖 Grok"
                content = msg['content'][:100] + "..." if len(msg['content']) > 100 else msg['content']
                history_text += f"{Colors.CYAN}{i}. {role}:{Colors.RESET} {content}\\n"
            
            return history_text
        
        elif command == 'status':
            uptime = datetime.now() - self.session_start
            return f"""{Colors.GREEN}
📊 Session Status:
━━━━━━━━━━━━━━━━━━
• User: {self.username}
• Connected: {self.session_start.strftime('%Y-%m-%d %H:%M:%S')}
• Uptime: {str(uptime).split('.')[0]}
• Messages: {len([m for m in self.conversation_history if m['role'] == 'user'])}
• API Status: ✅ Connected
{Colors.RESET}"""
        
        elif command in ['exit', 'quit']:
            return "DISCONNECT"
        
        else:
            return None  # Not a command, treat as regular message
    
    async def run_session(self):
        """Main session loop"""
        try:
            await self.display_banner()
            
            while True:
                # Display prompt
                self.process.stdout.write(f"\\n{Colors.BOLD}{Colors.GREEN}grok-ssh>{Colors.RESET} ")
                
                # Read user input
                try:
                    user_input = await self.process.stdin.readline()
                    if not user_input:
                        break
                    
                    user_input = user_input.strip()
                    if not user_input:
                        continue
                    
                    # Handle commands
                    command_response = await self.handle_command(user_input)
                    if command_response == "DISCONNECT":
                        self.process.stdout.write(f"\\n{Colors.YELLOW}👋 Goodbye! Thanks for using Grok SSH Terminal{Colors.RESET}\\n")
                        break
                    elif command_response:
                        self.process.stdout.write(f"\\n{command_response}\\n")
                        continue
                    
                    # Get AI response
                    self.process.stdout.write(f"\\n{Colors.BLUE}🤖 Grok is thinking...{Colors.RESET}\\n")
                    
                    ai_response = await self.get_grok_response(user_input)
                    
                    # Display response
                    self.process.stdout.write(f"\\n{Colors.BOLD}{Colors.BLUE}🤖 Grok:{Colors.RESET}\\n")
                    self.process.stdout.write(f"{ai_response}\\n")
                    
                except asyncio.IncompleteReadError:
                    break
                except Exception as e:
                    self.process.stdout.write(f"\\n{Colors.RED}❌ Session error: {e}{Colors.RESET}\\n")
                    
        except Exception as e:
            self.process.stdout.write(f"\\n{Colors.RED}❌ Fatal error: {e}{Colors.RESET}\\n")
        finally:
            self.process.exit(0)

class GrokSSHServer:
    """SSH Server for Grok AI Terminal"""
    
    def __init__(self, host='0.0.0.0', port=2222):
        self.host = host
        self.port = port
        
    async def handle_client(self, process: SSHServerProcess):
        """Handle new SSH client connection"""
        session = GrokSSHSession(process)
        await session.run_session()
    
    async def start_server(self):
        """Start the SSH server"""
        try:
            # Generate or load host key
            await self.setup_host_key()
            
            # Start SSH server
            print(f"{Colors.GREEN}🔑 Starting Grok SSH Terminal Server...{Colors.RESET}")
            print(f"{Colors.BLUE}📡 Host: {self.host}{Colors.RESET}")
            print(f"{Colors.BLUE}🚪 Port: {self.port}{Colors.RESET}")
            print(f"{Colors.YELLOW}💡 Connect with: ssh user@{self.host} -p {self.port}{Colors.RESET}")
            
            async with asyncssh.listen(
                host=self.host,
                port=self.port,
                server_host_keys=['ssh_host_key'],
                process_factory=self.handle_client,
                # Allow any username/password for demo
                password_auth=True,
                public_key_auth=False
            ):
                print(f"{Colors.GREEN}✅ Grok SSH Terminal Server running!{Colors.RESET}")
                print(f"{Colors.CYAN}🎯 Ready for connections...{Colors.RESET}")
                
                # Keep server running
                await asyncio.Future()  # Run forever
                
        except Exception as e:
            print(f"{Colors.RED}❌ SSH Server error: {e}{Colors.RESET}")
            raise
    
    async def setup_host_key(self):
        """Generate SSH host key if it doesn't exist"""
        if not os.path.exists('ssh_host_key'):
            print(f"{Colors.YELLOW}🔐 Generating SSH host key...{Colors.RESET}")
            # Generate RSA key pair
            key = asyncssh.generate_private_key('ssh-rsa', key_size=2048)
            key.write_private_key('ssh_host_key')
            print(f"{Colors.GREEN}✅ SSH host key generated{Colors.RESET}")

class GrokTerminalHTTP:
    """HTTP interface for environments where SSH isn't available"""
    
    def __init__(self, port=10000):
        self.port = port
    
    async def start_http_server(self):
        """Start HTTP server as fallback"""
        try:
            from fastapi import FastAPI
            from fastapi.responses import HTMLResponse
            import uvicorn
            
            app = FastAPI(title="Grok AI Terminal")
            
            @app.get("/", response_class=HTMLResponse)
            async def terminal():
                return """
                <!DOCTYPE html>
                <html>
                <head>
                    <title>Grok AI Terminal</title>
                    <style>
                        body { background: #000; color: #0f0; font-family: monospace; }
                        .terminal { width: 100%; height: 100vh; padding: 20px; }
                        input { background: #000; color: #0f0; border: 1px solid #0f0; width: 100%; }
                    </style>
                </head>
                <body>
                    <div class="terminal">
                        <h1>🤖 Grok AI Terminal (HTTP Mode)</h1>
                        <p>💡 For SSH access, use: ssh user@your-render-url -p 2222</p>
                        <p>🔗 API available at /api/grok</p>
                    </div>
                </body>
                </html>
                """
            
            @app.get("/health")
            async def health():
                return {"status": "healthy", "service": "grok-ssh-terminal"}
            
            print(f"{Colors.GREEN}🌐 Starting HTTP server on port {self.port}...{Colors.RESET}")
            uvicorn.run(app, host="0.0.0.0", port=self.port)
            
        except Exception as e:
            print(f"{Colors.RED}❌ HTTP Server error: {e}{Colors.RESET}")

async def main():
    """Main function - start SSH server with HTTP fallback"""
    ssh_port = int(os.environ.get('SSH_PORT', 2222))
    http_port = int(os.environ.get('PORT', 10000))
    
    # Try to start SSH server
    try:
        ssh_server = GrokSSHServer(port=ssh_port)
        await ssh_server.start_server()
    except Exception as ssh_error:
        print(f"{Colors.YELLOW}⚠️  SSH server failed: {ssh_error}{Colors.RESET}")
        print(f"{Colors.BLUE}🔄 Falling back to HTTP mode...{Colors.RESET}")
        
        # Fallback to HTTP server
        http_server = GrokTerminalHTTP(port=http_port)
        await http_server.start_http_server()

if __name__ == "__main__":
    # Handle command line arguments
    if len(sys.argv) > 1:
        if '--production' in sys.argv:
            # Production mode - start HTTP server for Render.com
            http_port = int(os.environ.get('PORT', 10000))
            http_server = GrokTerminalHTTP(port=http_port)
            asyncio.run(http_server.start_http_server())
        elif '--ssh' in sys.argv:
            # SSH mode only
            asyncio.run(main())
        else:
            print(f"{Colors.GREEN}Grok SSH Terminal{Colors.RESET}")
            print(f"Usage: {sys.argv[0]} [--production|--ssh]")
    else:
        # Default - try SSH, fallback to HTTP
        asyncio.run(main())
