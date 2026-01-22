"""
YouTube Trending MCP Server

A Model Context Protocol server for collecting trending YouTube videos
without web scraping. Uses yt-dlp for stable, API-based data collection.

Author: AIKONG2024
License: MIT
"""

__version__ = "1.0.0"
__author__ = "AIKONG2024"
__license__ = "MIT"

from .ytdlp_collector import YtDlpTrendingCollector
from .rss_collector import YouTubeRSSCollector
from .filters import VideoFilter

__all__ = [
    "YtDlpTrendingCollector",
    "YouTubeRSSCollector",
    "VideoFilter",
]
