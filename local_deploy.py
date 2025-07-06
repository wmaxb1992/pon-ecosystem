#!/usr/bin/env python3
"""
Local Deployment with Online Access
===================================
Deploy PON ecosystem locally with options for online accessibility
"""

import subprocess
import time
import os
import requests
import json
from pathlib import Path

class LocalDeployer:
    def __init__(self):
        self.base_dir = Path("/Users/maxwoldenberg/Desktop/pon")
        self.backend_dir = self.base_dir / "backend"
        self.frontend_dir = self.base_dir / "frontend"
        
    def check_requirements(self):
        """Check if all requirements are met"""
        print("🔍 Checking requirements...")
        
        # Check Python
        try:
            result = subprocess.run(['python3', '--version'], capture_output=True, text=True)
            print(f"✅ Python: {result.stdout.strip()}")
        except:
            print("❌ Python3 not found")
            return False
            
        # Check Node.js
        try:
            result = subprocess.run(['node', '--version'], capture_output=True, text=True)
            print(f"✅ Node.js: {result.stdout.strip()}")
        except:
            print("❌ Node.js not found")
            return False
            
        return True
        
    def install_dependencies(self):
        """Install all dependencies"""
        print("\n📦 Installing dependencies...")
        
        # Backend dependencies
        print("🐍 Installing Python dependencies...")
        subprocess.run(['pip3', 'install', '-r', 'requirements.txt'], 
                      cwd=self.backend_dir, check=True)
        
        # Frontend dependencies
        print("📱 Installing Node.js dependencies...")
        subprocess.run(['npm', 'install'], cwd=self.frontend_dir, check=True)
        
    def start_backend(self):
        """Start the backend server"""
        print("\n🚀 Starting backend server...")
        
        # Start backend on port 8000
        backend_process = subprocess.Popen(
            ['python3', '-m', 'uvicorn', 'main:app', '--host', '0.0.0.0', '--port', '8000', '--reload'],
            cwd=self.backend_dir
        )
        
        # Wait for backend to start
        time.sleep(3)
        
        # Check if backend is running
        try:
            response = requests.get('http://localhost:8000', timeout=5)
            print("✅ Backend started successfully!")
            return backend_process
        except:
            print("❌ Backend failed to start")
            return None
            
    def start_frontend(self):
        """Start the frontend server"""
        print("\n🌐 Starting frontend server...")
        
        # Build frontend first
        print("🔨 Building frontend...")
        subprocess.run(['npm', 'run', 'build'], cwd=self.frontend_dir, check=True)
        
        # Start frontend on port 3000
        frontend_process = subprocess.Popen(
            ['npm', 'start'],
            cwd=self.frontend_dir
        )
        
        # Wait for frontend to start
        time.sleep(5)
        
        # Check if frontend is running
        try:
            response = requests.get('http://localhost:3000', timeout=5)
            print("✅ Frontend started successfully!")
            return frontend_process
        except:
            print("❌ Frontend failed to start")
            return None
            
    def setup_online_access(self):
        """Setup online access using ngrok or similar"""
        print("\n🌍 Setting up online access...")
        
        # Check if ngrok is installed
        try:
            subprocess.run(['which', 'ngrok'], check=True, capture_output=True)
            print("✅ ngrok found")
            
            # Start ngrok for backend
            print("🔗 Creating public URL for backend...")
            backend_tunnel = subprocess.Popen(['ngrok', 'http', '8000', '--log=stdout'])
            time.sleep(3)
            
            # Start ngrok for frontend
            print("🔗 Creating public URL for frontend...")
            frontend_tunnel = subprocess.Popen(['ngrok', 'http', '3000', '--log=stdout'])
            time.sleep(3)
            
            print("✅ Online access configured!")
            print("📋 Check ngrok dashboard at: http://localhost:4040")
            
            return backend_tunnel, frontend_tunnel
            
        except subprocess.CalledProcessError:
            print("⚠️ ngrok not found. Install with: brew install ngrok")
            print("💡 Alternative: Your app is still accessible locally at:")
            print("   - Backend: http://localhost:8000")
            print("   - Frontend: http://localhost:3000")
            return None, None
            
    def deploy_local(self, online=False):
        """Deploy the entire ecosystem locally"""
        print("🚀 Starting PON Ecosystem Local Deployment")
        print("=" * 50)
        
        if not self.check_requirements():
            print("❌ Requirements not met. Please install missing dependencies.")
            return False
            
        try:
            # Install dependencies
            self.install_dependencies()
            
            # Start services
            backend_process = self.start_backend()
            if not backend_process:
                return False
                
            frontend_process = self.start_frontend()
            if not frontend_process:
                backend_process.terminate()
                return False
                
            # Setup online access if requested
            if online:
                backend_tunnel, frontend_tunnel = self.setup_online_access()
            else:
                backend_tunnel = frontend_tunnel = None
                
            print("\n🎉 PON Ecosystem deployed successfully!")
            print("=" * 50)
            print("📍 Local Access:")
            print("   - Backend API: http://localhost:8000")
            print("   - Frontend App: http://localhost:3000")
            
            if online and backend_tunnel:
                print("🌍 Online Access:")
                print("   - Check ngrok dashboard: http://localhost:4040")
                
            print("\n⚡ Services running...")
            print("   Press Ctrl+C to stop all services")
            
            # Keep running until interrupted
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\n🛑 Stopping services...")
                backend_process.terminate()
                frontend_process.terminate()
                if backend_tunnel:
                    backend_tunnel.terminate()
                if frontend_tunnel:
                    frontend_tunnel.terminate()
                print("✅ All services stopped")
                
            return True
            
        except Exception as e:
            print(f"❌ Deployment failed: {e}")
            return False

def main():
    deployer = LocalDeployer()
    
    print("🎯 PON Ecosystem Local Deployment Options:")
    print("1. Local only (localhost access)")
    print("2. Local + Online (public URLs via ngrok)")
    
    choice = input("\nChoose option (1 or 2): ").strip()
    
    if choice == "2":
        online = True
        print("🌍 Deploying with online access...")
    else:
        online = False
        print("🏠 Deploying locally only...")
        
    success = deployer.deploy_local(online=online)
    
    if success:
        print("🎉 Deployment completed successfully!")
    else:
        print("❌ Deployment failed")

if __name__ == "__main__":
    main()
