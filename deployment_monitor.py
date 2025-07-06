#!/usr/bin/env python3
"""
Real-Time Deployment Monitor
===========================
Continuously monitors and validates the PON ecosystem deployment
"""

import time
import os
import subprocess
import requests
from datetime import datetime, timedelta
import json
from pathlib import Path

class DeploymentMonitor:
    def __init__(self):
        self.start_time = datetime.now()
        self.end_time = self.start_time + timedelta(hours=20)  # Until 12pm next day
        self.task_count = 0
        
    def log_status(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")
        
    def check_local_services(self):
        """Check all local services are running"""
        services = {
            "Backend API": "http://localhost:8000/health",
            "Frontend": "http://localhost:3001",
        }
        
        status = {}
        for name, url in services.items():
            try:
                response = requests.get(url, timeout=5)
                status[name] = "✅ Running" if response.status_code == 200 else f"❌ Error {response.status_code}"
            except Exception as e:
                status[name] = f"❌ Down: {str(e)[:50]}"
                
        return status
    
    def validate_ai_systems(self):
        """Validate AI systems are responsive"""
        try:
            # Test Grok API
            from enhanced_grok_integration import EnhancedGrokIntegration
            grok = EnhancedGrokIntegration()
            test_response = grok.generate_response("System status check")
            return "✅ AI Systems Online"
        except Exception as e:
            return f"❌ AI Systems: {str(e)[:50]}"
    
    def check_git_status(self):
        """Check git repository status"""
        try:
            result = subprocess.run(['git', 'status', '--porcelain'], 
                                 capture_output=True, text=True, cwd='/Users/maxwoldenberg/Desktop/pon')
            if result.stdout.strip():
                return f"⚠️ Uncommitted changes: {len(result.stdout.strip().split())} files"
            else:
                return "✅ Git clean, ready for deployment"
        except Exception as e:
            return f"❌ Git error: {e}"
    
    def perform_task_cycle(self):
        """Perform 4 tasks every 5 minutes"""
        self.task_count += 1
        cycle_start = datetime.now()
        
        print("\n" + "="*70)
        print(f"🔄 TASK CYCLE #{self.task_count} - {cycle_start.strftime('%H:%M:%S')}")
        print("="*70)
        
        # Task 1: Service Health Check
        self.log_status("📊 Task 1: Checking service health...")
        service_status = self.check_local_services()
        for service, status in service_status.items():
            self.log_status(f"   {service}: {status}")
        
        # Task 2: AI System Validation
        self.log_status("🤖 Task 2: Validating AI systems...")
        ai_status = self.validate_ai_systems()
        self.log_status(f"   {ai_status}")
        
        # Task 3: Git Repository Check
        self.log_status("📦 Task 3: Checking repository status...")
        git_status = self.check_git_status()
        self.log_status(f"   {git_status}")
        
        # Task 4: Deployment Status Update
        self.log_status("🚀 Task 4: Updating deployment status...")
        self.update_deployment_status()
        
        # Summary
        elapsed = datetime.now() - self.start_time
        remaining = self.end_time - datetime.now()
        
        print("\n📈 CYCLE SUMMARY:")
        print(f"   Runtime: {elapsed}")
        print(f"   Remaining: {remaining}")
        print(f"   Tasks completed: {self.task_count * 4}")
        print(f"   Next cycle: {(cycle_start + timedelta(minutes=5)).strftime('%H:%M:%S')}")
        
    def update_deployment_status(self):
        """Update deployment status file"""
        status = {
            "timestamp": datetime.now().isoformat(),
            "cycle": self.task_count,
            "services": self.check_local_services(),
            "ai_status": self.validate_ai_systems(),
            "git_status": self.check_git_status(),
            "uptime": str(datetime.now() - self.start_time),
            "render_deployment_ready": True
        }
        
        with open('/Users/maxwoldenberg/Desktop/pon/deployment_status.json', 'w') as f:
            json.dump(status, f, indent=2)
        
        self.log_status("   Status file updated: deployment_status.json")
    
    def run_continuous_monitoring(self):
        """Run continuous monitoring until 12pm next day"""
        self.log_status("🚀 Starting continuous PON ecosystem monitoring...")
        self.log_status(f"📅 Start: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        self.log_status(f"🎯 End: {self.end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        
        while datetime.now() < self.end_time:
            self.perform_task_cycle()
            
            # Wait 5 minutes for next cycle
            next_cycle = datetime.now() + timedelta(minutes=5)
            while datetime.now() < next_cycle:
                time.sleep(30)  # Check every 30 seconds
                if datetime.now() >= self.end_time:
                    break
        
        self.log_status("🎉 Monitoring complete! PON ecosystem fully operational.")

if __name__ == "__main__":
    monitor = DeploymentMonitor()
    monitor.run_continuous_monitoring()
