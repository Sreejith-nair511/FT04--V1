# CogniShield API Reference

Base URL: `http://localhost:8000`

All timestamps are ISO 8601 format (UTC).

---

## Health Endpoints

### GET /api/health

System health check.

**Response:**
```json
{
  "status": "ok",
  "database": "ok",
  "storage": "ok",
  "gemini_configured": true,
  "gemini_model": "gemini-2.0-flash-exp"
}
```

**Status Values:**
- `ok` - All systems operational
- `degraded` - Some systems unavailable
- `error` - Critical failure

---

### GET /api/health/gemini

Gemini API connectivity check.

**Response (Connected):**
```json
{
  "status": "connected",
  "model": "gemini-2.0-flash-exp",
  "message": "Gemini API is healthy"
}
```

**Response (Not Configured):**
```json
{
  "status": "not_configured",
  "model": null,
  "message": "Gemini API key is not configured"
}
```

**Response (Error):**
```json
{
  "status": "error",
  "model": "gemini-2.0-flash-exp",
  "message": "Failed to connect to Gemini API"
}
```

---

## Analysis Endpoints

### POST /api/analyze/image

Upload and analyze a screenshot.

**Parameters:**
- `file` (required, multipart/form-data) - Image file (PNG, JPG, WEBP, max 20MB)
- `application_name` (required) - App name, e.g., "FinFlow"
- `platform` (required) - Platform: "iOS", "Android", or "Web"
- `analysis_depth` (optional) - "Deep analysis" or "Quick scan" (default: "Deep analysis")

**Example Request:**
```bash
curl -X POST http://localhost:8000/api/analyze/image \
  -F "file=@screenshot.png" \
  -F "application_name=FinFlow" \
  -F "platform=iOS" \
  -F "analysis_depth=Deep analysis"
```

**Response:**
```json
{
  "audit_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "progress": 5,
  "current_stage": "Queued for analysis",
  "message": "Image uploaded successfully, analysis starting..."
}
```

**Status Codes:**
- `200` - Upload successful
- `400` - Invalid file (wrong type, too large)
- `413` - File too large
- `500` - Server error

**Error Response:**
```json
{
  "error": {
    "code": "INVALID_FILE",
    "message": "Invalid image format. Allowed: .png, .jpg, .jpeg, .webp",
    "details": null
  }
}
```

---

### POST /api/analyze/video

Upload and analyze a screen recording.

**Parameters:**
- `file` (required) - Video file (MP4, MOV, WEBM, max 200MB)
- `application_name` (required) - App name
- `platform` (required) - "iOS", "Android", or "Web"

**Example Request:**
```bash
curl -X POST http://localhost:8000/api/analyze/video \
  -F "file=@recording.mp4" \
  -F "application_name=FinFlow" \
  -F "platform=iOS"
```

**Response:**
```json
{
  "audit_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "progress": 5,
  "current_stage": "Queued for video analysis",
  "message": "Video uploaded successfully, analysis starting..."
}
```

---

## Audit Endpoints

### GET /api/analysis/{audit_id}

Get audit details with all findings and evidence.

**Parameters:**
- `audit_id` (required, path) - Audit UUID

**Example Request:**
```bash
curl http://localhost:8000/api/analysis/550e8400-e29b-41d4-a716-446655440000
```

**Response:**
```json
{
  "audit": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    "application_name": "FinFlow",
    "platform": "iOS",
    "input_type": "image",
    "status": "completed",
    "risk_score": 72,
    "risk_level": "HIGH",
    "summary": "Multiple deceptive interaction patterns detected...",
    "model_name": "gemini-2.0-flash-exp",
    "created_at": "2024-10-08T14:32:00Z",
    "updated_at": "2024-10-08T14:35:00Z",
    "completed_at": "2024-10-08T14:35:00Z",
    "findings": [
      {
        "id": "f123...",
        "audit_id": "550e8400-e29b-41d4-a716-446655440000",
        "finding_number": 1,
        "category": "subscription_trap",
        "title": "Subscription Trap",
        "severity": "high",
        "confidence": 94,
        "evidence_text": "Free trial — ₹499/month after 7 days",
        "why_problematic": "The recurring payment condition is visually subordinate...",
        "user_impact": "Users may unintentionally enter a recurring billing agreement.",
        "recommended_fix": "Make the trial terms and recurring cost equally prominent.",
        "status": "open",
        "created_at": "2024-10-08T14:35:00Z",
        "evidence": [
          {
            "id": "e456...",
            "finding_id": "f123...",
            "audit_id": "550e8400-e29b-41d4-a716-446655440000",
            "evidence_type": "box",
            "x": 0.18,
            "y": 0.57,
            "width": 0.64,
            "height": 0.14,
            "image_path": null,
            "text": null,
            "created_at": "2024-10-08T14:35:00Z"
          }
        ]
      }
    ]
  },
  "status": "completed",
  "risk_score": 72,
  "risk_level": "HIGH"
}
```

