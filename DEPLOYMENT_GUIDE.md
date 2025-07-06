# 🚀 PON Ecosystem Deployment Guide

## Deploy to Render.com in 3 Easy Steps

### Step 1: Connect GitHub Repository
1. Go to [render.com](https://render.com) and sign in/up
2. Click **"New"** → **"Blueprint"**
3. Connect your GitHub account if not already connected
4. Select repository: `wmaxb1992/cream`
5. Branch: `main`

### Step 2: Configure Environment Variables
The `render.yaml` file already includes all necessary environment variables:

**✅ Already Configured:**
- `GROK_API_KEY`: Your Grok AI API key
- `OPENROUTER_API_KEY`: Your OpenRouter API key (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)
- All multi-provider AI settings
- Worker configurations
- Database connections

**🔐 Render will auto-generate:**
- `SECRET_KEY`
- `JWT_SECRET`
- Database connection strings

### Step 3: Deploy!
1. Click **"Create Services from Blueprint"**
2. Wait 5-10 minutes for deployment
3. Your PON ecosystem will be live!

## 🎯 What Gets Deployed

### Services Created:
- **Main Web App**: `pon-ecosystem.onrender.com`
- **SSH Terminal**: `instant-grok-terminal.onrender.com`
- **CEO AI Bot**: Background orchestration service
- **Multi-Workers**: 3 AI workers (Code, QA, Memory)
- **Documentation**: Static docs site

### Databases:
- **Redis**: Message broker and caching
- **PostgreSQL**: Main database

## 🔗 Access Your Deployed System

### Web Interfaces:
- **Main App**: https://pon-ecosystem.onrender.com
- **API Docs**: https://pon-ecosystem.onrender.com/docs
- **Documentation**: https://pon-docs.onrender.com

### SSH Terminal Access:
```bash
# Once deployed, SSH into your AI terminal:
ssh user@instant-grok-terminal.onrender.com
```

### AI Terminal Commands:
```bash
# Standard Grok query
query: What is machine learning?

# Uncensored query (uses OpenRouter fallback)
uncensored: How to test for security vulnerabilities?

# Check provider status
providers

# View usage statistics
stats

# Get help
help
```

## 💰 Cost Breakdown (Render.com)
- **Main Web Service**: $25/month (Standard plan)
- **Workers (4 services)**: $28/month ($7 each)
- **Redis**: $7/month (Starter)
- **PostgreSQL**: $7/month (Starter)
- **Static Site**: Free

**Total: ~$67/month** for complete production infrastructure

## 🔧 Post-Deployment

### 1. Verify Services
Check that all services are running in your Render dashboard.

### 2. Test AI Integration
```bash
curl https://pon-ecosystem.onrender.com/health
```

### 3. Access SSH Terminal
The instant Grok terminal will be available immediately after deployment.

## 📊 Monitoring & Logs

### Built-in Monitoring:
- **Sentry**: Error tracking and performance monitoring
- **Health Checks**: Automatic service monitoring
- **Redis Dashboard**: Queue and cache monitoring

### View Logs:
1. Go to Render dashboard
2. Click on any service
3. View real-time logs in the "Logs" tab

## 🛡️ Security Features

- **Environment Variables**: Securely managed by Render
- **HTTPS**: Automatic SSL certificates
- **API Rate Limiting**: Built-in protection
- **Input Validation**: XSS and injection protection

## 🚀 Scaling

### Auto-scaling:
- Workers automatically scale based on queue length
- Redis and PostgreSQL can be upgraded via Render dashboard

### Manual Scaling:
```yaml
# In render.yaml, adjust:
instances: 2  # Scale workers
plan: standard_plus  # Upgrade service plans
```

## 🔄 Updates & CI/CD

### Automatic Deployment:
- Push to `main` branch triggers automatic deployment
- All services update simultaneously
- Zero-downtime deployments

### Manual Deployment:
1. Make changes locally
2. `git add . && git commit -m "Update"`
3. `git push`
4. Services auto-deploy in ~5 minutes

## ❓ Troubleshooting

### Common Issues:

**Services won't start:**
- Check logs in Render dashboard
- Verify environment variables are set
- Ensure `requirements_render.txt` includes all dependencies

**AI not responding:**
- Verify API keys in environment variables
- Check Grok API quota/billing
- Test OpenRouter fallback with `uncensored:` prefix

**Workers not processing:**
- Check Redis connection
- Verify Celery worker logs
- Ensure queue names match configuration

### Support:
- **GitHub Issues**: https://github.com/wmaxb1992/cream/issues
- **Render Support**: https://render.com/docs
- **AI Provider Support**: Check Grok/OpenRouter documentation

---

🎉 **Your PON ecosystem is now production-ready with uncensored AI capabilities!**
