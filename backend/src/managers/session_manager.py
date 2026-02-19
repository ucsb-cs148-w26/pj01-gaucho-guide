import json
import os
import sqlite3
import uuid
from datetime import datetime
from typing import List, Optional, Tuple
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage

DB_PATH = os.getenv("SESSION_DB_PATH", "chat_history.db")


class SessionManager:
    def __init__(self):
        self.conn = sqlite3.connect(DB_PATH, check_same_thread=False)
        self.create_tables()

    def create_tables(self):
        cursor = self.conn.cursor()
        # Table for Sessions
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                session_id TEXT PRIMARY KEY,
                name TEXT,
                last_updated TIMESTAMP
            )
        ''')
        # Table for Messages
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                role TEXT,
                content TEXT,
                timestamp TIMESTAMP,
                FOREIGN KEY(session_id) REFERENCES sessions(session_id)
            )
        ''')
        # Table for Transcripts (one per session, wiped when session ends)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS transcripts (
                session_id TEXT PRIMARY KEY,
                data TEXT,
                uploaded_at TIMESTAMP
            )
        ''')
        self.conn.commit()

    def create_session(self, name: str = None) -> str:
        """Creates a new chat session and returns its ID."""
        session_id = str(uuid.uuid4())
        if not name:
            name = f"Session {datetime.now().strftime('%Y-%m-%d %H:%M')}"

        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO sessions (session_id, name, last_updated) VALUES (?, ?, ?)",
            (session_id, name, datetime.now())
        )
        self.conn.commit()
        return session_id

    def get_recent_sessions(self, limit: int = 5) -> List[Tuple[str, str, str]]:
        """Returns the last N sessions (id, name, last_updated)."""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT session_id, name, last_updated FROM sessions ORDER BY last_updated DESC LIMIT ?",
            (limit,)
        )
        return cursor.fetchall()

    def save_message(self, session_id: str, role: str, content: str):
        """Saves a message to the database and updates session timestamp."""
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT INTO messages (session_id, role, content, timestamp) VALUES (?, ?, ?, ?)",
            (session_id, role, content, datetime.now())
        )
        # Update session timestamp to bump it to the top of the queue
        cursor.execute(
            "UPDATE sessions SET last_updated = ? WHERE session_id = ?",
            (datetime.now(), session_id)
        )
        self.conn.commit()

    def load_history(self, session_id: str) -> List[BaseMessage]:
        """Loads all messages for a session as LangChain message objects."""
        cursor = self.conn.cursor()
        cursor.execute(
            "SELECT role, content FROM messages WHERE session_id = ? ORDER BY id ASC",
            (session_id,)
        )
        rows = cursor.fetchall()

        history = []
        for role, content in rows:
            if role == "human":
                history.append(HumanMessage(content=content))
            elif role == "ai":
                history.append(AIMessage(content=content))
        return history

    def rename_session(self, session_id: str, new_name: str):
        """Updates the friendly name of a session."""
        cursor = self.conn.cursor()
        cursor.execute("UPDATE sessions SET name = ? WHERE session_id = ?", (new_name, session_id))
        self.conn.commit()

    def save_transcript(self, session_id: str, data: dict):
        """Stores parsed transcript JSON for a session, replacing any existing entry."""
        cursor = self.conn.cursor()
        cursor.execute(
            "INSERT OR REPLACE INTO transcripts (session_id, data, uploaded_at) VALUES (?, ?, ?)",
            (session_id, json.dumps(data), datetime.now())
        )
        self.conn.commit()

    def load_transcript(self, session_id: str) -> Optional[dict]:
        """Returns the parsed transcript dict for a session, or None if not uploaded."""
        cursor = self.conn.cursor()
        cursor.execute("SELECT data FROM transcripts WHERE session_id = ?", (session_id,))
        row = cursor.fetchone()
        if row:
            return json.loads(row[0])
        return None

    def clear_transcript(self, session_id: str):
        """Wipes the transcript for a session (call on session end)."""
        cursor = self.conn.cursor()
        cursor.execute("DELETE FROM transcripts WHERE session_id = ?", (session_id,))
        self.conn.commit()
