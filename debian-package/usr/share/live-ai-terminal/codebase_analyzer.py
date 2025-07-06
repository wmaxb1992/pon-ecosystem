import os
import ast
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Set, Optional
from dataclasses import dataclass, asdict
import re

@dataclass
class FileInfo:
    path: str
    file_type: str
    size: int
    lines: int
    last_modified: float
    dependencies: List[str]
    imports: List[str]
    functions: List[str]
    classes: List[str]
    complexity_score: float
    issues: List[str]
    suggestions: List[str]

@dataclass
class CodebaseStructure:
    total_files: int
    total_lines: int
    languages: Dict[str, int]
    file_types: Dict[str, int]
    dependencies: Dict[str, List[str]]
    architecture: Dict[str, List[str]]
    hotspots: List[str]
    technical_debt: List[str]
    improvement_opportunities: List[str]

class CodebaseAnalyzer:
    def __init__(self, root_path: str = "."):
        self.root_path = Path(root_path)
        self.ignore_patterns = {
            '.git', '__pycache__', 'node_modules', '.next', 
            '.env', '.DS_Store', '*.pyc', '*.log', 'logs/',
            'venv', 'env', '.venv', '.env.local'
        }
        self.file_extensions = {
            '.py': 'Python',
            '.js': 'JavaScript',
            '.jsx': 'React',
            '.ts': 'TypeScript',
            '.tsx': 'TypeScript React',
            '.html': 'HTML',
            '.css': 'CSS',
            '.scss': 'SCSS',
            '.json': 'JSON',
            '.md': 'Markdown',
            '.yml': 'YAML',
            '.yaml': 'YAML',
            '.sh': 'Shell',
            '.sql': 'SQL'
        }
    
    def should_ignore(self, path: Path) -> bool:
        """Check if file/directory should be ignored"""
        path_str = str(path)
        for pattern in self.ignore_patterns:
            if pattern in path_str:
                return True
        return False
    
    def analyze_file(self, file_path: Path) -> Optional[FileInfo]:
        """Analyze a single file"""
        try:
            if not file_path.is_file():
                return None
            
            file_type = self.file_extensions.get(file_path.suffix, 'Unknown')
            stat = file_path.stat()
            
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                content = f.read()
                lines = content.split('\n')
            
            file_info = FileInfo(
                path=str(file_path),
                file_type=file_type,
                size=stat.st_size,
                lines=len(lines),
                last_modified=stat.st_mtime,
                dependencies=[],
                imports=[],
                functions=[],
                classes=[],
                complexity_score=0.0,
                issues=[],
                suggestions=[]
            )
            
            # Analyze based on file type
            if file_path.suffix == '.py':
                self.analyze_python_file(file_info, content)
            elif file_path.suffix in ['.js', '.jsx', '.ts', '.tsx']:
                self.analyze_javascript_file(file_info, content)
            elif file_path.suffix == '.html':
                self.analyze_html_file(file_info, content)
            elif file_path.suffix in ['.css', '.scss']:
                self.analyze_css_file(file_info, content)
            
            return file_info
            
        except Exception as e:
            print(f"Error analyzing {file_path}: {e}")
            return None
    
    def analyze_python_file(self, file_info: FileInfo, content: str):
        """Analyze Python file"""
        try:
            tree = ast.parse(content)
            
            # Extract imports
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    for alias in node.names:
                        file_info.imports.append(alias.name)
                elif isinstance(node, ast.ImportFrom):
                    module = node.module or ""
                    for alias in node.names:
                        file_info.imports.append(f"{module}.{alias.name}")
                elif isinstance(node, ast.FunctionDef):
                    file_info.functions.append(node.name)
                elif isinstance(node, ast.ClassDef):
                    file_info.classes.append(node.name)
            
            # Calculate complexity
            complexity = 0
            for node in ast.walk(tree):
                if isinstance(node, (ast.If, ast.For, ast.While, ast.Try, ast.ExceptHandler)):
                    complexity += 1
                elif isinstance(node, ast.FunctionDef):
                    complexity += 1
            
            file_info.complexity_score = complexity
            
            # Identify issues
            if complexity > 10:
                file_info.issues.append("High complexity - consider refactoring")
            
            if len(file_info.functions) > 20:
                file_info.issues.append("Too many functions - consider splitting")
            
            if len(file_info.classes) > 5:
                file_info.issues.append("Too many classes - consider modularization")
            
            # Generate suggestions
            if complexity > 5:
                file_info.suggestions.append("Extract complex logic into separate functions")
            
            if len(file_info.imports) > 15:
                file_info.suggestions.append("Consider organizing imports and removing unused ones")
                
        except SyntaxError:
            file_info.issues.append("Syntax error in Python code")
        except Exception as e:
            file_info.issues.append(f"Analysis error: {e}")
    
    def analyze_javascript_file(self, file_info: FileInfo, content: str):
        """Analyze JavaScript/TypeScript file"""
        # Extract imports
        import_pattern = r'import\s+(?:{[^}]*}|\*\s+as\s+\w+|\w+)\s+from\s+[\'"]([^\'"]+)[\'"]'
        imports = re.findall(import_pattern, content)
        file_info.imports.extend(imports)
        
        # Extract function definitions
        function_pattern = r'(?:function\s+(\w+)|const\s+(\w+)\s*=\s*(?:\([^)]*\)\s*=>|function)|(\w+)\s*\([^)]*\)\s*\{)'
        functions = re.findall(function_pattern, content)
        for func in functions:
            name = next((f for f in func if f), None)
            if name:
                file_info.functions.append(name)
        
        # Extract class definitions
        class_pattern = r'class\s+(\w+)'
        classes = re.findall(class_pattern, content)
        file_info.classes.extend(classes)
        
        # Calculate complexity
        complexity = len(re.findall(r'\b(if|for|while|switch|catch)\b', content))
        file_info.complexity_score = complexity
        
        # Identify issues
        if complexity > 15:
            file_info.issues.append("High complexity - consider refactoring")
        
        if len(file_info.functions) > 25:
            file_info.issues.append("Too many functions - consider splitting")
    
    def analyze_html_file(self, file_info: FileInfo, content: str):
        """Analyze HTML file"""
        # Extract script and style dependencies
        script_pattern = r'<script[^>]*src=[\'"]([^\'"]+)[\'"]'
        style_pattern = r'<link[^>]*href=[\'"]([^\'"]+)[\'"]'
        
        scripts = re.findall(script_pattern, content)
        styles = re.findall(style_pattern, content)
        
        file_info.dependencies.extend(scripts)
        file_info.dependencies.extend(styles)
        
        # Check for common issues
        if content.count('<div') > 20:
            file_info.issues.append("Too many div elements - consider semantic HTML")
        
        if not re.search(r'<meta[^>]*charset', content):
            file_info.suggestions.append("Add charset meta tag")
    
    def analyze_css_file(self, file_info: FileInfo, content: str):
        """Analyze CSS file"""
        # Check for common issues
        if content.count('!important') > 5:
            file_info.issues.append("Too many !important declarations - consider refactoring")
        
        if content.count('position: absolute') > 10:
            file_info.issues.append("Many absolute positions - consider flexbox/grid")
        
        # Calculate complexity
        selectors = len(re.findall(r'[.#][\w-]+', content))
        file_info.complexity_score = selectors / 10  # Normalize
    
    def scan_codebase(self) -> CodebaseStructure:
        """Scan and analyze the entire codebase"""
        files_info = []
        languages = {}
        file_types = {}
        all_dependencies = {}
        
        print("🔍 Scanning codebase...")
        
        for file_path in self.root_path.rglob('*'):
            if self.should_ignore(file_path):
                continue
            
            file_info = self.analyze_file(file_path)
            if file_info:
                files_info.append(file_info)
                
                # Count languages
                lang = file_info.file_type
                languages[lang] = languages.get(lang, 0) + 1
                
                # Count file types
                ext = Path(file_info.path).suffix
                file_types[ext] = file_types.get(ext, 0) + 1
                
                # Collect dependencies
                for dep in file_info.dependencies:
                    if dep not in all_dependencies:
                        all_dependencies[dep] = []
                    all_dependencies[dep].append(file_info.path)
        
        # Analyze architecture
        architecture = self.analyze_architecture(files_info)
        
        # Identify hotspots
        hotspots = self.identify_hotspots(files_info)
        
        # Identify technical debt
        technical_debt = self.identify_technical_debt(files_info)
        
        # Generate improvement opportunities
        opportunities = self.generate_improvement_opportunities(files_info)
        
        return CodebaseStructure(
            total_files=len(files_info),
            total_lines=sum(f.lines for f in files_info),
            languages=languages,
            file_types=file_types,
            dependencies=all_dependencies,
            architecture=architecture,
            hotspots=hotspots,
            technical_debt=technical_debt,
            improvement_opportunities=opportunities
        )
    
    def analyze_architecture(self, files_info: List[FileInfo]) -> Dict[str, List[str]]:
        """Analyze application architecture"""
        architecture = {
            'frontend': [],
            'backend': [],
            'database': [],
            'config': [],
            'docs': [],
            'tests': [],
            'scripts': []
        }
        
        for file_info in files_info:
            path = file_info.path.lower()
            
            if any(x in path for x in ['frontend', 'src', 'components', 'pages']):
                architecture['frontend'].append(file_info.path)
            elif any(x in path for x in ['backend', 'api', 'main_', 'database']):
                architecture['backend'].append(file_info.path)
            elif any(x in path for x in ['db', 'sql', 'migration']):
                architecture['database'].append(file_info.path)
            elif any(x in path for x in ['config', 'settings', '.env']):
                architecture['config'].append(file_info.path)
            elif any(x in path for x in ['readme', 'docs', 'documentation']):
                architecture['docs'].append(file_info.path)
            elif any(x in path for x in ['test', 'spec', '__tests__']):
                architecture['tests'].append(file_info.path)
            elif any(x in path for x in ['script', '.sh', 'start']):
                architecture['scripts'].append(file_info.path)
        
        return architecture
    
    def identify_hotspots(self, files_info: List[FileInfo]) -> List[str]:
        """Identify code hotspots (complex files)"""
        hotspots = []
        
        # Sort by complexity and size
        complex_files = sorted(
            files_info, 
            key=lambda x: (x.complexity_score, x.lines), 
            reverse=True
        )
        
        for file_info in complex_files[:10]:  # Top 10 hotspots
            if file_info.complexity_score > 5 or file_info.lines > 200:
                hotspots.append(f"{file_info.path} (complexity: {file_info.complexity_score}, lines: {file_info.lines})")
        
        return hotspots
    
    def identify_technical_debt(self, files_info: List[FileInfo]) -> List[str]:
        """Identify technical debt"""
        debt = []
        
        for file_info in files_info:
            for issue in file_info.issues:
                debt.append(f"{file_info.path}: {issue}")
        
        return debt
    
    def generate_improvement_opportunities(self, files_info: List[FileInfo]) -> List[str]:
        """Generate improvement opportunities"""
        opportunities = []
        
        # Performance opportunities
        large_files = [f for f in files_info if f.lines > 500]
        if large_files:
            opportunities.append(f"Refactor {len(large_files)} large files for better maintainability")
        
        # Code quality opportunities
        complex_files = [f for f in files_info if f.complexity_score > 10]
        if complex_files:
            opportunities.append(f"Reduce complexity in {len(complex_files)} files")
        
        # Testing opportunities
        test_files = [f for f in files_info if 'test' in f.path.lower()]
        if len(test_files) < len(files_info) * 0.2:  # Less than 20% test coverage
            opportunities.append("Increase test coverage")
        
        # Documentation opportunities
        doc_files = [f for f in files_info if f.file_type in ['Markdown', 'Documentation']]
        if len(doc_files) < 5:
            opportunities.append("Add more documentation")
        
        # Security opportunities
        for file_info in files_info:
            if any(x in file_info.path.lower() for x in ['password', 'secret', 'key']):
                if '.env' not in file_info.path:
                    opportunities.append(f"Secure sensitive data in {file_info.path}")
        
        return opportunities
    
    def generate_codebase_report(self) -> str:
        """Generate a comprehensive codebase report"""
        structure = self.scan_codebase()
        
        report = []
        report.append("📊 CODEBASE ANALYSIS REPORT")
        report.append("=" * 50)
        
        # Overview
        report.append(f"\n📈 OVERVIEW:")
        report.append(f"  Total Files: {structure.total_files}")
        report.append(f"  Total Lines: {structure.total_lines:,}")
        report.append(f"  Languages: {len(structure.languages)}")
        
        # Languages breakdown
        report.append(f"\n🔤 LANGUAGES:")
        for lang, count in sorted(structure.languages.items(), key=lambda x: x[1], reverse=True):
            report.append(f"  {lang}: {count} files")
        
        # Architecture
        report.append(f"\n🏗️  ARCHITECTURE:")
        for component, files in structure.architecture.items():
            if files:
                report.append(f"  {component.title()}: {len(files)} files")
        
        # Hotspots
        if structure.hotspots:
            report.append(f"\n🔥 CODE HOTSPOTS:")
            for hotspot in structure.hotspots[:5]:
                report.append(f"  • {hotspot}")
        
        # Technical debt
        if structure.technical_debt:
            report.append(f"\n⚠️  TECHNICAL DEBT:")
            for debt in structure.technical_debt[:10]:
                report.append(f"  • {debt}")
        
        # Improvement opportunities
        if structure.improvement_opportunities:
            report.append(f"\n💡 IMPROVEMENT OPPORTUNITIES:")
            for opportunity in structure.improvement_opportunities:
                report.append(f"  • {opportunity}")
        
        return "\n".join(report)
    
    def get_files_for_grok(self) -> Dict[str, str]:
        """Get key files for Grok to understand the codebase"""
        key_files = {}
        
        # Important configuration files
        config_files = [
            'package.json', 'requirements.txt', 'pyproject.toml',
            'next.config.js', 'tailwind.config.js', 'tsconfig.json',
            'dockerfile', 'docker-compose.yml', '.env.example'
        ]
        
        # Main application files
        main_files = [
            'main_enhanced.py', 'database.py', 'grok_client.py',
            'frontend/pages/index.tsx', 'frontend/styles/globals.css',
            'start.sh', 'README.md'
        ]
        
        for file_name in config_files + main_files:
            file_path = self.root_path / file_name
            if file_path.exists():
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        key_files[file_name] = f.read()
                except Exception as e:
                    print(f"Error reading {file_name}: {e}")
        
        return key_files

# Global analyzer instance
analyzer = CodebaseAnalyzer() 