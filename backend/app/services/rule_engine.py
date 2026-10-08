"""
Rule-based dark pattern detection engine.
Detects obvious patterns WITHOUT calling Gemini.
"""

import json
import re
import logging
from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session
from app.models.pattern_rule import PatternRule

logger = logging.getLogger(__name__)


class RuleEngine:
    """Rule-based pattern detection without AI"""
    
    @staticmethod
    def detect_from_text(text: str, db: Session) -> List[Dict[str, Any]]:
        """
        Detect dark patterns from extracted text using rules.
        
        Args:
            text: Extracted text from screenshot/OCR
            db: Database session
        
        Returns:
            List of findings detected by rules
        """
        findings = []
        
        if not text or not text.strip():
            logger.info("No text to analyze, skipping rule detection")
            return findings
        
        # Get all enabled rules
        rules = db.query(PatternRule).filter(
            PatternRule.enabled == True
        ).order_by(PatternRule.priority.desc()).all()
        
        if not rules:
            logger.warning("No pattern rules configured")
            return findings
        
        for rule in rules:
            result = RuleEngine._check_rule(text, rule)
            if result:
                findings.append(result)
        
        logger.info(f"Rule detection found {len(findings)} patterns")
        return findings
    
    @staticmethod
    def _check_rule(text: str, rule: PatternRule) -> Optional[Dict[str, Any]]:
        """
        Check if text matches a rule.
        
        Args:
            text: Text to check
            rule: Pattern rule
        
        Returns:
            Finding dict if matched, None otherwise
        """
        text_lower = text.lower()
        
        # Check trigger phrases
        try:
            trigger_phrases = json.loads(rule.trigger_phrases)
        except json.JSONDecodeError:
            trigger_phrases = [rule.trigger_phrases]
        
        matched_phrase = None
        for phrase in trigger_phrases:
            if phrase.lower() in text_lower:
                matched_phrase = phrase
                break
        
        if not matched_phrase:
            return None
        
        # Check keyword patterns if specified
        if rule.keyword_patterns:
            try:
                patterns = json.loads(rule.keyword_patterns)
            except json.JSONDecodeError:
                patterns = [rule.keyword_patterns]
            
            pattern_matched = False
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    pattern_matched = True
                    break
            
            if not pattern_matched:
                return None
        
        # Pattern matched!
        logger.info(f"Rule matched: {rule.category} - {rule.title}")
        
        return {
            "category": rule.category,
            "title": rule.title,
            "severity": rule.default_severity,
            "confidence": rule.confidence_threshold,
            "evidence_text": matched_phrase,
            "why_problematic": rule.description,
            "user_impact": f"This {rule.category.replace('_', ' ')} pattern affects user autonomy.",
            "recommended_fix": f"Review this {rule.category.replace('_', ' ')} pattern.",
            "detection_method": "RULE_ENGINE",
            "evidence": {
                "x": 0.0,
                "y": 0.0,
                "width": 0.0,
                "height": 0.0
            }
        }
    
    @staticmethod
    def initialize_rules(db: Session):
        """
        Initialize standard dark pattern rules if table is empty.
        This is called on backend startup.
        """
        count = db.query(PatternRule).count()
        if count > 0:
            logger.info(f"Pattern rules already initialized ({count} rules)")
            return
        
        logger.info("Initializing pattern rules...")
        
        # Define standard rules
        standard_rules = [
            {
                "category": "subscription_trap",
                "title": "Subscription Trap",
                "description": "Hidden or unclear recurring billing",
                "trigger_phrases": json.dumps([
                    "free trial",
                    "then ₹",
                    "per month after",
                    "automatically charge",
                    "recurring"
                ]),
                "default_severity": "high",
                "confidence_threshold": 0.85,
                "priority": 90
            },
            {
                "category": "false_urgency",
                "title": "False Urgency",
                "description": "Artificial time pressure without legitimate reason",
                "trigger_phrases": json.dumps([
                    "only today",
                    "limited time",
                    "hurry",
                    "ending soon",
                    "offer ends in",
                    "last chance",
                    "expires"
                ]),
                "default_severity": "medium",
                "confidence_threshold": 0.75,
                "priority": 80
            },
            {
                "category": "confirm_shaming",
                "title": "Confirm Shaming",
                "description": "Decline option is harder to see or click",
                "trigger_phrases": json.dumps([
                    "no thanks",
                    "decline",
                    "skip",
                    "continue",
                    "later"
                ]),
                "default_severity": "medium",
                "confidence_threshold": 0.70,
                "priority": 70
            },
            {
                "category": "forced_action",
                "title": "Forced Action",
                "description": "Required action to proceed without meaningful alternative",
                "trigger_phrases": json.dumps([
                    "accept to continue",
                    "must enable",
                    "required permission",
                    "blocked",
                    "unlock"
                ]),
                "default_severity": "high",
                "confidence_threshold": 0.80,
                "priority": 85
            },
            {
                "category": "hidden_costs",
                "title": "Hidden Costs",
                "description": "Fees or charges not disclosed prominently",
                "trigger_phrases": json.dumps([
                    "processing fee",
                    "convenience charge",
                    "service fee",
                    "admin fee",
                    "plus charges"
                ]),
                "default_severity": "high",
                "confidence_threshold": 0.85,
                "priority": 88
            },
            {
                "category": "trick_questions",
                "title": "Trick Questions",
                "description": "Confusing wording that can trick user into unintended choice",
                "trigger_phrases": json.dumps([
                    "not to receive",
                    "do not want",
                    "no thanks",
                    "opt out"
                ]),
                "default_severity": "medium",
                "confidence_threshold": 0.75,
                "priority": 75
            }
        ]
        
        for rule_data in standard_rules:
            rule = PatternRule(
                category=rule_data["category"],
                title=rule_data["title"],
                description=rule_data["description"],
                trigger_phrases=rule_data["trigger_phrases"],
                default_severity=rule_data["default_severity"],
                confidence_threshold=rule_data["confidence_threshold"],
                priority=rule_data["priority"],
                enabled=True
            )
            db.add(rule)
        
        db.commit()
        logger.info(f"Initialized {len(standard_rules)} pattern rules")
