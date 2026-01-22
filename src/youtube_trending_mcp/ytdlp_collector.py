"""
yt-dlp based YouTube video collector

Stable, API-based collection without web scraping.
"""

import subprocess
import json
from typing import List, Dict, Optional
from datetime import datetime


class YtDlpTrendingCollector:
    """yt-dlp wrapper for trending video collection"""
    
    DEFAULT_KEYWORDS = ['trending', 'viral', 'popular']
    
    CATEGORY_KEYWORDS = {
        "all": [],
        "pets": ['cute animals', 'funny pets', 'dogs', 'cats', 'puppies', 'kittens'],
        "music": ['music video', 'official music video', 'new music 2024'],
        "gaming": ['gaming', 'gameplay', 'lets play', 'game review'],
        "entertainment": ['entertainment', 'comedy', 'funny videos', 'viral']
    }
    
    SORT_OPTIONS = ["relevance", "views", "date"]
    
    def __init__(self, timeout: int = 120):
        """
        Initialize collector
        
        Args:
            timeout: Command timeout in seconds
        """
        self.timeout = timeout
        self._check_ytdlp_installed()
    
    def _check_ytdlp_installed(self) -> None:
        """Check if yt-dlp is installed"""
        try:
            subprocess.run(
                ['yt-dlp', '--version'],
                capture_output=True,
                check=True,
                timeout=10
            )
        except (subprocess.CalledProcessError, FileNotFoundError):
            raise RuntimeError(
                "yt-dlp is not installed. "
                "Install with: pip install yt-dlp"
            )
    
    def search_trending(
        self,
        keywords: Optional[List[str]] = None,
        max_results: int = 50,
        region: str = "US"
    ) -> List[Dict]:
        """
        Search trending videos using yt-dlp
        
        Args:
            keywords: Search keywords (default: ANIMAL_KEYWORDS)
            max_results: Maximum results to return
            region: Region code
        
        Returns:
            List of video metadata dictionaries
        """
        keywords = keywords or self.DEFAULT_KEYWORDS
        all_videos = {}
        
        # Limit keywords to avoid too many requests
        keywords_to_search = keywords[:5] if len(keywords) > 5 else keywords
        
        for keyword in keywords_to_search:
            videos = self._search_single_query(keyword, max_results=min(20, max_results))
            
            for video in videos:
                video_id = video.get('id')
                if video_id and video_id not in all_videos:
                    all_videos[video_id] = self._normalize_video_data(video)
        
        # Sort by view count
        sorted_videos = sorted(
            all_videos.values(),
            key=lambda x: x.get('views', 0),
            reverse=True
        )
        
        return sorted_videos[:max_results]
    
    def search_by_category(
        self,
        category: str = "all",
        max_results: int = 50,
        region: str = "US"
    ) -> List[Dict]:
        """
        Search videos by category
        
        Args:
            category: Video category (pets, music, gaming, entertainment, all)
            max_results: Maximum results to return
            region: Region code
        
        Returns:
            List of video metadata dictionaries
        """
        if category in self.CATEGORY_KEYWORDS:
            keywords = self.CATEGORY_KEYWORDS[category]
            if not keywords:
                keywords = ["trending", "viral", "popular"]
        else:
            keywords = [category]
        
        return self.search_trending(keywords=keywords, max_results=max_results, region=region)
    
    def search_custom_query(
        self,
        query: str,
        max_results: int = 20,
        sort_by: str = "relevance"
    ) -> List[Dict]:
        """
        Search videos with custom user query (LLM-driven)
        
        Args:
            query: User-provided search query (any topic)
            max_results: Maximum results to return
            sort_by: Sort order - 'relevance', 'views', or 'date'
        
        Returns:
            List of normalized video metadata dictionaries
        """
        videos = self._search_single_query(query, max_results=max_results)
        
        normalized = [self._normalize_video_data(v) for v in videos]
        
        if sort_by == "views":
            normalized = sorted(normalized, key=lambda x: x.get('views', 0), reverse=True)
        elif sort_by == "date":
            normalized = sorted(normalized, key=lambda x: x.get('upload_date', '') or '', reverse=True)
        
        return normalized
    
    def _search_single_query(
        self,
        query: str,
        max_results: int = 20
    ) -> List[Dict]:
        """
        Execute single yt-dlp search
        
        Args:
            query: Search query
            max_results: Maximum results
        
        Returns:
            List of raw video dictionaries from yt-dlp
        """
        cmd = [
            'yt-dlp',
            f'ytsearch{max_results}:{query}',
            '--dump-json',
            '--skip-download',
            '--no-warnings',
            '--no-check-certificate',
            '--ignore-errors',
            '--flat-playlist'
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            videos = []
            for line in result.stdout.strip().split('\n'):
                if line:
                    try:
                        video = json.loads(line)
                        # Skip playlist entries, only keep videos
                        if video.get('_type') != 'playlist':
                            videos.append(video)
                    except json.JSONDecodeError:
                        continue
            
            return videos
        
        except subprocess.TimeoutExpired:
            print(f"Timeout searching for: {query}")
            return []
        except Exception as e:
            print(f"Error searching {query}: {e}")
            return []
    
    def get_video_metadata(self, video_id: str) -> Optional[Dict]:
        """
        Get metadata for specific video
        
        Args:
            video_id: YouTube video ID
        
        Returns:
            Video metadata dictionary or None
        """
        url = f"https://www.youtube.com/watch?v={video_id}"
        
        cmd = [
            'yt-dlp',
            '--dump-json',
            '--skip-download',
            '--no-warnings',
            '--no-check-certificate',
            url
        ]
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=self.timeout
            )
            
            if result.stdout.strip():
                video = json.loads(result.stdout.strip())
                return self._normalize_video_data(video)
            
            return None
        
        except Exception as e:
            print(f"Error getting metadata for {video_id}: {e}")
            return None
    
    def _normalize_video_data(self, video: Dict) -> Dict:
        """
        Normalize yt-dlp output to consistent format
        
        Args:
            video: Raw yt-dlp video dictionary
        
        Returns:
            Normalized video metadata
        """
        video_id = video.get('id') or video.get('url', '').split('=')[-1]
        
        return {
            'video_id': video_id,
            'title': video.get('title', 'Unknown'),
            'channel': video.get('uploader') or video.get('channel') or 'Unknown',
            'channel_id': video.get('channel_id') or video.get('uploader_id'),
            'views': video.get('view_count') or 0,
            'likes': video.get('like_count') or 0,
            'upload_date': video.get('upload_date'),
            'duration': video.get('duration') or 0,
            'description': (video.get('description') or '')[:1000],
            'categories': video.get('categories') or [],
            'tags': (video.get('tags') or [])[:20],
            'thumbnail': video.get('thumbnail'),
            'url': f"https://www.youtube.com/watch?v={video_id}"
        }
