<!-- OPENSPEC:START -->
# OpenSpec Instructions

These instructions are for AI assistants working in this project.

Always open `@/openspec/AGENTS.md` when the request:
- Mentions planning or proposals (words like proposal, spec, change, plan)
- Introduces new capabilities, breaking changes, architecture shifts, or big performance/security work
- Sounds ambiguous and you need the authoritative spec before coding

Use `@/openspec/AGENTS.md` to learn:
- How to create and apply change proposals
- Spec format and conventions
- Project structure and guidelines

Keep this managed block so 'openspec update' can refresh the instructions.

<!-- OPENSPEC:END -->

## Testing

Use `uv venv` to create the virtual environment and run tests:

```bash
uv venv && source .venv/bin/activate
uv pip install -e ".[dev]"
pytest tests/
```

## Safety Rule: Stop Tracking an Already Tracked Item

When the user asks to stop tracking an item that is already tracked by Git, follow this exact procedure.

1. Create a local backup copy first (same directory with `.bak` suffix, or a timestamped copy).
2. Remove only from Git index with `git rm --cached <path>` (never remove the local file).
3. Ensure an ignore rule exists in `.gitignore` for that path/pattern.
4. Verify the file still exists on disk.
5. Verify Git reports it as ignored (`!!`) and no unintended deletion is pending.
6. Only then commit.

Hard constraints:
- Never use `git rm <path>` without `--cached` for this request type.
- Never overwrite the local file as part of this operation.
- If there is any ambiguity, ask before running destructive or lossy steps.
