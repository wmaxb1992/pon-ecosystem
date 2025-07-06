#!/usr/bin/env python3
"""
Instant Grok AI Terminal - Direct SSH Access
============================================
Provides immediate Grok AI access via terminal on Render.com
"""

import os
import sys
import asyncio
import json
from datetime import datetime
import requests

# Set your Grok API key
GROK_API_KEY = "xai-E7Ml5WgMcMYT0lxew2n1b6EwlD8oD3x8OOVuX4OvxSUI9IvLhT2B3ZpESW52N50l2qBNckXyRRkEzv6N"

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

class InstantGrokTerminal:
    """Instant Grok AI Terminal for immediate SSH access"""
    
    def __init__(self):
        self.api_key = GROK_API_KEY
        self.conversation_history = []
        self.session_start = datetime.now()
        
    def display_banner(self):
        """Display instant Grok terminal banner"""
        banner = f"""{Colors.BOLD}{Colors.CYAN}
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║    🚀 INSTANT GROK AI TERMINAL 🚀                                           ║
║                                                                              ║
║    💬 Direct AI Conversation  •  🎯 Instant Responses                       ║
║    🤖 Grok-3-Fast Model      •  🔥 Zero Setup Required                      ║
║                                                                              ║
║    Type your questions and get instant AI responses!                        ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝{Colors.RESET}"""
        
        print(banner)
        print(f"\n{Colors.GREEN}✅ Connected to Grok AI (grok-3-fast){Colors.RESET}")
        print(f"{Colors.YELLOW}📅 Session started: {self.session_start.strftime('%Y-%m-%d %H:%M:%S')}{Colors.RESET}")
        print(f"{Colors.CYAN}💡 Type 'help' for commands, 'quit' to exit{Colors.RESET}")
        print(f"{Colors.WHITE}{'─'*80}{Colors.RESET}")
    
    def call_grok(self, user_message: str) -> str:
        """Direct call to Grok AI API"""
        try:
            url = "https://api.x.ai/v1/chat/completions"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {self.api_key}"
            }
            
            messages = [
                {
                    "role": "system", 
                    "content": "You are Grok, a helpful AI assistant. Provide clear, concise, and practical responses. Be direct and useful."
                }
            ]
            
            # Add conversation history (last 5 exchanges)
            messages.extend(self.conversation_history[-10:])
            
            # Add current message
            messages.append({"role": "user", "content": user_message})
            
            data = {
                "messages": messages,
                "model": "grok-3-fast",
                "stream": False,
                "temperature": 0.7,
                "max_tokens": 2000
            }
            
            print(f"{Colors.YELLOW}🤖 Grok is thinking...{Colors.RESET}")
            
            response = requests.post(url, headers=headers, json=data, timeout=30)
            
            if response.status_code == 200:
                result = response.json()
                grok_response = result['choices'][0]['message']['content']
                
                # Add to conversation history
                self.conversation_history.append({"role": "user", "content": user_message})
                self.conversation_history.append({"role": "assistant", "content": grok_response})
                
                return grok_response
            else:
                return f"❌ API Error: {response.status_code} - {response.text}"
                
        except Exception as e:
            return f"❌ Error calling Grok: {str(e)}"
    
    def show_help(self):
        """Show available commands"""
        help_text = f"""
{Colors.BOLD}{Colors.CYAN}🤖 Instant Grok AI Commands:{Colors.RESET}

{Colors.GREEN}Basic Usage:{Colors.RESET}
  Just type your question and press Enter!
  
{Colors.YELLOW}Special Commands:{Colors.RESET}
  help                    - Show this help
  clear                   - Clear conversation history
  history                 - Show conversation history
  stats                   - Show session statistics
  quit/exit/q            - Exit terminal

{Colors.BLUE}Examples:{Colors.RESET}
  "How do I deploy a Python app to Render?"
  "Write a function to process CSV files"
  "Explain async/await in Python"
  "Debug this error: ModuleNotFoundError"

{Colors.WHITE}Pro Tips:{Colors.RESET}
  • Be specific in your questions for better responses
  • Ask for code examples, explanations, or debugging help
  • Grok remembers the conversation context
"""
        print(help_text)
    
    def show_stats(self):
        """Show session statistics"""
        duration = datetime.now() - self.session_start
        exchanges = len(self.conversation_history) // 2
        
        print(f"\n{Colors.CYAN}📊 Session Statistics:{Colors.RESET}")
        print(f"  Duration: {str(duration).split('.')[0]}")
        print(f"  Exchanges: {exchanges}")
        print(f"  Model: grok-3-fast")
        print(f"  History: {len(self.conversation_history)} messages")
    
    def show_history(self):
        """Show conversation history"""
        if not self.conversation_history:
            print(f"{Colors.YELLOW}No conversation history yet{Colors.RESET}")
            return
        
        print(f"\n{Colors.CYAN}📜 Conversation History:{Colors.RESET}")
        print(f"{Colors.WHITE}{'─'*60}{Colors.RESET}")
        
        for i, msg in enumerate(self.conversation_history[-10:], 1):  # Last 5 exchanges
            role_color = Colors.GREEN if msg['role'] == 'user' else Colors.BLUE
            role_name = "You" if msg['role'] == 'user' else "Grok"
            
            print(f"{role_color}{role_name}:{Colors.RESET} {msg['content'][:100]}...")
            if i % 2 == 0:  # After each exchange
                print()
    
    def run(self):
        """Run the instant Grok terminal"""
        self.display_banner()
        
        while True:
            try:
                # Get user input
                user_input = input(f"\n{Colors.BOLD}{Colors.WHITE}💬 You: {Colors.RESET}").strip()
                
                if not user_input:
                    continue
                
                # Handle commands
                if user_input.lower() in ['quit', 'exit', 'q']:
                    print(f"\n{Colors.GREEN}👋 Goodbye! Thanks for using Grok AI Terminal{Colors.RESET}")
                    break
                
                elif user_input.lower() == 'help':
                    self.show_help()
                    continue
                
                elif user_input.lower() == 'clear':
                    self.conversation_history = []
                    os.system('clear' if os.name == 'posix' else 'cls')
                    self.display_banner()
                    continue
                
                elif user_input.lower() == 'history':
                    self.show_history()
                    continue
                
                elif user_input.lower() == 'stats':
                    self.show_stats()
                    continue
                
                # Call Grok AI
                response = self.call_grok(user_input)
                
                # Display response
                print(f"\n{Colors.BOLD}{Colors.BLUE}🤖 Grok:{Colors.RESET}")
                print(f"{Colors.WHITE}{response}{Colors.RESET}")
                
            except KeyboardInterrupt:
                print(f"\n\n{Colors.YELLOW}Use 'quit' to exit properly{Colors.RESET}")
                continue
            except EOFError:
                print(f"\n{Colors.GREEN}👋 Goodbye!{Colors.RESET}")
                break
            except Exception as e:
                print(f"{Colors.RED}❌ Error: {e}{Colors.RESET}")

if __name__ == "__main__":
    terminal = InstantGrokTerminal()
    terminal.run()
