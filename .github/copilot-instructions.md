# Copilot Instructions — Claude for Financial Services

Reference Cowork plugins, Claude Managed Agent (CMA) templates, and a GitHub Copilot CLI port for FSI workflows. Everything is **markdown + JSON/YAML — no build step** (the only JS is the thin Copilot installer at `copilot-cli/bin/cli.mjs`). See [`README.md`](../README.md) and [`CLAUDE.md`](../CLAUDE.md) for full context.

## The "one source, three wrappers" model

Each named agent ships through **three** delivery channels, all sharing one canonical system prompt and one set of skills:

1. **Claude Cowork plugin** — `plugins/agent-plugins/<slug>/`
2. **Claude Managed Agent cookbook** — `managed-agent-cookbooks/<slug>/agent.yaml`
3. **GitHub Copilot CLI extension/plugin** — `copilot-cli/extensions/financial-services/specialists/<slug>/`

Canonical sources:

- System prompt: `plugins/agent-plugins/<slug>/agents/<slug>.md`
- Skill sources: `plugins/vertical-plugins/<vertical>/skills/<skill-name>/SKILL.md`

Mirrored copies (must stay byte-for-byte identical to source — drift is a check.py failure):

- `plugins/agent-plugins/<slug>/skills/` ← from `plugins/vertical-plugins/<vertical>/skills/`
- `copilot-cli/extensions/financial-services/specialists/<slug>/agents/<slug>.md` ← from `plugins/agent-plugins/<slug>/agents/`
- `copilot-cli/extensions/financial-services/specialists/<slug>/skills/` ← from `plugins/agent-plugins/<slug>/skills/`
- `copilot-cli/verticals/<vertical>/skills/` and `commands/` ← from `plugins/vertical-plugins/<vertical>/`

**Editing rule:** edit a skill in `plugins/vertical-plugins/<vertical>/skills/<name>/`, then run **both** sync scripts:

```bash
python3 scripts/sync-agent-skills.py     # propagates into plugins/agent-plugins/<slug>/skills/
python3 scripts/sync-copilot.py          # propagates into copilot-cli/
```

Never hand-edit anything under `copilot-cli/extensions/`, `copilot-cli/verticals/`, or `copilot-cli/commands/agents/` and `commands/skills/` — those are generated. The slash-command wrappers under `copilot-cli/commands/` are generated from `copilot-cli/commands/MAPPING.md`; edit that file to reclassify a command, then re-run `sync-copilot.py`.

## Validation / lint / "tests"

There is no test suite. The single command that gates everything:

```bash
python3 scripts/check.py     # requires pyyaml
```

It validates: YAML/JSON parses, `agents/*.md` frontmatter has `name` + `description`, every `system.file` / `skills.path` / `skills.from_plugin` / `callable_agents.manifest` resolves, marketplace `source` paths resolve, every `agent.md`'s prose-referenced ``` `skill-slug` ``` is bundled, every `managed-agent-cookbooks/<slug>/` has the required files, **no bundled skill has drifted from its vertical source**, and **no file under `copilot-cli/` has drifted from its `plugins/` source**.

`check.py` also self-installs `.githooks/pre-commit` via `git config core.hooksPath .githooks` on first run.

CI runs three workflows on every PR:

- `plugin-validate.yml` — `claude plugin validate` over every plugin (pinned `CLAUDE_VERSION: 2.1.143`).
- `version-bump.yml` — enforces the per-branch version bump policy.
- `copilot-validate.yml` — runs `check.py` plus a `node copilot-cli/bin/cli.mjs help` smoke + project-local install dry-run.

To validate a single plugin locally the way CI does (requires the Claude Code CLI):

```bash
claude plugin validate plugins/agent-plugins/gl-reconciler
```

To smoke the Copilot CLI installer end-to-end:

```bash
node copilot-cli/bin/cli.mjs init --project
node copilot-cli/bin/cli.mjs status --project
node copilot-cli/bin/cli.mjs uninstall --project
```

## Versioning — every plugin/extension change must bump `version`

A plugin's `.claude-plugin/plugin.json` `version` (and `copilot-cli/package.json` `version`) gates update delivery to already-installed users. The pre-commit hook (`scripts/version_bump.py`) **patch-bumps any modified plugin's `version` exactly once per branch** so the branch ends up one patch ahead of `main` (not one bump per commit). The `version-bump` GitHub Action enforces the same rule on PRs as a backstop. Bypass for a single commit with `git commit --no-verify`. `version_bump.py` treats `copilot-cli/package.json` identically to a `plugin.json`.

