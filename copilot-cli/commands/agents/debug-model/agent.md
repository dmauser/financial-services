---
name: debug-model
description: Debug and audit a financial model for errors
source: verticals/financial-analysis/commands/debug-model.md
tags: [command-agent, financial-analysis]
---

# /debug-model

Wrapper for the `/debug-model` slash command (vertical: **financial-analysis**, kind: **agent**).

The full workflow lives in [`verticals/financial-analysis/commands/debug-model.md`](verticals/financial-analysis/commands/debug-model.md). When this agent is selected,
load that file's instructions verbatim and execute its workflow. Inputs and
clarification questions are defined there.

This wrapper is **generated** by `scripts/sync-copilot.py` from
`commands/MAPPING.md`. Do not hand-edit.
