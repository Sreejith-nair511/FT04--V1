# BACKEND INTEGRATION GUIDE

## Executive Summary

The CogniShield frontend is a polished Next.js 16 application (v0-generated) that provides a complete dark-pattern auditing UI. This document outlines the frontend architecture and specifies the exact API contracts required for backend integration.

**Key Principle:** Do not redesign the frontend. The backend must adapt its API responses to match the frontend's existing TypeScript interfaces and component expectations.

---

## Frontend Architecture Overview

### Tech Stack
- **Framework:** Next.js 16.4.0
- **React:** v19
- **UI Library:** Shadcn (Tailwind CSS)
- **Icons:** Lucide React
- **Type Safety:** TypeScript 5.7.3
- **Package Manager:** pnpm 12.3.4

### Project Structure
```
COGNISHIELD/
├── app/
│   ├── page.tsx          # Main single-page application (all routes)
│   ├── layout.tsx        # Root layout wrapper
│   └── globals.css       # Tailwind + brand colors/variables
├── components/
│   └── ui/
│       └── button.tsx    # Base UI component (minimal usage)
├── lib/
│   └── utils.ts          # cn() helper (clsx + tailwind-merge)
├── public/               # Icons and placeholder images
├── package.json
├── tsconfig.json
└── next.config.mjs
```

### Application Architecture

The frontend is a **single-page application (SPA)** with client-side routing. All screens/pages are rendered in `app/page.tsx` using React state to manage which view is displayed.

```
User Action
    ↓
React State Change (setActive)
    ↓
Conditional Rendering (page === 'Dashboard' ? <Dashboard /> : ...)
    ↓
UI Updated (no page reload)
```

---

## Navigation & Route System

The frontend uses a **virtual routing system** based on the `active` state variable, not Next.js file-based routing. The navigation items are:

### Main Routes

```
Dashboard         → Hero overview with sample audit
New Audit         → File upload interface for image/video
Audit History     → List of completed audits
Evidence          → Detailed finding view (Evidence Page)
Findings          → Pattern intelligence table view
Risk Intelligence → Risk analysis (placeholder)
Reports           → Report management (placeholder)
Remediation       → Remediation guidance (placeholder)
Pattern Library   → Pattern taxonomy (placeholder)
Settings          → Settings page (placeholder)
```

### Critical Routes (Fully Implemented)

1. **Dashboard** - Hero + Sample Audit Display
2. **New Audit** - Upload form (image/video)
3. **Evidence** - Detailed findings with visual evidence
4. **Findings** - Findings table with filters

---

## Frontend Data Model (Hardcoded)

The frontend currently uses hardcoded mock data. Here's the exact structure:

### Finding Object

```typescript
{
  id: '01',                           // Finding ID (string)
  name: 'Subscription Trap',          // Pattern name
  severity: 'High',                   // 'High' | 'Medium' | 'Low' | 'Critical'
  confidence: 94,                     // Number (0-100)
  text: 'Free trial — ₹499/month after 7 days',  // Evidence text
  impact: 'Users may unintentionally enter a recurring billing agreement.',  // User impact
  color: 'red',                       // 'red' | 'amber' | 'green'
  top: '57%',                         // Bounding box Y position (CSS percentage)
  left: '18%',                        // Bounding box X position (CSS percentage)
  width: '64%',                       // Bounding box width (CSS percentage)
  height: '14%'                       // Bounding box height (CSS percentage)
}
```

### Current Hardcoded Findings (Dashboard)

```typescript
const findings = [
  { id: '01', name: 'Subscription Trap', severity: 'High', confidence: 94, 
    text: 'Free trial — ₹499/month after 7 days', 
    impact: 'Users may unintentionally enter a recurring billing agreement.', 
    color: 'red', top: '57%', left: '18%', width: '64%', height: '14%' },
  { id: '02', name: 'Forced Action', severity: 'High', confidence: 89, 
    text: 'Continue to unlock your account', 
    impact: 'The primary path obscures the option to proceed without consent.', 
    color: 'red', top: '76%', left: '17%', width: '66%', height: '10%' },
  { id: '03', name: 'Trick Question', severity: 'Medium', confidence: 82, 
    text: 'Yes, I want helpful updates', 
    impact: 'Consent language makes the decline option less salient.', 
    color: 'amber', top: '35%', left: '17%', width: '66%', height: '12%' }
]
```

