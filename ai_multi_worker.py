#!/usr/bin/env python3
"""
Multi-Worker AI System Architecture
==================================
Distributed AI workers using Celery and Redis for parallel processing:
- Worker 1: Code generation and file editing
- Worker 2: Code quality assurance and linting
- Worker 3: Indexing, memory management, and organization
"""

import asyncio
import json
import os
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from pathlib import Path
import subprocess
import threading

from celery import Celery
from celery.result import AsyncResult
import redis

# Import our AI systems
try:
    from enhanced_grok_integration import EnhancedGrokIntegration
    from ai_memory_system import ai_memory
    from ai_thought_processor import AIThoughtProcessor, ThoughtType, Colors
    from enhanced_ai_client import enhanced_ai_client, ask_ai, ask_uncensored
    MULTI_PROVIDER_AVAILABLE = True
except ImportError as e:
    print(f"Warning: AI system import failed: {e}")
    MULTI_PROVIDER_AVAILABLE = False

# Celery app configuration
app = Celery('ai_workers')
app.config_from_object({
    'broker_url': 'redis://localhost:6379/0',
    'result_backend': 'redis://localhost:6379/0',
    'task_serializer': 'json',
    'accept_content': ['json'],
    'result_serializer': 'json',
    'timezone': 'UTC',
    'enable_utc': True,
    'task_routes': {
        'ai_workers.code_worker': {'queue': 'code_queue'},
        'ai_workers.quality_worker': {'queue': 'quality_queue'},
        'ai_workers.memory_worker': {'queue': 'memory_queue'},
    },
    'worker_prefetch_multiplier': 1,
    'task_acks_late': True,
})

# Redis client for coordination
redis_client = redis.Redis(host='localhost', port=6379, db=1, decode_responses=True)

