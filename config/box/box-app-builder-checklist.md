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
2. Open the published `Contract Lifecycle Management` app and select **Edit**.
3. Confirm `CLM-2026-Northstar` is the primary workspace.
4. Add or open the top section named `Portfolio & Actions`.
5. Add `Document Approval Status` as a donut chart from `clmDocument.approvalStatus`.
6. Add `Document Risk Profile` as a donut chart from `clmDocument.clauseRisk`.
7. Add `Documents by Type` as a bar chart from `clmDocument.documentType`.
8. Add `Contract Package Status` as a bar chart from `clmDocument.versionStatus`.
9. Drag and resize the four charts into two equal columns and two rows.
10. Add an `Approved Clause Hub` Shortcut to `https://kadams.ent.box.com/hubs/1312630996`.
11. Add a `Start a New Contract` Form block using `New Contract Request`; set presentation to **Open in New Tab**.
12. Drag and resize the two action blocks into the third two-column row.
13. Add or verify the card grid named `Northstar Deal Room`.
14. Add these cards:

| Card | Target |
|------|--------|
| Contract Workspace | Folder `399081692991` |
| Critical Legal Redline | File `2342633195167`; task `42899891150` |
| Commercial Mismatch | File `2342633259967`; task `42899881417` |
| Privacy and Security Review | File `2342633156726`; task `42899893550` |
| Security Exhibit | File `2342636075017` |
| Obligation Register | Folder `399081567921` |

15. Add or verify a section named `Intake and Actions`.
16. Add the published `New Contract Request` form.
17. Verify the Legal, Finance, and Privacy/security review cards open their task-bearing review documents.
18. Add a document table from `clmDocument`.
19. Filter the document table to `approvalStatus = Pending` and `clauseRisk` equal to `Critical` or `High`.
20. Add or verify the bottom section named `Executed Agreements and Renewals`.
21. Add an executed-agreement folder view for folder `399080706253`.
22. Add an obligation table from `clmObligation` filtered to `status = Open`.
23. Add or verify the `Clause Library` page.
24. Add the `Approved Standards` view, `Clause Source Files` folder, and `Standard vs Fallback` donut chart defined in the live spec.
25. Set the app description to `Operational CLM cockpit for governed intake, document risk, approvals, approved clauses, execution, and renewal readiness.`
26. Preview at desktop width and confirm the three two-column rows remain aligned.
27. Confirm the `Clause Library` tab opens and all three blocks resolve to live content.
28. Save only after presenter confirmation.

## Demo Validation

Before running the primary demo, confirm:

| Check | Expected Result |
|-------|-----------------|
| Dashboard opens | App loads without custom code |
| Portfolio & Actions | Shows approval, risk, document-type, and version-status breakdowns from six live documents |
| Action cards | Open the published intake Form and approved-clause Hub |
| Deal room cards | Open the live folders/files |
| Pending reviews | Shows three incomplete review tasks |
| Critical/high risk table | Shows MSA, DPA, SOW, and Order Form metadata |
| Obligations table | Shows renewal notice obligation |
| Clause Library | Tab opens; approved view, source folder, and standard/fallback chart resolve |
