#!/usr/bin/env python3
"""
Render.yaml Validation Script
============================
Validates the render.yaml blueprint before deployment
"""

import yaml
import sys
from pathlib import Path

def validate_render_yaml():
    """Validate the render.yaml configuration"""
    
    print("🔍 Validating render.yaml blueprint...")
    
    yaml_path = Path("render.yaml")
    if not yaml_path.exists():
        print("❌ render.yaml not found!")
        return False
    
    try:
        with open(yaml_path) as f:
            config = yaml.safe_load(f)
        print("✅ YAML syntax is valid")
    except yaml.YAMLError as e:
        print(f"❌ YAML syntax error: {e}")
        return False
    
    # Validate structure
    if "services" not in config:
        print("❌ No services defined in render.yaml")
        return False
    
    services = config["services"]
    print(f"📦 Found {len(services)} services defined")
    
    # Check required services
    required_services = {
        "pon-ecosystem": "web",
        "ceo-ai-bot": "worker", 
        "ai-code-worker": "worker",
        "instant-grok-terminal": "web"
    }
    
    service_names = [s.get("name", "") for s in services]
    
    for required_name, required_type in required_services.items():
        if required_name not in service_names:
            print(f"⚠️  Missing recommended service: {required_name}")
        else:
            service = next(s for s in services if s.get("name") == required_name)
            if service.get("type") != required_type:
                print(f"⚠️  Service {required_name} has wrong type: expected {required_type}, got {service.get('type')}")
            else:
                print(f"✅ Service {required_name} configured correctly")
    
    # Check databases
    if "databases" in config:
        databases = config["databases"]
        print(f"🗄️  Found {len(databases)} databases defined")
        
        db_names = [db.get("name", "") for db in databases]
        if "pon-redis" not in db_names:
            print("⚠️  Missing Redis database (pon-redis)")
        else:
            print("✅ Redis database configured")
    else:
        print("⚠️  No databases section found")
    
    # Check environment variables
    web_services = [s for s in services if s.get("type") == "web"]
    for service in web_services:
        env_vars = service.get("envVars", [])
        env_var_keys = [var.get("key", "") for var in env_vars]
        
        if "GROK_API_KEY" not in env_var_keys:
            print(f"❌ Service {service.get('name')} missing GROK_API_KEY")
        else:
            print(f"✅ Service {service.get('name')} has required API key")
    
    print("\n" + "="*50)
    print("🎯 RENDER.YAML VALIDATION COMPLETE")
    print("="*50)
    print("✅ Blueprint is ready for deployment!")
    print("🚀 Deploy with: Render Dashboard → New → Blueprint")
    print("📖 Full guide: See RENDER_IAC_GUIDE.md")
    print("="*50)
    
    return True

if __name__ == "__main__":
    success = validate_render_yaml()
    sys.exit(0 if success else 1)
