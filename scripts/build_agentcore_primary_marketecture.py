#!/usr/bin/env python3
"""Build the AgentCore-primary executive marketecture variation."""

from __future__ import annotations

import html
from pathlib import Path

from build_executive_marketecture import PROOF, data_uri, icon


ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "output" / "html" / "06-agentcore-agent-experience-marketecture.html"

AGENTS = (
    {
        "name": "Intake Agent",
        "role": "Capture and classify",
        "summary": "Builds the request brief, checks package completeness, and prepares the governed workspace.",
        "recommendation": "Request the updated cyber-insurance certificate before final legal review.",
        "tone": "violet",
    },
    {
        "name": "Clause Risk Agent",
        "role": "Compare and explain",
        "summary": "Compares redlines with approved standards and cites the exact source language behind each risk.",
        "recommendation": "Route the indemnity cap and data-security deviations to Commercial Legal and Privacy.",
        "tone": "blue",
    },
    {
        "name": "Approval Agent",
        "role": "Route and govern",
        "summary": "Identifies accountable reviewers, tracks decisions, and prevents action until required approvals exist.",
        "recommendation": "Legal is complete; Finance and Privacy approval remain required before execution.",
        "tone": "teal",
    },
    {
        "name": "Obligation Agent",
        "role": "Track and learn",
        "summary": "Turns signed commitments into owner-linked obligations, renewal events, and performance signals.",
        "recommendation": "Create three owner tasks and schedule the 90-day renewal-notice checkpoint.",
        "tone": "amber",
    },
)


def agent_buttons() -> str:
    return "\n".join(
        f'''<button class="agent-button {item['tone']} {'selected' if index == 0 else ''}" type="button" data-agent="{index}" aria-pressed="{'true' if index == 0 else 'false'}">
          <span class="agent-symbol">{index + 1:02d}</span><span><strong>{html.escape(item['name'])}</strong><small>{html.escape(item['role'])}</small></span>
        </button>'''
        for index, item in enumerate(AGENTS)
    )


def proof_cards() -> str:
    return "\n".join(
        f'''<article class="proof-card">
          <button class="proof-image" type="button" data-proof="{index}" aria-label="Open {html.escape(item['title'])} screenshot">
            <img src="{data_uri(item['path'])}" alt="{html.escape(item['title'])} real demo screenshot">
            <span>Open real demo screen</span>
          </button>
          <div><p>{html.escape(item['label'])}</p><h3>{html.escape(item['title'])}</h3><small>{html.escape(item['copy'])}</small></div>
        </article>'''
        for index, item in enumerate(PROOF)
    )


