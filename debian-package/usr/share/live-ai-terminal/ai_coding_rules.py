"""
AI CODING RULES AND STANDARDS
============================
This file defines the rules that Grok AI must ALWAYS follow when coding.
These rules are immutable and must be applied to every code change.
"""

import os
import json
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum

class FileType(Enum):
    PYTHON = "python"
    JAVASCRIPT = "javascript"
    TYPESCRIPT = "typescript"
    REACT = "react"
    HTML = "html"
    CSS = "css"
    SCSS = "scss"
    JSON = "json"
    YAML = "yaml"
    SQL = "sql"
    SHELL = "shell"
    MARKDOWN = "markdown"

class ComponentType(Enum):
    BACKEND = "backend"
    FRONTEND = "frontend"
    DATABASE = "database"
    CONFIG = "config"
    UTILS = "utils"
    TESTS = "tests"
    DOCS = "docs"
    SCRIPTS = "scripts"
    API = "api"

@dataclass
class CodingRule:
    rule_id: str
    category: str
    title: str
    description: str
    examples: List[str]
    priority: int  # 1-10, 10 being highest
    file_types: List[FileType]
    component_types: List[ComponentType]

class AICodingRules:
    def __init__(self):
        self.rules = self._initialize_rules()
        self.folder_structure = self._initialize_folder_structure()
        self.naming_conventions = self._initialize_naming_conventions()
        self.code_standards = self._initialize_code_standards()
        
    def _initialize_rules(self) -> List[CodingRule]:
        """Initialize all coding rules"""
        return [
            # File Organization Rules
            CodingRule(
                rule_id="FILE_001",
                category="File Organization",
                title="Consistent File Naming",
                description="All files must use snake_case for Python, kebab-case for frontend, and PascalCase for React components",
                examples=[
                    "Python: user_management.py, database_connection.py",
                    "Frontend: user-profile.tsx, video-player.tsx",
                    "React Components: UserProfile.tsx, VideoPlayer.tsx"
                ],
                priority=10,
                file_types=[FileType.PYTHON, FileType.JAVASCRIPT, FileType.TYPESCRIPT, FileType.REACT],
                component_types=[ComponentType.BACKEND, ComponentType.FRONTEND]
            ),
            
            CodingRule(
                rule_id="FILE_002",
                category="File Organization",
                title="Logical Folder Structure",
                description="Organize files by feature/domain, not by type",
                examples=[
                    "✅ Good: /user/ (models, views, controllers)",
                    "❌ Bad: /models/, /views/, /controllers/"
                ],
                priority=9,
                file_types=[FileType.PYTHON, FileType.JAVASCRIPT, FileType.TYPESCRIPT],
                component_types=[ComponentType.BACKEND, ComponentType.FRONTEND]
            ),
            
            # Code Quality Rules
            CodingRule(
                rule_id="CODE_001",
                category="Code Quality",
                title="Single Responsibility Principle",
                description="Each function/class must have one clear purpose",
                examples=[
                    "✅ Good: def validate_email(email: str) -> bool:",
                    "❌ Bad: def process_user_data_and_send_email_and_update_database():"
                ],
                priority=10,
                file_types=[FileType.PYTHON, FileType.JAVASCRIPT, FileType.TYPESCRIPT],
                component_types=[ComponentType.BACKEND, ComponentType.FRONTEND]
            ),
            
            CodingRule(
                rule_id="CODE_002",
                category="Code Quality",
                title="Type Hints and Documentation",
                description="All functions must have type hints and docstrings",
                examples=[
                    "def get_user_by_id(user_id: int) -> Optional[User]:",
                    '    """Retrieve user by ID from database."""'
                ],
                priority=8,
                file_types=[FileType.PYTHON, FileType.TYPESCRIPT],
                component_types=[ComponentType.BACKEND, ComponentType.FRONTEND]
            ),
            
            # Security Rules
            CodingRule(
                rule_id="SEC_001",
                category="Security",
                title="Input Validation",
                description="Validate all user inputs and sanitize data",
                examples=[
                    "from pydantic import BaseModel, validator",
                    "class UserInput(BaseModel):",
                    "    email: str",
                    "    @validator('email')",
                    "    def validate_email(cls, v):"
                ],
                priority=10,
                file_types=[FileType.PYTHON, FileType.TYPESCRIPT],
                component_types=[ComponentType.BACKEND, ComponentType.FRONTEND]
            ),
            
            CodingRule(
                rule_id="SEC_002",
                category="Security",
                title="SQL Injection Prevention",
                description="Always use parameterized queries or ORM",
                examples=[
                    "✅ Good: cursor.execute('SELECT * FROM users WHERE id = %s', (user_id,))",
                    "❌ Bad: cursor.execute(f'SELECT * FROM users WHERE id = {user_id}')"
                ],
                priority=10,
                file_types=[FileType.PYTHON, FileType.SQL],
                component_types=[ComponentType.BACKEND, ComponentType.DATABASE]
            ),
            
            # Performance Rules
            CodingRule(
                rule_id="PERF_001",
                category="Performance",
                title="Database Query Optimization",
                description="Use indexes, limit results, and avoid N+1 queries",
                examples=[
                    "✅ Good: users = User.objects.select_related('profile').filter(active=True)[:100]",
                    "❌ Bad: for user in User.objects.all(): user.profile.name"
                ],
                priority=8,
                file_types=[FileType.PYTHON, FileType.SQL],
                component_types=[ComponentType.BACKEND, ComponentType.DATABASE]
            ),
            
            CodingRule(
                rule_id="PERF_002",
                category="Performance",
                title="Async/Await Usage",
                description="Use async/await for I/O operations",
                examples=[
                    "async def fetch_user_data(user_id: int) -> User:",
                    "    async with aiohttp.ClientSession() as session:",
                    "        async with session.get(url) as response:"
                ],
                priority=7,
                file_types=[FileType.PYTHON, FileType.JAVASCRIPT, FileType.TYPESCRIPT],
                component_types=[ComponentType.BACKEND, ComponentType.FRONTEND]
            ),
            
            # Error Handling Rules
            CodingRule(
                rule_id="ERROR_001",
                category="Error Handling",
                title="Comprehensive Error Handling",
                description="Handle all possible errors with meaningful messages",
                examples=[
                    "try:",
                    "    result = risky_operation()",
                    "except SpecificError as e:",
                    "    logger.error(f'Operation failed: {e}')",
                    "    raise CustomError('User-friendly message')"
                ],
                priority=9,
                file_types=[FileType.PYTHON, FileType.JAVASCRIPT, FileType.TYPESCRIPT],
                component_types=[ComponentType.BACKEND, ComponentType.FRONTEND]
            ),
            
            # Testing Rules
            CodingRule(
                rule_id="TEST_001",
                category="Testing",
                title="Test Coverage",
                description="Write tests for all business logic",
                examples=[
                    "def test_user_creation():",
                    "    user = User.create(name='Test', email='test@example.com')",
                    "    assert user.name == 'Test'",
                    "    assert user.email == 'test@example.com'"
                ],
                priority=8,
                file_types=[FileType.PYTHON, FileType.JAVASCRIPT, FileType.TYPESCRIPT],
                component_types=[ComponentType.BACKEND, ComponentType.FRONTEND, ComponentType.TESTS]
            ),
            
            # API Design Rules
            CodingRule(
                rule_id="API_001",
                category="API Design",
                title="RESTful Endpoints",
                description="Follow REST conventions for API endpoints",
                examples=[
                    "GET /api/users - List users",
                    "POST /api/users - Create user",
                    "PUT /api/users/{id} - Update user",
                    "DELETE /api/users/{id} - Delete user"
                ],
                priority=9,
                file_types=[FileType.PYTHON, FileType.JAVASCRIPT, FileType.TYPESCRIPT],
                component_types=[ComponentType.BACKEND, ComponentType.API]
            ),
            
            # Frontend Rules
            CodingRule(
                rule_id="FE_001",
                category="Frontend",
                title="Component Structure",
                description="Use consistent component structure with props interface",
                examples=[
                    "interface UserProfileProps {",
                    "    user: User;",
                    "    onUpdate: (user: User) => void;",
                    "}",
                    "export const UserProfile: React.FC<UserProfileProps> = ({ user, onUpdate }) => {"
                ],
                priority=8,
                file_types=[FileType.REACT, FileType.TYPESCRIPT],
                component_types=[ComponentType.FRONTEND]
            ),
            
            CodingRule(
                rule_id="FE_002",
                category="Frontend",
                title="State Management",
                description="Use appropriate state management patterns",
                examples=[
                    "// Local state for component-specific data",
                    "const [isLoading, setIsLoading] = useState(false);",
                    "// Global state for shared data",
                    "const { user, setUser } = useUserContext();"
                ],
                priority=7,
                file_types=[FileType.REACT, FileType.TYPESCRIPT],
                component_types=[ComponentType.FRONTEND]
            ),
            
            # Database Rules
            CodingRule(
                rule_id="DB_001",
                category="Database",
                title="Schema Design",
                description="Design normalized schemas with proper relationships",
                examples=[
                    "CREATE TABLE users (",
                    "    id SERIAL PRIMARY KEY,",
                    "    email VARCHAR(255) UNIQUE NOT NULL,",
                    "    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP",
                    ");"
                ],
                priority=9,
                file_types=[FileType.SQL],
                component_types=[ComponentType.DATABASE]
            ),
            
            # Configuration Rules
            CodingRule(
                rule_id="CONFIG_001",
                category="Configuration",
                title="Environment Variables",
                description="Use environment variables for configuration",
                examples=[
                    "DATABASE_URL=postgresql://user:pass@localhost/db",
                    "API_KEY=${GROK_API_KEY}",
                    "DEBUG=false"
                ],
                priority=8,
                file_types=[FileType.PYTHON, FileType.JAVASCRIPT, FileType.YAML],
                component_types=[ComponentType.CONFIG]
            )
        ]
    
    def _initialize_folder_structure(self) -> Dict[str, Any]:
        """Define standard folder structure"""
        return {
            "backend": {
                "api": {
                    "endpoints": "API route handlers",
                    "middleware": "Custom middleware",
                    "dependencies": "Dependency injection"
                },
                "core": {
                    "config": "Configuration management",
                    "database": "Database models and migrations",
                    "security": "Security utilities"
                },
                "services": {
                    "business_logic": "Business logic services",
                    "external": "External API integrations"
                },
                "utils": {
                    "helpers": "Helper functions",
                    "validators": "Data validation"
                },
                "tests": {
                    "unit": "Unit tests",
                    "integration": "Integration tests",
                    "fixtures": "Test data"
                }
            },
            "frontend": {
                "components": {
                    "ui": "Reusable UI components",
                    "forms": "Form components",
                    "layout": "Layout components"
                },
                "pages": {
                    "routes": "Page components",
                    "api": "API route handlers"
                },
                "hooks": {
                    "custom": "Custom React hooks"
                },
                "utils": {
                    "helpers": "Helper functions",
                    "api": "API client functions"
                },
                "styles": {
                    "globals": "Global styles",
                    "components": "Component-specific styles"
                },
                "types": {
                    "interfaces": "TypeScript interfaces"
                }
            },
            "shared": {
                "types": "Shared type definitions",
                "constants": "Shared constants",
                "utils": "Shared utilities"
            }
        }
    
    def _initialize_naming_conventions(self) -> Dict[str, Dict[str, str]]:
        """Define naming conventions for different file types"""
        return {
            "python": {
                "files": "snake_case",
                "classes": "PascalCase",
                "functions": "snake_case",
                "variables": "snake_case",
                "constants": "UPPER_SNAKE_CASE",
                "modules": "snake_case"
            },
            "javascript": {
                "files": "kebab-case",
                "classes": "PascalCase",
                "functions": "camelCase",
                "variables": "camelCase",
                "constants": "UPPER_SNAKE_CASE",
                "modules": "camelCase"
            },
            "typescript": {
                "files": "kebab-case",
                "classes": "PascalCase",
                "functions": "camelCase",
                "variables": "camelCase",
                "constants": "UPPER_SNAKE_CASE",
                "interfaces": "PascalCase",
                "types": "PascalCase"
            },
            "react": {
                "components": "PascalCase",
                "files": "PascalCase.tsx",
                "hooks": "useCamelCase",
                "props": "PascalCaseProps"
            },
            "css": {
                "files": "kebab-case",
                "classes": "kebab-case",
                "variables": "kebab-case"
            },
            "sql": {
                "tables": "snake_case",
                "columns": "snake_case",
                "functions": "snake_case"
            }
        }
    
    def _initialize_code_standards(self) -> Dict[str, Any]:
        """Define code formatting and style standards"""
        return {
            "python": {
                "formatter": "black",
                "line_length": 88,
                "imports": "isort",
                "linter": "flake8",
                "docstring_style": "google"
            },
            "javascript": {
                "formatter": "prettier",
                "line_length": 80,
                "semicolons": True,
                "quotes": "single"
            },
            "typescript": {
                "formatter": "prettier",
                "line_length": 80,
                "strict": True,
                "no_any": True
            },
            "react": {
                "formatter": "prettier",
                "jsx_single_quotes": True,
                "trailing_comma": "es5"
            }
        }
    
    def get_rules_by_category(self, category: str) -> List[CodingRule]:
        """Get rules by category"""
        return [rule for rule in self.rules if rule.category == category]
    
    def get_rules_by_file_type(self, file_type: FileType) -> List[CodingRule]:
        """Get rules applicable to a specific file type"""
        return [rule for rule in self.rules if file_type in rule.file_types]
    
    def get_rules_by_priority(self, min_priority: int = 8) -> List[CodingRule]:
        """Get rules by minimum priority"""
        return [rule for rule in self.rules if rule.priority >= min_priority]
    
    def validate_file_structure(self, file_path: str) -> List[str]:
        """Validate if a file follows the folder structure rules"""
        violations = []
        path_parts = file_path.split('/')
        
        # Check if file is in appropriate folder
        if len(path_parts) >= 2:
            component = path_parts[0]
            subfolder = path_parts[1] if len(path_parts) > 1 else ""
            
            if component == "backend" and subfolder not in self.folder_structure["backend"]:
                violations.append(f"Backend file should be in appropriate subfolder: {subfolder}")
            elif component == "frontend" and subfolder not in self.folder_structure["frontend"]:
                violations.append(f"Frontend file should be in appropriate subfolder: {subfolder}")
        
        return violations
    
    def validate_naming(self, name: str, file_type: str, naming_type: str) -> bool:
        """Validate naming convention"""
        conventions = self.naming_conventions.get(file_type, {})
        expected_pattern = conventions.get(naming_type, "")
        
        if not expected_pattern:
            return True
        
        # Simple pattern matching (can be enhanced with regex)
        if expected_pattern == "snake_case":
            return "_" in name and name.islower()
        elif expected_pattern == "camelCase":
            return name[0].islower() and any(c.isupper() for c in name)
        elif expected_pattern == "PascalCase":
            return name[0].isupper() and any(c.isupper() for c in name)
        elif expected_pattern == "kebab-case":
            return "-" in name and name.islower()
        elif expected_pattern == "UPPER_SNAKE_CASE":
            return "_" in name and name.isupper()
        
        return True
    
    def get_code_standards(self, file_type: str) -> Dict[str, Any]:
        """Get code standards for a file type"""
        return self.code_standards.get(file_type, {})
    
    def export_rules(self) -> str:
        """Export rules as formatted text"""
        output = []
        output.append("🤖 AI CODING RULES AND STANDARDS")
        output.append("=" * 50)
        
        # Group by category
        categories = {}
        for rule in self.rules:
            if rule.category not in categories:
                categories[rule.category] = []
            categories[rule.category].append(rule)
        
        for category, rules in categories.items():
            output.append(f"\n📋 {category.upper()}")
            output.append("-" * 30)
            
            for rule in sorted(rules, key=lambda x: x.priority, reverse=True):
                output.append(f"\n🔸 {rule.title} (Priority: {rule.priority})")
                output.append(f"   {rule.description}")
                for example in rule.examples:
                    output.append(f"   • {example}")
        
        return "\n".join(output)

# Global instance
ai_rules = AICodingRules() 