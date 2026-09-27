"""
Sahayak AI — Stateful Session Service
Manages multi-turn interaction sessions for Document Q&A, Voice Dialogues,
Navigation State, and Accessible Task Completion.
Provides lightweight, thread-safe in-memory caching tailored for hackathon MVP.
"""

import time
import uuid
from typing import Dict, Any, Optional, List
from threading import Lock
from datetime import datetime


class SessionService:
    def __init__(self, session_ttl_seconds: int = 3600):
        self._ttl = session_ttl_seconds
        self._lock = Lock()
        self._document_sessions: Dict[str, Dict[str, Any]] = {}
        self._navigation_sessions: Dict[str, Dict[str, Any]] = {}
        self._voice_sessions: Dict[str, Dict[str, Any]] = {}
        self._user_personalization: Dict[str, Dict[str, Any]] = {}

    # ----------------------------------------------------
    # Document Sessions (Scan -> QA -> Tasks)
    # ----------------------------------------------------
    def create_document_session(
        self,
        doc_data: Dict[str, Any],
        twin_id: str = "default_user",
        custom_id: Optional[str] = None
    ) -> str:
        doc_id = custom_id or f"doc_{uuid.uuid4().hex[:8]}"
        with self._lock:
            self._document_sessions[doc_id] = {
                "document_id": doc_id,
                "twin_id": twin_id,
                "created_at": time.time(),
                "last_accessed": time.time(),
                "title": doc_data.get("title", doc_data.get("document_title", "Scanned Notice")),
                "authority": doc_data.get("authority", doc_data.get("issuing_authority", "Authority")),
                "deadlines": doc_data.get("deadlines", doc_data.get("key_deadlines", [])),
                "required_documents": doc_data.get("required_documents", []),
                "application_fee": doc_data.get("application_fee", "NIL"),
                "action_required": doc_data.get("action_required", "Review & Apply"),
                "summary_en": doc_data.get("summary_en", doc_data.get("simplified_summary_en", "")),
                "summary_hi": doc_data.get("summary_hi", doc_data.get("simplified_summary_hi", "")),
                "raw_text": doc_data.get("raw_text", ""),
                "qa_history": [],
                "tasks": [],
            }
        return doc_id

    def get_document_session(self, doc_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            session = self._document_sessions.get(doc_id)
            if session:
                session["last_accessed"] = time.time()
                return dict(session)
        return None

    def add_document_qa(
        self,
        doc_id: str,
        question: str,
        answer: str,
        supporting_info: Optional[List[str]] = None
    ) -> bool:
        with self._lock:
            session = self._document_sessions.get(doc_id)
            if not session:
                return False
            session["qa_history"].append({
                "question": question,
                "answer": answer,
                "supporting_info": supporting_info or [],
                "timestamp": datetime.utcnow().isoformat(),
            })
            session["last_accessed"] = time.time()
            return True

    def store_document_tasks(self, doc_id: str, tasks: List[Dict[str, Any]]) -> bool:
        with self._lock:
            session = self._document_sessions.get(doc_id)
            if not session:
                return False
            session["tasks"] = tasks
            session["last_accessed"] = time.time()
            return True

    # ----------------------------------------------------
    # Navigation Sessions (Stateful Spatial Obstacle Guidance)
    # ----------------------------------------------------
    def create_navigation_session(
        self,
        destination: str = "exit",
        twin_id: str = "default_user",
        custom_id: Optional[str] = None
    ) -> str:
        session_id = custom_id or f"nav_{uuid.uuid4().hex[:8]}"
        with self._lock:
            self._navigation_sessions[session_id] = {
                "session_id": session_id,
                "twin_id": twin_id,
                "destination": destination,
                "created_at": time.time(),
                "last_accessed": time.time(),
                "active": True,
                "steps_guided": 0,
                "guidance_history": [],
                "heading_degrees": 0.0,
                "obstacles": [],
            }
        return session_id

    def get_navigation_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            session = self._navigation_sessions.get(session_id)
            if session:
                session["last_accessed"] = time.time()
                return dict(session)
        return None

    def update_navigation_guidance(
        self,
        session_id: str,
        guidance: str,
        obstacles: List[Dict[str, Any]],
        heading: float = 0.0
    ) -> bool:
        with self._lock:
            session = self._navigation_sessions.get(session_id)
            if not session:
                return False
            session["steps_guided"] += 1
            session["heading_degrees"] = heading
            session["obstacles"] = obstacles
            session["guidance_history"].append({
                "step": session["steps_guided"],
                "guidance": guidance,
                "obstacles_count": len(obstacles),
                "timestamp": datetime.utcnow().isoformat(),
            })
            session["last_accessed"] = time.time()
            return True

    # ----------------------------------------------------
    # Voice & Dialogue Sessions
    # ----------------------------------------------------
    def get_or_create_voice_session(
        self,
        session_id: Optional[str] = None,
        twin_id: str = "default_user"
    ) -> Dict[str, Any]:
        with self._lock:
            sid = session_id or f"voice_{uuid.uuid4().hex[:8]}"
            if sid not in self._voice_sessions:
                self._voice_sessions[sid] = {
                    "session_id": sid,
                    "twin_id": twin_id,
                    "created_at": time.time(),
                    "last_accessed": time.time(),
                    "turn_count": 0,
                    "dialogue": [],
                    "active_intent": None,
                }
            session = self._voice_sessions[sid]
            session["last_accessed"] = time.time()
            return dict(session)

    def record_voice_turn(
        self,
        session_id: str,
        user_transcript: str,
        assistant_reply: str,
        intent: str
    ) -> bool:
        with self._lock:
            session = self._voice_sessions.get(session_id)
            if not session:
                return False
            session["turn_count"] += 1
            session["active_intent"] = intent
            session["dialogue"].append({
                "turn": session["turn_count"],
                "user": user_transcript,
                "assistant": assistant_reply,
                "intent": intent,
                "timestamp": datetime.utcnow().isoformat(),
            })
            session["last_accessed"] = time.time()
            return True

    # ----------------------------------------------------
    # Personalization Cache
    # ----------------------------------------------------
    def update_personalization_profile(self, twin_id: str, profile_data: Dict[str, Any]) -> Dict[str, Any]:
        with self._lock:
            existing = self._user_personalization.get(twin_id, {})
            existing.update(profile_data)
            existing["twin_id"] = twin_id
            existing["updated_at"] = datetime.utcnow().isoformat()
            self._user_personalization[twin_id] = existing
            return dict(existing)

    def get_personalization_profile(self, twin_id: str) -> Optional[Dict[str, Any]]:
        with self._lock:
            profile = self._user_personalization.get(twin_id)
            return dict(profile) if profile else None


# Global singleton instance
session_service = SessionService()
