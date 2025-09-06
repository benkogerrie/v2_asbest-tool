"""
Scoring system for analysis findings.
"""
from typing import List, Dict, Any

# Severity weights for scoring
SEVERITY_WEIGHTS = {
    "CRITICAL": 20,
    "HIGH": 12,
    "MEDIUM": 6,
    "LOW": 3,
}


def compute_score(findings: List[Dict[str, Any]]) -> float:
    """
    Compute score based on findings severity.
    
    Args:
        findings: List of finding dictionaries with 'severity' key
        
    Returns:
        Score between 0 and 100
    """
    score = 100
    for finding in findings:
        severity = finding.get("severity", "LOW")
        score -= SEVERITY_WEIGHTS.get(severity, 0)
    
    return max(0, min(100, score))
