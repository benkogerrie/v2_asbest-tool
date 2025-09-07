from pydantic import BaseModel
from typing import List, Optional, Literal

Severity = Literal["LOW","MEDIUM","HIGH","CRITICAL"]
Status = Literal["PASS","FAIL","UNKNOWN"]

class AIFinding(BaseModel):
    code: str
    title: Optional[str]
    category: Literal["FORMAL","CONTENT","RISK","CONSISTENCY","ADMIN"]
    severity: Severity
    status: Status
    page: Optional[int] = None
    evidence_snippet: Optional[str]
    suggested_fix: Optional[str]

class AIOutput(BaseModel):
    report_summary: Optional[str]
    score: float
    findings: List[AIFinding]
