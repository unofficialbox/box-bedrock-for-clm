# Presenting

Complete this after the smoke test and before rehearsal.

There is one presentation artifact: [DEMO-STORYBOARD.html](../DEMO-STORYBOARD.html) at the
repository root. It holds the preflight steps, the beats with every prompt, what to expect
from each, and the questions worth answering honestly. Nothing to build — open it.

This replaced a library of nine generated self-contained HTML pages: a setup guide, a
narrative guide, a visual gallery, two marketectures, a datasheet and an all-in-one edition
that embedded the rest. Together they were 21MB of derived bytes regenerated on every
validation run, and the Markdown under `docs/` was authoritative the whole time. The
storyboard is the one page a presenter actually reads from.

## Rehearsal package

1. Work the [Setup](SETUP.md) path, then [Documents Setup](DOCUMENTS-SETUP.md).
2. Run the [Smoke Test](SMOKE-TEST.md).
3. Read the [Scenario Guide](SCENARIO-GUIDE.md) for the narrative behind the beats.
4. Rehearse from [DEMO-STORYBOARD.html](../DEMO-STORYBOARD.html), start to finish, once.
5. Verify every claim against the current readiness state in [CONVENTIONS.md](CONVENTIONS.md).
6. Complete every relevant item in the [Manual-Task Register](MANUAL-TASKS.md).
7. Record reset ownership and the post-demo reconciliation path.

An assistant presenting alongside you follows
[skills/clm-contract-lifecycle/SKILL.md](../skills/clm-contract-lifecycle/SKILL.md), not
this page.

## Screenshot requirements

- Capture the real Box, Salesforce or React page viewport.
- Exclude browser tabs, address bars, desktop content, notifications and unrelated records.
- Use the target scenario directory under `output/screenshots/`.
- Update `config/demo/screenshot-manifest.json` with source, capture date, crop rule,
  scenario and readiness state.
