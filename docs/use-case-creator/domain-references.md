# Legal and Commercial References

## Purpose

This document defines the demo-safe legal and commercial reference model for the CLM demo. It is not legal advice and should be treated as a synthetic demo playbook.

The life-sciences demo uses formal regulatory citations because regulatory traceability is the sales motion. The CLM demo should instead emphasize policy alignment, business risk, contract controls, and human legal review.

---

## Contract Package

| Document | Purpose | Demo Handling |
|----------|---------|---------------|
| MSA | Main legal terms | Clause risk analysis, redline summary, approval routing |
| DPA | Data processing and privacy obligations | Privacy/security review, obligation extraction |
| SOW | Services scope, milestones, deliverables | Delivery obligations and owner assignment |
| Order form | Commercial terms | Salesforce quote comparison, finance approval |
| Security exhibit | Security controls and audit commitments | Security approval and annual evidence tasks |
| Insurance certificate | Risk transfer evidence | Expiration tracking and renewal reminders |

---

## Clause Playbook Model

| Clause | Standard Position | Acceptable Fallback | Escalation Trigger |
|--------|-------------------|---------------------|--------------------|
| Liability cap | 12 months fees paid | 24 months fees for strategic deals | Unlimited cap or broad exclusions |
| Indemnity | Mutual third-party claims | Expanded IP indemnity with carveouts | One-way broad business-loss indemnity |
| Confidentiality | Mutual, 3-5 years | Perpetual for trade secrets | Publicity rights without approval |
| Data processing | Approved DPA | Customer DPA with privacy review | PHI without required safeguards |
| Payment terms | Net 30 / Net 45 | Net 60 with finance approval | Net 90 or unilateral setoff |
| Termination | Cause plus cure period | Limited convenience termination with fees | Convenience termination without fees |
| SLA credits | Capped credits | Higher credits with service owner approval | Refunds or uncapped service credits |
| Governing law | Approved jurisdictions | Negotiated with legal approval | Unapproved forum or venue |

---

## Policy Sources

| Source | Owner | Used By |
|--------|-------|---------|
| Contract playbook | Legal Operations | Agentforce clause comparison and Box AI Agent review |
| Approval matrix | Legal Operations + Finance | Approval Routing Agent |
| Privacy addendum template | Privacy | Clause Risk Agent |
| Security exhibit template | Security | Clause Risk Agent, Obligation Monitor |
| Revenue policy | Finance | Approval Routing Agent |
| Signature authority policy | Legal + Finance | Approval Routing Agent |
| Retention policy | Records Management | Box Governance configuration |

---

## Commercial Data Sources

| Source | Data | Demo Use |
|--------|------|----------|
| Salesforce Account | Counterparty, industry, region, account owner | Intake context and routing |
| Salesforce Opportunity | Stage, amount, close date, products | Commercial term comparison |
| Salesforce Quote | Price, discounts, term, billing | Order form validation |
| Databricks | Historical clause outcomes and cycle times | Risk benchmarks and negotiation recommendations |

---

## Demo-Safe Risk Categories

| Risk Level | Meaning | Example |
|------------|---------|---------|
| Low | Contract follows standard template and approval matrix | Standard MSA, Net 30, 12-month liability cap |
| Medium | Negotiated fallback within playbook | 24-month cap, Net 60, customer DPA accepted after review |
| High | Non-standard exception requiring senior approval | Unlimited liability, broad indemnity, PHI commitments |
| Critical | Blocks execution until resolved | Missing DPA for sensitive data, quote mismatch, no signature authority |

---

## Human-in-the-Loop Rules

| Decision | Human Owner |
|----------|-------------|
| Accept non-standard legal clause | Legal |
| Accept privacy/security commitments | Privacy + Security |
| Accept non-standard payment terms | Finance |
| Approve discount or commercial exception | Sales leadership / Finance |
| Sign agreement | Authorized signatory |
| Interpret ambiguous executed obligation | Legal / business owner |

---

## AI Output Rules

AI outputs in the CLM demo should follow these rules:

| Rule | Reason |
|------|--------|
| Cite source documents and clauses | Contract review must be traceable |
| Use approved playbook positions | Prevent invented legal policy |
| Separate facts from recommendations | Make human review easier |
| Mark uncertainty explicitly | Avoid false precision |
| Do not present legal advice as final | Preserve attorney and signatory accountability |
| Never modify source contracts silently | Preserve negotiation history |

---

## Retention and Audit Model

| Record | Retention Pattern |
|--------|-------------------|
| Draft contracts | Retain through negotiation and defined post-execution window |
| Executed agreements | Retain for contract term plus policy-defined period |
| Approval records | Retain with contract package |
| Signature envelope | Retain with executed agreement |
| Obligation register | Retain while obligation is active and through audit period |
| AI review output | Retain as supporting work product when used in approval decisions |

---

## Demo Caveat

This demo uses synthetic contracts and policy examples. Live customer deployments require review by the customer's legal, privacy, security, records-management, and compliance teams.
