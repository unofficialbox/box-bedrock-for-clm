# AI-Assisted Operator Protocol

Use this protocol when an AI agent assists a human with setup. The machine-readable phase contract is `config/operator/operator-workflow.json`.

## Control loop

For each phase:

1. Read the phase, its owner, command, write boundary, completion condition, and confirmation gates.
2. Inspect the current local/runtime state before acting.
3. Run the documented dry run when one exists.
4. State the target Box enterprise, Salesforce org ID, affected resources, and rollback plan before external writes.
5. Execute only the current phase.
6. Verify the phase's completion condition from command output or visible UI state.
7. Record non-secret IDs/URLs only in the gitignored runtime files.
8. Stop at any confirmation gate or mismatch.

## Mandatory stops

Stop and ask the human when:

- Box requests sign-in or the enterprise/user differs from runtime configuration.
- Salesforce requests sign-in or the org ID differs from runtime configuration.
- A required product surface or permission is unavailable.
- A browser label or option differs enough that the documented binding is ambiguous.
- A command would overwrite an existing resource not recorded in bootstrap state.
- A secret would need to enter chat, source, screenshots, terminal history, or runtime JSON.
- The next action is Publish, Share, Activate, Generate, Send, deletion, collaborator removal, or permission expansion.
- A live response contradicts the completion condition.

## Allowed autonomous work

- Read repository files and runtime state.
- Run `doctor`, dry runs, generators, resolvers, unit tests, and read-only validation.
- Use `doctor --platform box` or `doctor --platform salesforce` when administrators have separate credentials.
- Create the explicitly scoped Box foundation after enterprise and parent-folder verification.
- Apply the deterministic metadata seed after the dry run.
- Deploy portable Salesforce metadata after exact org-ID verification.
- Assemble unpublished Box App/Hub/Automate drafts from resolved specifications.
- Test inactive workflows with labeled non-production data when credentials are already configured and the human authorized the test scope.

## Browser execution

Use `docs/operator/browser-configuration.md` and its canonical Form, App, Hub, workflow, agent, and connector specifications. Resolve IDs first:

```bash
python3 scripts/demo_operator.py resolve-config --allow-unresolved
```

Never copy an ID from screenshots, chat history, or another environment. Use only `config/runtime/bootstrap-state.json` and the generated specs.

Before a final publish or activation click, report:

```text
Action:
Surface/workflow:
Target Box enterprise:
Target folder or trigger:
External Salesforce org:
Expected side effect:
Rollback:
Confirmation required from:
```

## Handoff format

```text
Completed phase:
Verified evidence:
Runtime values recorded:
External resources created or reused:
Confirmation-gated actions not performed:
Current blocker:
Next phase:
```
