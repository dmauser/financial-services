# Changelog

All notable changes to the **financial-services** GitHub Copilot CLI extension and plugin marketplace are documented here. Versioning follows [Semantic Versioning](https://semver.org/).

The version field in `package.json` is bumped exactly once per branch (single patch bump) by the repo's pre-commit hook (`scripts/version_bump.py`) and enforced on PRs by the `version-bump` GitHub Action — same policy as every other plugin in this repo.

## [Unreleased]

## [0.4.0] - Path B umbrella plugin

- **New umbrella plugin.** Adds a single Path B install that bundles every Claude for Financial Services specialist + skill + slash command + a markdown orchestrator. Source at `copilot-cli/plugins/financial-services/` is **generated** by `scripts/sync-copilot.py` from the canonical `plugins/` tree. Layout follows the standard Claude/Copilot plugin format (flat `agents/<slug>.md`, `skills/<name>/SKILL.md`, `commands/<name>.md`).
  - 11 agents (10 specialists + 1 orchestrator at `agents/financial-services.md`)
  - 66 unique skills (deduped across vertical + partner-built + specialist-bundled sources)
  - 39 slash commands (flat copies of the existing `copilot-cli/commands/{agents,skills}/` wrappers)
  - 12 MCP connector templates at `.mcp.json` (disabled by default)
  - The orchestrator's system prompt instructs the model to mirror the Path A `fs_capabilities` behavior: list specialists + slash commands when asked, route incoming requests to the right specialist for any other ask. Markdown only - the in-process `fs_*` tool registration still requires Path A.
- **New Copilot-dedicated marketplace** at `copilot-cli/.copilot-plugin/marketplace.json` registering only the umbrella plugin. **Kept entirely separate from the upstream-tracked root `.claude-plugin/marketplace.json`** so daily syncs from `anthropics/financial-services` never conflict on it. Install:
  ```text
  git clone https://github.com/dmauser/financial-services
  cd financial-services
  copilot plugin marketplace add ./copilot-cli
  copilot plugin install financial-services@financial-services-copilot
  ```
  (The marketplace name is `financial-services-copilot` and is registered separately from the upstream `claude-for-financial-services` marketplace - install both if you want both.)
- `scripts/sync-copilot.py` gains `sync_umbrella(dest=...)` and `sync_copilot_marketplace(dest_dir=...)` functions, both accepting an optional output path so `scripts/check.py` can regenerate into a temp dir and diff against the committed copies. Drift detection is now byte-for-byte enforced.
- `scripts/check.py` 4d.5 - new drift check for the umbrella tree and the Copilot marketplace JSON; verified it actually fails when the committed tree is hand-edited.

## [0.3.2] - Cleanup

- Remove `copilot-cli/.copilot-plugin/` (the speculative empty marketplace). Empirical testing confirmed Copilot CLI adopts Claude's plugin format verbatim and reads root `.claude-plugin/marketplace.json` directly. *(Subsequently restored in 0.4.0 with a different purpose - Copilot-dedicated marketplace registering only the umbrella plugin.)*

## [0.3.1] - Pre-existing on `main` (superseded)

- Earlier attempt at fixing the marketplace install via a generated root `.copilot-plugin/marketplace.json`. Replaced by the docs fix in 0.3.2 once empirical testing showed Copilot CLI uses `.claude-plugin/` instead.

## [0.3.0] - Real slash commands

- Register **41 slash commands** with the Copilot CLI host via the `@github/copilot-sdk/extension` `joinSession({ commands })` API:
  - **12 command-agents**: `/dcf`, `/lbo`, `/comps`, `/3-statement-model`, `/debug-model`, `/cim`, `/merger-model`, `/earnings`, `/initiate`, `/ic-memo`, `/financial-plan`, `/client-review`.
  - **27 command-skills**: `/buyer-list`, `/teaser`, `/one-pager`, `/process-letter`, `/deal-tracker`, `/morning-note`, `/sector`, `/screen`, `/catalysts`, `/thesis`, `/earnings-preview`, `/model-update`, `/dd-checklist`, `/dd-prep`, `/unit-economics`, `/returns`, `/source`, `/screen-deal`, `/portfolio`, `/value-creation`, `/ai-readiness`, `/tlh`, `/rebalance`, `/proposal`, `/client-report`, `/competitive-analysis`, `/ppt-template`.
  - **2 discovery commands**: `/fs-help` + `/finance-help` alias — render the `fs_capabilities` map.
- Slash commands are parsed from the canonical `commands/MAPPING.md`. Adding a row + `python scripts/sync-copilot.py` is the only step needed to surface a new slash command on the next extension load.
- Each handler reads the underlying `commands/agents/<name>/agent.md` or `commands/skills/<name>/SKILL.md` workflow markdown and forwards it (with the user's args appended as `User input: …`) into the session via `session.send()`. The agent then executes the workflow as a normal user turn.
- The 39 underlying `fs_cmd_*` / `fs_cmd_skill_*` MCP tools continue to work unchanged — slash-command registration is additive.
- Banner + presence note updated to advertise slash commands.

## [0.2.1] - Emoji + table capabilities output

- `fs_capabilities` now renders a finance-desk-style markdown table with emoji icons (📊 Earnings Review, 📒 GL Reconciliation, 🎯 Pitch Deck / M&A, 💰 Valuation Review, 🏦 Investment Banking, 💼 Private Equity, …) for both the 10 specialists and 9 verticals, plus a per-specialist / per-vertical skills detail section.

## [0.2.0] - Fix extension loading

- **BREAKING**: rewrote `extension.mjs` and `registry.mjs` to match the actual `@github/copilot-sdk/extension` contract (`joinSession({ tools, hooks })`). The previous `session.registerAgent`/`registerSkill`/`registerMcpServer` calls were not real SDK methods, which caused the extension to show as **failed** in `Manage Extensions`.
- Tools are now generated from the install tree at module load: every specialist agent, specialist skill, vertical skill, and slash-command agent/skill becomes a discovery tool the model can call (`fs_<slug>_role`, `fs_<slug>_skill_<name>`, `fs_<vertical>_skill_<name>`, `fs_cmd_<name>`, `fs_cmd_skill_<name>`).
- New ambient tools: `fs_capabilities` (full map), `fs_instructions` (compliance posture), `fs_mcp_status` (enabled connectors).
- Presence note injected via `onSessionStart` + `onUserPromptSubmitted` hooks so the agent learns the extension is available from turn 1.
- Added a thin root `package.json` so `npx -y github:dmauser/financial-services init` works (npm requires a root manifest before it will run any bin).

## [0.1.0] - Initial port

- Scaffold `copilot-cli/` subtree with `bin/cli.mjs` installer, `extension.mjs` + `registry.mjs` entrypoints.
- Mirror all 10 named agents under `extensions/financial-services/specialists/<slug>/`.
- Mirror all 9 verticals (7 first-party + LSEG + S&P partner-built) under `verticals/`.
- Ship `mcp/.mcp.json.template` with all 12 MCP connectors disabled by default.
- Split slash commands: high-value workflows become per-command agents; the rest become trigger-only skills.
- `instructions/AGENTS.md` carries the compliance posture (no autonomous decisioning, all output staged for human sign-off).
- Native `/plugin marketplace add dmauser/financial-services` install path via `.copilot-plugin/marketplace.json`.
- `npx -y github:dmauser/financial-services init` install path.
