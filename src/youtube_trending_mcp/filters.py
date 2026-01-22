"""
Video filtering utilities
"""

from typing import List, Dict, Optional


class VideoFilter:
    """Video filtering by various criteria"""
    
    @staticmethod
    def filter_by_views(
        videos: List[Dict],
        min_views: Optional[int] = None,
        max_views: Optional[int] = None
    ) -> List[Dict]:
        """
        Filter videos by view count range
        
        Args:
            videos: List of video dictionaries
            min_views: Minimum view count
            max_views: Maximum view count
        
        Returns:
            Filtered video list
        """
        filtered = videos.copy()
        
        if min_views is not None:
            filtered = [v for v in filtered if v.get('views', 0) >= min_views]
        
        if max_views is not None:
            filtered = [v for v in filtered if v.get('views', 0) <= max_views]
        
        return filtered
    
    @staticmethod
    def filter_by_likes(
        videos: List[Dict],
        min_likes: Optional[int] = None
    ) -> List[Dict]:
        """
        Filter videos by like count
        
        Args:
            videos: List of video dictionaries
            min_likes: Minimum like count
        
        Returns:
            Filtered video list
        """
        if min_likes is None:
            return videos
        
        return [v for v in videos if v.get('likes', 0) >= min_likes]
    
    @staticmethod
    def filter_by_categories(
        videos: List[Dict],
        categories: List[str]
    ) -> List[Dict]:
        """
        Filter videos by categories
        
        Args:
            videos: List of video dictionaries
            categories: Required categories
        
        Returns:
            Filtered video list
        """
        if not categories:
            return videos
        
        filtered = []
        
        for video in videos:
            video_categories = video.get('categories', [])
            # Case-insensitive category matching
            if any(
                any(cat.lower() in vc.lower() for vc in video_categories)
                for cat in categories
            ):
                filtered.append(video)
        
        return filtered
    
    @staticmethod
    def filter_by_keywords(
        videos: List[Dict],
        include_keywords: Optional[List[str]] = None,
        exclude_keywords: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        Filter videos by keywords in title/description
        
        Args:
            videos: List of video dictionaries
            include_keywords: Keywords that must be present
            exclude_keywords: Keywords to exclude
        
        Returns:
            Filtered video list
        """
        filtered = videos.copy()
        
        # Include filter
        if include_keywords:
            new_filtered = []
            for video in filtered:
                title = video.get('title', '').lower()
                description = video.get('description', '').lower()
                text = f"{title} {description}"
                
                if any(kw.lower() in text for kw in include_keywords):
                    new_filtered.append(video)
            filtered = new_filtered
        
        # Exclude filter
        if exclude_keywords:
            new_filtered = []
            for video in filtered:
                title = video.get('title', '').lower()
                description = video.get('description', '').lower()
                text = f"{title} {description}"
                
                if not any(kw.lower() in text for kw in exclude_keywords):
                    new_filtered.append(video)
            filtered = new_filtered
        
        return filtered
    
    @staticmethod
    def filter_by_duration(
        videos: List[Dict],
        min_duration: Optional[int] = None,
        max_duration: Optional[int] = None
    ) -> List[Dict]:
        """
        Filter by duration range (in seconds)
        
        Args:
            videos: List of video dictionaries
            min_duration: Minimum duration in seconds
            max_duration: Maximum duration in seconds
        
        Returns:
            Filtered video list
        """
        filtered = videos.copy()
        
        if min_duration is not None:
            filtered = [
                v for v in filtered
                if v.get('duration', 0) >= min_duration
            ]
        
        if max_duration is not None:
            filtered = [
                v for v in filtered
                if v.get('duration', float('inf')) <= max_duration
            ]
        
        return filtered
    
    @classmethod
    def apply_filters(
        cls,
        videos: List[Dict],
        min_views: Optional[int] = None,
        max_views: Optional[int] = None,
        min_likes: Optional[int] = None,
        min_duration: Optional[int] = None,
        max_duration: Optional[int] = None,
        categories: Optional[List[str]] = None,
        include_keywords: Optional[List[str]] = None,
        exclude_keywords: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        Apply all filters at once
        
        Args:
            videos: List of video dictionaries
            Various filter parameters
        
        Returns:
            Filtered video list
        """
        filtered = videos.copy()
        
        # Apply each filter
        filtered = cls.filter_by_views(filtered, min_views, max_views)
        filtered = cls.filter_by_likes(filtered, min_likes)
        filtered = cls.filter_by_duration(filtered, min_duration, max_duration)
        filtered = cls.filter_by_categories(filtered, categories or [])
        filtered = cls.filter_by_keywords(filtered, include_keywords, exclude_keywords)
        
        return filtered
