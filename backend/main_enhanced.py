from fastapi import FastAPI, HTTPException, Request, Form, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional, Dict
import asyncio
import json
import os
from datetime import datetime
import httpx
import yt_dlp
from database import db, favorites_manager, sites_manager
import threading
import time
import sqlite3
import requests
from urllib.parse import urlparse

app = FastAPI(title="Enhanced Video Scraper API", version="2.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
os.makedirs("videos", exist_ok=True)
os.makedirs("thumbnails", exist_ok=True)
app.mount("/videos", StaticFiles(directory="videos"), name="videos")
app.mount("/thumbnails", StaticFiles(directory="thumbnails"), name="thumbnails")

# Data models
class VideoInfo(BaseModel):
    id: str
    title: str
    url: str
    thumbnail: Optional[str] = None
    duration: Optional[str] = None
    upload_date: Optional[str] = None
    description: Optional[str] = None
    source_site: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = []
    preview_url: Optional[str] = None
    embed_url: Optional[str] = None

class URLParseRequest(BaseModel):
    url: str

class PlaylistVideoAdd(BaseModel):
    video_id: str
    video_title: str
    video_url: str
    video_thumbnail: Optional[str] = None
    video_duration: Optional[str] = None
    video_source: Optional[str] = None
    video_category: Optional[str] = None

class PlaylistCreate(BaseModel):
    name: str
    description: Optional[str] = ""

class SearchRequest(BaseModel):
    query: str
    category: Optional[str] = None
    max_results: int = 50

class SiteAddRequest(BaseModel):
    name: str
    url: str
    category: str
    description: Optional[str] = ""

class KeywordAddRequest(BaseModel):
    keyword: str
    category: Optional[str] = None
    priority: int = 1

# Global variables
crawling_active = False
crawl_thread = None

def get_proxy_url():
    """Get a fresh proxy URL"""
    try:
        from free_proxy import FreeProxy
        proxy = FreeProxy(rand=True, timeout=5).get()
        if not proxy.startswith('http'):
            proxy = 'http://' + proxy
        return proxy
    except Exception as e:
        print(f"Failed to get proxy: {e}")
        return None

async def fetch_with_proxy(url: str, **kwargs):
    """Make HTTP request with proxy"""
    proxy_url = get_proxy_url()
    async with httpx.AsyncClient(proxies=proxy_url) as client:
        return await client.get(url, **kwargs)

async def search_videos_with_proxy(query: str, max_results: int = 10) -> List[dict]:
    """Search for videos using yt-dlp with proxy"""
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
                            'source_site': 'YouTube',
                            'category': 'Entertainment',
                            'tags': entry.get('tags', [])
                        }
                        videos.append(video_info)
            
            return videos
    except Exception as e:
        print(f"Error searching videos: {e}")
        return []

async def crawl_video_sites():
    """Background task to crawl video sites"""
    global crawling_active
    
    while crawling_active:
        try:
            print("🕷️ Starting video site crawl...")
            
            # Get all active video sites
            sites = sites_manager.get_video_sites()
            
            for site in sites:
                try:
                    print(f"Crawling {site['name']}...")
                    
                    # This is a simplified crawl - in a real implementation,
                    # you'd use site-specific patterns to extract videos
                    # For now, we'll just search for popular keywords
                    
                    keywords = sites_manager.get_search_keywords()
                    for keyword_data in keywords[:5]:  # Limit to 5 keywords per site
                        query = keyword_data['keyword']
                        
                        # Search for videos on this site
                        videos = await search_videos_with_proxy(query, max_results=5)
                        
                        # Store in database
                        for video in videos:
                            video['source_site'] = site['name']
                            video['category'] = keyword_data.get('category', 'Entertainment')
                            
                            # Add to crawled videos
                            conn = sqlite3.connect(db.sites_db)
                            cursor = conn.cursor()
                            
                            cursor.execute('''
                                INSERT OR IGNORE INTO crawled_videos 
                                (site_id, video_id, title, url, thumbnail, duration, upload_date, description, category, tags)
                                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                            ''', (
                                site['id'],
                                video['id'],
                                video['title'],
                                video['url'],
                                video['thumbnail'],
                                video['duration'],
                                video['upload_date'],
                                video['description'],
                                video['category'],
                                json.dumps(video['tags'])
                            ))
                            
                            conn.commit()
                            conn.close()
                    
                    # Update last crawled timestamp
                    conn = sqlite3.connect(db.sites_db)
                    cursor = conn.cursor()
                    cursor.execute('''
                        UPDATE video_sites SET last_crawled = CURRENT_TIMESTAMP WHERE id = ?
                    ''', (site['id'],))
                    conn.commit()
                    conn.close()
                    
                except Exception as e:
                    print(f"Error crawling {site['name']}: {e}")
                    continue
            
            print("✅ Crawl completed")
            
            # Wait for next crawl (1 hour)
            await asyncio.sleep(3600)
            
        except Exception as e:
            print(f"Crawl error: {e}")
            await asyncio.sleep(300)  # Wait 5 minutes on error

