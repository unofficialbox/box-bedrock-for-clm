# Inbound Email Intake Service

Captures a contract that arrives **by email** (the realistic first hop — a counterparty emails an internal rep an MSA or redline) onto the matching Salesforce Opportunity, and stages the attachment for Box.

## What it does

`EmailIntakeHandler` (Apex `Messaging.InboundEmailHandler`, in `clm-salesforce-project/force-app/main/default/classes/`):

1. Resolves the sender: `Contact.Email = fromAddress` → `Contact.Account`. Falls back to matching the sender's email domain against an `Account` website.
2. Picks the open Opportunity on that Account (the email subject may name a specific Opportunity to override the default).
3. Logs the email on the Opportunity's **activity timeline** — an `EmailMessage` where Enhanced Email is enabled, otherwise a `Task`.
4. Saves each attachment as a Salesforce **File** (`ContentVersion` + `ContentDocumentLink`) on the Opportunity.

It **never bounces** the sender (always returns success), and it **does not create `CLM_Contract__c`** — contract-record creation stays in the governed, human-gated Box intake path. This handler only captures the inbound content.

## Boundary

Content (the attachment) belongs in Box; Salesforce keeps the email **activity** plus a File reference. The authoritative `CLM_Contract__c` record is still created only by the Box metadata-trigger intake workflow after human review. No file bytes are written into the structured record.

## Per-org setup (Email Service)

The Apex deploys with the metadata; the inbound **address** and its **Run As** user are environment-specific and are configured in the org (not committed):

1. **Setup → Email Services → New Email Service.**
   - Apex class: `EmailIntakeHandler`
   - Accept Attachments: **All** (binary + text)
   - Active: checked
2. **New Email Address** under that service:
   - Run As: a licensed user with access to `Contact`/`Account`/`Opportunity` and create on `EmailMessage`/`Task`/`ContentVersion` (e.g. the CLM integration user with `CLM_Box_Automate_Integration`).
   - Active: checked. Optionally restrict **Accept Email From** to the counterparty domains.
3. Salesforce generates the inbound address (`<localpart>@<...>.apex.salesforce.com`). Route counterparty mail to it — forward a shared mailbox, or add it as a BCC/recipient on the counterparty thread.

Verify: send a test email (with a PDF) from a known counterparty Contact address; confirm the email appears on that Contact's Account Opportunity timeline and the PDF shows in the Opportunity's Files.

## Phase 2 — push the attachment into Box (not yet wired)

Getting the captured file into Box `01 - Intake` (where the `clmContract` metadata trigger fires) requires a Salesforce → Box callout:

- An **External Credential + Named Credential** for a Box custom app (OAuth 2.0). *These credentials must be created in Box and the org — they are not committed.*
- A `BoxFileUploader` Queueable that uploads the `ContentVersion` to the intake folder (folder id held in a `CLM_Integration_Setting__mdt` record, set per-org).
- The handler enqueues that job after capture (the hook is present but commented out in `EmailIntakeHandler`).

Until the Box credentials exist, the service delivers the Salesforce half: email + attachment captured on the Opportunity.
