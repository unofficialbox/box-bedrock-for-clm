# Executive Demo: Reading Customer Paper Against Governed Positions

## Demo card

| Item | Value |
|---|---:|
| Duration | 4-5 minutes |
| Audience | General counsel, CRO, CIO, legal and sales leadership |
| Scenario | Calder Financial Group sends **its own** MSA template; Acme must decide what to push back on |
| Internal surface | Claude Desktop over the Salesforce and Box MCP servers |
| External surface | Experience Cloud site, scoped to one counterparty |
| Core message | The exposure is not where a diff or a keyword search would look. Only reading the document against a governed clause library finds it. |

## The problem this opens on

Enterprise deals close on the customer's template, not yours. Every negotiated MSA comes back
with different payment terms, liability caps, renewal notice periods and termination rights.
That information drives revenue recognition, the renewal motion and risk exposure -- and it
exists only inside a document, sitting outside the systems and the permissions your agents
draw from.

## Why this scenario

Acme is on **customer paper**. There is no Acme template to diff against, the document has no
section called "Limitation of Liability", and a keyword search for that phrase returns nothing.
The uncapped exposure lives in two places that only mean something when read together --
Article 19.2 and a sub-clause buried in General Provisions at 22.4. That is the demo: a
CRM record and a full-text search cannot answer this, and a governed clause library can.

## Scope of this telling

Generation and signature are **not** in this script. Both are real Box capabilities and
neither is wired in this repository -- `VITE_BOX_DOCGEN_FOLDER_ID` and
`VITE_BOX_SIGNATURE_FOLDER_ID` are empty configuration, and no Apex writes back to the
contract record. Do not narrate them as live. The four beats below are all verified.

## Pre-demo state

| Check | How |
|---|---|
| Three Calder contracts exist: `CLM-SAMPLE-CAL-2022`, `-2024` (both Executed) and `-2026` (Legal Review) | Beat 4 needs the two executed ones |
| Calder contract has a Box folder with a **direct** collaboration for the configured Box user | `GET /2.0/folders/<id>/collaborations` -- inherited access does not downscope |
| `clmDocument` metadata applied to the Calder and Northstar documents | Otherwise beat 2's query returns nothing |
| `CLM_Box_Config__c.Clause_Library_Hub_Id__c` is populated and the Hub holds the `CLM-LIAB-*` clauses | Beat 3 depends on it entirely |
| Claude Desktop connected to the `CLMContractTools` MCP server, tools listed | `listContracts`, `getContractPackage`, `askContractDocument` |
| Counterparty user can sign in to the site | See **Known constraints** -- Login As is unavailable for this licence |

Open two windows before you start: Claude Desktop on the internal side, a private browser
window for the counterparty. Do not switch accounts on stage.

## Script

### Beat 1 — Their paper arrives (45 seconds)

**Say**

> Calder sent us their standard form. Their legal team does not accept supplier paper, so
> this is the document we are negotiating.

**Show**

- The contract's Box folder and `calder-msa-customer-paper-v2.pdf` in the workspace preview.
- Scroll the contents: Articles 1, 2, 3, 6, 11, 14, 19, 20, 22. **There is no Limitation of Liability section.**

**Land**

One folder per contract, provisioned and governed by Box. The commercial record lives in
Salesforce; the document never leaves Box.

### Beat 2 — The portfolio already knows what is risky (45 seconds)

**Say**

> Before anyone reads a page, the content itself has been classified.

**Show**

- One `search_files_metadata` query against the `clmDocument` template, `clauseRisk = Critical`.
- Two files come back, on **two different papers** -- the Northstar redline and the Calder draft.

**Land**

Box metadata is the retrieval index. This is one query, not a folder listing and nine reads.
`documentType` makes "find the insurance certificate" deterministic instead of a filename guess.

**Presenter honesty:** this tagging was applied by hand. A metadata cascade policy on the
contract folder is what makes it survive the next contract, and that is not built yet.

### Beat 3 — Read it against our approved positions (90 seconds)

This is the beat the demo exists for. Run it in Claude Desktop.

**Prompt**

> Where is Acme's liability exposure in the Calder agreement, and how does it compare to our
> approved position? Cite the clause library.

**Expected response**

- Exposure at **19.2** -- the indemnities are primary obligations, survive without limit of
  time, and are expressly *not* subject to any limitation elsewhere in the agreement.
- Exposure at **22.4** -- "Responsibility for Losses", which states no financial cap applies
  to the Supplier, and caps Calder's own liability at unpaid invoiced charges.
- Approved position **CLM-LIAB-001**: aggregate liability capped at 12 months' fees.
- Approved fallback **CLM-LIAB-002**: 24 months.
- Uncapped liability is **not an approved position**; deviation is owned by **Commercial Legal**.

**Land**

