"""
Tests for hallucination guardrails
"""

import pytest
from app.utils.guardrails import HallucinationGuardrail


class TestGuardrails:
    """Test hallucination detection and prevention"""
    
    def test_valid_finding(self, sample_finding):
        """Valid finding passes validation"""
        is_valid, reason, sanitized = HallucinationGuardrail.validate_finding(sample_finding)
        assert is_valid
        assert reason == "Valid"
        assert sanitized["category"] == "subscription_trap"
    
    def test_missing_required_fields(self):
        """Missing required fields fails validation"""
        incomplete = {
            "category": "subscription_trap",
            "title": "Test"
            # Missing severity, confidence, evidence_text
        }
        is_valid, reason, _ = HallucinationGuardrail.validate_finding(incomplete)
        assert not is_valid
        assert "Missing required fields" in reason
    
    def test_invalid_category(self):
        """Invalid category gets corrected to 'other'"""
        finding = {
            "category": "invalid_pattern",
            "title": "Test",
            "severity": "high",
            "confidence": 80,
            "evidence_text": "Test evidence"
        }
        is_valid, reason, sanitized = HallucinationGuardrail.validate_finding(finding)
        assert is_valid
        assert sanitized["category"] == "other"
    
    def test_invalid_severity(self):
        """Invalid severity gets corrected"""
        finding = {
            "category": "subscription_trap",
            "title": "Test",
            "severity": "extreme",
            "confidence": 80,
            "evidence_text": "Test evidence"
        }
        is_valid, reason, sanitized = HallucinationGuardrail.validate_finding(finding)
        assert is_valid
        assert sanitized["severity"] == "medium"
    
    def test_confidence_out_of_range(self):
        """Confidence > 100 fails"""
        finding = {
            "category": "subscription_trap",
            "title": "Test",
            "severity": "high",
            "confidence": 150,
            "evidence_text": "Test evidence"
        }
        is_valid, reason, _ = HallucinationGuardrail.validate_finding(finding)
        assert not is_valid
        assert "out of range" in reason
    
    def test_confidence_too_low(self):
        """Confidence < 40% rejected"""
        finding = {
            "category": "subscription_trap",
            "title": "Test",
            "severity": "high",
            "confidence": 30,
            "evidence_text": "Test evidence"
        }
        is_valid, reason, _ = HallucinationGuardrail.validate_finding(finding)
        assert not is_valid
        assert "too low" in reason
    
    def test_empty_evidence_text(self):
        """Empty evidence text fails"""
        finding = {
            "category": "subscription_trap",
            "title": "Test",
            "severity": "high",
            "confidence": 80,
            "evidence_text": ""
        }
        is_valid, reason, _ = HallucinationGuardrail.validate_finding(finding)
        assert not is_valid
    
    def test_fabrication_detection(self):
        """Fabrication phrases detected"""
        finding = {
            "category": "subscription_trap",
            "title": "Test",
            "severity": "high",
            "confidence": 80,
            "evidence_text": "Hallucinated button that says 'Subscribe'"
        }
        is_valid, reason, _ = HallucinationGuardrail.validate_finding(finding)
        assert not is_valid
        assert "Potential fabrication" in reason
    
    def test_coordinate_validation(self):
        """Invalid coordinates are normalized"""
        finding = {
            "category": "subscription_trap",
            "title": "Test",
            "severity": "high",
            "confidence": 80,
            "evidence_text": "Test",
            "evidence": {
                "x": 1.5,  # Out of range
                "y": -0.1,  # Out of range
                "width": 0.5,
                "height": 0.5
            }
        }
        is_valid, reason, sanitized = HallucinationGuardrail.validate_finding(finding)
        assert is_valid
        assert 0.0 <= sanitized["evidence"]["x"] <= 1.0
        assert 0.0 <= sanitized["evidence"]["y"] <= 1.0
    
    def test_response_validation(self, sample_finding):
        """Full response validation"""
        response = {
            "overall_risk_score": 72,
            "risk_level": "HIGH",
            "summary": "Test analysis",
            "findings": [sample_finding]
        }
        is_valid, valid_findings, issues = HallucinationGuardrail.validate_response(response)
        assert is_valid
        assert len(valid_findings) == 1
        assert len(issues) == 0
    
    def test_response_with_issues(self, sample_finding):
        """Response with some invalid findings"""
        bad_finding = {
            "category": "subscription_trap",
            "title": "Test",
            "severity": "high",
            "confidence": 20,  # Too low
            "evidence_text": "Test"
        }
        response = {
            "overall_risk_score": 72,
            "risk_level": "HIGH",
            "findings": [sample_finding, bad_finding]
        }
        is_valid, valid_findings, issues = HallucinationGuardrail.validate_response(response)
        assert is_valid  # Has at least one valid finding
        assert len(valid_findings) == 1  # One valid
        assert len(issues) == 1  # One issue
    
    def test_empty_response(self):
        """Empty findings response is valid but returns warning"""
        response = {
            "overall_risk_score": 0,
            "risk_level": "LOW",
            "findings": []
        }
        is_valid, valid_findings, issues = HallucinationGuardrail.validate_response(response)
        assert is_valid
        assert len(valid_findings) == 0
        assert any("No findings" in issue for issue in issues)
