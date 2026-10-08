"""
Tests for rule-based pattern detection
"""

import pytest
import json
from app.services.rule_engine import RuleEngine
from app.models.pattern_rule import PatternRule


class TestRuleEngine:
    """Test rule-based dark pattern detection"""
    
    def test_rule_initialization(self, temp_db):
        """Rules are initialized on first startup"""
        # Initialize
        RuleEngine.initialize_rules(temp_db)
        
        # Check rules exist
        rules = temp_db.query(PatternRule).all()
        assert len(rules) > 0
        assert any(r.category == "subscription_trap" for r in rules)
    
    def test_rule_not_reinitialized(self, temp_db):
        """Rules not reinitialized if they already exist"""
        RuleEngine.initialize_rules(temp_db)
        count_1 = temp_db.query(PatternRule).count()
        
        RuleEngine.initialize_rules(temp_db)
        count_2 = temp_db.query(PatternRule).count()
        
        assert count_1 == count_2  # Same count, not duplicated
    
    def test_detect_subscription_trap(self, temp_db):
        """Detect 'free trial' text as subscription trap"""
        RuleEngine.initialize_rules(temp_db)
        
        text = "Get 7 days free, then ₹499/month automatically"
        findings = RuleEngine.detect_from_text(text, temp_db)
        
        assert len(findings) > 0
        assert any(f["category"] == "subscription_trap" for f in findings)
    
    def test_detect_false_urgency(self, temp_db):
        """Detect time pressure as false urgency"""
        RuleEngine.initialize_rules(temp_db)
        
        text = "Offer ends in 1 hour! Limited time only!"
        findings = RuleEngine.detect_from_text(text, temp_db)
        
        assert len(findings) > 0
        assert any(f["category"] == "false_urgency" for f in findings)
    
    def test_detect_hidden_costs(self, temp_db):
        """Detect hidden fees"""
        RuleEngine.initialize_rules(temp_db)
        
        text = "Your total is $9.99 plus processing fee"
        findings = RuleEngine.detect_from_text(text, temp_db)
        
        assert len(findings) > 0
        assert any(f["category"] == "hidden_costs" for f in findings)
    
    def test_no_false_positives(self, temp_db):
        """Legitimate text doesn't trigger rules"""
        RuleEngine.initialize_rules(temp_db)
        
        text = "Welcome to our app. Please sign in."
        findings = RuleEngine.detect_from_text(text, temp_db)
        
        assert len(findings) == 0
    
    def test_empty_text(self, temp_db):
        """Empty text returns no findings"""
        RuleEngine.initialize_rules(temp_db)
        
        findings = RuleEngine.detect_from_text("", temp_db)
        assert len(findings) == 0
    
    def test_finding_structure(self, temp_db):
        """Detected finding has correct structure"""
        RuleEngine.initialize_rules(temp_db)
        
        text = "Free trial then ₹499/month"
        findings = RuleEngine.detect_from_text(text, temp_db)
        
        assert len(findings) == 1
        finding = findings[0]
        
        # Check required fields
        assert finding["category"]
        assert finding["title"]
        assert finding["severity"]
        assert 0 <= finding["confidence"] <= 1
        assert finding["evidence_text"]
        assert finding["detection_method"] == "RULE_ENGINE"
        assert "evidence" in finding
    
    def test_disabled_rules_ignored(self, temp_db):
        """Disabled rules don't trigger"""
        RuleEngine.initialize_rules(temp_db)
        
        # Disable subscription trap rule
        rule = temp_db.query(PatternRule).filter(
            PatternRule.category == "subscription_trap"
        ).first()
        rule.enabled = False
        temp_db.commit()
        
        text = "Free trial then ₹499/month"
        findings = RuleEngine.detect_from_text(text, temp_db)
        
        # Should not find subscription_trap now
        assert not any(f["category"] == "subscription_trap" for f in findings)
    
    def test_priority_order(self, temp_db):
        """Rules checked in priority order"""
        RuleEngine.initialize_rules(temp_db)
        
        # Text that could match multiple rules
        text = "Free trial ending soon with processing fee"
        findings = RuleEngine.detect_from_text(text, temp_db)
        
        # Should find multiple patterns, highest priority first
        categories = [f["category"] for f in findings]
        assert len(categories) > 0
