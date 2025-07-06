#!/usr/bin/env python3
"""
Continuous Health Monitor
========================
Monitors all systems and auto-heals issues
"""

import os
import sys
import time
import json
import logging
import subprocess
import requests
import psutil
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s] %(levelname)s %(message)s',
    handlers=[
        logging.FileHandler('/Users/maxwoldenberg/Desktop/pon/logs/health_monitor.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class ContinuousHealthMonitor:
    def __init__(self):
        self.health_history = []
        self.alert_count = 0
        self.auto_fix_count = 0
        
    def check_service_health(self, service_name, url, expected_status=200):
        """Check if a service is healthy"""
        try:
            response = requests.get(url, timeout=10)
            healthy = response.status_code == expected_status
            response_time = response.elapsed.total_seconds()
            
            return {
                'service': service_name,
                'healthy': healthy,
                'status_code': response.status_code,
                'response_time': response_time,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'service': service_name,
                'healthy': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def check_system_resources(self):
        """Check system resource usage"""
        try:
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            return {
                'cpu_percent': cpu_percent,
                'memory_percent': memory.percent,
                'memory_available_gb': memory.available / (1024**3),
                'disk_percent': disk.percent,
                'disk_free_gb': disk.free / (1024**3),
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Resource check error: {e}")
            return None
    
    def check_process_health(self, process_name):
        """Check if a process is running"""
        try:
            result = subprocess.run(['pgrep', '-f', process_name], 
                                  capture_output=True, text=True)
            pids = result.stdout.strip().split('\n') if result.stdout.strip() else []
            
            return {
                'process': process_name,
                'running': len(pids) > 0,
                'pid_count': len(pids),
                'pids': pids,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            return {
                'process': process_name,
                'running': False,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def auto_heal_service(self, service_issue):
        """Attempt to auto-heal a service issue"""
        service_name = service_issue['service']
        
        logger.info(f"🔧 Attempting auto-heal for: {service_name}")
        
        # Service-specific healing logic
        if 'backend' in service_name.lower():
            return self.restart_backend_service()
        elif 'frontend' in service_name.lower():
            return self.restart_frontend_service()
        elif 'autonomous' in service_name.lower():
            return self.restart_autonomous_executor()
        else:
            logger.warning(f"⚠️ No auto-heal strategy for: {service_name}")
            return False
    
    def restart_backend_service(self):
        """Restart backend service"""
        try:
            logger.info("🔄 Restarting backend service...")
            
            # Kill existing backend processes
            subprocess.run(['pkill', '-f', 'main_enhanced.py'], 
                         capture_output=True)
            time.sleep(2)
            
            # Start new backend process
            process = subprocess.Popen([
                'python3', 'backend/main_enhanced.py'
            ], cwd='/Users/maxwoldenberg/Desktop/pon')
            
            logger.info(f"✅ Backend restarted with PID: {process.pid}")
            self.auto_fix_count += 1
            return True
            
        except Exception as e:
            logger.error(f"❌ Backend restart failed: {e}")
            return False
    
    def restart_frontend_service(self):
        """Restart frontend service"""
        try:
            logger.info("🔄 Restarting frontend service...")
            
            # Kill existing frontend processes
            subprocess.run(['pkill', '-f', 'next'], capture_output=True)
            time.sleep(2)
            
            # Start new frontend process
            process = subprocess.Popen([
                'npm', 'run', 'dev'
            ], cwd='/Users/maxwoldenberg/Desktop/pon/frontend')
            
            logger.info(f"✅ Frontend restarted with PID: {process.pid}")
            self.auto_fix_count += 1
            return True
            
        except Exception as e:
            logger.error(f"❌ Frontend restart failed: {e}")
            return False
    
    def restart_autonomous_executor(self):
        """Restart autonomous executor if it stops"""
        try:
            logger.info("🔄 Restarting autonomous executor...")
            
            # Check if it's actually stopped
            result = subprocess.run(['pgrep', '-f', 'autonomous_deployment_executor'], 
                                  capture_output=True, text=True)
            
            if not result.stdout.strip():
                # Start new executor
                process = subprocess.Popen([
                    'python3', 'autonomous_deployment_executor.py'
                ], cwd='/Users/maxwoldenberg/Desktop/pon')
                
                logger.info(f"✅ Autonomous executor restarted with PID: {process.pid}")
                self.auto_fix_count += 1
                return True
            else:
                logger.info("✅ Autonomous executor is already running")
                return True
                
        except Exception as e:
            logger.error(f"❌ Autonomous executor restart failed: {e}")
            return False
    
    def generate_health_report(self, health_data):
        """Generate comprehensive health report"""
        report = {
            'timestamp': datetime.now().isoformat(),
            'overall_health': 'unknown',
            'services': health_data.get('services', []),
            'resources': health_data.get('resources', {}),
            'processes': health_data.get('processes', []),
            'alerts': [],
            'auto_fixes_applied': self.auto_fix_count
        }
        
        # Calculate overall health score
        healthy_services = sum(1 for svc in report['services'] if svc.get('healthy', False))
        total_services = len(report['services'])
        service_health = healthy_services / max(1, total_services)
        
        # Resource health
        resources = report['resources']
        resource_health = 1.0
        if resources.get('cpu_percent', 0) > 80:
            resource_health -= 0.3
            report['alerts'].append("High CPU usage")
        if resources.get('memory_percent', 0) > 80:
            resource_health -= 0.3
            report['alerts'].append("High memory usage")
        if resources.get('disk_percent', 0) > 90:
            resource_health -= 0.2
            report['alerts'].append("Low disk space")
        
        # Overall health calculation
        overall_score = (service_health * 0.6) + (resource_health * 0.4)
        
        if overall_score >= 0.9:
            report['overall_health'] = 'excellent'
        elif overall_score >= 0.7:
            report['overall_health'] = 'good'
        elif overall_score >= 0.5:
            report['overall_health'] = 'fair'
        else:
            report['overall_health'] = 'poor'
        
        report['health_score'] = overall_score
        
        return report
    
    def save_health_report(self, report):
        """Save health report to file"""
        try:
            # Save latest report
            with open('/Users/maxwoldenberg/Desktop/pon/health_report.json', 'w') as f:
                json.dump(report, f, indent=2)
            
            # Append to history
            self.health_history.append(report)
            
            # Keep only last 100 reports
            if len(self.health_history) > 100:
                self.health_history = self.health_history[-100:]
            
            # Save history
            with open('/Users/maxwoldenberg/Desktop/pon/health_history.json', 'w') as f:
                json.dump(self.health_history, f, indent=2)
                
        except Exception as e:
            logger.error(f"Health report save error: {e}")
    
    def run_continuous_monitoring(self):
        """Run continuous health monitoring"""
        logger.info("🏥 Starting continuous health monitoring...")
        
        cycle = 0
        
        while True:
            try:
                cycle += 1
                logger.info(f"🔍 Health Check Cycle #{cycle}")
                
                # Check all services
                services_health = [
                    self.check_service_health('Backend API', 'http://localhost:8000/health'),
                    self.check_service_health('Frontend', 'http://localhost:3000'),
                    self.check_service_health('Backend Root', 'http://localhost:8000/')
                ]
                
                # Check system resources
                resources_health = self.check_system_resources()
                
                # Check critical processes
                processes_health = [
                    self.check_process_health('autonomous_deployment_executor'),
                    self.check_process_health('autonomous_ai_approval'),
                    self.check_process_health('main_enhanced.py'),
                    self.check_process_health('next')
                ]
                
                # Compile health data
                health_data = {
                    'services': services_health,
                    'resources': resources_health,
                    'processes': processes_health
                }
                
                # Generate report
                report = self.generate_health_report(health_data)
                
                # Log health status
                logger.info(f"🏥 Overall Health: {report['overall_health'].upper()} ({report['health_score']:.2f})")
                
                if report['alerts']:
                    logger.warning(f"⚠️ Alerts: {', '.join(report['alerts'])}")
                
                # Auto-heal if needed
                for service in services_health:
                    if not service.get('healthy', False):
                        logger.warning(f"❌ Unhealthy service: {service['service']}")
                        if self.auto_heal_service(service):
                            logger.info(f"✅ Auto-heal successful for: {service['service']}")
                        else:
                            logger.error(f"❌ Auto-heal failed for: {service['service']}")
                            self.alert_count += 1
                
                # Save report
                self.save_health_report(report)
                
                # Log summary
                healthy_services = sum(1 for svc in services_health if svc.get('healthy', False))
                running_processes = sum(1 for proc in processes_health if proc.get('running', False))
                
                logger.info(f"📊 Services: {healthy_services}/{len(services_health)} healthy")
                logger.info(f"📊 Processes: {running_processes}/{len(processes_health)} running")
                logger.info(f"📊 Auto-fixes applied: {self.auto_fix_count}")
                
                # Wait before next check
                logger.info("⏳ Waiting 1 minute before next health check...")
                time.sleep(60)  # Check every minute
                
            except KeyboardInterrupt:
                logger.info("🛑 Health monitoring stopped")
                break
            except Exception as e:
                logger.error(f"❌ Health check error: {e}")
                time.sleep(30)

if __name__ == "__main__":
    monitor = ContinuousHealthMonitor()
    monitor.run_continuous_monitoring()
