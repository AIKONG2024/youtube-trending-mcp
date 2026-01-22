# youtube-trending-mcp - LLM Reference

MCP server for YouTube video search and collection. Uses yt-dlp internally. No API keys required.

## Tools

### 1. search_trending_videos

Search trending videos by category.

```
Parameters:
- category: string (default: "all")
  Options: "all", "pets", "music", "gaming", "entertainment", or any custom topic
- max_results: integer (default: 20, range: 1-100)
- region: string (default: "US") - Country code: US, KR, GB, JP, etc.

Returns:
{
  "success": true,
  "count": 20,
  "category": "gaming",
  "region": "US",
  "videos": [VideoObject],
  "source": "yt-dlp",
  "collected_at": "2024-01-15T10:30:00"
}
```

### 2. search_custom_videos

Search videos with any query. Most flexible option.

```
Parameters:
- query: string (required, 1-200 chars) - Any search term
- max_results: integer (default: 20, range: 1-100)
- min_views: integer (default: 0) - Filter by minimum views
- sort_by: string (default: "relevance")
  Options: "relevance", "views", "date"

Returns:
{
  "success": true,
  "query": "cooking tutorials",
  "count": 20,
  "videos": [VideoObject],
  "source": "yt-dlp",
  "collected_at": "2024-01-15T10:30:00"
}
```

### 3. get_video_metadata

Get detailed info for a specific video.

```
Parameters:
- video_id: string (required) - YouTube video ID (11 chars, e.g., "dQw4w9WgXcQ")

Returns:
{
  "success": true,
  "video": VideoObject
}
```

### 4. collect_daily_ranking

Collect trending videos and save to database/JSON file.

```
Parameters:
- category: string (default: "all")
- max_results: integer (default: 50)
- save_to_db: boolean (default: true) - Save to SQLite
- save_to_json: boolean (default: true) - Save JSON snapshot

Returns:
{
  "success": true,
  "count": 50,
  "category": "all",
  "output_paths": ["/path/to/rankings.json", "/path/to/db.sqlite"],
  "collected_at": "2024-01-15T10:30:00"
}
```

### 5. get_youtube_rss_feed

Fetch RSS feed from YouTube channel or playlist.

```
Parameters:
- channel_id: string (optional) - Channel ID starting with "UC..."
- playlist_id: string (optional) - Playlist ID
(At least one required)

Returns:
{
  "success": true,
  "count": 15,
  "feed_type": "channel",
  "feed_id": "UCxxxxxx",
  "videos": [VideoObject],
  "collected_at": "2024-01-15T10:30:00"
}
```

### 6. filter_videos

Filter a list of videos by criteria.

```
Parameters:
- videos: array (required) - List of VideoObjects to filter
- min_views: integer (optional) - Minimum view count
- min_likes: integer (optional) - Minimum like count
- max_duration: integer (optional) - Maximum duration in seconds
- exclude_keywords: array of strings (optional) - Keywords to exclude from titles

Returns:
{
  "success": true,
  "original_count": 50,
  "filtered_count": 12,
  "videos": [VideoObject],
  "filters_applied": {
    "min_views": 100000,
    "max_duration": 600
  }
}
```

## VideoObject Schema

```json
{
  "video_id": "dQw4w9WgXcQ",
  "title": "Video Title",
  "channel": "Channel Name",
  "channel_id": "UCuAXFkgsw1L7xaCfnd5JJOw",
  "views": 1500000000,
  "likes": 16000000,
  "upload_date": "20091025",
  "duration": 212,
  "description": "Video description (truncated to 1000 chars)",
  "categories": ["Music"],
  "tags": ["tag1", "tag2"],
  "thumbnail": "https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
}
```

## Common Workflows

### Find popular videos on any topic
```
1. search_custom_videos(query="machine learning tutorial", max_results=30, sort_by="views")
```

### Get trending videos in a category
```
1. search_trending_videos(category="gaming", max_results=50, region="KR")
```

### Filter results by criteria
```
1. search_custom_videos(query="cooking", max_results=100)
2. filter_videos(videos=<result>, min_views=50000, max_duration=600)
```

### Collect daily rankings for tracking
```
1. collect_daily_ranking(category="music", max_results=100, save_to_db=true)
```

### Get channel's recent videos
```
1. get_youtube_rss_feed(channel_id="UCxxxxxxxxxxxxxxxxxxxxxx")
```

## Error Response

All tools return this format on error:
```json
{
  "success": false,
  "error": "Error message",
  "tool": "tool_name"
}
```

## Notes

- No API key or quota limits
- Rate limiting: Be reasonable, avoid rapid successive calls
- Video IDs are 11 characters (e.g., "dQw4w9WgXcQ")
- Channel IDs start with "UC" followed by 22 characters
- Duration is in seconds
- Upload date format: "YYYYMMDD"
