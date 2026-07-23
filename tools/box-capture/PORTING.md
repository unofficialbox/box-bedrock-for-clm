# Porting box-capture to Go (box-dispatch)

Contract for reimplementing this directory inside `box-dispatch`. Written for someone who has never seen the Python.

## 1. What is actually being ported

**Not an API client.** Box Forms, Apps, and Automate have no supported authoring API. The private endpoints require the web application's session *and* its anti-forgery context; a direct same-origin request without that context returns `403`.

So the deliverable is a **code generator**. Go builds a single-line JavaScript executor; a human applies it in an already-authenticated Box tab. Go never authenticates, never holds a credential, and never calls Box.

Anything in a port that opens an HTTP connection to Box is out of scope and almost certainly wrong.

## 2. Two modes, and why the split matters

| Mode | Guarantee | Applies to |
|---|---|---|
| **Write executor** | Reconciles an exact-title *lab* object only | Empty draft, Manual Start graph, Form, App shell |
| **Read inspector** | Issues no operation at all; mutates nothing | Any unpublished workflow, including production-named ones |

The split is deliberate and must be preserved.

Writes are restricted to lab titles because the **GraphQL mutation shape for richer outcome types has never been observed.** Folder actions, agents, approval tasks, and HTTPS connector calls are authored through the editor UI, not through a captured mutation. Do not infer those shapes. If a port adds write support for them, it must be from a real captured `CreateItemV2`/`UpdateItemV2` request body, which does not exist yet.

Reads are unrestricted by title because reading is safe, and reading production workflows is the entire point of the capture capability.

## 3. Guards that must survive the port

Enforced **in the emitted JavaScript**, not only in Go, because the operator pastes the script and the Go process is long gone by then.

| Guard | Rule |
|---|---|
| Target | `location.hostname` must equal the configured host exactly |
| Hostname shape | Config host must match `[a-z0-9.-]+\.box\.com`; reject anything else before emitting |
| Surface | `location.pathname` must start with the expected surface prefix (`/automate`, etc.) |
| Exact title | Write mode: title must begin `CLM Surface API Lab - ` |
| Forbidden titles | Write mode: refuse the four production CLM workflow titles outright |
| Duplicate | More than one exact-title match aborts before writing |
| Status | Write mode requires an inactive target; read mode refuses anything ever published |
| Graph shape | Write mode refuses a target whose graph is richer than the mode supports |
| Acknowledgement | Refuse to emit unless the operator passes the exact acknowledgement string |

**Never emit** delete, publish, activate, share, run, or submit operations in any mode. The Python tests assert their absence by string search; the Go tests should too.

**Never read, return, log, or store** cookies, tokens, or anti-forgery values. Tests assert the emitted script contains no `cookie`, `authorization`, or `x-csrf-token`.

## 4. Emitted-script requirements

- **Single line.** The script is pasted into a console or applied by a controller; newlines break some paths. Python collapses it by stripping and joining. Preserve that, and keep the one-line property under test.
- **No `//` comments** — a line comment would swallow the rest of the single line. Use `/* */` only.
- **No JavaScript dialogs.** `alert`/`confirm`/`prompt` block the controller and require manual dismissal.
- **Assign a promise to a stable global** so the caller can await the result: `window.__clmPrivateAutomateInspectionPromise`.
- **Emit one structured console line** with a stable prefix (`CLM_AUTOMATE_PRIVATE_API_INSPECTION`) so a controller can locate the payload.

## 5. How the inspector reads a workflow

The only reliable read path found. Worth stating precisely because it is not obvious:

1. GraphQL request/response bodies are **not readable** from the browser controller — it blocks them as a credential-exfiltration guard.
2. The Automate editor stores the **server-provided workflow definition** in client application state once the page finishes loading. That is the definition *before* any local edit.
3. Walk the React fiber tree from `document.getElementById("app")`, following the `__reactContainer*` key, breadth-first over `child`/`sibling`, scanning `memoizedState` and `memoizedProps`.
4. A workflow graph is an object with all four of `outcomes`, `trigger`, `edges`, `configuration`. Several candidates appear; **choose the one with the most outcomes** — the others are empty stores or fresh templates.
5. Bound the walk (30k fibers, depth 4, 40 keys per object) or it will not terminate on a large page.

**There is no status enum in that state.** Derive status from `configuration.firstPublishedAt` / `lastPublishedAt` and report the derivation alongside the value. This was verified against the editor's own header badge.

A Go port emits the same traversal as JavaScript. The traversal cannot move to Go.

## 6. Config input

BCL is the only supported config format. `bcl.py` is a minimal reader of the same inventory `bcl.LoadBCL` parses.

**A Go port should delete `bcl.py` entirely and call `internal/bcl` directly.** One caveat, currently a real mismatch:

- `BCL_ARTIFACT_CONTRACT.md` §1 writes the inventory key unquoted: `locals { bcl = { ... } }`
- `parseBCLLocals` searches for the **quoted** `"bcl"` via `strings.Index(text, "\"bcl\"")`

This repository emits the **quoted** form to match the shipped parser. If box-dispatch changes the parser to accept the bare key, accept both — do not break the quoted form.

Also note §2 and §3 of that contract disagree about where identity fields live. `ExtractArtifactsFromBCL` reads `provider_object_id`, `artifact_name` and `enterprise_id` from **`config`**, and `FromDeployedArtifacts` writes them there. §2's resource-level listing is misleading; follow the code. This repository's artifacts follow the code.

## 7. Platform behaviour a port must not rediscover

Learned by live failure, not documented by Box:

- **An unresolved variable renders as the literal string `Variable unavailable`.** Not empty, not null. Any typed destination field receiving it will reject the request. Only bind values whose source field is mandatory.
- **Connector faults surface only as `errorCode: UNKNOWN_ERROR` with an empty payload.** The underlying `/app-api/graphql` call still returns HTTP 200, because the failure happens inside Box's server-side connector invocation. The external system's error text is never exposed.
- The fully resolved request body **is** recorded in the `CALL_CONNECTOR` run event. That is the only reliable place to diagnose a connector fault.
- **An HTTPS body is stored as an ordered `CONCAT` of operands**, not a template string. Operand types observed: `VALUE`, `VARIABLE`, `DYNAMIC_VARIABLE`, `GET_FILE_METADATA_FIELD`, `DATE_FORMAT`.
- **There is no `YYYY-MM-DD` date preset.** A date-only value is three `DATE_FORMAT` operands joined by literal hyphens. Component format is encoded as a `__YYYY__` style suffix on the token name.
- **Variable tokens are namespaced by trigger type.** A form trigger yields `static.trigger.form.<formFieldId>`; a metadata trigger yields `trigger.fileId` and `trigger.metadata.<field>`. Bindings are by **element ID, not label**, so rebuilding a Form silently breaks every binding.

## 8. Test parity

The 34 Python tests are the behavioural specification. A Go port should reproduce at least:

- every guard string appears in the emitted script
- no forbidden operation string appears in any mode
- no credential-bearing string appears in any mode
- the emitted script is exactly one line
- building without the exact acknowledgement raises and writes no file
- a spec with any consequential flag set to true is rejected
- a production title is rejected in write mode
- the read inspector contains no mutation call and no query call

## 9. Suggested Go shape

```
internal/boxcapture/
  capture.go     // shared guards, hostname validation, script collapsing
  automate.go    // write executor + read inspector
  forms.go
  apps.go
  script/        // JS templates as embedded assets, kept readable
```

Keep the JavaScript in separate embedded files rather than Go string literals. It is the part most likely to need iteration against a live Box surface, and it must stay reviewable.
