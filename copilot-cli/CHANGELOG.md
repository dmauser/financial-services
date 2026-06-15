# Changelog

All notable changes to the **financial-services** GitHub Copilot CLI extension and plugin marketplace are documented here. Versioning follows [Semantic Versioning](https://semver.org/).

The version field in `package.json` is bumped exactly once per branch (single patch bump) by the repo's pre-commit hook (`scripts/version_bump.py`) and enforced on PRs by the `version-bump` GitHub Action — same policy as every other plugin in this repo.

## [Unreleased]

- **Fix `/plugin install ...@financial-services-copilot` "Marketplace not found" error.** Copilot CLI's `/plugin marketplace add <owner>/<repo>` looks for `.copilot-plugin/marketplace.json` at the **repo root**, but the canonical file lives at `copilot-cli/.copilot-plugin/marketplace.json`. `scripts/sync-copilot.py` now generates `<repo-root>/.copilot-plugin/marketplace.json` from the canonical file, rebasing each plugin's `source` (`..` -> `copilot-cli`, `../verticals/...` -> `copilot-cli/verticals/...`) so the marketplace is discoverable from the repo root. `scripts/check.py` enforces no drift between the two.
- Add `LICENSE` and `NOTICE` files at the `copilot-cli/` package root so the npm-publishable sub-package carries the Apache-2.0 text and upstream attribution to `anthropics/financial-services` independently of the repo root. License section added to `README.md`. Root `NOTICE` file also added.

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
