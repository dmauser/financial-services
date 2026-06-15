# Claude for Financial Services - GitHub Copilot CLI

This subdirectory packages the repo's agents, skills, and MCP connectors as a **GitHub Copilot CLI** extension and plugin marketplace. The content is the same as the [top-level Claude Cowork plugins](../README.md) and the [Managed Agent cookbooks](../managed-agent-cookbooks/) - one source, three delivery channels.

> [!IMPORTANT]
> Nothing here constitutes investment, legal, tax, or accounting advice. The agents draft analyst work product (models, memos, research notes, reconciliations) for review by a qualified professional. They do not make investment recommendations, execute transactions, post to ledgers, or approve onboarding. See [`instructions/AGENTS.md`](./instructions/AGENTS.md) for the full compliance posture.

## What you get

- **10 specialist agents** under [`extensions/financial-services/specialists/`](./extensions/financial-services/specialists) - one per workflow (pitch deck, GL recon, earnings, KYC, ...).
- **9 verticals** of skills + commands under [`verticals/`](./verticals) (financial-analysis, investment-banking, equity-research, private-equity, wealth-management, fund-admin, operations, lseg, spglobal).
- **39 slash commands** at [`commands/`](./commands) - 12 expressed as agents, 27 as trigger-only skills. See [`commands/MAPPING.md`](./commands/MAPPING.md).
- **12 MCP connectors** in [`mcp/.mcp.json.template`](./mcp/.mcp.json.template), all disabled by default; flip them on individually with the CLI.
- **Compliance + house-style instructions** under [`instructions/`](./instructions), loaded ambiently in every session.

See [`RECOMMENDATIONS.md`](./RECOMMENDATIONS.md) for day-in-the-life workflows showing how to combine them.

## Install

### Path A: `npx` installer (recommended for individuals)

```bash
# Install into ~/.copilot/extensions/financial-services/
npx -y github:dmauser/financial-services init

# Install into THIS repo only (./.copilot/extensions/financial-services/)
npx -y github:dmauser/financial-services init --project

# Show install location, version, and MCP enable state
npx financial-services status

# List all 12 MCP connectors and toggle individually
npx financial-services mcp list
npx financial-services mcp enable daloopa
npx financial-services mcp enable factset

# Uninstall (matches whichever scope you installed)
npx -y github:dmauser/financial-services uninstall            # user scope (~/.copilot)
npx -y github:dmauser/financial-services uninstall --project  # project scope (./.copilot)
```

After install, restart Copilot CLI (or run `/restart`) and confirm with `/env` that the extension, agents, skills, and any enabled MCP servers are loaded.

### Path B: native `/plugin` marketplace (for users who already manage Copilot CLI plugins)

> Copilot CLI reads `.claude-plugin/marketplace.json` at the repo root and registers the marketplace under that file's `name` field, which is **`claude-for-financial-services`** (inherited unchanged from upstream Anthropic — *not* `financial-services-copilot`). Install syntax is `<plugin-name>@<marketplace-name>`.

```text
copilot plugin marketplace add dmauser/financial-services
copilot plugin marketplace browse claude-for-financial-services
copilot plugin install financial-analysis@claude-for-financial-services
```

Or install individual plugins from the marketplace - e.g. just the equity-research vertical or just the pitch-agent specialist:

```text
copilot plugin install equity-research@claude-for-financial-services
copilot plugin install pitch-agent@claude-for-financial-services
```

Valid plugin names: `financial-analysis`, `investment-banking`, `equity-research`, `private-equity`, `wealth-management`, `fund-admin`, `operations`, `lseg`, `sp-global`, `pitch-agent`, `market-researcher`, `earnings-reviewer`, `meeting-prep-agent`, `model-builder`, `gl-reconciler`, `kyc-screener`, `valuation-reviewer`, `month-end-closer`, `statement-auditor`, `claude-for-msft-365-install`.

Uninstall a single plugin, or remove the marketplace altogether (which also removes anything installed from it):

```text
copilot plugin list                                              # see what's installed
copilot plugin uninstall financial-analysis@claude-for-financial-services
copilot plugin uninstall equity-research@claude-for-financial-services

copilot plugin marketplace list                                  # see registered marketplaces
copilot plugin marketplace remove claude-for-financial-services
```

The native marketplace manifest is the root [`/.claude-plugin/marketplace.json`](../.claude-plugin/marketplace.json) (inherited unchanged from upstream — Copilot CLI reads the exact same file Claude Code does, so there is **no Copilot-side patching of the upstream marketplace**).

### Path B umbrella - one plugin = everything

