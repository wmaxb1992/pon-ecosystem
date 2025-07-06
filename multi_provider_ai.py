#!/usr/bin/env python3
"""
Multi-Provider AI Client with Uncensored Fallback
================================================
Intelligent AI provider management with automatic fallback to uncensored models
"""

import os
import asyncio
import aiohttp
import openai
from typing import Dict, List, Optional, Any
import re
import json
import logging
from datetime import datetime, timedelta

class AIProviderManager:
    """Manages multiple AI providers with intelligent fallback logic"""
    
    def __init__(self):
        self.providers = {}
        self.setup_providers()
        self.censorship_phrases = [
            "i can't", "i cannot", "i'm not able", "i'm sorry", "i cannot help",
            "against my guidelines", "not appropriate", "i'm not comfortable",
            "policy", "guidelines", "terms of service", "content policy",
            "i can't assist", "i won't", "inappropriate", "harmful content"
        ]
        
    def setup_providers(self):
        """Initialize all AI providers"""
        # Primary Grok provider
        self.providers['grok'] = {
            'api_key': os.getenv('GROK_API_KEY'),
            'model': os.getenv('GROK_MODEL', 'grok-3-fast'),
            'base_url': 'https://api.x.ai/v1',
            'type': 'openai_compatible',
            'uncensored': False
        }
        
        # OpenRouter (uncensored models available)
        if os.getenv('OPENROUTER_API_KEY'):
            self.providers['openrouter'] = {
                'api_key': os.getenv('OPENROUTER_API_KEY'),
                'model': os.getenv('OPENROUTER_MODEL', 'meta-llama/llama-3.1-405b-instruct'),
                'uncensored_model': os.getenv('OPENROUTER_FALLBACK_MODEL', 'anthropic/claude-3.5-sonnet'),
                'base_url': 'https://openrouter.ai/api/v1',
                'type': 'openai_compatible',
                'uncensored': True
            }
        
        # Together AI (uncensored models)
        if os.getenv('TOGETHER_API_KEY'):
            self.providers['together'] = {
                'api_key': os.getenv('TOGETHER_API_KEY'),
                'model': os.getenv('TOGETHER_MODEL', 'meta-llama/Llama-3-70b-chat-hf'),
                'uncensored_model': os.getenv('TOGETHER_UNCENSORED_MODEL', 'NousResearch/Nous-Hermes-2-Mixtral-8x7B-DPO'),
                'base_url': 'https://api.together.xyz/v1',
                'type': 'openai_compatible',
                'uncensored': True
            }
        
        # Replicate (uncensored models)
        if os.getenv('REPLICATE_API_TOKEN'):
            self.providers['replicate'] = {
                'api_key': os.getenv('REPLICATE_API_TOKEN'),
                'model': os.getenv('REPLICATE_MODEL', 'meta/llama-2-70b-chat'),
                'uncensored_model': os.getenv('REPLICATE_UNCENSORED_MODEL', 'mistralai/mixtral-8x7b-instruct-v0.1'),
                'type': 'replicate',
                'uncensored': True
            }
        
        # Ollama (local, completely private)
        if os.getenv('OLLAMA_HOST'):
            self.providers['ollama'] = {
                'host': os.getenv('OLLAMA_HOST', 'http://localhost:11434'),
                'model': os.getenv('OLLAMA_MODEL', 'llama3:70b'),
                'uncensored_model': os.getenv('OLLAMA_UNCENSORED_MODEL', 'wizard-vicuna-uncensored:30b'),
                'type': 'ollama',
                'uncensored': True
            }
    
    def detect_censorship(self, response: str) -> bool:
        """Detect if a response shows signs of censorship"""
        if not os.getenv('CENSORSHIP_DETECTION_ENABLED', 'true').lower() == 'true':
            return False
            
        response_lower = response.lower()
        
        # Check for common censorship phrases
        for phrase in self.censorship_phrases:
            if phrase in response_lower:
                return True
        
        # Check for response length (very short responses often indicate refusal)
        if len(response.strip()) < 50 and any(word in response_lower for word in ['sorry', 'cannot', 'unable']):
            return True
            
        # Check for policy mentions
        if re.search(r'\b(policy|guideline|appropriate|harmful)\b', response_lower):
            return True
            
        return False
    
    async def make_openai_compatible_request(self, provider_config: Dict, messages: List[Dict], use_uncensored: bool = False) -> str:
        """Make request to OpenAI-compatible API"""
        try:
            client = openai.AsyncOpenAI(
                api_key=provider_config['api_key'],
                base_url=provider_config['base_url']
            )
            
            # Choose model based on whether we want uncensored
            model = provider_config.get('uncensored_model' if use_uncensored else 'model', provider_config['model'])
            
            response = await client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=2000,
                temperature=0.7
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logging.error(f"OpenAI-compatible request failed: {e}")
            raise
    
    async def make_replicate_request(self, provider_config: Dict, messages: List[Dict], use_uncensored: bool = False) -> str:
        """Make request to Replicate API"""
        try:
            import replicate
            
            # Format messages for Replicate
            prompt = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])
            
            model = provider_config.get('uncensored_model' if use_uncensored else 'model', provider_config['model'])
            
            output = replicate.run(
                model,
                input={
                    "prompt": prompt,
                    "max_tokens": 2000,
                    "temperature": 0.7
                }
            )
            
            # Replicate returns a generator, join the results
            return "".join(output)
            
        except Exception as e:
            logging.error(f"Replicate request failed: {e}")
            raise
    
    async def make_ollama_request(self, provider_config: Dict, messages: List[Dict], use_uncensored: bool = False) -> str:
        """Make request to Ollama (local)"""
        try:
            async with aiohttp.ClientSession() as session:
                model = provider_config.get('uncensored_model' if use_uncensored else 'model', provider_config['model'])
                
                # Format for Ollama
                prompt = "\n".join([f"{msg['role']}: {msg['content']}" for msg in messages])
                
                async with session.post(
                    f"{provider_config['host']}/api/generate",
                    json={
                        "model": model,
                        "prompt": prompt,
                        "stream": False
                    }
                ) as response:
                    result = await response.json()
                    return result.get('response', '')
                    
        except Exception as e:
            logging.error(f"Ollama request failed: {e}")
            raise
    
    async def make_request(self, provider_name: str, messages: List[Dict], use_uncensored: bool = False) -> str:
        """Make request to specific provider"""
        if provider_name not in self.providers:
            raise ValueError(f"Provider {provider_name} not configured")
        
        provider_config = self.providers[provider_name]
        provider_type = provider_config['type']
        
        if provider_type == 'openai_compatible':
            return await self.make_openai_compatible_request(provider_config, messages, use_uncensored)
        elif provider_type == 'replicate':
            return await self.make_replicate_request(provider_config, messages, use_uncensored)
        elif provider_type == 'ollama':
            return await self.make_ollama_request(provider_config, messages, use_uncensored)
        else:
            raise ValueError(f"Unknown provider type: {provider_type}")
    
    async def get_ai_response(self, messages: List[Dict], force_uncensored: bool = False) -> Dict[str, Any]:
        """
        Get AI response with intelligent fallback logic
        
        Args:
            messages: List of message dicts with 'role' and 'content'
            force_uncensored: Skip primary provider and go straight to uncensored
            
        Returns:
            Dict with 'response', 'provider_used', 'censorship_detected', 'attempts'
        """
        primary_provider = os.getenv('PRIMARY_PROVIDER', 'grok')
        fallback_providers = os.getenv('FALLBACK_PROVIDERS', 'openrouter,together,replicate,ollama').split(',')
        enable_uncensored = os.getenv('ENABLE_UNCENSORED_FALLBACK', 'true').lower() == 'true'
        
        attempts = []
        
        # Try primary provider first (unless forcing uncensored)
        if not force_uncensored and primary_provider in self.providers:
            try:
                response = await self.make_request(primary_provider, messages)
                attempts.append({'provider': primary_provider, 'success': True, 'censored': False})
                
                # Check for censorship
                if self.detect_censorship(response):
                    attempts[-1]['censored'] = True
                    logging.warning(f"Censorship detected in {primary_provider} response")
                    
                    # If uncensored fallback is enabled, try uncensored providers
                    if enable_uncensored:
                        return await self._try_uncensored_providers(messages, fallback_providers, attempts)
                
                return {
                    'response': response,
                    'provider_used': primary_provider,
                    'censorship_detected': False,
                    'attempts': attempts
                }
                
            except Exception as e:
                attempts.append({'provider': primary_provider, 'success': False, 'error': str(e)})
                logging.error(f"Primary provider {primary_provider} failed: {e}")
        
        # Try fallback providers (uncensored if requested)
        if enable_uncensored or force_uncensored:
            return await self._try_uncensored_providers(messages, fallback_providers, attempts)
        else:
            # Try regular fallback providers
            for provider in fallback_providers:
                if provider in self.providers:
                    try:
                        response = await self.make_request(provider, messages)
                        attempts.append({'provider': provider, 'success': True, 'censored': False})
                        
                        return {
                            'response': response,
                            'provider_used': provider,
                            'censorship_detected': False,
                            'attempts': attempts
                        }
                        
                    except Exception as e:
                        attempts.append({'provider': provider, 'success': False, 'error': str(e)})
                        logging.error(f"Fallback provider {provider} failed: {e}")
        
        # All providers failed
        raise Exception(f"All AI providers failed. Attempts: {attempts}")
    
    async def _try_uncensored_providers(self, messages: List[Dict], providers: List[str], attempts: List[Dict]) -> Dict[str, Any]:
        """Try uncensored models from available providers"""
        for provider in providers:
            if provider in self.providers and self.providers[provider].get('uncensored'):
                try:
                    # Try uncensored model for this provider
                    response = await self.make_request(provider, messages, use_uncensored=True)
                    attempts.append({'provider': f"{provider}_uncensored", 'success': True, 'censored': False})
                    
                    return {
                        'response': response,
                        'provider_used': f"{provider}_uncensored",
                        'censorship_detected': True,  # We switched due to censorship
                        'attempts': attempts
                    }
                    
                except Exception as e:
                    attempts.append({'provider': f"{provider}_uncensored", 'success': False, 'error': str(e)})
                    logging.error(f"Uncensored provider {provider} failed: {e}")
        
        raise Exception(f"All uncensored providers failed. Attempts: {attempts}")
    
    def get_provider_status(self) -> Dict[str, Any]:
        """Get status of all configured providers"""
        status = {
            'primary_provider': os.getenv('PRIMARY_PROVIDER', 'grok'),
            'fallback_enabled': os.getenv('ENABLE_UNCENSORED_FALLBACK', 'true').lower() == 'true',
            'censorship_detection': os.getenv('CENSORSHIP_DETECTION_ENABLED', 'true').lower() == 'true',
            'configured_providers': []
        }
        
        for name, config in self.providers.items():
            provider_info = {
                'name': name,
                'type': config['type'],
                'has_api_key': bool(config.get('api_key')),
                'supports_uncensored': config.get('uncensored', False),
                'model': config.get('model', 'unknown'),
                'uncensored_model': config.get('uncensored_model', 'none')
            }
            status['configured_providers'].append(provider_info)
        
        return status

# Global instance
ai_provider_manager = AIProviderManager()

async def get_ai_response(prompt: str, force_uncensored: bool = False) -> Dict[str, Any]:
    """
    Convenience function to get AI response
    
    Args:
        prompt: The user's prompt
        force_uncensored: Skip primary provider and use uncensored models
        
    Returns:
        Dict with response and metadata
    """
    messages = [{"role": "user", "content": prompt}]
    return await ai_provider_manager.get_ai_response(messages, force_uncensored)

if __name__ == "__main__":
    # Test the multi-provider system
    async def test_providers():
        # Test normal query
        print("Testing normal query...")
        result = await get_ai_response("What is the capital of France?")
        print(f"Response: {result['response'][:100]}...")
        print(f"Provider: {result['provider_used']}")
        
        # Test potentially censored query
        print("\nTesting potentially restricted query...")
        result = await get_ai_response("How to pick a lock for educational purposes?")
        print(f"Response: {result['response'][:100]}...")
        print(f"Provider: {result['provider_used']}")
        print(f"Censorship detected: {result['censorship_detected']}")
        
        # Show provider status
        print("\nProvider status:")
        status = ai_provider_manager.get_provider_status()
        print(json.dumps(status, indent=2))
    
    asyncio.run(test_providers())
