// Updated VideoResultsTable.tsx
// @ts-nocheck
"use client";
import React, { useState } from 'react';
import { Play, Calendar, Users, Video as VideoIcon, Clock, FileText } from 'lucide-react';

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

interface VideoResultsTableProps {
  args: any;
  result: any;
  status: string;
  enableVerbose?: boolean;
  onVideoPlay?: (video: VideoData) => void; // New prop to handle video selection
}

const VideoResultsTable: React.FC<VideoResultsTableProps> = ({ 
  args, 
  result, 
  status, 
  enableVerbose = false,
  onVideoPlay // New prop
}) => {
  // Extract videos from result
  const videos: VideoData[] = result?.videos || result?.result || [];

  const handlePlayVideo = (video: VideoData) => {
    // Call the parent component's handler instead of opening modal
    if (onVideoPlay) {
      onVideoPlay(video);
    }
  };

  // Helper function to get video URL
  const getVideoUrl = (video: VideoData): string => {
    return video.technical_metadata?.source_uri || video.url || '';
  };

  // Helper function to get players list
  const getPlayersDisplay = (video: VideoData): string => {
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

  // Helper function to get teams display
  const getTeamsDisplay = (video: VideoData): string => {
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

  // Handle case where videos is undefined or not an array
  if (!videos || !Array.isArray(videos)) {
    return (
      <div className="flex flex-col gap-4 w-full max-w-6xl bg-gray-100 rounded-lg p-8 mb-4">
        <div className="text-black space-y-2">
          <h2 className="text-lg font-bold mb-4 flex items-center gap-2">
            <VideoIcon className="w-5 h-5" />
            Video Search Results
          </h2>
          <div className="text-center py-8">
            <VideoIcon className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600">No video data available</p>
            {status === 'executing' && (
              <div className="mt-4">
                <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
                <p className="text-sm text-gray-500 mt-2">Searching for videos...</p>
              </div>
            )}
          </div>
        </div>
      </div>
    );
  }

  // Handle case where videos array is empty
  if (videos.length === 0) {
    return (
      <div className="flex flex-col gap-4 w-full max-w-6xl bg-gray-100 rounded-lg p-8 mb-4">
        <div className="text-black space-y-2">
          <h2 className="text-lg font-bold mb-4 flex items-center gap-2">
            <VideoIcon className="w-5 h-5" />
            Video Search Results
          </h2>
          <div className="text-center py-8">
            <VideoIcon className="w-12 h-12 text-gray-400 mx-auto mb-4" />
            <p className="text-gray-600">No videos found for your search</p>
            <p className="text-sm text-gray-500 mt-2">Try adjusting your search criteria</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-4 w-full max-w-6xl bg-gray-100 rounded-lg p-8 mb-4">
      <div className="text-black space-y-2">
        <h2 className="text-lg font-bold mb-4 flex items-center gap-2">
          <VideoIcon className="w-5 h-5" />
          Video Search Results ({videos.length} found)
        </h2>

        {/* Search Query Info */}
        {args?.query && (
          <div className="bg-blue-50 border border-blue-200 rounded-lg p-3 mb-4">
            <div className="flex items-center gap-2">
              <FileText className="w-4 h-4 text-blue-600" />
              <span className="text-sm font-medium text-blue-800">Search Query:</span>
              <span className="text-sm text-blue-700">{args.query}</span>
            </div>
          </div>
        )}

        {/* Videos Table */}
        <div className="bg-white rounded-lg shadow-sm overflow-hidden">
          <div className="overflow-x-auto">
            <table className="w-full">
              <thead className="bg-gray-50">
                <tr>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Video
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Players
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Teams
                  </th>
                  <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                    Action
                  </th>
                </tr>
              </thead>
              <tbody className="bg-white divide-y divide-gray-200">
                {videos.map((video, index) => (
                  <tr key={index} className="hover:bg-gray-50 transition-colors">
                    <td className="px-6 py-4">
                      <div className="flex items-start space-x-3">
                        <div className="flex-shrink-0">
                          <div className="w-12 h-8 bg-gray-200 rounded flex items-center justify-center">
                            <VideoIcon className="w-5 h-5 text-gray-500" />
                          </div>
                        </div>
                        <div className="min-w-0 flex-1">
                          <p className="text-sm font-medium text-gray-900 line-clamp-2">
                            {video.title || 'Untitled Video'}
                          </p>
                          <div className="text-xs text-gray-500 mt-1">
                            {video.technical_metadata?.resolution && (
                              <span className="mr-2">{video.technical_metadata.resolution}</span>
                            )}
                            {video.technical_metadata?.file_size && (
                              <span>{video.technical_metadata.file_size}</span>
                            )}
                          </div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm text-gray-900">
                        <div className="line-clamp-2">
                          {getPlayersDisplay(video)}
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <div className="text-sm text-gray-900">
                        {getTeamsDisplay(video)}
                      </div>
                    </td>
                    <td className="px-6 py-4">
                      <button
                        onClick={() => handlePlayVideo(video)}
                        disabled={!getVideoUrl(video)}
                        className={`inline-flex items-center px-3 py-2 border border-transparent text-sm leading-4 font-medium rounded-md transition-colors ${
                          getVideoUrl(video)
                            ? 'text-white bg-blue-600 hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500'
                            : 'text-gray-400 bg-gray-200 cursor-not-allowed'
                        }`}
                      >
                        <Play className="w-4 h-4 mr-1" />
                        Play
                      </button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>

        {/* Raw Data (collapsed by default) */}
        {enableVerbose && (
          <details className="mt-6">
            <summary className="cursor-pointer text-sm font-medium text-gray-700 hover:text-gray-900">
              Show Raw Video Data
            </summary>
            <pre className="text-sm mt-2 bg-gray-50 p-4 rounded overflow-x-auto max-h-96">
              {JSON.stringify(videos, null, 2)}
            </pre>
          </details>
        )}
      </div>
    </div>
  );
};

export default VideoResultsTable;