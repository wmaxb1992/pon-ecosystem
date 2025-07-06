import os
import time
import json
import subprocess
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import threading
import schedule

from improvement_tracker import ImprovementTracker, Improvement, ImprovementCategory, ImprovementStatus
from codebase_analyzer import CodebaseAnalyzer
from grok_client import GrokClient
from ai_improvement_system import AIImprovementSystem

class ContinuousImprovementEngine:
    def __init__(self):
        self.tracker = ImprovementTracker()
        self.analyzer = CodebaseAnalyzer()
        self.grok_client = GrokClient()
        self.ai_system = AIImprovementSystem()
        
        self.is_running = False
        self.improvement_thread = None
        self.last_analysis = None
        self.analysis_interval = timedelta(minutes=30)
        
        # Improvement categories with weights for prioritization
        self.category_weights = {
            ImprovementCategory.SECURITY: 10,
            ImprovementCategory.PERFORMANCE: 9,
            ImprovementCategory.UI_UX: 8,
            ImprovementCategory.FEATURES: 7,
            ImprovementCategory.CODE_QUALITY: 6,
            ImprovementCategory.DATABASE: 5,
            ImprovementCategory.API: 4,
            ImprovementCategory.FRONTEND: 3,
            ImprovementCategory.BACKEND: 2,
            ImprovementCategory.DOCUMENTATION: 1
        }
    
    def start(self):
        """Start the continuous improvement engine"""
        print("🚀 Starting Continuous Improvement Engine...")
        self.is_running = True
        
        # Start improvement thread
        self.improvement_thread = threading.Thread(target=self.improvement_loop)
        self.improvement_thread.daemon = True
        self.improvement_thread.start()
        
        # Schedule regular tasks
        schedule.every(15).minutes.do(self.check_commit_ready)
        schedule.every(30).minutes.do(self.analyze_codebase)
        schedule.every(1).hours.do(self.generate_milestone)
        
        print("✅ Continuous Improvement Engine started!")
        print("📊 Monitoring for improvements every 15 minutes")
        print("🔍 Codebase analysis every 30 minutes")
        print("🎯 Milestone generation every hour")
    
    def stop(self):
        """Stop the continuous improvement engine"""
        print("🛑 Stopping Continuous Improvement Engine...")
        self.is_running = False
        if self.improvement_thread:
            self.improvement_thread.join()
        print("✅ Continuous Improvement Engine stopped!")
    
    def improvement_loop(self):
        """Main improvement loop"""
        while self.is_running:
            try:
                # Generate AI suggestions
                suggestions = self.generate_ai_suggestions()
                
                # Process each suggestion
                for suggestion in suggestions:
                    if not self.is_running:
                        break
                    
                    # Prompt user for approval
                    approval = self.tracker.prompt_user_approval(suggestion)
                    
                    if approval is True:
                        # User approved - implement improvement
                        self.implement_improvement(suggestion)
                    elif approval is False:
                        # User rejected - mark as rejected
                        self.tracker.update_improvement_status(suggestion.id, ImprovementStatus.REJECTED)
                    # If None, user skipped - do nothing
                
                # Check if ready for commit
                if self.tracker.check_commit_ready():
                    self.prepare_commit()
                
                # Wait before next iteration
                time.sleep(60)  # Check every minute
                
            except Exception as e:
                print(f"❌ Error in improvement loop: {e}")
                time.sleep(300)  # Wait 5 minutes on error
    
    def generate_ai_suggestions(self) -> List[Improvement]:
        """Generate AI-powered improvement suggestions"""
        suggestions = []
        
        try:
            # Get codebase context
            codebase_report = self.analyzer.generate_codebase_report()
            key_files = self.analyzer.get_files_for_grok()
            
            # Create context for Grok
            context = {
                "codebase_report": codebase_report,
                "key_files": key_files,
                "current_improvements": self.tracker.get_improvements(),
                "statistics": self.tracker.get_statistics()
            }
            
            # Get suggestions from Grok
            grok_suggestions = self.grok_client.get_improvement_suggestions(context)
            
            # Convert to Improvement objects
            for i, suggestion_data in enumerate(grok_suggestions):
                improvement = Improvement(
                    id=f"grok_suggestion_{int(time.time())}_{i}",
                    title=suggestion_data.get('title', 'AI Suggested Improvement'),
                    description=suggestion_data.get('description', ''),
                    category=ImprovementCategory(suggestion_data.get('category', 'FEATURES')),
                    priority=suggestion_data.get('priority', 5),
                    estimated_effort=suggestion_data.get('estimated_effort', '30min'),
                    status=ImprovementStatus.PENDING,
                    created_at=datetime.now(),
                    grok_suggested=True,
                    impact_score=suggestion_data.get('impact_score', 5),
                    complexity=suggestion_data.get('complexity', 5),
                    tags=suggestion_data.get('tags', []),
                    files_affected=suggestion_data.get('files_affected', []),
                    dependencies=suggestion_data.get('dependencies', [])
                )
                
                # Add to tracker
                if self.tracker.add_improvement(improvement):
                    suggestions.append(improvement)
            
            print(f"🤖 Generated {len(suggestions)} AI suggestions")
            
        except Exception as e:
            print(f"❌ Error generating AI suggestions: {e}")
        
        return suggestions
    
    def implement_improvement(self, improvement: Improvement):
        """Implement an approved improvement"""
        print(f"🔧 Implementing: {improvement.title}")
        
        try:
            # Update status to approved
            self.tracker.update_improvement_status(improvement.id, ImprovementStatus.APPROVED)
            
            # Use AI system to implement
            success = self.ai_system.implement_improvement(improvement)
            
            if success:
                # Update status to implemented
                self.tracker.update_improvement_status(improvement.id, ImprovementStatus.IMPLEMENTED)
                improvement.implemented_at = datetime.now()
                improvement.user_approved = True
                
                # Increment improvements since last commit
                self.tracker.improvements_since_commit += 1
                
                print(f"✅ Successfully implemented: {improvement.title}")
            else:
                print(f"❌ Failed to implement: {improvement.title}")
                
        except Exception as e:
            print(f"❌ Error implementing improvement: {e}")
    
    def prepare_commit(self):
        """Prepare and execute a commit with improvements"""
        print("🚀 Preparing commit with improvements...")
        
        try:
            # Get implemented improvements since last commit
            implemented = self.tracker.get_improvements(status=ImprovementStatus.IMPLEMENTED)
            
            if not implemented:
                print("No improvements to commit")
                return
            
            # Create commit message
            commit_message = self.create_commit_message(implemented)
            
            # Stage changes
            subprocess.run(['git', 'add', '.'], check=True)
            
            # Commit
            subprocess.run(['git', 'commit', '-m', commit_message], check=True)
            
            # Push to main branch
            subprocess.run(['git', 'push', 'origin', 'main'], check=True)
            
            # Update tracker
            self.tracker.last_commit_time = datetime.now()
            self.tracker.improvements_since_commit = 0
            
            print(f"✅ Committed {len(implemented)} improvements to main branch")
            print(f"📝 Commit message: {commit_message}")
            
        except Exception as e:
            print(f"❌ Error preparing commit: {e}")
    
    def create_commit_message(self, improvements: List[Improvement]) -> str:
        """Create a commit message for improvements"""
        lines = []
        lines.append("🚀 Continuous Improvement Commit")
        lines.append("")
        lines.append(f"Implements {len(improvements)} improvements:")
        lines.append("")
        
        # Group by category
        by_category = {}
        for imp in improvements:
            cat = imp.category.value
            if cat not in by_category:
                by_category[cat] = []
            by_category[cat].append(imp)
        
        for category, imps in by_category.items():
            lines.append(f"## {category}")
            for imp in imps:
                lines.append(f"- {imp.title}")
            lines.append("")
        
        lines.append("Generated by Continuous Improvement Engine with Grok AI")
        
        return "\n".join(lines)
    
    def analyze_codebase(self):
        """Analyze codebase and identify improvement opportunities"""
        print("🔍 Analyzing codebase...")
        
        try:
            # Generate analysis report
            report = self.analyzer.generate_codebase_report()
            
            # Save report
            with open('codebase_analysis.json', 'w') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'report': report
                }, f, indent=2)
            
            # Generate improvement opportunities
            structure = self.analyzer.scan_codebase()
            
            for opportunity in structure.improvement_opportunities:
                improvement = Improvement(
                    id=f"analysis_{int(time.time())}",
                    title=f"Codebase Analysis: {opportunity}",
                    description=opportunity,
                    category=ImprovementCategory.CODE_QUALITY,
                    priority=6,
                    estimated_effort="1hour",
                    status=ImprovementStatus.PENDING,
                    created_at=datetime.now(),
                    grok_suggested=False
                )
                
                self.tracker.add_improvement(improvement)
            
            self.last_analysis = datetime.now()
            print(f"✅ Codebase analysis complete - found {len(structure.improvement_opportunities)} opportunities")
            
        except Exception as e:
            print(f"❌ Error analyzing codebase: {e}")
    
    def generate_milestone(self):
        """Generate a new milestone based on current improvements"""
        print("🎯 Generating milestone...")
        
        try:
            # Get pending improvements
            pending = self.tracker.get_improvements(status=ImprovementStatus.PENDING)
            
            if len(pending) < 5:
                print("Not enough pending improvements for milestone")
                return
            
            # Group by category
            by_category = {}
            for imp in pending:
                cat = imp.category.value
                if cat not in by_category:
                    by_category[cat] = []
                by_category[cat].append(imp)
            
            # Find category with most improvements
            target_category = max(by_category.items(), key=lambda x: len(x[1]))[0]
            target_improvements = by_category[target_category][:5]  # Top 5
            
            # Create milestone
            milestone_title = f"Improve {target_category} - {len(target_improvements)} enhancements"
            milestone_desc = f"Focus on {target_category} improvements including: " + \
                           ", ".join([imp.title for imp in target_improvements])
            
            target_date = datetime.now() + timedelta(days=7)
            
            milestone_id = self.tracker.create_milestone(
                title=milestone_title,
                description=milestone_desc,
                target_date=target_date,
                improvement_ids=[imp.id for imp in target_improvements]
            )
            
            if milestone_id:
                print(f"✅ Created milestone: {milestone_title}")
                print(f"📅 Target date: {target_date.strftime('%Y-%m-%d')}")
            
        except Exception as e:
            print(f"❌ Error generating milestone: {e}")
    
    def check_commit_ready(self):
        """Check if ready for commit and prompt user"""
        if self.tracker.check_commit_ready():
            print("\n🚀 READY FOR COMMIT!")
            print(f"📈 {self.tracker.improvements_since_commit} improvements ready")
            
            response = input("Do you want to commit now? (y/n): ").lower().strip()
            if response in ['y', 'yes']:
                self.prepare_commit()
    
    def show_status(self):
        """Show current status of the improvement engine"""
        print("\n📊 CONTINUOUS IMPROVEMENT ENGINE STATUS")
        print("=" * 50)
        
        # Show tracker status
        self.tracker.print_master_checklist()
        
        # Show statistics
        stats = self.tracker.get_statistics()
        print(f"\n📈 STATISTICS:")
        print(f"  Total Improvements: {stats['total']}")
        print(f"  Grok Suggested: {stats['grok_suggested']}")
        print(f"  User Approved: {stats['user_approved']}")
        print(f"  Implemented: {stats['implemented']}")
        print(f"  Pending: {stats['pending']}")
        
        # Show engine status
        print(f"\n⚙️  ENGINE STATUS:")
        print(f"  Running: {self.is_running}")
        print(f"  Last Analysis: {self.last_analysis or 'Never'}")
        print(f"  Improvements Since Commit: {self.tracker.improvements_since_commit}")
        print(f"  Time Since Last Commit: {datetime.now() - self.tracker.last_commit_time}")
        
        # Show next scheduled tasks
        print(f"\n⏰ NEXT SCHEDULED TASKS:")
        print(f"  Codebase Analysis: {self.last_analysis + self.analysis_interval if self.last_analysis else 'Pending'}")
        print(f"  Milestone Generation: {datetime.now() + timedelta(hours=1)}")
    
    def run_interactive(self):
        """Run the engine in interactive mode"""
        print("🎮 Interactive Mode - Continuous Improvement Engine")
        print("Commands: start, stop, status, commit, analyze, milestone, quit")
        
        while True:
            try:
                command = input("\n> ").lower().strip()
                
                if command == 'start':
                    self.start()
                elif command == 'stop':
                    self.stop()
                elif command == 'status':
                    self.show_status()
                elif command == 'commit':
                    self.prepare_commit()
                elif command == 'analyze':
                    self.analyze_codebase()
                elif command == 'milestone':
                    self.generate_milestone()
                elif command == 'quit':
                    self.stop()
                    break
                else:
                    print("Unknown command. Available: start, stop, status, commit, analyze, milestone, quit")
                    
            except KeyboardInterrupt:
                print("\n🛑 Interrupted by user")
                self.stop()
                break
            except Exception as e:
                print(f"❌ Error: {e}")

# Global engine instance
engine = ContinuousImprovementEngine()

if __name__ == "__main__":
    engine.run_interactive() 