---

## UI Components That Need Backend Integration

### 1. Dashboard Page Component

**Current Behavior:**
- Displays hero section
- Shows sample audit (CS-1042) with hardcoded findings
- Phone preview with annotated evidence
- Risk ring showing 72/100 HIGH RISK

**Required Backend Integration:**
- Load sample audit data on component mount
- Fetch findings for the sample audit
- Display evidence coordinates on phone preview

**Expected Data Contract:**

```typescript
// Audit object
{
  id: string;              // UUID
  application_name: string; // "FinFlow Mobile Banking"
  platform: string;        // "iOS" | "Android" | "Web"
  status: 'queued' | 'processing' | 'completed' | 'failed';
  risk_score: number;      // 0-100
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL';
  summary: string;
  created_at: string;      // ISO 8601
  updated_at: string;      // ISO 8601
}

// Finding object
{
  id: string;
  finding_number: number;
  category: string;        // 'subscription_trap', 'forced_action', etc.
  title: string;           // "Subscription Trap"
  severity: 'low' | 'medium' | 'high' | 'critical';
  confidence: number;      // 0-100
  evidence_text: string;   // "Free trial — ₹499/month..."
  why_problematic: string;
  user_impact: string;
  recommended_fix: string;
}

// Evidence object (for bounding boxes)
{
  id: string;
  evidence_type: 'box' | 'text' | 'interactive';
  x: number;               // 0.0 - 1.0 (normalized)
  y: number;               // 0.0 - 1.0 (normalized)
  width: number;           // 0.0 - 1.0 (normalized)
  height: number;          // 0.0 - 1.0 (normalized)
  image_path: string;      // Path to evidence image
}
```

### 2. New Audit Component

**Current Behavior:**
- Two tabs: "Screenshot" and "Screen Recording"
- File input (not connected to anything)
- Form fields: Application, Platform, Analysis depth, AI model
- Submit button: "Run AI audit"

**Required Backend Integration:**
- Handle file upload when user clicks "Run AI audit"
- Send POST request to `/api/analyze/image` or `/api/analyze/video`
- Redirect to Evidence page on success
- Show error modal on failure

**Expected Form Fields:**
```typescript
{
  file: File;              // The uploaded image/video
  application_name: string; // From dropdown
  platform: string;        // From dropdown (iOS, Android, Web)
  analysis_depth: string;  // Deep analysis | Quick scan
}
```

**Expected API Request:**
```typescript
// POST /api/analyze/image
multipart/form-data {
  file: File
  application_name: "FinFlow Mobile Banking"
  platform: "iOS"
  analysis_depth: "Deep analysis"
}
```

**Expected API Response:**
```typescript
{
  audit_id: string;         // UUID of created audit
  status: "processing" | "completed";
  progress: number;         // 0-100
  current_stage: string;    // "Uploading evidence" | etc.
  result?: {
    risk_score: number;
    findings: Finding[];
  }
}
```

### 3. Evidence Page Component

**Current Behavior:**
- Displays audit summary (risk ring, stats)
- Shows phone preview with annotated evidence boxes
- Lists findings with expandable cards
- Finding click highlights bounding box on phone

**Required Backend Integration:**
- Load audit data by ID (from URL or state)
- Fetch all findings for the audit
- Fetch evidence coordinates
- Map backend evidence coordinates to CSS percentages

**Data Flow:**
```
Evidence Page
    ↓
GET /api/analysis/{audit_id}
    ↓
Display audit info + findings
    ↓
User clicks finding
    ↓
Highlight evidence box on phone preview
```

### 4. Findings Page Component

**Current Behavior:**
- Table view of all findings
- Severity and confidence columns
- Filter buttons (All, High, Medium)
- Search input (not connected)

**Required Backend Integration:**
- GET /api/findings?severity=high&search=...
- Support pagination
- Filter by severity, category, application, status

