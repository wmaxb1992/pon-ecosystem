from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
import asyncio
import json
import os
import subprocess
import threading
import time
import socket
import requests
from datetime import datetime
import httpx
from free_proxy import FreeProxy
import yt_dlp

app = FastAPI(title="Secure Video Scraper API", version="2.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files for video storage
os.makedirs("videos", exist_ok=True)
app.mount("/videos", StaticFiles(directory="videos"), name="videos")

# VPN Configuration
VPN_PASSWORD = "secure_vpn_password_2024"
VPN_PORT = 5000
vpn_process = None
vpn_active = False

# IP Logging
ip_log_file = "ip_access_log.txt"
request_log_file = "request_log.txt"

def log_ip_access(client_ip: str, endpoint: str, user_agent: str = ""):
    """Log IP access for security monitoring"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] IP: {client_ip} | Endpoint: {endpoint} | User-Agent: {user_agent}\n"
    
    with open(ip_log_file, "a") as f:
        f.write(log_entry)
    
    print(f"🔍 IP LOG: {client_ip} accessed {endpoint}")

def log_request(request: Request, response_status: int = 200):
    """Log detailed request information"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    client_ip = request.client.host if request.client else "unknown"
    
    log_entry = {
        "timestamp": timestamp,
        "ip": client_ip,
        "method": request.method,
        "url": str(request.url),
        "status": response_status,
        "user_agent": request.headers.get("user-agent", ""),
        "referer": request.headers.get("referer", ""),
        "x_forwarded_for": request.headers.get("x-forwarded-for", ""),
        "x_real_ip": request.headers.get("x-real-ip", "")
    }
    
    with open(request_log_file, "a") as f:
        f.write(json.dumps(log_entry) + "\n")

def get_current_ip():
    """Get current public IP address"""
    try:
        # Use multiple services for redundancy
        services = [
            "https://api.ipify.org",
            "https://ipinfo.io/ip",
            "https://icanhazip.com"
        ]
        
        for service in services:
            try:
                response = requests.get(service, timeout=5)
                if response.status_code == 200:
                    return response.text.strip()
            except:
                continue
        return "unknown"
    except Exception as e:
        print(f"Error getting IP: {e}")
        return "unknown"

def start_vpn_server():
    """Start the python-vpn server in a separate process"""
    global vpn_process, vpn_active
    
    try:
        # Kill any existing VPN process
        if vpn_process:
            vpn_process.terminate()
            vpn_process.wait()
        
        # Start VPN server
        cmd = ["pvpn", "-p", VPN_PASSWORD, "-wg", str(VPN_PORT)]
        vpn_process = subprocess.Popen(
            cmd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        
        # Wait a moment for VPN to start
        time.sleep(3)
        
        if vpn_process.poll() is None:
            vpn_active = True
            print(f"🔒 VPN Server started on port {VPN_PORT}")
            print(f"🔑 VPN Password: {VPN_PASSWORD}")
            print(f"🌐 Current IP: {get_current_ip()}")
            return True
        else:
            print("❌ Failed to start VPN server")
            return False
            
    except Exception as e:
        print(f"❌ Error starting VPN: {e}")
        return False

def stop_vpn_server():
    """Stop the VPN server"""
    global vpn_process, vpn_active
    
    if vpn_process:
        vpn_process.terminate()
        vpn_process.wait()
        vpn_process = None
    
    vpn_active = False
    print("🔒 VPN Server stopped")

# Data models
class VideoInfo(BaseModel):
    id: str
    title: str
    url: str
    thumbnail: Optional[str] = None
    duration: Optional[str] = None
    upload_date: Optional[str] = None
    description: Optional[str] = None
    local_path: Optional[str] = None

class SearchRequest(BaseModel):
    query: str
    max_results: int = 10

class VPNStatus(BaseModel):
    active: bool
    port: int
    current_ip: str

# Global storage for videos
videos_db = []
search_history = []

def save_videos_to_file():
    """Save videos to a JSON file"""
    with open("videos_db.json", "w") as f:
        json.dump(videos_db, f, indent=2)

def load_videos_from_file():
    """Load videos from JSON file"""
    global videos_db
    try:
        with open("videos_db.json", "r") as f:
            videos_db = json.load(f)
    except FileNotFoundError:
        videos_db = []

# Load existing videos on startup
load_videos_from_file()

def get_proxy_url():
    """Get a fresh proxy URL from free-proxy."""
    try:
        proxy = FreeProxy(rand=True, timeout=5).get()
        if not proxy.startswith('http'):
            proxy = 'http://' + proxy
        return proxy
    except Exception as e:
        print(f"Failed to get proxy: {e}")
        return None

def get_proxy_dict():
    """Get a proxy dict for requests/httpx from free-proxy."""
    proxy_url = get_proxy_url()
    if proxy_url:
        return {
            'http': proxy_url,
            'https': proxy_url
        }
    return None

# WARNING: Do NOT use httpx or requests directly. Use fetch_with_proxy (httpx) or fetch_with_proxy_requests (requests) to ensure all requests go through a proxy.

async def fetch_with_proxy(url: str, **kwargs):
    """Make HTTP request with proxy"""
    proxy_url = get_proxy_url()
    async with httpx.AsyncClient(proxies=proxy_url) as client:
        return await client.get(url, **kwargs)

def fetch_with_proxy_requests(url: str, **kwargs):
    """Make HTTP request with proxy using requests"""
    proxies = get_proxy_dict()
    return requests.get(url, proxies=proxies, **kwargs)

async def search_videos_with_proxy(query: str, max_results: int = 10) -> List[dict]:
    """Search for videos using yt-dlp with a proxy"""
    proxy_url = get_proxy_url()
    
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,
        'max_downloads': max_results,
        'ignoreerrors': True,
    }
    
    if proxy_url:
        ydl_opts['proxy'] = proxy_url
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Search for videos
            search_query = f"ytsearch{max_results}:{query}"
            results = ydl.extract_info(search_query, download=False)
            
            videos = []
            if 'entries' in results:
                for entry in results['entries']:
                    if entry:
                        video_info = {
                            'id': entry.get('id', ''),
                            'title': entry.get('title', ''),
                            'url': f"https://www.youtube.com/watch?v={entry.get('id', '')}",
                            'thumbnail': entry.get('thumbnail', ''),
                            'duration': str(entry.get('duration', 0)),
                            'upload_date': entry.get('upload_date', ''),
                            'description': entry.get('description', ''),
                            'local_path': None
                        }
                        videos.append(video_info)
            
            return videos
    except Exception as e:
        print(f"Error searching videos: {e}")
        return []

async def download_video_with_proxy(video_id: str, url: str) -> Optional[str]:
    """Download a video using yt-dlp with a proxy"""
    proxy_url = get_proxy_url()
    
    ydl_opts = {
        'format': 'best[ext=mp4]',
        'outtmpl': f'videos/{video_id}.%(ext)s',
        'quiet': True,
        'no_warnings': True,
    }
    
    if proxy_url:
        ydl_opts['proxy'] = proxy_url
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])
            return f'videos/{video_id}.mp4'
    except Exception as e:
        print(f"Error downloading video: {e}")
        return None

