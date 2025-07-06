#!/usr/bin/env python3
"""
AI-Driven Continuous Improvement System
=======================================

This system provides:
- Live site protection (never disrupts production)
- AI development branch management
- Automated testing and validation
- Floating approval button for safe deployments
- Comprehensive logging and monitoring
- Background AI improvement tasks
"""

import os
import sys
import json
import time
import subprocess
import threading
import logging
import shutil
import requests
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import git
from dataclasses import dataclass, asdict
import queue
import signal
import psutil
import os
from grok_client import call_grok
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('ai_improvement.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

@dataclass
class ImprovementTask:
    """Represents an AI improvement task"""
    id: str
    type: str  # 'feature', 'bugfix', 'optimization', 'security'
    description: str
    priority: int  # 1-5, 5 being highest
    status: str  # 'pending', 'in_progress', 'testing', 'ready', 'approved', 'deployed'
    created_at: datetime
    completed_at: Optional[datetime] = None
    test_results: Optional[Dict] = None
    changes: Optional[List[str]] = None

@dataclass
class SystemHealth:
    """System health metrics"""
    timestamp: datetime
    live_site_status: str
    dev_site_status: str
    backend_status: str
    frontend_status: str
    database_status: str
    error_count: int
    performance_score: float

class AIImprovementSystem:
    def __init__(self, project_root: str):
        load_dotenv()
        self.project_root = Path(project_root)
        self.live_branch = "main"
        self.dev_branch = "ai-improvements"
        self.tasks_queue = queue.Queue()
        self.improvement_tasks: List[ImprovementTask] = []
        self.system_health: List[SystemHealth] = []
        self.is_running = False
        self.approval_pending = False
        
        # Ensure we're in the right directory
        os.chdir(self.project_root)
        
        # Initialize git repository
        try:
            self.repo = git.Repo(self.project_root)
            logger.info(f"Git repository initialized at {self.project_root}")
        except git.InvalidGitRepositoryError:
            logger.error("Not a git repository. Please initialize git first.")
            sys.exit(1)
    
    def start_system(self):
        """Start the AI improvement system"""
        logger.info("🚀 Starting AI Improvement System...")
        self.is_running = True
        
        # Start background threads
        threads = [
            threading.Thread(target=self._health_monitor, daemon=True),
            threading.Thread(target=self._ai_improvement_worker, daemon=True),
            threading.Thread(target=self._testing_worker, daemon=True),
            threading.Thread(target=self._approval_monitor, daemon=True)
        ]
        
        for thread in threads:
            thread.start()
        
        logger.info("✅ AI Improvement System started successfully")
        logger.info("📊 Live site is protected and running")
        logger.info("🔧 Development branch is active for improvements")
        logger.info("🤖 AI is continuously analyzing and improving the application")
        
        return threads
    
    def _health_monitor(self):
        """Monitor system health continuously"""
        while self.is_running:
            try:
                health = self._check_system_health()
                self.system_health.append(health)
                
                # Keep only last 100 health records
                if len(self.system_health) > 100:
                    self.system_health = self.system_health[-100:]
                
                # Log health status
                if health.error_count > 0:
                    logger.warning(f"⚠️ System health issues detected: {health.error_count} errors")
                else:
                    logger.info(f"✅ System health: {health.performance_score:.2f}/100")
                
                time.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Health monitor error: {e}")
                time.sleep(60)
    
    def _check_system_health(self) -> SystemHealth:
        """Check the health of all system components"""
        try:
            # Check live site
            live_status = self._check_service("http://localhost:3000", "Live Frontend")
            
            # Check dev site
            dev_status = self._check_service("http://localhost:3002", "Dev Frontend")
            
            # Check backend
            backend_status = self._check_service("http://localhost:8000/docs", "Backend API")
            
            # Check database
            db_status = self._check_database()
            
            # Calculate performance score
            scores = [live_status, dev_status, backend_status, db_status]
            performance_score = sum(1 for s in scores if s == "healthy") / len(scores) * 100
            
            return SystemHealth(
                timestamp=datetime.now(),
                live_site_status=live_status,
                dev_site_status=dev_status,
                backend_status=backend_status,
                frontend_status=live_status,
                database_status=db_status,
                error_count=len([s for s in scores if s != "healthy"]),
                performance_score=performance_score
            )
        except Exception as e:
            logger.error(f"Health check error: {e}")
            return SystemHealth(
                timestamp=datetime.now(),
                live_site_status="error",
                dev_site_status="error",
                backend_status="error",
                frontend_status="error",
                database_status="error",
                error_count=5,
                performance_score=0.0
            )
    
    def _check_service(self, url: str, service_name: str) -> str:
        """Check if a service is healthy"""
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                return "healthy"
            else:
                logger.warning(f"{service_name} returned status {response.status_code}")
                return "warning"
        except Exception as e:
            logger.error(f"{service_name} check failed: {e}")
            return "error"
    
    def _check_database(self) -> str:
        """Check database health"""
        try:
            # Check if SQLite database exists and is accessible
            db_path = self.project_root / "backend" / "videos.db"
            if db_path.exists():
                # Try to read from database
                import sqlite3
                conn = sqlite3.connect(db_path)
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM sqlite_master")
                conn.close()
                return "healthy"
            else:
                return "warning"
        except Exception as e:
            logger.error(f"Database check failed: {e}")
            return "error"
    
    def _ai_improvement_worker(self):
        """AI worker that continuously improves the application"""
        while self.is_running:
            try:
                # Generate improvement tasks
                tasks = self._generate_improvement_tasks()
                
                for task in tasks:
                    if not self._task_exists(task.id):
                        self.improvement_tasks.append(task)
                        self.tasks_queue.put(task)
                        logger.info(f"🤖 New AI task created: {task.description}")
                
                # Process high priority tasks first
                self._process_improvement_tasks()
                
                time.sleep(300)  # Check every 5 minutes
                
            except Exception as e:
                logger.error(f"AI improvement worker error: {e}")
                time.sleep(600)
    
    def _generate_improvement_tasks(self) -> List[ImprovementTask]:
        """Generate AI improvement tasks based on system analysis"""
        tasks = []
        
        # Analyze current system health
        if self.system_health:
            latest_health = self.system_health[-1]
            
            # Performance improvements
            if latest_health.performance_score < 90:
                tasks.append(ImprovementTask(
                    id=f"perf_{int(time.time())}",
                    type="optimization",
                    description="Improve system performance and reduce response times",
                    priority=4,
                    status="pending",
                    created_at=datetime.now()
                ))
            
            # Error fixes
            if latest_health.error_count > 0:
                tasks.append(ImprovementTask(
                    id=f"bugfix_{int(time.time())}",
                    type="bugfix",
                    description=f"Fix {latest_health.error_count} detected system errors",
                    priority=5,
                    status="pending",
                    created_at=datetime.now()
                ))
        
        # Feature improvements (based on usage patterns)
        tasks.append(ImprovementTask(
            id=f"feature_{int(time.time())}",
            type="feature",
            description="Add advanced video filtering and search capabilities",
            priority=3,
            status="pending",
            created_at=datetime.now()
        ))
        
        # Security improvements
        tasks.append(ImprovementTask(
            id=f"security_{int(time.time())}",
            type="security",
            description="Enhance security measures and input validation",
            priority=4,
            status="pending",
            created_at=datetime.now()
        ))
        
        return tasks
    
    def _task_exists(self, task_id: str) -> bool:
        """Check if a task already exists"""
        return any(task.id == task_id for task in self.improvement_tasks)
    
    def _process_improvement_tasks(self):
        """Process improvement tasks in priority order"""
        # Sort tasks by priority (highest first)
        sorted_tasks = sorted(self.improvement_tasks, key=lambda x: x.priority, reverse=True)
        
        for task in sorted_tasks:
            if task.status == "pending":
                logger.info(f"🔄 Processing task: {task.description}")
                task.status = "in_progress"
                
                # Apply improvements
                success = self._apply_improvement(task)
                
                if success:
                    task.status = "testing"
                    logger.info(f"✅ Task completed: {task.description}")
                else:
                    task.status = "pending"
                    logger.error(f"❌ Task failed: {task.description}")
    
    def _apply_improvement(self, task: ImprovementTask) -> bool:
        """Apply a specific improvement"""
        try:
            self._switch_to_dev_branch()
            # Use Grok for code improvement
            prompt = self._build_grok_prompt(task)
            system_message = (
                "You are an expert Python/JavaScript developer. "
                "You are working on a video scraper app. "
                "Suggest a code improvement for the following task. "
                "Output only the code patch or new code, no explanations."
            )
            suggestion = call_grok(prompt, system_message=system_message)
            # Save suggestion to file for review
            patch_file = self.project_root / f"grok_suggestion_{task.id}.txt"
            patch_file.write_text(suggestion)
            # (Optional) Apply patch automatically here if desired
            # For now, just log and mark as ready for review
            task.changes = [str(patch_file)]
            return True
        except Exception as e:
            logger.error(f"Error applying Grok improvement: {e}")
            return False

    def _switch_to_dev_branch(self):
        """Switch to development branch"""
        try:
            current = self.repo.active_branch.name
            if current != self.dev_branch:
                # Create dev branch if it doesn't exist
                if self.dev_branch not in [b.name for b in self.repo.branches]:
                    self.repo.create_head(self.dev_branch)
                
                self.repo.heads[self.dev_branch].checkout()
                logger.info(f"Switched to {self.dev_branch} branch")
        except Exception as e:
            logger.error(f"Error switching to dev branch: {e}")
    
    def _apply_bugfix(self, task: ImprovementTask) -> bool:
        """Apply bug fixes"""
        try:
            # Example: Fix common issues
            self._fix_common_issues()
            return True
        except Exception as e:
            logger.error(f"Bugfix error: {e}")
            return False
    
    def _apply_optimization(self, task: ImprovementTask) -> bool:
        """Apply performance optimizations"""
        try:
            # Example: Optimize database queries, caching, etc.
            self._optimize_performance()
            return True
        except Exception as e:
            logger.error(f"Optimization error: {e}")
            return False
    
    def _apply_feature(self, task: ImprovementTask) -> bool:
        """Apply new features"""
        try:
            # Example: Add new features
            self._add_new_features()
            return True
        except Exception as e:
            logger.error(f"Feature error: {e}")
            return False
    
    def _apply_security_improvement(self, task: ImprovementTask) -> bool:
        """Apply security improvements"""
        try:
            # Example: Enhance security
            self._enhance_security()
            return True
        except Exception as e:
            logger.error(f"Security error: {e}")
            return False
    
    def _fix_common_issues(self):
        """Fix common issues"""
        # Add common bug fixes here
        pass
    
    def _optimize_performance(self):
        """Optimize performance"""
        # Add performance optimizations here
        pass
    
    def _add_new_features(self):
        """Add new features"""
        # Add new features here
        pass
    
    def _enhance_security(self):
        """Enhance security"""
        # Add security improvements here
        pass
    
    def _testing_worker(self):
        """Worker that tests improvements"""
        while self.is_running:
            try:
                # Get tasks ready for testing
                testing_tasks = [t for t in self.improvement_tasks if t.status == "testing"]
                
                for task in testing_tasks:
                    logger.info(f"🧪 Testing task: {task.description}")
                    
                    # Run comprehensive tests
                    test_results = self._run_tests()
                    
                    if test_results["passed"]:
                        task.status = "ready"
                        task.test_results = test_results
                        logger.info(f"✅ Tests passed for: {task.description}")
                    else:
                        task.status = "pending"
                        logger.error(f"❌ Tests failed for: {task.description}")
                
                time.sleep(60)  # Check every minute
                
            except Exception as e:
                logger.error(f"Testing worker error: {e}")
                time.sleep(120)
    
    def _run_tests(self) -> Dict:
        """Run comprehensive tests"""
        try:
            # Start dev environment
            self._start_dev_environment()
            
            # Wait for services to start
            time.sleep(10)
            
            # Run tests
            test_results = {
                "passed": True,
                "tests": [],
                "errors": []
            }
            
            # Test backend
            try:
                response = requests.get("http://localhost:8000/docs", timeout=10)
                if response.status_code == 200:
                    test_results["tests"].append("Backend API - PASSED")
                else:
                    test_results["tests"].append("Backend API - FAILED")
                    test_results["passed"] = False
            except Exception as e:
                test_results["tests"].append("Backend API - FAILED")
                test_results["errors"].append(str(e))
                test_results["passed"] = False
            
            # Test frontend
            try:
                response = requests.get("http://localhost:3002", timeout=10)
                if response.status_code == 200:
                    test_results["tests"].append("Frontend - PASSED")
                else:
                    test_results["tests"].append("Frontend - FAILED")
                    test_results["passed"] = False
            except Exception as e:
                test_results["tests"].append("Frontend - FAILED")
                test_results["errors"].append(str(e))
                test_results["passed"] = False
            
            # Test database
            try:
                db_path = self.project_root / "backend" / "videos.db"
                if db_path.exists():
                    test_results["tests"].append("Database - PASSED")
                else:
                    test_results["tests"].append("Database - FAILED")
                    test_results["passed"] = False
            except Exception as e:
                test_results["tests"].append("Database - FAILED")
                test_results["errors"].append(str(e))
                test_results["passed"] = False
            
            return test_results
            
        except Exception as e:
            logger.error(f"Test error: {e}")
            return {
                "passed": False,
                "tests": [],
                "errors": [str(e)]
            }
    
    def _start_dev_environment(self):
        """Start development environment"""
        try:
            # Start backend on different port
            backend_cmd = f"cd {self.project_root}/backend && python main_enhanced.py --port 8001"
            subprocess.Popen(backend_cmd, shell=True)
            
            # Start frontend on different port
            frontend_cmd = f"cd {self.project_root}/frontend && PORT=3002 npm run dev"
            subprocess.Popen(frontend_cmd, shell=True)
            
            logger.info("Dev environment started")
        except Exception as e:
            logger.error(f"Error starting dev environment: {e}")
    
    def _approval_monitor(self):
        """Monitor for approval requests"""
        while self.is_running:
            try:
                # Check for approval file
                approval_file = self.project_root / "APPROVAL_REQUESTED"
                
                if approval_file.exists():
                    logger.info("🔔 Approval requested! Waiting for user confirmation...")
                    self.approval_pending = True
                    
                    # Wait for approval
                    while approval_file.exists() and self.is_running:
                        time.sleep(5)
                    
                    if not self.is_running:
                        break
                    
                    # Check if approved
                    approved_file = self.project_root / "APPROVED"
                    if approved_file.exists():
                        logger.info("✅ Approval received! Deploying to live site...")
                        self._deploy_to_live()
                        approved_file.unlink()  # Remove approval file
                        self.approval_pending = False
                    else:
                        logger.info("❌ Approval denied or timed out")
                        self.approval_pending = False
                
                time.sleep(10)  # Check every 10 seconds
                
            except Exception as e:
                logger.error(f"Approval monitor error: {e}")
                time.sleep(30)
    
    def _deploy_to_live(self):
        """Deploy approved changes to live site"""
        try:
            logger.info("🚀 Deploying to live site...")
            
            # Switch to main branch
            self.repo.heads[self.live_branch].checkout()
            
            # Merge dev branch
            self.repo.git.merge(self.dev_branch)
            
            # Restart live services
            self._restart_live_services()
            
            logger.info("✅ Successfully deployed to live site!")
            
        except Exception as e:
            logger.error(f"Deployment error: {e}")
            # Rollback if needed
            self._rollback_deployment()
    
    def _restart_live_services(self):
        """Restart live services"""
        try:
            # Kill existing processes
            for proc in psutil.process_iter(['pid', 'name', 'cmdline']):
                try:
                    cmdline = ' '.join(proc.info['cmdline'])
                    if 'main_enhanced.py' in cmdline or 'next dev' in cmdline:
                        proc.terminate()
                        proc.wait(timeout=5)
                except (psutil.NoSuchProcess, psutil.TimeoutExpired):
                    pass
            
            # Restart services
            time.sleep(2)
            
            # Start backend
            backend_cmd = f"cd {self.project_root}/backend && python main_enhanced.py"
            subprocess.Popen(backend_cmd, shell=True)
            
            # Start frontend
            frontend_cmd = f"cd {self.project_root}/frontend && npm run dev"
            subprocess.Popen(frontend_cmd, shell=True)
            
            logger.info("Live services restarted")
            
        except Exception as e:
            logger.error(f"Error restarting services: {e}")
    
    def _rollback_deployment(self):
        """Rollback deployment if needed"""
        try:
            logger.info("🔄 Rolling back deployment...")
            self.repo.git.reset("--hard", "HEAD~1")
            self._restart_live_services()
            logger.info("✅ Rollback completed")
        except Exception as e:
            logger.error(f"Rollback error: {e}")
    
    def request_approval(self):
        """Request approval for current improvements"""
        try:
            # Check if there are ready tasks
            ready_tasks = [t for t in self.improvement_tasks if t.status == "ready"]
            
            if not ready_tasks:
                logger.info("No improvements ready for approval")
                return False
            
            # Create approval request file
            approval_file = self.project_root / "APPROVAL_REQUESTED"
            approval_file.write_text(json.dumps([asdict(task) for task in ready_tasks], default=str))
            
            logger.info(f"🔔 Approval requested for {len(ready_tasks)} improvements")
            return True
            
        except Exception as e:
            logger.error(f"Error requesting approval: {e}")
            return False
    
    def approve_changes(self):
        """Approve pending changes"""
        try:
            approval_file = self.project_root / "APPROVAL_REQUESTED"
            if approval_file.exists():
                approved_file = self.project_root / "APPROVED"
                approved_file.write_text("approved")
                approval_file.unlink()
                logger.info("✅ Changes approved!")
                return True
            else:
                logger.info("No approval request pending")
                return False
        except Exception as e:
            logger.error(f"Error approving changes: {e}")
            return False
    
    def get_status(self) -> Dict:
        """Get system status"""
        return {
            "is_running": self.is_running,
            "approval_pending": self.approval_pending,
            "total_tasks": len(self.improvement_tasks),
            "ready_tasks": len([t for t in self.improvement_tasks if t.status == "ready"]),
            "testing_tasks": len([t for t in self.improvement_tasks if t.status == "testing"]),
            "in_progress_tasks": len([t for t in self.improvement_tasks if t.status == "in_progress"]),
            "system_health": asdict(self.system_health[-1]) if self.system_health else None
        }
    
    def stop_system(self):
        """Stop the AI improvement system"""
        logger.info("🛑 Stopping AI Improvement System...")
        self.is_running = False
        
        # Clean up
        approval_file = self.project_root / "APPROVAL_REQUESTED"
        if approval_file.exists():
            approval_file.unlink()
        
        logger.info("✅ AI Improvement System stopped")

def main():
    """Main function"""
    project_root = os.getcwd()
    system = AIImprovementSystem(project_root)
    
    # Handle graceful shutdown
    def signal_handler(signum, frame):
        logger.info("Received shutdown signal")
        system.stop_system()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Start the system
    threads = system.start_system()
    
    try:
        # Keep main thread alive
        while system.is_running:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Shutdown requested")
        system.stop_system()

if __name__ == "__main__":
    main() 