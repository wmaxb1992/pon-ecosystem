#!/usr/bin/env python3
"""
Security Monitor for the Video Scraper API
Monitors IP access logs and provides security alerts
"""

import os
import time
import json
from datetime import datetime, timedelta
from collections import defaultdict, Counter
import requests

class SecurityMonitor:
    def __init__(self):
        self.ip_log_file = "ip_access_log.txt"
        self.request_log_file = "request_log.txt"
        self.suspicious_ips = set()
        self.ip_frequency = Counter()
        self.last_check = datetime.now()
        
    def get_current_ip(self):
        """Get current public IP address"""
        try:
            response = requests.get("https://api.ipify.org", timeout=5)
            return response.text.strip()
        except:
            return "unknown"
    
    def parse_ip_log_line(self, line):
        """Parse a line from the IP log file"""
        try:
            # Format: [timestamp] IP: x.x.x.x | Endpoint: /path | User-Agent: agent
            parts = line.strip().split(" | ")
            if len(parts) >= 2:
                timestamp_str = parts[0].split("]")[0].replace("[", "")
                ip_part = parts[0].split("IP: ")[1]
                endpoint_part = parts[1].split("Endpoint: ")[1]
                
                return {
                    "timestamp": timestamp_str,
                    "ip": ip_part,
                    "endpoint": endpoint_part,
                    "user_agent": parts[2].split("User-Agent: ")[1] if len(parts) > 2 else ""
                }
        except:
            pass
        return None
    
    def analyze_logs(self):
        """Analyze logs for security threats"""
        threats = []
        recent_ips = Counter()
        
        # Read IP logs
        if os.path.exists(self.ip_log_file):
            with open(self.ip_log_file, "r") as f:
                lines = f.readlines()
                
            for line in lines[-1000:]:  # Last 1000 entries
                log_entry = self.parse_ip_log_line(line)
                if log_entry:
                    recent_ips[log_entry["ip"]] += 1
                    
                    # Check for suspicious patterns
                    if recent_ips[log_entry["ip"]] > 50:  # Too many requests
                        threats.append({
                            "type": "High Frequency",
                            "ip": log_entry["ip"],
                            "count": recent_ips[log_entry["ip"]],
                            "severity": "HIGH"
                        })
                    
                    # Check for suspicious endpoints
                    suspicious_endpoints = ["/admin", "/config", "/.env", "/wp-admin"]
                    if any(endpoint in log_entry["endpoint"] for endpoint in suspicious_endpoints):
                        threats.append({
                            "type": "Suspicious Endpoint",
                            "ip": log_entry["ip"],
                            "endpoint": log_entry["endpoint"],
                            "severity": "MEDIUM"
                        })
        
        return threats, recent_ips
    
    def display_dashboard(self):
        """Display security dashboard"""
        os.system('clear' if os.name == 'posix' else 'cls')
        
        print("🔒 SECURITY MONITOR DASHBOARD")
        print("=" * 50)
        print(f"📅 Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"🌐 Current IP: {self.get_current_ip()}")
        print()
        
        # Analyze logs
        threats, recent_ips = self.analyze_logs()
        
        # Display recent activity
        print("📊 RECENT ACTIVITY (Last 1000 requests)")
        print("-" * 30)
        if recent_ips:
            for ip, count in recent_ips.most_common(10):
                print(f"  {ip}: {count} requests")
        else:
            print("  No recent activity")
        print()
        
        # Display threats
        print("🚨 SECURITY THREATS")
        print("-" * 20)
        if threats:
            for threat in threats:
                severity_color = "🔴" if threat["severity"] == "HIGH" else "🟡"
                print(f"  {severity_color} {threat['type']}: {threat['ip']}")
                if "count" in threat:
                    print(f"     Count: {threat['count']}")
                if "endpoint" in threat:
                    print(f"     Endpoint: {threat['endpoint']}")
                print()
        else:
            print("  ✅ No threats detected")
        print()
        
        # Display log file status
        print("📁 LOG FILES")
        print("-" * 15)
        if os.path.exists(self.ip_log_file):
            size = os.path.getsize(self.ip_log_file)
            print(f"  IP Log: {size} bytes")
        else:
            print("  IP Log: Not found")
            
        if os.path.exists(self.request_log_file):
            size = os.path.getsize(self.request_log_file)
            print(f"  Request Log: {size} bytes")
        else:
            print("  Request Log: Not found")
        print()
        
        print("Press Ctrl+C to exit")
        print("=" * 50)
    
    def monitor_continuously(self, interval=5):
        """Monitor continuously with specified interval"""
        print("🔒 Starting Security Monitor...")
        print("Monitoring IP access logs for security threats")
        print(f"Update interval: {interval} seconds")
        print()
        
        try:
            while True:
                self.display_dashboard()
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\n🔌 Security Monitor stopped")

def main():
    monitor = SecurityMonitor()
    
    if len(sys.argv) > 1 and sys.argv[1] == "--once":
        monitor.display_dashboard()
    else:
        interval = int(sys.argv[1]) if len(sys.argv) > 1 else 5
        monitor.monitor_continuously(interval)

if __name__ == "__main__":
    import sys
    main() 