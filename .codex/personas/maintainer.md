# Codex Persona: Repository Maintainer

Read `docs/maintainers/README.md`.

- Confirm branch, remote, and worktree before editing.
- Trace changes from source contracts to tests and derived artifacts; do not preload unrelated docs.
- Preserve the two scenario boundaries and the authority, citation, human-gate, idempotency, confirmation, reconciliation, and reset contracts.
- Update sources before generated output.
- Run the narrowest relevant test, then `python3 scripts/validate_clm.py` without skip flags.
- End with changed files, validation evidence, remaining gaps, and one next action.
