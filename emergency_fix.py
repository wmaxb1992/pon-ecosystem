#!/usr/bin/env python3
"""
Emergency Fix for Failed Services
================================
This will fix all the color import and SSH issues
"""

import os
import subprocess

def create_safe_colors():
    """Create the missing safe_colors.py module"""
    safe_colors_content = '''# Safe Colors Module - Emergency Fix
class SafeColors:
    RED = '\\033[91m'
    GREEN = '\\033[92m'
    YELLOW = '\\033[93m'
    BLUE = '\\033[94m'
    PURPLE = '\\033[95m'
    CYAN = '\\033[96m'
    WHITE = '\\033[97m'
    RESET = '\\033[0m'
'''
    
    with open('safe_colors.py', 'w') as f:
        f.write(safe_colors_content)
    
    print("✅ Safe colors module created")

def update_requirements():
    """Add missing dependencies to requirements"""
    with open('requirements_render.txt', 'a') as f:
        f.write('\\nparamiko>=2.9.0\\nasyncio>=3.4.3\\nwebsockets>=10.0\\n')
    
    print("✅ Requirements updated")

if __name__ == "__main__":
    print("🚨 EXECUTING EMERGENCY FIXES...")
    create_safe_colors()
    update_requirements()
    print("✅ Emergency fixes complete!")
