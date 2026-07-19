#!/usr/bin/env python3
"""Build separate offline CLM galleries from real product screenshots."""

from __future__ import annotations

import base64
import html
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCREENSHOTS = ROOT / "output" / "screenshots"
OUTPUT = ROOT / "output" / "html"
BRAND_ASSETS = ROOT / "docs" / "design" / "brand-assets"

BOX_EXPERIENCES = [
    {
        "file": "box-app-dashboard-live.png",
        "eyebrow": "Box Apps",
        "title": "Contract Lifecycle Management dashboard",
        "description": "The published Box App cockpit with live approval, risk, document-type, and package-status charts, plus direct intake, approved-clause, and executed-agreement actions.",
    },
    {
        "file": "box-app-dashboard-actions-live.png",
        "eyebrow": "Box Apps actions",
        "title": "Intake, clauses, and deal room",
        "description": "The published dashboard action row keeps one governed intake Form alongside approved-clause and executed-agreement shortcuts, followed by live Northstar workspace and contract-document cards.",
    },
    {
        "file": "box-app-clause-library-live.png",
        "eyebrow": "Box Apps",
        "title": "Clause Library dashboard page",
        "description": "The published Box App page combines the Approved Standards view, governed source files, and a live Standard versus Approved Fallback portfolio chart.",
    },
    {
        "file": "box-app-approved-standards-view.png",
        "eyebrow": "Box Apps view",
        "title": "Approved clause standards",
        "description": "The live metadata-backed Box Apps view over individual Markdown clause files in the CLM clause library.",
    },
    {
        "file": "box-form-new-contract-request.png",
        "eyebrow": "Box Forms",
        "title": "New Contract Request",
        "description": "The published intake form used to capture requester, counterparty, commercial terms, target date, and the contract package.",
    },
    {
        "file": "box-hub-clause-library-live.png",
        "eyebrow": "Box Hubs",
        "title": "Acme Contract Clause Library",
        "description": "The published Hub combines the governed clause folder, current-standard status, intake/App/executed-agreement cards, and review-cadence guidance.",
    },
    {
        "file": "automate-intake-agents.png",
        "eyebrow": "Box Automate",
        "title": "Extract and agent enrichment",
        "description": "The real workflow builder shows deterministic Extract and Box Agent stages before the human decision point.",
    },
    {
        "file": "automate-approval-flow.png",
        "eyebrow": "Box Automate",
        "title": "Human validation gate",
        "description": "The workflow's approval task and approved/rejected branches, preserving human accountability before downstream actions.",
    },
    {
        "file": "automate-https-connector.png",
        "eyebrow": "Box Automate",
        "title": "HTTPS connector stage",
        "description": "The saved Salesforce standard REST external-ID PATCH request with the deployed My Domain, OAuth 2.0 credentials, and deterministic smoke contract identifier. Final OAuth smoke and workflow activation remain operator-gated.",
    },
    {
        "file": "box-docgen-templates.png",
        "eyebrow": "Box Doc Gen",
        "title": "CLM document templates",
        "description": "The signed-in Box Doc Gen catalog containing the approval memo, commercial order summary, and renewal notice templates.",
    },
]

REACT_EXPERIENCES = [
    {
        "file": "clm-react-workspace.png",
        "eyebrow": "React workspace",
        "title": "Northstar Health contract workspace",
        "description": "The running Multi-Framework React demo with live Box file identifiers, contract context, risk signals, and the Salesforce Agentforce copilot rail.",
    },
    {
        "file": "clm-react-redline-reviews.png",
        "eyebrow": "React redline reviews",
        "title": "Domain expert review queue",
        "description": "The running demo app groups cited differences into human-owned Commercial Legal, Finance, and Privacy reviews grounded in live Box task identifiers.",
    },
]

for experience in BOX_EXPERIENCES:
    experience["source"] = "box-automate-agentic-orchestration"

for experience in REACT_EXPERIENCES:
    experience["source"] = "cross-platform-agentic-orchestration"