def start_crawl_thread():
    """Start crawling in a separate thread"""
    global crawling_active, crawl_thread
    
    if not crawling_active:
        crawling_active = True
        crawl_thread = threading.Thread(target=lambda: asyncio.run(crawl_video_sites()))
        crawl_thread.daemon = True
        crawl_thread.start()
        print("🕷️ Crawl thread started")

def stop_crawl_thread():
    """Stop crawling thread"""
    global crawling_active
    crawling_active = False
    print("🛑 Crawl thread stopped")

@app.on_event("startup")
async def startup_event():
    """Start background tasks on startup"""
    print("🚀 Starting Enhanced Video Scraper API...")
    print(f"🌐 Current IP: {get_current_ip()}")
    
    # Start crawling thread
    start_crawl_thread()

@app.on_event("shutdown")
async def shutdown_event():
    """Stop background tasks on shutdown"""
    stop_crawl_thread()

def get_current_ip():
    """Get current public IP address"""
    try:
        response = requests.get("https://api.ipify.org", timeout=5)
        return response.text.strip()
    except:
        return "unknown"

def log_request(request: Request, response_status: int = 200):
    """Log request information"""
    client_ip = request.client.host if request.client else "unknown"
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    print(f"🔍 [{timestamp}] {client_ip} - {request.method} {request.url.path} - {response_status}")

# Root endpoint
@app.get("/")
async def root(request: Request):
    """Root endpoint"""
    log_request(request)
    
    return {
        "message": "Enhanced Video Scraper API",
        "version": "2.0.0",
        "features": [
            "Favorites & Playlists",
            "Multi-site Video Crawling",
            "Category-based Search",
            "Thumbnail Management"
        ],
        "current_ip": get_current_ip()
    }

# Playlist endpoints
@app.post("/playlists")
async def create_playlist(request: Request, playlist: PlaylistCreate):
    """Create a new playlist"""
    log_request(request)
    
    playlist_id = favorites_manager.create_playlist(playlist.name, playlist.description)
    return {"id": playlist_id, "name": playlist.name, "message": "Playlist created successfully"}

@app.get("/playlists")
async def get_playlists(request: Request):
    """Get all playlists"""
    log_request(request)
    
    playlists = favorites_manager.get_playlists()
    return playlists

@app.get("/playlists/{playlist_id}/videos")
async def get_playlist_videos(request: Request, playlist_id: int):
    """Get videos in a playlist"""
    log_request(request)
    
    videos = favorites_manager.get_playlist_videos(playlist_id)
    return videos

@app.post("/playlists/{playlist_id}/videos")
async def add_video_to_playlist(request: Request, playlist_id: int, video: VideoInfo):
    """Add a video to a playlist"""
    log_request(request)
    
    success = favorites_manager.add_video_to_playlist(playlist_id, video.dict())
    if success:
        return {"message": "Video added to playlist successfully"}
    else:
        raise HTTPException(status_code=400, detail="Failed to add video to playlist")

# Video sites endpoints
@app.post("/sites")
async def add_video_site(request: Request, site: SiteAddRequest):
    """Add a new video site for crawling"""
    log_request(request)
    
    site_id = sites_manager.add_video_site(site.name, site.url, site.category, site.description)
    return {"id": site_id, "name": site.name, "message": "Video site added successfully"}

