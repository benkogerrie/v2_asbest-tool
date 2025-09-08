# app/schemas/ai_config.py
from __future__ import annotations
from typing import Optional, Literal, Dict, Any
from pydantic import BaseModel, Field, constr

AIConfigProvider = Literal["anthropic", "openai"]

# ---- AI Configuration ----
class AIConfigBase(BaseModel):
    name: constr(strip_whitespace=True, min_length=1, max_length=255)
    provider: AIConfigProvider
    model: constr(strip_whitespace=True, min_length=1, max_length=100)
    api_key: constr(min_length=1)

class AIConfigCreate(AIConfigBase):
    pass

class AIConfigUpdate(BaseModel):
    name: Optional[constr(strip_whitespace=True, min_length=1, max_length=255)] = None
    provider: Optional[AIConfigProvider] = None
    model: Optional[constr(strip_whitespace=True, min_length=1, max_length=100)] = None
    api_key: Optional[constr(min_length=1)] = None

class AIConfigOut(BaseModel):
    id: str
    name: str
    provider: AIConfigProvider
    model: str
    api_key: str = Field(..., description="Masked API key for security")
    is_active: bool
    created_at: str
    updated_at: str

# ---- Test Result ----
class AIConfigTestResult(BaseModel):
    success: bool
    message: str
    response_time_ms: Optional[int] = None
    error_details: Optional[str] = None
    model_info: Optional[Dict[str, Any]] = None

# ---- Test Request ----
class AIConfigTestRequest(BaseModel):
    test_message: Optional[str] = Field(default="Test message for AI configuration validation")
