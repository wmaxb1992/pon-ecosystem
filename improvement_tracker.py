import json
import os
import time
from datetime import datetime, timedelta
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import sqlite3
from pathlib import Path

class ImprovementCategory(Enum):
    UI_UX = "UI/UX"
    PERFORMANCE = "Performance"
    SECURITY = "Security"
    FEATURES = "Features"
    CODE_QUALITY = "Code Quality"
    DATABASE = "Database"
    API = "API"
    FRONTEND = "Frontend"
    BACKEND = "Backend"
    DEPLOYMENT = "Deployment"
    MONITORING = "Monitoring"
    TESTING = "Testing"
    DOCUMENTATION = "Documentation"
    ACCESSIBILITY = "Accessibility"
    SEO = "SEO"
    MOBILE = "Mobile"
    INTEGRATION = "Integration"
    AUTOMATION = "Automation"
    SCALABILITY = "Scalability"
    USER_EXPERIENCE = "User Experience"

class ImprovementStatus(Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    IMPLEMENTED = "implemented"
    TESTING = "testing"
    DEPLOYED = "deployed"

@dataclass
class Improvement:
    id: str
    title: str
    description: str
    category: ImprovementCategory
    priority: int  # 1-10, 10 being highest
    estimated_effort: str  # "5min", "1hour", "1day", etc.
    status: ImprovementStatus
    created_at: datetime
    implemented_at: Optional[datetime] = None
    grok_suggested: bool = False
    user_approved: bool = False
    impact_score: int = 5  # 1-10
    complexity: int = 5  # 1-10
    tags: List[str] = None
    files_affected: List[str] = None
    dependencies: List[str] = None

@dataclass
class Milestone:
    id: str
    title: str
    description: str
    target_date: datetime
    improvements: List[str]  # List of improvement IDs
    status: str  # "active", "completed", "overdue"
    created_at: datetime
    completed_at: Optional[datetime] = None

class ImprovementTracker:
    def __init__(self, db_path: str = "improvements.db"):
        self.db_path = db_path
        self.init_database()
        self.last_commit_time = datetime.now()
        self.improvements_since_commit = 0
        self.commit_interval = timedelta(minutes=15)
        self.target_improvements_per_commit = 8
        
    def init_database(self):
        """Initialize SQLite database for improvements tracking"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Create improvements table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS improvements (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                category TEXT NOT NULL,
                priority INTEGER,
                estimated_effort TEXT,
                status TEXT NOT NULL,
                created_at TEXT,
                implemented_at TEXT,
                grok_suggested BOOLEAN,
                user_approved BOOLEAN,
                impact_score INTEGER,
                complexity INTEGER,
                tags TEXT,
                files_affected TEXT,
                dependencies TEXT
            )
        ''')
        
        # Create milestones table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS milestones (
                id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                description TEXT,
                target_date TEXT,
                improvements TEXT,
                status TEXT,
                created_at TEXT,
                completed_at TEXT
            )
        ''')
        
        # Create improvement_log table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS improvement_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                improvement_id TEXT,
                action TEXT,
                timestamp TEXT,
                details TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def add_improvement(self, improvement: Improvement) -> bool:
        """Add a new improvement to the tracker"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO improvements VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                improvement.id,
                improvement.title,
                improvement.description,
                improvement.category.value,
                improvement.priority,
                improvement.estimated_effort,
                improvement.status.value,
                improvement.created_at.isoformat(),
                improvement.implemented_at.isoformat() if improvement.implemented_at else None,
                improvement.grok_suggested,
                improvement.user_approved,
                improvement.impact_score,
                improvement.complexity,
                json.dumps(improvement.tags) if improvement.tags else None,
                json.dumps(improvement.files_affected) if improvement.files_affected else None,
                json.dumps(improvement.dependencies) if improvement.dependencies else None
            ))
            
            # Log the addition
            cursor.execute('''
                INSERT INTO improvement_log (improvement_id, action, timestamp, details)
                VALUES (?, ?, ?, ?)
            ''', (
                improvement.id,
                'created',
                datetime.now().isoformat(),
                f"Added improvement: {improvement.title}"
            ))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error adding improvement: {e}")
            return False
        finally:
            conn.close()
    
    def get_improvements(self, category: Optional[ImprovementCategory] = None, 
                        status: Optional[ImprovementStatus] = None) -> List[Improvement]:
        """Get improvements with optional filtering"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        query = "SELECT * FROM improvements WHERE 1=1"
        params = []
        
        if category:
            query += " AND category = ?"
            params.append(category.value)
        
        if status:
            query += " AND status = ?"
            params.append(status.value)
        
        query += " ORDER BY priority DESC, created_at DESC"
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        
        improvements = []
        for row in rows:
            improvement = Improvement(
                id=row[0],
                title=row[1],
                description=row[2],
                category=ImprovementCategory(row[3]),
                priority=row[4],
                estimated_effort=row[5],
                status=ImprovementStatus(row[6]),
                created_at=datetime.fromisoformat(row[7]),
                implemented_at=datetime.fromisoformat(row[8]) if row[8] else None,
                grok_suggested=bool(row[9]),
                user_approved=bool(row[10]),
                impact_score=row[11],
                complexity=row[12],
                tags=json.loads(row[13]) if row[13] else None,
                files_affected=json.loads(row[14]) if row[14] else None,
                dependencies=json.loads(row[15]) if row[15] else None
            )
            improvements.append(improvement)
        
        return improvements
    
    def update_improvement_status(self, improvement_id: str, status: ImprovementStatus) -> bool:
        """Update improvement status"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE improvements SET status = ? WHERE id = ?
            ''', (status.value, improvement_id))
            
            # Log the update
            cursor.execute('''
                INSERT INTO improvement_log (improvement_id, action, timestamp, details)
                VALUES (?, ?, ?, ?)
            ''', (
                improvement_id,
                'status_updated',
                datetime.now().isoformat(),
                f"Status changed to: {status.value}"
            ))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error updating improvement status: {e}")
            return False
        finally:
            conn.close()
    
    def prompt_user_approval(self, improvement: Improvement) -> bool:
        """Prompt user for approval of an improvement"""
        print(f"\n🤖 Grok AI Suggestion:")
        print(f"📝 {improvement.title}")
        print(f"📄 {improvement.description}")
        print(f"🏷️  Category: {improvement.category.value}")
        print(f"⭐ Priority: {improvement.priority}/10")
        print(f"⏱️  Estimated Effort: {improvement.estimated_effort}")
        print(f"📊 Impact Score: {improvement.impact_score}/10")
        print(f"🔧 Complexity: {improvement.complexity}/10")
        
        if improvement.files_affected:
            print(f"📁 Files Affected: {', '.join(improvement.files_affected)}")
        
        if improvement.tags:
            print(f"🏷️  Tags: {', '.join(improvement.tags)}")
        
        while True:
            response = input(f"\n❓ Do you want to implement this improvement? (y/n/skip): ").lower().strip()
            if response in ['y', 'yes']:
                return True
            elif response in ['n', 'no']:
                return False
            elif response in ['s', 'skip']:
                return None
            else:
                print("Please enter 'y', 'n', or 's' for skip")
    
    def check_commit_ready(self) -> bool:
        """Check if it's time for a commit"""
        time_since_last_commit = datetime.now() - self.last_commit_time
        return (time_since_last_commit >= self.commit_interval or 
                self.improvements_since_commit >= self.target_improvements_per_commit)
    
    def get_master_checklist(self) -> Dict[str, List[Improvement]]:
        """Get master checklist organized by categories"""
        improvements = self.get_improvements()
        checklist = {}
        
        for category in ImprovementCategory:
            checklist[category.value] = [
                imp for imp in improvements 
                if imp.category == category and imp.status != ImprovementStatus.IMPLEMENTED
            ]
        
        return checklist
    
    def print_master_checklist(self):
        """Print the master checklist"""
        checklist = self.get_master_checklist()
        
        print("\n📋 MASTER IMPROVEMENT CHECKLIST")
        print("=" * 50)
        
        total_improvements = 0
        for category, improvements in checklist.items():
            if improvements:
                print(f"\n🏷️  {category.upper()} ({len(improvements)} items)")
                print("-" * 30)
                for imp in improvements:
                    status_emoji = {
                        ImprovementStatus.PENDING: "⏳",
                        ImprovementStatus.APPROVED: "✅",
                        ImprovementStatus.REJECTED: "❌",
                        ImprovementStatus.TESTING: "🧪",
                        ImprovementStatus.DEPLOYED: "🚀"
                    }.get(imp.status, "❓")
                    
                    print(f"  {status_emoji} {imp.title} (Priority: {imp.priority})")
                    total_improvements += 1
        
        print(f"\n📊 Total Pending Improvements: {total_improvements}")
        
        # Show commit status
        time_since_last_commit = datetime.now() - self.last_commit_time
        print(f"⏰ Time since last commit: {time_since_last_commit}")
        print(f"📈 Improvements since last commit: {self.improvements_since_commit}")
        print(f"🎯 Target improvements per commit: {self.target_improvements_per_commit}")
        
        if self.check_commit_ready():
            print("🚀 READY FOR COMMIT!")
        else:
            remaining_time = self.commit_interval - time_since_last_commit
            print(f"⏳ Next commit in: {remaining_time}")
    
    def create_milestone(self, title: str, description: str, target_date: datetime, 
                        improvement_ids: List[str]) -> str:
        """Create a new milestone"""
        milestone_id = f"milestone_{int(time.time())}"
        milestone = Milestone(
            id=milestone_id,
            title=title,
            description=description,
            target_date=target_date,
            improvements=improvement_ids,
            status="active",
            created_at=datetime.now()
        )
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO milestones VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                milestone.id,
                milestone.title,
                milestone.description,
                milestone.target_date.isoformat(),
                json.dumps(milestone.improvements),
                milestone.status,
                milestone.created_at.isoformat(),
                milestone.completed_at.isoformat() if milestone.completed_at else None
            ))
            
            conn.commit()
            return milestone_id
        except Exception as e:
            print(f"Error creating milestone: {e}")
            return None
        finally:
            conn.close()
    
    def get_statistics(self) -> Dict:
        """Get improvement statistics"""
        improvements = self.get_improvements()
        
        stats = {
            'total': len(improvements),
            'by_category': {},
            'by_status': {},
            'by_priority': {},
            'grok_suggested': len([i for i in improvements if i.grok_suggested]),
            'user_approved': len([i for i in improvements if i.user_approved]),
            'implemented': len([i for i in improvements if i.status == ImprovementStatus.IMPLEMENTED]),
            'pending': len([i for i in improvements if i.status == ImprovementStatus.PENDING])
        }
        
        for category in ImprovementCategory:
            stats['by_category'][category.value] = len([i for i in improvements if i.category == category])
        
        for status in ImprovementStatus:
            stats['by_status'][status.value] = len([i for i in improvements if i.status == status])
        
        for priority in range(1, 11):
            stats['by_priority'][priority] = len([i for i in improvements if i.priority == priority])
        
        return stats

# Global tracker instance
tracker = ImprovementTracker() 