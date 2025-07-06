# Video Scraper - Ashley Got Videos

A full-stack web application that scrapes videos from the internet using yt-dlp and provides a beautiful video player interface with a scrollable menu. Features a background task that continuously searches for "ashley got" videos.

## Features

- 🎥 **Video Scraping**: Uses yt-dlp to search and download videos from YouTube
- 🔄 **Background Tasks**: Automatically searches for "ashley got" videos every 30 minutes
- 📱 **Modern UI**: Beautiful, responsive interface built with Next.js and Tailwind CSS
- 🎮 **Video Player**: Built-in video player with controls
- 📋 **Scrollable Menu**: Easy navigation through downloaded videos
- 🔍 **Search Functionality**: Search for any videos manually
- 💾 **Local Storage**: Videos are downloaded and stored locally
- 🗑️ **Video Management**: Delete videos you no longer want

## Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **yt-dlp**: Video downloading library
- **Uvicorn**: ASGI server
- **Python 3.8+**: Programming language

### Frontend
- **Next.js 14**: React framework with App Router
- **TypeScript**: Type-safe JavaScript
- **Tailwind CSS**: Utility-first CSS framework
- **Axios**: HTTP client
- **Lucide React**: Beautiful icons

## Prerequisites

- Python 3.8 or higher
- Node.js 18 or higher
- npm or yarn

## Installation

### 1. Clone the repository
```bash
git clone <repository-url>
cd pon
```

### 2. Set up the Backend (FastAPI)

```bash
# Create and activate virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Create videos directory
mkdir videos
```

### 3. Set up the Frontend (Next.js)

```bash
# Navigate to frontend directory
cd frontend

# Install Node.js dependencies
npm install

# Or if using yarn
yarn install
```

## Running the Application

### 1. Start the Backend Server

```bash
# From the root directory
cd backend
python main.py
```

The FastAPI server will start on `http://localhost:8000`

### 2. Start the Frontend Development Server

```bash
# From the frontend directory
cd frontend
npm run dev
# Or: yarn dev
```

The Next.js application will start on `http://localhost:3000`

### 3. Access the Application

Open your browser and navigate to `http://localhost:3000`

## Usage

### Searching for Videos
1. Use the search bar in the header to search for any videos
2. Click the search button or press Enter
3. Search results will appear in the right sidebar

### Downloading Videos
1. Click the download icon (📥) next to any video in the search results
2. The video will be downloaded to the local storage
3. Downloaded videos appear in the "Downloaded Videos" section

### Playing Videos
1. Click on any downloaded video in the right sidebar
2. The video will load in the main player
3. Use the video controls to play, pause, seek, etc.

### Managing Videos
- **Delete**: Click the trash icon (🗑️) next to any downloaded video
- **Refresh**: Click the refresh icon to reload the video list

### Background Task
The application automatically searches for "ashley got" videos every 30 minutes. New videos found will be automatically downloaded and added to your collection.

## API Endpoints

### Backend API (FastAPI)

- `GET /` - Health check
- `GET /videos` - Get all downloaded videos
- `POST /search` - Search for videos
- `POST /download/{video_id}` - Download a specific video
- `DELETE /videos/{video_id}` - Delete a video
- `GET /search-history` - Get search history

## File Structure

```
pon/
├── backend/
│   ├── main.py              # FastAPI application
│   └── videos/              # Downloaded videos storage
├── frontend/
│   ├── app/
│   │   ├── globals.css      # Global styles
│   │   ├── layout.tsx       # Root layout
│   │   └── page.tsx         # Main page component
│   ├── package.json         # Node.js dependencies
│   ├── next.config.js       # Next.js configuration
│   ├── tailwind.config.js   # Tailwind CSS configuration
│   └── tsconfig.json        # TypeScript configuration
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## Configuration

### Video Quality
You can modify the video quality in `backend/main.py` by changing the `format` option in the `ydl_opts`:

```python
ydl_opts = {
    'format': 'best[height<=720]',  # Change this line
    # ... other options
}
```

### Background Task Interval
To change how often the background task searches for videos, modify the sleep duration in `backend/main.py`:

```python
await asyncio.sleep(1800)  # 30 minutes (1800 seconds)
```

## Troubleshooting

### Common Issues

1. **yt-dlp not working**: Make sure you have the latest version installed
   ```bash
   pip install --upgrade yt-dlp
   ```

2. **CORS errors**: The backend is configured to allow requests from `http://localhost:3000`. If you're using a different port, update the CORS settings in `backend/main.py`

3. **Video not playing**: Check that the video file exists in the `backend/videos/` directory

4. **Port already in use**: Change the port in the respective configuration files

### Performance Tips

- Videos are downloaded in 720p quality by default to save storage space
- The background task runs every 30 minutes to avoid overwhelming the system
- Videos are stored locally, so make sure you have enough disk space

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is for educational purposes. Please respect YouTube's terms of service and copyright laws when downloading videos.

## Disclaimer

This application is for personal use only. Users are responsible for ensuring they have the right to download and store any videos. The developers are not responsible for any copyright violations or misuse of this application. 