## Adding content

- **New skill** → add under `plugins/vertical-plugins/<vertical>/skills/<name>/SKILL.md`, then run **both** sync scripts.
- **New agent** → create both `plugins/agent-plugins/<slug>/` (with `.claude-plugin/plugin.json`, `agents/<slug>.md`, and bundled `skills/`) **and** `managed-agent-cookbooks/<slug>/` (with `agent.yaml`, `subagents/*.yaml`, `README.md`, `steering-examples.json`). Register it in `.claude-plugin/marketplace.json` **and** in `copilot-cli/.copilot-plugin/marketplace.json`. Run `sync-copilot.py`. Mirror the structure of an existing pair like `gl-reconciler`.
- **New slash command** → add the canonical command file under `plugins/vertical-plugins/<vertical>/commands/<name>.md`, then add a row to `copilot-cli/commands/MAPPING.md` choosing `agent` or `skill`, then run `sync-copilot.py`.
- `agents/<slug>.md` must start with `---` YAML frontmatter containing `name` + `description`.
- Inside `agent.md` prose, refer to a skill as ``` `skill-slug` ``` (backticked, kebab-case) — `check.py` enforces that any such reference is actually bundled in that agent's `skills/`.

## Conventions worth knowing

- **CMA subagents are depth-1 leaf workers only** — orchestrators dispatch to them; they don't recurse. See `managed-agent-cookbooks/<slug>/subagents/*.yaml`.
- Orchestrator `agent.yaml` typically restricts the orchestrator to read-only tools (read/grep/glob + read-only MCP servers); writes/bash live in subagents. See `managed-agent-cookbooks/gl-reconciler/agent.yaml` for the canonical pattern.
- All MCP connectors are centralized in `plugins/vertical-plugins/financial-analysis/.mcp.json` and shared across other verticals — don't duplicate them per-vertical. The Copilot CLI port mirrors them in `copilot-cli/mcp/.mcp.json.template`, all `disabled: true` by default.
- `mcp-categories.json` defines canonical MCP category labels shared across plugins.
- `*.local.md` files are gitignored — user-specific, never commit.
- `.copilot/` (project-local Copilot CLI install dir, created by `npx financial-services init --project`) is gitignored.
- `claude-for-msft-365-install/` is **separate** admin tooling for the Microsoft 365 add-in; it is not an FSI plugin and isn't part of the agent/vertical structure.
- Slash commands (`commands/*.md`) are invoked as `/<plugin-name>:<command-name>` in Claude. In Copilot CLI they're surfaced as either dedicated agents or skills with explicit triggers per `copilot-cli/commands/MAPPING.md`.
- **No emoji or non-ASCII glyphs in CLI output** — the Copilot installer and any agent CLI output runs on Windows hosts where the default cp1252 console raises `UnicodeEncodeError` on Unicode glyphs.

## Compliance posture

These agents draft analyst work product for human sign-off — they do **not** make investment recommendations, execute transactions, post to ledgers, or approve onboarding. Don't add language or tool wiring that implies autonomous decisioning; every output is staged for review. The Copilot port enforces this via `copilot-cli/instructions/AGENTS.md` and `copilot-cli/instructions/instructions/compliance.instructions.md`.

## Deploying a CMA cookbook

```bash
export ANTHROPIC_API_KEY=sk-ant-...
scripts/deploy-managed-agent.sh <slug>     # e.g. gl-reconciler
```

The script resolves `{file:}` / `{path:}` / `{manifest:}` references, uploads skills, creates leaf-worker subagents, and POSTs the orchestrator to `/v1/agents`. `scripts/orchestrate.py` is a reference event loop for routing `handoff_request` events.

## Installing the Copilot CLI port

```bash
# One machine, all repos:
npx -y github:dmauser/financial-services init

# This repo only:
npx -y github:dmauser/financial-services init --project

# Or via Copilot CLI's native marketplace:
# /plugin marketplace add dmauser/financial-services
# /plugin install pitch-agent@financial-services-copilot
```

See [`copilot-cli/RECOMMENDATIONS.md`](../copilot-cli/RECOMMENDATIONS.md) for day-in-the-life workflows.