class WorkerCoordinator:
    """Coordinates multiple AI workers for different tasks"""
    
    def __init__(self):
        self.grok_integration = EnhancedGrokIntegration()
        self.thought_processor = AIThoughtProcessor()
        self.active_tasks = {}
        self.worker_stats = {
            'code_worker': {'tasks_completed': 0, 'errors': 0, 'avg_time': 0},
            'quality_worker': {'tasks_completed': 0, 'errors': 0, 'avg_time': 0},
            'memory_worker': {'tasks_completed': 0, 'errors': 0, 'avg_time': 0}
        }
    
    def assign_code_task(self, task_type: str, content: str, file_path: str = None) -> str:
        """Assign a code generation/editing task to Worker 1"""
        task_id = f"code_{int(time.time())}"
        
        task_data = {
            'task_id': task_id,
            'task_type': task_type,
            'content': content,
            'file_path': file_path,
            'timestamp': datetime.now().isoformat(),
            'priority': 'high' if task_type in ['fix_error', 'security_fix'] else 'normal'
        }
        
        # Submit to Celery
        result = code_worker.delay(task_data)
        self.active_tasks[task_id] = {
            'celery_id': result.id,
            'worker': 'code_worker',
            'status': 'pending',
            'data': task_data
        }
        
        print(f"{Colors.GREEN}🔧 Assigned code task {task_id} to Worker 1 (Code Generation){Colors.RESET}")
        return task_id
    
    def assign_quality_task(self, code_content: str, file_path: str, original_task_id: str) -> str:
        """Assign a quality assurance task to Worker 2"""
        task_id = f"quality_{int(time.time())}"
        
        task_data = {
            'task_id': task_id,
            'code_content': code_content,
            'file_path': file_path,
            'original_task_id': original_task_id,
            'timestamp': datetime.now().isoformat(),
            'checks': ['syntax', 'style', 'security', 'performance', 'best_practices']
        }
        
        result = quality_worker.delay(task_data)
        self.active_tasks[task_id] = {
            'celery_id': result.id,
            'worker': 'quality_worker',
            'status': 'pending',
            'data': task_data
        }
        
        print(f"{Colors.YELLOW}🔍 Assigned quality check {task_id} to Worker 2 (QA){Colors.RESET}")
        return task_id
    
    def assign_memory_task(self, operation: str, data: Dict) -> str:
        """Assign a memory/indexing task to Worker 3"""
        task_id = f"memory_{int(time.time())}"
        
        task_data = {
            'task_id': task_id,
            'operation': operation,  # 'index', 'update', 'search', 'organize'
            'data': data,
            'timestamp': datetime.now().isoformat()
        }
        
        result = memory_worker.delay(task_data)
        self.active_tasks[task_id] = {
            'celery_id': result.id,
            'worker': 'memory_worker',
            'status': 'pending',
            'data': task_data
        }
        
        print(f"{Colors.CYAN}🧠 Assigned memory task {task_id} to Worker 3 (Memory/Indexing){Colors.RESET}")
        return task_id
    
    def get_task_status(self, task_id: str) -> Dict:
        """Get status of a specific task"""
        if task_id not in self.active_tasks:
            return {'status': 'not_found'}
        
        task_info = self.active_tasks[task_id]
        celery_result = AsyncResult(task_info['celery_id'], app=app)
        
        task_info['status'] = celery_result.status.lower()
        if celery_result.ready():
            if celery_result.successful():
                task_info['result'] = celery_result.result
            else:
                task_info['error'] = str(celery_result.info)
        
        return task_info
    
    def wait_for_task(self, task_id: str, timeout: int = 300) -> Dict:
        """Wait for a task to complete with timeout"""
        start_time = time.time()
        
        while time.time() - start_time < timeout:
            status = self.get_task_status(task_id)
            if status['status'] in ['success', 'failure']:
                return status
            time.sleep(1)
        
        return {'status': 'timeout', 'message': f'Task {task_id} timed out after {timeout}s'}
    
    def process_file_with_pipeline(self, file_path: str, task_description: str) -> Dict:
        """Process a file through the complete AI pipeline"""
        pipeline_id = f"pipeline_{int(time.time())}"
        
        print(f"\n{Colors.BOLD}{Colors.WHITE}🚀 Starting AI Pipeline {pipeline_id}{Colors.RESET}")
        print(f"📁 File: {file_path}")
        print(f"📋 Task: {task_description}")
        
        # Step 1: Code Worker generates/modifies code
        print(f"\n{Colors.GREEN}Step 1: Code Generation/Editing{Colors.RESET}")
        code_task_id = self.assign_code_task('edit_file', task_description, file_path)
        code_result = self.wait_for_task(code_task_id)
        
        if code_result['status'] != 'success':
            return {'status': 'failed', 'step': 'code_generation', 'error': code_result}
        
        generated_code = code_result['result']['code']
        
        # Step 2: Quality Worker reviews the code
        print(f"\n{Colors.YELLOW}Step 2: Quality Assurance{Colors.RESET}")
        quality_task_id = self.assign_quality_task(generated_code, file_path, code_task_id)
        quality_result = self.wait_for_task(quality_task_id)
        
        if quality_result['status'] != 'success':
            return {'status': 'failed', 'step': 'quality_assurance', 'error': quality_result}
        
        # Step 3: Apply fixes if needed
        quality_feedback = quality_result['result']
        if quality_feedback['issues_found']:
            print(f"\n{Colors.ORANGE}Step 2.1: Applying Quality Fixes{Colors.RESET}")
            fix_task_id = self.assign_code_task('apply_fixes', 
                                              json.dumps(quality_feedback['fixes']), 
                                              file_path)
            fix_result = self.wait_for_task(fix_task_id)
            if fix_result['status'] == 'success':
                generated_code = fix_result['result']['code']
        
        # Step 4: Memory Worker indexes the changes
        print(f"\n{Colors.CYAN}Step 3: Memory & Indexing{Colors.RESET}")
        memory_task_id = self.assign_memory_task('index', {
            'file_path': file_path,
            'code': generated_code,
            'task_description': task_description,
            'pipeline_id': pipeline_id
        })
        memory_result = self.wait_for_task(memory_task_id)
        
        # Final result
        pipeline_result = {
            'pipeline_id': pipeline_id,
            'status': 'success',
            'file_path': file_path,
            'final_code': generated_code,
            'quality_score': quality_feedback.get('score', 0),
            'steps_completed': ['code_generation', 'quality_assurance', 'memory_indexing'],
            'task_ids': [code_task_id, quality_task_id, memory_task_id]
        }
        
        print(f"\n{Colors.GREEN}✅ Pipeline {pipeline_id} completed successfully!{Colors.RESET}")
        return pipeline_result
    
    def show_worker_dashboard(self):
        """Display real-time worker status dashboard"""
        print(f"\n{Colors.BOLD}{Colors.CYAN}🤖 AI WORKERS DASHBOARD{Colors.RESET}")
        print(f"{Colors.CYAN}{'='*80}{Colors.RESET}")
        
        # Worker status
        for worker_name, stats in self.worker_stats.items():
            status_color = Colors.GREEN if stats['errors'] == 0 else Colors.YELLOW
            print(f"{status_color}🔧 {worker_name.replace('_', ' ').title()}:{Colors.RESET}")
            print(f"   Tasks: {stats['tasks_completed']} | Errors: {stats['errors']} | Avg Time: {stats['avg_time']:.2f}s")
        
        # Active tasks
        active_count = len([t for t in self.active_tasks.values() if t['status'] == 'pending'])
        print(f"\n{Colors.WHITE}📊 Active Tasks: {active_count}{Colors.RESET}")
        
        # Queue status (Redis)
        try:
            queue_lengths = {
                'code_queue': redis_client.llen('celery:code_queue'),
                'quality_queue': redis_client.llen('celery:quality_queue'),
                'memory_queue': redis_client.llen('celery:memory_queue')
            }
            
            print(f"{Colors.WHITE}📋 Queue Status:{Colors.RESET}")
            for queue, length in queue_lengths.items():
                print(f"   {queue}: {length} pending")
        except Exception:
            print(f"{Colors.RED}❌ Could not connect to Redis{Colors.RESET}")
        
        print(f"{Colors.CYAN}{'='*80}{Colors.RESET}")

