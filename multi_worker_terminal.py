#!/usr/bin/env python3
"""
Multi-Worker AI Terminal Interface
=================================
Terminal interface for managing multiple Grok AI workers via Celery/Redis
"""

import asyncio
import os
import sys
import time
import json
from datetime import datetime
from pathlib import Path
import subprocess
import threading

# Import the multi-worker system
from ai_multi_worker import coordinator, app as celery_app
from ai_thought_processor import Colors

class MultiWorkerTerminal:
    """Enhanced terminal interface with multi-worker AI support"""
    
    def __init__(self):
        self.coordinator = coordinator
        self.running = False
        self.command_history = []
        
    def start(self):
        """Start the multi-worker terminal"""
        self.running = True
        
        # Display startup banner
        self._show_startup_banner()
        
        # Check Redis/Celery status
        self._check_dependencies()
        
        # Main command loop
        try:
            asyncio.run(self._main_loop())
        except KeyboardInterrupt:
            self._shutdown()
    
    def _show_startup_banner(self):
        """Display multi-worker AI banner"""
        banner = f"""{Colors.CYAN}{Colors.BOLD}
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║    🤖 MULTI-WORKER AI TERMINAL 🤖                                           ║
║                                                                              ║
║    Worker 1: 🔧 Code Generation & File Editing                              ║
║    Worker 2: 🔍 Quality Assurance & Linting                                 ║
║    Worker 3: 🧠 Memory Management & Indexing                                ║
║                                                                              ║
║    Powered by: Grok AI + Celery + Redis                                     ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝{Colors.RESET}"""
        print(banner)
    
    def _check_dependencies(self):
        """Check if Redis and Celery are available"""
        print(f"\n{Colors.YELLOW}🔍 Checking dependencies...{Colors.RESET}")
        
        # Check Redis
        try:
            from ai_multi_worker import redis_client
            redis_client.ping()
            print(f"{Colors.GREEN}✅ Redis connection successful{Colors.RESET}")
        except Exception as e:
            print(f"{Colors.RED}❌ Redis connection failed: {e}{Colors.RESET}")
            print(f"{Colors.YELLOW}💡 Start Redis with: redis-server{Colors.RESET}")
        
        # Check if Celery workers are running
        try:
            active_workers = celery_app.control.active()
            worker_count = len(active_workers)
            print(f"{Colors.GREEN}✅ {worker_count} Celery workers active{Colors.RESET}")
            
            if worker_count == 0:
                print(f"{Colors.YELLOW}💡 Start workers with: celery -A ai_multi_worker worker --loglevel=info{Colors.RESET}")
        except Exception as e:
            print(f"{Colors.RED}❌ Could not check Celery workers: {e}{Colors.RESET}")
    
    async def _main_loop(self):
        """Main command processing loop"""
        while self.running:
            try:
                # Show prompt
                user_input = await self._get_user_input()
                
                if not user_input:
                    continue
                    
                # Add to history
                self.command_history.append({
                    'command': user_input,
                    'timestamp': datetime.now()
                })
                
                # Process command
                await self._process_command(user_input)
                
            except Exception as e:
                print(f"{Colors.RED}Error: {e}{Colors.RESET}")
    
    async def _get_user_input(self):
        """Get user input with enhanced prompt"""
        prompt = f"\n{Colors.BOLD}{Colors.WHITE}🤖 Multi-AI> {Colors.RESET}"
        print(prompt, end="")
        
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, input)
    
    async def _process_command(self, command: str):
        """Process user commands"""
        cmd_parts = command.strip().split()
        if not cmd_parts:
            return
        
        cmd = cmd_parts[0].lower()
        args = cmd_parts[1:] if len(cmd_parts) > 1 else []
        
        if cmd in ['quit', 'exit', 'q']:
            self.running = False
        
        elif cmd == 'help':
            self._show_help()
        
        elif cmd == 'status':
            self._show_system_status()
        
        elif cmd == 'dashboard':
            self.coordinator.show_worker_dashboard()
        
        elif cmd == 'workers':
            await self._show_worker_info()
        
        elif cmd == 'edit':
            await self._handle_edit_command(args)
        
        elif cmd == 'create':
            await self._handle_create_command(args)
        
        elif cmd == 'review':
            await self._handle_review_command(args)
        
        elif cmd == 'pipeline':
            await self._handle_pipeline_command(args)
        
        elif cmd == 'search':
            await self._handle_search_command(args)
        
        elif cmd == 'tasks':
            self._show_active_tasks()
        
        elif cmd == 'clear':
            os.system('clear' if os.name == 'posix' else 'cls')
            self._show_startup_banner()
        
        else:
            # Default: treat as a general AI request
            await self._handle_ai_request(command)
    
    def _show_help(self):
        """Show available commands"""
        help_text = f"""
{Colors.BOLD}{Colors.CYAN}🤖 Multi-Worker AI Commands:{Colors.RESET}

{Colors.GREEN}File Operations:{Colors.RESET}
  edit <file> <description>     - Edit a file using Worker 1
  create <file> <description>   - Create a new file using Worker 1
  review <file>                 - Quality review using Worker 2
  pipeline <file> <description> - Full pipeline (all workers)

{Colors.YELLOW}Worker Management:{Colors.RESET}
  workers                       - Show worker information
  dashboard                     - Real-time worker dashboard
  tasks                         - Show active tasks
  status                        - System status

{Colors.CYAN}AI Operations:{Colors.RESET}
  search <query>                - Search indexed knowledge (Worker 3)
  <any text>                    - Send request to available worker

{Colors.WHITE}System:{Colors.RESET}
  help                          - Show this help
  clear                         - Clear screen
  quit/exit/q                   - Exit terminal

{Colors.BOLD}Examples:{Colors.RESET}
  edit src/main.py "add error handling to the login function"
  create utils/helpers.py "utility functions for data validation"
  pipeline frontend/app.js "add dark mode toggle feature"
  search "authentication patterns"
"""
        print(help_text)
    
    def _show_system_status(self):
        """Show system status"""
        print(f"\n{Colors.BOLD}{Colors.CYAN}🖥️  System Status:{Colors.RESET}")
        
        # Redis status
        try:
            from ai_multi_worker import redis_client
            redis_info = redis_client.info()
            print(f"{Colors.GREEN}✅ Redis: Connected (v{redis_info.get('redis_version', 'unknown')}){Colors.RESET}")
        except:
            print(f"{Colors.RED}❌ Redis: Disconnected{Colors.RESET}")
        
        # Celery workers
        try:
            active_workers = celery_app.control.active()
            print(f"{Colors.GREEN}✅ Celery Workers: {len(active_workers)} active{Colors.RESET}")
        except:
            print(f"{Colors.RED}❌ Celery Workers: Not available{Colors.RESET}")
        
        # Active tasks
        active_count = len([t for t in self.coordinator.active_tasks.values() if t['status'] == 'pending'])
        print(f"{Colors.YELLOW}📊 Active Tasks: {active_count}{Colors.RESET}")
        
        # Command history
        print(f"{Colors.WHITE}📝 Commands Executed: {len(self.command_history)}{Colors.RESET}")
    
    async def _show_worker_info(self):
        """Show detailed worker information"""
        print(f"\n{Colors.BOLD}{Colors.CYAN}🔧 Worker Information:{Colors.RESET}")
        
        try:
            # Get worker stats from Celery
            stats = celery_app.control.stats()
            active_workers = celery_app.control.active()
            
            print(f"\n{Colors.GREEN}Worker 1 - Code Generation:{Colors.RESET}")
            print(f"  Purpose: File editing, code generation, bug fixes")
            print(f"  Queue: code_queue")
            print(f"  Status: {'🟢 Active' if any('code_worker' in str(w) for w in active_workers.values()) else '🔴 Inactive'}")
            
            print(f"\n{Colors.YELLOW}Worker 2 - Quality Assurance:{Colors.RESET}")
            print(f"  Purpose: Code review, linting, security checks")
            print(f"  Queue: quality_queue")
            print(f"  Status: {'🟢 Active' if any('quality_worker' in str(w) for w in active_workers.values()) else '🔴 Inactive'}")
            
            print(f"\n{Colors.CYAN}Worker 3 - Memory & Indexing:{Colors.RESET}")
            print(f"  Purpose: Knowledge indexing, pattern recognition, organization")
            print(f"  Queue: memory_queue")
            print(f"  Status: {'🟢 Active' if any('memory_worker' in str(w) for w in active_workers.values()) else '🔴 Inactive'}")
            
        except Exception as e:
            print(f"{Colors.RED}Could not retrieve worker information: {e}{Colors.RESET}")
    
    async def _handle_edit_command(self, args):
        """Handle file editing command"""
        if len(args) < 2:
            print(f"{Colors.RED}Usage: edit <file_path> <description>{Colors.RESET}")
            return
        
        file_path = args[0]
        description = ' '.join(args[1:])
        
        print(f"\n{Colors.GREEN}🔧 Assigning edit task to Worker 1...{Colors.RESET}")
        task_id = self.coordinator.assign_code_task('edit_file', description, file_path)
        
        print(f"{Colors.YELLOW}⏳ Waiting for completion...{Colors.RESET}")
        result = self.coordinator.wait_for_task(task_id, timeout=120)
        
        if result['status'] == 'success':
            print(f"{Colors.GREEN}✅ File edited successfully!{Colors.RESET}")
            print(f"📁 File: {result['result']['file_path']}")
            print(f"📝 Lines: {result['result']['lines_written']}")
        else:
            print(f"{Colors.RED}❌ Edit failed: {result.get('error', 'Unknown error')}{Colors.RESET}")
    
    async def _handle_create_command(self, args):
        """Handle file creation command"""
        if len(args) < 2:
            print(f"{Colors.RED}Usage: create <file_path> <description>{Colors.RESET}")
            return
        
        file_path = args[0]
        description = ' '.join(args[1:])
        
        # Check if file already exists
        if os.path.exists(file_path):
            response = input(f"{Colors.YELLOW}File exists. Overwrite? (y/N): {Colors.RESET}")
            if response.lower() != 'y':
                return
        
        print(f"\n{Colors.GREEN}🔧 Creating file with Worker 1...{Colors.RESET}")
        task_id = self.coordinator.assign_code_task('edit_file', f"Create new file: {description}", file_path)
        
        print(f"{Colors.YELLOW}⏳ Waiting for completion...{Colors.RESET}")
        result = self.coordinator.wait_for_task(task_id, timeout=120)
        
        if result['status'] == 'success':
            print(f"{Colors.GREEN}✅ File created successfully!{Colors.RESET}")
            print(f"📁 File: {result['result']['file_path']}")
        else:
            print(f"{Colors.RED}❌ Creation failed: {result.get('error', 'Unknown error')}{Colors.RESET}")
    
    async def _handle_review_command(self, args):
        """Handle code review command"""
        if len(args) < 1:
            print(f"{Colors.RED}Usage: review <file_path>{Colors.RESET}")
            return
        
        file_path = args[0]
        
        if not os.path.exists(file_path):
            print(f"{Colors.RED}File not found: {file_path}{Colors.RESET}")
            return
        
        # Read file content
        with open(file_path, 'r') as f:
            content = f.read()
        
        print(f"\n{Colors.YELLOW}🔍 Assigning review task to Worker 2...{Colors.RESET}")
        task_id = self.coordinator.assign_quality_task(content, file_path, 'manual_review')
        
        print(f"{Colors.YELLOW}⏳ Analyzing code quality...{Colors.RESET}")
        result = self.coordinator.wait_for_task(task_id, timeout=120)
        
        if result['status'] == 'success':
            review_data = result['result']
            print(f"\n{Colors.GREEN}✅ Code Review Complete!{Colors.RESET}")
            print(f"📊 Quality Score: {review_data.get('score', 'N/A')}/100")
            
            if review_data.get('issues_found'):
                print(f"\n{Colors.YELLOW}🚨 Issues Found:{Colors.RESET}")
                for issue in review_data.get('issues', []):
                    severity_color = Colors.RED if issue['severity'] == 'high' else Colors.YELLOW
                    print(f"  {severity_color}{issue['severity'].upper()}: Line {issue.get('line', '?')} - {issue['issue']}{Colors.RESET}")
            else:
                print(f"{Colors.GREEN}✅ No issues found!{Colors.RESET}")
                
        else:
            print(f"{Colors.RED}❌ Review failed: {result.get('error', 'Unknown error')}{Colors.RESET}")
    
    async def _handle_pipeline_command(self, args):
        """Handle full pipeline processing"""
        if len(args) < 2:
            print(f"{Colors.RED}Usage: pipeline <file_path> <description>{Colors.RESET}")
            return
        
        file_path = args[0]
        description = ' '.join(args[1:])
        
        print(f"\n{Colors.BOLD}{Colors.CYAN}🚀 Starting Full AI Pipeline...{Colors.RESET}")
        result = self.coordinator.process_file_with_pipeline(file_path, description)
        
        if result['status'] == 'success':
            print(f"\n{Colors.GREEN}🎉 Pipeline completed successfully!{Colors.RESET}")
            print(f"📁 File: {result['file_path']}")
            print(f"📊 Quality Score: {result['quality_score']}/100")
            print(f"🔗 Pipeline ID: {result['pipeline_id']}")
        else:
            print(f"{Colors.RED}❌ Pipeline failed at {result['step']}: {result['error']}{Colors.RESET}")
    
    async def _handle_search_command(self, args):
        """Handle knowledge search"""
        if len(args) < 1:
            print(f"{Colors.RED}Usage: search <query>{Colors.RESET}")
            return
        
        query = ' '.join(args)
        
        print(f"\n{Colors.CYAN}🔍 Searching knowledge base...{Colors.RESET}")
        task_id = self.coordinator.assign_memory_task('search', {'query': query})
        
        result = self.coordinator.wait_for_task(task_id, timeout=30)
        
        if result['status'] == 'success':
            search_results = result['result']['results']
            print(f"\n{Colors.GREEN}🔍 Found {len(search_results)} results:{Colors.RESET}")
            
            for i, item in enumerate(search_results[:5], 1):  # Show top 5
                print(f"\n{i}. {Colors.CYAN}{item.get('file_path', 'Unknown')}{Colors.RESET}")
                print(f"   📝 {item.get('task_description', 'No description')}")
                print(f"   🕐 {item.get('timestamp', 'Unknown time')}")
        else:
            print(f"{Colors.RED}❌ Search failed: {result.get('error', 'Unknown error')}{Colors.RESET}")
    
    async def _handle_ai_request(self, request: str):
        """Handle general AI requests"""
        print(f"\n{Colors.CYAN}🤖 Processing AI request...{Colors.RESET}")
        
        # Determine which worker should handle this
        if any(keyword in request.lower() for keyword in ['edit', 'create', 'code', 'function', 'class']):
            task_id = self.coordinator.assign_code_task('general_request', request)
            worker_name = "Code Worker"
        else:
            # Use memory worker for general queries
            task_id = self.coordinator.assign_memory_task('search', {'query': request})
            worker_name = "Memory Worker"
        
        print(f"{Colors.YELLOW}⏳ {worker_name} processing...{Colors.RESET}")
        result = self.coordinator.wait_for_task(task_id, timeout=120)
        
        if result['status'] == 'success':
            print(f"\n{Colors.GREEN}🤖 AI Response:{Colors.RESET}")
            if 'result' in result and isinstance(result['result'], dict):
                for key, value in result['result'].items():
                    if key not in ['task_id', 'status']:
                        print(f"{Colors.WHITE}{key}: {value}{Colors.RESET}")
            else:
                print(f"{Colors.WHITE}{result.get('result', 'No response')}{Colors.RESET}")
        else:
            print(f"{Colors.RED}❌ Request failed: {result.get('error', 'Unknown error')}{Colors.RESET}")
    
    def _show_active_tasks(self):
        """Show currently active tasks"""
        print(f"\n{Colors.BOLD}{Colors.CYAN}📋 Active Tasks:{Colors.RESET}")
        
        if not self.coordinator.active_tasks:
            print(f"{Colors.YELLOW}No active tasks{Colors.RESET}")
            return
        
        for task_id, task_info in self.coordinator.active_tasks.items():
            status_color = Colors.GREEN if task_info['status'] == 'success' else Colors.YELLOW if task_info['status'] == 'pending' else Colors.RED
            print(f"{status_color}🔧 {task_id}: {task_info['status']}{Colors.RESET}")
            print(f"   Worker: {task_info['worker']}")
            print(f"   Started: {task_info['data'].get('timestamp', 'Unknown')}")
    
    def _shutdown(self):
        """Shutdown the terminal"""
        print(f"\n{Colors.YELLOW}Shutting down Multi-Worker AI Terminal...{Colors.RESET}")
        self.running = False
        print(f"{Colors.GREEN}✅ Goodbye!{Colors.RESET}")

if __name__ == "__main__":
    terminal = MultiWorkerTerminal()
    terminal.start()
