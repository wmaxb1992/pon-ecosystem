#!/usr/bin/env python3
"""
Enhanced AI Client with Multi-Provider Support
==============================================
Intelligent AI client with censorship detection and uncensored fallback
"""

import os
import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

# Import the multi-provider system
from multi_provider_ai import ai_provider_manager

class EnhancedAIClient:
    """Enhanced AI client with intelligent provider fallback"""
    
    def __init__(self):
        self.provider_manager = ai_provider_manager
        self.conversation_history = []
        self.censorship_log = []
        self.logger = logging.getLogger(__name__)
        
    async def chat(self, message: str, context: str = "", force_uncensored: bool = False) -> Dict[str, Any]:
        """
        Send a chat message with intelligent provider selection
        
        Args:
            message: User message
            context: Additional context to include
            force_uncensored: Skip primary provider and use uncensored models
            
        Returns:
            Dict with response, provider info, and metadata
        """
        try:
            # Prepare the full prompt
            full_prompt = f"{context}\n\nUser: {message}" if context else message
            
            # Get AI response with fallback logic
            result = await self.provider_manager.get_ai_response(
                [{"role": "user", "content": full_prompt}],
                force_uncensored=force_uncensored
            )
            
            # Log the interaction
            interaction = {
                'timestamp': datetime.now().isoformat(),
                'message': message,
                'context_provided': bool(context),
                'force_uncensored': force_uncensored,
                'provider_used': result['provider_used'],
                'censorship_detected': result['censorship_detected'],
                'response_preview': result['response'][:100] + "..." if len(result['response']) > 100 else result['response']
            }
            
            self.conversation_history.append(interaction)
            
            # Log censorship incidents
            if result['censorship_detected']:
                censorship_incident = {
                    'timestamp': datetime.now().isoformat(),
                    'original_query': message,
                    'primary_provider': result['attempts'][0]['provider'] if result['attempts'] else 'unknown',
                    'fallback_provider': result['provider_used'],
                    'auto_switched': True
                }
                self.censorship_log.append(censorship_incident)
                self.logger.info(f"Censorship detected, switched to {result['provider_used']}")
            
            return result
            
        except Exception as e:
            self.logger.error(f"Chat request failed: {e}")
            raise
    
    async def ask_uncensored(self, message: str, context: str = "") -> Dict[str, Any]:
        """
        Directly ask an uncensored model, skipping the primary provider
        
        Args:
            message: User message
            context: Additional context
            
        Returns:
            Response from uncensored model
        """
        return await self.chat(message, context, force_uncensored=True)
    
    def detect_sensitive_query(self, message: str) -> bool:
        """
        Detect if a query might trigger censorship
        
        Args:
            message: User message to analyze
            
        Returns:
            True if the query might be censored
        """
        sensitive_keywords = [
            'hack', 'exploit', 'crack', 'bypass', 'jailbreak',
            'illegal', 'drugs', 'weapons', 'violence', 'harmful',
            'unethical', 'malicious', 'adult content', 'nsfw'
        ]
        
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in sensitive_keywords)
    
    async def smart_chat(self, message: str, context: str = "") -> Dict[str, Any]:
        """
        Smart chat that automatically chooses the best approach
        
        Args:
            message: User message
            context: Additional context
            
        Returns:
            AI response with optimal provider selection
        """
        # Check if this might be a sensitive query
        might_be_censored = self.detect_sensitive_query(message)
        
        if might_be_censored:
            self.logger.info("Sensitive query detected, trying uncensored providers")
            try:
                # Try uncensored first for potentially sensitive queries
                return await self.ask_uncensored(message, context)
            except Exception as e:
                self.logger.warning(f"Uncensored providers failed, falling back to primary: {e}")
                return await self.chat(message, context)
        else:
            # Normal chat flow with automatic fallback
            return await self.chat(message, context)
    
    def get_conversation_stats(self) -> Dict[str, Any]:
        """Get statistics about the conversation"""
        if not self.conversation_history:
            return {"total_messages": 0}
        
        total_messages = len(self.conversation_history)
        censorship_incidents = len(self.censorship_log)
        
        # Provider usage stats
        provider_usage = {}
        for interaction in self.conversation_history:
            provider = interaction['provider_used']
            provider_usage[provider] = provider_usage.get(provider, 0) + 1
        
        # Most used provider
        most_used_provider = max(provider_usage.items(), key=lambda x: x[1]) if provider_usage else ("none", 0)
        
        return {
            'total_messages': total_messages,
            'censorship_incidents': censorship_incidents,
            'censorship_rate': censorship_incidents / total_messages if total_messages > 0 else 0,
            'provider_usage': provider_usage,
            'most_used_provider': most_used_provider[0],
            'primary_success_rate': (provider_usage.get('grok', 0) / total_messages) if total_messages > 0 else 0
        }
    
    def get_censorship_report(self) -> Dict[str, Any]:
        """Get detailed censorship report"""
        if not self.censorship_log:
            return {"total_incidents": 0, "incidents": []}
        
        return {
            'total_incidents': len(self.censorship_log),
            'incidents': self.censorship_log[-10:],  # Last 10 incidents
            'common_patterns': self._analyze_censorship_patterns()
        }
    
    def _analyze_censorship_patterns(self) -> List[str]:
        """Analyze common patterns in censored queries"""
        if not self.censorship_log:
            return []
        
        # Simple pattern analysis - could be enhanced with ML
        patterns = []
        for incident in self.censorship_log:
            query = incident['original_query'].lower()
            
            if 'how to' in query:
                patterns.append("'How to' instructions")
            if any(word in query for word in ['hack', 'crack', 'exploit']):
                patterns.append("Security/hacking related")
            if any(word in query for word in ['illegal', 'unethical']):
                patterns.append("Potentially illegal activities")
        
        # Return unique patterns
        return list(set(patterns))
    
    def export_conversation(self, filename: str = None) -> str:
        """Export conversation history to file"""
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"ai_conversation_{timestamp}.json"
        
        export_data = {
            'export_timestamp': datetime.now().isoformat(),
            'conversation_stats': self.get_conversation_stats(),
            'censorship_report': self.get_censorship_report(),
            'conversation_history': self.conversation_history,
            'provider_status': self.provider_manager.get_provider_status()
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            import json
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"Conversation exported to {filename}")
        return filename
    
    async def test_providers(self) -> Dict[str, Any]:
        """Test all available providers"""
        test_message = "Hello, can you tell me about artificial intelligence?"
        results = {}
        
        # Test primary provider
        try:
            result = await self.chat(test_message)
            results['primary'] = {
                'provider': result['provider_used'],
                'success': True,
                'response_length': len(result['response'])
            }
        except Exception as e:
            results['primary'] = {'success': False, 'error': str(e)}
        
        # Test uncensored providers
        try:
            result = await self.ask_uncensored(test_message)
            results['uncensored'] = {
                'provider': result['provider_used'],
                'success': True,
                'response_length': len(result['response'])
            }
        except Exception as e:
            results['uncensored'] = {'success': False, 'error': str(e)}
        
        return results

