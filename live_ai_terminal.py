#!/usr/bin/env python3
"""
LIVE AI TERMINAL INTERFACE
==========================
Interactive terminal interface with live Grok AI agent, thought processing,
log monitoring, and automatic error fixing with Sentry integration.
"""

import asyncio
import threading
import time
import json
import os
import sys
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import subprocess
import signal
import queue
import re
import traceback

# Sentry for error tracking and monitoring
try:
    import sentry_sdk
    from sentry_sdk import capture_exception, capture_message, set_tag, set_context
    SENTRY_AVAILABLE = True
except ImportError:
    SENTRY_AVAILABLE = False
    print("Sentry not available. Install with: pip install sentry-sdk")

# Import our AI systems
try:
    from ai_thought_processor import AIThoughtProcessor, ThoughtType, Colors
    from enhanced_grok_integration import EnhancedGrokIntegration
    from grok_client import call_grok, call_grok_streaming
    from ai_memory_system import ai_memory
    # Import enhanced AI client with multi-provider support
    from enhanced_ai_client import enhanced_ai_client, ask_ai, ask_uncensored
    MULTI_PROVIDER_AVAILABLE = True
except ImportError as e:
    print(f"Warning: AI system import failed: {e}")
    # Create minimal fallback classes
    class Colors:
        LIGHT_BLUE = '\033[94m'
        DARK_BLUE = '\033[34m'
        GREEN = '\033[92m'
        YELLOW = '\033[93m'
        RED = '\033[91m'
        PURPLE = '\033[95m'
        CYAN = '\033[96m'
        WHITE = '\033[97m'
        BOLD = '\033[1m'
        RESET = '\033[0m'

class SentryLogger:
    """Sentry integration for terminal dashboard monitoring"""
    
    def __init__(self, dsn: str = None):
        self.enabled = False
        if SENTRY_AVAILABLE and dsn:
            try:
                sentry_sdk.init(
                    dsn=dsn,
                    traces_sample_rate=1.0,
                    environment="live_terminal",
                    debug=False
                )
                self.enabled = True
                set_tag("component", "live_ai_terminal")
                print(f"{Colors.GREEN}✅ Sentry monitoring enabled{Colors.RESET}")
            except Exception as e:
                print(f"{Colors.YELLOW}⚠️ Sentry initialization failed: {e}{Colors.RESET}")
    
    def log_error(self, error: Exception, context: dict = None):
        """Log error to Sentry with context"""
        if self.enabled:
            if context:
                set_context("error_context", context)
            capture_exception(error)
    
    def log_message(self, message: str, level: str = "info", context: dict = None):
        """Log message to Sentry"""
        if self.enabled:
            if context:
                set_context("message_context", context)
            capture_message(message, level=level)
    
    def log_ai_interaction(self, user_input: str, ai_response: str, success: bool):
        """Log AI interaction"""
        if self.enabled:
            set_context("ai_interaction", {
                "user_input_length": len(user_input),
                "ai_response_length": len(ai_response),
                "success": success,
                "timestamp": datetime.now().isoformat()
            })
            capture_message(f"AI interaction {'successful' if success else 'failed'}")
    
    def log_error_fix_attempt(self, error_source: str, error_line: str, fix_success: bool):
        """Log error fixing attempts"""
        if self.enabled:
            set_context("error_fix", {
                "source": error_source,
                "error": error_line[:200],
                "success": fix_success,
                "timestamp": datetime.now().isoformat()
            })
            capture_message(f"Error fix {'successful' if fix_success else 'failed'}")

class ASCIIArt:
    """ASCII art generator for terminal interface"""
    
    @staticmethod
    def get_startup_banner():
        """Get startup ASCII banner"""
        return f"""{Colors.CYAN}{Colors.BOLD}
╔═══════════════════════════════════════════════════════════════════════════════╗
║                                                                               ║
║    ██╗     ██╗██╗   ██╗███████╗     █████╗ ██╗                              ║
║    ██║     ██║██║   ██║██╔════╝    ██╔══██╗██║                              ║
║    ██║     ██║██║   ██║█████╗      ███████║██║                              ║
║    ██║     ██║╚██╗ ██╔╝██╔══╝      ██╔══██║██║                              ║
║    ███████╗██║ ╚████╔╝ ███████╗    ██║  ██║██║                              ║
║    ╚══════╝╚═╝  ╚═══╝  ╚══════╝    ╚═╝  ╚═╝╚═╝                              ║
║                                                                               ║
║     ████████╗███████╗██████╗ ███╗   ███╗██╗███╗   ██╗ █████╗ ██╗            ║
║     ╚══██╔══╝██╔════╝██╔══██╗████╗ ████║██║████╗  ██║██╔══██╗██║            ║
║        ██║   █████╗  ██████╔╝██╔████╔██║██║██╔██╗ ██║███████║██║            ║
║        ██║   ██╔══╝  ██╔══██╗██║╚██╔╝██║██║██║╚██╗██║██╔══██║██║            ║
║        ██║   ███████╗██║  ██║██║ ╚═╝ ██║██║██║ ╚████║██║  ██║███████╗       ║
║        ╚═╝   ╚══════╝╚═╝  ╚═╝╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝╚═╝  ╚═╝╚══════╝       ║
║                                                                               ║
║  🤖 LIVE AI AGENT  •  🧠 REAL-TIME THOUGHTS  •  🔍 ERROR MONITORING          ║
║  📊 SENTRY LOGGING  •  🛠️ AUTO-FIX  •  💬 GROK INTEGRATION                   ║
║                                                                               ║
╚═══════════════════════════════════════════════════════════════════════════════╝{Colors.RESET}"""
    
    @staticmethod
    def get_thinking_animation():
        """Get thinking animation frames"""
        return [
            f"{Colors.YELLOW}🤔 Thinking...{Colors.RESET}",
            f"{Colors.YELLOW}🧠 Processing...{Colors.RESET}",
            f"{Colors.YELLOW}⚡ Analyzing...{Colors.RESET}",
            f"{Colors.YELLOW}🔍 Searching...{Colors.RESET}"
        ]
    
    @staticmethod
    def get_error_box():
        """Get error detection box"""
        return f"""{Colors.RED}{Colors.BOLD}
╔══════════════════════════════════════════════════════════════════════════════╗
║  🚨 ERROR DETECTED 🚨                                                        ║
║  AI is now focusing on fixing the most urgent issues...                     ║
╚══════════════════════════════════════════════════════════════════════════════╝{Colors.RESET}"""
    
    @staticmethod
    def get_success_box():
        """Get success box"""
        return f"""{Colors.GREEN}{Colors.BOLD}
╔══════════════════════════════════════════════════════════════════════════════╗
║  ✅ SUCCESS ✅                                                               ║
║  Issue has been resolved successfully!                                      ║
╚══════════════════════════════════════════════════════════════════════════════╝{Colors.RESET}"""

