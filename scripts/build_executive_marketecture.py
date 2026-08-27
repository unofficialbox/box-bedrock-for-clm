#!/usr/bin/env python3
"""Build a self-contained executive marketecture page for the CLM demo."""

from __future__ import annotations

import base64
import html
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCREENSHOTS = ROOT / "output" / "screenshots"
OUTPUT = ROOT / "output" / "html" / "03-executive-marketecture.html"
BRAND_ASSETS = ROOT / "docs" / "design" / "brand-assets"

PROOF = (
    {
        "path": SCREENSHOTS / "box-automate-agentic-orchestration" / "box-app-dashboard-live.png",
        "label": "Operate",
        "title": "One contract operations cockpit",
        "copy": "Status, risk, approvals, intake, clause standards, and executed agreements stay visible in a governed workspace.",
    },
    {
        "path": SCREENSHOTS / "box-automate-agentic-orchestration" / "automate-approval-flow.png",
        "label": "Govern",
        "title": "Human accountability by design",
        "copy": "AI prepares the evidence; named reviewers make the consequential decisions before downstream action.",
    },
    {
        "path": SCREENSHOTS / "cross-platform-agentic-orchestration" / "clm-react-workspace.png",
        "label": "Engage",
        "title": "Business context where teams work",
        "copy": "The contract workspace brings governed Box content and Salesforce Agentforce context into one experience.",
    },
    {
        "path": SCREENSHOTS / "cross-platform-agentic-orchestration" / "clm-react-redline-reviews.png",
        "label": "Decide",
        "title": "Route exceptions to the right experts",
        "copy": "Redline differences become cited, domain-specific reviews for Legal, Finance, Privacy, and other owners.",
    },
)


def data_uri(path: Path) -> str:
    if not path.is_file():
        raise FileNotFoundError(path)
    mime = "image/png" if path.suffix.lower() == ".png" else "image/jpeg"
    return f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode('ascii')}"


def asset_data_uri(filename: str, media_type: str) -> str:
    """Return an official brand asset as an embedded data URI."""

    encoded = base64.b64encode((BRAND_ASSETS / filename).read_bytes()).decode("ascii")
    return f"data:{media_type};base64,{encoded}"


def icon(name: str) -> str:
    paths = {
        "intake": '<path d="M12 3v12m0 0 4-4m-4 4-4-4"/><path d="M5 15v4h14v-4"/>',
        "understand": '<circle cx="10.5" cy="10.5" r="5.5"/><path d="m15 15 4 4"/>',
        "decide": '<path d="M7 7h10v10H7z"/><path d="m9.5 12 1.8 1.8 3.7-4"/>',
        "execute": '<path d="M4 18c4-1 6-4 8-8l2 2 5-5-2-2-5 5"/><path d="M4 20h16"/>',
        "learn": '<path d="M5 18V9m5 9V5m5 13v-6m5 6V3"/>',
        "shield": '<path d="M12 3 5 6v5c0 4.4 2.8 7.8 7 10 4.2-2.2 7-5.6 7-10V6l-7-3Z"/><path d="m9 12 2 2 4-4"/>',
        "check": '<circle cx="12" cy="12" r="9"/><path d="m8 12 2.6 2.6L16.5 9"/>',
        "target": '<circle cx="12" cy="12" r="8"/><circle cx="12" cy="12" r="4"/><path d="m15 9 5-5"/>',
    }
    return f'<svg viewBox="0 0 24 24" aria-hidden="true">{paths[name]}</svg>'


def proof_cards() -> str:
    cards = []
    for index, item in enumerate(PROOF, start=1):
        title = html.escape(item["title"])
        cards.append(
            f'''<article class="proof-card">
              <button class="proof-image" type="button" data-proof="{index - 1}" aria-label="Open {title} screenshot">
                <img src="{data_uri(item['path'])}" alt="{title} real demo screenshot" loading="lazy">
                <span>View real demo screen</span>
              </button>
              <div class="proof-copy"><p class="label">{html.escape(item['label'])}</p><h3>{title}</h3><p>{html.escape(item['copy'])}</p></div>
            </article>'''
        )
    return "\n".join(cards)


