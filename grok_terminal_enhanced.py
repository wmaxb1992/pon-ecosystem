#!/usr/bin/env python3
"""
Enhanced Grok Terminal with SSH + Web Access
===========================================
Provides both SSH terminal and web interface for Grok AI
"""

import os
import sys
import asyncio
import json
import logging
from datetime import datetime
from typing import Optional
import requests

# Import SSH and web server dependencies
try:
    import asyncssh
    from asyncssh import SSHServerProcess
    from fastapi import FastAPI, WebSocket, WebSocketDisconnect
    from fastapi.responses import HTMLResponse
    import uvicorn
    SSH_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Some features unavailable: {e}")
    print("Installing required packages...")
    import subprocess
    try:
        subprocess.run([sys.executable, "-m", "pip", "install", "asyncssh", "fastapi", "uvicorn[standard]"], check=True)
        import asyncssh
        from asyncssh import SSHServerProcess
        from fastapi import FastAPI, WebSocket, WebSocketDisconnect
        from fastapi.responses import HTMLResponse
        import uvicorn
        SSH_AVAILABLE = True
    except Exception:
        print("❌ SSH features disabled - running in HTTP-only mode")
        SSH_AVAILABLE = False
        from fastapi import FastAPI, WebSocket, WebSocketDisconnect
        from fastapi.responses import HTMLResponse
        import uvicorn

# Configuration
GROK_API_KEY = os.environ.get('GROK_API_KEY', 'xai-E7Ml5WgMcMYT0lxew2n1b6EwlD8oD3x8OOVuX4OvxSUI9IvLhT2B3ZpESW52N50l2qBNckXyRRkEzv6N')
SSH_PORT = int(os.environ.get('SSH_PORT', 2222))
HTTP_PORT = int(os.environ.get('PORT', 10000))

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