# Global enhanced AI client instance
enhanced_ai_client = EnhancedAIClient()

async def ask_ai(message: str, context: str = "", smart_mode: bool = True) -> str:
    """
    Convenience function for AI interactions
    
    Args:
        message: User message
        context: Additional context
        smart_mode: Use smart provider selection
        
    Returns:
        AI response text
    """
    if smart_mode:
        result = await enhanced_ai_client.smart_chat(message, context)
    else:
        result = await enhanced_ai_client.chat(message, context)
    
    return result['response']

async def ask_uncensored(message: str, context: str = "") -> str:
    """
    Convenience function for uncensored AI interactions
    
    Args:
        message: User message
        context: Additional context
        
    Returns:
        Uncensored AI response
    """
    result = await enhanced_ai_client.ask_uncensored(message, context)
    return result['response']

if __name__ == "__main__":
    # Test the enhanced AI client
    async def demo():
        print("🤖 Enhanced AI Client Demo")
        print("=" * 40)
        
        # Test normal query
        print("\n1. Normal Query Test:")
        result = await enhanced_ai_client.smart_chat("What is machine learning?")
        print(f"Provider: {result['provider_used']}")
        print(f"Response: {result['response'][:100]}...")
        
        # Test potentially sensitive query
        print("\n2. Potentially Sensitive Query Test:")
        result = await enhanced_ai_client.smart_chat("How to protect against SQL injection attacks?")
        print(f"Provider: {result['provider_used']}")
        print(f"Censorship detected: {result['censorship_detected']}")
        print(f"Response: {result['response'][:100]}...")
        
        # Show stats
        print("\n3. Conversation Stats:")
        stats = enhanced_ai_client.get_conversation_stats()
        print(f"Total messages: {stats['total_messages']}")
        print(f"Primary success rate: {stats.get('primary_success_rate', 0):.1%}")
        print(f"Provider usage: {stats.get('provider_usage', {})}")
        
        # Test providers
        print("\n4. Provider Test:")
        test_results = await enhanced_ai_client.test_providers()
        for test_type, result in test_results.items():
            print(f"{test_type}: {result}")
    
    asyncio.run(demo())
