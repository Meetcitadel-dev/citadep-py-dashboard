"""
Database schema and connection management for Citadel Analytics Demo System
"""
import sqlite3
import os
from datetime import datetime
from typing import Optional
from config import DB_PATH, DEMO_MODE

class Database:
    def __init__(self, db_path: str = DB_PATH):
        if not DEMO_MODE:
            raise ValueError("Database operations are only available in DEMO_MODE")
        self.db_path = db_path
        self.conn: Optional[sqlite3.Connection] = None
    
    def connect(self):
        """Create database connection"""
        self.conn = sqlite3.connect(self.db_path)
        self.conn.row_factory = sqlite3.Row
        return self.conn
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()
            self.conn = None
    
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
    
    def create_schema(self):
        """Create all database tables"""
        if not self.conn:
            self.connect()
        
        cursor = self.conn.cursor()
        
        # Users table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                signup_timestamp TEXT NOT NULL,
                gender TEXT NOT NULL,
                academic_year TEXT NOT NULL,
                profile_image_uploaded INTEGER DEFAULT 1,
                is_premium INTEGER DEFAULT 0,
                premium_upgrade_timestamp TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Sessions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sessions (
                session_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                start_timestamp TEXT NOT NULL,
                end_timestamp TEXT,
                duration_seconds INTEGER,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        
        # Vibes table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS vibes (
                vibe_id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender_id INTEGER NOT NULL,
                receiver_id INTEGER NOT NULL,
                adjective TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                FOREIGN KEY (sender_id) REFERENCES users(user_id),
                FOREIGN KEY (receiver_id) REFERENCES users(user_id)
            )
        """)
        
        # Matches table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS matches (
                match_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user1_id INTEGER NOT NULL,
                user2_id INTEGER NOT NULL,
                vibe1_id INTEGER NOT NULL,
                vibe2_id INTEGER NOT NULL,
                adjective TEXT NOT NULL,
                created_timestamp TEXT NOT NULL,
                expires_at TEXT NOT NULL,
                FOREIGN KEY (user1_id) REFERENCES users(user_id),
                FOREIGN KEY (user2_id) REFERENCES users(user_id),
                FOREIGN KEY (vibe1_id) REFERENCES vibes(vibe_id),
                FOREIGN KEY (vibe2_id) REFERENCES vibes(vibe_id)
            )
        """)
        
        # Conversations table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS conversations (
                conversation_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user1_id INTEGER NOT NULL,
                user2_id INTEGER NOT NULL,
                match_id INTEGER,
                message_request_id INTEGER,
                created_timestamp TEXT NOT NULL,
                last_message_timestamp TEXT,
                FOREIGN KEY (user1_id) REFERENCES users(user_id),
                FOREIGN KEY (user2_id) REFERENCES users(user_id),
                FOREIGN KEY (match_id) REFERENCES matches(match_id),
                FOREIGN KEY (message_request_id) REFERENCES message_requests(request_id)
            )
        """)
        
        # Messages table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS messages (
                message_id INTEGER PRIMARY KEY AUTOINCREMENT,
                conversation_id INTEGER NOT NULL,
                sender_id INTEGER NOT NULL,
                content TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                parent_message_id INTEGER,
                FOREIGN KEY (conversation_id) REFERENCES conversations(conversation_id),
                FOREIGN KEY (sender_id) REFERENCES users(user_id),
                FOREIGN KEY (parent_message_id) REFERENCES messages(message_id)
            )
        """)
        
        # Message requests table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS message_requests (
                request_id INTEGER PRIMARY KEY AUTOINCREMENT,
                sender_id INTEGER NOT NULL,
                receiver_id INTEGER NOT NULL,
                timestamp TEXT NOT NULL,
                status TEXT NOT NULL,
                responded_at TEXT,
                FOREIGN KEY (sender_id) REFERENCES users(user_id),
                FOREIGN KEY (receiver_id) REFERENCES users(user_id)
            )
        """)
        
        # Premium subscriptions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS premium_subscriptions (
                subscription_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                start_timestamp TEXT NOT NULL,
                end_timestamp TEXT,
                amount_paid INTEGER NOT NULL,
                status TEXT DEFAULT 'active',
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        
        # User events table (for tracking first actions)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_events (
                event_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER NOT NULL,
                event_type TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        
        # Create indexes for performance
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_sessions_user_timestamp ON sessions(user_id, start_timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_vibes_sender_timestamp ON vibes(sender_id, timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_vibes_receiver_timestamp ON vibes(receiver_id, timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_matches_timestamp ON matches(created_timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_messages_conversation_timestamp ON messages(conversation_id, timestamp)")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_conversations_timestamp ON conversations(created_timestamp)")
        
        self.conn.commit()
    
    def clear_all_data(self):
        """Clear all data from tables (for regeneration)"""
        if not self.conn:
            self.connect()
        
        cursor = self.conn.cursor()
        tables = [
            'user_events', 'premium_subscriptions', 'message_requests',
            'messages', 'conversations', 'matches', 'vibes', 'sessions', 'users'
        ]
        for table in tables:
            cursor.execute(f"DELETE FROM {table}")
        self.conn.commit()
    
    def get_connection(self):
        """Get database connection"""
        if not self.conn:
            self.connect()
        return self.conn