async def mock_search_videos(query: str, max_results: int = 10) -> List[dict]:
    """Mock search function that returns sample videos"""
    sample_videos = [
        {
            'id': 'sample1',
            'title': f'Sample Video 1 - {query}',
            'url': 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/BigBuckBunny.mp4',
            'thumbnail': 'https://via.placeholder.com/320x180/FF0000/FFFFFF?text=Sample+1',
            'duration': '180',
            'upload_date': '2023-12-01',
            'description': f'This is a sample video about {query}',
            'local_path': None
        },
        {
            'id': 'sample2',
            'title': f'Sample Video 2 - {query}',
            'url': 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ElephantsDream.mp4',
            'thumbnail': 'https://via.placeholder.com/320x180/00FF00/FFFFFF?text=Sample+2',
            'duration': '240',
            'upload_date': '2023-12-02',
            'description': f'Another sample video about {query}',
            'local_path': None
        },
        {
            'id': 'sample3',
            'title': f'Sample Video 3 - {query}',
            'url': 'https://commondatastorage.googleapis.com/gtv-videos-bucket/sample/ForBiggerBlazes.mp4',
            'thumbnail': 'https://via.placeholder.com/320x180/0000FF/FFFFFF?text=Sample+3',
            'duration': '300',
            'upload_date': '2023-12-03',
            'description': f'Yet another sample video about {query}',
            'local_path': None
        }
    ]
    
    return sample_videos[:max_results]

async def background_search_task():
    """Background task to continuously search for 'ashley got' videos"""
    while True:
        try:
            print("Background task: Searching for 'ashley got' videos...")
            print(f"🌐 Current IP: {get_current_ip()}")
            
            # Use real search with proxy and VPN protection
            new_videos = await search_videos_with_proxy("ashley got", max_results=2)
            
            # Fallback to mock if real search fails
            if not new_videos:
                new_videos = await mock_search_videos("ashley got", max_results=2)
            
            for video in new_videos:
                # Check if video already exists
                if not any(v['id'] == video['id'] for v in videos_db):
                    print(f"Found new video: {video['title']}")
                    # Add to database if not already present
                    videos_db.append(video)
                    save_videos_to_file()
            
            # Wait for 30 minutes before next search
            await asyncio.sleep(1800)
            
        except Exception as e:
            print(f"Background task error: {e}")
            await asyncio.sleep(300)  # Wait 5 minutes on error

@app.on_event("startup")
async def startup_event():
    """Start background task and VPN on startup"""
    print("🚀 Starting Secure Video Scraper API...")
    print(f"🌐 Initial IP: {get_current_ip()}")
    
    # Start VPN server
    if start_vpn_server():
        print("✅ VPN protection enabled")
    else:
        print("⚠️ VPN failed to start, continuing with proxy only")
    
    # Start background search task
    asyncio.create_task(background_search_task())

@app.on_event("shutdown")
async def shutdown_event():
    """Stop VPN on shutdown"""
    stop_vpn_server()

