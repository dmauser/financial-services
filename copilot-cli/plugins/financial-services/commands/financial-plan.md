---
name: financial-plan
description: Build or update a financial plan
source: verticals/wealth-management/commands/financial-plan.md
tags: [command-agent, wealth-management]
---

# /financial-plan

Wrapper for the `/financial-plan` slash command (vertical: **wealth-management**, kind: **agent**).

The full workflow lives in [`verticals/wealth-management/commands/financial-plan.md`](verticals/wealth-management/commands/financial-plan.md). When this agent is selected,
load that file's instructions verbatim and execute its workflow. Inputs and
clarification questions are defined there.

This wrapper is **generated** by `scripts/sync-copilot.py` from
`commands/MAPPING.md`. Do not hand-edit.