SCENARIOS = [
    {
        "order": "02",
        "slug": "box-automate-agentic-orchestration",
        "title": "Box Automate Agentic Orchestration",
        "headline": "Agentic contract operations directed by Box Automate.",
        "description": "A workflow-directed orchestration of Apps, Forms, Automate, Extract, Box AI, Agentforce, human approvals, Hubs, Doc Gen, and execution controls.",
        "status": "Live Box surfaces. Automate is saved and inactive while its final OAuth smoke and activation remain gated.",
        "experiences": BOX_EXPERIENCES,
        "brands": ("box", "salesforce"),
    },
    {
        "order": "04",
        "slug": "cross-platform-agentic-orchestration",
        "title": "Cross-Platform Agentic Orchestration",
        "headline": "The complete multi-platform CLM operating model.",
        "description": "The governed Box journey plus the Salesforce Agentforce experience in the Multi-Framework React workspace. AgentCore, Strands, and Databricks are documented with a local trace until managed deployment is complete.",
        "status": "Real Box and React screens. No live AWS AgentCore or Databricks screenshots are claimed.",
        "experiences": REACT_EXPERIENCES + BOX_EXPERIENCES,
        "brands": ("box", "salesforce", "databricks"),
    },
]


def data_uri(path: Path) -> str:
    """Return an embedded image data URI for a screenshot path."""

    suffix = path.suffix.lower()
    mime = {
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
        ".svg": "image/svg+xml",
    }.get(suffix)
    if mime is None:
        raise ValueError(f"Unsupported embedded image: {path}")
    return f"data:{mime};base64,{base64.b64encode(path.read_bytes()).decode('ascii')}"


def brand_logos(names: tuple[str, ...]) -> str:
    """Render official embedded platform logos for the gallery scenario."""

    assets = {
        "box": ("box-logo-blue.svg", "Box"),
        "salesforce": ("salesforce-logo.jpeg", "Salesforce"),
        "databricks": ("databricks-primary-lockup-full-color.png", "Databricks"),
    }
    return "".join(
        f'<img class="brand-logo brand-logo-{name}" data-brand-logo="{name}" '
        f'src="{data_uri(BRAND_ASSETS / assets[name][0])}" alt="{assets[name][1]}">'
        for name in names
    )


def render_card(item: dict[str, str], index: int) -> str:
    """Render one gallery card and fail if its real screenshot is missing."""

    path = SCREENSHOTS / item["source"] / item["file"]
    if not path.exists():
        raise FileNotFoundError(path)
    return f"""
      <article class="experience" id="experience-{index}">
        <div class="copy">
          <p class="eyebrow">{html.escape(item['eyebrow'])}</p>
          <h2>{html.escape(item['title'])}</h2>
          <p>{html.escape(item['description'])}</p>
        </div>
        <figure>
          <img src="{data_uri(path)}" alt="{html.escape(item['title'])} real demo screenshot" loading="lazy">
          <figcaption>Captured from the real CLM demo experience in the signed-in Box tenant or the running React app.</figcaption>
        </figure>
      </article>"""


