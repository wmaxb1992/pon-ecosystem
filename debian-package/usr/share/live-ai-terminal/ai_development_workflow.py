"""
AI DEVELOPMENT WORKFLOW
======================
Orchestrates the entire AI coding process with rules, memory, and thought processing.
"""

import os
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path
import subprocess
import threading

# Import AI systems
from enhanced_grok_integration import enhanced_grok
from ai_thought_processor import thought_processor, ThoughtType, Colors
from ai_memory_system import ai_memory
from ai_coding_rules import ai_rules

class AIDevelopmentWorkflow:
    def __init__(self):
        self.current_task = None
        self.task_history = []
        self.workflow_steps = []
        self.auto_commit = True
        self.auto_test = True
        self.continuous_improvement = True
        
        # Initialize workflow
        self._initialize_workflow()
    
    def _initialize_workflow(self):
        """Initialize the AI development workflow"""
        thought_processor.add_thought(
            ThoughtType.ANALYSIS,
            "Initializing AI Development Workflow with automated coding, testing, and improvement",
            {"features": ["auto_commit", "auto_test", "continuous_improvement"]},
            confidence=0.9
        )
    
    def start_development_session(self, project_path: str, task_description: str):
        """Start a new development session"""
        self.current_task = {
            "id": f"task_{int(time.time())}",
            "description": task_description,
            "project_path": project_path,
            "started_at": datetime.now(),
            "status": "in_progress",
            "steps": []
        }
        
        # Set project context
        enhanced_grok.set_project_context(project_path, "web_app")
        
        thought_processor.add_thought(
            ThoughtType.ANALYSIS,
            f"Starting development session: {task_description}",
            {"project_path": project_path, "task": task_description},
            confidence=0.8
        )
        
        print(f"{Colors.CYAN}🚀 {Colors.BOLD}AI Development Session Started{Colors.RESET}")
        print(f"{Colors.CYAN}Task: {task_description}{Colors.RESET}")
        print(f"{Colors.CYAN}Project: {project_path}{Colors.RESET}")
    
    def analyze_project_structure(self) -> Dict[str, Any]:
        """Analyze the current project structure"""
        thought_processor.add_thought(
            ThoughtType.ANALYSIS,
            "Analyzing project structure and identifying improvement opportunities",
            {"project_path": enhanced_grok.current_project["path"] if enhanced_grok.current_project else None},
            confidence=0.7
        )
        
        if not enhanced_grok.current_project:
            return {"error": "No project context set"}
        
        analysis = {
            "project_info": enhanced_grok.current_project,
            "file_analysis": [],
            "structure_violations": [],
            "improvement_opportunities": []
        }
        
        # Analyze each file
        for file_info in enhanced_grok.current_project["files"]:
            file_path = os.path.join(enhanced_grok.current_project["path"], file_info["path"])
            if os.path.exists(file_path):
                file_analysis = enhanced_grok.analyze_code_file(file_path)
                analysis["file_analysis"].append(file_analysis)
                
                # Check for violations
                if file_analysis.get("violations"):
                    analysis["structure_violations"].extend(file_analysis["violations"])
        
        # Generate improvement opportunities
        analysis["improvement_opportunities"] = self._identify_improvements(analysis)
        
        return analysis
    
    def _identify_improvements(self, analysis: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Identify improvement opportunities"""
        improvements = []
        
        # Check for missing tests
        has_python = any("python" in str(fa.get("file_type", "")).lower() for fa in analysis["file_analysis"])
        has_tests = any("test" in fa.get("file_path", "").lower() for fa in analysis["file_analysis"])
        
        if has_python and not has_tests:
            improvements.append({
                "type": "testing",
                "priority": "high",
                "description": "Add unit tests for Python code",
                "impact": "Improves code reliability and maintainability"
            })
        
        # Check for code quality issues
        total_violations = len(analysis["structure_violations"])
        if total_violations > 10:
            improvements.append({
                "type": "code_quality",
                "priority": "medium",
                "description": f"Fix {total_violations} coding rule violations",
                "impact": "Improves code consistency and maintainability"
            })
        
        # Check for performance opportunities
        high_complexity_files = [fa for fa in analysis["file_analysis"] if fa.get("complexity", 0) > 0.5]
        if high_complexity_files:
            improvements.append({
                "type": "performance",
                "priority": "medium",
                "description": f"Optimize {len(high_complexity_files)} high-complexity files",
                "impact": "Improves code performance and readability"
            })
        
        return improvements
    
    def generate_code_improvements(self, target_files: Optional[List[str]] = None) -> Dict[str, Any]:
        """Generate code improvements for the project"""
        thought_processor.add_thought(
            ThoughtType.OPTIMIZATION,
            "Generating code improvements based on AI analysis",
            {"target_files": target_files},
            confidence=0.8
        )
        
        improvements = {
            "generated_files": [],
            "optimized_files": [],
            "new_patterns": [],
            "decisions_made": []
        }
        
        # Get project analysis
        analysis = self.analyze_project_structure()
        
        # Generate improvements for each opportunity
        for opportunity in analysis.get("improvement_opportunities", []):
            if opportunity["type"] == "testing":
                test_files = self._generate_test_files(analysis["file_analysis"])
                improvements["generated_files"].extend(test_files)
            
            elif opportunity["type"] == "code_quality":
                optimized_files = self._fix_code_quality_issues(analysis["structure_violations"])
                improvements["optimized_files"].extend(optimized_files)
            
            elif opportunity["type"] == "performance":
                performance_improvements = self._optimize_performance(analysis["file_analysis"])
                improvements["optimized_files"].extend(performance_improvements)
        
        # Store new patterns and decisions
        if improvements["generated_files"] or improvements["optimized_files"]:
            self._store_improvement_patterns(improvements)
        
        return improvements
    
    def _generate_test_files(self, file_analysis: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate test files for the project"""
        test_files = []
        
        for analysis in file_analysis:
            if "python" in str(analysis.get("file_type", "")).lower():
                test_file = self._generate_python_test(analysis)
                if test_file:
                    test_files.append(test_file)
        
        return test_files
    
    def _generate_python_test(self, file_analysis: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Generate a Python test file"""
        file_path = file_analysis.get("file_path", "")
        if not file_path:
            return None
        
        # Extract functions and classes
        functions = file_analysis.get("functions", [])
        classes = file_analysis.get("classes", [])
        
        if not functions and not classes:
            return None
        
        # Generate test content
        test_content = f'''"""
Tests for {file_path}
Generated by AI Development Workflow
"""

import unittest
from unittest.mock import Mock, patch
import sys
import os

# Add the project root to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import the module to test
import {Path(file_path).stem}

class Test{Path(file_path).stem.title()}(unittest.TestCase):
    """Test cases for {Path(file_path).stem} module"""
    
    def setUp(self):
        """Set up test fixtures"""
        pass
    
    def tearDown(self):
        """Clean up after tests"""
        pass
'''
        
        # Add test methods for functions
        for func in functions:
            test_content += f'''
    def test_{func}(self):
        """Test {func} function"""
        # TODO: Implement test for {func}
        self.skipTest("Test not implemented yet")
'''
        
        # Add test methods for classes
        for cls in classes:
            test_content += f'''
    def test_{cls}_creation(self):
        """Test {cls} class creation"""
        # TODO: Implement test for {cls}
        self.skipTest("Test not implemented yet")
'''
        
        test_content += '''

if __name__ == '__main__':
    unittest.main()
'''
        
        # Create test file path
        test_file_path = file_path.replace('.py', '_test.py')
        test_file_path = test_file_path.replace('/', '/tests/')
        
        return {
            "file_path": test_file_path,
            "content": test_content,
            "type": "test_file",
            "original_file": file_path
        }
    
    def _fix_code_quality_issues(self, violations: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Fix code quality issues"""
        fixed_files = []
        
        for violation in violations:
            # This would require more sophisticated code analysis
            # For now, we'll create a report
            fixed_files.append({
                "file_path": violation.get("file_path", "unknown"),
                "issue": violation.get("violation", "unknown"),
                "fix": violation.get("suggestion", "manual fix required"),
                "type": "quality_fix"
            })
        
        return fixed_files
    
    def _optimize_performance(self, file_analysis: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Optimize performance of files"""
        optimizations = []
        
        for analysis in file_analysis:
            if analysis.get("complexity", 0) > 0.5:
                optimization = enhanced_grok.optimize_code(analysis.get("file_path", ""))
                if "error" not in optimization:
                    optimizations.append(optimization)
        
        return optimizations
    
    def _store_improvement_patterns(self, improvements: Dict[str, Any]):
        """Store improvement patterns in memory"""
        # Store generated files as patterns
        for file_info in improvements.get("generated_files", []):
            pattern = {
                "pattern_id": f"gen_{int(time.time())}",
                "pattern_type": "generated_file",
                "language": "python",
                "content": file_info.get("content", ""),
                "context": {"original_file": file_info.get("original_file", "")},
                "usage_count": 1,
                "success_rate": 0.8,
                "last_used": datetime.now(),
                "created_at": datetime.now(),
                "tags": ["generated", "test", "ai_workflow"],
                "complexity_score": 0.3,
                "performance_score": 0.8
            }
            
            # This would be stored in the memory system
            # ai_memory.add_code_pattern(pattern)
    
    def run_automated_tests(self) -> Dict[str, Any]:
        """Run automated tests for the project"""
        thought_processor.add_thought(
            ThoughtType.VALIDATION,
            "Running automated tests to validate code quality",
            {"auto_test": self.auto_test},
            confidence=0.7
        )
        
        if not self.auto_test:
            return {"status": "disabled"}
        
        test_results = {
            "total_tests": 0,
            "passed_tests": 0,
            "failed_tests": 0,
            "test_files": [],
            "coverage": 0.0
        }
        
        # Find test files
        project_path = enhanced_grok.current_project["path"] if enhanced_grok.current_project else None
        if not project_path:
            return {"error": "No project path"}
        
        test_files = []
        for root, dirs, files in os.walk(project_path):
            for file in files:
                if file.endswith('_test.py') or file.startswith('test_'):
                    test_files.append(os.path.join(root, file))
        
        # Run tests
        for test_file in test_files:
            try:
                result = subprocess.run(
                    ['python', '-m', 'pytest', test_file, '-v'],
                    capture_output=True,
                    text=True,
                    cwd=project_path
                )
                
                test_results["test_files"].append({
                    "file": test_file,
                    "output": result.stdout,
                    "error": result.stderr,
                    "return_code": result.returncode
                })
                
                if result.returncode == 0:
                    test_results["passed_tests"] += 1
                else:
                    test_results["failed_tests"] += 1
                
                test_results["total_tests"] += 1
                
            except Exception as e:
                test_results["test_files"].append({
                    "file": test_file,
                    "error": str(e),
                    "return_code": -1
                })
                test_results["failed_tests"] += 1
                test_results["total_tests"] += 1
        
        return test_results
    
    def commit_changes(self, message: str = None) -> Dict[str, Any]:
        """Commit changes to version control"""
        thought_processor.add_thought(
            ThoughtType.VALIDATION,
            "Committing changes to version control",
            {"auto_commit": self.auto_commit, "message": message},
            confidence=0.8
        )
        
        if not self.auto_commit:
            return {"status": "disabled"}
        
        project_path = enhanced_grok.current_project["path"] if enhanced_grok.current_project else None
        if not project_path:
            return {"error": "No project path"}
        
        try:
            # Check if git repository
            result = subprocess.run(
                ['git', 'status'],
                capture_output=True,
                text=True,
                cwd=project_path
            )
            
            if result.returncode != 0:
                return {"error": "Not a git repository"}
            
            # Add all changes
            subprocess.run(['git', 'add', '.'], cwd=project_path)
            
            # Commit with message
            commit_message = message or f"AI-generated improvements - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            result = subprocess.run(
                ['git', 'commit', '-m', commit_message],
                capture_output=True,
                text=True,
                cwd=project_path
            )
            
            return {
                "status": "success",
                "message": commit_message,
                "output": result.stdout,
                "error": result.stderr
            }
            
        except Exception as e:
            return {"error": str(e)}
    
    def continuous_improvement_cycle(self, duration_minutes: int = 15) -> Dict[str, Any]:
        """Run a continuous improvement cycle"""
        thought_processor.add_thought(
            ThoughtType.OPTIMIZATION,
            f"Starting continuous improvement cycle for {duration_minutes} minutes",
            {"duration": duration_minutes, "continuous_improvement": self.continuous_improvement},
            confidence=0.8
        )
        
        if not self.continuous_improvement:
            return {"status": "disabled"}
        
        cycle_results = {
            "start_time": datetime.now(),
            "end_time": None,
            "improvements_made": 0,
            "tests_run": 0,
            "commits_made": 0,
            "errors": []
        }
        
        end_time = datetime.now() + timedelta(minutes=duration_minutes)
        
        while datetime.now() < end_time:
            try:
                # Generate improvements
                improvements = self.generate_code_improvements()
                if improvements.get("generated_files") or improvements.get("optimized_files"):
                    cycle_results["improvements_made"] += 1
                
                # Run tests
                test_results = self.run_automated_tests()
                if test_results.get("total_tests", 0) > 0:
                    cycle_results["tests_run"] += 1
                
                # Commit changes
                commit_result = self.commit_changes()
                if commit_result.get("status") == "success":
                    cycle_results["commits_made"] += 1
                
                # Wait before next cycle
                time.sleep(60)  # Wait 1 minute between cycles
                
            except Exception as e:
                cycle_results["errors"].append(str(e))
        
        cycle_results["end_time"] = datetime.now()
        
        thought_processor.add_thought(
            ThoughtType.OPTIMIZATION,
            f"Completed improvement cycle: {cycle_results['improvements_made']} improvements, {cycle_results['commits_made']} commits",
            cycle_results,
            confidence=0.9
        )
        
        return cycle_results
    
    def get_workflow_status(self) -> Dict[str, Any]:
        """Get current workflow status"""
        status = {
            "current_task": self.current_task,
            "project_context": enhanced_grok.current_context,
            "ai_systems": {
                "coding_rules": len(ai_rules.rules),
                "memory_enabled": enhanced_grok.memory_enabled,
                "thought_enabled": enhanced_grok.thought_enabled
            },
            "workflow_settings": {
                "auto_commit": self.auto_commit,
                "auto_test": self.auto_test,
                "continuous_improvement": self.continuous_improvement
            },
            "task_history": self.task_history
        }
        
        return status
    
    def end_development_session(self) -> Dict[str, Any]:
        """End the current development session"""
        if not self.current_task:
            return {"error": "No active session"}
        
        self.current_task["ended_at"] = datetime.now()
        self.current_task["status"] = "completed"
        self.current_task["duration"] = (self.current_task["ended_at"] - self.current_task["started_at"]).total_seconds()
        
        # Add to history
        self.task_history.append(self.current_task)
        
        # Get final insights
        insights = enhanced_grok.get_ai_insights()
        
        session_summary = {
            "task": self.current_task,
            "insights": insights,
            "recommendations": insights.get("recommendations", [])
        }
        
        thought_processor.add_thought(
            ThoughtType.ANALYSIS,
            f"Completed development session: {self.current_task['description']}",
            {"duration": self.current_task["duration"], "insights": len(insights.get("recommendations", []))},
            confidence=0.9
        )
        
        print(f"{Colors.GREEN}✅ {Colors.BOLD}Development Session Completed{Colors.RESET}")
        print(f"{Colors.GREEN}Duration: {self.current_task['duration']:.1f} seconds{Colors.RESET}")
        print(f"{Colors.GREEN}Recommendations: {len(session_summary['recommendations'])}{Colors.RESET}")
        
        self.current_task = None
        
        return session_summary
    
    def show_workflow_dashboard(self):
        """Show the workflow dashboard"""
        status = self.get_workflow_status()
        
        print(f"{Colors.CYAN}🤖 {Colors.BOLD}AI Development Workflow Dashboard{Colors.RESET}")
        print(f"{Colors.CYAN}{'='*60}{Colors.RESET}")
        
        # Current task
        if status["current_task"]:
            task = status["current_task"]
            print(f"{Colors.GREEN}📋 Current Task: {task['description']}{Colors.RESET}")
            print(f"{Colors.GREEN}   Started: {task['started_at'].strftime('%H:%M:%S')}{Colors.RESET}")
            print(f"{Colors.GREEN}   Status: {task['status']}{Colors.RESET}")
        else:
            print(f"{Colors.YELLOW}📋 No active task{Colors.RESET}")
        
        # Project context
        if status["project_context"]:
            context = status["project_context"]
            print(f"\n{Colors.LIGHT_BLUE}📁 Project: {context.get('project_type', 'unknown')}{Colors.RESET}")
            print(f"{Colors.LIGHT_BLUE}   Files: {context.get('file_count', 0)}{Colors.RESET}")
        
        # AI systems
        ai_systems = status["ai_systems"]
        print(f"\n{Colors.LIGHT_BLUE}🧠 AI Systems:{Colors.RESET}")
        print(f"   Coding Rules: {ai_systems['coding_rules']} rules")
        print(f"   Memory: {'✅ Enabled' if ai_systems['memory_enabled'] else '❌ Disabled'}")
        print(f"   Thoughts: {'✅ Enabled' if ai_systems['thought_enabled'] else '❌ Disabled'}")
        
        # Workflow settings
        settings = status["workflow_settings"]
        print(f"\n{Colors.LIGHT_BLUE}⚙️ Workflow Settings:{Colors.RESET}")
        print(f"   Auto Commit: {'✅ Enabled' if settings['auto_commit'] else '❌ Disabled'}")
        print(f"   Auto Test: {'✅ Enabled' if settings['auto_test'] else '❌ Disabled'}")
        print(f"   Continuous Improvement: {'✅ Enabled' if settings['continuous_improvement'] else '❌ Disabled'}")
        
        # Task history
        if status["task_history"]:
            print(f"\n{Colors.LIGHT_BLUE}📚 Task History: {len(status['task_history'])} sessions{Colors.RESET}")
            for task in status["task_history"][-3:]:  # Show last 3
                duration = task.get("duration", 0)
                print(f"   {task['description'][:40]}... ({duration:.1f}s)")

# Global workflow instance
ai_workflow = AIDevelopmentWorkflow() 