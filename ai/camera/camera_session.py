"""
Sahayak AI — Camera Session
Maintains ephemeral camera-analysis state, recent perceptual frame hashes,
active mode context, and duplicate prevention per session.
Strictly does not persist raw user images to disk.
"""

import time
import uuid
from typing import Dict, Any, Optional, List
from collections import deque


class CameraSession:
    """
    Manages session-level state for continuous camera streams or multi-turn
    conversational camera tasks.
    """

    MAX_RECENT_HASHES = 10

    def __init__(self, session_id: Optional[str] = None):
        self.session_id: str = session_id or f"cam_sess_{uuid.uuid4().hex[:8]}"
        self.active_mode: str = "auto"
        self.created_at: float = time.time()
        self.last_activity: float = time.time()
        self.turn_count: int = 0
        self.context: Dict[str, Any] = {}
        self._recent_hashes: deque = deque(maxlen=self.MAX_RECENT_HASHES)
        self.last_analysis_result: Optional[Dict[str, Any]] = None

    def record_frame(self, frame_hash: str):
        """Records frame perceptual hash and updates timestamp."""
        if not frame_hash:
            return
        self._recent_hashes.append(frame_hash)
        self.last_activity = time.time()
        self.turn_count += 1

    def is_duplicate(self, frame_hash: Optional[str] = None) -> bool:
        """
        Returns True if the frame matches the immediate previous frame.
        """
        if not frame_hash or not self._recent_hashes:
            return False
        return self._recent_hashes[-1] == frame_hash

    def update_context(self, key: str, value: Any):
        """Sets temporary task context."""
        self.context[key] = value
        self.last_activity = time.time()

    def set_mode(self, mode: str):
        """Updates active camera mode."""
        self.active_mode = mode
        self.last_activity = time.time()

    def reset(self):
        """Gracefully clears frame history and cached results."""
        self._recent_hashes.clear()
        self.context.clear()
        self.last_analysis_result = None
        self.last_activity = time.time()


class CameraSessionManager:
    """
    In-memory registry of ephemeral camera sessions.
    """

    def __init__(self):
        self._sessions: Dict[str, CameraSession] = {}

    def get_or_create(self, session_id: Optional[str] = None) -> CameraSession:
        """Fetches active session or creates a new one."""
        if session_id and session_id in self._sessions:
            sess = self._sessions[session_id]
            sess.last_activity = time.time()
            return sess

        new_sess = CameraSession(session_id)
        self._sessions[new_sess.session_id] = new_sess
        return new_sess

    def remove_session(self, session_id: str):
        """Removes a session from memory."""
        self._sessions.pop(session_id, None)

    def cleanup_idle_sessions(self, max_idle_seconds: float = 3600.0):
        """Prunes sessions inactive for over an hour."""
        now = time.time()
        expired = [sid for sid, s in self._sessions.items() if (now - s.last_activity) > max_idle_seconds]
        for sid in expired:
            del self._sessions[sid]


# Singleton instance
camera_session_manager = CameraSessionManager()
