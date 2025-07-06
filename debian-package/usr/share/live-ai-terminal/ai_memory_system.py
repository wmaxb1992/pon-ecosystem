"""
AI MEMORY SYSTEM
===============
Advanced indexing and recall system for Grok AI to remember code patterns,
folder structures, and coding decisions for rapid formatting and consistency.
"""

import json
import hashlib
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass, asdict
from pathlib import Path
import pickle
import zlib

@dataclass
class CodePattern:
    pattern_id: str
    pattern_type: str  # "function", "class", "component", "api_endpoint", "database_query"
    language: str
    content: str
    context: Dict[str, Any]
    usage_count: int
    success_rate: float
    last_used: datetime
    created_at: datetime
    tags: List[str]
    complexity_score: float
    performance_score: float

@dataclass
class FolderStructure:
    path: str
    structure_type: str  # "backend", "frontend", "database", "config"
    files: List[str]
    subfolders: List[str]
    patterns: List[str]
    last_updated: datetime
    usage_frequency: int

@dataclass
class CodingDecision:
    decision_id: str
    context: str
    problem: str
    solution: str
    rationale: str
    alternatives: List[str]
    chosen_approach: str
    outcome: str
    created_at: datetime
    tags: List[str]
    confidence_score: float

@dataclass
class CodeIndex:
    file_path: str
    file_hash: str
    content_hash: str
    patterns: List[str]
    dependencies: List[str]
    imports: List[str]
    functions: List[str]
    classes: List[str]
    complexity: float
    last_modified: datetime
    indexed_at: datetime