@app.get("/sites")
async def get_video_sites(request: Request, category: Optional[str] = None):
    """Get video sites, optionally filtered by category"""
    log_request(request)
    
    sites = sites_manager.get_video_sites(category)
    return sites

@app.get("/categories")
async def get_categories(request: Request):
    """Get all site categories"""
    log_request(request)
    
    categories = sites_manager.get_categories()
    return categories

# Search endpoints
@app.post("/search")
async def search_videos(request: Request, search_request: SearchRequest):
    """Search videos across all sites"""
    log_request(request)
    
    print(f"🔍 Search request: {search_request.query} (category: {search_request.category})")
    
    # Search in crawled videos first
    videos = sites_manager.search_videos(
        search_request.query, 
        search_request.category, 
        search_request.max_results
    )
    
    # If not enough results, search YouTube as fallback
    if len(videos) < search_request.max_results // 2:
        youtube_videos = await search_videos_with_proxy(
            search_request.query, 
            search_request.max_results - len(videos)
        )
        videos.extend(youtube_videos)
    
    return {"videos": videos, "total": len(videos)}

@app.get("/search/keywords")
async def get_search_keywords(request: Request, category: Optional[str] = None):
    """Get search keywords"""
    log_request(request)
    
    keywords = sites_manager.get_search_keywords(category)
    return keywords

@app.post("/search/keywords")
async def add_search_keyword(request: Request, keyword: KeywordAddRequest):
    """Add a new search keyword"""
    log_request(request)
    
    keyword_id = sites_manager.add_search_keyword(keyword.keyword, keyword.category, keyword.priority)
    return {"id": keyword_id, "keyword": keyword.keyword, "message": "Keyword added successfully"}

