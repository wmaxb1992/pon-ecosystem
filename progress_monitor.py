#!/usr/bin/env python3
"""
Continuous Progress Monitor
=========================
Monitors autonomous execution progress and logs everything
"""

import time
import json
import subprocess
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s')
logger = logging.getLogger(__name__)

def monitor_progress():
    logger.info("📊 Starting continuous progress monitoring...")
    
    while True:
        try:
            current_time = datetime.now()
            target_time = current_time.replace(hour=12, minute=0, second=0, microsecond=0)
            if target_time <= current_time:
                target_time = target_time.replace(day=target_time.day + 1)
            
            remaining = target_time - current_time
            hours = int(remaining.total_seconds() // 3600)
            minutes = int((remaining.total_seconds() % 3600) // 60)
            
            logger.info(f"⏰ Time until 12pm: {hours}h {minutes}m")
            
            # Check autonomous status
            try:
                with open('/Users/maxwoldenberg/Desktop/pon/autonomous_status.json', 'r') as f:
                    status = json.load(f)
                    logger.info(f"🤖 Cycle: {status.get('cycle', 0)}, Improvements: {status.get('improvements', 0)}")
            except FileNotFoundError:
                logger.info("📄 Status file not created yet...")
            
            # Check if services are running
            try:
                result = subprocess.run(['pgrep', '-f', 'autonomous_deployment_executor'], 
                                      capture_output=True, text=True)
                if result.stdout.strip():
                    logger.info("✅ Autonomous executor is running")
                else:
                    logger.warning("❌ Autonomous executor not found")
            except:
                pass
            
            # Check git status
            try:
                result = subprocess.run(['git', 'log', '--oneline', '-5'], 
                                      cwd='/Users/maxwoldenberg/Desktop/pon',
                                      capture_output=True, text=True)
                if result.stdout:
                    recent_commits = result.stdout.strip().split('\n')
                    logger.info(f"📝 Recent commits: {len(recent_commits)}")
            except:
                pass
            
            if remaining.total_seconds() <= 0:
                logger.info("🎉 Target time reached! Monitoring complete.")
                break
                
            time.sleep(300)  # Check every 5 minutes
            
        except KeyboardInterrupt:
            logger.info("🛑 Monitoring stopped")
            break
        except Exception as e:
            logger.error(f"❌ Monitor error: {e}")
            time.sleep(60)

if __name__ == "__main__":
    monitor_progress()
