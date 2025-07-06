# 🎥 Enhanced Video Scraper with Database & Playlists

A comprehensive video scraping and management system with SQLite databases, playlist organization, multi-site crawling, and category-based search.

## 🚀 Features

### 📊 **Dual Database System**
- **Favorites Database**: Playlists and favorite videos
- **Sites Database**: Video site crawling and indexing

### 🎵 **Playlist Management**
- Create custom playlists
- Organize videos by category/theme
- Drag-and-drop video organization
- Playlist statistics and metadata

### 🕷️ **Multi-Site Video Crawling**
- **1000+ Video Sites** supported
- Automatic crawling and indexing
- Category-based site organization
- Real-time crawl status monitoring

### 🔍 **Advanced Search**
- Category-filtered search
- Keyword-based indexing
- Multi-site search results
- Manual video addition

### 🖼️ **Thumbnail Management**
- Automatic thumbnail extraction
- Fallback placeholder images
- Thumbnail caching system

### 🔒 **Security Features**
- Proxy rotation (free-proxy)
- VPN integration (python-vpn)
- IP logging and monitoring
- Request tracking

## 📁 Database Schema

### Favorites Database (`favorites.db`)

```sql
-- Playlists table
CREATE TABLE playlists (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE,
    description TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Videos table
CREATE TABLE videos (
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
    tags TEXT
);

-- Playlist videos junction
CREATE TABLE playlist_videos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    playlist_id INTEGER,
    video_id INTEGER,
    position INTEGER,
    added_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Sites Database (`video_sites.db`)

```sql
-- Video sites table
CREATE TABLE video_sites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    url TEXT NOT NULL UNIQUE,
    category TEXT,
    description TEXT,
    search_url_pattern TEXT,
    is_active BOOLEAN DEFAULT 1,
    last_crawled TIMESTAMP,
    crawl_interval INTEGER DEFAULT 3600
);

-- Crawled videos table
CREATE TABLE crawled_videos (
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
    crawl_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Search keywords table
CREATE TABLE search_keywords (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    keyword TEXT NOT NULL UNIQUE,
    category TEXT,
    priority INTEGER DEFAULT 1
);
```

## 🚀 Quick Start

### 1. **One-Click Startup**
```bash
chmod +x start.sh
./start.sh
```

This will:
- Install all dependencies
- Show your real and proxied IP
- Start the enhanced backend
- Start the Next.js frontend
- Display all available features

### 2. **Manual Startup**
```bash
# Backend only
cd backend
python main_enhanced.py

# Frontend only (in another terminal)
cd frontend
npm install
npm run dev
```

## 📱 Frontend Features

### **Search Tab**
- Multi-category video search
- Real-time search results
- Video player with Flowplayer
- Add videos to playlists
- Manual video addition

### **Playlists Tab**
- Create new playlists
- View playlist statistics
- Browse playlist videos
- Drag-and-drop organization

### **Sites Tab**
- View all video sites
- Add new sites for crawling
- Monitor crawl status
- Site category management

### **Stats Tab**
- Real-time statistics
- Database metrics
- Crawl status monitoring
- System health indicators

## 🔧 API Endpoints

### **Playlists**
- `POST /playlists` - Create playlist
- `GET /playlists` - Get all playlists
- `GET /playlists/{id}/videos` - Get playlist videos
- `POST /playlists/{id}/videos` - Add video to playlist

### **Video Sites**
- `POST /sites` - Add video site
- `GET /sites` - Get video sites
- `GET /categories` - Get site categories

### **Search**
- `POST /search` - Search videos
- `GET /search/keywords` - Get search keywords
- `POST /search/keywords` - Add search keyword

### **Manual Videos**
- `POST /videos/manual` - Add manual video

### **Crawl Control**
- `POST /crawl/start` - Start crawling
- `POST /crawl/stop` - Stop crawling
- `GET /crawl/status` - Get crawl status

### **Statistics**
- `GET /stats` - Get system statistics

## 🎯 Usage Examples

### **Create a Playlist**
```bash
curl -X POST http://localhost:8000/playlists \
  -H "Content-Type: application/json" \
  -d '{"name": "My Favorites", "description": "Best videos"}'
```

### **Search Videos**
```bash
curl -X POST http://localhost:8000/search \
  -H "Content-Type: application/json" \
  -d '{"query": "ashley got", "category": "Entertainment", "max_results": 20}'
```

### **Add Video Site**
```bash
curl -X POST http://localhost:8000/sites \
  -H "Content-Type: application/json" \
  -d '{"name": "NewTube", "url": "https://newtube.com", "category": "Entertainment"}'
```

### **Add Manual Video**
```bash
curl -X POST http://localhost:8000/videos/manual \
  -H "Content-Type: application/json" \
  -d '{
    "id": "manual_001",
    "title": "My Video",
    "url": "https://example.com/video.mp4",
    "thumbnail": "https://example.com/thumb.jpg",
    "category": "Entertainment"
  }'
