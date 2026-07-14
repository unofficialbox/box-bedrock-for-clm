# Box App Builder Checklist: CLM Dashboard

Use this checklist in the Box web UI to assemble the CLM dashboard used by the primary demo.

## Source Workspace

| Item | Value |
|------|-------|
| App name | Contract Lifecycle Management |
| Source folder | CLM-2026-Northstar |
| Source folder ID | 399081692991 |
| Shared link | https://kadams.ent.box.com/folder/399081692991 |

## Build Steps

1. Open Box Apps.
2. Create a new app named `Contract Lifecycle Management`.
3. Add `CLM-2026-Northstar` as the primary workspace.
4. Add a top section named `Contract Overview`.
5. Add a contract pipeline table from `clmContract`.
6. Add charts for `riskLevel` and `status`.
7. Add a card grid named `Northstar Deal Room`.
8. Add these cards:

| Card | Target |
|------|--------|
| Contract Workspace | Folder `399081692991` |
| Critical Legal Redline | File `2342633195167`; task `42899891150` |
| Commercial Mismatch | File `2342633259967`; task `42899881417` |
| Privacy and Security Review | File `2342633156726`; task `42899893550` |
| Security Exhibit | File `2342636075017` |
| Obligation Register | Folder `399081567921` |

9. Add a section named `Intake and Actions`.
10. Add a form block placeholder named `New Contract Request`.
11. Add a pending-review task list with:

| Review | Task ID |
|--------|---------|
| Legal review | `42899891150` |
| Finance review | `42899881417` |
| Privacy/security review | `42899893550` |

12. Add a document table from `clmDocument`.
13. Filter the document table to `approvalStatus = Pending`.
14. Add a second filter for `clauseRisk = Critical` or `clauseRisk = High`.
15. Add a bottom section named `Executed Agreements and Renewals`.
16. Add an executed-agreement folder view for folder `399080706253`.
17. Add an obligation table from `clmObligation`.
18. Filter obligations to `status = Open`.
19. Publish the Box App.
20. Paste the published app URL into `config/box/live-box-surface.json` under `boxAppUrl`.

## Demo Validation

Before running the primary demo, confirm:

| Check | Expected Result |
|-------|-----------------|
| Dashboard opens | App loads without custom code |
| Contract overview | Shows Northstar contract metadata |
| Deal room cards | Open the live folders/files |
| Pending reviews | Shows three incomplete review tasks |
| Critical/high risk table | Shows MSA, DPA, SOW, and Order Form metadata |
| Obligations table | Shows renewal notice obligation |