# Celery Tasks
@app.task(bind=True, name='ai_workers.code_worker')
def code_worker(self, task_data):
    """Worker 1: Code Generation and File Editing with Smart AI Selection"""
    try:
        task_id = task_data['task_id']
        task_type = task_data['task_type']
        content = task_data['content']
        file_path = task_data.get('file_path')
        
        print(f"[Worker 1] Processing {task_type} task: {task_id}")
        
        if task_type == 'edit_file':
            # Read existing file if it exists
            existing_content = ""
            if file_path and os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    existing_content = f.read()
            
            # Generate/edit code using enhanced AI client
            prompt = f"""
            Task: {content}
            File: {file_path}
            
            Existing content:
            {existing_content}
            
            Please provide the complete updated file content. Be specific and practical.
            Focus on clean, maintainable code that follows best practices.
            """
            
            # Use smart AI client - automatically handles provider selection
            if MULTI_PROVIDER_AVAILABLE:
                import asyncio
                try:
                    # Use smart chat for automatic provider selection
                    result = asyncio.run(enhanced_ai_client.smart_chat(prompt))
                    code_result = result['response']
                    ai_provider = result['provider_used']
                    print(f"[Worker 1] Used AI provider: {ai_provider}")
                except Exception as e:
                    print(f"[Worker 1] Enhanced AI failed, falling back to Grok: {e}")
                    # Fallback to direct Grok
                    grok = EnhancedGrokIntegration()
                    code_result = grok.call_grok(prompt)
                    ai_provider = "grok_fallback"
            else:
                # Use direct Grok integration
                grok = EnhancedGrokIntegration()
                code_result = grok.call_grok(prompt)
                ai_provider = "grok_direct"
            
            # Extract code from response
            if "```" in code_result:
                code_blocks = code_result.split("```")
                for i, block in enumerate(code_blocks):
                    if i % 2 == 1:  # Odd indices are code blocks
                        # Remove language identifier if present
                        lines = block.strip().split('\n')
                        if lines[0] in ['python', 'javascript', 'typescript', 'html', 'css', 'bash', 'json', 'yaml']:
                            code_result = '\n'.join(lines[1:])
                        else:
                            code_result = block.strip()
                        break
            
            # Write to file if path provided
            if file_path:
                os.makedirs(os.path.dirname(file_path), exist_ok=True)
                with open(file_path, 'w') as f:
                    f.write(code_result)
                print(f"[Worker 1] Updated file: {file_path}")
            
            return {
                'task_id': task_id,
                'status': 'success',
                'code': code_result,
                'file_path': file_path,
                'lines_written': len(code_result.split('\n')),
                'ai_provider': ai_provider
            }
        
        elif task_type == 'apply_fixes':
            # Apply quality fixes to code
            fixes = json.loads(content)
            
            if file_path and os.path.exists(file_path):
                with open(file_path, 'r') as f:
                    current_code = f.read()
                
                # Apply each fix using enhanced AI
                for fix in fixes:
                    prompt = f"""
                    Apply this fix to the code:
                    Fix: {fix['description']}
                    Issue: {fix['issue']}
                    
                    Current code:
                    {current_code}
                    
                    Provide the corrected code:
                    """
                    
                    if MULTI_PROVIDER_AVAILABLE:
                        import asyncio
                        try:
                            result = asyncio.run(enhanced_ai_client.smart_chat(prompt))
                            current_code = result['response']
                        except Exception:
                            grok = EnhancedGrokIntegration()
                            current_code = grok.call_grok(prompt)
                    else:
                        grok = EnhancedGrokIntegration()
                        current_code = grok.call_grok(prompt)
                    
                    # Extract code block
                    if "```" in current_code:
                        code_blocks = current_code.split("```")
                        for i, block in enumerate(code_blocks):
                            if i % 2 == 1:
                                current_code = block.strip()
                                break
                
                # Write updated code
                with open(file_path, 'w') as f:
                    f.write(current_code)
                
                return {
                    'task_id': task_id,
                    'status': 'success',
                    'code': current_code,
                    'fixes_applied': len(fixes)
                }
        
        return {'task_id': task_id, 'status': 'error', 'message': f'Unknown task type: {task_type}'}
        
    except Exception as e:
        return {'task_id': task_data.get('task_id', 'unknown'), 'status': 'error', 'message': str(e)}

