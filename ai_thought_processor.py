"""
AI THOUGHT PROCESSOR
===================
Displays Grok AI's thinking process in the terminal with colored output.
Light blue for thoughts, dark blue for questions.
"""

import time
import json
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from enum import Enum
import threading
import queue

# ANSI color codes
class Colors:
    LIGHT_BLUE = '\033[94m'      # Light blue for thoughts
    DARK_BLUE = '\033[34m'       # Dark blue for questions
    BLUE = '\033[94m'            # Blue (alias for light blue)
    GREEN = '\033[92m'           # Green for success
    YELLOW = '\033[93m'          # Yellow for warnings
    RED = '\033[91m'             # Red for errors
    PURPLE = '\033[95m'          # Purple for analysis
    CYAN = '\033[96m'            # Cyan for info
    WHITE = '\033[97m'           # White for normal text
    BOLD = '\033[1m'             # Bold text
    UNDERLINE = '\033[4m'        # Underlined text
    RESET = '\033[0m'            # Reset all formatting

class ThoughtType(Enum):
    ANALYSIS = "analysis"
    DECISION = "decision"
    QUESTION = "question"
    SOLUTION = "solution"
    MEMORY_RECALL = "memory_recall"
    PATTERN_MATCHING = "pattern_matching"
    CODE_GENERATION = "code_generation"
    VALIDATION = "validation"
    OPTIMIZATION = "optimization"
    ERROR_HANDLING = "error_handling"

@dataclass
class Thought:
    thought_id: str
    thought_type: ThoughtType
    content: str
    context: Dict[str, Any]
    timestamp: datetime
    duration: Optional[float] = None
    confidence: float = 0.0
    related_thoughts: List[str] = None
    metadata: Dict[str, Any] = None

@dataclass
class Question:
    question_id: str
    question: str
    context: str
    options: List[str]
    reasoning: str
    timestamp: datetime
    answered: bool = False
    answer: Optional[str] = None

