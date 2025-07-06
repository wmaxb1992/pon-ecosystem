import os
import requests
import json
from typing import Iterator, Optional

GROK_API_KEY = os.getenv("GROK_API_KEY")
GROK_API_URL = "https://api.grok.x.ai/v1/chat/completions"  # Update if xAI changes endpoint


def call_grok(prompt, system_message=None, max_tokens=1024, temperature=0.2):
    """Standard Grok API call"""
    if not GROK_API_KEY:
        raise ValueError("GROK_API_KEY environment variable not set.")
    headers = {
        "Authorization": f"Bearer {GROK_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "grok-1",  # Update if xAI changes model name
        "messages": [
            {"role": "system", "content": system_message or "You are a helpful AI code assistant."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": max_tokens,
        "temperature": temperature
    }
    response = requests.post(GROK_API_URL, headers=headers, json=data)
    response.raise_for_status()
    result = response.json()
    return result["choices"][0]["message"]["content"]


def call_grok_streaming(prompt, system_message=None, max_tokens=1024, temperature=0.2) -> Iterator[str]:
    """Streaming Grok API call for real-time responses"""
    if not GROK_API_KEY:
        raise ValueError("GROK_API_KEY environment variable not set.")
    
    headers = {
        "Authorization": f"Bearer {GROK_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": "grok-1",
        "messages": [
            {"role": "system", "content": system_message or "You are a helpful AI code assistant."},
            {"role": "user", "content": prompt}
        ],
        "max_tokens": max_tokens,
        "temperature": temperature,
        "stream": True
    }
    
    try:
        response = requests.post(GROK_API_URL, headers=headers, json=data, stream=True)
        response.raise_for_status()
        
        for line in response.iter_lines():
            if line:
                line = line.decode('utf-8')
                if line.startswith('data: '):
                    data_str = line[6:]
                    if data_str.strip() == '[DONE]':
                        break
                    
                    try:
                        data_obj = json.loads(data_str)
                        if 'choices' in data_obj and len(data_obj['choices']) > 0:
                            choice = data_obj['choices'][0]
                            if 'delta' in choice and 'content' in choice['delta']:
                                yield choice['delta']['content']
                    except json.JSONDecodeError:
                        continue
    except Exception as e:
        # Fallback to regular call if streaming fails
        yield call_grok(prompt, system_message, max_tokens, temperature)


def get_grok_model_info():
    """Get available Grok models and info"""
    if not GROK_API_KEY:
        return {"error": "GROK_API_KEY not set"}
    
    try:
        headers = {
            "Authorization": f"Bearer {GROK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        # Try to get models endpoint (may not be available)
        models_url = GROK_API_URL.replace("/chat/completions", "/models")
        response = requests.get(models_url, headers=headers)
        
        if response.status_code == 200:
            return response.json()
        else:
            return {
                "available_models": ["grok-1"],
                "default_model": "grok-1",
                "status": "connected"
            }
    except Exception as e:
        return {"error": str(e)} 