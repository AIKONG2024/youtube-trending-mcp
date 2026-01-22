"""
MCP Server for YouTube Trending Collection

Provides MCP tools for searching, filtering, and collecting
trending YouTube videos using yt-dlp (no web scraping).
"""

import os
import json
import asyncio
from typing import List, Dict, Optional
from datetime import datetime
from pathlib import Path

from mcp.server import Server
from mcp.types import Tool, TextContent
from mcp.server.stdio import stdio_server

from .ytdlp_collector import YtDlpTrendingCollector
from .rss_collector import YouTubeRSSCollector
from .filters import VideoFilter
from .database import DatabaseHelper
from .validators import QueryValidator, SortValidator, ResultCountValidator

# Configuration
DATA_DIR = Path(os.getenv("DATA_DIR", "data"))
SQLITE_DB_PATH = os.getenv("SQLITE_DB_PATH", str(DATA_DIR / "youtube_collection.db"))

# Initialize server and components
server = Server("youtube-trending-mcp")

# Lazy initialization for collectors
_ytdlp_collector = None
_rss_collector = None
_video_filter = None
_db_helper = None


def get_ytdlp_collector():
    global _ytdlp_collector
    if _ytdlp_collector is None:
        _ytdlp_collector = YtDlpTrendingCollector()
    return _ytdlp_collector


def get_rss_collector():
    global _rss_collector
    if _rss_collector is None:
        _rss_collector = YouTubeRSSCollector()
    return _rss_collector


def get_video_filter():
    global _video_filter
    if _video_filter is None:
        _video_filter = VideoFilter()
    return _video_filter


def get_db_helper():
    global _db_helper
    if _db_helper is None:
        _db_helper = DatabaseHelper(SQLITE_DB_PATH)
    return _db_helper


