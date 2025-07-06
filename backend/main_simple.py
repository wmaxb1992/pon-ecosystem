from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional
import asyncio
import json
import os
from datetime import datetime
import httpx

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
    """Start background task on startup"""
    asyncio.create_task(background_search_task())

@app.get("/")
async def root():
    return {"message": "Video Scraper API is running (Mock Mode)"}

@app.get("/videos")
async def get_videos():
    """Get all downloaded videos"""
    return videos_db

@app.post("/search")
async def search_videos(request: SearchRequest):
    """Search for videos"""
    videos = await mock_search_videos(request.query, request.max_results)
    search_history.append({
        'query': request.query,
        'timestamp': datetime.now().isoformat(),
        'results_count': len(videos)
    })
    return {"videos": videos}

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