**Expected Query Parameters:**
```typescript
{
  page?: number;           // Default: 1
  page_size?: number;      // Default: 20
  severity?: 'low' | 'medium' | 'high' | 'critical';
  category?: string;
  application?: string;
  status?: 'open' | 'reviewed' | 'resolved';
  search?: string;         // Search in title/evidence_text
}
```

**Expected Response:**
```typescript
{
  items: Finding[];
  page: number;
  page_size: number;
  total: number;
  pages: number;
}
```

### 5. Report Generation

**Current Behavior:**
- "Export report" button on Evidence page
- No backend connection

**Required Backend Integration:**
- POST /api/reports/{audit_id}/pdf
- POST /api/reports/{audit_id}/json
- Return downloadable file or URL

---

## Coordinate System: CSS Percentages ↔ Normalized Coordinates

**Critical for Evidence Visualization**

The backend uses **normalized coordinates (0.0 - 1.0)** to be resolution-independent.
The frontend uses **CSS percentage coordinates** to match the phone preview.

### Conversion Formula

```typescript
// Backend normalized → Frontend CSS percentage
x_percent = x_normalized * 100 + "%"
y_percent = y_normalized * 100 + "%"
width_percent = width_normalized * 100 + "%"
height_percent = height_normalized * 100 + "%"

// Example:
// Backend: { x: 0.18, y: 0.57, width: 0.64, height: 0.14 }
// Frontend: { left: "18%", top: "57%", width: "64%", height: "14%" }
```

---

## Styling Color Mapping

The frontend uses these color classes for severity levels:

```typescript
// Severity → Color Mapping
'critical' or high-priority → 'red' (--red: #e9787d)
'high' → 'red'
'medium' → 'amber' (--amber: #d9aa61)
'low' → 'green' (--green: #62c899)

// Applied in finding-card CSS class
color: 'red' | 'amber' | 'green'

// UI Elements:
// - finding-number badge background
// - confidence-line fill
// - evidence-box border
// - severity label
```

---

## Existing Component Props & State

### Dashboard Component
```typescript
function Dashboard({ setActive }: { setActive: (s: string) => void }) {
  const [selected, setSelected] = useState(0)  // Currently selected finding index
  // ... renders phone with findings annotations
}
```

### Evidence Page Component
```typescript
function EvidencePage({ setActive }: { setActive: (s: string) => void }) {
  const [selected, setSelected] = useState(0)  // Currently selected finding index
  // ... displays full audit + findings
}
```

### New Audit Component
```typescript
function NewAudit({ setActive }: { setActive: (s: string) => void }) {
  const [tab, setTab] = useState('Screenshot')  // Screenshot | Screen Recording
  // ... file upload form
}
```

---

## API Endpoints Required by Frontend

### Health & Status
- `GET /api/health` - Backend health check
- `GET /api/health/gemini` - Gemini API connectivity check

### Audit Management
- `POST /api/analyze/image` - Upload and analyze screenshot
- `POST /api/analyze/video` - Upload and analyze video
- `GET /api/analysis/{audit_id}` - Get audit details + findings
- `GET /api/analysis/{audit_id}/status` - Get analysis progress
- `GET /api/analyses` - List all audits (pagination + filters)

### Findings
- `GET /api/findings` - List all findings (with filters)
- `GET /api/findings/{finding_id}` - Get single finding details

### Evidence
- `GET /api/evidence/{evidence_id}` - Get evidence details

### Reports
- `POST /api/reports/{audit_id}/pdf` - Generate PDF report
- `POST /api/reports/{audit_id}/json` - Generate JSON report
- `GET /api/reports/{audit_id}` - Get report details

### Cleanup
- `DELETE /api/audits/{audit_id}` - Delete audit (optional)

---

## Integration Checklist

### Phase 1: Discovery ✓ COMPLETE
- [x] Inspected frontend structure
- [x] Identified all routes and components
- [x] Documented data models
- [x] Mapped coordinate systems
- [x] Listed required API endpoints

### Phase 2: Backend Setup (Next)
- [ ] Create FastAPI project structure
- [ ] Set up SQLite database
- [ ] Create SQLAlchemy models
- [ ] Create Pydantic schemas