**Status Codes:**
- `200` - Success
- `404` - Audit not found
- `500` - Server error

---

### GET /api/analysis/{audit_id}/status

Get real-time analysis status.

**Parameters:**
- `audit_id` (required, path) - Audit UUID

**Example Request:**
```bash
curl http://localhost:8000/api/analysis/550e8400-e29b-41d4-a716-446655440000/status
```

**Response (Processing):**
```json
{
  "audit_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "processing",
  "progress": 65,
  "current_stage": "Detecting dark patterns",
  "error_message": null,
  "started_at": "2024-10-08T14:32:15Z",
  "completed_at": null
}
```

**Response (Completed):**
```json
{
  "audit_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "progress": 100,
  "current_stage": "Analysis complete",
  "error_message": null,
  "started_at": "2024-10-08T14:32:15Z",
  "completed_at": "2024-10-08T14:35:00Z"
}
```

**Response (Failed):**
```json
{
  "audit_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "failed",
  "progress": 0,
  "current_stage": "Failed",
  "error_message": "Image analysis failed: Invalid response format",
  "started_at": "2024-10-08T14:32:15Z",
  "completed_at": "2024-10-08T14:33:00Z"
}
```

**Stages:**
1. Queued
2. Uploading evidence (20%)
3. Extracting interface structure (40%)
4. Analyzing visual hierarchy (60%)
5. Detecting dark patterns (80%)
6. Calculating risk score (90%)
7. Saving results (95%)
8. Analysis complete (100%)

---

### GET /api/analyses

List all audits with pagination and filtering.

**Query Parameters:**
- `page` (optional, int) - Page number (default: 1, min: 1)
- `page_size` (optional, int) - Items per page (default: 20, max: 100)
- `severity` (optional) - Filter by severity: "low", "medium", "high", "critical"
- `status` (optional) - Filter by status: "queued", "processing", "completed", "failed"
- `search` (optional) - Search in application name or summary

**Example Requests:**
```bash
# List all audits
curl http://localhost:8000/api/analyses

# Page 2, 10 items per page
curl http://localhost:8000/api/analyses?page=2&page_size=10

# Filter by HIGH severity
curl http://localhost:8000/api/analyses?severity=high

# Search for FinFlow
curl "http://localhost:8000/api/analyses?search=finflow"

# Completed audits, page 1
curl "http://localhost:8000/api/analyses?status=completed&page=1"
```

**Response:**
```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "application_name": "FinFlow",
      "platform": "iOS",
      "input_type": "image",
      "status": "completed",
      "risk_score": 72,
      "risk_level": "HIGH",
      "summary": "Multiple deceptive patterns...",
      "model_name": "gemini-2.0-flash-exp",
      "created_at": "2024-10-08T14:32:00Z",
      "updated_at": "2024-10-08T14:35:00Z",
      "completed_at": "2024-10-08T14:35:00Z"
    }
  ],
  "page": 1,
  "page_size": 20,
  "total": 42,
  "pages": 3
}
```

---

### DELETE /api/audits/{audit_id}

Delete an audit and all associated data.

**Parameters:**
- `audit_id` (required, path) - Audit UUID

**Example Request:**
```bash
curl -X DELETE http://localhost:8000/api/audits/550e8400-e29b-41d4-a716-446655440000
```

**Response:**
```json
{
  "message": "Audit 550e8400-e29b-41d4-a716-446655440000 deleted"
}
```

**Status Codes:**
- `200` - Deleted successfully
- `404` - Audit not found
- `500` - Server error

---

## Finding Endpoints

### GET /api/findings

List all findings with filtering and pagination.

**Query Parameters:**
- `page` (optional) - Page number (default: 1)
- `page_size` (optional) - Items per page (default: 20)
- `severity` (optional) - "low", "medium", "high", "critical"
- `category` (optional) - Pattern category name
- `status` (optional) - "open", "reviewed", "resolved"
- `search` (optional) - Search in title and evidence text

**Example Requests:**
```bash
# All findings
curl http://localhost:8000/api/findings

# High severity only
curl http://localhost:8000/api/findings?severity=high

# Search for "subscription"
curl "http://localhost:8000/api/findings?search=subscription"
```

**Response:**
```json
{
  "items": [
    {
      "id": "f123...",
      "audit_id": "550e8400-e29b-41d4-a716-446655440000",
      "finding_number": 1,
      "category": "subscription_trap",
      "title": "Subscription Trap",
      "severity": "high",
      "confidence": 94,
      "evidence_text": "Free trial — ₹499/month after 7 days",
      "why_problematic": "...",
      "user_impact": "...",
      "recommended_fix": "...",
      "status": "open",
      "created_at": "2024-10-08T14:35:00Z"
    }
  ],
  "page": 1,
  "page_size": 20,
  "total": 48,
  "pages": 3
}
```

---

### GET /api/findings/{finding_id}

Get a single finding.

**Parameters:**
- `finding_id` (required, path) - Finding UUID

