# CLM Marketecture

This page routes use-case creators to the canonical messaging, visual sources, and generated collateral. Do not copy marketecture prose into additional Markdown files.

## Source material

- [Agent orchestration messaging](../design/agent-orchestration-messaging.md)
- [Marketecture visual concepts](../design/marketecture-concepts/README.md)
- [Approved brand assets](../design/brand-assets/README.md)
- [Architecture](architecture.md)
- [Control Matrix](control-matrix.md)
- [ROI Analysis](roi-analysis.md)

## Generated deliverables

| Deliverable | Exact generator |
|---|---|
| `output/html/05-executive-marketecture.html` | `scripts/build_executive_marketecture.py` |
| `output/html/06-agentcore-agent-experience-marketecture.html` | `scripts/build_agentcore_primary_marketecture.py` |
| `output/html/07-customer-solution-datasheet.html` | `scripts/build_customer_datasheet.py` |
| `output/html/08-contract-lifecycle-readiness-marketecture.html` | `scripts/build_contract_lifecycle_readiness_marketecture.py` |

Update the exact generator and its Markdown/configuration inputs before regenerating a deliverable. The outputs must remain self-contained, use approved logos, distinguish real screenshots from illustrative diagrams, and preserve the readiness language in `README.md`.