class AIMemorySystem:
    def __init__(self, db_path: str = "ai_memory.db"):
        self.db_path = db_path
        self.init_database()
        self.pattern_cache = {}
        self.structure_cache = {}
        self.decision_cache = {}
        self.index_cache = {}
        
    def init_database(self):
        """Initialize SQLite database for AI memory"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Code patterns table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS code_patterns (
                pattern_id TEXT PRIMARY KEY,
                pattern_type TEXT NOT NULL,
                language TEXT NOT NULL,
                content TEXT NOT NULL,
                context TEXT,
                usage_count INTEGER DEFAULT 0,
                success_rate REAL DEFAULT 0.0,
                last_used TEXT,
                created_at TEXT,
                tags TEXT,
                complexity_score REAL DEFAULT 0.0,
                performance_score REAL DEFAULT 0.0
            )
        ''')
        
        # Folder structures table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS folder_structures (
                path TEXT PRIMARY KEY,
                structure_type TEXT NOT NULL,
                files TEXT,
                subfolders TEXT,
                patterns TEXT,
                last_updated TEXT,
                usage_frequency INTEGER DEFAULT 0
            )
        ''')
        
        # Coding decisions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS coding_decisions (
                decision_id TEXT PRIMARY KEY,
                context TEXT NOT NULL,
                problem TEXT NOT NULL,
                solution TEXT NOT NULL,
                rationale TEXT,
                alternatives TEXT,
                chosen_approach TEXT NOT NULL,
                outcome TEXT,
                created_at TEXT,
                tags TEXT,
                confidence_score REAL DEFAULT 0.0
            )
        ''')
        
        # Code index table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS code_index (
                file_path TEXT PRIMARY KEY,
                file_hash TEXT NOT NULL,
                content_hash TEXT NOT NULL,
                patterns TEXT,
                dependencies TEXT,
                imports TEXT,
                functions TEXT,
                classes TEXT,
                complexity REAL DEFAULT 0.0,
                last_modified TEXT,
                indexed_at TEXT
            )
        ''')
        
        # Pattern usage history
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pattern_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_id TEXT,
                file_path TEXT,
                usage_context TEXT,
                success BOOLEAN,
                timestamp TEXT,
                performance_metrics TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_code_pattern(self, pattern: CodePattern) -> bool:
        """Add a new code pattern to memory"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO code_patterns VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                pattern.pattern_id,
                pattern.pattern_type,
                pattern.language,
                pattern.content,
                json.dumps(pattern.context),
                pattern.usage_count,
                pattern.success_rate,
                pattern.last_used.isoformat(),
                pattern.created_at.isoformat(),
                json.dumps(pattern.tags),
                pattern.complexity_score,
                pattern.performance_score
            ))
            
            conn.commit()
            self.pattern_cache[pattern.pattern_id] = pattern
            return True
        except Exception as e:
            print(f"Error adding code pattern: {e}")
            return False
        finally:
            conn.close()
    
    def get_code_patterns(self, pattern_type: Optional[str] = None, 
                         language: Optional[str] = None, 
                         tags: Optional[List[str]] = None) -> List[CodePattern]:
        """Get code patterns with optional filtering"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT * FROM code_patterns WHERE 1=1"
        params = []
        
        if pattern_type:
            query += " AND pattern_type = ?"
            params.append(pattern_type)
        
        if language:
            query += " AND language = ?"
            params.append(language)
        
        if tags:
            for tag in tags:
                query += " AND tags LIKE ?"
                params.append(f"%{tag}%")
        
        query += " ORDER BY usage_count DESC, success_rate DESC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        patterns = []
        for row in rows:
            pattern = CodePattern(
                pattern_id=row[0],
                pattern_type=row[1],
                language=row[2],
                content=row[3],
                context=json.loads(row[4]) if row[4] else {},
                usage_count=row[5],
                success_rate=row[6],
                last_used=datetime.fromisoformat(row[7]) if row[7] else None,
                created_at=datetime.fromisoformat(row[8]),
                tags=json.loads(row[9]) if row[9] else [],
                complexity_score=row[10],
                performance_score=row[11]
            )
            patterns.append(pattern)
        
        return patterns
    
    def find_similar_patterns(self, content: str, pattern_type: str, 
                            language: str, threshold: float = 0.7) -> List[CodePattern]:
        """Find similar code patterns using content similarity"""
        patterns = self.get_code_patterns(pattern_type, language)
        similar_patterns = []
        
        content_hash = hashlib.md5(content.encode()).hexdigest()
        
        for pattern in patterns:
            # Simple similarity check (can be enhanced with more sophisticated algorithms)
            pattern_hash = hashlib.md5(pattern.content.encode()).hexdigest()
            similarity = self._calculate_similarity(content_hash, pattern_hash)
            
            if similarity >= threshold:
                similar_patterns.append(pattern)
        
        return sorted(similar_patterns, key=lambda x: x.success_rate, reverse=True)
    
    def _calculate_similarity(self, hash1: str, hash2: str) -> float:
        """Calculate similarity between two hashes"""
        # Simple hash similarity (can be enhanced)
        common_chars = sum(1 for a, b in zip(hash1, hash2) if a == b)
        return common_chars / len(hash1)
    
    def add_folder_structure(self, structure: FolderStructure) -> bool:
        """Add folder structure to memory"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO folder_structures VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                structure.path,
                structure.structure_type,
                json.dumps(structure.files),
                json.dumps(structure.subfolders),
                json.dumps(structure.patterns),
                structure.last_updated.isoformat(),
                structure.usage_frequency
            ))
            
            conn.commit()
            self.structure_cache[structure.path] = structure
            return True
        except Exception as e:
            print(f"Error adding folder structure: {e}")
            return False
        finally:
            conn.close()
    
    def get_folder_structure(self, structure_type: str) -> List[FolderStructure]:
        """Get folder structures by type"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT * FROM folder_structures WHERE structure_type = ? ORDER BY usage_frequency DESC
        ''', (structure_type,))
        
        rows = cursor.fetchall()
        conn.close()
        
        structures = []
        for row in rows:
            structure = FolderStructure(
                path=row[0],
                structure_type=row[1],
                files=json.loads(row[2]) if row[2] else [],
                subfolders=json.loads(row[3]) if row[3] else [],
                patterns=json.loads(row[4]) if row[4] else [],
                last_updated=datetime.fromisoformat(row[5]),
                usage_frequency=row[6]
            )
            structures.append(structure)
        
        return structures
    
    def add_coding_decision(self, decision: CodingDecision) -> bool:
        """Add coding decision to memory"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO coding_decisions VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                decision.decision_id,
                decision.context,
                decision.problem,
                decision.solution,
                decision.rationale,
                json.dumps(decision.alternatives),
                decision.chosen_approach,
                decision.outcome,
                decision.created_at.isoformat(),
                json.dumps(decision.tags),
                decision.confidence_score
            ))
            
            conn.commit()
            self.decision_cache[decision.decision_id] = decision
            return True
        except Exception as e:
            print(f"Error adding coding decision: {e}")
            return False
        finally:
            conn.close()
    
    def get_coding_decisions(self, context: Optional[str] = None, 
                           tags: Optional[List[str]] = None) -> List[CodingDecision]:
        """Get coding decisions with optional filtering"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT * FROM coding_decisions WHERE 1=1"
        params = []
        
        if context:
            query += " AND context LIKE ?"
            params.append(f"%{context}%")
        
        if tags:
            for tag in tags:
                query += " AND tags LIKE ?"
                params.append(f"%{tag}%")
        
        query += " ORDER BY confidence_score DESC, created_at DESC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        decisions = []
        for row in rows:
            decision = CodingDecision(
                decision_id=row[0],
                context=row[1],
                problem=row[2],
                solution=row[3],
                rationale=row[4],
                alternatives=json.loads(row[5]) if row[5] else [],
                chosen_approach=row[6],
                outcome=row[7],
                created_at=datetime.fromisoformat(row[8]),
                tags=json.loads(row[9]) if row[9] else [],
                confidence_score=row[10]
            )
            decisions.append(decision)
        
        return decisions
    
    def index_file(self, file_path: str, content: str) -> bool:
        """Index a file for rapid recall"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            # Generate hashes
            file_hash = hashlib.md5(file_path.encode()).hexdigest()
            content_hash = hashlib.md5(content.encode()).hexdigest()
            
            # Extract patterns (simplified)
            patterns = self._extract_patterns(content)
            dependencies = self._extract_dependencies(content)
            imports = self._extract_imports(content)
            functions = self._extract_functions(content)
            classes = self._extract_classes(content)
            complexity = self._calculate_complexity(content)
            
            cursor.execute('''
                INSERT OR REPLACE INTO code_index VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                file_path,
                file_hash,
                content_hash,
                json.dumps(patterns),
                json.dumps(dependencies),
                json.dumps(imports),
                json.dumps(functions),
                json.dumps(classes),
                complexity,
                datetime.now().isoformat(),
                datetime.now().isoformat()
            ))
            
            conn.commit()
            
            # Update cache
            index_entry = CodeIndex(
                file_path=file_path,
                file_hash=file_hash,
                content_hash=content_hash,
                patterns=patterns,
                dependencies=dependencies,
                imports=imports,
                functions=functions,
                classes=classes,
                complexity=complexity,
                last_modified=datetime.now(),
                indexed_at=datetime.now()
            )
            self.index_cache[file_path] = index_entry
            
            return True
        except Exception as e:
            print(f"Error indexing file: {e}")
            return False
        finally:
            conn.close()
    
    def _extract_patterns(self, content: str) -> List[str]:
        """Extract code patterns from content"""
        patterns = []
        
        # Look for common patterns
        if "async def" in content:
            patterns.append("async_function")
        if "class " in content:
            patterns.append("class_definition")
        if "@app.route" in content or "@app.get" in content:
            patterns.append("api_endpoint")
        if "SELECT" in content.upper():
            patterns.append("database_query")
        if "useState" in content or "useEffect" in content:
            patterns.append("react_hooks")
        
        return patterns
    
    def _extract_dependencies(self, content: str) -> List[str]:
        """Extract dependencies from content"""
        dependencies = []
        
        # Python imports
        import_lines = [line for line in content.split('\n') if line.strip().startswith('import ') or line.strip().startswith('from ')]
        for line in import_lines:
            if 'import ' in line:
                dep = line.split('import ')[1].split(' as ')[0].strip()
                dependencies.append(dep)
            elif 'from ' in line:
                dep = line.split('from ')[1].split(' import ')[0].strip()
                dependencies.append(dep)
        
        return dependencies
    
    def _extract_imports(self, content: str) -> List[str]:
        """Extract import statements"""
        return [line.strip() for line in content.split('\n') 
                if line.strip().startswith(('import ', 'from ', 'import {', 'import *'))]
    
    def _extract_functions(self, content: str) -> List[str]:
        """Extract function names"""
        functions = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('def ') or line.startswith('async def '):
                func_name = line.split('def ')[1].split('(')[0].strip()
                functions.append(func_name)
            elif 'function ' in line or 'const ' in line and '= (' in line:
                # JavaScript/TypeScript functions
                if 'function ' in line:
                    func_name = line.split('function ')[1].split('(')[0].strip()
                else:
                    func_name = line.split('const ')[1].split(' = ')[0].strip()
                functions.append(func_name)
        
        return functions
    
    def _extract_classes(self, content: str) -> List[str]:
        """Extract class names"""
        classes = []
        lines = content.split('\n')
        
        for line in lines:
            line = line.strip()
            if line.startswith('class '):
                class_name = line.split('class ')[1].split('(')[0].split(':')[0].strip()
                classes.append(class_name)
        
        return classes
    
    def _calculate_complexity(self, content: str) -> float:
        """Calculate code complexity score"""
        complexity = 0.0
        
        # Count control structures
        complexity += content.count('if ') * 1
        complexity += content.count('for ') * 1
        complexity += content.count('while ') * 1
        complexity += content.count('try:') * 1
        complexity += content.count('except') * 1
        
        # Count functions and classes
        complexity += content.count('def ') * 0.5
        complexity += content.count('class ') * 0.5
        
        # Normalize by lines
        lines = len(content.split('\n'))
        if lines > 0:
            complexity = complexity / lines
        
        return complexity
    
    def recall_pattern(self, context: str, pattern_type: str, language: str) -> Optional[CodePattern]:
        """Recall the best pattern for a given context"""
        patterns = self.get_code_patterns(pattern_type, language)
        
        if not patterns:
            return None
        
        # Find the most successful pattern for this context
        best_pattern = None
        best_score = 0.0
        
        for pattern in patterns:
            # Calculate context similarity
            context_similarity = self._calculate_context_similarity(context, pattern.context)
            score = pattern.success_rate * context_similarity
            
            if score > best_score:
                best_score = score
                best_pattern = pattern
        
        return best_pattern
    
    def _calculate_context_similarity(self, context1: str, context2: Dict[str, Any]) -> float:
        """Calculate similarity between contexts"""
        # Simple keyword matching (can be enhanced)
        context1_words = set(context1.lower().split())
        context2_words = set(str(context2).lower().split())
        
        if not context1_words or not context2_words:
            return 0.0
        
        intersection = context1_words.intersection(context2_words)
        union = context1_words.union(context2_words)
        
        return len(intersection) / len(union)
    
    def get_memory_stats(self) -> Dict[str, Any]:
        """Get memory system statistics"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        stats = {}
        
        # Pattern stats
        cursor.execute("SELECT COUNT(*) FROM code_patterns")
        stats['total_patterns'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT AVG(success_rate) FROM code_patterns")
        stats['avg_success_rate'] = cursor.fetchone()[0] or 0.0
        
        # Structure stats
        cursor.execute("SELECT COUNT(*) FROM folder_structures")
        stats['total_structures'] = cursor.fetchone()[0]
        
        # Decision stats
        cursor.execute("SELECT COUNT(*) FROM coding_decisions")
        stats['total_decisions'] = cursor.fetchone()[0]
        
        cursor.execute("SELECT AVG(confidence_score) FROM coding_decisions")
        stats['avg_confidence'] = cursor.fetchone()[0] or 0.0
        
        # Index stats
        cursor.execute("SELECT COUNT(*) FROM code_index")
        stats['total_indexed_files'] = cursor.fetchone()[0]
        
        conn.close()
        
        return stats
    
    def export_memory(self, file_path: str):
        """Export memory to file"""
        data = {
            'patterns': [asdict(p) for p in self.pattern_cache.values()],
            'structures': [asdict(s) for s in self.structure_cache.values()],
            'decisions': [asdict(d) for d in self.decision_cache.values()],
            'index': [asdict(i) for i in self.index_cache.values()],
            'stats': self.get_memory_stats(),
            'exported_at': datetime.now().isoformat()
        }
        
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
    
    def import_memory(self, file_path: str):
        """Import memory from file"""
        with open(file_path, 'r') as f:
            data = json.load(f)
        
        # Import patterns
        for pattern_data in data.get('patterns', []):
            pattern = CodePattern(**pattern_data)
            self.add_code_pattern(pattern)
        
        # Import structures
        for structure_data in data.get('structures', []):
            structure = FolderStructure(**structure_data)
            self.add_folder_structure(structure)
        
        # Import decisions
        for decision_data in data.get('decisions', []):
            decision = CodingDecision(**decision_data)
            self.add_coding_decision(decision)

# Global memory system instance
ai_memory = AIMemorySystem() 