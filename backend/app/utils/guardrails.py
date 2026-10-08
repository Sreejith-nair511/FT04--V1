"""
Hallucination guardrails - validates AI responses before storing.
Prevents false positives and fabricated evidence.
"""

import logging
from typing import Dict, Any, List, Tuple

logger = logging.getLogger(__name__)


class HallucinationGuardrail:
    """Validates AI findings for hallucinations and issues"""
    
    VALID_CATEGORIES = {
        "subscription_trap",
        "false_urgency",
        "forced_action",
        "basket_sneaking",
        "confirm_shaming",
        "bait_and_switch",
        "disguised_ads",
        "nagging",
        "trick_questions",
        "hidden_costs",
        "other"
    }
    
    VALID_SEVERITIES = {"low", "medium", "high", "critical"}
    
    @staticmethod
    def validate_finding(finding: Dict[str, Any]) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Validate a single finding for hallucinations.
        
        Args:
            finding: Finding dict from AI
        
        Returns:
            (is_valid, reason, sanitized_finding)
        """
        
        # Check required fields
        required = ["category", "title", "severity", "confidence", "evidence_text"]
        missing = [f for f in required if f not in finding or not finding[f]]
        if missing:
            return False, f"Missing required fields: {missing}", finding
        
        # Validate category
        if finding["category"] not in HallucinationGuardrail.VALID_CATEGORIES:
            logger.warning(f"Invalid category: {finding['category']}")
            finding["category"] = "other"
        
        # Validate severity
        if finding.get("severity", "").lower() not in HallucinationGuardrail.VALID_SEVERITIES:
            logger.warning(f"Invalid severity: {finding.get('severity')}")
            finding["severity"] = "medium"
        else:
            finding["severity"] = finding["severity"].lower()
        
        # Validate confidence (0-100)
        try:
            conf = float(finding.get("confidence", 0))
            if conf < 0 or conf > 100:
                return False, f"Confidence out of range: {conf}", finding
            finding["confidence"] = conf
        except (ValueError, TypeError):
            return False, f"Invalid confidence value: {finding.get('confidence')}", finding
        
        # Check confidence threshold (reject low confidence)
        if finding["confidence"] < 40:
            return False, f"Confidence too low ({finding['confidence']}%)", finding
        
        # Validate evidence
        evidence = finding.get("evidence", {})
        if not evidence or not isinstance(evidence, dict):
            logger.warning("Invalid or missing evidence coordinates")
            finding["evidence"] = {"x": 0.0, "y": 0.0, "width": 0.0, "height": 0.0}
        
        # Validate evidence coordinates
        for coord in ["x", "y", "width", "height"]:
            try:
                val = float(evidence.get(coord, 0.0))
                if val < 0.0 or val > 1.0:
                    logger.warning(f"Coordinate {coord} out of range: {val}")
                    evidence[coord] = max(0.0, min(1.0, val))
                else:
                    evidence[coord] = val
            except (ValueError, TypeError):
                logger.warning(f"Invalid coordinate {coord}: {evidence.get(coord)}")
                evidence[coord] = 0.0
        
        finding["evidence"] = evidence
        
        # Check evidence text is not empty or generic
        evidence_text = finding.get("evidence_text", "").strip()
        if not evidence_text or len(evidence_text) < 2:
            return False, "Evidence text is empty or too short", finding
        
        # Check for fabrication patterns
        fabrication_phrases = [
            "hallucinated",
            "invented",
            "no visible",
            "not present",
            "assumed",
            "imaginary"
        ]
        evidence_lower = evidence_text.lower()
        if any(phrase in evidence_lower for phrase in fabrication_phrases):
            logger.warning(f"Potential fabrication detected: {evidence_text}")
            return False, f"Potential fabrication: {evidence_text}", finding
        
        # Check why_problematic is not empty
        if not finding.get("why_problematic", "").strip():
            finding["why_problematic"] = f"This {finding['category']} pattern may be deceptive."
        
        # Check user_impact is not empty
        if not finding.get("user_impact", "").strip():
            finding["user_impact"] = f"Users may be negatively affected by this pattern."
        
        # Check recommended_fix is not empty
        if not finding.get("recommended_fix", "").strip():
            finding["recommended_fix"] = f"Review and remediate this {finding['category']} pattern."
        
        return True, "Valid", finding
    
    @staticmethod
    def validate_response(response: Dict[str, Any]) -> Tuple[bool, List[Dict[str, Any]], List[str]]:
        """
        Validate entire AI response and findings.
        
        Args:
            response: Full AI response dict
        
        Returns:
            (is_valid, valid_findings, validation_issues)
        """
        issues = []
        valid_findings = []
        
        if not isinstance(response, dict):
            issues.append("Response is not a dictionary")
            return False, [], issues
        
        # Check findings array exists
        findings = response.get("findings", [])
        if not isinstance(findings, list):
            issues.append("Findings is not an array")
            return False, [], issues
        
        if not findings:
            issues.append("No findings detected")
            return True, [], issues
        
        # Validate each finding
        for idx, finding in enumerate(findings):
            is_valid, reason, sanitized = HallucinationGuardrail.validate_finding(finding)
            
            if not is_valid:
                issues.append(f"Finding {idx}: {reason}")
            else:
                valid_findings.append(sanitized)
        
        # Check risk score
        try:
            risk_score = float(response.get("overall_risk_score", 0))
            if risk_score < 0 or risk_score > 100:
                issues.append(f"Risk score out of range: {risk_score}")
                response["overall_risk_score"] = max(0, min(100, risk_score))
        except (ValueError, TypeError):
            issues.append("Invalid risk score")
            response["overall_risk_score"] = 0
        
        # Check risk level
        valid_levels = {"LOW", "MEDIUM", "HIGH", "CRITICAL"}
        if response.get("risk_level", "").upper() not in valid_levels:
            response["risk_level"] = "MEDIUM"
            issues.append("Invalid risk level, defaulting to MEDIUM")
        
        is_valid = len(valid_findings) > 0 or "No findings detected" in issues
        
        return is_valid, valid_findings, issues
