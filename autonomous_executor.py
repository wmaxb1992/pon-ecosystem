#!/usr/bin/env python3
"""
Autonomous PON Ecosystem Executor
===============================
Runs until 12pm next day, executing all deployment and improvement tasks
"""

import os
import sys
import json
import time
import subprocess
import requests
from datetime import datetime, timedelta
from pathlib import Path
import threading
import signal

class AutonomousExecutor:
    def __init__(self):
        self.start_time = datetime.now()
        self.end_time = datetime.now().replace(hour=12, minute=0, second=0, microsecond=0)
        if self.end_time <= self.start_time:
            self.end_time += timedelta(days=1)
        
        self.status_file = "/Users/maxwoldenberg/Desktop/pon/autonomous_status.json"
        self.health_file = "/Users/maxwoldenberg/Desktop/pon/health_report.json"
        self.cycles_completed = 0
        self.running = True
        
        # Service tracking
        self.services = {
            'backend': None,
            'frontend': None,
            'monitoring': None
        }
        
        print(f"🤖 AUTONOMOUS EXECUTOR STARTED")
        print(f"📅 Start: {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🎯 End: {self.end_time.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"⏱️ Duration: {self.end_time - self.start_time}")
        
    def log(self, message):
        timestamp = datetime.now().strftime("%H:%M:%S")
        print(f"[{timestamp}] {message}")
        
        # Also log to file
        with open("/Users/maxwoldenberg/Desktop/pon/logs/autonomous.log", "a") as f:
            f.write(f"[{timestamp}] {message}\n")
    
    def update_status(self, updates):
        """Update autonomous status file"""
        try:
            if os.path.exists(self.status_file):
                with open(self.status_file, 'r') as f:
                    status = json.load(f)
            else:
                status = {}
            
            status.update(updates)
            status['timestamp'] = datetime.now().isoformat()
            status['cycles_completed'] = self.cycles_completed
            
            with open(self.status_file, 'w') as f:
                json.dump(status, f, indent=2)
                
        except Exception as e:
            self.log(f"❌ Status update failed: {e}")
    
    def update_health(self, health_data):
        """Update health report file"""
        try:
            health_report = {
                "health_report": {
                    "timestamp": datetime.now().isoformat(),
                    "overall_health": health_data.get('overall_health', 'unknown'),
                    "health_score": health_data.get('health_score', 0),
                    **health_data
                }
            }
            
            with open(self.health_file, 'w') as f:
                json.dump(health_report, f, indent=2)
                
        except Exception as e:
            self.log(f"❌ Health update failed: {e}")
    
    def start_backend(self):
        """Start the backend server"""
        try:
            if self.services['backend'] is None:
                self.log("🔧 Starting Backend API...")
                self.services['backend'] = subprocess.Popen([
                    sys.executable, 
                    '/Users/maxwoldenberg/Desktop/pon/backend/main_enhanced.py'
                ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                time.sleep(5)  # Give it time to start
                self.log("✅ Backend API started")
                return True
        except Exception as e:
            self.log(f"❌ Backend start failed: {e}")
            return False
        return True
    
    def start_frontend(self):
        """Start the frontend server"""
        try:
            if self.services['frontend'] is None:
                self.log("🎨 Starting Frontend...")
                os.chdir('/Users/maxwoldenberg/Desktop/pon/frontend')
                
                # First build
                build_result = subprocess.run(['npm', 'run', 'build'], 
                                           capture_output=True, text=True)
                if build_result.returncode != 0:
                    self.log(f"⚠️ Frontend build had issues, continuing...")
                
                # Start on port 3001 to avoid conflicts
                self.services['frontend'] = subprocess.Popen([
                    'npm', 'start', '--', '--port', '3001'
                ], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                
                os.chdir('/Users/maxwoldenberg/Desktop/pon')
                time.sleep(3)
                self.log("✅ Frontend started on port 3001")
                return True
        except Exception as e:
            self.log(f"❌ Frontend start failed: {e}")
            return False
        return True
    
    def check_services(self):
        """Check if services are running"""
        services_status = {}
        
        # Check backend
        try:
            response = requests.get('http://localhost:8000/health', timeout=5)
            services_status['backend'] = response.status_code == 200
        except:
            services_status['backend'] = False
        
        # Check frontend
        try:
            response = requests.get('http://localhost:3001', timeout=5)
            services_status['frontend'] = response.status_code == 200
        except:
            services_status['frontend'] = False
        
        return services_status
    
    def deploy_to_render(self):
        """Deploy to Render.com"""
        try:
            self.log("🚀 Deploying to Render.com...")
            
            # Ensure all changes are committed
            subprocess.run(['git', 'add', '-A'], cwd='/Users/maxwoldenberg/Desktop/pon')
            result = subprocess.run([
                'git', 'commit', '-m', 
                f'🤖 AUTONOMOUS: Cycle {self.cycles_completed} - Auto-deployment'
            ], cwd='/Users/maxwoldenberg/Desktop/pon', capture_output=True)
            
            # Push to trigger Render deployment
            push_result = subprocess.run([
                'git', 'push', 'origin', 'main'
            ], cwd='/Users/maxwoldenberg/Desktop/pon', capture_output=True, text=True)
            
            if push_result.returncode == 0:
                self.log("✅ Pushed to GitHub - Render auto-deployment triggered")
                return True
            else:
                self.log(f"⚠️ Git push result: {push_result.stderr}")
                return False
                
        except Exception as e:
            self.log(f"❌ Render deployment failed: {e}")
            return False
    
    def generate_ai_improvement(self):
        """Generate an AI improvement"""
        try:
            self.log("🤖 Generating AI improvement...")
            
            # Use Grok to generate an improvement
            from enhanced_grok_integration import EnhancedGrokIntegration
            grok = EnhancedGrokIntegration()
            
            improvement_prompt = f"""
            Analyze the PON video ecosystem and suggest one small improvement.
            Current cycle: {self.cycles_completed}
            Focus on: performance, security, user experience, or functionality.
            Provide a specific, implementable suggestion.
            """
            
            response = grok.generate_response(improvement_prompt)
            
            # Log the improvement
            improvement = {
                "cycle": self.cycles_completed,
                "timestamp": datetime.now().isoformat(),
                "suggestion": response[:500],  # Truncate for logging
                "status": "generated"
            }
            
            # Save improvement
            improvements_file = "/Users/maxwoldenberg/Desktop/pon/ai_improvements.json"
            if os.path.exists(improvements_file):
                with open(improvements_file, 'r') as f:
                    improvements = json.load(f)
            else:
                improvements = []
            
            improvements.append(improvement)
            
            with open(improvements_file, 'w') as f:
                json.dump(improvements, f, indent=2)
            
            self.log(f"✅ AI improvement generated: {response[:100]}...")
            return True
            
        except Exception as e:
            self.log(f"❌ AI improvement failed: {e}")
            return False
    
    def execute_cycle(self):
        """Execute one complete cycle"""
        self.cycles_completed += 1
        cycle_start = datetime.now()
        
        self.log(f"🔄 CYCLE #{self.cycles_completed} STARTING")
        self.log("="*60)
        
        # Task 1: Ensure services are running
        self.log("📋 Task 1: Service Management")
        if not self.start_backend():
            self.log("⚠️ Backend issues, continuing...")
        if not self.start_frontend():
            self.log("⚠️ Frontend issues, continuing...")
        
        # Task 2: Check health
        self.log("📋 Task 2: Health Check")
        services_status = self.check_services()
        health_score = sum(services_status.values()) * 50  # 0-100 scale
        
        self.update_health({
            'overall_health': 'operational' if health_score > 50 else 'degraded',
            'health_score': health_score,
            'services': services_status,
            'uptime': str(datetime.now() - self.start_time)
        })
        
        # Task 3: Generate AI improvement
        self.log("📋 Task 3: AI Improvement")
        self.generate_ai_improvement()
        
        # Task 4: Deploy if needed
        self.log("📋 Task 4: Deployment")
        if self.cycles_completed % 3 == 0:  # Deploy every 3 cycles
            self.deploy_to_render()
        
        # Update status
        self.update_status({
            'system_status': 'running',
            'deployment_phase': 'continuous_improvement',
            'services_running': services_status,
            'health_score': health_score,
            'next_action': 'next_cycle'
        })
        
        cycle_duration = datetime.now() - cycle_start
        remaining_time = self.end_time - datetime.now()
        
        self.log(f"✅ CYCLE #{self.cycles_completed} COMPLETE")
        self.log(f"⏱️ Duration: {cycle_duration}")
        self.log(f"🕐 Remaining: {remaining_time}")
        self.log("="*60)
    
    def cleanup(self):
        """Cleanup processes before exit"""
        self.log("🧹 Cleaning up processes...")
        
        for service_name, process in self.services.items():
            if process and process.poll() is None:
                self.log(f"🛑 Stopping {service_name}...")
                process.terminate()
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    process.kill()
        
        self.update_status({
            'system_status': 'completed',
            'end_timestamp': datetime.now().isoformat(),
            'total_cycles': self.cycles_completed
        })
        
        self.log("✅ Cleanup complete")
    
    def run(self):
        """Main execution loop"""
        try:
            # Setup signal handlers
            signal.signal(signal.SIGINT, lambda s, f: setattr(self, 'running', False))
            signal.signal(signal.SIGTERM, lambda s, f: setattr(self, 'running', False))
            
            while self.running and datetime.now() < self.end_time:
                self.execute_cycle()
                
                # Wait 5 minutes between cycles
                next_cycle = datetime.now() + timedelta(minutes=5)
                while datetime.now() < next_cycle and self.running:
                    time.sleep(30)  # Check every 30 seconds
                    
                    if datetime.now() >= self.end_time:
                        break
            
            self.log("🎉 AUTONOMOUS EXECUTION COMPLETE!")
            self.log(f"📊 Total cycles completed: {self.cycles_completed}")
            
        except KeyboardInterrupt:
            self.log("⚠️ Interrupted by user")
        except Exception as e:
            self.log(f"❌ Execution error: {e}")
        finally:
            self.cleanup()

if __name__ == "__main__":
    # Ensure logs directory exists
    os.makedirs("/Users/maxwoldenberg/Desktop/pon/logs", exist_ok=True)
    
    executor = AutonomousExecutor()
    executor.run()
