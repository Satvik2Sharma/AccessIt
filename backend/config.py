"""
Sahayak AI — Backend Configuration
"""

import os
from pydantic import BaseModel


class Settings(BaseModel):
    app_name: str = "Sahayak AI — Intent-Aware Personal Accessibility Copilot"
    version: str = "1.0.0"
    api_prefix: str = "/api/v1"
    host: str = os.getenv("HOST", "0.0.0.0")
    port: int = int(os.getenv("PORT", "8000"))
    debug: bool = os.getenv("DEBUG", "True").lower() == "true"


settings = Settings()