# Manual video addition
@app.post("/videos/manual")
async def add_manual_video(request: Request, video: VideoInfo):
    """Manually add a video to the database"""
    log_request(request)
    
    # Add to favorites database
    conn = sqlite3.connect(db.favorites_db)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT OR IGNORE INTO videos 
        (video_id, title, url, thumbnail, duration, upload_date, description, source_site, category, tags)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    ''', (
        video.id,
        video.title,
        video.url,
        video.thumbnail,
        video.duration,
        video.upload_date,
        video.description,
        video.source_site,
        video.category,
        json.dumps(video.tags)
    ))
    
    conn.commit()
    conn.close()
    
    return {"message": "Video added successfully"}

@app.post("/test-parse")
async def test_parse():
    return {"message": "Test endpoint works"}

@app.post("/parse-video-url")
async def parse_video_url(request: Request, url_request: URLParseRequest):
    """Parse a video URL and extract video information"""
    log_request(request)
    
    try:
        proxy_url = get_proxy_url()
        
        ydl_opts = {
            'quiet': True,
            'no_warnings': True,
            'extract_flat': False,
        }
        
        if proxy_url:
            ydl_opts['proxy'] = proxy_url
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url_request.url, download=False)
            
            # Generate thumbnail filename
            thumbnail_filename = f"thumb_{info.get('id', 'unknown')}.jpg"
            thumbnail_path = f"thumbnails/{thumbnail_filename}"
            
            # Download thumbnail if available
            if info.get('thumbnail'):
                try:
                    response = requests.get(info['thumbnail'])
                    if response.status_code == 200:
                        with open(thumbnail_path, 'wb') as f:
                            f.write(response.content)
                except:
                    thumbnail_path = None
            
            video_info = {
                'id': info.get('id', ''),
                'title': info.get('title', ''),
                'url': url_request.url,
                'thumbnail': f"/thumbnails/{thumbnail_filename}" if thumbnail_path else None,
                'duration': str(info.get('duration', 0)),
                'upload_date': info.get('upload_date', ''),
                'description': info.get('description', ''),
                'source_site': info.get('extractor', 'Unknown'),
                'category': 'Entertainment',
                'tags': info.get('tags', []),
                'preview_url': info.get('thumbnail'),
                'embed_url': generate_embed_url(url_request.url, info.get('extractor', ''))
            }
            
            return {"video": video_info}
    except Exception as e:
        # Fallback for URLs that yt-dlp can't parse
        try:
            video_info = parse_url_fallback(url_request.url)
            if video_info:
                return {"video": video_info}
        except Exception as fallback_error:
            print(f"Fallback parsing also failed: {fallback_error}")
        
        raise HTTPException(status_code=500, detail=f"Error parsing URL: {str(e)}")

def parse_url_fallback(url: str) -> dict:
    """Fallback URL parsing for sites not supported by yt-dlp"""
    try:
        # Handle xhamster URLs
        if 'xhamster.com' in url:
            video_id = url.split('/')[-1].split('#')[0]
            title = url.split('/')[-1].replace('-', ' ').title()
            
            return {
                'id': video_id,
                'title': title,
                'url': url,
                'thumbnail': None,
                'duration': '0',
                'upload_date': '',
                'description': f'Video from XHamster: {title}',
                'source_site': 'XHamster',
                'category': 'Entertainment',
                'tags': [],
                'preview_url': None,
                'embed_url': f"https://xhamster.com/embed/{video_id}"
            }
        
        # Handle pornhub URLs
        elif 'pornhub.com' in url:
            video_id = url.split('viewkey=')[-1] if 'viewkey=' in url else url.split('/')[-1]
            title = url.split('/')[-1].replace('-', ' ').title()
            
            return {
                'id': video_id,
                'title': title,
                'url': url,
                'thumbnail': None,
                'duration': '0',
                'upload_date': '',
                'description': f'Video from Pornhub: {title}',
                'source_site': 'Pornhub',
                'category': 'Entertainment',
                'tags': [],
                'preview_url': None,
                'embed_url': f"https://www.pornhub.com/embed/{video_id}"
            }
        
        # Generic fallback
        else:
            video_id = url.split('/')[-1].split('#')[0]
            title = url.split('/')[-1].replace('-', ' ').title()
            
            return {
                'id': video_id,
                'title': title,
                'url': url,
                'thumbnail': None,
                'duration': '0',
                'upload_date': '',
                'description': f'Video from {urlparse(url).netloc}: {title}',
                'source_site': urlparse(url).netloc,
                'category': 'Entertainment',
                'tags': [],
                'preview_url': None,
                'embed_url': url
            }
    except Exception as e:
        print(f"Fallback parsing error: {e}")
        return None

def generate_embed_url(url: str, extractor: str) -> str:
    """Generate embed URL for different video platforms"""
    if 'youtube' in extractor.lower() or 'youtu.be' in url:
        video_id = url.split('v=')[-1] if 'v=' in url else url.split('/')[-1]
        return f"https://www.youtube.com/embed/{video_id}"
    elif 'vimeo' in extractor.lower():
        video_id = url.split('/')[-1]
        return f"https://player.vimeo.com/video/{video_id}"
    elif 'dailymotion' in extractor.lower():
        video_id = url.split('/')[-1]
        return f"https://www.dailymotion.com/embed/video/{video_id}"
    elif 'xhamster' in url.lower():
        # Extract video ID from xhamster URL
        video_id = url.split('/')[-1].split('#')[0]
        return f"https://xhamster.com/embed/{video_id}"
    elif 'pornhub' in url.lower():
        # Extract video ID from pornhub URL
        video_id = url.split('viewkey=')[-1] if 'viewkey=' in url else url.split('/')[-1]
        return f"https://www.pornhub.com/embed/{video_id}"
    else:
        return url

@app.post("/playlists/{playlist_id}/videos/add")
async def add_video_to_playlist_simple(request: Request, playlist_id: int, video: PlaylistVideoAdd):
    """Add a video to a playlist with simplified data"""
    log_request(request)
    
    try:
        conn = sqlite3.connect(db.favorites_db)
        cursor = conn.cursor()
        
        # Check if playlist exists
        cursor.execute('SELECT id FROM playlists WHERE id = ?', (playlist_id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Playlist not found")
        
        # Add video to playlist
        cursor.execute('''
            INSERT OR IGNORE INTO playlist_videos 
            (playlist_id, video_id, title, url, thumbnail, duration, source_site, category, added_date)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (
            playlist_id,
            video.video_id,
            video.video_title,
            video.video_url,
            video.video_thumbnail,
            video.video_duration,
            video.video_source,
            video.video_category
        ))
        
        conn.commit()
        conn.close()
        
        return {"message": "Video added to playlist successfully"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error adding video to playlist: {str(e)}")

@app.delete("/playlists/{playlist_id}/videos/{video_id}")
async def remove_video_from_playlist(request: Request, playlist_id: int, video_id: str):
    """Remove a video from a playlist"""
    log_request(request)
    
    try:
        conn = sqlite3.connect(db.favorites_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            DELETE FROM playlist_videos 
            WHERE playlist_id = ? AND video_id = ?
        ''', (playlist_id, video_id))
        
        conn.commit()
        conn.close()
        
        return {"message": "Video removed from playlist successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error removing video from playlist: {str(e)}")

@app.get("/videos/thumbnails/{video_id}")
async def get_video_thumbnail(request: Request, video_id: str):
    """Get video thumbnail with hover preview"""
    log_request(request)
    
    try:
        conn = sqlite3.connect(db.sites_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT thumbnail, title, duration, source_site 
            FROM crawled_videos 
            WHERE video_id = ?
        ''', (video_id,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            thumbnail, title, duration, source_site = result
            return {
                "thumbnail": thumbnail,
                "title": title,
                "duration": duration,
                "source_site": source_site,
                "preview_url": thumbnail  # For hover preview
            }
        else:
            raise HTTPException(status_code=404, detail="Video not found")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error getting thumbnail: {str(e)}")

@app.get("/search/aggregated")
async def search_aggregated_videos(request: Request, query: str, category: Optional[str] = None, max_results: int = 50):
    """Search across multiple sites and aggregate results"""
    log_request(request)
    
    try:
        # Get all active video sites
        sites = sites_manager.get_video_sites()
        
        all_videos = []
        
        for site in sites:
            try:
                # Search on this specific site
                site_videos = await search_videos_with_proxy(f"site:{site['url']} {query}", max_results=10)
                
                for video in site_videos:
                    video['source_site'] = site['name']
                    video['site_url'] = site['url']
                    all_videos.append(video)
                    
            except Exception as e:
                print(f"Error searching {site['name']}: {e}")
                continue
        
        # Filter by category if specified
        if category:
            all_videos = [v for v in all_videos if v.get('category', '').lower() == category.lower()]
        
        # Sort by relevance and limit results
        all_videos = all_videos[:max_results]
        
        return {
            "videos": all_videos,
            "total": len(all_videos),
            "sites_searched": len(sites)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error in aggregated search: {str(e)}")

# Crawl control endpoints
@app.post("/crawl/start")
async def start_crawling(request: Request):
    """Start video site crawling"""
    log_request(request)
    
    start_crawl_thread()
    return {"message": "Crawling started"}

@app.post("/crawl/stop")
async def stop_crawling(request: Request):
    """Stop video site crawling"""
    log_request(request)
    
    stop_crawl_thread()
    return {"message": "Crawling stopped"}

@app.get("/crawl/status")
async def get_crawl_status(request: Request):
    """Get crawling status"""
    log_request(request)
    
    return {
        "active": crawling_active,
        "thread_alive": crawl_thread.is_alive() if crawl_thread else False
    }

# Statistics endpoints
@app.get("/stats")
async def get_statistics(request: Request):
    """Get database statistics"""
    log_request(request)
    
    # Favorites stats
    conn = sqlite3.connect(db.favorites_db)
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM playlists')
    playlist_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM videos')
    video_count = cursor.fetchone()[0]
    
    conn.close()
    
    # Sites stats
    conn = sqlite3.connect(db.sites_db)
    cursor = conn.cursor()
    
    cursor.execute('SELECT COUNT(*) FROM video_sites WHERE is_active = 1')
    site_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM crawled_videos')
    crawled_count = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM search_keywords')
    keyword_count = cursor.fetchone()[0]
    
    conn.close()
    
    return {
        "playlists": playlist_count,
        "favorite_videos": video_count,
        "active_sites": site_count,
        "crawled_videos": crawled_count,
        "search_keywords": keyword_count,
        "crawling_active": crawling_active
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 Starting Enhanced Video Scraper with Database Support")
    print(f"🌐 Initial IP: {get_current_ip()}")
    uvicorn.run(app, host="0.0.0.0", port=8000) 