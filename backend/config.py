"""
Adapt-X (Sahayak AI) — Backend Configuration
"""

import os
from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "Adapt-X — Intent-Aware Personal Accessibility Copilot"
    version: str = "1.0.0"
    api_prefix: str = "/api/v1"
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))
    debug: bool = os.getenv("DEBUG", "True").lower() == "true"
    jwt_secret: str = os.getenv("JWT_SECRET", "adaptx_secure_hackathon_jwt_secret_2026")
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = int(os.getenv("JWT_EXPIRATION_HOURS", "24"))


settings = Settings()
