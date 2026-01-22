"""
CLI entry point for youtube-trending-mcp
"""

import sys
import asyncio
from .server import main


def run():
    """Main CLI entry point"""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\nShutting down YouTube Trending MCP server...")
        sys.exit(0)
    except Exception as e:
        print(f"Error running server: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    run()
