"""
Risk scoring utilities
"""

import logging
from typing import List

logger = logging.getLogger(__name__)


def severity_to_weight(severity: str) -> float:
    """
    Convert severity level to numerical weight
    
    Args:
        severity: 'low', 'medium', 'high', 'critical'
    
    Returns:
        Weight value (0-25)
    """
    weights = {
        'critical': 25.0,
        'high': 15.0,
        'medium': 8.0,
        'low': 3.0,
    }
    return weights.get(severity.lower(), 0.0)


def calculate_risk_score(findings: List[dict]) -> tuple[float, str]:
    """
    Calculate overall risk score from findings
    
    Algorithm:
    - Base score: 0
    - For each finding: score += severity_weight * confidence (normalized to 0-1)
    - Cap at 100
    - Determine risk level based on score
    
    Args:
        findings: List of finding dicts with 'severity' and 'confidence' keys
    
    Returns:
        (risk_score, risk_level) where risk_score is 0-100 and risk_level is LOW/MEDIUM/HIGH/CRITICAL
    """
    if not findings:
        return 0.0, "LOW"
    
    score = 0.0
    
    for finding in findings:
        severity = finding.get('severity', 'low').lower()
        confidence = finding.get('confidence', 0) / 100.0  # Normalize to 0-1
        
        weight = severity_to_weight(severity)
        score += weight * confidence
    
    # Cap at 100
    score = min(score, 100.0)
    
    # Determine risk level
    if score < 25:
        risk_level = "LOW"
    elif score < 50:
        risk_level = "MEDIUM"
    elif score < 75:
        risk_level = "HIGH"
    else:
        risk_level = "CRITICAL"
    
    return score, risk_level