def build() -> Path:
    box_logo = asset_data_uri("box-logo-blue.svg", "image/svg+xml")
    salesforce_logo = asset_data_uri("salesforce-logo.jpeg", "image/jpeg")
    databricks_logo = asset_data_uri(
        "databricks-primary-lockup-full-color.png", "image/png"
    )
    document = f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="Executive marketecture for governed, AI-assisted contract lifecycle management.">
  <title>Acme CLM · Executive Marketecture</title>
  <style>
    :root {{
      color-scheme: light;
      --ink: #0b1f41;
      --muted: #52647e;
      --blue: #0061d5;
      --blue-soft: #eaf3ff;
      --teal: #087f8c;
      --teal-soft: #e7f8f7;
      --violet: #6b4ed6;
      --violet-soft: #f2efff;
      --line: #d8e1ee;
      --surface: #ffffff;
      --canvas: #f5f8fc;
      --shadow: 0 18px 50px rgba(21, 53, 96, .1);
      --radius: 22px;
    }}
    * {{ box-sizing: border-box; }}
    html {{ scroll-behavior: smooth; }}
    body {{ margin: 0; color: var(--ink); background: var(--surface); font: 16px/1.55 -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}
    button {{ font: inherit; }}
    svg {{ width: 24px; height: 24px; fill: none; stroke: currentColor; stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round; }}
    .shell {{ width: min(1240px, calc(100% - 40px)); margin-inline: auto; }}
    .topbar {{ min-height: 74px; display: flex; align-items: center; justify-content: space-between; gap: 24px; border-bottom: 1px solid var(--line); }}
    .brand {{ display: flex; align-items: center; gap: 18px; font-weight: 720; letter-spacing: -.01em; }}
    .box-mark {{ width: 68px; height: 38px; object-fit: contain; }}
    .brand span:last-child {{ border-left: 1px solid var(--line); padding-left: 18px; }}
    .audience {{ color: var(--muted); font-size: .82rem; }}
    .hero {{ padding: 76px 0 56px; }}
    h1, h2 {{ font-family: ui-serif, Georgia, Cambria, "Times New Roman", serif; font-weight: 620; letter-spacing: -.045em; }}
    h1 {{ max-width: 980px; margin: 0; font-size: clamp(3.4rem, 7.3vw, 6.7rem); line-height: .96; }}
    .lead {{ max-width: 760px; margin: 28px 0 0; color: var(--muted); font-size: clamp(1.1rem, 2vw, 1.38rem); }}
    .metrics {{ margin-top: 48px; display: grid; grid-template-columns: repeat(4, 1fr); gap: 14px; }}
    .metric {{ min-height: 190px; padding: 24px; border: 1px solid var(--line); border-radius: 18px; background: var(--surface); box-shadow: 0 9px 28px rgba(24, 66, 120, .06); }}
    .metric strong {{ display: block; margin: 14px 0 2px; color: var(--blue); font: 650 clamp(2.2rem, 4vw, 3.8rem)/1 ui-serif, Georgia, serif; letter-spacing: -.045em; }}
    .metric b {{ display: block; margin-top: 10px; font-size: .98rem; }}
    .metric small {{ display: block; margin-top: 4px; color: var(--muted); }}
    .metric .icon {{ color: var(--blue); width: 44px; height: 44px; display: grid; place-items: center; border: 1px solid #a9cafa; border-radius: 50%; }}
    .metric-note {{ margin: 12px 0 0; color: #6a7b92; font-size: .78rem; text-align: right; }}
    .journey {{ padding: 38px 0 64px; }}
    .journey-grid {{ display: grid; grid-template-columns: repeat(5, 1fr); border: 1px solid #b9d1ef; border-radius: var(--radius); overflow: hidden; }}
    .step {{ position: relative; min-height: 220px; padding: 28px 24px; background: linear-gradient(180deg, #fff, #f8fbff); border-right: 1px solid var(--line); }}
    .step:last-child {{ border-right: 0; }}
    .step::after {{ content: ""; position: absolute; top: 48px; right: -6px; width: 10px; height: 10px; border-top: 1px solid var(--blue); border-right: 1px solid var(--blue); transform: rotate(45deg); z-index: 2; background: #fff; }}
    .step:last-child::after {{ display: none; }}
    .step .number {{ color: var(--blue); font-weight: 760; }}
    .step h3 {{ margin: 26px 0 8px; font-size: 1.05rem; }}
    .step p {{ margin: 0; color: var(--muted); font-size: .88rem; }}
    .step-icon {{ width: 44px; height: 44px; display: grid; place-items: center; color: var(--blue); border: 1px solid #a9cafa; border-radius: 50%; }}
    .governance {{ margin-top: 16px; display: flex; align-items: center; justify-content: space-between; gap: 24px; padding: 18px 24px; color: #123c73; border: 1px solid var(--blue); border-radius: 14px; background: #f8fbff; }}
    .governance strong {{ display: flex; align-items: center; gap: 12px; }}
    .governance span {{ color: var(--muted); font-size: .85rem; }}
    .section {{ padding: 78px 0; border-top: 1px solid var(--line); }}
    .section-head {{ display: grid; grid-template-columns: 1.35fr .8fr; gap: 48px; align-items: end; margin-bottom: 34px; }}
    h2 {{ margin: 0; font-size: clamp(2.5rem, 5vw, 4.5rem); line-height: 1; }}
    .section-head p {{ margin: 0; color: var(--muted); }}
    .orchestrator {{ position: relative; width: min(760px, 100%); margin: 0 auto 48px; padding: 26px 30px; text-align: center; border: 1.5px solid #9b83e7; border-radius: var(--radius); background: var(--violet-soft); box-shadow: 0 12px 32px rgba(93, 66, 176, .09); }}
    .orchestrator::after {{ content: ""; position: absolute; left: 50%; bottom: -49px; width: 1px; height: 48px; background: #9b83e7; }}
    .orchestrator .platform-name {{ color: var(--violet); margin-bottom: 8px; }}
    .orchestrator p:last-child {{ max-width: 610px; margin: 8px auto 0; color: var(--muted); }}
    .platforms {{ position: relative; display: grid; grid-template-columns: repeat(3, 1fr); gap: 28px; }}
    .platform {{ position: relative; min-height: 310px; padding: 30px; border: 1.5px solid; border-radius: var(--radius); background: #fff; }}
    .platform.core {{ border-color: #6ca8ef; }} .platform.engage {{ border-color: #67babb; }} .platform.analytics {{ border-color: #e4a766; }}
    .platform + .platform::before {{ content: "+"; position: absolute; left: -44px; top: 130px; width: 30px; height: 30px; display: grid; place-items: center; color: var(--blue); font-weight: 800; background: #fff; border: 1px solid #9fc2ed; border-radius: 50%; }}
    .platform-name {{ margin: 0 0 28px; color: var(--blue); font-size: 1.45rem; font-weight: 800; letter-spacing: -.03em; }}
    .platform-logo {{ display: flex; align-items: center; min-height: 64px; margin: 0 0 22px; }}
    .platform-logo img {{ display: block; max-width: 100%; object-fit: contain; }}
    .platform-logo .logo-box {{ width: 90px; height: 50px; }}
    .platform-logo .logo-salesforce {{ width: 190px; height: 72px; border-radius: 10px; }}
    .platform-logo .logo-databricks {{ width: 170px; height: auto; }}
    .platform.analytics .platform-name {{ color: #a35a08; }}
    .platform h3 {{ margin: 0 0 16px; font-size: 1.02rem; }}
    .platform ul {{ margin: 0; padding-left: 20px; color: var(--muted); }}
    .platform li + li {{ margin-top: 10px; }}
    .foundation {{ margin-top: 16px; padding: 18px 24px; display: flex; align-items: center; justify-content: space-between; gap: 20px; border: 1px solid #91b8ea; border-radius: 14px; background: var(--blue-soft); }}
    .foundation strong {{ display: flex; align-items: center; gap: 12px; }}
    .foundation span {{ color: var(--muted); font-size: .84rem; }}
    .paths {{ background: var(--canvas); }}
    .path-tabs {{ display: flex; gap: 8px; padding: 6px; width: fit-content; border: 1px solid var(--line); border-radius: 13px; background: #fff; }}
    .path-tabs button {{ padding: 10px 16px; color: var(--muted); border: 0; border-radius: 9px; background: transparent; cursor: pointer; }}
    .path-tabs button[aria-selected="true"] {{ color: #fff; background: var(--blue); }}
    .path-panel {{ display: none; margin-top: 22px; grid-template-columns: 1.05fr 1fr 1fr; border: 1px solid var(--line); border-radius: var(--radius); overflow: hidden; background: #fff; box-shadow: var(--shadow); }}
    .path-panel.active {{ display: grid; }}
    .path-panel > div {{ min-height: 230px; padding: 28px; border-right: 1px solid var(--line); }}
    .path-panel > div:last-child {{ border-right: 0; }}
    .path-panel h3 {{ margin: 0 0 12px; font-size: 1.3rem; }}
    .path-panel p {{ color: var(--muted); }}
    .path-panel .value {{ color: var(--blue); font-size: 1.15rem; font-weight: 760; }}
    .readiness {{ display: inline-flex; margin-top: 8px; padding: 5px 9px; color: #17683b; background: #e8f7ee; border-radius: 999px; font-size: .76rem; font-weight: 700; }}
    .readiness.future {{ color: #6846b6; background: var(--violet-soft); }}
    .proof-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 24px; }}
    .proof-card {{ overflow: hidden; border: 1px solid var(--line); border-radius: var(--radius); background: #fff; box-shadow: 0 12px 36px rgba(21, 53, 96, .07); }}
    .proof-image {{ position: relative; display: block; width: 100%; padding: 0; border: 0; background: #eef3f8; cursor: zoom-in; overflow: hidden; }}
    .proof-image img {{ display: block; width: 100%; aspect-ratio: 16/8.8; object-fit: cover; object-position: top; transition: transform .25s ease; }}
    .proof-image span {{ position: absolute; right: 14px; bottom: 14px; padding: 7px 10px; color: #fff; background: rgba(11,31,65,.86); border-radius: 8px; font-size: .75rem; }}
    .proof-image:hover img {{ transform: scale(1.015); }}
    .proof-copy {{ padding: 24px; }}
    .label {{ margin: 0 0 8px; color: var(--teal); font-size: .72rem; font-weight: 800; letter-spacing: .12em; text-transform: uppercase; }}
    .proof-copy h3 {{ margin: 0 0 8px; font-size: 1.2rem; }}
    .proof-copy > p:last-child {{ margin: 0; color: var(--muted); }}
    .decision {{ display: grid; grid-template-columns: 1.2fr .8fr; gap: 48px; }}
    .checklist {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 15px 28px; margin-top: 28px; }}
    .check {{ display: flex; align-items: flex-start; gap: 10px; color: #354b69; }}
    .check svg {{ flex: 0 0 auto; width: 20px; height: 20px; color: var(--blue); }}
    .result {{ padding: 30px; color: #fff; background: var(--ink); border-radius: var(--radius); }}
    .result h3 {{ margin: 0 0 12px; font: 600 2rem/1.05 ui-serif, Georgia, serif; }}
    .result p {{ color: #c7d4e6; }}
    .result strong {{ display: block; margin-top: 34px; color: #88b8ff; font-size: 1.1rem; }}
    footer {{ padding: 30px 0 46px; color: #667890; border-top: 1px solid var(--line); font-size: .78rem; }}
    footer .shell {{ display: flex; justify-content: space-between; gap: 24px; }}
    dialog {{ width: min(1500px, calc(100% - 32px)); max-height: calc(100vh - 32px); padding: 0; border: 0; border-radius: 18px; box-shadow: 0 28px 100px rgba(0,0,0,.35); }}
    dialog::backdrop {{ background: rgba(4,14,29,.76); }}
    .dialog-head {{ position: sticky; top: 0; z-index: 1; display: flex; justify-content: space-between; align-items: center; padding: 14px 18px; color: #fff; background: #0b1f41; }}
    .dialog-head button {{ width: 36px; height: 36px; color: #fff; border: 1px solid rgba(255,255,255,.3); border-radius: 50%; background: transparent; cursor: pointer; }}
    dialog img {{ display: block; width: 100%; height: auto; background: #fff; }}
    @media (max-width: 900px) {{
      .metrics {{ grid-template-columns: repeat(2, 1fr); }}
      .journey-grid {{ grid-template-columns: 1fr; }}
      .step {{ min-height: 0; display: grid; grid-template-columns: auto 1fr; gap: 0 18px; border-right: 0; border-bottom: 1px solid var(--line); }}
      .step:last-child {{ border-bottom: 0; }} .step::after {{ display: none; }} .step h3 {{ margin: 0 0 6px; }} .step p, .step h3 {{ grid-column: 2; }}
      .governance, .foundation {{ align-items: flex-start; flex-direction: column; }}
      .section-head, .decision {{ grid-template-columns: 1fr; }}
      .platforms {{ grid-template-columns: 1fr; }} .platform + .platform::before {{ display: none; }}
      .path-panel.active {{ grid-template-columns: 1fr; }} .path-panel > div {{ border-right: 0; border-bottom: 1px solid var(--line); }} .path-panel > div:last-child {{ border-bottom: 0; }}
    }}
    @media (max-width: 650px) {{
      .shell {{ width: min(100% - 24px, 1240px); }} .audience {{ display: none; }} .hero {{ padding-top: 48px; }}
      h1 {{ font-size: clamp(3rem, 16vw, 4.5rem); }} .metrics, .proof-grid, .checklist {{ grid-template-columns: 1fr; }}
      .metric {{ min-height: 0; }} .section {{ padding: 58px 0; }} .path-tabs {{ width: 100%; }} .path-tabs button {{ flex: 1; }}
      footer .shell {{ flex-direction: column; }}
    }}
    @media (prefers-reduced-motion: reduce) {{ html {{ scroll-behavior: auto; }} .proof-image img {{ transition: none; }} }}
    @media print {{
      .topbar, .proof-image span, .path-tabs, dialog {{ display: none; }}
      .hero, .section {{ padding: 30px 0; }} .path-panel {{ display: grid !important; break-inside: avoid; margin-bottom: 16px; }}
      .proof-card, .platform, .metric {{ break-inside: avoid; box-shadow: none; }}
    }}
  </style>
</head>
<body>
  <header class="topbar shell">
    <div class="brand"><img class="box-mark" data-brand-logo="box" src="{box_logo}" alt="Box"><span>Contract Lifecycle Management</span></div>
    <div class="audience">Executive marketecture · IT and business decision makers</div>
  </header>
  <main>
    <section class="hero shell">
      <h1>Governed contract operations, accelerated by AI.</h1>
      <p class="lead">Unify content, business context, and intelligence to move every contract from intake to insight—faster, with human accountability and complete governance.</p>
      <div class="metrics" aria-label="Illustrative business targets">
        <article class="metric"><span class="icon">{icon('target')}</span><strong>20–40%</strong><b>Faster cycle time</b><small>for standard agreements</small></article>
        <article class="metric"><span class="icon">{icon('understand')}</span><strong>20–30%</strong><b>Less legal touch time</b><small>for low and medium risk work</small></article>
        <article class="metric"><span class="icon">{icon('decide')}</span><strong>30–50%</strong><b>Fewer approval breaches</b><small>through visible routing and SLAs</small></article>
        <article class="metric"><span class="icon">{icon('shield')}</span><strong>95%+</strong><b>Metadata completeness</b><small>for governed executed agreements</small></article>
      </div>
      <p class="metric-note">Illustrative targets from the demo ROI model; validate with customer baselines before making commitments.</p>
    </section>

    <section class="journey shell" aria-labelledby="journey-title">
      <h2 id="journey-title" style="position:absolute;left:-9999px">Contract lifecycle journey</h2>
      <div class="journey-grid">
        <article class="step"><span class="step-icon">{icon('intake')}</span><span class="number">1. Intake</span><h3>Start with complete context</h3><p>Capture requests and documents through a consistent, policy-aware entry point.</p></article>
        <article class="step"><span class="step-icon">{icon('understand')}</span><span class="number">2. Understand</span><h3>Turn content into evidence</h3><p>Extract terms, compare standards, identify obligations, and surface exceptions.</p></article>
        <article class="step"><span class="step-icon">{icon('decide')}</span><span class="number">3. Decide</span><h3>Engage the right experts</h3><p>Route legal, privacy, finance, and security issues with cited source context.</p></article>
        <article class="step"><span class="step-icon">{icon('execute')}</span><span class="number">4. Execute</span><h3>Approve and sign securely</h3><p>Preserve decision rights, signature authority, versions, and the final package.</p></article>
        <article class="step"><span class="step-icon">{icon('learn')}</span><span class="number">5. Learn</span><h3>Manage what was promised</h3><p>Track renewals, obligations, performance, and portfolio risk over time.</p></article>
      </div>
      <div class="governance"><strong>{icon('shield')} Human governance at every step</strong><span>Policy controls · Role-based access · Audit trail · Retention and legal hold · Data residency</span></div>
    </section>

    <section class="section" id="architecture">
      <div class="shell">
        <div class="section-head"><h2>Purpose-built platform roles.</h2><p>AgentCore directs work across the governed content, business context, and analytics platforms required for the target operating model.</p></div>
        <article class="orchestrator"><p class="platform-name">AWS Bedrock AgentCore</p><h3>Cross-platform traffic director</h3><p>Supervises specialist agents, selects the right tools, maintains negotiation context, applies guardrails, and coordinates work across every system.</p></article>
        <div class="platforms">
          <article class="platform core"><div class="platform-logo"><img class="logo-box" data-brand-logo="box" src="{box_logo}" alt="Box"></div><h3>Governed content foundation</h3><ul><li>Single source of truth for contracts and related content</li><li>Security, classification, retention, legal hold, and audit</li><li>Apps, Forms, Automate, AI, Hubs, Doc Gen, Sign, and collaboration</li></ul></article>
          <article class="platform engage"><div class="platform-logo"><img class="logo-salesforce" data-brand-logo="salesforce" src="{salesforce_logo}" alt="Salesforce"></div><h3>Business context and engagement</h3><ul><li>Contract requests in the flow of work</li><li>Account, opportunity, quote, and approval context</li><li>Agents for routing, grounded insights, and next-best actions</li></ul></article>
          <article class="platform analytics"><div class="platform-logo"><img class="logo-databricks" data-brand-logo="databricks" src="{databricks_logo}" alt="Databricks"></div><h3>Intelligence and analytics foundation</h3><ul><li>Historical clause, outcome, spend, and revenue context</li><li>Governed enterprise data for specialist agents</li><li>Portfolio analytics, predictive insight, and performance measurement</li></ul></article>
        </div>
        <div class="foundation"><strong>{icon('shield')} Unified governance foundation</strong><span>Identity and access · Policy enforcement · Data protection · Monitoring and audit · Compliance and eDiscovery</span></div>
      </div>
    </section>

    <section class="section paths" id="adoption">
      <div class="shell">
        <div class="section-head"><h2>Phased delivery. One target architecture.</h2><p>Sequence delivery to prove value early without changing the destination: AgentCore directing Box, Salesforce Agentforce, and Databricks with human decision boundaries intact.</p></div>
        <div class="path-tabs" role="tablist" aria-label="Delivery phases">
          <button type="button" role="tab" aria-selected="true" aria-controls="path-one" id="tab-one">Establish the foundation</button>
          <button type="button" role="tab" aria-selected="false" aria-controls="path-two" id="tab-two">Scale intelligence</button>
        </div>
        <div class="path-panel active" id="path-one" role="tabpanel" aria-labelledby="tab-one">
          <div><h3>Governed operations foundation</h3><p>Begin with repeatable contract processes, governed content, business context, shared data, visible controls, and measurable baselines.</p><span class="readiness">Real Box and React surfaces demonstrated</span></div>
          <div><p class="label">What teams gain</p><p class="value">Governed intake, AI-assisted review, approval routing, clause publication, document generation, and execution controls.</p></div>
          <div><p class="label">Business fit</p><p>Fastest route to measurable cycle-time and consistency improvements while establishing the data and governance needed to scale.</p></div>
        </div>
        <div class="path-panel" id="path-two" role="tabpanel" aria-labelledby="tab-two">
          <div><h3>Supervisor-directed intelligence</h3><p>Activate AgentCore as the traffic director across Box, Salesforce Agentforce, and Databricks specialist capabilities.</p><span class="readiness future">Managed AgentCore and Databricks deployment planned</span></div>
          <div><p class="label">What teams gain</p><p class="value">Dynamic delegation, cross-system context, historical outcome analytics, deeper risk insight, and portfolio intelligence.</p></div>
          <div><p class="label">Business fit</p><p>Scale the target architecture across contract portfolios, business units, and decision patterns after the foundation proves control and value.</p></div>
        </div>
      </div>
    </section>

    <section class="section" id="proof">
      <div class="shell">
        <div class="section-head"><h2>Proof, not promises.</h2><p>These are real screens from the CLM demonstration. Open any image for the full experience; no documentation-site screenshots are used.</p></div>
        <div class="proof-grid">{proof_cards()}</div>
      </div>
    </section>

    <section class="section" id="decision">
      <div class="shell decision">
        <div><h2>What should an executive sponsor ask?</h2><div class="checklist">
          <span class="check">{icon('check')} Where do contracts stall today?</span>
          <span class="check">{icon('check')} Which systems hold content and deal context?</span>
          <span class="check">{icon('check')} Which decisions must remain human?</span>
          <span class="check">{icon('check')} Which clauses create the most escalation?</span>
          <span class="check">{icon('check')} What governance controls are non-negotiable?</span>
          <span class="check">{icon('check')} Which baseline metrics will prove value?</span>
          <span class="check">{icon('check')} Where can workflow deliver an early win?</span>
          <span class="check">{icon('check')} When does cross-platform scale justify expansion?</span>
        </div></div>
        <aside class="result"><span class="step-icon">{icon('target')}</span><h3>Lower risk. Faster deals. More value from every contract.</h3><p>Start with governed content and measurable workflow outcomes. Extend the platform only where additional intelligence creates a clear return.</p><strong>Govern first. Automate intelligently. Scale deliberately.</strong></aside>
      </div>
    </section>
  </main>
  <footer><div class="shell"><span>Acme CLM executive marketecture · self-contained offline artifact</span><span>Targets are illustrative and require customer validation. AI recommends; people approve.</span></div></footer>
  <dialog id="proof-dialog" aria-labelledby="dialog-title"><div class="dialog-head"><strong id="dialog-title">Demo experience</strong><button type="button" aria-label="Close">×</button></div><img alt=""></dialog>
  <script>
    const tabs = [...document.querySelectorAll('[role="tab"]')];
    tabs.forEach((tab) => tab.addEventListener('click', () => {{
      tabs.forEach((item) => item.setAttribute('aria-selected', String(item === tab)));
      document.querySelectorAll('[role="tabpanel"]').forEach((panel) => panel.classList.toggle('active', panel.id === tab.getAttribute('aria-controls')));
    }}));
    const proof = {str([{"title": item["title"], "src": data_uri(item["path"])} for item in PROOF])};
    const dialog = document.getElementById('proof-dialog');
    document.querySelectorAll('[data-proof]').forEach((button) => button.addEventListener('click', () => {{
      const item = proof[Number(button.dataset.proof)];
      dialog.querySelector('strong').textContent = item.title;
      dialog.querySelector('img').src = item.src;
      dialog.querySelector('img').alt = item.title + ' real demo screenshot';
      dialog.showModal();
    }}));
    dialog.querySelector('button').addEventListener('click', () => dialog.close());
    dialog.addEventListener('click', (event) => {{ if (event.target === dialog) dialog.close(); }});
  </script>
</body>
</html>'''
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(document, encoding="utf-8")
    return OUTPUT


if __name__ == "__main__":
    print(build())
