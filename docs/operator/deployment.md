# Deploying into a new environment

What binds this demo to one Salesforce org and one Box enterprise, where each value lives,
and what breaks when one is missing.

The code carries none of it. There is no org id, Box folder id or enterprise id in Apex or
metadata; the named credential is `https://api.box.com`, the Experience Cloud site is
identified by a URL path prefix rather than a host, and the storyboard says `<your-site>`.
Everything environment-bound arrives through **one custom setting**, `CLM_Box_Config__c`,
and the encrypted halves of two credentials.

## The one file to edit

[`config/deploy/environment.bcl`](../../config/deploy/environment.bcl) declares every
environment-specific setting: the field it lands in, the environment variable that carries
it, how to find its value, and what stops working without it. It is committed and holds
**placeholders only** — a live folder id in the working tree is what the secret scan
rejects, and it makes a repository readable by exactly one person.

```bash
cp config/deploy/environment.bcl config/deploy/environment.local.bcl
```

Replace each `<placeholder>` in the copy. `environment.local.bcl` is gitignored.

Check what is resolved before touching an org:

```bash
python3 scripts/clm_env.py --check
```

It prints each setting as `set` or `MISSING`, and for the missing ones, the sentence that
says what a presenter will see instead. Precedence is environment variable, then the local
BCL — so a one-off run can override the file without editing it.

## Applying it

```bash
clm-salesforce-project/scripts/configure-clm-box-settings.sh <org-alias>
```

The wrapper resolves values, substitutes them into a temporary copy of the Apex, and runs
that — no live identifier is ever written into the working tree. It is idempotent: reruns
update the same org-default row and report whether anything changed.

## What each setting costs when it is blank

The actions were built to refuse rather than guess, so a half-configured org does not
produce wrong answers. It produces refusals, on stage.

| Setting | Missing means |
|---|---|
| `Box_User_Id__c` *or* `Enterprise_Id__c` | The token endpoint answers `box_not_configured` (503) and the workspace shows no documents |
| `Allowed_Folder_Ids__c` | The endpoint will mint a token for **any** folder — the opposite of what the demo claims |
| `Contracts_Root_Folder_Id__c` | The portfolio risk search refuses: it cannot be bounded, and will not run unbounded |
| `Clause_Library_Hub_Id__c` | Clause-library questions have nothing governed to read against |
| `Counter_Position_Template_ID__c` | The counter-position memo cannot be generated |
| `Demo_Signer_Email__c` | The signature action answers "I need a signer before I can send this for signature" |

The last one is worth a sentence. Left blank in a **real** environment that refusal is
correct and should stay. It is only a demo that stalls on "who is signing?", which is why
the address is configuration rather than a default in source.

## What is deliberately not in the BCL

- **Box client id and secret** — the `CLM_Box` external credential, set by
  `configure-clm-box-credential.sh` (MT-038). Encrypted in the org; never in this
  repository and never through an assistant.
- **External Client App consumer key and secret** — Setup only (MT-032). Retrieving that
  metadata brings the secret back with it.
- **The site URL** — read from the org at run time.

## Order of operations

1. Install the Box for Salesforce managed package, and complete its **Box Sign setup**
   (MT-075) — that is what schedules the job that keeps signature statuses current.
2. `python3 scripts/demo_operator.py salesforce-deploy` for the data model, Apex and UI.
3. `configure-clm-box-credential.sh` (MT-038), then `configure-clm-box-settings.sh`.
4. `python3 scripts/clm_env.py --check` should report no missing settings.
5. Seed the demo records and files:
   `clm-salesforce-project/scripts/seed-clm-sample-data.sh` and
   `seed-clm-contract-files.sh`.
6. Work the remaining Required rows in the
   [manual-task register](manual-task-register.md).

## The honest cost

Thirty-four of the forty-eight rows in the manual-task register are Required, and they are
the real work: authorizing the Box app **in the same enterprise the package writes to**,
the External Client App, the Experience Cloud guest user, sharing sets, Lightning Out, and
Box Sign setup. This is a documented checklist someone works through, not a one-command
deploy, and most of the failures it prevents are the kind that surface as an opaque error
hours later.

## Demo data that is not seeded

`seed-clm-salesforce-sample-data.apex` creates the Northstar and Halcyon records the beats
need, including `CLM-2026-0017`, the approved contract the signature beat sends against.

The **Calder** records are not seeded — the repository carries no Calder sample documents,
only Northstar ones. A fresh environment therefore answers the portfolio risk beat with the
Northstar redline alone, where this environment returns two files on two different papers.
The beat still lands; it is one paper rather than two.
