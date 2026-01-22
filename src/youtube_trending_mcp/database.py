"""
SQLite database helper
"""

import sqlite3
from typing import List, Dict, Optional
from pathlib import Path
from datetime import datetime


class DatabaseHelper:
    """SQLite database operations for YouTube collection"""
    
    def __init__(self, db_path: str):
        """
        Initialize database helper
        
        Args:
            db_path: Path to SQLite database
        """
        self.db_path = db_path
        self._ensure_tables()
    
    def _ensure_tables(self) -> None:
        """Create tables if they don't exist"""
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Videos table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS videos (
                video_id TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                channel TEXT,
                channel_id TEXT,
                views INTEGER DEFAULT 0,
                likes INTEGER DEFAULT 0,
                upload_date TEXT,
                duration INTEGER DEFAULT 0,
                description TEXT,
                categories TEXT,
                tags TEXT,
                thumbnail TEXT,
                url TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Rankings table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS rankings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                date TEXT NOT NULL,
                category TEXT NOT NULL,
                video_id TEXT NOT NULL,
                position INTEGER NOT NULL,
                title TEXT,
                channel TEXT,
                views INTEGER,
                likes INTEGER,
                collected_at TEXT,
                UNIQUE(date, category, video_id)
            )
        """)
        
        # Transcripts table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS transcripts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                video_id TEXT NOT NULL,
                language TEXT NOT NULL,
                language_code TEXT,
                is_generated BOOLEAN DEFAULT 0,
                text TEXT,
                transcript_json TEXT,
                char_count INTEGER DEFAULT 0,
                extracted_at TEXT,
                UNIQUE(video_id, language_code)
            )
        """)
        
        # Create indexes
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_rankings_date ON rankings(date)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_rankings_category ON rankings(category)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_videos_channel ON videos(channel_id)")
        
        conn.commit()
        conn.close()
    
    def save_video(self, video: Dict) -> bool:
        """
        Save or update video metadata
        
        Args:
            video: Video dictionary
        
        Returns:
            True if successful
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        try:
            cursor.execute("""
                INSERT OR REPLACE INTO videos
                (video_id, title, channel, channel_id, views, likes, upload_date,
                 duration, description, categories, tags, thumbnail, url, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                video.get('video_id'),
                video.get('title'),
                video.get('channel'),
                video.get('channel_id'),
                video.get('views', 0),
                video.get('likes', 0),
                video.get('upload_date'),
                video.get('duration', 0),
                video.get('description', ''),
                ','.join(video.get('categories', [])),
                ','.join(video.get('tags', [])),
                video.get('thumbnail'),
                video.get('url'),
                datetime.now().isoformat()
            ))
            
            conn.commit()
            return True
        except Exception as e:
            print(f"Error saving video {video.get('video_id')}: {e}")
            return False
        finally:
            conn.close()
    
    def save_rankings(
        self,
        videos: List[Dict],
        category: str
    ) -> str:
        """
        Save video rankings to database
        
        Args:
            videos: List of video dictionaries
            category: Category name
        
        Returns:
            Database path
        """
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        date_str = datetime.now().strftime("%Y-%m-%d")
        collected_at = datetime.now().isoformat()
        
        for i, video in enumerate(videos, 1):
            try:
                cursor.execute("""
                    INSERT OR REPLACE INTO rankings
                    (date, category, video_id, position, title, channel, views, likes, collected_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    date_str,
                    category,
                    video.get('video_id'),
                    i,
                    video.get('title'),
                    video.get('channel'),
                    video.get('views', 0),
                    video.get('likes', 0),
                    collected_at
                ))
                
                # Also save video metadata
                self.save_video(video)
            except Exception as e:
                print(f"Error saving ranking for {video.get('video_id')}: {e}")
        
        conn.commit()
        conn.close()
        
        return self.db_path
    
    def get_rankings(
        self,
        date: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict]:
        """
        Get rankings from database
        
        Args:
            date: Date string (YYYY-MM-DD), defaults to today
            category: Category filter
            limit: Maximum results
        
        Returns:
            List of ranking dictionaries
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        if date is None:
            date = datetime.now().strftime("%Y-%m-%d")
        
        query = "SELECT * FROM rankings WHERE date = ?"
        params = [date]
        
        if category:
            query += " AND category = ?"
            params.append(category)
        
        query += " ORDER BY position ASC LIMIT ?"
        params.append(limit)
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        conn.close()
        
        return [dict(row) for row in rows]
    
    def get_video(self, video_id: str) -> Optional[Dict]:
        """
        Get video by ID
        
        Args:
            video_id: YouTube video ID
        
        Returns:
            Video dictionary or None
        """
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM videos WHERE video_id = ?", (video_id,))
        row = cursor.fetchone()
        
        conn.close()
        
        if row:
            video = dict(row)
            # Parse comma-separated fields back to lists
            video['categories'] = video.get('categories', '').split(',') if video.get('categories') else []
            video['tags'] = video.get('tags', '').split(',') if video.get('tags') else []
            return video
        
        return None
