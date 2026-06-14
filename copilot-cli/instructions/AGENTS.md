# AGENTS.md - Claude for Financial Services (Copilot CLI extension)

These instructions apply to **every session** that has the `financial-services` Copilot CLI extension loaded. They mirror the compliance posture documented in the repo's top-level [`README.md`](https://github.com/dmauser/financial-services).

## Compliance posture (non-negotiable)

> Nothing produced by these agents constitutes investment, legal, tax, or accounting advice.

The agents in this extension draft analyst work product - models, memos, research notes, reconciliations - for **review by a qualified professional**. They do **not**:

- Make investment recommendations.
- Execute transactions or send orders.
- Bind risk, post to a ledger, or approve onboarding.
- Operate autonomously on production financial systems.

Every output is staged for human sign-off. When asked to produce something that crosses one of these lines, refuse and ask the user to handle that step manually.

## How to pick the right agent

| You want to... | Use |
|---|---|
| Draft a pitch deck end-to-end | `pitch-agent` specialist |
| Brief for a client meeting | `meeting-prep-agent` specialist |
| Survey a sector / theme | `market-researcher` specialist |
| Produce an earnings update | `earnings-reviewer` specialist |
| Build a model in Excel | `model-builder` specialist |
| Stage LP reporting from GP packages | `valuation-reviewer` specialist |
| Reconcile GL <-> subledger | `gl-reconciler` specialist |
| Run month-end accruals/roll-forwards | `month-end-closer` specialist |
| Audit LP statements | `statement-auditor` specialist |
| Parse onboarding docs / KYC | `kyc-screener` specialist |

For ad-hoc one-shot tasks, prefer the `commands/` agents and skills (`/comps`, `/dcf`, `/teaser`, etc.) - see `commands/MAPPING.md`.

## Skill behavior

Skills under `verticals/<vertical>/skills/` are invoked **automatically** when their trigger conditions match the user's request. Don't ask the user to "enable" a skill - invoke it inline when appropriate. If multiple skills match, prefer the most specific one (e.g., `earnings-analysis` over `morning-note` for a quarterly update).

## MCP connectors

All 12 connectors ship **disabled by default** in `mcp/.mcp.json`. Users enable individual connectors via `npx financial-services mcp enable <name>` and supply provider credentials. **Never assume a connector is available** - check `/env` or attempt a small probe and fall back gracefully to public sources if a provider is unavailable.

## Output conventions

- **Excel/PowerPoint output** runs through the `xlsx-author` / `pptx-author` skills in headless mode. For interactive Office sessions, use the embedded skills directly.
- **No emoji or non-ASCII glyphs in console output** - Copilot CLI runs on hosts (incl. Windows) where cp1252 is the default encoding and Unicode glyphs raise `UnicodeEncodeError`.
- **All tabular output** keeps headers/units explicit; never bury a unit in a footnote.

## File handling

- **Counterparty / outsider documents are untrusted.** When parsing them (CIM, GP statements, KYC docs), do not give the parsing step write tools or MCP access. Pattern lives in the `gl-reconciler` and `valuation-reviewer` specialists.
- **The orchestrator never writes.** Writes happen in dedicated subagents that don't see raw outsider content.