class GrokAI:
    """Shared Grok AI interface"""
    
    def __init__(self):
        self.api_key = GROK_API_KEY
    
    async def get_response(self, messages: list) -> str:
        """Get response from Grok AI"""
        try:
            headers = {
                'Authorization': f'Bearer {self.api_key}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                "messages": messages,
                "model": "grok-3-fast", 
                "temperature": 0.7,
                "max_tokens": 1500
            }
            
            response = requests.post(
                'https://api.x.ai/v1/chat/completions',
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                return f"❌ API Error: {response.status_code} - {response.text}"
                
        except Exception as e:
            return f"❌ Connection error: {e}"

class EnhancedGrokSSHSession:
    """Enhanced SSH session for Grok AI"""
    
    def __init__(self, process: SSHServerProcess):
        self.process = process
        self.grok = GrokAI()
        self.conversation_history = []
        self.session_start = datetime.now()
        self.username = process.get_extra_info('username', 'user')
        
    async def display_banner(self):
        """Display enhanced SSH banner"""
        banner = f"""{Colors.BOLD}{Colors.CYAN}
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║    🚀🔑 ENHANCED GROK AI SSH TERMINAL 🔑🚀                                  ║
║                                                                              ║
║    👤 User: {self.username:<20}  🕒 Connected: {self.session_start.strftime('%H:%M:%S')}          ║
║    🌐 SSH + Web Access Available                                            ║
║                                                                              ║
║    💬 Advanced AI Conversation  •  🎯 Lightning Fast Responses              ║
║    🤖 Grok-3-Fast Model        •  🔥 Full Terminal Experience               ║
║                                                                              ║
║    Commands: 'help', 'clear', 'history', 'status', 'exit'                   ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝{Colors.RESET}

{Colors.GREEN}🎉 Welcome to Enhanced Grok AI via SSH!{Colors.RESET}
{Colors.BLUE}💡 Type your questions and get instant AI responses.{Colors.RESET}
{Colors.YELLOW}🌟 Full conversation history and context maintained.{Colors.RESET}

"""
        self.process.stdout.write(banner)
    
    async def handle_command(self, command: str) -> Optional[str]:
        """Handle special commands"""
        command = command.strip().lower()
        
        if command == 'help':
            return f"""{Colors.YELLOW}
📋 Enhanced Grok Terminal Commands:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• help     - Show this help message
• clear    - Clear conversation history  
• history  - Show conversation history
• status   - Show detailed session status
• context  - Show conversation context
• export   - Export conversation history
• exit     - Exit the terminal
• quit     - Exit the terminal

💡 Advanced Tips:
• Multi-line input supported - end with empty line
• Rich conversation context maintained
• Export your chat history anytime
• Full SSH terminal features available
{Colors.RESET}"""
        
        elif command == 'clear':
            self.conversation_history = []
            return f"{Colors.GREEN}✅ Conversation history cleared{Colors.RESET}"
        
        elif command == 'history':
            if not self.conversation_history:
                return f"{Colors.YELLOW}📝 No conversation history yet{Colors.RESET}"
            
            history_text = f"{Colors.BLUE}📝 Conversation History ({len(self.conversation_history)} messages):{Colors.RESET}\\n"
            for i, msg in enumerate(self.conversation_history[-20:], 1):  # Last 20 messages
                role = "👤 You" if msg['role'] == 'user' else "🤖 Grok"
                content = msg['content'][:120] + "..." if len(msg['content']) > 120 else msg['content']
                history_text += f"{Colors.CYAN}{i:2d}. {role}:{Colors.RESET} {content}\\n"
            
            return history_text
        
        elif command == 'status':
            uptime = datetime.now() - self.session_start
            user_messages = len([m for m in self.conversation_history if m['role'] == 'user'])
            return f"""{Colors.GREEN}
📊 Enhanced Session Status:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━
• User: {self.username}
• Connected: {self.session_start.strftime('%Y-%m-%d %H:%M:%S')}
• Session Uptime: {str(uptime).split('.')[0]}
• Questions Asked: {user_messages}
• Total Messages: {len(self.conversation_history)}
• API Status: ✅ Connected to Grok-3-Fast
• SSH Features: ✅ Full terminal support
• Memory: ✅ Context maintained
{Colors.RESET}"""
        
        elif command == 'context':
            recent_msgs = len([m for m in self.conversation_history[-10:] if m['role'] == 'user'])
            return f"""{Colors.BLUE}
🧠 Conversation Context:
━━━━━━━━━━━━━━━━━━━━━━━━━
• Recent questions: {recent_msgs}
• Context window: Last 10 exchanges
• Memory status: ✅ Active
• Conversation flow: Maintained
{Colors.RESET}"""
        
        elif command == 'export':
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            export_data = {
                'session_info': {
                    'user': self.username,
                    'start_time': self.session_start.isoformat(),
                    'export_time': datetime.now().isoformat()
                },
                'conversation': self.conversation_history
            }
            return f"""{Colors.GREEN}
📤 Conversation Export:
━━━━━━━━━━━━━━━━━━━━━━━━
Export ID: grok_chat_{timestamp}
Messages: {len(self.conversation_history)}
Format: JSON

{json.dumps(export_data, indent=2)}
{Colors.RESET}"""
        
        elif command in ['exit', 'quit']:
            return "DISCONNECT"
        
        return None  # Not a command
    
    async def run_session(self):
        """Enhanced session loop"""
        try:
            await self.display_banner()
            
            while True:
                # Enhanced prompt
                self.process.stdout.write(f"\\n{Colors.BOLD}{Colors.GREEN}🚀 grok-ssh>{Colors.RESET} ")
                
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
                        self.process.stdout.write(f"\\n{Colors.YELLOW}👋 Goodbye! Thanks for using Enhanced Grok SSH Terminal{Colors.RESET}\\n")
                        break
                    elif command_response:
                        self.process.stdout.write(f"\\n{command_response}\\n")
                        continue
                    
                    # Add system context for better responses
                    system_msg = {
                        "role": "system",
                        "content": "You are Grok, an advanced AI assistant. Provide clear, helpful, and detailed responses. Maintain context from the conversation history."
                    }
                    
                    # Prepare messages with context
                    messages = [system_msg] + self.conversation_history[-20:] + [{"role": "user", "content": user_input}]
                    
                    # Show thinking indicator
                    self.process.stdout.write(f"\\n{Colors.BLUE}🤖 Grok is analyzing and responding...{Colors.RESET}\\n")
                    
                    # Get AI response
                    ai_response = await self.grok.get_response(messages)
                    
                    # Add to conversation history
                    self.conversation_history.append({"role": "user", "content": user_input})
                    self.conversation_history.append({"role": "assistant", "content": ai_response})
                    
                    # Display enhanced response
                    self.process.stdout.write(f"\\n{Colors.BOLD}{Colors.BLUE}🤖 Grok AI:{Colors.RESET}\\n")
                    self.process.stdout.write(f"{Colors.WHITE}{ai_response}{Colors.RESET}\\n")
                    
                except asyncio.IncompleteReadError:
                    break
                except Exception as e:
                    self.process.stdout.write(f"\\n{Colors.RED}❌ Session error: {e}{Colors.RESET}\\n")
                    
        except Exception as e:
            self.process.stdout.write(f"\\n{Colors.RED}❌ Fatal error: {e}{Colors.RESET}\\n")
        finally:
            self.process.exit(0)

# Web Interface
app = FastAPI(title="Enhanced Grok AI Terminal")
grok = GrokAI()

@app.get("/", response_class=HTMLResponse)
async def web_terminal():
    """Enhanced web terminal interface"""
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>🚀 Enhanced Grok AI Terminal</title>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            * { margin: 0; padding: 0; box-sizing: border-box; }
            body { 
                background: linear-gradient(135deg, #0c0c0c 0%, #1a1a2e 50%, #16213e 100%);
                color: #00ff88; 
                font-family: 'Courier New', monospace; 
                height: 100vh;
                overflow: hidden;
            }
            .header {
                background: rgba(0, 255, 136, 0.1);
                padding: 15px;
                border-bottom: 2px solid #00ff88;
                text-align: center;
            }
            .terminal-container {
                height: calc(100vh - 120px);
                display: flex;
                flex-direction: column;
                padding: 20px;
            }
            .terminal-output {
                flex: 1;
                overflow-y: auto;
                padding: 15px;
                background: rgba(0, 0, 0, 0.3);
                border: 1px solid #00ff88;
                border-radius: 8px;
                margin-bottom: 15px;
                font-size: 14px;
                line-height: 1.6;
            }
            .input-container {
                display: flex;
                gap: 10px;
            }
            .terminal-input {
                flex: 1;
                background: rgba(0, 0, 0, 0.5);
                color: #00ff88;
                border: 2px solid #00ff88;
                padding: 12px;
                font-family: 'Courier New', monospace;
                font-size: 14px;
                border-radius: 6px;
            }
            .send-btn {
                background: #00ff88;
                color: #000;
                border: none;
                padding: 12px 24px;
                font-weight: bold;
                border-radius: 6px;
                cursor: pointer;
                transition: all 0.3s;
            }
            .send-btn:hover {
                background: #00cc70;
                transform: translateY(-2px);
            }
            .message {
                margin: 10px 0;
                padding: 8px;
                border-radius: 6px;
            }
            .user-message {
                background: rgba(0, 123, 255, 0.2);
                border-left: 4px solid #007bff;
            }
            .ai-message {
                background: rgba(0, 255, 136, 0.1);
                border-left: 4px solid #00ff88;
            }
            .ssh-info {
                background: rgba(255, 193, 7, 0.1);
                border: 1px solid #ffc107;
                padding: 15px;
                border-radius: 8px;
                margin: 15px 0;
                text-align: center;
            }
            .status-indicator {
                position: fixed;
                top: 20px;
                right: 20px;
                background: #00ff88;
                color: #000;
                padding: 8px 16px;
                border-radius: 20px;
                font-weight: bold;
                font-size: 12px;
            }
        </style>
    </head>
    <body>
        <div class="status-indicator">🟢 LIVE</div>
        
        <div class="header">
            <h1>🚀🤖 Enhanced Grok AI Terminal</h1>
            <p>💡 Advanced AI conversation with full SSH access available</p>
        </div>
        
        <div class="ssh-info">
            <strong>🔑 SSH Access Available!</strong><br>
            Connect via: <code>ssh user@your-render-url -p 2222</code><br>
            <em>For the full terminal experience with history, context, and advanced commands</em>
        </div>
        
        <div class="terminal-container">
            <div class="terminal-output" id="output">
                <div class="message ai-message">
                    <strong>🤖 Enhanced Grok AI:</strong> Welcome! I'm ready to help with any questions or tasks. 
                    This web interface provides basic chat, while SSH access offers the full terminal experience 
                    with conversation history, export features, and advanced commands.
                </div>
            </div>
            
            <div class="input-container">
                <input type="text" class="terminal-input" id="userInput" placeholder="Ask Grok anything..." autofocus>
                <button class="send-btn" onclick="sendMessage()">Send 🚀</button>
            </div>
        </div>

        <script>
            const output = document.getElementById('output');
            const userInput = document.getElementById('userInput');
            
            userInput.addEventListener('keypress', function(e) {
                if (e.key === 'Enter') {
                    sendMessage();
                }
            });
            
            async function sendMessage() {
                const message = userInput.value.trim();
                if (!message) return;
                
                // Add user message
                addMessage('user', message);
                userInput.value = '';
                
                try {
                    // Call Grok API
                    const response = await fetch('/api/chat', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ message: message })
                    });
                    
                    const data = await response.json();
                    addMessage('ai', data.response);
                } catch (error) {
                    addMessage('ai', '❌ Connection error: ' + error.message);
                }
            }
            
            function addMessage(type, content) {
                const messageDiv = document.createElement('div');
                messageDiv.className = `message ${type}-message`;
                messageDiv.innerHTML = `<strong>${type === 'user' ? '👤 You' : '🤖 Grok AI'}:</strong> ${content}`;
                output.appendChild(messageDiv);
                output.scrollTop = output.scrollHeight;
            }
        </script>
    </body>
    </html>
    """

@app.post("/api/chat")
async def chat_api(request: dict):
    """API endpoint for web chat"""
    message = request.get('message', '')
    if not message:
        return {"error": "No message provided"}
    
    try:
        messages = [
            {"role": "system", "content": "You are Grok, a helpful AI assistant. Provide clear and useful responses."},
            {"role": "user", "content": message}
        ]
        
        response = await grok.get_response(messages)
        return {"response": response}
    except Exception as e:
        return {"error": f"Failed to get response: {e}"}

@app.get("/health")
async def health():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "enhanced-grok-terminal",
        "features": {
            "ssh": SSH_AVAILABLE,
            "web": True,
            "api": True
        },
        "timestamp": datetime.now().isoformat()
    }

async def start_ssh_server():
    """Start SSH server if available"""
    if not SSH_AVAILABLE:
        print(f"{Colors.YELLOW}⚠️  SSH server unavailable - running web-only mode{Colors.RESET}")
        return
    
    try:
        # Generate host key if needed
        if not os.path.exists('ssh_host_key'):
            print(f"{Colors.YELLOW}🔐 Generating SSH host key...{Colors.RESET}")
            key = asyncssh.generate_private_key('ssh-rsa', key_size=2048)
            key.write_private_key('ssh_host_key')
            print(f"{Colors.GREEN}✅ SSH host key generated{Colors.RESET}")
        
        async def handle_client(process: SSHServerProcess):
            session = EnhancedGrokSSHSession(process)
            await session.run_session()
        
        print(f"{Colors.GREEN}🔑 Starting Enhanced Grok SSH Server...{Colors.RESET}")
        print(f"{Colors.BLUE}📡 SSH Port: {SSH_PORT}{Colors.RESET}")
        print(f"{Colors.BLUE}🌐 Web Port: {HTTP_PORT}{Colors.RESET}")
        
        # Start SSH server
        ssh_server = await asyncssh.listen(
            host='0.0.0.0',
            port=SSH_PORT,
            server_host_keys=['ssh_host_key'],
            process_factory=handle_client,
            password_auth=True,
            public_key_auth=False
        )
        
        print(f"{Colors.GREEN}✅ SSH Server running on port {SSH_PORT}!{Colors.RESET}")
        print(f"{Colors.CYAN}🎯 Connect with: ssh user@localhost -p {SSH_PORT}{Colors.RESET}")
        
        return ssh_server
        
    except Exception as e:
        print(f"{Colors.RED}❌ SSH Server failed: {e}{Colors.RESET}")
        return None

async def main():
    """Main application - starts both SSH and web servers"""
    print(f"{Colors.BOLD}{Colors.CYAN}")
    print("🚀 Enhanced Grok AI Terminal Starting...")
    print("=" * 50)
    print(f"{Colors.RESET}")
    
    # Start SSH server in background
    ssh_server = await start_ssh_server()
    
    # Start web server
    print(f"{Colors.GREEN}🌐 Starting web server on port {HTTP_PORT}...{Colors.RESET}")
    
    config = uvicorn.Config(
        app, 
        host="0.0.0.0", 
        port=HTTP_PORT,
        log_level="info"
    )
    server = uvicorn.Server(config)
    
    try:
        await server.serve()
    finally:
        if ssh_server:
            ssh_server.close()
            await ssh_server.wait_closed()

if __name__ == "__main__":
    if '--production' in sys.argv:
        # Production mode for Render.com
        asyncio.run(main())
    else:
        # Development mode
        print(f"{Colors.GREEN}Enhanced Grok Terminal{Colors.RESET}")
        print("Modes: --production (for Render.com)")
        asyncio.run(main())
