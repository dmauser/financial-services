# Slash command classification

Each slash command from `verticals/<vertical>/commands/` is exposed in Copilot CLI either as:

- **`agent`** — high-value, multi-step workflows that benefit from a dedicated specialist context (`commands/agents/<name>/agent.md`).
- **`skill`** — single-shot or trigger-cued behaviors registered as skills (`commands/skills/<name>/SKILL.md`).

The wrappers under `commands/` are **generated** by `scripts/sync-copilot.py` from this table. **Edit this table, then run sync** — never hand-edit files in `commands/`. `scripts/check.py` enforces the mirror.

| Command | Vertical | Kind | Source |
|---|---|---|---|
| `/comps` | financial-analysis | agent | `verticals/financial-analysis/commands/comps.md` |
| `/dcf` | financial-analysis | agent | `verticals/financial-analysis/commands/dcf.md` |
| `/lbo` | financial-analysis | agent | `verticals/financial-analysis/commands/lbo.md` |
| `/3-statement-model` | financial-analysis | agent | `verticals/financial-analysis/commands/3-statement-model.md` |
| `/debug-model` | financial-analysis | agent | `verticals/financial-analysis/commands/debug-model.md` |
| `/competitive-analysis` | financial-analysis | skill | `verticals/financial-analysis/commands/competitive-analysis.md` |
| `/ppt-template` | financial-analysis | skill | `verticals/financial-analysis/commands/ppt-template.md` |
| `/cim` | investment-banking | agent | `verticals/investment-banking/commands/cim.md` |
| `/merger-model` | investment-banking | agent | `verticals/investment-banking/commands/merger-model.md` |
| `/teaser` | investment-banking | skill | `verticals/investment-banking/commands/teaser.md` |
| `/one-pager` | investment-banking | skill | `verticals/investment-banking/commands/one-pager.md` |
| `/buyer-list` | investment-banking | skill | `verticals/investment-banking/commands/buyer-list.md` |
| `/process-letter` | investment-banking | skill | `verticals/investment-banking/commands/process-letter.md` |
| `/deal-tracker` | investment-banking | skill | `verticals/investment-banking/commands/deal-tracker.md` |
| `/earnings` | equity-research | agent | `verticals/equity-research/commands/earnings.md` |
| `/initiate` | equity-research | agent | `verticals/equity-research/commands/initiate.md` |
| `/earnings-preview` | equity-research | skill | `verticals/equity-research/commands/earnings-preview.md` |
| `/model-update` | equity-research | skill | `verticals/equity-research/commands/model-update.md` |
| `/morning-note` | equity-research | skill | `verticals/equity-research/commands/morning-note.md` |
| `/sector` | equity-research | skill | `verticals/equity-research/commands/sector.md` |
| `/screen` | equity-research | skill | `verticals/equity-research/commands/screen.md` |
| `/catalysts` | equity-research | skill | `verticals/equity-research/commands/catalysts.md` |
| `/thesis` | equity-research | skill | `verticals/equity-research/commands/thesis.md` |
| `/ic-memo` | private-equity | agent | `verticals/private-equity/commands/ic-memo.md` |
| `/dd-checklist` | private-equity | skill | `verticals/private-equity/commands/dd-checklist.md` |
| `/dd-prep` | private-equity | skill | `verticals/private-equity/commands/dd-prep.md` |
| `/unit-economics` | private-equity | skill | `verticals/private-equity/commands/unit-economics.md` |
| `/returns` | private-equity | skill | `verticals/private-equity/commands/returns.md` |
| `/source` | private-equity | skill | `verticals/private-equity/commands/source.md` |
| `/screen-deal` | private-equity | skill | `verticals/private-equity/commands/screen-deal.md` |
| `/portfolio` | private-equity | skill | `verticals/private-equity/commands/portfolio.md` |
| `/value-creation` | private-equity | skill | `verticals/private-equity/commands/value-creation.md` |
| `/ai-readiness` | private-equity | skill | `verticals/private-equity/commands/ai-readiness.md` |
| `/financial-plan` | wealth-management | agent | `verticals/wealth-management/commands/financial-plan.md` |
| `/client-review` | wealth-management | agent | `verticals/wealth-management/commands/client-review.md` |
| `/tlh` | wealth-management | skill | `verticals/wealth-management/commands/tlh.md` |
| `/rebalance` | wealth-management | skill | `verticals/wealth-management/commands/rebalance.md` |
| `/proposal` | wealth-management | skill | `verticals/wealth-management/commands/proposal.md` |
| `/client-report` | wealth-management | skill | `verticals/wealth-management/commands/client-report.md` |

**Total**: 12 agents, 27 skills, 39 commands.
