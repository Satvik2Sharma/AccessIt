"""
Sahayak AI — FastAPI Orchestrator Core
Coordinates the 7-stage Intent-Aware Accessibility Pipeline across:
- Accessibility Twin
- Intent Engine
- Barrier Engine & Compiler
- Real OCR Form & Document Understanding
- ISL Sign Language Interpreter
- Spatial Vision & 12-Hour Clock Direction
- Scene Understanding & Object + OCR Fusion
- Voice Assistant & TTS Contracts
- Smart Navigation & Obstacle Guidance
- Multimodal Assistance, Verification & Telemetry Learning
"""

import sys
import os
import builtins
import typing
builtins.Union = typing.Union
import logging
from typing import Optional, Dict, Any


# Ensure project root is in python path
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from backend.config import settings
from shared.schemas.models import (
    AccessibilityTwin,
    PipelineStage,
    RecoveryStatus,
    RecoveryResult,
)
from backend.services.pipeline_service import pipeline_service

# Routers
from backend.routes.complete import router as complete_router
from backend.routes.read import router as read_router
from backend.routes.isl import router as isl_router
from backend.routes.see import router as see_router
from backend.routes.voice import router as voice_router
from backend.routes.scene import router as scene_router
from backend.routes.assistance import router as assistance_router
from backend.routes.navigation import router as navigation_router
from backend.routes.verification import router as verification_router
from backend.routes.learning import router as learning_router
from backend.routes.camera import router as camera_router
from backend.routes.auth import router as auth_router

logger = logging.getLogger("sahayak.api")


# Initialize FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.version,
    description="Intent-Aware Personal Accessibility Copilot — 7-Stage Pipeline Core",
)

# CORS configuration
raw_cors = os.environ.get("CORS_ORIGINS", "")
allowed_origins = [o.strip() for o in raw_cors.split(",") if o.strip()] if raw_cors else [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:8085",
    "http://127.0.0.1:8085",
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global Exception Handler with Structured Recovery Result
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception on {request.url}: {exc}", exc_info=True)
    recovery = pipeline_service.build_recovery_result(
        stage=PipelineStage.UNKNOWN,
        error_message=str(exc),
        fallback_used=True,
        strategy="GLOBAL_SAFE_RECOVERY",
    )
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Pipeline Recoverable Error",
            "detail": str(exc),
            "recovery": recovery.dict(),
        },
    )


# ----------------------------------------------------
# 1. System Health
# ----------------------------------------------------

@app.get(f"{settings.api_prefix}/health")
async def health_check():
    """Health check endpoint confirming pipeline readiness."""
    return {
        "status": "healthy",
        "version": settings.version,
        "system": "Sahayak AI Orchestrator",
        "pipeline": [
            "UNDERSTAND_USER",
            "UNDERSTAND_TASK",
            "DETECT_BARRIERS",
            "COMPILE_ACCESSIBLE_TASK_FLOW",
            "ASSIST",
            "VERIFY",
            "LEARN",
        ],
        "engines": {
            "accessibility_twin": True,
            "intent_engine": True,
            "barrier_engine": True,
            "task_engine": True,
            "flow_compiler": True,
            "assistance_engine": True,
            "verification_service": True,
            "learning_service": True,
            "spatial_vision": True,
            "scene_fusion": True,
            "voice_assistant": True,
            "smart_navigation": True,
            "document_qa": True,
            "session_service": True,
            "camera_intelligence": True,
            "auth_service": True,
        },
    }


# ----------------------------------------------------
# 2. Accessibility Twin Profile Endpoints
# ----------------------------------------------------

@app.get(f"{settings.api_prefix}/accessibility/profile", response_model=AccessibilityTwin)
async def get_profile(twin_id: str = "default_user"):
    return pipeline_service.twin_service.get_twin(twin_id)


@app.post(f"{settings.api_prefix}/accessibility/profile", response_model=AccessibilityTwin)
async def update_profile(twin: AccessibilityTwin):
    return pipeline_service.twin_service.update_twin(twin)


# ----------------------------------------------------
# 3. Intent Engine Endpoint
# ----------------------------------------------------

class IntentRequest(BaseModel):
    query: str
    twin_id: Optional[str] = "default_user"


@app.post(f"{settings.api_prefix}/intent")
async def classify_intent(request: IntentRequest):
    twin = pipeline_service.twin_service.get_twin(request.twin_id)
    task_type, confidence, rationale = pipeline_service.intent_engine.classify_intent(request.query, twin)
    return {
        "query": request.query,
        "intent": task_type.value,
        "confidence": confidence,
        "rationale": rationale,
        "recommended_pipeline_action": f"INITIATE_{task_type.value}",
    }


# ----------------------------------------------------
# Register Modular Domain Routers
# ----------------------------------------------------
app.include_router(auth_router, prefix=settings.api_prefix)
app.include_router(complete_router, prefix=settings.api_prefix)
app.include_router(read_router, prefix=settings.api_prefix)
app.include_router(isl_router, prefix=settings.api_prefix)
app.include_router(see_router, prefix=settings.api_prefix)
app.include_router(voice_router, prefix=settings.api_prefix)
app.include_router(scene_router, prefix=settings.api_prefix)
app.include_router(assistance_router, prefix=settings.api_prefix)
app.include_router(navigation_router, prefix=settings.api_prefix)
app.include_router(verification_router, prefix=settings.api_prefix)
app.include_router(learning_router, prefix=settings.api_prefix)
app.include_router(camera_router, prefix=settings.api_prefix)



if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host=settings.host, port=settings.port, reload=settings.debug)

