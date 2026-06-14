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
```

After install, restart Copilot CLI (or run `/restart`) and confirm with `/env` that the extension, agents, skills, and any enabled MCP servers are loaded.

### Path B: native `/plugin` marketplace (for users who already manage Copilot CLI plugins)

```text
/plugin marketplace add dmauser/financial-services
/plugin install financial-services@financial-services-copilot
```

Or install individual plugins from the marketplace - e.g. just the equity-research vertical or just the pitch-agent specialist:

```text
/plugin install equity-research@financial-services-copilot
/plugin install pitch-agent@financial-services-copilot
```

The native marketplace manifest lives at [`.copilot-plugin/marketplace.json`](./.copilot-plugin/marketplace.json) and points at the same files the `npx` installer copies.

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
