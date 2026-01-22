"""
Tests for YtDlpTrendingCollector
"""

import pytest
from youtube_trending_mcp.ytdlp_collector import YtDlpTrendingCollector


class TestYtDlpTrendingCollector:
    """Test cases for YtDlpTrendingCollector"""
    
    @pytest.fixture
    def collector(self):
        """Create collector instance"""
        return YtDlpTrendingCollector(timeout=60)
    
    def test_initialization(self, collector):
        """Test collector initializes correctly"""
        assert collector is not None
        assert collector.timeout == 60
    
    def test_animal_keywords_defined(self, collector):
        """Test that animal keywords are defined"""
        assert len(collector.ANIMAL_KEYWORDS) > 0
        assert "cute animals" in collector.ANIMAL_KEYWORDS
    
    def test_category_keywords_defined(self, collector):
        """Test that category keywords are defined"""
        assert "pets" in collector.CATEGORY_KEYWORDS
        assert "music" in collector.CATEGORY_KEYWORDS
        assert "gaming" in collector.CATEGORY_KEYWORDS
    
    def test_normalize_video_data(self, collector):
        """Test video data normalization"""
        raw_video = {
            "id": "test123",
            "title": "Test Video",
            "uploader": "Test Channel",
            "channel_id": "UC123",
            "view_count": 1000,
            "like_count": 100,
            "upload_date": "20240101",
            "duration": 300,
            "description": "Test description",
            "categories": ["Entertainment"],
            "tags": ["test", "video"],
            "thumbnail": "https://example.com/thumb.jpg"
        }
        
        normalized = collector._normalize_video_data(raw_video)
        
        assert normalized["video_id"] == "test123"
        assert normalized["title"] == "Test Video"
        assert normalized["channel"] == "Test Channel"
        assert normalized["views"] == 1000
        assert normalized["likes"] == 100
        assert "url" in normalized
    
    def test_normalize_video_data_missing_fields(self, collector):
        """Test normalization handles missing fields"""
        raw_video = {
            "id": "test123",
            "title": "Test Video"
        }
        
        normalized = collector._normalize_video_data(raw_video)
        
        assert normalized["video_id"] == "test123"
        assert normalized["views"] == 0
        assert normalized["likes"] == 0
        assert normalized["categories"] == []
        assert normalized["tags"] == []


class TestYtDlpIntegration:
    """Integration tests (require yt-dlp and network)"""
    
    @pytest.fixture
    def collector(self):
        """Create collector instance"""
        return YtDlpTrendingCollector(timeout=120)
    
    @pytest.mark.slow
    def test_search_trending_returns_results(self, collector):
        """Test that search returns results (integration test)"""
        videos = collector.search_trending(
            keywords=["cute animals"],
            max_results=5
        )
        
        # Should return some videos
        assert isinstance(videos, list)
        # May be empty if network issues
        if len(videos) > 0:
            assert "video_id" in videos[0]
            assert "title" in videos[0]
    
    @pytest.mark.slow
    def test_search_by_category(self, collector):
        """Test category search"""
        videos = collector.search_by_category(
            category="pets",
            max_results=5
        )
        
        assert isinstance(videos, list)
    
    @pytest.mark.slow
    def test_get_video_metadata(self, collector):
        """Test getting single video metadata"""
        metadata = collector.get_video_metadata("dQw4w9WgXcQ")
        
        if metadata is not None:
            assert metadata["video_id"] == "dQw4w9WgXcQ"
            assert "title" in metadata
            assert "views" in metadata
    
    @pytest.mark.slow
    def test_search_custom_query(self, collector):
        """Test custom query search (LLM-driven)"""
        videos = collector.search_custom_query(
            query="python programming tutorials",
            max_results=5
        )
        
        assert isinstance(videos, list)
        if len(videos) > 0:
            assert "video_id" in videos[0]
            assert "title" in videos[0]
            assert "views" in videos[0]
    
    @pytest.mark.slow
    def test_search_custom_query_sort_by_views(self, collector):
        """Test custom query with view count sorting"""
        videos = collector.search_custom_query(
            query="cooking recipes",
            max_results=10,
            sort_by="views"
        )
        
        assert isinstance(videos, list)
        if len(videos) >= 2:
            assert videos[0]["views"] >= videos[1]["views"]
    
    @pytest.mark.slow
    def test_search_by_custom_category(self, collector):
        """Test search_by_category with custom (non-predefined) category"""
        videos = collector.search_by_category(
            category="meditation music",
            max_results=5
        )
        
        assert isinstance(videos, list)
