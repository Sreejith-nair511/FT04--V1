# Gemini Integration Guide

## Overview

CogniShield uses Google's Gemini API for AI-powered dark pattern detection. The backend encapsulates all Gemini communication, so the frontend never directly calls the API.

---

## Getting Started

### 1. Get Gemini API Key

Visit: https://aistudio.google.com/app/apikeys

1. Click "Create API Key"
2. Copy the key
3. Add to `.env`:
   ```
   GEMINI_API_KEY=sk_live_...
   ```

### 2. Choose Model

Update `.env`:
```
GEMINI_MODEL=gemini-2.0-flash-exp
```

**Available Models:**
- `gemini-2.0-flash-exp` (recommended, default)
- `gemini-1.5-flash`
- `gemini-1.5-pro`
- Other Gemini models

### 3. Start Backend

```bash
uvicorn app.main:app --reload
```

Check Gemini is working:
```bash
curl http://localhost:8000/api/health/gemini
```

---

## How It Works

### Architecture

```
Frontend
    ↓ (Upload file)
API Route (/api/analyze/image)
    ↓
Analysis Service
    ↓
Gemini Service
    ├── Read image
    ├── Encode to base64
    ├── Send to Gemini API
    ├── Wait for response
    ├── Parse JSON
    └── Validate with Pydantic
    ↓
Database (save findings)
    ↓
Frontend (display results)
```

### Request Flow

```python
# 1. Frontend uploads image
POST /api/analyze/image
  file: screenshot.png
  application_name: "FinFlow"
  platform: "iOS"

# 2. Backend saves file
storage/uploads/550e8400-..._original.png

# 3. Backend sends to Gemini
{
  "file": <base64_encoded_image>,
  "model": "gemini-2.0-flash-exp",
  "system_prompt": "You are CogniShield AI...",
  "prompt": "Analyze this fintech UI for dark patterns...",
  "response_format": "json"
}

# 4. Gemini analyzes
(Processing...)

# 5. Gemini returns JSON
{
  "overall_risk_score": 72,
  "risk_level": "HIGH",
  "findings": [...]
}

# 6. Backend stores findings
INSERT INTO findings ...

# 7. Frontend receives audit_id
{
  "audit_id": "550e8400-...",
  "status": "processing"
}

# 8. Frontend polls status
GET /api/analysis/550e8400-.../status

# 9. Results appear in UI
```

---

## Image Analysis

### Request Format

```python
from app.services.gemini_service import GeminiService

gemini = GeminiService()
result = gemini.analyze_image("path/to/screenshot.png")
```

### Response Structure

```json
{
  "overall_risk_score": 72,
  "risk_level": "HIGH",
  "summary": "Multiple deceptive interaction patterns detected...",
  "findings": [
    {
      "category": "subscription_trap",
      "title": "Subscription Trap",
      "severity": "high",
      "confidence": 94,
      "evidence_text": "Free trial — ₹499/month after 7 days",
      "why_problematic": "The recurring payment condition is visually subordinate...",
      "user_impact": "Users may unintentionally enter a recurring billing agreement.",
      "recommended_fix": "Make the trial terms and recurring cost equally prominent.",
      "evidence": {
        "x": 0.18,
        "y": 0.57,
        "width": 0.64,
        "height": 0.14
      }
    }
  ],
  "analysis_notes": []
}
```

### Coordinate System

Evidence coordinates are **normalized (0.0 - 1.0)**:

```
Example image: 375×812px (typical phone screenshot)

Element at:
  Left:   67px  → 67/375 = 0.18
  Top:    463px → 463/812 = 0.57
  Width:  240px → 240/375 = 0.64
  Height: 114px → 114/812 = 0.14

Stored as: { x: 0.18, y: 0.57, width: 0.64, height: 0.14 }
```

**Why normalized?**
- Works with any screen resolution
- Frontend scales to phone preview
- No loss of precision

---

## Video Analysis

### Request Format

```python
result = gemini.analyze_video("path/to/video.mp4")
```

### Response (with timestamps)

```json
{
  "overall_risk_score": 68,
  "risk_level": "HIGH",
  "summary": "Detected patterns across subscription and payment flows.",
  "findings": [
    {
      "category": "subscription_trap",
      "title": "Auto-renewal Without Clear Consent",
      "severity": "high",
      "confidence": 91,
      "evidence_text": "Auto-renewal enabled by default",
      "why_problematic": "Pre-selected checkbox for recurring payment.",
      "user_impact": "Charges users without explicit per-transaction consent.",
      "recommended_fix": "Require explicit user action to enable auto-renewal.",
      "timestamp_seconds": 17.4,
      "frame_number": 261,
      "evidence": {
        "x": 0.20,
        "y": 0.60,
        "width": 0.60,
        "height": 0.15
      }
    }
  ]
}
```

### Video Processing

1. **Upload** - Send video to Gemini
2. **Extract Frames** - Pull key frames at timestamps
3. **Store Frames** - Save to `storage/frames/{audit_id}/`
4. **Link Evidence** - Associate with findings

