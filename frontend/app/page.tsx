'use client'

import React, { useState, useEffect, useRef } from 'react'
import axios from 'axios'
import { Search, Play, Trash2, RefreshCw, X, Plus, Heart, Star, Eye, Clock, User } from 'lucide-react'
import Plyr from 'plyr'
import 'plyr/dist/plyr.css'
import AIApprovalButton from '../components/AIApprovalButton'

interface Video {
  id: string | number
  title: string
  url: string
  thumbnail?: string
  duration?: string
  upload_date?: string
  description?: string
  local_path?: string
  video_id?: string
  site_id?: number
  category?: string
  tags?: string | string[]
  crawl_date?: string
  site_name?: string
  source_site?: string
  preview_url?: string
  embed_url?: string
  site_url?: string
}

interface Playlist {
  id: number
  name: string
  description: string
  created_date: string
  video_count: number
}

interface Category {
  name: string
  count: number
}

interface Actress {
  id: string
  name: string
  image?: string
  videoCount: number
}

export default function Home() {
  const [videos, setVideos] = useState<Video[]>([])
  const [selectedVideo, setSelectedVideo] = useState<Video | null>(null)
  const [searchQuery, setSearchQuery] = useState('')
  const [selectedCategory, setSelectedCategory] = useState<string>('')
  const [isLoading, setIsLoading] = useState(false)
  const [isSearching, setIsSearching] = useState(false)
  const [searchResults, setSearchResults] = useState<Video[]>([])
  const [playlists, setPlaylists] = useState<Playlist[]>([])
  const [categories, setCategories] = useState<Category[]>([])
  const [urlInput, setUrlInput] = useState('')
  const [isUrlLoading, setIsUrlLoading] = useState(false)
  const [showPlaylistDropdown, setShowPlaylistDropdown] = useState(false)
  const [hoveredVideo, setHoveredVideo] = useState<Video | null>(null)
  const [showVideoModal, setShowVideoModal] = useState(false)
  const [favoriteActresses, setFavoriteActresses] = useState<Actress[]>([])
  const [favoriteVideos, setFavoriteVideos] = useState<Video[]>([])
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [plyrPlayer, setPlyrPlayer] = useState<Plyr | null>(null)

  const API_BASE = 'http://localhost:8000'

  // Sample favorite actresses (in real app, this would come from backend)
  const sampleActresses: Actress[] = [
    { id: '1', name: 'Ashley Got', image: 'https://via.placeholder.com/60x60/ff6b6b/ffffff?text=AG', videoCount: 45 },
    { id: '2', name: 'Riley Reid', image: 'https://via.placeholder.com/60x60/4ecdc4/ffffff?text=RR', videoCount: 32 },
    { id: '3', name: 'Lana Rhoades', image: 'https://via.placeholder.com/60x60/45b7d1/ffffff?text=LR', videoCount: 28 },
    { id: '4', name: 'Mia Khalifa', image: 'https://via.placeholder.com/60x60/96ceb4/ffffff?text=MK', videoCount: 15 },
    { id: '5', name: 'Abella Danger', image: 'https://via.placeholder.com/60x60/ffeaa7/ffffff?text=AD', videoCount: 23 },
  ]

  // Load videos on component mount
  useEffect(() => {
    loadVideos()
    loadPlaylists()
    loadCategories()
    setFavoriteActresses(sampleActresses)
  }, [])

  const loadPlaylists = async () => {
    try {
      const response = await axios.get(`${API_BASE}/playlists`)
      setPlaylists(response.data)
    } catch (error) {
      console.error('Error loading playlists:', error)
    }
  }

  const loadCategories = async () => {
    try {
      const response = await axios.get(`${API_BASE}/categories`)
      setCategories(response.data)
    } catch (error) {
      console.error('Error loading categories:', error)
    }
  }

  const parseVideoUrl = async () => {
    if (!urlInput.trim()) return
    
    try {
      setIsUrlLoading(true)
      const response = await axios.post(`${API_BASE}/parse-video-url`, {
        url: urlInput
      })
      
      const video = response.data.video
      setSelectedVideo(video)
      setUrlInput('')
      
      // Add to search results if not already there
      if (!searchResults.find(v => v.id === video.id)) {
        setSearchResults(prev => [video, ...prev])
      }
    } catch (error) {
      console.error('Error parsing URL:', error)
      // Try alternative approach - search for the URL
      try {
        const searchResponse = await axios.get(`${API_BASE}/search/aggregated`, {
          params: {
            query: urlInput,
            max_results: 1
          }
        })
        
        if (searchResponse.data.videos.length > 0) {
          const video = searchResponse.data.videos[0]
          setSelectedVideo(video)
          setUrlInput('')
          if (!searchResults.find(v => v.id === video.id)) {
            setSearchResults(prev => [video, ...prev])
          }
        } else {
          alert('Could not find video. Please check the URL and try again.')
        }
      } catch (searchError) {
        console.error('Search fallback also failed:', searchError)
        alert('Failed to parse video URL. Please check the URL and try again.')
      }
    } finally {
      setIsUrlLoading(false)
    }
  }

  const addVideoToPlaylist = async (playlistId: number, video: Video) => {
    try {
      await axios.post(`${API_BASE}/playlists/${playlistId}/videos/add`, {
        video_id: video.id,
        video_title: video.title,
        video_url: video.url,
        video_thumbnail: video.thumbnail,
        video_duration: video.duration,
        video_source: video.source_site,
        video_category: video.category
      })
      
      // Refresh playlists
      loadPlaylists()
      setShowPlaylistDropdown(false)
    } catch (error) {
      console.error('Error adding video to playlist:', error)
    }
  }

  const createPlaylist = async (name: string) => {
    try {
      await axios.post(`${API_BASE}/playlists`, {
        name,
        description: `Playlist for ${name}`
      })
      loadPlaylists()
    } catch (error) {
      console.error('Error creating playlist:', error)
    }
  }

  const loadVideos = async () => {
    try {
      setIsLoading(true)
      setVideos([])
    } catch (error) {
      console.error('Error loading videos:', error)
      setVideos([])
    } finally {
      setIsLoading(false)
    }
  }

  const searchVideos = async () => {
    if (!searchQuery.trim()) return
    
    try {
      setIsSearching(true)
      
      // Use aggregated search for better results
      const response = await axios.get(`${API_BASE}/search/aggregated`, {
        params: {
          query: searchQuery,
          category: selectedCategory || undefined,
          max_results: 20
        }
      })
      
      setSearchResults(response.data.videos)
    } catch (error) {
      console.error('Error searching videos:', error)
      // Fallback to regular search
      try {
        const fallbackResponse = await axios.post(`${API_BASE}/search`, {
          query: searchQuery,
          category: selectedCategory,
          max_results: 10
        })
        setSearchResults(fallbackResponse.data.videos)
      } catch (fallbackError) {
        console.error('Fallback search also failed:', fallbackError)
      }
    } finally {
      setIsSearching(false)
    }
  }

  const deleteVideo = async (videoId: string | number) => {
    try {
      await axios.delete(`${API_BASE}/videos/${videoId}`)
      setVideos(videos.filter(v => v.id !== videoId))
      if (selectedVideo?.id === videoId) {
        setSelectedVideo(videos.length > 1 ? videos[0] : null)
      }
    } catch (error) {
      console.error('Error deleting video:', error)
    }
  }

  const formatDuration = (seconds: number | string) => {
    if (typeof seconds === 'string') {
      return seconds;
    }
    const minutes = Math.floor(seconds / 60)
    const remainingSeconds = seconds % 60
    return `${minutes}:${remainingSeconds.toString().padStart(2, '0')}`
  }

  const toggleFavorite = (video: Video) => {
    if (favoriteVideos.find(v => v.id === video.id)) {
      setFavoriteVideos(favoriteVideos.filter(v => v.id !== video.id))
    } else {
      setFavoriteVideos([...favoriteVideos, video])
    }
  }

  const openVideoModal = (video: Video) => {
    setSelectedVideo(video)
    setShowVideoModal(true)
  }

  // Initialize Plyr player when modal opens
  useEffect(() => {
    if (showVideoModal && selectedVideo) {
      // Small delay to ensure DOM is ready
      const timer = setTimeout(() => {
        const videoElement = document.getElementById('plyr-video') as HTMLVideoElement
        if (videoElement && !plyrPlayer) {
          const player = new Plyr(videoElement, {
            controls: [
              'play-large',
              'play',
              'progress',
              'current-time',
              'mute',
              'volume',
              'captions',
              'settings',
              'pip',
              'airplay',
              'fullscreen'
            ],
            settings: ['captions', 'quality', 'speed'],
            speed: { selected: 1, options: [0.5, 0.75, 1, 1.25, 1.5, 2] },
            quality: {
              default: 720,
              options: [4320, 2880, 2160, 1440, 1080, 720, 576, 480, 360, 240]
            },
            keyboard: { focused: true, global: true },
            tooltips: { controls: true, seek: true },
            autoplay: false,
            muted: false,
            hideControls: true,
            resetOnEnd: false,
            disableContextMenu: false,
            loadSprite: false,
            iconPrefix: 'plyr',
            blankVideo: 'https://cdn.plyr.io/static/blank.mp4'
          })
          
          setPlyrPlayer(player)
          
          // Cleanup function
          return () => {
            if (player) {
              player.destroy()
            }
          }
        }
      }, 100)
      
      return () => clearTimeout(timer)
    }
  }, [showVideoModal, selectedVideo, plyrPlayer])

  // Cleanup player when modal closes
  useEffect(() => {
    if (!showVideoModal && plyrPlayer) {
      plyrPlayer.destroy()
      setPlyrPlayer(null)
    }
  }, [showVideoModal, plyrPlayer])

  return (
    <div className="min-h-screen bg-gray-100 dark:bg-gray-900">
      {/* Top Navigation - Favorite Actresses */}
      <header className="bg-white dark:bg-gray-800 shadow-sm border-b border-gray-200 dark:border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-16">
            {/* Logo */}
            <div className="flex items-center">
              <h1 className="text-2xl font-bold text-red-600 dark:text-red-400">
                VideoHub
              </h1>
            </div>
            
            {/* Search Bar */}
            <div className="flex-1 max-w-2xl mx-8">
              <div className="relative">
                <input
                  type="text"
                  placeholder="Search for videos, actresses, categories..."
                  value={searchQuery}
                  onChange={(e) => setSearchQuery(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && searchVideos()}
                  className="w-full px-4 py-2 pl-10 pr-4 text-sm border border-gray-300 dark:border-gray-600 rounded-full focus:ring-2 focus:ring-red-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                />
                <Search className="absolute left-3 top-2.5 h-4 w-4 text-gray-400" />
              </div>
            </div>
            
            {/* URL Input */}
            <div className="flex items-center space-x-4">
              <div className="relative">
                <input
                  type="text"
                  placeholder="Paste video URL..."
                  value={urlInput}
                  onChange={(e) => setUrlInput(e.target.value)}
                  onKeyPress={(e) => e.key === 'Enter' && parseVideoUrl()}
                  className="w-64 px-3 py-2 pl-8 pr-4 text-sm border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                />
                <Play className="absolute left-2 top-2.5 h-4 w-4 text-gray-400" />
              </div>
              <button
                onClick={parseVideoUrl}
                disabled={isUrlLoading || !urlInput.trim()}
                className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 flex items-center space-x-2"
              >
                {isUrlLoading ? (
                  <RefreshCw className="h-4 w-4 animate-spin" />
                ) : (
                  <Plus className="h-4 w-4" />
                )}
                <span>Load</span>
              </button>
            </div>
          </div>
          
          {/* Favorite Actresses Bar */}
          <div className="py-3 border-t border-gray-200 dark:border-gray-700">
            <div className="flex items-center space-x-6 overflow-x-auto actress-nav">
              <span className="text-sm font-medium text-gray-700 dark:text-gray-300 whitespace-nowrap">
                Favorite Actresses:
              </span>
              {favoriteActresses.map((actress) => (
                <div
                  key={actress.id}
                  className="flex items-center space-x-2 cursor-pointer hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg p-2 transition-colors"
                  onClick={() => {
                    setSearchQuery(actress.name)
                    searchVideos()
                  }}
                >
                  <img
                    src={actress.image}
                    alt={actress.name}
                    className="w-8 h-8 rounded-full object-cover"
                  />
                  <span className="text-sm font-medium text-gray-900 dark:text-white">
                    {actress.name}
                  </span>
                  <span className="text-xs text-gray-500 dark:text-gray-400">
                    ({actress.videoCount})
                  </span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </header>

      <div className="flex">
        {/* Left Sidebar - Favorites */}
        <div className={`${sidebarOpen ? 'w-80' : 'w-16'} bg-white dark:bg-gray-800 shadow-sm border-r border-gray-200 dark:border-gray-700 sidebar-transition min-h-screen`}>
          <div className="p-4">
            <div className="flex items-center justify-between mb-4">
              <h3 className={`font-semibold text-gray-900 dark:text-white ${!sidebarOpen && 'hidden'}`}>
                Favorites
              </h3>
              <button
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className="p-1 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
              >
                {sidebarOpen ? <X className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
              </button>
            </div>
            
            {sidebarOpen && (
              <>
                {/* Favorite Videos */}
                <div className="mb-6">
                  <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3 flex items-center">
                    <Heart className="h-4 w-4 mr-2" />
                    Favorite Videos ({favoriteVideos.length})
                  </h4>
                  <div className="space-y-2 max-h-64 overflow-y-auto">
                    {favoriteVideos.map((video) => (
                      <div
                        key={video.id}
                        className="flex items-center space-x-2 p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer"
                        onClick={() => openVideoModal(video)}
                      >
                        <img
                          src={video.thumbnail || 'https://via.placeholder.com/40x30/666/fff?text=?'}
                          alt={video.title}
                          className="w-10 h-7 object-cover rounded"
                        />
                        <div className="flex-1 min-w-0">
                          <p className="text-xs font-medium text-gray-900 dark:text-white truncate">
                            {video.title}
                          </p>
                          {video.duration && (
                            <p className="text-xs text-gray-500 dark:text-gray-400">
                              {formatDuration(video.duration)}
                            </p>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>

                {/* Playlists */}
                <div>
                  <h4 className="text-sm font-medium text-gray-700 dark:text-gray-300 mb-3 flex items-center">
                    <Star className="h-4 w-4 mr-2" />
                    Playlists ({playlists.length})
                  </h4>
                  <div className="space-y-2">
                    {playlists.map((playlist) => (
                      <div
                        key={playlist.id}
                        className="p-2 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 cursor-pointer"
                      >
                        <div className="flex items-center justify-between">
                          <span className="text-sm font-medium text-gray-900 dark:text-white truncate">
                            {playlist.name}
                          </span>
                          <span className="text-xs text-gray-500 dark:text-gray-400">
                            {playlist.video_count}
                          </span>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              </>
            )}
          </div>
        </div>

        {/* Main Content */}
        <div className="flex-1 p-6">
          {/* Search Results Grid */}
          <div className="mb-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold text-gray-900 dark:text-white">
                {searchQuery ? `Search Results for "${searchQuery}"` : 'Popular Videos'}
              </h2>
              <div className="flex items-center space-x-4">
                <select
                  value={selectedCategory}
                  onChange={(e) => setSelectedCategory(e.target.value)}
                  className="px-3 py-2 text-sm border border-gray-300 dark:border-gray-600 rounded-lg focus:ring-2 focus:ring-red-500 focus:border-transparent bg-white dark:bg-gray-700 text-gray-900 dark:text-white"
                >
                  <option value="">All Categories</option>
                  {categories.map((category) => (
                    <option key={category.name} value={category.name}>
                      {category.name} ({category.count})
                    </option>
                  ))}
                </select>
                <button
                  onClick={searchVideos}
                  disabled={isSearching}
                  className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 disabled:opacity-50 flex items-center space-x-2"
                >
                  {isSearching ? (
                    <RefreshCw className="h-4 w-4 animate-spin" />
                  ) : (
                    <Search className="h-4 w-4" />
                  )}
                  <span>Search</span>
                </button>
              </div>
            </div>

            {/* Video Grid */}
            <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
              {searchResults.map((video) => (
                <div
                  key={video.id}
                  className="bg-white dark:bg-gray-800 rounded-lg shadow-sm overflow-hidden video-card-hover cursor-pointer group"
                  onClick={() => openVideoModal(video)}
                  onMouseEnter={() => setHoveredVideo(video)}
                  onMouseLeave={() => setHoveredVideo(null)}
                >
                  <div className="relative">
                    <img
                      src={video.thumbnail || 'https://via.placeholder.com/300x200/666/fff?text=No+Thumbnail'}
                      alt={video.title}
                      className="w-full h-48 object-cover"
                    />
                    
                    {/* Duration Badge */}
                    {video.duration && (
                      <div className="absolute bottom-2 right-2 bg-black/80 text-white text-xs px-2 py-1 rounded">
                        {formatDuration(video.duration)}
                      </div>
                    )}
                    
                    {/* Play Button Overlay */}
                    <div className="absolute inset-0 bg-black/20 opacity-0 group-hover:opacity-100 play-overlay flex items-center justify-center">
                      <Play className="h-12 w-12 text-white" />
                    </div>
                    
                    {/* Favorite Button */}
                    <button
                      onClick={(e) => {
                        e.stopPropagation()
                        toggleFavorite(video)
                      }}
                      className="absolute top-2 right-2 p-1 bg-black/50 rounded-full hover:bg-black/70 favorite-button"
                    >
                      <Heart 
                        className={`h-4 w-4 ${
                          favoriteVideos.find(v => v.id === video.id) 
                            ? 'text-red-500 fill-current' 
                            : 'text-white'
                        }`} 
                      />
                    </button>
                  </div>
                  
                  <div className="p-3">
                    <h3 className="text-sm font-medium text-gray-900 dark:text-white line-clamp-2 mb-1">
                      {video.title}
                    </h3>
                    <div className="flex items-center justify-between text-xs text-gray-500 dark:text-gray-400">
                      <span>{video.source_site || 'Unknown'}</span>
                      {video.category && (
                        <span className="bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400 px-2 py-1 rounded">
                          {video.category}
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              ))}
            </div>

            {searchResults.length === 0 && !isLoading && (
              <div className="text-center py-12">
                <Play className="h-16 w-16 text-gray-400 mx-auto mb-4" />
                <p className="text-gray-500 dark:text-gray-400">
                  No videos found. Start by searching for videos!
                </p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* AI Approval Button */}
      <AIApprovalButton
        onApprove={() => {
          console.log('AI improvements approved and deployed!')
          // Refresh the page to show new improvements
          window.location.reload()
        }}
        onReject={() => {
          console.log('AI improvements rejected')
        }}
      />

      {/* Video Modal */}
      {showVideoModal && selectedVideo && (
        <div className="fixed inset-0 bg-black/80 modal-backdrop flex items-center justify-center z-50 p-4">
          <div className="bg-white dark:bg-gray-800 rounded-lg max-w-4xl w-full max-h-[90vh] overflow-hidden">
            <div className="p-4 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between">
              <h2 className="text-lg font-semibold text-gray-900 dark:text-white truncate">
                {selectedVideo.title}
              </h2>
              <div className="flex items-center space-x-2">
                <button
                  onClick={() => toggleFavorite(selectedVideo)}
                  className="p-2 text-gray-400 hover:text-red-500"
                >
                  <Heart 
                    className={`h-5 w-5 ${
                      favoriteVideos.find(v => v.id === selectedVideo.id) 
                        ? 'text-red-500 fill-current' 
                        : ''
                    }`} 
                  />
                </button>
                <button
                  onClick={() => setShowVideoModal(false)}
                  className="p-2 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300"
                >
                  <X className="h-5 w-5" />
                </button>
              </div>
            </div>
            
            <div className="p-4">
              <div className="aspect-video bg-gray-200 dark:bg-gray-700 rounded-lg overflow-hidden mb-4">
                {selectedVideo.embed_url ? (
                  <iframe
                    src={selectedVideo.embed_url}
                    className="w-full h-full"
                    frameBorder="0"
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                    allowFullScreen
                  />
                ) : selectedVideo.url.includes('youtube.com') || selectedVideo.url.includes('youtu.be') ? (
                  <iframe
                    src={`https://www.youtube.com/embed/${selectedVideo.url.split('v=')[1] || selectedVideo.url.split('youtu.be/')[1]}`}
                    className="w-full h-full"
                    frameBorder="0"
                    allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture"
                    allowFullScreen
                  />
                ) : (
                  <video
                    id="plyr-video"
                    className="w-full h-full"
                    poster={selectedVideo.thumbnail}
                    playsInline
                  >
                    <source src={selectedVideo.url} type="video/mp4" />
                    <source src={selectedVideo.url} type="video/webm" />
                    <source src={selectedVideo.url} type="video/ogg" />
                    Your browser does not support the video tag.
                  </video>
                )}
              </div>
              
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  {selectedVideo.description && (
                    <p className="text-sm text-gray-600 dark:text-gray-300 mb-2">
                      {selectedVideo.description}
                    </p>
                  )}
                  <div className="flex items-center space-x-4 text-xs text-gray-500 dark:text-gray-400">
                    {selectedVideo.duration && (
                      <span className="flex items-center">
                        <Clock className="h-3 w-3 mr-1" />
                        {formatDuration(selectedVideo.duration)}
                      </span>
                    )}
                    {selectedVideo.source_site && (
                      <span className="flex items-center">
                        <User className="h-3 w-3 mr-1" />
                        {selectedVideo.source_site}
                      </span>
                    )}
                    {selectedVideo.category && (
                      <span className="bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400 px-2 py-1 rounded">
                        {selectedVideo.category}
                      </span>
                    )}
                  </div>
                </div>
                
                {/* Playlist Dropdown */}
                <div className="relative">
                  <button
                    onClick={() => setShowPlaylistDropdown(!showPlaylistDropdown)}
                    className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 flex items-center space-x-2"
                  >
                    <Plus className="h-4 w-4" />
                    <span>Add to Playlist</span>
                  </button>
                  
                  {showPlaylistDropdown && (
                    <div className="absolute right-0 mt-2 w-64 bg-white dark:bg-gray-800 rounded-lg shadow-lg border border-gray-200 dark:border-gray-600 z-10">
                      <div className="p-2">
                        {playlists.map((playlist) => (
                          <button
                            key={playlist.id}
                            onClick={() => addVideoToPlaylist(playlist.id, selectedVideo)}
                            className="w-full text-left px-3 py-2 text-sm text-gray-700 dark:text-gray-300 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
                          >
                            {playlist.name} ({playlist.video_count} videos)
                          </button>
                        ))}
                        <div className="border-t border-gray-200 dark:border-gray-600 mt-2 pt-2">
                          <button
                            onClick={() => {
                              const name = prompt('Enter playlist name:')
                              if (name) createPlaylist(name)
                            }}
                            className="w-full text-left px-3 py-2 text-sm text-red-600 dark:text-red-400 hover:bg-gray-100 dark:hover:bg-gray-700 rounded"
                          >
                            + Create New Playlist
                          </button>
                        </div>
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
} 