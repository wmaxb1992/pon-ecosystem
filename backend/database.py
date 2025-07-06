import sqlite3
import json
import os
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import hashlib
import requests
from urllib.parse import urlparse, urljoin
import re

class VideoDatabase:
    def __init__(self):
        self.favorites_db = "favorites.db"
        self.sites_db = "video_sites.db"
        self.init_databases()
    
    def init_databases(self):
        """Initialize both databases with proper schemas"""
        self.init_favorites_db()
        self.init_sites_db()
    
    def init_favorites_db(self):
        """Initialize favorites database with playlists and videos"""
        conn = sqlite3.connect(self.favorites_db)
        cursor = conn.cursor()
        
        # Playlists table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS playlists (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Videos table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS videos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_id TEXT NOT NULL,
                title TEXT NOT NULL,
                url TEXT NOT NULL,
                thumbnail TEXT,
                duration TEXT,
                upload_date TEXT,
                description TEXT,
                source_site TEXT,
                category TEXT,
                tags TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Playlist videos junction table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS playlist_videos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                playlist_id INTEGER,
                video_id INTEGER,
                position INTEGER,
                added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (playlist_id) REFERENCES playlists (id),
                FOREIGN KEY (video_id) REFERENCES videos (id),
                UNIQUE(playlist_id, video_id)
            )
        ''')
        
        # Video tags table for better search
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS video_tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_id INTEGER,
                tag TEXT,
                FOREIGN KEY (video_id) REFERENCES videos (id)
            )
        ''')
        
        # Create indexes for better performance
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_videos_title ON videos (title)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_videos_category ON videos (category)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_videos_source ON videos (source_site)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_video_tags_tag ON video_tags (tag)')
        
        conn.commit()
        conn.close()
    
    def init_sites_db(self):
        """Initialize video sites database for crawling and indexing"""
        conn = sqlite3.connect(self.sites_db)
        cursor = conn.cursor()
        
        # Video sites table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS video_sites (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                url TEXT NOT NULL UNIQUE,
                category TEXT,
                description TEXT,
                search_url_pattern TEXT,
                video_url_pattern TEXT,
                thumbnail_pattern TEXT,
                title_pattern TEXT,
                duration_pattern TEXT,
                description_pattern TEXT,
                is_active BOOLEAN DEFAULT 1,
                last_crawled TIMESTAMP,
                crawl_interval INTEGER DEFAULT 3600,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Crawled videos table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS crawled_videos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                site_id INTEGER,
                video_id TEXT NOT NULL,
                title TEXT NOT NULL,
                url TEXT NOT NULL UNIQUE,
                thumbnail TEXT,
                duration TEXT,
                upload_date TEXT,
                description TEXT,
                category TEXT,
                tags TEXT,
                crawl_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (site_id) REFERENCES video_sites (id)
            )
        ''')
        
        # Site categories table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS site_categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                description TEXT,
                color TEXT DEFAULT '#3B82F6'
            )
        ''')
        
        # Search keywords table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS search_keywords (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                keyword TEXT NOT NULL UNIQUE,
                category TEXT,
                priority INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_crawled_videos_title ON crawled_videos (title)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_crawled_videos_category ON crawled_videos (category)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_crawled_videos_site ON crawled_videos (site_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_video_sites_category ON video_sites (category)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_video_sites_active ON video_sites (is_active)')
        
        conn.commit()
        conn.close()
        
        # Initialize with default categories and popular sites
        self.init_default_data()
    
    def init_default_data(self):
        """Initialize with default categories and popular video sites"""
        conn = sqlite3.connect(self.sites_db)
        cursor = conn.cursor()
        
        # Default categories
        categories = [
            ('Entertainment', 'General entertainment videos', '#3B82F6'),
            ('Music', 'Music videos and audio content', '#10B981'),
            ('Gaming', 'Gaming videos and streams', '#F59E0B'),
            ('Education', 'Educational and tutorial content', '#8B5CF6'),
            ('Sports', 'Sports and fitness content', '#EF4444'),
            ('News', 'News and current events', '#6B7280'),
            ('Comedy', 'Comedy and humor content', '#F97316'),
            ('Technology', 'Tech reviews and tutorials', '#06B6D4'),
            ('Lifestyle', 'Lifestyle and vlog content', '#EC4899'),
            ('Movies', 'Movie trailers and film content', '#84CC16')
        ]
        
        for name, desc, color in categories:
            cursor.execute('''
                INSERT OR IGNORE INTO site_categories (name, description, color)
                VALUES (?, ?, ?)
            ''', (name, desc, color))
        
        # Popular video sites (sample data)
        popular_sites = [
            ('YouTube', 'https://www.youtube.com', 'Entertainment', 'https://www.youtube.com/results?search_query={query}'),
            ('Vimeo', 'https://vimeo.com', 'Entertainment', 'https://vimeo.com/search?q={query}'),
            ('Dailymotion', 'https://www.dailymotion.com', 'Entertainment', 'https://www.dailymotion.com/search/{query}'),
            ('Twitch', 'https://www.twitch.tv', 'Gaming', 'https://www.twitch.tv/search?term={query}'),
            ('TikTok', 'https://www.tiktok.com', 'Entertainment', 'https://www.tiktok.com/search?q={query}'),
            ('XHamster', 'https://xhamster.com', 'Entertainment', 'https://xhamster.com/search?q={query}'),
            ('Pornhub', 'https://pornhub.com', 'Entertainment', 'https://pornhub.com/video/search?search={query}'),
            ('RedTube', 'https://redtube.com', 'Entertainment', 'https://redtube.com/?search={query}'),
            ('YouPorn', 'https://youporn.com', 'Entertainment', 'https://www.youporn.com/search/?query={query}'),
            ('Instagram', 'https://www.instagram.com', 'Lifestyle', 'https://www.instagram.com/explore/tags/{query}/'),
            ('Reddit', 'https://www.reddit.com', 'Entertainment', 'https://www.reddit.com/search/?q={query}&restrict_sr=&t=all&sort=relevance'),
            ('Bilibili', 'https://www.bilibili.com', 'Entertainment', 'https://search.bilibili.com/all?keyword={query}'),
            ('Niconico', 'https://nicovideo.jp', 'Entertainment', 'https://nicovideo.jp/search/{query}'),
            ('Pornhub', 'https://www.pornhub.com', 'Adult', 'https://www.pornhub.com/video/search?search={query}')
        ]
        
        for name, url, category, search_pattern in popular_sites:
            cursor.execute('''
                INSERT OR IGNORE INTO video_sites 
                (name, url, category, search_url_pattern, description)
                VALUES (?, ?, ?, ?, ?)
            ''', (name, url, category, search_pattern, f'Popular {category.lower()} video site'))
        
        # Default search keywords
        default_keywords = [
            ('ashley got', 'Entertainment', 10),
            ('music', 'Music', 5),
            ('gaming', 'Gaming', 5),
            ('tutorial', 'Education', 5),
            ('news', 'News', 5),
            ('comedy', 'Comedy', 5),
            ('tech', 'Technology', 5),
            ('lifestyle', 'Lifestyle', 5),
            ('movie', 'Movies', 5),
            ('sports', 'Sports', 5)
        ]
        
        for keyword, category, priority in default_keywords:
            cursor.execute('''
                INSERT OR IGNORE INTO search_keywords (keyword, category, priority)
                VALUES (?, ?, ?)
            ''', (keyword, category, priority))
        
        conn.commit()
        conn.close()

class FavoritesManager:
    def __init__(self, db: VideoDatabase):
        self.db = db
    
    def create_playlist(self, name: str, description: str = "") -> int:
        """Create a new playlist"""
        conn = sqlite3.connect(self.db.favorites_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO playlists (name, description)
            VALUES (?, ?)
        ''', (name, description))
        
        playlist_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return playlist_id
    
    def get_playlists(self) -> List[Dict]:
        """Get all playlists with video counts"""
        conn = sqlite3.connect(self.db.favorites_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT p.*, COUNT(pv.video_id) as video_count
            FROM playlists p
            LEFT JOIN playlist_videos pv ON p.id = pv.playlist_id
            GROUP BY p.id
            ORDER BY p.updated_at DESC
        ''')
        
        playlists = []
        for row in cursor.fetchall():
            playlists.append({
                'id': row[0],
                'name': row[1],
                'description': row[2],
                'created_at': row[3],
                'updated_at': row[4],
                'video_count': row[5]
            })
        
        conn.close()
        return playlists
    
    def add_video_to_playlist(self, playlist_id: int, video_data: Dict) -> bool:
        """Add a video to a playlist"""
        conn = sqlite3.connect(self.db.favorites_db)
        cursor = conn.cursor()
        
        try:
            # First, add or get video
            cursor.execute('''
                INSERT OR IGNORE INTO videos 
                (video_id, title, url, thumbnail, duration, upload_date, description, source_site, category, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                video_data.get('id', ''),
                video_data.get('title', ''),
                video_data.get('url', ''),
                video_data.get('thumbnail', ''),
                video_data.get('duration', ''),
                video_data.get('upload_date', ''),
                video_data.get('description', ''),
                video_data.get('source_site', ''),
                video_data.get('category', ''),
                json.dumps(video_data.get('tags', []))
            ))
            
            # Get video ID
            cursor.execute('SELECT id FROM videos WHERE video_id = ?', (video_data.get('id', ''),))
            video_row = cursor.fetchone()
            if video_row:
                video_id = video_row[0]
                
                # Add to playlist
                cursor.execute('''
                    INSERT OR IGNORE INTO playlist_videos (playlist_id, video_id, position)
                    VALUES (?, ?, (SELECT COALESCE(MAX(position), 0) + 1 FROM playlist_videos WHERE playlist_id = ?))
                ''', (playlist_id, video_id, playlist_id))
                
                # Update playlist timestamp
                cursor.execute('''
                    UPDATE playlists SET updated_at = CURRENT_TIMESTAMP WHERE id = ?
                ''', (playlist_id,))
                
                conn.commit()
                return True
        
        except Exception as e:
            print(f"Error adding video to playlist: {e}")
            return False
        finally:
            conn.close()
    
    def get_playlist_videos(self, playlist_id: int) -> List[Dict]:
        """Get all videos in a playlist"""
        conn = sqlite3.connect(self.db.favorites_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT v.*, pv.position
            FROM videos v
            JOIN playlist_videos pv ON v.id = pv.video_id
            WHERE pv.playlist_id = ?
            ORDER BY pv.position
        ''', (playlist_id,))
        
        videos = []
        for row in cursor.fetchall():
            videos.append({
                'id': row[0],
                'video_id': row[1],
                'title': row[2],
                'url': row[3],
                'thumbnail': row[4],
                'duration': row[5],
                'upload_date': row[6],
                'description': row[7],
                'source_site': row[8],
                'category': row[9],
                'tags': json.loads(row[10]) if row[10] else [],
                'created_at': row[11],
                'position': row[12]
            })
        
        conn.close()
        return videos

class SitesManager:
    def __init__(self, db: VideoDatabase):
        self.db = db
    
    def add_video_site(self, name: str, url: str, category: str, description: str = "") -> int:
        """Add a new video site for crawling"""
        conn = sqlite3.connect(self.db.sites_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO video_sites (name, url, category, description)
            VALUES (?, ?, ?, ?)
        ''', (name, url, category, description))
        
        site_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return site_id
    
    def get_video_sites(self, category: str = None) -> List[Dict]:
        """Get all video sites, optionally filtered by category"""
        conn = sqlite3.connect(self.db.sites_db)
        cursor = conn.cursor()
        
        if category:
            cursor.execute('''
                SELECT * FROM video_sites 
                WHERE category = ? AND is_active = 1
                ORDER BY name
            ''', (category,))
        else:
            cursor.execute('''
                SELECT * FROM video_sites 
                WHERE is_active = 1
                ORDER BY category, name
            ''')
        
        sites = []
        for row in cursor.fetchall():
            sites.append({
                'id': row[0],
                'name': row[1],
                'url': row[2],
                'category': row[3],
                'description': row[4],
                'search_url_pattern': row[5],
                'video_url_pattern': row[6],
                'thumbnail_pattern': row[7],
                'title_pattern': row[8],
                'duration_pattern': row[9],
                'description_pattern': row[10],
                'is_active': row[11],
                'last_crawled': row[12],
                'crawl_interval': row[13],
                'created_at': row[14],
                'updated_at': row[15]
            })
        
        conn.close()
        return sites
    
    def get_categories(self) -> List[Dict]:
        """Get all site categories"""
        conn = sqlite3.connect(self.db.sites_db)
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM site_categories ORDER BY name')
        
        categories = []
        for row in cursor.fetchall():
            categories.append({
                'id': row[0],
                'name': row[1],
                'description': row[2],
                'color': row[3]
            })
        
        conn.close()
        return categories
    
    def search_videos(self, query: str, category: str = None, limit: int = 50) -> List[Dict]:
        """Search videos across all crawled sites"""
        conn = sqlite3.connect(self.db.sites_db)
        cursor = conn.cursor()
        
        if category:
            cursor.execute('''
                SELECT cv.*, vs.name as site_name
                FROM crawled_videos cv
                JOIN video_sites vs ON cv.site_id = vs.id
                WHERE (cv.title LIKE ? OR cv.description LIKE ? OR cv.tags LIKE ?)
                AND cv.category = ?
                ORDER BY cv.crawl_date DESC
                LIMIT ?
            ''', (f'%{query}%', f'%{query}%', f'%{query}%', category, limit))
        else:
            cursor.execute('''
                SELECT cv.*, vs.name as site_name
                FROM crawled_videos cv
                JOIN video_sites vs ON cv.site_id = vs.id
                WHERE cv.title LIKE ? OR cv.description LIKE ? OR cv.tags LIKE ?
                ORDER BY cv.crawl_date DESC
                LIMIT ?
            ''', (f'%{query}%', f'%{query}%', f'%{query}%', limit))
        
        videos = []
        for row in cursor.fetchall():
            videos.append({
                'id': row[0],
                'site_id': row[1],
                'video_id': row[2],
                'title': row[3],
                'url': row[4],
                'thumbnail': row[5],
                'duration': row[6],
                'upload_date': row[7],
                'description': row[8],
                'category': row[9],
                'tags': row[10],
                'crawl_date': row[11],
                'site_name': row[12]
            })
        
        conn.close()
        return videos
    
    def add_search_keyword(self, keyword: str, category: str = None, priority: int = 1) -> int:
        """Add a new search keyword"""
        conn = sqlite3.connect(self.db.sites_db)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT OR REPLACE INTO search_keywords (keyword, category, priority)
            VALUES (?, ?, ?)
        ''', (keyword, category, priority))
        
        keyword_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return keyword_id
    
    def get_search_keywords(self, category: str = None) -> List[Dict]:
        """Get search keywords, optionally filtered by category"""
        conn = sqlite3.connect(self.db.sites_db)
        cursor = conn.cursor()
        
        if category:
            cursor.execute('''
                SELECT * FROM search_keywords 
                WHERE category = ?
                ORDER BY priority DESC, keyword
            ''', (category,))
        else:
            cursor.execute('''
                SELECT * FROM search_keywords 
                ORDER BY priority DESC, keyword
            ''')
        
        keywords = []
        for row in cursor.fetchall():
            keywords.append({
                'id': row[0],
                'keyword': row[1],
                'category': row[2],
                'priority': row[3],
                'created_at': row[4]
            })
        
        conn.close()
        return keywords

# Global database instance
db = VideoDatabase()
favorites_manager = FavoritesManager(db)
sites_manager = SitesManager(db) 