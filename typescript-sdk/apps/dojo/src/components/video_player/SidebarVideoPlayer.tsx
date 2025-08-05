// SidebarVideoPlayer.tsx - New component for sidebar video display
// @ts-nocheck
"use client";
import React, { useState, useRef, useEffect } from "react";
import { Play, Pause, Volume2, VolumeX, X, SkipBack, SkipForward, Maximize2 } from "lucide-react";

interface VideoData {
  title: string;
  url: string;
  duration?: string;
  sport?: string;
  players?: string[];
  teams?: string[];
  video_type?: string;
  technical_metadata?: {
    source_uri: string;
    duration?: string;
    resolution?: string;
    file_size?: string;
    thumbnail_url?: string;
  };
  context_metadata?: {
    sport?: string;
    video_type?: string;
    players?: Array<{ name: string; position?: string; actions?: string[] }>;
    teams?: Array<{ name: string }>;
  };
}

interface SidebarVideoPlayerProps {
  video: VideoData;
  onClose: () => void;
}

const SidebarVideoPlayer: React.FC<SidebarVideoPlayerProps> = ({ video, onClose }) => {
  const [isPlaying, setIsPlaying] = useState(false);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [volume, setVolume] = useState(0.7);
  const [isMuted, setIsMuted] = useState(false);
  const [currentTime, setCurrentTime] = useState(0);
  const [videoDuration, setVideoDuration] = useState(0);
  
  const videoRef = useRef<HTMLVideoElement>(null);

  // Get video URL
  const videoUrl = video.technical_metadata?.source_uri || video.url || '';

  // Get players display
  const getPlayersDisplay = (): string => {
    if (video.context_metadata?.players && Array.isArray(video.context_metadata.players)) {
      return video.context_metadata.players
        .slice(0, 3)
        .map(p => p.name)
        .join(', ') + (video.context_metadata.players.length > 3 ? ` +${video.context_metadata.players.length - 3} more` : '');
    }
    if (video.players && Array.isArray(video.players)) {
      return video.players.slice(0, 3).join(', ') + (video.players.length > 3 ? ` +${video.players.length - 3} more` : '');
    }
    return 'N/A';
  };

  // Get teams display
  const getTeamsDisplay = (): string => {
    if (video.context_metadata?.teams && Array.isArray(video.context_metadata.teams)) {
      return video.context_metadata.teams
        .slice(0, 2)
        .map(t => t.name)
        .join(' vs ') + (video.context_metadata.teams.length > 2 ? ` +${video.context_metadata.teams.length - 2} more` : '');
    }
    if (video.teams && Array.isArray(video.teams)) {
      return video.teams.slice(0, 2).join(' vs ') + (video.teams.length > 2 ? ` +${video.teams.length - 2} more` : '');
    }
    return 'N/A';
  };

  const togglePlayPause = () => {
    if (videoRef.current) {
      if (isPlaying) {
        videoRef.current.pause();
      } else {
        videoRef.current.play();
      }
      setIsPlaying(!isPlaying);
    }
  };

  const toggleMute = () => {
    if (videoRef.current) {
      videoRef.current.muted = !isMuted;
      setIsMuted(!isMuted);
    }
  };

  const handleVolumeChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newVolume = parseFloat(e.target.value);
    setVolume(newVolume);
    if (videoRef.current) {
      videoRef.current.volume = newVolume;
      if (newVolume === 0) {
        setIsMuted(true);
      } else if (isMuted) {
        setIsMuted(false);
      }
    }
  };

  const handleTimeUpdate = () => {
    if (videoRef.current) {
      setCurrentTime(videoRef.current.currentTime);
    }
  };

  const handleLoadedMetadata = () => {
    if (videoRef.current) {
      setVideoDuration(videoRef.current.duration);
      setIsLoading(false);
      // Set initial volume
      videoRef.current.volume = volume;
    }
  };

  const handleSeek = (e: React.ChangeEvent<HTMLInputElement>) => {
    const newTime = parseFloat(e.target.value);
    setCurrentTime(newTime);
    if (videoRef.current) {
      videoRef.current.currentTime = newTime;
    }
  };

  const skipTime = (seconds: number) => {
    if (videoRef.current) {
      const newTime = Math.max(0, Math.min(videoDuration, currentTime + seconds));
      videoRef.current.currentTime = newTime;
      setCurrentTime(newTime);
    }
  };

  const formatTime = (time: number) => {
    const minutes = Math.floor(time / 60);
    const seconds = Math.floor(time % 60);
    return `${minutes}:${seconds.toString().padStart(2, '0')}`;
  };

  const openFullscreen = () => {
    // You can implement fullscreen modal here if needed
    console.log('Open fullscreen video player');
  };

  const playersDisplay = getPlayersDisplay();
  const teamsDisplay = getTeamsDisplay();

  return (
    <div className="w-96 bg-white border-l border-gray-200 h-full flex flex-col">
      {/* Header */}
      <div className="bg-gradient-to-r from-blue-600 to-purple-600 text-white p-4 flex-shrink-0">
        <div className="flex justify-between items-start">
          <div className="flex-1 min-w-0 mr-2">
            <h3 className="text-lg font-bold mb-1 truncate">{video.title || "Video Player"}</h3>
            <div className="text-sm text-blue-100 space-y-1">
              {video.context_metadata?.sport || video.sport && (
                <div className="flex items-center gap-2">
                  <span className="bg-blue-700 px-2 py-1 rounded text-xs">
                    {video.context_metadata?.sport || video.sport}
                  </span>
                  {video.technical_metadata?.duration || video.duration && (
                    <span className="bg-gray-600 px-2 py-1 rounded text-xs">
                      {video.technical_metadata?.duration || video.duration}
                    </span>
                  )}
                </div>
              )}
              {playersDisplay !== 'N/A' && (
                <div className="text-xs">
                  <span className="font-medium">Players:</span> {playersDisplay}
                </div>
              )}
              {teamsDisplay !== 'N/A' && (
                <div className="text-xs">
                  <span className="font-medium">Teams:</span> {teamsDisplay}
                </div>
              )}
            </div>
          </div>
          <button
            onClick={onClose}
            className="text-blue-100 hover:text-white p-1 rounded hover:bg-white hover:bg-opacity-20 transition-colors flex-shrink-0"
            aria-label="Close video player"
          >
            <X className="w-5 h-5" />
          </button>
        </div>
      </div>

      {/* Video Container */}
      <div className="relative bg-black flex-1 min-h-0">
        {isLoading && (
          <div className="absolute inset-0 flex items-center justify-center text-white z-10">
            <div className="text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-white mx-auto mb-2"></div>
              <p className="text-sm">Loading video...</p>
            </div>
          </div>
        )}
        
        {error && (
          <div className="absolute inset-0 flex items-center justify-center text-red-400 text-center p-4 z-10">
            <div>
              <p className="text-sm font-medium mb-2">Error loading video</p>
              <p className="text-xs text-red-300 mb-3">{error}</p>
              <button
                onClick={() => {
                  setError(null);
                  setIsLoading(true);
                  if (videoRef.current) {
                    videoRef.current.load();
                  }
                }}
                className="bg-red-600 hover:bg-red-700 text-white px-3 py-1 rounded text-xs transition-colors"
              >
                Retry
              </button>
            </div>
          </div>
        )}

        <video
          ref={videoRef}
          src={videoUrl}
          className="w-full h-full object-contain"
          onTimeUpdate={handleTimeUpdate}
          onLoadedMetadata={handleLoadedMetadata}
          onCanPlay={() => setIsLoading(false)}
          onError={(e) => {
            console.error('Video error:', e);
            setError("Failed to load video. Please check the video URL.");
            setIsLoading(false);
          }}
          onEnded={() => setIsPlaying(false)}
          poster={video.technical_metadata?.thumbnail_url}
          preload="metadata"
        />

        {/* Custom Controls Overlay */}
        {!isLoading && !error && (
          <div className="absolute bottom-0 left-0 right-0 bg-gradient-to-t from-black/90 via-black/50 to-transparent p-3">
            {/* Progress Bar */}
            <div className="mb-3">
              <input
                type="range"
                min={0}
                max={videoDuration || 0}
                value={currentTime}
                onChange={handleSeek}
                className="w-full h-1 bg-gray-600 rounded-lg appearance-none cursor-pointer"
                style={{
                  background: `linear-gradient(to right, #3b82f6 0%, #3b82f6 ${(currentTime / videoDuration) * 100}%, #4b5563 ${(currentTime / videoDuration) * 100}%, #4b5563 100%)`
                }}
              />
              <div className="flex justify-between text-xs text-gray-300 mt-1">
                <span>{formatTime(currentTime)}</span>
                <span>{formatTime(videoDuration)}</span>
              </div>
            </div>

            {/* Control Buttons */}
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <button
                  onClick={() => skipTime(-10)}
                  className="text-white hover:text-blue-400 transition-colors p-1"
                  aria-label="Skip back 10 seconds"
                >
                  <SkipBack className="w-4 h-4" />
                </button>
                
                <button
                  onClick={togglePlayPause}
                  className="bg-blue-600 hover:bg-blue-700 text-white rounded-full p-2 transition-colors"
                  aria-label={isPlaying ? "Pause" : "Play"}
                >
                  {isPlaying ? <Pause className="w-4 h-4" /> : <Play className="w-4 h-4" />}
                </button>
                
                <button
                  onClick={() => skipTime(10)}
                  className="text-white hover:text-blue-400 transition-colors p-1"
                  aria-label="Skip forward 10 seconds"
                >
                  <SkipForward className="w-4 h-4" />
                </button>
              </div>

              <div className="flex items-center gap-2">
                {/* Volume Control */}
                <button
                  onClick={toggleMute}
                  className="text-white hover:text-blue-400 transition-colors"
                  aria-label={isMuted ? "Unmute" : "Mute"}
                >
                  {isMuted ? <VolumeX className="w-4 h-4" /> : <Volume2 className="w-4 h-4" />}
                </button>
                <input
                  type="range"
                  min={0}
                  max={1}
                  step={0.1}
                  value={isMuted ? 0 : volume}
                  onChange={handleVolumeChange}
                  className="w-16 h-1 bg-gray-600 rounded-lg appearance-none cursor-pointer"
                  aria-label="Volume"
                />

                {/* Fullscreen Button */}
                <button
                  onClick={openFullscreen}
                  className="text-white hover:text-blue-400 transition-colors"
                  aria-label="Open in fullscreen"
                >
                  <Maximize2 className="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
        )}
      </div>

      {/* Video Details */}
      <div className="p-4 bg-gray-50 border-t border-gray-200 flex-shrink-0">
        <div className="space-y-2 text-sm">
          {video.technical_metadata?.resolution && (
            <div className="flex justify-between">
              <span className="text-gray-600">Resolution:</span>
              <span className="font-medium">{video.technical_metadata.resolution}</span>
            </div>
          )}
          {video.technical_metadata?.file_size && (
            <div className="flex justify-between">
              <span className="text-gray-600">Size:</span>
              <span className="font-medium">{video.technical_metadata.file_size}</span>
            </div>
          )}
          {video.video_type && (
            <div className="flex justify-between">
              <span className="text-gray-600">Type:</span>
              <span className="font-medium">{video.video_type}</span>
            </div>
          )}
        </div>
      </div>

      {/* Keyboard Shortcuts Help */}
      <div className="px-4 py-2 bg-gray-100 text-xs text-gray-500 border-t border-gray-200 flex-shrink-0">
        <span className="font-medium">Shortcuts:</span> Space (play/pause) • ← → (skip 10s) • M (mute)
      </div>
    </div>
  );
};

export default SidebarVideoPlayer;