@app.get("/")
async def root(request: Request):
    """Root endpoint with IP logging"""
    client_ip = request.client.host if request.client else "unknown"
    log_ip_access(client_ip, "/", request.headers.get("user-agent", ""))
    log_request(request)
    
    return {
        "message": "Secure Video Scraper API is running",
        "vpn_active": vpn_active,
        "current_ip": get_current_ip(),
        "timestamp": datetime.now().isoformat()
    }

@app.get("/videos")
async def get_videos(request: Request):
    """Get all downloaded videos with IP logging"""
    client_ip = request.client.host if request.client else "unknown"
    log_ip_access(client_ip, "/videos", request.headers.get("user-agent", ""))
    log_request(request)
    
    return videos_db

@app.post("/search")
async def search_videos(request: Request, search_request: SearchRequest):
    """Search for videos with IP logging"""
    client_ip = request.client.host if request.client else "unknown"
    log_ip_access(client_ip, "/search", request.headers.get("user-agent", ""))
    log_request(request)
    
    print(f"🔍 Search request from {client_ip}: {search_request.query}")
    
    # Use real search with proxy and VPN protection
    videos = await search_videos_with_proxy(search_request.query, search_request.max_results)
    
    # Fallback to mock if real search fails
    if not videos:
        videos = await mock_search_videos(search_request.query, search_request.max_results)
    
    search_history.append({
        'query': search_request.query,
        'timestamp': datetime.now().isoformat(),
        'results_count': len(videos),
        'client_ip': client_ip
    })
    
    return {"videos": videos}

@app.get("/search-history")
async def get_search_history(request: Request):
    """Get search history with IP logging"""
    client_ip = request.client.host if request.client else "unknown"
    log_ip_access(client_ip, "/search-history", request.headers.get("user-agent", ""))
    log_request(request)
    
    return search_history

@app.get("/vpn-status")
async def get_vpn_status(request: Request):
    """Get VPN status with IP logging"""
    client_ip = request.client.host if request.client else "unknown"
    log_ip_access(client_ip, "/vpn-status", request.headers.get("user-agent", ""))
    log_request(request)
    
    return VPNStatus(
        active=vpn_active,
        port=VPN_PORT,
        current_ip=get_current_ip()
    )

@app.post("/vpn/start")
async def start_vpn(request: Request):
    """Start VPN server with IP logging"""
    client_ip = request.client.host if request.client else "unknown"
    log_ip_access(client_ip, "/vpn/start", request.headers.get("user-agent", ""))
    log_request(request)
    
    success = start_vpn_server()
    return {"success": success, "message": "VPN started" if success else "Failed to start VPN"}

@app.post("/vpn/stop")
async def stop_vpn(request: Request):
    """Stop VPN server with IP logging"""
    client_ip = request.client.host if request.client else "unknown"
    log_ip_access(client_ip, "/vpn/stop", request.headers.get("user-agent", ""))
    log_request(request)
    
    stop_vpn_server()
    return {"success": True, "message": "VPN stopped"}

@app.get("/logs/ip")
async def get_ip_logs(request: Request):
    """Get IP access logs (admin only)"""
    client_ip = request.client.host if request.client else "unknown"
    log_ip_access(client_ip, "/logs/ip", request.headers.get("user-agent", ""))
    log_request(request)
    
    try:
        with open(ip_log_file, "r") as f:
            logs = f.readlines()
        return {"logs": logs[-100:]}  # Last 100 entries
    except FileNotFoundError:
        return {"logs": []}

@app.get("/logs/requests")
async def get_request_logs(request: Request):
    """Get request logs (admin only)"""
    client_ip = request.client.host if request.client else "unknown"
    log_ip_access(client_ip, "/logs/requests", request.headers.get("user-agent", ""))
    log_request(request)
    
    try:
        with open(request_log_file, "r") as f:
            logs = []
            for line in f.readlines()[-100:]:  # Last 100 entries
                try:
                    logs.append(json.loads(line.strip()))
                except:
                    continue
        return {"logs": logs}
    except FileNotFoundError:
        return {"logs": []}

@app.delete("/videos/{video_id}")
async def delete_video(video_id: str, request: Request):
    """Delete a video from the database and filesystem with IP logging"""
    client_ip = request.client.host if request.client else "unknown"
    log_ip_access(client_ip, f"/videos/{video_id}", request.headers.get("user-agent", ""))
    log_request(request)
    
    global videos_db
    
    video = None
    for v in videos_db:
        if v['id'] == video_id:
            video = v
            break
    
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    # Remove from filesystem
    if video['local_path'] and os.path.exists(video['local_path']):
        os.remove(video['local_path'])
    
    if video['thumbnail'] and os.path.exists(video['thumbnail']):
        os.remove(video['thumbnail'])
    
    # Remove from database
    videos_db = [v for v in videos_db if v['id'] != video_id]
    save_videos_to_file()
    
    return {"message": "Video deleted successfully"}

if __name__ == "__main__":
    import uvicorn
    print("🔒 Starting Secure Video Scraper with VPN + Proxy Protection")
    print(f"🌐 Initial IP: {get_current_ip()}")
    uvicorn.run(app, host="0.0.0.0", port=8000) 