@app.task(bind=True, name='ai_workers.quality_worker')
def quality_worker(self, task_data):
    """Worker 2: Code Quality Assurance with Enhanced AI Analysis"""
    try:
        task_id = task_data['task_id']
        code_content = task_data['code_content']
        file_path = task_data['file_path']
        checks = task_data['checks']
        
        print(f"[Worker 2] Quality checking task: {task_id}")
        
        # Analyze code quality using enhanced AI
        prompt = f"""
        Perform a comprehensive code quality analysis on this code:
        
        File: {file_path}
        Code:
        {code_content}
        
        Check for:
        - Syntax errors
        - Style issues (PEP8, best practices)
        - Security vulnerabilities
        - Performance issues
        - Code organization
        - Documentation
        
        Respond in JSON format:
        {{
            "score": 85,
            "issues_found": true/false,
            "issues": [
                {{"severity": "high/medium/low", "line": 10, "issue": "description", "fix": "suggested fix"}}
            ],
            "fixes": [
                {{"description": "what to fix", "issue": "the problem", "priority": "high/medium/low"}}
            ],
            "suggestions": ["general improvements"]
        }}
        """
        
        # Use enhanced AI client for potentially technical/detailed analysis
        if MULTI_PROVIDER_AVAILABLE:
            import asyncio
            try:
                # Use smart chat - may switch to uncensored for detailed security analysis
                result = asyncio.run(enhanced_ai_client.smart_chat(prompt))
                quality_result = result['response']
                ai_provider = result['provider_used']
                print(f"[Worker 2] Used AI provider: {ai_provider}")
            except Exception as e:
                print(f"[Worker 2] Enhanced AI failed, falling back to Grok: {e}")
                grok = EnhancedGrokIntegration()
                quality_result = grok.call_grok(prompt)
                ai_provider = "grok_fallback"
        else:
            grok = EnhancedGrokIntegration()
            quality_result = grok.call_grok(prompt)
            ai_provider = "grok_direct"
        
        # Parse JSON response
        try:
            if "```json" in quality_result:
                json_part = quality_result.split("```json")[1].split("```")[0]
            elif "```" in quality_result:
                # Try to find any JSON in code blocks
                code_blocks = quality_result.split("```")
                for block in code_blocks:
                    if block.strip().startswith('{'):
                        json_part = block
                        break
                else:
                    json_part = quality_result
            else:
                json_part = quality_result
            
            quality_data = json.loads(json_part.strip())
        except:
            # Fallback if JSON parsing fails
            quality_data = {
                "score": 70,
                "issues_found": False,
                "issues": [],
                "fixes": [],
                "suggestions": ["Code review completed - JSON parsing failed, manual review recommended"]
            }
        
        # Run additional automated checks
        automated_issues = []
        
        # Check for common Python issues
        if file_path and file_path.endswith('.py'):
            try:
                # Basic syntax check
                compile(code_content, file_path, 'exec')
            except SyntaxError as e:
                automated_issues.append({
                    "severity": "high",
                    "line": e.lineno or 0,
                    "issue": f"Syntax error: {e.msg}",
                    "fix": "Fix syntax error"
                })
        
        # Check for security patterns
        security_patterns = [
            ('eval(', 'Dangerous eval() usage'),
            ('exec(', 'Dangerous exec() usage'),
            ('os.system(', 'Potential command injection'),
            ('subprocess.call(', 'Check subprocess security'),
            ('pickle.loads(', 'Unsafe pickle deserialization'),
            ('yaml.load(', 'Use yaml.safe_load() instead')
        ]
        
        for pattern, warning in security_patterns:
            if pattern in code_content:
                automated_issues.append({
                    "severity": "medium",
                    "line": 0,
                    "issue": f"Security concern: {warning}",
                    "fix": f"Review usage of {pattern}"
                })
        
        # Add automated issues to the result
        quality_data['issues'].extend(automated_issues)
        quality_data['issues_found'] = len(quality_data['issues']) > 0
        
        # Adjust score based on automated findings
        if automated_issues:
            severity_penalties = {'high': 20, 'medium': 10, 'low': 5}
            penalty = sum(severity_penalties.get(issue['severity'], 5) for issue in automated_issues)
            quality_data['score'] = max(0, quality_data.get('score', 70) - penalty)
        
        return {
            'task_id': task_id,
            'status': 'success',
            'file_path': file_path,
            'ai_provider': ai_provider,
            'automated_checks': len(automated_issues),
            **quality_data
        }
        
    except Exception as e:
        return {'task_id': task_data.get('task_id', 'unknown'), 'status': 'error', 'message': str(e)}

