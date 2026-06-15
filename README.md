# Claude for Financial Services — GitHub Copilot CLI port

> [!NOTE]
> **This fork (`dmauser/financial-services`) publishes only the GitHub Copilot CLI port** under [`copilot-cli/`](./copilot-cli). For the upstream **Claude Cowork / Claude Code / Managed Agents** distribution, install from [`anthropics/financial-services`](https://github.com/anthropics/financial-services) — that's the canonical home for the Claude side.
>
> The `plugins/` and `managed-agent-cookbooks/` trees in this fork exist as the **single source of truth** that the Copilot CLI mirror is generated from. Don't install Claude plugins from this fork — go upstream.

## Quick install (Copilot CLI)

### Prerequisites

- **GitHub Copilot CLI** installed and signed in — `gh extension install github/gh-copilot` and `gh auth login`, or follow [the Copilot CLI install docs](https://docs.github.com/en/copilot/github-copilot-in-the-cli). Verify with `copilot --version`.
- **Node.js ≥ 18** on PATH — required by both install paths. Verify with `node --version`.
- **Git** — needed by `npx` to clone the repo install.
- *(Optional)* **Python ≥ 3.10** — only needed if you intend to run `scripts/check.py` / `scripts/sync-copilot.py` locally to contribute changes.
- *(Optional)* **API keys** for any data connectors you plan to enable (FactSet, Daloopa, LSEG, S&P Global, Moody's, Pitchbook, etc.). The 12 MCP connectors ship **disabled by default** — enable individually after install.

### Path A — Extension (npx installer)

```bash
# Install into ~/.copilot/extensions/financial-services/ (one machine, all repos)
npx -y github:dmauser/financial-services init

# Or install into ./.copilot/extensions/financial-services/ (this repo only)
npx -y github:dmauser/financial-services init --project

# Enable the data connectors you have credentials for (all start disabled)
npx financial-services mcp enable factset
npx financial-services mcp enable daloopa

# Confirm install location, version, and MCP state
npx financial-services status

# Remove later
npx -y github:dmauser/financial-services uninstall
```

Restart Copilot CLI after `init`. The extension surfaces as `financial-services` in `Manage Extensions` and registers ~169 discovery tools (`fs_capabilities`, `fs_<slug>_role`, `fs_<slug>_skill_<name>`, `fs_<vertical>_skill_<name>`, …). Try `> what can financial-services do?` — it'll call `fs_capabilities` and list every specialist and skill.

> If `npx` errors with `ENOENT … package.json` after a prior install, clear the npx cache once: `Remove-Item -Recurse -Force "$env:LOCALAPPDATA\npm-cache\_npx"` (Windows) / `rm -rf ~/.npm/_npx` (Unix), then re-run `npx -y github:dmauser/financial-services init`.

### Path B — Plugin marketplace

> Copilot CLI's `copilot plugin marketplace add <owner>/<repo>` reads `.claude-plugin/marketplace.json` at the repo root and registers the marketplace under that file's `name` field, which is **`claude-for-financial-services`** (inherited unchanged from upstream — *not* `financial-services-copilot`). The plugin install syntax is `<plugin-name>@<marketplace-name>`.

```text
# 1. Register the marketplace (one-time)
copilot plugin marketplace add dmauser/financial-services

# 2. Discover what's available
copilot plugin marketplace list
copilot plugin marketplace browse claude-for-financial-services

# 3. Install one or more plugins
copilot plugin install financial-analysis@claude-for-financial-services
copilot plugin install pitch-agent@claude-for-financial-services
copilot plugin install equity-research@claude-for-financial-services

# 4. Verify
copilot plugin list

# Uninstall a single plugin
copilot plugin uninstall financial-analysis@claude-for-financial-services

# Remove the marketplace altogether (also removes any plugins installed from it)
copilot plugin marketplace remove claude-for-financial-services
```

Valid plugin names: `financial-analysis`, `investment-banking`, `equity-research`, `private-equity`, `wealth-management`, `fund-admin`, `operations`, `lseg`, `sp-global`, `pitch-agent`, `market-researcher`, `earnings-reviewer`, `meeting-prep-agent`, `model-builder`, `gl-reconciler`, `kyc-screener`, `valuation-reviewer`, `month-end-closer`, `statement-auditor`, `claude-for-msft-365-install`.

If you previously installed and see `Marketplace "<name>" not found`, the registered name doesn't match what you typed after `@`. Run `copilot plugin marketplace list` to see the actual registered name and use that exact string.

#### Path B umbrella — one plugin = everything

If you want a single Path B install that gives you all 10 specialists + every skill + every slash command + a markdown orchestrator that routes between them, the fork ships a **Copilot-dedicated marketplace** under `copilot-cli/.copilot-plugin/` (kept separate from the upstream `.claude-plugin/marketplace.json` so daily upstream syncs never touch it):

```text
git clone https://github.com/dmauser/financial-services
cd financial-services
copilot plugin marketplace add ./copilot-cli
copilot plugin install financial-services@financial-services-copilot
```

The umbrella plugin source is generated at [`copilot-cli/plugins/financial-services/`](./copilot-cli/plugins/financial-services/) by `scripts/sync-copilot.py` from the canonical `plugins/` tree, and drift-checked by `scripts/check.py`. **Markdown only** — no JS runtime tools; for in-process `fs_capabilities`, prefer Path A.

> [!IMPORTANT]
> **Path A vs Path B parity.** Path A (npx extension) runs `extension.mjs` + `registry.mjs` and exposes runtime tools — `fs_capabilities` (emoji table of all specialists + verticals), `fs_instructions`, `fs_mcp_status`, plus per-agent and per-skill loaders. Path B (marketplace install) delivers the same agent and skill **markdown content**; runtime JS tools are not loaded by the plugin host. The Path B umbrella above gets you the equivalent agent + skill + slash-command coverage with a markdown orchestrator that mimics the Path A routing behavior. **For full runtime tool registration, prefer Path A.**

See [`copilot-cli/RECOMMENDATIONS.md`](./copilot-cli/RECOMMENDATIONS.md) for day-in-the-life workflows once you're installed.

### Slash commands

Once the extension is loaded (Path A), the following slash commands are registered with Copilot CLI's slash-command picker. Type `/` and start typing to autocomplete; everything after the command name is forwarded as user input (ticker, target, file path, scope, …) and the corresponding workflow markdown is executed as a new turn.

| Command | Domain | Example |
|---|---|---|
| `/dcf` | Financial analysis | `/dcf NVDA` |
| `/lbo` | Financial analysis | `/lbo "Acme Industrials"` |
| `/comps` | Financial analysis | `/comps MSFT GOOGL META` |
| `/3-statement-model` | Financial analysis | `/3-statement-model AMZN` |
| `/debug-model` | Financial analysis | `/debug-model models/q3-forecast.xlsx` |
| `/cim` | Investment banking | `/cim "Project Helios"` |
| `/merger-model` | Investment banking | `/merger-model "MSFT acquires AVGO"` |
| `/earnings` | Equity research | `/earnings AAPL` |
| `/initiate` | Equity research | `/initiate ASML` |
| `/ic-memo` | Private equity | `/ic-memo "Series B Acme"` |
| `/financial-plan` | Wealth management | `/financial-plan "Smith family, retire 2032"` |
| `/client-review` | Wealth management | `/client-review "Q3 review for Acme Foundation"` |

Plus 27 single-shot skills: `/buyer-list`, `/teaser`, `/one-pager`, `/process-letter`, `/deal-tracker`, `/morning-note`, `/sector`, `/screen`, `/catalysts`, `/thesis`, `/earnings-preview`, `/model-update`, `/dd-checklist`, `/dd-prep`, `/unit-economics`, `/returns`, `/source`, `/screen-deal`, `/portfolio`, `/value-creation`, `/ai-readiness`, `/tlh`, `/rebalance`, `/proposal`, `/client-report`, `/competitive-analysis`, `/ppt-template`.

Discovery: type **`/fs-help`** (or `/finance-help`) to print the full capability map and the most useful command examples without leaving the chat.

The canonical command list lives in [`copilot-cli/commands/MAPPING.md`](./copilot-cli/commands/MAPPING.md). Add a row, run `python scripts/sync-copilot.py`, and the new slash command surfaces on the next extension load.

## Goal of this fork

The goal of this repository is to **port [`anthropics/financial-services`](https://github.com/anthropics/financial-services) to GitHub Copilot CLI** — taking the Claude-native agents, skills, slash commands and MCP connectors and making them installable as a Copilot CLI extension (`npx -y github:dmauser/financial-services init`) and as a Copilot CLI plugin marketplace (`/plugin marketplace add dmauser/financial-services`). The Claude side stays untouched and canonical at upstream; this fork only adds the `copilot-cli/` delivery channel and the sync tooling that keeps it in lock-step with upstream.

### Staying in sync with upstream

This fork tracks `anthropics/financial-services` automatically. A scheduled GitHub Action (`.github/workflows/upstream-sync.yml`) runs daily, pulls upstream `main`, and opens a PR titled `chore: sync upstream anthropics/financial-services` with any new commits. The PR runs the normal CI gates (`check.py`, `sync-copilot.py` drift check, version-bump) so reviewing the diff is enough — merge it and the Copilot CLI mirror picks up the new agent / skill / MCP automatically on the next `sync-copilot.py` run.

Manual one-off sync from a clone of this repo:

```bash
git remote add upstream https://github.com/anthropics/financial-services.git   # once
git fetch upstream
git checkout -b sync/upstream-$(date +%Y%m%d)
git merge upstream/main                  # resolve conflicts only inside copilot-cli/ if any
python scripts/sync-copilot.py           # regenerate the Copilot CLI mirror
python scripts/check.py                  # must report 0 issues
git push origin HEAD && gh pr create
```

Reference agents, skills, and data connectors for the financial-services workflows we see most — investment banking, equity research, private equity, and wealth management.

Everything here is available **two ways from one source**: install it as a [Claude Cowork](https://claude.com/product/cowork) plugin (from upstream), or deploy it through the [Claude Managed Agents API](https://docs.claude.com/en/api/managed-agents) behind your own workflow engine. This fork adds a third channel: **GitHub Copilot CLI** — see [`copilot-cli/`](./copilot-cli).

> [!IMPORTANT]
> Nothing in this repository constitutes investment, legal, tax, or accounting advice. These agents draft analyst work product — models, memos, research notes, reconciliations — for review by a qualified professional. They do not make investment recommendations, execute transactions, bind risk, post to a ledger, or approve onboarding; every output is staged for human sign-off. You are responsible for verifying outputs and for compliance with the laws and regulations that apply to your firm.

What's in the repo:

- **[Agents](#agents)** — named, end-to-end workflow agents (Pitch Agent, Market Researcher, GL Reconciler, …). Each ships as a Cowork plugin **and** as a [Claude Managed Agent template](./managed-agent-cookbooks) you deploy via `/v1/agents`.
- **[Vertical plugins](#vertical-plugins)** — the underlying skills, slash commands, and data connectors, bundled by FSI vertical. Install these on their own if you just want `/comps`, `/dcf`, `/earnings` and the connectors without a full agent.

## Agents

Each agent is named for the workflow it runs. They're starting points: install the ones that match your work, then tune the prompts, skills, and connectors to how your firm does it.

Each agent plugin is **self-contained** — it bundles the skills it uses, so installing the agent is all you need.

| Function | Agent | What it does |
|---|---|---|
| **Coverage & advisory** | **[Pitch Agent](./plugins/agent-plugins/pitch-agent)** | Comps, precedents, LBO → branded pitch deck, end to end |
| | **[Meeting Prep Agent](./plugins/agent-plugins/meeting-prep-agent)** | Briefing pack before every client meeting |
| **Research & modeling** | **[Market Researcher](./plugins/agent-plugins/market-researcher)** | Sector or theme → industry overview, competitive landscape, peer comps, ideas shortlist |
| | **[Earnings Reviewer](./plugins/agent-plugins/earnings-reviewer)** | Earnings call + filings → model update → note draft |
| | **[Model Builder](./plugins/agent-plugins/model-builder)** | DCF, LBO, 3-statement, comps — live in Excel |
| **Fund admin & finance ops** | **[Valuation Reviewer](./plugins/agent-plugins/valuation-reviewer)** | Ingests GP packages, runs valuation template, stages LP reporting |
| | **[GL Reconciler](./plugins/agent-plugins/gl-reconciler)** | Finds breaks, traces root cause, routes for sign-off |
| | **[Month-End Closer](./plugins/agent-plugins/month-end-closer)** | Accruals, roll-forwards, variance commentary |
| | **[Statement Auditor](./plugins/agent-plugins/statement-auditor)** | Audits LP statements before distribution |
| **Operations & onboarding** | **[KYC Screener](./plugins/agent-plugins/kyc-screener)** | Parses onboarding docs, runs the rules engine, flags gaps |

For Managed Agent deployment — `agent.yaml`, leaf-worker subagents, steering-event examples, and per-agent security notes — see **[managed-agent-cookbooks/](./managed-agent-cookbooks)**.

## Repository Layout

```
plugins/
  agent-plugins/               # Named agents — one self-contained plugin each
  vertical-plugins/            # Skill + command bundles by FSI vertical, plus MCP connectors
  partner-built/               # Partner-authored plugins (LSEG, S&P Global)
managed-agent-cookbooks/       # Claude Managed Agent cookbooks — one dir per agent
copilot-cli/                   # GitHub Copilot CLI extension + plugin marketplace (mirrors plugins/)
claude-for-msft-365-install/   # Admin tooling to provision the Claude Microsoft 365 add-in
scripts/                       # deploy-managed-agent.sh · check.py · validate.py · orchestrate.py · sync-agent-skills.py · sync-copilot.py
```

## Getting Started

### GitHub Copilot CLI (this fork's primary distribution)

```bash
# Install into ~/.copilot/extensions/financial-services/ (one machine, all repos)
npx -y github:dmauser/financial-services init

# Or install only into the current repo
npx -y github:dmauser/financial-services init --project

# Enable individual MCP connectors (still requires provider credentials)
npx financial-services mcp enable daloopa
npx financial-services mcp enable factset
```

Or install via Copilot CLI's native `/plugin` marketplace (registered as `claude-for-financial-services`):

```text
copilot plugin marketplace add dmauser/financial-services
copilot plugin install financial-analysis@claude-for-financial-services
copilot plugin install pitch-agent@claude-for-financial-services
copilot plugin install equity-research@claude-for-financial-services
```

After install, the 10 named specialists, all 39 slash commands, the 12 MCP connectors (disabled by default), and the compliance/house-style instructions load automatically. See [`copilot-cli/README.md`](./copilot-cli/README.md) for the full install reference and [`copilot-cli/RECOMMENDATIONS.md`](./copilot-cli/RECOMMENDATIONS.md) for day-in-the-life workflows.

---

The sections below describe the **upstream Claude distributions** ([`anthropics/financial-services`](https://github.com/anthropics/financial-services)). Install them from upstream, not from this fork.

### Cowork (upstream)

In Cowork, open **Settings → Plugins → Add plugin** and either:

- **Paste this repo URL** — `https://github.com/anthropics/financial-services` — then pick the agents and verticals you want from the marketplace list, or
- **Upload a zip** — zip any directory under `plugins/` (e.g. `plugins/agent-plugins/pitch-agent/`) and drop it in.

### Claude Code (upstream)

```bash
# Add the marketplace
claude plugin marketplace add anthropics/financial-services

# Core skills + connectors (install first)
claude plugin install financial-analysis@claude-for-financial-services

# Named agents — pick the ones you want
claude plugin install pitch-agent@claude-for-financial-services
claude plugin install gl-reconciler@claude-for-financial-services
claude plugin install market-researcher@claude-for-financial-services

# Vertical skill bundles
claude plugin install investment-banking@claude-for-financial-services
claude plugin install equity-research@claude-for-financial-services
```

Once installed, agents appear in Cowork dispatch, skills fire automatically when relevant, and slash commands are available in your session (`/comps`, `/dcf`, `/earnings`, `/ic-memo`, …).

### Claude Managed Agents (upstream)

```bash
export ANTHROPIC_API_KEY=sk-ant-...
scripts/deploy-managed-agent.sh gl-reconciler
```

Each template under [`managed-agent-cookbooks/`](./managed-agent-cookbooks) references the same system prompt and skills as its plugin counterpart. The deploy script resolves file references, uploads skills, creates leaf-worker subagents, and POSTs the orchestrator to `/v1/agents`. See [`scripts/orchestrate.py`](./scripts/orchestrate.py) for a reference event loop that routes `handoff_request` events between agents via your own orchestration layer.

> **Research Preview:** subagent delegation (`callable_agents`) is a preview capability. See per-agent READMEs for security and handoff guidance.

## How It Fits Together

| | What it is | Where it lives |
|---|---|---|
| **Agents** | Self-contained plugins that own a workflow end to end — system prompt plus the skills it uses. Cowork and the Managed Agent wrapper both reference the same directory. | `plugins/agent-plugins/<slug>/` |
| **Skills** | Domain expertise, conventions, and step-by-step methods Claude draws on automatically when relevant. Authored once in the verticals; each agent bundles a synced copy of the ones it needs. | `plugins/vertical-plugins/<vertical>/skills/` (source) · `plugins/agent-plugins/<slug>/skills/` (bundled) |
| **Commands** | Slash actions you trigger explicitly (`/comps`, `/earnings`, `/ic-memo`). | `plugins/vertical-plugins/<vertical>/commands/` |
| **Connectors** | [MCP servers](https://modelcontextprotocol.io/) that wire Claude to your data — terminals, research platforms, document stores. | `plugins/vertical-plugins/financial-analysis/.mcp.json` |
| **Managed-agent wrappers** | `agent.yaml` + depth-1 subagents + steering examples for headless deployment. | `managed-agent-cookbooks/<slug>/` |

Everything is file-based — markdown and JSON, no build step.

## Vertical Plugins

Start with **financial-analysis** — it carries the shared modeling skills and all data connectors. Add verticals for the workflows you need.

| Plugin | What it adds |
|---|---|
| **[financial-analysis](./plugins/vertical-plugins/financial-analysis)** *(core)* | Comps, DCF, LBO, 3-statement, deck QC, Excel audit. All 11 data connectors. |
| **[investment-banking](./plugins/vertical-plugins/investment-banking)** | CIMs, teasers, process letters, buyer lists, merger models, deal tracking. |
| **[equity-research](./plugins/vertical-plugins/equity-research)** | Earnings notes, initiations, model updates, thesis and catalyst tracking. |
| **[private-equity](./plugins/vertical-plugins/private-equity)** | Sourcing, screening, diligence checklists, IC memos, portfolio monitoring. |
| **[wealth-management](./plugins/vertical-plugins/wealth-management)** | Client reviews, financial plans, rebalancing, reporting, TLH. |
| **[fund-admin](./plugins/vertical-plugins/fund-admin)** | GL recon, break tracing, accruals, roll-forwards, variance commentary, NAV tie-out. |
| **[operations](./plugins/vertical-plugins/operations)** | KYC document parsing and rules-grid evaluation. |
| **[lseg](./plugins/partner-built/lseg)** *(partner)* | Bond RV, swap curves, FX carry, options vol, macro-rates monitoring on LSEG data. |
| **[sp-global](./plugins/partner-built/spglobal)** *(partner)* | Tear sheets, earnings previews, funding digests on S&P Capital IQ. |

## MCP Integrations

All connectors are centralized in the **financial-analysis** core plugin and shared across the rest.

| Provider | URL |
|---|---|
| [Daloopa](https://www.daloopa.com/) | `https://mcp.daloopa.com/server/mcp` |
| [Morningstar](https://www.morningstar.com/) | `https://mcp.morningstar.com/mcp` |
| [S&P Global](https://www.spglobal.com/) | `https://kfinance.kensho.com/integrations/mcp` |
| [FactSet](https://www.factset.com/) | `https://mcp.factset.com/mcp` |
| [Moody's](https://www.moodys.com/) | `https://api.moodys.com/genai-ready-data/m1/mcp` |
| [MT Newswires](https://www.mtnewswires.com/) | `https://vast-mcp.blueskyapi.com/mtnewswires` |
| [Aiera](https://www.aiera.com/) | `https://mcp-pub.aiera.com` |
| [LSEG](https://www.lseg.com/) | `https://api.analytics.lseg.com/lfa/mcp` |
| [PitchBook](https://pitchbook.com/) | `https://premium.mcp.pitchbook.com/mcp` |
| [Chronograph](https://www.chronograph.pe/) | `https://ai.chronograph.pe/mcp` |
| [Egnyte](https://www.egnyte.com/) | `https://mcp-server.egnyte.com/mcp` |
| [Box](https://www.box.com/home) | `https://mcp.box.com` |

> MCP access may require a subscription or API key from the provider.

## Claude for Microsoft 365 — Install Tooling

If your firm runs Claude inside Excel, PowerPoint, Word, and Outlook via the Microsoft 365 add-in, [`claude-for-msft-365-install/`](./claude-for-msft-365-install) is the admin tooling to provision it against **your own cloud** — Vertex AI, Bedrock, or an internal LLM gateway — instead of Anthropic's API.

It's a Claude Code plugin (not a Cowork plugin) that walks an IT admin through generating the customized add-in manifest, granting Azure admin consent, and writing per-user routing config via Microsoft Graph. Install with:

```bash
claude plugin install claude-for-msft-365-install@claude-for-financial-services
/claude-for-msft-365-install:setup
```

This is separate from the agents and vertical plugins above — it's the on-ramp that gets the add-in deployed in a tenant, after which the agents and skills here are what runs inside it.

## Making It Yours

These are reference templates — they get better when you tune them to how your firm works.

- **Swap connectors** — point `.mcp.json` at your data providers and internal systems.
- **Add firm context** — drop your terminology, processes, and formatting standards into skill files.
- **Bring your templates** — `/ppt-template` teaches Claude your branded PowerPoint layouts.
- **Adjust agent scope** — edit `agents/<slug>.md` to match how your team actually runs the workflow.
- **Add your own** — copy the structure for workflows we haven't covered.

## Skill & Command Reference

<details>
<summary><b>financial-analysis</b> — core modeling, Excel, deck QC</summary>

| Skill | Command | Description |
|---|---|---|
| comps-analysis | `/comps` | Comparable company analysis with trading multiples |
| dcf-model | `/dcf` | DCF valuation with WACC and sensitivity analysis |
| lbo-model | `/lbo` | Leveraged buyout model |
| 3-statement-model | `/3-statement-model` | Populate 3-statement financial model templates |
| audit-xls | `/debug-model` | Excel model audit — formula tracing, hardcode detection, balance checks |
| clean-data-xls | — | Normalize and clean tabular data in Excel |
| deck-refresh | — | Re-link and refresh embedded charts/tables across a deck |
| competitive-analysis | `/competitive-analysis` | Competitive landscape and market positioning |
| ib-check-deck | — | QC presentations for errors and consistency |
| pptx-author | — | Produce a `.pptx` file headlessly (Managed Agent mode) |
| xlsx-author | — | Produce a `.xlsx` file headlessly (Managed Agent mode) |
| ppt-template-creator | `/ppt-template` | Create reusable PPT template skills |
| skill-creator | — | Guide for creating new skills |

</details>

<details>
<summary><b>investment-banking</b> — deal materials and execution</summary>

| Skill | Command | Description |
|---|---|---|
| strip-profile | `/one-pager` | One-page company profiles for pitch books |
| pitch-deck | — | Populate pitch deck templates with data |
| datapack-builder | — | Build data packs from CIMs and filings |
| cim-builder | `/cim` | Draft Confidential Information Memorandums |
| teaser | `/teaser` | Anonymous one-page company teasers |
| buyer-list | `/buyer-list` | Strategic and financial buyer universe |
| merger-model | `/merger-model` | Accretion/dilution M&A analysis |
| process-letter | `/process-letter` | Bid instructions and process correspondence |
| deal-tracker | `/deal-tracker` | Track live deals, milestones, and action items |

</details>

<details>
<summary><b>equity-research</b> — coverage and publishing</summary>

| Skill | Command | Description |
|---|---|---|
| earnings-analysis | `/earnings` | Post-earnings quarterly update reports |
| earnings-preview | `/earnings-preview` | Pre-earnings scenario analysis and key metrics |
| initiating-coverage | `/initiate` | Institutional-quality initiation reports |
| model-update | `/model-update` | Update financial models with new data |
| morning-note | `/morning-note` | Morning meeting notes and trade ideas |
| sector-overview | `/sector` | Industry landscape and thematic reports |
| thesis-tracker | `/thesis` | Maintain and update investment theses |
| catalyst-calendar | `/catalysts` | Track upcoming catalysts across coverage |
| idea-generation | `/screen` | Stock screening and idea sourcing |

</details>

<details>
<summary><b>private-equity</b> — sourcing through portfolio ops</summary>

| Skill | Command | Description |
|---|---|---|
| deal-sourcing | `/source` | Discover companies, check CRM, draft founder outreach |
| deal-screening | `/screen-deal` | Quick pass/fail on inbound CIMs and teasers |
| dd-checklist | `/dd-checklist` | Diligence checklists by workstream |
| dd-meeting-prep | `/dd-prep` | Prep for management presentations and expert calls |
| unit-economics | `/unit-economics` | ARR cohorts, LTV/CAC, net retention, revenue quality |
| returns-analysis | `/returns` | IRR/MOIC sensitivity tables |
| ic-memo | `/ic-memo` | Investment committee memo drafting |
| portfolio-monitoring | `/portfolio` | Track portfolio company KPIs and variances |
| value-creation-plan | `/value-creation` | Post-close 100-day plans and EBITDA bridges |
| ai-readiness | `/ai-readiness` | Assess a portfolio company's AI readiness |

</details>

<details>
<summary><b>wealth-management</b> — advisor workflows</summary>

| Skill | Command | Description |
|---|---|---|
| client-review | `/client-review` | Prep for client meetings with performance and talking points |
| financial-plan | `/financial-plan` | Retirement, education, estate, and cash-flow projections |
| portfolio-rebalance | `/rebalance` | Allocation drift analysis and tax-aware rebalancing |
| client-report | `/client-report` | Client-facing performance reports |
| investment-proposal | `/proposal` | Proposals for prospective clients |
| tax-loss-harvesting | `/tlh` | Identify TLH opportunities and manage wash sales |

</details>

## Contributing

Everything here is markdown and YAML. Fork, edit, PR. For new content:

- New skill → add it under `plugins/vertical-plugins/<vertical>/skills/`, then run `python3 scripts/sync-agent-skills.py` to propagate to any agent that bundles it, **and** `python3 scripts/sync-copilot.py` to propagate into `copilot-cli/`.
- New agent → `plugins/agent-plugins/<slug>/` (with `agents/<slug>.md` + `skills/`) and a matching `managed-agent-cookbooks/<slug>/`. `python3 scripts/sync-copilot.py` mirrors it into `copilot-cli/extensions/financial-services/specialists/<slug>/`.
- Run `python3 scripts/check.py` before pushing — it lints every manifest, verifies all cross-file references resolve, and fails if any bundled skill or `copilot-cli/` mirror has drifted from its source.

## License

[Apache License 2.0](./LICENSE). See [`NOTICE`](./NOTICE) for attribution to the upstream `anthropics/financial-services` project.
