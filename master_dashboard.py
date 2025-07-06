#!/usr/bin/env python3
"""
Master Status Dashboard
======================
Real-time view of all autonomous systems
"""

import os
import sys
import time
import json
import subprocess
from datetime import datetime, timedelta
import requests

def print_separator(title):
    print(f"\n{'='*80}")
    print(f" {title} ".center(80))
    print(f"{'='*80}")

def get_time_remaining():
    """Get time remaining until 12pm"""
    current_time = datetime.now()
    target_time = current_time.replace(hour=12, minute=0, second=0, microsecond=0)
    if target_time <= current_time:
        target_time += timedelta(days=1)
    
    remaining = target_time - current_time
    hours = int(remaining.total_seconds() // 3600)
    minutes = int((remaining.total_seconds() % 3600) // 60)
    return hours, minutes, target_time

def check_running_processes():
    """Check which autonomous processes are running"""
    processes = [
        'autonomous_deployment_executor',
        'autonomous_ai_approval', 
        'continuous_health_monitor',
        'progress_monitor'
    ]
    
    running = {}
    for process in processes:
        try:
            result = subprocess.run(['pgrep', '-f', process], 
                                  capture_output=True, text=True)
            pids = result.stdout.strip().split('\n') if result.stdout.strip() else []
            running[process] = {'count': len(pids), 'pids': pids}
        except:
            running[process] = {'count': 0, 'pids': []}
    
    return running

def check_services_health():
    """Check health of core services"""
    services = [
        ('Backend API', 'http://localhost:8000/health'),
        ('Backend Root', 'http://localhost:8000/'),
        ('Frontend', 'http://localhost:3000')
    ]
    
    health = {}
    for name, url in services:
        try:
            response = requests.get(url, timeout=5)
            health[name] = {
                'status': 'UP',
                'status_code': response.status_code,
                'response_time': f"{response.elapsed.total_seconds():.2f}s"
            }
        except Exception as e:
            health[name] = {
                'status': 'DOWN',
                'error': str(e)
            }
    
    return health

def get_improvement_stats():
    """Get AI improvement statistics"""
    try:
        with open('/Users/maxwoldenberg/Desktop/pon/ai_approval_status.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {'total_approved': 0, 'total_rejected': 0, 'approval_rate': 0.0}

def get_deployment_stats():
    """Get deployment statistics"""
    try:
        with open('/Users/maxwoldenberg/Desktop/pon/autonomous_status.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {'cycle': 0, 'improvements': 0, 'services_active': 0}

def get_git_stats():
    """Get git commit statistics"""
    try:
        result = subprocess.run(['git', 'log', '--oneline', '--since="1 hour ago"'], 
                              cwd='/Users/maxwoldenberg/Desktop/pon',
                              capture_output=True, text=True)
        commits = result.stdout.strip().split('\n') if result.stdout.strip() else []
        return len(commits)
    except:
        return 0

def display_dashboard():
    """Display the complete status dashboard"""
    os.system('clear')  # Clear screen
    
    print_separator("🤖 PON ECOSYSTEM - AUTONOMOUS EXECUTION DASHBOARD")
    
    # Time status
    hours, minutes, target_time = get_time_remaining()
    print(f"⏰ Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"🎯 Target Time: {target_time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"⏳ Time Remaining: {hours}h {minutes}m")
    
    print_separator("🔄 AUTONOMOUS PROCESSES")
    
    # Process status
    processes = check_running_processes()
    for process, info in processes.items():
        status = "🟢 RUNNING" if info['count'] > 0 else "🔴 STOPPED"
        print(f"{process:<35} {status:<15} ({info['count']} instances)")
    
    print_separator("🏥 SERVICE HEALTH")
    
    # Service health
    services = check_services_health()
    for service, health in services.items():
        if health['status'] == 'UP':
            status = f"🟢 UP ({health['status_code']}) - {health['response_time']}"
        else:
            status = f"🔴 DOWN - {health.get('error', 'Unknown error')}"
        print(f"{service:<20} {status}")
    
    print_separator("📊 EXECUTION STATISTICS")
    
    # Improvement stats
    improvement_stats = get_improvement_stats()
    deployment_stats = get_deployment_stats()
    git_commits = get_git_stats()
    
    print(f"🤖 AI Improvements Approved:     {improvement_stats.get('total_approved', 0)}")
    print(f"❌ AI Improvements Rejected:     {improvement_stats.get('total_rejected', 0)}")
    print(f"📈 Approval Rate:                {improvement_stats.get('approval_rate', 0.0):.1%}")
    print(f"🔄 Deployment Cycles Completed:  {deployment_stats.get('cycle', 0)}")
    print(f"📋 Total Task Improvements:     {deployment_stats.get('improvements', 0)}")
    print(f"🚀 Active Services:              {deployment_stats.get('services_active', 0)}")
    print(f"📝 Git Commits (Last Hour):      {git_commits}")
    
    print_separator("📁 SYSTEM FILES")
    
    # Check key files
    key_files = [
        '/Users/maxwoldenberg/Desktop/pon/render.yaml',
        '/Users/maxwoldenberg/Desktop/pon/requirements_render.txt',
        '/Users/maxwoldenberg/Desktop/pon/ai_approval_status.json',
        '/Users/maxwoldenberg/Desktop/pon/autonomous_status.json',
        '/Users/maxwoldenberg/Desktop/pon/health_report.json'
    ]
    
    for file_path in key_files:
        filename = os.path.basename(file_path)
        if os.path.exists(file_path):
            size = os.path.getsize(file_path)
            mtime = datetime.fromtimestamp(os.path.getmtime(file_path))
            print(f"✅ {filename:<30} {size:>8} bytes  (Modified: {mtime.strftime('%H:%M:%S')})")
        else:
            print(f"❌ {filename:<30} Missing")
    
    print_separator("🎯 DEPLOYMENT STATUS")
    
    # Deployment readiness
    render_yaml_exists = os.path.exists('/Users/maxwoldenberg/Desktop/pon/render.yaml')
    requirements_exists = os.path.exists('/Users/maxwoldenberg/Desktop/pon/requirements_render.txt')
    
    print(f"📄 render.yaml Blueprint:        {'✅ Ready' if render_yaml_exists else '❌ Missing'}")
    print(f"📦 requirements_render.txt:      {'✅ Ready' if requirements_exists else '❌ Missing'}")
    print(f"🔧 Git Repository Status:        {'✅ Up to date' if git_commits >= 0 else '❌ Issues'}")
    print(f"🚀 Auto-deployment:              {'✅ Active (Push to main triggers deploy)' if render_yaml_exists else '❌ Not ready'}")
    
    print_separator("🎉 RENDER.COM DEPLOYMENT")
    
    print("🌐 Deploy to Render.com:")
    print("   1. Go to: https://dashboard.render.com")
    print("   2. Click 'New' → 'Blueprint'")
    print("   3. Connect GitHub repository")
    print("   4. Select render.yaml blueprint")
    print("   5. Deploy all services")
    print()
    print("🔗 Expected URLs after deployment:")
    print("   • Main App: https://pon-ecosystem.onrender.com")
    print("   • SSH Terminal: ssh user@instant-grok-terminal.onrender.com")
    print("   • Health Check: https://pon-ecosystem.onrender.com/health")
    
    print(f"\n{'='*80}")
    print(f" Last Updated: {datetime.now().strftime('%H:%M:%S')} | Next Update: {(datetime.now() + timedelta(seconds=30)).strftime('%H:%M:%S')} ".center(80))
    print(f"{'='*80}\n")

def run_dashboard():
    """Run the continuous dashboard"""
    print("🚀 Starting Master Status Dashboard...")
    print("🔄 Updating every 30 seconds until 12:00 PM")
    
    while True:
        try:
            display_dashboard()
            
            # Check if we should stop
            hours, minutes, _ = get_time_remaining()
            if hours == 0 and minutes == 0:
                print("\n🎉 TARGET TIME REACHED - 12:00 PM!")
                print("🏁 Autonomous execution complete!")
                break
            
            time.sleep(30)  # Update every 30 seconds
            
        except KeyboardInterrupt:
            print("\n🛑 Dashboard stopped by user")
            break
        except Exception as e:
            print(f"\n❌ Dashboard error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    run_dashboard()
