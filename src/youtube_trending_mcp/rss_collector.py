"""
YouTube RSS feed collector (fallback data source)
"""

import feedparser
from typing import List, Dict, Optional


class YouTubeRSSCollector:
    """YouTube RSS feed collector for fallback data"""
    
    def get_channel_feed(self, channel_id: str) -> List[Dict]:
        """
        Get channel RSS feed
        
        Args:
            channel_id: YouTube channel ID (starts with UC...)
        
        Returns:
            List of video dictionaries from RSS
        """
        feed_url = f"https://www.youtube.com/feeds/videos.xml?channel_id={channel_id}"
        
        try:
            feed = feedparser.parse(feed_url)
            videos = []
            
            for entry in feed.entries:
                # Extract video ID from different possible locations
                video_id = None
                if hasattr(entry, 'yt_videoid'):
                    video_id = entry.yt_videoid
                elif hasattr(entry, 'id'):
                    video_id = entry.id.split(':')[-1] if ':' in entry.id else entry.id
                
                if video_id:
                    videos.append({
                        'video_id': video_id,
                        'title': entry.title,
                        'channel': entry.author if hasattr(entry, 'author') else 'Unknown',
                        'published': entry.published if hasattr(entry, 'published') else None,
                        'link': entry.link,
                        'description': entry.summary if hasattr(entry, 'summary') else '',
                        'thumbnail': self._extract_thumbnail(entry),
                        'url': f"https://www.youtube.com/watch?v={video_id}"
                    })
            
            return videos
        
        except Exception as e:
            print(f"Error fetching RSS feed for channel {channel_id}: {e}")
            return []
    
    def get_playlist_feed(self, playlist_id: str) -> List[Dict]:
        """
        Get playlist RSS feed
        
        Args:
            playlist_id: YouTube playlist ID
        
        Returns:
            List of video dictionaries from RSS
        """
        feed_url = f"https://www.youtube.com/feeds/videos.xml?playlist_id={playlist_id}"
        
        try:
            feed = feedparser.parse(feed_url)
            videos = []
            
            for entry in feed.entries:
                video_id = None
                if hasattr(entry, 'yt_videoid'):
                    video_id = entry.yt_videoid
                elif hasattr(entry, 'id'):
                    video_id = entry.id.split(':')[-1] if ':' in entry.id else entry.id
                
                if video_id:
                    videos.append({
                        'video_id': video_id,
                        'title': entry.title,
                        'channel': entry.author if hasattr(entry, 'author') else 'Unknown',
                        'published': entry.published if hasattr(entry, 'published') else None,
                        'link': entry.link,
                        'description': entry.summary if hasattr(entry, 'summary') else '',
                        'url': f"https://www.youtube.com/watch?v={video_id}"
                    })
            
            return videos
        
        except Exception as e:
            print(f"Error fetching RSS feed for playlist {playlist_id}: {e}")
            return []
    
    def _extract_thumbnail(self, entry) -> Optional[str]:
        """Extract thumbnail URL from RSS entry"""
        # Try media_thumbnail
        if hasattr(entry, 'media_thumbnail'):
            thumbnails = entry.media_thumbnail
            if thumbnails and len(thumbnails) > 0:
                return thumbnails[0].get('url')
        
        # Try media_content
        if hasattr(entry, 'media_content'):
            for content in entry.media_content:
                if content.get('type', '').startswith('image'):
                    return content.get('url')
        
        return None
