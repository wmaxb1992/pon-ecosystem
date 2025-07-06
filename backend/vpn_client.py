#!/usr/bin/env python3
"""
VPN Client for connecting to the python-vpn server
This provides an additional layer of security on top of proxies
"""

import subprocess
import sys
import time
import socket
import requests

def get_current_ip():
    """Get current public IP address"""
    try:
        response = requests.get("https://api.ipify.org", timeout=5)
        return response.text.strip()
    except:
        return "unknown"

def connect_vpn(server_ip: str, password: str, port: int = 5000):
    """Connect to VPN server using pvpn client"""
    print(f"🔒 Connecting to VPN server at {server_ip}:{port}")
    print(f"🌐 Current IP: {get_current_ip()}")
    
    try:
        # Connect to VPN server
        cmd = ["pvpn", "-c", f"{server_ip}:{port}", "-p", password]
        
        print("Starting VPN connection...")
        print("Press Ctrl+C to disconnect")
        
        # Start VPN client
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        
        # Wait a moment for connection
        time.sleep(3)
        
        if process.poll() is None:
            print("✅ VPN connection established")
            print(f"🌐 New IP: {get_current_ip()}")
            
            try:
                # Keep connection alive
                while True:
                    time.sleep(1)
                    if process.poll() is not None:
                        break
            except KeyboardInterrupt:
                print("\n🔌 Disconnecting from VPN...")
                process.terminate()
                process.wait()
                print("✅ VPN disconnected")
        else:
            print("❌ Failed to connect to VPN")
            stdout, stderr = process.communicate()
            print(f"Error: {stderr.decode()}")
            
    except Exception as e:
        print(f"❌ Error connecting to VPN: {e}")

def main():
    if len(sys.argv) < 3:
        print("Usage: python vpn_client.py <server_ip> <password> [port]")
        print("Example: python vpn_client.py 192.168.1.100 secure_vpn_password_2024 5000")
        sys.exit(1)
    
    server_ip = sys.argv[1]
    password = sys.argv[2]
    port = int(sys.argv[3]) if len(sys.argv) > 3 else 5000
    
    connect_vpn(server_ip, password, port)

if __name__ == "__main__":
    main() 