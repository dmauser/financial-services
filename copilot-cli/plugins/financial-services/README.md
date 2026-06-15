# financial-services (umbrella plugin)

Bundles every Claude for Financial Services specialist + skill + slash
command into a single Claude/Copilot plugin install. Behaves as a markdown
orchestrator (`agents/financial-services.md`) that routes incoming requests
to the right specialist.

**Generated** by `scripts/sync-copilot.py` from the canonical sources under
`plugins/agent-plugins/`, `plugins/vertical-plugins/`, `plugins/partner-built/`,
and `copilot-cli/commands/`. Do not hand-edit.

Install:

```text
copilot plugin marketplace add dmauser/financial-services
copilot plugin install financial-services@claude-for-financial-services
```

For the runtime tool registration (`fs_capabilities`, `fs_<slug>_role`, ...) use
the npx extension instead: `npx -y github:dmauser/financial-services init`.
