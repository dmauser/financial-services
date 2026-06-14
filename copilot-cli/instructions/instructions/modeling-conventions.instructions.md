---
applyTo: "**/*.{xlsx,xlsm,csv}"
description: "House conventions for any model produced by financial-services agents."
---

# Modeling conventions

When producing or editing a financial model:

- **Inputs blue, formulas black, links green** - standard banker color code; the `audit-xls` skill enforces it.
- **Top-down sheet order**: Cover -> Assumptions -> Inputs -> Model -> Output/Outputs -> Sensitivity -> Sources.
- **No hardcoded numbers in formula cells.** All assumptions live on the Assumptions sheet and are referenced by name or absolute address.
- **Units explicit in row label**, never in column header alone (e.g. `Revenue ($M)`, `Margin (%)`, not just `Margin`).
- **Date axes**: fiscal year for company-level, calendar year for macro/peer comparisons. Always label which.
- **Three-statement balance check** is mandatory: Assets - Liabilities - Equity = 0 to a tolerance of $1 (or local-currency equivalent). The `3-statement-model` skill emits a balance-check row.
- **Currency**: report in USD millions unless the company reports in a different presentation currency; if so, state the FX assumption.
- **Sources sheet** lists every external number with provider + retrieval date.
