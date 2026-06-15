---
name: rebalance
description: Analyze drift and generate rebalancing trades
source: verticals/wealth-management/commands/rebalance.md
trigger: |
  User explicitly invokes /rebalance, or asks for the workflow described in verticals/wealth-management/commands/rebalance.md.
tags: [command-skill, wealth-management]
---

# /rebalance

Skill wrapper for the `/rebalance` slash command (vertical: **wealth-management**).

The full instructions live in [`verticals/wealth-management/commands/rebalance.md`](verticals/wealth-management/commands/rebalance.md). On invocation, follow that
file's workflow exactly.

This wrapper is **generated** by `scripts/sync-copilot.py` from
`commands/MAPPING.md`. Do not hand-edit.