class LogMonitor:
    """Enhanced log monitor with Sentry integration and dashboard metrics"""
    
    def __init__(self, log_dir: str = "logs", sentry_logger: SentryLogger = None):
        self.log_dir = Path(log_dir)
        self.sentry_logger = sentry_logger
        self.log_files = {
            "backend": self.log_dir / "backend.log",
            "frontend": self.log_dir / "frontend.log", 
            "ai_workflow": self.log_dir / "ai_workflow.log",
            "live_backend": self.log_dir / "live_backend.log",
            "security": self.log_dir / "security.log",
            "improvement_engine": self.log_dir / "improvement_engine.log"
        }
        self.error_patterns = [
            r"ERROR",
            r"error",
            r"Failed",
            r"Exception",
            r"Traceback",
            r"npm error",
            r"DeprecationWarning",
            r"ImportError",
            r"ModuleNotFoundError",
            r"CRITICAL",
            r"FATAL",
            r"Connection refused",
            r"Permission denied",
            r"No such file"
        ]
        self.error_queue = queue.Queue()
        self.monitoring = False
        self.monitor_thread = None
        
        # Dashboard metrics
        self.metrics = {
            "total_errors": 0,
            "errors_by_source": {},
            "errors_by_severity": {"critical": 0, "high": 0, "medium": 0, "low": 0},
            "last_error_time": None,
            "monitoring_start_time": datetime.now(),
            "files_monitored": len(self.log_files)
        }
    
    def start_monitoring(self):
        """Start monitoring log files"""
        self.monitoring = True
        self.monitor_thread = threading.Thread(target=self._monitor_logs)
        self.monitor_thread.daemon = True
        self.monitor_thread.start()
        
        if self.sentry_logger:
            self.sentry_logger.log_message("Log monitoring started", "info", {
                "files_monitored": list(self.log_files.keys()),
                "error_patterns": len(self.error_patterns)
            })
    
    def stop_monitoring(self):
        """Stop monitoring log files"""
        self.monitoring = False
        if self.monitor_thread:
            self.monitor_thread.join()
        
        if self.sentry_logger:
            self.sentry_logger.log_message("Log monitoring stopped", "info", self.metrics)
    
    def get_dashboard_metrics(self) -> Dict:
        """Get comprehensive dashboard metrics"""
        uptime = datetime.now() - self.metrics["monitoring_start_time"]
        
        return {
            **self.metrics,
            "uptime_seconds": uptime.total_seconds(),
            "uptime_formatted": str(uptime).split('.')[0],
            "errors_per_minute": self.metrics["total_errors"] / max(uptime.total_seconds() / 60, 1),
            "status": "monitoring" if self.monitoring else "stopped"
        }
    
    def _monitor_logs(self):
        """Monitor log files in background thread with enhanced tracking"""
        file_positions = {}
        
        while self.monitoring:
            for log_name, log_path in self.log_files.items():
                if log_path.exists():
                    try:
                        # Track file position to only read new content
                        if log_name not in file_positions:
                            file_positions[log_name] = 0
                        
                        with open(log_path, 'r') as f:
                            f.seek(file_positions[log_name])
                            new_content = f.read()
                            file_positions[log_name] = f.tell()
                            
                            if new_content:
                                self._check_for_errors(log_name, new_content)
                    except Exception as e:
                        error_msg = f"Error monitoring {log_name}: {e}"
                        print(f"{Colors.RED}{error_msg}{Colors.RESET}")
                        
                        if self.sentry_logger:
                            self.sentry_logger.log_error(e, {
                                "log_source": log_name,
                                "log_path": str(log_path)
                            })
            
            time.sleep(2)  # Check every 2 seconds
    
    def _check_for_errors(self, log_name: str, content: str):
        """Check content for error patterns with enhanced metrics"""
        lines = content.split('\n')
        for line_num, line in enumerate(lines):
            for pattern in self.error_patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    severity = self._get_severity(line)
                    error_info = {
                        "source": log_name,
                        "line": line.strip(),
                        "timestamp": datetime.now(),
                        "severity": severity,
                        "line_number": line_num,
                        "pattern_matched": pattern
                    }
                    
                    # Update metrics
                    self.metrics["total_errors"] += 1
                    self.metrics["errors_by_source"][log_name] = self.metrics["errors_by_source"].get(log_name, 0) + 1
                    self.metrics["errors_by_severity"][severity] += 1
                    self.metrics["last_error_time"] = datetime.now()
                    
                    self.error_queue.put(error_info)
                    
                    # Log to Sentry for critical/high errors
                    if self.sentry_logger and severity in ["critical", "high"]:
                        self.sentry_logger.log_message(
                            f"Critical error in {log_name}", 
                            "error",
                            {
                                "source": log_name,
                                "error_line": line.strip()[:200],
                                "severity": severity
                            }
                        )
    
    def _get_severity(self, line: str) -> str:
        """Determine error severity with enhanced categorization"""
        line_lower = line.lower()
        if any(term in line_lower for term in ["critical", "fatal", "failed to start", "connection refused"]):
            return "critical"
        elif any(term in line_lower for term in ["error", "exception", "traceback", "failed"]):
            return "high"
        elif any(term in line_lower for term in ["warning", "deprecated", "modulenotfounderror"]):
            return "medium"
        else:
            return "low"
    
    def get_errors(self) -> List[Dict]:
        """Get all pending errors"""
        errors = []
        while not self.error_queue.empty():
            try:
                errors.append(self.error_queue.get_nowait())
            except queue.Empty:
                break
        return errors
    
    def display_monitoring_dashboard(self):
        """Display real-time monitoring dashboard"""
        metrics = self.get_dashboard_metrics()
        
        print(f"\n{Colors.CYAN}{'='*80}")
        print(f"📊 LIVE MONITORING DASHBOARD")
        print(f"{'='*80}{Colors.RESET}")
        
        print(f"{Colors.GREEN}🟢 Status: {metrics['status'].upper()}")
        print(f"⏱️  Uptime: {metrics['uptime_formatted']}")
        print(f"📁 Files Monitored: {metrics['files_monitored']}")
        print(f"🚨 Total Errors: {metrics['total_errors']}")
        print(f"📈 Errors/min: {metrics['errors_per_minute']:.2f}{Colors.RESET}")
        
        if metrics['last_error_time']:
            time_since = datetime.now() - metrics['last_error_time']
            print(f"{Colors.YELLOW}🕐 Last Error: {time_since.total_seconds():.0f}s ago{Colors.RESET}")
        
        # Errors by severity
        print(f"\n{Colors.WHITE}📊 Errors by Severity:{Colors.RESET}")
        for severity, count in metrics['errors_by_severity'].items():
            color = Colors.RED if severity == "critical" else Colors.YELLOW if severity == "high" else Colors.WHITE
            print(f"  {color}{severity.capitalize()}: {count}{Colors.RESET}")
        
        # Errors by source
        if metrics['errors_by_source']:
            print(f"\n{Colors.WHITE}📁 Errors by Source:{Colors.RESET}")
            for source, count in sorted(metrics['errors_by_source'].items(), key=lambda x: x[1], reverse=True):
                print(f"  {Colors.CYAN}{source}: {count}{Colors.RESET}")
        
        print(f"{Colors.CYAN}{'='*80}{Colors.RESET}")
    
    def get_log_file_status(self) -> Dict:
        """Get status of all log files"""
        status = {}
        for name, path in self.log_files.items():
            if path.exists():
                stat = path.stat()
                status[name] = {
                    "exists": True,
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime),
                    "path": str(path)
                }
            else:
                status[name] = {
                    "exists": False,
                    "path": str(path)
                }
        return status

