# Changelog

All notable changes to the **financial-services** GitHub Copilot CLI extension and plugin marketplace are documented here. Versioning follows [Semantic Versioning](https://semver.org/).

The version field in `package.json` is bumped exactly once per branch (single patch bump) by the repo's pre-commit hook (`scripts/version_bump.py`) and enforced on PRs by the `version-bump` GitHub Action — same policy as every other plugin in this repo.

## [Unreleased]

## [0.1.0] - Initial port

- Scaffold `copilot-cli/` subtree with `bin/cli.mjs` installer, `extension.mjs` + `registry.mjs` entrypoints.
- Mirror all 10 named agents under `extensions/financial-services/specialists/<slug>/`.
- Mirror all 9 verticals (7 first-party + LSEG + S&P partner-built) under `verticals/`.
- Ship `mcp/.mcp.json.template` with all 12 MCP connectors disabled by default.
- Split slash commands: high-value workflows become per-command agents; the rest become trigger-only skills.
- `instructions/AGENTS.md` carries the compliance posture (no autonomous decisioning, all output staged for human sign-off).
- Native `/plugin marketplace add dmauser/financial-services` install path via `.copilot-plugin/marketplace.json`.
- `npx -y github:dmauser/financial-services init` install path.
