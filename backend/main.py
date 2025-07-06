from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
import yt_dlp
import asyncio
import json
import os
from datetime import datetime
import httpx
from bs4 import BeautifulSoup
import re
from free_proxy import FreeProxy
import requests

app = FastAPI(title="Video Scraper API", version="1.0.0")

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
# Example usage for httpx:
async def fetch_with_proxy(url: str, **kwargs):
    proxy_url = get_proxy_url()
    async with httpx.AsyncClient(proxies=proxy_url) as client:
        response = await client.get(url, **kwargs)
        return response

# Example usage for requests:
def fetch_with_proxy_requests(url: str, **kwargs):
    proxies = get_proxy_dict()
    response = requests.get(url, proxies=proxies, **kwargs)
    return response

async def search_youtube_videos(query: str, max_results: int = 10) -> List[dict]:
    """Search for videos using yt-dlp with a proxy"""
    proxy_url = get_proxy_url()
    ydl_opts = {
        'quiet': True,
        'no_warnings': True,
        'extract_flat': True,
        'default_search': 'ytsearch',
        'max_downloads': max_results,
    }
    if proxy_url:
        ydl_opts['proxy'] = proxy_url
    
    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
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
                            'duration': entry.get('duration', ''),
                            'upload_date': entry.get('upload_date', ''),
                            'description': entry.get('description', ''),
                            'local_path': None
                        }
                        videos.append(video_info)
            
            return videos
    except Exception as e:
        print(f"Error searching videos: {e}")
        return []

async def download_video(video_info: dict):
    """Download a video using yt-dlp with a proxy"""
    proxy_url = get_proxy_url()
    try:
        ydl_opts = {
            'format': 'best[height<=720]',
            'outtmpl': f'videos/%(id)s.%(ext)s',
            'writethumbnail': True,
        }
        if proxy_url:
            ydl_opts['proxy'] = proxy_url
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_info['url'], download=True)
            video_info['local_path'] = f"videos/{info['id']}.{info['ext']}"
            video_info['thumbnail'] = f"videos/{info['id']}.webp"
            
            # Add to database if not already present
            if not any(v['id'] == video_info['id'] for v in videos_db):
                videos_db.append(video_info)
                save_videos_to_file()
                
    except Exception as e:
        print(f"Error downloading video {video_info['title']}: {e}")

async def background_search_task():
    """Background task to continuously search for 'ashley got' videos"""
    while True:
        try:
            print("Background task: Searching for 'ashley got' videos...")
            new_videos = await search_youtube_videos("ashley got", max_results=5)
            
            for video in new_videos:
                # Check if video already exists
                if not any(v['id'] == video['id'] for v in videos_db):
                    print(f"Found new video: {video['title']}")
                    await download_video(video)
            
            # Wait for 30 minutes before next search
            await asyncio.sleep(1800)
            
        except Exception as e:
            print(f"Background task error: {e}")
            await asyncio.sleep(300)  # Wait 5 minutes on error

@app.on_event("startup")
async def startup_event():
    """Start background task on startup"""
    asyncio.create_task(background_search_task())

@app.get("/")
async def root():
    return {"message": "Video Scraper API is running"}

@app.get("/videos", response_model=List[VideoInfo])
async def get_videos():
    """Get all downloaded videos"""
    return videos_db

@app.post("/search")
async def search_videos(request: SearchRequest):
    """Search for videos"""
    videos = await search_youtube_videos(request.query, request.max_results)
    search_history.append({
        'query': request.query,
        'timestamp': datetime.now().isoformat(),
        'results_count': len(videos)
    })
    return {"videos": videos}

@app.post("/download/{video_id}")
async def download_video_endpoint(video_id: str):
    """Download a specific video"""
    # Find video in search results or database
    video = None
    for v in videos_db:
        if v['id'] == video_id:
            video = v
            break
    
    if not video:
        raise HTTPException(status_code=404, detail="Video not found")
    
    if video['local_path'] and os.path.exists(video['local_path']):
        return {"message": "Video already downloaded", "video": video}
    
    await download_video(video)
    return {"message": "Video download started", "video": video}

@app.get("/search-history")
async def get_search_history():
    """Get search history"""
    return search_history

@app.delete("/videos/{video_id}")
async def delete_video(video_id: str):
    """Delete a video from the database and filesystem"""
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
    uvicorn.run(app, host="0.0.0.0", port=8000) 