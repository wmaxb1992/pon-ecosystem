#!/usr/bin/env python3
"""
Autonomous Progress Monitor
=========================
Check the progress of the autonomous executor
"""

import json
import os
from datetime import datetime

def check_status():
    print("🤖 AUTONOMOUS EXECUTOR STATUS")
    print("="*50)
    
    # Check status file
    status_file = "/Users/maxwoldenberg/Desktop/pon/autonomous_status.json"
    if os.path.exists(status_file):
        with open(status_file, 'r') as f:
            status = json.load(f)
        
        print(f"📊 System Status: {status.get('system_status', 'unknown')}")
        print(f"🔄 Cycles Completed: {status.get('cycles_completed', 0)}")
        print(f"💯 Health Score: {status.get('health_score', 0)}")
        print(f"⏰ Last Update: {status.get('timestamp', 'unknown')}")
    else:
        print("❌ Status file not found")
    
    # Check health file
    health_file = "/Users/maxwoldenberg/Desktop/pon/health_report.json"
    if os.path.exists(health_file):
        with open(health_file, 'r') as f:
            health = json.load(f)
        
        print("\n🏥 HEALTH REPORT")
        print("-"*30)
        health_data = health.get('health_report', {})
        print(f"Overall Health: {health_data.get('overall_health', 'unknown')}")
        print(f"Health Score: {health_data.get('health_score', 0)}")
        
        services = health_data.get('services', {})
        for service, status in services.items():
            if isinstance(status, dict):
                print(f"  {service}: {status.get('status', 'unknown')}")
            else:
                print(f"  {service}: {status}")
    
    # Check for AI improvements
    improvements_file = "/Users/maxwoldenberg/Desktop/pon/ai_improvements.json"
    if os.path.exists(improvements_file):
        with open(improvements_file, 'r') as f:
            improvements = json.load(f)
        print(f"\n🤖 AI Improvements Generated: {len(improvements)}")
        if improvements:
            latest = improvements[-1]
            print(f"Latest: {latest.get('suggestion', '')[:100]}...")
    
    print("\n🎯 AUTONOMOUS MODE ACTIVE UNTIL 12:00 PM")

if __name__ == "__main__":
    check_status()