@server.list_tools()
async def list_tools() -> List[Tool]:
    """List available MCP tools"""
    return [
        Tool(
            name="search_trending_videos",
            description="Search trending YouTube videos by category using yt-dlp. No API key required. Supports predefined categories (pets, music, gaming, entertainment) or custom topics.",
            inputSchema={
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "Video category: 'all', 'pets', 'music', 'gaming', 'entertainment', or any custom topic (e.g., 'cooking', 'technology')",
                        "default": "all"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum number of videos to return (1-100)",
                        "default": 20,
                        "minimum": 1,
                        "maximum": 100
                    },
                    "region": {
                        "type": "string",
                        "description": "Region code (US, KR, GB, etc.)",
                        "default": "US"
                    }
                }
            }
        ),

        Tool(
            name="get_video_metadata",
            description="Get detailed metadata for a specific YouTube video.",
            inputSchema={
                "type": "object",
                "properties": {
                    "video_id": {
                        "type": "string",
                        "description": "YouTube video ID (11 characters)"
                    }
                },
                "required": ["video_id"]
            }
        ),
        Tool(
            name="collect_daily_ranking",
            description="Collect daily trending videos and save rankings to database and JSON file.",
            inputSchema={
                "type": "object",
                "properties": {
                    "category": {
                        "type": "string",
                        "description": "Category to collect",
                        "default": "all"
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Number of videos to collect",
                        "default": 50
                    },
                    "save_to_db": {
                        "type": "boolean",
                        "description": "Whether to save to database",
                        "default": True
                    },
                    "save_to_json": {
                        "type": "boolean",
                        "description": "Whether to save JSON snapshot",
                        "default": True
                    }
                }
            }
        ),
        Tool(
            name="get_youtube_rss_feed",
            description="Fetch YouTube RSS feed for a channel or playlist (fallback data source).",
            inputSchema={
                "type": "object",
                "properties": {
                    "channel_id": {
                        "type": "string",
                        "description": "YouTube channel ID (starts with UC...)"
                    },
                    "playlist_id": {
                        "type": "string",
                        "description": "YouTube playlist ID"
                    }
                }
            }
        ),
        Tool(
            name="filter_videos",
            description="Filter videos by various criteria (views, likes, duration, keywords).",
            inputSchema={
                "type": "object",
                "properties": {
                    "videos": {
                        "type": "array",
                        "items": {"type": "object"},
                        "description": "List of video dictionaries to filter"
                    },
                    "min_views": {
                        "type": "integer",
                        "description": "Minimum view count"
                    },
                    "min_likes": {
                        "type": "integer",
                        "description": "Minimum like count"
                    },
                    "max_duration": {
                        "type": "integer",
                        "description": "Maximum duration in seconds"
                    },
                    "exclude_keywords": {
                        "type": "array",
                        "items": {"type": "string"},
                        "description": "Keywords to exclude"
                    }
                },
                "required": ["videos"]
            }
        ),
        Tool(
            name="search_custom_videos",
            description="Search YouTube videos with any custom query. LLM can specify any topic without restrictions. Use this for flexible, user-driven video discovery.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "Custom search query (e.g., 'cooking recipes', 'AI tutorials', 'space documentaries')",
                        "minLength": 1,
                        "maxLength": 200
                    },
                    "max_results": {
                        "type": "integer",
                        "description": "Maximum videos to return (1-100)",
                        "default": 20,
                        "minimum": 1,
                        "maximum": 100
                    },
                    "min_views": {
                        "type": "integer",
                        "description": "Minimum view count filter (0 = no filter)",
                        "default": 0,
                        "minimum": 0
                    },
                    "sort_by": {
                        "type": "string",
                        "description": "Sort order for results",
                        "enum": ["relevance", "views", "date"],
                        "default": "relevance"
                    }
                },
                "required": ["query"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> List[TextContent]:
    """Handle tool calls"""
    
    try:
        if name == "search_trending_videos":
            result = await search_trending_videos(
                category=arguments.get("category", "all"),
                max_results=arguments.get("max_results", 20),
                region=arguments.get("region", "US")
            )
        

        
        elif name == "get_video_metadata":
            result = await get_video_metadata(
                video_id=arguments["video_id"]
            )
        
        elif name == "collect_daily_ranking":
            result = await collect_daily_ranking(
                category=arguments.get("category", "all"),
                max_results=arguments.get("max_results", 50),
                save_to_db=arguments.get("save_to_db", True),
                save_to_json=arguments.get("save_to_json", True)
            )
        
        elif name == "get_youtube_rss_feed":
            result = await get_youtube_rss_feed(
                channel_id=arguments.get("channel_id"),
                playlist_id=arguments.get("playlist_id")
            )
        
        elif name == "filter_videos":
            result = await filter_videos(
                videos=arguments["videos"],
                min_views=arguments.get("min_views"),
                min_likes=arguments.get("min_likes"),
                max_duration=arguments.get("max_duration"),
                exclude_keywords=arguments.get("exclude_keywords")
            )
        
        elif name == "search_custom_videos":
            result = await search_custom_videos(
                query=arguments["query"],
                max_results=arguments.get("max_results", 20),
                min_views=arguments.get("min_views", 0),
                sort_by=arguments.get("sort_by", "relevance")
            )
        
        else:
            result = {"error": f"Unknown tool: {name}"}
        
        return [TextContent(
            type="text",
            text=json.dumps(result, indent=2, ensure_ascii=False)
        )]
    
    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e),
            "tool": name
        }
        return [TextContent(
            type="text",
            text=json.dumps(error_result, indent=2)
        )]


async def search_trending_videos(
    category: str = "all",
    max_results: int = 20,
    region: str = "US"
) -> Dict:
    """Search trending videos by category"""
    try:
        collector = get_ytdlp_collector()
        videos = collector.search_by_category(
            category=category,
            max_results=max_results,
            region=region
        )
        
        return {
            "success": True,
            "count": len(videos),
            "category": category,
            "region": region,
            "videos": videos,
            "source": "yt-dlp",
            "collected_at": datetime.now().isoformat()
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "category": category
        }


async def get_video_metadata(video_id: str) -> Dict:
    """Get metadata for specific video"""
    try:
        collector = get_ytdlp_collector()
        metadata = collector.get_video_metadata(video_id)
        
        if metadata:
            return {
                "success": True,
                "video": metadata
            }
        else:
            return {
                "success": False,
                "error": f"Video {video_id} not found"
            }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "video_id": video_id
        }