> A template diff cannot find this -- there is no Acme template to diff against. A keyword
> search for "limitation of liability" returns nothing, because the phrase does not appear.
> The document had to be read against a governed library of what we have already approved,
> and the answer came back with the clause ID and the owner attached.

**Then say what it costs.** A redline like this is what holds up signature and pushes a deal
out of the forecasted quarter. The point is not that the agent found it -- it is that legal
now has the approved fallback and the named owner in the same answer, which is what removes
a week of back-and-forth.

Verified live on 2026-09-01: the Hub returns exactly these positions with file-level citations.

### Beat 4 — What they agreed the last two times (45 seconds)

The clause library says the position is off-policy. This says something better.

**Prompt**

> Compare clause 22.4 and clause 19.2 across Calder's executed agreements and this draft.
> What did they actually agree before?

**Expected response**

- **2022** and **2024** both carry a negotiated 22.4: an aggregate cap at **24 months** of
  charges, with 19.2 making the indemnities subject to that cap except for IP infringement
  and data-breach claims, which stay uncapped.
- Both record the departure in a **Schedule 1** of agreed amendments to Calder's own
  standard form.
- The **2026** draft restores the unamended house text of both clauses.

**Land**

> Calder is not asking for something new. Their template regressed two positions their own
> legal team conceded, in writing, twice. That is not a policy argument any more -- it is a
> course-of-dealing argument, and it is the one that actually moves a negotiation.

Verified live on 2026-09-01 across all three documents, with per-file citations.

### Beat 5 — The same platform, scoped to the other side (60 seconds)

**Say**

> The counterparty gets a view of the same governed content, bounded to what is theirs.

**Show**

- The Experience Cloud site signed in as the Northstar contact.
- Their four Northstar contracts. No Calder, no Acme-internal record.

**Land**

> Same content, same page, a different person -- and a different result. Nobody configured a
> view for them. Record access is enforced by a Salesforce sharing set on
> `Counterparty_Account__c`, the query runs `with sharing`, and the Box token is downscoped
> to one folder. The analysis from beat 3 -- our positions, our fallbacks, our owner -- never
> crosses to this side.

**Do not extend this claim to the agent.** The workspace is scoped by the signed-in identity;
the Copilot is not, and cannot be on this surface. See **Known constraints**.

**Presenter warning:** do not invite the audience to prompt the Copilot here. See
**Known constraints**.

## Close

> Salesforce holds the commercial record. Box governs the content and the approved positions.
> The internal team works headlessly through MCP, the counterparty works through the portal,
> and the boundary between them is enforced by the platforms, not by the prompt.

## Pass criteria

1. The Calder document renders from live Box, and the audience sees no Limitation of Liability heading.
2. One metadata query returns critical documents across two contracts.
3. The clause-library answer names 19.2, 22.4, `CLM-LIAB-001`, `CLM-LIAB-002`, and Commercial Legal.
4. The precedent answer names the 24-month cap in both executed agreements and the reversion in the draft.
5. The counterparty view shows only that counterparty's contracts.
6. No generation and no signature is shown or claimed.

## Known constraints

Read these before presenting. Each is a real limitation, not a setup error.

- **The Contract Copilot is not identity-scoped.** It is a Service Agent
  (`ExternalCopilot` / `EinsteinServiceAgent`), which runs as its assigned agent user, and its
  contract argument is filled from the conversation -- so a counterparty can ask it about
  another company's contract by naming it. The scoping in beat 4 is the *workspace*, not the
  agent. Keep the Copilot out of the counterparty half of this demo.

  This is a property of the agent type, not of Agentforce. An **Employee Agent** inherits the
  permissions of the logged-in user and takes no agent user, which is the surface where
  "same agent, different access" would hold.
- **Login As is unavailable for the counterparty user.** The Customer Community licence does
  not offer it, and the org preference is already enabled. Set the user's password by reset
  and sign in to the site in a private window instead.
- **Contract folders need a direct Box collaboration.** A freshly provisioned folder inherits
  access, which is not enough to downscope a token; the workspace falls back to fixtures with
  an `invalid_resource` error that reads like a scope problem. `ClmBoxFolderService` grants it
  on provisioning -- verify it for any folder created another way.
- **The `clmContract` template is not applied to folders**, so contract-level facts are not
  searchable and beat 2 stays at document level.

## Where this story goes next

One build would add a beat:

| Build | Beat it unlocks |
|---|---|
| Wire Box Doc Gen and Box Sign | *Respond and execute.* On customer paper the honest generation is the counter-position drawn from the approved fallback -- `CLM-LIAB-002` is already that text -- not "generate the agreement". |

## References

- [Cross-platform agentic orchestration scenario](../README.md)
- [Salesforce record contract](../../../../use-case-creator/salesforce-record-contract.md)
- [Operator setup and activation](../../../start-here.md)
- [Supporting React scripts](README.md)
