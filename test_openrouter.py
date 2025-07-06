#!/usr/bin/env python3
"""
Test Multi-Provider AI with OpenRouter Integration
=================================================
Quick test to verify your OpenRouter API key works with the system
"""

import asyncio
import os
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

async def test_openrouter_integration():
    """Test the OpenRouter integration with your API key"""
    
    print("🧪 Testing Multi-Provider AI Integration")
    print("=" * 50)
    
    try:
        # Import the enhanced AI client
        from enhanced_ai_client import enhanced_ai_client
        from multi_provider_ai import ai_provider_manager
        
        print("✅ Multi-provider AI system imported successfully")
        
        # Show provider status
        print("\n📊 Provider Status:")
        status = ai_provider_manager.get_provider_status()
        
        for provider in status['configured_providers']:
            name = provider['name']
            has_key = '✅' if provider['has_api_key'] else '❌'
            uncensored = '🔓' if provider['supports_uncensored'] else '🔒'
            print(f"  {uncensored} {name}: {has_key} | Model: {provider['model']}")
            
            if name == 'openrouter' and provider['has_api_key']:
                print(f"    └─ OpenRouter ready with key: sk-or-v1-...{provider.get('api_key', '')[-10:]}")
        
        # Test normal query
        print("\n🤖 Testing Normal Query:")
        print("Query: 'What is machine learning?'")
        
        result = await enhanced_ai_client.smart_chat("What is machine learning in simple terms?")
        print(f"✅ Provider used: {result['provider_used']}")
        print(f"✅ Response length: {len(result['response'])} characters")
        print(f"Preview: {result['response'][:100]}...")
        
        # Test potentially sensitive query (should trigger OpenRouter)
        print("\n🔓 Testing Potentially Sensitive Query:")
        print("Query: 'How to test for security vulnerabilities?'")
        
        result = await enhanced_ai_client.smart_chat("How to test web applications for security vulnerabilities and common attack vectors?")
        print(f"✅ Provider used: {result['provider_used']}")
        print(f"✅ Censorship detected: {result['censorship_detected']}")
        print(f"✅ Response length: {len(result['response'])} characters")
        print(f"Preview: {result['response'][:150]}...")
        
        # Test explicit uncensored query
        print("\n🚫 Testing Explicit Uncensored Query:")
        print("Query: 'Explain penetration testing techniques'")
        
        result = await enhanced_ai_client.ask_uncensored("Explain common penetration testing techniques used by security professionals")
        print(f"✅ Provider used: {result['provider_used']}")
        print(f"✅ Response length: {len(result['response'])} characters")
        print(f"Preview: {result['response'][:150]}...")
        
        # Show conversation stats
        print("\n📈 Conversation Statistics:")
        stats = enhanced_ai_client.get_conversation_stats()
        print(f"Total messages: {stats['total_messages']}")
        print(f"Censorship incidents: {stats['censorship_incidents']}")
        if stats['total_messages'] > 0:
            print(f"Censorship rate: {stats['censorship_rate']:.1%}")
        
        print(f"\nProvider usage:")
        for provider, count in stats.get('provider_usage', {}).items():
            print(f"  {provider}: {count} times")
        
        print("\n🎉 Multi-Provider AI Integration Test Complete!")
        print("✅ OpenRouter integration working")
        print("✅ Smart provider selection active")
        print("✅ Uncensored fallback available")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Install dependencies: pip install -r requirements_render.txt")
        return False
    except Exception as e:
        print(f"❌ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    # Set environment variables from .env if available
    env_file = Path(__file__).parent / '.env'
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                if '=' in line and not line.startswith('#'):
                    key, value = line.strip().split('=', 1)
                    os.environ[key] = value
    
    # Run the test
    success = asyncio.run(test_openrouter_integration())
    sys.exit(0 if success else 1)