@app.task(bind=True, name='ai_workers.memory_worker')
def memory_worker(self, task_data):
    """Worker 3: Memory Management and Code Indexing"""
    try:
        task_id = task_data['task_id']
        operation = task_data['operation']
        data = task_data['data']
        
        print(f"[Worker 3] Memory operation: {operation} for task: {task_id}")
        
        # Use Redis for indexing and memory
        memory_key = f"ai_memory:{operation}"
        
        if operation == 'index':
            # Index new code and knowledge
            file_path = data.get('file_path')
            code = data.get('code', '')
            task_description = data.get('task_description', '')
            
            # Create index entry
            index_entry = {
                'timestamp': datetime.now().isoformat(),
                'file_path': file_path,
                'task_description': task_description,
                'code_hash': hash(code),
                'lines_of_code': len(code.split('\n')),
                'task_id': task_id
            }
            
            # Store in Redis
            redis_client.hset(f"file_index:{file_path}", mapping=index_entry)
            redis_client.lpush("recent_changes", json.dumps(index_entry))
            redis_client.ltrim("recent_changes", 0, 99)  # Keep last 100 changes
            
            # Update global stats
            redis_client.hincrby("global_stats", "files_processed", 1)
            redis_client.hincrby("global_stats", "total_lines", len(code.split('\n')))
            
            # Store code patterns for learning
            pattern_prompt = f"""
            Analyze this code for reusable patterns and knowledge:
            
            File: {file_path}
            Task: {task_description}
            Code:
            {code[:1000]}...
            
            Extract:
            - Key patterns used
            - Technologies/frameworks
            - Common functions/classes
            - Best practices demonstrated
            
            Respond with JSON:
            {{"patterns": ["pattern1", "pattern2"], "technologies": ["tech1"], "insights": ["insight1"]}}
            """
            
            try:
                if MULTI_PROVIDER_AVAILABLE:
                    import asyncio
                    result = asyncio.run(enhanced_ai_client.smart_chat(pattern_prompt))
                    pattern_result = result['response']
                    ai_provider = result['provider_used']
                else:
                    grok = EnhancedGrokIntegration()
                    pattern_result = grok.call_grok(pattern_prompt)
                    ai_provider = "grok_direct"
                
                if "```json" in pattern_result:
                    pattern_data = json.loads(pattern_result.split("```json")[1].split("```")[0])
                elif "```" in pattern_result:
                    # Try to find JSON in any code block
                    code_blocks = pattern_result.split("```")
                    for block in code_blocks:
                        if block.strip().startswith('{'):
                            pattern_data = json.loads(block.strip())
                            break
                    else:
                        pattern_data = {"patterns": [], "technologies": [], "insights": []}
                else:
                    pattern_data = json.loads(pattern_result.strip())
                
                # Add AI provider info
                pattern_data['ai_provider'] = ai_provider
                redis_client.hset(f"patterns:{file_path}", mapping=pattern_data)
                
            except Exception as e:
                print(f"[Worker 3] Pattern analysis failed: {e}")
                pass  # Continue if pattern analysis fails
            
            return {
                'task_id': task_id,
                'status': 'success',
                'operation': 'index',
                'indexed_file': file_path,
                'memory_entries': 1
            }
        
        elif operation == 'search':
            # Search indexed knowledge
            query = data.get('query', '')
            
            # Simple search through indexed files
            results = []
            for key in redis_client.scan_iter(match="file_index:*"):
                file_data = redis_client.hgetall(key)
                if query.lower() in file_data.get('task_description', '').lower():
                    results.append(file_data)
            
            return {
                'task_id': task_id,
                'status': 'success',
                'operation': 'search',
                'query': query,
                'results': results
            }
        
        elif operation == 'organize':
            # Organize and clean up memory
            # Remove old entries, consolidate patterns
            
            all_keys = list(redis_client.scan_iter(match="file_index:*"))
            organized = len(all_keys)
            
            # Could add more sophisticated organization logic here
            
            return {
                'task_id': task_id,
                'status': 'success',
                'operation': 'organize',
                'files_organized': organized
            }
        
        return {'task_id': task_id, 'status': 'error', 'message': f'Unknown operation: {operation}'}
        
    except Exception as e:
        return {'task_id': task_data.get('task_id', 'unknown'), 'status': 'error', 'message': str(e)}

# Initialize coordinator instance
coordinator = WorkerCoordinator()

if __name__ == "__main__":
    print("Multi-Worker AI System initialized!")
    print("Start workers with: celery -A ai_multi_worker worker --loglevel=info")
