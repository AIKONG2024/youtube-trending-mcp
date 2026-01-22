"""
Tests for VideoFilter
"""

import pytest
from youtube_trending_mcp.filters import VideoFilter


class TestVideoFilter:
    """Test cases for VideoFilter"""
    
    @pytest.fixture
    def sample_videos(self):
        """Sample video data for testing"""
        return [
            {
                "video_id": "vid1",
                "title": "Cute puppies playing",
                "views": 100000,
                "likes": 5000,
                "duration": 300,
                "categories": ["Pets & Animals"],
                "description": "Adorable puppies"
            },
            {
                "video_id": "vid2",
                "title": "Cat compilation 2024",
                "views": 50000,
                "likes": 2000,
                "duration": 600,
                "categories": ["Pets & Animals", "Entertainment"],
                "description": "Funny cats"
            },
            {
                "video_id": "vid3",
                "title": "Gaming stream highlights",
                "views": 200000,
                "likes": 10000,
                "duration": 1800,
                "categories": ["Gaming"],
                "description": "Epic gameplay"
            },
            {
                "video_id": "vid4",
                "title": "Clickbait fake video",
                "views": 1000,
                "likes": 10,
                "duration": 60,
                "categories": ["Entertainment"],
                "description": "fake content"
            }
        ]
    
    def test_filter_by_views_min(self, sample_videos):
        """Test filtering by minimum views"""
        filtered = VideoFilter.filter_by_views(
            sample_videos,
            min_views=60000
        )
        
        assert len(filtered) == 2
        assert all(v["views"] >= 60000 for v in filtered)
    
    def test_filter_by_views_max(self, sample_videos):
        """Test filtering by maximum views"""
        filtered = VideoFilter.filter_by_views(
            sample_videos,
            max_views=100000
        )
        
        assert len(filtered) == 3
        assert all(v["views"] <= 100000 for v in filtered)
    
    def test_filter_by_views_range(self, sample_videos):
        """Test filtering by view range"""
        filtered = VideoFilter.filter_by_views(
            sample_videos,
            min_views=50000,
            max_views=150000
        )
        
        assert len(filtered) == 2
    
    def test_filter_by_likes(self, sample_videos):
        """Test filtering by minimum likes"""
        filtered = VideoFilter.filter_by_likes(
            sample_videos,
            min_likes=3000
        )
        
        assert len(filtered) == 2
        assert all(v["likes"] >= 3000 for v in filtered)
    
    def test_filter_by_categories(self, sample_videos):
        """Test filtering by categories"""
        filtered = VideoFilter.filter_by_categories(
            sample_videos,
            categories=["Pets"]
        )
        
        assert len(filtered) == 2  # vid1 and vid2 have Pets & Animals
    
    def test_filter_by_keywords_include(self, sample_videos):
        """Test filtering with include keywords"""
        filtered = VideoFilter.filter_by_keywords(
            sample_videos,
            include_keywords=["puppies", "cats"]
        )
        
        assert len(filtered) == 2  # vid1 and vid2
    
    def test_filter_by_keywords_exclude(self, sample_videos):
        """Test filtering with exclude keywords"""
        filtered = VideoFilter.filter_by_keywords(
            sample_videos,
            exclude_keywords=["fake", "clickbait"]
        )
        
        assert len(filtered) == 3  # All except vid4
    
    def test_filter_by_duration(self, sample_videos):
        """Test filtering by duration"""
        filtered = VideoFilter.filter_by_duration(
            sample_videos,
            min_duration=100,
            max_duration=1000
        )
        
        assert len(filtered) == 2  # vid1 and vid2
    
    def test_apply_all_filters(self, sample_videos):
        """Test applying multiple filters at once"""
        filtered = VideoFilter.apply_filters(
            sample_videos,
            min_views=40000,
            min_likes=1000,
            exclude_keywords=["gaming"],
            max_duration=1000
        )
        
        assert len(filtered) == 2  # vid1 and vid2
    
    def test_empty_list_returns_empty(self):
        """Test that empty input returns empty output"""
        filtered = VideoFilter.filter_by_views([], min_views=100)
        assert filtered == []
    
    def test_no_filters_returns_original(self, sample_videos):
        """Test that no filters returns original list"""
        filtered = VideoFilter.apply_filters(sample_videos)
        assert len(filtered) == len(sample_videos)
