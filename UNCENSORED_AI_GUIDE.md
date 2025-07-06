# 🔓 Uncensored AI Integration Guide

## 🎯 Overview

Your PON ecosystem now includes **intelligent multi-provider AI** with automatic fallback to uncensored models when Grok refuses to answer certain queries.

## 🚀 How It Works

### **Automatic Smart Detection**
The system automatically detects when queries might be censored and:
1. **Tries Grok first** (your primary provider)
2. **Detects censorship** if Grok refuses or gives a restrictive response
3. **Automatically switches** to uncensored providers
4. **Returns the unrestricted response**

### **Manual Uncensored Mode**
For sensitive topics, you can directly use uncensored providers:
```bash
uncensored: How to implement penetration testing for web applications?
uncensored: Explain advanced reverse engineering techniques for security research
uncensored: How to detect and prevent SQL injection attacks in detail?
```

## 🔧 Available Providers

### **Primary Provider (Censored)**
- **Grok**: Your main AI provider (fast, reliable, some restrictions)

### **Uncensored Fallback Providers**
- **OpenRouter**: Access to Llama, Claude, and other uncensored models
- **Together AI**: Open-source models without restrictions
- **Replicate**: Cloud-hosted uncensored models
- **Ollama**: Local uncensored models (completely private)

## 📋 Setup Instructions

### 1. **API Keys** (Optional - for more providers)
Add these to your `.env` file if you want more uncensored options:

```bash
# OpenRouter (recommended for uncensored)
OPENROUTER_API_KEY=your_openrouter_key_here

# Together AI (good for open models)
TOGETHER_API_KEY=your_together_key_here

# Replicate (cloud models)
REPLICATE_API_TOKEN=your_replicate_token_here

# Ollama (local - no API key needed)
OLLAMA_HOST=http://localhost:11434
```

### 2. **Current Setup** (Already Working!)
Your current setup uses **single Grok API key** for most operations, which is optimal:
- ✅ **Cost effective**: One subscription
- ✅ **Rate limit pooling**: Shared across all workers
- ✅ **Simple management**: One key to maintain
- ✅ **Fallback ready**: Additional providers when needed

## 🎮 Terminal Commands

### **Check Provider Status**
```bash
providers
```
Shows all configured AI providers and their availability.

### **View AI Statistics**
```bash
stats  
```
Shows conversation stats, censorship incidents, and provider usage.

### **Use Uncensored AI**
```bash
uncensored: <your sensitive query here>
```
Directly uses uncensored providers, skipping Grok.

### **Smart Chat** (Default)
```bash
<any regular message>
```
Automatically detects if censorship occurs and switches providers.

## 🧠 Smart Query Detection

The system automatically detects potentially censored queries by looking for:
- Security/hacking related terms
- "How to" instructions for sensitive topics
- Potentially illegal activities
- Adult content references

**Example automatic fallback:**
```
User: "How to bypass web application security measures?"
System: Detects sensitive query → Tries uncensored providers automatically
```

## 🔍 Censorship Detection

The system detects censorship by analyzing responses for:
- Common refusal phrases ("I can't", "against my guidelines")
- Policy mentions
- Very short refusal responses
- Content policy warnings

## 📊 Monitoring & Analytics

### **Real-time Stats**
- Track which providers are used most
- Monitor censorship incident rates
- Analyze common censorship patterns
- Export conversation history

### **Usage Examples**
```bash
# View provider status
providers

# Check AI conversation statistics  
stats

# Export conversation history
# (Available in code - auto-exports to JSON)
```

## 🔒 Privacy & Security

### **Data Handling**
- **Grok**: Standard OpenAI-compatible API
- **OpenRouter/Together**: Third-party but reputable
- **Replicate**: Cloud-hosted models
- **Ollama**: **Completely local** (most private)

### **Recommendation for Sensitive Queries**
1. **Ollama** (local) - Most private
2. **OpenRouter** - Good balance of privacy/capability
3. **Together AI** - Open-source models
4. **Replicate** - Last resort

## 💡 Best Practices

### **For Regular Queries**
- Just chat normally - the system handles provider selection automatically
- Let Grok try first (it's fast and usually sufficient)

### **For Sensitive/Educational Queries**
- Use `uncensored:` prefix for direct access to unrestricted models
- Great for security research, penetration testing, reverse engineering
- Educational content that might trigger false positives

### **For Maximum Privacy**
- Set up Ollama locally for completely private queries
- No data leaves your machine

## 🎯 Example Usage Scenarios

### **Security Research**
```bash
uncensored: Explain common web application vulnerabilities and how to test for them
uncensored: How to set up a controlled penetration testing environment?
```

### **Programming/Technical**
```bash
uncensored: How to implement cryptographic functions that might be flagged as 'dangerous'?
uncensored: Explain buffer overflow techniques for educational purposes
```

### **General Unrestricted Queries**
```bash
uncensored: Discuss controversial technical topics without content filtering
uncensored: Provide unfiltered analysis of security tools and techniques
```

## 🚀 Already Deployed!

This multi-provider system is **already included** in your `render.yaml` deployment:
- ✅ All dependencies included in `requirements_render.txt`
- ✅ Environment variables configured in `.env`
- ✅ Commands available in live AI terminal
- ✅ Ready for production use

**No additional setup needed** - just start using the new commands!

## 🎉 Benefits

### **For Users**
- **No more censorship frustration** - automatic fallback
- **Educational freedom** - access unrestricted models for learning
- **Research capabilities** - security/technical research without barriers

### **For Developers**  
- **Single API key strategy** - cost effective
- **Intelligent routing** - best provider for each query type
- **Monitoring** - track provider usage and success rates
- **Flexibility** - easy to add new providers

**Your PON ecosystem now provides unrestricted AI access while maintaining cost efficiency and ease of use!** 🎯🔓
