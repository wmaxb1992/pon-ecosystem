#!/usr/bin/env python3
"""
SSH Grok Entry Point
===================
Instant Grok AI access when you SSH into Render.com
"""

import os
import sys
import signal
from instant_grok_terminal import InstantGrokTerminal

def signal_handler(sig, frame):
    """Handle Ctrl+C gracefully"""
    print('\n\n👋 Goodbye from Grok AI Terminal!')
    sys.exit(0)

def main():
    """Main entry point for SSH users"""
    # Handle Ctrl+C
    signal.signal(signal.SIGINT, signal_handler)
    
    # Set Grok API key from environment
    if 'GROK_API_KEY' in os.environ:
        # Update the API key in instant_grok_terminal
        import instant_grok_terminal
        instant_grok_terminal.GROK_API_KEY = os.environ['GROK_API_KEY']
    
    # Clear screen for clean startup
    os.system('clear' if os.name == 'posix' else 'cls')
    
    # Launch instant Grok terminal
    print("🔌 Connecting to Grok AI...")
    terminal = InstantGrokTerminal()
    terminal.run()

if __name__ == "__main__":
    main()
