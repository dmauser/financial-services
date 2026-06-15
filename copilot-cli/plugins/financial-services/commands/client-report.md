---
name: client-report
description: Generate a client performance report
source: verticals/wealth-management/commands/client-report.md
trigger: |
  User explicitly invokes /client-report, or asks for the workflow described in verticals/wealth-management/commands/client-report.md.
tags: [command-skill, wealth-management]
---

# /client-report

Skill wrapper for the `/client-report` slash command (vertical: **wealth-management**).

The full instructions live in [`verticals/wealth-management/commands/client-report.md`](verticals/wealth-management/commands/client-report.md). On invocation, follow that
file's workflow exactly.

This wrapper is **generated** by `scripts/sync-copilot.py` from
`commands/MAPPING.md`. Do not hand-edit.
