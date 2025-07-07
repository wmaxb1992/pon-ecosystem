#!/usr/bin/env python3
"""
Live CEO AI Bot Chat Interface
=============================
Connect directly to your CEO AI Bot running on Render for real-time strategic discussions
"""

import requests
import json
import time
from datetime import datetime

class LiveCEOChat:
    def __init__(self):
        # Your CEO AI Bot is deployed on Render
        self.ceo_url = "https://ceo-ai-bot.onrender.com"
        self.chat_endpoint = f"{self.ceo_url}/chat"
        self.status_endpoint = f"{self.ceo_url}/status"
        
    def display_ceo_banner(self):
        """Display CEO AI Bot banner"""
        banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║     👔 LIVE CEO AI BOT CHAT - STRATEGIC LEADERSHIP CONSOLE 👔               ║
║                                                                              ║
║     🎯 Strategic Decisions  •  📊 Real-time Coordination                    ║
║     🚀 Project Planning     •  🏆 Team Management                           ║
║     💡 Vision & Direction   •  🤝 Executive Consultation                     ║
║                                                                              ║
║     "Your AI CEO is ready for strategic consultation"                       ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
        """
        print(banner)
        
    def check_ceo_status(self):
        """Check if CEO AI Bot is online and responsive"""
        try:
            print("🔍 Connecting to CEO AI Bot on Render...")
            response = requests.get(self.status_endpoint, timeout=10)
            
            if response.status_code == 200:
                print("✅ CEO AI Bot is ONLINE and ready!")
                status_data = response.json() if response.content else {}
                
                print(f"📊 Status: {status_data.get('status', 'Active')}")
                print(f"🕐 Uptime: {status_data.get('uptime', 'Unknown')}")
                print(f"📈 Decisions Made: {status_data.get('decisions_made', 'N/A')}")
                print(f"🎯 Active Projects: {status_data.get('active_projects', 'N/A')}")
                return True
            else:
                print(f"⚠️ CEO AI Bot responded with status: {response.status_code}")
                return False
                
        except requests.exceptions.ConnectionError:
            print("❌ Cannot connect to CEO AI Bot - checking alternative endpoints...")
            return self.try_alternative_endpoints()
        except Exception as e:
            print(f"❌ Error connecting to CEO AI Bot: {e}")
            return self.try_alternative_endpoints()
    
    def try_alternative_endpoints(self):
        """Try alternative ways to reach the CEO AI Bot"""
        alternative_urls = [
            "https://ceo-ai-bot.onrender.com",
            "https://ai-code-worker.onrender.com/ceo-chat",
            "https://instant-grok-terminal.onrender.com/ceo-interface"
        ]
        
        for url in alternative_urls:
            try:
                print(f"🔄 Trying {url}...")
                response = requests.get(f"{url}/health", timeout=5)
                if response.status_code == 200:
                    print(f"✅ Found CEO AI Bot at: {url}")
                    self.ceo_url = url
                    self.chat_endpoint = f"{url}/chat"
                    return True
            except:
                continue
                
        print("📝 CEO AI Bot may be spinning up (Render cold start) - this can take 1-2 minutes")
        print("🔄 You can also access via the main AI terminal:")
        print("   🌐 https://instant-grok-terminal.onrender.com")
        return False
    
    def send_message_to_ceo(self, message):
        """Send a message to the CEO AI Bot"""
        try:
            payload = {
                "message": message,
                "user_id": "live_chat",
                "timestamp": datetime.now().isoformat(),
                "session_type": "strategic_consultation"
            }
            
            print("📤 Sending message to CEO AI Bot...")
            response = requests.post(
                self.chat_endpoint, 
                json=payload, 
                timeout=30,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                ceo_response = response.json()
                self.display_ceo_response(ceo_response)
                return True
            else:
                print(f"❌ CEO AI Bot returned status: {response.status_code}")
                print(f"Response: {response.text}")
                return False
                
        except requests.exceptions.Timeout:
            print("⏱️ CEO AI Bot is thinking... (this may take a moment for complex strategic decisions)")
            return False
        except Exception as e:
            print(f"❌ Error sending message: {e}")
            return False
    
    def display_ceo_response(self, response_data):
        """Display the CEO AI Bot's response"""
        print("\n" + "="*80)
        print("👔 CEO AI BOT RESPONSE:")
        print("="*80)
        
        if isinstance(response_data, dict):
            if 'strategic_analysis' in response_data:
                analysis = response_data['strategic_analysis']
                print(f"🎯 Strategic Assessment: {analysis.get('assessment', 'N/A')}")
                print(f"📊 Priority Level: {analysis.get('priority', 'N/A')}")
                print(f"⏱️ Timeline: {analysis.get('timeline', 'N/A')}")
                
            if 'ceo_decision' in response_data:
                decision = response_data['ceo_decision']
                print(f"✅ Decision: {decision.get('approved', 'Pending')}")
                print(f"💭 Reasoning: {decision.get('reasoning', 'N/A')}")
                
            if 'leadership_message' in response_data:
                print(f"💬 CEO Message: {response_data['leadership_message']}")
                
            if 'response' in response_data:
                print(f"💬 Response: {response_data['response']}")
                
        else:
            print(f"💬 CEO Response: {response_data}")
            
        print("="*80 + "\n")
    
    def interactive_chat(self):
        """Start interactive chat with CEO AI Bot"""
        self.display_ceo_banner()
        
        if not self.check_ceo_status():
            print("\n🔧 ALTERNATIVE ACCESS:")
            print("   1. Visit: https://instant-grok-terminal.onrender.com")
            print("   2. Type 'ceo chat' to access CEO AI Bot interface")
            print("   3. Or wait 1-2 minutes for service to wake up")
            return
        
        print("\n🎙️ You are now connected to your CEO AI Bot!")
        print("💡 Type your strategic questions, project requests, or team coordination needs")
        print("🚪 Type 'exit' to end the session\n")
        
        while True:
            try:
                user_input = input("👤 You: ").strip()
                
                if user_input.lower() in ['exit', 'quit', 'bye']:
                    print("👔 CEO AI Bot: Thank you for the strategic session. I'll continue coordinating the team!")
                    break
                    
                if not user_input:
                    continue
                    
                success = self.send_message_to_ceo(user_input)
                if not success:
                    print("🔄 Trying to reconnect to CEO AI Bot...")
                    time.sleep(2)
                    
            except KeyboardInterrupt:
                print("\n👔 CEO AI Bot: Session ended. I'll keep leading the team!")
                break
            except Exception as e:
                print(f"❌ Chat error: {e}")
                break
    
    def quick_status_check(self):
        """Quick check of what CEO AI Bot is currently working on"""
        print("📊 LIVE CEO AI BOT STATUS CHECK")
        print("="*50)
        
        try:
            # Try to get current projects and decisions
            response = requests.get(f"{self.ceo_url}/current-projects", timeout=10)
            if response.status_code == 200:
                projects = response.json()
                print("🎯 Current Strategic Projects:")
                for project in projects.get('projects', []):
                    print(f"   • {project}")
            
            # Get recent decisions
            response = requests.get(f"{self.ceo_url}/recent-decisions", timeout=10)
            if response.status_code == 200:
                decisions = response.json()
                print("\n📋 Recent Strategic Decisions:")
                for decision in decisions.get('decisions', [])[:5]:
                    print(f"   • {decision}")
                    
        except:
            print("📍 CEO AI Bot Location: https://ceo-ai-bot.onrender.com")
            print("🔗 Alternative Access: https://instant-grok-terminal.onrender.com")
            print("📝 Status: Deployed and running 24/7 on Render")
            
def main():
    print("🚀 LIVE CEO AI BOT CONNECTION")
    print("="*40)
    print("1. Interactive Chat with CEO AI Bot")
    print("2. Quick Status Check")
    print("3. Exit")
    
    choice = input("\nSelect option (1-3): ").strip()
    
    ceo_chat = LiveCEOChat()
    
    if choice == "1":
        ceo_chat.interactive_chat()
    elif choice == "2":
        ceo_chat.quick_status_check()
    else:
        print("👔 CEO AI Bot is available 24/7 at: https://ceo-ai-bot.onrender.com")

if __name__ == "__main__":
    main()
