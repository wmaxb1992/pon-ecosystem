#!/usr/bin/env python3
"""
Render.com Main Server - Multi-Worker AI Terminal
"""
import os
import asyncio
from flask import Flask, request, jsonify
import threading
import subprocess
import time

# Set environment variables
os.environ['GROK_API_KEY'] = 'xai-E7Ml5WgMcMYT0lxew2n1b6EwlD8oD3x8OOVuX4OvxSUI9IvLhT2B3ZpESW52N50l2qBNckXyRRkEzv6N'

app = Flask(__name__)

# Import AI systems
try:
    from epic_terminal_interface import EpicTerminalInterface
    from ceo_ai_bot import get_ceo_ai
    from ai_multi_worker import coordinator
except ImportError as e:
    print(f"Warning: {e}")

# Global instances
terminal = None
ceo_bot = None

@app.route('/')
def home():
    return jsonify({
        "status": "running",
        "service": "Multi-Worker AI Terminal",
        "endpoints": ["/terminal", "/ceo", "/workers", "/status"]
    })

@app.route('/terminal', methods=['POST'])
def terminal_endpoint():
    global terminal
    if not terminal:
        terminal = EpicTerminalInterface()
    
    command = request.json.get('command', '')
    result = terminal.process_command_api(command)
    return jsonify(result)

@app.route('/ceo', methods=['POST'])
def ceo_endpoint():
    global ceo_bot
    if not ceo_bot:
        ceo_bot = get_ceo_ai(os.environ['GROK_API_KEY'])
    
    request_text = request.json.get('request', '')
    
    # Run async CEO planning
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    result = loop.run_until_complete(ceo_bot.strategic_planning_session(request_text))
    loop.close()
    
    return jsonify(result)

@app.route('/status')
def status():
    return jsonify({
        "workers": "active",
        "ceo": "ready",
        "terminal": "online"
    })

def start_redis():
    """Start Redis in background"""
    try:
        subprocess.run(['redis-server', '--daemonize', 'yes'], check=False)
    except:
        pass

def start_workers():
    """Start Celery workers"""
    try:
        subprocess.Popen(['celery', '-A', 'ai_multi_worker', 'worker', '--loglevel=info'], 
                        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except:
        pass

if __name__ == '__main__':
    print("🚀 Starting Multi-Worker AI Terminal Server...")
    
    # Start Redis and workers
    start_redis()
    time.sleep(2)
    start_workers()
    
    # Start Flask server
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