If you want a single Path B install that gives you all 10 specialists + every skill + every slash command + a markdown orchestrator that routes between them (functionally equivalent to Path A's runtime tools), the fork ships a Copilot-dedicated marketplace at [`copilot-cli/.copilot-plugin/marketplace.json`](./.copilot-plugin/marketplace.json) registering one plugin: `financial-services`. Source lives at [`copilot-cli/plugins/financial-services/`](./plugins/financial-services/) and is generated by `scripts/sync-copilot.py` from the canonical `plugins/` tree (drift-checked by `scripts/check.py`).

```text
# 1. Clone the repo (the marketplace lives in a non-default path so it has to be
#    added by file, not by '<owner>/<repo>' shorthand which only finds .claude-plugin/).
git clone https://github.com/dmauser/financial-services
cd financial-services

# 2. Register the dedicated Copilot marketplace.
copilot plugin marketplace add ./copilot-cli

# 3. Install the umbrella.
copilot plugin install financial-services@financial-services-copilot
```

The orchestrator agent (`agents/financial-services.md`) instructs the model to behave like Path A's `fs_capabilities` tool: when you ask "what can financial-services do?" it lists all specialists and slash commands; for any other request it identifies the right specialist or slash command and runs that workflow. **Markdown-only** - no JS extension code; for the in-process `fs_*` tool registration you still want Path A.

## MCP connectors

All 12 connectors ship **disabled** in `mcp/.mcp.json.template`. The first time you run any `mcp` subcommand, the CLI seeds an active `mcp/.mcp.json` from the template - that's the file you toggle.

| Connector | Provider | Notes |
|---|---|---|
| `daloopa` | [Daloopa](https://www.daloopa.com/) | Institutional research data |
| `morningstar` | [Morningstar](https://www.morningstar.com/) | Fund/security analytics |
| `sp-global` | [S&P Global / Kensho](https://www.spglobal.com/) | Capital IQ data |
| `factset` | [FactSet](https://www.factset.com/) | Terminal data |
| `moodys` | [Moody's](https://www.moodys.com/) | Credit/risk data |
| `mtnewswire` | [MT Newswires](https://www.mtnewswires.com/) | Financial news |
| `aiera` | [Aiera](https://www.aiera.com/) | Earnings calls + transcripts |
| `lseg` | [LSEG](https://www.lseg.com/) | Refinitiv/LSEG analytics |
| `pitchbook` | [PitchBook](https://pitchbook.com/) | Private markets data |
| `chronograph` | [Chronograph](https://www.chronograph.pe/) | PE portfolio monitoring |
| `egnyte` | [Egnyte](https://www.egnyte.com/) | Document store |
| `box` | [Box](https://www.box.com/) | Document store |

All require a provider subscription/API key. The CLI does not store credentials; supply them through the host's MCP credential mechanism (e.g. `/mcp` UI in Copilot CLI).

## Day-one quickstart

```bash
# 1. Install
npx -y github:dmauser/financial-services init

# 2. Enable the connectors you have
npx financial-services mcp enable daloopa
```

## License & attribution

This package is distributed under the [Apache License 2.0](./LICENSE).

It is a derivative work of [`anthropics/financial-services`](https://github.com/anthropics/financial-services), Copyright (c) Anthropic, PBC, also licensed under Apache-2.0. The agent prompts, skill markdown, slash commands, and MCP connector templates shipped under `extensions/`, `verticals/`, `commands/`, and `mcp/` are generated mirrors of the upstream sources; the modifications introduced by this fork wire that content into the GitHub Copilot CLI as an installable extension and plugin marketplace. See [`NOTICE`](./NOTICE) for the full attribution and [`CHANGELOG.md`](./CHANGELOG.md) for the list of changes.

Third-party skills retain their own license terms - see `verticals/spglobal/skills/*/LICENSE` and `verticals/financial-analysis/skills/skill-creator/LICENSE.txt`.

"Claude" and "Anthropic" are trademarks of Anthropic, PBC, used descriptively to identify the upstream work.
npx financial-services mcp enable aiera

# 3. Open Copilot CLI in any repo and confirm load
copilot
> /env
```

Then try:

```text
> Use the pitch-agent specialist to draft a pitch deck for Tesla
> Run /comps NVDA
> /earnings AAPL Q3 2026
```

See **[`RECOMMENDATIONS.md`](./RECOMMENDATIONS.md)** for full workflows.

## How content flows

This directory is **generated** from the canonical sources under `../plugins/`:

- Specialist system prompts mirror `../plugins/agent-plugins/<slug>/agents/<slug>.md`.
- Skills mirror `../plugins/vertical-plugins/<vertical>/skills/<name>/`.
- Commands wrappers under `commands/agents/` and `commands/skills/` are generated from `commands/MAPPING.md`.

**Edit the canonical sources** under `../plugins/`, then run:

```bash
python3 ../scripts/sync-copilot.py
```

`../scripts/check.py` fails the build if any file in `copilot-cli/` has drifted from its source - same drift policy as `agent-plugins/skills/` already has against `vertical-plugins/skills/`.

## Versioning

`package.json` follows semver. The repo's pre-commit hook (`../scripts/version_bump.py`) patch-bumps it once per branch, mirroring the policy for `.claude-plugin/plugin.json` files. The `version-bump` GitHub Action enforces it on PRs. See [`CHANGELOG.md`](./CHANGELOG.md).
