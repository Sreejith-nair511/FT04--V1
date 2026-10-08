'use client'

import React, { useState, useEffect } from 'react'
import {
  Activity,
  AlertTriangle,
  ArrowRight,
  BarChart3,
  Bell,
  BookOpen,
  BrainCircuit,
  Check,
  ChevronDown,
  CircleHelp,
  Clock3,
  FileCheck2,
  FileText,
  Filter,
  Gauge,
  History,
  LayoutDashboard,
  LifeBuoy,
  LockKeyhole,
  Menu,
  Plus,
  Search,
  Settings,
  Shield,
  ShieldCheck,
  Sparkles,
  UploadCloud,
  UserRound,
  X,
  Zap,
  Loader,
} from 'lucide-react'

const API_BASE = 'http://localhost:8000/api'

type Finding = {
  id: string
  category: string
  title: string
  severity: string
  confidence: number
  evidence_text: string
  why_problematic: string
  user_impact: string
  recommended_fix: string
  evidence?: { x: number; y: number; width: number; height: number }[]
}

type Audit = {
  id: string
  application_name: string
  platform: string
  status: string
  risk_score: number
  risk_level: string
  summary?: string
  findings: Finding[]
}

// Helper to convert severity to color
const severityToColor = (severity: string) => severity?.toLowerCase() === 'high' || severity?.toLowerCase() === 'critical' ? 'red' : severity?.toLowerCase() === 'medium' ? 'amber' : 'green'

const navGroups = [
  { label: 'OVERVIEW', items: [['Dashboard', LayoutDashboard], ['New Audit', Plus], ['Audit History', History]] },
  { label: 'ANALYSIS', items: [['Findings', AlertTriangle], ['Evidence', FileCheck2], ['Risk Intelligence', BarChart3]] },
  { label: 'COMPLIANCE', items: [['Reports', FileText], ['Remediation', Sparkles], ['Pattern Library', BookOpen]] },
]

function Sidebar({ active, setActive, open, setOpen }: { active: string; setActive: (s: string) => void; open: boolean; setOpen: (b: boolean) => void }) {
  return <aside className={`sidebar ${open ? 'is-open' : ''}`}>
    <div className="brand"><span className="brand-mark"><ShieldCheck /></span><span>Cogni<span>Shield</span></span><button className="sidebar-close" onClick={() => setOpen(false)} aria-label="Close navigation"><X /></button></div>
    <div className="workspace"><div className="workspace-icon">C</div><div><strong>Compliance OS</strong><small>FinFlow workspace</small></div><ChevronDown /></div>
    <nav>{navGroups.map(group => <div className="nav-group" key={group.label}><p>{group.label}</p>{group.items.map(([label, Icon]) => <button key={label as string} className={`nav-item ${active === label ? 'active' : ''}`} onClick={() => { setActive(label as string); setOpen(false) }}><Icon />{label as string}{label === 'Findings' && <span className="nav-count">12</span>}</button>)}</div>)}</nav>
    <div className="sidebar-bottom"><button className="nav-item" onClick={() => setActive('Settings')}><Settings />Settings</button><button className="nav-item"><Activity /><span>API Status</span><i className="status-dot" /></button><div className="profile"><div className="avatar">AR</div><div><strong>Alex Rivera</strong><small>Administrator</small></div><MoreDots /></div></div>
  </aside>
}

function MoreDots() { return <span className="more-dots">•••</span> }

function Topbar({ active, setOpen }: { active: string; setOpen: (b: boolean) => void }) {
  return <header className="topbar"><button className="mobile-menu" onClick={() => setOpen(true)} aria-label="Open navigation"><Menu /></button><div className="crumb"><span>Workspace</span><b>/</b><strong>{active}</strong></div><div className="top-actions"><div className="operational"><i className="status-dot" />System Operational</div><div className="model-pill"><BrainCircuit />Gemini Multimodal <span>v2.5</span></div><button className="icon-button" aria-label="Notifications"><Bell /><i /></button><div className="avatar small">AR</div></div></header>
}

function RiskRing({ score = 72, level = 'HIGH' }: { score?: number; level?: string }) { return <div className="risk-ring"><div><strong>{score}</strong><span>/ 100</span><small>{level} RISK</small></div></div> }

