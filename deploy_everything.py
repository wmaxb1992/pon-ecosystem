#!/usr/bin/env python3
"""
Complete PON Ecosystem Deployment
=================================
Deploys everything locally and makes it accessible online
"""

import os
import sys
import time
import subprocess
import requests
import json
from datetime import datetime
from pathlib import Path

class PONDeployer:
    def __init__(self):
        self.workspace = "/Users/maxwoldenberg/Desktop/pon"
        self.processes = {}
        self.status = {
            "backend": False,
            "frontend": False,
            "ai_systems": False,
            "tunnel": False
        }
        
    def log(self, message, level="INFO"):
        timestamp = datetime.now().strftime("%H:%M:%S")
        icon = {"INFO": "ℹ️", "SUCCESS": "✅", "ERROR": "❌", "WARN": "⚠️"}[level]
        print(f"[{timestamp}] {icon} {message}")
        
    def check_dependencies(self):
        """Check if required dependencies are installed"""
        self.log("Checking dependencies...")
        
        # Check Python packages
        required_packages = ['requests', 'fastapi', 'uvicorn']
        for package in required_packages:
            try:
                __import__(package)
                self.log(f"✓ {package} installed", "SUCCESS")
            except ImportError:
                self.log(f"Installing {package}...", "WARN")
                subprocess.run([sys.executable, '-m', 'pip', 'install', package])
        
        # Check Node.js
        try:
            result = subprocess.run(['node', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                self.log(f"✓ Node.js {result.stdout.strip()}", "SUCCESS")
            else:
                self.log("Node.js not found!", "ERROR")
                return False
        except FileNotFoundError:
            self.log("Node.js not found - please install it", "ERROR")
            return False
            
        return True
    
    def start_backend(self):
        """Start the backend API server"""
        self.log("Starting backend API...")
        
        backend_dir = os.path.join(self.workspace, "backend")
        
        # Install Python dependencies
        if os.path.exists(os.path.join(backend_dir, "requirements.txt")):
            subprocess.run([sys.executable, '-m', 'pip', 'install', '-r', 
                          os.path.join(backend_dir, "requirements.txt")])
        
        # Start backend server
        backend_process = subprocess.Popen(
            [sys.executable, '-m', 'uvicorn', 'main:app', '--host', '0.0.0.0', '--port', '8000'],
            cwd=backend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        self.processes['backend'] = backend_process
        
        # Wait for backend to start
        for i in range(30):
            try:
                response = requests.get("http://localhost:8000", timeout=2)
                if response.status_code in [200, 404]:  # 404 is OK, means server is running
                    self.status['backend'] = True
                    self.log("Backend API started successfully!", "SUCCESS")
                    return True
            except:
                time.sleep(1)
        
        self.log("Backend failed to start", "ERROR")
        return False
    
    def start_frontend(self):
        """Start the frontend server"""
        self.log("Starting frontend...")
        
        frontend_dir = os.path.join(self.workspace, "frontend")
        
        # Install Node dependencies
        self.log("Installing Node.js dependencies...")
        npm_install = subprocess.run(['npm', 'install'], cwd=frontend_dir)
        if npm_install.returncode != 0:
            self.log("Failed to install npm dependencies", "ERROR")
            return False
        
        # Start frontend server
        frontend_process = subprocess.Popen(
            ['npm', 'run', 'dev'],
            cwd=frontend_dir,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        
        self.processes['frontend'] = frontend_process
        
        # Wait for frontend to start
        for i in range(60):
            try:
                response = requests.get("http://localhost:3000", timeout=2)
                if response.status_code == 200:
                    self.status['frontend'] = True
                    self.log("Frontend started successfully!", "SUCCESS")
                    return True
            except:
                time.sleep(2)
        
        self.log("Frontend failed to start", "ERROR")
        return False
    
    def start_ai_systems(self):
        """Start AI systems"""
        self.log("Starting AI systems...")
        
        try:
            # Test AI integration
            if os.path.exists(os.path.join(self.workspace, "enhanced_grok_integration.py")):
                ai_process = subprocess.Popen(
                    [sys.executable, 'enhanced_grok_integration.py'],
                    cwd=self.workspace,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                self.processes['ai'] = ai_process
                self.status['ai_systems'] = True
                self.log("AI systems started!", "SUCCESS")
                return True
        except Exception as e:
            self.log(f"AI systems warning: {e}", "WARN")
            return True  # Continue without AI
    
    def setup_online_access(self):
        """Set up online access using ngrok or similar"""
        self.log("Setting up online access...")
        
        # Check if ngrok is installed
        try:
            result = subprocess.run(['ngrok', 'version'], capture_output=True, text=True)
            if result.returncode == 0:
                self.log("Found ngrok, setting up tunnels...", "SUCCESS")
                
                # Start ngrok for backend
                backend_tunnel = subprocess.Popen(
                    ['ngrok', 'http', '8000', '--log', 'stdout'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                
                # Start ngrok for frontend
                frontend_tunnel = subprocess.Popen(
                    ['ngrok', 'http', '3000', '--log', 'stdout'],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE
                )
                
                self.processes['backend_tunnel'] = backend_tunnel
                self.processes['frontend_tunnel'] = frontend_tunnel
                
                time.sleep(3)  # Wait for tunnels to establish
                
                # Get tunnel URLs
                try:
                    api_response = requests.get('http://localhost:4040/api/tunnels')
                    tunnels = api_response.json()['tunnels']
                    
                    for tunnel in tunnels:
                        port = tunnel['config']['addr'].split(':')[-1]
                        url = tunnel['public_url']
                        if port == '3000':
                            self.log(f"Frontend online: {url}", "SUCCESS")
                        elif port == '8000':
                            self.log(f"Backend online: {url}", "SUCCESS")
                            
                    self.status['tunnel'] = True
                    return True
                except:
                    self.log("Tunnels started but couldn't get URLs", "WARN")
                    return True
                    
        except FileNotFoundError:
            self.log("ngrok not found - install with: brew install ngrok", "WARN")
            self.log("Your apps are running locally:", "INFO")
            self.log("Frontend: http://localhost:3000", "INFO")
            self.log("Backend: http://localhost:8000", "INFO")
            return True
    
    def monitor_services(self):
        """Monitor all services"""
        self.log("Starting service monitoring...")
        
        while True:
            try:
                # Check backend
                try:
                    requests.get("http://localhost:8000", timeout=2)
                    backend_status = "✅"
                except:
                    backend_status = "❌"
                
                # Check frontend
                try:
                    requests.get("http://localhost:3000", timeout=2)
                    frontend_status = "✅"
                except:
                    frontend_status = "❌"
                
                # Check cloud services
                try:
                    cloud_response = requests.get("https://pon-ecosystem.onrender.com/health", timeout=5)
                    cloud_status = "✅" if cloud_response.status_code == 200 else "🔄"
                except:
                    cloud_status = "❌"
                
                # Status update
                print(f"\r[{datetime.now().strftime('%H:%M:%S')}] Backend: {backend_status} | Frontend: {frontend_status} | Cloud: {cloud_status}", end='', flush=True)
                
                time.sleep(10)
                
            except KeyboardInterrupt:
                self.log("\nShutting down services...", "INFO")
                self.cleanup()
                break
    
    def cleanup(self):
        """Clean up all processes"""
        for name, process in self.processes.items():
            try:
                process.terminate()
                self.log(f"Stopped {name}", "SUCCESS")
            except:
                pass
    
    def deploy_everything(self):
        """Deploy the complete PON ecosystem"""
        self.log("🚀 Starting PON Ecosystem Deployment", "SUCCESS")
        
        # Check dependencies
        if not self.check_dependencies():
            return False
        
        # Start backend
        if not self.start_backend():
            self.log("Deployment failed at backend", "ERROR")
            return False
        
        # Start frontend
        if not self.start_frontend():
            self.log("Deployment failed at frontend", "ERROR")
            return False
        
        # Start AI systems
        self.start_ai_systems()
        
        # Setup online access
        self.setup_online_access()
        
        # Display status
        self.log("🎉 PON Ecosystem deployed successfully!", "SUCCESS")
        self.log("Local URLs:", "INFO")
        self.log("  Frontend: http://localhost:3000", "INFO")
        self.log("  Backend: http://localhost:8000", "INFO")
        
        if self.status['tunnel']:
            self.log("Online access configured with ngrok!", "SUCCESS")
        
        self.log("Press Ctrl+C to stop all services", "INFO")
        
        # Start monitoring
        self.monitor_services()
        
        return True

if __name__ == "__main__":
    deployer = PONDeployer()
    deployer.deploy_everything()