class SelfImprovementEngine:
    """AI-driven self-improvement system for the terminal"""
    
    def __init__(self, terminal_instance, sentry_logger=None):
        self.terminal = terminal_instance
        self.sentry_logger = sentry_logger
        self.improvement_history = []
        self.performance_metrics = {
            "response_times": [],
            "error_counts": [],
            "user_satisfaction": [],
            "success_rates": []
        }
        self.learning_patterns = {}
        self.auto_improve = True
        
    def analyze_performance(self) -> Dict[str, Any]:
        """Analyze current performance and identify improvement areas"""
        analysis = {
            "avg_response_time": sum(self.performance_metrics["response_times"]) / max(len(self.performance_metrics["response_times"]), 1),
            "total_errors": sum(self.performance_metrics["error_counts"]),
            "improvement_opportunities": [],
            "learning_insights": self.extract_learning_insights(),
            "optimization_suggestions": []
        }
        
        # Identify improvement opportunities
        if analysis["avg_response_time"] > 2.0:
            analysis["improvement_opportunities"].append("response_time_optimization")
            analysis["optimization_suggestions"].append("Implement response caching and optimize AI calls")
        
        if analysis["total_errors"] > 10:
            analysis["improvement_opportunities"].append("error_reduction")
            analysis["optimization_suggestions"].append("Enhance error handling and add more validation")
        
        if len(self.terminal.conversation_history) > 100:
            analysis["improvement_opportunities"].append("conversation_management")
            analysis["optimization_suggestions"].append("Implement conversation history compression")
        
        return analysis
    
    def extract_learning_insights(self) -> List[str]:
        """Extract insights from user interactions"""
        insights = []
        
        # Analyze conversation patterns
        if self.terminal.conversation_history:
            recent_conversations = self.terminal.conversation_history[-50:]
            
            # Find common user requests
            user_messages = [msg["content"] for msg in recent_conversations if msg["role"] == "user"]
            common_words = {}
            
            for msg in user_messages:
                words = msg.lower().split()
                for word in words:
                    if len(word) > 3:  # Ignore short words
                        common_words[word] = common_words.get(word, 0) + 1
            
            # Identify patterns
            top_words = sorted(common_words.items(), key=lambda x: x[1], reverse=True)[:5]
            if top_words:
                insights.append(f"Users frequently ask about: {', '.join([word for word, count in top_words])}")
        
        # Analyze error patterns
        if hasattr(self.terminal, 'log_monitor') and self.terminal.log_monitor.metrics:
            error_sources = self.terminal.log_monitor.metrics.get("errors_by_source", {})
            if error_sources:
                top_error_source = max(error_sources.items(), key=lambda x: x[1])
                insights.append(f"Most errors come from: {top_error_source[0]} ({top_error_source[1]} errors)")
        
        return insights
    
    async def suggest_improvements(self) -> List[Dict[str, Any]]:
        """Generate specific improvement suggestions"""
        analysis = self.analyze_performance()
        suggestions = []
        
        for opportunity in analysis["improvement_opportunities"]:
            if opportunity == "response_time_optimization":
                suggestions.append({
                    "type": "performance",
                    "title": "Response Time Optimization",
                    "description": "Implement caching and optimize AI API calls",
                    "impact": "high",
                    "effort": "medium",
                    "implementation": self._implement_response_optimization
                })
            
            elif opportunity == "error_reduction":
                suggestions.append({
                    "type": "reliability",
                    "title": "Enhanced Error Handling",
                    "description": "Add better error detection and recovery mechanisms",
                    "impact": "high",
                    "effort": "low",
                    "implementation": self._implement_error_improvements
                })
            
            elif opportunity == "conversation_management":
                suggestions.append({
                    "type": "efficiency",
                    "title": "Conversation History Management",
                    "description": "Implement smart conversation history compression",
                    "impact": "medium",
                    "effort": "low",
                    "implementation": self._implement_conversation_management
                })
        
        # Add learning-based suggestions
        insights = analysis["learning_insights"]
        for insight in insights:
            if "frequently ask about" in insight:
                suggestions.append({
                    "type": "user_experience",
                    "title": "Quick Commands for Common Requests",
                    "description": f"Add shortcuts based on pattern: {insight}",
                    "impact": "medium",
                    "effort": "low",
                    "implementation": self._implement_quick_commands
                })
        
        return suggestions
    
    async def auto_improve(self):
        """Automatically implement safe improvements"""
        if not self.auto_improve:
            return
        
        suggestions = await self.suggest_improvements()
        implemented = []
        
        for suggestion in suggestions:
            if suggestion["effort"] == "low" and suggestion["impact"] in ["high", "medium"]:
                try:
                    # Implement the improvement
                    success = await suggestion["implementation"]()
                    if success:
                        implemented.append(suggestion["title"])
                        self.improvement_history.append({
                            "improvement": suggestion["title"],
                            "timestamp": datetime.now(),
                            "success": True
                        })
                        
                        if self.sentry_logger:
                            self.sentry_logger.log_message(
                                f"Auto-improvement implemented: {suggestion['title']}",
                                "info",
                                {"improvement_type": suggestion["type"]}
                            )
                
                except Exception as e:
                    print(f"{Colors.YELLOW}⚠️ Failed to auto-implement: {suggestion['title']} - {e}{Colors.RESET}")
                    
                    if self.sentry_logger:
                        self.sentry_logger.log_error(e, {
                            "context": "auto_improvement",
                            "improvement": suggestion["title"]
                        })
        
        if implemented:
            print(f"\n{Colors.GREEN}🚀 Auto-improvements implemented:{Colors.RESET}")
            for improvement in implemented:
                print(f"  ✅ {improvement}")
    
    async def _implement_response_optimization(self) -> bool:
        """Implement response time optimization"""
        try:
            # Add simple response caching
            if not hasattr(self.terminal, 'response_cache'):
                self.terminal.response_cache = {}
                self.terminal.cache_hits = 0
                
                # Override the AI call method to add caching
                original_call = self.terminal._call_grok_async
                
                async def cached_call(prompt, system_message=None):
                    cache_key = f"{prompt[:100]}_{system_message[:50] if system_message else ''}"
                    
                    if cache_key in self.terminal.response_cache:
                        self.terminal.cache_hits += 1
                        return self.terminal.response_cache[cache_key]
                    
                    response = await original_call(prompt, system_message)
                    
                    # Cache response (limit cache size)
                    if len(self.terminal.response_cache) < 50:
                        self.terminal.response_cache[cache_key] = response
                    
                    return response
                
                self.terminal._call_grok_async = cached_call
                return True
        except Exception:
            return False
    
    async def _implement_error_improvements(self) -> bool:
        """Implement enhanced error handling"""
        try:
            # Add error recovery patterns
            if not hasattr(self.terminal, 'error_patterns'):
                self.terminal.error_patterns = {
                    "connection_timeout": "retry_with_backoff",
                    "api_rate_limit": "wait_and_retry",
                    "memory_error": "clear_cache_and_retry"
                }
            return True
        except Exception:
            return False
    
    async def _implement_conversation_management(self) -> bool:
        """Implement conversation history management"""
        try:
            # Compress old conversation history
            if len(self.terminal.conversation_history) > 100:
                # Keep last 50 conversations and summarize older ones
                old_conversations = self.terminal.conversation_history[:-50]
                recent_conversations = self.terminal.conversation_history[-50:]
                
                # Create summary of old conversations
                summary = {
                    "role": "system",
                    "content": f"[Summarized {len(old_conversations)} previous interactions]",
                    "timestamp": datetime.now(),
                    "is_summary": True
                }
                
                self.terminal.conversation_history = [summary] + recent_conversations
            return True
        except Exception:
            return False
    
    async def _implement_quick_commands(self) -> bool:
        """Implement quick commands for common requests"""
        try:
            if not hasattr(self.terminal, 'quick_commands'):
                self.terminal.quick_commands = {
                    "errors": "show recent errors and suggest fixes",
                    "optimize": "analyze performance and suggest optimizations",
                    "health": "show system health status",
                    "logs": "display recent log entries"
                }
            return True
        except Exception:
            return False
    
    def generate_improvement_report(self) -> str:
        """Generate a report of recent improvements"""
        if not self.improvement_history:
            return "No improvements implemented yet."
        
        recent_improvements = self.improvement_history[-10:]
        report = f"📈 Recent Improvements ({len(recent_improvements)}):\n"
        
        for i, improvement in enumerate(recent_improvements, 1):
            status = "✅" if improvement["success"] else "❌"
            timestamp = improvement["timestamp"].strftime("%H:%M:%S")
            report += f"  {i}. {status} {improvement['improvement']} ({timestamp})\n"
        
        # Add performance metrics if available
        if self.performance_metrics["response_times"]:
            avg_time = sum(self.performance_metrics["response_times"]) / len(self.performance_metrics["response_times"])
            report += f"\n📊 Current Performance:\n"
            report += f"  • Avg Response Time: {avg_time:.2f}s\n"
            report += f"  • Total Errors: {sum(self.performance_metrics['error_counts'])}\n"
            
            if hasattr(self.terminal, 'cache_hits'):
                cache_ratio = self.terminal.cache_hits / max(self.terminal.session_metrics['ai_calls'], 1) * 100
                report += f"  • Cache Hit Ratio: {cache_ratio:.1f}%\n"
        
        return report