function PhonePreview({ annotated = true, selected = 0, findings = [] }: { annotated?: boolean; selected?: number; findings?: any[] }) {
  return <div className="phone-wrap"><div className="phone"><div className="phone-notch" /><div className="phone-screen"><div className="phone-status"><span>9:41</span><span>▮▮▮ ◉</span></div><div className="finflow-head"><span className="mini-logo">f</span><div><b>FinFlow</b><small>Good morning, Alex</small></div><Bell /></div><div className="balance"><small>Total balance</small><strong>₹84,290.42</strong><span>↑ 12.8% this month</span></div><div className="quick-actions"><div><span>↗</span><small>Send</small></div><div><span>＋</span><small>Add</small></div><div><span>⌁</span><small>Pay</small></div><div><span>•••</span><small>More</small></div></div><div className="phone-card"><div className="card-top"><span>Unlock premium insights</span><small>×</small></div><b>Make your money work harder.</b><small>Get 7 days free, then ₹499/month.</small><button>Continue</button></div><div className="phone-section"><b>Recent activity</b><span>See all</span></div><div className="transaction"><i className="txn-icon">A</i><div><b>Adobe Creative Cloud</b><small>Today, 11:42 AM</small></div><strong>− ₹1,675</strong></div><div className="consent"><span>Yes, I want helpful updates</span><small>No thanks</small></div>{annotated && findings.map((f, i) => <button aria-label={`Evidence ${f.id}: ${f.name}`} key={f.id} onClick={() => {}} className={`evidence-box ${f.color} ${selected === i ? 'selected' : ''}`} style={{ top: f.top, left: f.left, width: f.width, height: f.height }}><span>{f.id}</span></button>)}</div></div></div>
}

function FindingCard({ finding, index, selected, onSelect }: { finding: any; index: number; selected: boolean; onSelect: () => void }) {
  return <article className={`finding-card ${selected ? 'selected' : ''}`} onClick={onSelect}><div className="finding-heading"><span className={`finding-number ${finding.color || 'red'}`}>{finding.id}</span><div><div className="finding-title"><b>{finding.name}</b><span className={`severity ${finding.color || 'red'}`}>{finding.severity}</span></div><small>{finding.confidence}% confidence</small></div><ChevronDown className={selected ? 'rotate' : ''} /></div><div className="confidence-line"><span style={{ width: `${finding.confidence}%` }} /></div><p className="evidence-quote">"{finding.text}"</p>{selected && <div className="finding-expanded"><p><b>Why it matters</b>{finding.why_problematic || 'This pattern may negatively impact users.'}</p><p><b>User impact</b>{finding.impact}</p><button className="text-button">Show remediation <ArrowRight /></button></div>}</article>
}

