# app/schemas/prompts.py
from __future__ import annotations
from typing import Optional, List, Literal, Dict
from pydantic import BaseModel, Field, constr

PromptRole = Literal["system", "user", "tool"]
PromptStatus = Literal["draft", "active", "archived"]
OverrideStatus = Literal["draft", "active"]

# ---- Prompt ----
class PromptBase(BaseModel):
    name: constr(strip_whitespace=True, min_length=1)
    description: Optional[str] = None
    role: PromptRole = "system"
    content: constr(min_length=1)
    version: Optional[int] = Field(None, ge=1)  # Optional, will be auto-generated
    status: PromptStatus = "draft"

class PromptCreate(PromptBase):
    pass

class PromptUpdate(BaseModel):
    description: Optional[str] = None
    content: Optional[str] = None
    version: Optional[int] = Field(None, ge=1)
    status: Optional[PromptStatus] = None

class PromptOut(BaseModel):
    id: str
    name: str
    description: Optional[str] = None
    role: PromptRole
    content: str
    version: int
    status: PromptStatus
    created_at: str
    updated_at: str
    overrides_count: int = 0

# ---- Override ----
class PromptOverrideCreate(BaseModel):
    scope: constr(strip_whitespace=True, min_length=1)  # "global" | "tenant:{id}"
    content_override: constr(min_length=1)
    status: OverrideStatus = "draft"

class PromptOverrideUpdate(BaseModel):
    scope: Optional[str] = None
    content_override: Optional[str] = None
    status: Optional[OverrideStatus] = None

class PromptOverrideOut(BaseModel):
    id: str
    prompt_id: str
    scope: str
    content_override: str
    status: OverrideStatus
    created_at: str
    updated_at: str

# ---- Test-run ----
class PromptTestRunIn(BaseModel):
    sample_text: constr(min_length=1)
    checklist: Optional[str] = None
    severity_weights: Optional[Dict[str, int]] = None
    output_schema: Optional[str] = None
    provider: Optional[Literal["anthropic", "openai"]] = None
    model: Optional[str] = None

class PromptTestRunOut(BaseModel):
    raw_output: str
    parsed: Optional[Dict] = None