def build_scenario(scenario: dict[str, object]) -> Path:
    """Build one self-contained scenario gallery."""

    slug = str(scenario["slug"])
    experiences = scenario["experiences"]
    if not isinstance(experiences, list):
        raise TypeError("scenario experiences must be a list")
    cards = "\n".join(
        render_card(item, i + 1)
        for i, item in enumerate(experiences)
    )
    document = f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Acme CLM Visual Gallery · {html.escape(str(scenario['title']))}</title>
  <style>
    :root {{
      color-scheme: dark;
      --ink: #f6f7fb;
      --muted: #aab1c2;
      --line: rgba(255,255,255,.12);
      --panel: rgba(20,24,35,.82);
      --blue: #72a7ff;
      --mint: #7ce7c6;
      --radius: 24px;
    }}
    * {{ box-sizing: border-box; }}
    html {{ scroll-behavior: smooth; }}
    body {{
      margin: 0;
      color: var(--ink);
      background:
        radial-gradient(circle at 12% 0%, rgba(45,103,220,.28), transparent 34rem),
        radial-gradient(circle at 90% 20%, rgba(37,183,143,.17), transparent 28rem),
        #080b12;
      font: 16px/1.55 Inter, ui-sans-serif, -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
    }}
    header, main, footer {{ width: min(1440px, calc(100% - 40px)); margin-inline: auto; }}
    header {{ padding: 84px 0 56px; display: grid; grid-template-columns: 1.5fr 1fr; gap: 48px; align-items: end; }}
    .kicker, .eyebrow {{ color: var(--mint); font-size: .78rem; font-weight: 750; letter-spacing: .13em; text-transform: uppercase; }}
    h1 {{ margin: 10px 0 18px; max-width: 920px; font-size: clamp(2.8rem, 6vw, 6rem); line-height: .95; letter-spacing: -.055em; }}
    header p {{ margin: 0; color: var(--muted); font-size: 1.08rem; max-width: 700px; }}
    .brand-logos {{ display: flex; flex-wrap: wrap; align-items: center; gap: 18px; min-height: 54px; margin-bottom: 28px; }}
    .brand-logos img {{ display: block; width: auto; max-width: 150px; height: 42px; object-fit: contain; border: 0; border-radius: 0; background: transparent; }}
    .brand-logos .brand-logo-box {{ width: 76px; }}
    .brand-logos .brand-logo-salesforce {{ width: 128px; height: 46px; border-radius: 8px; }}
    .brand-logos .brand-logo-databricks {{ width: 144px; }}
    .status {{ border: 1px solid var(--line); border-radius: var(--radius); padding: 24px; background: var(--panel); backdrop-filter: blur(14px); }}
    .status strong {{ display: block; margin-bottom: 8px; font-size: 1.15rem; }}
    .status span {{ color: var(--muted); }}
    main {{ display: grid; gap: 30px; padding-bottom: 72px; }}
    .experience {{
      border: 1px solid var(--line);
      border-radius: var(--radius);
      overflow: hidden;
      background: linear-gradient(145deg, rgba(27,32,46,.94), rgba(12,15,23,.94));
      box-shadow: 0 26px 90px rgba(0,0,0,.28);
    }}
    .copy {{ display: grid; grid-template-columns: 180px minmax(250px, 1fr) minmax(280px, .9fr); gap: 28px; align-items: start; padding: 30px 34px; border-bottom: 1px solid var(--line); }}
    .copy p {{ margin: 0; color: var(--muted); }}
    .copy .eyebrow {{ color: var(--mint); }}
    h2 {{ margin: 0; font-size: clamp(1.35rem, 2.4vw, 2rem); line-height: 1.1; letter-spacing: -.025em; }}
    figure {{ margin: 0; padding: 18px; }}
    img {{ display: block; width: 100%; height: auto; border-radius: 14px; border: 1px solid rgba(255,255,255,.1); background: #fff; }}
    figcaption {{ padding: 13px 4px 0; color: #7f8799; font-size: .78rem; }}
    footer {{ padding: 0 0 64px; color: #7f8799; }}
    @media (max-width: 860px) {{
      header {{ grid-template-columns: 1fr; padding-top: 52px; }}
      header > * {{ min-width: 0; }}
      .copy {{ grid-template-columns: 1fr; gap: 12px; padding: 24px; }}
      .copy .eyebrow {{ margin-bottom: 2px; }}
    }}
    @media (prefers-reduced-motion: no-preference) {{
      .experience {{ animation: settle .55s ease both; animation-delay: calc(var(--i, 0) * 40ms); }}
      @keyframes settle {{ from {{ opacity: 0; transform: translateY(14px); }} to {{ opacity: 1; transform: none; }} }}
    }}
  </style>
</head>
<body>
  <header>
    <div>
      <div class="brand-logos" aria-label="Platforms in this scenario">{brand_logos(tuple(scenario['brands']))}</div>
      <p class="kicker">Acme Robotics · Visual Gallery · {html.escape(str(scenario['title']))}</p>
      <h1>{html.escape(str(scenario['headline']))}</h1>
      <p>{html.escape(str(scenario['description']))} Every product image below was captured from the real demo app or live Box tenant—not a documentation site.</p>
    </div>
    <aside class="status">
      <strong>Capture state · July 14, 2026</strong>
      <span>{html.escape(str(scenario['status']))}</span>
    </aside>
  </header>
  <main>
{cards}
  </main>
  <footer>Visual-only companion · Embedded real-demo screenshots · No external fonts, scripts, stylesheets, or image references</footer>
</body>
</html>
"""
    OUTPUT.mkdir(parents=True, exist_ok=True)
    output_path = OUTPUT / f"{scenario['order']}-{slug}-gallery.html"
    output_path.write_text(document, encoding="utf-8")
    return output_path


def build() -> None:
    """Build both scenario galleries."""

    for scenario in SCENARIOS:
        print(build_scenario(scenario))


if __name__ == "__main__":
    build()
