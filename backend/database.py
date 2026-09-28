"""
Sahayak AI — Lightweight SQLite Persistence Layer
Provides thread-safe local persistence for users, sessions, accessibility preferences,
task verification states, and personalization telemetry.
"""

import os
import json
import sqlite3
import logging
from threading import Lock
from typing import Dict, Any, Optional, List
from datetime import datetime

logger = logging.getLogger("sahayak.database")

DB_PATH = os.getenv("SAHAYAK_DB_PATH", os.path.join(os.path.dirname(__file__), "sahayak_ai.db"))


class DatabaseManager:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = db_path
        self._lock = Lock()
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path, check_same_thread=False)
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self):
        """Initializes tables and indexes if they do not exist."""
        with self._lock:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()

                # 1. Users Table
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS users (
                        user_id TEXT PRIMARY KEY,
                        email TEXT UNIQUE NOT NULL,
                        username TEXT,
                        full_name TEXT,
                        password_hash TEXT NOT NULL,
                        pin TEXT,
                        twin_id TEXT,
                        is_guest INTEGER DEFAULT 0,
                        active_persona TEXT DEFAULT 'default',
                        created_at TEXT
                    )
                """)

                # 2. Accessibility Twins (Preferences)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS accessibility_twins (
                        twin_id TEXT PRIMARY KEY,
                        profile_json TEXT NOT NULL,
                        updated_at TEXT
                    )
                """)

                # 3. Sessions (Document, Camera, Navigation, Voice)
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS sessions (
                        session_id TEXT PRIMARY KEY,
                        session_type TEXT NOT NULL,
                        twin_id TEXT,
                        data_json TEXT NOT NULL,
                        created_at REAL,
                        last_accessed REAL
                    )
                """)

                # 4. Form Verifications & Submissions
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS verifications (
                        task_id TEXT PRIMARY KEY,
                        twin_id TEXT,
                        status TEXT,
                        completion_percentage INTEGER,
                        completed_fields_json TEXT,
                        verification_token TEXT,
                        created_at TEXT
                    )
                """)

                # 5. Telemetry & Personalization Heatmap
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS telemetry (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        twin_id TEXT,
                        interaction_point TEXT,
                        complexity TEXT,
                        frequency INTEGER DEFAULT 1,
                        friction_score REAL DEFAULT 0.0,
                        updated_at TEXT
                    )
                """)

                conn.commit()
            finally:
                conn.close()

    # ----------------------------------------------------
    # User Persistence
    # ----------------------------------------------------
    def save_user(self, user: Dict[str, Any]) -> bool:
        with self._lock:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO users 
                    (user_id, email, username, full_name, password_hash, pin, twin_id, is_guest, active_persona, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    user.get("user_id"),
                    user.get("email"),
                    user.get("username"),
                    user.get("full_name"),
                    user.get("password_hash"),
                    user.get("pin"),
                    user.get("twin_id"),
                    1 if user.get("is_guest") else 0,
                    user.get("active_persona", "default"),
                    user.get("created_at", datetime.utcnow().isoformat()),
                ))
                conn.commit()
                return True
            except Exception as e:
                logger.error(f"Failed to save user: {e}")
                return False
            finally:
                conn.close()

    def get_user_by_email(self, email: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users WHERE LOWER(email) = LOWER(?)", (email.strip(),))
                row = cursor.fetchone()
                if row:
                    res = dict(row)
                    res["is_guest"] = bool(res.get("is_guest"))
                    return res
                return None
            finally:
                conn.close()

    def get_user_by_id(self, user_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
                row = cursor.fetchone()
                if row:
                    res = dict(row)
                    res["is_guest"] = bool(res.get("is_guest"))
                    return res
                return None
            finally:
                conn.close()

    # ----------------------------------------------------
    # Session Persistence
    # ----------------------------------------------------
    def save_session(self, session_id: str, session_type: str, data: Dict[str, Any], twin_id: str = "default_user") -> bool:
        with self._lock:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                now_ts = data.get("created_at", datetime.utcnow().timestamp())
                last_ts = data.get("last_accessed", datetime.utcnow().timestamp())
                cursor.execute("""
                    INSERT OR REPLACE INTO sessions
                    (session_id, session_type, twin_id, data_json, created_at, last_accessed)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    session_id,
                    session_type,
                    twin_id,
                    json.dumps(data),
                    now_ts,
                    last_ts,
                ))
                conn.commit()
                return True
            except Exception as e:
                logger.error(f"Failed to save session {session_id}: {e}")
                return False
            finally:
                conn.close()

    def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT data_json FROM sessions WHERE session_id = ?", (session_id,))
                row = cursor.fetchone()
                if row and row["data_json"]:
                    return json.loads(row["data_json"])
                return None
            except Exception as e:
                logger.error(f"Failed to get session {session_id}: {e}")
                return None
            finally:
                conn.close()

    def list_sessions(self, session_type: Optional[str] = None) -> List[Dict[str, Any]]:
        with self._lock:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                if session_type:
                    cursor.execute("SELECT data_json FROM sessions WHERE session_type = ?", (session_type,))
                else:
                    cursor.execute("SELECT data_json FROM sessions")
                rows = cursor.fetchall()
                results = []
                for r in rows:
                    if r["data_json"]:
                        results.append(json.loads(r["data_json"]))
                return results
            finally:
                conn.close()

    # ----------------------------------------------------
    # Verification & Submission Persistence
    # ----------------------------------------------------
    def save_verification(self, task_id: str, verification: Dict[str, Any], twin_id: str = "default_user") -> bool:
        with self._lock:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO verifications
                    (task_id, twin_id, status, completion_percentage, completed_fields_json, verification_token, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (
                    task_id,
                    twin_id,
                    verification.get("status", "IN_PROGRESS"),
                    int(verification.get("completion_percentage", 0)),
                    json.dumps(verification.get("completed_fields", [])),
                    verification.get("verification_token"),
                    datetime.utcnow().isoformat(),
                ))
                conn.commit()
                return True
            except Exception as e:
                logger.error(f"Failed to save verification for {task_id}: {e}")
                return False
            finally:
                conn.close()

    def get_verification(self, task_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            conn = self._get_connection()
            try:
                cursor = conn.cursor()
                cursor.execute("SELECT * FROM verifications WHERE task_id = ?", (task_id,))
                row = cursor.fetchone()
                if row:
                    res = dict(row)
                    if res.get("completed_fields_json"):
                        res["completed_fields"] = json.loads(res["completed_fields_json"])
                    return res
                return None
            finally:
                conn.close()


db = DatabaseManager()
