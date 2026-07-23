# box-capture

Guarded tooling for Box surfaces that have **no supported authoring API**: Forms, Apps, and Automate. It exists to capture and reconcile configuration that cannot be reached any other way.

This directory is carved out deliberately. It is the part of the CLM repository that is *not* scenario content — it is reusable Box platform capability, and it is intended to be ported to Go inside `box-dispatch`. See [PORTING.md](PORTING.md) for the contract a Go implementation must honour.

## What it does

Each module builds a **browser executor**: a single-line JavaScript snippet that an operator applies inside an already-authenticated Box web-app tab. The Python never authenticates, never holds a credential, and never talks to Box itself.

| Module | Surface | Capability |
|---|---|---|
| `forms.py` | Box Forms | Reconcile an exact-title lab Form |
| `apps.py` | Box Apps | Reconcile an exact-title lab App shell and page sections |
| `automate.py` | Box Automate | Reconcile an empty or Manual Start lab draft; **read** any unpublished workflow graph |

`bcl.py` is a minimal reader for the BCL artifact format. BCL is the only supported config format in this repository.

## Why a browser executor and not an API client

These surfaces have no public authoring API. The private endpoints require the web application's own session and anti-forgery context; a direct same-origin request without it returns `403`. The executor therefore runs *inside* the authenticated page and reuses the page's existing client.

The consequence for a Go port: **the Go side generates and hands over the script, it does not perform the calls.** Nothing here can be replaced by an HTTP client.

## Safety model

Every executor enforces, in the browser, before acting:

- **Target guard** — `location.hostname` must equal the configured host
- **Surface guard** — the page must be the expected Box surface
- **Exact-title guard** — writes only ever touch a title beginning `CLM Surface API Lab - `
- **Forbidden-title guard** — production workflow titles are refused outright
- **Duplicate guard** — more than one exact-title match aborts
- **Status guard** — writes require an inactive/unpublished target
- **Acknowledgement** — building any executor requires `--acknowledge 'I understand this uses an unsupported Box private API'`

Never emitted, in any mode: delete, publish, activate, share, run, or submit.

Credentials, cookies, and anti-forgery tokens are never read, returned, or stored. The generated scripts are asserted free of them by test.

## Usage

```bash
# inspect what would happen
python3 tools/box-capture/automate.py --dry-run

# build a write executor for a lab draft
python3 tools/box-capture/automate.py \
  --write-executor \
  --acknowledge 'I understand this uses an unsupported Box private API'

# build a read-only reader for an existing unpublished workflow
python3 tools/box-capture/automate.py \
  --write-inspector \
  --expect-title 'CLM - Contract Intake Enrichment' \
  --acknowledge 'I understand this uses an unsupported Box private API'
```

Apply the generated file inside the authenticated tab, in the page origin.

## The inspector is the important one

`--write-inspector` is the capture capability worth preserving. It reads a workflow's **server-provided definition** out of the editor's client application state after the page loads — the definition before any local edit.

It issues **no GraphQL operation at all**, mutates nothing, refuses any workflow that has ever been published, and redacts GUIDs, long numeric IDs, and email addresses before printing.

This exists because GraphQL request and response bodies are not readable from the controller, so reading loaded client state is the only practical way to capture an existing workflow.

## Tests

```bash
python3 -m unittest discover -s tools/box-capture/tests
```

34 tests. They assert the guards are present in emitted scripts and that no credential-bearing string ever appears. Treat them as the behavioural specification for a port.
