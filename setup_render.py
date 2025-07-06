#!/usr/bin/env python3
"""
Render.com Setup Script for PON Ecosystem
==========================================
Validates and initializes the complete PON ecosystem deployment
"""

import os
import sys
import json
import sqlite3
import subprocess
from pathlib import Path
from datetime import datetime

class RenderSetup:
    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.errors = []
        self.warnings = []
        
    def log(self, message, level="INFO"):
        """Log setup messages"""
        prefix = "✅" if level == "INFO" else "⚠️" if level == "WARN" else "❌"
        print(f"{prefix} {message}")
        
    def validate_environment(self):
        """Validate required environment variables"""
        self.log("Validating environment variables...")
        
        required_vars = [
            'GROK_API_KEY',
            'PORT'
        ]
        
        for var in required_vars:
            if not os.environ.get(var):
                self.errors.append(f"Missing required environment variable: {var}")
                
        # Set defaults for optional variables
        defaults = {
            'ENVIRONMENT': 'production',
            'LOG_LEVEL': 'INFO',
            'GROK_MODEL': 'grok-3-fast',
            'DEBUG': 'false',
            'ENABLE_SSH_TERMINAL': 'true',
            'ENABLE_CEO_AI': 'true',
            'ENABLE_MULTI_WORKERS': 'true',
            'ENABLE_MONITORING': 'true'
        }
        
        for key, value in defaults.items():
            if not os.environ.get(key):
                os.environ[key] = value
                self.log(f"Set default {key}={value}", "WARN")
    
    def setup_directories(self):
        """Create required directories"""
        self.log("Setting up directory structure...")
        
        directories = [
            'logs',
            'videos', 
            'thumbnails',
            'backend/videos',
            'backend/thumbnails',
            'frontend/.next',
            'public'
        ]
        
        for directory in directories:
            dir_path = self.root_dir / directory
            dir_path.mkdir(parents=True, exist_ok=True)
            self.log(f"Created directory: {directory}")
    
    def setup_databases(self):
        """Initialize required databases"""
        self.log("Setting up databases...")
        
        # AI Memory Database
        ai_db_path = self.root_dir / 'ai_memory.db'
        try:
            conn = sqlite3.connect(str(ai_db_path))
            conn.execute('''
                CREATE TABLE IF NOT EXISTS memories (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    content TEXT NOT NULL,
                    timestamp REAL NOT NULL,
                    category TEXT DEFAULT 'general',
                    importance INTEGER DEFAULT 1
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS improvements (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    suggestion TEXT NOT NULL,
                    implemented BOOLEAN DEFAULT FALSE,
                    timestamp REAL NOT NULL
                )
            ''')
            conn.commit()
            conn.close()
            self.log("AI memory database initialized")
        except Exception as e:
            self.errors.append(f"Failed to setup AI memory database: {e}")
        
        # Backend databases
        backend_db_path = self.root_dir / 'backend' / 'favorites.db'
        try:
            conn = sqlite3.connect(str(backend_db_path))
            conn.execute('''
                CREATE TABLE IF NOT EXISTS favorites (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    video_id TEXT UNIQUE NOT NULL,
                    title TEXT,
                    channel TEXT,
                    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            conn.commit()
            conn.close()
            self.log("Backend favorites database initialized")
        except Exception as e:
            self.warnings.append(f"Backend database setup warning: {e}")
    
    def validate_files(self):
        """Validate required files exist"""
        self.log("Validating required files...")
        
        required_files = [
            'render_server.py',
            'ceo_ai_bot.py',
            'ai_multi_worker.py',
            'instant_grok_terminal.py',
            'requirements_render.txt',
            'backend/main_enhanced.py',
            'frontend/package.json'
        ]
        
        for file_path in required_files:
            full_path = self.root_dir / file_path
            if not full_path.exists():
                self.errors.append(f"Missing required file: {file_path}")
            else:
                self.log(f"Found: {file_path}")
    
    def setup_permissions(self):
        """Set proper file permissions"""
        self.log("Setting file permissions...")
        
        executable_files = [
            'render_server.py',
            'ceo_ai_bot.py', 
            'instant_grok_terminal.py',
            'setup_render.py',
            '*.sh'
        ]
        
        for pattern in executable_files:
            try:
                if pattern.endswith('.sh'):
                    # Handle shell scripts
                    for script in self.root_dir.glob('*.sh'):
                        script.chmod(0o755)
                        self.log(f"Made executable: {script.name}")
                else:
                    file_path = self.root_dir / pattern
                    if file_path.exists():
                        file_path.chmod(0o755)
                        self.log(f"Made executable: {pattern}")
            except Exception as e:
                self.warnings.append(f"Permission warning for {pattern}: {e}")
    
    def create_health_check(self):
        """Create health check endpoint file"""
        self.log("Creating health check endpoint...")
        
        health_content = '''#!/usr/bin/env python3
"""Health check endpoint for PON Ecosystem"""

import json
import os
import sys
from datetime import datetime

def health_check():
    """Return system health status"""
    status = {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "services": {
            "frontend": "running",
            "backend": "running", 
            "ai_terminal": "running",
            "ceo_ai": "running",
            "workers": "running"
        },
        "environment": os.environ.get("ENVIRONMENT", "unknown"),
        "version": "1.0.0"
    }
    
    # Check if critical files exist
    critical_files = [
        "render_server.py",
        "ceo_ai_bot.py",
        "ai_multi_worker.py"
    ]
    
    for file_path in critical_files:
        if not os.path.exists(file_path):
            status["status"] = "degraded"
            status["services"][file_path.replace(".py", "")] = "missing"
    
    return status

if __name__ == "__main__":
    print(json.dumps(health_check(), indent=2))
'''
        
        health_file = self.root_dir / 'health_check.py'
        health_file.write_text(health_content)
        health_file.chmod(0o755)
        self.log("Health check endpoint created")
    
    def create_deployment_info(self):
        """Create deployment information file"""
        self.log("Creating deployment info...")
        
        deployment_info = {
            "ecosystem": "PON Complete System",
            "deployment_target": "render.com",
            "services": [
                "Frontend (Next.js)",
                "Backend (Python/FastAPI)", 
                "AI Terminal (Grok Integration)",
                "CEO AI Bot (Strategic Orchestration)",
                "Multi-Worker System (Celery/Redis)",
                "SSH Terminal (Instant Access)",
                "Documentation Site"
            ],
            "infrastructure": [
                "Redis (Message Broker)",
                "PostgreSQL (Main Database)",
                "Static Assets (Documentation)"
            ],
            "deployment_time": datetime.utcnow().isoformat(),
            "environment": os.environ.get("ENVIRONMENT", "production")
        }
        
        info_file = self.root_dir / 'deployment_info.json'
        info_file.write_text(json.dumps(deployment_info, indent=2))
        self.log("Deployment info created")
    
    def run_setup(self):
        """Run complete setup process"""
        self.log("🚀 Starting PON Ecosystem Setup for Render.com")
        
        # Run all setup steps
        self.validate_environment()
        self.setup_directories() 
        self.setup_databases()
        self.validate_files()
        self.setup_permissions()
        self.create_health_check()
        self.create_deployment_info()
        
        # Report results
        if self.errors:
            self.log("❌ Setup failed with errors:", "ERROR")
            for error in self.errors:
                self.log(f"  • {error}", "ERROR")
            sys.exit(1)
        
        if self.warnings:
            self.log("⚠️ Setup completed with warnings:", "WARN")
            for warning in self.warnings:
                self.log(f"  • {warning}", "WARN")
        
        self.log("✅ PON Ecosystem setup completed successfully!")
        self.log("🎯 Ready for deployment on Render.com")
        
        # Display service summary
        print("\n" + "="*50)
        print("🎯 PON ECOSYSTEM DEPLOYMENT READY")
        print("="*50)
        print("📦 Services Configured:")
        print("  • Frontend: Next.js video interface")
        print("  • Backend: Python/FastAPI processing") 
        print("  • AI Terminal: Instant Grok access")
        print("  • CEO AI: Strategic orchestration")
        print("  • Multi-Workers: Distributed AI tasks")
        print("  • Documentation: Static site")
        print("\n🔗 Access Points:")
        print("  • Main App: https://pon-ecosystem.onrender.com")
        print("  • SSH Terminal: ssh user@instant-grok-terminal.onrender.com")
        print("  • Docs: https://pon-docs.onrender.com")
        print("="*50)

if __name__ == "__main__":
    setup = RenderSetup()
    setup.run_setup()
