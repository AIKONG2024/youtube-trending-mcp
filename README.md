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
- **Category Filtering** - Pets, Music, Gaming, Entertainment
- **Daily Rankings** - Track trending videos over time
- **RSS Fallback** - Alternative data source
- **SQLite Storage** - Built-in database support
- **MCP Compatible** - Works with Claude Desktop, Cline, Cursor, and more

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

### Claude Desktop

Add to your `claude_desktop_config.json`:

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

### Cline (VS Code)

Add to your MCP settings:

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

## Available Tools

### `search_trending_videos`

Find trending videos by category.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `category` | string | `"all"` | Category: `all`, `pets`, `music`, `gaming`, `entertainment` |
| `max_results` | int | `20` | Number of videos (1-100) |
| `region` | string | `"US"` | Region code |

**Example**: "Search for trending pet videos, get me 30 results"

### `search_custom_videos`

Search any topic with custom query.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `query` | string | required | Search query |
| `max_results` | int | `20` | Number of videos |
| `sort_by` | string | `"relevance"` | Sort: `relevance`, `date`, `views`, `rating` |

**Example**: "Search for cooking tutorial videos"

### `get_video_metadata`

Get detailed metadata for specific video.

| Parameter | Type | Description |
|-----------|------|-------------|
| `video_id` | string | YouTube video ID |

**Example**: "Get details for video dQw4w9WgXcQ"

### `collect_daily_ranking`

Collect daily trending snapshot and save to database.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `category` | string | `"all"` | Category to collect |
| `max_results` | int | `50` | Number of videos |
| `save_to_db` | bool | `true` | Save to SQLite |
| `save_to_json` | bool | `true` | Save JSON snapshot |

**Example**: "Collect today's top 50 pet videos and save them"

### `get_youtube_rss_feed`

Fetch RSS feed from channels/playlists.

| Parameter | Type | Description |
|-----------|------|-------------|
| `channel_id` | string | YouTube channel ID |
| `playlist_id` | string | YouTube playlist ID |

**Example**: "Get recent videos from channel UCOpcACMWblDls9Z6GERVi1A"

### `filter_videos`

Filter videos by criteria.

| Parameter | Type | Description |
|-----------|------|-------------|
| `videos` | list | List of videos to filter |
| `min_views` | int | Minimum view count |
| `min_likes` | int | Minimum like count |
| `max_duration` | int | Maximum duration (seconds) |
| `exclude_keywords` | list | Keywords to exclude |

## Video Metadata Structure

```json
{
  "video_id": "dQw4w9WgXcQ",
  "title": "Rick Astley - Never Gonna Give You Up",
  "channel": "Rick Astley",
  "channel_id": "UCuAXFkgsw1L7xaCfnd5JJOw",
  "views": 1500000000,
  "likes": 16000000,
  "upload_date": "20091025",
  "duration": 212,
  "description": "The official video for...",
  "categories": ["Music"],
  "tags": ["rick astley", "never gonna give you up"],
  "thumbnail": "https://i.ytimg.com/vi/dQw4w9WgXcQ/maxresdefault.jpg",
  "url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
}
```

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
# Clone repository
git clone https://github.com/AIKONG2024/youtube-trending-mcp.git
cd youtube-trending-mcp

# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v

# Run linting
ruff check src/
black src/ --check
```

## Project Structure

```
youtube-trending-mcp/
├── pyproject.toml              # Package configuration
├── README.md                   # This file
├── LICENSE                     # MIT License
├── src/
│   └── youtube_trending_mcp/
│       ├── __init__.py         # Package exports
│       ├── __main__.py         # CLI entry point
│       ├── server.py           # MCP server implementation
│       ├── ytdlp_collector.py  # yt-dlp wrapper
│       ├── rss_collector.py    # RSS feed collector
│       ├── filters.py          # Video filtering
│       ├── validators.py       # Input validation
│       └── database.py         # SQLite helper
└── tests/                      # Test files
```

## Related Projects

- [yt-dlp-mcp](https://github.com/kevinwatt/yt-dlp-mcp) - Download videos and transcripts via MCP

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Add tests
5. Submit a pull request

## License

MIT License - see [LICENSE](LICENSE) file for details.

## Credits

Built with:
- [yt-dlp](https://github.com/yt-dlp/yt-dlp) - Video data extraction
- [MCP](https://modelcontextprotocol.io/) - Model Context Protocol
- [feedparser](https://github.com/kurtmckee/feedparser) - RSS feed parsing

---

**Made with love by AIKONG2024**