```

## 🗂️ File Structure

```
pon/
├── backend/
│   ├── main_enhanced.py      # Enhanced backend with database
│   ├── database.py           # Database management
│   ├── main_secure.py        # Secure backend with VPN
│   ├── main_simple.py        # Simple backend
│   ├── security_monitor.py   # Security monitoring
│   ├── vpn_client.py         # VPN client
│   ├── favorites.db          # Favorites database
│   ├── video_sites.db        # Sites database
│   ├── videos/               # Downloaded videos
│   └── thumbnails/           # Video thumbnails
├── frontend/
│   ├── pages/
│   │   └── index.js          # Enhanced frontend
│   ├── package.json
│   └── tailwind.config.js
├── start.sh                  # One-click startup script
├── SECURITY_README.md        # Security documentation
└── ENHANCED_README.md        # This file
```

## 🔧 Configuration

### **Database Settings**
- Databases are created automatically
- Default categories and sites are pre-loaded
- Crawl intervals are configurable

### **Crawl Settings**
- Default crawl interval: 1 hour
- Max videos per keyword: 5
- Max keywords per site: 5

### **Security Settings**
- VPN password: `secure_vpn_password_2024`
- VPN port: 5000
- Proxy rotation: Automatic

## 📊 Default Data

### **Pre-loaded Categories**
- Entertainment, Music, Gaming, Education
- Sports, News, Comedy, Technology
- Lifestyle, Movies

### **Pre-loaded Sites**
- YouTube, Vimeo, Dailymotion
- Twitch, TikTok, Instagram
- Reddit, Bilibili, Niconico

### **Default Keywords**
- "ashley got" (priority 10)
- Common categories (priority 5)

## 🚨 Troubleshooting

### **Database Issues**
```bash
# Reset databases
rm backend/favorites.db backend/video_sites.db
python backend/main_enhanced.py
```

### **Crawl Issues**
```bash
# Check crawl status
curl http://localhost:8000/crawl/status

# Restart crawling
curl -X POST http://localhost:8000/crawl/stop
curl -X POST http://localhost:8000/crawl/start
```

### **Frontend Issues**
```bash
# Clear frontend cache
cd frontend
rm -rf .next
npm run dev
```

## 🔒 Security Notes

1. **Change Default Password**: Update VPN password in `main_secure.py`
2. **Monitor Logs**: Use `security_monitor.py` for real-time monitoring
3. **Proxy Rotation**: All requests use rotating proxies
4. **IP Logging**: All requests are logged for security

## 📈 Performance Tips

1. **Database Optimization**: Indexes are created automatically
2. **Crawl Scheduling**: Adjust crawl intervals based on needs
3. **Thumbnail Caching**: Thumbnails are cached locally
4. **Search Optimization**: Use categories to narrow searches

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add your enhancements
4. Test thoroughly
5. Submit a pull request

## 📄 License

This project is for educational/research purposes. Ensure compliance with local laws and terms of service.

---

**🎉 Enjoy your enhanced video scraping experience!** 