### Phase 3: Health & Basic Endpoints
- [ ] Implement GET /api/health
- [ ] Implement GET /api/health/gemini
- [ ] Add CORS middleware

### Phase 4: File Upload & Audit Creation
- [ ] Implement POST /api/analyze/image
- [ ] Implement POST /api/analyze/video
- [ ] Add file validation
- [ ] Create audit records in DB

### Phase 5: Gemini Integration
- [ ] Set up Gemini API client
- [ ] Implement image analysis
- [ ] Implement video analysis
- [ ] Structured output validation

### Phase 6: Findings & Evidence
- [ ] Implement finding creation from AI response
- [ ] Implement evidence box creation
- [ ] Implement coordinate system conversion
- [ ] Implement finding filtering

### Phase 7: Frontend Connection
- [ ] Create frontend API client (lib/api.ts)
- [ ] Connect New Audit form to backend
- [ ] Connect Evidence page to backend
- [ ] Connect Findings page to backend
- [ ] Test end-to-end flow

### Phase 8: Reports & Additional Features
- [ ] Implement PDF report generation
- [ ] Implement JSON report generation
- [ ] Add error handling
- [ ] Add logging

### Phase 9: Testing
- [ ] Unit tests for backends
- [ ] Integration tests for API endpoints
- [ ] Demo mode testing

### Phase 10: Documentation
- [ ] Create API.md
- [ ] Create DATABASE.md
- [ ] Create GEMINI_INTEGRATION.md
- [ ] Create ARCHITECTURE.md
- [ ] Create README.md
- [ ] Create TROUBLESHOOTING.md

---

## Frontend API Client (To Be Created)

Create: `src/lib/api.ts`

```typescript
const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

export async function createImageAudit(
  file: File,
  applicationName: string,
  platform: string,
  analysisDepth: string
) {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('application_name', applicationName)
  formData.append('platform', platform)
  formData.append('analysis_depth', analysisDepth)
  
  const res = await fetch(`${API_BASE}/api/analyze/image`, {
    method: 'POST',
    body: formData
  })
  return res.json()
}

export async function createVideoAudit(
  file: File,
  applicationName: string,
  platform: string
) {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('application_name', applicationName)
  formData.append('platform', platform)
  
  const res = await fetch(`${API_BASE}/api/analyze/video`, {
    method: 'POST',
    body: formData
  })
  return res.json()
}

export async function getAudit(auditId: string) {
  const res = await fetch(`${API_BASE}/api/analysis/${auditId}`)
  return res.json()
}

export async function getAudits(page = 1, pageSize = 20) {
  const res = await fetch(`${API_BASE}/api/analyses?page=${page}&page_size=${pageSize}`)
  return res.json()
}

export async function getFindings(filters?: {
  severity?: string
  category?: string
  search?: string
}) {
  const params = new URLSearchParams(filters)
  const res = await fetch(`${API_BASE}/api/findings?${params}`)
  return res.json()
}

export async function generatePdfReport(auditId: string) {
  const res = await fetch(`${API_BASE}/api/reports/${auditId}/pdf`)
  return res.blob()
}
```

---

## Environment Configuration (Frontend)

Create: `.env.local`

```
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Summary: What Backend Must Do

1. **Preserve all frontend UI** - No redesigns, no component changes
2. **Match data contracts** - Use exact field names from this document
3. **Implement all endpoints** - List above
4. **Handle file uploads** - Image and video validation
5. **Call Gemini API** - Get structured AI analysis
6. **Create findings** - Parse AI response into database records
7. **Provide evidence coordinates** - Normalized 0.0-1.0 values
8. **Support pagination & filtering** - For findings and audits lists
9. **Generate reports** - PDF and JSON exports
10. **Handle errors gracefully** - Return proper error responses

---

## Final Notes

- The frontend uses **hardcoded mock data** currently. The backend will replace these with real API calls.
- The frontend is a **single SPA**—there are no separate pages, just state-driven rendering.
- **Color mapping** (red/amber/green) is based on severity in the backend response.
- **Coordinate normalization** is critical—the frontend expects percentages, the backend should send normalized values.
- All frontend code is in `app/page.tsx`—this is the only file you need to understand for UI contracts.

Ready to build the backend. ✓

