# 🔒 Secure Video Scraper with VPN + Proxy Protection

This enhanced version of the video scraper includes multiple layers of security to protect your privacy and anonymity while scraping videos.

## 🛡️ Security Features

### 1. **VPN Protection** (python-vpn)
- **Layer 1**: VPN server running on port 5000
- **Protocols**: IKEv1, IKEv2, L2TP, WireGuard
- **Password**: `secure_vpn_password_2024` (change this!)
- **Automatic**: Starts with the backend server

### 2. **Proxy Protection** (free-proxy)
- **Layer 2**: Rotating HTTP/HTTPS proxies
- **Automatic**: All HTTP requests go through proxies
- **Fallback**: Multiple proxy sources for reliability

### 3. **IP Logging & Monitoring**
- **Real-time**: All requests logged with IP addresses
- **Security**: Threat detection and alerts
- **Audit**: Complete request history for analysis

## 🚀 Quick Start

### 1. Start the Secure Backend
```bash
cd backend
python main_secure.py
```

This will:
- Start the VPN server automatically
- Begin IP logging
- Start the background video search task
- Display current IP address

### 2. Monitor Security (Optional)
In a new terminal:
```bash
cd backend
python security_monitor.py
```

This provides a real-time security dashboard showing:
- Recent IP activity
- Security threats
- Log file status
- Current public IP

### 3. Connect VPN Client (Optional)
To connect another device to the VPN:
```bash
cd backend
python vpn_client.py <server_ip> <password> [port]
```

Example:
```bash
python vpn_client.py 192.168.1.100 secure_vpn_password_2024 5000
```

## 📊 Security Monitoring

### IP Access Logs
All requests are logged to `ip_access_log.txt`:
```
[2024-01-15 14:30:25] IP: 192.168.1.100 | Endpoint: /videos | User-Agent: Mozilla/5.0...
```

### Request Logs
Detailed request information in `request_log.txt`:
```json
{
  "timestamp": "2024-01-15 14:30:25",
  "ip": "192.168.1.100",
  "method": "GET",
  "url": "http://localhost:8000/videos",
  "status": 200,
  "user_agent": "Mozilla/5.0...",
  "referer": "",
  "x_forwarded_for": "",
  "x_real_ip": ""
}
```

### Security Alerts
The monitor detects:
- **High Frequency**: IPs making >50 requests
- **Suspicious Endpoints**: Access to admin/config paths
- **Unusual Patterns**: Anomalous behavior

## 🔧 Configuration

### VPN Settings
Edit `main_secure.py` to change VPN settings:
```python
VPN_PASSWORD = "your_secure_password_here"
VPN_PORT = 5000  # Change if needed
```

### Proxy Settings
The system automatically uses free proxies, but you can configure:
- Timeout settings
- Proxy rotation frequency
- Fallback sources

### Logging Settings
- Log files are created automatically
- Rotate logs periodically to manage disk space
- Monitor log file sizes

## 🌐 Network Architecture

```
Internet
    ↓
[VPN Server (python-vpn)]
    ↓
[Proxy Layer (free-proxy)]
    ↓
[FastAPI Backend]
    ↓
[IP Logging & Monitoring]
```

## 📱 API Endpoints

### Security Endpoints
- `GET /vpn-status` - Check VPN status
- `POST /vpn/start` - Start VPN server
- `POST /vpn/stop` - Stop VPN server
- `GET /logs/ip` - View IP access logs
- `GET /logs/requests` - View detailed request logs

### Video Endpoints
- `GET /videos` - Get all videos
- `POST /search` - Search for videos
- `GET /search-history` - View search history
- `DELETE /videos/{id}` - Delete video

## 🔍 Security Best Practices

### 1. **Change Default Password**
```python
# In main_secure.py
VPN_PASSWORD = "your_very_secure_password_here"
```

### 2. **Monitor Logs Regularly**
```bash
# Check for suspicious activity
python security_monitor.py --once

# Continuous monitoring
python security_monitor.py 10  # Update every 10 seconds
```

### 3. **Rotate Logs**
```bash
# Archive old logs
mv ip_access_log.txt ip_access_log_$(date +%Y%m%d).txt
mv request_log.txt request_log_$(date +%Y%m%d).txt
```

### 4. **Network Security**
- Use firewall rules to restrict access
- Monitor VPN connections
- Regularly update dependencies

## 🚨 Troubleshooting

### VPN Won't Start
```bash
# Check if port is in use
lsof -i :5000

# Kill existing process
kill -9 <PID>

# Restart backend
python main_secure.py
```

### Proxy Issues
```bash
# Test proxy connectivity
python -c "from free_proxy import FreeProxy; print(FreeProxy().get())"
```

### Log File Issues
```bash
# Check log file permissions
ls -la ip_access_log.txt

# Create if missing
touch ip_access_log.txt request_log.txt
```

## 📋 Dependencies

```bash
pip install fastapi uvicorn pvpn free-proxy yt-dlp httpx requests
```

## ⚠️ Important Notes

1. **Research Purposes Only**: This tool is for educational/research use
2. **Legal Compliance**: Ensure you comply with local laws and terms of service
3. **Privacy**: The VPN and proxy layers help protect your privacy
4. **Monitoring**: All activity is logged for security purposes
5. **Updates**: Keep dependencies updated for security patches

## 🔗 References

- [python-vpn GitHub](https://github.com/qwj/python-vpn)
- [free-proxy Documentation](https://pypi.org/project/free-proxy/)
- [FastAPI Security](https://fastapi.tiangolo.com/tutorial/security/)

---

**Remember**: This system provides multiple layers of security, but no system is 100% anonymous. Always use responsibly and in compliance with applicable laws and terms of service. 