class AIThoughtProcessor:
    def __init__(self):
        self.thoughts: List[Thought] = []
        self.questions: List[Question] = []
        self.current_context: Dict[str, Any] = {}
        self.thought_queue = queue.Queue()
        self.is_processing = False
        self.thought_thread = None
        
        # Start thought processing thread
        self.start_processing()
    
    def start_processing(self):
        """Start the thought processing thread"""
        self.is_processing = True
        self.thought_thread = threading.Thread(target=self._process_thoughts)
        self.thought_thread.daemon = True
        self.thought_thread.start()
    
    def stop_processing(self):
        """Stop the thought processing thread"""
        self.is_processing = False
        if self.thought_thread:
            self.thought_thread.join()
    
    def _process_thoughts(self):
        """Process thoughts in background thread"""
        while self.is_processing:
            try:
                thought = self.thought_queue.get(timeout=1)
                self._display_thought(thought)
                self.thought_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                print(f"{Colors.RED}Error processing thought: {e}{Colors.RESET}")
    
    def add_thought(self, thought_type: ThoughtType, content: str, 
                   context: Dict[str, Any] = None, confidence: float = 0.0) -> str:
        """Add a new thought to the processor"""
        thought_id = f"thought_{int(time.time() * 1000)}"
        
        thought = Thought(
            thought_id=thought_id,
            thought_type=thought_type,
            content=content,
            context=context or {},
            timestamp=datetime.now(),
            confidence=confidence,
            related_thoughts=[],
            metadata={}
        )
        
        self.thoughts.append(thought)
        self.thought_queue.put(thought)
        
        return thought_id
    
    def add_question(self, question: str, context: str, options: List[str] = None, 
                    reasoning: str = "") -> str:
        """Add a question for user input"""
        question_id = f"question_{int(time.time() * 1000)}"
        
        ai_question = Question(
            question_id=question_id,
            question=question,
            context=context,
            options=options or [],
            reasoning=reasoning,
            timestamp=datetime.now()
        )
        
        self.questions.append(ai_question)
        self._display_question(ai_question)
        
        return question_id
    
    def _display_thought(self, thought: Thought):
        """Display a thought with appropriate formatting"""
        timestamp = thought.timestamp.strftime("%H:%M:%S")
        
        # Determine color based on thought type
        if thought.thought_type == ThoughtType.QUESTION:
            color = Colors.DARK_BLUE
        else:
            color = Colors.LIGHT_BLUE
        
        # Thought type icon
        type_icons = {
            ThoughtType.ANALYSIS: "🔍",
            ThoughtType.DECISION: "🤔",
            ThoughtType.QUESTION: "❓",
            ThoughtType.SOLUTION: "💡",
            ThoughtType.MEMORY_RECALL: "🧠",
            ThoughtType.PATTERN_MATCHING: "🔗",
            ThoughtType.CODE_GENERATION: "⚡",
            ThoughtType.VALIDATION: "✅",
            ThoughtType.OPTIMIZATION: "🚀",
            ThoughtType.ERROR_HANDLING: "⚠️"
        }
        
        icon = type_icons.get(thought.thought_type, "💭")
        
        # Display the thought
        print(f"{color}[{timestamp}] {icon} {Colors.BOLD}Grok AI{Colors.RESET}{color}: {thought.content}{Colors.RESET}")
        
        # Show confidence if available
        if thought.confidence > 0:
            confidence_bar = "█" * int(thought.confidence * 10)
            print(f"{color}   Confidence: {confidence_bar} ({thought.confidence:.1%}){Colors.RESET}")
        
        # Show context if available
        if thought.context:
            context_str = json.dumps(thought.context, indent=2)
            if len(context_str) < 100:  # Only show short contexts
                print(f"{color}   Context: {context_str}{Colors.RESET}")
    
    def _display_question(self, question: Question):
        """Display a question with dark blue formatting"""
        timestamp = question.timestamp.strftime("%H:%M:%S")
        
        print(f"\n{Colors.DARK_BLUE}[{timestamp}] ❓ {Colors.BOLD}Grok AI Question{Colors.RESET}{Colors.DARK_BLUE}:{Colors.RESET}")
        print(f"{Colors.DARK_BLUE}   {question.question}{Colors.RESET}")
        
        if question.context:
            print(f"{Colors.DARK_BLUE}   Context: {question.context}{Colors.RESET}")
        
        if question.reasoning:
            print(f"{Colors.DARK_BLUE}   Reasoning: {question.reasoning}{Colors.RESET}")
        
        if question.options:
            print(f"{Colors.DARK_BLUE}   Options:{Colors.RESET}")
            for i, option in enumerate(question.options, 1):
                print(f"{Colors.DARK_BLUE}     {i}. {option}{Colors.RESET}")
    
    def answer_question(self, question_id: str, answer: str):
        """Answer a question"""
        for question in self.questions:
            if question.question_id == question_id:
                question.answered = True
                question.answer = answer
                
                # Display the answer
                timestamp = datetime.now().strftime("%H:%M:%S")
                print(f"{Colors.GREEN}[{timestamp}] ✅ {Colors.BOLD}User Answer{Colors.RESET}{Colors.GREEN}: {answer}{Colors.RESET}")
                break
    
    def analyze_code(self, code: str, context: str = "") -> str:
        """Analyze code and generate thoughts"""
        thought_id = self.add_thought(
            ThoughtType.ANALYSIS,
            f"Analyzing code for: {context}",
            {"code_length": len(code), "context": context},
            confidence=0.8
        )
        
        # Add pattern matching thought
        self.add_thought(
            ThoughtType.PATTERN_MATCHING,
            "Looking for familiar code patterns and structures",
            {"code_snippet": code[:100] + "..." if len(code) > 100 else code},
            confidence=0.7
        )
        
        return thought_id
    
    def make_decision(self, problem: str, options: List[str], reasoning: str = "") -> str:
        """Make a decision and generate thoughts"""
        thought_id = self.add_thought(
            ThoughtType.DECISION,
            f"Making decision about: {problem}",
            {"options": options, "reasoning": reasoning},
            confidence=0.6
        )
        
        # Add memory recall thought
        self.add_thought(
            ThoughtType.MEMORY_RECALL,
            "Recalling similar decisions and their outcomes",
            {"problem_type": problem},
            confidence=0.5
        )
        
        return thought_id
    
    def generate_solution(self, problem: str, solution: str, confidence: float = 0.0) -> str:
        """Generate a solution and display thoughts"""
        thought_id = self.add_thought(
            ThoughtType.SOLUTION,
            f"Generated solution for: {problem}",
            {"solution": solution, "problem": problem},
            confidence=confidence
        )
        
        # Add validation thought
        self.add_thought(
            ThoughtType.VALIDATION,
            "Validating solution against coding rules and best practices",
            {"solution_length": len(solution)},
            confidence=0.8
        )
        
        return thought_id
    
    def optimize_code(self, original: str, optimized: str, improvements: List[str]) -> str:
        """Optimize code and show thoughts"""
        thought_id = self.add_thought(
            ThoughtType.OPTIMIZATION,
            f"Optimizing code with {len(improvements)} improvements",
            {"improvements": improvements, "original_length": len(original), "optimized_length": len(optimized)},
            confidence=0.9
        )
        
        for improvement in improvements:
            self.add_thought(
                ThoughtType.OPTIMIZATION,
                f"Improvement: {improvement}",
                {"improvement_type": improvement},
                confidence=0.8
            )
        
        return thought_id
    
    def handle_error(self, error: str, context: str = "") -> str:
        """Handle an error and show thoughts"""
        thought_id = self.add_thought(
            ThoughtType.ERROR_HANDLING,
            f"Handling error: {error}",
            {"error": error, "context": context},
            confidence=0.7
        )
        
        # Add analysis thought
        self.add_thought(
            ThoughtType.ANALYSIS,
            "Analyzing error patterns and potential solutions",
            {"error_type": type(error).__name__},
            confidence=0.6
        )
        
        return thought_id
    
    def recall_memory(self, query: str, results: List[str]) -> str:
        """Recall from memory and show thoughts"""
        thought_id = self.add_thought(
            ThoughtType.MEMORY_RECALL,
            f"Recalling memory for: {query}",
            {"query": query, "results_count": len(results)},
            confidence=0.8
        )
        
        if results:
            self.add_thought(
                ThoughtType.MEMORY_RECALL,
                f"Found {len(results)} relevant patterns/decisions",
                {"results": results[:3]},  # Show first 3 results
                confidence=0.9
            )
        
        return thought_id
    
    def generate_code(self, purpose: str, language: str, complexity: str = "medium") -> str:
        """Generate code and show thoughts"""
        thought_id = self.add_thought(
            ThoughtType.CODE_GENERATION,
            f"Generating {language} code for: {purpose}",
            {"purpose": purpose, "language": language, "complexity": complexity},
            confidence=0.8
        )
        
        # Add pattern matching thought
        self.add_thought(
            ThoughtType.PATTERN_MATCHING,
            f"Applying {language} coding patterns and conventions",
            {"language": language, "complexity": complexity},
            confidence=0.7
        )
        
        return thought_id
    
    def ask_user_question(self, question: str, context: str = "", 
                         options: List[str] = None, reasoning: str = "") -> str:
        """Ask user a question and wait for response"""
        question_id = self.add_question(question, context, options, reasoning)
        
        # Display input prompt
        print(f"{Colors.DARK_BLUE}   Your answer: {Colors.RESET}", end="")
        
        # Get user input
        answer = input()
        
        # Record the answer
        self.answer_question(question_id, answer)
        
        return answer
    
    def show_thought_summary(self):
        """Show a summary of all thoughts"""
        print(f"\n{Colors.CYAN}🤖 {Colors.BOLD}Grok AI Thought Summary{Colors.RESET}")
        print(f"{Colors.CYAN}{'='*50}{Colors.RESET}")
        
        # Group thoughts by type
        thoughts_by_type = {}
        for thought in self.thoughts:
            if thought.thought_type not in thoughts_by_type:
                thoughts_by_type[thought.thought_type] = []
            thoughts_by_type[thought.thought_type].append(thought)
        
        for thought_type, thoughts in thoughts_by_type.items():
            print(f"\n{Colors.LIGHT_BLUE}📊 {thought_type.value.title()}: {len(thoughts)} thoughts{Colors.RESET}")
            
            for thought in thoughts[-3:]:  # Show last 3 thoughts of each type
                timestamp = thought.timestamp.strftime("%H:%M:%S")
                print(f"   [{timestamp}] {thought.content[:60]}...")
        
        # Show questions
        if self.questions:
            print(f"\n{Colors.DARK_BLUE}❓ Questions Asked: {len(self.questions)}{Colors.RESET}")
            for question in self.questions:
                timestamp = question.timestamp.strftime("%H:%M:%S")
                status = "✅ Answered" if question.answered else "⏳ Pending"
                print(f"   [{timestamp}] {status}: {question.question[:50]}...")
    
    def get_thought_history(self) -> List[Dict[str, Any]]:
        """Get thought history for analysis"""
        return [
            {
                "id": thought.thought_id,
                "type": thought.thought_type.value,
                "content": thought.content,
                "timestamp": thought.timestamp.isoformat(),
                "confidence": thought.confidence,
                "context": thought.context
            }
            for thought in self.thoughts
        ]
    
    def clear_thoughts(self):
        """Clear all thoughts (useful for new sessions)"""
        self.thoughts.clear()
        self.questions.clear()
        print(f"{Colors.YELLOW}🧹 Thought history cleared{Colors.RESET}")
    
    def display_thinking_animation(self, message: str, duration: float = 2.0):
        """Display animated thinking process"""
        thinking_chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        start_time = time.time()
        
        while time.time() - start_time < duration:
            for char in thinking_chars:
                if time.time() - start_time >= duration:
                    break
                print(f"\r{Colors.LIGHT_BLUE}{char} {message}...{Colors.RESET}", end="", flush=True)
                time.sleep(0.1)
        
        print(f"\r{' ' * (len(message) + 10)}\r", end="")  # Clear line
    
    def display_streaming_response(self, response_generator, prefix: str = "🤖 Grok AI"):
        """Display streaming AI response with live updates"""
        print(f"\n{Colors.BOLD}{Colors.GREEN}{prefix}:{Colors.RESET}")
        
        collected_text = ""
        for chunk in response_generator:
            if chunk:
                print(f"{Colors.WHITE}{chunk}{Colors.RESET}", end="", flush=True)
                collected_text += chunk
        
        print()  # New line after complete response
        return collected_text
    
    def display_priority_thought(self, thought_type: ThoughtType, content: str, priority: str = "normal"):
        """Display high-priority thoughts with special formatting"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        # Priority indicators
        priority_indicators = {
            "critical": f"{Colors.RED}🚨 CRITICAL",
            "high": f"{Colors.YELLOW}⚡ URGENT", 
            "normal": f"{Colors.LIGHT_BLUE}💭",
            "low": f"{Colors.CYAN}ℹ️"
        }
        
        indicator = priority_indicators.get(priority, priority_indicators["normal"])
        
        # Enhanced display for high priority
        if priority in ["critical", "high"]:
            print(f"\n{Colors.BOLD}{'=' * 60}")
            print(f"{indicator} [{timestamp}] {content}")
            print(f"{'=' * 60}{Colors.RESET}")
        else:
            type_icons = {
                ThoughtType.ANALYSIS: "🔍",
                ThoughtType.DECISION: "🤔",
                ThoughtType.QUESTION: "❓",
                ThoughtType.SOLUTION: "💡",
                ThoughtType.MEMORY_RECALL: "🧠",
                ThoughtType.PATTERN_MATCHING: "🔗",
                ThoughtType.CODE_GENERATION: "⚡",
                ThoughtType.VALIDATION: "✅",
                ThoughtType.OPTIMIZATION: "🚀",
                ThoughtType.ERROR_HANDLING: "⚠️"
            }
            
            icon = type_icons.get(thought_type, "💭")
            print(f"{indicator} [{timestamp}] {icon} {content}{Colors.RESET}")
    
    def display_ascii_separator(self, title: str = "AI PROCESS", width: int = 80):
        """Display ASCII art separator"""
        print(f"\n{Colors.CYAN}")
        print("╔" + "═" * (width - 2) + "╗")
        print("║" + f" {title} ".center(width - 2, ".") + "║")
        print("╚" + "═" * (width - 2) + "╝")
        print(f"{Colors.RESET}")

# Global thought processor instance
thought_processor = AIThoughtProcessor()