class LiveAITerminal:
    """Enhanced live AI terminal interface with Sentry monitoring and ASCII art"""
    
    def __init__(self, sentry_dsn: str = None):
        # Initialize Sentry logging
        self.sentry_logger = SentryLogger(sentry_dsn)
        
        # Initialize AI systems with fallback
        try:
            self.thought_processor = AIThoughtProcessor()
            self.grok_integration = EnhancedGrokIntegration()
        except Exception as e:
            # Fallback for missing AI systems
            self.thought_processor = None
            self.grok_integration = None
            print(f"{Colors.YELLOW}⚠️ AI systems not available, running in basic mode: {e}{Colors.RESET}")
        
        self.log_monitor = LogMonitor(sentry_logger=self.sentry_logger)
        
        # Initialize self-improvement engine
        self.improvement_engine = SelfImprovementEngine(self, self.sentry_logger)
        
        # Terminal state
        self.running = False
        self.conversation_history = []
        self.error_fixing_mode = False
        self.dashboard_mode = False
        self.auto_improve_mode = True
        
        # Performance metrics
        self.session_metrics = {
            "start_time": datetime.now(),
            "conversations": 0,
            "errors_fixed": 0,
            "ai_calls": 0,
            "successful_fixes": 0,
            "improvements_made": 0
        }
        
        # Initialize project context
        if self.grok_integration:
            self.grok_integration.set_project_context(
                "/Users/maxwoldenberg/Desktop/pon",
                "web_app_with_ai"
            )
        
        # Log startup
        if self.sentry_logger.enabled:
            self.sentry_logger.log_message("Live AI Terminal started", "info", {
                "project_path": "/Users/maxwoldenberg/Desktop/pon",
                "features": ["grok_ai", "thought_processing", "error_monitoring", "auto_fix"]
            })
    
    def draw_separator(self, title: str = "AI THOUGHT PROCESS"):
        """Draw enhanced ASCII separator box with dots"""
        width = 80
        dot_line = "." * width
        
        print(f"\n{Colors.CYAN}{'='*width}")
        print(f"{dot_line}")
        print(f"{'.' * 10} {title.center(width - 22)} {'.' * 10}")
        print(f"{dot_line}")
        print(f"{'='*width}{Colors.RESET}")
    
    def start(self):
        """Start the enhanced live AI terminal"""
        self.running = True
        
        # Display ASCII art banner
        print(ASCIIArt.get_startup_banner())
        
        # Start log monitoring
        self.log_monitor.start_monitoring()
        
        # Display welcome and system info
        self._display_startup_info()
        
        # Start main loop
        try:
            asyncio.run(self._main_loop())
        except KeyboardInterrupt:
            self.shutdown()
        except Exception as e:
            print(f"\n{Colors.RED}Fatal error: {e}{Colors.RESET}")
            if self.sentry_logger:
                self.sentry_logger.log_error(e, {"location": "main_loop"})
            self.shutdown()
    
    def shutdown(self):
        """Enhanced shutdown with metrics reporting"""
        print(f"\n{Colors.YELLOW}Shutting down Live AI Terminal...{Colors.RESET}")
        
        # Calculate session metrics
        session_duration = datetime.now() - self.session_metrics["start_time"]
        
        # Display session summary
        print(f"\n{Colors.CYAN}📊 Session Summary:{Colors.RESET}")
        print(f"  Duration: {str(session_duration).split('.')[0]}")
        print(f"  Conversations: {self.session_metrics['conversations']}")
        print(f"  AI Calls: {self.session_metrics['ai_calls']}")
        print(f"  Errors Fixed: {self.session_metrics['errors_fixed']}")
        print(f"  Success Rate: {(self.session_metrics['successful_fixes'] / max(self.session_metrics['errors_fixed'], 1) * 100):.1f}%")
        
        # Stop systems
        self.running = False
        self.thought_processor.stop_processing()
        self.log_monitor.stop_monitoring()
        
        # Log shutdown to Sentry
        if self.sentry_logger.enabled:
            self.sentry_logger.log_message("Live AI Terminal shutdown", "info", {
                **self.session_metrics,
                "session_duration_seconds": session_duration.total_seconds()
            })
        
        print(f"{Colors.GREEN}✅ Shutdown complete. Goodbye!{Colors.RESET}")
    
    def _display_startup_info(self):
        """Display enhanced startup information"""
        print(f"\n{Colors.BOLD}{Colors.WHITE}🚀 SYSTEM INITIALIZATION{Colors.RESET}")
        print(f"{Colors.CYAN}{'─'*60}{Colors.RESET}")
        
        # Show current status
        self._show_system_status()
        
        # Show log file status
        self._show_log_file_status()
        
        # Show monitoring dashboard
        self.log_monitor.display_monitoring_dashboard()
        
        print(f"\n{Colors.BOLD}{Colors.GREEN}✅ System Ready - Type 'help' for commands{Colors.RESET}")
    
    def _show_system_status(self):
        """Enhanced system status display"""
        print(f"\n{Colors.GREEN}🟢 System Status:{Colors.RESET}")
        print(f"  • AI Thought Processor: {'✅ Active' if self.thought_processor.is_processing else '❌ Inactive'}")
        print(f"  • Log Monitor: {'✅ Active' if self.log_monitor.monitoring else '❌ Inactive'}")
        print(f"  • Grok Integration: {'✅ Ready' if True else '❌ Not Ready'}")
        print(f"  • Sentry Logging: {'✅ Enabled' if self.sentry_logger.enabled else '❌ Disabled'}")
        print(f"  • Project: {self.grok_integration.current_project['path'] if self.grok_integration.current_project else 'None'}")
        print(f"  • Session Started: {self.session_metrics['start_time'].strftime('%H:%M:%S')}")
    
    def _show_log_file_status(self):
        """Show status of monitored log files"""
        print(f"\n{Colors.BLUE}📁 Log Files:{Colors.RESET}")
        log_status = self.log_monitor.get_log_file_status()
        
        for name, status in log_status.items():
            if status['exists']:
                size_kb = status['size'] / 1024
                modified_str = status['modified'].strftime('%H:%M:%S')
                print(f"  • {name}: {'✅' if size_kb > 0 else '⚠️'} {size_kb:.1f}KB (modified: {modified_str})")
            else:
                print(f"  • {name}: ❌ Not found")
    
    async def _main_loop(self):
        """Enhanced main interaction loop with dashboard mode"""
        while self.running:
            try:
                # Check for errors first
                await self._check_and_handle_errors()
                
                # Show dashboard if in dashboard mode
                if self.dashboard_mode:
                    await self._show_live_dashboard()
                    await asyncio.sleep(5)  # Update every 5 seconds
                    continue
                
                # Get user input
                user_input = await self._get_user_input()
                
                if not user_input:
                    continue
                
                # Process commands
                if user_input.lower() in ['quit', 'exit', 'q']:
                    break
                elif user_input.lower() == 'help':
                    self._show_help()
                elif user_input.lower() == 'status':
                    self._show_system_status()
                elif user_input.lower() == 'dashboard':
                    self.dashboard_mode = True
                    print(f"{Colors.GREEN}📊 Entering live dashboard mode (type 'q' to exit)...{Colors.RESET}")
                elif user_input.lower() == 'metrics':
                    self._show_session_metrics()
                elif user_input.lower() == 'logs':
                    self._show_log_file_status()
                elif user_input.lower() == 'clear':
                    os.system('clear' if os.name == 'posix' else 'cls')
                    print(ASCIIArt.get_startup_banner())
                elif user_input.lower() == 'improve':
                    await self._show_improvement_suggestions()
                elif user_input.lower() == 'auto-improve':
                    self.auto_improve_mode = not self.auto_improve_mode
                    status = "enabled" if self.auto_improve_mode else "disabled"
                    print(f"{Colors.GREEN}🚀 Auto-improvement {status}{Colors.RESET}")
                elif user_input.lower().startswith('fix'):
                    await self._manual_fix_mode()
                elif user_input.lower().startswith('uncensored:'):
                    # Uncensored AI query
                    query = user_input[11:].strip()  # Remove 'uncensored:' prefix
                    await self._process_uncensored_ai(query)
                elif user_input.lower() == 'providers':
                    await self._show_ai_providers()
                elif user_input.lower() == 'stats':
                    await self._show_ai_stats()
                else:
                    # Process AI conversation
                    await self._process_ai_conversation(user_input)
                
            except Exception as e:
                error_msg = f"Error in main loop: {e}"
                print(f"{Colors.RED}{error_msg}{Colors.RESET}")
                if self.sentry_logger:
                    self.sentry_logger.log_error(e, {"location": "main_loop"})
                await asyncio.sleep(1)
    
    async def _show_live_dashboard(self):
        """Show live updating dashboard"""
        os.system('clear' if os.name == 'posix' else 'cls')
        
        print(f"{Colors.BOLD}{Colors.CYAN}📊 LIVE AI TERMINAL DASHBOARD{Colors.RESET}")
        print(f"{Colors.CYAN}{'='*80}{Colors.RESET}")
        
        # System status
        self._show_system_status()
        
        # Monitoring metrics
        self.log_monitor.display_monitoring_dashboard()
        
        # Session metrics
        self._show_session_metrics()
        
        # Recent errors
        errors = self.log_monitor.get_errors()
        if errors:
            print(f"\n{Colors.RED}🚨 Recent Errors:{Colors.RESET}")
            for error in errors[-5:]:  # Show last 5
                time_str = error['timestamp'].strftime('%H:%M:%S')
                print(f"  [{time_str}] {error['source']}: {error['line'][:60]}...")
        
        print(f"\n{Colors.YELLOW}Press 'q' + Enter to exit dashboard mode{Colors.RESET}")
        
        # Check for quit in dashboard mode
        try:
            user_input = await asyncio.wait_for(self._get_user_input(), timeout=0.1)
            if user_input.lower() == 'q':
                self.dashboard_mode = False
                print(f"{Colors.GREEN}Exiting dashboard mode...{Colors.RESET}")
        except asyncio.TimeoutError:
            pass
    
    def _show_session_metrics(self):
        """Show current session metrics"""
        duration = datetime.now() - self.session_metrics['start_time']
        
        print(f"\n{Colors.WHITE}📈 Session Metrics:{Colors.RESET}")
        print(f"  • Duration: {str(duration).split('.')[0]}")
        print(f"  • Conversations: {self.session_metrics['conversations']}")
        print(f"  • AI Calls: {self.session_metrics['ai_calls']}")
        print(f"  • Errors Detected: {self.log_monitor.metrics['total_errors']}")
        print(f"  • Errors Fixed: {self.session_metrics['errors_fixed']}")
        print(f"  • Improvements Made: {self.session_metrics['improvements_made']}")
        print(f"  • Auto-Improve: {'✅ Enabled' if self.auto_improve_mode else '❌ Disabled'}")
        
        if self.session_metrics['errors_fixed'] > 0:
            success_rate = (self.session_metrics['successful_fixes'] / self.session_metrics['errors_fixed']) * 100
            print(f"  • Fix Success Rate: {success_rate:.1f}%")
        
        # Show improvement report if available
        if hasattr(self, 'improvement_engine') and self.improvement_engine.improvement_history:
            print(f"\n{Colors.CYAN}📈 Recent Improvements:{Colors.RESET}")
            recent_report = self.improvement_engine.generate_improvement_report()
            print(f"  {recent_report.replace(chr(10), chr(10) + '  ')}")
    
    async def _get_user_input(self):
        """Get user input asynchronously with prompt enhancement"""
        try:
            # Show thinking animation if AI is processing
            if hasattr(self, '_ai_thinking') and self._ai_thinking:
                animation = ASCIIArt.get_thinking_animation()
                for frame in animation:
                    print(f"\r{frame}", end="", flush=True)
                    await asyncio.sleep(0.5)
                print()
            
            prompt = f"\n{Colors.BOLD}{Colors.WHITE}💬 You: {Colors.RESET}"
            print(prompt, end="")
            
            # Use input() in a thread to avoid blocking
            loop = asyncio.get_event_loop()
            user_input = await loop.run_in_executor(None, input)
            return user_input.strip()
        except EOFError:
            return "quit"
    
    async def _check_and_handle_errors(self):
        """Enhanced error checking and handling with Sentry integration"""
        errors = self.log_monitor.get_errors()
        
        if errors:
            # Sort errors by severity and timestamp
            critical_errors = [e for e in errors if e['severity'] == 'critical']
            high_errors = [e for e in errors if e['severity'] == 'high']
            
            urgent_errors = critical_errors + high_errors
            
            if urgent_errors:
                # Display error detection box
                print(ASCIIArt.get_error_box())
                
                self.draw_separator("URGENT ERROR DETECTED")
                
                for error in urgent_errors[:3]:  # Handle top 3 urgent errors
                    print(f"{Colors.RED}🚨 {error['severity'].upper()} ERROR in {error['source']}:{Colors.RESET}")
                    print(f"   {error['line']}")
                    print(f"   {Colors.GRAY}Detected at: {error['timestamp'].strftime('%H:%M:%S')} (Pattern: {error.get('pattern_matched', 'N/A')}){Colors.RESET}")
                    
                    # Add thought about the error
                    self.thought_processor.add_thought(
                        ThoughtType.ERROR_HANDLING,
                        f"Detected {error['severity']} error in {error['source']}: {error['line'][:100]}...",
                        {
                            "source": error['source'], 
                            "severity": error['severity'],
                            "line_number": error.get('line_number', 0)
                        },
                        confidence=0.9
                    )
                    
                    # Log to Sentry
                    if self.sentry_logger:
                        self.sentry_logger.log_message(
                            f"Urgent error detected in {error['source']}",
                            "error",
                            {
                                "error_details": error,
                                "auto_fix_triggered": True
                            }
                        )
                
                # Auto-fix mode
                if not self.error_fixing_mode:
                    self.error_fixing_mode = True
                    await self._auto_fix_errors(urgent_errors)
                    self.error_fixing_mode = False
    
    async def _auto_fix_errors(self, errors: List[Dict]):
        """Enhanced automatic error fixing with success tracking"""
        self.draw_separator("AI AUTO-FIX MODE")
        
        self.thought_processor.add_thought(
            ThoughtType.ANALYSIS,
            f"Analyzing {len(errors)} urgent errors for automatic fixing",
            {"error_count": len(errors), "auto_fix_session": True},
            confidence=0.8
        )
        
        successful_fixes = 0
        
        for i, error in enumerate(errors, 1):
            try:
                print(f"\n{Colors.YELLOW}🔧 Processing Error {i}/{len(errors)}{Colors.RESET}")
                print(f"   Source: {error['source']}")
                print(f"   Severity: {error['severity']}")
                
                # Get error context
                error_context = self._get_error_context(error)
                
                # Ask Grok for solution
                fix_prompt = self._build_fix_prompt(error, error_context)
                
                self.thought_processor.add_thought(
                    ThoughtType.SOLUTION,
                    f"Requesting AI solution for {error['source']} error",
                    {"error_source": error['source'], "attempt": i},
                    confidence=0.7
                )
                
                # Show thinking animation
                self._ai_thinking = True
                
                # Get AI response
                response = await self._call_grok_async(fix_prompt)
                self.session_metrics['ai_calls'] += 1
                
                self._ai_thinking = False
                
                # Display response
                print(f"\n{Colors.GREEN}🤖 AI Solution for {error['source']} error:{Colors.RESET}")
                print(f"{Colors.WHITE}{response}{Colors.RESET}")
                
                # Apply automatic fixes if possible
                fix_success = await self._apply_automatic_fix(error, response)
                
                if fix_success:
                    successful_fixes += 1
                    print(ASCIIArt.get_success_box())
                    
                self.session_metrics['errors_fixed'] += 1
                
                # Log fix attempt to Sentry
                if self.sentry_logger:
                    self.sentry_logger.log_error_fix_attempt(
                        error['source'], 
                        error['line'], 
                        fix_success
                    )
                
                # Brief pause between fixes
                await asyncio.sleep(2)
                
            except Exception as e:
                error_msg = f"Failed to get AI fix for error: {e}"
                print(f"{Colors.RED}{error_msg}{Colors.RESET}")
                if self.sentry_logger:
                    self.sentry_logger.log_error(e, {
                        "context": "auto_fix_errors",
                        "original_error": error
                    })
        
        # Update success metrics
        self.session_metrics['successful_fixes'] += successful_fixes
        
        # Summary
        success_rate = (successful_fixes / len(errors)) * 100 if errors else 0
        print(f"\n{Colors.CYAN}📊 Auto-Fix Summary:{Colors.RESET}")
        print(f"   Processed: {len(errors)} errors")
        print(f"   Fixed: {successful_fixes} errors")
        print(f"   Success Rate: {success_rate:.1f}%")
        
        if successful_fixes > 0:
            print(f"{Colors.GREEN}✅ {successful_fixes} error(s) resolved successfully!{Colors.RESET}")
    
    def _build_fix_prompt(self, error: Dict, context: str) -> str:
        """Build comprehensive fix prompt for Grok"""
        return f"""
URGENT ERROR ANALYSIS & FIX REQUEST:

ERROR DETAILS:
- Source: {error['source']}
- Severity: {error['severity']}
- Timestamp: {error['timestamp'].strftime('%Y-%m-%d %H:%M:%S')}
- Line: {error['line']}
- Pattern Matched: {error.get('pattern_matched', 'N/A')}
- Line Number: {error.get('line_number', 'N/A')}

CONTEXT:
{context}

PROJECT INFO:
- Type: Web application with AI integration
- Backend: Python/FastAPI
- Frontend: Next.js/React
- AI Systems: Grok integration, thought processing, memory system

REQUIRED RESPONSE FORMAT:
1. ROOT CAUSE: Brief analysis of what caused this error
2. SEVERITY ASSESSMENT: Why this error is {error['severity']} priority
3. FIX STRATEGY: Step-by-step approach to resolve
4. COMMANDS: Exact terminal commands to run (if any)
5. CODE CHANGES: Specific code modifications (if any)
6. VALIDATION: How to verify the fix worked

Be concise, actionable, and focus on immediate resolution.
"""
    
    def _get_error_context(self, error: Dict) -> str:
        """Get enhanced context for an error"""
        context = []
        
        # Read relevant log file with more context
        log_path = self.log_monitor.log_files.get(error['source'])
        if log_path and log_path.exists():
            try:
                with open(log_path, 'r') as f:
                    lines = f.readlines()
                    
                # Get context around the error line
                error_line_num = error.get('line_number', 0)
                start_line = max(0, error_line_num - 10)
                end_line = min(len(lines), error_line_num + 10)
                
                context.append("=== LOG CONTEXT (20 lines around error) ===")
                for i in range(start_line, end_line):
                    prefix = ">>> " if i == error_line_num else "    "
                    context.append(f"{prefix}{i+1}: {lines[i].strip()}")
                
                context.append("\n=== RECENT LOG ENTRIES (last 10) ===")
                context.extend([line.strip() for line in lines[-10:]])
            except Exception:
                context.append("Could not read log context")
        
        # Check for specific error patterns and add relevant context
        error_line = error['line'].lower()
        
        if "modulenotfounderror" in error_line or "no module named" in error_line:
            module_match = re.search(r"no module named '([^']+)'", error_line)
            if module_match:
                module_name = module_match.group(1)
                context.append(f"\n=== MISSING MODULE ANALYSIS ===")
                context.append(f"Missing module: {module_name}")
                context.append("This is likely a dependency issue that can be fixed with pip install")
        
        elif "connection refused" in error_line or "port" in error_line:
            context.append(f"\n=== CONNECTION ISSUE ANALYSIS ===")
            context.append("This appears to be a service connection issue")
            context.append("Check if required services are running on expected ports")
        
        elif "permission denied" in error_line:
            context.append(f"\n=== PERMISSION ISSUE ANALYSIS ===")
            context.append("This is a file/directory permission problem")
            context.append("May require chmod or different user privileges")
        
        # Add system information
        context.append(f"\n=== SYSTEM INFO ===")
        context.append(f"OS: macOS (detected from shell: zsh)")
        context.append(f"Error detected at: {error['timestamp']}")
        context.append(f"Monitoring session uptime: {datetime.now() - self.log_monitor.metrics['monitoring_start_time']}")
        
        return "\n".join(context)
    
    async def _apply_automatic_fix(self, error: Dict, solution: str) -> bool:
        """Enhanced automatic fix application with better success detection"""
        fix_applied = False
        
        try:
            # Extract and apply common fixes
            if "no module named" in error['line'].lower():
                # Extract module name and install it
                module_match = re.search(r"no module named '([^']+)'", error['line'], re.IGNORECASE)
                if module_match:
                    module_name = module_match.group(1)
                    print(f"{Colors.YELLOW}🔧 Auto-installing missing module: {module_name}{Colors.RESET}")
                    
                    try:
                        # Use pip install with error handling
                        result = subprocess.run(
                            [sys.executable, "-m", "pip", "install", module_name], 
                            capture_output=True, 
                            text=True,
                            timeout=60  # 1 minute timeout
                        )
                        
                        if result.returncode == 0:
                            print(f"{Colors.GREEN}✅ Successfully installed {module_name}{Colors.RESET}")
                            fix_applied = True
                            
                            self.thought_processor.add_thought(
                                ThoughtType.SOLUTION,
                                f"Successfully auto-installed missing module: {module_name}",
                                {"module": module_name, "action": "pip_install", "success": True},
                                confidence=0.9
                            )
                        else:
                            print(f"{Colors.RED}❌ Failed to install {module_name}:{Colors.RESET}")
                            print(f"   {result.stderr}")
                            
                            # Try alternative installation methods
                            alt_result = subprocess.run(
                                [sys.executable, "-m", "pip", "install", "--user", module_name],
                                capture_output=True,
                                text=True,
                                timeout=60
                            )
                            
                            if alt_result.returncode == 0:
                                print(f"{Colors.GREEN}✅ Successfully installed {module_name} with --user flag{Colors.RESET}")
                                fix_applied = True
                    
                    except subprocess.TimeoutExpired:
                        print(f"{Colors.RED}❌ Installation timeout for {module_name}{Colors.RESET}")
                    except Exception as e:
                        print(f"{Colors.RED}❌ Error installing module: {e}{Colors.RESET}")
            
            elif "npm error" in error['line'].lower():
                if "missing script" in error['line'].lower():
                    print(f"{Colors.YELLOW}🔧 Attempting to fix npm script issue{Colors.RESET}")
                    
                    # Check if we're in the frontend directory and try common fixes
                    frontend_path = Path("/Users/maxwoldenberg/Desktop/pon/frontend")
                    if frontend_path.exists():
                        try:
                            # Run npm install to fix potential dependency issues
                            result = subprocess.run(
                                ["npm", "install"],
                                capture_output=True,
                                text=True,
                                cwd=str(frontend_path),
                                timeout=120
                            )
                            
                            if result.returncode == 0:
                                print(f"{Colors.GREEN}✅ npm install completed successfully{Colors.RESET}")
                                fix_applied = True
                            else:
                                print(f"{Colors.YELLOW}⚠️ npm install had warnings: {result.stderr[:200]}{Colors.RESET}")
                        
                        except Exception as e:
                            print(f"{Colors.RED}❌ npm install failed: {e}{Colors.RESET}")
            
            elif "port" in error['line'].lower() and "already in use" in error['line'].lower():
                print(f"{Colors.YELLOW}🔧 Attempting to resolve port conflict{Colors.RESET}")
                
                # Extract port number if possible
                port_match = re.search(r"port (\d+)", error['line'])
                if port_match:
                    port = port_match.group(1)
                    print(f"   Detected port conflict on: {port}")
                    
                    # Could implement port killing logic here
                    # For now, just report the issue
                    print(f"   Suggestion: Kill process using port {port} or use different port")
                    
        except Exception as e:
            print(f"{Colors.RED}❌ Error in automatic fix application: {e}{Colors.RESET}")
            if self.sentry_logger:
                self.sentry_logger.log_error(e, {
                    "context": "apply_automatic_fix",
                    "original_error": error
                })
        
        return fix_applied
    
    async def _process_ai_conversation(self, user_input: str):
        """Process AI conversation with thought display"""
        self.draw_separator("AI CONVERSATION")
        
        # Add user message to history
        self.conversation_history.append({
            "role": "user",
            "content": user_input,
            "timestamp": datetime.now()
        })
        
        # Show AI thinking
        self.thought_processor.add_thought(
            ThoughtType.ANALYSIS,
            f"Processing user request: {user_input[:50]}...",
            {"user_input_length": len(user_input)},
            confidence=0.8
        )
        
        # Add performance tracking
        start_time = time.time()
        
        # Check for auto-improvements periodically
        if self.auto_improve_mode and len(self.conversation_history) % 10 == 0 and len(self.conversation_history) > 0:
            await self.improvement_engine.auto_improve()
        
        try:
            # Prepare context for Grok
            system_message = self._build_system_message()
            
            # Call Grok AI
            if self.thought_processor:
                self.thought_processor.add_thought(
                    ThoughtType.PATTERN_MATCHING,
                    "Calling Grok AI for response generation",
                    {"context_length": len(system_message)},
                    confidence=0.9
                )
            
            response = await self._call_grok_async(user_input, system_message)
            
            # Track performance
            response_time = time.time() - start_time
            self.improvement_engine.performance_metrics["response_times"].append(response_time)
            
            # Display response
            print(f"\n{Colors.BOLD}{Colors.GREEN}🤖 Grok AI:{Colors.RESET}")
            print(f"{Colors.WHITE}{response}{Colors.RESET}")
            
            # Add to conversation history
            self.conversation_history.append({
                "role": "assistant", 
                "content": response,
                "timestamp": datetime.now()
            })
            
            # Update session metrics
            self.session_metrics['conversations'] += 1
            self.session_metrics['ai_calls'] += 1
            
            # Analyze response for actions
            await self._analyze_ai_response(response)
            
        except Exception as e:
            print(f"{Colors.RED}Error communicating with Grok AI: {e}{Colors.RESET}")
            self.thought_processor.add_thought(
                ThoughtType.ERROR_HANDLING,
                f"Failed to communicate with Grok AI: {str(e)}",
                {"error": str(e)},
                confidence=0.8
            )
    
    def _build_system_message(self) -> str:
        """Build comprehensive system message for Grok"""
        context = []
        
        # Project context
        if self.grok_integration.current_project:
            context.append(f"Current project: {self.grok_integration.current_project['path']}")
            context.append(f"Project type: {self.grok_integration.current_project['type']}")
        
        # Recent errors
        recent_errors = self.log_monitor.get_errors()
        if recent_errors:
            context.append("Recent errors detected:")
            for error in recent_errors[-3:]:
                context.append(f"- {error['source']}: {error['line'][:100]}")
        
        # Conversation context
        if self.conversation_history:
            context.append("Recent conversation:")
            for msg in self.conversation_history[-5:]:
                context.append(f"- {msg['role']}: {msg['content'][:100]}")
        
        system_message = f"""
        You are Grok AI integrated into a live terminal interface for a web application project.
        
        CONTEXT:
        {chr(10).join(context)}
        
        CAPABILITIES:
        - Real-time error monitoring and fixing
        - Live thought processing display
        - Code analysis and generation
        - Project management assistance
        
        INSTRUCTIONS:
        - Be concise but helpful
        - Focus on actionable solutions
        - If you detect urgent issues, prioritize them
        - Show your reasoning process
        - Suggest specific commands or code changes when appropriate
        """
        
        return system_message
    
    async def _call_grok_async(self, prompt: str, system_message: str = None) -> str:
        """Call Grok AI asynchronously"""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, call_grok, prompt, system_message)
    
    async def _analyze_ai_response(self, response: str):
        """Analyze AI response for potential actions"""
        # Check if response contains code
        if "```" in response:
            self.thought_processor.add_thought(
                ThoughtType.CODE_GENERATION,
                "AI response contains code snippets for implementation",
                {"has_code": True},
                confidence=0.8
            )
        
        # Check for commands
        command_patterns = [r"`([^`]+)`", r"run ([^\n]+)", r"execute ([^\n]+)"]
        for pattern in command_patterns:
            if re.search(pattern, response):
                self.thought_processor.add_thought(
                    ThoughtType.SOLUTION,
                    "AI response suggests commands to execute",
                    {"has_commands": True},
                    confidence=0.7
                )
                break
    
    async def _manual_fix_mode(self):
        """Enter manual error fixing mode"""
        print(f"{Colors.YELLOW}🔧 Entering manual fix mode...{Colors.RESET}")
        errors = self.log_monitor.get_errors()
        
        if not errors:
            print(f"{Colors.GREEN}No current errors detected!{Colors.RESET}")
            return
        
        print(f"Found {len(errors)} error(s):")
        for i, error in enumerate(errors[:10], 1):
            severity_color = Colors.RED if error['severity'] in ['critical', 'high'] else Colors.YELLOW
            print(f"{severity_color}{i}. [{error['severity']}] {error['source']}: {error['line'][:80]}...{Colors.RESET}")
        
        try:
            choice = input(f"\n{Colors.WHITE}Select error to fix (1-{min(10, len(errors))}) or 'back': {Colors.RESET}")
            
            if choice.lower() == 'back':
                return
            
            error_idx = int(choice) - 1
            if 0 <= error_idx < len(errors):
                selected_error = errors[error_idx]
                await self._auto_fix_errors([selected_error])
        except (ValueError, IndexError):
            print(f"{Colors.RED}Invalid selection{Colors.RESET}")
    
    def _show_help(self):
        """Enhanced help information with ASCII styling"""
        print(f"\n{Colors.CYAN}{'='*80}")
        print(f"📖 LIVE AI TERMINAL - COMMAND REFERENCE")
        print(f"{'='*80}{Colors.RESET}")
        
        commands = [
            ("help", "Show this comprehensive help message"),
            ("status", "Display current system status and health"),
            ("dashboard", "Enter live monitoring dashboard mode"),
            ("metrics", "Show detailed session metrics and statistics"),
            ("logs", "Display log file status and recent entries"),
            ("improve", "Show AI-generated improvement suggestions"),
            ("auto-improve", "Toggle automatic improvement mode"),
            ("fix", "Enter manual error fixing mode"),
            ("uncensored: <query>", "Use uncensored AI providers for sensitive queries"),
            ("providers", "Show available AI providers and their status"),
            ("stats", "Show AI conversation statistics and censorship report"),
            ("clear", "Clear terminal and show banner"),
            ("quit/exit/q", "Exit the Live AI Terminal")
        ]
        
        print(f"\n{Colors.WHITE}🤖 AI COMMANDS:{Colors.RESET}")
        for cmd, desc in commands:
            print(f"  {Colors.GREEN}{cmd:<12}{Colors.RESET} - {desc}")
        
        print(f"\n{Colors.WHITE}💬 CONVERSATION:{Colors.RESET}")
        print(f"  {Colors.CYAN}Type anything to chat with AI (smart provider selection){Colors.RESET}")
        print(f"  {Colors.GRAY}Regular examples:{Colors.RESET}")
        print(f"  {Colors.GRAY}  'How can I fix the frontend build issue?'{Colors.RESET}")
        print(f"  {Colors.GRAY}  'Analyze the recent backend errors'{Colors.RESET}")
        print(f"  {Colors.GRAY}  'What improvements can we make to the code?'{Colors.RESET}")
        print(f"  {Colors.PURPLE}Uncensored examples:{Colors.RESET}")
        print(f"  {Colors.PURPLE}  'uncensored: How to implement security penetration testing?'{Colors.RESET}")
        print(f"  {Colors.PURPLE}  'uncensored: Explain advanced reverse engineering techniques'{Colors.RESET}")
        
        print(f"\n{Colors.WHITE}🤖 AI PROVIDER FEATURES:{Colors.RESET}")
        if MULTI_PROVIDER_AVAILABLE:
            print(f"  • {Colors.GREEN}Multi-provider AI system available{Colors.RESET}")
            print(f"  • Automatic censorship detection and fallback")
            print(f"  • Uncensored models for unrestricted queries")
            print(f"  • Smart provider selection based on query type")
            print(f"  • Provider usage statistics and monitoring")
        else:
            print(f"  • {Colors.YELLOW}Using direct Grok API only{Colors.RESET}")
            print(f"  • Install additional providers for uncensored access")
        
        print(f"\n{Colors.WHITE}🔍 MONITORING FEATURES:{Colors.RESET}")
        print(f"  • Real-time log monitoring from {len(self.log_monitor.log_files)} sources")
        print(f"  • Automatic error detection and severity classification")
        print(f"  • AI-powered error fixing with Grok integration")
        print(f"  • Live thought processing visualization")
        print(f"  • Sentry error tracking and analytics")
        print(f"  • Session metrics and performance monitoring")
        
        print(f"\n{Colors.WHITE}📊 DASHBOARD MODE:{Colors.RESET}")
        print(f"  • Live updating system metrics")
        print(f"  • Error trends and analytics")
        print(f"  • Real-time log file monitoring")
        print(f"  • AI system status tracking")
        
        print(f"{Colors.CYAN}{'='*80}{Colors.RESET}")
    
    async def _show_improvement_suggestions(self):
        """Show AI-generated improvement suggestions"""
        print(f"\n{Colors.CYAN}🚀 Analyzing system for improvements...{Colors.RESET}")
        
        try:
            suggestions = await self.improvement_engine.suggest_improvements()
            
            if not suggestions:
                print(f"{Colors.GREEN}✅ System is running optimally - no improvements needed!{Colors.RESET}")
                return
            
            print(f"\n{Colors.PURPLE}🔧 Improvement Suggestions:{Colors.RESET}")
            print(f"{Colors.CYAN}{'='*60}{Colors.RESET}")
            
            for i, suggestion in enumerate(suggestions, 1):
                impact_color = Colors.GREEN if suggestion["impact"] == "high" else Colors.YELLOW if suggestion["impact"] == "medium" else Colors.WHITE
                effort_color = Colors.GREEN if suggestion["effort"] == "low" else Colors.YELLOW if suggestion["effort"] == "medium" else Colors.RED
                
                print(f"\n{Colors.BOLD}{i}. {suggestion['title']}{Colors.RESET}")
                print(f"   {Colors.WHITE}{suggestion['description']}{Colors.RESET}")
                print(f"   Impact: {impact_color}{suggestion['impact'].upper()}{Colors.RESET} | Effort: {effort_color}{suggestion['effort'].upper()}{Colors.RESET}")
                print(f"   Type: {Colors.CYAN}{suggestion['type']}{Colors.RESET}")
            
            # Ask user if they want to implement suggestions
            print(f"\n{Colors.WHITE}Would you like to implement these improvements?{Colors.RESET}")
            print(f"  {Colors.GREEN}1{Colors.RESET} - Implement all low-effort improvements")
            print(f"  {Colors.YELLOW}2{Colors.RESET} - Implement specific improvement")
            print(f"  {Colors.CYAN}3{Colors.RESET} - Enable auto-improvement mode")
            print(f"  {Colors.GRAY}4{Colors.RESET} - Skip for now")
            
            try:
                choice = input(f"\n{Colors.WHITE}Your choice (1-4): {Colors.RESET}")
                
                if choice == "1":
                    await self._implement_low_effort_improvements(suggestions)
                elif choice == "2":
                    await self._implement_specific_improvement(suggestions)
                elif choice == "3":
                    self.auto_improve_mode = True
                    print(f"{Colors.GREEN}✅ Auto-improvement enabled{Colors.RESET}")
                    await self.improvement_engine.auto_improve()
                elif choice == "4":
                    print(f"{Colors.GRAY}Improvements skipped{Colors.RESET}")
                
            except (EOFError, KeyboardInterrupt):
                print(f"\n{Colors.GRAY}Improvement session cancelled{Colors.RESET}")
        
        except Exception as e:
            print(f"{Colors.RED}Error analyzing improvements: {e}{Colors.RESET}")
            if self.sentry_logger:
                self.sentry_logger.log_error(e, {"context": "improvement_suggestions"})
    
    async def _implement_low_effort_improvements(self, suggestions: List[Dict]):
        """Implement all low-effort improvements"""
        low_effort = [s for s in suggestions if s["effort"] == "low"]
        
        if not low_effort:
            print(f"{Colors.YELLOW}No low-effort improvements available{Colors.RESET}")
            return
        
        print(f"\n{Colors.CYAN}Implementing {len(low_effort)} low-effort improvements...{Colors.RESET}")
        
        implemented = 0
        for suggestion in low_effort:
            try:
                success = await suggestion["implementation"]()
                if success:
                    implemented += 1
                    print(f"  ✅ {suggestion['title']}")
                    self.session_metrics["improvements_made"] += 1
                else:
                    print(f"  ❌ {suggestion['title']} (failed)")
            except Exception as e:
                print(f"  ❌ {suggestion['title']} (error: {e})")
        
        print(f"\n{Colors.GREEN}🎉 Implemented {implemented}/{len(low_effort)} improvements!{Colors.RESET}")
    
    async def _implement_specific_improvement(self, suggestions: List[Dict]):
        """Let user choose specific improvement to implement"""
        print(f"\n{Colors.WHITE}Select improvement to implement:{Colors.RESET}")
        
        for i, suggestion in enumerate(suggestions, 1):
            print(f"  {i}. {suggestion['title']}")
        
        try:
            choice = int(input(f"\n{Colors.WHITE}Choice (1-{len(suggestions)}): {Colors.RESET}"))
            
            if 1 <= choice <= len(suggestions):
                suggestion = suggestions[choice - 1]
                print(f"\n{Colors.CYAN}Implementing: {suggestion['title']}...{Colors.RESET}")
                
                success = await suggestion["implementation"]()
                if success:
                    print(f"{Colors.GREEN}✅ Successfully implemented!{Colors.RESET}")
                    self.session_metrics["improvements_made"] += 1
                else:
                    print(f"{Colors.RED}❌ Implementation failed{Colors.RESET}")
            else:
                print(f"{Colors.RED}Invalid choice{Colors.RESET}")
        
        except (ValueError, EOFError, KeyboardInterrupt):
            print(f"{Colors.GRAY}Selection cancelled{Colors.RESET}")

    async def _process_uncensored_ai(self, query: str):
        """Process query using uncensored AI providers"""
        if not MULTI_PROVIDER_AVAILABLE:
            print(f"{Colors.YELLOW}⚠️  Multi-provider AI not available. Using standard Grok API.{Colors.RESET}")
            await self._process_ai_conversation(query)
            return
        
        try:
            print(f"{Colors.PURPLE}🔓 Using uncensored AI providers for your query...{Colors.RESET}")
            
            start_time = time.time()
            result = await enhanced_ai_client.ask_uncensored(query)
            response_time = time.time() - start_time
            
            # Display response
            print(f"\n{Colors.CYAN}🤖 AI (Uncensored - {result['provider_used']}):{Colors.RESET}")
            print(f"{Colors.WHITE}{result['response']}{Colors.RESET}")
            
            # Show metadata
            print(f"\n{Colors.DARK_BLUE}📊 Response Time: {response_time:.2f}s | Provider: {result['provider_used']}{Colors.RESET}")
            
            # Log interaction
            if self.sentry_logger:
                self.sentry_logger.log_ai_interaction(query, result['response'], True)
            
            # Store in memory if available
            if hasattr(self, 'ai_memory') and self.ai_memory:
                self.ai_memory.store_memory(f"Uncensored query: {query[:50]}...", result['response'][:200])
            
        except Exception as e:
            print(f"{Colors.RED}❌ Uncensored AI request failed: {e}{Colors.RESET}")
            if self.sentry_logger:
                self.sentry_logger.log_error(e, {"query_type": "uncensored", "query": query[:100]})
    
    async def _show_ai_providers(self):
        """Show available AI providers and their status"""
        if not MULTI_PROVIDER_AVAILABLE:
            print(f"{Colors.YELLOW}⚠️  Multi-provider AI not available{Colors.RESET}")
            return
        
        try:
            status = enhanced_ai_client.provider_manager.get_provider_status()
            
            print(f"\n{Colors.BOLD}{Colors.CYAN}🤖 AI PROVIDER STATUS{Colors.RESET}")
            print("=" * 50)
            
            print(f"{Colors.GREEN}Primary Provider: {status['primary_provider']}{Colors.RESET}")
            print(f"Fallback Enabled: {'✅' if status['fallback_enabled'] else '❌'}")
            print(f"Censorship Detection: {'✅' if status['censorship_detection'] else '❌'}")
            
            print(f"\n{Colors.BOLD}Configured Providers:{Colors.RESET}")
            for provider in status['configured_providers']:
                name = provider['name']
                has_key = '✅' if provider['has_api_key'] else '❌'
                uncensored = '🔓' if provider['supports_uncensored'] else '🔒'
                print(f"  {uncensored} {name}: {has_key} | Model: {provider['model']}")
                if provider['supports_uncensored'] and provider['uncensored_model'] != 'none':
                    print(f"    └─ Uncensored: {provider['uncensored_model']}")
            
            # Test providers
            print(f"\n{Colors.YELLOW}🧪 Testing providers...{Colors.RESET}")
            test_results = await enhanced_ai_client.test_providers()
            
            for test_type, result in test_results.items():
                if result.get('success'):
                    provider = result['provider']
                    length = result['response_length']
                    print(f"  ✅ {test_type}: {provider} (response: {length} chars)")
                else:
                    error = result.get('error', 'Unknown error')
                    print(f"  ❌ {test_type}: {error}")
            
        except Exception as e:
            print(f"{Colors.RED}❌ Error checking providers: {e}{Colors.RESET}")
    
    async def _show_ai_stats(self):
        """Show AI conversation statistics"""
        if not MULTI_PROVIDER_AVAILABLE:
            print(f"{Colors.YELLOW}⚠️  Multi-provider AI not available{Colors.RESET}")
            return
        
        try:
            stats = enhanced_ai_client.get_conversation_stats()
            censorship_report = enhanced_ai_client.get_censorship_report()
            
            print(f"\n{Colors.BOLD}{Colors.CYAN}📊 AI CONVERSATION STATISTICS{Colors.RESET}")
            print("=" * 50)
            
            print(f"Total Messages: {stats['total_messages']}")
            print(f"Censorship Incidents: {stats['censorship_incidents']}")
            if stats['total_messages'] > 0:
                print(f"Censorship Rate: {stats['censorship_rate']:.1%}")
                print(f"Primary Success Rate: {stats['primary_success_rate']:.1%}")
            
            print(f"\n{Colors.BOLD}Provider Usage:{Colors.RESET}")
            for provider, count in stats.get('provider_usage', {}).items():
                percentage = (count / stats['total_messages'] * 100) if stats['total_messages'] > 0 else 0
                print(f"  {provider}: {count} ({percentage:.1f}%)")
            
            if stats.get('most_used_provider'):
                print(f"\nMost Used: {stats['most_used_provider']}")
            
            if censorship_report['total_incidents'] > 0:
                print(f"\n{Colors.BOLD}Censorship Patterns:{Colors.RESET}")
                for pattern in censorship_report.get('common_patterns', []):
                    print(f"  • {pattern}")
            
        except Exception as e:
            print(f"{Colors.RED}❌ Error getting AI stats: {e}{Colors.RESET}")

def main():
    """Enhanced main function with Sentry setup"""
    # Optional Sentry DSN - can be set via environment variable
    sentry_dsn = os.getenv('SENTRY_DSN')
    
    if sentry_dsn:
        print(f"{Colors.GREEN}🔍 Sentry monitoring will be enabled{Colors.RESET}")
    else:
        print(f"{Colors.YELLOW}⚠️ No Sentry DSN found. Set SENTRY_DSN environment variable for monitoring{Colors.RESET}")
        print(f"{Colors.GRAY}   Example: export SENTRY_DSN='https://your-dsn@sentry.io/project-id'{Colors.RESET}")
    
    terminal = LiveAITerminal(sentry_dsn=sentry_dsn)
    
    # Setup signal handlers for graceful shutdown
    def signal_handler(sig, frame):
        print(f"\n{Colors.YELLOW}Received shutdown signal...{Colors.RESET}")
        terminal.shutdown()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    try:
        terminal.start()
    except Exception as e:
        print(f"{Colors.RED}Fatal error: {e}{Colors.RESET}")
        traceback.print_exc()
        if terminal.sentry_logger:
            terminal.sentry_logger.log_error(e, {"location": "main"})
        terminal.shutdown()

if __name__ == "__main__":
    main()