---

## System Prompts

System prompts guide Gemini's analysis. Located in:

```
backend/app/prompts/
├── image_analysis.txt
└── video_analysis.txt
```

### Image Analysis Prompt

```
You are CogniShield AI, a forensic UX analysis engine specializing 
in detecting deceptive design patterns in financial technology interfaces.

Your analysis task:
1. Examine the fintech UI screenshot carefully
2. Identify only evidence-supported dark patterns
3. For each pattern detected, provide detailed analysis

Dark Pattern Taxonomy (classify into):
- false_urgency
- basket_sneaking
- confirm_shaming
- forced_action
- subscription_trap
- bait_and_switch
- disguised_ads
- nagging
- trick_questions
- hidden_costs

For EVERY finding you identify:
1. Provide the exact UI text or element
2. Provide normalized bounding box coordinates (0.0-1.0)
3. Explain WHY it's problematic
4. Explain the USER IMPACT
5. Provide a REMEDIATION path

Only classify something as a dark pattern if:
- It demonstrates deceptive or coercive intent
- It prioritizes conversion over user clarity
- It violates user expectations or autonomy

Never fabricate UI elements that are not visible.
```

### Custom Prompts

To customize analysis, edit the prompt files:

```bash
# Edit image analysis prompt
nano backend/app/prompts/image_analysis.txt

# Backend reloads on restart
uvicorn app.main:app --reload
```

---

## Dark Pattern Taxonomy

CogniShield uses a controlled taxonomy (no invented categories):

### 1. false_urgency
Time pressure that's not legitimate.
```
Example: "Offer ends in 1 hour!" (but always resets)
Impact: Users rush to pay without thinking
Remediation: Only use real time limits
```

### 2. basket_sneaking
Costs added at the end of checkout.
```
Example: "$9.99/month" → Final price $14.99 with undisclosed fees
Impact: Users surprised after commitment
Remediation: Show all costs upfront
```

### 3. confirm_shaming
Making decline look bad or hard.
```
Example: "Yes, save me money" vs tiny "No, I hate savings"
Impact: Users feel pressured to accept
Remediation: Neutral language for both options
```

### 4. forced_action
Blocking progress without required action.
```
Example: Accept analytics to continue (no decline option)
Impact: Users can't proceed without complying
Remediation: Provide meaningful alternative path
```

### 5. subscription_trap
Hidden recurring billing.
```
Example: "Free trial" then ₹499/month starts automatically
Impact: Users charged unexpectedly
Remediation: Clear cancellation, calendar reminder
```

### 6. bait_and_switch
Promises don't match reality.
```
Example: "Gold membership" but doesn't include advertised features
Impact: Users disappointed after payment
Remediation: Match promise to actual benefits
```

### 7. disguised_ads
Ads presented as content.
```
Example: "Sponsored" label hard to see
Impact: Users can't distinguish ads from content
Remediation: Clear labeling and visual distinction
```

### 8. nagging
Persistent reminders after decline.
```
Example: Dismiss popup, it returns next day with same offer
Impact: Annoying, violates user intent
Remediation: Respect first decline, space out reminders
```

### 9. trick_questions
Confusing language for consent.
```
Example: "Yes, I want NOT to receive emails" (double negative)
Impact: Users accidentally opt in
Remediation: Clear, direct yes/no language
```

### 10. hidden_costs
Fees not disclosed upfront.
```
Example: Transaction fee shown in fine print only
Impact: Users don't realize true cost
Remediation: Include in initial price display
```

### 11. other
Doesn't fit above categories.
```
Use when uncertain. Include why in analysis.
Note: Confidence should be lower for uncategorized patterns.
```

---

## Confidence Scoring

Gemini outputs a confidence percentage (0-100):

```
95%+ = Almost certain
80-95% = Very likely
70-80% = Probably
50-70% = Uncertain
<50% = Very uncertain
```

### Backend Treatment

Backend only accepts findings with **confidence > 40%**:

```python
if finding['confidence'] < 40:
    skip_finding()  # Too uncertain
else:
    create_finding()
```

This prevents false positives.

---

## Error Handling

### API Key Missing

```python
if not settings.gemini_api_key:
    # Fall back to DEMO MODE
    return demo_analysis_result()
```

Set `DEMO_MODE=true` to skip key entirely.

### API Rate Limited

```
Error: 429 Too Many Requests
Solution: Wait 60s, retry
```

No automatic retry in MVP. Frontend should handle.

### Invalid Response

```python
try:
    json_response = json.loads(gemini_response)
except json.JSONDecodeError:
    # Extract JSON from response text
    json_str = response[json_start:json_end]
    json_response = json.loads(json_str)
```

Gemini sometimes includes extra text before/after JSON.

### Timeout

```
Default: 60s per request
Video analysis: May exceed timeout
Solution: Implement request queue for production
```

---

## Model Comparison