function Dashboard({ setActive }: { setActive: (s: string) => void }) {
  const [selected, setSelected] = useState(0)
  const [audit, setAudit] = useState<Audit | null>(null)
  const [findings, setFindings] = useState<Finding[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const fetchLatestAudit = async () => {
      try {
        const res = await fetch(`${API_BASE}/analyses?page=1&page_size=1`)
        if (!res.ok) throw new Error('Failed to fetch audits')
        const data = await res.json()
        
        if (data.items && data.items.length > 0) {
          const latestAudit = data.items[0]
          
          // Fetch full audit with findings
          const auditRes = await fetch(`${API_BASE}/analysis/${latestAudit.id}`)
          if (!auditRes.ok) throw new Error('Failed to fetch audit details')
          const auditData = await auditRes.json()
          
          setAudit(auditData.audit)
          setFindings(auditData.audit.findings || [])
        }
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load audit')
        console.error('Error fetching audit:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchLatestAudit()
  }, [])

  // Convert findings to display format
  const sampleFindings = findings.slice(0, 3).map((f, i) => ({
    id: `${i + 1}`,
    name: f.title,
    severity: f.severity?.charAt(0).toUpperCase() + f.severity?.slice(1).toLowerCase(),
    confidence: f.confidence,
    text: f.evidence_text,
    impact: f.user_impact,
    why_problematic: f.why_problematic,
    color: severityToColor(f.severity),
    top: (40 + i * 18) + '%',
    left: '17%',
    width: '66%',
    height: '12%'
  }))

  return <div className="page-content dashboard-page"><section className="hero"><div className="hero-copy"><div className="eyebrow"><span className="pulse-dot" />AI-POWERED DARK-PATTERN AUDITOR</div><h1>Find the manipulation<br /><em>before users pay the price.</em></h1><p>Analyze fintech interfaces for deceptive UX, hidden costs, coercive flows, and dark patterns — with visual evidence and actionable remediation.</p><div className="hero-ctas"><button className="primary-button" onClick={() => setActive('New Audit')}>Start New Audit <ArrowRight /></button><button className="secondary-button" onClick={() => setActive('Evidence')}>View Sample Audit</button></div><div className="trust-row"><ShieldCheck /> Synthetic demo data · No customer data stored</div></div><div className="hero-visual"><div className="scan-label top">LIVE ANALYSIS <i className="status-dot" /></div><PhonePreview selected={selected} annotated={sampleFindings.length > 0} findings={sampleFindings} /><div className="scan-orbit orbit-one" /><div className="scan-orbit orbit-two" />{sampleFindings.length > 0 && <>
    <div className="scan-callout callout-one"><span>{sampleFindings[0].id}</span><div><b>{sampleFindings[0].name}</b><small>{sampleFindings[0].confidence}% confidence</small></div></div>
    {sampleFindings[1] && <div className="scan-callout callout-two"><span>{sampleFindings[1].id}</span><div><b>{sampleFindings[1].name}</b><small>{sampleFindings[1].severity} severity</small></div></div>}
  </>}<div className="scan-line" /></div></section><section className="metrics-row"><Metric icon={Gauge} value="10+" label="Pattern classes" /><Metric icon={FileCheck2} value="Visual" label="Evidence-first" /><Metric icon={BrainCircuit} value="AI" label="Multimodal analysis" /></section><section className="how-section"><div className="section-heading"><div><span className="eyebrow">THE COGNISHIELD METHOD</span><h2>Evidence to action.</h2></div><p>One forensic workflow for every fintech experience.</p></div><div className="steps"><Step number="01" title="Upload" text="Screenshot or screen recording" icon={UploadCloud} /><Step number="02" title="Analyze" text="AI detects suspicious patterns" icon={ScanIcon} /><Step number="03" title="Remediate" text="Understand the issue and fix it" icon={Sparkles} /></div></section>{audit && findings.length > 0 && <section className="results-preview"><div className="section-heading"><div><span className="eyebrow">SAMPLE AUDIT · {audit.id.slice(0, 8).toUpperCase()}</span><h2>{audit.application_name}</h2></div><button className="text-button" onClick={() => setActive('Evidence')}>Open full audit <ArrowRight /></button></div><div className="audit-summary"><div className="risk-summary"><RiskRing score={audit.risk_score} level={audit.risk_level} /><div><span className="eyebrow">AI ASSESSMENT</span><p>{findings.length} deceptive interaction patterns were detected.</p></div></div><div className="summary-stats"><div><strong>{findings.length}</strong><span>Potential issues</span></div><div><strong>{findings.filter(f => f.severity?.toLowerCase() === 'high' || f.severity?.toLowerCase() === 'critical').length}</strong><span>High severity</span></div><div><strong>{findings.filter(f => f.severity?.toLowerCase() === 'medium').length}</strong><span>Medium</span></div></div></div><div className="evidence-layout"><div className="evidence-panel"><div className="panel-toolbar"><span>VISUAL EVIDENCE</span><div><button className="toolbar-active">Annotated</button><button>Compare</button><button>Fit</button></div></div><div className="evidence-stage"><PhonePreview selected={selected} annotated={true} findings={sampleFindings} /></div></div><div className="findings-panel"><div className="panel-title"><div><span className="eyebrow">DETECTED PATTERNS</span><h3>{findings.length} findings</h3></div><Filter /></div><div className="filter-row"><button className="filter-active">All <span>{findings.length}</span></button><button>High <span>{findings.filter(f => f.severity?.toLowerCase() === 'high' || f.severity?.toLowerCase() === 'critical').length}</span></button><button>Medium <span>{findings.filter(f => f.severity?.toLowerCase() === 'medium').length}</span></button></div>{sampleFindings.map((finding, i) => <FindingCard key={`${i}-${finding.id}`} finding={finding} index={i} selected={selected === i} onSelect={() => setSelected(i)} />)}</div></div></section>}</div>
}

function Metric({ icon: Icon, value, label }: { icon: any; value: string; label: string }) { return <div className="metric"><Icon /><div><strong>{value}</strong><span>{label}</span></div></div> }
function Step({ number, title, text, icon: Icon }: { number: string; title: string; text: string; icon: any }) { return <div className="step"><div className="step-num">{number}</div><div className="step-icon"><Icon /></div><h3>{title}</h3><p>{text}</p><ArrowRight /></div> }
function ScanIcon() { return <Zap /> }

function FindingsPage({ setActive }: { setActive: (s: string) => void }) {
  const [findings, setFindings] = useState<Finding[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchFindings = async () => {
      try {
        const res = await fetch(`${API_BASE}/findings?page=1&page_size=50`)
        if (!res.ok) throw new Error('Failed to fetch findings')
        const data = await res.json()
        setFindings(data.items || [])
      } catch (err) {
        console.error('Error fetching findings:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchFindings()
  }, [])

  return <div className="page-content inner-page"><div className="inner-header"><div><span className="eyebrow">ANALYSIS / PATTERN INTELLIGENCE</span><h1>Every signal, in one view.</h1><p>Detected dark patterns across your audited experiences.</p></div><button className="primary-button" onClick={() => setActive('New Audit')}><Plus /> New audit</button></div><div className="stat-grid"><Stat label="Total findings" value={findings.length.toString()} trend={`↑ ${Math.floor(findings.length * 0.18)}%`} /><Stat label="High risk" value={findings.filter(f => f.severity?.toLowerCase() === 'high' || f.severity?.toLowerCase() === 'critical').length.toString()} trend="↑ 6" danger /><Stat label="Financial impact" value="₹2.4M" trend="estimated" /><Stat label="Recurring patterns" value={new Set(findings.map(f => f.category)).size.toString()} trend={`across ${Math.ceil(findings.length / 6)} apps`} /></div><div className="table-card"><div className="table-toolbar"><div className="search-box"><Search /><input placeholder="Search findings..." /></div><button className="filter-button"><Filter /> Filters <span>2</span></button></div><table><thead><tr><th>Pattern</th><th>Application</th><th>Severity</th><th>Confidence</th><th>Detected</th><th>Status</th></tr></thead><tbody>{findings.slice(0, 6).map((f, i) => <tr key={f.id}><td><div className="pattern-cell"><span className={`pattern-icon ${severityToColor(f.severity)}`}>{i + 1}</span><b>{f.title}</b></div></td><td>FinFlow Mobile</td><td><span className={`severity ${severityToColor(f.severity)}`}>{f.severity?.charAt(0).toUpperCase() + f.severity?.slice(1).toLowerCase()}</span></td><td>{f.confidence}%</td><td>Oct {8 - i}, 2026</td><td><span className="status-badge">Open</span></td></tr>)}</tbody></table></div></div> }
function Stat({ label, value, trend, danger = false }: { label: string; value: string; trend: string; danger?: boolean }) { return <div className="stat-card"><span>{label}</span><strong className={danger ? 'danger-text' : ''}>{value}</strong><small className={danger ? 'danger-text' : ''}>{trend}</small></div> }

function NewAudit({ setActive }: { setActive: (s: string) => void }) {
  const [tab, setTab] = useState('Screenshot')
  const [uploading, setUploading] = useState(false)
  const [auditId, setAuditId] = useState<string | null>(null)

  const handleUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (!file) return

    try {
      setUploading(true)
      const formData = new FormData()
      formData.append('file', file)
      formData.append('application_name', 'FinFlow')
      formData.append('platform', 'iOS')

      const endpoint = tab === 'Screenshot' ? '/analyze/image' : '/analyze/video'
      const res = await fetch(`${API_BASE}${endpoint}`, {
        method: 'POST',
        body: formData
      })

      if (!res.ok) throw new Error('Upload failed')
      const data = await res.json()
      setAuditId(data.audit_id)
      
      // Redirect to evidence page after upload
      setTimeout(() => setActive('Evidence'), 2000)
    } catch (err) {
      console.error('Upload error:', err)
      alert('Upload failed. Please try again.')
    } finally {
      setUploading(false)
    }
  }

  return <div className="page-content inner-page"><div className="inner-header"><div><span className="eyebrow">NEW AUDIT / EVIDENCE INTAKE</span><h1>Analyze an experience.</h1><p>Upload evidence to identify deceptive design before it reaches users.</p></div></div><div className="audit-grid"><div className="upload-card"><div className="tabs"><button className={tab === 'Screenshot' ? 'tab-active' : ''} onClick={() => setTab('Screenshot')}>Screenshot</button><button className={tab === 'Screen Recording' ? 'tab-active' : ''} onClick={() => setTab('Screen Recording')}>Screen recording</button></div><div className="dropzone"><div className="upload-icon">{uploading ? <Loader className="animate-spin" /> : <UploadCloud />}</div><h2>Drop your evidence here</h2><p>{tab === 'Screenshot' ? 'PNG, JPG, WEBP up to 20MB' : 'MP4, MOV up to 200MB'}</p><label className="secondary-button" htmlFor="audit-file">{uploading ? 'Uploading...' : 'Browse files'}</label><input id="audit-file" type="file" accept={tab === 'Screenshot' ? 'image/png,image/jpeg,image/webp' : 'video/mp4,video/quicktime'} onChange={handleUpload} disabled={uploading} className="sr-only" /><span>or use <button className="link-button" onClick={() => setActive('Evidence')}>Sample FinTech Audit</button></span></div></div><div className="config-card"><div className="eyebrow">AUDIT CONFIGURATION</div><Field label="Application" value="FinFlow Mobile Banking" /><Field label="Platform" value="iOS" /><Field label="Analysis depth" value="Deep analysis" /><Field label="AI model" value="Gemini Multimodal" icon={BrainCircuit} /><button className="primary-button full" onClick={() => setActive('Evidence')}>Run AI audit <ArrowRight /></button></div></div><div className="upload-note"><LockKeyhole /> Files are encrypted in transit and retained for 30 days. <a>View data policy</a></div></div> }
function Field({ label, value, icon: Icon }: { label: string; value: string; icon?: any }) { return <label className="field"><span>{label}</span><div>{Icon && <Icon />}{value}<ChevronDown /></div></label> }

function EvidencePage({ setActive }: { setActive: (s: string) => void }) {
  const [selected, setSelected] = useState(0)
  const [audit, setAudit] = useState<Audit | null>(null)
  const [findings, setFindings] = useState<Finding[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const fetchLatestAudit = async () => {
      try {
        const res = await fetch(`${API_BASE}/analyses?page=1&page_size=1`)
        if (!res.ok) throw new Error('Failed to fetch audits')
        const data = await res.json()
        
        if (data.items && data.items.length > 0) {
          const latestAudit = data.items[0]
          
          const auditRes = await fetch(`${API_BASE}/analysis/${latestAudit.id}`)
          if (!auditRes.ok) throw new Error('Failed to fetch audit details')
          const auditData = await auditRes.json()
          
          setAudit(auditData.audit)
          setFindings(auditData.audit.findings || [])
        }
      } catch (err) {
        console.error('Error fetching audit:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchLatestAudit()
  }, [])

  const sampleFindings = findings.slice(0, 3).map((f, i) => ({
    id: `${i + 1}`,
    name: f.title,
    severity: f.severity?.charAt(0).toUpperCase() + f.severity?.slice(1).toLowerCase(),
    confidence: f.confidence,
    text: f.evidence_text,
    impact: f.user_impact,
    why_problematic: f.why_problematic,
    color: severityToColor(f.severity),
    top: (40 + i * 18) + '%',
    left: '17%',
    width: '66%',
    height: '12%'
  }))

  return <div className="page-content inner-page evidence-page"><div className="inner-header"><div><span className="eyebrow">AUDIT #{audit?.id.slice(0, 8).toUpperCase() || 'CS-1042'} · {audit?.status === 'completed' ? 'ANALYSIS COMPLETE' : 'PROCESSING'}</span><h1>{audit?.application_name || 'FinFlow Mobile Banking'}</h1><p>Last analyzed {new Date().toLocaleDateString()} · Synthetic demo data</p></div><div className="header-actions"><button className="secondary-button"><FileText /> Export report</button><button className="primary-button" onClick={() => setActive('New Audit')}><Plus /> New audit</button></div></div><div className="audit-overview"><div className="overview-risk"><RiskRing score={audit?.risk_score || 72} level={audit?.risk_level || 'HIGH'} /><div><span className="eyebrow">OVERALL RISK</span><h2>{audit?.risk_level || 'High'} risk experience</h2><p>{audit?.summary || 'The highest-risk issue involves a preselected recurring payment option combined with ambiguous cancellation language.'}</p></div></div><div className="overview-stat"><strong>{findings.length}</strong><span>Potential issues</span></div><div className="overview-stat"><strong className="danger-text">{findings.filter(f => f.severity?.toLowerCase() === 'high' || f.severity?.toLowerCase() === 'critical').length}</strong><span>High severity</span></div><div className="overview-stat"><strong className="amber-text">{findings.filter(f => f.severity?.toLowerCase() === 'medium').length}</strong><span>Medium severity</span></div><div className="overview-stat"><strong className="green-text">{findings.filter(f => f.severity?.toLowerCase() === 'low').length}</strong><span>Low severity</span></div></div><div className="evidence-layout full-evidence"><div className="evidence-panel"><div className="panel-toolbar"><span>VISUAL EVIDENCE <small>{findings.length} markers</small></span><div><button className="toolbar-active">Annotated</button><button>Original</button><button>Compare</button><button>＋</button><button>−</button></div></div><div className="evidence-stage large"><PhonePreview selected={selected} annotated={true} findings={sampleFindings} /></div></div><div className="findings-panel"><div className="panel-title"><div><span className="eyebrow">DETECTED PATTERNS</span><h3>Findings</h3></div><button className="icon-button"><Filter /></button></div><div className="filter-row"><button className="filter-active">All <span>{findings.length}</span></button><button>High <span>{findings.filter(f => f.severity?.toLowerCase() === 'high' || f.severity?.toLowerCase() === 'critical').length}</span></button><button>Medium <span>{findings.filter(f => f.severity?.toLowerCase() === 'medium').length}</span></button></div>{sampleFindings.map((finding, i) => <FindingCard key={`${i}-${finding.id}`} finding={finding} index={i} selected={selected === i} onSelect={() => setSelected(i)} />)}</div></div><div className="remediation-strip"><div><span className="eyebrow">NEXT BEST ACTION</span><h3>Make consent as clear as the conversion.</h3><p>Review the compliant alternative for Subscription Trap and add it to your compliance report.</p></div><button className="secondary-button" onClick={() => setActive('Remediation')}>View remediation <ArrowRight /></button></div></div> }

function GenericPage({ title, eyebrow, setActive }: { title: string; eyebrow: string; setActive: (s: string) => void }) { return <div className="page-content inner-page empty-page"><div className="inner-header"><div><span className="eyebrow">{eyebrow}</span><h1>{title}</h1><p>Explore your compliance intelligence workspace.</p></div><button className="primary-button" onClick={() => setActive('New Audit')}><Plus /> New audit</button></div><div className="generic-visual"><div className="generic-orb"><ShieldCheck /></div><h2>Your intelligence layer is ready.</h2><p>Run an audit to populate this view with evidence-backed insights and remediation paths.</p><button className="secondary-button" onClick={() => setActive('New Audit')}>Start an audit <ArrowRight /></button></div></div> }

export default function Page() { const [active, setActive] = useState('Dashboard'); const [sidebarOpen, setSidebarOpen] = useState(false); const page = active === 'Dashboard' ? <Dashboard setActive={setActive} /> : active === 'New Audit' ? <NewAudit setActive={setActive} /> : active === 'Evidence' ? <EvidencePage setActive={setActive} /> : active === 'Findings' ? <FindingsPage setActive={setActive} /> : <GenericPage title={active} eyebrow={`COGNISHIELD / ${active.toUpperCase()}`} setActive={setActive} />; return <div className="app-shell"><Sidebar active={active} setActive={setActive} open={sidebarOpen} setOpen={setSidebarOpen} /><div className="main-shell"><Topbar active={active} setOpen={setSidebarOpen} />{page}</div></div> }
