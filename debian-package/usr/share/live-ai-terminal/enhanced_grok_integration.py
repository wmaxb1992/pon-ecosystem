"""
ENHANCED GROK INTEGRATION
========================
Combines AI coding rules, memory system, and thought processor for comprehensive AI development.
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from pathlib import Path

# Import our AI systems
from ai_coding_rules import ai_rules, CodingRule, FileType, ComponentType
from ai_memory_system import ai_memory, CodePattern, FolderStructure, CodingDecision
from ai_thought_processor import thought_processor, ThoughtType, Colors

class EnhancedGrokIntegration:
    def __init__(self):
        self.current_project = None
        self.current_context = {}
        self.active_rules = []
        self.memory_enabled = True
        self.thought_enabled = True
        
        # Initialize AI systems
        self._initialize_ai_systems()
    
    def _initialize_ai_systems(self):
        """Initialize all AI systems"""
        if self.thought_enabled:
            thought_processor.add_thought(
                ThoughtType.ANALYSIS,
                "Initializing Enhanced Grok Integration with AI coding rules, memory system, and thought processor",
                {"systems": ["coding_rules", "memory", "thought_processor"]},
                confidence=0.9
            )
    
    def set_project_context(self, project_path: str, project_type: str = "web_app"):
        """Set the current project context"""
        self.current_project = {
            "path": project_path,
            "type": project_type,
            "created_at": datetime.now(),
            "files": self._scan_project_files(project_path)
        }
        
        self.current_context = {
            "project_path": project_path,
            "project_type": project_type,
            "file_count": len(self.current_project["files"])
        }
        
        if self.thought_enabled:
            thought_processor.add_thought(
                ThoughtType.ANALYSIS,
                f"Setting project context: {project_type} at {project_path}",
                self.current_context,
                confidence=0.8
            )
    
    def _scan_project_files(self, project_path: str) -> List[Dict[str, Any]]:
        """Scan project files for analysis"""
        files = []
        project_dir = Path(project_path)
        
        if not project_dir.exists():
            return files
        
        for file_path in project_dir.rglob("*"):
            if file_path.is_file() and not file_path.name.startswith('.'):
                file_info = {
                    "path": str(file_path.relative_to(project_dir)),
                    "name": file_path.name,
                    "size": file_path.stat().st_size,
                    "extension": file_path.suffix,
                    "modified": datetime.fromtimestamp(file_path.stat().st_mtime)
                }
                files.append(file_info)
        
        return files
    
    def analyze_code_file(self, file_path: str) -> Dict[str, Any]:
        """Analyze a code file using AI systems"""
        if not os.path.exists(file_path):
            return {"error": "File not found"}
        
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Determine file type
        file_type = self._determine_file_type(file_path)
        
        # Analyze with thought processor
        if self.thought_enabled:
            thought_processor.analyze_code(content, f"File: {file_path}")
        
        # Check against coding rules
        violations = self._check_coding_rules(file_path, content, file_type)
        
        # Index in memory system
        if self.memory_enabled:
            ai_memory.index_file(file_path, content)
        
        # Extract patterns
        patterns = self._extract_code_patterns(content, file_type)
        
        analysis = {
            "file_path": file_path,
            "file_type": file_type.value if file_type else "unknown",
            "content_length": len(content),
            "violations": violations,
            "patterns": patterns,
            "complexity": self._calculate_complexity(content),
            "suggestions": self._generate_suggestions(content, file_type, violations)
        }
        
        if self.thought_enabled:
            thought_processor.add_thought(
                ThoughtType.ANALYSIS,
                f"Completed analysis of {file_path} - found {len(violations)} violations, {len(patterns)} patterns",
                {"analysis": analysis},
                confidence=0.8
            )
        
        return analysis
    
    def _determine_file_type(self, file_path: str) -> Optional[FileType]:
        """Determine the file type based on extension"""
        ext = Path(file_path).suffix.lower()
        
        file_type_map = {
            '.py': FileType.PYTHON,
            '.js': FileType.JAVASCRIPT,
            '.ts': FileType.TYPESCRIPT,
            '.tsx': FileType.REACT,
            '.jsx': FileType.REACT,
            '.html': FileType.HTML,
            '.css': FileType.CSS,
            '.scss': FileType.SCSS,
            '.json': FileType.JSON,
            '.yaml': FileType.YAML,
            '.yml': FileType.YAML,
            '.sql': FileType.SQL,
            '.sh': FileType.SHELL,
            '.md': FileType.MARKDOWN
        }
        
        return file_type_map.get(ext)
    
    def _check_coding_rules(self, file_path: str, content: str, file_type: FileType) -> List[Dict[str, Any]]:
        """Check code against AI coding rules"""
        violations = []
        
        if not file_type:
            return violations
        
        # Get applicable rules
        rules = ai_rules.get_rules_by_file_type(file_type)
        
        for rule in rules:
            violation = self._check_rule_violation(rule, file_path, content)
            if violation:
                violations.append(violation)
        
        return violations
    
    def _check_rule_violation(self, rule: CodingRule, file_path: str, content: str) -> Optional[Dict[str, Any]]:
        """Check if a specific rule is violated"""
        # This is a simplified check - can be enhanced with more sophisticated analysis
        if rule.rule_id == "FILE_001":  # Consistent File Naming
            file_name = Path(file_path).name
            if not self._validate_naming(file_name, rule.file_types[0].value, "files"):
                return {
                    "rule_id": rule.rule_id,
                    "rule_title": rule.title,
                    "violation": f"File naming doesn't follow {rule.file_types[0].value} conventions",
                    "suggestion": rule.examples[0] if rule.examples else "Follow naming conventions"
                }
        
        elif rule.rule_id == "CODE_001":  # Single Responsibility Principle
            # Check for overly complex functions
            lines = content.split('\n')
            for i, line in enumerate(lines):
                if 'def ' in line and len(line) > 100:
                    return {
                        "rule_id": rule.rule_id,
                        "rule_title": rule.title,
                        "violation": f"Function definition too long at line {i+1}",
                        "suggestion": "Break down complex functions into smaller, focused functions"
                    }
        
        return None
    
    def _validate_naming(self, name: str, file_type: str, naming_type: str) -> bool:
        """Validate naming convention"""
        return ai_rules.validate_naming(name, file_type, naming_type)
    
    def _extract_code_patterns(self, content: str, file_type: FileType) -> List[str]:
        """Extract code patterns from content"""
        patterns = []
        
        if file_type == FileType.PYTHON:
            if "async def" in content:
                patterns.append("async_function")
            if "class " in content:
                patterns.append("class_definition")
            if "@app.route" in content or "@app.get" in content:
                patterns.append("api_endpoint")
            if "from pydantic import" in content:
                patterns.append("pydantic_model")
        
        elif file_type in [FileType.REACT, FileType.TYPESCRIPT]:
            if "useState" in content:
                patterns.append("react_state")
            if "useEffect" in content:
                patterns.append("react_effect")
            if "interface " in content:
                patterns.append("typescript_interface")
            if "export const" in content:
                patterns.append("react_component")
        
        return patterns
    
    def _calculate_complexity(self, content: str) -> float:
        """Calculate code complexity"""
        complexity = 0.0
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith(('if ', 'for ', 'while ', 'try:', 'except')):
                complexity += 1
            if line.startswith(('def ', 'class ')):
                complexity += 0.5
        
        return complexity / max(len(lines), 1)
    
    def _generate_suggestions(self, content: str, file_type: FileType, violations: List[Dict[str, Any]]) -> List[str]:
        """Generate improvement suggestions"""
        suggestions = []
        
        # Add suggestions based on violations
        for violation in violations:
            if "suggestion" in violation:
                suggestions.append(violation["suggestion"])
        
        # Add general suggestions based on file type
        if file_type == FileType.PYTHON:
            if "def " in content and "->" not in content:
                suggestions.append("Add type hints to function definitions")
            if "print(" in content:
                suggestions.append("Consider using logging instead of print statements")
        
        elif file_type in [FileType.REACT, FileType.TYPESCRIPT]:
            if "any" in content:
                suggestions.append("Avoid using 'any' type, use specific types instead")
            if "console.log" in content:
                suggestions.append("Remove console.log statements for production")
        
        return suggestions
    
    def generate_code_with_ai(self, purpose: str, language: str, context: str = "") -> str:
        """Generate code using AI systems"""
        if self.thought_enabled:
            thought_processor.generate_code(purpose, language)
        
        # Recall relevant patterns from memory
        if self.memory_enabled:
            patterns = ai_memory.find_similar_patterns(purpose, "code_generation", language)
            if patterns:
                best_pattern = patterns[0]
                if self.thought_enabled:
                    thought_processor.recall_memory(f"code generation for {purpose}", [best_pattern.content])
                return best_pattern.content
        
        # Generate new code based on rules
        code = self._generate_code_from_rules(purpose, language, context)
        
        # Store in memory
        if self.memory_enabled:
            pattern = CodePattern(
                pattern_id=f"gen_{int(time.time())}",
                pattern_type="code_generation",
                language=language,
                content=code,
                context={"purpose": purpose, "context": context},
                usage_count=1,
                success_rate=0.8,
                last_used=datetime.now(),
                created_at=datetime.now(),
                tags=[purpose, language],
                complexity_score=0.5,
                performance_score=0.7
            )
            ai_memory.add_code_pattern(pattern)
        
        return code
    
    def _generate_code_from_rules(self, purpose: str, language: str, context: str) -> str:
        """Generate code following AI coding rules"""
        if language == "python":
            return self._generate_python_code(purpose, context)
        elif language in ["javascript", "typescript"]:
            return self._generate_js_code(purpose, context)
        elif language == "react":
            return self._generate_react_code(purpose, context)
        else:
            return f"# Generated code for: {purpose}\n# Language: {language}\n# Context: {context}"
    
    def _generate_python_code(self, purpose: str, context: str) -> str:
        """Generate Python code following rules"""
        code = f'''"""
{purpose}
Context: {context}
Generated by Grok AI following coding rules
"""

from typing import Optional, List, Dict, Any
from dataclasses import dataclass
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class GeneratedData:
    """Data structure for generated content"""
    id: str
    name: str
    description: Optional[str] = None

def process_data(data: List[GeneratedData]) -> Dict[str, Any]:
    """
    Process the generated data following single responsibility principle.
    
    Args:
        data: List of data items to process
        
    Returns:
        Dictionary containing processed results
    """
    try:
        results = {
            "total_items": len(data),
            "processed_items": 0,
            "errors": []
        }
        
        for item in data:
            try:
                # Process each item
                logger.info(f"Processing item: {item.name}")
                results["processed_items"] += 1
            except Exception as e:
                logger.error(f"Error processing {item.name}: {e}")
                results["errors"].append(str(e))
        
        return results
    except Exception as e:
        logger.error(f"Error in process_data: {e}")
        raise

if __name__ == "__main__":
    # Example usage
    sample_data = [
        GeneratedData(id="1", name="Sample 1", description="First sample"),
        GeneratedData(id="2", name="Sample 2", description="Second sample")
    ]
    
    result = process_data(sample_data)
    print(f"Processing complete: {result}")
'''
        return code
    
    def _generate_js_code(self, purpose: str, context: str) -> str:
        """Generate JavaScript/TypeScript code following rules"""
        code = f'''/**
 * {purpose}
 * Context: {context}
 * Generated by Grok AI following coding rules
 */

// Type definitions
interface GeneratedData {{
    id: string;
    name: string;
    description?: string;
}}

interface ProcessResult {{
    totalItems: number;
    processedItems: number;
    errors: string[];
}}

/**
 * Process the generated data following single responsibility principle
 * @param data - List of data items to process
 * @returns Promise containing processed results
 */
async function processData(data: GeneratedData[]): Promise<ProcessResult> {{
    const results: ProcessResult = {{
        totalItems: data.length,
        processedItems: 0,
        errors: []
    }};
    
    try {{
        for (const item of data) {{
            try {{
                // Process each item
                console.log(`Processing item: ${{item.name}}`);
                results.processedItems++;
            }} catch (error) {{
                console.error(`Error processing ${{item.name}}:`, error);
                results.errors.push(error.message);
            }}
        }}
        
        return results;
    }} catch (error) {{
        console.error('Error in processData:', error);
        throw error;
    }}
}}

// Example usage
const sampleData: GeneratedData[] = [
    {{ id: '1', name: 'Sample 1', description: 'First sample' }},
    {{ id: '2', name: 'Sample 2', description: 'Second sample' }}
];

processData(sampleData)
    .then(result => console.log('Processing complete:', result))
    .catch(error => console.error('Processing failed:', error));
'''
        return code
    
    def _generate_react_code(self, purpose: str, context: str) -> str:
        """Generate React component following rules"""
        code = f'''/**
 * {purpose}
 * Context: {context}
 * Generated by Grok AI following coding rules
 */

import React, {{ useState, useEffect }} from 'react';

// Type definitions
interface GeneratedData {{
    id: string;
    name: string;
    description?: string;
}}

interface ProcessResult {{
    totalItems: number;
    processedItems: number;
    errors: string[];
}}

interface GeneratedComponentProps {{
    data: GeneratedData[];
    onProcess: (result: ProcessResult) => void;
}}

/**
 * Generated component following React best practices
 */
export const GeneratedComponent: React.FC<GeneratedComponentProps> = ({{
    data,
    onProcess
}}) => {{
    const [isProcessing, setIsProcessing] = useState<boolean>(false);
    const [result, setResult] = useState<ProcessResult | null>(null);
    const [error, setError] = useState<string | null>(null);
    
    const processData = async (): Promise<void> => {{
        setIsProcessing(true);
        setError(null);
        
        try {{
            const processResult: ProcessResult = {{
                totalItems: data.length,
                processedItems: 0,
                errors: []
            }};
            
            for (const item of data) {{
                try {{
                    // Process each item
                    console.log(`Processing item: ${{item.name}}`);
                    processResult.processedItems++;
                }} catch (err) {{
                    console.error(`Error processing ${{item.name}}:`, err);
                    processResult.errors.push(err.message);
                }}
            }}
            
            setResult(processResult);
            onProcess(processResult);
        }} catch (err) {{
            setError(err.message);
        }} finally {{
            setIsProcessing(false);
        }}
    }};
    
    useEffect(() => {{
        if (data.length > 0) {{
            processData();
        }}
    }}, [data]);
    
    if (error) {{
        return (
            <div className="error-container">
                <h3>Error</h3>
                <p>{{error}}</p>
            </div>
        );
    }}
    
    return (
        <div className="generated-component">
            <h2>Generated Component</h2>
            {{isProcessing ? (
                <p>Processing...</p>
            ) : result ? (
                <div>
                    <h3>Results</h3>
                    <p>Total items: {{result.totalItems}}</p>
                    <p>Processed items: {{result.processedItems}}</p>
                    {{result.errors.length > 0 && (
                        <div>
                            <h4>Errors:</h4>
                            <ul>
                                {{result.errors.map((err, index) => (
                                    <li key={{index}}>{{err}}</li>
                                ))}}
                            </ul>
                        </div>
                    )}}
                </div>
            ) : (
                <p>No data to process</p>
            )}}
        </div>
    );
}};

export default GeneratedComponent;
'''
        return code
    
    def optimize_code(self, file_path: str) -> Dict[str, Any]:
        """Optimize code using AI systems"""
        if not os.path.exists(file_path):
            return {"error": "File not found"}
        
        with open(file_path, 'r', encoding='utf-8') as f:
            original_content = f.read()
        
        if self.thought_enabled:
            thought_processor.optimize_code(original_content, "", ["Starting optimization"])
        
        # Get optimization suggestions
        suggestions = self._get_optimization_suggestions(original_content, file_path)
        
        # Apply optimizations
        optimized_content = self._apply_optimizations(original_content, suggestions)
        
        # Store optimization decision
        if self.memory_enabled:
            decision = CodingDecision(
                decision_id=f"opt_{int(time.time())}",
                context=f"Optimizing {file_path}",
                problem="Code optimization needed",
                solution="Applied AI-suggested optimizations",
                rationale="Improve performance and maintainability",
                alternatives=["Manual optimization", "No optimization"],
                chosen_approach="AI-guided optimization",
                outcome="Code optimized successfully",
                created_at=datetime.now(),
                tags=["optimization", "ai", "code_quality"],
                confidence_score=0.8
            )
            ai_memory.add_coding_decision(decision)
        
        return {
            "file_path": file_path,
            "original_length": len(original_content),
            "optimized_length": len(optimized_content),
            "suggestions": suggestions,
            "improvements": self._calculate_improvements(original_content, optimized_content)
        }
    
    def _get_optimization_suggestions(self, content: str, file_path: str) -> List[str]:
        """Get optimization suggestions for code"""
        suggestions = []
        file_type = self._determine_file_type(file_path)
        
        if file_type == FileType.PYTHON:
            if "import *" in content:
                suggestions.append("Replace wildcard imports with specific imports")
            if "print(" in content:
                suggestions.append("Replace print statements with proper logging")
            if "except:" in content:
                suggestions.append("Use specific exception types instead of bare except")
        
        elif file_type in [FileType.REACT, FileType.TYPESCRIPT]:
            if "any" in content:
                suggestions.append("Replace 'any' types with specific types")
            if "console.log" in content:
                suggestions.append("Remove console.log statements")
            if "useState" in content and "useEffect" not in content:
                suggestions.append("Consider using useEffect for side effects")
        
        return suggestions
    
    def _apply_optimizations(self, content: str, suggestions: List[str]) -> str:
        """Apply optimizations to code"""
        optimized = content
        
        for suggestion in suggestions:
            if "Replace wildcard imports" in suggestion:
                # This would require more sophisticated parsing
                pass
            elif "Replace print statements" in suggestion:
                optimized = optimized.replace("print(", "logger.info(")
            elif "Use specific exception types" in suggestion:
                optimized = optimized.replace("except:", "except Exception:")
            elif "Replace 'any' types" in suggestion:
                optimized = optimized.replace(": any", ": unknown")
            elif "Remove console.log statements" in suggestion:
                # This would require more sophisticated parsing
                pass
        
        return optimized
    
    def _calculate_improvements(self, original: str, optimized: str) -> Dict[str, Any]:
        """Calculate improvement metrics"""
        return {
            "lines_reduced": len(original.split('\n')) - len(optimized.split('\n')),
            "characters_reduced": len(original) - len(optimized),
            "complexity_reduced": self._calculate_complexity(original) - self._calculate_complexity(optimized)
        }
    
    def get_ai_insights(self) -> Dict[str, Any]:
        """Get comprehensive AI insights about the project"""
        insights = {
            "project_info": self.current_project,
            "coding_rules": {
                "total_rules": len(ai_rules.rules),
                "high_priority_rules": len(ai_rules.get_rules_by_priority(8)),
                "rule_categories": list(set(rule.category for rule in ai_rules.rules))
            },
            "memory_stats": ai_memory.get_memory_stats() if self.memory_enabled else {},
            "thought_summary": thought_processor.get_thought_history() if self.thought_enabled else [],
            "recommendations": self._generate_recommendations()
        }
        
        return insights
    
    def _generate_recommendations(self) -> List[str]:
        """Generate AI recommendations for the project"""
        recommendations = []
        
        if not self.current_project:
            return recommendations
        
        # Analyze project structure
        files = self.current_project["files"]
        file_types = [f["extension"] for f in files if f["extension"]]
        
        if ".py" in file_types and not any("test" in f["name"].lower() for f in files):
            recommendations.append("Add unit tests for Python code")
        
        if ".ts" in file_types and not any("test" in f["name"].lower() for f in files):
            recommendations.append("Add unit tests for TypeScript code")
        
        if len(files) > 50:
            recommendations.append("Consider organizing code into smaller modules")
        
        return recommendations
    
    def show_ai_status(self):
        """Show current AI system status"""
        print(f"{Colors.CYAN}🤖 {Colors.BOLD}Enhanced Grok AI Status{Colors.RESET}")
        print(f"{Colors.CYAN}{'='*50}{Colors.RESET}")
        
        # Project status
        if self.current_project:
            print(f"{Colors.GREEN}📁 Project: {self.current_project['type']} at {self.current_project['path']}{Colors.RESET}")
            print(f"{Colors.GREEN}   Files: {len(self.current_project['files'])}{Colors.RESET}")
        else:
            print(f"{Colors.YELLOW}📁 No project context set{Colors.RESET}")
        
        # AI systems status
        print(f"\n{Colors.LIGHT_BLUE}🧠 AI Systems:{Colors.RESET}")
        print(f"   Coding Rules: {len(ai_rules.rules)} rules loaded")
        print(f"   Memory System: {'Enabled' if self.memory_enabled else 'Disabled'}")
        print(f"   Thought Processor: {'Enabled' if self.thought_enabled else 'Disabled'}")
        
        # Memory stats
        if self.memory_enabled:
            stats = ai_memory.get_memory_stats()
            print(f"\n{Colors.LIGHT_BLUE}📊 Memory Stats:{Colors.RESET}")
            print(f"   Patterns: {stats.get('total_patterns', 0)}")
            print(f"   Decisions: {stats.get('total_decisions', 0)}")
            print(f"   Indexed Files: {stats.get('total_indexed_files', 0)}")
        
        # Thought summary
        if self.thought_enabled:
            thought_processor.show_thought_summary()

# Global enhanced Grok integration instance
enhanced_grok = EnhancedGrokIntegration() 