def build() -> Path:
    agent_json = str(
        [
            {
                "name": item["name"],
                "role": item["role"],
                "summary": item["summary"],
                "recommendation": item["recommendation"],
            }
            for item in AGENTS
        ]
    )
    proof_json = str(
        [{"title": item["title"], "src": data_uri(item["path"])} for item in PROOF]
    )
    document = f'''<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="description" content="Executive marketecture with AgentCore Agents as the primary contract experience.">
  <title>Acme CLM · AgentCore Agent Experience</title>
  <style>
    :root {{
      color-scheme: light;
      --ink: #0b1f41;
      --muted: #50627b;
      --line: #d6deea;
      --canvas: #f6f8fc;
      --violet: #6842d8;
      --violet-soft: #f1edff;
      --blue: #0061d5;
      --blue-soft: #eaf3ff;
      --teal: #087f8c;
      --teal-soft: #e7f8f7;
      --amber: #a95e00;
      --amber-soft: #fff4e5;
      --shadow: 0 20px 60px rgba(28, 48, 92, .1);
      --radius: 20px;
    }}
    * {{ box-sizing: border-box; }}
    html {{ scroll-behavior: smooth; }}
    body {{ margin: 0; color: var(--ink); background: #fff; font: 16px/1.5 -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; }}
    button {{ font: inherit; }}
    svg {{ width: 22px; height: 22px; fill: none; stroke: currentColor; stroke-width: 1.8; stroke-linecap: round; stroke-linejoin: round; }}
    .shell {{ width: min(1240px, calc(100% - 40px)); margin-inline: auto; }}
    header {{ min-height: 74px; display: flex; align-items: center; justify-content: space-between; gap: 24px; border-bottom: 1px solid var(--line); }}
    .brand {{ display: flex; align-items: center; gap: 18px; font-weight: 750; }}
    .brand-mark {{ color: var(--violet); font-size: 1.4rem; font-weight: 850; }}
    .brand span:last-child {{ padding-left: 18px; border-left: 1px solid var(--line); }}
    header small {{ color: var(--muted); }}
    .hero {{ padding: 74px 0 38px; }}
    h1, h2 {{ margin: 0; font-family: ui-serif, Georgia, Cambria, "Times New Roman", serif; font-weight: 620; letter-spacing: -.045em; }}
    h1 {{ max-width: 960px; font-size: clamp(3.5rem, 7vw, 6.6rem); line-height: .95; }}
    .lead {{ max-width: 790px; margin: 26px 0 0; color: var(--muted); font-size: clamp(1.1rem, 2vw, 1.38rem); }}
    .workbench {{ display: grid; grid-template-columns: 250px 1fr 270px; min-height: 590px; margin-top: 42px; overflow: hidden; border: 1px solid #c9d2e2; border-radius: var(--radius); background: #fff; box-shadow: var(--shadow); }}
    .workbench h3 {{ margin: 0; font-size: .78rem; letter-spacing: .1em; text-transform: uppercase; }}
    .agent-list {{ padding: 24px 16px; border-right: 1px solid var(--line); background: #fbfcfe; }}
    .agent-list h3 {{ padding: 0 8px 14px; color: var(--muted); }}
    .agent-button {{ width: 100%; display: flex; align-items: center; gap: 12px; padding: 15px 10px; text-align: left; color: var(--ink); border: 1px solid transparent; border-radius: 12px; background: transparent; cursor: pointer; }}
    .agent-button + .agent-button {{ margin-top: 6px; }}
    .agent-button:hover, .agent-button:focus-visible {{ background: #f2f5fa; outline: none; }}
    .agent-button.selected {{ border-color: #a994f0; background: var(--violet-soft); }}
    .agent-button strong, .agent-button small {{ display: block; }}
    .agent-button small {{ margin-top: 3px; color: var(--muted); font-size: .76rem; }}
    .agent-symbol {{ flex: 0 0 38px; height: 38px; display: grid; place-items: center; color: #fff; font-size: .72rem; font-weight: 800; border-radius: 10px; background: var(--violet); }}
    .agent-button.blue .agent-symbol {{ background: var(--blue); }} .agent-button.teal .agent-symbol {{ background: var(--teal); }} .agent-button.amber .agent-symbol {{ background: #d98200; }}
    .brief {{ padding: 24px; background: #fff; }}
    .brief-top {{ display: flex; justify-content: space-between; gap: 20px; align-items: start; }}
    .brief-top h3 {{ color: var(--violet); }}
    .brief-top strong {{ display: block; margin-top: 7px; font-size: 1.25rem; }}
    .brief-top span {{ color: var(--muted); font-size: .78rem; }}
    .brief-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 12px; margin: 22px 0; }}
    .field {{ padding: 12px; border: 1px solid var(--line); border-radius: 10px; }}
    .field small, .field strong {{ display: block; }} .field small {{ color: var(--muted); font-size: .7rem; }} .field strong {{ margin-top: 5px; font-size: .83rem; }}
    .panel {{ margin-top: 14px; padding: 18px; border: 1px solid var(--line); border-radius: 12px; }}
    .panel h3 {{ color: var(--muted); }}
    .source {{ display: grid; grid-template-columns: 110px 1fr auto; gap: 14px; align-items: center; padding: 10px 0; border-bottom: 1px solid #edf0f5; }}
    .source:last-child {{ border-bottom: 0; }}
    .source b {{ font-size: .78rem; }} .source span {{ color: var(--muted); font-size: .76rem; }} .source em {{ color: var(--violet); font-size: .7rem; font-style: normal; }}
    .recommendation {{ margin-top: 10px; color: #273e5f; }}
    .approval {{ margin-top: 14px; padding: 16px 18px; display: flex; justify-content: space-between; gap: 18px; align-items: center; border: 2px solid var(--violet); border-radius: 12px; background: #fcfbff; }}
    .approval strong, .approval small {{ display: block; }} .approval small {{ margin-top: 2px; color: var(--muted); }}
    .approval span {{ padding: 9px 13px; color: #fff; background: var(--violet); border-radius: 8px; font-size: .78rem; font-weight: 750; }}
    .conversation {{ padding: 24px 18px; border-left: 1px solid var(--line); background: #fbfcfe; }}
    .conversation h3 {{ color: var(--muted); }}
    .message {{ margin-top: 18px; padding: 14px; border: 1px solid var(--line); border-radius: 12px; background: #fff; }}
    .message.agent {{ border-color: #c9bdf5; background: var(--violet-soft); }}
    .message strong {{ display: block; font-size: .8rem; }} .message p {{ margin: 6px 0 0; color: var(--muted); font-size: .79rem; }}
    .truth {{ margin-top: 14px; padding: 13px 16px; color: #554178; background: var(--violet-soft); border-radius: 10px; font-size: .78rem; }}
    .section {{ padding: 78px 0; border-top: 1px solid var(--line); }}
    .section-head {{ display: grid; grid-template-columns: 1.2fr .8fr; gap: 48px; align-items: end; margin-bottom: 34px; }}
    h2 {{ font-size: clamp(2.6rem, 5.2vw, 4.7rem); line-height: 1; }}
    .section-head p {{ margin: 0; color: var(--muted); }}
    .architecture {{ display: grid; grid-template-columns: 190px 1fr; gap: 22px 30px; align-items: stretch; }}
    .layer-label {{ align-self: center; color: var(--muted); font-size: .73rem; font-weight: 800; letter-spacing: .11em; text-transform: uppercase; }}
    .primary-layer {{ padding: 28px 30px; display: grid; grid-template-columns: 1fr repeat(4, 100px); gap: 18px; align-items: center; color: #fff; border-radius: var(--radius); background: var(--violet); box-shadow: 0 16px 40px rgba(104,66,216,.22); }}
    .primary-layer h3 {{ margin: 0; font-size: 1.35rem; }} .primary-layer p {{ margin: 5px 0 0; color: #e5ddff; font-size: .84rem; }}
    .capability {{ padding-left: 18px; text-align: center; border-left: 1px solid rgba(255,255,255,.28); font-size: .8rem; }}
    .capability svg {{ display: block; margin: 0 auto 5px; }}
    .sources {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 18px; }}
    .source-card {{ min-height: 260px; padding: 24px; border: 1.5px solid; border-radius: var(--radius); background: #fff; }}
    .source-card.box {{ border-color: #6ca8ef; }} .source-card.salesforce {{ border-color: #67babb; }} .source-card.databricks {{ border-color: #e4a766; }}
    .source-card .system {{ margin: 0 0 20px; font-size: 1.35rem; font-weight: 850; }} .source-card.box .system {{ color: var(--blue); }} .source-card.salesforce .system {{ color: var(--teal); }} .source-card.databricks .system {{ color: var(--amber); }}
    .source-card h3 {{ margin: 0; font-size: 1rem; }} .source-card p {{ color: var(--muted); }} .source-card ul {{ margin: 16px 0 0; padding-left: 20px; color: var(--muted); font-size: .86rem; }} .source-card li + li {{ margin-top: 8px; }}
    .governance {{ padding: 20px 24px; display: grid; grid-template-columns: 180px repeat(6, 1fr); gap: 12px; align-items: center; color: #123b71; border: 1px solid #88b5eb; border-radius: 14px; background: var(--blue-soft); }}
    .governance strong {{ display: flex; align-items: center; gap: 10px; }} .governance span {{ text-align: center; font-size: .78rem; }}
    .work-flow {{ display: grid; grid-template-columns: repeat(7, 1fr); border: 1px solid var(--line); border-radius: var(--radius); overflow: hidden; }}
    .work-step {{ position: relative; min-height: 190px; padding: 22px 18px; text-align: center; border-right: 1px solid var(--line); background: linear-gradient(180deg,#fff,#f8faff); }}
    .work-step:last-child {{ border-right: 0; }} .work-step::after {{ content: "›"; position: absolute; right: -8px; top: 43px; z-index: 2; color: var(--violet); font-size: 1.7rem; background: #fff; }} .work-step:last-child::after {{ display: none; }}
    .work-step span {{ width: 44px; height: 44px; display: grid; place-items: center; margin: 0 auto 15px; color: var(--violet); border: 1px solid #bcaef0; border-radius: 50%; }} .work-step strong {{ display: block; }} .work-step p {{ margin: 8px 0 0; color: var(--muted); font-size: .77rem; }}
    .outcomes {{ background: var(--canvas); }}
    .outcome-grid {{ display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; }}
    .outcome {{ padding: 28px; border: 1px solid var(--line); border-radius: var(--radius); background: #fff; }} .outcome span {{ width: 46px; height: 46px; display: grid; place-items: center; color: var(--violet); border-radius: 50%; background: var(--violet-soft); }} .outcome h3 {{ margin: 22px 0 8px; }} .outcome p {{ margin: 0; color: var(--muted); }}
    .proof-grid {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 22px; }}
    .proof-card {{ overflow: hidden; border: 1px solid var(--line); border-radius: var(--radius); background: #fff; box-shadow: 0 12px 35px rgba(23,51,91,.07); }}
    .proof-image {{ position: relative; width: 100%; display: block; padding: 0; overflow: hidden; border: 0; background: #eef2f7; cursor: zoom-in; }}
    .proof-image img {{ display: block; width: 100%; aspect-ratio: 16/8.8; object-fit: cover; object-position: top; transition: transform .25s ease; }} .proof-image:hover img {{ transform: scale(1.015); }} .proof-image span {{ position: absolute; right: 13px; bottom: 13px; padding: 7px 10px; color: #fff; background: rgba(11,31,65,.88); border-radius: 8px; font-size: .74rem; }}
    .proof-card > div {{ padding: 22px; }} .proof-card p {{ margin: 0 0 7px; color: var(--teal); font-size: .7rem; font-weight: 800; letter-spacing: .12em; text-transform: uppercase; }} .proof-card h3 {{ margin: 0 0 7px; }} .proof-card small {{ color: var(--muted); }}
    .decision {{ display: grid; grid-template-columns: 1.1fr .9fr; gap: 42px; }}
    .checks {{ display: grid; grid-template-columns: repeat(2,1fr); gap: 14px 22px; margin-top: 26px; }} .check {{ display: flex; gap: 9px; color: #354b69; }} .check svg {{ flex: 0 0 auto; color: var(--violet); }}
    .result {{ padding: 30px; color: #fff; background: var(--ink); border-radius: var(--radius); }} .result h3 {{ margin: 0; font: 600 2rem/1.08 ui-serif,Georgia,serif; }} .result p {{ color: #c8d4e5; }} .result strong {{ display: block; margin-top: 28px; color: #c3b5ff; }}
    footer {{ padding: 30px 0 46px; color: #687a91; border-top: 1px solid var(--line); font-size: .78rem; }} footer .shell {{ display: flex; justify-content: space-between; gap: 24px; }}
    dialog {{ width: min(1500px, calc(100% - 32px)); max-height: calc(100vh - 32px); padding: 0; border: 0; border-radius: 18px; box-shadow: 0 28px 100px rgba(0,0,0,.35); }} dialog::backdrop {{ background: rgba(4,14,29,.76); }} .dialog-head {{ position: sticky; top: 0; z-index: 1; display: flex; justify-content: space-between; align-items: center; padding: 14px 18px; color: #fff; background: var(--ink); }} .dialog-head button {{ width: 36px; height: 36px; color: #fff; border: 1px solid rgba(255,255,255,.3); border-radius: 50%; background: transparent; cursor: pointer; }} dialog img {{ display: block; width: 100%; }}
    @media (max-width: 980px) {{
      .workbench {{ grid-template-columns: 220px 1fr; }} .conversation {{ grid-column: 1/-1; border-left: 0; border-top: 1px solid var(--line); }}
      .architecture {{ grid-template-columns: 1fr; }} .layer-label {{ margin-top: 12px; }} .primary-layer {{ grid-template-columns: 1fr repeat(2,100px); }} .sources {{ grid-template-columns: 1fr; }} .governance {{ grid-template-columns: repeat(3,1fr); }} .governance strong {{ grid-column: 1/-1; }}
      .work-flow {{ grid-template-columns: 1fr; }} .work-step {{ min-height: 0; display: grid; grid-template-columns: 60px 100px 1fr; align-items: center; text-align: left; border-right: 0; border-bottom: 1px solid var(--line); }} .work-step:last-child {{ border-bottom: 0; }} .work-step::after {{ display: none; }} .work-step span {{ margin: 0; }} .work-step p {{ margin: 0; }}
      .section-head, .decision {{ grid-template-columns: 1fr; }}
    }}
    @media (max-width: 680px) {{
      .shell {{ width: min(100% - 24px,1240px); }} header small {{ display: none; }} .hero {{ padding-top: 48px; }} h1 {{ font-size: clamp(3rem,16vw,4.7rem); }}
      .workbench {{ grid-template-columns: 1fr; }} .agent-list {{ border-right: 0; border-bottom: 1px solid var(--line); }} .brief-grid {{ grid-template-columns: repeat(2,1fr); }} .source {{ grid-template-columns: 88px 1fr; }} .source em {{ grid-column: 2; }} .approval {{ align-items: flex-start; flex-direction: column; }}
      .primary-layer {{ grid-template-columns: 1fr 1fr; }} .primary-layer > div:first-child {{ grid-column: 1/-1; }} .capability {{ border-left: 0; border-top: 1px solid rgba(255,255,255,.25); padding: 12px 0 0; }}
      .governance {{ grid-template-columns: repeat(2,1fr); }} .work-step {{ grid-template-columns: 52px 76px 1fr; padding: 18px 12px; }} .outcome-grid,.proof-grid,.checks {{ grid-template-columns: 1fr; }} footer .shell {{ flex-direction: column; }}
    }}
    @media (prefers-reduced-motion: reduce) {{ html {{ scroll-behavior: auto; }} .proof-image img {{ transition: none; }} }}
    @media print {{ header,.proof-image span,dialog {{ display:none; }} .section,.hero {{ padding:30px 0; }} .workbench,.source-card,.outcome,.proof-card {{ break-inside:avoid; box-shadow:none; }} }}
  </style>
</head>
<body>
  <header class="shell"><div class="brand"><span class="brand-mark">AgentCore</span><span>Contract Agent Experience</span></div><small>Executive marketecture · agents as the primary experience</small></header>
  <main>
    <section class="hero shell">
      <h1>One agent experience. Every contract system.</h1>
      <p class="lead">AgentCore agents plan, reason, and act across governed enterprise content, business context, and curated analytical intelligence—while people retain decision authority.</p>
      <div class="workbench" aria-label="Illustrative AgentCore contract workbench">
        <aside class="agent-list"><h3>Specialist agents</h3>{agent_buttons()}</aside>
        <section class="brief">
          <div class="brief-top"><div><h3>Contract brief</h3><strong>Northstar Health master services agreement</strong><span>Renewal · Medium risk · $2.1M value</span></div><span id="agent-role">Capture and classify</span></div>
          <div class="brief-grid"><div class="field"><small>Counterparty</small><strong>Northstar Health</strong></div><div class="field"><small>Contract type</small><strong>MSA</strong></div><div class="field"><small>Effective date</small><strong>May 1, 2026</strong></div><div class="field"><small>Renewal date</small><strong>April 30, 2027</strong></div></div>
          <div class="panel"><h3>Grounded sources</h3><div class="source"><b>Box</b><span>Contract, redline, and approved clause evidence</span><em>Unstructured content</em></div><div class="source"><b>Salesforce</b><span>Account, opportunity, quote, and approval state</span><em>Structured context</em></div><div class="source"><b>Databricks</b><span>Similar outcomes, portfolio trends, and risk patterns</span><em>Curated analytical intelligence</em></div></div>
          <div class="panel"><h3>Proposed next action</h3><p class="recommendation" id="agent-recommendation">{html.escape(AGENTS[0]['recommendation'])}</p></div>
          <div class="approval"><div><strong>Human approval required</strong><small>Review the recommendation before any external action.</small></div><span>Awaiting decision</span></div>
        </section>
        <aside class="conversation"><h3>Agent conversation</h3><div class="message"><strong>You</strong><p>Summarize the risk and recommend the next governed step.</p></div><div class="message agent"><strong id="agent-name">{html.escape(AGENTS[0]['name'])}</strong><p id="agent-summary">{html.escape(AGENTS[0]['summary'])}</p></div><div class="truth">Illustrative primary experience. Real Box and React evidence appears below; managed AgentCore and Databricks deployment remains a readiness gate.</div></aside>
      </div>
    </section>

    <section class="section" id="architecture"><div class="shell">
      <div class="section-head"><h2>Agents on top. Systems of record below. Humans govern across.</h2><p>The employee interacts with one agent experience. Box, Salesforce Agentforce, and Databricks operate headlessly behind AgentCore while remaining authoritative for their own data and controls.</p></div>
      <div class="architecture">
        <div class="layer-label">Primary experience</div><div class="primary-layer"><div><h3>AWS Bedrock AgentCore</h3><p>Primary employee experience and cross-platform orchestration layer</p></div><div class="capability">{icon('understand')}Plan</div><div class="capability">{icon('target')}Reason</div><div class="capability">{icon('execute')}Act</div><div class="capability">{icon('learn')}Monitor</div></div>
        <div class="layer-label">Governed systems of record</div><div class="sources">
          <article class="source-card box"><p class="system">box</p><h3>Unstructured content</h3><p>Contracts, redlines, clauses, evidence, signatures, and collaboration history.</p><ul><li>Versioned content</li><li>Metadata and classification</li><li>Retention, legal hold, and audit</li></ul></article>
          <article class="source-card salesforce"><p class="system">Salesforce Agentforce</p><h3>Structured business context</h3><p>Accounts, opportunities, quotes, commercial terms, approvals, and owners.</p><ul><li>Master business data</li><li>Workflow and approval state</li><li>Customer and deal context</li></ul></article>
          <article class="source-card databricks"><p class="system">Databricks</p><h3>Curated analytical intelligence</h3><p>Historical outcomes, portfolio trends, comparable positions, and predictive signals.</p><ul><li>Governed data products</li><li>Models and analytical insights</li><li>Performance measurement</li></ul></article>
        </div>
        <div class="layer-label">Governance across all layers</div><div class="governance"><strong>{icon('shield')} Govern every agent and action</strong><span>Identity</span><span>Policy</span><span>Audit</span><span>Retention</span><span>Data protection</span><span>Human approval</span></div>
      </div>
    </div></section>

    <section class="section" id="flow"><div class="shell">
      <div class="section-head"><h2>How work gets done.</h2><p>The experience hides system complexity without hiding evidence, decision rights, or accountability.</p></div>
      <div class="work-flow"><article class="work-step"><span>1</span><strong>Ask</strong><p>A person requests an outcome.</p></article><article class="work-step"><span>2</span><strong>Plan</strong><p>Agents decompose the work.</p></article><article class="work-step"><span>3</span><strong>Gather</strong><p>Systems return governed context.</p></article><article class="work-step"><span>4</span><strong>Recommend</strong><p>Agents synthesize cited evidence.</p></article><article class="work-step"><span>5</span><strong>Approve</strong><p>A person reviews the decision.</p></article><article class="work-step"><span>6</span><strong>Act</strong><p>Approved tools execute.</p></article><article class="work-step"><span>7</span><strong>Learn</strong><p>Outcomes improve future work.</p></article></div>
    </div></section>

    <section class="section outcomes" id="outcomes"><div class="shell">
      <div class="section-head"><h2>What changes for the enterprise.</h2><p>The agent layer becomes the consistent front door while existing platforms keep their governance, data ownership, and specialized capabilities.</p></div>
      <div class="outcome-grid"><article class="outcome"><span>{icon('understand')}</span><h3>One consistent experience</h3><p>Employees use a single, intuitive agent experience across contract systems and content.</p></article><article class="outcome"><span>{icon('execute')}</span><h3>Fewer handoffs</h3><p>Agents coordinate people and systems, reducing swivel-chair work and process latency.</p></article><article class="outcome"><span>{icon('shield')}</span><h3>Governed decisions at scale</h3><p>Policies, citations, approvals, and audit controls remain built into every action.</p></article></div>
    </div></section>

    <section class="section" id="proof"><div class="shell">
      <div class="section-head"><h2>Grounded in real demo experiences.</h2><p>These screens prove the content, workflow, engagement, and expert-review foundations that the AgentCore experience would orchestrate. No live AWS or Databricks console screenshot is claimed.</p></div><div class="proof-grid">{proof_cards()}</div>
    </div></section>

    <section class="section"><div class="shell decision"><div><h2>Executive design questions.</h2><div class="checks"><span class="check">{icon('check')} What should become the primary employee experience?</span><span class="check">{icon('check')} Which systems remain authoritative?</span><span class="check">{icon('check')} Which actions require human approval?</span><span class="check">{icon('check')} What evidence must accompany recommendations?</span><span class="check">{icon('check')} Which analytical data products guide decisions?</span><span class="check">{icon('check')} How will agent actions be monitored and audited?</span></div></div><aside class="result"><h3>Hide complexity, not control.</h3><p>AgentCore provides one experience across the enterprise. Box, Salesforce Agentforce, and Databricks remain governed, authoritative, and independently valuable.</p><strong>Agents coordinate. Systems inform. Humans decide.</strong></aside></div></section>
  </main>
  <footer><div class="shell"><span>Acme CLM · AgentCore-primary experience marketecture</span><span>Marketecture variation · managed deployment readiness remains explicit</span></div></footer>
  <dialog id="proof-dialog" aria-labelledby="dialog-title"><div class="dialog-head"><strong id="dialog-title">Demo experience</strong><button type="button" aria-label="Close">×</button></div><img alt=""></dialog>
  <script>
    const agents = {agent_json};
    document.querySelectorAll('[data-agent]').forEach((button) => button.addEventListener('click', () => {{
      const agent = agents[Number(button.dataset.agent)];
      document.querySelectorAll('[data-agent]').forEach((item) => {{ item.classList.toggle('selected', item === button); item.setAttribute('aria-pressed', String(item === button)); }});
      document.getElementById('agent-role').textContent = agent.role;
      document.getElementById('agent-name').textContent = agent.name;
      document.getElementById('agent-summary').textContent = agent.summary;
      document.getElementById('agent-recommendation').textContent = agent.recommendation;
    }}));
    const proof = {proof_json};
    const dialog = document.getElementById('proof-dialog');
    document.querySelectorAll('[data-proof]').forEach((button) => button.addEventListener('click', () => {{ const item = proof[Number(button.dataset.proof)]; dialog.querySelector('strong').textContent = item.title; dialog.querySelector('img').src = item.src; dialog.querySelector('img').alt = item.title + ' real demo screenshot'; dialog.showModal(); }}));
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
