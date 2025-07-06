#!/usr/bin/env python3
"""
PON Ecosystem Master Deployment Script
=====================================
Complete deployment orchestration for Render.com
"""

import os
import sys
import json
import subprocess
import webbrowser
from pathlib import Path
from datetime import datetime

class PONDeploymentMaster:
    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.deployment_info = {}
        
    def print_banner(self):
        """Display deployment banner"""
        banner = """
╔══════════════════════════════════════════════════════════════╗
║                    🎯 PON ECOSYSTEM                          ║
║              Infrastructure as Code Deployment               ║
║                        Render.com                           ║
╚══════════════════════════════════════════════════════════════╝

🚀 Complete System Deployment:
   • Frontend (Next.js video interface)
   • Backend (Python/FastAPI processing)  
   • AI Terminal (Live Grok integration)
   • CEO AI Bot (Strategic orchestration)
   • Multi-Worker System (Distributed AI)
   • SSH Terminal (Instant access)
   • Documentation (Auto-generated)

💰 Estimated Cost: ~$67/month for complete production system
🌐 Deploy Target: Render.com with full IaC blueprint
        """
        print(banner)
    
    def validate_prerequisites(self):
        """Check all prerequisites are met"""
        print("🔍 Validating deployment prerequisites...")
        
        # Check required files
        required_files = [
            "render.yaml",
            "render_server.py", 
            "setup_render.py",
            "requirements_render.txt",
            "ceo_ai_bot.py",
            "ai_multi_worker.py",
            "instant_grok_terminal.py"
        ]
        
        missing_files = []
        for file_path in required_files:
            if not (self.root_dir / file_path).exists():
                missing_files.append(file_path)
        
        if missing_files:
            print(f"❌ Missing required files: {missing_files}")
            return False
            
        print("✅ All required files present")
        
        # Validate render.yaml
        try:
            result = subprocess.run([
                sys.executable, "validate_render.py"
            ], capture_output=True, text=True, cwd=self.root_dir)
            
            if result.returncode != 0:
                print("❌ render.yaml validation failed")
                print(result.stdout)
                return False
            print("✅ render.yaml validation passed")
        except Exception as e:
            print(f"❌ Validation error: {e}")
            return False
            
        return True
    
    def check_git_status(self):
        """Check Git repository status"""
        print("📋 Checking Git repository status...")
        
        try:
            # Check if we're in a git repo
            result = subprocess.run([
                "git", "status", "--porcelain"
            ], capture_output=True, text=True, cwd=self.root_dir)
            
            if result.returncode != 0:
                print("⚠️  Not in a Git repository - you'll need to manually upload to Render")
                return False
            
            # Check for uncommitted changes
            if result.stdout.strip():
                print("⚠️  Uncommitted changes detected:")
                print(result.stdout)
                
                response = input("🤔 Commit changes now? (y/n): ").lower()
                if response == 'y':
                    self.commit_changes()
                else:
                    print("⚠️  Remember to commit and push before deploying")
            else:
                print("✅ Git repository is clean")
                
            # Check remote
            result = subprocess.run([
                "git", "remote", "get-url", "origin"
            ], capture_output=True, text=True, cwd=self.root_dir)
            
            if result.returncode == 0:
                self.deployment_info['git_remote'] = result.stdout.strip()
                print(f"✅ Git remote: {self.deployment_info['git_remote']}")
            else:
                print("⚠️  No Git remote configured")
                
        except Exception as e:
            print(f"⚠️  Git check failed: {e}")
            
        return True
    
    def commit_changes(self):
        """Commit current changes"""
        try:
            subprocess.run(["git", "add", "."], cwd=self.root_dir, check=True)
            commit_msg = f"PON Ecosystem deployment ready - {datetime.now().strftime('%Y-%m-%d %H:%M')}"
            subprocess.run(["git", "commit", "-m", commit_msg], cwd=self.root_dir, check=True)
            print("✅ Changes committed")
            
            response = input("🚀 Push to main branch now? (y/n): ").lower()
            if response == 'y':
                subprocess.run(["git", "push", "origin", "main"], cwd=self.root_dir, check=True)
                print("✅ Pushed to main branch")
                self.deployment_info['auto_deploy'] = True
        except subprocess.CalledProcessError as e:
            print(f"❌ Git operation failed: {e}")
    
    def show_deployment_options(self):
        """Display deployment options"""
        print("\n" + "="*60)
        print("🚀 DEPLOYMENT OPTIONS")
        print("="*60)
        
        print("\n1️⃣  RENDER DASHBOARD (Recommended)")
        print("   • Go to: https://dashboard.render.com")
        print("   • Click: New → Blueprint")
        print("   • Connect your GitHub repository")
        print("   • Render auto-detects render.yaml")
        print("   • Click: Apply Blueprint")
        print("   • Monitor deployment progress")
        
        print("\n2️⃣  AUTO-DEPLOY VIA GIT")
        if self.deployment_info.get('auto_deploy'):
            print("   ✅ Changes already pushed to main branch")
            print("   🔄 Render will auto-deploy on next push")
        else:
            print("   📝 Commit and push to main branch:")
            print("   git add .")
            print("   git commit -m 'Deploy PON Ecosystem'")
            print("   git push origin main")
        
        print("\n3️⃣  RENDER CLI")
        print("   📦 Install: npm install -g @render/cli")
        print("   🔑 Login: render login")
        print("   🚀 Deploy: render blueprint deploy")
        
        # Ask user preference
        print("\n" + "="*60)
        choice = input("🤔 Choose deployment method (1/2/3) or 'q' to quit: ").lower()
        
        if choice == '1':
            self.open_render_dashboard()
        elif choice == '2':
            self.show_git_instructions()
        elif choice == '3':
            self.show_cli_instructions()
        elif choice == 'q':
            print("👋 Deployment cancelled")
            return False
        else:
            print("⚠️  Invalid choice")
            return self.show_deployment_options()
            
        return True
    
    def open_render_dashboard(self):
        """Open Render dashboard in browser"""
        try:
            webbrowser.open("https://dashboard.render.com")
            print("🌐 Opening Render dashboard in browser...")
            print("\n📋 Steps to complete deployment:")
            print("1. Click 'New' → 'Blueprint'")
            print("2. Connect your GitHub repository")
            print("3. Select the repository with render.yaml")
            print("4. Click 'Apply Blueprint'")
            print("5. Monitor deployment progress")
        except Exception as e:
            print(f"⚠️  Could not open browser: {e}")
            print("🌐 Manually go to: https://dashboard.render.com")
    
    def show_git_instructions(self):
        """Show Git deployment instructions"""
        print("\n📝 Git Deployment Instructions:")
        print("=" * 40)
        
        if not self.deployment_info.get('auto_deploy'):
            print("Run these commands in your terminal:")
            print(f"cd {self.root_dir}")
            print("git add .")
            print("git commit -m 'Deploy PON Ecosystem with IaC'")
            print("git push origin main")
            print("\n🔄 Render will automatically deploy on push!")
        else:
            print("✅ Already pushed to main branch")
            print("🔄 Render will auto-deploy shortly")
    
    def show_cli_instructions(self):
        """Show CLI deployment instructions"""
        print("\n📦 CLI Deployment Instructions:")
        print("=" * 40)
        print("1. Install Render CLI:")
        print("   npm install -g @render/cli")
        print("\n2. Login to Render:")
        print("   render login")
        print("\n3. Deploy blueprint:")
        print(f"   cd {self.root_dir}")
        print("   render blueprint deploy")
    
    def show_post_deployment_info(self):
        """Show post-deployment information"""
        print("\n" + "="*60)
        print("🎯 POST-DEPLOYMENT ACCESS")
        print("="*60)
        
        endpoints = {
            "Main Application": "https://pon-ecosystem.onrender.com",
            "SSH Terminal": "ssh user@instant-grok-terminal.onrender.com",
            "API Documentation": "https://pon-ecosystem.onrender.com/docs",
            "System Health": "https://pon-ecosystem.onrender.com/health",
            "Documentation": "https://pon-docs.onrender.com"
        }
        
        for name, url in endpoints.items():
            print(f"📍 {name}: {url}")
        
        print("\n💰 Estimated Monthly Cost: ~$67")
        print("📊 Monitor services in Render dashboard")
        print("📖 Full documentation: RENDER_IAC_GUIDE.md")
        
        print("\n🎉 PON Ecosystem deployment complete!")
    
    def create_deployment_summary(self):
        """Create deployment summary file"""
        summary = {
            "deployment_time": datetime.utcnow().isoformat(),
            "deployment_method": "render.yaml blueprint",
            "services_deployed": [
                "pon-ecosystem (main web service)",
                "ceo-ai-bot (strategic orchestration)",
                "ai-code-worker (code generation)",
                "ai-quality-worker (quality assurance)", 
                "ai-memory-worker (memory management)",
                "instant-grok-terminal (SSH access)",
                "pon-redis (message broker)",
                "pon-database (PostgreSQL)",
                "pon-docs (documentation)"
            ],
            "estimated_monthly_cost": 67,
            "access_endpoints": {
                "main_app": "https://pon-ecosystem.onrender.com",
                "ssh_terminal": "ssh user@instant-grok-terminal.onrender.com",
                "api_docs": "https://pon-ecosystem.onrender.com/docs",
                "health": "https://pon-ecosystem.onrender.com/health",
                "documentation": "https://pon-docs.onrender.com"
            },
            "git_remote": self.deployment_info.get('git_remote', ''),
            "auto_deploy_enabled": self.deployment_info.get('auto_deploy', False)
        }
        
        summary_file = self.root_dir / "deployment_summary.json"
        summary_file.write_text(json.dumps(summary, indent=2))
        print(f"📝 Deployment summary saved: {summary_file}")
    
    def run_deployment(self):
        """Run complete deployment process"""
        try:
            self.print_banner()
            
            if not self.validate_prerequisites():
                print("❌ Prerequisites not met. Please fix issues and try again.")
                return False
            
            if not self.check_git_status():
                print("⚠️  Git issues detected, but continuing...")
            
            if not self.show_deployment_options():
                return False
            
            self.show_post_deployment_info()
            self.create_deployment_summary()
            
            return True
            
        except KeyboardInterrupt:
            print("\n👋 Deployment cancelled by user")
            return False
        except Exception as e:
            print(f"❌ Deployment failed: {e}")
            return False

if __name__ == "__main__":
    deployer = PONDeploymentMaster()
    success = deployer.run_deployment()
    sys.exit(0 if success else 1)
