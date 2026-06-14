# Recommendations - day-in-the-life with Copilot CLI

How to combine the agents, skills, and MCP connectors in **`financial-services`** for the workflows we see most. Each recipe assumes you've installed the extension (`npx -y github:dmauser/financial-services init`) and have Copilot CLI running in a repo where you can drop output files.

These are **starting points** - tune them to your firm's process.

## 1. Equity analyst morning

**Goal**: 30-minute pre-market read of overnight news, your coverage's catalysts, and one prepared earnings update.

**Connectors to enable**: `daloopa`, `aiera`, `mtnewswire`, optionally `morningstar`.

```bash
npx financial-services mcp enable daloopa
npx financial-services mcp enable aiera
npx financial-services mcp enable mtnewswire
```

**Session**:

```text
> /morning-note for my coverage list (AAPL MSFT NVDA AMD GOOG)
> /catalysts for the next 5 trading days
> Use the earnings-reviewer specialist on AAPL Q3 2026 - load the call from Aiera, refresh the model with Daloopa, and draft a quarterly note.
```

The `earnings-reviewer` specialist orchestrates `earnings-analysis`, `model-update`, and a critique pass before producing the draft note. It will ask for your house style if it doesn't find one in `instructions/`.

## 2. Investment banking - deal week

**Goal**: from sector pitch through teaser, one-pager, buyer list, and CIM.

**Connectors**: `daloopa` or `factset` (financials), `pitchbook` (private comps), `sp-global` (precedents), `box` or `egnyte` (drop the deliverables).

```text
> Use the pitch-agent specialist for a sector pitch on industrial automation - target $1-3B EV
> /teaser for ${target}
> /one-pager for ${target}
> /buyer-list for ${target} - 8 strategics, 12 sponsors
> /cim for ${target} - draft sections 1-4 only, financials placeholder
> /merger-model ${acquirer} acquiring ${target} at $${price}M, 60% stock 40% cash
```

The pitch-agent stitches `comps-analysis`, `precedent-transactions`, `lbo-model`, and `pptx-author` together. Branded templates: see `/ppt-template`.

## 3. Fund admin - month-end close

**Goal**: GL <-> subledger reconciliation, accruals, statements out the door.

**Connectors**: your firm's internal `internal-gl` and `subledger` MCPs (configure in `mcp/.mcp.json` - the 12 shipped connectors are public-provider only).

```text
> Use the gl-reconciler specialist for trade date 2026-06-30 across equities, fixed income, derivatives
> Use the month-end-closer specialist - run accruals and roll-forwards for fund alpha
> Use the statement-auditor specialist on the draft LP statements in ./out/statements/
```

The gl-reconciler dispatches reader subagents that cannot write or call MCPs (counterparty docs are untrusted), then a critic re-verifies, and only the resolver subagent formats the exception report. See [`extensions/financial-services/specialists/gl-reconciler/agents/gl-reconciler.md`](./extensions/financial-services/specialists/gl-reconciler/agents/gl-reconciler.md).

## 4. Private equity - diligence sprint

**Goal**: from inbound CIM to IC memo.

**Connectors**: `pitchbook`, `sp-global`, `chronograph`, `egnyte` (data room mounted).

```text
> /screen-deal on ./inbound/cim_acme.pdf
> Use the market-researcher specialist for the ${target} sector - peer comps, growth drivers, regulatory
> /dd-checklist for a control buyout - workstreams: commercial, financial, tech, legal
> /unit-economics on the ${target} cohort data in ./dataroom/cohorts.xlsx
> /returns - sensitivity over entry multiple [10x, 12x, 14x] and exit year [2029, 2030, 2031]
> /ic-memo for ${target}
```

`/dd-checklist` and `/dd-prep` are skills (not full agents) - they're cued by the user request. `/ic-memo` is an agent because it's multi-section and benefits from a dedicated context.

## 5. Wealth advisor - quarterly client cycle

**Goal**: review packages, rebalance, harvest losses.

**Connectors**: `morningstar`, optionally `daloopa` for individual-stock detail.

```text
> Use the meeting-prep-agent specialist for client ${name} - load the latest performance from ./clients/${name}/
> /client-review for ${name}
> /rebalance ${name}'s portfolio against the moderate model, drift threshold 5%
> /tlh for ${name} year-to-date - exclude wash-sale candidates
> /client-report for ${name} Q2 2026
```

## 6. Pure ad-hoc - "I just need a comps table"

You don't have to drive a specialist. Any vertical skill is reachable via its slash command:

```text
> /comps NVDA
> /dcf NVDA - 5-year explicit, 2.5% terminal growth, 9% WACC
> /lbo ACME at 11.5x EBITDA, 60% leverage, 5-year hold
```

These run as either agents (`/comps`, `/dcf`, `/lbo`) or skills (`/teaser`, etc.) based on `commands/MAPPING.md`. Either way, you only need them installed - no extra config.

## Gotchas

- **MCPs require credentials.** Enabling a connector via `npx financial-services mcp enable` does not store keys; provide them through the Copilot CLI host's `/mcp` configuration UI.
- **Specialists run a critic pass.** Multi-step workflows (gl-reconciler, earnings-reviewer, statement-auditor) re-verify their own output before producing the final artifact - expect them to take 2-4 turns.
- **No emoji in shell output.** Copilot CLI runs on Windows hosts where the default cp1252 console can't render Unicode glyphs. The skills here keep all CLI output ASCII-safe.
- **Counterparty documents are untrusted.** When a workflow ingests a CIM, GP statement, or KYC pack, the parsing subagent cannot write or call MCPs. Trust boundary lives in the agent's system prompt - don't override it.
- **Output files** land in `./out/` by convention when you run a specialist headlessly. The `xlsx-author` and `pptx-author` skills require the host to allow file writes.

## Combine with your custom instructions

Drop firm-specific guidance into:

- `~/.copilot/instructions/firm.instructions.md` - applies everywhere
- `<repo>/.github/copilot-instructions.md` - applies in this repo
- `<repo>/AGENTS.md` - applies in this repo

The financial-services compliance and house-style instructions in [`instructions/`](./instructions) will compose with yours.