async def collect_daily_ranking(
    category: str = "all",
    max_results: int = 50,
    save_to_db: bool = True,
    save_to_json: bool = True
) -> Dict:
    """Collect daily ranking and save"""
    try:
        # Search videos
        search_result = await search_trending_videos(
            category=category,
            max_results=max_results
        )
        
        if not search_result.get("success"):
            return search_result
        
        videos = search_result["videos"]
        output_paths = []
        
        # Save to JSON
        if save_to_json:
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            rankings_dir = DATA_DIR / "rankings"
            rankings_dir.mkdir(parents=True, exist_ok=True)
            
            date_str = datetime.now().strftime("%Y-%m-%d")
            json_path = rankings_dir / f"{date_str}_{category}.json"
            
            rankings_data = {
                "date": datetime.now().isoformat(),
                "category": category,
                "source": "yt-dlp",
                "count": len(videos),
                "videos": videos
            }
            
            with open(json_path, "w", encoding="utf-8") as f:
                json.dump(rankings_data, f, indent=2, ensure_ascii=False)
            
            output_paths.append(str(json_path))
        
        # Save to database
        if save_to_db:
            db = get_db_helper()
            db_path = db.save_rankings(videos, category)
            output_paths.append(db_path)
        
        return {
            "success": True,
            "count": len(videos),
            "category": category,
            "output_paths": output_paths,
            "collected_at": datetime.now().isoformat()
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "category": category
        }


async def get_youtube_rss_feed(
    channel_id: Optional[str] = None,
    playlist_id: Optional[str] = None
) -> Dict:
    """Fetch YouTube RSS feed"""
    try:
        if not channel_id and not playlist_id:
            return {
                "success": False,
                "error": "Either channel_id or playlist_id must be provided"
            }
        
        collector = get_rss_collector()
        
        if channel_id:
            videos = collector.get_channel_feed(channel_id)
            feed_type = "channel"
            feed_id = channel_id
        else:
            videos = collector.get_playlist_feed(playlist_id)
            feed_type = "playlist"
            feed_id = playlist_id
        
        return {
            "success": True,
            "count": len(videos),
            "feed_type": feed_type,
            "feed_id": feed_id,
            "videos": videos,
            "collected_at": datetime.now().isoformat()
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


async def filter_videos(
    videos: List[Dict],
    min_views: Optional[int] = None,
    min_likes: Optional[int] = None,
    max_duration: Optional[int] = None,
    exclude_keywords: Optional[List[str]] = None
) -> Dict:
    """Filter videos by criteria"""
    try:
        video_filter = get_video_filter()
        
        filtered = VideoFilter.apply_filters(
            videos,
            min_views=min_views,
            min_likes=min_likes,
            max_duration=max_duration,
            exclude_keywords=exclude_keywords
        )
        
        return {
            "success": True,
            "original_count": len(videos),
            "filtered_count": len(filtered),
            "videos": filtered,
            "filters_applied": {
                "min_views": min_views,
                "min_likes": min_likes,
                "max_duration": max_duration,
                "exclude_keywords": exclude_keywords
            }
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e)
        }


async def search_custom_videos(
    query: str,
    max_results: int = 20,
    min_views: int = 0,
    sort_by: str = "relevance"
) -> Dict:
    """Search videos with custom LLM-driven query"""
    try:
        is_valid, error_msg = QueryValidator.validate_query(query)
        if not is_valid:
            return {
                "success": False,
                "error": error_msg,
                "hint": "Query must be 1-200 chars, no special characters like ;, &, |, $",
                "valid_example": "cooking recipes"
            }
        
        is_valid, error_msg = SortValidator.validate_sort(sort_by)
        if not is_valid:
            return {
                "success": False,
                "error": error_msg
            }
        
        max_results = ResultCountValidator.normalize_max_results(max_results)
        sort_by = SortValidator.normalize_sort(sort_by)
        
        collector = get_ytdlp_collector()
        video_filter = get_video_filter()
        
        videos = collector.search_custom_query(
            query=query.strip(),
            max_results=max_results * 2 if min_views > 0 else max_results,
            sort_by=sort_by
        )
        
        if min_views > 0:
            videos = video_filter.filter_by_views(videos, min_views=min_views)[:max_results]
        
        return {
            "success": True,
            "query": query.strip(),
            "count": len(videos),
            "max_results": max_results,
            "min_views": min_views,
            "sort_by": sort_by,
            "videos": videos,
            "source": "yt-dlp",
            "collected_at": datetime.now().isoformat()
        }
    
    except Exception as e:
        return {
            "success": False,
            "error": str(e),
            "query": query
        }


async def main():
    """Run the MCP server"""
    async with stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            server.create_initialization_options()
        )


if __name__ == "__main__":
    asyncio.run(main())