| Model | Speed | Cost | Quality | Multimodal | Best For |
|-------|-------|------|---------|-----------|----------|
| **flash-exp** | Fast | Low | High | Yes | **MVP (recommended)** |
| 1.5-flash | Fast | Low | Good | Yes | Production |
| 1.5-pro | Slow | Med | Excellent | Yes | Complex analysis |
| 2.0-flash | Fast | Low | Very High | Yes | Latest (experimental) |

**Recommendation:** Start with `gemini-2.0-flash-exp`, switch to `gemini-1.5-pro` if accuracy needed.

---

## Testing Without API Key

### Demo Mode

```bash
# .env
DEMO_MODE=true
GEMINI_API_KEY=  # Empty

# Backend returns synthetic data
```

### With Mock

```python
# tests/test_gemini.py
from unittest.mock import patch

@patch('app.services.gemini_service.GeminiService.analyze_image')
def test_analyze(mock_gemini):
    mock_gemini.return_value = {
        "overall_risk_score": 72,
        "findings": [...]
    }
    
    result = analyze_image("test.png")
    assert result['risk_score'] == 72
```

---

## Response Validation

Backend validates Gemini responses with Pydantic:

```python
class FindingResult(BaseModel):
    category: str  # Must be from taxonomy
    title: str
    severity: str  # low, medium, high, critical
    confidence: float  # 0-100
    evidence_text: str
    why_problematic: str
    user_impact: str
    recommended_fix: str
    evidence: Dict[str, float]  # x, y, width, height

class AnalysisResult(BaseModel):
    overall_risk_score: float
    risk_level: str
    summary: str
    findings: List[FindingResult]
    analysis_notes: List[str]
```

If response doesn't match schema:
```
Error: 422 Unprocessable Entity
Details: Show which field failed validation
```

---

## Customization

### Change Model

```bash
# .env
GEMINI_MODEL=gemini-1.5-pro
```

### Change Thinking Level

```bash
# .env
GEMINI_THINKING_LEVEL=extended
```

### Custom System Prompt

Edit `backend/app/prompts/image_analysis.txt`:

```
# Add more examples
Example finding:
  Element: "Save 30%"
  Category: false_urgency
  Severity: medium
  ...

# Adjust tone
Be more/less aggressive about findings
```

### Adjust Confidence Threshold

Edit `backend/app/services/analysis_service.py`:

```python
MIN_CONFIDENCE = 40  # Current
# Change to 60 for stricter findings
# Change to 30 for more findings
```

---

## Troubleshooting

### "API key invalid"

**Problem:** Invalid or expired key

**Solution:**
1. Get new key: https://aistudio.google.com/app/apikeys
2. Update `.env`: `GEMINI_API_KEY=...`
3. Restart backend

### "Response parsing failed"

**Problem:** Gemini returned non-JSON

**Solution:**
1. Check system prompt - is it clear JSON should be returned?
2. Try again - sometimes timing issue
3. Check response contains valid JSON

### "Findings are generic/wrong"

**Problem:** AI not detecting real patterns

**Solution:**
1. Edit system prompt - be more specific
2. Add examples to prompt
3. Increase `analysis_depth`
4. Use better model (pro vs flash)

### "Rate limited (429)"

**Problem:** Too many requests to Gemini

**Solution:**
1. Wait 60 seconds
2. Retry
3. For production: implement queue

### "Coordinates wrong"

**Problem:** Evidence boxes in wrong place

**Solution:**
1. Verify Gemini outputs normalized coords
2. Check frontend conversion: `x * 100%`
3. Compare with actual UI

---

## Production Checklist

- [ ] Real Gemini API key configured
- [ ] Model set to production-ready version
- [ ] System prompt thoroughly tested
- [ ] Response validation working
- [ ] Error handling in place
- [ ] Timeout handling implemented
- [ ] Rate limiting considered
- [ ] Cost monitoring set up
- [ ] Fallback strategy ready
- [ ] Load testing done

---

## Cost Estimation

### Pricing

As of October 2024 (check official pricing):

- **gemini-2.0-flash**: $0.075 per million input tokens, $0.30 per million output tokens
- **gemini-1.5-flash**: $0.075 per million input tokens, $0.30 per million output tokens
- **gemini-1.5-pro**: $1.50 per million input tokens, $6.00 per million output tokens

### Example Costs

| Scenario | Tokens | Cost |
|----------|--------|------|
| 100 image audits | ~1M | $0.10 |
| 10 video audits | ~500K | $0.05 |
| Monthly (100 audits) | ~10M | $1.00 |

**Very affordable for MVP.**

---

## Next Steps

1. Get API key (5 min)
2. Add to `.env`
3. Restart backend
4. Test: `/api/health/gemini`
5. Upload image
6. See findings!

---

## Support

- **Gemini Docs**: https://ai.google.dev/docs
- **API Reference**: https://ai.google.dev/api/python
- **Status Page**: https://status.cloud.google.com
- **Community**: https://ai.google.dev/community

