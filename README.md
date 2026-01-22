# YouTube Trending MCP Server

[![PyPI version](https://badge.fury.io/py/youtube-trending-mcp.svg)](https://badge.fury.io/py/youtube-trending-mcp)
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![MCP](https://img.shields.io/badge/MCP-compatible-green.svg)](https://modelcontextprotocol.io/)

Collect trending YouTube videos without web scraping! This MCP server provides stable, API-based YouTube data collection using [yt-dlp](https://github.com/yt-dlp/yt-dlp). No web scraping, no API keys required, no quotas!

## Features

- **No Web Scraping** - Uses yt-dlp's stable API access
- **No API Keys** - Completely free forever
- **No Quotas** - Unlimited data collection
- **Category Filtering** - Any topic: Music, Gaming, Cooking, Tech, etc.
- **Daily Rankings** - Track trending videos over time
- **RSS Fallback** - Alternative data source
- **SQLite Storage** - Built-in database support

## Installation

```bash
pip install youtube-trending-mcp
```

Or install from source:

```bash
git clone https://github.com/AIKONG2024/youtube-trending-mcp.git
cd youtube-trending-mcp
pip install -e .
```

## Quick Start

### Claude Code

Add to your MCP config:

```json
{
  "mcpServers": {
    "youtube-trending": {
      "command": "python",
      "args": ["-m", "youtube_trending_mcp"],
      "env": {
        "DATA_DIR": "/path/to/data"
      }
    }
  }
}
```

### Cursor

Add to `~/.cursor/mcp.json`:

```json
{
  "mcpServers": {
    "youtube-trending": {
      "command": "python",
      "args": ["-m", "youtube_trending_mcp"]
    }
  }
}
```

### OpenAI Codex

```json
{
  "mcpServers": {
    "youtube-trending": {
      "command": "python",
      "args": ["-m", "youtube_trending_mcp"],
      "env": {
        "DATA_DIR": "./data"
      }
    }
  }
}
```

## LLM Tool Reference

### Tools Overview

| Tool | Description |
|------|-------------|
| `search_trending_videos` | Search trending videos by category |
| `search_custom_videos` | Search any topic with custom query |
| `get_video_metadata` | Get detailed metadata for a video |
| `collect_daily_ranking` | Collect and save daily rankings |
| `get_youtube_rss_feed` | Fetch RSS feed from channel/playlist |
| `filter_videos` | Filter videos by views, likes, duration |

### search_trending_videos

```
Parameters:
  category: string (default: "all") - "all", "pets", "music", "gaming", "entertainment", or any topic
  max_results: int (default: 20, range: 1-100)
  region: string (default: "US") - Country code

Returns: { success, count, category, videos: [VideoObject] }
```

### search_custom_videos

```
Parameters:
  query: string (required) - Any search term
  max_results: int (default: 20)
  min_views: int (default: 0) - Filter by minimum views
  sort_by: string (default: "relevance") - "relevance", "views", "date"

Returns: { success, query, count, videos: [VideoObject] }
```

### get_video_metadata

```
Parameters:
  video_id: string (required) - YouTube video ID (11 chars)

Returns: { success, video: VideoObject }
```

### collect_daily_ranking

```
Parameters:
  category: string (default: "all")
  max_results: int (default: 50)
  save_to_db: bool (default: true)
  save_to_json: bool (default: true)

Returns: { success, count, output_paths: [...] }
```

### get_youtube_rss_feed

```
Parameters:
  channel_id: string - Channel ID (starts with "UC...")
  playlist_id: string - Playlist ID
  (At least one required)

Returns: { success, count, feed_type, videos: [VideoObject] }
```

### filter_videos

```
Parameters:
  videos: array (required) - List of VideoObjects
  min_views: int - Minimum view count
  min_likes: int - Minimum like count
  max_duration: int - Max duration in seconds
  exclude_keywords: array - Keywords to exclude

Returns: { success, original_count, filtered_count, videos: [VideoObject] }
```

### VideoObject Schema

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
  "description": "Description (max 1000 chars)",
  "categories": ["Music"],
  "tags": ["tag1", "tag2"],
  "thumbnail": "https://i.ytimg.com/vi/.../maxresdefault.jpg",
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
}
```

### Common Workflows

```python
# Find popular videos on any topic
search_custom_videos(query="machine learning", max_results=30, sort_by="views")

# Get trending by category
search_trending_videos(category="gaming", max_results=50, region="KR")

# Filter results
videos = search_custom_videos(query="cooking", max_results=100)
filter_videos(videos=videos, min_views=50000, max_duration=600)

# Save daily rankings
collect_daily_ranking(category="music", max_results=100)
```

### Notes

- Video IDs: 11 characters (e.g., `dQw4w9WgXcQ`)
- Channel IDs: Start with `UC` + 22 characters
- Duration: In seconds
- Upload date: `YYYYMMDD` format

## Why yt-dlp Instead of Web Scraping?

| Web Scraping | yt-dlp Approach |
|--------------|-----------------|
| Requires Playwright (heavy) | No browser needed |
| Breaks with site changes | Stable internal APIs |
| Anti-bot protection issues | Community maintained (143k+ stars) |
| Legal concerns (ToS) | Weekly updates |
| High maintenance | Reliable & fast |

## Development

```bash
git clone https://github.com/AIKONG2024/youtube-trending-mcp.git
cd youtube-trending-mcp
pip install -e ".[dev]"
pytest tests/ -v
```

## Related Projects

- [yt-dlp-mcp](https://github.com/kevinwatt/yt-dlp-mcp) - Download videos and transcripts via MCP

## License

MIT License - see [LICENSE](LICENSE) file for details.

---

**Made with love by AIKONG2024**