**Response:**
```json
{
  "id": "f123...",
  "audit_id": "550e8400-e29b-41d4-a716-446655440000",
  "finding_number": 1,
  "category": "subscription_trap",
  "title": "Subscription Trap",
  "severity": "high",
  "confidence": 94,
  "evidence_text": "Free trial — ₹499/month after 7 days",
  "why_problematic": "...",
  "user_impact": "...",
  "recommended_fix": "...",
  "status": "open",
  "created_at": "2024-10-08T14:35:00Z"
}
```

---

## Evidence Endpoints

### GET /api/evidence/{evidence_id}

Get a single evidence item.

**Parameters:**
- `evidence_id` (required, path) - Evidence UUID

**Response:**
```json
{
  "id": "e456...",
  "finding_id": "f123...",
  "audit_id": "550e8400-e29b-41d4-a716-446655440000",
  "evidence_type": "box",
  "frame_number": null,
  "timestamp_seconds": null,
  "x": 0.18,
  "y": 0.57,
  "width": 0.64,
  "height": 0.14,
  "image_path": null,
  "text": null,
  "created_at": "2024-10-08T14:35:00Z"
}
```

**Coordinate Notes:**
- All coordinates are normalized (0.0 - 1.0)
- Convert to CSS percentages for display: `x * 100 + "%"`
- `frame_number` and `timestamp_seconds` are set for video evidence

---

## Report Endpoints

### POST /api/reports/{audit_id}/json

Generate JSON report.

**Parameters:**
- `audit_id` (required, path) - Audit UUID

**Response:**
```json
{
  "report_type": "json",
  "generated_at": "2024-10-08T14:35:00Z",
  "audit": {
    "id": "550e8400-e29b-41d4-a716-446655440000",
    ...all audit data...
  }
}
```

---

### POST /api/reports/{audit_id}/pdf

Generate PDF report (placeholder).

**Parameters:**
- `audit_id` (required, path) - Audit UUID

**Status:**
- PDF generation is not yet implemented
- Currently returns JSON response
- Will be implemented in Phase 8

---

### GET /api/reports/{audit_id}

Get report metadata.

**Parameters:**
- `audit_id` (required, path) - Audit UUID

**Response:**
```json
{
  "audit_id": "550e8400-e29b-41d4-a716-446655440000",
  "status": "completed",
  "available_formats": ["json", "pdf"],
  "json_url": "/api/reports/550e8400-e29b-41d4-a716-446655440000/json",
  "pdf_url": "/api/reports/550e8400-e29b-41d4-a716-446655440000/pdf"
}
```

---

## Error Handling

All errors return consistent JSON structure:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": "Optional additional details"
  }
}
```

**Common Error Codes:**
- `INVALID_FILE` - File format or size invalid
- `ANALYSIS_FAILED` - AI analysis failed
- `NOT_FOUND` - Resource not found
- `INTERNAL_ERROR` - Server error

**Status Codes:**
- `200` - Success
- `400` - Bad request (client error)
- `404` - Not found
- `413` - Payload too large
- `500` - Server error

---

## Rate Limiting

Currently unlimited. For production, implement:
- 100 requests/minute per IP
- 10 video uploads/day per user
- 1000 requests/day per API key

---

## Data Types

### Risk Levels
```
"LOW"      (0-24)
"MEDIUM"   (25-49)
"HIGH"     (50-74)
"CRITICAL" (75-100)
```

### Severities
```
"low"
"medium"
"high"
"critical"
```

### Statuses
```
Audit: "queued", "processing", "completed", "failed"
Finding: "open", "reviewed", "resolved"
Job: "queued", "processing", "completed", "failed"
```

### Evidence Types
```
"box"         - Bounding box
"text"        - Text content
"interactive" - Interactive element
```

### Categories
```
"subscription_trap"  - Hidden recurring billing
"false_urgency"      - Time-based pressure
"forced_action"      - Blocking without consent
"basket_sneaking"    - Hidden costs at checkout
"confirm_shaming"    - Hard to decline
"bait_and_switch"    - Promise vs reality
"disguised_ads"      - Ads as content
"nagging"            - Persistent reminders
"trick_questions"    - Confusing language
"hidden_costs"       - Fees not upfront
"other"              - Uncategorized
```

---

## Pagination

All list endpoints support pagination:

```
GET /api/findings?page=2&page_size=50

Response:
{
  "items": [...],
  "page": 2,
  "page_size": 50,
  "total": 1234,
  "pages": 25
}
```

- Default page size: 20
- Max page size: 100
- Pages start at 1

---

## Authentication

Currently no authentication (MVP).

For production, add:
- JWT bearer tokens
- User audits isolation
- Admin endpoints

---

## CORS

Frontend origin must be in `CORS_ORIGINS` env var:

```
CORS_ORIGINS=http://localhost:3000,https://cognishield.example.com
```

---

## Timestamps

All timestamps in ISO 8601 UTC format:
```
"2024-10-08T14:35:00Z"
```

Use `.isoformat()` in Python, `toISOString()` in JavaScript.

